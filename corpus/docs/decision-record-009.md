# Decision Record: Batch Size

**Document ID:** `decision-record-009`  
**Classification:** eng  
**Owner:** Security Engineering

---

## Context

We evaluated options for batch size affecting the ingest gateway. The current approach was chosen 2 years ago and has not been revisited since.

## Decision

We will adopt disabling the flag and re-enabling it for a smaller cohort for batch size.

Latency figures quoted here are for the service only and are not comparable with the published tier commitments.

## Consequences

This adds operational surface for Core Services and requires approximately 10 engineer-days.
