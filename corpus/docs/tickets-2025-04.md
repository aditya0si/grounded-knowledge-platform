# Incident Tickets — April 2025

**Document ID:** `tickets-2025-04`  
**Classification:** eng  
**Owner:** Security Engineering

---

## INC-70411

**Raised:** 2025-04-29 · **Severity:** S1 · **Owner:** Customer Engineering

The webhook dispatcher experienced elevated p99 latency for roughly 32 minutes during the evening traffic peak.

Root cause was a cache key that collided across tenants.

Resolved by rotating the certificate and adding an expiry alert.

Documented the workaround in the service runbook.

## INC-70414

**Raised:** 2025-04-23 · **Severity:** S2 · **Owner:** Data Platform

The metrics aggregator experienced a growing backlog of unprocessed messages for roughly 148 minutes during the morning traffic peak.

Root cause was an upstream dependency quietly raising its timeout.

Resolved by raising the pool ceiling and restarting the workers.

Reviewed the alert threshold, which was too noisy to act on.

## INC-70417

**Raised:** 2025-04-03 · **Severity:** S2 · **Owner:** Customer Engineering

The tenant provisioning worker experienced a partial outage in one availability zone for roughly 69 minutes during the afternoon traffic peak.

Root cause was a bad rollout of the connection pooler.

Resolved by adding the missing index concurrently.

Reviewed the alert threshold, which was too noisy to act on.

The uptime commitment for this component is reported monthly and excludes planned maintenance windows.

## INC-70420

**Raised:** 2025-04-11 · **Severity:** S2 · **Owner:** Platform Reliability

The audit log pipeline experienced connection pool exhaustion for roughly 76 minutes during the morning traffic peak.

Root cause was a cache key that collided across tenants.

Resolved by adding the missing index concurrently.

Added a saturation dashboard for the connection pool.

## INC-70423

**Raised:** 2025-04-17 · **Severity:** S2 · **Owner:** Billing Systems

The session store experienced elevated p99 latency for roughly 161 minutes during the morning traffic peak.

Root cause was a runaway batch job competing for I/O.

Resolved by disabling the flag and re-enabling it for a smaller cohort.

Documented the workaround in the service runbook.

## INC-70426

**Raised:** 2025-04-12 · **Severity:** S3 · **Owner:** Billing Systems

The recommendation service experienced unbounded queue depth growth for roughly 81 minutes during the night traffic peak.

Root cause was a schema migration holding an exclusive lock.

Resolved by purging and rebuilding the affected cache entries.

Reviewed the alert threshold, which was too noisy to act on.

## INC-70429

**Raised:** 2025-04-11 · **Severity:** S2 · **Owner:** Developer Experience

The billing reconciler experienced disk pressure on the primary for roughly 124 minutes during the morning traffic peak.

Root cause was a runaway batch job competing for I/O.

Resolved by failing the workload over to the secondary region.

Requested a capacity review for the next quarter.

## INC-70432

**Raised:** 2025-04-14 · **Severity:** S2 · **Owner:** Core Services

The billing reconciler experienced a growing backlog of unprocessed messages for roughly 77 minutes during the afternoon traffic peak.

Root cause was a certificate that expired without an alert firing.

Resolved by raising the pool ceiling and restarting the workers.

Documented the workaround in the service runbook.

Note that the escalation path for this service differs from the standard paging route and is documented by the owning team.

## INC-70435

**Raised:** 2025-04-12 · **Severity:** S3 · **Owner:** Platform Reliability

The embedding worker experienced a slow memory leak in the worker pool for roughly 64 minutes during the morning traffic peak.

Root cause was a configuration change that was not rolled out gradually.

Resolved by adding jitter and a retry ceiling to the client.

Added a lint rule to catch the misconfiguration at review time.

Carry-over of unspent budget for this line item is not permitted under the current finance policy.

## INC-70438

**Raised:** 2025-04-20 · **Severity:** S3 · **Owner:** Core Services

The reranker experienced timeouts against a downstream dependency for roughly 37 minutes during the night traffic peak.

Root cause was a schema migration holding an exclusive lock.

Resolved by adding the missing index concurrently.

Scheduled a dependency upgrade for the next maintenance window.

## INC-70441

**Raised:** 2025-04-08 · **Severity:** S2 · **Owner:** Billing Systems

The tenant provisioning worker experienced a slow memory leak in the worker pool for roughly 59 minutes during the night traffic peak.

Root cause was an upstream dependency quietly raising its timeout.

Resolved by rotating the certificate and adding an expiry alert.

Added a lint rule to catch the misconfiguration at review time.

## INC-70444

**Raised:** 2025-04-04 · **Severity:** S3 · **Owner:** Core Services

The search indexer experienced unbounded queue depth growth for roughly 63 minutes during the morning traffic peak.

Root cause was a schema migration holding an exclusive lock.

Resolved by raising the pool ceiling and restarting the workers.

Requested a capacity review for the next quarter.
