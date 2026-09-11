# Decision Record: Cache Invalidation

**Document ID:** `decision-record-007`  
**Classification:** eng  
**Owner:** Security Engineering

---

## Context

We evaluated options for cache invalidation affecting the billing reconciler. The current approach was chosen 3 years ago and has not been revisited since.

## Decision

We will adopt disabling the flag and re-enabling it for a smaller cohort for cache invalidation.

Voting node membership was unchanged, so no split-brain risk was assessed for this event.

## Consequences

This adds operational surface for Data Platform and requires approximately 9 engineer-days.
