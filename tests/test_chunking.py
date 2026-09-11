"""Chunker behaviour.

The property that matters most: a chunk boundary must never fall inside a table
row or a paragraph. Small violations here would silently depress every retrieval
metric and be very hard to attribute later.
"""

from __future__ import annotations

import itertools

import pytest

from gkp.eval.chunking import chunk_document

TABLE_DOC = """\
# Service Tier Commitments

**Document ID:** `service-tiers`

---

## Tier commitments

Each tier carries a commitment.

| Tier | Monthly uptime | p95 latency |
| --- | --- | --- |
| Platinum | 99.95% | 180 ms |
| Gold | 99.90% | 420 ms |
| Silver | 99.50% | 950 ms |

## Credits

Credits are issued monthly.
"""


def test_chunk_ids_are_stable_and_sequential() -> None:
    chunks = chunk_document("d1", TABLE_DOC, target_chars=200, overlap_chars=20)
    assert [c.seq for c in chunks] == list(range(len(chunks)))
    assert [c.chunk_id for c in chunks] == [f"d1#{i}" for i in range(len(chunks))]


def test_no_table_row_is_ever_split() -> None:
    """The failure mode that motivated structural chunking."""
    chunks = chunk_document("d1", TABLE_DOC, target_chars=120, overlap_chars=16)
    assert len(chunks) > 1, "test is vacuous if the document fits in one chunk"

    for row in (
        "| Platinum | 99.95% | 180 ms |",
        "| Gold | 99.90% | 420 ms |",
        "| Silver | 99.50% | 950 ms |",
    ):
        intact = [c for c in chunks if row in c.text]
        assert intact, f"row was split across chunks and appears intact nowhere: {row}"


def test_a_table_split_across_chunks_repeats_its_header() -> None:
    chunks = chunk_document("d1", TABLE_DOC, target_chars=120, overlap_chars=16)
    holding_rows = [c for c in chunks if "| Gold | 99.90% | 420 ms |" in c.text]
    for chunk in holding_rows:
        assert "| Tier | Monthly uptime | p95 latency |" in chunk.text, (
            "a chunk containing table rows must restate the header, or the row is "
            "uninterpretable in isolation"
        )


def test_section_headings_are_tracked_onto_chunks() -> None:
    # min_chars=0 disables the stub-merge, so the short final section keeps its
    # own chunk and its section label can be observed.
    chunks = chunk_document("d1", TABLE_DOC, target_chars=120, overlap_chars=16, min_chars=0)
    sections = {c.section for c in chunks}
    assert "Tier commitments" in sections
    assert "Credits" in sections


def test_a_stub_final_chunk_is_merged_into_its_predecessor() -> None:
    """A chunk too short to retrieve meaningfully is folded back rather than
    emitted as a near-empty row in the index."""
    chunks = chunk_document("d1", TABLE_DOC, target_chars=400, overlap_chars=32)
    assert all(len(c.text) >= 120 for c in chunks)


def test_merging_a_stub_does_not_duplicate_overlap_units() -> None:
    chunks = chunk_document("d1", TABLE_DOC, target_chars=200, overlap_chars=64)
    for chunk in chunks:
        # "Credits are issued monthly." sits in exactly one chunk.
        assert chunk.text.count("Credits are issued monthly.") <= 1


def test_consecutive_chunks_overlap() -> None:
    text = "\n\n".join(f"Paragraph number {i} with some filler words." for i in range(20))
    chunks = chunk_document("d1", text, target_chars=200, overlap_chars=64)
    assert len(chunks) > 2

    for previous, following in itertools.pairwise(chunks):
        assert previous.char_end >= following.char_start, "chunks must overlap or abut"


def test_a_unit_longer_than_the_target_is_emitted_whole() -> None:
    """Truncating would lose exactly the text a gold span might be anchored to."""
    long_paragraph = "x" * 900
    chunks = chunk_document("d1", f"Short intro.\n\n{long_paragraph}\n", target_chars=200)
    assert any(long_paragraph in c.text for c in chunks)


def test_char_offsets_stay_within_the_document() -> None:
    chunks = chunk_document("d1", TABLE_DOC, target_chars=150, overlap_chars=16)
    for chunk in chunks:
        assert 0 <= chunk.char_start < chunk.char_end <= len(TABLE_DOC)


def test_empty_input_produces_no_chunks() -> None:
    assert chunk_document("d1", "") == []
    assert chunk_document("d1", "\n\n   \n") == []


def test_invalid_configuration_is_rejected() -> None:
    with pytest.raises(ValueError, match="target_chars must be positive"):
        chunk_document("d1", TABLE_DOC, target_chars=0)
    with pytest.raises(ValueError, match="overlap_chars must be smaller"):
        chunk_document("d1", TABLE_DOC, target_chars=100, overlap_chars=100)


def test_smaller_target_produces_more_chunks() -> None:
    coarse = chunk_document("d1", TABLE_DOC, target_chars=400, overlap_chars=32)
    fine = chunk_document("d1", TABLE_DOC, target_chars=120, overlap_chars=16)
    assert len(fine) > len(coarse)
