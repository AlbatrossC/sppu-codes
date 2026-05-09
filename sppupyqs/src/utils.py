import glob
import json
import os
from functools import lru_cache
from urllib.parse import urlparse

from .config import QP_METADATA_DIR, QP_PDF_DIR, QP_SEO_DIR


def _extract_semesters_from_data(data):
    if "sems" in data and isinstance(data["sems"], dict):
        return data["sems"]
    return {
        key: value
        for key, value in data.items()
        if key.startswith("sem-") and isinstance(value, dict)
    }


def _safe_load_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file_obj:
            return json.load(file_obj)
    except Exception:
        return None


def _derive_exam_type_from_url(pdf_url):
    lowered = (pdf_url or "").lower()
    if "insem" in lowered:
        return "insem"
    if "endsem" in lowered:
        return "endsem"
    return "unknown"


def _format_paper_label_from_url(pdf_url):
    filename = os.path.basename(urlparse(pdf_url).path or "")
    stem = os.path.splitext(filename)[0]
    if not stem:
        return "Paper"

    parts = stem.split("-")
    months = []
    month_tokens = {
        "jan", "january", "feb", "february", "mar", "march", "apr", "april",
        "may", "jun", "june", "jul", "july", "aug", "august", "sep", "sept",
        "september", "oct", "october", "nov", "november", "dec", "december",
    }
    year = next((part for part in parts if part.isdigit() and len(part) == 4), "")

    for part in parts:
        token = part.lower()
        if token in month_tokens:
            months.append(part.capitalize())

    exam_type = _derive_exam_type_from_url(pdf_url)
    exam_label = "Insem" if exam_type == "insem" else "Endsem" if exam_type == "endsem" else "Paper"

    label_parts = []
    if year:
        label_parts.append(year)
    if months:
        label_parts.append(" ".join(months))
    label_parts.append(exam_label)
    return " ".join(part for part in label_parts if part).strip() or stem


def _normalize_questions(questions):
    normalized = []
    for question in questions or []:
        if not isinstance(question, dict):
            continue
        normalized.append({
            "question_number": str(question.get("question_number") or "").strip(),
            "subquestion": str(question.get("subquestion") or "").strip(),
            "question_text": str(question.get("question_text") or "").strip(),
            "marks": question.get("marks"),
            "question_id": str(question.get("question_id") or "").strip(),
        })
    return normalized


def _build_subject_papers(branch_code, sem_key, subject_link, pdf_links):
    papers_by_url = {}
    ordered_urls = []

    for pdf_url in pdf_links or []:
        if not isinstance(pdf_url, str) or not pdf_url.strip():
            continue
        cleaned_url = pdf_url.strip()
        filename = os.path.basename(urlparse(cleaned_url).path)
        papers_by_url[cleaned_url] = {
            "pdf_id": os.path.splitext(filename)[0],
            "pdf_url": cleaned_url,
            "filename": filename,
            "paper_label": _format_paper_label_from_url(cleaned_url),
            "exam_type": _derive_exam_type_from_url(cleaned_url),
            "metadata": {},
            "questions": [],
            "question_count": 0,
            "has_structured_content": False,
        }
        ordered_urls.append(cleaned_url)

    metadata_path = os.path.join(QP_METADATA_DIR, branch_code, sem_key, f"{subject_link}.json")
    metadata_subject = _safe_load_json(metadata_path) or {}
    metadata_papers = metadata_subject.get("papers") if isinstance(metadata_subject, dict) else []

    if isinstance(metadata_papers, list):
        for metadata_paper in metadata_papers:
            if not isinstance(metadata_paper, dict):
                continue
            pdf_url = str(metadata_paper.get("pdf_url") or "").strip()
            if not pdf_url:
                continue

            filename = os.path.basename(urlparse(pdf_url).path)
            paper_entry = papers_by_url.get(pdf_url)
            if not paper_entry:
                paper_entry = {
                    "pdf_id": str(metadata_paper.get("pdf_id") or os.path.splitext(filename)[0]).strip(),
                    "pdf_url": pdf_url,
                    "filename": filename,
                    "paper_label": _format_paper_label_from_url(pdf_url),
                    "exam_type": _derive_exam_type_from_url(pdf_url),
                    "metadata": {},
                    "questions": [],
                    "question_count": 0,
                    "has_structured_content": False,
                }
                papers_by_url[pdf_url] = paper_entry
                ordered_urls.append(pdf_url)

            questions = _normalize_questions(metadata_paper.get("questions") or [])
            paper_entry.update({
                "pdf_id": str(metadata_paper.get("pdf_id") or paper_entry["pdf_id"]).strip() or paper_entry["pdf_id"],
                "metadata": metadata_paper.get("metadata") or {},
                "questions": questions,
                "question_count": len(questions),
                "has_structured_content": bool(questions or metadata_paper.get("metadata")),
                "extraction_info": metadata_paper.get("extraction_info") or {},
            })

    return [papers_by_url[url] for url in ordered_urls if url in papers_by_url]


def _load_seo_index():
    seo_index = {}
    branch_meta = {}

    if not os.path.exists(QP_SEO_DIR):
        return seo_index, branch_meta

    for file_path in glob.glob(os.path.join(QP_SEO_DIR, "*.json")):
        branch_code = os.path.splitext(os.path.basename(file_path))[0]
        data = _safe_load_json(file_path)
        if not data:
            continue

        branch_meta[branch_code] = {
            "branch_name": data.get("branch_name") or branch_code,
            "branch_code": data.get("branch_code") or branch_code,
        }

        sems = _extract_semesters_from_data(data)
        for _sem_key, subjects in sems.items():
            if not isinstance(subjects, dict):
                continue
            for subject_link, subject in subjects.items():
                if isinstance(subject, dict) and "seo_data" in subject:
                    seo_index[subject_link] = subject["seo_data"]

    return seo_index, branch_meta


@lru_cache(maxsize=1)
def load_question_papers():
    branches = []
    papers_list = []
    subjects_index = {}

    if not os.path.exists(QP_PDF_DIR):
        return {"branches": [], "question_papers_list": [], "subjects_index": {}}

    seo_index, branch_meta = _load_seo_index()

    for file_path in glob.glob(os.path.join(QP_PDF_DIR, "*.json")):
        branch_code = os.path.splitext(os.path.basename(file_path))[0]
        data = _safe_load_json(file_path)
        if not data:
            continue

        branch_name = data.get("branch_name") or branch_meta.get(branch_code, {}).get("branch_name") or branch_code
        branch_entry = {"branch_name": branch_name, "branch_code": branch_code, "semesters": {}}
        sems = _extract_semesters_from_data(data)

        for sem_key, subjects in sems.items():
            if not isinstance(subjects, dict):
                continue
            try:
                sem_no = int(sem_key.split("-")[-1])
            except ValueError:
                continue

            subjects_for_sem = []
            for subject_link, subject in subjects.items():
                if not isinstance(subject, dict):
                    continue

                subject_name = subject.get("subject_name", subject_link)
                seo_data = seo_index.get(subject_link) or subject.get("seo_data") or {}
                subject_papers = _build_subject_papers(branch_code, sem_key, subject_link, subject.get("pdf_links", []))
                subject_obj = {
                    "subject_name": subject_name,
                    "seo_data": seo_data,
                    "pdf_links": subject.get("pdf_links", []),
                    "papers": subject_papers,
                    "branch_name": branch_name,
                    "branch_code": branch_code,
                    "semester": sem_no,
                    "semester_key": sem_key,
                    "subject_link": subject_link,
                }
                subjects_index[subject_link] = subject_obj
                subjects_for_sem.append({"subject_name": subject_name, "subject_link": subject_link})
                papers_list.append({
                    "type": "QUESTION_PAPER",
                    "subject_name": subject_name,
                    "subject_link": subject_link,
                    "branch_name": branch_name,
                    "branch_code": branch_code,
                    "semester": sem_no,
                    "public_url": f"/{subject_link}",
                    "repo_path": f"{branch_code}/sem-{sem_no}/{subject_link}",
                })

            branch_entry["semesters"][f"Semester {sem_no}"] = subjects_for_sem
        branches.append(branch_entry)

    return {
        "branches": branches,
        "question_papers_list": papers_list,
        "subjects_index": subjects_index,
    }
