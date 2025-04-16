from app import app, socketio

import logging
import os
import socket
import sqlite3
import threading
import webbrowser

base_dir = os.path.dirname(os.path.abspath(__file__))


def get_lan_ip() -> None:
    """get the LAN IP address of the machine running the server"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
    except socket.error:
        return None


def launch_server(config: dict, open_browser: bool = False) -> None:
    """Launch the server and optionally open in the browser"""
    host = config['broadcast_ip']
    port = config['port']

    logging.basicConfig(filename=config['log_file'], level=logging.INFO)
    app.config.update(config)

    # ensure the database exists
    with sqlite3.connect(config['db_file']) as con:
        with open(f'{base_dir}/server/queries/create.sql', 'r') as f:
            cur = con.cursor()
            cur.execute(f.read())
            con.commit()
            cur.close()

    if open_browser:
        url = f'http://{host}:{port}'
        threading.Timer(0.5, webbrowser.open_new, [url]).start()

    socketio.run(
        app,
        host=host,
        port=port,
        debug=True,
        allow_unsafe_werkzeug=True
    )


def main():

    config = {
        'broadcast_ip': '0.0.0.0',
        'socket_ip': os.environ.get('TS_IP', get_lan_ip()),
        'port': 8080,
        'db_file': os.path.expanduser('/app/data/pvserv.db'),
        'log_file': os.path.expanduser('/app/data/pvserv.log')
    }

    launch_server(config) #, open_browser=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.info(e)
