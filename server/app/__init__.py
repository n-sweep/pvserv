from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    transport='websocket',
    use_reloader=False
)

from server.app import routes, events
