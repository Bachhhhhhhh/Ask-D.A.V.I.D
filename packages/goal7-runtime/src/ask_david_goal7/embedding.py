"""Canonical embedding configuration and offline-safe test provider."""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class EmbeddingConfig:
    """Model identity and vector shape shared by indexing and retrieval."""

    model_id: str
    dimension: int

    def validate(self, vector: tuple[float, ...] | list[float]) -> None:
        if len(vector) != self.dimension:
            raise ValueError(
                f"embedding dimension mismatch: expected {self.dimension}, got {len(vector)}"
            )


# Databricks-hosted GTE Large returns a fixed 1024-dimensional vector.  The
# SQL bundle uses this exact model ID; the local provider below is only a
# deterministic offline substitute and never claims to be the live model.
CANONICAL_EMBEDDING_CONFIG = EmbeddingConfig(
    model_id="databricks-gte-large-en",
    dimension=1024,
)


class EmbeddingProvider(Protocol):
    config: EmbeddingConfig

    def embed(self, text: str) -> tuple[float, ...]:
        """Return one vector using the provider's declared config."""


class HashEmbeddingProvider:
    """Deterministic, dependency-free provider used only by offline tests.

    It deliberately has the same vector shape as the canonical model so that
    contract, ACL, and upsert behavior can be tested without network calls.
    Connected validation must use the Databricks provider configured in the
    Goal 7 SQL bundle.
    """

    def __init__(self, config: EmbeddingConfig = CANONICAL_EMBEDDING_CONFIG) -> None:
        self.config = config

    def embed(self, text: str) -> tuple[float, ...]:
        values: list[float] = []
        counter = 0
        while len(values) < self.config.dimension:
            digest = hashlib.sha256(f"{self.config.model_id}\0{counter}\0{text}".encode()).digest()
            for offset in range(0, len(digest), 4):
                raw = int.from_bytes(digest[offset : offset + 4], "big", signed=False)
                values.append((raw / 2**31) - 1.0)
                if len(values) == self.config.dimension:
                    break
            counter += 1
        magnitude = math.sqrt(sum(value * value for value in values))
        if magnitude == 0:
            return tuple(0.0 for _ in values)
        return tuple(value / magnitude for value in values)
