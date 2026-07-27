# ADR-002: HybridRAG Document Assistant — Corpus & Retrieval Design

## Context
Following Module H1 (Theis pumping test analysis), the goal was to add
a document-intelligence capability reusing the HybridRAG architecture
from the AI/ML portfolio's Module 2, applied to hydrogeology and
groundwater remediation content, with the ability to also query
user-uploaded PDFs.

## Decision 1: Original notes as the default corpus, not textbook excerpts
The default, publicly-deployed knowledge base consists of original
explanatory notes written to summarize established hydrogeology and
remediation concepts (contaminant transport, monitored natural
attenuation, bioremediation, engineered remediation technologies,
geochemistry fundamentals) — not excerpts or close paraphrases of any
specific copyrighted textbook (e.g., Appelo & Postma; Domenico &
Schwartz; Hinchee). This keeps the publicly-deployed app free of
copyright exposure while still demonstrating a real, working retrieval
system over genuine technical content.

## Decision 2: PDF upload for personal/session use
A user-facing PDF upload feature lets anyone (including the portfolio
owner, using their own legally-owned copies of reference textbooks)
query their own documents at runtime. Uploaded content is processed
in-memory for the session only and is not persisted or added to the
public default corpus — functionally similar to any "chat with your
document" tool, and legally no different from a person reading their
own book with a better search function.

## Decision 3: TF-IDF + cosine similarity instead of transformer embeddings
Module 2 (the AI/ML portfolio's original HybridRAG) uses
sentence-transformer embeddings (all-MiniLM-L6-v2) with FAISS. This
module instead uses TF-IDF vectorization with cosine similarity.

Reasoning:
- The corpus here is small and domain-specific (a handful of documents
  plus whatever a user uploads), where TF-IDF's term-level transparency
  is arguably more useful than dense embeddings — a reviewer can see
  exactly which terms drove a match.
- Avoids a heavy transformer-model dependency, keeping the app's
  resource footprint smaller for Streamlit Community Cloud's free-tier
  CPU limits (see: throttling encountered on Module H1).
- The *architecture* — blending a vector-similarity score with a
  keyword-overlap score via the same `α·VectorSim + (1−α)·KeywordScore`
  formula — is preserved and reused identically; only the vector
  representation method differs. This is a deliberate, documented
  trade-off, not an oversight.

## Decision 4: Extractive retrieval by default, generation as an optional add-on
The deployed default returns ranked source passages directly (extractive
retrieval) rather than a synthesized LLM-generated answer, since
generation requires an API key (e.g., Groq, as used in Module 1) that
isn't assumed to be present in every deployment context. The retrieval
layer is structured so a generation step (passing the top-k retrieved
chunks to an LLM as context) can be added on top without changing the
retrieval logic — the same layered pattern as Module 1's agent design.

## Consequences
- Public deployment is copyright-safe by construction, not by
  after-the-fact review.
- The tool is honest about being retrieval-only unless an LLM API is
  connected — no overstated "AI answers your questions" framing.
- Swapping in transformer embeddings later (e.g., if resource limits
  allow) is a contained change to `hydro_rag.py` only.