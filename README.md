# Grounded Knowledge Platform

[![ci](https://github.com/aditya0si/grounded-knowledge-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/aditya0si/grounded-knowledge-platform/actions/workflows/ci.yml)
[![python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![mypy](https://img.shields.io/badge/mypy-strict-blue.svg)](https://mypy-lang.org/)
[![license](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Enterprise-grade RAG where the retrieval numbers are measured, not asserted.**

ACL-enforced hybrid retrieval over an internal-docs corpus. Retrieval quality is
measured against gold chunk labels and gated in CI; permission boundaries are
enforced *inside* the retrieval predicate rather than filtered after the fact.

---

## Why this exists

Most RAG projects, including the prototype this one replaces, report an
impressive faithfulness score produced by a harness that **could not have
failed**. In the predecessor repo the evaluation corpus came to 151 words in
three chunks while the retriever requested `top-k=6` — so retrieval returned the
entire corpus on every query, and every published metric was a measurement of
generation alone. The test set carried no gold chunk identifiers, which meant
recall@k, MRR, and nDCG were not computable at all.

The pipeline was fine. The **harness** was the problem, and a harness that cannot
fail cannot defend an improvement.

This project is built the other way round: the evaluation harness exists before
the retrieval improvements it measures, and it is designed so that a regression
turns the build red.

## Status

Honest, per-milestone. Nothing below claims to be finished when it is not.

| Milestone | Scope | State |
|---|---|---|
| **M0** | Skeleton, dev stack, CI, strict typing | ✅ complete |
| **M1** | Corpus, golden set, metric functions, dense baseline, ACL negative control | ✅ complete |
| **M2** | Hybrid retrieval (RRF) + cross-encoder rerank, proven by ablation | 🚧 in progress |
| **M3** | Parsing / chunking / embedding ablation | ⬜ planned |
| **M4** | Durable, idempotent ingestion | ⬜ planned |
| **M5** | Tenancy and authentication | ⬜ planned |
| **M6** | Verified citations, untrusted-context hardening | ⬜ planned |
| **M7** | Cost, latency, observability, load test | ⬜ planned |
| **M8** | Live demo surface | ⬜ planned |

The full plan, including the milestone acceptance criteria, lives in
[`.hermes/plans/`](.hermes/plans/).

## Measured baseline

Dense retrieval alone, measured before hybrid retrieval or reranking exists, so
M2 has something to beat that was measured rather than assumed. Full report with
per-category breakdowns: [`results/BASELINE.md`](results/BASELINE.md).

**Corpus:** 89 documents · 153,558 characters · 325 chunks · 54 questions
(42 answerable, 12 unanswerable). **Embedder:** `BAAI/bge-small-en-v1.5` (384d).

| metric | k | mean | 95% CI | n |
|---|---|---|---|---|
| recall | 1 | 0.6071 | [0.464, 0.738] | 42 |
| recall | 5 | 0.9167 | [0.821, 0.988] | 42 |
| recall | 10 | 0.9167 | [0.821, 0.988] | 42 |
| recall | 20 | 0.9762 | [0.929, 1.000] | 42 |
| nDCG | 10 | 0.7919 | [0.696, 0.875] | 42 |
| MRR | 20 | 0.7621 | [0.659, 0.857] | 42 |

**Permission controls: 0 leaks.** Two negative controls run on every question — a
principal holding a tag no document carries must retrieve nothing, and a principal
holding every corpus tag *except* the ones a question requires must retrieve none
of that question's gold documents. Any nonzero count fails the run. This is an
invariant, not a metric.

Two things this baseline already shows, stated rather than smoothed over:

- **recall@5 = recall@10 exactly.** Retrieving more does not help past five, so
  the remaining misses are a *ranking* problem, not a window problem. That is
  precisely the failure hybrid retrieval and reranking are supposed to address,
  and it is the gap M2 has to close.
- **recall@20 = 0.9762, and exactly one question never retrieves its gold chunk at
  any window size.** It is `f_ticket_split_table` — *"What caused the relevance
  regression reported by a customer in INC-88490?"* — whose gold chunk contains
  the literal string `INC-88490`, and whose top-6 results are six *other* monthly
  ticket archives that share its vocabulary. A dense arm cannot distinguish an
  exact identifier from a semantically similar one. This is the textbook case for
  the sparse arm and is the concrete hypothesis M2 has to test.
- **policy-lookup recall@10 is 0.75** against 1.00 for version-conflict and
  restricted questions. The category that looks easiest is the one that fails.

## Architecture

```mermaid
flowchart TB
    subgraph client["Client"]
        UI["Demo UI (M8)"]
    end

    subgraph api["API — FastAPI"]
        AUTH["auth → workspace_id<br/><i>server-derived, never client-supplied</i>"]
        Q["/query"]
    end

    subgraph data["Data — single Postgres instance"]
        PG[("Postgres 16<br/>pgvector + tsvector")]
        CH["chunks<br/>embedding ‖ tsv ‖ acl_tags"]
        PG --- CH
    end

    subgraph ret["Retrieval"]
        D["dense arm<br/>HNSW cosine"]
        S["sparse arm<br/>GIN ts_rank_cd"]
        F["RRF fusion<br/>k=60"]
        R["cross-encoder<br/>rerank"]
        D --> F
        S --> F
        F --> R
    end

    subgraph sup["Supporting"]
        RD[("Redis<br/>cache · queue")]
        OBJ[("MinIO / R2<br/>originals")]
        W["worker<br/>ingest (M4)"]
    end

    UI --> AUTH --> Q
    Q --> D
    Q --> S
    CH -.->|"workspace_id = $1<br/>AND acl_tags && $2"| D
    CH -.->|"workspace_id = $1<br/>AND acl_tags && $2"| S
```

**Both retrieval arms and the permission predicate execute in one transactional
query.** A dedicated vector database forces a two-phase *fetch-then-filter*,
which either leaks rows across permission boundaries or silently destroys recall
when the filter is applied after ANN. See [ADR-001](docs/adr/ADR-001-postgres-over-vector-db.md).

## Design decisions

| ADR | Decision |
|---|---|
| [001](docs/adr/ADR-001-postgres-over-vector-db.md) | Postgres + pgvector + tsvector over a dedicated vector DB |
| [002](docs/adr/ADR-002-evaluation-before-optimization.md) | Build the evaluation harness before the retrieval improvements |
| [003](docs/adr/ADR-003-deterministic-retrieval-metrics.md) | Retrieval metrics computed in-process; LLM judges only for generation |
| [004](docs/adr/ADR-004-server-derived-acl.md) | ACL filtering is server-derived and applied in the retrieval predicate |

## Quickstart

Requires [uv](https://docs.astral.sh/uv/) and Docker.

```bash
git clone https://github.com/aditya0si/grounded-knowledge-platform.git
cd grounded-knowledge-platform

uv sync --all-extras          # create the locked environment
python scripts/tasks.py up    # start Postgres + Redis + MinIO, wait for health
python scripts/tasks.py check # ruff + mypy --strict + unit tests
```

The API runs on **:8010** (ports are offset from their defaults so this stack can
coexist with other local Postgres/Redis containers):

```bash
python scripts/tasks.py serve
# then: http://localhost:8010/docs
```

**The test suite passes with no provider API key and no running infrastructure.**
Anything requiring live services is marked `integration` and excluded from the
default job. Retrieval evaluation (M1/M2) makes no LLM calls at all, so the
measured-retrieval story is reproducible at zero cost.

### Task runner

`make` is not available on every development machine, so tasks are defined once
in [`scripts/tasks.py`](scripts/tasks.py) and the `Makefile` delegates to it —
there is exactly one definition of each command, so local and CI runs cannot
drift.

```bash
python scripts/tasks.py --list
```

## Repository layout

```
src/gkp/
  api/         HTTP layer — routers and schemas
  core/        config, logging, Redis, security
  db/          SQLAlchemy models, Alembic migrations, repositories
  ingest/      parsing, chunking, embedding, durable queue (M4)
  retrieve/    dense · sparse · RRF fusion · reranking
  generate/    provider adapters, prompts, citation verification (M6)
  eval/        corpus · golden set · metric functions · runners · reporting
```

## What this project does *not* claim

Stated up front so the numbers above are read in context:

- **The evaluation corpus is synthetic.** The *methodology* is real — the corpus
  is published, the gold labels are derived from construction, and the harness
  is gated in CI — but the document *distribution* is not a real enterprise
  corpus. This is repeated in every results file, not buried here.
- **Single-node Postgres.** The ACL design is scale-ready; the deployment is not.
  No horizontal-scale claim is made, and the chunk count at which the ANN index
  was tested is stated rather than generalised from.
- **No generation quality is claimed yet.** M6 adds citations and refusal
  behaviour. Until then the 12 unanswerable questions measure nothing and are
  excluded from every mean, which is why the `excluded` column exists.
- **No uptime, throughput-at-scale, or cost-per-user figures** until M7's load
  test and a live deployment actually produce them. If they are not measured,
  they are not published.

## Roadmap

Evaluation-first, by construction: corpus and golden set → metric functions →
dense baseline → ACL negative control → hybrid + rerank proven by ablation →
parsing ablation → durable ingestion → tenancy → verified citations → cost and
latency → demo surface.

## License

MIT — see [LICENSE](LICENSE).
