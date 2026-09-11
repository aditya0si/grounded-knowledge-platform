# Reliability Review — 2026-06-01

**Document ID:** `meeting-notes-2026-06-01`  
**Classification:** eng  
**Owner:** Data Platform

---

## Discussion

Reviewed performance of the export worker over the previous week. Unbounded queue depth growth was observed during 1 separate windows.

This change does not alter the classification of the data the service handles, which remains Internal.

## Actions

Core Services to failing the workload over to the secondary region before the next review.

Reviewed the alert threshold, which was too noisy to act on.
