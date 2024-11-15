from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple

import numpy as np
from faiss import IndexFlatL2
from sentence_transformers import SentenceTransformer
from yarl import URL

from .chunker import Chunker

__all__ = ("Indexer",)


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
        self._documents: List[Tuple[URL, str]] = []

    def add(self, url: URL, tokens: List[str]) -> None:
        """
        Add page tokens to index.

        :param url: Page URL.
        :param tokens: Page tokens.
        """
        embeddings = self._embed_tokens(tokens)

        chunker = Chunker(
            list(zip(tokens, embeddings)),
            dimension=self._dimension,
            threshold=self._threshold,
        )

        for paragraph, embedding in chunker:
            self._index.add(embedding.reshape(1, -1))  # type: ignore
            self._documents.append((url, paragraph))

    def search(self, query: str, k: int) -> List[Tuple[URL, str]]:
        """
        Search for similar documents.

        :param query: Query string.
        :param k: Top-k documents.
        :return: Similar documents.
        """
        embeddings = self._embed_tokens([query])

        _, indices = self._index.search(embeddings.reshape(1, -1), k)  # type: ignore

        return [self._documents[i] for i in indices[0]]

    def _embed_tokens(self, tokens: List[str]) -> np.ndarray:
        """
        Embed tokens.

        :param tokens: Tokens.
        :return: Embeddings.
        """
        with ThreadPoolExecutor() as executor:
            embeddings = list(executor.map(self._model.encode, tokens))

        return np.array(embeddings, dtype=np.float32)
