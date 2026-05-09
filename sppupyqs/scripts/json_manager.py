from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable

from utils import ensure_directory, load_json_file


def iter_branch_files(input_dir: Path) -> list[Path]:
    return sorted(path for path in input_dir.glob("*.json") if path.is_file())


def iter_branch_items(branch_payload: dict[str, Any]) -> Iterable[tuple[str, str, dict[str, Any]]]:
    for semester, semester_payload in branch_payload.items():
        if not semester.startswith("sem-") or not isinstance(semester_payload, dict):
            continue

        for subject_slug, subject_payload in semester_payload.items():
            if not isinstance(subject_payload, dict):
                continue
            yield semester, subject_slug, subject_payload


def read_json(path: Path) -> dict[str, Any]:
    return load_json_file(path)


def subject_output_path(output_dir: Path, branch: str, semester: str, subject_slug: str) -> Path:
    return output_dir / branch / semester / f"{subject_slug}.json"


def load_subject_document(
    output_dir: Path,
    branch: str,
    semester: str,
    subject_slug: str,
    subject_name: str,
) -> tuple[Path, dict[str, Any]]:
    output_path = subject_output_path(output_dir, branch, semester, subject_slug)

    if output_path.exists():
        return output_path, read_json(output_path)

    return output_path, {
        "subject_name": subject_name,
        "subject_slug": subject_slug,
        "branch": branch,
        "semester": semester,
        "papers": [],
    }


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    ensure_directory(path.parent)

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        delete=False,
        dir=path.parent,
        suffix=".tmp",
    ) as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        temp_path = Path(handle.name)

    os.replace(temp_path, path)


def count_total_pdfs(branch_files: list[Path]) -> int:
    total = 0

    for branch_file in branch_files:
        branch_payload = read_json(branch_file)
        for _, _, subject_payload in iter_branch_items(branch_payload):
            pdf_links = subject_payload.get("pdf_links", [])
            if isinstance(pdf_links, list):
                total += len(pdf_links)

    return total


def count_target_pdfs(
    branch_files: list[Path],
    branch_filter: str | None = None,
    semester_filter: str | None = None,
    subject_filter: str | None = None,
) -> int:
    total = 0

    for branch_file in branch_files:
        if branch_filter and branch_file.stem.lower() != branch_filter:
            continue

        branch_payload = read_json(branch_file)
        for semester, subject_slug, subject_payload in iter_branch_items(branch_payload):
            if semester_filter and semester != semester_filter:
                continue
            if subject_filter and subject_slug != subject_filter:
                continue

            pdf_links = subject_payload.get("pdf_links", [])
            if isinstance(pdf_links, list):
                total += len(pdf_links)

    return total
