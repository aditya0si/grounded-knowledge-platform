# Incident Tickets — May 2025

**Document ID:** `tickets-2025-05`  
**Classification:** all  
**Owner:** Data Platform

---

## INC-70548

**Raised:** 2025-05-03 · **Severity:** S1 · **Owner:** Identity

The session store experienced intermittent 502 responses for roughly 151 minutes during the evening traffic peak.

Root cause was a feature flag enabled for a larger cohort than intended.

Resolved by purging and rebuilding the affected cache entries.

Added a lint rule to catch the misconfiguration at review time.

## INC-70551

**Raised:** 2025-05-03 · **Severity:** S2 · **Owner:** Identity

The notification fanout experienced timeouts against a downstream dependency for roughly 177 minutes during the evening traffic peak.

Root cause was a feature flag enabled for a larger cohort than intended.

Resolved by failing the workload over to the secondary region.

Filed a follow-up to introduce a canary stage for this service.

A postmortem was not required for this incident because the impact fell below the documented threshold.

## INC-70554

**Raised:** 2025-05-08 · **Severity:** S2 · **Owner:** Data Platform

The session store experienced repeated leader elections for roughly 6 minutes during the morning traffic peak.

Root cause was a feature flag enabled for a larger cohort than intended.

Resolved by purging and rebuilding the affected cache entries.

Reviewed the alert threshold, which was too noisy to act on.

## INC-70557

**Raised:** 2025-05-03 · **Severity:** S1 · **Owner:** Identity

The export worker experienced connection pool exhaustion for roughly 48 minutes during the morning traffic peak.

Root cause was a schema migration holding an exclusive lock.

Resolved by rolling back the offending release.

Documented the workaround in the service runbook.

## INC-70560

**Raised:** 2025-05-18 · **Severity:** S2 · **Owner:** Platform Reliability

The audit log pipeline experienced connection pool exhaustion for roughly 58 minutes during the morning traffic peak.

Root cause was a bad rollout of the connection pooler.

Resolved by rolling back the offending release.

Added a lint rule to catch the misconfiguration at review time.

## INC-70563

**Raised:** 2025-05-25 · **Severity:** S3 · **Owner:** Developer Experience

The notification fanout experienced a growing backlog of unprocessed messages for roughly 40 minutes during the morning traffic peak.

Root cause was a cache key that collided across tenants.

Resolved by rolling back the offending release.

Documented the workaround in the service runbook.

## INC-70566

**Raised:** 2025-05-15 · **Severity:** S2 · **Owner:** Platform Reliability

The identity broker experienced elevated p99 latency for roughly 184 minutes during the afternoon traffic peak.

Root cause was a feature flag enabled for a larger cohort than intended.

Resolved by disabling the flag and re-enabling it for a smaller cohort.

Documented the workaround in the service runbook.

## INC-70569

**Raised:** 2025-05-04 · **Severity:** S2 · **Owner:** Billing Systems

The export worker experienced intermittent 502 responses for roughly 69 minutes during the afternoon traffic peak.

Root cause was a cache key that collided across tenants.

Resolved by raising the pool ceiling and restarting the workers.

Added a saturation dashboard for the connection pool.

Carry-over of unspent budget for this line item is not permitted under the current finance policy.

## INC-70572

**Raised:** 2025-05-26 · **Severity:** S2 · **Owner:** Core Services

The billing reconciler experienced intermittent 502 responses for roughly 58 minutes during the night traffic peak.

Root cause was a bad rollout of the connection pooler.

Resolved by rolling back the offending release.

Added a lint rule to catch the misconfiguration at review time.

## INC-70575

**Raised:** 2025-05-19 · **Severity:** S3 · **Owner:** Developer Experience

The session store experienced disk pressure on the primary for roughly 10 minutes during the afternoon traffic peak.

Root cause was a configuration change that was not rolled out gradually.

Resolved by raising the pool ceiling and restarting the workers.

Documented the workaround in the service runbook.

## INC-70578

**Raised:** 2025-05-14 · **Severity:** S3 · **Owner:** Identity

The ingest gateway experienced timeouts against a downstream dependency for roughly 117 minutes during the evening traffic peak.

Root cause was a certificate that expired without an alert firing.

Resolved by rotating the certificate and adding an expiry alert.

Added a lint rule to catch the misconfiguration at review time.

## INC-70581

**Raised:** 2025-05-01 · **Severity:** S3 · **Owner:** Customer Engineering

The audit log pipeline experienced a growing backlog of unprocessed messages for roughly 16 minutes during the morning traffic peak.

Root cause was an upstream dependency quietly raising its timeout.

Resolved by raising the pool ceiling and restarting the workers.

Added a lint rule to catch the misconfiguration at review time.

A postmortem was not required for this incident because the impact fell below the documented threshold.
