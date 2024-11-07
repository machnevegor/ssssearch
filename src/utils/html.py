from __future__ import annotations

from typing import Generator

from bs4 import BeautifulSoup
from yarl import URL

__all__ = ("extract_hrefs",)


def extract_hrefs(html: str) -> Generator[URL, None, None]:
    """
    Extract all hrefs from the HTML content.

    :param html: HTML content.
    :return: Yields all hrefs.
    """
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all("a", href=True):
        yield URL(tag["href"])
