# Runbook: Document Parser

**Document ID:** `runbook-document-parser`  
**Classification:** all  
**Owner:** Platform Reliability

---

## Preconditions

Confirm that the document parser is reporting healthy before starting. Check the saturation dashboard for the last 2 hours.

## Procedure

Drain traffic from the affected node by removing it from the load balancer, then purging and rebuilding the affected cache entries.

If the condition persists for more than 16 minutes, escalate to Developer Experience and rotating the certificate and adding an expiry alert.

## Rollback

Restore the previous configuration and verify that the document parser recovers within 38 minutes.

A postmortem was not required for this incident because the impact fell below the documented threshold.
