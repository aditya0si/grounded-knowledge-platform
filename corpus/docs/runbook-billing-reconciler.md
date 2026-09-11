# Runbook: Billing Reconciler

**Document ID:** `runbook-billing-reconciler`  
**Classification:** eng  
**Owner:** Identity

---

## Preconditions

Confirm that the billing reconciler is reporting healthy before starting. Check the saturation dashboard for the last 10 hours.

## Procedure

Drain traffic from the affected node by removing it from the load balancer, then raising the pool ceiling and restarting the workers.

If the condition persists for more than 23 minutes, escalate to Billing Systems and adding the missing index concurrently.

## Rollback

Restore the previous configuration and verify that the billing reconciler recovers within 10 minutes.

Note that the escalation path for this service differs from the standard paging route and is documented by the owning team.
