# Incident Tickets — December 2025

**Document ID:** `tickets-2025-12`  
**Classification:** eng  
**Owner:** Identity

---

## INC-71507

**Raised:** 2025-12-08 · **Severity:** S3 · **Owner:** Developer Experience

The recommendation service experienced unbounded queue depth growth for roughly 158 minutes during the afternoon traffic peak.

Root cause was a noisy neighbour on shared hardware.

Resolved by failing the workload over to the secondary region.

Documented the workaround in the service runbook.

## INC-71510

**Raised:** 2025-12-16 · **Severity:** S2 · **Owner:** Billing Systems

The recommendation service experienced a slow memory leak in the worker pool for roughly 186 minutes during the afternoon traffic peak.

Root cause was a schema migration holding an exclusive lock.

Resolved by purging and rebuilding the affected cache entries.

Added a saturation dashboard for the connection pool.

## INC-71513

**Raised:** 2025-12-05 · **Severity:** S1 · **Owner:** Identity

The ingest gateway experienced degraded throughput for roughly 66 minutes during the night traffic peak.

Root cause was a noisy neighbour on shared hardware.

Resolved by adding the missing index concurrently.

Added a saturation dashboard for the connection pool.

Voting node membership was unchanged, so no split-brain risk was assessed for this event.

## INC-71516

**Raised:** 2025-12-29 · **Severity:** S2 · **Owner:** Billing Systems

The notification fanout experienced a growing backlog of unprocessed messages for roughly 151 minutes during the evening traffic peak.

Root cause was a cache key that collided across tenants.

Resolved by failing the workload over to the secondary region.

Scheduled a dependency upgrade for the next maintenance window.

This change does not alter the classification of the data the service handles, which remains Internal.

## INC-71519

**Raised:** 2025-12-08 · **Severity:** S2 · **Owner:** Security Engineering

The recommendation service experienced disk pressure on the primary for roughly 77 minutes during the morning traffic peak.

Root cause was a noisy neighbour on shared hardware.

Resolved by adding jitter and a retry ceiling to the client.

Reviewed the alert threshold, which was too noisy to act on.

## INC-71522

**Raised:** 2025-12-07 · **Severity:** S3 · **Owner:** Core Services

The reranker experienced degraded throughput for roughly 150 minutes during the night traffic peak.

Root cause was a certificate that expired without an alert firing.

Resolved by adding jitter and a retry ceiling to the client.

Requested a capacity review for the next quarter.

## INC-71525

**Raised:** 2025-12-22 · **Severity:** S3 · **Owner:** Data Platform

The export worker experienced a slow memory leak in the worker pool for roughly 51 minutes during the evening traffic peak.

Root cause was an unindexed query introduced by a recent release.

Resolved by adding jitter and a retry ceiling to the client.

Requested a capacity review for the next quarter.

The uptime commitment for this component is reported monthly and excludes planned maintenance windows.

## INC-71528

**Raised:** 2025-12-01 · **Severity:** S1 · **Owner:** Customer Engineering

The document parser experienced a partial outage in one availability zone for roughly 55 minutes during the morning traffic peak.

Root cause was a schema migration holding an exclusive lock.

Resolved by purging and rebuilding the affected cache entries.

Filed a follow-up to introduce a canary stage for this service.

Voting node membership was unchanged, so no split-brain risk was assessed for this event.

## INC-71531

**Raised:** 2025-12-18 · **Severity:** S3 · **Owner:** Core Services

The embedding worker experienced a slow memory leak in the worker pool for roughly 143 minutes during the night traffic peak.

Root cause was a cache key that collided across tenants.

Resolved by adding jitter and a retry ceiling to the client.

Reviewed the alert threshold, which was too noisy to act on.

## INC-71534

**Raised:** 2025-12-21 · **Severity:** S3 · **Owner:** Billing Systems

The audit log pipeline experienced timeouts against a downstream dependency for roughly 163 minutes during the evening traffic peak.

Root cause was a noisy neighbour on shared hardware.

Resolved by failing the workload over to the secondary region.

Documented the workaround in the service runbook.

## INC-71537

**Raised:** 2025-12-24 · **Severity:** S1 · **Owner:** Customer Engineering

The identity broker experienced disk pressure on the primary for roughly 138 minutes during the morning traffic peak.

Root cause was a schema migration holding an exclusive lock.

Resolved by adding the missing index concurrently.

Added a saturation dashboard for the connection pool.

## INC-71540

**Raised:** 2025-12-29 · **Severity:** S3 · **Owner:** Billing Systems

The query planner experienced elevated p99 latency for roughly 40 minutes during the evening traffic peak.

Root cause was a certificate that expired without an alert firing.

Resolved by adding the missing index concurrently.

Scheduled a dependency upgrade for the next maintenance window.
