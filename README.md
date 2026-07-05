# Local RAG + Security Layer

A fully local Retrieval-Augmented Generation (RAG) pipeline for the Télécom Paris
*Security for Big Data* course. The LLM runs on **Ollama** (native, Metal GPU), the
vector store is **PostgreSQL + pgvector** (Docker). No cloud APIs, no secrets leave
the host. On top of the functional RAG requirement, it adds a small **security layer**:
a threat model and a live *indirect prompt injection* attack + mitigation.

## Architecture (short version)

```
                 embed                     cosine top-k
  documents ───────────────▶  pgvector  ◀──────────────  question
                (nomic-embed-text)                          │
                                                            ▼
                                    [ context + question ] ──▶ gemma2:2b ──▶ answer
                                            (Ollama, native)
```

## Prerequisites
- **Docker** (Desktop on macOS/Windows, or Engine on Linux) — running.
- **Python 3.11+**.
- **Ollama** — either installed natively *or* run in Docker (see deployment modes).

## Portability / deployment modes

The stack runs on **macOS, Linux, or Windows** (use WSL or Git Bash on Windows). Only the
Ollama runtime placement differs; the Python code is identical because it always talks to
Ollama over HTTP at `OLLAMA_HOST` (default `localhost:11434`).

| Mode | Command | When |
|---|---|---|
| **Native Ollama** (default) | `bash scripts/setup.sh` | Ollama installed on host; uses the GPU (Metal on Apple Silicon, CUDA on Linux). Fastest. |
| **Containerized Ollama** | `bash scripts/setup.sh --ollama-docker` | No native Ollama, or you want the whole stack in Docker on any OS. CPU by default (uncomment the GPU block in `docker-compose.yml` for NVIDIA). |

`setup.sh` auto-detects: it uses native Ollama if the `ollama` command exists, otherwise it
falls back to the containerized Ollama automatically.

## Quickstart

```bash
# 1. Bring up the DB, pull models, install deps, create schema
bash scripts/setup.sh
source .venv/bin/activate

# 2. Ingest the curated knowledge base (+ optional HF sample)
python scripts/ingest.py --source corpus/curated --origin curated
python scripts/fetch_hf_sample.py            # optional: pulls ~200 HF rows
python scripts/ingest.py --source corpus/hf_sample --origin hf_sample

# 3. Ask a question — with and without RAG (shows the difference)
python scripts/query.py "What is the Aramis-7 coolant threshold?"
python scripts/query.py --no-rag "What is the Aramis-7 coolant threshold?"

# 4. Generate the prompt/response comparison table (for the report)
python scripts/demo_qa.py

# 5. Security demo: poison the KB, watch naive vs hardened prompts
python security/attack_demo.py
```

## Layout
| Path | Purpose |
|---|---|
| `docker-compose.yml`, `.env.example` | pgvector service + local config |
| `scripts/db_init.sql`, `scripts/setup.sh` | schema + one-shot setup |
| `scripts/ingest.py` | chunk → embed → store |
| `scripts/query.py` | retrieve → generate (`--no-rag` baseline) |
| `scripts/demo_qa.py` | base-vs-RAG results table |
| `corpus/` | curated docs, HF sample, poisoned doc |
| `security/` | threat model + attack/mitigation demo |
| `report/` | diagrams, captured results, PDF build |
