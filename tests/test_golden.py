"""Golden-set resolution.

The critical property: a gold label that cannot be resolved must **fail loudly**,
because an unresolved label means the chunker lost the text carrying the answer.
Skipping it would silently score every configuration against a question that
cannot be answered by anyone.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from gkp.eval.chunking import chunk_document
from gkp.eval.corpus import Fact
from gkp.eval.corpus_data import build as build_corpus
from gkp.eval.golden import (
    GoldenSetError,
    build_golden_set,
    load_golden_set,
    write_golden_set,
)

CORPUS = build_corpus()
CHUNKS = [
    chunk
    for doc_id in sorted(CORPUS.rendered)
    for chunk in chunk_document(doc_id, CORPUS.rendered[doc_id])
]
ENTRIES, REPORT = build_golden_set(CORPUS, CHUNKS)


def test_every_hand_authored_fact_resolved_to_at_least_one_chunk() -> None:
    assert REPORT.is_clean
    assert len(ENTRIES) == len(CORPUS.facts) + len(CORPUS.unanswerable)


def test_answerable_entries_carry_gold_chunks_from_their_document() -> None:
    by_id = {entry.id: entry for entry in ENTRIES}
    for fact in CORPUS.facts:
        entry = by_id[fact.id]
        assert entry.answerable
        assert entry.gold_chunk_ids, f"{fact.id} resolved to no chunk"
        assert entry.gold_doc_ids == (fact.doc_id,)
        assert entry.expected_span == fact.span

        # Gold chunks must belong to the fact's own document.
        for chunk_id in entry.gold_chunk_ids:
            assert chunk_id.split("#")[0] == fact.doc_id


def test_unanswerable_entries_carry_no_gold() -> None:
    unanswerable = [entry for entry in ENTRIES if not entry.answerable]
    assert len(unanswerable) == len(CORPUS.unanswerable)
    for entry in unanswerable:
        assert entry.category == "unanswerable"
        assert entry.gold_chunk_ids == ()
        assert entry.gold_doc_ids == ()
        assert entry.expected_span is None
        assert entry.required_acl_tags


def test_acl_tags_come_from_the_document_that_carries_the_fact() -> None:
    by_id = {entry.id: entry for entry in ENTRIES}
    for fact in CORPUS.facts:
        expected = CORPUS.acl_tags_for_fact(fact)
        assert by_id[fact.id].required_acl_tags == expected


def test_resolution_raises_when_a_span_is_absent_from_every_chunk() -> None:
    """A chunker that drops answer text must fail the run, not quietly reduce n."""
    fact = Fact("f1", "d1", "S", "the uniquely identifying sentence", "q?", "policy-lookup")
    tiny = type(CORPUS)(
        documents={},
        rendered={},
        facts=(fact,),
        unanswerable=(),
    )
    with pytest.raises(GoldenSetError, match="resolved to no chunk"):
        build_golden_set(tiny, [])


def test_round_trip_preserves_every_field(tmp_path: Path) -> None:
    path = tmp_path / "questions.jsonl"
    digest = write_golden_set(ENTRIES, path)
    assert len(digest) == 16

    reloaded = load_golden_set(path)
    assert len(reloaded) == len(ENTRIES)
    for original, restored in zip(ENTRIES, reloaded, strict=True):
        assert original.id == restored.id
        assert original.question == restored.question
        assert original.answerable == restored.answerable
        assert original.category == restored.category
        assert original.required_acl_tags == restored.required_acl_tags
        assert original.gold_chunk_ids == restored.gold_chunk_ids
        assert original.gold_doc_ids == restored.gold_doc_ids
        assert original.expected_span == restored.expected_span


def test_write_is_deterministic(tmp_path: Path) -> None:
    """A stable hash lets a result be attributed to an exact answer key."""
    first = write_golden_set(ENTRIES, tmp_path / "a.jsonl")
    second = write_golden_set(ENTRIES, tmp_path / "b.jsonl")
    assert first == second


def test_golden_set_covers_every_category_it_claims_to() -> None:
    categories = {entry.category for entry in ENTRIES}
    assert {
        "version-conflict",
        "table-lookup",
        "multi-hop",
        "policy-lookup",
        "restricted",
        "unanswerable",
    } <= categories
