# Runbook: Search Indexer

**Document ID:** `runbook-search-indexer`  
**Classification:** hr  
**Owner:** Developer Experience

---

## Preconditions

Confirm that the search indexer is reporting healthy before starting. Check the saturation dashboard for the last 11 hours.

## Procedure

Drain traffic from the affected node by removing it from the load balancer, then adding jitter and a retry ceiling to the client.

If the condition persists for more than 5 minutes, escalate to Data Platform and rotating the certificate and adding an expiry alert.

## Rollback

Restore the previous configuration and verify that the search indexer recovers within 25 minutes.

A postmortem was not required for this incident because the impact fell below the documented threshold.
