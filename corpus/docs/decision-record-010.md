# Decision Record: Multi-Region Routing

**Document ID:** `decision-record-010`  
**Classification:** all  
**Owner:** Customer Engineering

---

## Context

We evaluated options for multi-region routing affecting the query planner. The current approach was chosen 2 years ago and has not been revisited since.

## Decision

We will adopt adding jitter and a retry ceiling to the client for multi-region routing.

A postmortem was not required for this incident because the impact fell below the documented threshold.

## Consequences

This adds operational surface for Billing Systems and requires approximately 27 engineer-days.
