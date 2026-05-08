from flask import Blueprint, abort, render_template

from ..utils import get_ext, get_question_by_id, load_answer_files_ssr, load_subject_data

subjects_bp = Blueprint("subjects", __name__)

_RESERVED_PATHS = {"submit", "contact", "images", "static", "api", "question-papers", "questionpapers"}


def _resolve_subject(subject_link):
    if subject_link in _RESERVED_PATHS:
        abort(404)
    data = load_subject_data(subject_link)
    if not data:
        abort(404)
    return data


@subjects_bp.route("/<subject_link>")
def subject_listing(subject_link):
    data = _resolve_subject(subject_link)
    subject = data.get("default", {})
    groups = data.get("processed_groups", {})
    sorted_groups = data.get("sorted_groups", [])
    question_prefetch_map = [str(q.get("question_no")) for q in data.get("questions", [])]

    page_title = subject.get("subject_name", subject_link.upper())
    page_description = subject.get("description", "")

    return render_template(
        "subject.html",
        title=page_title,
        description=page_description,
        keywords=subject.get("keywords", []),
        url=subject.get("url", ""),
        subject_code=subject_link,
        subject_name=subject.get("subject_name"),
        question_paper_url=subject.get("question_paper_url"),
        groups=groups,
        sorted_groups=sorted_groups,
        question_prefetch_map=question_prefetch_map,
    )


@subjects_bp.route("/<subject_link>/<question_id>")
def question_page(subject_link, question_id):
    data = _resolve_subject(subject_link)

    subject = data.get("default", {})
    questions = data.get("questions", [])
    groups = data.get("processed_groups", {})
    sorted_groups = data.get("sorted_groups", [])
    question_prefetch_map = [str(q.get("question_no")) for q in questions]

    selected_question = get_question_by_id(questions, question_id)
    if not selected_question:
        abort(404)

    question_title = selected_question.get("title")
    if not question_title:
        question_text = selected_question.get("question", "")
        question_title = (question_text[:50] + "...") if len(question_text) > 50 else question_text

    subject_name = subject.get("subject_name", subject_link.upper())
    page_title = f"{question_title} | {subject_name}"
    q_full_text = selected_question.get("question", "")
    page_description = f"Question {selected_question.get('question_no')}: {q_full_text[:160]}..."
    base_url = subject.get("url", "")
    page_url = f"{base_url}/{selected_question.get('id')}" if base_url else ""

    answer_files = load_answer_files_ssr(subject_link, selected_question.get("file_name", []))

    return render_template(
        "question.html",
        title=page_title,
        description=page_description,
        keywords=subject.get("keywords", []),
        url=page_url,
        subject_code=subject_link,
        subject_name=subject_name,
        question_paper_url=subject.get("question_paper_url"),
        groups=groups,
        sorted_groups=sorted_groups,
        question=selected_question,
        question_prefetch_map=question_prefetch_map,
        answer_files=answer_files,
        get_ext=get_ext,
    )
