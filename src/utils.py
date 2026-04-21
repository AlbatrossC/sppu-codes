import os
import json
import glob
from functools import lru_cache
from .config import QP_SEO_DIR, QP_PDF_DIR, QUESTIONS_DIR, ANSWERS_DIR

def _extract_semesters_from_data(data):
    """
    Extracts a {sem_key: subjects_dict} mapping from a branch JSON.

    Supports two layouts:
      - R2 layout:       Top-level keys like "sem-1", "sem-2", ...
      - Supabase layout: Nested under a "sems" key → { "sem-1": {...}, ... }
    """
    if "sems" in data and isinstance(data["sems"], dict):
        return data["sems"]

    return {
        key: value
        for key, value in data.items()
        if key.startswith("sem-") and isinstance(value, dict)
    }


def _load_seo_index():
    """
    Loads the SEO data from pyqs-seo/ and returns two dicts:
      seo_index    : { subject_link: { title, description, keywords } }
      branch_meta  : { branch_code: { branch_name, branch_code } }

    branch_meta is used as a fallback when the PDF source JSONs have
    null/empty branch_name fields.
    """
    seo_index = {}
    branch_meta = {}

    if not os.path.exists(QP_SEO_DIR):
        return seo_index, branch_meta

    for file_path in glob.glob(os.path.join(QP_SEO_DIR, "*.json")):
        branch_code = os.path.splitext(os.path.basename(file_path))[0]
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Warning: Could not read SEO file {file_path}: {e}")
            continue

        branch_meta[branch_code] = {
            "branch_name": data.get("branch_name") or branch_code,
            "branch_code": data.get("branch_code") or branch_code,
        }

        sems = _extract_semesters_from_data(data)
        for sem_key, subjects in sems.items():
            if not isinstance(subjects, dict):
                continue
            for subject_link, subject in subjects.items():
                if isinstance(subject, dict) and "seo_data" in subject:
                    seo_index[subject_link] = subject["seo_data"]

    return seo_index, branch_meta


@lru_cache(maxsize=1)
def load_question_papers():
    """
    Loads and caches question papers data from the active PDF source.
    """
    branches = []
    papers_list = []
    subjects_index = {}

    if not os.path.exists(QP_PDF_DIR):
        print(f"Warning: PDF source directory not found: {QP_PDF_DIR}")
        return {
            "branches": [],
            "question_papers_list": [],
            "subjects_index": {}
        }

    seo_index, branch_meta = _load_seo_index()

    for file_path in glob.glob(os.path.join(QP_PDF_DIR, "*.json")):
        branch_code = os.path.splitext(os.path.basename(file_path))[0]

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Warning: Could not read PDF source file {file_path}: {e}")
            continue

        branch_name = (
            data.get("branch_name")
            or branch_meta.get(branch_code, {}).get("branch_name")
            or branch_code
        )

        branch_entry = {
            "branch_name": branch_name,
            "branch_code": branch_code,
            "semesters": {}
        }

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

                subject_obj = {
                    "subject_name": subject_name,
                    "seo_data": seo_data,
                    "pdf_links": subject.get("pdf_links", []),
                    "branch_name": branch_name,
                    "branch_code": branch_code,
                    "semester": sem_no,
                    "subject_link": subject_link
                }

                subjects_index[subject_link] = subject_obj

                subjects_for_sem.append({
                    "subject_name": subject_name,
                    "subject_link": subject_link
                })

                papers_list.append({
                    "type": "QUESTION_PAPER",
                    "subject_name": subject_name,
                    "subject_link": subject_link,
                    "branch_name": branch_name,
                    "branch_code": branch_code,
                    "semester": sem_no,
                    "public_url": f"/question-papers/{subject_link}",
                    "repo_path": f"{branch_code}/sem-{sem_no}/{subject_link}"
                })

            branch_entry["semesters"][f"Semester {sem_no}"] = subjects_for_sem

        branches.append(branch_entry)

    return {
        "branches": branches,
        "question_papers_list": papers_list,
        "subjects_index": subjects_index
    }


def load_subject_data(subject_link):
    """Loads subject data from JSON file."""
    json_path = os.path.join(QUESTIONS_DIR, f"{subject_link}.json")
    if not os.path.exists(json_path):
        return None
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for q in data.get("questions", []):
        question_text = q.get("question")
        if isinstance(question_text, str):
            q["question"] = question_text.replace("/n", "\n")

    return data


def get_question_by_id(questions, question_id):
    """Finds a question by its ID."""
    return next((q for q in questions if q["id"] == question_id), None)


def get_question_by_number(questions, question_no):
    """Finds a question by its number."""
    return next((q for q in questions if str(q.get("question_no")) == str(question_no)), None)


def organize_questions_by_group(questions):
    """Organizes questions into groups."""
    groups = {}
    for q in questions:
        groups.setdefault(q["group"], []).append(q)
    return groups, sorted(groups.keys())


def load_answer_files(subject_link, files):
    """Loads answer files for a question."""
    subject_dir = os.path.join(ANSWERS_DIR, subject_link)
    if not os.path.exists(subject_dir):
        return None, "Answer directory missing"
    
    contents = []
    for fname in files:
        path = os.path.join(subject_dir, fname)
        if not os.path.exists(path):
            return None, f"File missing: {fname}"
        
        ext = fname.split('.')[-1].lower() if '.' in fname else ''
        if ext in ['pdf', 'jpg', 'jpeg', 'png', 'gif', 'svg', 'webp']:
            contents.append((fname, "[Binary File - Use Raw Route]"))
        else:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    contents.append((fname, f.read().strip()))
            except UnicodeDecodeError:
                contents.append((fname, "[Binary or Unsupported Text Format]"))
    
    return contents, None
