# ADR-003 — Deterministic retrieval metrics; LLM judges only for generation

- **Status:** Accepted
- **Date:** 2026-09-12

## Context

RAG evaluation commonly reaches for an LLM-as-judge framework for everything,
including retrieval quality. This has three costs that matter here:

1. **Non-determinism.** The same commit evaluated twice yields different numbers,
   so a CI gate built on it either flaps or has to be loosened until it detects
   nothing.
2. **Cost and rate limits.** Every evaluation run spends tokens, which makes the
   cheap, frequent evaluation loop — the one that actually catches regressions —
   the expensive one.
3. **Unvalidated instrument.** An LLM judge is itself an unmeasured component. A
   system evaluated by an unvalidated judge has a measurement of the judge, not
   of the system.

Retrieval quality, unlike generation quality, does not require judgement. If the
gold chunk identifiers for a question are known, then recall@k, precision@k, MRR,
and nDCG are arithmetic.

## Decision

**Split the harness by whether the metric needs judgement.**

| Layer | Method | Properties |
|---|---|---|
| Retrieval | Pure functions over gold chunk IDs | Deterministic · free · fast · unit-tested against hand-computed values |
| Authorisation | Invariant assertion, not a metric | Leak count must be exactly `0` |
| Citation validity | String containment against the cited chunk | Deterministic — the claim is checkable by construction |
| Generation (M6) | LLM judge | Cached by content hash; the judge's own reliability is measured |

Consequences of that split for the golden set: each entry must carry
`gold_chunk_ids`, and options such as `expected_span` must be verified to appear
verbatim in a gold chunk at test time, not at evaluation time.

**The judge is validated, not trusted.** M6 hand-labels a subset and publishes
judge–human agreement. If the judge disagrees with the human labels frequently,
that is reported as a limitation of the generation metrics rather than quietly
carried into the results.

Where a metric genuinely requires judgement, the honest alternative to a judge is
often a *constructed* label. Because the corpus is synthetic and generated from a
manifest that records which facts each document contains, gold chunk labels are
derived from construction. They are not a model's opinion about relevance, and
they cannot drift between runs.

## Consequences

**Positive**

- The CI gate is deterministic and therefore genuinely enforcing.
- The M2 ablation over the full parameter grid is fast and free to re-run, which
  makes running the full grid practical rather than aspirational.
- Every metric function is testable against hand-computed expectations, including
  edge cases (empty gold set, `k` exceeding the retrieved list, all-gold
  retrieved, nothing retrieved) — cases that LLM-judged metrics cannot express
  at all.

**Negative**

- Construction-derived labels validate that the *correct chunk was retrieved*,
  not that the chunk is *useful to a human*. A chunk can be the gold answer and
  still be poorly written. That gap belongs to the generation-side evaluation.
- Building the corpus from a manifest is more work up front than pointing a
  loader at a folder of PDFs.

## Alternatives considered

| Option | Why not |
|---|---|
| **LLM judge for everything** | Non-deterministic, costs tokens per run, and puts an unvalidated instrument at the centre of the measurement. |
| **Human evaluation only** | The most trustworthy signal and worth doing on a sample — used in M6 to validate the judge — but it cannot run in CI and cannot be repeated per configuration across a 50-cell ablation grid. |
| **No retrieval metrics; infer quality from final answer quality** | Conflates retrieval and generation, so a failure cannot be attributed to either. This is the specific conflation the predecessor's harness could not detect. |
