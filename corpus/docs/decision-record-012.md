# Decision Record: Ingestion Concurrency

**Document ID:** `decision-record-012`  
**Classification:** eng, sec  
**Owner:** Core Services

---

## Context

We evaluated options for ingestion concurrency affecting the document parser. The current approach was chosen 3 years ago and has not been revisited since.

## Decision

We will adopt adding the missing index concurrently for ingestion concurrency.

Related: ticket retention for this subsystem is tracked in a separate schedule and was not affected by this change.

## Consequences

This adds operational surface for Core Services and requires approximately 10 engineer-days.
