import os
import re
import fitz
from datetime import datetime

REPORT_FILE = "rename_update.txt"


# --------------------------------------------------
# PDF TEXT EXTRACTION
# --------------------------------------------------

def extract_text_from_pdf(pdf_path):
    try:
        with fitz.open(pdf_path) as doc:
            return " ".join(page.get_text() for page in doc)
    except Exception:
        return ""


# --------------------------------------------------
# EXAM TYPE
# --------------------------------------------------

def detect_exam_type(text):
    t = text.lower()

    if re.search(r"(max|maximum)\s*\.?\s*marks\s*:\s*30\b", t):
        return "insem"

    if re.search(r"(max|maximum)\s*\.?\s*marks\s*:\s*(50|70)\b", t):
        return "endsem"

    return "other"


# --------------------------------------------------
# EXAM MONTH (FROM FILENAME)
# --------------------------------------------------

def extract_exam_month_from_filename(filename):
    name = os.path.splitext(filename)[0].lower()
    name = name.replace("_", " ").replace("-", " ")

    year_match = re.search(r"(19|20)\d{2}", name)
    if not year_match:
        return None

    prefix = name[:year_match.start()]

    prefix = re.sub(
        r"\b(exam|examination|sem|semester|odd|even|insem|endsem|other)\b",
        "",
        prefix,
        flags=re.IGNORECASE
    )

    prefix = prefix.strip()
    return "-".join(prefix.split()) if prefix else None


# --------------------------------------------------
# EXAM YEAR (AGGRESSIVE & FAIL-SAFE)
# --------------------------------------------------

def extract_exam_year(filename, text):
    # 1) From filename (ANY 4-digit year)
    m = re.search(r"(19|20)\d{2}", filename)
    if m:
        return m.group()

    # 2) From PDF text near "Examination"
    m = re.search(r"examination\s*,?\s*(19|20)\d{2}", text, re.IGNORECASE)
    if m:
        return m.group().split()[-1]

    # 3) From PDF text ANY year in valid range
    m = re.search(
        r"\b(2018|2019|2020|2021|2022|2023|2024|2025|2026|2027|2028|2029|2030)\b",
        text
    )
    if m:
        return m.group()

    return None


# --------------------------------------------------
# PATTERN YEAR (ROBUST)
# --------------------------------------------------

def extract_pattern_year(text):
    m = re.search(
        r"(19|20)\d{2}\s*(?:credit\s*)?pattern",
        text,
        re.IGNORECASE
    )
    if m:
        return re.search(r"(19|20)\d{2}", m.group()).group()
    return None


# --------------------------------------------------
# SCHEME (ROMAN SAFE)
# --------------------------------------------------

def get_scheme_from_subject(folder_name):
    parts = re.split(r"[-\s]+", folder_name.lower())
    scheme = ""

    for p in parts:
        if not p:
            continue
        if re.fullmatch(r"i{1,4}|iv|v|vi{0,3}|ix|x", p):
            scheme += p
        else:
            scheme += p[0]

    return scheme


# --------------------------------------------------
# FINAL NAME CHECK
# --------------------------------------------------

FINAL_NAME_REGEX = re.compile(
    r"^(insem|endsem|other)-[a-z-]+-\d{4}-pat\d{4}-[a-z]+\.pdf$"
)

def already_correct(filename):
    return bool(FINAL_NAME_REGEX.match(filename))


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():
    folders_input = input(
        "Enter folders to process (comma separated, e.g. fy, aids, cse, it): "
    )

    target_folders = [f.strip() for f in folders_input.split(",") if f.strip()]

    renamed = []
    failed = []
    skipped = []

    for root_folder in target_folders:
        if not os.path.isdir(root_folder):
            failed.append((root_folder, ["branch folder not found"]))
            continue

        for dirpath, _, files in os.walk(root_folder):
            subject_folder = os.path.basename(dirpath)

            for file in files:
                if not file.lower().endswith(".pdf"):
                    continue

                old_path = os.path.abspath(os.path.join(dirpath, file))

                if already_correct(file):
                    skipped.append(old_path)
                    continue

                text = extract_text_from_pdf(old_path)
                if not text:
                    failed.append((old_path, ["unreadable pdf"]))
                    continue

                exam_type = detect_exam_type(text)
                exam_month = extract_exam_month_from_filename(file)
                exam_year = extract_exam_year(file, text)
                pattern_year = extract_pattern_year(text)
                scheme = get_scheme_from_subject(subject_folder)

                missing = []
                if not exam_month: missing.append("exam month")
                if not exam_year: missing.append("exam year")
                if not pattern_year: missing.append("pattern year")
                if not scheme: missing.append("scheme")

                if missing:
                    failed.append((old_path, missing))
                    continue

                new_name = (
                    f"{exam_type}-{exam_month}-{exam_year}"
                    f"-pat{pattern_year}-{scheme}.pdf"
                )

                if not FINAL_NAME_REGEX.match(new_name):
                    failed.append((old_path, ["generated filename invalid"]))
                    continue

                new_path = os.path.abspath(os.path.join(dirpath, new_name))

                if os.path.exists(new_path):
                    failed.append((old_path, ["target file already exists"]))
                    continue

                os.rename(old_path, new_path)
                renamed.append((old_path, new_path))


    # --------------------------------------------------
    # REPORT
    # --------------------------------------------------

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("SPPU QUESTION PAPER RENAME REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"Run Time           : {datetime.now()}\n")
        f.write(f"Folders Processed  : {', '.join(target_folders)}\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"TOTAL FILES RENAMED : {len(renamed)}\n")
        f.write(f"TOTAL FILES FAILED  : {len(failed)}\n")
        f.write(f"TOTAL FILES SKIPPED : {len(skipped)}\n\n")

        if renamed:
            f.write("✅ FILES RENAMED\n")
            f.write("-" * 80 + "\n")
            for old, new in renamed:
                f.write(f"OLD : {old}\n")
                f.write(f"NEW : {new}\n\n")

        if failed:
            f.write("❌ FILES NOT RENAMED (REASONS)\n")
            f.write("-" * 80 + "\n")
            for path, issues in failed:
                f.write(f"FILE : {path}\n")
                f.write(f"ISSUE: {', '.join(issues)}\n\n")

        if skipped:
            f.write("ℹ️ FILES ALREADY CORRECTLY NAMED\n")
            f.write("-" * 80 + "\n")
            for path in skipped:
                f.write(f"{path}\n")

    print("\n✅ DONE")
    print("📄 Detailed report written to:", os.path.abspath(REPORT_FILE))


if __name__ == "__main__":
    main()
