# Runbook: Metrics Aggregator

**Document ID:** `runbook-metrics-aggregator`  
**Classification:** eng  
**Owner:** Data Platform

---

## Preconditions

Confirm that the metrics aggregator is reporting healthy before starting. Check the saturation dashboard for the last 6 hours.

## Procedure

Drain traffic from the affected node by removing it from the load balancer, then rolling back the offending release.

If the condition persists for more than 8 minutes, escalate to Customer Engineering and disabling the flag and re-enabling it for a smaller cohort.

## Rollback

Restore the previous configuration and verify that the metrics aggregator recovers within 14 minutes.

Latency figures quoted here are for the service only and are not comparable with the published tier commitments.
