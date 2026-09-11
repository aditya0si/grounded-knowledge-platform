# Runbook: Embedding Worker

**Document ID:** `runbook-embedding-worker`  
**Classification:** eng  
**Owner:** Customer Engineering

---

## Preconditions

Confirm that the embedding worker is reporting healthy before starting. Check the saturation dashboard for the last 6 hours.

## Procedure

Drain traffic from the affected node by removing it from the load balancer, then splitting the batch job into smaller windows.

If the condition persists for more than 8 minutes, escalate to Core Services and rolling back the offending release.

## Rollback

Restore the previous configuration and verify that the embedding worker recovers within 17 minutes.

A postmortem was not required for this incident because the impact fell below the documented threshold.
