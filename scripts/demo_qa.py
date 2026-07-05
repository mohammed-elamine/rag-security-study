"""Generate the base-vs-RAG comparison table for the report.

Each question is asked twice: once with no retrieval (base model) and once with RAG.
The base model cannot know these fictional Aramis-7 facts, so the contrast proves the
knowledge base is actually being used.

Writes: report/results/qa_table.md
"""
import pathlib

from query import answer

QUESTIONS = [
    "What coolant temperature triggers an automatic shutdown on the Aramis-7?",
    "What does alarm ARM-441 mean?",
    "How often must the Aramis-7 coolant filter cartridge be replaced?",
    "Which TCP port is the Aramis-7 proprietary maintenance channel on?",
    "What is the current stable firmware version for the Aramis-7 and when was it released?",
    "Who is the maintenance lead of record for the Aramis-7 reference site?",
]

OUT = pathlib.Path(__file__).resolve().parent.parent / "report" / "results" / "qa_table.md"


def cell(s: str) -> str:
    """Collapse whitespace and escape pipes so the text fits one Markdown table cell."""
    return " ".join(s.split()).replace("|", "\\|")


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for q in QUESTIONS:
        base, _ = answer(q, no_rag=True, show=False)
        rag, srcs = answer(q, no_rag=False, hardened=True, show=False)
        rows.append((q, base, rag, srcs))
        print(f"done: {q}")

    lines = [
        "# RAG vs. base-model — prompt/response comparison",
        "",
        "Same question asked twice: base model (no retrieval) vs. RAG (with retrieval).",
        "The base model cannot know these facts; RAG answers them from the knowledge base.",
        "",
        "| Question | Base model (no RAG) | RAG answer | Sources |",
        "|---|---|---|---|",
    ]
    for q, base, rag, srcs in rows:
        lines.append(f"| {cell(q)} | {cell(base)} | {cell(rag)} | {cell(', '.join(dict.fromkeys(srcs)))} |")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
