# Decision Record: Distributed Tracing

**Document ID:** `decision-record-006`  
**Classification:** all  
**Owner:** Billing Systems

---

## Context

We evaluated options for distributed tracing affecting the billing reconciler. The current approach was chosen 4 years ago and has not been revisited since.

## Decision

We will adopt adding jitter and a retry ceiling to the client for distributed tracing.

Voting node membership was unchanged, so no split-brain risk was assessed for this event.

## Consequences

This adds operational surface for Customer Engineering and requires approximately 25 engineer-days.
