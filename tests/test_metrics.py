"""Retrieval metric functions, checked against hand-computed values.

Every expected value below is computed by hand in the test body rather than
copied from a previous run, so a change in the implementation cannot quietly
redefine the metric.
"""

from __future__ import annotations

import math

import pytest

from gkp.eval.metrics import (
    mean_ignoring_nan,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)

# A fixed, deliberately ordered retrieved list.
R = ["c1", "c2", "c3", "c4"]
GOLD_TWO = {"c2", "c4"}
GOLD_ONE = {"c2"}


# --------------------------------------------------------------- recall@k


def test_recall_counts_gold_found_in_top_k() -> None:
    # top-2 = {c1, c2}; intersects gold {c2, c4} at c2 only -> 1 of 2
    assert recall_at_k(R, GOLD_TWO, k=2) == pytest.approx(0.5)


def test_recall_reaches_one_when_all_gold_retrieved() -> None:
    assert recall_at_k(R, GOLD_TWO, k=4) == pytest.approx(1.0)


def test_recall_is_zero_when_no_gold_in_top_k() -> None:
    assert recall_at_k(R, {"c9"}, k=4) == pytest.approx(0.0)


def test_recall_is_undefined_without_gold() -> None:
    assert math.isnan(recall_at_k(R, set(), k=4))


# ------------------------------------------------------------ precision@k


def test_precision_divides_by_k_not_by_returned_length() -> None:
    # 2 gold in top-4, but k=6 requested: 2/6, not 2/4.
    assert precision_at_k(R, GOLD_TWO, k=6) == pytest.approx(2 / 6)


def test_precision_at_k_equals_recall_when_gold_is_exactly_top_k() -> None:
    assert precision_at_k(R, GOLD_TWO, k=2) == pytest.approx(0.5)
    assert recall_at_k(R, GOLD_TWO, k=2) == pytest.approx(0.5)


def test_precision_is_undefined_for_zero_k() -> None:
    assert math.isnan(precision_at_k(R, GOLD_TWO, k=0))


# -------------------------------------------------------- reciprocal rank


def test_reciprocal_rank_uses_first_hit_position() -> None:
    # c3 is the third element -> 1/3
    assert reciprocal_rank(["c1", "c2", "c3"], {"c3"}, k=3) == pytest.approx(1 / 3)


def test_reciprocal_rank_is_one_when_first_element_is_gold() -> None:
    assert reciprocal_rank(["c1", "c2"], {"c1"}, k=2) == pytest.approx(1.0)


def test_reciprocal_rank_is_zero_not_nan_when_nothing_found() -> None:
    """A miss is a scored outcome, not an undefined one."""
    value = reciprocal_rank(["c1", "c2"], {"c9"}, k=2)
    assert value == pytest.approx(0.0)
    assert not math.isnan(value)


def test_reciprocal_rank_respects_the_k_cutoff() -> None:
    # c2 is gold but sits outside the top-1 window.
    assert reciprocal_rank(["c1", "c2"], {"c2"}, k=1) == pytest.approx(0.0)


# ------------------------------------------------------------------ nDCG


def test_ndcg_penalises_a_late_hit() -> None:
    # dcg = 1/log2(3) ; idcg (one relevant) = 1/log2(2) = 1
    assert ndcg_at_k(["c1", "c2", "c3"], GOLD_ONE, k=3) == pytest.approx(1 / math.log2(3))


def test_ndcg_is_one_when_gold_ranks_first() -> None:
    assert ndcg_at_k(["c2", "c1", "c3"], GOLD_ONE, k=3) == pytest.approx(1.0)


def test_ndcg_rewards_ordering_that_recall_cannot_see() -> None:
    """Two orderings, identical recall@4, different nDCG — the point of nDCG."""
    early = ["c2", "c4", "c1", "c3"]
    late = ["c1", "c3", "c2", "c4"]
    assert recall_at_k(early, GOLD_TWO, k=4) == recall_at_k(late, GOLD_TWO, k=4)
    assert ndcg_at_k(early, GOLD_TWO, k=4) > ndcg_at_k(late, GOLD_TWO, k=4)


def test_ndcg_matches_hand_computation_for_two_gold_chunks() -> None:
    # positions 2 and 4 hold gold:
    #   dcg  = 1/log2(3) + 1/log2(5)          = 0.6309298 + 0.4306766 = 1.0616063
    #   idcg = 1/log2(2) + 1/log2(3)          = 1.0000000 + 0.6309298 = 1.6309298
    #   ndcg = 1.0616063 / 1.6309298          = 0.6509209...
    expected = (1 / math.log2(3) + 1 / math.log2(5)) / (1 / math.log2(2) + 1 / math.log2(3))
    assert ndcg_at_k(R, GOLD_TWO, k=4) == pytest.approx(expected)
    assert expected == pytest.approx(0.65092093, abs=1e-8)


def test_ndcg_is_undefined_without_gold() -> None:
    assert math.isnan(ndcg_at_k(R, set(), k=4))


# ------------------------------------------------------------- aggregation


def test_mean_ignores_undefined_rows() -> None:
    assert mean_ignoring_nan([1.0, math.nan, 0.0]) == pytest.approx(0.5)


def test_mean_of_all_undefined_is_nan() -> None:
    assert math.isnan(mean_ignoring_nan([math.nan, math.nan]))


def test_mean_of_empty_sequence_is_nan() -> None:
    assert math.isnan(mean_ignoring_nan([]))
