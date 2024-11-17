from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
from faiss import IndexFlatL2
from sentence_transformers import SentenceTransformer
from yarl import URL

from .chunker import Chunker


class Indexer:
    def __init__(
        self, model: SentenceTransformer, *, dimension: int, threshold: float
    ) -> None:
        """
        :param model: Sentence transformer model.
        :param dimension: Embedding dimension.
        :param threshold: Similarity threshold.
        """
        self._model = model

        self._dimension = dimension
        self._threshold = threshold

        self._index = IndexFlatL2(self._dimension)
        self._table: List[URL] = []

        self._pages: Dict[URL, str] = {}

    def append(self, url: URL, page: str, tokens: List[str]) -> None:
        """
        Append a page to the index.

        :param url: URL of the page.
        :param page: Content of the page.
        :param tokens: List of tokens.
        """
        embeddings = self._embed_tokens(tokens)
        pairs = list(zip(tokens, embeddings))

        chunker = Chunker(pairs, dimension=self._dimension, threshold=self._threshold)

        for _, embedding in chunker:
            self._index.add(embedding)  # type: ignore
            self._table.append(url)

        self._pages[url] = page

    def search(self, query: str, k: int) -> List[Tuple[URL, str]]:
        """
        Search for similar pages based on the query.

        :param query: Query string.
        :param k: Top-k matches.
        :return: List of URLs and their corresponding pages.
        """
        embeddings = self._embed_tokens([query])

        _, indices = self._index.search(embeddings, k)  # type: ignore
        urls = set(self._table[i] for i in indices[0])

        return [(url, self._pages[url]) for url in urls]

    def _embed_tokens(self, tokens: List[str]) -> np.ndarray:
        """
        Embed tokens using the sentence transformer model.

        :param tokens: List of tokens.
        :return: Array of embeddings.
        """
        return self._model.encode(tokens)
