from __future__ import annotations

import asyncio
from contextlib import suppress
from datetime import datetime, timedelta, timezone
from typing import Optional

import aiohttp
from yarl import URL

from src.utils.date import is_date_past
from src.utils.hash import generate_sha

from .cache import AbstractCache
from .types import PageMeta

__all__ = ("Fetcher",)


class Fetcher:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        timeout: aiohttp.ClientTimeout,
        cache: bool = True,
        *,
        cache_map: Optional[AbstractCache] = None,
        cache_ttl: Optional[timedelta] = None,
    ) -> None:
        """
        :param session: Client session.
        :param timeout: Client timeout.
        :param cache: Whether to cache fetched pages.
        :param cache_map: Cache map.
        :param cache_ttl: Cache TTL.
        """
        self._session = session
        self._timeout = timeout
        self._cache = cache

        if cache:
            if cache_map is None:
                raise ValueError("Cache map required if caching is enabled")
            if cache_ttl is None:
                raise ValueError("Cache TTL required if caching is enabled")

            self._cache_map = cache_map
            self._cache_ttl = cache_ttl

    async def __call__(self, url: URL) -> Optional[bytes]:
        """
        Fetch page at specified URL. Cache if enabled.

        :param url: URL of the page.
        :return: Page content if page exists; None otherwise.
        """
        if not self._cache:
            return await self._fetch_page(url)

        meta = await self._cache_map.get_meta(url)

        if meta is None or is_date_past(meta.exp):
            return await self._cache_page(url, meta)

        if meta.sha is None:
            return None

        return await self._cache_map.get_page(url)

    async def _fetch_page(self, url: URL) -> Optional[bytes]:
        """
        Fetch URL and return the page content.

        :param url: URL of the page.
        :return: Page content if page exists; None otherwise.
        """
        with suppress(asyncio.TimeoutError):
            async with self._session.get(url, timeout=self._timeout) as res:
                if _should_continue_fetching(res):
                    return await res.read()

    async def _cache_page(
        self, url: URL, last_meta: Optional[PageMeta]
    ) -> Optional[bytes]:
        """
        Fetch URL and cache the result.

        :param url: URL of the page.
        :param last_meta: Last metadata.
        :return: Page content if page exists; None otherwise.
        """
        page = await self._fetch_page(url)

        sha = generate_sha(page) if page else None
        now = datetime.now(timezone.utc)

        next_meta = PageMeta(
            url=url.human_repr(),  # type: ignore
            sha=sha,
            exp=now + self._cache_ttl,
            iat=now,
        )

        await self._store_page(url, page, last_meta, next_meta)

        return page

    async def _store_page(
        self,
        url: URL,
        page: Optional[bytes],
        last_meta: Optional[PageMeta],
        next_meta: PageMeta,
    ) -> None:
        """
        Put page content and metadata into cache map.

        :param url: URL of the page.
        :param page: Page content.
        :param last_meta: Last metadata.
        :param next_meta: Next metadata.
        """
        if _should_set_meta_only(last_meta, next_meta):
            await self._cache_map.set_meta(url, next_meta)
        elif page:
            await asyncio.gather(
                self._cache_map.set_meta(url, next_meta),
                self._cache_map.set_page(url, page),
            )
        else:
            await asyncio.gather(
                self._cache_map.set_meta(url, next_meta),
                self._cache_map.delele_page(url),
            )


def _should_continue_fetching(res: aiohttp.ClientResponse) -> bool:
    """
    Check if response should be received. Only HTML responses are accepted.

    :param res: Response from the server.
    :return: True if it is appropriate to receive the response next; False
        otherwise.
    """
    if res.status == 200:
        return "text/html" in res.headers.get("Content-Type", "").lower()

    return False


def _should_set_meta_only(last_meta: Optional[PageMeta], next_meta: PageMeta) -> bool:
    """
    Check if only metadata should be updated.

    :param last_meta: Last metadata.
    :param next_meta: Next metadata.
    :return: True if only metadata should be updated; False otherwise.
    """
    if last_meta is None:
        return next_meta.sha is None

    return last_meta.sha == next_meta.sha
