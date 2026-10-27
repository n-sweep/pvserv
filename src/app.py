import os
import sqlite3
from datetime import datetime, timezone
from queue import Empty, Queue
from threading import Lock
from typing import Generator

from flask import Flask, Response, abort, render_template, request, stream_with_context

app = Flask(__name__)
app.config['db_file'] = os.environ.get('DB_PATH', '/data/db.sqlite3')


PLOTLY_MIME = 'application/vnd.plotly.v1+json'

# read-side column list; image bytes are never loaded here, so `data` is the
# figure JSON for plotly rows and NULL for everything else
PLOT_COLS = ( f"id, mime, created_at, CASE WHEN mime = '{PLOTLY_MIME}' THEN data END AS data")


def init_db() -> None:
    """create the plot table if it does not exist."""
    with sqlite3.connect(app.config['db_file']) as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS plot (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                mime       TEXT NOT NULL,
                data       BLOB NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def create_plot(data: str | bytes, mime: str = PLOTLY_MIME) -> dict:
    """insert a new plot and return it as a dict.

    Parameters
    ----------
    data : str or bytes
        raw plotly figure JSON string, or decoded image bytes
    mime : str, optional
        mime type of the data, by default the plotly figure type

    Returns
    -------
    dict
        the newly created plot row with keys id, mime, created_at, data;
        data is None for non-plotly rows
    """
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    with sqlite3.connect(app.config['db_file']) as con:
        cur = con.execute(
            'INSERT INTO plot (mime, data, created_at) VALUES (?, ?, ?)',
            (mime, data, now),
        )
        con.commit()
        cur = con.execute(f'SELECT {PLOT_COLS} FROM plot WHERE id = ?', (cur.lastrowid,))
        cols = [desc[0] for desc in cur.description]
        return dict(zip(cols, cur.fetchone()))


def get_recent_plots(n: int = 20) -> list[dict]:
    """return the n most recent plots ordered newest first.

    Parameters
    ----------
    n : int, optional
        number of plots to return, by default 20

    Returns
    -------
    list[dict]
        list of plot rows with keys id, mime, created_at, data;
        data is None for non-plotly rows
    """
    with sqlite3.connect(app.config['db_file']) as con:
        cur = con.execute(f'SELECT {PLOT_COLS} FROM plot ORDER BY created_at DESC LIMIT ?', (n,))
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def get_plot(plot_id: int) -> dict | None:
    """return a single plot by id, or None if not found.

    Parameters
    ----------
    plot_id : int
        primary key of the plot to fetch

    Returns
    -------
    dict or None
        plot row with keys id, mime, created_at, data, or None;
        data is None for non-plotly rows
    """
    with sqlite3.connect(app.config['db_file']) as con:
        cur = con.execute(f'SELECT {PLOT_COLS} FROM plot WHERE id = ?', (plot_id,))
        row = cur.fetchone()
        if row is None:
            return None
        cols = [desc[0] for desc in cur.description]
        return dict(zip(cols, row))


class SSEBroker:
    """in-process pub/sub broker for server-sent events."""

    def __init__(self) -> None:
        self.clients: list[Queue] = []
        self.lock = Lock()

    def subscribe(self) -> Queue:
        """register a new subscriber and return its queue."""
        q: Queue = Queue()
        with self.lock:
            self.clients.append(q)
        return q

    def unsubscribe(self, q: Queue) -> None:
        """remove a subscriber queue."""
        with self.lock:
            self.clients.remove(q)

    def publish(self, event_type: str, data: dict) -> None:
        """broadcast an event to all subscribers."""
        with self.lock:
            for q in self.clients:
                q.put((event_type, data))


broker = SSEBroker()


@app.get('/plotviewer/')
def index() -> str:
    plots = get_recent_plots()
    return render_template('index.html', plots=plots)


@app.post('/plotviewer/plot')
@app.post('/plotviewer/plot/')
def handle_new_plot() -> tuple[str, int]:
    data = request.get_data(as_text=True)
    plot = create_plot(data)
    broker.publish('new-plot', plot)
    return '', 201


@app.get('/plotviewer/plot/<int:plot_id>/')
def plot(plot_id: int) -> str:
    p = get_plot(plot_id)
    if p is None:
        abort(404)
    return render_template('partials/plot.html', plot=p)


@app.get('/plotviewer/events/')
def sse_stream() -> Response:
    @stream_with_context
    def event_generator() -> Generator[str, None, None]:
        q = broker.subscribe()
        yield ': connected\n\n'
        try:
            while True:
                try:
                    event_type, plot = q.get(timeout=1)
                except Empty:
                    continue
                html = render_template('partials/plot_list_item.html', plot=plot)
                data_lines = '\n'.join(f'data: {line}' for line in html.splitlines())
                yield f'event: {event_type}\n{data_lines}\n\n'
        finally:
            broker.unsubscribe(q)

    return Response(
        event_generator(),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'},
    )


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080, threaded=True)
