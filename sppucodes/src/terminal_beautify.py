import csv
import io
import nbformat
from rich.console import Console
from rich.markdown import Markdown

CSV_PREVIEW_ROWS = 7


def _render_ipynb_plain(content):
    """Render a .ipynb notebook as plain numbered cells, no outputs, no styling."""
    try:
        nb = nbformat.reads(content, as_version=4)
    except Exception:
        return "Failed to parse notebook."

    parts = []
    cell_num = 1

    for cell in nb.cells:
        source = cell.source
        if isinstance(source, list):
            source = "".join(source)
        source = source.strip()
        if not source:
            continue

        parts.append(f"Cell {cell_num}:")
        parts.append(source)
        parts.append("")
        cell_num += 1

    return "\n".join(parts).strip()


def _render_csv_plain(content, full=False, max_rows=CSV_PREVIEW_ROWS, request_url=None):
    """Show CSV as a plain text table. Truncates to max_rows unless full=True."""
    lines = content.strip().splitlines()
    if not lines:
        return "(empty file)"

    reader = csv.reader(lines)
    all_rows = list(reader)

    if not all_rows:
        return "(empty file)"

    rows = all_rows if full else all_rows[: max_rows + 1]  # header + max_rows data

    # Align columns
    col_widths = [max(len(str(cell)) for cell in col) for col in zip(*rows)]
    table = []
    for r in rows:
        table.append("  ".join(str(cell).ljust(w) for cell, w in zip(r, col_widths)))

    if not full:
        total_data_rows = len(all_rows) - 1  # subtract header
        hidden = total_data_rows - max_rows
        if hidden > 0:
            if request_url:
                full_url = (request_url + "&full") if "?" in request_url else (request_url + "?full")
                table.append(f"\n{hidden} more rows. To get the whole CSV run:\ncurl.exe {full_url}")
            else:
                table.append(f"\n{hidden} more rows. To get the whole CSV, append ?full to the URL.")

    return "\n".join(table)


def _needs_special_handling(fname):
    ext = fname.rsplit(".", 1)[-1].lower() if "." in fname else ""
    return ext in ("md", "ipynb", "csv")


def _render_file_plain(fname, content, full_csv=False, request_url=None):
    """Render a single file to plain text (no ANSI)."""
    ext = fname.rsplit(".", 1)[-1].lower() if "." in fname else ""
    if ext == "ipynb":
        return _render_ipynb_plain(content)
    if ext == "csv":
        return _render_csv_plain(content, full=full_csv, request_url=request_url)
    return content.strip()


def beautify_terminal_output(contents, question_text, full_csv=False, request_url=None):
    """Beautify answer files for terminal display. Returns string or None.

    - .md    -> rendered with Rich Markdown (ANSI colours)
    - .ipynb -> plain numbered cells, no outputs, no colours
    - .csv   -> top 7 rows as a plain text table (all rows if full_csv=True)
    - other  -> caller handles (returns None)
    """
    has_md = any(fname.lower().endswith(".md") for fname, _ in contents)
    any_special = any(_needs_special_handling(fname) for fname, _ in contents)

    if not any_special:
        return None

    # No .md present -> pure plain text, zero Rich, zero ANSI
    if not has_md:
        parts = []
        if question_text:
            parts.append(question_text.strip())
            parts.append("")

        for fname, content in contents:
            if len(contents) > 1:
                sep = "-" * 40
                parts.append(sep)
                parts.append(f"File: {fname}")
                parts.append(sep)
            parts.append(_render_file_plain(fname, content, full_csv=full_csv, request_url=request_url))
            parts.append("")

        return "\n".join(parts).strip()

    # .md present (possibly mixed): use Rich for .md, plain text for everything else
    console = Console(
        file=io.StringIO(), force_terminal=True, color_system="truecolor", width=100
    )

    with console.capture() as capture:
        if question_text:
            console.print(question_text.strip())
            console.print()

        for fname, content in contents:
            ext = fname.rsplit(".", 1)[-1].lower() if "." in fname else ""
            if ext == "md":
                console.print(Markdown(content))
            else:
                console.print(_render_file_plain(fname, content, full_csv=full_csv, request_url=request_url))
            console.print()

    return capture.get()
