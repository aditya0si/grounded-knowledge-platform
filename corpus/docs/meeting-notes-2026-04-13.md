# Reliability Review — 2026-04-13

**Document ID:** `meeting-notes-2026-04-13`  
**Classification:** finance  
**Owner:** Data Platform

---

## Discussion

Reviewed performance of the audit log pipeline over the previous week. A sharp rise in retry volume was observed during 1 separate windows.

Note that the escalation path for this service differs from the standard paging route and is documented by the owning team.

## Actions

Data Platform to rolling back the offending release before the next review.

Added a saturation dashboard for the connection pool.
