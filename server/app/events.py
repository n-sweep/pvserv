from app import app, socketio
from app.handler import FileHandler


@socketio.on('connect')
def handle_connect():
    """ once connected, start file watcher """
    handler = FileHandler(app, socketio)
    socketio.start_background_task(target=handler.watch_for_modification)
