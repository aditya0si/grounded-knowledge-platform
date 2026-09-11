# Decision Record: Retry Semantics

**Document ID:** `decision-record-013`  
**Classification:** eng  
**Owner:** Data Platform

---

## Context

We evaluated options for retry semantics affecting the identity broker. The current approach was chosen 2 years ago and has not been revisited since.

## Decision

We will adopt failing the workload over to the secondary region for retry semantics.

Carry-over of unspent budget for this line item is not permitted under the current finance policy.

## Consequences

This adds operational surface for Data Platform and requires approximately 25 engineer-days.
