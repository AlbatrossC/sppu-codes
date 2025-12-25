from flask import (
    Flask, render_template, send_from_directory,
    abort, request, redirect, jsonify, flash, url_for
)
from werkzeug.exceptions import HTTPException
import os
import json
import psycopg2
import requests
from functools import lru_cache
from urllib.parse import urlparse
import glob
from datetime import datetime

# =============================================================================
# APP INIT
# =============================================================================

app = Flask(__name__)
# Use an environment variable for secret key in production, fallback to hardcoded for local
app.secret_key = os.getenv("SECRET_KEY", "karltos")

BASE_DIR = os.path.dirname(__file__)
QUESTIONS_DIR = os.path.join(BASE_DIR, "questions")
ANSWERS_DIR = os.path.join(BASE_DIR, "answers")
QUESTION_PAPERS_DIR = os.path.join(BASE_DIR, "question-papers")

# Environment Variables
DATABASE_URL = os.getenv("DATABASE_URL")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# =============================================================================
# DATABASE & NOTIFICATION UTILS
# =============================================================================

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    if not DATABASE_URL:
        return None
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def init_db():
    """Creates necessary tables if they don't exist."""
    conn = get_db_connection()
    if not conn:
        print("Warning: DATABASE_URL not set. Database features disabled.")
        return

    try:
        with conn:
            with conn.cursor() as cur:
                # Table for Code Submissions
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS submissions (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100),
                        year VARCHAR(10),
                        branch VARCHAR(50),
                        subject VARCHAR(200),
                        question TEXT,
                        answer TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                # Table for Contact Messages
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS contacts (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100),
                        email VARCHAR(150),
                        message TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

def send_discord_notification(notification_type, data):
    """Sends a formatted embed message to Discord with Custom Headers for Vercel."""
    if not DISCORD_WEBHOOK_URL:
        print("Discord Webhook URL not set.")
        return

    embed = {}
    
    if notification_type == "submit":
        embed = {
            "title": "🚀 New Code Submission",
            "color": 5763719,  # Green/Blue
            "fields": [
                {"name": "Contributor Name", "value": data.get("name", "Anonymous"), "inline": True},
                {"name": "Subject", "value": data.get("subject"), "inline": True},
                {"name": "Branch/Year", "value": f"{data.get('branch')} - {data.get('year')}", "inline": False}
            ],
            "footer": {"text": "Check database for full code"}
        }
    elif notification_type == "contact":
        embed = {
            "title": "📩 New Contact Query",
            "color": 15158332,  # Red/Orange
            "fields": [
                {"name": "From", "value": data.get("name"), "inline": True},
                {"name": "Email", "value": data.get("email"), "inline": True},
                {"name": "Message Snippet", "value": (data.get("message")[:200] + '...') if len(data.get("message")) > 200 else data.get("message"), "inline": False}
            ]
        }

    payload = {
        "embeds": [embed]
    }

    # CRITICAL FIX FOR VERCEL:
    # Discord blocks default python-requests user agents from cloud IPs.
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "SPPU-Codes-Bot/1.0 (Vercel; +https://yourwebsite.com)"
    }

    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL, 
            json=payload, 
            headers=headers, 
            timeout=5 # Add timeout to prevent serverless function hanging
        )
        response.raise_for_status() # Raises error for 4xx/5xx codes
        print(f"Discord notification sent successfully. Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Discord notification: {e}")
        if hasattr(e, 'response') and e.response is not None:
             print(f"Discord Response: {e.response.text}")

# =============================================================================
# MAINTENANCE MODE
# =============================================================================

MAINTENANCE_MODE = os.getenv("MAINTENANCE_MODE", "false").lower() == "true"
MAINTENANCE_BYPASS_IP = os.getenv("MAINTENANCE_BYPASS_IP")

@app.before_request
def maintenance():
    if MAINTENANCE_MODE:
        if MAINTENANCE_BYPASS_IP and request.remote_addr == MAINTENANCE_BYPASS_IP:
            return
        if request.path.startswith("/static") or request.path.startswith("/images"):
            return
        return render_template("maintenance.html"), 503

# =============================================================================
# STATIC FILES
# =============================================================================

@app.route("/images/<filename>")
def get_image(filename):
    images_dir = os.path.join(BASE_DIR, "images")
    path = os.path.join(images_dir, filename)
    if not os.path.exists(path):
        abort(404)
    return send_from_directory(images_dir, filename)

# =============================================================================
# URL MIGRATION (OLD → NEW)
# =============================================================================

@app.before_request
def questionpapers_redirect():
    path = request.path
    if path == "/questionpapers":
        return redirect("/question-papers", code=301)
    if path.startswith("/questionpapers/"):
        return redirect("/question-papers" + path[len("/questionpapers"):], code=301)

# =============================================================================
# QUESTION PAPERS CACHE
# =============================================================================

@lru_cache(maxsize=1)
def load_question_papers():
    branches = []
    subjects_index = {}
    search_index = []

    if not os.path.exists(QUESTION_PAPERS_DIR):
        return {
            "branches": [],
            "subjects_index": {},
            "search_index": []
        }

    for file_path in glob.glob(os.path.join(QUESTION_PAPERS_DIR, "*.json")):
        branch_code = os.path.splitext(os.path.basename(file_path))[0]

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        branch_name = data.get("branch_name")

        branch_entry = {
            "branch_name": branch_name,
            "branch_code": branch_code,
            "semesters": {}
        }

        for key, value in data.items():
            if not key.startswith("sem-") or not isinstance(value, dict):
                continue

            sem_no = key.split("-")[-1]
            subjects = []

            for subject_link, subject in value.items():
                subject_name = subject.get("subject_name")

                subjects.append({
                    "subject_name": subject_name,
                    "subject_link": subject_link
                })

                subjects_index.setdefault(subject_link, []).extend(
                    subject.get("pdf_links", [])
                )

                search_index.append({
                    "type": "QUESTION_PAPER",
                    "subject_name": subject_name,
                    "branch": branch_name,
                    "branch_code": branch_code,
                    "semester": sem_no,
                    "link": f"/question-papers/{subject_link}"
                })

            branch_entry["semesters"][f"Semester {sem_no}"] = subjects

        branches.append(branch_entry)

    return {
        "branches": branches,
        "subjects_index": subjects_index,
        "search_index": search_index
    }

# =============================================================================
# MAIN ROUTES
# =============================================================================

@app.route("/")
def index():
    return render_template("index.html")

# -----------------------------------------------------------------------------
# SUBMIT ROUTE
# -----------------------------------------------------------------------------
@app.route("/submit", methods=["GET", "POST"])
def submit_code():
    if request.method == "POST":
        name = request.form.get("name", "Anonymous")
        year = request.form.get("year")
        branch = request.form.get("branch")
        subject = request.form.get("subject")
        question = request.form.get("question")
        answer = request.form.get("answer")

        # Database Insertion
        conn = get_db_connection()
        if conn:
            try:
                with conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "INSERT INTO submissions (name, year, branch, subject, question, answer) VALUES (%s, %s, %s, %s, %s, %s)",
                            (name, year, branch, subject, question, answer)
                        )
                flash("Your code has been submitted successfully! It will be reviewed shortly.", "success")
                
                # Send Discord Notification
                send_discord_notification("submit", {
                    "name": name,
                    "year": year,
                    "branch": branch,
                    "subject": subject
                })
            except Exception as e:
                print(f"Submit Error: {e}")
                flash("An error occurred while saving your submission. Please try again.", "error")
            finally:
                conn.close()
        else:
            flash("Database connection unavailable. Please try again later.", "error")

        return redirect(url_for('submit_code'))

    return render_template("submit.html")

# -----------------------------------------------------------------------------
# CONTACT ROUTE
# -----------------------------------------------------------------------------
@app.route("/contact", methods=["GET", "POST"])
def contact_us():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        # Database Insertion
        conn = get_db_connection()
        if conn:
            try:
                with conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "INSERT INTO contacts (name, email, message) VALUES (%s, %s, %s)",
                            (name, email, message)
                        )
                flash("Your message has been sent successfully!", "success")

                # Send Discord Notification
                send_discord_notification("contact", {
                    "name": name,
                    "email": email,
                    "message": message
                })
            except Exception as e:
                print(f"Contact Error: {e}")
                flash("An error occurred. Please try again.", "error")
            finally:
                conn.close()
        else:
            flash("Database connection unavailable. Please try again later.", "error")

        return redirect(url_for('contact_us'))

    return render_template("contact.html")

# =============================================================================
# QUESTION PAPERS
# =============================================================================

@app.route("/question-papers")
def select_page():
    qp = load_question_papers()
    organized_data = {
        b["branch_name"]: b["semesters"] for b in qp["branches"]
    }
    return render_template("select.html", organized_data=organized_data)

@app.route("/question-papers/<subject_link>")
def viewer_page(subject_link):
    qp = load_question_papers()
    pdfs = qp["subjects_index"].get(subject_link)

    if not pdfs:
        abort(404)

    subject_display = subject_link.replace("-", " ").title()
    pdf_data = [
        {"filename": os.path.basename(urlparse(u).path), "url": u}
        for u in pdfs
    ]

    seo_data = {
        "title": f"{subject_display} Question Papers | SPPU Codes",
        "description": f"Download {subject_display} SPPU question papers",
        "keywords": f"{subject_display}, sppu, question papers",
        "subject_name": subject_display
    }

    return render_template(
        "viewer.html",
        subject_name=subject_display,
        pdf_data_for_js=pdf_data,
        seo_data=seo_data
    )

# =============================================================================
# 🔥 SUBJECT ROUTES (FIXED)
# filename == link (ai.json → /ai)
# =============================================================================

@app.route("/<subject_link>")
@app.route("/<subject_link>/<question_id>")
def subject_page(subject_link, question_id=None):
    # Avoid conflict with reserved routes
    if subject_link in ['submit', 'contact', 'images', 'static', 'api']:
        abort(404)

    json_path = os.path.join(QUESTIONS_DIR, f"{subject_link}.json")

    if not os.path.exists(json_path):
        abort(404)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    subject = data.get("default", {})
    questions = data.get("questions", [])

    groups = {}
    for q in questions:
        groups.setdefault(q["group"], []).append(q)

    sorted_groups = sorted(groups.keys())

    selected_question = None
    if question_id:
        selected_question = next(
            (q for q in questions if q["id"] == question_id), None
        )
        if not selected_question:
            abort(404)

    return render_template(
        "subject.html",
        title=subject.get("subject_name", subject_link.upper()),
        description=subject.get("description", ""),
        keywords=subject.get("keywords", []),
        url=subject.get("url"),
        subject_code=subject_link,          # 🔑 link, not JSON subject_code
        subject_name=subject.get("subject_name"),
        question_paper_url=subject.get("question_paper_url"),
        groups=groups,
        sorted_groups=sorted_groups,
        question=selected_question
    )

# =============================================================================
# ANSWER API (TERMINAL + MODAL)
# =============================================================================

@app.route("/api/<subject_link>/<question_no>")
def answer_api(subject_link, question_no):
    json_path = os.path.join(QUESTIONS_DIR, f"{subject_link}.json")
    if not os.path.exists(json_path):
        return "Subject not found", 404, {"Content-Type": "text/plain"}

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    question = next(
        (q for q in data.get("questions", [])
         if str(q.get("question_no")) == str(question_no)),
        None
    )

    if not question:
        return "Question not found", 404, {"Content-Type": "text/plain"}

    files = question.get("file_name", [])
    if not files:
        return "No answer files", 404, {"Content-Type": "text/plain"}

    subject_dir = os.path.join(ANSWERS_DIR, subject_link)
    if not os.path.exists(subject_dir):
        return "Answer directory missing", 404, {"Content-Type": "text/plain"}

    # ---------------------------
    # Query flags
    # ---------------------------
    no_question = request.args.get("no_question") == "1"
    split = request.args.get("split")

    output = []

    # Include question (terminal default)
    if not no_question:
        output.append(question["question"].strip())
        output.append("")

    # Split mode → return only ONE file
    if split:
        try:
            index = int(split) - 1
            if index < 0 or index >= len(files):
                return "Invalid split index", 400, {"Content-Type": "text/plain"}
            files = [files[index]]
        except ValueError:
            return "Invalid split parameter", 400, {"Content-Type": "text/plain"}

    # Read files
    for fname in files:
        path = os.path.join(subject_dir, fname)
        if not os.path.exists(path):
            return f"File missing: {fname}", 404, {"Content-Type": "text/plain"}

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        if not split:
            output.append("-" * 40)
            output.append(f"File: {fname}")
            output.append("-" * 40)

        output.append(content.strip())
        output.append("")

    return "\n".join(output).strip(), 200, {
        "Content-Type": "text/plain; charset=utf-8"
    }

# =============================================================================
# SEARCH API
# =============================================================================

@app.route("/api/question-papers/search")
def question_papers_search():
    return jsonify(load_question_papers()["search_index"])

@app.route("/api/subjects/search")
def subjects_search():
    subjects = []
    if os.path.exists(QUESTIONS_DIR):
        for file in os.listdir(QUESTIONS_DIR):
            if file.endswith(".json"):
                subject_link = file[:-5]
                json_path = os.path.join(QUESTIONS_DIR, file)
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    subject_name = data.get("default", {}).get("subject_name", subject_link)
                except Exception:
                    subject_name = subject_link
                subjects.append({
                    "subject_link": subject_link,
                    "subject_name": subject_name
                })
    return jsonify(subjects)
# =============================================================================
# SEO FILES
# =============================================================================

@app.route("/robots.txt")
def robots():
    return send_from_directory(".", "robots.txt")

@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory(".", "sitemap.xml")

# =============================================================================
# ERRORS
# =============================================================================

@app.errorhandler(404)
def not_found(e):
    path = request.path
    app.logger.info(f"404 Not Found: {path} from {request.remote_addr}")
    return render_template("error.html", error_code=404, requested_path=path), 404

@app.errorhandler(500)
def server_error(e):
    # Log full exception with stack trace
    app.logger.exception(f"500 Internal Server Error at {request.path}")

    # In debug mode, expose a short error message to the template for easier debugging
    error_message = None
    try:
        if app.debug:
            error_message = str(e)
    except Exception:
        error_message = None

    return render_template("error.html", error_code=500, error_message=error_message), 500


@app.errorhandler(HTTPException)
def handle_http_exception(e):
    """Catch other HTTP exceptions (e.g., 403, 405) and render the error page with context."""
    code = getattr(e, 'code', 500) or 500
    description = getattr(e, 'description', '')
    app.logger.warning(f"HTTP {code} {e.name} for path {request.path} from {request.remote_addr}")
    return render_template("error.html", error_code=code, error_message=description, requested_path=request.path), code

# =============================================================================
# ENTRY
# =============================================================================

# This logic is usually for local dev. Vercel uses WSGI but might not trigger __main__
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=3000, debug=True)
else:
    pass