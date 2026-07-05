"""Store documents in the RAG knowledge base.

Pipeline per document:  read -> chunk -> embed each chunk -> INSERT into pgvector.

Usage:
    python scripts/ingest.py --source corpus/curated   --origin curated
    python scripts/ingest.py --source corpus/hf_sample  --origin hf_sample
    python scripts/ingest.py --source corpus/poisoned   --origin poisoned
"""
import argparse
import pathlib

from rag_common import chunk_text, connect, embed

TEXT_SUFFIXES = {".md", ".txt"}


def iter_files(source: str):
    root = pathlib.Path(source)
    return sorted(f for f in root.rglob("*") if f.suffix.lower() in TEXT_SUFFIXES)


def main():
    ap = argparse.ArgumentParser(description="Ingest documents into the pgvector KB.")
    ap.add_argument("--source", required=True, help="folder of .md/.txt files")
    ap.add_argument("--origin", default="curated",
                    help="provenance tag stored with each chunk (curated|hf_sample|poisoned)")
    ap.add_argument("--reset-origin", action="store_true",
                    help="delete existing rows with this origin before ingesting")
    args = ap.parse_args()

    conn = connect()
    cur = conn.cursor()

    if args.reset_origin:
        cur.execute("DELETE FROM docs WHERE origin = %s", (args.origin,))
        print(f"  cleared existing rows with origin={args.origin}")

    files = iter_files(args.source)
    if not files:
        print(f"No .md/.txt files found under {args.source!r}. Nothing to do.")
        return

    n_chunks = 0
    for f in files:
        chunks = chunk_text(f.read_text(encoding="utf-8", errors="ignore"))
        for ch in chunks:
            cur.execute(
                "INSERT INTO docs (source, origin, content, embedding) "
                "VALUES (%s, %s, %s, %s::vector)",
                (f.name, args.origin, ch, embed(ch)),
            )
        n_chunks += len(chunks)
        print(f"  ingested {f.name}: {len(chunks)} chunk(s)")

    conn.commit()
    cur.execute("SELECT count(*) FROM docs")
    total = cur.fetchone()[0]
    conn.close()
    print(f"Done: {len(files)} file(s), {n_chunks} chunk(s) added "
          f"(origin={args.origin}). Total rows in KB: {total}")


if __name__ == "__main__":
    main()
