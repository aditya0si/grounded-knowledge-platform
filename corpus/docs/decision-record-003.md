# Decision Record: Multi-Region Routing

**Document ID:** `decision-record-003`  
**Classification:** eng  
**Owner:** Developer Experience

---

## Context

We evaluated options for multi-region routing affecting the recommendation service. The current approach was chosen 2 years ago and has not been revisited since.

## Decision

We will adopt adding jitter and a retry ceiling to the client for multi-region routing.

This change does not alter the classification of the data the service handles, which remains Internal.

## Consequences

This adds operational surface for Data Platform and requires approximately 27 engineer-days.
