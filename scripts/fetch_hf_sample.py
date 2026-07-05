"""Download a small sample of the spec-recommended HuggingFace dataset.

The RAG brief highlights `neural-bridge/rag-dataset-12000` as a resource. We pull only
a couple hundred rows (streaming, so the full ~12k dataset is never downloaded) to show
the pipeline scales beyond the curated corpus. Each row's `context` becomes one .txt file.

Usage:
    python scripts/fetch_hf_sample.py [--n 200]
"""
import argparse
import pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "corpus" / "hf_sample"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200, help="number of documents to keep")
    args = ap.parse_args()

    try:
        from datasets import load_dataset
    except ImportError:
        raise SystemExit("The 'datasets' package is required: pip install datasets")

    OUT.mkdir(parents=True, exist_ok=True)
    ds = load_dataset("neural-bridge/rag-dataset-12000", split="train", streaming=True)

    written = 0
    for row in ds:
        if written >= args.n:
            break
        context = (row.get("context") or "").strip()
        if not context:
            continue
        (OUT / f"hf_{written:04d}.txt").write_text(context, encoding="utf-8")
        written += 1

    print(f"Wrote {written} sample documents to {OUT}")
    print("Next: python scripts/ingest.py --source corpus/hf_sample --origin hf_sample")


if __name__ == "__main__":
    main()
