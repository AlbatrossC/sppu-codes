import glob
import json
import os
from functools import lru_cache

from .config import QP_PDF_DIR, QP_SEO_DIR


def _extract_semesters_from_data(data):
    if "sems" in data and isinstance(data["sems"], dict):
        return data["sems"]
    return {
        key: value
        for key, value in data.items()
        if key.startswith("sem-") and isinstance(value, dict)
    }


def _load_seo_index():
    seo_index = {}
    branch_meta = {}

    if not os.path.exists(QP_SEO_DIR):
        return seo_index, branch_meta

    for file_path in glob.glob(os.path.join(QP_SEO_DIR, "*.json")):
        branch_code = os.path.splitext(os.path.basename(file_path))[0]
        try:
            with open(file_path, "r", encoding="utf-8") as file_obj:
                data = json.load(file_obj)
        except Exception:
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
        try:
            with open(file_path, "r", encoding="utf-8") as file_obj:
                data = json.load(file_obj)
        except Exception:
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
                subject_obj = {
                    "subject_name": subject_name,
                    "seo_data": seo_data,
                    "pdf_links": subject.get("pdf_links", []),
                    "branch_name": branch_name,
                    "branch_code": branch_code,
                    "semester": sem_no,
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
