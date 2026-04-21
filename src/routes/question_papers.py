from flask import Blueprint, render_template, abort
from urllib.parse import urlparse
import html as _html
import os
from ..utils import load_question_papers

question_papers_bp = Blueprint('question_papers', __name__)

@question_papers_bp.route("/question-papers")
def select_page():
    qp = load_question_papers()
    organized_data = {
        branch["branch_name"]: branch["semesters"]
        for branch in qp["branches"]
    }
    return render_template("select.html", organized_data=organized_data)

@question_papers_bp.route("/question-papers/<subject_link>")
def viewer_page(subject_link):
    qp = load_question_papers()
    subject = qp["subjects_index"].get(subject_link)

    if not subject:
        abort(404)

    subject_name = subject.get("subject_name", subject_link)
    branch_name = subject.get("branch_name", "").strip() or "Engineering"

    raw_seo = subject.get("seo_data") or {}

    fallback_title = f"SPPU {subject_name} | {branch_name} Engineering Question Papers | SPPU Codes"
    seo_data = {
        "title":       _html.unescape(raw_seo.get("title")       or fallback_title),
        "description": _html.unescape(raw_seo.get("description") or (
            f"{subject_name} question papers for {branch_name} students of Savitribai Phule Pune University."
        )),
        "keywords":    _html.unescape(raw_seo.get("keywords")    or (
            f"{subject_name}, {branch_name}, SPPU question papers"
        ))
    }

    pdf_data = [
        {
            "filename": os.path.basename(urlparse(u).path),
            "url": u
        }
        for u in subject.get("pdf_links", [])
        if isinstance(u, str)
    ]

    return render_template(
        "viewer.html",
        subject_name=subject_name,
        subject_link=subject_link,
        pdf_data_for_js=pdf_data,
        seo_data=seo_data
    )
