"""
Generate static/search.1.json from pyqs-seo JSON files.
Run: python generate_search.py

Output: static/search.1.json
Each entry: branch_name, branch_code, sem_no, subject_name, subject_link, keywords
"""

import json
import os

SEARCH_VERSION = 1
SEO_DIR = os.path.join("question-papers", "pyqs-seo")
OUTPUT_FILE = os.path.join("static", f"search.{SEARCH_VERSION}.json")


def extract_sems(data):
    if "sems" in data and isinstance(data["sems"], dict):
        return data["sems"]
    return {
        key: value
        for key, value in data.items()
        if key.startswith("sem-") and isinstance(value, dict)
    }


def generate():
    if not os.path.exists(SEO_DIR):
        print(f"ERROR: Directory not found: {SEO_DIR}")
        return

    entries = []

    for filename in sorted(os.listdir(SEO_DIR)):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(SEO_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        branch_name = data.get("branch_name", "")
        branch_code = data.get("branch_code", "")

        sems = extract_sems(data)
        for sem_key, subjects in sems.items():
            try:
                sem_no = int(sem_key.split("-")[-1])
            except ValueError:
                continue

            if not isinstance(subjects, dict):
                continue

            for subject_link, subject in subjects.items():
                if not isinstance(subject, dict):
                    continue

                subject_name = subject.get("subject_name", "")
                seo_data = subject.get("seo_data", {})
                keywords = seo_data.get("keywords", "")

                abbreviation = "".join(
                    word[0] for word in subject_name.split() if word
                ).lower()

                entries.append({
                    "branch_name": branch_name,
                    "branch_code": branch_code,
                    "sem_no": sem_no,
                    "subject_name": subject_name,
                    "subject_link": subject_link,
                    "keywords": keywords,
                    "abbreviation": abbreviation,
                })

    # Write output
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, separators=(",", ":"))

    print(f"Generated {OUTPUT_FILE} with {len(entries)} entries")


if __name__ == "__main__":
    generate()
