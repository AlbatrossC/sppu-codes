import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
QUESTIONS_DIR = os.path.join(BASE_DIR, "questions")
ANSWERS_DIR = os.path.join(BASE_DIR, "answers")
QUESTION_PAPERS_DIR = os.path.join(BASE_DIR, "question-papers")

PDF_SOURCE = os.getenv("PDF_SOURCE", "r2").strip().lower()
_VALID_PDF_SOURCES = {"r2", "supabase"}
if PDF_SOURCE not in _VALID_PDF_SOURCES:
    print(f"Warning: PDF_SOURCE='{PDF_SOURCE}' is invalid. Falling back to 'r2'.")
    PDF_SOURCE = "r2"

QP_PDF_DIR = os.path.join(QUESTION_PAPERS_DIR, f"question-papers-{PDF_SOURCE}")
QP_SEO_DIR = os.path.join(QUESTION_PAPERS_DIR, "pyqs-seo")

DATABASE_URL = os.getenv("DATABASE_URL")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
MAINTENANCE_MODE = os.getenv("MAINTENANCE_MODE", "false").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "karltos")

print(f"[PDF Source] Using '{PDF_SOURCE}' -> {QP_PDF_DIR}")
