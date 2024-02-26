from app import app, socketio

import logging
import os
import socket
import threading
import webbrowser


def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]

    except socket.error:
        return None


def ensure_dir(dir):
    if not os.path.isdir(dir):
        os.makedirs(dir)


def launch_server(host, port, config):
    app.config.update(config)
    threading.Timer(0.5, webbrowser.open_new, [app.config['url']]).start()
    socketio.run(app, host=host, port=port, allow_unsafe_werkzeug=True)


def main():
    plot_file = '/tmp/vis/plot.json'
    log_file = os.path.expanduser('~/.local/share/nvim/pvserv.log')

    logging.basicConfig(filename=log_file, level=logging.INFO)

    ip = get_lan_ip()
    port = 5619

    config = {
        'file': plot_file,
        'interval': 0.1,
        'ip': ip,
        'port': port,
        'url': f'http://{ip}:{port}'
    }

    ensure_dir(os.path.dirname(plot_file))
    launch_server(ip, port, config)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.info(e)
