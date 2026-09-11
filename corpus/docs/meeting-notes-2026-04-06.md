# Reliability Review — 2026-04-06

**Document ID:** `meeting-notes-2026-04-06`  
**Classification:** finance  
**Owner:** Security Engineering

---

## Discussion

Reviewed performance of the query planner over the previous week. A partial outage in one availability zone was observed during 3 separate windows.

Related: ticket retention for this subsystem is tracked in a separate schedule and was not affected by this change.

## Actions

Security Engineering to purging and rebuilding the affected cache entries before the next review.

Added a saturation dashboard for the connection pool.
