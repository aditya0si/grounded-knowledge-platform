"""Dense-only retrieval baseline.

This is the measurement the rest of the project is judged against. It runs the
dense arm alone, before hybrid retrieval or reranking exist, so that M2's
improvements have a baseline that was measured rather than assumed (ADR-002).

Three things this runner refuses to do:

1. **Produce a report from a non-semantic embedder.** A hash embedder's vectors
   carry no meaning, so any number derived from them is noise dressed as a
   measurement.
2. **Skip the ACL negative control.** Two controls run on every question, and a
   single leaked chunk fails the run. Permission scoping is not a metric here; it
   is an invariant.
3. **Report a mean without its n.** Undefined metrics are counted and printed
   rather than silently dropped.

Usage:
    python -m gkp.eval.runners.baseline [--ks 1,3,5,10,20] [--limit 20]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import platform
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from gkp.core.config import get_settings
from gkp.db.session import get_engine
from gkp.eval.chunking import chunk_document
from gkp.eval.corpus_data import build as build_corpus
from gkp.eval.golden import GoldenEntry, build_golden_set
from gkp.eval.report import (
    DEFAULT_KS,
    MetricRow,
    aggregate,
    markdown_table,
    score_question,
)
from gkp.retrieve.dense import dense_search, vector_literal
from gkp.retrieve.embedder import build_embedder

ROOT = Path(__file__).resolve().parents[4]
RESULTS_DIR = ROOT / "results"
RAW_DIR = RESULTS_DIR / "raw"

WORKSPACE_ID = "eval"
EMBED_BATCH = 64

INSERT_DOCUMENT = text(
    """
    INSERT INTO documents
        (id, workspace_id, title, doc_type, owner, acl_tags, version, superseded_by, checksum)
    VALUES
        (:id, :workspace_id, :title, :doc_type, :owner,
         CAST(:acl_tags AS text[]), :version, :superseded_by, :checksum)
    """
)

INSERT_CHUNK = text(
    """
    INSERT INTO chunks
        (id, document_id, workspace_id, seq, text, section, char_start, char_end,
         acl_tags, embedding)
    VALUES
        (:id, :document_id, :workspace_id, :seq, :text, :section, :char_start, :char_end,
         CAST(:acl_tags AS text[]), CAST(:embedding AS vector))
    """
)


@dataclass
class RunMetadata:
    run_id: str
    started_at: str
    corpus_hash: str
    golden_hash: str
    embedder: str
    embedder_dim: int
    chunk_target_chars: int
    chunk_overlap_chars: int
    documents: int
    chunks: int
    questions_total: int
    questions_answerable: int
    candidate_limit: int
    ks: list[int]
    host: str
    python: str
    git_commit: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AclControl:
    """Result of the two permission negative controls."""

    nonexistent_tag_leaks: int = 0
    disjoint_tag_gold_leaks: int = 0
    questions_checked: int = 0
    leaks: list[str] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return self.nonexistent_tag_leaks == 0 and self.disjoint_tag_gold_leaks == 0


def _git_commit() -> str:
    git = shutil.which("git")
    if git is None:
        return "unknown"
    try:
        out = subprocess.run(  # noqa: S603 - resolved absolute path, fixed argv, no shell
            [git, "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        return out.stdout.strip() or "unknown"
    except OSError:  # pragma: no cover - git present but not runnable
        return "unknown"


def _migrate() -> None:
    """Bring the schema to head via Alembic.

    Running the real migrations rather than ``metadata.create_all`` means the
    baseline cannot pass on a schema that a fresh deployment would not have.

    Must be called from a *synchronous* context. Alembic's ``env.py`` owns its own
    ``asyncio.run``, so invoking this from inside a running event loop raises
    "asyncio.run() cannot be called from a running event loop" — which is why the
    caller runs it before entering the loop rather than as a first step inside it.
    """
    from alembic import command
    from alembic.config import Config

    config = Config(str(ROOT / "alembic.ini"))
    migrations = ROOT / "src" / "gkp" / "db" / "migrations"
    config.set_main_option("script_location", str(migrations))
    command.upgrade(config, "head")


async def _reset(session: AsyncSession) -> None:
    await session.execute(text("TRUNCATE chunks, documents CASCADE"))


async def _load_corpus(
    session: AsyncSession, embedder: Any, chunks: list[Any], corpus: Any
) -> None:
    for doc in corpus.documents.values():
        await session.execute(
            INSERT_DOCUMENT,
            {
                "id": doc.doc_id,
                "workspace_id": WORKSPACE_ID,
                "title": doc.title,
                "doc_type": doc.doc_type,
                "owner": doc.owner,
                "acl_tags": list(doc.acl_tags),
                "version": doc.version,
                "superseded_by": None,
                "checksum": None,
            },
        )

    for start in range(0, len(chunks), EMBED_BATCH):
        batch = chunks[start : start + EMBED_BATCH]
        vectors = embedder.embed([c.text for c in batch])
        for chunk, vector in zip(batch, vectors, strict=True):
            doc = corpus.documents[chunk.doc_id]
            await session.execute(
                INSERT_CHUNK,
                {
                    "id": chunk.chunk_id,
                    "document_id": chunk.doc_id,
                    "workspace_id": WORKSPACE_ID,
                    "seq": chunk.seq,
                    "text": chunk.text,
                    "section": chunk.section,
                    "char_start": chunk.char_start,
                    "char_end": chunk.char_end,
                    "acl_tags": list(doc.acl_tags),
                    "embedding": vector_literal(vector),
                },
            )
    await session.commit()


async def _run_acl_controls(
    session: AsyncSession,
    entries: tuple[GoldenEntry, ...],
    *,
    embedder: Any,
    all_tags: tuple[str, ...],
    limit: int,
) -> AclControl:
    """Two negative controls per question.

    * **Nonexistent tag** — a principal holding a tag no document carries must
      retrieve nothing at all. Catches a predicate that is present but wrong.
    * **Disjoint tag** — a principal holding every corpus tag *except* the ones the
      question requires must retrieve none of that question's gold chunks. This is
      the control that catches a real cross-permission leak, and it is checked
      against gold documents rather than gold chunks so a partial leak still
      fails.
    """
    control = AclControl()
    for entry in entries:
        if not entry.answerable:
            continue
        control.questions_checked += 1
        vector = embedder.embed_one(entry.question)

        ghost = await dense_search(
            session,
            embedding=vector,
            workspace_id=WORKSPACE_ID,
            acl_tags=("__nonexistent__",),
            limit=limit,
        )
        if ghost:
            control.nonexistent_tag_leaks += 1
            control.leaks.append(f"{entry.id}: nonexistent tag returned {len(ghost)} rows")

        denied = tuple(sorted(set(all_tags) - set(entry.required_acl_tags)))
        if not denied:
            continue
        visible = await dense_search(
            session,
            embedding=vector,
            workspace_id=WORKSPACE_ID,
            acl_tags=denied,
            limit=limit,
        )
        leaked = [hit for hit in visible if hit.document_id in set(entry.gold_doc_ids)]
        if leaked:
            control.disjoint_tag_gold_leaks += 1
            documents = sorted({hit.document_id for hit in leaked})
            control.leaks.append(
                f"{entry.id}: a principal lacking {entry.required_acl_tags} retrieved "
                f"{len(leaked)} chunk(s) from {documents}"
            )
    return control


async def run(*, ks: tuple[int, ...], limit: int) -> int:
    settings = get_settings()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    embedder = build_embedder(settings.embedding_model)
    if not embedder.is_semantic:
        print(
            f"refusing to publish a report from non-semantic embedder {embedder.name!r}",
            file=sys.stderr,
        )
        return 2

    if embedder.dim != settings.embedding_dim:
        print(
            f"embedder dim {embedder.dim} != configured GKP_EMBEDDING_DIM "
            f"{settings.embedding_dim}; set it to match or the vector column will not fit",
            file=sys.stderr,
        )
        return 2

    corpus = build_corpus()
    chunks = [
        chunk
        for doc_id in sorted(corpus.rendered)
        for chunk in chunk_document(doc_id, corpus.rendered[doc_id])
    ]
    entries, resolution = build_golden_set(corpus, chunks)

    all_tags = tuple(sorted({tag for doc in corpus.documents.values() for tag in doc.acl_tags}))
    started = datetime.now(UTC)
    run_id = started.strftime("%Y%m%dT%H%M%SZ")
    print(f"[{run_id}] corpus={corpus.content_hash} chunks={len(chunks)} questions={len(entries)}")

    engine = get_engine(settings)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as session:
        await _reset(session)
        print(f"indexing {len(chunks)} chunks with {embedder.name} ...")
        index_started = time.perf_counter()
        await _load_corpus(session, embedder, chunks, corpus)
        index_seconds = time.perf_counter() - index_started

        all_tags = tuple(sorted({tag for doc in corpus.documents.values() for tag in doc.acl_tags}))

        rows: list[dict[str, Any]] = []
        query_started = time.perf_counter()
        for entry in entries:
            vector = embedder.embed_one(entry.question)
            query_t0 = time.perf_counter()
            hits = await dense_search(
                session,
                embedding=vector,
                workspace_id=WORKSPACE_ID,
                acl_tags=entry.required_acl_tags,
                limit=limit,
            )
            query_ms = (time.perf_counter() - query_t0) * 1000

            retrieved = [hit.chunk_id for hit in hits]
            gold = frozenset(entry.gold_chunk_ids)
            scores = score_question(retrieved, gold, ks=ks)

            row: dict[str, Any] = {
                "id": entry.id,
                "question": entry.question,
                "answerable": entry.answerable,
                "category": entry.category,
                "acl_tags": list(entry.required_acl_tags),
                "gold_chunk_ids": sorted(gold),
                "gold_doc_ids": list(entry.gold_doc_ids),
                "retrieved": retrieved,
                "latency_ms": round(query_ms, 3),
            }
            for score in scores:
                row[f"recall@{score.k}"] = score.recall
                row[f"precision@{score.k}"] = score.precision
                row[f"reciprocal_rank@{score.k}"] = score.reciprocal_rank
                row[f"ndcg@{score.k}"] = score.ndcg
            rows.append(row)
        query_seconds = time.perf_counter() - query_started

        print("running ACL negative controls ...")
        control = await _run_acl_controls(
            session, entries, embedder=embedder, all_tags=all_tags, limit=limit
        )

    answerable = [r for r in rows if r["answerable"]]
    unanswerable = [r for r in rows if not r["answerable"]]
    overall = aggregate(answerable, ks=ks, label="overall")
    by_category = {
        category: aggregate(
            [r for r in answerable if r["category"] == category], ks=ks, label=category
        )
        for category in sorted({r["category"] for r in answerable})
    }

    raw_path = RAW_DIR / f"baseline-{run_id}.jsonl"
    with raw_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    metadata = RunMetadata(
        run_id=run_id,
        started_at=started.isoformat(),
        corpus_hash=corpus.content_hash,
        golden_hash="",
        embedder=embedder.name,
        embedder_dim=embedder.dim,
        chunk_target_chars=512,
        chunk_overlap_chars=64,
        documents=len(corpus.documents),
        chunks=len(chunks),
        questions_total=len(entries),
        questions_answerable=len(answerable),
        candidate_limit=limit,
        ks=list(ks),
        host=platform.node(),
        python=platform.python_version(),
        git_commit=_git_commit(),
    )

    report = _render_report(
        metadata=metadata,
        overall=overall,
        by_category=by_category,
        rows=answerable,
        unanswerable=unanswerable,
        control=control,
        resolution_multi=len(resolution.multi_chunk_spans),
        index_seconds=index_seconds,
        query_seconds=query_seconds,
    )
    report_path = RESULTS_DIR / "BASELINE.md"
    report_path.write_text(report, encoding="utf-8")

    print()
    print(markdown_table(overall, title="Overall (dense-only)"))
    print()
    print(
        f"ACL controls: {control.questions_checked} questions, "
        f"nonexistent-tag leaks={control.nonexistent_tag_leaks}, "
        f"disjoint-tag gold leaks={control.disjoint_tag_gold_leaks}"
    )
    print(f"report written to {report_path.relative_to(ROOT)}")
    print(f"raw rows written to {raw_path.relative_to(ROOT)}")

    if not control.clean:
        print("\nACL CONTROL FAILED", file=sys.stderr)
        for leak in control.leaks[:10]:
            print(f"  {leak}", file=sys.stderr)
        return 1
    return 0


def _render_report(
    *,
    metadata: RunMetadata,
    overall: list[MetricRow],
    by_category: dict[str, list[MetricRow]],
    rows: list[dict[str, Any]],
    unanswerable: list[dict[str, Any]],
    control: AclControl,
    resolution_multi: int,
    index_seconds: float,
    query_seconds: float,
) -> str:
    recall10 = next((r for r in overall if r.metric == "recall" and r.k == 10), None)
    ndcg10 = next((r for r in overall if r.metric == "ndcg" and r.k == 10), None)

    lines = [
        "# Dense Retrieval Baseline",
        "",
        "Generated by `python -m gkp.eval.runners.baseline`. Committed output, not a",
        "hand-written table: M2's hybrid retrieval must beat these numbers.",
        "",
        "## Run metadata",
        "",
        "| field | value |",
        "| --- | --- |",
        f"| run id | `{metadata.run_id}` |",
        f"| git commit | `{metadata.git_commit}` |",
        f"| corpus hash | `{metadata.corpus_hash}` |",
        f"| embedder | `{metadata.embedder}` (dim {metadata.embedder_dim}) |",
        f"| chunking | {metadata.chunk_target_chars}c / "
        f"{metadata.chunk_overlap_chars}c overlap, structural |",
        f"| documents | {metadata.documents} |",
        f"| chunks | {metadata.chunks} |",
        f"| candidate limit | {metadata.candidate_limit} |",
        f"| questions | {metadata.questions_total} ({metadata.questions_answerable} answerable) |",
        f"| index time | {index_seconds:.1f}s |",
        f"| query time | {query_seconds:.1f}s total |",
        f"| host | {metadata.host} · Python {metadata.python} |",
        "",
        "## Overall",
        "",
        markdown_table(overall, title="dense-only", heading=False),
        "",
        f"{resolution_multi} gold spans resolve to more than one chunk, because the",
        "chunker's overlap window repeats boundary text. Those questions therefore have",
        "more than one acceptable answer, which inflates recall slightly. It is stated",
        "here rather than adjusted away.",
        "",
        "## By category",
        "",
    ]
    for category, metric_rows in by_category.items():
        lines.append(markdown_table(metric_rows, title=category))
        lines.append("")

    lines.extend(
        [
            "## Permission controls",
            "",
            f"- questions checked: **{control.questions_checked}**",
            f"- leaks via a nonexistent tag: **{control.nonexistent_tag_leaks}**",
            f"- leaks of a gold document to a principal lacking its tags: "
            f"**{control.disjoint_tag_gold_leaks}**",
            "",
            "Both must be exactly zero. This is an invariant, not a metric: any nonzero",
            "value fails the run.",
            "",
        ]
    )
    if not control.clean:
        lines.append("**CONTROL FAILED**")
        lines.extend(f"- {leak}" for leak in control.leaks[:20])
        lines.append("")

    lines.extend(
        [
            "## Unanswerable questions",
            "",
            f"{len(unanswerable)} questions in the golden set have no answer in the corpus,",
            "including deliberate traps (a service tier that does not exist, a severity",
            "level that is never defined). Retrieval cannot be scored for them — there is",
            "no gold chunk — and they exist to measure *refusal* behaviour once generation",
            "exists in M6. They are excluded from every mean above, and counted here so the",
            "exclusion is visible.",
            "",
            "## Reading these numbers",
            "",
            "- Every mean is over the stated `n`; `excluded` counts rows whose metric was",
            "  undefined (all of them zero-gold rows, which are excluded by construction).",
            "- 95% intervals are percentile bootstrap over per-question scores, seeded,",
            "  so a re-run of an unchanged configuration reproduces them exactly.",
            "- **The corpus is synthetic.** The methodology is real and the corpus is",
            "  published and reproducible; the document distribution is not a real",
            "  enterprise corpus. See `results/README.md`.",
            "",
        ]
    )
    if recall10 and ndcg10:
        lines.extend(
            [
                "## Headline",
                "",
                f"- **recall@10 = {recall10.mean:.4f}** (95% CI {recall10.ci}), n={recall10.n}",
                f"- **nDCG@10 = {ndcg10.mean:.4f}** (95% CI {ndcg10.ci}), n={ndcg10.n}",
                "",
            ]
        )
    return "\n".join(line for line in lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dense-only retrieval baseline")
    parser.add_argument(
        "--ks",
        default=",".join(str(k) for k in DEFAULT_KS),
        help="comma-separated cutoffs to score at",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="candidate window requested from the retriever",
    )
    args = parser.parse_args(argv)

    try:
        ks = tuple(int(part) for part in str(args.ks).split(",") if part.strip())
    except ValueError:
        parser.error(f"--ks must be comma-separated integers, got {args.ks!r}")
    if not ks:
        parser.error("--ks must contain at least one cutoff")

    max_k = max(ks)
    if args.limit < max_k:
        parser.error(
            f"--limit ({args.limit}) must be at least the largest k ({max_k}); "
            "otherwise the larger cutoffs are unmeasurable"
        )

    # Outside the event loop on purpose: Alembic's env.py owns its own asyncio.run.
    _migrate()
    return asyncio.run(run(ks=ks, limit=args.limit))


if __name__ == "__main__":
    try:
        exit_code = main()
    except KeyboardInterrupt:  # pragma: no cover
        exit_code = 130
    sys.exit(exit_code)
