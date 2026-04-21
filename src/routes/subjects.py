from flask import Blueprint, render_template, abort
from ..utils import (
    load_subject_data,
    get_question_by_id,
    organize_questions_by_group
)

subjects_bp = Blueprint('subjects', __name__)

@subjects_bp.route("/<subject_link>")
@subjects_bp.route("/<subject_link>/<question_id>")
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

    page_title = subject.get("subject_name", subject_link.upper())
    page_description = subject.get("description", "")
    base_url = subject.get("url", "")
    page_url = base_url

    if selected_question:
        q_title = selected_question.get("title")
        if not q_title:
             q_text = selected_question.get("question", "")
             q_title = (q_text[:50] + '...') if len(q_text) > 50 else q_text
        
        page_title = f"{q_title} | {page_title}"
        q_full_text = selected_question.get("question", "")
        page_description = f"Question {selected_question.get('question_no')}: {q_full_text[:160]}..."

        if base_url:
            page_url = f"{base_url}/{selected_question.get('id')}"

    return render_template(
        "subject.html",
        title=page_title,
        description=page_description,
        keywords=subject.get("keywords", []),
        url=page_url,
        subject_code=subject_link,
        subject_name=subject.get("subject_name"),
        question_paper_url=subject.get("question_paper_url"),
        groups=groups,
        sorted_groups=sorted_groups,
        question=selected_question
    )
