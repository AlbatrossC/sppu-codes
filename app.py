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

# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "karltos")

BASE_DIR = os.path.dirname(__file__)
QUESTIONS_DIR = os.path.join(BASE_DIR, "questions")
ANSWERS_DIR = os.path.join(BASE_DIR, "answers")
QUESTION_PAPERS_DIR = os.path.join(BASE_DIR, "question-papers")

DATABASE_URL = os.getenv("DATABASE_URL")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
MAINTENANCE_MODE = os.getenv("MAINTENANCE_MODE", "false").lower() == "true"
MAINTENANCE_BYPASS_IP = os.getenv("MAINTENANCE_BYPASS_IP")

# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    if not DATABASE_URL:
        return None
    try:
        return psycopg2.connect(DATABASE_URL, sslmode='require')
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


def save_submission(name, year, branch, subject, question, answer):
    """Saves a code submission to the database."""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO submissions (name, year, branch, subject, question, answer) VALUES (%s, %s, %s, %s, %s, %s)",
                    (name, year, branch, subject, question, answer)
                )
        return True
    except Exception as e:
        print(f"Submit Error: {e}")
        return False
    finally:
        conn.close()


def save_contact(name, email, message):
    """Saves a contact message to the database."""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO contacts (name, email, message) VALUES (%s, %s, %s)",
                    (name, email, message)
                )
        return True
    except Exception as e:
        print(f"Contact Error: {e}")
        return False
    finally:
        conn.close()

# ============================================================================
# NOTIFICATION SYSTEM
# ============================================================================

def send_discord_notification(notification_type, data):
    """Sends a formatted embed message to Discord."""
    if not DISCORD_WEBHOOK_URL:
        print("Discord Webhook URL not set.")
        return

    embed = _build_discord_embed(notification_type, data)
    if not embed:
        return

    payload = {"embeds": [embed]}
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "SPPU-Codes-Bot/1.0 (Vercel; +https://yourwebsite.com)"
    }

    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL, 
            json=payload, 
            headers=headers, 
            timeout=5
        )
        response.raise_for_status()
        print(f"Discord notification sent successfully. Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Discord notification: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Discord Response: {e.response.text}")


def _build_discord_embed(notification_type, data):
    """Builds the appropriate Discord embed based on notification type."""
    if notification_type == "submit":
        return {
            "title": "New Code Submission",
            "color": 5763719,
            "fields": [
                {"name": "Contributor Name", "value": data.get("name", "Anonymous"), "inline": True},
                {"name": "Subject", "value": data.get("subject"), "inline": True},
                {"name": "Branch/Year", "value": f"{data.get('branch')} - {data.get('year')}", "inline": False}
            ],
            "footer": {"text": "Check database for full code"}
        }
    
    elif notification_type == "contact":
        message = data.get("message", "")
        message_snippet = (message[:200] + '...') if len(message) > 200 else message
        return {
            "title": "New Contact Query",
            "color": 15158332,
            "fields": [
                {"name": "From", "value": data.get("name"), "inline": True},
                {"name": "Email", "value": data.get("email"), "inline": True},
                {"name": "Message Snippet", "value": message_snippet, "inline": False}
            ]
        }
    
    elif notification_type == "download":
        user_agent = data.get("user_agent", "")
        ua_snippet = (user_agent[:200] + '...') if len(user_agent) > 200 else user_agent
        return {
            "title": "ZIP Download",
            "color": 3447003,
            "fields": [
                {"name": "Subject", "value": data.get("subject_name", data.get("subject_link", "Unknown")), "inline": True},
                {"name": "Subject Link", "value": data.get("subject_link", "unknown"), "inline": True},
                {"name": "Exam Type", "value": data.get("exam_type", "all"), "inline": True},
                {"name": "Files In ZIP", "value": str(data.get("file_count", 0)), "inline": True},
                {"name": "Success", "value": "Yes" if data.get("success", True) else "No", "inline": True},
                {"name": "From IP", "value": data.get("ip", "unknown"), "inline": False},
                {"name": "User Agent (truncated)", "value": ua_snippet, "inline": False}
            ],
            "footer": {"text": "No file or repo URLs included"}
        }
    
    return None

# ============================================================================
# QUESTION PAPERS MANAGEMENT
# ============================================================================

@lru_cache(maxsize=1)
def load_question_papers():
    """
    Loads and caches question papers data from JSON files.
    Normalizes subject data so subjects_index always stores a DICT.
    """

    branches = []
    papers_list = []
    subjects_index = {}

    if not os.path.exists(QUESTION_PAPERS_DIR):
        return {
            "branches": [],
            "question_papers_list": [],
            "subjects_index": {}
        }

    for file_path in glob.glob(os.path.join(QUESTION_PAPERS_DIR, "*.json")):
        branch_code = os.path.splitext(os.path.basename(file_path))[0]

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        branch_name = data.get("branch_name", branch_code)

        branch_entry = {
            "branch_name": branch_name,
            "branch_code": branch_code,
            "semesters": {}
        }

        for key, value in data.items():
            if not key.startswith("sem-") or not isinstance(value, dict):
                continue

            sem_no = int(key.split("-")[-1])
            subjects_for_sem = []

            for subject_link, subject in value.items():
                if not isinstance(subject, dict):
                    continue

                subject_name = subject.get("subject_name", subject_link)

                # ----------------------------
                # NORMALIZED SUBJECT OBJECT
                # ----------------------------
                subject_obj = {
                    "subject_name": subject_name,
                    "seo_data": subject.get("seo_data", {}),
                    "pdf_links": subject.get("pdf_links", []),
                    "branch_name": branch_name,
                    "branch_code": branch_code,
                    "semester": sem_no,
                    "subject_link": subject_link
                }

                # Used by /question-papers/<subject>
                subjects_index[subject_link] = subject_obj

                # Used by select page
                subjects_for_sem.append({
                    "subject_name": subject_name,
                    "subject_link": subject_link
                })

                # Used by API list
                papers_list.append({
                    "type": "QUESTION_PAPER",
                    "subject_name": subject_name,
                    "subject_link": subject_link,
                    "branch_name": branch_name,
                    "branch_code": branch_code,
                    "semester": sem_no,
                    "public_url": f"/question-papers/{subject_link}",
                    "repo_path": f"{branch_code}/sem-{sem_no}/{subject_link}"
                })

            branch_entry["semesters"][f"Semester {sem_no}"] = subjects_for_sem

        branches.append(branch_entry)

    return {
        "branches": branches,
        "question_papers_list": papers_list,
        "subjects_index": subjects_index
    }


# ============================================================================
# SUBJECT/QUESTIONS OPERATIONS
# ============================================================================

def load_subject_data(subject_link):
    """Loads subject data from JSON file."""
    json_path = os.path.join(QUESTIONS_DIR, f"{subject_link}.json")
    if not os.path.exists(json_path):
        return None
    
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_question_by_id(questions, question_id):
    """Finds a question by its ID."""
    return next((q for q in questions if q["id"] == question_id), None)


def get_question_by_number(questions, question_no):
    """Finds a question by its number."""
    return next((q for q in questions if str(q.get("question_no")) == str(question_no)), None)


def organize_questions_by_group(questions):
    """Organizes questions into groups."""
    groups = {}
    for q in questions:
        groups.setdefault(q["group"], []).append(q)
    return groups, sorted(groups.keys())


def load_answer_files(subject_link, files):
    """Loads answer files for a question."""
    subject_dir = os.path.join(ANSWERS_DIR, subject_link)
    if not os.path.exists(subject_dir):
        return None, "Answer directory missing"
    
    contents = []
    for fname in files:
        path = os.path.join(subject_dir, fname)
        if not os.path.exists(path):
            return None, f"File missing: {fname}"
        
        with open(path, "r", encoding="utf-8") as f:
            contents.append((fname, f.read().strip()))
    
    return contents, None

# ============================================================================
# MIDDLEWARE AND REQUEST HANDLERS
# ============================================================================

@app.before_request
def maintenance():
    """Handles maintenance mode."""
    if MAINTENANCE_MODE:
        if MAINTENANCE_BYPASS_IP and request.remote_addr == MAINTENANCE_BYPASS_IP:
            return
        if request.path.startswith("/static") or request.path.startswith("/images"):
            return
        return render_template("maintenance.html"), 503


@app.before_request
def questionpapers_redirect():
    """Redirects old question papers URLs to new format."""
    path = request.path
    if path == "/questionpapers":
        return redirect("/question-papers", code=301)
    if path.startswith("/questionpapers/"):
        return redirect("/question-papers" + path[len("/questionpapers"):], code=301)

# ============================================================================
# MAIN ROUTES
# ============================================================================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/submit", methods=["GET", "POST"])
def submit_code():
    if request.method == "POST":
        name = request.form.get("name", "Anonymous")
        year = request.form.get("year")
        branch = request.form.get("branch")
        subject = request.form.get("subject")
        question = request.form.get("question")
        answer = request.form.get("answer")

        if save_submission(name, year, branch, subject, question, answer):
            flash("Your code has been submitted successfully! It will be reviewed shortly.", "success")
            send_discord_notification("submit", {
                "name": name,
                "year": year,
                "branch": branch,
                "subject": subject
            })
        else:
            flash("An error occurred while saving your submission. Please try again.", "error")

        return redirect(url_for('submit_code'))

    return render_template("submit.html")


@app.route("/contact", methods=["GET", "POST"])
def contact_us():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        if save_contact(name, email, message):
            flash("Your message has been sent successfully!", "success")
            send_discord_notification("contact", {
                "name": name,
                "email": email,
                "message": message
            })
        else:
            flash("An error occurred. Please try again.", "error")

        return redirect(url_for('contact_us'))

    return render_template("contact.html")

# ============================================================================
# QUESTION PAPERS ROUTES
# ============================================================================

@app.route("/question-papers")
def select_page():
    qp = load_question_papers()
    organized_data = {
        branch["branch_name"]: branch["semesters"]
        for branch in qp["branches"]
    }
    return render_template("select.html", organized_data=organized_data)


@app.route("/question-papers/<subject_link>")
def viewer_page(subject_link):
    qp = load_question_papers()
    subject = qp["subjects_index"].get(subject_link)

    if not subject:
        abort(404)

    subject_name = subject["subject_name"]
    seo_data = subject.get("seo_data", {})

    pdf_data = [
        {
            "filename": os.path.basename(urlparse(u).path),
            "url": u
        }
        for u in subject.get("pdf_links", [])
    ]

    seo_data = {
        "title": seo_data.get(
            "title",
            f"{subject_name} Question Papers | SPPU Codes"
        ),
        "description": seo_data.get(
            "description",
            f"{subject_name} SPPU question papers for exam preparation"
        ),
        "keywords": seo_data.get(
            "keywords",
            f"{subject_name}, sppu question papers"
        )
    }

    return render_template(
        "viewer.html",
        subject_name=subject_name,
        subject_link=subject_link,
        pdf_data_for_js=pdf_data,
        seo_data=seo_data
    )

# ============================================================================
# SUBJECT/QUESTIONS ROUTES
# ============================================================================

@app.route("/<subject_link>")
@app.route("/<subject_link>/<question_id>")
def subject_page(subject_link, question_id=None):
    if subject_link in ['submit', 'contact', 'images', 'static', 'api']:
        abort(404)

    data = load_subject_data(subject_link)
    if not data:
        abort(404)

    subject = data.get("default", {})
    questions = data.get("questions", [])
    groups, sorted_groups = organize_questions_by_group(questions)

    selected_question = None
    if question_id:
        selected_question = get_question_by_id(questions, question_id)
        if not selected_question:
            abort(404)

    return render_template(
        "subject.html",
        title=subject.get("subject_name", subject_link.upper()),
        description=subject.get("description", ""),
        keywords=subject.get("keywords", []),
        url=subject.get("url"),
        subject_code=subject_link,
        subject_name=subject.get("subject_name"),
        question_paper_url=subject.get("question_paper_url"),
        groups=groups,
        sorted_groups=sorted_groups,
        question=selected_question
    )

# ============================================================================
# API ROUTES
# ============================================================================

@app.route("/api/question-papers/list")
def question_papers_list():
    return jsonify(load_question_papers()["question_papers_list"])


@app.route("/api/subjects/search")
def subjects_search():
    subjects = []
    if os.path.exists(QUESTIONS_DIR):
        for file in os.listdir(QUESTIONS_DIR):
            if file.endswith(".json"):
                subject_link = file[:-5]
                data = load_subject_data(subject_link)
                subject_name = subject_link
                if data:
                    subject_name = data.get("default", {}).get("subject_name", subject_link)
                
                subjects.append({
                    "subject_link": subject_link,
                    "subject_name": subject_name
                })
    return jsonify(subjects)


@app.route("/api/<subject_link>/<question_no>")
def answer_api(subject_link, question_no):
    data = load_subject_data(subject_link)

    # ===============================
    # SUBJECT NOT FOUND
    # ===============================
    if not data:
        output = []
        output.append("No question found")
        output.append("")
        output.append("Available subjects:")
        output.append("")

        if os.path.exists(QUESTIONS_DIR):
            for f in sorted(os.listdir(QUESTIONS_DIR)):
                if f.endswith(".json"):
                    code = f[:-5]
                    d = load_subject_data(code)
                    full_name = d.get("default", {}).get("subject_name", code.upper()) if d else code.upper()
                    output.append(f"{code} --> {full_name}")
                    output.append("")

        return "\n".join(output).strip(), 404, {
            "Content-Type": "text/plain; charset=utf-8"
        }

    questions = data.get("questions", [])
    question = get_question_by_number(questions, question_no)

    # ===============================
    # QUESTION NOT FOUND
    # ===============================
    if not question:
        output = []
        output.append("No question found")
        output.append("")
        output.append(f"Available questions for subject: {subject_link}")
        output.append("")

        for q in questions:
            q_no = q.get("question_no", "N/A")
            q_text = q.get("question", "").strip()
            output.append(f"{q_no} --> {q_text}")
            output.append("")

        return "\n".join(output).strip(), 404, {
            "Content-Type": "text/plain; charset=utf-8"
        }

    files = question.get("file_name", [])
    if not files:
        return "No answer files", 404, {"Content-Type": "text/plain"}

    no_question = request.args.get("no_question") == "1"
    split = request.args.get("split")

    if split:
        try:
            index = int(split) - 1
            if index < 0 or index >= len(files):
                return "Invalid split index", 400, {"Content-Type": "text/plain"}
            files = [files[index]]
        except ValueError:
            return "Invalid split parameter", 400, {"Content-Type": "text/plain"}

    contents, error = load_answer_files(subject_link, files)
    if error:
        return error, 404, {"Content-Type": "text/plain"}

    output = []

    if not no_question:
        output.append(question["question"].strip())
        output.append("")

    for fname, content in contents:
        if not split:
            output.append("-" * 40)
            output.append(f"File: {fname}")
            output.append("-" * 40)
        output.append(content)
        output.append("")

    return "\n".join(output).strip(), 200, {
        "Content-Type": "text/plain; charset=utf-8"
    }


@app.route("/api/notify-download", methods=["POST"])
def notify_download():
    """Receives download event from client and forwards to Discord."""
    if not DISCORD_WEBHOOK_URL:
        return ("", 204)

    try:
        payload = request.get_json(silent=True)
        if not payload:
            return jsonify({"error": "invalid json"}), 400

        send_discord_notification("download", {
            "subject_link": payload.get("subject_link"),
            "subject_name": payload.get("subject_name"),
            "exam_type": payload.get("exam_type"),
            "file_count": int(payload.get("file_count") or 0),
            "success": bool(payload.get("success", True)),
            "user_agent": request.headers.get("User-Agent", "")[:1000],
            "ip": request.remote_addr or "unknown"
        })
        return jsonify({"ok": True}), 200
    except Exception:
        app.logger.exception("notify_download error")
        return jsonify({"error": "server error"}), 500

# ============================================================================
# STATIC FILES AND SEO
# ============================================================================

@app.route("/images/<filename>")
def get_image(filename):
    images_dir = os.path.join(BASE_DIR, "images")
    if not os.path.exists(os.path.join(images_dir, filename)):
        abort(404)
    return send_from_directory(images_dir, filename)


@app.route("/robots.txt")
def robots():
    return send_from_directory(".", "robots.txt")


@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory(".", "sitemap.xml")

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    path = request.path
    app.logger.info(f"404 Not Found: {path} from {request.remote_addr}")
    return render_template("error.html", error_code=404, requested_path=path), 404


@app.errorhandler(500)
def server_error(e):
    app.logger.exception(f"500 Internal Server Error at {request.path}")
    error_message = str(e) if app.debug else None
    return render_template("error.html", error_code=500, error_message=error_message), 500


@app.errorhandler(HTTPException)
def handle_http_exception(e):
    code = getattr(e, 'code', 500) or 500
    description = getattr(e, 'description', '')
    app.logger.warning(f"HTTP {code} {e.name} for path {request.path} from {request.remote_addr}")
    return render_template("error.html", error_code=code, error_message=description, requested_path=request.path), code

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    init_db()
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=3000, debug=debug_mode)