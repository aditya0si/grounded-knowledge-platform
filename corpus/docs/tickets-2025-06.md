# Incident Tickets — June 2025

**Document ID:** `tickets-2025-06`  
**Classification:** eng  
**Owner:** Data Platform

---

## INC-70685

**Raised:** 2025-06-10 · **Severity:** S3 · **Owner:** Core Services

The query planner experienced intermittent 502 responses for roughly 56 minutes during the afternoon traffic peak.

Root cause was a runaway batch job competing for I/O.

Resolved by failing the workload over to the secondary region.

Added an integration test covering the failure path.

## INC-70688

**Raised:** 2025-06-27 · **Severity:** S2 · **Owner:** Data Platform

The reranker experienced unbounded queue depth growth for roughly 93 minutes during the morning traffic peak.

Root cause was a schema migration holding an exclusive lock.

Resolved by purging and rebuilding the affected cache entries.

Requested a capacity review for the next quarter.

## INC-70691

**Raised:** 2025-06-28 · **Severity:** S1 · **Owner:** Billing Systems

The metrics aggregator experienced degraded throughput for roughly 152 minutes during the morning traffic peak.

Root cause was a noisy neighbour on shared hardware.

Resolved by disabling the flag and re-enabling it for a smaller cohort.

Added a saturation dashboard for the connection pool.

Related: ticket retention for this subsystem is tracked in a separate schedule and was not affected by this change.

## INC-70694

**Raised:** 2025-06-13 · **Severity:** S2 · **Owner:** Platform Reliability

The ingest gateway experienced degraded throughput for roughly 37 minutes during the evening traffic peak.

Root cause was an unindexed query introduced by a recent release.

Resolved by adding the missing index concurrently.

Filed a follow-up to introduce a canary stage for this service.

## INC-70697

**Raised:** 2025-06-24 · **Severity:** S2 · **Owner:** Data Platform

The query planner experienced a sharp rise in retry volume for roughly 179 minutes during the morning traffic peak.

Root cause was a feature flag enabled for a larger cohort than intended.

Resolved by adding the missing index concurrently.

Documented the workaround in the service runbook.

## INC-70700

**Raised:** 2025-06-16 · **Severity:** S1 · **Owner:** Customer Engineering

The search indexer experienced unbounded queue depth growth for roughly 88 minutes during the evening traffic peak.

Root cause was a retry policy with no jitter and no ceiling.

Resolved by purging and rebuilding the affected cache entries.

Added a lint rule to catch the misconfiguration at review time.

## INC-70703

**Raised:** 2025-06-03 · **Severity:** S2 · **Owner:** Security Engineering

The notification fanout experienced elevated p99 latency for roughly 145 minutes during the night traffic peak.

Root cause was a feature flag enabled for a larger cohort than intended.

Resolved by purging and rebuilding the affected cache entries.

Added a saturation dashboard for the connection pool.

## INC-70706

**Raised:** 2025-06-08 · **Severity:** S1 · **Owner:** Customer Engineering

The document parser experienced connection pool exhaustion for roughly 99 minutes during the evening traffic peak.

Root cause was a certificate that expired without an alert firing.

Resolved by adding jitter and a retry ceiling to the client.

Scheduled a dependency upgrade for the next maintenance window.

## INC-70709

**Raised:** 2025-06-27 · **Severity:** S1 · **Owner:** Customer Engineering

The audit log pipeline experienced disk pressure on the primary for roughly 159 minutes during the night traffic peak.

Root cause was a configuration change that was not rolled out gradually.

Resolved by disabling the flag and re-enabling it for a smaller cohort.

Added a saturation dashboard for the connection pool.

## INC-70712

**Raised:** 2025-06-11 · **Severity:** S1 · **Owner:** Data Platform

The billing reconciler experienced a partial outage in one availability zone for roughly 32 minutes during the night traffic peak.

Root cause was a cache key that collided across tenants.

Resolved by splitting the batch job into smaller windows.

Documented the workaround in the service runbook.

## INC-70715

**Raised:** 2025-06-30 · **Severity:** S3 · **Owner:** Core Services

The billing reconciler experienced a slow memory leak in the worker pool for roughly 90 minutes during the morning traffic peak.

Root cause was a bad rollout of the connection pooler.

Resolved by rolling back the offending release.

Added an integration test covering the failure path.

The rotation schedule for the credentials involved was verified and found to be current.

## INC-70718

**Raised:** 2025-06-03 · **Severity:** S2 · **Owner:** Developer Experience

The metrics aggregator experienced disk pressure on the primary for roughly 102 minutes during the afternoon traffic peak.

Root cause was a configuration change that was not rolled out gradually.

Resolved by adding the missing index concurrently.

Added a saturation dashboard for the connection pool.
