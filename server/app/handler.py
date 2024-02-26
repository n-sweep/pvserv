import os
import logging


class FileHandler:
    """ file handler watches for and emits updates to plot file """
    def __init__(self, app, socketio):
        self.mt = 0
        self.app = app
        self.socketio = socketio

        self.ensure_directory()
        logging.info('server started')

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
