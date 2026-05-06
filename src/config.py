import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
QUESTIONS_DIR = os.path.join(BASE_DIR, "questions")
ANSWERS_DIR = os.path.join(BASE_DIR, "answers")
QUESTION_PAPERS_DIR = os.path.join(BASE_DIR, "question-papers")

PDF_SOURCE = os.getenv("PDF_SOURCE", "r2").strip().lower()
_VALID_PDF_SOURCES = {"r2"}
if PDF_SOURCE not in _VALID_PDF_SOURCES:
    print(f"Warning: PDF_SOURCE='{PDF_SOURCE}' is invalid. Falling back to 'r2'.")
    PDF_SOURCE = "r2"

QP_PDF_DIR = os.path.join(QUESTION_PAPERS_DIR, f"question-papers-{PDF_SOURCE}")
QP_SEO_DIR = os.path.join(QUESTION_PAPERS_DIR, "pyqs-seo")

# Cloudflare D1 Worker DB
CF_WORKER_DB_URL = os.getenv("CF_WORKER_DB_URL", "").strip().rstrip("/")
DB_API_KEY = os.getenv("DB_API_KEY", "").strip()
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
MAINTENANCE_MODE = os.getenv("MAINTENANCE_MODE", "false").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY") or os.getenv("FLASK_SECRET_KEY", "karltos")

DEFAULT_EXAM_TYPE = os.getenv("DEFAULT_EXAM_TYPE", "endsem").strip().lower()
_VALID_EXAM_TYPES = {"insem", "endsem"}
if DEFAULT_EXAM_TYPE not in _VALID_EXAM_TYPES:
    print(f"Warning: DEFAULT_EXAM_TYPE='{DEFAULT_EXAM_TYPE}' is invalid. Falling back to 'endsem'.")
    DEFAULT_EXAM_TYPE = "endsem"

print(f"[PDF Source] Using '{PDF_SOURCE}' -> {QP_PDF_DIR}")
