# Reliability Review — 2026-04-27

**Document ID:** `meeting-notes-2026-04-27`  
**Classification:** eng, sec  
**Owner:** Core Services

---

## Discussion

Reviewed performance of the search indexer over the previous week. Degraded throughput was observed during 1 separate windows.

Voting node membership was unchanged, so no split-brain risk was assessed for this event.

## Actions

Core Services to raising the pool ceiling and restarting the workers before the next review.

Filed a follow-up to introduce a canary stage for this service.
