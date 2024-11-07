from __future__ import annotations

from yarl import URL

__all__ = ("normalize_href",)


def normalize_href(href: URL, base: URL) -> URL:
    """
    Normalize the given href to an absolute URL.

    :param href: Href to normalize.
    :param base: Base URL.
    :return: Absolute URL.
    """
    return href if href.absolute else base.join(href)
