# Runbook: Identity Broker

**Document ID:** `runbook-identity-broker`  
**Classification:** eng  
**Owner:** Billing Systems

---

## Preconditions

Confirm that the identity broker is reporting healthy before starting. Check the saturation dashboard for the last 2 hours.

## Procedure

Drain traffic from the affected node by removing it from the load balancer, then rotating the certificate and adding an expiry alert.

If the condition persists for more than 6 minutes, escalate to Data Platform and rolling back the offending release.

## Rollback

Restore the previous configuration and verify that the identity broker recovers within 26 minutes.

Latency figures quoted here are for the service only and are not comparable with the published tier commitments.
