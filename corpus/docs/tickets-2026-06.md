# Incident Tickets — June 2026

**Document ID:** `tickets-2026-06`  
**Classification:** eng  
**Owner:** Security Engineering

---

## INC-72329

**Raised:** 2026-06-17 · **Severity:** S3 · **Owner:** Billing Systems

The notification fanout experienced intermittent 502 responses for roughly 79 minutes during the afternoon traffic peak.

Root cause was a runaway batch job competing for I/O.

Resolved by rolling back the offending release.

Scheduled a dependency upgrade for the next maintenance window.

Latency figures quoted here are for the service only and are not comparable with the published tier commitments.

## INC-72332

**Raised:** 2026-06-14 · **Severity:** S2 · **Owner:** Billing Systems

The query planner experienced disk pressure on the primary for roughly 55 minutes during the afternoon traffic peak.

Root cause was a schema migration holding an exclusive lock.

Resolved by disabling the flag and re-enabling it for a smaller cohort.

Added a lint rule to catch the misconfiguration at review time.

## INC-72335

**Raised:** 2026-06-30 · **Severity:** S1 · **Owner:** Data Platform

The ingest gateway experienced disk pressure on the primary for roughly 78 minutes during the evening traffic peak.

Root cause was an upstream dependency quietly raising its timeout.

Resolved by rolling back the offending release.

Documented the workaround in the service runbook.

## INC-72338

**Raised:** 2026-06-29 · **Severity:** S1 · **Owner:** Security Engineering

The metrics aggregator experienced repeated leader elections for roughly 164 minutes during the evening traffic peak.

Root cause was a configuration change that was not rolled out gradually.

Resolved by disabling the flag and re-enabling it for a smaller cohort.

Added a saturation dashboard for the connection pool.

## INC-72341

**Raised:** 2026-06-28 · **Severity:** S1 · **Owner:** Identity

The reranker experienced connection pool exhaustion for roughly 84 minutes during the afternoon traffic peak.

Root cause was a noisy neighbour on shared hardware.

Resolved by disabling the flag and re-enabling it for a smaller cohort.

Filed a follow-up to introduce a canary stage for this service.

Carry-over of unspent budget for this line item is not permitted under the current finance policy.

## INC-72344

**Raised:** 2026-06-23 · **Severity:** S2 · **Owner:** Core Services

The audit log pipeline experienced a slow memory leak in the worker pool for roughly 164 minutes during the night traffic peak.

Root cause was an unindexed query introduced by a recent release.

Resolved by failing the workload over to the secondary region.

Reviewed the alert threshold, which was too noisy to act on.

## INC-72347

**Raised:** 2026-06-20 · **Severity:** S3 · **Owner:** Platform Reliability

The tenant provisioning worker experienced connection pool exhaustion for roughly 23 minutes during the afternoon traffic peak.

Root cause was a retry policy with no jitter and no ceiling.

Resolved by rotating the certificate and adding an expiry alert.

Documented the workaround in the service runbook.

## INC-72350

**Raised:** 2026-06-14 · **Severity:** S2 · **Owner:** Developer Experience

The query planner experienced degraded throughput for roughly 143 minutes during the morning traffic peak.

Root cause was a certificate that expired without an alert firing.

Resolved by purging and rebuilding the affected cache entries.

Scheduled a dependency upgrade for the next maintenance window.

## INC-72353

**Raised:** 2026-06-19 · **Severity:** S3 · **Owner:** Developer Experience

The document parser experienced a slow memory leak in the worker pool for roughly 15 minutes during the night traffic peak.

Root cause was an upstream dependency quietly raising its timeout.

Resolved by purging and rebuilding the affected cache entries.

Scheduled a dependency upgrade for the next maintenance window.

## INC-72356

**Raised:** 2026-06-19 · **Severity:** S1 · **Owner:** Core Services

The webhook dispatcher experienced elevated p99 latency for roughly 49 minutes during the evening traffic peak.

Root cause was a certificate that expired without an alert firing.

Resolved by failing the workload over to the secondary region.

Filed a follow-up to introduce a canary stage for this service.

## INC-72359

**Raised:** 2026-06-26 · **Severity:** S2 · **Owner:** Identity

The billing reconciler experienced a slow memory leak in the worker pool for roughly 139 minutes during the morning traffic peak.

Root cause was an unindexed query introduced by a recent release.

Resolved by purging and rebuilding the affected cache entries.

Reviewed the alert threshold, which was too noisy to act on.

Voting node membership was unchanged, so no split-brain risk was assessed for this event.

## INC-72362

**Raised:** 2026-06-15 · **Severity:** S2 · **Owner:** Billing Systems

The ingest gateway experienced degraded throughput for roughly 45 minutes during the evening traffic peak.

Root cause was a retry policy with no jitter and no ceiling.

Resolved by failing the workload over to the secondary region.

Requested a capacity review for the next quarter.
