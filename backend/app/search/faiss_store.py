"""
FAISS vector search module.

Provides an in-memory vector store for semantic search over publications,
funding opportunities, and patents. Uses sentence-transformers when available
and falls back to TF-IDF for environments without a GPU/heavy deps.
"""
from __future__ import annotations

import threading
from typing import List, Tuple, Optional

import numpy as np

try:
    import faiss  # type: ignore
    HAS_FAISS = True
except Exception:
    HAS_FAISS = False

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
    HAS_SBERT = True
except Exception:
    HAS_SBERT = False

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.core.logging import logger
from app.ai.text_preprocessing import TextPreprocessor


class FaissVectorStore:
    """Thread-safe vector store with TF-IDF fallback."""

    def __init__(self, dim: int = 384):
        self.dim = dim
        self.lock = threading.Lock()
        self.documents: List[dict] = []
        self.preprocessor = TextPreprocessor()
        self.index = None
        self._tfidf = None
        self._tfidf_matrix = None
        self._embedder = None
        self._mode = "tfidf"
        self._initialize()

    def _initialize(self) -> None:
        if HAS_SBERT:
            try:
                # Lightweight model by default
                self._embedder = SentenceTransformer("all-MiniLM-L6-v2")
                self.dim = self._embedder.get_sentence_embedding_dimension()
                self._mode = "sbert"
                logger.info("FAISS vector store using sentence-transformers")
            except Exception as e:
                logger.warning(f"Failed to load sentence-transformers: {e}")
        if self._mode == "tfidf":
            logger.info("FAISS vector store using TF-IDF fallback")
            self._tfidf = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_df=0.95)
        if HAS_FAISS:
            try:
                self.index = faiss.IndexFlatIP(self.dim)
            except Exception as e:
                logger.warning(f"FAISS init failed: {e}")
                self.index = None

    def add(self, doc_id: str, text: str, payload: dict) -> None:
        """Add a document to the store."""
        with self.lock:
            self.documents.append({"id": doc_id, "text": text, "payload": payload})

    def build(self) -> None:
        """Build the index from added documents. Call after bulk add()."""
        with self.lock:
            if not self.documents:
                return
            texts = [d["text"] for d in self.documents]
            if self._mode == "sbert" and self._embedder is not None:
                try:
                    embeddings = self._embedder.encode(texts, convert_to_numpy=True, show_progress_bar=False)
                    faiss.normalize_L2(embeddings)
                    if self.index is not None and HAS_FAISS:
                        self.index.add(embeddings.astype("float32"))
                    else:
                        self._tfidf_matrix = embeddings
                except Exception as e:
                    logger.warning(f"SBERT encode failed, falling back to TF-IDF: {e}")
                    self._mode = "tfidf"
            if self._mode == "tfidf":
                corpus = self.preprocessor.build_corpus(texts)
                if not any(corpus):
                    return
                self._tfidf_matrix = self._tfidf.fit_transform(corpus)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float, dict]]:
        """Return top-K (doc_id, score, payload) tuples for a query."""
        with self.lock:
            if not self.documents:
                return []
            if self._mode == "sbert" and self._embedder is not None:
                try:
                    q_vec = self._embedder.encode([query], convert_to_numpy=True)
                    faiss.normalize_L2(q_vec)
                    if self.index is not None and self.index.ntotal > 0 and HAS_FAISS:
                        scores, indices = self.index.search(q_vec.astype("float32"), min(top_k, len(self.documents)))
                        results = []
                        for score, idx in zip(scores[0], indices[0]):
                            if 0 <= idx < len(self.documents):
                                results.append((self.documents[idx]["id"], float(score), self.documents[idx]["payload"]))
                        return results
                    if self._tfidf_matrix is not None:
                        sims = cosine_similarity(q_vec, self._tfidf_matrix).flatten()
                        order = sims.argsort()[::-1][:top_k]
                        return [(self.documents[i]["id"], float(sims[i]), self.documents[i]["payload"]) for i in order]
                except Exception as e:
                    logger.warning(f"FAISS search failed: {e}")
            # TF-IDF fallback
            cleaned = " ".join(self.preprocessor.tokenize(query))
            if not cleaned or self._tfidf is None or self._tfidf_matrix is None:
                return []
            q_vec = self._tfidf.transform([cleaned])
            sims = cosine_similarity(q_vec, self._tfidf_matrix).flatten()
            order = sims.argsort()[::-1][:top_k]
            return [(self.documents[i]["id"], float(sims[i]), self.documents[i]["payload"]) for i in order]

    def clear(self) -> None:
        with self.lock:
            self.documents = []
            if self.index is not None and HAS_FAISS:
                self.index.reset()
            self._tfidf_matrix = None


# Global store instances by collection
_stores: dict[str, FaissVectorStore] = {}


def get_store(collection: str = "publications") -> FaissVectorStore:
    if collection not in _stores:
        _stores[collection] = FaissVectorStore()
    return _stores[collection]
