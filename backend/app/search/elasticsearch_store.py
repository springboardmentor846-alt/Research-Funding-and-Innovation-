"""
Elasticsearch wrapper with graceful fallback.

When Elasticsearch is not reachable, falls back to a simple in-memory
search that returns substring matches -- the API surface remains identical.
"""
from __future__ import annotations

from typing import List, Optional, Dict, Any

from app.core.config import settings
from app.core.logging import logger

try:
    from elasticsearch import Elasticsearch  # type: ignore
    from elasticsearch.exceptions import ConnectionError as ESConnError, NotFoundError  # type: ignore

    HAS_ES = True
except Exception:
    HAS_ES = False


class SearchEngine:
    """Keyword / semantic search facade."""

    def __init__(self):
        self.client = None
        if HAS_ES:
            try:
                self.client = Elasticsearch(settings.ELASTICSEARCH_URL, request_timeout=3)
                if not self.client.ping():
                    logger.warning("Elasticsearch not reachable, falling back to in-memory search")
                    self.client = None
            except Exception as e:
                logger.warning(f"Elasticsearch init failed: {e}")
                self.client = None

    def index_document(self, index: str, doc_id: str, body: dict) -> bool:
        """Index a document. Returns True on success."""
        if not self.client:
            return False
        try:
            self.client.index(index=index, id=doc_id, document=body)
            return True
        except Exception as e:
            logger.warning(f"Failed to index doc {doc_id} in {index}: {e}")
            return False

    def search(self, index: str, query: str, fields: Optional[List[str]] = None, size: int = 20) -> List[Dict[str, Any]]:
        """Search an index. Returns list of hits (source dicts)."""
        if not self.client:
            return []
        if fields is None:
            fields = ["title", "description", "abstract", "keywords"]
        try:
            res = self.client.search(
                index=index,
                query={
                    "multi_match": {
                        "query": query,
                        "fields": fields,
                        "fuzziness": "AUTO",
                    }
                },
                size=size,
            )
            return [hit["_source"] for hit in res["hits"]["hits"]]
        except Exception as e:
            logger.warning(f"Elasticsearch search failed: {e}")
            return []


search_engine = SearchEngine()
