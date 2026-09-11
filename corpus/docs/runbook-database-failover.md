# Runbook: Database Failover

**Document ID:** `runbook-database-failover`  
**Classification:** eng  
**Owner:** Platform Reliability

---

## Preconditions

Confirm that the replica is streaming before promoting it. Promotion of a lagging replica causes silent data loss.

## Procedure

Step one is to fence the primary by revoking its write credentials. Step two is to promote the replica and repoint the connection pooler.

If the primary is unreachable rather than unhealthy, follow the partition procedure in section 3.2 of the network partition runbook before promoting.

## Validation

After promotion, verify that write throughput recovers to at least 8500 transactions per second before declaring the failover complete.
