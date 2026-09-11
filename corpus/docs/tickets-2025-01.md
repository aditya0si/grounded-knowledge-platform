# Incident Tickets — January 2025

**Document ID:** `tickets-2025-01`  
**Classification:** eng  
**Owner:** Security Engineering

---

## INC-70000

**Raised:** 2025-01-14 · **Severity:** S1 · **Owner:** Identity

The export worker experienced intermittent 502 responses for roughly 55 minutes during the morning traffic peak.

Root cause was an upstream dependency quietly raising its timeout.

Resolved by purging and rebuilding the affected cache entries.

Added a lint rule to catch the misconfiguration at review time.

## INC-70003

**Raised:** 2025-01-19 · **Severity:** S2 · **Owner:** Identity

The billing reconciler experienced elevated p99 latency for roughly 119 minutes during the morning traffic peak.

Root cause was a retry policy with no jitter and no ceiling.

Resolved by raising the pool ceiling and restarting the workers.

Added a lint rule to catch the misconfiguration at review time.

## INC-70006

**Raised:** 2025-01-03 · **Severity:** S1 · **Owner:** Core Services

The identity broker experienced connection pool exhaustion for roughly 67 minutes during the afternoon traffic peak.

Root cause was a bad rollout of the connection pooler.

Resolved by adding the missing index concurrently.

Added an integration test covering the failure path.

## INC-70009

**Raised:** 2025-01-30 · **Severity:** S3 · **Owner:** Security Engineering

The search indexer experienced disk pressure on the primary for roughly 119 minutes during the afternoon traffic peak.

Root cause was an upstream dependency quietly raising its timeout.

Resolved by splitting the batch job into smaller windows.

Added an integration test covering the failure path.

The rotation schedule for the credentials involved was verified and found to be current.

## INC-70012

**Raised:** 2025-01-31 · **Severity:** S2 · **Owner:** Core Services

The session store experienced a growing backlog of unprocessed messages for roughly 40 minutes during the night traffic peak.

Root cause was a schema migration holding an exclusive lock.

Resolved by raising the pool ceiling and restarting the workers.

Reviewed the alert threshold, which was too noisy to act on.

## INC-70015

**Raised:** 2025-01-14 · **Severity:** S1 · **Owner:** Security Engineering

The notification fanout experienced degraded throughput for roughly 47 minutes during the morning traffic peak.

Root cause was an upstream dependency quietly raising its timeout.

Resolved by rotating the certificate and adding an expiry alert.

Requested a capacity review for the next quarter.

## INC-70018

**Raised:** 2025-01-23 · **Severity:** S3 · **Owner:** Customer Engineering

The notification fanout experienced intermittent 502 responses for roughly 34 minutes during the afternoon traffic peak.

Root cause was a feature flag enabled for a larger cohort than intended.

Resolved by failing the workload over to the secondary region.

Added an integration test covering the failure path.

Carry-over of unspent budget for this line item is not permitted under the current finance policy.

## INC-70021

**Raised:** 2025-01-17 · **Severity:** S1 · **Owner:** Identity

The export worker experienced elevated p99 latency for roughly 79 minutes during the evening traffic peak.

Root cause was a feature flag enabled for a larger cohort than intended.

Resolved by purging and rebuilding the affected cache entries.

Requested a capacity review for the next quarter.

Note that the escalation path for this service differs from the standard paging route and is documented by the owning team.

## INC-70024

**Raised:** 2025-01-13 · **Severity:** S2 · **Owner:** Identity

The session store experienced intermittent 502 responses for roughly 157 minutes during the morning traffic peak.

Root cause was a runaway batch job competing for I/O.

Resolved by adding jitter and a retry ceiling to the client.

Documented the workaround in the service runbook.

## INC-70027

**Raised:** 2025-01-26 · **Severity:** S2 · **Owner:** Customer Engineering

The audit log pipeline experienced intermittent 502 responses for roughly 49 minutes during the evening traffic peak.

Root cause was an unindexed query introduced by a recent release.

Resolved by rolling back the offending release.

Reviewed the alert threshold, which was too noisy to act on.

Voting node membership was unchanged, so no split-brain risk was assessed for this event.

## INC-70030

**Raised:** 2025-01-15 · **Severity:** S3 · **Owner:** Data Platform

The notification fanout experienced elevated p99 latency for roughly 24 minutes during the afternoon traffic peak.

Root cause was a cache key that collided across tenants.

Resolved by rolling back the offending release.

Reviewed the alert threshold, which was too noisy to act on.

## INC-70033

**Raised:** 2025-01-22 · **Severity:** S3 · **Owner:** Core Services

The tenant provisioning worker experienced connection pool exhaustion for roughly 132 minutes during the evening traffic peak.

Root cause was a bad rollout of the connection pooler.

Resolved by raising the pool ceiling and restarting the workers.

Added a lint rule to catch the misconfiguration at review time.

Latency figures quoted here are for the service only and are not comparable with the published tier commitments.
