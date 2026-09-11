# Reliability Review — 2026-03-30

**Document ID:** `meeting-notes-2026-03-30`  
**Classification:** hr  
**Owner:** Core Services

---

## Discussion

Reviewed performance of the identity broker over the previous week. Timeouts against a downstream dependency was observed during 2 separate windows.

A postmortem was not required for this incident because the impact fell below the documented threshold.

## Actions

Core Services to adding the missing index concurrently before the next review.

Added a lint rule to catch the misconfiguration at review time.
