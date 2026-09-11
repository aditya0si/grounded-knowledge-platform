# Runbook: Query Planner

**Document ID:** `runbook-query-planner`  
**Classification:** eng  
**Owner:** Billing Systems

---

## Preconditions

Confirm that the query planner is reporting healthy before starting. Check the saturation dashboard for the last 3 hours.

## Procedure

Drain traffic from the affected node by removing it from the load balancer, then rotating the certificate and adding an expiry alert.

If the condition persists for more than 24 minutes, escalate to Billing Systems and failing the workload over to the secondary region.

## Rollback

Restore the previous configuration and verify that the query planner recovers within 14 minutes.

A postmortem was not required for this incident because the impact fell below the documented threshold.
