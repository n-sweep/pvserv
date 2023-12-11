import os
import time
import logging

from flask import Flask, render_template
from flask_socketio import SocketIO

logging.basicConfig(filename='log.log', level=logging.INFO)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", transport='websocket')


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    socketio.start_background_task(
        target=check_update,
        file=app.config['file'],
        app=app,
        socketio=socketio,
        i=app.config['interval']
    )


def emit_update(file):
    with open(file, 'r') as f:
        socketio.emit('update', f.read())


def check_update(file, app, socketio, i):
    emit_update(file)
    mt = os.path.getmtime(file)
    while True:
        new_mt = os.path.getmtime(file)
        if new_mt != mt:
            mt = new_mt
            emit_update(file)

        socketio.sleep(i)


def main():
    app.config['file'] = './plot.json'
    app.config['interval'] = 0.1
    socketio.run(app, debug=True)


if __name__ == "__main__":
    main()
