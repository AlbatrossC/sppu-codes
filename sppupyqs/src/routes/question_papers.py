import html as _html
import os
from urllib.parse import urlparse

from flask import Blueprint, abort, render_template

from ..config import CODES_SITE_URL, DEFAULT_EXAM_TYPE, QUESTION_ANSWER_WORKER_URL, SITE_URL
from ..utils import load_question_papers

question_papers_bp = Blueprint("question_papers", __name__)


@question_papers_bp.route("/")
def select_page():
    qp = load_question_papers()
    organized_data = {
        branch["branch_name"]: branch["semesters"]
        for branch in qp["branches"]
    }
    return render_template(
        "select.html",
        organized_data=organized_data,
        site_url=SITE_URL,
        codes_site_url=CODES_SITE_URL,
    )


@question_papers_bp.route("/<subject_link>")
def viewer_page(subject_link):
    qp = load_question_papers()
    subject = qp["subjects_index"].get(subject_link)
    if not subject:
        abort(404)

    subject_name = subject.get("subject_name", subject_link)
    branch_name = subject.get("branch_name", "").strip() or "Engineering"
    raw_seo = subject.get("seo_data") or {}
    fallback_title = f"SPPU {subject_name} | {branch_name} Engineering Question Papers"
    seo_data = {
        "title": _html.unescape(raw_seo.get("title") or fallback_title),
        "description": _html.unescape(
            raw_seo.get("description")
            or f"{subject_name} question papers for {branch_name} students of Savitribai Phule Pune University."
        ),
        "keywords": _html.unescape(
            raw_seo.get("keywords")
            or f"{subject_name}, {branch_name}, SPPU question papers"
        ),
        "subject_name": subject_name,
    }

    subject_papers = subject.get("papers", [])
    pdf_data = [
        {
            "filename": paper.get("filename") or os.path.basename(urlparse(paper.get("pdf_url", "")).path),
            "originalFilename": paper.get("filename") or os.path.basename(urlparse(paper.get("pdf_url", "")).path),
            "url": paper.get("pdf_url"),
            "link": paper.get("pdf_url"),
            "date": paper.get("paper_label") or "Paper",
            "paperId": paper.get("pdf_id"),
            "examType": paper.get("exam_type", "unknown"),
        }
        for paper in subject_papers
        if isinstance(paper, dict) and paper.get("pdf_url")
    ]

    initial_paper = next(
        (paper for paper in subject_papers if paper.get("exam_type") == DEFAULT_EXAM_TYPE),
        subject_papers[0] if subject_papers else None,
    )

    return render_template(
        "viewer.html",
        subject_name=subject_name,
        branch_name=branch_name,
        subject_link=subject_link,
        pdf_data_for_js=pdf_data,
        subject_papers=subject_papers,
        subject_semester_key=subject.get("semester_key", ""),
        initial_questions_paper_id=(initial_paper or {}).get("pdf_id", ""),
        seo_data=seo_data,
        default_exam_type=DEFAULT_EXAM_TYPE,
        question_answer_worker_url=QUESTION_ANSWER_WORKER_URL,
        site_url=SITE_URL,
        codes_site_url=CODES_SITE_URL,
        site_name="SPPU PYQs",
    )
