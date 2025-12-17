import os

ROOT = r"D:\Sppu-questionpapers"

print("Scanning folders...\n")

for branch in os.listdir(ROOT):
    branch_path = os.path.join(ROOT, branch)

    # Only process directories (skip files)
    if not os.path.isdir(branch_path):
        continue

    print(f"📁 Branch: {branch}")

    # Traverse sem folders
    for item in os.listdir(branch_path):
        if item.startswith("sem-") and os.path.isdir(os.path.join(branch_path, item)):
            sem_path = os.path.join(branch_path, item)
            print(f"  ├── Semester: {item}")

            # List all folders inside sem-n
            subfolders = [
                f for f in os.listdir(sem_path)
                if os.path.isdir(os.path.join(sem_path, f))
            ]

            if subfolders:
                for sub in subfolders:
                    print(f"      • {sub}")
            else:
                print("      (No folders found)")

    print()
