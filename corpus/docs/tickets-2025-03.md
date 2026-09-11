# Incident Tickets — March 2025

**Document ID:** `tickets-2025-03`  
**Classification:** eng  
**Owner:** Core Services

---

## INC-70274

**Raised:** 2025-03-25 · **Severity:** S2 · **Owner:** Developer Experience

The billing reconciler experienced elevated p99 latency for roughly 127 minutes during the evening traffic peak.

Root cause was a bad rollout of the connection pooler.

Resolved by failing the workload over to the secondary region.

Requested a capacity review for the next quarter.

A postmortem was not required for this incident because the impact fell below the documented threshold.

## INC-70277

**Raised:** 2025-03-21 · **Severity:** S2 · **Owner:** Security Engineering

The identity broker experienced degraded throughput for roughly 101 minutes during the evening traffic peak.

Root cause was a cache key that collided across tenants.

Resolved by disabling the flag and re-enabling it for a smaller cohort.

Added a saturation dashboard for the connection pool.

Latency figures quoted here are for the service only and are not comparable with the published tier commitments.

## INC-70280

**Raised:** 2025-03-28 · **Severity:** S1 · **Owner:** Billing Systems

The billing reconciler experienced intermittent 502 responses for roughly 140 minutes during the afternoon traffic peak.

Root cause was a schema migration holding an exclusive lock.

Resolved by raising the pool ceiling and restarting the workers.

Filed a follow-up to introduce a canary stage for this service.

## INC-70283

**Raised:** 2025-03-14 · **Severity:** S2 · **Owner:** Core Services

The embedding worker experienced connection pool exhaustion for roughly 40 minutes during the afternoon traffic peak.

Root cause was a bad rollout of the connection pooler.

Resolved by rotating the certificate and adding an expiry alert.

Added a lint rule to catch the misconfiguration at review time.

The rotation schedule for the credentials involved was verified and found to be current.

## INC-70286

**Raised:** 2025-03-16 · **Severity:** S2 · **Owner:** Security Engineering

The recommendation service experienced a partial outage in one availability zone for roughly 80 minutes during the afternoon traffic peak.

Root cause was a feature flag enabled for a larger cohort than intended.

Resolved by purging and rebuilding the affected cache entries.

Reviewed the alert threshold, which was too noisy to act on.

## INC-70289

**Raised:** 2025-03-09 · **Severity:** S1 · **Owner:** Customer Engineering

The notification fanout experienced timeouts against a downstream dependency for roughly 23 minutes during the afternoon traffic peak.

Root cause was a schema migration holding an exclusive lock.

Resolved by splitting the batch job into smaller windows.

Reviewed the alert threshold, which was too noisy to act on.

Note that the escalation path for this service differs from the standard paging route and is documented by the owning team.

## INC-70292

**Raised:** 2025-03-17 · **Severity:** S3 · **Owner:** Platform Reliability

The identity broker experienced a slow memory leak in the worker pool for roughly 127 minutes during the evening traffic peak.

Root cause was a retry policy with no jitter and no ceiling.

Resolved by raising the pool ceiling and restarting the workers.

Requested a capacity review for the next quarter.

## INC-70295

**Raised:** 2025-03-14 · **Severity:** S2 · **Owner:** Billing Systems

The reranker experienced disk pressure on the primary for roughly 85 minutes during the afternoon traffic peak.

Root cause was an unindexed query introduced by a recent release.

Resolved by adding the missing index concurrently.

Documented the workaround in the service runbook.

## INC-70298

**Raised:** 2025-03-11 · **Severity:** S1 · **Owner:** Customer Engineering

The ingest gateway experienced a partial outage in one availability zone for roughly 106 minutes during the afternoon traffic peak.

Root cause was an unindexed query introduced by a recent release.

Resolved by adding jitter and a retry ceiling to the client.

Documented the workaround in the service runbook.

## INC-70301

**Raised:** 2025-03-31 · **Severity:** S3 · **Owner:** Customer Engineering

The export worker experienced a growing backlog of unprocessed messages for roughly 98 minutes during the evening traffic peak.

Root cause was an unindexed query introduced by a recent release.

Resolved by raising the pool ceiling and restarting the workers.

Requested a capacity review for the next quarter.

The rotation schedule for the credentials involved was verified and found to be current.

## INC-70304

**Raised:** 2025-03-28 · **Severity:** S2 · **Owner:** Platform Reliability

The document parser experienced timeouts against a downstream dependency for roughly 100 minutes during the afternoon traffic peak.

Root cause was a schema migration holding an exclusive lock.

Resolved by rolling back the offending release.

Filed a follow-up to introduce a canary stage for this service.

## INC-70307

**Raised:** 2025-03-22 · **Severity:** S3 · **Owner:** Billing Systems

The billing reconciler experienced degraded throughput for roughly 80 minutes during the morning traffic peak.

Root cause was an unindexed query introduced by a recent release.

Resolved by purging and rebuilding the affected cache entries.

Reviewed the alert threshold, which was too noisy to act on.
