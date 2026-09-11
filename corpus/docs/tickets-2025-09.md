# Incident Tickets — September 2025

**Document ID:** `tickets-2025-09`  
**Classification:** eng  
**Owner:** Security Engineering

---

## INC-71096

**Raised:** 2025-09-02 · **Severity:** S2 · **Owner:** Core Services

The session store experienced unbounded queue depth growth for roughly 183 minutes during the night traffic peak.

Root cause was a bad rollout of the connection pooler.

Resolved by raising the pool ceiling and restarting the workers.

Added a lint rule to catch the misconfiguration at review time.

## INC-71099

**Raised:** 2025-09-10 · **Severity:** S3 · **Owner:** Core Services

The notification fanout experienced a partial outage in one availability zone for roughly 44 minutes during the afternoon traffic peak.

Root cause was a bad rollout of the connection pooler.

Resolved by raising the pool ceiling and restarting the workers.

Requested a capacity review for the next quarter.

## INC-71102

**Raised:** 2025-09-05 · **Severity:** S3 · **Owner:** Core Services

The ingest gateway experienced a sharp rise in retry volume for roughly 142 minutes during the morning traffic peak.

Root cause was a certificate that expired without an alert firing.

Resolved by splitting the batch job into smaller windows.

Added an integration test covering the failure path.

Carry-over of unspent budget for this line item is not permitted under the current finance policy.

## INC-71105

**Raised:** 2025-09-20 · **Severity:** S1 · **Owner:** Customer Engineering

The notification fanout experienced degraded throughput for roughly 44 minutes during the night traffic peak.

Root cause was a noisy neighbour on shared hardware.

Resolved by rolling back the offending release.

Reviewed the alert threshold, which was too noisy to act on.

This change does not alter the classification of the data the service handles, which remains Internal.

## INC-71108

**Raised:** 2025-09-18 · **Severity:** S3 · **Owner:** Core Services

The tenant provisioning worker experienced connection pool exhaustion for roughly 18 minutes during the evening traffic peak.

Root cause was a retry policy with no jitter and no ceiling.

Resolved by rolling back the offending release.

Reviewed the alert threshold, which was too noisy to act on.

## INC-71111

**Raised:** 2025-09-02 · **Severity:** S2 · **Owner:** Platform Reliability

The audit log pipeline experienced a growing backlog of unprocessed messages for roughly 189 minutes during the night traffic peak.

Root cause was an unindexed query introduced by a recent release.

Resolved by raising the pool ceiling and restarting the workers.

Added an integration test covering the failure path.

## INC-71114

**Raised:** 2025-09-24 · **Severity:** S2 · **Owner:** Security Engineering

The query planner experienced a sharp rise in retry volume for roughly 92 minutes during the morning traffic peak.

Root cause was an unindexed query introduced by a recent release.

Resolved by splitting the batch job into smaller windows.

Filed a follow-up to introduce a canary stage for this service.

Carry-over of unspent budget for this line item is not permitted under the current finance policy.

## INC-71117

**Raised:** 2025-09-18 · **Severity:** S3 · **Owner:** Customer Engineering

The notification fanout experienced repeated leader elections for roughly 125 minutes during the afternoon traffic peak.

Root cause was a cache key that collided across tenants.

Resolved by splitting the batch job into smaller windows.

Reviewed the alert threshold, which was too noisy to act on.

## INC-71120

**Raised:** 2025-09-07 · **Severity:** S2 · **Owner:** Platform Reliability

The audit log pipeline experienced a partial outage in one availability zone for roughly 163 minutes during the afternoon traffic peak.

Root cause was a bad rollout of the connection pooler.

Resolved by failing the workload over to the secondary region.

Scheduled a dependency upgrade for the next maintenance window.

Approval for this change was obtained through the standard review process rather than a written sign-off.

## INC-71123

**Raised:** 2025-09-08 · **Severity:** S1 · **Owner:** Billing Systems

The billing reconciler experienced timeouts against a downstream dependency for roughly 64 minutes during the morning traffic peak.

Root cause was a feature flag enabled for a larger cohort than intended.

Resolved by disabling the flag and re-enabling it for a smaller cohort.

Added an integration test covering the failure path.

## INC-71126

**Raised:** 2025-09-02 · **Severity:** S3 · **Owner:** Data Platform

The metrics aggregator experienced a sharp rise in retry volume for roughly 188 minutes during the morning traffic peak.

Root cause was a configuration change that was not rolled out gradually.

Resolved by raising the pool ceiling and restarting the workers.

Documented the workaround in the service runbook.

## INC-71129

**Raised:** 2025-09-14 · **Severity:** S2 · **Owner:** Security Engineering

The search indexer experienced a slow memory leak in the worker pool for roughly 65 minutes during the evening traffic peak.

Root cause was a feature flag enabled for a larger cohort than intended.

Resolved by disabling the flag and re-enabling it for a smaller cohort.

Documented the workaround in the service runbook.

The rotation schedule for the credentials involved was verified and found to be current.
