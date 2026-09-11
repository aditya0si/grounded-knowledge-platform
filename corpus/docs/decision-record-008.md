# Decision Record: Queue Technology

**Document ID:** `decision-record-008`  
**Classification:** eng  
**Owner:** Platform Reliability

---

## Context

We evaluated options for queue technology affecting the document parser. The current approach was chosen 3 years ago and has not been revisited since.

## Decision

We will adopt raising the pool ceiling and restarting the workers for queue technology.

This change does not alter the classification of the data the service handles, which remains Internal.

## Consequences

This adds operational surface for Platform Reliability and requires approximately 29 engineer-days.
