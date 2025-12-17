import cloudinary
import cloudinary.api
from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()

CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
API_KEY = os.getenv("CLOUDINARY_API_KEY")
API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

cloudinary.config(
    cloud_name=CLOUD_NAME,
    api_key=API_KEY,
    api_secret=API_SECRET
)

def delete_all_resources():
    # Delete all types: images, videos, raw
    resource_types = ["image", "video", "raw"]

    for r_type in resource_types:
        print(f"Deleting all {r_type} files...")

        # Delete ALL resources (including derived)
        cloudinary.api.delete_all_resources(
            resource_type=r_type,
            type="upload",
            keep_original=False,   # delete transformed images too
            invalidate=True        # purge CDN
        )

def delete_all_folders():
    print("Deleting all empty folders...")

    # List all root folders
    try:
        folders = cloudinary.api.root_folders()["folders"]
    except Exception:
        folders = []

    for folder in folders:
        name = folder["name"]
        print(f"Attempting to delete folder: {name}")

        try:
            cloudinary.api.delete_folder(name)
        except Exception:
            # Folder may not be empty (already cleared above)
            pass


if __name__ == "__main__":
    print("🚨 WARNING: This will delete EVERYTHING in your Cloudinary account!")
    print("Starting full wipe...")

    delete_all_resources()
    delete_all_folders()

    print("✔️ All Cloudinary resources deleted.")
    print("⚠️ Go to Cloudinary Dashboard → Trash → Empty Trash (required).")
    