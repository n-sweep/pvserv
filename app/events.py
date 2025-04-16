import sqlite3

from app import app, socketio


def get_recent_plots(n: int = 1) -> list:
    with sqlite3.connect(app.config['db_file']) as con:
        cur = con.cursor()
        cur.execute("SELECT json, created_at FROM plots ORDER BY created_at DESC LIMIT ?", (n,))
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, result)) for result in cur.fetchall()]


@socketio.on('connect')
def handle_connect():
    plots = get_recent_plots(20)
    socketio.emit('log', f"Logging to `{app.config['log_file']}`")
    socketio.emit('initialize', plots)
