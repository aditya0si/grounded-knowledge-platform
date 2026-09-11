# Incident Tickets — February 2025

**Document ID:** `tickets-2025-02`  
**Classification:** eng, sec  
**Owner:** Identity

---

## INC-70137

**Raised:** 2025-02-10 · **Severity:** S3 · **Owner:** Customer Engineering

The metrics aggregator experienced a growing backlog of unprocessed messages for roughly 77 minutes during the night traffic peak.

Root cause was a runaway batch job competing for I/O.

Resolved by rotating the certificate and adding an expiry alert.

Scheduled a dependency upgrade for the next maintenance window.

Voting node membership was unchanged, so no split-brain risk was assessed for this event.

## INC-70140

**Raised:** 2025-02-10 · **Severity:** S3 · **Owner:** Customer Engineering

The notification fanout experienced degraded throughput for roughly 184 minutes during the night traffic peak.

Root cause was a retry policy with no jitter and no ceiling.

Resolved by rotating the certificate and adding an expiry alert.

Requested a capacity review for the next quarter.

A postmortem was not required for this incident because the impact fell below the documented threshold.

## INC-70143

**Raised:** 2025-02-11 · **Severity:** S2 · **Owner:** Customer Engineering

The metrics aggregator experienced a growing backlog of unprocessed messages for roughly 21 minutes during the evening traffic peak.

Root cause was a runaway batch job competing for I/O.

Resolved by adding the missing index concurrently.

Filed a follow-up to introduce a canary stage for this service.

## INC-70146

**Raised:** 2025-02-07 · **Severity:** S2 · **Owner:** Platform Reliability

The billing reconciler experienced unbounded queue depth growth for roughly 71 minutes during the night traffic peak.

Root cause was a certificate that expired without an alert firing.

Resolved by disabling the flag and re-enabling it for a smaller cohort.

Added a saturation dashboard for the connection pool.

## INC-70149

**Raised:** 2025-02-06 · **Severity:** S3 · **Owner:** Platform Reliability

The document parser experienced a sharp rise in retry volume for roughly 82 minutes during the night traffic peak.

Root cause was a certificate that expired without an alert firing.

Resolved by rotating the certificate and adding an expiry alert.

Added a saturation dashboard for the connection pool.

## INC-70152

**Raised:** 2025-02-17 · **Severity:** S3 · **Owner:** Billing Systems

The session store experienced unbounded queue depth growth for roughly 156 minutes during the evening traffic peak.

Root cause was a runaway batch job competing for I/O.

Resolved by failing the workload over to the secondary region.

Documented the workaround in the service runbook.

## INC-70155

**Raised:** 2025-02-13 · **Severity:** S3 · **Owner:** Billing Systems

The notification fanout experienced connection pool exhaustion for roughly 47 minutes during the evening traffic peak.

Root cause was a schema migration holding an exclusive lock.

Resolved by raising the pool ceiling and restarting the workers.

Added a saturation dashboard for the connection pool.

The rotation schedule for the credentials involved was verified and found to be current.

## INC-70158

**Raised:** 2025-02-18 · **Severity:** S1 · **Owner:** Core Services

The audit log pipeline experienced repeated leader elections for roughly 98 minutes during the evening traffic peak.

Root cause was a feature flag enabled for a larger cohort than intended.

Resolved by adding jitter and a retry ceiling to the client.

Filed a follow-up to introduce a canary stage for this service.

## INC-70161

**Raised:** 2025-02-26 · **Severity:** S1 · **Owner:** Core Services

The export worker experienced timeouts against a downstream dependency for roughly 8 minutes during the night traffic peak.

Root cause was a bad rollout of the connection pooler.

Resolved by splitting the batch job into smaller windows.

Added a saturation dashboard for the connection pool.

## INC-70164

**Raised:** 2025-02-27 · **Severity:** S2 · **Owner:** Identity

The webhook dispatcher experienced connection pool exhaustion for roughly 168 minutes during the afternoon traffic peak.

Root cause was a cache key that collided across tenants.

Resolved by splitting the batch job into smaller windows.

Scheduled a dependency upgrade for the next maintenance window.

## INC-70167

**Raised:** 2025-02-15 · **Severity:** S3 · **Owner:** Customer Engineering

The document parser experienced connection pool exhaustion for roughly 176 minutes during the afternoon traffic peak.

Root cause was a retry policy with no jitter and no ceiling.

Resolved by adding the missing index concurrently.

Added a saturation dashboard for the connection pool.

Related: ticket retention for this subsystem is tracked in a separate schedule and was not affected by this change.

## INC-70170

**Raised:** 2025-02-08 · **Severity:** S3 · **Owner:** Security Engineering

The document parser experienced connection pool exhaustion for roughly 30 minutes during the night traffic peak.

Root cause was a certificate that expired without an alert firing.

Resolved by adding the missing index concurrently.

Added a lint rule to catch the misconfiguration at review time.
