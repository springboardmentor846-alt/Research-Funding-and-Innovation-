"""Shared async HTTP client for patent-intel providers.

Centralises connection pooling, timeouts, retries with exponential
backoff, and a uniform user-agent string.  Mirrors
``funding_intel.core.http_client`` so the two services share
behaviour.
"""
from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, Optional

import httpx

from app.core.logging import logger
from .config import patent_intel_settings


class PatentProviderHTTPClient:
    """Async HTTP client with retry, backoff, and provider-aware logging."""

    def __init__(
        self,
        *,
        name: str,
        base_url: str,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        backoff: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        s = patent_intel_settings
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout or s.HTTP_TIMEOUT_SECONDS
        self.max_retries = max_retries or s.HTTP_MAX_RETRIES
        self.backoff = backoff or s.HTTP_RETRY_BACKOFF_SECONDS

        limits = httpx.Limits(
            max_connections=s.HTTP_MAX_CONNECTIONS,
            max_keepalive_connections=s.HTTP_MAX_KEEPALIVE,
        )
        ua = s.HTTP_USER_AGENT
        default_headers = {"User-Agent": ua, "Accept": "application/json"}
        if headers:
            default_headers.update(headers)

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            limits=limits,
            headers=default_headers,
            follow_redirects=True,
            http2=False,
        )

    async def aclose(self) -> None:
        try:
            await self._client.aclose()
        except Exception:  # pragma: no cover - shutdown best-effort
            pass

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        expect_json: bool = True,
    ) -> httpx.Response:
        """Issue a request with retry/backoff. Returns the final response."""
        attempt = 0
        last_exc: Optional[Exception] = None
        url = path if path.startswith("/") else f"/{path}"

        while attempt <= self.max_retries:
            attempt += 1
            started = time.perf_counter()
            try:
                response = await self._client.request(
                    method,
                    url,
                    params=params,
                    json=json,
                    data=data,
                    headers=headers,
                )
                elapsed_ms = (time.perf_counter() - started) * 1000.0

                if response.status_code in (429, 500, 502, 503, 504):
                    if attempt <= self.max_retries:
                        delay = self.backoff * (2 ** (attempt - 1))
                        logger.warning(
                            f"[{self.name}] HTTP {response.status_code} on "
                            f"{method} {url} (attempt {attempt}/{self.max_retries}); "
                            f"retrying in {delay:.1f}s"
                        )
                        await asyncio.sleep(delay)
                        continue
                    response.raise_for_status()

                if expect_json and response.headers.get("content-type", "").split(";")[0].strip() != "application/json":
                    if not response.text.lstrip().startswith(("{", "[")):
                        raise httpx.HTTPError(
                            f"Non-JSON response (status {response.status_code}, "
                            f"content-type {response.headers.get('content-type')!r})"
                        )
                return response

            except (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError) as exc:
                last_exc = exc
                if attempt <= self.max_retries:
                    delay = self.backoff * (2 ** (attempt - 1))
                    logger.warning(
                        f"[{self.name}] {exc.__class__.__name__} on "
                        f"{method} {url} (attempt {attempt}/{self.max_retries}); "
                        f"retrying in {delay:.1f}s"
                    )
                    await asyncio.sleep(delay)
                    continue
                break

        if last_exc:
            raise last_exc
        raise httpx.HTTPError(f"[{self.name}] request failed without exception")

    async def get_json(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        response = await self.request("GET", path, params=params)
        return response.json()

    async def post_json(
        self,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        response = await self.request("POST", path, params=params, json=json)
        return response.json()
