from __future__ import annotations

from typing import Sequence, Tuple

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

__all__ = ("Chunker",)


class Chunker:
    def __init__(
        self,
        sentences: Sequence[Tuple[str, np.ndarray]],
        *,
        dimension: int,
        threshold: float,
    ) -> None:
        """
        :param sentences: Sequence of token-embedding pairs.
        :param dimension: Embedding dimension.
        :param threshold: Similarity threshold.
        """
        self._sentences = sentences

        self._dimension = dimension
        self._threshold = threshold

        self._cursor = 0

    def __iter__(self) -> Chunker:
        return self

    def __next__(self) -> Tuple[str, np.ndarray]:
        if self._cursor >= len(self._sentences):
            raise StopIteration

        chunk = []
        cumulative_embedding = np.zeros(self._dimension)
        count = 0

        while self._cursor < len(self._sentences):
            token, embedding = self._sentences[self._cursor]

            if count and self._should_close_chunk(
                embedding, cumulative_embedding, count
            ):
                break

            chunk.append(token)
            cumulative_embedding += embedding
            count += 1

            self._cursor += 1

        return " ".join(chunk), cumulative_embedding / count

    def _should_close_chunk(
        self, embedding: np.ndarray, cumulative_embedding: np.ndarray, count: int
    ) -> bool:
        """
        Check if the chunk should be closed.

        :param embedding: Current token embedding.
        :param cumulative_embedding: Cumulative embedding of the chunk.
        :param count: Number of tokens in the chunk.
        :return: True if the chunk should be closed; False otherwise.
        """
        similarity_score = _measure_similarity(embedding, cumulative_embedding / count)

        return similarity_score < self._threshold


def _measure_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Measure the similarity between two vectors.

    :param a: Vector A.
    :param b: Vector B.
    :return: Similarity score.
    """
    return cosine_similarity(a.reshape(1, -1), b.reshape(1, -1))[0][0]
