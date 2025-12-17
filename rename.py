import os
import re
import fitz
from datetime import datetime

REPORT_FILE = "rename_update.txt"


def extract_text_from_pdf(pdf_path):
    try:
        with fitz.open(pdf_path) as doc:
            return "".join(page.get_text() for page in doc)
    except Exception:
        return ""


def detect_exam_type(text):
    t = text.lower()

    if re.search(r"(max|maximum)\s*\.?\s*marks\s*:\s*30\b", t):
        return "insem"

    if re.search(r"(max|maximum)\s*\.?\s*marks\s*:\s*(50|70)\b", t):
        return "endsem"

    return "other"


def extract_exam_month_from_filename(filename):
    name = os.path.splitext(filename)[0].lower()
    name = name.replace("_", " ").replace("-", " ")

    year_match = re.search(r"\b(19|20)\d{2}\b", name)
    if not year_match:
        return None

    prefix = name[:year_match.start()]

    # Remove ALL noise words strictly
    prefix = re.sub(
        r"\b(exam|examination|sem|semester|odd|even|insem|endsem|other)\b",
        "",
        prefix,
        flags=re.IGNORECASE
    )

    prefix = prefix.strip()
    if not prefix:
        return None

    return "-".join(prefix.split())


def extract_exam_year_from_filename(filename):
    m = re.search(r"\b(19|20)\d{2}\b", filename)
    return m.group(0) if m else None


def extract_exam_year_from_text(text):
    m = re.search(r"examination\s*,?\s*(\d{4})", text, re.IGNORECASE)
    return m.group(1) if m else None


def extract_pattern_year(text):
    m = re.search(
        r"\(\s*(\d{4})\s*(?:credit\s*)?pattern\s*\)",
        text,
        re.IGNORECASE
    )
    return m.group(1) if m else None


# ✅ FIXED SCHEME LOGIC (ROMAN NUMERALS PRESERVED)
def get_scheme_from_subject(folder_name):
    parts = re.split(r"[-\s]+", folder_name.lower())

    scheme_parts = []
    for p in parts:
        if not p:
            continue

        # Preserve roman numerals fully (i, ii, iii, iv, v, etc.)
        if re.fullmatch(r"i{1,4}|iv|v|vi{0,3}|ix|x", p):
            scheme_parts.append(p)
        else:
            scheme_parts.append(p[0])

    return "".join(scheme_parts)


FINAL_NAME_REGEX = re.compile(
    r"^(insem|endsem|other)-[a-z-]+-\d{4}-pat\d{4}-[a-z]+\.pdf$"
)


def already_correct(filename):
    return bool(FINAL_NAME_REGEX.match(filename))


def main():
    folders_input = input(
        "Enter folders to process (comma separated, e.g. fy, aids, cse): "
    )

    target_folders = [f.strip() for f in folders_input.split(",") if f.strip()]

    renamed = []
    failed = []
    skipped = []

    for root_folder in target_folders:
        if not os.path.isdir(root_folder):
            continue

        for dirpath, _, files in os.walk(root_folder):
            subject_folder = os.path.basename(dirpath)

            for file in files:
                if not file.lower().endswith(".pdf"):
                    continue

                full_path = os.path.join(dirpath, file)

                if already_correct(file):
                    skipped.append(full_path)
                    continue

                text = extract_text_from_pdf(full_path)
                if not text:
                    failed.append((full_path, ["unreadable pdf"]))
                    continue

                exam_type = detect_exam_type(text)
                exam_month = extract_exam_month_from_filename(file)

                exam_year = (
                    extract_exam_year_from_filename(file)
                    or extract_exam_year_from_text(text)
                )

                pattern_year = extract_pattern_year(text)
                scheme = get_scheme_from_subject(subject_folder)

                missing = []
                if not exam_month:
                    missing.append("exam month")
                if not exam_year:
                    missing.append("exam year")
                if not pattern_year:
                    missing.append("pattern year")
                if not scheme:
                    missing.append("scheme")

                if missing:
                    failed.append((full_path, missing))
                    continue

                new_name = (
                    f"{exam_type}-{exam_month}-{exam_year}"
                    f"-pat{pattern_year}-{scheme}.pdf"
                )

                # Final safety check
                if not FINAL_NAME_REGEX.match(new_name):
                    failed.append((full_path, ["generated name invalid"]))
                    continue

                new_path = os.path.join(dirpath, new_name)

                if os.path.exists(new_path):
                    failed.append((full_path, ["target already exists"]))
                    continue

                os.rename(full_path, new_path)
                renamed.append((full_path, new_path))

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("SPPU QUESTION PAPER RENAME REPORT\n")
        f.write("=" * 72 + "\n")
        f.write(f"Run Time : {datetime.now()}\n\n")

        f.write(f"TOTAL FILES RENAMED : {len(renamed)}\n")
        f.write(f"TOTAL FILES FAILED  : {len(failed)}\n")
        f.write(f"TOTAL FILES SKIPPED : {len(skipped)}\n\n")

        if renamed:
            f.write("✅ FILES RENAMED\n")
            f.write("-" * 72 + "\n")
            for old, new in renamed:
                f.write(f"{old} → {os.path.basename(new)}\n")
            f.write("\n")

        if failed:
            f.write("❌ FILES NOT RENAMED (ISSUES FOUND)\n")
            f.write("-" * 72 + "\n")
            for path, issues in failed:
                f.write(f"{path} → Missing/Issue: {', '.join(issues)}\n")
            f.write("\n")

        if skipped:
            f.write("ℹ️ FILES ALREADY CORRECTLY NAMED\n")
            f.write("-" * 72 + "\n")
            for path in skipped:
                f.write(f"{path}\n")

    print("\n✔ Done. Report generated:", REPORT_FILE)


if __name__ == "__main__":
    main()
