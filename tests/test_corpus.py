"""Corpus construction and the properties that make it a usable benchmark.

The point of these tests is that "the corpus is hostile" is an assertion with
teeth rather than a claim in a docstring. If a future edit flattens the version
families, removes the tables, or shrinks the haystack back to the size where
recall is 1.0 by construction, the suite says so.
"""

from __future__ import annotations

from collections import Counter, defaultdict

import pytest

from gkp.eval import corpus_data
from gkp.eval.chunking import chunk_document
from gkp.eval.corpus import (
    CorpusError,
    DocumentSpec,
    Fact,
    Section,
    build_corpus,
)

CORPUS = corpus_data.build()

#: ``k`` used for the retriever's candidate window in the baseline evaluation.
CANDIDATE_K = 20


def test_corpus_builds_and_is_deterministic() -> None:
    """The haystack is seeded, so a published result maps to one corpus revision."""
    assert corpus_data.build().content_hash == CORPUS.content_hash


def test_haystack_is_far_larger_than_the_retrieved_window() -> None:
    """The property the prototype lacked.

    With three chunks in the corpus and ``top-k=6``, recall was 1.0 by
    construction and the evaluation measured generation alone.
    """
    chunks = [
        chunk
        for doc_id in sorted(CORPUS.rendered)
        for chunk in chunk_document(doc_id, CORPUS.rendered[doc_id])
    ]
    assert len(chunks) >= 250, f"haystack too small: {len(chunks)} chunks"

    share = CANDIDATE_K / len(chunks)
    assert share < 0.10, f"k={CANDIDATE_K} sees {share:.1%} of the corpus; not a retrieval test"


def test_version_families_exist() -> None:
    """Near-duplicate revisions are what separate 'found a plausible revision'
    from 'found the authoritative one'."""
    titles: defaultdict[str, set[int]] = defaultdict(set)
    for doc in CORPUS.documents.values():
        if doc.version is not None:
            titles[doc.title].add(doc.version)

    families = {title: versions for title, versions in titles.items() if len(versions) >= 2}
    assert len(families) >= 2, f"expected at least 2 version families, got {families}"
    assert max(len(v) for v in families.values()) >= 3, "expected a family with 3+ revisions"


def test_every_superseded_document_points_at_a_real_predecessor() -> None:
    for doc in CORPUS.documents.values():
        if doc.supersedes is not None:
            assert doc.supersedes in CORPUS.documents


def test_corpus_contains_tables() -> None:
    table_docs = [d for d in CORPUS.rendered.values() if "| --- " in d or "| ---|" in d]
    assert len(table_docs) >= 2, "tables are a primary way naive chunking loses answers"


def test_corpus_contains_cross_document_questions() -> None:
    multi_hop = [f for f in CORPUS.facts if f.category == "multi-hop"]
    assert len(multi_hop) >= 2, "multi-hop questions are what single-shot retrieval fails"

    # A cross-reference must actually route to a different document than the one
    # carrying it, otherwise the question is answerable in a single hop.
    referencing = [
        f for f in multi_hop if f.doc_id == "runbook-database-failover" and "section 3.2" in f.span
    ]
    assert referencing, "expected the failover runbook to defer to another document"
    assert referencing[0].doc_id != "runbook-network-partition"
    assert "runbook-network-partition" in CORPUS.documents


def test_haystack_contains_lexical_confusers() -> None:
    """Generated documents that share vocabulary with the gold questions.

    Without these the haystack is separable on keywords alone and the dense arm
    would look far better than it is.
    """
    from gkp.eval.corpus_haystack import CONFUSERS

    joined = "\n".join(CORPUS.rendered.values())
    present = [c for c in CONFUSERS if c in joined]
    assert len(present) >= 5, f"only {len(present)} confuser forms appear in the corpus"


def test_acl_tags_spread_across_the_corpus() -> None:
    counts = Counter(tag for doc in CORPUS.documents.values() for tag in doc.acl_tags)
    for tag in ("eng", "sec", "hr", "finance", "all"):
        assert counts[tag] > 0, f"no documents tagged {tag!r}; the predicate is untested"


def test_enough_unanswerable_questions_to_measure_refusal() -> None:
    assert len(CORPUS.unanswerable) >= 10

    # Several must be traps that name something adjacent but absent.
    trap = next(q for q in CORPUS.unanswerable if q.id == "u_bronze_tier")
    assert "Bronze" in trap.question


def test_every_fact_span_is_present_and_unique() -> None:
    for fact in CORPUS.facts:
        text = CORPUS.rendered[fact.doc_id]
        assert fact.span in text, f"{fact.id} span missing from {fact.doc_id}"
        assert text.count(fact.span) == 1, f"{fact.id} span is ambiguous within its document"

    spans = [f.span for f in CORPUS.facts]
    assert len(spans) == len(set(spans)), "gold spans must be unique across the corpus"


def test_facts_outnumber_questions_by_document_coverage() -> None:
    """Every hand-authored document should carry at least one gold fact, or it is
    haystack that was written in the voice of a source."""
    curated = {
        "incident-response-policy-v1",
        "incident-response-policy-v2",
        "incident-response-policy-v3",
        "leave-policy-v1",
        "leave-policy-v2",
        "service-tiers",
        "oncall-escalation-matrix",
        "runbook-database-failover",
        "runbook-network-partition",
        "key-rotation-policy",
        "data-classification-standard",
        "changelog-2026-q2",
        "tickets-2026-09",
        "disaster-recovery-overview",
        "procurement-guidelines",
    }
    assert curated <= set(CORPUS.documents), "a curated document went missing"

    covered = {f.doc_id for f in CORPUS.facts}
    missing = curated - covered
    assert not missing, f"curated documents with no gold fact: {sorted(missing)}"


# ---------------------------------------------------------------- negative tests
# The validator exists to catch authoring mistakes. Prove it does.


def _doc(text: str) -> DocumentSpec:
    return DocumentSpec(
        doc_id="d1",
        title="T",
        doc_type="policy",
        acl_tags=("eng",),
        owner="O",
        sections=(Section("S", paragraphs=(text,)),),
    )


def test_build_rejects_a_span_absent_from_its_document() -> None:
    docs = (_doc("Alpha beta gamma."),)
    facts = (Fact("f1", "d1", "S", "not present", "q?", "policy-lookup"),)
    with pytest.raises(CorpusError, match="does not appear verbatim"):
        build_corpus(docs, facts, ())


def test_build_rejects_an_ambiguous_span_across_documents() -> None:
    """The failure that made the gold labels unusable the first time they were written."""
    shared = "retained for 400 days after closure"
    docs = (
        DocumentSpec("d1", "T", "policy", ("eng",), "O", (Section("S", (f"A {shared}.",)),)),
        DocumentSpec("d2", "T", "policy", ("eng",), "O", (Section("S", (f"B {shared}.",)),)),
    )
    facts = (Fact("f1", "d1", "S", shared, "q?", "policy-lookup"),)
    with pytest.raises(CorpusError, match="also occurs in"):
        build_corpus(docs, facts, ())


def test_build_rejects_a_fact_tagged_more_strictly_than_its_document() -> None:
    docs = (_doc("Alpha."),)
    facts = (Fact("f1", "d1", "S", "Alpha", "q?", "policy-lookup", required_acl_tags=("hr",)),)
    with pytest.raises(CorpusError, match="requires"):
        build_corpus(docs, facts, ())
