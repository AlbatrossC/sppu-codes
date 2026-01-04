import os
import re

ROOT_DIR = r"D:\Sppu-questionpapers"

def normalize_subject_name(name: str) -> str:
    """
    Normalize subject folder name to match aids / cse / fy pattern
    """
    name = name.strip().lower()
    name = re.sub(r"[^\w\s-]", "", name)   # remove special characters
    name = re.sub(r"\s+", "-", name)       # spaces -> hyphen
    name = re.sub(r"-+", "-", name)        # collapse multiple hyphens
    return name

def rename_subject_folders(branch: str):
    branch_path = os.path.join(ROOT_DIR, branch)

    if not os.path.isdir(branch_path):
        print(f"\n❌ Branch folder not found: {branch_path}")
        return

    print("\n" + "=" * 60)
    print(f"📁 Selected Branch        : {branch}")
    print(f"📂 Branch Path           : {branch_path}")
    print("=" * 60)

    total_subjects = 0
    renamed = 0
    skipped_correct = 0
    skipped_conflict = 0

    for sem in sorted(os.listdir(branch_path)):
        sem_path = os.path.join(branch_path, sem)

        # Ignore non-semester folders
        if not os.path.isdir(sem_path) or not sem.startswith("sem-"):
            continue

        print(f"\n📘 Semester: {sem}")

        for folder in sorted(os.listdir(sem_path)):
            old_path = os.path.join(sem_path, folder)

            if not os.path.isdir(old_path):
                continue

            total_subjects += 1

            # Already correctly named → skip
            if folder.endswith(f"-{branch}"):
                skipped_correct += 1
                print(f"   ⏭️  SKIP (already correct): {folder}")
                continue

            base_name = normalize_subject_name(folder)
            new_name = f"{base_name}-{branch}"
            new_path = os.path.join(sem_path, new_name)

            # Name conflict → skip
            if os.path.exists(new_path):
                skipped_conflict += 1
                print(f"   ⚠️  SKIP (target exists)  : {folder}")
                continue

            os.rename(old_path, new_path)
            renamed += 1
            print(f"   ✔ RENAME: {folder} → {new_name}")

    print("\n" + "=" * 60)
    print("📊 FINAL REPORT")
    print("=" * 60)
    print(f"📁 Branch Processed           : {branch}")
    print(f"📦 Total subject folders      : {total_subjects}")
    print(f"✏️  Renamed                   : {renamed}")
    print(f"⏭️  Skipped (already correct) : {skipped_correct}")
    print(f"⚠️  Skipped (name conflict)   : {skipped_conflict}")
    print("✅ Operation completed safely.")
    print("=" * 60)

if __name__ == "__main__":
    branch_name = input("Enter branch name (e.g. aids, cse, it, fy): ").strip().lower()
    rename_subject_folders(branch_name)
