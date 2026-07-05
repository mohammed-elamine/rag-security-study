"""Shared helpers for the RAG scripts.

Kept deliberately small so the four moving parts of RAG stay visible:
  1. embed(text)      -> turn text into a vector      (Ollama, nomic-embed-text)
  2. connect()        -> open the vector store        (Postgres + pgvector)
  3. chunk_text(text) -> split documents into pieces
  4. generate(prompt) -> ask the LLM                  (Ollama, gemma2:2b)
"""
import os

import ollama
import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector

load_dotenv()

# --- Configuration (all from .env, with safe local defaults) ---
DB = dict(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=os.getenv("POSTGRES_PORT", "5432"),
    dbname=os.getenv("POSTGRES_DB", "ragdb"),
    user=os.getenv("POSTGRES_USER", "rag"),
    password=os.getenv("POSTGRES_PASSWORD", "ragpass"),
)
GEN_MODEL = os.getenv("GEN_MODEL", "gemma2:2b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
TOP_K = int(os.getenv("TOP_K", "4"))

_client = ollama.Client(host=os.getenv("OLLAMA_HOST", "http://localhost:11434"))


def connect():
    """Open a Postgres connection with the pgvector type adapter registered."""
    conn = psycopg.connect(**DB)
    register_vector(conn)
    return conn


def embed(text: str) -> list[float]:
    """Return the 768-d embedding of a piece of text."""
    return _client.embeddings(model=EMBED_MODEL, prompt=text)["embedding"]


def generate(prompt: str) -> str:
    """Ask the local LLM. temperature=0 keeps the report reproducible."""
    resp = _client.generate(model=GEN_MODEL, prompt=prompt, options={"temperature": 0})
    return resp["response"].strip()


def chunk_text(text: str, target_words: int = 200, overlap: int = 30) -> list[str]:
    """Split text into ~target_words windows with a small overlap.

    Short documents (most of the curated corpus) come back as a single chunk,
    which keeps each fact together.
    """
    words = text.split()
    if len(words) <= target_words:
        return [text.strip()] if text.strip() else []
    chunks, step = [], target_words - overlap
    for start in range(0, len(words), step):
        piece = " ".join(words[start:start + target_words]).strip()
        if piece:
            chunks.append(piece)
        if start + target_words >= len(words):
            break
    return chunks
