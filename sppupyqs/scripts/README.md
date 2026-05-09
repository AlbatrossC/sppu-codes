# PYQ Metadata Pipeline

This pipeline reads SPPU question paper branch JSON files, downloads each linked PDF, extracts paper text, sends that text to Gemini using your existing prompt and schema files, and stores resumable structured metadata output inside `pyqs-metadata`.

## Folder Layout

The pipeline expects this structure:

```text
sppupyqs/
├── scripts/
│   ├── .env
│   ├── config.py
│   ├── extractor.py
│   ├── gemini_client.py
│   ├── json_manager.py
│   ├── logger.py
│   ├── main.py
│   ├── metadata.txt
│   ├── prompt.txt
│   ├── README.md
│   ├── requirements.txt
│   ├── structure_output.json
│   ├── strucutre_output.json
│   └── utils.py
├── question-papers/
│   └── question-papers-r2/
└── pyqs-metadata/
```

## How It Works

When you run `main.py`, the pipeline performs these steps:

1. Loads `.env` from `sppupyqs/scripts/.env`.
2. Loads the Gemini system prompt from `prompt.txt`.
3. Loads the response schema from `structure_output.json`.
   If that file is missing, it automatically falls back to the existing `strucutre_output.json`.
4. Shows a terminal selection for available branch JSON files when `--branch` is not passed.
5. Processes only one selected branch at a time.
6. Iterates:
   `branch -> semester -> subject -> pdf_links`
7. Downloads each PDF and extracts text with PyMuPDF using `page.get_text("text")`.
8. If extracted text is too small or invalid, retries using OCR fallback.
9. Sends extracted text to Gemini using:
   `gemini-3.1-flash-lite`
10. Tries `PRIMARY_GEMINI_API_KEY` first and retries with `SECONDARY_GEMINI_API_KEY` if needed.
11. Generates deterministic `pdf_id` values from `sha1(pdf_url)[:12]`.
12. Generates local `question_id` values after Gemini returns JSON.
13. Skips PDFs already present in the target subject metadata file.
14. Writes subject JSON files atomically so partial writes do not corrupt output.
15. Appends progress snapshots and failure logs to `metadata.txt`.

## Interactive Branch Selection

If you run `main.py` without `--branch`, it will show one selectable branch at a time from:

```text
sppupyqs/question-papers/question-papers-r2/*.json
```

If `questionary` is installed, you get a dropdown-style terminal selector.

If `questionary` is not installed, the script falls back to a numbered terminal menu.

Examples:

```bash
python main.py
python main.py --no-interactive
python main.py --branch aids
python main.py --branch aids --semester sem-3
python main.py --branch aids --semester sem-3 --subject discrete-mathematics-aids
python main.py --branch aids --limit 5
```

## Input Format

Each branch JSON file inside `question-papers/question-papers-r2/` should follow this shape:

```json
{
  "branch_name": "Artificial Intelligence and Data Science",
  "branch_code": "AI & DS",
  "sem-3": {
    "discrete-mathematics-aids": {
      "subject_name": "Discrete Mathematics",
      "pdf_links": [
        "https://example.com/paper.pdf"
      ]
    }
  }
}
```

The pipeline ignores non-semester top-level keys like `branch_name` and `branch_code`.

## Output Format

Output is written to:

```text
sppupyqs/pyqs-metadata/<branch>/<semester>/<subject-slug>.json
```

Example:

```text
pyqs-metadata/
└── aids/
    └── sem-3/
        └── discrete-mathematics-aids.json
```

Each subject JSON looks like:

```json
{
  "subject_name": "Discrete Mathematics",
  "subject_slug": "discrete-mathematics-aids",
  "branch": "aids",
  "semester": "sem-3",
  "papers": [
    {
      "pdf_id": "a8f9c21d41ab",
      "pdf_url": "https://example.com/paper.pdf",
      "metadata": {},
      "questions": [],
      "extraction_info": {
        "method": "pymupdf_text",
        "used_ocr": false,
        "page_count": 4,
        "character_count": 5271,
        "processed_at": "2026-05-09 12:10:00"
      }
    }
  ]
}
```

## Environment Variables

Create `sppupyqs/scripts/.env` with:

```env
PRIMARY_GEMINI_API_KEY=your_primary_key
SECONDARY_GEMINI_API_KEY=your_secondary_key
GEMINI_MODEL=gemini-3.1-flash-lite
REQUEST_TIMEOUT_SECONDS=60
GEMINI_RETRIES_PER_KEY=3
GEMINI_RETRY_DELAY_SECONDS=3
PDF_TEXT_MIN_CHARACTERS=200
OCR_LANGUAGE=eng
TESSERACT_CMD=
```

`TESSERACT_CMD` is optional. Set it only if Tesseract is installed in a custom location.

## Install Dependencies

Install the pipeline dependencies from the `scripts` folder:

```bash
pip install -r requirements.txt
```

Main packages:

- `PyMuPDF` for default PDF text extraction
- `pytesseract` and `Pillow` for OCR fallback
- `google-genai` for Gemini requests
- `questionary` for the terminal dropdown selector

## Running The Pipeline

From `sppupyqs/scripts`:

```bash
python main.py
```

Or from the repo root:

```bash
python sppupyqs/scripts/main.py
```

Useful filters:

- `--branch` processes one branch directly without prompting
- `--semester` narrows processing to one semester
- `--subject` narrows processing to one subject
- `--limit` processes only a fixed number of new PDFs
- `--no-interactive` disables the terminal selector if you want batch behavior

## metadata.txt Logging

The script appends progress to:

```text
sppupyqs/scripts/metadata.txt
```

It records:

- processed count
- skipped count
- failed count
- remaining count
- current branch
- current semester
- current subject
- Gemini failures
- OCR usage
- timestamps

## Resumable Behavior

The pipeline is safe to rerun.

Before processing a PDF, it loads the existing subject output JSON and checks whether that `pdf_url` is already present in `papers`.

If found, the PDF is skipped.

This prevents duplicate processing and supports long-running incremental builds.

## Error Handling

The pipeline is designed to continue when one PDF fails.

- PDF extraction failures are logged and counted.
- Gemini failures are logged and counted separately.
- OCR is used only when normal text extraction is not good enough.
- Output writes are atomic.
- All files use UTF-8.

## Notes

- `extract.py` is an older standalone helper and is not used by the production pipeline.
- `structure_output.json` is now the preferred schema filename.
- `strucutre_output.json` is still supported as a fallback for compatibility.
