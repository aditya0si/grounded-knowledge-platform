"""Golden set: gold labels resolved from the corpus at evaluation time.

**Why spans and not chunk IDs.** The obvious encoding of a gold label is a list
of chunk identifiers. That encoding breaks the moment chunk size changes, and
chunk size is precisely what the M2 ablation varies — every configuration would
need its own hand-built answer key, and comparing them would be comparing two
different tests.

Instead a golden entry references the *facts* that answer it, and each fact
carries a verbatim span. Chunk identifiers are resolved at evaluation time by
finding the chunks that contain the span. One golden set therefore scores every
configuration, and the ablation compares like with like.

The cost is that resolution must be checked. A span that resolves to no chunk
means the chunker lost the answer — which is a real finding, not a bug to be
silently swallowed, so resolution failures are raised rather than skipped.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

from gkp.eval.chunking import Chunk
from gkp.eval.corpus import BuiltCorpus, Fact

__all__ = [
    "GoldenEntry",
    "GoldenSetError",
    "ResolutionReport",
    "build_golden_set",
    "load_golden_set",
    "write_golden_set",
]


class GoldenSetError(ValueError):
    """A gold label could not be resolved against the corpus."""


@dataclass(frozen=True)
class GoldenEntry:
    id: str
    question: str
    answerable: bool
    category: str
    required_acl_tags: tuple[str, ...]
    gold_chunk_ids: tuple[str, ...]
    gold_doc_ids: tuple[str, ...]
    expected_span: str | None
    notes: str = ""

    @property
    def is_unanswerable(self) -> bool:
        return not self.answerable


@dataclass
class ResolutionReport:
    """Diagnostics from resolving the golden set. Published, not discarded: a
    span that resolved to many chunks is a weak label even when it "works"."""

    span_to_chunks: dict[str, tuple[str, ...]] = field(default_factory=dict)
    multi_chunk_spans: dict[str, tuple[str, ...]] = field(default_factory=dict)
    unresolved: list[str] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return not self.unresolved


def _index_spans(chunks: list[Chunk], spans: set[str]) -> dict[str, tuple[str, ...]]:
    """Map each span to the chunk ids containing it, in one pass over the chunks."""
    found: dict[str, list[str]] = {span: [] for span in spans}
    for chunk in chunks:
        for span, hits in found.items():
            if span in chunk.text:
                hits.append(chunk.chunk_id)
    return {span: tuple(hits) for span, hits in found.items()}


def build_golden_set(
    corpus: BuiltCorpus,
    chunks: list[Chunk],
) -> tuple[tuple[GoldenEntry, ...], ResolutionReport]:
    """Resolve every fact to the chunks that contain it.

    Raises :class:`GoldenSetError` if any fact resolves to nothing: that means the
    chunker split or dropped the text carrying the answer, and continuing would
    score every configuration against an unanswerable question.
    """
    spans = {fact.span for fact in corpus.facts}
    span_chunks = _index_spans(chunks, spans)

    report = ResolutionReport(span_to_chunks=span_chunks)
    entries: list[GoldenEntry] = []

    for fact in corpus.facts:
        hits = span_chunks[fact.span]
        if not hits:
            report.unresolved.append(fact.id)
            continue
        if len(hits) > 1:
            report.multi_chunk_spans[fact.span] = hits
        entries.append(
            GoldenEntry(
                id=fact.id,
                question=fact.question,
                answerable=True,
                category=fact.category,
                required_acl_tags=corpus.acl_tags_for_fact(fact),
                gold_chunk_ids=hits,
                gold_doc_ids=(fact.doc_id,),
                expected_span=fact.span,
                notes=fact.notes,
            )
        )

    if report.unresolved:
        preview = ", ".join(report.unresolved[:5])
        raise GoldenSetError(
            f"{len(report.unresolved)} gold spans resolved to no chunk "
            f"(e.g. {preview}). The chunker is losing answer text."
        )

    for question in corpus.unanswerable:
        entries.append(
            GoldenEntry(
                id=question.id,
                question=question.question,
                answerable=False,
                category="unanswerable",
                required_acl_tags=question.required_acl_tags,
                gold_chunk_ids=(),
                gold_doc_ids=(),
                expected_span=None,
                notes=question.notes,
            )
        )

    return tuple(entries), report


def _entry_to_json(entry: GoldenEntry) -> dict[str, object]:
    return {
        "id": entry.id,
        "question": entry.question,
        "answerable": entry.answerable,
        "category": entry.category,
        "acl_tags": list(entry.required_acl_tags),
        "gold_chunk_ids": list(entry.gold_chunk_ids),
        "gold_doc_ids": list(entry.gold_doc_ids),
        "expected_span": entry.expected_span,
        "notes": entry.notes,
    }


def write_golden_set(entries: tuple[GoldenEntry, ...], path: Path) -> str:
    """Write the golden set as JSONL. Returns its SHA-256 prefix.

    The hash is stamped into results so a score is attributable to an exact
    answer key, and so a run cannot be silently compared against a different one.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        json.dumps(_entry_to_json(entry), ensure_ascii=False, sort_keys=True) for entry in entries
    ]
    payload = "\n".join(lines) + "\n"
    path.write_text(payload, encoding="utf-8")
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def load_golden_set(path: Path) -> tuple[GoldenEntry, ...]:
    entries: list[GoldenEntry] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        record = json.loads(raw)
        entries.append(
            GoldenEntry(
                id=record["id"],
                question=record["question"],
                answerable=bool(record["answerable"]),
                category=record["category"],
                required_acl_tags=tuple(record["acl_tags"]),
                gold_chunk_ids=tuple(record["gold_chunk_ids"]),
                gold_doc_ids=tuple(record["gold_doc_ids"]),
                expected_span=record["expected_span"],
                notes=record.get("notes", ""),
            )
        )
    return tuple(entries)


def spans_for_facts(corpus: BuiltCorpus, fact_ids: tuple[str, ...]) -> tuple[str, ...]:
    """Look up the spans backing a set of facts. Used by multi-hop reporting."""
    by_id: dict[str, Fact] = {fact.id: fact for fact in corpus.facts}
    return tuple(by_id[fid].span for fid in fact_ids if fid in by_id)
