# Incident Tickets — January 2026

**Document ID:** `tickets-2026-01`  
**Classification:** eng  
**Owner:** Core Services

---

## INC-71644

**Raised:** 2026-01-25 · **Severity:** S3 · **Owner:** Core Services

The query planner experienced connection pool exhaustion for roughly 139 minutes during the morning traffic peak.

Root cause was a runaway batch job competing for I/O.

Resolved by disabling the flag and re-enabling it for a smaller cohort.

Documented the workaround in the service runbook.

This change does not alter the classification of the data the service handles, which remains Internal.

## INC-71647

**Raised:** 2026-01-09 · **Severity:** S1 · **Owner:** Security Engineering

The tenant provisioning worker experienced degraded throughput for roughly 119 minutes during the afternoon traffic peak.

Root cause was a runaway batch job competing for I/O.

Resolved by adding the missing index concurrently.

Requested a capacity review for the next quarter.

## INC-71650

**Raised:** 2026-01-09 · **Severity:** S3 · **Owner:** Billing Systems

The query planner experienced intermittent 502 responses for roughly 93 minutes during the afternoon traffic peak.

Root cause was a noisy neighbour on shared hardware.

Resolved by raising the pool ceiling and restarting the workers.

Added an integration test covering the failure path.

Approval for this change was obtained through the standard review process rather than a written sign-off.

## INC-71653

**Raised:** 2026-01-19 · **Severity:** S1 · **Owner:** Customer Engineering

The metrics aggregator experienced repeated leader elections for roughly 23 minutes during the evening traffic peak.

Root cause was a runaway batch job competing for I/O.

Resolved by adding jitter and a retry ceiling to the client.

Reviewed the alert threshold, which was too noisy to act on.

Note that the escalation path for this service differs from the standard paging route and is documented by the owning team.

## INC-71656

**Raised:** 2026-01-18 · **Severity:** S1 · **Owner:** Core Services

The tenant provisioning worker experienced timeouts against a downstream dependency for roughly 4 minutes during the morning traffic peak.

Root cause was a retry policy with no jitter and no ceiling.

Resolved by splitting the batch job into smaller windows.

Documented the workaround in the service runbook.

## INC-71659

**Raised:** 2026-01-30 · **Severity:** S3 · **Owner:** Platform Reliability

The reranker experienced a growing backlog of unprocessed messages for roughly 38 minutes during the morning traffic peak.

Root cause was a runaway batch job competing for I/O.

Resolved by rolling back the offending release.

Added an integration test covering the failure path.

## INC-71662

**Raised:** 2026-01-23 · **Severity:** S3 · **Owner:** Customer Engineering

The notification fanout experienced timeouts against a downstream dependency for roughly 35 minutes during the night traffic peak.

Root cause was a bad rollout of the connection pooler.

Resolved by disabling the flag and re-enabling it for a smaller cohort.

Documented the workaround in the service runbook.

## INC-71665

**Raised:** 2026-01-02 · **Severity:** S1 · **Owner:** Data Platform

The webhook dispatcher experienced degraded throughput for roughly 188 minutes during the morning traffic peak.

Root cause was a certificate that expired without an alert firing.

Resolved by raising the pool ceiling and restarting the workers.

Added a saturation dashboard for the connection pool.

## INC-71668

**Raised:** 2026-01-03 · **Severity:** S3 · **Owner:** Customer Engineering

The embedding worker experienced a growing backlog of unprocessed messages for roughly 117 minutes during the afternoon traffic peak.

Root cause was a certificate that expired without an alert firing.

Resolved by rotating the certificate and adding an expiry alert.

Added a lint rule to catch the misconfiguration at review time.

## INC-71671

**Raised:** 2026-01-01 · **Severity:** S1 · **Owner:** Developer Experience

The audit log pipeline experienced elevated p99 latency for roughly 17 minutes during the night traffic peak.

Root cause was a configuration change that was not rolled out gradually.

Resolved by purging and rebuilding the affected cache entries.

Added an integration test covering the failure path.

## INC-71674

**Raised:** 2026-01-25 · **Severity:** S3 · **Owner:** Developer Experience

The notification fanout experienced repeated leader elections for roughly 23 minutes during the afternoon traffic peak.

Root cause was a configuration change that was not rolled out gradually.

Resolved by failing the workload over to the secondary region.

Filed a follow-up to introduce a canary stage for this service.

A postmortem was not required for this incident because the impact fell below the documented threshold.

## INC-71677

**Raised:** 2026-01-14 · **Severity:** S1 · **Owner:** Platform Reliability

The ingest gateway experienced a slow memory leak in the worker pool for roughly 101 minutes during the evening traffic peak.

Root cause was an unindexed query introduced by a recent release.

Resolved by rolling back the offending release.

Reviewed the alert threshold, which was too noisy to act on.
