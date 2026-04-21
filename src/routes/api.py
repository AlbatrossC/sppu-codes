from flask import Blueprint, jsonify, request, send_from_directory, abort, current_app, Response, stream_with_context
import os
import requests
from urllib.parse import urlparse
from ..config import ANSWERS_DIR, QUESTIONS_DIR, DISCORD_WEBHOOK_URL
from ..notifications import send_discord_notification
from ..utils import (
    load_question_papers,
    load_subject_data,
    get_question_by_number,
    load_answer_files
)

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route("/question-papers/list")
def question_papers_list():
    return jsonify(load_question_papers()["question_papers_list"])

@api_bp.route("/subjects/search")
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

@api_bp.route("/notify-download", methods=["POST"])
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
        current_app.logger.exception("notify_download error")
        return jsonify({"error": "server error"}), 500

_ALLOWED_PDF_HOSTS = {
    "sppucodes.albatrossc.workers.dev",
    "zauiiivigqoifsvtqhnt.supabase.co",
}

@api_bp.route("/pdf-proxy")
def pdf_proxy():
    pdf_url = request.args.get("url", "").strip()
    if not pdf_url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    try:
        parsed = urlparse(pdf_url)
    except Exception:
        return jsonify({"error": "Invalid URL"}), 400

    if parsed.netloc not in _ALLOWED_PDF_HOSTS:
        return jsonify({"error": "Domain not allowed"}), 403

    if not parsed.path.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    try:
        upstream = requests.get(
            pdf_url,
            timeout=30,
            stream=True,
            headers={"User-Agent": "SPPU-Codes/1.0"},
        )
        upstream.raise_for_status()
    except requests.exceptions.RequestException as e:
        current_app.logger.warning(f"pdf_proxy fetch error for {pdf_url}: {e}")
        return jsonify({"error": "Failed to fetch PDF"}), 502

    def generate():
        for chunk in upstream.iter_content(chunk_size=8192):
            if chunk:
                yield chunk

    response = Response(
        stream_with_context(generate()),
        status=upstream.status_code,
        content_type=upstream.headers.get("Content-Type", "application/pdf"),
    )
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Cache-Control"] = "public, max-age=86400"
    response.headers["X-Content-Type-Options"] = "nosniff"

    content_length = upstream.headers.get("Content-Length")
    if content_length:
        response.headers["Content-Length"] = content_length

    return response

@api_bp.route("/<subject_link>/<question_no>")
def answer_api(subject_link, question_no):
    data = load_subject_data(subject_link)

    if not data:
        output = ["No question found", "", "Available subjects:", ""]

        if os.path.exists(QUESTIONS_DIR):
            for f in sorted(os.listdir(QUESTIONS_DIR)):
                if f.endswith(".json"):
                    code = f[:-5]
                    d = load_subject_data(code)
                    full_name = d.get("default", {}).get("subject_name", code.upper()) if d else code.upper()
                    output.append(f"{code} --> {full_name}")
                    output.append("")

        return "\n".join(output).strip(), 404, {"Content-Type": "text/plain; charset=utf-8"}

    questions = data.get("questions", [])
    question = get_question_by_number(questions, question_no)

    if not question:
        output = ["No question found", "", f"Available questions for subject: {subject_link}", ""]

        for q in questions:
            q_no = q.get("question_no", "N/A")
            q_text = q.get("question", "").strip()
            output.append(f"{q_no} --> {q_text}")
            output.append("")

        return "\n".join(output).strip(), 404, {"Content-Type": "text/plain; charset=utf-8"}

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

    return "\n".join(output).strip(), 200, {"Content-Type": "text/plain; charset=utf-8"}

raw_api_bp = Blueprint('raw_api', __name__)

@raw_api_bp.route("/raw-answers/<subject_link>/<path:filename>")
def raw_answer_file(subject_link, filename):
    subject_dir = os.path.join(ANSWERS_DIR, subject_link)
    if not os.path.exists(os.path.join(subject_dir, filename)):
        abort(404)
    return send_from_directory(subject_dir, filename)
