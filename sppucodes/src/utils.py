import json
import os
from functools import lru_cache

from .config import QUESTIONS_DIR, ANSWERS_DIR


@lru_cache(maxsize=64)
def load_subject_data(subject_link):
    json_path = os.path.join(QUESTIONS_DIR, f"{subject_link}.json")
    if not os.path.exists(json_path):
        return None

    with open(json_path, "r", encoding="utf-8-sig") as file_obj:
        data = json.load(file_obj)

    questions = data.get("questions", [])
    groups = {}
    for question in questions:
        question_text = question.get("question")
        if isinstance(question_text, str):
            question["question"] = question_text.replace("/n", "\n")
        groups.setdefault(question.get("group", ""), []).append(question)

    data["processed_groups"] = groups
    data["sorted_groups"] = sorted(groups.keys())
    data["_q_index"] = {
        str(question.get("question_no")): question
        for question in questions
    }
    return data


def get_question_by_id(questions, question_id):
    return next((question for question in questions if question["id"] == question_id), None)


def get_question_by_number(questions, question_no):
    return next((question for question in questions if str(question.get("question_no")) == str(question_no)), None)


def organize_questions_by_group(questions):
    groups = {}
    for question in questions:
        groups.setdefault(question["group"], []).append(question)
    return groups, sorted(groups.keys())


@lru_cache(maxsize=256)
def _read_answer_file(filepath):
    ext = filepath.split(".")[-1].lower() if "." in filepath else ""
    if ext in ["pdf", "jpg", "jpeg", "png", "gif", "svg", "webp"]:
        return "[Binary File - Use Raw Route]"

    try:
        with open(filepath, "r", encoding="utf-8") as file_obj:
            return file_obj.read().strip()
    except UnicodeDecodeError:
        return "[Binary or Unsupported Text Format]"


@lru_cache(maxsize=256)
def load_answer_files(subject_link, files):
    subject_dir = os.path.join(ANSWERS_DIR, subject_link)
    if not os.path.exists(subject_dir):
        return None, "Answer directory missing"

    contents = []
    for filename in files:
        path = os.path.join(subject_dir, filename)
        if not os.path.exists(path):
            return None, f"File missing: {filename}"
        contents.append((filename, _read_answer_file(path)))

    return contents, None


def preload_subject_cache():
    if not os.path.exists(QUESTIONS_DIR):
        return

    for filename in os.listdir(QUESTIONS_DIR):
        if filename.endswith(".json"):
            load_subject_data(filename[:-5])
