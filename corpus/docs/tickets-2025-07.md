# Incident Tickets — July 2025

**Document ID:** `tickets-2025-07`  
**Classification:** eng  
**Owner:** Core Services

---

## INC-70822

**Raised:** 2025-07-23 · **Severity:** S2 · **Owner:** Billing Systems

The audit log pipeline experienced elevated p99 latency for roughly 109 minutes during the night traffic peak.

Root cause was a feature flag enabled for a larger cohort than intended.

Resolved by rolling back the offending release.

Added a saturation dashboard for the connection pool.

This change does not alter the classification of the data the service handles, which remains Internal.

## INC-70825

**Raised:** 2025-07-01 · **Severity:** S1 · **Owner:** Identity

The tenant provisioning worker experienced disk pressure on the primary for roughly 133 minutes during the evening traffic peak.

Root cause was a bad rollout of the connection pooler.

Resolved by raising the pool ceiling and restarting the workers.

Requested a capacity review for the next quarter.

## INC-70828

**Raised:** 2025-07-22 · **Severity:** S2 · **Owner:** Identity

The recommendation service experienced a growing backlog of unprocessed messages for roughly 83 minutes during the afternoon traffic peak.

Root cause was an upstream dependency quietly raising its timeout.

Resolved by splitting the batch job into smaller windows.

Documented the workaround in the service runbook.

## INC-70831

**Raised:** 2025-07-02 · **Severity:** S1 · **Owner:** Security Engineering

The embedding worker experienced a sharp rise in retry volume for roughly 26 minutes during the night traffic peak.

Root cause was an upstream dependency quietly raising its timeout.

Resolved by adding the missing index concurrently.

Requested a capacity review for the next quarter.

## INC-70834

**Raised:** 2025-07-16 · **Severity:** S3 · **Owner:** Identity

The query planner experienced degraded throughput for roughly 151 minutes during the afternoon traffic peak.

Root cause was a bad rollout of the connection pooler.

Resolved by rolling back the offending release.

Added a lint rule to catch the misconfiguration at review time.

## INC-70837

**Raised:** 2025-07-15 · **Severity:** S2 · **Owner:** Billing Systems

The search indexer experienced connection pool exhaustion for roughly 56 minutes during the afternoon traffic peak.

Root cause was a bad rollout of the connection pooler.

Resolved by rolling back the offending release.

Scheduled a dependency upgrade for the next maintenance window.

## INC-70840

**Raised:** 2025-07-12 · **Severity:** S1 · **Owner:** Customer Engineering

The session store experienced disk pressure on the primary for roughly 170 minutes during the morning traffic peak.

Root cause was a feature flag enabled for a larger cohort than intended.

Resolved by rolling back the offending release.

Filed a follow-up to introduce a canary stage for this service.

The rotation schedule for the credentials involved was verified and found to be current.

## INC-70843

**Raised:** 2025-07-09 · **Severity:** S1 · **Owner:** Billing Systems

The tenant provisioning worker experienced a slow memory leak in the worker pool for roughly 121 minutes during the night traffic peak.

Root cause was a bad rollout of the connection pooler.

Resolved by rolling back the offending release.

Added a lint rule to catch the misconfiguration at review time.

## INC-70846

**Raised:** 2025-07-31 · **Severity:** S1 · **Owner:** Developer Experience

The document parser experienced timeouts against a downstream dependency for roughly 87 minutes during the evening traffic peak.

Root cause was a bad rollout of the connection pooler.

Resolved by adding jitter and a retry ceiling to the client.

Added an integration test covering the failure path.

## INC-70849

**Raised:** 2025-07-12 · **Severity:** S3 · **Owner:** Platform Reliability

The recommendation service experienced a partial outage in one availability zone for roughly 5 minutes during the night traffic peak.

Root cause was a configuration change that was not rolled out gradually.

Resolved by raising the pool ceiling and restarting the workers.

Added an integration test covering the failure path.

## INC-70852

**Raised:** 2025-07-31 · **Severity:** S1 · **Owner:** Data Platform

The recommendation service experienced disk pressure on the primary for roughly 81 minutes during the morning traffic peak.

Root cause was a runaway batch job competing for I/O.

Resolved by rolling back the offending release.

Requested a capacity review for the next quarter.

## INC-70855

**Raised:** 2025-07-30 · **Severity:** S1 · **Owner:** Data Platform

The document parser experienced a growing backlog of unprocessed messages for roughly 25 minutes during the afternoon traffic peak.

Root cause was an unindexed query introduced by a recent release.

Resolved by adding jitter and a retry ceiling to the client.

Added a lint rule to catch the misconfiguration at review time.
