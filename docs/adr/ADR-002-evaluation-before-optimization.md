# ADR-002 — Build the evaluation harness before the retrieval improvements it measures

- **Status:** Accepted
- **Date:** 2026-09-12

## Context

The natural build order for a retrieval system is: get retrieval working, add
hybrid search, add reranking, then evaluate. This produces a comfortable
narrative and a serious methodological problem — every measurement taken after
an improvement is confounded by the possibility that the *harness* changed, or
that it was calibrated against the improved system and therefore favours it.

The predecessor project demonstrates the failure mode in its most extreme form.
Its evaluation corpus totalled 151 words across three chunks while the retriever
requested `top-k=6`. Retrieval could not fail, so the published faithfulness
score measured generation quality against a context that was always the entire
corpus. The harness was not wrong about the number it produced; it was measuring
something other than what it claimed to measure, and nothing in the setup would
ever have revealed that.

A harness that cannot fail cannot defend an improvement.

## Decision

Milestone 1 delivers **corpus, golden set, metric functions, and the dense-only
baseline — before any improvement to retrieval exists.** M2's hybrid retrieval
and reranking are then evaluated against a harness that was already in place and
already produced a baseline the change must beat.

Two rules follow from this:

1. **The baseline is measured, not assumed.** The M1 output is a committed
   `results/BASELINE.md`. M2's threshold is derived from it, never guessed in
   advance.
2. **The harness is adversarially designed.** The corpus deliberately contains
   near-duplicate document versions, embedded tables, cross-referenced runbooks,
   and lexical distractors. A corpus of clean, self-contained prose would make
   every retrieval strategy look equivalent, which is not a neutral choice — it
   is a harness that cannot discriminate.

## Consequences

**Positive**

- Any M2 result is attributable. A regression localises to a specific stage
  through per-stage scoring (dense-only → fused → reranked) rather than
  appearing as an unexplained movement in a single aggregate.
- The negative-result policy becomes possible to honour: if hybrid does not beat
  dense, that is a finding *from a harness capable of showing otherwise*, which
  is materially stronger evidence than a positive result from a harness that
  could not have said no.
- The CI gate has something real to gate on from the first milestone.

**Negative**

- M1 produces no user-visible feature. It is the least demonstrable milestone and
  the easiest to skip under time pressure — which is precisely why it is locked
  first and why its acceptance criteria are the most explicit in the plan.
- The corpus is synthetic, because a real internal-docs corpus with known gold
  labels is not available. This is a genuine limitation and is published as one.

## Alternatives considered

| Option | Why not |
|---|---|
| **RAGAS as the primary harness** | RAGAS metrics are LLM-judged and expensive, and the prototype's use of them is what produced a number nobody could interpret. RAGAS remains useful for generation-side quality in M6; it is a complement to deterministic retrieval metrics, not a substitute. |
| **Evaluate on a public benchmark (BEIR, MS MARCO)** | Comparable against published numbers, which is a real advantage. Rejected as the *primary* harness because it cannot express this project's central question — permission-scoped retrieval — and because no public benchmark carries per-document ACLs. Retained as a possible second column in the M2 ablation. |
| **Evaluate after building, with a test set written at the end** | The specific failure the predecessor exhibits. Rejected. |
