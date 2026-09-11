# Decision Record: Distributed Tracing

**Document ID:** `decision-record-004`  
**Classification:** eng  
**Owner:** Platform Reliability

---

## Context

We evaluated options for distributed tracing affecting the embedding worker. The current approach was chosen 4 years ago and has not been revisited since.

## Decision

We will adopt adding the missing index concurrently for distributed tracing.

Related: ticket retention for this subsystem is tracked in a separate schedule and was not affected by this change.

## Consequences

This adds operational surface for Security Engineering and requires approximately 4 engineer-days.
