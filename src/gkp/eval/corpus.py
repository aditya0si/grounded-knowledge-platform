"""Hostile synthetic corpus for retrieval evaluation.

**Why synthetic.** A real internal-docs corpus with trustworthy gold labels is
not available, so the document *distribution* here is not representative. That
limitation is published rather than hidden (ADR-002). What the corpus does
provide is ground truth *by construction*: every fact records the verbatim span
that answers it, so relevance labels are derived from how the corpus was built,
not from a model's opinion about relevance.

**Why hostile.** Clean, self-contained prose makes every retrieval strategy look
equivalent, which is not a neutral design — it is a harness that cannot
discriminate. The properties that matter are asserted in tests rather than
documented and hoped for:

* near-duplicate **version families**, so "retrieved a similar-looking stale
  revision" is distinguishable from "retrieved the right chunk";
* **markdown tables**, whose rows naive character chunking splits mid-record;
* **cross-document references**, which cannot be answered in a single hop;
* **lexical distractors** that share vocabulary with a question without
  answering it.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Literal

DocType = Literal["policy", "runbook", "standard", "hr-policy", "table", "changelog", "ticket"]

Category = Literal["policy-lookup", "table-lookup", "multi-hop", "version-conflict", "restricted"]

AclTag = Literal["all", "eng", "sec", "hr", "finance"]


class CorpusError(ValueError):
    """A construction invariant is violated.

    These are raised while building the corpus, so a broken gold label fails
    loudly at generation time rather than silently skewing an evaluation.
    """


@dataclass(frozen=True)
class TableSpec:
    """A markdown pipe table. Rows are raw cells, rendered verbatim."""

    headers: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]

    def render(self) -> str:
        head = "| " + " | ".join(self.headers) + " |"
        rule = "|" + "|".join(" --- " for _ in self.headers) + "|"
        body = ["| " + " | ".join(row) + " |" for row in self.rows]
        return "\n".join([head, rule, *body])


@dataclass(frozen=True)
class Section:
    heading: str
    paragraphs: tuple[str, ...] = ()
    table: TableSpec | None = None


@dataclass(frozen=True)
class DocumentSpec:
    doc_id: str
    title: str
    doc_type: DocType
    acl_tags: tuple[AclTag, ...]
    owner: str
    sections: tuple[Section, ...]
    version: int | None = None
    supersedes: str | None = None


@dataclass(frozen=True)
class Fact:
    """A single answerable fact, with the verbatim span that answers it.

    ``span`` is the load-bearing field: it must appear character-for-character in
    the rendered document, and it must be unique across the whole corpus. Both
    are enforced by :func:`build_corpus`.
    """

    id: str
    doc_id: str
    section: str
    span: str
    question: str
    category: Category
    notes: str = ""
    # Defaults to the document's own tags; set explicitly only where a fact is
    # restricted more tightly than the document that carries it.
    required_acl_tags: tuple[AclTag, ...] | None = None


@dataclass(frozen=True)
class UnanswerableQuestion:
    """A question the corpus must decline to answer.

    Without these, refusal correctness is unmeasurable and a system that never
    declines is indistinguishable from one that answers correctly.
    """

    id: str
    question: str
    required_acl_tags: tuple[AclTag, ...]
    notes: str = ""


@dataclass(frozen=True)
class BuiltCorpus:
    """A validated corpus: rendered documents plus their facts."""

    documents: dict[str, DocumentSpec] = field(default_factory=dict)
    rendered: dict[str, str] = field(default_factory=dict)
    facts: tuple[Fact, ...] = ()
    unanswerable: tuple[UnanswerableQuestion, ...] = ()

    @property
    def content_hash(self) -> str:
        """Stable hash of every rendered document.

        Stamped into results so a number is attributable to a corpus revision,
        and so two runs cannot be compared across a corpus change without it
        being visible.
        """
        digest = hashlib.sha256()
        for doc_id in sorted(self.rendered):
            digest.update(doc_id.encode())
            digest.update(b"\x00")
            digest.update(self.rendered[doc_id].encode())
            digest.update(b"\x00")
        return digest.hexdigest()[:16]

    def facts_for(self, doc_id: str) -> tuple[Fact, ...]:
        return tuple(f for f in self.facts if f.doc_id == doc_id)

    def acl_tags_for_fact(self, fact: Fact) -> tuple[AclTag, ...]:
        if fact.required_acl_tags is not None:
            return fact.required_acl_tags
        return self.documents[fact.doc_id].acl_tags


def render_markdown(doc: DocumentSpec) -> str:
    """Render a document to markdown with a realistic metadata header.

    The header is not decoration: it gives every document an explicit
    classification line, which is how a reader would know the document is
    restricted, and it gives retrievers a lexical hook that is *not* the answer.
    """
    lines: list[str] = [f"# {doc.title}", ""]

    meta: list[str] = [f"**Document ID:** `{doc.doc_id}`"]
    if doc.version is not None:
        meta.append(f"**Version:** {doc.version}")
    if doc.supersedes is not None:
        meta.append(f"**Supersedes:** `{doc.supersedes}`")
    meta.append(f"**Classification:** {', '.join(doc.acl_tags)}")
    meta.append(f"**Owner:** {doc.owner}")
    lines.extend(["  \n".join(meta), "", "---", ""])

    for section in doc.sections:
        lines.extend([f"## {section.heading}", ""])
        for paragraph in section.paragraphs:
            lines.extend([paragraph, ""])
        if section.table is not None:
            lines.extend([section.table.render(), ""])

    return "\n".join(lines).rstrip() + "\n"


def build_corpus(
    documents: tuple[DocumentSpec, ...],
    facts: tuple[Fact, ...],
    unanswerable: tuple[UnanswerableQuestion, ...],
) -> BuiltCorpus:
    """Render every document and enforce the construction invariants.

    Every check here protects the validity of a gold label. A corpus that fails
    any of them would still *run* — and would quietly produce an evaluation that
    looks fine and means nothing, which is the failure mode this project exists
    to avoid.
    """
    _check_unique("document id", [d.doc_id for d in documents])
    _check_unique("fact id", [f.id for f in facts])
    _check_unique("unanswerable id", [q.id for q in unanswerable])

    by_id = {d.doc_id: d for d in documents}
    rendered = {d.doc_id: render_markdown(d) for d in documents}

    for doc in documents:
        if doc.supersedes is not None and doc.supersedes not in by_id:
            raise CorpusError(f"{doc.doc_id}: supersedes unknown document {doc.supersedes!r}")

    # --- spans must be present, and unambiguous ---------------------------
    span_owners: dict[str, str] = {}
    for fact in facts:
        if fact.doc_id not in by_id:
            raise CorpusError(f"{fact.id}: unknown document {fact.doc_id!r}")

        text = rendered[fact.doc_id]
        if fact.span not in text:
            raise CorpusError(
                f"{fact.id}: span does not appear verbatim in {fact.doc_id}. Span was {fact.span!r}"
            )

        # A span appearing in more than one place makes the gold label
        # ambiguous: retrieving the *other* occurrence would score as a hit.
        occurrences = text.count(fact.span)
        if occurrences != 1:
            raise CorpusError(
                f"{fact.id}: span occurs {occurrences}x in {fact.doc_id}, must be exactly 1"
            )

        previous = span_owners.get(fact.span)
        if previous is not None:
            raise CorpusError(
                f"{fact.id}: span also claimed by {previous}. "
                "Gold labels must be unambiguous across the corpus."
            )
        span_owners[fact.span] = fact.id

        # The span must not occur in any OTHER document either. If it does, a
        # retriever returning that other document's chunk lexically contains the
        # answer and is still scored as a miss — an unfairness that would
        # silently depress every metric and make the ablation unreadable.
        other_docs = sorted(
            other_id
            for other_id, other_text in rendered.items()
            if other_id != fact.doc_id and fact.span in other_text
        )
        if other_docs:
            raise CorpusError(
                f"{fact.id}: span also occurs in {other_docs}. "
                "Gold spans must identify exactly one document."
            )

        doc_tags = set(by_id[fact.doc_id].acl_tags)
        if fact.required_acl_tags is not None:
            extra = set(fact.required_acl_tags) - doc_tags
            if extra:
                raise CorpusError(
                    f"{fact.id}: requires {sorted(extra)} but {fact.doc_id} is tagged "
                    f"{sorted(doc_tags)}"
                )

    return BuiltCorpus(
        documents=by_id,
        rendered=rendered,
        facts=facts,
        unanswerable=unanswerable,
    )


def _check_unique(label: str, values: list[str]) -> None:
    seen: set[str] = set()
    for value in values:
        if value in seen:
            raise CorpusError(f"duplicate {label}: {value!r}")
        seen.add(value)


def corpus_manifest(corpus: BuiltCorpus) -> str:
    """Serialise the corpus as JSONL: one record per fact, then unanswerables."""
    records: list[dict[str, object]] = []
    for fact in corpus.facts:
        doc = corpus.documents[fact.doc_id]
        records.append(
            {
                "kind": "fact",
                "id": fact.id,
                "doc_id": fact.doc_id,
                "doc_title": doc.title,
                "doc_type": doc.doc_type,
                "version": doc.version,
                "section": fact.section,
                "span": fact.span,
                "question": fact.question,
                "category": fact.category,
                "acl_tags": list(corpus.acl_tags_for_fact(fact)),
                "notes": fact.notes,
            }
        )
    for question in corpus.unanswerable:
        records.append(
            {
                "kind": "unanswerable",
                "id": question.id,
                "question": question.question,
                "acl_tags": list(question.required_acl_tags),
                "notes": question.notes,
            }
        )
    return "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in records) + "\n"
