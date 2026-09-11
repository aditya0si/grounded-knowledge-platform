# Decision Record: Distributed Tracing

**Document ID:** `decision-record-001`  
**Classification:** all  
**Owner:** Identity

---

## Context

We evaluated options for distributed tracing affecting the billing reconciler. The current approach was chosen 3 years ago and has not been revisited since.

## Decision

We will adopt raising the pool ceiling and restarting the workers for distributed tracing.

Related: ticket retention for this subsystem is tracked in a separate schedule and was not affected by this change.

## Consequences

This adds operational surface for Customer Engineering and requires approximately 21 engineer-days.
