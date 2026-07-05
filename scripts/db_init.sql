-- Schema for the RAG knowledge base.
-- One row = one chunk of a source document + its embedding vector.

CREATE EXTENSION IF NOT EXISTS vector;

DROP TABLE IF EXISTS docs;
CREATE TABLE docs (
    id        BIGSERIAL PRIMARY KEY,
    source    TEXT   NOT NULL,                    -- provenance: the file the chunk came from
    origin    TEXT   NOT NULL DEFAULT 'curated',  -- 'curated' | 'hf_sample' | 'poisoned'
    content   TEXT   NOT NULL,                    -- the raw chunk text
    embedding vector(768) NOT NULL                -- nomic-embed-text is 768-dimensional
);

-- HNSW index for fast approximate nearest-neighbour search under COSINE distance.
-- The `<=>` operator in query.py uses this opclass. HNSW needs no training step,
-- which makes it ideal for a small demo corpus.
CREATE INDEX IF NOT EXISTS docs_embedding_idx
    ON docs USING hnsw (embedding vector_cosine_ops);

-- The `origin` column lets the security demo add/remove the poisoned document
-- cleanly and supports the "source vetting / provenance" mitigation narrative.
CREATE INDEX IF NOT EXISTS docs_origin_idx ON docs (origin);
