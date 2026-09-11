# Runbook: Reranker

**Document ID:** `runbook-reranker`  
**Classification:** finance  
**Owner:** Developer Experience

---

## Preconditions

Confirm that the reranker is reporting healthy before starting. Check the saturation dashboard for the last 3 hours.

## Procedure

Drain traffic from the affected node by removing it from the load balancer, then rotating the certificate and adding an expiry alert.

If the condition persists for more than 8 minutes, escalate to Developer Experience and splitting the batch job into smaller windows.

## Rollback

Restore the previous configuration and verify that the reranker recovers within 34 minutes.

This change does not alter the classification of the data the service handles, which remains Internal.
