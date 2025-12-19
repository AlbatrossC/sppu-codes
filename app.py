from flask import (
    Flask, render_template, send_from_directory,
    abort, request, redirect, jsonify
)
import os
import json
from functools import lru_cache
from urllib.parse import urlparse
import glob

# =============================================================================
# APP INIT
# =============================================================================

app = Flask(__name__)
app.secret_key = "karltos"

BASE_DIR = os.path.dirname(__file__)
QUESTIONS_DIR = os.path.join(BASE_DIR, "questions")
ANSWERS_DIR = os.path.join(BASE_DIR, "answers")
QUESTION_PAPERS_DIR = os.path.join(BASE_DIR, "question-papers")

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
        if request.path.startswith("/static"):
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
                    "type": "QUESTION_PAPER",
                    "subject_name": subject.get("subject_name"),
                    "branch": branch_name,
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
    return render_template("error.html", error_code=404), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", error_code=500), 500

# =============================================================================
# ENTRY
# =============================================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
