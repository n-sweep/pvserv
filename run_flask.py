import os
import time
import socket
import logging
import webbrowser

from flask_socketio import SocketIO
from app import app

socketio = SocketIO(app, cors_allowed_origins="*", transport='websocket')


@socketio.on('connect')
def handle_connect():
    """ once connected, start file watcher """
    handler = Handler(app, socketio)
    socketio.start_background_task(target=handler.watch_for_modification)


class Handler:
    """ file handler watches for and emits updates to plot file """
    def __init__(self, app, socketio):
        self.mt = 0
        self.app = app
        self.socketio = socketio

        self.ensure_directory()
        logging.info('handler started')

    def watch_for_modification(self):
        """ look for change in modified time of `file` every `i` ms """
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
        """ ensure the tmp directory exists before attempting to save a file """
        file = self.app.config['file']
        dir = os.path.dirname(file)
        if not os.path.exists(dir):
            os.makedirs(dir)


def main():
    host_name = socket.getfqdn()
    ip = socket.gethostbyname(host_name)
    port = 5619
    logging.basicConfig(filename='pvserv.log', level=logging.INFO)

    config = {
        'file': '/tmp/vis/plot.json',
        'interval': 0.1,
        'url': f'http://{ip}:{port}'
    }

    app.config.update(config)

    webbrowser.open_new(app.config['url'])
    socketio.run(app, host=ip, port=port, debug=True)


if __name__ == "__main__":
    main()
