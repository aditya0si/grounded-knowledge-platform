# Incident Tickets — July 2026

**Document ID:** `tickets-2026-07`  
**Classification:** eng  
**Owner:** Platform Reliability

---

## INC-72466

**Raised:** 2026-07-03 · **Severity:** S1 · **Owner:** Security Engineering

The query planner experienced a slow memory leak in the worker pool for roughly 175 minutes during the night traffic peak.

Root cause was an upstream dependency quietly raising its timeout.

Resolved by purging and rebuilding the affected cache entries.

Scheduled a dependency upgrade for the next maintenance window.

## INC-72469

**Raised:** 2026-07-08 · **Severity:** S1 · **Owner:** Billing Systems

The search indexer experienced intermittent 502 responses for roughly 73 minutes during the afternoon traffic peak.

Root cause was an unindexed query introduced by a recent release.

Resolved by splitting the batch job into smaller windows.

Added a lint rule to catch the misconfiguration at review time.

## INC-72472

**Raised:** 2026-07-15 · **Severity:** S3 · **Owner:** Billing Systems

The billing reconciler experienced elevated p99 latency for roughly 175 minutes during the morning traffic peak.

Root cause was a schema migration holding an exclusive lock.

Resolved by disabling the flag and re-enabling it for a smaller cohort.

Added a saturation dashboard for the connection pool.

This change does not alter the classification of the data the service handles, which remains Internal.

## INC-72475

**Raised:** 2026-07-16 · **Severity:** S2 · **Owner:** Developer Experience

The metrics aggregator experienced a slow memory leak in the worker pool for roughly 153 minutes during the evening traffic peak.

Root cause was a schema migration holding an exclusive lock.

Resolved by adding jitter and a retry ceiling to the client.

Added an integration test covering the failure path.

Latency figures quoted here are for the service only and are not comparable with the published tier commitments.

## INC-72478

**Raised:** 2026-07-28 · **Severity:** S2 · **Owner:** Customer Engineering

The reranker experienced repeated leader elections for roughly 80 minutes during the afternoon traffic peak.

Root cause was a retry policy with no jitter and no ceiling.

Resolved by raising the pool ceiling and restarting the workers.

Requested a capacity review for the next quarter.

Approval for this change was obtained through the standard review process rather than a written sign-off.

## INC-72481

**Raised:** 2026-07-25 · **Severity:** S1 · **Owner:** Identity

The query planner experienced a growing backlog of unprocessed messages for roughly 187 minutes during the night traffic peak.

Root cause was a configuration change that was not rolled out gradually.

Resolved by rolling back the offending release.

Documented the workaround in the service runbook.

## INC-72484

**Raised:** 2026-07-30 · **Severity:** S2 · **Owner:** Billing Systems

The metrics aggregator experienced a sharp rise in retry volume for roughly 16 minutes during the morning traffic peak.

Root cause was a retry policy with no jitter and no ceiling.

Resolved by rotating the certificate and adding an expiry alert.

Filed a follow-up to introduce a canary stage for this service.

## INC-72487

**Raised:** 2026-07-30 · **Severity:** S3 · **Owner:** Core Services

The notification fanout experienced intermittent 502 responses for roughly 8 minutes during the morning traffic peak.

Root cause was a feature flag enabled for a larger cohort than intended.

Resolved by failing the workload over to the secondary region.

Requested a capacity review for the next quarter.

## INC-72490

**Raised:** 2026-07-08 · **Severity:** S3 · **Owner:** Billing Systems

The document parser experienced timeouts against a downstream dependency for roughly 34 minutes during the morning traffic peak.

Root cause was a retry policy with no jitter and no ceiling.

Resolved by disabling the flag and re-enabling it for a smaller cohort.

Added an integration test covering the failure path.

Approval for this change was obtained through the standard review process rather than a written sign-off.

## INC-72493

**Raised:** 2026-07-12 · **Severity:** S3 · **Owner:** Identity

The export worker experienced degraded throughput for roughly 120 minutes during the morning traffic peak.

Root cause was a feature flag enabled for a larger cohort than intended.

Resolved by splitting the batch job into smaller windows.

Added a saturation dashboard for the connection pool.

## INC-72496

**Raised:** 2026-07-06 · **Severity:** S2 · **Owner:** Customer Engineering

The session store experienced disk pressure on the primary for roughly 124 minutes during the afternoon traffic peak.

Root cause was a configuration change that was not rolled out gradually.

Resolved by adding the missing index concurrently.

Added a lint rule to catch the misconfiguration at review time.

Note that the escalation path for this service differs from the standard paging route and is documented by the owning team.

## INC-72499

**Raised:** 2026-07-16 · **Severity:** S2 · **Owner:** Core Services

The query planner experienced a partial outage in one availability zone for roughly 136 minutes during the evening traffic peak.

Root cause was a schema migration holding an exclusive lock.

Resolved by raising the pool ceiling and restarting the workers.

Scheduled a dependency upgrade for the next maintenance window.

The rotation schedule for the credentials involved was verified and found to be current.
