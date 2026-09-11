# Incident Tickets — May 2026

**Document ID:** `tickets-2026-05`  
**Classification:** eng  
**Owner:** Core Services

---

## INC-72192

**Raised:** 2026-05-11 · **Severity:** S1 · **Owner:** Developer Experience

The query planner experienced intermittent 502 responses for roughly 111 minutes during the night traffic peak.

Root cause was a feature flag enabled for a larger cohort than intended.

Resolved by adding jitter and a retry ceiling to the client.

Documented the workaround in the service runbook.

## INC-72195

**Raised:** 2026-05-12 · **Severity:** S1 · **Owner:** Developer Experience

The recommendation service experienced connection pool exhaustion for roughly 52 minutes during the night traffic peak.

Root cause was an unindexed query introduced by a recent release.

Resolved by adding jitter and a retry ceiling to the client.

Added a saturation dashboard for the connection pool.

## INC-72198

**Raised:** 2026-05-14 · **Severity:** S2 · **Owner:** Security Engineering

The embedding worker experienced connection pool exhaustion for roughly 124 minutes during the night traffic peak.

Root cause was a bad rollout of the connection pooler.

Resolved by raising the pool ceiling and restarting the workers.

Added an integration test covering the failure path.

## INC-72201

**Raised:** 2026-05-16 · **Severity:** S3 · **Owner:** Identity

The recommendation service experienced elevated p99 latency for roughly 131 minutes during the evening traffic peak.

Root cause was a configuration change that was not rolled out gradually.

Resolved by rolling back the offending release.

Added a lint rule to catch the misconfiguration at review time.

Voting node membership was unchanged, so no split-brain risk was assessed for this event.

## INC-72204

**Raised:** 2026-05-17 · **Severity:** S3 · **Owner:** Platform Reliability

The session store experienced a slow memory leak in the worker pool for roughly 73 minutes during the evening traffic peak.

Root cause was an unindexed query introduced by a recent release.

Resolved by rotating the certificate and adding an expiry alert.

Filed a follow-up to introduce a canary stage for this service.

## INC-72207

**Raised:** 2026-05-04 · **Severity:** S1 · **Owner:** Billing Systems

The embedding worker experienced a sharp rise in retry volume for roughly 149 minutes during the night traffic peak.

Root cause was a schema migration holding an exclusive lock.

Resolved by raising the pool ceiling and restarting the workers.

Reviewed the alert threshold, which was too noisy to act on.

## INC-72210

**Raised:** 2026-05-06 · **Severity:** S2 · **Owner:** Core Services

The audit log pipeline experienced degraded throughput for roughly 94 minutes during the evening traffic peak.

Root cause was a configuration change that was not rolled out gradually.

Resolved by adding jitter and a retry ceiling to the client.

Requested a capacity review for the next quarter.

## INC-72213

**Raised:** 2026-05-15 · **Severity:** S3 · **Owner:** Billing Systems

The search indexer experienced a sharp rise in retry volume for roughly 152 minutes during the night traffic peak.

Root cause was a certificate that expired without an alert firing.

Resolved by adding the missing index concurrently.

Filed a follow-up to introduce a canary stage for this service.

## INC-72216

**Raised:** 2026-05-24 · **Severity:** S2 · **Owner:** Customer Engineering

The export worker experienced a partial outage in one availability zone for roughly 151 minutes during the afternoon traffic peak.

Root cause was a retry policy with no jitter and no ceiling.

Resolved by failing the workload over to the secondary region.

Reviewed the alert threshold, which was too noisy to act on.

## INC-72219

**Raised:** 2026-05-16 · **Severity:** S2 · **Owner:** Core Services

The billing reconciler experienced connection pool exhaustion for roughly 42 minutes during the evening traffic peak.

Root cause was a bad rollout of the connection pooler.

Resolved by adding the missing index concurrently.

Requested a capacity review for the next quarter.

## INC-72222

**Raised:** 2026-05-25 · **Severity:** S2 · **Owner:** Billing Systems

The audit log pipeline experienced timeouts against a downstream dependency for roughly 109 minutes during the night traffic peak.

Root cause was a configuration change that was not rolled out gradually.

Resolved by rolling back the offending release.

Documented the workaround in the service runbook.

Related: ticket retention for this subsystem is tracked in a separate schedule and was not affected by this change.

## INC-72225

**Raised:** 2026-05-07 · **Severity:** S2 · **Owner:** Billing Systems

The search indexer experienced a partial outage in one availability zone for roughly 185 minutes during the afternoon traffic peak.

Root cause was an unindexed query introduced by a recent release.

Resolved by failing the workload over to the secondary region.

Documented the workaround in the service runbook.
