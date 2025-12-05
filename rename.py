import os
import fitz  # PyMuPDF
import re
from collections import defaultdict

def normalize_name(name):
    # Replace underscores with hyphens, replace '@' with 'and',
    # replace spaces with hyphens, lowercase everything.
    name = name.replace('_', '-')
    name = name.replace('@', 'and')
    name = '-'.join(name.lower().split())

    # Collapse multiple hyphens (--- → -)
    name = re.sub(r'-+', '-', name)

    return name


def get_subject_acronym(subject_name):
    """
    Generate acronym from subject name.
    Special handling for electives ending with -ele-i or -ele-ii
    """
    # Check if it's an elective with roman numeral
    elective_match = re.search(r'-ele-(i{1,2})$', subject_name)
    
    if elective_match:
        # Remove the elective suffix for acronym generation
        base_subject = re.sub(r'-ele-(i{1,2})$', '', subject_name)
        elective_num = elective_match.group(1)  # 'i' or 'ii'
        
        # Generate acronym from base subject
        words = base_subject.split('-')
        acronym = ''.join(word[0] for word in words if word)
        
        # Add elective number
        return f"{acronym}-ele-{elective_num}"
    else:
        # Regular subject - just take first letter of each word
        words = subject_name.split('-')
        acronym = ''.join(word[0] for word in words if word)
        return acronym


def detect_duplicate_folders(root_dir):
    """
    Detect folders with same names across different branches/semesters.
    Returns a dict mapping folder_name -> list of (full_path, branch_name)
    """
    folder_map = defaultdict(list)
    
    # Pattern: branch/semester/subject
    for branch_name in os.listdir(root_dir):
        branch_path = os.path.join(root_dir, branch_name)
        if not os.path.isdir(branch_path):
            continue
            
        for sem_name in os.listdir(branch_path):
            sem_path = os.path.join(branch_path, sem_name)
            if not os.path.isdir(sem_path):
                continue
                
            for subject_name in os.listdir(sem_path):
                subject_path = os.path.join(sem_path, subject_name)
                if not os.path.isdir(subject_path):
                    continue
                    
                folder_map[subject_name].append((subject_path, branch_name))
    
    return folder_map


def resolve_duplicate_folders(root_dir):
    """
    Rename duplicate folder names by appending branch name.
    """
    print("\n🔍 Checking for duplicate folder names...")
    folder_map = detect_duplicate_folders(root_dir)
    
    duplicates_found = 0
    renamed_count = 0
    
    for folder_name, locations in folder_map.items():
        if len(locations) > 1:
            duplicates_found += 1
            print(f"\n⚠️  Duplicate found: '{folder_name}' exists in {len(locations)} locations")
            
            for subject_path, branch_name in locations:
                # New name: subject-branch
                new_folder_name = f"{folder_name}-{branch_name}"
                parent_dir = os.path.dirname(subject_path)
                new_path = os.path.join(parent_dir, new_folder_name)
                
                if new_path != subject_path and not os.path.exists(new_path):
                    try:
                        os.rename(subject_path, new_path)
                        print(f"   ✓ Renamed: {folder_name} → {new_folder_name} (in {branch_name})")
                        renamed_count += 1
                    except Exception as e:
                        print(f"   ✗ Error renaming {subject_path}: {e}")
                else:
                    if os.path.exists(new_path):
                        print(f"   ⊘ Skipped: {new_folder_name} already exists")
    
    if duplicates_found == 0:
        print("✓ No duplicate folder names found")
    else:
        print(f"\n📊 Resolved {renamed_count} duplicate folders out of {duplicates_found} duplicates detected")


def rename_recursively(root_dir):
    # Walk with topdown=False so we rename inner folders first
    renamed_folders = 0
    renamed_files = 0
    skipped_folders = 0
    skipped_files = 0
    
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):

        # Rename files
        for filename in filenames:
            new_name = normalize_name(filename)
            if new_name != filename:
                src = os.path.join(dirpath, filename)
                dst = os.path.join(dirpath, new_name)
                if not os.path.exists(dst):
                    os.rename(src, dst)
                    renamed_files += 1
                else:
                    skipped_files += 1

        # Rename folders
        for dirname in dirnames:
            new_name = normalize_name(dirname)
            if new_name != dirname:
                src = os.path.join(dirpath, dirname)
                dst = os.path.join(dirpath, new_name)
                if not os.path.exists(dst):
                    os.rename(src, dst)
                    renamed_folders += 1
                else:
                    skipped_folders += 1
    
    print(f"✓ Renamed {renamed_folders} folders and {renamed_files} files")
    if skipped_folders > 0 or skipped_files > 0:
        print(f"⊘ Skipped {skipped_folders} folders and {skipped_files} files (already exist)")


def extract_text_from_pdf(file_path):
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        print(f"✗ Error reading {file_path}: {e}")
        return ""


def add_subject_acronym_to_pdf(file_path):
    """
    Add subject acronym to PDF filename if not already present.
    Example: endsem-nov-dec-2024.pdf → endsem-nov-dec-2024-dbms.pdf
    """
    # Get subject folder name (parent directory)
    subject_folder = os.path.basename(os.path.dirname(file_path))
    filename = os.path.basename(file_path)
    
    # Generate acronym from subject folder name
    acronym = get_subject_acronym(subject_folder)
    
    # Check if acronym already exists in filename
    name_without_ext, ext = os.path.splitext(filename)
    
    # Check if it already ends with the acronym
    if name_without_ext.endswith(f"-{acronym}"):
        return "skipped", file_path
    
    # Add acronym before extension
    new_filename = f"{name_without_ext}-{acronym}{ext}"
    new_path = os.path.join(os.path.dirname(file_path), new_filename)
    
    if os.path.exists(new_path):
        return "skipped", file_path
    
    try:
        os.rename(file_path, new_path)
        return "renamed", new_path
    except Exception as e:
        print(f"✗ Error adding acronym to {file_path}: {e}")
        return "error", file_path


def classify_and_rename(file_path):
    text = extract_text_from_pdf(file_path)
    base_dir = os.path.dirname(file_path)
    filename = os.path.basename(file_path)

    # Normalize filename first
    norm_filename = normalize_name(filename)

    # Avoid double prefixing
    if norm_filename.startswith(("endsem-", "insem-", "other-")):
        return "skipped", file_path

    text_lower = text.lower()

    if "max. marks : 70" in text_lower:
        prefix = "endsem-"
    elif "max. marks : 30" in text_lower:
        prefix = "insem-"
    else:
        prefix = "other-"

    new_filename = prefix + norm_filename
    new_path = os.path.join(base_dir, new_filename)

    if new_path == file_path:
        return "skipped", file_path

    if os.path.exists(new_path):
        return "skipped", file_path

    try:
        os.rename(file_path, new_path)
    except Exception as e:
        print(f"✗ Failed to rename {file_path}: {e}")
        return "error", file_path

    return prefix.rstrip("-"), new_path


def main():
    root_directory = "."

    if not os.path.isdir(root_directory):
        print("❌ Invalid directory. Please try again.")
        return

    print("=" * 70)
    print("📚 SPPU Question Papers - Automated Renaming Tool")
    print("=" * 70)

    # Step 1: Normalize all names
    print("\n🔄 STEP 1: Normalizing folder and file names...")
    rename_recursively(root_directory)

    # Step 2: Resolve duplicate folder names
    print("\n🔄 STEP 2: Resolving duplicate folder names...")
    resolve_duplicate_folders(root_directory)

    # Step 3: Classify PDFs based on content
    print("\n🔄 STEP 3: Classifying and renaming PDFs...")
    summary = {"endsem": 0, "insem": 0, "other": 0, "skipped": 0, "error": 0}
    other_files = []

    for current_dir, _, files in os.walk(root_directory):
        for file in files:
            if file.lower().endswith(".pdf"):
                full_path = os.path.join(current_dir, file)
                category, new_path = classify_and_rename(full_path)

                if category in summary:
                    summary[category] += 1
                else:
                    summary["other"] += 1

                # Store full path of "other" PDFs
                if category == "other":
                    other_files.append(new_path)

    print(f"✓ Classified {summary['endsem']} endsem, {summary['insem']} insem, {summary['other']} other PDFs")
    print(f"⊘ Skipped {summary['skipped']} already classified PDFs")

    # Step 4: Add subject acronyms to PDF filenames
    print("\n🔄 STEP 4: Adding subject acronyms to PDF filenames...")
    acronym_stats = {"renamed": 0, "skipped": 0, "error": 0}
    
    for current_dir, _, files in os.walk(root_directory):
        for file in files:
            if file.lower().endswith(".pdf"):
                full_path = os.path.join(current_dir, file)
                status, new_path = add_subject_acronym_to_pdf(full_path)
                acronym_stats[status] += 1

    print(f"✓ Added acronyms to {acronym_stats['renamed']} PDF files")
    print(f"⊘ Skipped {acronym_stats['skipped']} files (already have acronyms)")

    # Final Summary
    print("\n" + "=" * 70)
    print("📊 FINAL SUMMARY")
    print("=" * 70)
    print(f"  📂 PDF Classification:")
    print(f"     • Endsem PDFs  : {summary['endsem']}")
    print(f"     • Insem PDFs   : {summary['insem']}")
    print(f"     • Other PDFs   : {summary['other']}")
    print(f"     • Skipped      : {summary['skipped']}")
    print(f"     • Errors       : {summary['error']}")
    print(f"\n  🏷️  Subject Acronyms:")
    print(f"     • Added        : {acronym_stats['renamed']}")
    print(f"     • Skipped      : {acronym_stats['skipped']}")
    print(f"     • Errors       : {acronym_stats['error']}")

    if other_files:
        print(f"\n  ⚠️  Files classified as 'other' ({len(other_files)}):")
        for f in other_files[:10]:  # Show first 10
            print(f"     - {os.path.relpath(f, root_directory)}")
        if len(other_files) > 10:
            print(f"     ... and {len(other_files) - 10} more")

    print("\n✅ Processing complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()