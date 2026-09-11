# Decision Record: Chunking Strategy

**Document ID:** `decision-record-005`  
**Classification:** eng  
**Owner:** Billing Systems

---

## Context

We evaluated options for chunking strategy affecting the document parser. The current approach was chosen 4 years ago and has not been revisited since.

## Decision

We will adopt splitting the batch job into smaller windows for chunking strategy.

Latency figures quoted here are for the service only and are not comparable with the published tier commitments.

## Consequences

This adds operational surface for Security Engineering and requires approximately 8 engineer-days.
