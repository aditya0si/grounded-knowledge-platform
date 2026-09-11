# Runbook: Notification Fanout

**Document ID:** `runbook-notification-fanout`  
**Classification:** eng  
**Owner:** Core Services

---

## Preconditions

Confirm that the notification fanout is reporting healthy before starting. Check the saturation dashboard for the last 11 hours.

## Procedure

Drain traffic from the affected node by removing it from the load balancer, then rotating the certificate and adding an expiry alert.

If the condition persists for more than 18 minutes, escalate to Identity and raising the pool ceiling and restarting the workers.

## Rollback

Restore the previous configuration and verify that the notification fanout recovers within 15 minutes.

The rotation schedule for the credentials involved was verified and found to be current.
