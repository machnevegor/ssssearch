import asyncio
from typing import Optional, Set

import nltk
from bs4 import BeautifulSoup
from html2text import HTML2Text
from tqdm.asyncio import tqdm
from yarl import URL

from .crawler import Crawler
from .fetcher import Fetcher
from .indexer import Indexer

# HTML-to-Markdown converter
h = HTML2Text()
h.ignore_links = True
h.ignore_images = True

# Sentence tokenizer
nltk.download("punkt")


__all__ = ("Scraper",)


class Scraper:
    def __init__(
        self,
        fetcher: Fetcher,
        indexer: Indexer,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        """
        :param fetcher: Page fetcher.
        :param indexer: Page indexer.
        :param loop: Asynchronous event loop.
        """
        self._fetcher = fetcher
        self._indexer = indexer

        self._loop = loop or asyncio.get_event_loop()

    async def crawl_page(
        self, url: URL, *, host: Optional[str] = None, pbar: Optional[tqdm] = None
    ) -> Set[URL]:
        """
        Crawl page at specified URL.

        :param url: URL of the page.
        :param host: Trusted host.
        :param pbar: Progress bar.
        """
        crawl = Crawler(self._fetcher, host=host, loop=self._loop, pbar=pbar)

        await crawl(url)

        return crawl.done

    def index_page(self, url: URL, html: str) -> None:
        """
        Index page at specified URL.

        :param url: URL of the page.
        :param html: HTML content.
        """
        soup = BeautifulSoup(html, "html.parser")
        tag = soup.find("div", {"class": "mw-parser-output"})

        if tag is None:
            return

        text = h.handle(str(tag))
        tokens = nltk.sent_tokenize(" ".join(tag.stripped_strings))

        self._indexer.append(url, text, tokens)
