from __future__ import annotations

import argparse
from pathlib import Path

from config import load_config
from json_manager import (
    atomic_write_json,
    count_target_pdfs,
    iter_branch_files,
    iter_branch_items,
    load_subject_document,
    read_json,
)
from logger import PipelineStats, ProgressLogger
from utils import (
    assign_question_ids,
    branch_name_from_file,
    build_pdf_id,
    ensure_directory,
    load_json_file,
    load_text_file,
    timestamp_string,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract PYQ metadata into JSON files.")
    parser.add_argument("--branch", help="Process only one branch slug, for example aids.")
    parser.add_argument("--semester", help="Process only one semester slug, for example sem-3.")
    parser.add_argument("--subject", help="Process only one subject slug.")
    parser.add_argument("--limit", type=int, help="Stop after processing N new PDFs.")
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Disable terminal branch selection when --branch is not provided.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config()
    progress_logger = ProgressLogger(config.metadata_report_path)

    try:
        from extractor import PDFTextExtractor
        from gemini_client import GeminiExtractionError, GeminiMetadataClient
    except ImportError as error:
        progress_logger.append_event(f"Dependency error: {error}")
        print(f"Dependency error: {error}")
        return 1

    ensure_directory(config.output_dir)
    ensure_directory(config.scripts_dir)

    system_prompt = load_text_file(config.prompt_path)
    response_schema = load_json_file(config.schema_path)

    available_branch_files = iter_branch_files(config.input_dir)
    selected_branch = resolve_branch_selection(
        available_branch_files,
        provided_branch=args.branch,
        interactive=not args.no_interactive,
    )
    if selected_branch:
        print(f"Selected branch: {selected_branch}")

    branch_files = filtered_branch_files(available_branch_files, selected_branch)
    stats = PipelineStats(
        total=count_target_pdfs(
            branch_files,
            branch_filter=selected_branch,
            semester_filter=args.semester,
            subject_filter=args.subject,
        )
    )
    progress_logger.append_event("Pipeline started.")
    print(f"Pipeline started. Target PDFs: {stats.total}")

    extractor = PDFTextExtractor(
        timeout_seconds=config.request_timeout_seconds,
        min_text_characters=config.pdf_text_min_characters,
        ocr_language=config.ocr_language,
        tesseract_cmd=config.tesseract_cmd,
    )
    try:
        gemini_client = GeminiMetadataClient(
            api_keys=config.gemini_api_keys,
            model_name=config.model_name,
            system_prompt=system_prompt,
            response_schema=response_schema,
            retries_per_key=config.gemini_retries_per_key,
            retry_delay_seconds=config.gemini_retry_delay_seconds,
        )
    except ValueError as error:
        progress_logger.append_event(f"Configuration error: {error}")
        progress_logger.append_snapshot(stats)
        print(f"Configuration error: {error}")
        print(f"Check: {config.scripts_dir / '.env'}")
        return 1

    processed_this_run = 0

    for branch_file in branch_files:
        branch = branch_name_from_file(branch_file)
        branch_payload = read_json(branch_file)

        for semester, subject_slug, subject_payload in iter_branch_items(branch_payload):
            if args.semester and semester != args.semester:
                continue
            if args.subject and subject_slug != args.subject:
                continue

            subject_name = str(subject_payload.get("subject_name", subject_slug))
            stats.current_branch = branch
            stats.current_semester = semester
            stats.current_subject = subject_slug

            output_path, subject_document = load_subject_document(
                config.output_dir,
                branch,
                semester,
                subject_slug,
                subject_name,
            )
            existing_pdf_urls = {
                paper.get("pdf_url")
                for paper in subject_document.get("papers", [])
                if isinstance(paper, dict)
            }

            for pdf_url in subject_payload.get("pdf_links", []):
                pdf_id = build_pdf_id(pdf_url)

                if pdf_url in existing_pdf_urls:
                    stats.skipped += 1
                    progress_logger.append_event(f"Skipped existing PDF: {pdf_url}")
                    progress_logger.append_snapshot(stats)
                    print(f"Skipped existing PDF: {pdf_url}")
                    continue

                try:
                    print(f"Processing PDF: {pdf_url}")
                    extracted_document = extractor.extract_from_url(pdf_url)
                    if extracted_document.used_ocr:
                        stats.ocr_used += 1
                        progress_logger.append_event(f"OCR used for {pdf_url}")
                        print(f"OCR used for: {pdf_url}")

                    gemini_payload = gemini_client.extract_metadata(
                        branch=branch,
                        semester=semester,
                        subject_name=subject_name,
                        subject_slug=subject_slug,
                        pdf_url=pdf_url,
                        extracted_text=extracted_document.text,
                    )
                    questions = gemini_payload.get("questions", [])
                    normalized_questions = assign_question_ids(pdf_id, questions)

                    paper_payload = {
                        "pdf_id": pdf_id,
                        "pdf_url": pdf_url,
                        "metadata": gemini_payload.get("metadata", {}),
                        "questions": normalized_questions,
                        "extraction_info": {
                            "method": extracted_document.extraction_method,
                            "used_ocr": extracted_document.used_ocr,
                            "page_count": extracted_document.page_count,
                            "character_count": extracted_document.character_count,
                            "processed_at": timestamp_string(),
                        },
                    }
                    subject_document.setdefault("papers", []).append(paper_payload)
                    atomic_write_json(output_path, subject_document)

                    existing_pdf_urls.add(pdf_url)
                    stats.processed += 1
                    processed_this_run += 1
                    progress_logger.append_event(f"Processed PDF: {pdf_url}")
                    progress_logger.append_snapshot(stats)
                    print(f"Processed PDF: {pdf_url}")

                    if args.limit and processed_this_run >= args.limit:
                        progress_logger.append_event("Processing limit reached.")
                        print("Processing limit reached.")
                        print_summary(stats)
                        return 0
                except GeminiExtractionError as error:
                    stats.failed += 1
                    stats.gemini_failures += 1
                    progress_logger.append_event(f"Gemini failure for {pdf_url}: {error}")
                    progress_logger.append_snapshot(stats)
                    print(f"Gemini failure for {pdf_url}: {error}")
                except Exception as error:  # pragma: no cover
                    stats.failed += 1
                    progress_logger.append_event(f"PDF failure for {pdf_url}: {error}")
                    progress_logger.append_snapshot(stats)
                    print(f"PDF failure for {pdf_url}: {error}")

    progress_logger.append_event("Pipeline completed.")
    progress_logger.append_snapshot(stats)
    print("Pipeline completed.")
    print_summary(stats)
    return 0


def filtered_branch_files(branch_files: list[Path], branch_filter: str | None) -> list[Path]:
    if not branch_filter:
        return branch_files
    return [path for path in branch_files if branch_name_from_file(path) == branch_filter]


def resolve_branch_selection(
    branch_files: list[Path],
    *,
    provided_branch: str | None,
    interactive: bool,
) -> str | None:
    if provided_branch:
        return provided_branch
    if not interactive or not branch_files:
        return None
    if len(branch_files) == 1:
        return branch_name_from_file(branch_files[0])

    return prompt_for_branch(branch_files)


def prompt_for_branch(branch_files: list[Path]) -> str:
    choices = [branch_name_from_file(path) for path in branch_files]

    try:
        import questionary

        selection = questionary.select(
            "Select one branch JSON file to process:",
            choices=choices,
            qmark=">",
        ).ask()
        if not selection:
            raise KeyboardInterrupt("Branch selection cancelled.")
        return selection
    except Exception:
        print("Select one branch JSON file to process:")
        for index, choice in enumerate(choices, start=1):
            print(f"{index}. {choice}")

        while True:
            raw_value = input("Enter selection number: ").strip()
            if not raw_value.isdigit():
                print("Please enter a valid number.")
                continue

            selected_index = int(raw_value)
            if 1 <= selected_index <= len(choices):
                return choices[selected_index - 1]

            print("Selection out of range. Try again.")


def print_summary(stats: PipelineStats) -> None:
    print(
        "Summary:"
        f" processed={stats.processed},"
        f" skipped={stats.skipped},"
        f" failed={stats.failed},"
        f" remaining={stats.remaining},"
        f" gemini_failures={stats.gemini_failures},"
        f" ocr_used={stats.ocr_used}"
    )


if __name__ == "__main__":
    raise SystemExit(main())
