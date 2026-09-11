# Reliability Review — 2026-05-11

**Document ID:** `meeting-notes-2026-05-11`  
**Classification:** eng  
**Owner:** Identity

---

## Discussion

Reviewed performance of the recommendation service over the previous week. A slow memory leak in the worker pool was observed during 2 separate windows.

Latency figures quoted here are for the service only and are not comparable with the published tier commitments.

## Actions

Billing Systems to adding jitter and a retry ceiling to the client before the next review.

Documented the workaround in the service runbook.
