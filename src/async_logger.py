import queue
import threading

from .db import save_api_request


class AsyncAPILogger:
    def __init__(self, maxsize=1000):
        self._queue = queue.Queue(maxsize=maxsize)
        self._thread = None
        self._lock = threading.Lock()

    def start(self):
        if self._thread and self._thread.is_alive():
            return

        with self._lock:
            if self._thread and self._thread.is_alive():
                return

            self._thread = threading.Thread(
                target=self._worker,
                name="api-request-logger",
                daemon=True,
            )
            self._thread.start()

    def log_api_request(self, subject_link, question_no, ip_address, user_agent):
        try:
            self._queue.put_nowait(
                (subject_link, str(question_no), ip_address or "", user_agent or "")
            )
        except queue.Full:
            return False
        return True

    def _worker(self):
        while True:
            item = self._queue.get()
            try:
                save_api_request(*item)
            except Exception as exc:
                print(f"Async API logger error: {exc}")
            finally:
                self._queue.task_done()


api_logger = AsyncAPILogger()