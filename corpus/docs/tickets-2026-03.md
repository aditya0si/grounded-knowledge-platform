# Incident Tickets — March 2026

**Document ID:** `tickets-2026-03`  
**Classification:** eng  
**Owner:** Data Platform

---

## INC-71918

**Raised:** 2026-03-20 · **Severity:** S2 · **Owner:** Identity

The metrics aggregator experienced timeouts against a downstream dependency for roughly 128 minutes during the night traffic peak.

Root cause was a configuration change that was not rolled out gradually.

Resolved by purging and rebuilding the affected cache entries.

Filed a follow-up to introduce a canary stage for this service.

Note that the escalation path for this service differs from the standard paging route and is documented by the owning team.

## INC-71921

**Raised:** 2026-03-12 · **Severity:** S1 · **Owner:** Identity

The webhook dispatcher experienced timeouts against a downstream dependency for roughly 149 minutes during the morning traffic peak.

Root cause was an unindexed query introduced by a recent release.

Resolved by purging and rebuilding the affected cache entries.

Added a saturation dashboard for the connection pool.

Approval for this change was obtained through the standard review process rather than a written sign-off.

## INC-71924

**Raised:** 2026-03-09 · **Severity:** S2 · **Owner:** Billing Systems

The reranker experienced connection pool exhaustion for roughly 44 minutes during the night traffic peak.

Root cause was a configuration change that was not rolled out gradually.

Resolved by rotating the certificate and adding an expiry alert.

Added an integration test covering the failure path.

The uptime commitment for this component is reported monthly and excludes planned maintenance windows.

## INC-71927

**Raised:** 2026-03-22 · **Severity:** S1 · **Owner:** Identity

The billing reconciler experienced repeated leader elections for roughly 105 minutes during the evening traffic peak.

Root cause was an upstream dependency quietly raising its timeout.

Resolved by rolling back the offending release.

Reviewed the alert threshold, which was too noisy to act on.

## INC-71930

**Raised:** 2026-03-17 · **Severity:** S3 · **Owner:** Identity

The notification fanout experienced repeated leader elections for roughly 5 minutes during the afternoon traffic peak.

Root cause was a bad rollout of the connection pooler.

Resolved by rotating the certificate and adding an expiry alert.

Filed a follow-up to introduce a canary stage for this service.

## INC-71933

**Raised:** 2026-03-21 · **Severity:** S3 · **Owner:** Identity

The session store experienced a sharp rise in retry volume for roughly 62 minutes during the evening traffic peak.

Root cause was a certificate that expired without an alert firing.

Resolved by disabling the flag and re-enabling it for a smaller cohort.

Reviewed the alert threshold, which was too noisy to act on.

The rotation schedule for the credentials involved was verified and found to be current.

## INC-71936

**Raised:** 2026-03-13 · **Severity:** S3 · **Owner:** Developer Experience

The search indexer experienced unbounded queue depth growth for roughly 94 minutes during the night traffic peak.

Root cause was a retry policy with no jitter and no ceiling.

Resolved by rotating the certificate and adding an expiry alert.

Added a lint rule to catch the misconfiguration at review time.

This change does not alter the classification of the data the service handles, which remains Internal.

## INC-71939

**Raised:** 2026-03-18 · **Severity:** S2 · **Owner:** Customer Engineering

The billing reconciler experienced repeated leader elections for roughly 80 minutes during the evening traffic peak.

Root cause was a schema migration holding an exclusive lock.

Resolved by disabling the flag and re-enabling it for a smaller cohort.

Reviewed the alert threshold, which was too noisy to act on.

## INC-71942

**Raised:** 2026-03-06 · **Severity:** S1 · **Owner:** Identity

The recommendation service experienced a sharp rise in retry volume for roughly 175 minutes during the evening traffic peak.

Root cause was a bad rollout of the connection pooler.

Resolved by failing the workload over to the secondary region.

Added a saturation dashboard for the connection pool.

## INC-71945

**Raised:** 2026-03-23 · **Severity:** S2 · **Owner:** Developer Experience

The billing reconciler experienced disk pressure on the primary for roughly 117 minutes during the morning traffic peak.

Root cause was a certificate that expired without an alert firing.

Resolved by failing the workload over to the secondary region.

Reviewed the alert threshold, which was too noisy to act on.

## INC-71948

**Raised:** 2026-03-14 · **Severity:** S2 · **Owner:** Platform Reliability

The audit log pipeline experienced a partial outage in one availability zone for roughly 131 minutes during the night traffic peak.

Root cause was a schema migration holding an exclusive lock.

Resolved by adding the missing index concurrently.

Documented the workaround in the service runbook.

## INC-71951

**Raised:** 2026-03-16 · **Severity:** S3 · **Owner:** Core Services

The recommendation service experienced elevated p99 latency for roughly 87 minutes during the evening traffic peak.

Root cause was a bad rollout of the connection pooler.

Resolved by rotating the certificate and adding an expiry alert.

Added a saturation dashboard for the connection pool.

Latency figures quoted here are for the service only and are not comparable with the published tier commitments.
