# DB operations delegated to Cloudflare Worker → Cloudflare D1
# All calls are fire-and-forget — the caller gets an immediate response
# while the actual DB insert happens in a background thread.
import threading
import requests
from .config import CF_WORKER_DB_URL, DB_API_KEY

_http = requests.Session()


def _db_post(endpoint, payload):
    """Fire-and-forget POST to the sppucodes-db Worker."""
    if not CF_WORKER_DB_URL or not DB_API_KEY:
        return

    def _send():
        try:
            _http.post(
                f"{CF_WORKER_DB_URL}{endpoint}",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": DB_API_KEY,
                },
                timeout=3,
            )
        except Exception:
            pass  # Worker unreachable — silently ignore to keep app fast

    threading.Thread(target=_send, daemon=True).start()


def init_db():
    """No-op: Schema is managed via wrangler d1 execute on deploy."""
    pass


def save_submission(name, email, subject, question, code):
    """Saves a code submission via Cloudflare D1 Worker."""
    _db_post("/api/submit", {
        "name": name,
        "email": email,
        "subject": subject,
        "question": question,
        "code": code,
    })
    return True


def save_contact(name, email, message):
    """Saves a contact message via Cloudflare D1 Worker."""
    _db_post("/api/contact", {
        "name": name,
        "email": email,
        "message": message,
    })
    return True


def save_api_request(subject_link, question_no, status):
    """Saves an API request log via Cloudflare D1 Worker."""
    _db_post("/api/log", {
        "subject": subject_link,
        "question_no": str(question_no),
        "status": status,
    })
    return True


def save_paper_download(fingerprint_id, subject):
    """Saves a paper download event via Cloudflare D1 Worker (upserts)."""
    _db_post("/api/download", {
        "fingerprint_id": fingerprint_id,
        "subject": subject,
    })
    return True
