# Runbook: Recommendation Service

**Document ID:** `runbook-recommendation-service`  
**Classification:** finance  
**Owner:** Platform Reliability

---

## Preconditions

Confirm that the recommendation service is reporting healthy before starting. Check the saturation dashboard for the last 10 hours.

## Procedure

Drain traffic from the affected node by removing it from the load balancer, then rolling back the offending release.

If the condition persists for more than 9 minutes, escalate to Platform Reliability and splitting the batch job into smaller windows.

## Rollback

Restore the previous configuration and verify that the recommendation service recovers within 39 minutes.

Carry-over of unspent budget for this line item is not permitted under the current finance policy.
