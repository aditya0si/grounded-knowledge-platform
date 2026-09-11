# Incident Tickets — August 2025

**Document ID:** `tickets-2025-08`  
**Classification:** eng  
**Owner:** Billing Systems

---

## INC-70959

**Raised:** 2025-08-15 · **Severity:** S2 · **Owner:** Core Services

The embedding worker experienced intermittent 502 responses for roughly 163 minutes during the evening traffic peak.

Root cause was a cache key that collided across tenants.

Resolved by adding the missing index concurrently.

Added an integration test covering the failure path.

## INC-70962

**Raised:** 2025-08-13 · **Severity:** S3 · **Owner:** Identity

The webhook dispatcher experienced disk pressure on the primary for roughly 146 minutes during the afternoon traffic peak.

Root cause was a bad rollout of the connection pooler.

Resolved by rotating the certificate and adding an expiry alert.

Added an integration test covering the failure path.

## INC-70965

**Raised:** 2025-08-18 · **Severity:** S1 · **Owner:** Customer Engineering

The reranker experienced a growing backlog of unprocessed messages for roughly 120 minutes during the night traffic peak.

Root cause was a certificate that expired without an alert firing.

Resolved by adding jitter and a retry ceiling to the client.

Documented the workaround in the service runbook.

## INC-70968

**Raised:** 2025-08-12 · **Severity:** S2 · **Owner:** Data Platform

The webhook dispatcher experienced repeated leader elections for roughly 97 minutes during the morning traffic peak.

Root cause was an unindexed query introduced by a recent release.

Resolved by raising the pool ceiling and restarting the workers.

Added a lint rule to catch the misconfiguration at review time.

## INC-70971

**Raised:** 2025-08-31 · **Severity:** S3 · **Owner:** Billing Systems

The export worker experienced intermittent 502 responses for roughly 173 minutes during the morning traffic peak.

Root cause was a runaway batch job competing for I/O.

Resolved by adding the missing index concurrently.

Documented the workaround in the service runbook.

## INC-70974

**Raised:** 2025-08-15 · **Severity:** S1 · **Owner:** Billing Systems

The tenant provisioning worker experienced elevated p99 latency for roughly 109 minutes during the evening traffic peak.

Root cause was a bad rollout of the connection pooler.

Resolved by failing the workload over to the secondary region.

Added a lint rule to catch the misconfiguration at review time.

## INC-70977

**Raised:** 2025-08-13 · **Severity:** S1 · **Owner:** Identity

The notification fanout experienced degraded throughput for roughly 183 minutes during the afternoon traffic peak.

Root cause was a certificate that expired without an alert firing.

Resolved by rolling back the offending release.

Added a saturation dashboard for the connection pool.

## INC-70980

**Raised:** 2025-08-24 · **Severity:** S3 · **Owner:** Core Services

The search indexer experienced a growing backlog of unprocessed messages for roughly 131 minutes during the afternoon traffic peak.

Root cause was a cache key that collided across tenants.

Resolved by splitting the batch job into smaller windows.

Reviewed the alert threshold, which was too noisy to act on.

Carry-over of unspent budget for this line item is not permitted under the current finance policy.

## INC-70983

**Raised:** 2025-08-10 · **Severity:** S1 · **Owner:** Billing Systems

The metrics aggregator experienced elevated p99 latency for roughly 105 minutes during the morning traffic peak.

Root cause was a schema migration holding an exclusive lock.

Resolved by disabling the flag and re-enabling it for a smaller cohort.

Added a lint rule to catch the misconfiguration at review time.

## INC-70986

**Raised:** 2025-08-20 · **Severity:** S3 · **Owner:** Core Services

The session store experienced intermittent 502 responses for roughly 89 minutes during the afternoon traffic peak.

Root cause was a retry policy with no jitter and no ceiling.

Resolved by disabling the flag and re-enabling it for a smaller cohort.

Requested a capacity review for the next quarter.

## INC-70989

**Raised:** 2025-08-15 · **Severity:** S3 · **Owner:** Security Engineering

The session store experienced connection pool exhaustion for roughly 45 minutes during the evening traffic peak.

Root cause was an upstream dependency quietly raising its timeout.

Resolved by raising the pool ceiling and restarting the workers.

Filed a follow-up to introduce a canary stage for this service.

## INC-70992

**Raised:** 2025-08-03 · **Severity:** S1 · **Owner:** Security Engineering

The webhook dispatcher experienced intermittent 502 responses for roughly 76 minutes during the evening traffic peak.

Root cause was a certificate that expired without an alert firing.

Resolved by purging and rebuilding the affected cache entries.

Documented the workaround in the service runbook.
