import os
import shutil

IGNORE_FOLDERS = {".git", ".github", ".vscode", "__pycache__"}

def folder_has_pdf(folder_path):
    """Return True if any PDF exists anywhere inside this folder."""
    for root, _, files in os.walk(folder_path):
        # Skip scanning .git internal folders
        if ".git" in root:
            continue

        for f in files:
            if f.lower().endswith(".pdf"):
                return True
    return False


def remove_empty_subject_folders(root_dir):
    """
    Removes subject folders ONLY inside branch/sem/subject levels.
    Ignores .git and hidden folders.
    """
    print("\n🔍 Checking for subject folders without PDFs...\n")

    removed = 0
    kept = 0

    for branch in os.listdir(root_dir):
        if branch in IGNORE_FOLDERS or branch.startswith("."):
            continue

        branch_path = os.path.join(root_dir, branch)
        if not os.path.isdir(branch_path):
            continue

        for sem in os.listdir(branch_path):
            if sem in IGNORE_FOLDERS or sem.startswith("."):
                continue

            sem_path = os.path.join(branch_path, sem)
            if not os.path.isdir(sem_path):
                continue

            for subject in os.listdir(sem_path):
                if subject in IGNORE_FOLDERS or subject.startswith("."):
                    continue

                subject_path = os.path.join(sem_path, subject)
                if not os.path.isdir(subject_path):
                    continue

                # ---------- CHECK FOR PDF ----------
                if folder_has_pdf(subject_path):
                    print(f"✓ Keeping (has PDFs): {subject_path}")
                    kept += 1
                else:
                    print(f"🗑️ Removing (no PDFs): {subject_path}")
                    try:
                        shutil.rmtree(subject_path)
                        removed += 1
                    except PermissionError:
                        print(f"❌ Permission denied, skipping: {subject_path}")
                    except Exception as e:
                        print(f"❌ Error deleting {subject_path}: {e}")

    print("\n📊 SUMMARY")
    print(f"  • Removed subject folders: {removed}")
    print(f"  • Kept subject folders   : {kept}")
    print("\n✅ Done.\n")


if __name__ == "__main__":
    root_directory = "."
    remove_empty_subject_folders(root_directory)
