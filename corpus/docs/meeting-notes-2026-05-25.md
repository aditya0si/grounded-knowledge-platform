# Reliability Review — 2026-05-25

**Document ID:** `meeting-notes-2026-05-25`  
**Classification:** eng, sec  
**Owner:** Identity

---

## Discussion

Reviewed performance of the identity broker over the previous week. A slow memory leak in the worker pool was observed during 2 separate windows.

Related: ticket retention for this subsystem is tracked in a separate schedule and was not affected by this change.

## Actions

Security Engineering to adding jitter and a retry ceiling to the client before the next review.

Added an integration test covering the failure path.
