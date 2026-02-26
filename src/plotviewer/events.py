from queue import Queue
from threading import Lock


class SSEBroker:
    def __init__(self) -> None:
        self.clients = []
        self.lock = Lock()

    def subscribe(self) -> Queue:
        """browser connects - create a queue"""
        q = Queue()
        with self.lock:
            self.clients.append(q)
        return q

    def unsubscribe(self, q) -> None:
        """browser disconnects - remove queue"""
        with self.lock:
            self.clients.remove(q)

    def publish(self, event_type, data) -> None:
        """POST endpoint"""
        with self.lock:
            for q in self.clients:
                q.put((event_type, data))


broker = SSEBroker()
