from __future__ import annotations

import asyncio
from typing import Awaitable, Dict, Optional, Set

from tqdm.asyncio import tqdm
from yarl import URL

from src.utils.href import normalize_href
from src.utils.html import extract_hrefs

from .fetcher import Fetcher

__all__ = ("Crawler",)


class Crawler:
    def __init__(
        self,
        fetcher: Fetcher,
        *,
        host: Optional[str] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        pbar: Optional[tqdm] = None,
    ) -> None:
        """
        :param fetcher: Page fetcher.
        :param host: Trusted host.
        :param loop: Asynchronous event loop.
        :param pbar: Progress bar.
        """
        self._fetcher = fetcher

        self._host = host
        self._loop = loop or asyncio.get_event_loop()
        self._pbar = pbar

        # URL -> Task
        self._pool: Dict[URL, asyncio.Task[None]] = {}
        self._done: Set[URL] = set()

    @property
    def done(self) -> Set[URL]:
        """
        Get URLs that have been crawled.

        :return: URLs that have been crawled.
        """
        return self._done

    def __call__(self, url: URL) -> Awaitable[None]:
        """
        Crawl page at specified URL. Create an asynchronous task. Return the
        existing task when the same URL is called again.

        :param url: URL of the page.
        :return: Cached or new task for the specified URL.
        """
        task = self._pool.get(url)

        if task:
            return task

        if self._pbar is not None:
            self._pbar.total += 1

        coro = self._crawl_page(url)
        task = self._loop.create_task(coro)

        self._pool[url] = task

        return task

    async def _crawl_page(self, url: URL) -> None:
        """
        Crawl page at specified URL.

        :param url: URL of the page.
        """
        page = await self._fetcher(url)

        self._done.add(url)

        if self._pbar is not None:
            self._pbar.update(1)

        if page is None:
            return

        hrefs = set(
            normalize_href(href, url)
            for href in extract_hrefs(page)
            if _should_crawl_page(href, self._host)
        )

        # Spawn asynchronous tasks for each URL.
        coros = [self(href) for href in hrefs if href not in self._pool]
        if coros:
            await asyncio.gather(*coros)


def _should_crawl_page(href: URL, host: Optional[str]) -> bool:
    """
    Check if the page should be crawled.

    :param href: URL of the page.
    :param host: Trusted host.
    """
    if href.scheme not in {"http", "https"}:
        return False

    if not href.absolute:
        return True
    if host is None:
        return True

    return href.host == host
