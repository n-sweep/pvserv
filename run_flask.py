import os
import time
import socket
import logging

from flask import Flask, render_template, request
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", transport='websocket')


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    handler = Handler(app, socketio)
    socketio.start_background_task(target=handler.watch_for_modification)


class Handler:
    def __init__(self, app, socketio):
        self.mt = 0
        self.app = app
        self.socketio = socketio

        self.ensure_directory()

    def watch_for_modification(self):
        file = self.app.config['file']
        i = self.app.config['interval']

        while True:

            if os.path.exists(file):
                mt = os.path.getmtime(file)
                if mt != self.mt:
                    self.mt = mt
                    with open(file, 'r') as f:
                        self.socketio.emit('update', f.read())

            self.socketio.sleep(i)

    def ensure_directory(self):
        file = self.app.config['file']
        dir = os.path.dirname(file)
        if not os.path.exists(dir):
            os.makedirs(dir)


def main():
    host_name = socket.getfqdn()
    ip = socket.gethostbyname(host_name)
    logging.basicConfig(filename='pvserv.log', level=logging.INFO)

    config = {
        'file': '/tmp/vis/plot.json',
        'interval': 0.1
    }

    app.config.update(config)

    socketio.run(app, host=ip, port=5619, debug=True)


if __name__ == "__main__":
    main()
