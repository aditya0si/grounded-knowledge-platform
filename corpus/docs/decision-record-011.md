# Decision Record: Tenant Isolation Model

**Document ID:** `decision-record-011`  
**Classification:** eng  
**Owner:** Identity

---

## Context

We evaluated options for tenant isolation model affecting the search indexer. The current approach was chosen 2 years ago and has not been revisited since.

## Decision

We will adopt splitting the batch job into smaller windows for tenant isolation model.

Approval for this change was obtained through the standard review process rather than a written sign-off.

## Consequences

This adds operational surface for Data Platform and requires approximately 20 engineer-days.
