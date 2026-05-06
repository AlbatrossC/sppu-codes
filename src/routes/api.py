from flask import Blueprint, jsonify, request, send_from_directory, abort, current_app, Response, stream_with_context, make_response
import os
import requests
from functools import lru_cache
from urllib.parse import urlparse
from ..config import ANSWERS_DIR, QUESTIONS_DIR
from ..async_logger import api_logger, log_paper_download_async
from ..utils import (
    load_question_papers,
    load_subject_data,
    load_answer_files
)

api_bp = Blueprint('api', __name__, url_prefix='/api')
API_CACHE_CONTROL = "public, s-maxage=3600, stale-while-revalidate=86400"
_pdf_http = requests.Session()


@api_bp.after_request
def add_api_cache_headers(response):
    response.headers["Cache-Control"] = API_CACHE_CONTROL
    return response


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


def is_terminal_request(request):
    return (
        "no_question" not in request.args and
        "split" not in request.args
    )


def _text_response(body, status_code):
    response = make_response(body, status_code)
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    return response


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
    """Receives paper download events from client and stores lightweight analytics."""
    try:
        payload = request.get_json(silent=True)
        if not payload:
            return jsonify({"error": "invalid json"}), 400

        fingerprint_id = (payload.get("fingerprint_id") or "").strip()[:255]
        subject_link = (payload.get("subject_link") or payload.get("subject") or "").strip()[:100]

        if not fingerprint_id or not subject_link:
            return jsonify({"error": "missing fingerprint_id or subject"}), 400

        log_paper_download_async(fingerprint_id, subject_link)
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
        upstream = _pdf_http.get(
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
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Accept-Ranges"] = "bytes"
    response.headers["Cache-Control"] = "public, max-age=86400, stale-while-revalidate=604800"

    # Forward essential headers for byte-range requests
    for header_name in ["Content-Length", "Content-Range", "Accept-Ranges", "ETag", "Last-Modified"]:
        header_val = upstream.headers.get(header_name)
        if header_val:
            response.headers[header_name] = header_val

    return response

@api_bp.route("/<subject_link>/<question_no>")
def answer_api(subject_link, question_no):
    terminal_request = is_terminal_request(request)
    data = load_subject_data(subject_link)

    if not data:
        if terminal_request:
            api_logger.log_api_request(subject_link, question_no, "not_found")
        return _text_response(_available_subjects_text(), 404)

    question = data["_q_index"].get(str(question_no))
    if not question:
        if terminal_request:
            api_logger.log_api_request(subject_link, question_no, "not_found")
        return _text_response(_question_not_found_text(subject_link, data.get("questions", [])), 404)

    no_question = request.args.get("no_question") == "1"
    split = request.args.get("split")
    cached_question, cached_contents, status = _cached_answer(subject_link, question_no)

    if status == 404:
        if cached_question is None:
            if terminal_request:
                api_logger.log_api_request(subject_link, question_no, "not_found")
            return _text_response(_question_not_found_text(subject_link, data.get("questions", [])), 404)
        if isinstance(cached_contents, str):
            if terminal_request:
                api_logger.log_api_request(subject_link, question_no, "not_found")
            return _text_response(cached_contents, 404)
        if terminal_request:
            api_logger.log_api_request(subject_link, question_no, "not_found")
        return _text_response("No answer files", 404)

    question = cached_question
    contents = list(cached_contents)

    if split:
        try:
            index = int(split) - 1
            if index < 0 or index >= len(contents):
                return _text_response("Invalid split index", 400)
            contents = [contents[index]]
        except ValueError:
            return _text_response("Invalid split parameter", 400)

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

    response = _text_response(response_text, 200)
    if terminal_request:
        api_logger.log_api_request(subject_link, question_no, "success")
    return response

raw_api_bp = Blueprint('raw_api', __name__)

@raw_api_bp.route("/raw-answers/<subject_link>/<path:filename>")
def raw_answer_file(subject_link, filename):
    subject_dir = os.path.join(ANSWERS_DIR, subject_link)
    if not os.path.exists(os.path.join(subject_dir, filename)):
        abort(404)
    response = send_from_directory(subject_dir, filename)
    response.headers["Cache-Control"] = "public, max-age=86400, immutable"
    return response
