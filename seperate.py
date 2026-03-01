import json
import os

# Config
INPUT_DIR = r"D:\sppu-codes\question-papers"
SEO_DIR = r"D:\sppu-codes\pyqs-seo"

os.makedirs(SEO_DIR, exist_ok=True)

branch_files = ["aids.json", "cse.json", "fy.json", "it.json"]

for filename in branch_files:
    input_path = os.path.join(INPUT_DIR, filename)
    branch_key = os.path.splitext(filename)[0]  # e.g. "fy", "cse"

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    branch_name = data.get("branch_name", "")
    branch_code = data.get("branch_code", "")

    seo_output = {
        "branch_name": branch_name,
        "branch_code": branch_code,
        "sems": {}
    }

    qp_output = {
        "branch_name": branch_name,
        "branch_code": branch_code,
        "sems": {}
    }

    for key, value in data.items():
        if not key.startswith("sem-"):
            continue

        sem = key  # e.g. "sem-1"
        seo_output["sems"][sem] = {}
        qp_output["sems"][sem] = {}

        for subject_id, subject_data in value.items():
            subject_name = subject_data.get("subject_name", "")
            seo_data = subject_data.get("seo_data", {})
            pdf_links = subject_data.get("pdf_links", [])

            # SEO file: branch_name, branch_code, sems, subject_name, seo_data
            seo_output["sems"][sem][subject_id] = {
                "subject_name": subject_name,
                "seo_data": seo_data
            }

            # Question-papers file: branch_name, subject_name as identifier, pdf_links
            qp_output["sems"][sem][subject_id] = {
                "subject_name": subject_name,
                "pdf_links": pdf_links
            }

    # Write SEO file
    seo_path = os.path.join(SEO_DIR, filename)
    with open(seo_path, "w", encoding="utf-8") as f:
        json.dump(seo_output, f, indent=4, ensure_ascii=False)
    print(f"✅ SEO written: {seo_path}")

    # Overwrite original question-papers file
    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(qp_output, f, indent=4, ensure_ascii=False)
    print(f"✅ QP updated: {input_path}")

print("\nDone! SEO files in:", SEO_DIR)