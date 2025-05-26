# This script is to upload the question papers pdfs files in bulk to cloudinary. before running make sure files are in a folder name 'pyqs' -> branch name -> semester number -> subjects -> pdfs.



import os
import json
import cloudinary
import cloudinary.uploader
from pathlib import Path
from colorama import init, Fore, Style
from dotenv import load_dotenv

# Initialize colorama and load .env
init(autoreset=True)
load_dotenv()

# --- Cloudinary Config from .env ---
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

# --- Configuration ---
BASE_FOLDER = 'pyqs'  # Local folder
CLOUD_FOLDER = 'pyqs'  # Cloudinary base folder
JSON_FILE = os.path.join('static', 'pyqs', 'questionpapers.json')

def ensure_output_dir(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)

def load_json_index(json_path):
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            return json.load(f)
    return {}

def save_json_index(json_path, data):
    ensure_output_dir(json_path)
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=4)

def sanitize_public_id(path):
    return path.replace(" ", "_").replace("\\", "/").replace("//", "/")

def upload_file_if_needed(file_path, relative_path, index, branch, sem, subject):
    file_name = os.path.basename(file_path)

    if file_name in index.get(branch, {}).get(sem, {}).get(subject, {}):
        print(Fore.YELLOW + f"⏭️  Skipping (already uploaded): {file_path}")
        return

    try:
        public_id = sanitize_public_id(f"{CLOUD_FOLDER}/{relative_path}/{Path(file_path).stem}")

        print(Fore.CYAN + f"⬆️  Uploading: {file_path}")
        result = cloudinary.uploader.upload(
            file_path,
            resource_type='raw',
            public_id=public_id,
            use_filename=True,
            unique_filename=True,
            overwrite=False
        )
        url = result['secure_url']
        print(Fore.GREEN + f"✅ Uploaded: {file_name} → {url}")

        index.setdefault(branch, {}).setdefault(sem, {}).setdefault(subject, {})[file_name] = url

    except Exception as e:
        print(Fore.RED + f"❌ Error uploading {file_path}: {e}")

def walk_and_upload(base_dir, cloud_folder, index):
    for branch in os.listdir(base_dir):
        branch_path = os.path.join(base_dir, branch)
        if not os.path.isdir(branch_path): continue

        for sem in os.listdir(branch_path):
            sem_path = os.path.join(branch_path, sem)
            if not os.path.isdir(sem_path): continue

            for subject in os.listdir(sem_path):
                subject_path = os.path.join(sem_path, subject)
                if not os.path.isdir(subject_path): continue

                for file in os.listdir(subject_path):
                    if not file.lower().endswith('.pdf'):
                        continue
                    file_path = os.path.join(subject_path, file)
                    relative_path = f"{branch}/{sem}/{subject}"
                    upload_file_if_needed(file_path, relative_path, index, branch, sem, subject)

def main():
    print(Fore.BLUE + Style.BRIGHT + "🚀 Starting upload process...\n")

    index = load_json_index(JSON_FILE)
    walk_and_upload(BASE_FOLDER, CLOUD_FOLDER, index)
    save_json_index(JSON_FILE, index)

    print(Fore.GREEN + Style.BRIGHT + f"\n✅ All uploads complete. JSON index saved to: {JSON_FILE}")

if __name__ == '__main__':
    main()
