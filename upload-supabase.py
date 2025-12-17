import os
import json
import boto3
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

# =========================
# Supabase S3 Credentials
# =========================
S3_ENDPOINT = os.getenv("SUPABASE_S3_ENDPOINT")
BUCKET_NAME = os.getenv("SUPABASE_S3_BUCKET")
ACCESS_KEY = os.getenv("SUPABASE_S3_ACCESS_KEY")
SECRET_KEY = os.getenv("SUPABASE_S3_SECRET_KEY")
PROJECT_ID = os.getenv("SUPABASE_PROJECT_ID")

PUBLIC_BASE = f"https://{PROJECT_ID}.supabase.co/storage/v1/object/public/{BUCKET_NAME}"

# =========================
# Init S3 Client
# =========================
s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)

# =========================
# Helpers
# =========================
ROMAN_MAP = {
    "i": "I",
    "ii": "II",
    "iii": "III",
    "iv": "IV",
    "v": "V"
}


def build_public_url(remote_path: str) -> str:
    return f"{PUBLIC_BASE}/{remote_path}"


def upload_file(local_path: str, remote_path: str) -> str | None:
    try:
        s3.upload_file(
            Filename=local_path,
            Bucket=BUCKET_NAME,
            Key=remote_path,
            ExtraArgs={
                "ContentType": "application/pdf",
                "CacheControl": "public, max-age=31536000",
            },
        )
        return build_public_url(remote_path)
    except Exception as e:
        print(f"❌ Upload failed → {local_path}: {e}")
        return None


def subject_link_to_name(subject_link: str) -> str:
    parts = subject_link.split("-")
    words = []

    for p in parts:
        pl = p.lower()
        if pl in ROMAN_MAP:
            words.append(ROMAN_MAP[pl])
        elif pl in ["fy", "cse", "aids", "it", "entc"]:
            continue
        else:
            words.append(p.capitalize())

    return " ".join(words)


def filename_from_url(url: str) -> str:
    return os.path.basename(urlparse(url).path)


def reorder_branch_data(branch_data: dict) -> dict:
    """
    Ensures branch_name and branch_code are the first keys (in that order).
    """
    ordered = {
        "branch_name": branch_data.get("branch_name"),
        "branch_code": branch_data.get("branch_code"),
    }

    for key in branch_data:
        if key not in ("branch_name", "branch_code"):
            ordered[key] = branch_data[key]

    return ordered


# =========================
# User Input
# =========================
branches_input = input(
    "Enter folders to process (comma separated, e.g. fy, aids, cse).\n"
    "For single branch, enter only one name: "
)

BRANCHES = [b.strip() for b in branches_input.split(",") if b.strip()]

# =========================
# Output Folder
# =========================
OUTPUT_DIR = "question-papers-supabase"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================
# Process Each Branch
# =========================
for BRANCH in BRANCHES:
    if not os.path.exists(BRANCH):
        print(f"⚠️ Skipping missing folder: {BRANCH}")
        continue

    output_json_path = os.path.join(OUTPUT_DIR, f"{BRANCH}.json")

    # =========================
    # Load existing JSON (if any)
    # =========================
    if os.path.exists(output_json_path):
        with open(output_json_path, "r", encoding="utf-8") as f:
            branch_data = json.load(f)
    else:
        branch_data = {}

    # =========================
    # Ensure branch_name & branch_code exist
    # =========================
    if "branch_name" not in branch_data:
        branch_data["branch_name"] = None

    if "branch_code" not in branch_data:
        branch_data["branch_code"] = None

    print(f"\n🚀 Processing branch: {BRANCH}")

    for sem in sorted(os.listdir(BRANCH)):
        sem_path = os.path.join(BRANCH, sem)

        if not os.path.isdir(sem_path):
            continue

        branch_data.setdefault(sem, {})

        for subject_link in os.listdir(sem_path):
            subject_path = os.path.join(sem_path, subject_link)

            if not os.path.isdir(subject_path):
                continue

            subject_entry = branch_data[sem].get(subject_link)

            if not subject_entry:
                subject_entry = {
                    "subject_name": subject_link_to_name(subject_link),
                    "seo_data": {
                        "title": None,
                        "description": None,
                        "keywords": None
                    },
                    "pdf_links": []
                }

            existing_files = {
                filename_from_url(url)
                for url in subject_entry.get("pdf_links", [])
                if isinstance(url, str)
            }

            for file in sorted(os.listdir(subject_path)):
                if not file.lower().endswith(".pdf"):
                    continue

                if file in existing_files:
                    print(f"[Skipped] Already uploaded → {file}")
                    continue

                local_path = os.path.join(subject_path, file)
                remote_path = f"{BRANCH}/{sem}/{subject_link}/{file}"

                uploaded_url = upload_file(local_path, remote_path)
                if uploaded_url:
                    subject_entry["pdf_links"].append(uploaded_url)
                    print(f"[Uploaded] {file}")

            if subject_entry["pdf_links"]:
                branch_data[sem][subject_link] = subject_entry

    # =========================
    # Reorder & Save JSON
    # =========================
    branch_data = reorder_branch_data(branch_data)

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(branch_data, f, indent=4)

    print(f"📄 JSON updated → {output_json_path}")

print("\n✅ Supabase incremental upload completed!")
