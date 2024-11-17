import asyncio
from dataclasses import dataclass
from datetime import timedelta

import aiohttp
from sentence_transformers import SentenceTransformer
from tqdm.asyncio import tqdm
from yarl import URL

from .cache import Cache
from .fetcher import Fetcher
from .indexer import Indexer
from .scraper import Scraper

# Load pre-trained model
model = SentenceTransformer("sentence-transformers/multi-qa-mpnet-base-dot-v1")

__all__ = ("Indexer", "scrap", "ScrapConfig")


@dataclass
class ScrapConfig:
    root: URL
    host: str

    timeout: aiohttp.ClientTimeout = aiohttp.ClientTimeout(sock_connect=60)

    cache_dir: str = ".cache"
    cache_ttl: timedelta = timedelta(weeks=1)


async def scrap(config: ScrapConfig) -> Indexer:
    loop = asyncio.get_event_loop()

    async with aiohttp.ClientSession(loop=loop) as session:
        cache = Cache(path=config.cache_dir, loop=loop)
        fetcher = Fetcher(
            session, config.timeout, cache_map=cache, cache_ttl=config.cache_ttl
        )

        indexer = Indexer(model, dimension=768, threshold=0.9)

        scraper = Scraper(fetcher, indexer, loop=loop)

        with tqdm(total=0, desc="Crawling") as pbar:
            crawled_urls = await scraper.crawl_page(
                config.root, host=config.host, pbar=pbar
            )

        with tqdm(total=len(crawled_urls), desc="Indexing") as pbar:
            for url in crawled_urls:
                page = await fetcher(url)

                if page:
                    # Note: During the indexing process, HTML content is
                    # converted to markdown. The content is assumed to be in
                    # the `div.mw-parser-output` tag. Otherwise, the content
                    # will NOT be indexed.
                    scraper.index_page(url, page)

                pbar.update(1)

        return indexer
