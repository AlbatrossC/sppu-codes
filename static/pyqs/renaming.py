import os
import fitz  # PyMuPDF

def normalize_name(name):
    name = name.replace('-', '')            # Remove all hyphens
    name = name.replace('@', 'and')         # Replace @ with 'and'
    name = '_'.join(name.lower().split())   # Replace spaces with underscores and lowercase
    return name

def rename_recursively(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # Rename files
        for filename in filenames:
            new_name = normalize_name(filename)
            if new_name != filename:
                src = os.path.join(dirpath, filename)
                dst = os.path.join(dirpath, new_name)
                os.rename(src, dst)
                print(f"Renamed file: {src} -> {dst}")
        
        # Rename folders
        for dirname in dirnames:
            new_name = normalize_name(dirname)
            if new_name != dirname:
                src = os.path.join(dirpath, dirname)
                dst = os.path.join(dirpath, new_name)
                os.rename(src, dst)
                print(f"Renamed folder: {src} -> {dst}")

def extract_text_from_pdf(file_path):
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""

def classify_and_rename(file_path):
    text = extract_text_from_pdf(file_path)
    base_dir = os.path.dirname(file_path)
    filename = os.path.basename(file_path)

    if filename.startswith(("endsem_", "insem_", "other_")):
        return "skipped", filename

    text_lower = text.lower()

    if "max. marks : 70" in text_lower:
        prefix = "endsem_"
    elif "max. marks : 30" in text_lower:
        prefix = "insem_"
    else:
        prefix = "other_"

    new_filename = prefix + filename
    new_path = os.path.join(base_dir, new_filename)

    try:
        os.rename(file_path, new_path)
    except Exception as e:
        print(f"Failed to rename {file_path}: {e}")
        return "error", filename

    return prefix.rstrip("_"), new_filename

def main():
    root_directory = "."
    
    if not os.path.isdir(root_directory):
        print("❌ Invalid directory. Please try again.")
        return

    print("🔄 Normalizing folder and file names...")
    rename_recursively(root_directory)

    print("🔍 Classifying and renaming PDFs...")
    summary = {"endsem": 0, "insem": 0, "other": 0, "skipped": 0, "error": 0}
    other_files = []

    for current_dir, _, files in os.walk(root_directory):
        for file in files:
            if file.lower().endswith(".pdf"):
                full_path = os.path.join(current_dir, file)
                category, new_filename = classify_and_rename(full_path)

                if category in summary:
                    summary[category] += 1
                else:
                    summary["other"] += 1
                    other_files.append(new_filename)

    print("\n📊 Summary:")
    for key, count in summary.items():
        print(f"  {key.capitalize()} PDFs : {count}")

    if other_files:
        print("\n📁 Files classified as 'other':")
        for f in other_files:
            print(" -", f)

if __name__ == "__main__":
    main()
