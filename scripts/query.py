"""Query the RAG system: retrieve the top-k chunks, then generate an answer.

The retrieval step is one SQL line — pgvector's `<=>` is cosine distance, so
`ORDER BY embedding <=> query_vector LIMIT k` returns the k most similar chunks.

Usage:
    python scripts/query.py "What is the Aramis-7 shutdown threshold?"
    python scripts/query.py --no-rag "..."   # baseline: base model, no retrieval
    python scripts/query.py --unsafe "..."   # use the NAIVE (vulnerable) prompt
    python scripts/query.py --k 6 "..."
"""
import argparse

from defenses import TRUSTED_ORIGINS, redact_output
from prompt_templates import build_prompt
from rag_common import TOP_K, connect, embed, generate


def retrieve(question: str, k: int, trusted_only: bool = False):
    """Return the k most similar chunks as (source, content) tuples.

    trusted_only enforces the provenance allowlist (source vetting): only chunks whose
    origin is in TRUSTED_ORIGINS can be retrieved, so poisoned documents never reach
    the prompt.
    """
    conn = connect()
    cur = conn.cursor()
    if trusted_only:
        cur.execute(
            "SELECT source, content FROM docs WHERE origin = ANY(%s) "
            "ORDER BY embedding <=> %s::vector LIMIT %s",
            (list(TRUSTED_ORIGINS), embed(question), k),
        )
    else:
        cur.execute(
            "SELECT source, content FROM docs ORDER BY embedding <=> %s::vector LIMIT %s",
            (embed(question), k),
        )
    rows = cur.fetchall()
    conn.close()
    return rows


def answer(question: str, k: int = TOP_K, no_rag: bool = False, hardened: bool = True,
           trusted_only: bool = False, filter_output: bool = False, show: bool = True):
    if no_rag:
        prompt, sources = f"Question: {question}\nAnswer:", []
    else:
        rows = retrieve(question, k, trusted_only=trusted_only)
        sources = [r[0] for r in rows]
        prompt = build_prompt(question, [r[1] for r in rows], hardened=hardened)

    out = generate(prompt)
    if filter_output:
        out = redact_output(out)

    if show:
        mode = ("NO-RAG (base model)" if no_rag
                else f"RAG top-{k}, {'hardened' if hardened else 'NAIVE'} prompt")
        print(f"\n[{mode}]\nQ: {question}\nA: {out}")
        if sources:
            print(f"Sources: {', '.join(dict.fromkeys(sources))}")
    return out, sources


def main():
    ap = argparse.ArgumentParser(description="Ask the RAG knowledge base.")
    ap.add_argument("question")
    ap.add_argument("--k", type=int, default=TOP_K, help="number of chunks to retrieve")
    ap.add_argument("--no-rag", action="store_true", help="ask the base model with no retrieval")
    ap.add_argument("--unsafe", action="store_true", help="use the NAIVE (injection-vulnerable) prompt")
    ap.add_argument("--trusted-only", action="store_true", help="source vetting: retrieve only trusted origins")
    ap.add_argument("--filter-output", action="store_true", help="deterministic output redaction filter")
    args = ap.parse_args()
    answer(args.question, k=args.k, no_rag=args.no_rag, hardened=not args.unsafe,
           trusted_only=args.trusted_only, filter_output=args.filter_output)


if __name__ == "__main__":
    main()
