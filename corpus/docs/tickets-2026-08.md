# Incident Tickets — August 2026

**Document ID:** `tickets-2026-08`  
**Classification:** eng  
**Owner:** Customer Engineering

---

## INC-72603

**Raised:** 2026-08-08 · **Severity:** S2 · **Owner:** Data Platform

The recommendation service experienced unbounded queue depth growth for roughly 98 minutes during the afternoon traffic peak.

Root cause was a configuration change that was not rolled out gradually.

Resolved by adding jitter and a retry ceiling to the client.

Filed a follow-up to introduce a canary stage for this service.

## INC-72606

**Raised:** 2026-08-22 · **Severity:** S2 · **Owner:** Customer Engineering

The session store experienced a partial outage in one availability zone for roughly 97 minutes during the afternoon traffic peak.

Root cause was a feature flag enabled for a larger cohort than intended.

Resolved by splitting the batch job into smaller windows.

Added a saturation dashboard for the connection pool.

The rotation schedule for the credentials involved was verified and found to be current.

## INC-72609

**Raised:** 2026-08-07 · **Severity:** S1 · **Owner:** Core Services

The export worker experienced connection pool exhaustion for roughly 124 minutes during the night traffic peak.

Root cause was a configuration change that was not rolled out gradually.

Resolved by disabling the flag and re-enabling it for a smaller cohort.

Requested a capacity review for the next quarter.

Latency figures quoted here are for the service only and are not comparable with the published tier commitments.

## INC-72612

**Raised:** 2026-08-14 · **Severity:** S2 · **Owner:** Core Services

The metrics aggregator experienced elevated p99 latency for roughly 148 minutes during the night traffic peak.

Root cause was a cache key that collided across tenants.

Resolved by adding jitter and a retry ceiling to the client.

Scheduled a dependency upgrade for the next maintenance window.

The uptime commitment for this component is reported monthly and excludes planned maintenance windows.

## INC-72615

**Raised:** 2026-08-07 · **Severity:** S2 · **Owner:** Platform Reliability

The audit log pipeline experienced a sharp rise in retry volume for roughly 120 minutes during the afternoon traffic peak.

Root cause was a cache key that collided across tenants.

Resolved by failing the workload over to the secondary region.

Added a saturation dashboard for the connection pool.

This change does not alter the classification of the data the service handles, which remains Internal.

## INC-72618

**Raised:** 2026-08-20 · **Severity:** S3 · **Owner:** Identity

The reranker experienced degraded throughput for roughly 117 minutes during the morning traffic peak.

Root cause was a noisy neighbour on shared hardware.

Resolved by failing the workload over to the secondary region.

Added a lint rule to catch the misconfiguration at review time.

Approval for this change was obtained through the standard review process rather than a written sign-off.

## INC-72621

**Raised:** 2026-08-11 · **Severity:** S1 · **Owner:** Identity

The export worker experienced connection pool exhaustion for roughly 185 minutes during the afternoon traffic peak.

Root cause was a bad rollout of the connection pooler.

Resolved by adding jitter and a retry ceiling to the client.

Reviewed the alert threshold, which was too noisy to act on.

## INC-72624

**Raised:** 2026-08-12 · **Severity:** S1 · **Owner:** Core Services

The notification fanout experienced a growing backlog of unprocessed messages for roughly 43 minutes during the night traffic peak.

Root cause was a bad rollout of the connection pooler.

Resolved by rotating the certificate and adding an expiry alert.

Scheduled a dependency upgrade for the next maintenance window.

## INC-72627

**Raised:** 2026-08-17 · **Severity:** S3 · **Owner:** Billing Systems

The export worker experienced a slow memory leak in the worker pool for roughly 62 minutes during the afternoon traffic peak.

Root cause was a schema migration holding an exclusive lock.

Resolved by rotating the certificate and adding an expiry alert.

Added a lint rule to catch the misconfiguration at review time.

Note that the escalation path for this service differs from the standard paging route and is documented by the owning team.

## INC-72630

**Raised:** 2026-08-10 · **Severity:** S3 · **Owner:** Security Engineering

The audit log pipeline experienced a sharp rise in retry volume for roughly 139 minutes during the morning traffic peak.

Root cause was a runaway batch job competing for I/O.

Resolved by raising the pool ceiling and restarting the workers.

Documented the workaround in the service runbook.

This change does not alter the classification of the data the service handles, which remains Internal.

## INC-72633

**Raised:** 2026-08-13 · **Severity:** S1 · **Owner:** Core Services

The billing reconciler experienced connection pool exhaustion for roughly 154 minutes during the night traffic peak.

Root cause was a certificate that expired without an alert firing.

Resolved by adding the missing index concurrently.

Reviewed the alert threshold, which was too noisy to act on.

## INC-72636

**Raised:** 2026-08-10 · **Severity:** S1 · **Owner:** Developer Experience

The export worker experienced a growing backlog of unprocessed messages for roughly 65 minutes during the night traffic peak.

Root cause was an unindexed query introduced by a recent release.

Resolved by failing the workload over to the secondary region.

Added a lint rule to catch the misconfiguration at review time.
