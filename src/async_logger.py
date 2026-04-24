import threading

from .db import save_api_request, save_paper_download


def _run_in_background(target, *args):
    thread = threading.Thread(target=target, args=args, daemon=True)
    thread.start()
    return True


def log_api_request_async(subject_link, question_no, status):
    def task():
        try:
            save_api_request(subject_link, question_no, status)
        except Exception:
            pass

    return _run_in_background(task)


def log_paper_download_async(fingerprint_id, subject):
    def task():
        try:
            save_paper_download(fingerprint_id, subject)
        except Exception:
            pass

    return _run_in_background(task)


class AsyncAPILogger:
    def start(self):
        return None

    def log_api_request(self, subject_link, question_no, status):
        return log_api_request_async(subject_link, question_no, status)


api_logger = AsyncAPILogger()
