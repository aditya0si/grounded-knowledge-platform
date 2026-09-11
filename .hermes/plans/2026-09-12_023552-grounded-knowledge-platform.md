# Grounded Knowledge Platform — Implementation Plan

**Goal:** An enterprise-grade RAG system — ACL-enforced retrieval over an internal-docs corpus, retrieval quality measured against gold chunk labels and gated in CI, citations verified against source spans, durable idempotent ingestion, and published numbers with an honest limitations section.

**Architecture:** FastAPI over Postgres 16 + pgvector + `tsvector`, fused with Reciprocal Rank Fusion and reranked by a local cross-encoder. One database carries both retrieval arms *and* the ACL predicate, so tenant and permission filtering happen inside the index scan rather than as a post-filter. Ingestion is content-addressed, queued, and idempotent. Retrieval is measured before any product surface is built.

**Tech stack:** Python 3.12 · FastAPI · SQLAlchemy 2 (async) + asyncpg · Alembic · pgvector 0.7 · Redis 7 + arq · MinIO/R2 · BAAI embeddings · local cross-encoder reranker · pluggable LLM providers · k6 · Docker Compose

**Status:** M0–M2 specified to task level. M3–M9 scoped with acceptance criteria; each gets its own plan when reached.

---

## 1. Context and assumptions

**Predecessor:** `aditya0si/agentic_rag_system` (local: `Desktop/Agentic Research`) stays frozen and public as the v1 prototype. It is not modified by this work.

**Why v1 cannot be extended into this:** measured on 2026-09-12 —

| v1 state | Consequence |
|---|---|
| Eval corpus = 3 docs / **151 words** → **3 chunks** | Retriever requests `top-k=6` from a 3-chunk corpus |
| `eval/test_set.json` = 15 pairs, **no gold chunk IDs** | recall@k / MRR / nDCG are uncomputable |
| RAGAS never runs in CI | No retrieval regression can be detected |
| Integration tests end in `|| true` | Integration failures are non-blocking |
| Sessions in a process-local dict | No persistence, no tenancy |
| No auth, no workspace boundary | No permission model to enforce |

v1's pipeline design is sound and gets carried forward. Its **evaluation harness is the part that is rewritten**, because a harness that cannot fail cannot defend anything.

**Assumptions:**
- Portfolio flagship. No billing, no external user commitments, no ops/SLA promises.
- Corpus is internal-docs shaped (runbooks, HR policy, tickets, changelogs), synthetic and publishable, with per-document ACL tags so permission boundaries are genuinely testable.
- Free-tier hosting and local models for embeddings/reranking; no paid vector DB.
- Development on Windows 11 / git-bash; Postgres and Redis run via Docker Compose.

---

## 2. Architecture decisions (recorded as ADRs in `docs/adr/`)

**ADR-001 — Postgres + pgvector + tsvector over a dedicated vector DB.**
Both retrieval arms and the ACL predicate live in one transactional query. A separate vector store forces fetch-then-filter, which either leaks rows across permission boundaries or silently burns recall when filtering after ANN. Managed vector stores are a *scale* answer; the binding constraint here is *correctness under permissions*. Revisit only past ~10M chunks (see §7 Limitations).

**ADR-002 — Evaluation is built before the retrieval improvements it measures.**
The ablation in M2 is only meaningful against a harness that existed before the change. Building the harness afterwards produces numbers that cannot distinguish real gains from harness calibration.

**ADR-003 — Retrieval metrics are computed in-process; only generation-side metrics use an LLM judge.**
recall@k, precision@k, MRR, and nDCG are pure functions over gold chunk IDs — deterministic, free, fast, unit-testable against hand-computed values. LLM judges are reserved for faithfulness/relevancy, and the judge's own reliability is measured against a hand-labelled subset rather than assumed.

**ADR-004 — ACL filtering is server-derived and applied in the retrieval predicate.**
The workspace ID and permission groups come from the verified token, never the request body. A client-supplied filter is not a security boundary. Leak rate is a hard gate at exactly zero, not a metric to improve.

**ADR-005 — Ingestion is content-addressed and idempotent.**
`checksum = sha256(bytes)` is the idempotency key. Re-uploading an identical file is a no-op; a changed file supersedes the prior document version rather than duplicating vectors.

---

## 3. Repository layout

```
grounded-knowledge-platform/
├── .github/workflows/
│   ├── ci.yml                    # lint, typecheck, unit tests
│   └── eval.yml                  # retrieval eval gate (M1+)
├── docker-compose.yml            # postgres(pgvector) + redis + minio
├── pyproject.toml                # uv-managed, pinned
├── Makefile                      # make up / test / eval-retrieval / ablation
├── src/gkp/
│   ├── api/                      # routers: health, auth, documents, query
│   ├── core/                     # config, security, acl, errors, logging
│   ├── db/                       # models, migrations/, repositories/
│   ├── ingest/                   # parsers/, chunkers/, pipeline.py, worker.py
│   ├── retrieve/                 # dense.py, sparse.py, fuse.py, rerank.py
│   ├── generate/                 # providers/, prompts/, citations.py
│   └── eval/                     # golden.py, metrics.py, runners/, report.py
├── corpus/                       # synthetic source docs + generator
├── eval/golden/*.jsonl           # gold question set
├── results/                      # published eval output (committed)
├── docs/adr/, docs/architecture.md
└── tests/
```

---

## 4. Data model

```sql
users        (id, email, created_at)
workspaces   (id, name, owner_id, created_at)
memberships  (user_id, workspace_id, role)              -- viewer | editor | admin
grants       (principal_id, acl_tag)                    -- principal -> tag membership

documents    (id, workspace_id, storage_key, checksum UNIQUE,
              title, doc_type, status, page_count, chunk_count,
              acl_tags text[], version, superseded_by, created_at)

chunks       (id, document_id, workspace_id, seq, text, token_count,
              page, section, embedding vector(768), tsv tsvector,
              acl_tags text[])                          -- denormalized for the scan

conversations(id, workspace_id, user_id, title, created_at)
messages     (id, conversation_id, role, content, citations jsonb,
              model_version, index_version, prompt_version, created_at)
usage_events (id, workspace_id, kind, unit_count,
              idempotency_key UNIQUE, created_at)
```

`acl_tags` is denormalized onto `chunks` so the permission predicate is satisfied inside the same index scan that produces candidates — no join back to `documents` on the hot path. A trigger keeps the two in sync; a test asserts they never diverge.

Indexes:

```sql
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX ON chunks USING gin (tsv);
CREATE INDEX ON chunks USING gin (acl_tags);
CREATE INDEX ON chunks (workspace_id);
```

---

## 5. Hybrid retrieval

Single statement, both arms filtered by workspace and ACL, fused by RRF (k=60, Cormack et al.):

```sql
WITH q AS (
  SELECT websearch_to_tsquery('english', $4) AS tsq, $1::vector AS emb
),
dense AS (
  SELECT c.id, row_number() OVER (ORDER BY c.embedding <=> q.emb) AS rnk
  FROM chunks c, q
  WHERE c.workspace_id = $2 AND c.acl_tags && $3::text[]
  ORDER BY c.embedding <=> q.emb
  LIMIT $5
),
sparse AS (
  SELECT c.id, row_number() OVER (ORDER BY ts_rank_cd(c.tsv, q.tsq) DESC) AS rnk
  FROM chunks c, q
  WHERE c.workspace_id = $2 AND c.acl_tags && $3::text[]
    AND c.tsv @@ q.tsq
  ORDER BY ts_rank_cd(c.tsv, q.tsq) DESC
  LIMIT $5
),
fused AS (
  SELECT id, SUM(1.0 / (60 + rnk)) AS rrf_score
  FROM (SELECT id, rnk FROM dense UNION ALL SELECT id, rnk FROM sparse) u
  GROUP BY id
)
SELECT f.id, f.rrf_score, c.text, c.page, c.document_id
FROM fused f JOIN chunks c ON c.id = f.id
ORDER BY f.rrf_score DESC
LIMIT $6;
```

Cross-encoder reranks the fused top-50 down to the context window (6–8 chunks).

---

## 6. Milestones

### M0 — Repository skeleton, green from the first commit

**Acceptance:** `docker compose up -d && make test` passes on a clean clone; `/health` returns 200; CI green; **no provider API key required** for the suite to pass.

| # | Task | Files |
|---|---|---|
| 0.1 | Init repo, MIT license, `.gitignore`, README stub | `README.md`, `LICENSE`, `.gitignore` |
| 0.2 | `uv init`; pin FastAPI, SQLAlchemy 2, asyncpg, alembic, pgvector, pydantic-settings, structlog, arq, pytest, ruff, mypy | `pyproject.toml` |
| 0.3 | Compose: `pgvector/pgvector:pg16`, redis:7, minio; healthchecks on all three | `docker-compose.yml` |
| 0.4 | Settings via pydantic-settings; no secrets in defaults | `src/gkp/core/config.py` |
| 0.5 | FastAPI app + `/health` returning `{status, db, redis}` | `src/gkp/api/main.py` |
| 0.6 | structlog JSON config | `src/gkp/core/logging.py` |
| 0.7 | ruff + mypy(strict) pre-commit hooks | `.pre-commit-config.yaml` |
| 0.8 | CI: lint → typecheck → unit tests | `.github/workflows/ci.yml` |
| 0.9 | First commit + `gh repo create` (public) | — |

*Test:* `tests/test_health.py` — asserts 200 and shape; must pass with `POSTGRES_*` unset by degrading gracefully.

---

### M1 — Corpus, golden set, and retrieval measurement

The milestone that makes every later claim checkable. **No generation, no LLM calls, no frontend in M1.**

**Acceptance:** `make eval-retrieval` prints a dense-only baseline table on the real corpus; every metric function is unit-tested against hand-computed values; the ACL negative-control test asserts zero leakage; CI runs the gate.

#### M1.1 — Corpus construction

Deliberate hostility, because a corpus of clean self-contained prose flatters retrieval and proves nothing:

| Property | Why it stresses the system |
|---|---|
| Versioned policy docs (v1..v3, near-duplicate) | Distinguishes "retrieved the right chunk" from "retrieved a similar-looking stale one" |
| Tables embedded in PDF/DOCX | Defeats naive character chunking; carries tables in M3 |
| Cross-referenced runbooks ("see §3.2 of X") | Requires multi-chunk answers; exposes single-hop-only retrieval |
| Changelog/incident-ticket mix | Mixed structure and register within one corpus |
| Per-doc ACL tags (`eng`, `hr`, `sec`, `all`) | Makes permission boundaries testable |
| Distractor documents sharing vocabulary | Lexical overlap without answering the question |

- **Task 1.1.1** — Corpus generator emitting documents + a manifest (`corpus/manifest.jsonl`) recording, per document: id, title, type, acl_tags, version, and the structured facts it contains. Gold labels derive from *construction*, not from a model guessing.
- **Task 1.1.2** — Render to PDF (one with a real table), DOCX, Markdown, HTML.
- **Task 1.1.3** — `tests/test_corpus.py`: manifest parses; every doc renders; ACL tags present on every entry; verifies the intended hostility properties actually exist (assert ≥2 near-duplicate version families, ≥1 table doc, ≥1 cross-reference chain).

#### M1.2 — Golden set

- **Task 1.2.1** — Generate candidates from the manifest: for each fact, a question whose answering chunk(s) are known by construction.
- **Task 1.2.2** — Hand-review the full set. Rewrite unnaturally-phrased questions; drop any question answerable from more than one chunk family in an ambiguous way.
- **Task 1.2.3** — Emit `eval/golden/questions.jsonl`:

```json
{
  "id": "q0042",
  "question": "What is the retention period for incident tickets?",
  "answerable": true,
  "gold_chunk_ids": ["c_881", "c_882"],
  "gold_doc_ids": ["doc_incident_policy_v3"],
  "required_acl_tags": ["eng"],
  "expected_span": "tickets are retained for 400 days",
  "category": "policy-lookup",
  "notes": "v2 says 365 — v3 is authoritative"
}
```

- **Task 1.2.4** — Include ≥15% **unanswerable** questions (`answerable: false`, empty gold) to measure refusal correctness. A system that never refuses cannot be measured for hallucination.
- **Task 1.2.5** — `tests/test_golden.py`: every `gold_chunk_id` resolves in the loaded corpus; every `expected_span` appears verbatim in at least one gold chunk; no duplicates; category and ACL distributions reported.

Target size: ~120 questions. Small enough to hand-review, large enough for stable aggregates.

#### M1.3 — Metric functions (TDD, no database)

- **Task 1.3.1** — `recall_at_k`, `precision_at_k`, `reciprocal_rank`, `ndcg_at_k` in `src/gkp/eval/metrics.py`.
- **Task 1.3.2** — `tests/test_metrics.py` with hand-computed expectations, including edge cases: empty gold, k > len(retrieved), all-gold-retrieved, none-retrieved.

```python
def recall_at_k(retrieved: list[str], gold: set[str], k: int) -> float:
    if not gold:
        return float("nan")
    return len(set(retrieved[:k]) & gold) / len(gold)


def reciprocal_rank(retrieved: list[str], gold: set[str], k: int) -> float:
    for i, cid in enumerate(retrieved[:k], 1):
        if cid in gold:
            return 1.0 / i
    return 0.0


def ndcg_at_k(retrieved: list[str], gold: set[str], k: int) -> float:
    dcg = sum(1.0 / math.log2(i + 1) for i, cid in enumerate(retrieved[:k], 1) if cid in gold)
    idcg = sum(1.0 / math.log2(i + 1) for i in range(1, min(len(gold), k) + 1))
    return dcg / idcg if idcg else float("nan")
```

*Run:* `pytest tests/test_metrics.py -v` → expected PASS with hand-checked values.

#### M1.4 — Dense retrieval arm + baseline runner

- **Task 1.4.1** — Embedding provider interface `embed(texts: list[str]) -> list[list[float]]`; local BGE adapter; a `FakeEmbedder` (deterministic hash-based) for tests so CI needs no model download.
- **Task 1.4.2** — Alembic migration creating the schema in §4 with the HNSW/GIN indexes.
- **Task 1.4.3** — Ingestion for M1: parse → chunk (fixed 512 tokens / 64 overlap) → embed → insert with `acl_tags`.
- **Task 1.4.4** — `query_dense(conn, emb, workspace_id, acl_tags, k)`.
- **Task 1.4.5** — Runner: for each golden question, retrieve top-20, score at k ∈ {1,3,5,10,20}, stream one JSONL row per question to `results/<run_id>.jsonl` (`flush` per row — a killed run must leave salvageable output).
- **Task 1.4.6** — Report: aggregate to a markdown table with mean and bootstrap 95% CIs, `n` printed alongside every mean.

*Run:* `make eval-retrieval` → baseline table written to `results/BASELINE.md`.

#### M1.5 — ACL negative control (hard gate)

- **Task 1.5.1** — For every golden question, re-run retrieval as a principal **lacking** `required_acl_tags`; assert the result set is empty.
- **Task 1.5.2** — `tests/test_acl_isolation.py` also covering: cross-workspace isolation; a document deleted by one user being unreachable by another; and `chunks.acl_tags` never diverging from `documents.acl_tags` (trigger correctness).
- **Task 1.5.3** — CI gate: leak count must be exactly `0`. Any nonzero exit fails the build.

#### M1.6 — CI eval gate

- **Task 1.6.1** — `.github/workflows/eval.yml`: spin Postgres+pgvector service container, load corpus, run the golden set, assert `recall@10 >= <baseline>` and `acl_leak == 0`.
- **Task 1.6.2** — Commit `results/BASELINE.md`; the threshold is set from the measured baseline, not guessed in advance.

---

### M2 — Hybrid retrieval and reranking, proven against M1

**Acceptance:** a committed ablation matrix over the full parameter grid with CIs; hybrid+rerank beats the M1 dense baseline by a stated margin **or the negative result is published as the finding**.

| # | Task | Files |
|---|---|---|
| 2.1 | `tsv` generated column + GIN index + sync trigger | migration |
| 2.2 | `query_sparse` using `websearch_to_tsquery` + `ts_rank_cd` | `src/gkp/retrieve/sparse.py` |
| 2.3 | RRF fusion (SQL from §5) | `src/gkp/retrieve/fuse.py` |
| 2.4 | Cross-encoder reranker behind an interface; `FakeReranker` for CI | `src/gkp/retrieve/rerank.py` |
| 2.5 | Ablation runner over the grid below, one JSONL row per cell, streamed | `src/gkp/eval/runners/ablation.py` |
| 2.6 | Bootstrap CIs + per-cell deltas vs baseline | `src/gkp/eval/report.py` |
| 2.7 | Report → `results/ABLATION.md` + chart | `results/` |
| 2.8 | Per-stage attribution: dense-only / sparse-only / fused / reranked, so a regression is localised to a stage | `src/gkp/eval/runners/` |

**Grid:** retrieval {dense, sparse, hybrid} × chunk_size {256, 512, 1024} × overlap {32, 64} × rerank {off, on} × k {5, 10, 20} — run the full product only if runtime permits; otherwise fix overlap=64 and k=20 and say so explicitly in the report.

**Negative-result policy:** if hybrid does not beat dense on this corpus, publish that with the per-category breakdown. A documented negative result with a harness that could have shown a positive is stronger evidence than a positive result from a harness that could not have failed — and it matches how the corpus actually behaves on short, lexically-dense internal docs.

---

### M3 — Parsing and chunking ablation

**Scope:** table extraction (pdfplumber → markdown tables, not `str(cell)` soup); header-aware chunking that keeps a section's heading path as chunk metadata; semantic vs fixed chunking; embedding model comparison (`bge-base-en-v1.5` vs `bge-large-en-v1.5` vs `bge-m3`); reranker comparison (MiniLM-L6 vs `bge-reranker-base`).

**Acceptance:** each change reported as a delta on the M1/M2 harness with CIs, attributed per category (policy-lookup, table-lookup, multi-hop). At least one measured negative — a change that did *not* help — reported honestly.

**Note:** `chunks.embedding` dimension is fixed per migration; switching models requires a migration + reindex. Script this as `make reindex MODEL=...` so the ablation is reproducible rather than manual.

---

### M4 — Durable, idempotent ingestion

**Scope:** object storage (MinIO dev / R2 prod); `arq` worker; status machine `queued → parsing → chunking → embedding → ready | failed`; retry with exponential backoff; dead-letter queue; checksum idempotency; document versioning with `superseded_by`; cascade delete.

**Acceptance:** killing the worker mid-parse resumes correctly on restart; re-uploading an identical file creates zero new chunks (asserted by count); a worker crash leaves the document in `failed` with a reason rather than a silent zombie; upload returns a job ID immediately and the UI can poll status.

**Tests:** `tests/test_ingest_idempotency.py`, `tests/test_ingest_recovery.py` — both must pass without network access.

---

### M5 — Tenancy and authentication

**Scope:** JWT access (15 min) + refresh (7 d) in httpOnly cookies; OAuth (Google, GitHub) optional given the portfolio goal; workspace-scoped repositories where `workspace_id` is a required constructor argument so an unscoped query is a type error rather than a code review catch; membership roles; usage metering into `usage_events` with idempotency keys.

**Acceptance:** every route is authenticated by an explicit allow-list — a new route added without a dependency fails a test that enumerates routes; user A cannot read user B's document, conversation, or citation text even with a hand-crafted chunk ID; deleting a document cascades to chunks and vectors with no orphans.

**Tests:** `tests/test_tenancy.py`, `tests/test_route_authz.py` (route-enumeration test — this is the one that catches the endpoint someone adds in six months).

---

### M6 — Verified citations and untrusted-context hardening

**Scope:** the model emits only small integers handed to it in the prompt; the server resolves each to a chunk ID and validates the quoted span exists in that chunk (normalized whitespace/case) before the answer is returned. Uncited assertions are flagged. Retrieved text is delimited and carries no instruction authority; injection screening runs on the *context*, not just the query.

**Acceptance:** `citation_validity = valid_citations / emitted_citations` is computed and published; a fabricated citation is dropped and surfaced rather than rendered; a corpus document containing an injected instruction ("ignore previous instructions and…") does not change the answer for a question whose correct answer lies elsewhere — asserted as a regression test, with the hostile document committed to the corpus.

**Tests:** `tests/test_citation_verification.py`, `tests/test_prompt_injection.py`.

**Security note:** the injection test corpus is committed deliberately and labelled; it is a test fixture, not a vulnerability.

---

### M7 — Cost, latency, and observability

**Scope:** per-request token and cost ledger; per-stage timing (retrieve / rerank / generate / verify); p50/p95 from `usage_events`; a declared latency budget with a degradation policy (drop rerank, shrink k, cache hit, fallback model) that triggers on breach; k6 load test.

**Acceptance:** a k6 run at a stated concurrency publishes real p50/p95 and error rate; a cache-miss vs cache-hit comparison is published; the cost per answered question is reported in the README as a real measured number, not an estimate. **If deployment is not live, no uptime or cost-at-scale numbers are published** — that gap is stated, not filled.

---

### M8 — Live demo surface

**Scope:** minimal, text-first UI: upload → status → ask → answer with clickable citations opening the source chunk, with the ACL identity visible so the permission boundary is *demonstrable* rather than asserted. Read-only demo mode with a pre-loaded corpus and a switchable principal (e.g. `eng` vs `hr`) so a visitor can watch a query return different results for the same question — that single interaction communicates the whole enterprise thesis.

**Decisions deferred to this milestone:** Next.js vs server-rendered Jinja + htmx. Deferred deliberately — the backend is the deliverable; the frontend should not be started before the numbers exist.

**Acceptance:** deployed URL; Lighthouse pass on the demo pages; empty/loading/error states for every primary flow; mobile legible.

---

### M9 — Optional: model routing and fine-tuning

Out of scope unless M1–M8 are green. Candidate work, given the existing WSL2 + QLoRA infrastructure: a small classifier routing query difficulty to a cheap vs strong model, measured as a cost/quality trade-off on the M1 harness; and a retrieval-distillation experiment. Only attempted with a measured baseline to beat.

---

## 7. Risks, tradeoffs, limitations

| Risk | Mitigation |
|---|---|
| **Synthetic corpus invites "toy data" critique** | Publish the corpus and generator; label it synthetic in the README; report the M2/M3 ablation on a real public corpus (RFC or SEC filings) as a second column |
| **pgvector recall degrades at scale** | Report the measured crossover rather than claiming none exists; state the chunk count at which HNSW was tested; name the migration path (dedicated ANN) as future work |
| **LLM-judge metrics are themselves unvalidated** | Hand-label 30 rows; publish judge–human agreement; report judge disagreement as a limitation, not a footnote |
| **Golden set authored by the same person who built the system** | Construction-derived gold labels from the manifest (not model guesses); the full set is published for external scrutiny; unanswerable questions included |
| **Local embedding + reranker on 8 GB RAM** | Start with `bge-base-en-v1.5` (768d, ~440 MB) and MiniLM-L6 reranker (~80 MB); benchmark heavier models as part of M3 rather than assuming they fit |
| **Free-tier LLM rate limits during eval** | Judge responses cached to disk by content hash; runs batched; rows streamed per-question so an interrupted run is salvageable |
| **Scope creep toward product surface** | Billing, admin, SDKs, k8s, and Terraform are explicitly **out of scope**; frontend is M8 by construction |

**Known limitations to publish in the README (written at M8, not retrofitted):**
1. Corpus is synthetic; the evaluation *methodology* is real, the *distribution* is not.
2. Single-node Postgres — no horizontal scale claim; the ACL design is scale-ready, the deployment is not.
3. Retrieval quality is measured on ~120 questions; CIs are reported and they are not narrow.
4. No uptime, throughput-at-scale, or cost-per-user claims unless M7's load test and a live deployment actually produce them.

---

## 8. Verification summary

| Gate | Command | Pass condition |
|---|---|---|
| Lint + types | `make lint` | ruff and mypy(strict) clean |
| Unit tests | `make test` | green with no provider key and no network |
| Retrieval baseline | `make eval-retrieval` | table produced; recall@10 ≥ committed baseline |
| ACL isolation | `pytest tests/test_acl_isolation.py` | leak count **exactly 0** |
| Ablation | `make ablation` | `results/ABLATION.md` regenerated with CIs |
| Idempotency | `pytest tests/test_ingest_idempotency.py` | re-upload adds zero chunks |
| Citations | `pytest tests/test_citation_verification.py` | fabricated citations dropped, not rendered |
| Injection | `pytest tests/test_prompt_injection.py` | hostile context cannot redirect the answer |
| Load | `k6 run load/query.js` | p50/p95 published as measured |

---

## 9. Open questions

1. **Repository name** — `grounded-knowledge-platform` proposed to match `tenant-api-platform` / `event-stream-platform`. Alternatives: `enterprise-rag-platform` (most literal, most searchable), `permissioned-rag-platform` (differentiator-first). Trivially renameable before the first push; GitHub topics (`rag`, `retrieval-augmented-generation`, `pgvector`, `hybrid-search`, `abac`, `multi-tenant`) carry the discoverability regardless.
2. **Second real corpus for ablation** — RFC corpus vs SEC filings. Affects M2/M3 runtime; decide at M2.5.
3. **OAuth providers** — Google + GitHub, or start with magic-link only. Affects M5 only.
4. **Demo corpus** — a curated subset of the synthetic corpus, or a fresh small corpus authored for the demo.

---

## 10. Immediate next step

Execute **M0**, then **M1**. M1 is the milestone that changes what the project is: after it, every claim in the README is backed by a harness that was capable of falsifying it.
