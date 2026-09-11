"""Embedding providers behind a single interface.

Two implementations, and the distinction between them is load-bearing:

* :class:`HashEmbedder` is deterministic, dependency-free, and **semantically
  meaningless**. It hashes tokens into buckets, so it captures lexical overlap and
  nothing else. It exists so the unit suite and CI can exercise the retrieval
  plumbing without a model download.
* :class:`FastEmbedEmbedder` is the real thing: ONNX BGE via ``fastembed``, with
  no torch dependency, so the install is tens of megabytes rather than gigabytes.
  That matters for a project that has to be reproducible on a laptop and in CI.

Because a hash embedder would make every published retrieval number meaningless,
:attr:`Embedder.is_semantic` is part of the interface and the evaluation runner
**refuses to produce a report from a non-semantic embedder** unless explicitly
forced. A number that cannot mean anything should be hard to produce by accident.
"""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod

import numpy as np

__all__ = ["Embedder", "FastEmbedEmbedder", "HashEmbedder", "build_embedder"]


class Embedder(ABC):
    """Embeds text into fixed-width vectors."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Identifier recorded in results, so a number maps to a model."""

    @property
    @abstractmethod
    def dim(self) -> int:
        """Vector width. Must match ``gkp.db.models.EMBEDDING_DIM``."""

    @property
    def is_semantic(self) -> bool:
        """False when vectors carry no meaning beyond lexical coincidence."""
        return True

    @abstractmethod
    def embed(self, texts: list[str]) -> np.ndarray:
        """Return an ``(len(texts), dim)`` float32 array of L2-normalised rows."""

    def embed_one(self, text: str) -> np.ndarray:
        return np.asarray(self.embed([text])[0], dtype=np.float32)

    @staticmethod
    def _normalise(matrix: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        # Cosine distance against a zero vector is undefined rather than zero;
        # nudge the norm so an empty chunk cannot produce NaNs downstream.
        np.maximum(norms, 1e-12, out=norms)
        return np.asarray(matrix / norms, dtype=np.float32)


class HashEmbedder(Embedder):
    """Deterministic token-hash projection. **Not semantically meaningful.**

    Used for plumbing tests and for CI runs that must not download a model. It
    will retrieve chunks sharing vocabulary with a query and nothing more, which
    is exactly why its output must not be published as a retrieval measurement.
    """

    def __init__(self, dim: int = 384) -> None:
        self._dim = dim

    @property
    def name(self) -> str:
        return f"hash-{self._dim}"

    @property
    def dim(self) -> int:
        return self._dim

    @property
    def is_semantic(self) -> bool:
        return False

    def embed(self, texts: list[str]) -> np.ndarray:
        matrix = np.zeros((len(texts), self._dim), dtype=np.float32)
        for row, text in enumerate(texts):
            for token in text.lower().split():
                digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
                matrix[row, int.from_bytes(digest, "big") % self._dim] += 1.0
        return self._normalise(matrix)


class FastEmbedEmbedder(Embedder):
    """ONNX BGE embeddings via ``fastembed``. No torch."""

    def __init__(self, model_name: str) -> None:
        from fastembed import TextEmbedding  # imported lazily: optional at test time

        self._model_name = model_name
        self._model = TextEmbedding(model_name=model_name)
        probe = next(iter(self._model.embed(["dimension probe"])))
        self._dim = int(probe.shape[0])

    @property
    def name(self) -> str:
        return self._model_name

    @property
    def dim(self) -> int:
        return self._dim

    def embed(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self._dim), dtype=np.float32)
        matrix = np.array(list(self._model.embed(texts)), dtype=np.float32)
        return self._normalise(matrix)


def build_embedder(model_name: str, *, allow_hash: bool = False) -> Embedder:
    """Construct an embedder by name.

    ``"hash"`` selects the non-semantic embedder and must be opted into
    explicitly, so that a meaningless run is never the path of least resistance.
    """
    if model_name in {"hash", "hash-384"}:
        if not allow_hash:
            raise ValueError(
                "Refusing to build the hash embedder implicitly: its vectors are not "
                "semantic and any retrieval number derived from them is meaningless. "
                "Pass allow_hash=True to use it for plumbing tests only."
            )
        return HashEmbedder()
    return FastEmbedEmbedder(model_name)
