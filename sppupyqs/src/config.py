import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE_URL = os.getenv(
    "SPPUPYQS_SITE_URL",
    "https://sppupyqs.vercel.app",
).strip().rstrip("/")
CODES_SITE_URL = os.getenv("SPPUCODES_SITE_URL", "https://sppucodes.vercel.app").strip().rstrip("/")
QUESTION_PAPERS_DIR = os.path.join(BASE_DIR, "question-papers")

PDF_SOURCE = os.getenv("PDF_SOURCE", "r2").strip().lower()
_VALID_PDF_SOURCES = {"r2", "supabase"}
if PDF_SOURCE not in _VALID_PDF_SOURCES:
    PDF_SOURCE = "r2"

QP_PDF_DIR = os.path.join(QUESTION_PAPERS_DIR, f"question-papers-{PDF_SOURCE}")
QP_SEO_DIR = os.path.join(QUESTION_PAPERS_DIR, "pyqs-seo")

CF_WORKER_DB_URL = os.getenv("CF_WORKER_DB_URL", "").strip().rstrip("/")
DB_API_KEY = os.getenv("DB_API_KEY", "").strip()
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
MAINTENANCE_MODE = os.getenv("MAINTENANCE_MODE", "false").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY") or os.getenv("FLASK_SECRET_KEY", "karltos")

DEFAULT_EXAM_TYPE = os.getenv("DEFAULT_EXAM_TYPE", "endsem").strip().lower()
if DEFAULT_EXAM_TYPE not in {"insem", "endsem"}:
    DEFAULT_EXAM_TYPE = "endsem"

PDF_PROXY_ALLOWED_HOSTS = {
    host.strip().lower()
    for host in os.getenv(
        "PDF_PROXY_ALLOWED_HOSTS",
        "sppucodes.albatrossc.workers.dev,zauiiivigqoifsvtqhnt.supabase.co",
    ).split(",")
    if host.strip()
}
