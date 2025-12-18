from flask import (
    Flask, render_template, send_from_directory, abort,
    request, redirect, url_for, flash, jsonify
)
import os
import json
import psycopg2
from functools import lru_cache
from urllib.parse import urlparse
import glob

# =============================================================================
# APP INIT & MAINTENANCE
# =============================================================================

app = Flask(__name__)
app.secret_key = 'karltos'

MAINTENANCE_MODE = os.getenv("MAINTENANCE_MODE", "false").lower() == "true"
MAINTENANCE_BYPASS_IP = os.getenv("MAINTENANCE_BYPASS_IP")


@app.before_request
def maintenance():
    if MAINTENANCE_MODE:
        if MAINTENANCE_BYPASS_IP and request.remote_addr == MAINTENANCE_BYPASS_IP:
            return
        if request.path.startswith("/static"):
            return
        return render_template("maintenance.html"), 503
    
@app.route("/images/<filename>")
def get_image(filename):
    images_dir = os.path.join(BASE_DIR, "images")
    if not os.path.exists(os.path.join(images_dir, filename)):
        abort(404)
    return send_from_directory(images_dir, filename)



# =============================================================================
# LOCAL FALLBACK REDIRECT
# =============================================================================

@app.before_request
def questionpapers_redirect():
    path = request.path
    if path == "/questionpapers":
        return redirect("/question-papers", code=301)
    if path.startswith("/questionpapers/"):
        return redirect("/question-papers" + path[len("/questionpapers"):], code=301)


# =============================================================================
# PATHS
# =============================================================================

BASE_DIR = os.path.dirname(__file__)
QUESTIONS_DIR = os.path.join(BASE_DIR, "questions")
QUESTION_PAPERS_DIR = os.path.join(BASE_DIR, "question-papers")

DATABASE_URL = os.getenv("DATABASE_URL")


# =============================================================================
# DATABASE
# =============================================================================

def connect_db():
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print("DB error:", e)
        return None


# =============================================================================
# QUESTION PAPERS – LOADER & CACHE
# =============================================================================

@lru_cache(maxsize=1)
def load_question_papers():
    """
    Loads and indexes all question-papers/*.json once.
    Returns:
    {
      "branches": [...],
      "subjects_index": {subject_link: [pdfs]},
      "search_index": [...]
    }
    """
    branches = []
    subjects_index = {}
    search_index = []

    for file_path in glob.glob(os.path.join(QUESTION_PAPERS_DIR, "*.json")):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        branch_name = data.get("branch_name")
        branch_code = data.get("branch_code")

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
                subjects.append({
                    "subject_name": subject.get("subject_name"),
                    "subject_link": subject_link
                })

                subjects_index.setdefault(subject_link, []).extend(
                    subject.get("pdf_links", [])
                )

                search_index.append({
                    "branch_name": branch_name,
                    "branch_code": branch_code,
                    "semester": sem_no,
                    "subject_name": subject.get("subject_name"),
                    "subject_link": subject_link
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


# =============================================================================
# QUESTION PAPERS ROUTES
# =============================================================================

@app.route("/question-papers")
def select_page():
    qp = load_question_papers()
    organized_data = {}

    for branch in qp["branches"]:
        organized_data[branch["branch_name"]] = branch["semesters"]

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
        "description": f"Download {subject_display} SPPU question papers.",
        "keywords": f"{subject_display}, sppu, question papers",
        "subject_name": subject_display  # Add this line
    }

    return render_template(
        "viewer.html",
        subject_name=subject_display,
        pdf_data_for_js=pdf_data,
        seo_data=seo_data
    )


# =============================================================================
# SEARCH API (FAST)
# =============================================================================

@app.route("/api/question-papers/search")
def question_papers_search():
    qp = load_question_papers()
    return jsonify(qp["search_index"])


@app.route("/api/subjects/search")
def subjects_search():
    subjects = []
    for file_path in glob.glob(os.path.join(QUESTIONS_DIR, "*.json")):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            default = data.get("default", {})
            subjects.append({
                "subject_code": default.get("subject_code"),
                "subject_name": default.get("subject_name"),
                "url": default.get("url")
            })
        except Exception as e:
            continue
    return jsonify(subjects)


# =============================================================================
# EXISTING SUBJECT / QUESTION ROUTES (UNCHANGED)
# =============================================================================

@app.route("/<subject_code>")
@app.route("/<subject_code>/<question_id>")
def question(subject_code, question_id=None):
    json_path = os.path.join(QUESTIONS_DIR, f"{subject_code}.json")
    if not os.path.exists(json_path):
        abort(404)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    subject = data.get("default", {})
    questions = data.get("questions", [])

    question_map = {q["id"]: q for q in questions}
    selected = question_map.get(question_id)

    title = subject.get("subject_name", subject_code)
    description = subject.get("description", "")

    groups = {}
    for q in questions:
        groups.setdefault(q["group"], []).append(q)

    return render_template(
        "subject.html",
        title=title,
        description=description,
        subject_code=subject_code,
        subject_name=subject.get("subject_name"),
        groups=groups,
        sorted_groups=sorted(groups),
        question=selected
    )


# =============================================================================
# STATIC & SEO FILES
# =============================================================================

@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory(".", "sitemap.xml")


@app.route("/robots.txt")
def robots():
    return send_from_directory(".", "robots.txt")


# =============================================================================
# ERRORS
# =============================================================================

@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", error_code=404), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", error_code=500), 500


# =============================================================================
# ANALYTICS INJECTION
# =============================================================================

@app.after_request
def inject_analytics(response):
    if response.content_type.startswith("text/html"):
        snippet = """
        <script defer src="https://cloud.umami.is/script.js"
        data-website-id="52ac9be0-a82e-4e1b-a1eb-38a1036db726"></script>
        """
        try:
            response.set_data(
                response.get_data().replace(b"</body>", snippet.encode() + b"</body>")
            )
        except Exception:
            pass
    return response


# =============================================================================
# ENTRY
# =============================================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
