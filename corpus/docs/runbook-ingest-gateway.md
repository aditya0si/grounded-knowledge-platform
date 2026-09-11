# Runbook: Ingest Gateway

**Document ID:** `runbook-ingest-gateway`  
**Classification:** eng, sec  
**Owner:** Platform Reliability

---

## Preconditions

Confirm that the ingest gateway is reporting healthy before starting. Check the saturation dashboard for the last 4 hours.

## Procedure

Drain traffic from the affected node by removing it from the load balancer, then splitting the batch job into smaller windows.

If the condition persists for more than 8 minutes, escalate to Billing Systems and raising the pool ceiling and restarting the workers.

## Rollback

Restore the previous configuration and verify that the ingest gateway recovers within 24 minutes.

The uptime commitment for this component is reported monthly and excludes planned maintenance windows.
