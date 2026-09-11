# ADR-001 — Postgres + pgvector + tsvector over a dedicated vector database

- **Status:** Accepted
- **Date:** 2026-09-12
- **Supersedes:** the local ChromaDB store used by the prototype

## Context

The system must satisfy two requirements that are usually treated as separate
concerns and here are not:

1. **Hybrid retrieval** — dense semantic search combined with lexical search, so
   that exact identifiers (`ERR_4021`, `runbook-7`) and rare terms are not lost
   to embedding compression.
2. **Permission-scoped retrieval** — every candidate row must be authorised for
   the requesting principal *before* it is scored or returned.

Requirement 2 is the one that constrains the architecture. The common pattern
with a dedicated vector store is a two-phase query: fetch the top-k nearest
neighbours, then filter the results by tenant or ACL. That pattern has two
failure modes and both are serious:

- If the filter runs **after** the ANN cutoff, a principal whose documents are a
  small minority of the index can have their entire result set filtered away,
  because the top-k is dominated by rows they may not see. Recall collapses in a
  way that is invisible in testing with a single principal.
- If the filter is applied by the vector store as a metadata pre-filter, it
  depends on that store's filter implementation being correct and on the filter
  values arriving from a trusted source. Correctness is outsourced to a
  component outside this codebase's test boundary.

## Decision

Use **one Postgres 16 instance** with `pgvector` for dense vectors and built-in
`tsvector` full-text search for the sparse arm. Both arms and the authorisation
predicate execute inside a single SQL statement, fused by Reciprocal Rank Fusion.

```sql
WITH dense AS (
  SELECT c.id, row_number() OVER (ORDER BY c.embedding <=> q.emb) AS rnk
  FROM chunks c, q
  WHERE c.workspace_id = $2 AND c.acl_tags && $3::text[]
  ORDER BY c.embedding <=> q.emb LIMIT $5
)
-- ... sparse arm with the same WHERE clause, then RRF over the union
```

`acl_tags` is denormalised onto `chunks` so the predicate is satisfied by the
same scan that produces candidates, with no join back to `documents` on the hot
path. A trigger keeps the copies in sync and a test asserts they never diverge.

## Consequences

**Positive**

- Authorisation cannot be bypassed by a retrieval strategy, because it is part of
  the predicate that produces candidates. "Retrieval returned an unauthorised
  row" is a single invariant to test rather than a property of every code path.
- Both arms are transactionally consistent: a document deleted in a transaction
  is invisible to retrieval in the same transaction. With an external vector
  store this requires outbox coordination and eventual consistency.
- One datastore to back up, secure, and reason about. Dev/prod parity is exact.
- `pgvector`'s HNSW index is adequate well past the corpus sizes this project
  targets, and the crossover point is measurable rather than assumed.

**Negative**

- Horizontal scaling of the vector index means scaling Postgres, which is harder
  than scaling a managed ANN service. This is accepted: the deployment is
  single-node and no scale claim is made (see README limitations).
- `pgvector` is slower than a purpose-built ANN service at very large `k` over
  tens of millions of vectors. If this project ever reaches that scale, the
  migration path is a dedicated store plus an explicit authorisation stage —
  a change worth making deliberately, with the measurement to justify it.

## Alternatives considered

| Option | Why not |
|---|---|
| **ChromaDB** (the prototype's choice) | Single-node, file-backed, no transactional join against relational metadata, no real permission model. Fine for a demo; it cannot carry an authorisation invariant. |
| **Pinecone / Weaviate / Qdrant (managed)** | Strong ANN performance and zero ops, but both introduce the fetch-then-filter problem above, and separately require trusting an external system for filter correctness. They are a *scale* answer to a problem this project does not have. |
| **Elasticsearch / OpenSearch** | Genuinely good at hybrid search and would be a defensible choice. Rejected for operational weight relative to the benefit at this scale, and because it still needs a second relational store for the metadata and permission model. |
| **pgvector-only, no sparse arm** | Rejected on the merits: hybrid retrieval is the M2 hypothesis under test. Removing the sparse arm would make the ablation trivially "confirm" itself. |
