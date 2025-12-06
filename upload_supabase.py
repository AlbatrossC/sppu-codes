import os
import json
import boto3
from dotenv import load_dotenv

load_dotenv()

# Load Supabase S3 credentials
S3_ENDPOINT = os.getenv("SUPABASE_S3_ENDPOINT")
BUCKET_NAME = os.getenv("SUPABASE_S3_BUCKET")
ACCESS_KEY = os.getenv("SUPABASE_S3_ACCESS_KEY")
SECRET_KEY = os.getenv("SUPABASE_S3_SECRET_KEY")

# Supabase public URL base
PROJECT_ID = os.getenv("SUPABASE_PROJECT_ID")  # Must exist in .env
PUBLIC_BASE = f"https://{PROJECT_ID}.supabase.co/storage/v1/object/public/{BUCKET_NAME}"

# Initialize S3 client for uploading ONLY
s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)

# Output JSON file
OUTPUT_JSON = "questionpapers.json"

# Load JSON or create new
if os.path.exists(OUTPUT_JSON):
    with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
        questionpapers = json.load(f)
else:
    questionpapers = {}

# 🔥 Multiple root folders allowed
ROOT_FOLDERS = ["fy", "aids", "cse"]


def build_public_url(remote_path: str) -> str:
    """Return the correct public Supabase URL."""
    return f"{PUBLIC_BASE}/{remote_path}"


def upload_file(local_path, remote_path):
    """Upload a PDF with correct MIME type + caching."""
    try:
        s3.upload_file(
            Filename=local_path,
            Bucket=BUCKET_NAME,
            Key=remote_path,
            ExtraArgs={
                "ContentType": "application/pdf",
                "CacheControl": "public, max-age=31536000"  # 1-year CDN caching
            }
        )
        return build_public_url(remote_path)

    except Exception as e:
        print(f"❌ Upload failed for {local_path}: {e}")
        return None


for ROOT_DIR in ROOT_FOLDERS:
    if not os.path.exists(ROOT_DIR):
        print(f"⚠️ Skipping missing folder: {ROOT_DIR}")
        continue

    mainfolder = os.path.basename(ROOT_DIR)
    questionpapers.setdefault(mainfolder, {})

    for root, _, files in os.walk(ROOT_DIR):
        for file in files:

            if not file.lower().endswith(".pdf"):
                continue

            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, ROOT_DIR).replace("\\", "/")

            parts = relative_path.split("/")
            if len(parts) < 3:
                print(f"[Skipped] Invalid folder structure → {relative_path}")
                continue

            branch, subject = parts[0], parts[1]

            questionpapers[mainfolder].setdefault(branch, {})
            questionpapers[mainfolder][branch].setdefault(subject, [])

            # Avoid duplicate uploads
            existing_files = {os.path.basename(url) for url in questionpapers[mainfolder][branch][subject]}
            if file in existing_files:
                print(f"[Skipped] Already uploaded → {file}")
                continue

            # Remote path = same folder structure
            remote_path = f"{mainfolder}/{relative_path}"

            uploaded_url = upload_file(local_path, remote_path)
            if uploaded_url:
                questionpapers[mainfolder][branch][subject].append(uploaded_url)
                print(f"[Uploaded] {file} → {uploaded_url}")

# Save JSON
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(questionpapers, f, indent=4)

print("\n✅ Upload complete!")
print("📄 JSON saved → questionpapers.json")
