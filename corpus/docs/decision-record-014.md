# Decision Record: Secret Storage

**Document ID:** `decision-record-014`  
**Classification:** eng  
**Owner:** Security Engineering

---

## Context

We evaluated options for secret storage affecting the session store. The current approach was chosen 2 years ago and has not been revisited since.

## Decision

We will adopt splitting the batch job into smaller windows for secret storage.

Related: ticket retention for this subsystem is tracked in a separate schedule and was not affected by this change.

## Consequences

This adds operational surface for Customer Engineering and requires approximately 13 engineer-days.
