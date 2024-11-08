from __future__ import annotations

import asyncio
import os
from abc import ABC, abstractmethod
from typing import Optional

import aiofiles
import aiofiles.os
from yarl import URL

from src.utils.hash import generate_sha

from .types import PageMeta

__all__ = ("AbstractCache", "Cache")


class AbstractCache(ABC):
    @abstractmethod
    async def set_meta(self, url: URL, meta: PageMeta) -> None:
        """
        Set metadata for specified URL.

        :param url: URL of the page.
        :param meta: Page metadata.
        """
        pass

    @abstractmethod
    async def get_meta(self, url: URL) -> Optional[PageMeta]:
        """
        Get metadata for specified URL.

        :param url: URL of the page.
        :return: Page metadata if exists; None otherwise.
        """
        pass

    @abstractmethod
    async def set_page(self, url: URL, page: str) -> None:
        """
        Set page content for specified URL.

        :param url: URL of the page.
        :param page: Page content.
        """
        pass

    @abstractmethod
    async def get_page(self, url: URL) -> str:
        """
        Get page content for specified URL.

        :param url: URL of the page.
        :return: Page content.
        """
        pass

    @abstractmethod
    async def delele_page(self, url: URL) -> None:
        """
        Forget page content for specified URL.

        :param url: URL of the page.
        """
        pass


class Cache(AbstractCache):
    def __init__(
        self, path: str, *, loop: Optional[asyncio.AbstractEventLoop] = None
    ) -> None:
        """
        :param path: Path to store the cache.
        :param loop: Asynchronous event loop.
        """
        self._path = path

        self._loop = loop or asyncio.get_event_loop()

        # Create a cache directory if it does not already exist
        os.makedirs(self._path, exist_ok=True)

    async def set_meta(self, url: URL, meta: PageMeta) -> None:
        """
        Set metadata for specified URL.

        :param url: URL of the page.
        :param meta: Page metadata.
        """
        filename = self._generate_filename(url, ".json")
        await self._write_file(filename, meta.serialize())

    async def get_meta(self, url: URL) -> Optional[PageMeta]:
        """
        Get metadata for specified URL.

        :param url: URL of the page.
        :return: Page metadata if exists; None otherwise.
        """
        filename = self._generate_filename(url, ".json")
        try:
            return PageMeta.parse(await self._read_file(filename))
        except FileNotFoundError:
            return None

    async def set_page(self, url: URL, page: str) -> None:
        """
        Set page content for specified URL.

        :param url: URL of the page.
        :param page: Page content.
        """
        filename = self._generate_filename(url, ".bin")
        await self._write_file(filename, page)

    async def get_page(self, url: URL) -> str:
        """
        Get page content for specified URL.

        :param url: URL of the page.
        :return: Page content.
        """
        filename = self._generate_filename(url, ".bin")
        return await self._read_file(filename)

    async def delele_page(self, url: URL) -> None:
        """
        Forget page content for specified URL.

        :param url: URL of the page.
        """
        filename = self._generate_filename(url, ".bin")
        await aiofiles.os.remove(filename, loop=self._loop)

    def _generate_filename(self, url: URL, ext: str) -> str:
        """
        Build a filename from a URL.

        :param url: URL of the page.
        :param ext: File extension.
        """
        return os.path.join(self._path, generate_sha(url.human_repr()) + ext)

    async def _write_file(self, filename: str, data: str) -> None:
        """
        Write data asynchronously to a file.

        :param filename: Path to the file.
        :param data: File content.
        """
        async with aiofiles.open(filename, "w", loop=self._loop) as file:
            await file.write(data)

    async def _read_file(self, filename: str) -> str:
        """
        Read data asynchronously from a file.

        :param filename: Path to the file.
        :return: File content.
        """
        async with aiofiles.open(filename, "r", loop=self._loop) as file:
            return await file.read()
