import io
import nbformat
from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.panel import Panel
from rich.rule import Rule


def _render_ipynb(console, content):
    try:
        nb = nbformat.reads(content, as_version=4)
    except Exception:
        console.print("[red]Failed to parse notebook[/red]")
        return

    for cell in nb.cells:
        cell_type = cell.cell_type
        source = cell.source
        if isinstance(source, list):
            source = "".join(source)

        if cell_type == "markdown":
            console.print(Markdown(source.strip()))
            console.print()
        elif cell_type == "code":
            exec_count = cell.get("execution_count")
            count_label = f" [{exec_count}]" if exec_count else ""
            console.print(
                Panel(
                    Syntax(source.strip(), "python", theme="monokai", line_numbers=False),
                    title=f"[bold yellow]In{count_label}[/bold yellow]",
                    border_style="dim",
                )
            )
            outputs = cell.get("outputs", [])
            for output in outputs:
                output_type = output.get("output_type")
                if output_type == "stream":
                    text = "".join(output.get("text", []))
                    if text.strip():
                        console.print(text.rstrip(), style="dim")
                elif output_type == "execute_result":
                    text = "".join(output.get("data", {}).get("text/plain", []))
                    if text.strip():
                        console.print(text.rstrip(), style="dim")
                elif output_type == "error":
                    traceback = "".join(output.get("traceback", []))
                    console.print(traceback.rstrip(), style="red")
            console.print()


def beautify_terminal_output(contents, question_text):
    """Beautify answer files for terminal display. Returns ANSI string or None."""
    needs_beautify = any(
        fname.lower().endswith((".md", ".ipynb")) for fname, _ in contents
    )

    if not needs_beautify:
        return None

    console = Console(
        file=io.StringIO(), force_terminal=True, color_system="truecolor", width=100
    )

    with console.capture() as capture:
        if question_text:
            console.print(question_text.strip())
            console.print()

        for fname, content in contents:
            ext = fname.split(".")[-1].lower() if "." in fname else ""

            console.print(Rule(f"[bold cyan]{fname}[/bold cyan]"))

            if ext == "md":
                console.print(Markdown(content))
            elif ext == "ipynb":
                _render_ipynb(console, content)
            else:
                console.print(content)

            console.print()

    return capture.get()
