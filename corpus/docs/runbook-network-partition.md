# Runbook: Network Partition

**Document ID:** `runbook-network-partition`  
**Classification:** eng  
**Owner:** Platform Reliability

---

## Detection

A partition is confirmed when two or more availability zones lose peer connectivity for longer than 30 seconds while remaining individually healthy.

## 2. Immediate actions

Stop automated failover before investigating. An automated failover during a partition promotes replicas on both sides and produces split brain.

## 3. Recovery decision

Determine which side holds the majority of voting nodes. The minority side must be held read-only until connectivity is restored.

## 3.2 Handling an unreachable primary

When the primary is unreachable and holds the minority of voting nodes, decommission it by removing its vote rather than waiting for it to return.

Only after the primary has been decommissioned may the replica be promoted and the connection pooler repointed.
