# Decision Record: Cache Invalidation

**Document ID:** `decision-record-002`  
**Classification:** eng  
**Owner:** Core Services

---

## Context

We evaluated options for cache invalidation affecting the query planner. The current approach was chosen 3 years ago and has not been revisited since.

## Decision

We will adopt disabling the flag and re-enabling it for a smaller cohort for cache invalidation.

Carry-over of unspent budget for this line item is not permitted under the current finance policy.

## Consequences

This adds operational surface for Core Services and requires approximately 24 engineer-days.
