from flask import Blueprint, jsonify, request, send_from_directory, abort, current_app, Response, stream_with_context
import os
import requests
from functools import lru_cache
from urllib.parse import urlparse
from ..config import ANSWERS_DIR, QUESTIONS_DIR, DISCORD_WEBHOOK_URL
from ..async_logger import api_logger
from ..notifications import send_discord_notification
from ..utils import (
    load_question_papers,
    load_subject_data,
    load_answer_files
)

api_bp = Blueprint('api', __name__, url_prefix='/api')


@lru_cache(maxsize=1)
def _available_subjects_text():
    output = ["No question found", "", "Available subjects:", ""]

    if os.path.exists(QUESTIONS_DIR):
        for filename in sorted(os.listdir(QUESTIONS_DIR)):
            if filename.endswith(".json"):
                code = filename[:-5]
                data = load_subject_data(code)
                full_name = data.get("default", {}).get("subject_name", code.upper()) if data else code.upper()
                output.append(f"{code} --> {full_name}")
                output.append("")

    return "\n".join(output).strip()


@lru_cache(maxsize=256)
def _cached_answer(subject_link, question_no):
    data = load_subject_data(subject_link)
    if not data:
        return None, None, 404

    question = data["_q_index"].get(str(question_no))
    if not question:
        return None, None, 404

    files = tuple(question.get("file_name", []))
    if not files:
        return question, None, 404

    contents, error = load_answer_files(subject_link, files)
    if error:
        return question, error, 404

    return question, contents, 200


def _question_not_found_text(subject_link, questions):
    output = ["No question found", "", f"Available questions for subject: {subject_link}", ""]

    for q in questions:
        q_no = q.get("question_no", "N/A")
        q_text = q.get("question", "").strip()
        output.append(f"{q_no} --> {q_text}")
        output.append("")

    return "\n".join(output).strip()


def _is_terminal_request(request):
    return len(request.args) == 0


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

    headers = {"User-Agent": "SPPU-Codes/1.0"}
    range_header = request.headers.get("Range")
    if range_header:
        headers["Range"] = range_header

    try:
        upstream = requests.get(
            pdf_url,
            timeout=30,
            stream=True,
            headers=headers,
        )
        upstream.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if upstream.status_code != 206:
            current_app.logger.warning(f"pdf_proxy fetch error for {pdf_url}: {e}")
            return jsonify({"error": "Failed to fetch PDF"}), 502
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
    response.headers["Accept-Ranges"] = "bytes"

    # Forward essential headers for byte-range requests
    for header_name in ["Content-Length", "Content-Range", "Accept-Ranges"]:
        header_val = upstream.headers.get(header_name)
        if header_val:
            response.headers[header_name] = header_val

    return response

@api_bp.route("/<subject_link>/<question_no>")
def answer_api(subject_link, question_no):
    data = load_subject_data(subject_link)

    if not data:
        return _available_subjects_text(), 404, {"Content-Type": "text/plain; charset=utf-8"}

    question = data["_q_index"].get(str(question_no))
    if not question:
        return _question_not_found_text(subject_link, data.get("questions", [])), 404, {"Content-Type": "text/plain; charset=utf-8"}

    no_question = request.args.get("no_question") == "1"
    split = request.args.get("split")
    cached_question, cached_contents, status = _cached_answer(subject_link, question_no)

    if status == 404:
        if cached_question is None:
            return _question_not_found_text(subject_link, data.get("questions", [])), 404, {"Content-Type": "text/plain; charset=utf-8"}
        if isinstance(cached_contents, str):
            return cached_contents, 404, {"Content-Type": "text/plain; charset=utf-8"}
        return "No answer files", 404, {"Content-Type": "text/plain; charset=utf-8"}

    question = cached_question
    contents = list(cached_contents)

    if split:
        try:
            index = int(split) - 1
            if index < 0 or index >= len(contents):
                return "Invalid split index", 400, {"Content-Type": "text/plain"}
            contents = [contents[index]]
        except ValueError:
            return "Invalid split parameter", 400, {"Content-Type": "text/plain"}

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

    response_text = "\n".join(output).strip()

    if _is_terminal_request(request):
        api_logger.log_api_request(
            subject_link,
            question_no,
            request.remote_addr,
            request.headers.get("User-Agent", "")
        )

    return response_text, 200, {
        "Content-Type": "text/plain; charset=utf-8",
        "Cache-Control": "public, max-age=3600"
    }

raw_api_bp = Blueprint('raw_api', __name__)

@raw_api_bp.route("/raw-answers/<subject_link>/<path:filename>")
def raw_answer_file(subject_link, filename):
    subject_dir = os.path.join(ANSWERS_DIR, subject_link)
    if not os.path.exists(os.path.join(subject_dir, filename)):
        abort(404)
    return send_from_directory(subject_dir, filename)
