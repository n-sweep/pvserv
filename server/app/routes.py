import sqlite3

from flask import request, render_template
from server.app import app, socketio


@app.route('/')
def index() -> str:
    return render_template(
        'index.html',
        ip_address=app.config['socket_ip'],
        port=app.config['port'],
    )


@app.route('/plot')
def handle_new_plot() -> str:
    data = request.json

    with sqlite3.connect(app.config['db_file']) as con:
        cur = con.cursor()
        cur.execute("INSERT INTO plots (json) VALUES (?)", (data,))
        con.commit()

        cur.execute("SELECT json, created_at FROM plots ORDER BY created_at DESC LIMIT 1")
        cols = [desc[0] for desc in cur.description]
        update_data = [dict(zip(cols, result)) for result in cur.fetchall()]

    socketio.emit('update', update_data[0])

    return '200'
