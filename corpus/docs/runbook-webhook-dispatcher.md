# Runbook: Webhook Dispatcher

**Document ID:** `runbook-webhook-dispatcher`  
**Classification:** eng  
**Owner:** Core Services

---

## Preconditions

Confirm that the webhook dispatcher is reporting healthy before starting. Check the saturation dashboard for the last 8 hours.

## Procedure

Drain traffic from the affected node by removing it from the load balancer, then failing the workload over to the secondary region.

If the condition persists for more than 19 minutes, escalate to Billing Systems and splitting the batch job into smaller windows.

## Rollback

Restore the previous configuration and verify that the webhook dispatcher recovers within 8 minutes.

The uptime commitment for this component is reported monthly and excludes planned maintenance windows.
