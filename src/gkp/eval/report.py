"""Result aggregation and reporting.

Two rules this module exists to enforce, both learned from the prototype's
evaluation, which reported four decimals with no indication of how many questions
they covered:

* every mean is printed with its ``n``, and the count of rows excluded as
  undefined is printed next to it;
* every mean carries a bootstrap 95% confidence interval, because a mean over 42
  questions is not a point estimate and printing it as one is a quiet lie.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any

from gkp.eval.metrics import (
    mean_ignoring_nan,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)

__all__ = [
    "BootstrapCI",
    "KsScores",
    "MetricRow",
    "bootstrap_ci",
    "markdown_table",
    "score_question",
]

DEFAULT_KS = (1, 3, 5, 10, 20)


@dataclass(frozen=True)
class BootstrapCI:
    low: float
    high: float
    iterations: int

    def __str__(self) -> str:
        if math.isnan(self.low):
            return "n/a"
        return f"[{self.low:.3f}, {self.high:.3f}]"


def bootstrap_ci(
    values: list[float],
    *,
    iterations: int = 2000,
    seed: int = 20260912,
    alpha: float = 0.05,
) -> BootstrapCI:
    """Percentile bootstrap CI over per-question scores.

    Seeded, so the interval is reproducible and a re-run of an unchanged
    configuration produces an identical report — which is what makes a CI gate
    on this number workable at all.
    """
    defined = [v for v in values if not math.isnan(v)]
    if len(defined) < 2:
        return BootstrapCI(math.nan, math.nan, iterations)

    rng = random.Random(seed)  # noqa: S311 - seeded for reproducibility, not security
    n = len(defined)
    means: list[float] = []
    for _ in range(iterations):
        total = 0.0
        for _ in range(n):
            total += defined[rng.randrange(n)]
        means.append(total / n)
    means.sort()

    low_index = max(0, int((alpha / 2) * iterations))
    high_index = min(iterations - 1, int((1 - alpha / 2) * iterations) - 1)
    return BootstrapCI(means[low_index], means[high_index], iterations)


@dataclass(frozen=True)
class KsScores:
    """Per-question scores at a single ``k``."""

    k: int
    recall: float
    precision: float
    reciprocal_rank: float
    ndcg: float


def score_question(
    retrieved: list[str],
    gold: frozenset[str],
    *,
    ks: tuple[int, ...] = DEFAULT_KS,
) -> tuple[KsScores, ...]:
    """Score one question at every ``k``. Unanswerable questions score ``nan``."""
    return tuple(
        KsScores(
            k=k,
            recall=recall_at_k(retrieved, gold, k),
            precision=precision_at_k(retrieved, gold, k),
            reciprocal_rank=reciprocal_rank(retrieved, gold, k),
            ndcg=ndcg_at_k(retrieved, gold, k),
        )
        for k in ks
    )


@dataclass
class MetricRow:
    """An aggregate over questions, with the counts needed to read it honestly."""

    label: str
    metric: str
    k: int
    mean: float
    ci: BootstrapCI
    n: int
    excluded: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "metric": self.metric,
            "k": self.k,
            "mean": None if math.isnan(self.mean) else round(self.mean, 6),
            "ci_low": None if math.isnan(self.ci.low) else round(self.ci.low, 6),
            "ci_high": None if math.isnan(self.ci.high) else round(self.ci.high, 6),
            "n": self.n,
            "excluded": self.excluded,
        }


def aggregate(
    rows: list[dict[str, Any]],
    *,
    metrics: tuple[str, ...] = ("recall", "precision", "reciprocal_rank", "ndcg"),
    ks: tuple[int, ...] = DEFAULT_KS,
    label: str = "overall",
) -> list[MetricRow]:
    """Aggregate per-question ``KsScores`` (as dicts) into rows with CIs."""
    out: list[MetricRow] = []
    for k in ks:
        for metric in metrics:
            values = [float(row[f"{metric}@{k}"]) for row in rows if f"{metric}@{k}" in row]
            if not values:
                continue
            defined = [v for v in values if not math.isnan(v)]
            out.append(
                MetricRow(
                    label=label,
                    metric=metric,
                    k=k,
                    mean=mean_ignoring_nan(values),
                    ci=bootstrap_ci(values),
                    n=len(defined),
                    excluded=len(values) - len(defined),
                )
            )
    return out


def markdown_table(rows: list[MetricRow], *, title: str, heading: bool = True) -> str:
    lines: list[str] = []
    if heading:
        lines.extend([f"## {title}", ""])
    lines.extend(
        [
            "| metric | k | mean | 95% CI | n | excluded |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        mean = "n/a" if math.isnan(row.mean) else f"{row.mean:.4f}"
        lines.append(f"| {row.metric} | {row.k} | {mean} | {row.ci} | {row.n} | {row.excluded} |")
    return "\n".join(lines)
