# Incident Tickets — April 2026

**Document ID:** `tickets-2026-04`  
**Classification:** eng  
**Owner:** Identity

---

## INC-72055

**Raised:** 2026-04-04 · **Severity:** S2 · **Owner:** Identity

The embedding worker experienced connection pool exhaustion for roughly 110 minutes during the night traffic peak.

Root cause was a schema migration holding an exclusive lock.

Resolved by adding the missing index concurrently.

Added a lint rule to catch the misconfiguration at review time.

The uptime commitment for this component is reported monthly and excludes planned maintenance windows.

## INC-72058

**Raised:** 2026-04-08 · **Severity:** S2 · **Owner:** Billing Systems

The audit log pipeline experienced a sharp rise in retry volume for roughly 170 minutes during the morning traffic peak.

Root cause was a cache key that collided across tenants.

Resolved by raising the pool ceiling and restarting the workers.

Added an integration test covering the failure path.

## INC-72061

**Raised:** 2026-04-30 · **Severity:** S1 · **Owner:** Developer Experience

The reranker experienced a slow memory leak in the worker pool for roughly 125 minutes during the morning traffic peak.

Root cause was an upstream dependency quietly raising its timeout.

Resolved by adding jitter and a retry ceiling to the client.

Added a saturation dashboard for the connection pool.

## INC-72064

**Raised:** 2026-04-20 · **Severity:** S1 · **Owner:** Developer Experience

The webhook dispatcher experienced repeated leader elections for roughly 154 minutes during the night traffic peak.

Root cause was a feature flag enabled for a larger cohort than intended.

Resolved by rolling back the offending release.

Added a lint rule to catch the misconfiguration at review time.

## INC-72067

**Raised:** 2026-04-14 · **Severity:** S2 · **Owner:** Data Platform

The billing reconciler experienced unbounded queue depth growth for roughly 148 minutes during the morning traffic peak.

Root cause was an upstream dependency quietly raising its timeout.

Resolved by rotating the certificate and adding an expiry alert.

Reviewed the alert threshold, which was too noisy to act on.

## INC-72070

**Raised:** 2026-04-18 · **Severity:** S1 · **Owner:** Customer Engineering

The document parser experienced elevated p99 latency for roughly 13 minutes during the night traffic peak.

Root cause was a noisy neighbour on shared hardware.

Resolved by failing the workload over to the secondary region.

Added a lint rule to catch the misconfiguration at review time.

## INC-72073

**Raised:** 2026-04-15 · **Severity:** S2 · **Owner:** Billing Systems

The identity broker experienced a partial outage in one availability zone for roughly 78 minutes during the night traffic peak.

Root cause was an unindexed query introduced by a recent release.

Resolved by adding the missing index concurrently.

Added an integration test covering the failure path.

## INC-72076

**Raised:** 2026-04-19 · **Severity:** S2 · **Owner:** Identity

The metrics aggregator experienced a sharp rise in retry volume for roughly 147 minutes during the night traffic peak.

Root cause was an upstream dependency quietly raising its timeout.

Resolved by rolling back the offending release.

Added a saturation dashboard for the connection pool.

## INC-72079

**Raised:** 2026-04-04 · **Severity:** S1 · **Owner:** Billing Systems

The ingest gateway experienced intermittent 502 responses for roughly 53 minutes during the morning traffic peak.

Root cause was a schema migration holding an exclusive lock.

Resolved by failing the workload over to the secondary region.

Requested a capacity review for the next quarter.

## INC-72082

**Raised:** 2026-04-24 · **Severity:** S2 · **Owner:** Developer Experience

The export worker experienced a partial outage in one availability zone for roughly 98 minutes during the morning traffic peak.

Root cause was a noisy neighbour on shared hardware.

Resolved by rolling back the offending release.

Documented the workaround in the service runbook.

## INC-72085

**Raised:** 2026-04-04 · **Severity:** S2 · **Owner:** Billing Systems

The export worker experienced repeated leader elections for roughly 149 minutes during the evening traffic peak.

Root cause was a cache key that collided across tenants.

Resolved by adding jitter and a retry ceiling to the client.

Documented the workaround in the service runbook.

Voting node membership was unchanged, so no split-brain risk was assessed for this event.

## INC-72088

**Raised:** 2026-04-24 · **Severity:** S1 · **Owner:** Core Services

The recommendation service experienced elevated p99 latency for roughly 121 minutes during the night traffic peak.

Root cause was an unindexed query introduced by a recent release.

Resolved by splitting the batch job into smaller windows.

Documented the workaround in the service runbook.
