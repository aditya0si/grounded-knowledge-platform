"""Aggregation and reporting.

These are the functions the CI gate reads, so the properties that matter are
determinism (a gate that flaps is not a gate) and honest counting (a mean over 40
of 120 questions must never be printed as if it covered all 120).
"""

from __future__ import annotations

import math

import pytest

from gkp.eval.report import (
    BootstrapCI,
    MetricRow,
    aggregate,
    bootstrap_ci,
    markdown_table,
    score_question,
)


def test_bootstrap_ci_is_deterministic_for_a_fixed_seed() -> None:
    values = [0.1, 0.4, 0.35, 0.9, 0.55, 0.2, 0.8, 0.65]
    first = bootstrap_ci(values)
    second = bootstrap_ci(values)
    assert (first.low, first.high) == (second.low, second.high)


def test_bootstrap_ci_brackets_the_point_estimate() -> None:
    values = [0.1, 0.4, 0.35, 0.9, 0.55, 0.2, 0.8, 0.65]
    ci = bootstrap_ci(values)
    mean = sum(values) / len(values)
    assert ci.low <= mean <= ci.high


def test_bootstrap_ci_is_undefined_below_two_observations() -> None:
    assert math.isnan(bootstrap_ci([]).low)
    assert math.isnan(bootstrap_ci([0.5]).low)


def test_bootstrap_ci_reports_n_a_when_undefined() -> None:
    assert str(BootstrapCI(math.nan, math.nan, 100)) == "n/a"


def test_score_question_is_undefined_for_an_unanswerable_question() -> None:
    """No gold means no retrieval metric — not a score of zero."""
    scores = score_question(["c1", "c2"], frozenset(), ks=(1, 5))
    for score in scores:
        assert math.isnan(score.recall)
        assert math.isnan(score.ndcg)
        # reciprocal rank is the exception: it is genuinely 0.0, not undefined.
        assert math.isnan(score.reciprocal_rank) or score.reciprocal_rank == 0.0


def test_aggregate_counts_undefined_rows_rather_than_dropping_them_silently() -> None:
    rows: list[dict[str, float]] = [
        {"recall@5": 1.0},
        {"recall@5": math.nan},  # an unanswerable question
        {"recall@5": 0.5},
    ]
    (metric,) = aggregate(rows, metrics=("recall",), ks=(5,))
    assert metric.n == 2
    assert metric.excluded == 1
    assert metric.mean == pytest.approx(0.75)


def test_aggregate_yields_nan_when_every_row_is_undefined() -> None:
    rows: list[dict[str, float]] = [{"recall@5": math.nan}, {"recall@5": math.nan}]
    (metric,) = aggregate(rows, metrics=("recall",), ks=(5,))
    assert math.isnan(metric.mean)
    assert metric.n == 0
    assert metric.excluded == 2


def test_aggregate_of_nothing_is_empty_not_an_error() -> None:
    assert aggregate([], metrics=("recall",), ks=(5,)) == []


def test_markdown_table_prints_n_and_excluded() -> None:
    row = MetricRow(
        label="overall",
        metric="recall",
        k=10,
        mean=0.9167,
        ci=BootstrapCI(0.82, 0.99, 2000),
        n=42,
        excluded=12,
    )
    rendered = markdown_table([row], title="overall")
    assert "| recall | 10 | 0.9167 |" in rendered
    assert "| 42 | 12 |" in rendered


def test_markdown_table_marks_an_undefined_mean() -> None:
    row = MetricRow(
        label="x",
        metric="recall",
        k=10,
        mean=math.nan,
        ci=BootstrapCI(math.nan, math.nan, 10),
        n=0,
        excluded=3,
    )
    assert "| n/a |" in markdown_table([row], title="x")
