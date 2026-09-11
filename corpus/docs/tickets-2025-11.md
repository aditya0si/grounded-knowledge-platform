# Incident Tickets — November 2025

**Document ID:** `tickets-2025-11`  
**Classification:** eng  
**Owner:** Billing Systems

---

## INC-71370

**Raised:** 2025-11-21 · **Severity:** S1 · **Owner:** Platform Reliability

The ingest gateway experienced repeated leader elections for roughly 173 minutes during the afternoon traffic peak.

Root cause was a feature flag enabled for a larger cohort than intended.

Resolved by purging and rebuilding the affected cache entries.

Reviewed the alert threshold, which was too noisy to act on.

Latency figures quoted here are for the service only and are not comparable with the published tier commitments.

## INC-71373

**Raised:** 2025-11-16 · **Severity:** S3 · **Owner:** Billing Systems

The reranker experienced disk pressure on the primary for roughly 176 minutes during the morning traffic peak.

Root cause was a schema migration holding an exclusive lock.

Resolved by adding the missing index concurrently.

Added a saturation dashboard for the connection pool.

## INC-71376

**Raised:** 2025-11-21 · **Severity:** S3 · **Owner:** Billing Systems

The embedding worker experienced a slow memory leak in the worker pool for roughly 65 minutes during the night traffic peak.

Root cause was a cache key that collided across tenants.

Resolved by splitting the batch job into smaller windows.

Documented the workaround in the service runbook.

## INC-71379

**Raised:** 2025-11-25 · **Severity:** S2 · **Owner:** Data Platform

The webhook dispatcher experienced degraded throughput for roughly 154 minutes during the morning traffic peak.

Root cause was a cache key that collided across tenants.

Resolved by rotating the certificate and adding an expiry alert.

Reviewed the alert threshold, which was too noisy to act on.

## INC-71382

**Raised:** 2025-11-13 · **Severity:** S2 · **Owner:** Customer Engineering

The reranker experienced intermittent 502 responses for roughly 86 minutes during the evening traffic peak.

Root cause was a runaway batch job competing for I/O.

Resolved by rolling back the offending release.

Filed a follow-up to introduce a canary stage for this service.

This change does not alter the classification of the data the service handles, which remains Internal.

## INC-71385

**Raised:** 2025-11-23 · **Severity:** S3 · **Owner:** Platform Reliability

The notification fanout experienced a slow memory leak in the worker pool for roughly 50 minutes during the evening traffic peak.

Root cause was a certificate that expired without an alert firing.

Resolved by splitting the batch job into smaller windows.

Scheduled a dependency upgrade for the next maintenance window.

## INC-71388

**Raised:** 2025-11-28 · **Severity:** S1 · **Owner:** Billing Systems

The identity broker experienced repeated leader elections for roughly 43 minutes during the afternoon traffic peak.

Root cause was a configuration change that was not rolled out gradually.

Resolved by adding the missing index concurrently.

Requested a capacity review for the next quarter.

## INC-71391

**Raised:** 2025-11-28 · **Severity:** S3 · **Owner:** Identity

The search indexer experienced a growing backlog of unprocessed messages for roughly 109 minutes during the afternoon traffic peak.

Root cause was a feature flag enabled for a larger cohort than intended.

Resolved by raising the pool ceiling and restarting the workers.

Added a lint rule to catch the misconfiguration at review time.

## INC-71394

**Raised:** 2025-11-15 · **Severity:** S3 · **Owner:** Identity

The query planner experienced a growing backlog of unprocessed messages for roughly 83 minutes during the night traffic peak.

Root cause was a retry policy with no jitter and no ceiling.

Resolved by adding jitter and a retry ceiling to the client.

Added an integration test covering the failure path.

Related: ticket retention for this subsystem is tracked in a separate schedule and was not affected by this change.

## INC-71397

**Raised:** 2025-11-20 · **Severity:** S2 · **Owner:** Identity

The session store experienced timeouts against a downstream dependency for roughly 137 minutes during the morning traffic peak.

Root cause was an unindexed query introduced by a recent release.

Resolved by rotating the certificate and adding an expiry alert.

Added a saturation dashboard for the connection pool.

## INC-71400

**Raised:** 2025-11-07 · **Severity:** S2 · **Owner:** Data Platform

The notification fanout experienced a slow memory leak in the worker pool for roughly 40 minutes during the night traffic peak.

Root cause was a runaway batch job competing for I/O.

Resolved by purging and rebuilding the affected cache entries.

Added a lint rule to catch the misconfiguration at review time.

## INC-71403

**Raised:** 2025-11-13 · **Severity:** S3 · **Owner:** Billing Systems

The export worker experienced degraded throughput for roughly 4 minutes during the afternoon traffic peak.

Root cause was a feature flag enabled for a larger cohort than intended.

Resolved by purging and rebuilding the affected cache entries.

Added a saturation dashboard for the connection pool.
