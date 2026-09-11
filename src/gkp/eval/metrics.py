"""Deterministic retrieval metrics.

Pure functions over gold chunk identifiers. No database, no model, no network:
these are arithmetic, and every one is unit-tested against hand-computed values
(ADR-003).

Conventions, both chosen to avoid silently biasing aggregates:

* An **undefined** metric returns ``nan``, never ``0.0``. Empty gold sets and
  ``k <= 0`` are undefined, not "scored zero" — collapsing the two would drag
  every mean that averages over a mixed set.
* ``retrieved`` is ordered best-first, exactly as a retriever returns it.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

__all__ = [
    "mean_ignoring_nan",
    "ndcg_at_k",
    "precision_at_k",
    "recall_at_k",
    "reciprocal_rank",
]

Gold = frozenset[str] | set[str]


def _top_k(retrieved: Sequence[str], k: int) -> list[str]:
    if k <= 0:
        return []
    return list(retrieved[:k])


def recall_at_k(retrieved: Sequence[str], gold: Gold, k: int) -> float:
    """Proportion of the gold set that appears in the top ``k``.

    The metric that matters most for retrieval: if a gold chunk is never
    retrieved, no amount of reranking can recover it.
    """
    if not gold:
        return math.nan
    hits = len(set(_top_k(retrieved, k)) & set(gold))
    return hits / len(gold)


def precision_at_k(retrieved: Sequence[str], gold: Gold, k: int) -> float:
    """Proportion of the top ``k`` that is gold.

    Note this is computed over ``k``, not over ``len(retrieved)``: a retriever
    that returns 3 rows when asked for 10 is penalised for the shortfall rather
    than rewarded for an empty tail.
    """
    if not gold or k <= 0:
        return math.nan
    hits = len(set(_top_k(retrieved, k)) & set(gold))
    return hits / k


def reciprocal_rank(retrieved: Sequence[str], gold: Gold, k: int) -> float:
    """``1 / rank`` of the first gold chunk in the top ``k``, else ``0.0``.

    Unlike the other metrics this is genuinely ``0.0`` — and not ``nan`` — when
    nothing is found, because "found nothing" is a scored outcome rather than an
    undefined one. An empty gold set is still ``nan``.
    """
    if not gold:
        return math.nan
    for rank, chunk_id in enumerate(_top_k(retrieved, k), start=1):
        if chunk_id in gold:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(retrieved: Sequence[str], gold: Gold, k: int) -> float:
    """Normalised discounted cumulative gain with binary relevance.

    Rewards placing gold chunks *early*, which recall@k cannot express — two
    systems with identical recall but different rank order are not equally
    useful to a downstream reader.
    """
    if not gold or k <= 0:
        return math.nan

    dcg = sum(
        1.0 / math.log2(rank + 1)
        for rank, chunk_id in enumerate(_top_k(retrieved, k), start=1)
        if chunk_id in gold
    )
    ideal_hits = min(len(gold), k)
    idcg = sum(1.0 / math.log2(rank + 1) for rank in range(1, ideal_hits + 1))
    if idcg == 0.0:  # pragma: no cover - unreachable while k > 0 and gold non-empty
        return math.nan
    return dcg / idcg


def mean_ignoring_nan(values: Sequence[float]) -> float:
    """Mean over the defined values, or ``nan`` if none are defined.

    Undefined rows are excluded rather than treated as zero. The caller is
    responsible for reporting how many rows were excluded, and the report
    helpers do exactly that — a mean over 40 of 120 questions must never be
    printed as if it covered all 120.
    """
    defined = [v for v in values if not math.isnan(v)]
    if not defined:
        return math.nan
    return sum(defined) / len(defined)
