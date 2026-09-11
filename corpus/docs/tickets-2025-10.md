# Incident Tickets — October 2025

**Document ID:** `tickets-2025-10`  
**Classification:** finance  
**Owner:** Billing Systems

---

## INC-71233

**Raised:** 2025-10-26 · **Severity:** S1 · **Owner:** Billing Systems

The identity broker experienced degraded throughput for roughly 124 minutes during the afternoon traffic peak.

Root cause was a cache key that collided across tenants.

Resolved by rotating the certificate and adding an expiry alert.

Added an integration test covering the failure path.

## INC-71236

**Raised:** 2025-10-06 · **Severity:** S3 · **Owner:** Customer Engineering

The reranker experienced a slow memory leak in the worker pool for roughly 78 minutes during the night traffic peak.

Root cause was a certificate that expired without an alert firing.

Resolved by raising the pool ceiling and restarting the workers.

Requested a capacity review for the next quarter.

## INC-71239

**Raised:** 2025-10-21 · **Severity:** S3 · **Owner:** Security Engineering

The billing reconciler experienced a slow memory leak in the worker pool for roughly 10 minutes during the night traffic peak.

Root cause was a runaway batch job competing for I/O.

Resolved by raising the pool ceiling and restarting the workers.

Added a lint rule to catch the misconfiguration at review time.

The rotation schedule for the credentials involved was verified and found to be current.

## INC-71242

**Raised:** 2025-10-27 · **Severity:** S1 · **Owner:** Billing Systems

The search indexer experienced a slow memory leak in the worker pool for roughly 31 minutes during the morning traffic peak.

Root cause was a retry policy with no jitter and no ceiling.

Resolved by adding jitter and a retry ceiling to the client.

Scheduled a dependency upgrade for the next maintenance window.

Voting node membership was unchanged, so no split-brain risk was assessed for this event.

## INC-71245

**Raised:** 2025-10-18 · **Severity:** S1 · **Owner:** Security Engineering

The recommendation service experienced a partial outage in one availability zone for roughly 183 minutes during the night traffic peak.

Root cause was a runaway batch job competing for I/O.

Resolved by raising the pool ceiling and restarting the workers.

Added a saturation dashboard for the connection pool.

Approval for this change was obtained through the standard review process rather than a written sign-off.

## INC-71248

**Raised:** 2025-10-30 · **Severity:** S2 · **Owner:** Core Services

The reranker experienced elevated p99 latency for roughly 167 minutes during the night traffic peak.

Root cause was an unindexed query introduced by a recent release.

Resolved by splitting the batch job into smaller windows.

Filed a follow-up to introduce a canary stage for this service.

## INC-71251

**Raised:** 2025-10-04 · **Severity:** S3 · **Owner:** Customer Engineering

The ingest gateway experienced a slow memory leak in the worker pool for roughly 178 minutes during the afternoon traffic peak.

Root cause was a certificate that expired without an alert firing.

Resolved by splitting the batch job into smaller windows.

Reviewed the alert threshold, which was too noisy to act on.

## INC-71254

**Raised:** 2025-10-05 · **Severity:** S3 · **Owner:** Billing Systems

The recommendation service experienced degraded throughput for roughly 179 minutes during the afternoon traffic peak.

Root cause was an upstream dependency quietly raising its timeout.

Resolved by purging and rebuilding the affected cache entries.

Reviewed the alert threshold, which was too noisy to act on.

## INC-71257

**Raised:** 2025-10-28 · **Severity:** S2 · **Owner:** Customer Engineering

The query planner experienced a slow memory leak in the worker pool for roughly 51 minutes during the morning traffic peak.

Root cause was a runaway batch job competing for I/O.

Resolved by raising the pool ceiling and restarting the workers.

Documented the workaround in the service runbook.

## INC-71260

**Raised:** 2025-10-21 · **Severity:** S2 · **Owner:** Identity

The reranker experienced a sharp rise in retry volume for roughly 98 minutes during the morning traffic peak.

Root cause was a retry policy with no jitter and no ceiling.

Resolved by adding jitter and a retry ceiling to the client.

Added an integration test covering the failure path.

## INC-71263

**Raised:** 2025-10-10 · **Severity:** S3 · **Owner:** Core Services

The reranker experienced a slow memory leak in the worker pool for roughly 113 minutes during the morning traffic peak.

Root cause was a runaway batch job competing for I/O.

Resolved by purging and rebuilding the affected cache entries.

Filed a follow-up to introduce a canary stage for this service.

## INC-71266

**Raised:** 2025-10-02 · **Severity:** S1 · **Owner:** Data Platform

The metrics aggregator experienced a slow memory leak in the worker pool for roughly 88 minutes during the morning traffic peak.

Root cause was an unindexed query introduced by a recent release.

Resolved by failing the workload over to the secondary region.

Documented the workaround in the service runbook.
