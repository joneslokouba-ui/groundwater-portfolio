"""
HybridRAG retrieval for hydrogeology/remediation documents.

Reuses the same scoring formula as Module 2 (Supervisor Multi-Agent +
HybridRAG): a weighted blend of vector similarity and keyword overlap.

    score = alpha * VectorSim + (1 - alpha) * KeywordScore

Vector similarity here uses TF-IDF + cosine similarity (lightweight,
no GPU/large-model dependency needed) rather than a transformer
embedding model — a deliberate architecture choice documented in
ADR-002, appropriate for a small, domain-specific document set where
transparency of the scoring is itself valuable (a reviewer can see
exactly which terms drove a match).
"""

import re
import numpy as np
from dataclasses import dataclass
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class Chunk:
    text: str
    source: str
    chunk_id: int


def chunk_text(text: str, source: str, chunk_size: int = 700, overlap: int = 100) -> List[Chunk]:
    """Split text into overlapping word-based chunks."""
    words = text.split()
    chunks = []
    start = 0
    cid = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_words = words[start:end]
        chunks.append(Chunk(text=" ".join(chunk_words), source=source, chunk_id=cid))
        cid += 1
        if end == len(words):
            break
        start = end - overlap
    return chunks


def keyword_score(query: str, text: str) -> float:
    """
    Simple, transparent keyword overlap score: fraction of unique
    query terms (excluding very common stopwords) found in the chunk.
    """
    stopwords = {
        "the", "a", "an", "of", "in", "on", "is", "are", "and", "or",
        "to", "for", "what", "how", "does", "do", "which", "why", "with",
        "at", "by", "from", "this", "that", "it", "as", "be", "can",
    }
    q_terms = {w.lower() for w in re.findall(r"[a-zA-Z]+", query) if w.lower() not in stopwords}
    if not q_terms:
        return 0.0
    text_lower = text.lower()
    hits = sum(1 for t in q_terms if t in text_lower)
    return hits / len(q_terms)


class HybridRetriever:
    """
    Builds a TF-IDF index over a set of chunks and retrieves the
    top-k most relevant chunks for a query using the Hybrid RAG
    formula: alpha * vector_similarity + (1 - alpha) * keyword_score.
    """

    def __init__(self, chunks: List[Chunk]):
        self.chunks = chunks
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.doc_matrix = self.vectorizer.fit_transform([c.text for c in chunks])

    def retrieve(self, query: str, top_k: int = 4, alpha: float = 0.6):
        query_vec = self.vectorizer.transform([query])
        vector_sims = cosine_similarity(query_vec, self.doc_matrix)[0]

        results = []
        for i, chunk in enumerate(self.chunks):
            v_sim = float(vector_sims[i])
            k_score = keyword_score(query, chunk.text)
            hybrid = alpha * v_sim + (1 - alpha) * k_score
            results.append({
                "chunk": chunk,
                "vector_sim": v_sim,
                "keyword_score": k_score,
                "hybrid_score": hybrid,
            })

        results.sort(key=lambda r: r["hybrid_score"], reverse=True)
        return results[:top_k]


def build_retriever_from_texts(texts_with_sources: List[tuple]) -> HybridRetriever:
    """texts_with_sources: list of (text, source_name) tuples."""
    all_chunks = []
    for text, source in texts_with_sources:
        all_chunks.extend(chunk_text(text, source))
    return HybridRetriever(all_chunks)