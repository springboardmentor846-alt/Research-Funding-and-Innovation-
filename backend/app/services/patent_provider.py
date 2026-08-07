"""
Provider Architecture for Multi-Source Patent Data Integration.
Supports local seed database and future APIs: Google Patents, USPTO, and The Lens.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BasePatentProvider(ABC):
    """Abstract base class for patent data source providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns provider identifier name."""
        pass

    @abstractmethod
    async def fetch_patent_by_id(self, patent_id: str) -> Optional[Dict[str, Any]]:
        """Fetch raw patent details by patent number or external ID."""
        pass

    @abstractmethod
    async def search_patents(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search external API for patents matching query string."""
        pass


class LocalPatentDatabaseProvider(BasePatentProvider):
    """Primary local database patent provider."""

    @property
    def provider_name(self) -> str:
        return "local_seed"

    async def fetch_patent_by_id(self, patent_id: str) -> Optional[Dict[str, Any]]:
        # Database query handled via PatentService AsyncSession
        return None

    async def search_patents(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        return []


class GooglePatentsProviderAdapter(BasePatentProvider):
    """Adapter for future Google Patents API / BigQuery Patent Dataset integration."""

    @property
    def provider_name(self) -> str:
        return "google_patents"

    async def fetch_patent_by_id(self, patent_id: str) -> Optional[Dict[str, Any]]:
        # Architecture stub: Ready for Google Patents BigQuery/API integration
        return {
            "source": self.provider_name,
            "external_id": patent_id,
            "status": "ready_for_adapter",
        }

    async def search_patents(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        return []


class USPTOProviderAdapter(BasePatentProvider):
    """Adapter for future USPTO Open Data API integration."""

    @property
    def provider_name(self) -> str:
        return "uspto"

    async def fetch_patent_by_id(self, patent_id: str) -> Optional[Dict[str, Any]]:
        # Architecture stub: Ready for USPTO Patent Examination Data System (PEDS) API
        return {
            "source": self.provider_name,
            "external_id": patent_id,
            "status": "ready_for_adapter",
        }

    async def search_patents(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        return []


class LensApiProviderAdapter(BasePatentProvider):
    """Adapter for future The Lens (lens.org) Patent API integration."""

    @property
    def provider_name(self) -> str:
        return "the_lens"

    async def fetch_patent_by_id(self, patent_id: str) -> Optional[Dict[str, Any]]:
        # Architecture stub: Ready for The Lens API v1/patents endpoint
        return {
            "source": self.provider_name,
            "external_id": patent_id,
            "status": "ready_for_adapter",
        }

    async def search_patents(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        return []
