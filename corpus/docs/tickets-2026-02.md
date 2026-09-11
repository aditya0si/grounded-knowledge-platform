# Incident Tickets — February 2026

**Document ID:** `tickets-2026-02`  
**Classification:** all  
**Owner:** Core Services

---

## INC-71781

**Raised:** 2026-02-14 · **Severity:** S2 · **Owner:** Data Platform

The recommendation service experienced unbounded queue depth growth for roughly 127 minutes during the evening traffic peak.

Root cause was a certificate that expired without an alert firing.

Resolved by adding the missing index concurrently.

Requested a capacity review for the next quarter.

Related: ticket retention for this subsystem is tracked in a separate schedule and was not affected by this change.

## INC-71784

**Raised:** 2026-02-20 · **Severity:** S2 · **Owner:** Developer Experience

The metrics aggregator experienced unbounded queue depth growth for roughly 120 minutes during the night traffic peak.

Root cause was a bad rollout of the connection pooler.

Resolved by adding the missing index concurrently.

Filed a follow-up to introduce a canary stage for this service.

## INC-71787

**Raised:** 2026-02-07 · **Severity:** S1 · **Owner:** Security Engineering

The recommendation service experienced degraded throughput for roughly 43 minutes during the night traffic peak.

Root cause was a schema migration holding an exclusive lock.

Resolved by rotating the certificate and adding an expiry alert.

Reviewed the alert threshold, which was too noisy to act on.

## INC-71790

**Raised:** 2026-02-13 · **Severity:** S1 · **Owner:** Billing Systems

The metrics aggregator experienced degraded throughput for roughly 152 minutes during the night traffic peak.

Root cause was an unindexed query introduced by a recent release.

Resolved by disabling the flag and re-enabling it for a smaller cohort.

Filed a follow-up to introduce a canary stage for this service.

This change does not alter the classification of the data the service handles, which remains Internal.

## INC-71793

**Raised:** 2026-02-16 · **Severity:** S3 · **Owner:** Core Services

The document parser experienced disk pressure on the primary for roughly 122 minutes during the afternoon traffic peak.

Root cause was a configuration change that was not rolled out gradually.

Resolved by raising the pool ceiling and restarting the workers.

Filed a follow-up to introduce a canary stage for this service.

## INC-71796

**Raised:** 2026-02-24 · **Severity:** S1 · **Owner:** Security Engineering

The export worker experienced a growing backlog of unprocessed messages for roughly 13 minutes during the evening traffic peak.

Root cause was a schema migration holding an exclusive lock.

Resolved by purging and rebuilding the affected cache entries.

Scheduled a dependency upgrade for the next maintenance window.

## INC-71799

**Raised:** 2026-02-22 · **Severity:** S2 · **Owner:** Data Platform

The recommendation service experienced disk pressure on the primary for roughly 183 minutes during the morning traffic peak.

Root cause was an upstream dependency quietly raising its timeout.

Resolved by adding the missing index concurrently.

Added an integration test covering the failure path.

## INC-71802

**Raised:** 2026-02-21 · **Severity:** S2 · **Owner:** Platform Reliability

The session store experienced a growing backlog of unprocessed messages for roughly 116 minutes during the night traffic peak.

Root cause was a certificate that expired without an alert firing.

Resolved by splitting the batch job into smaller windows.

Filed a follow-up to introduce a canary stage for this service.

## INC-71805

**Raised:** 2026-02-10 · **Severity:** S2 · **Owner:** Platform Reliability

The document parser experienced repeated leader elections for roughly 124 minutes during the evening traffic peak.

Root cause was a configuration change that was not rolled out gradually.

Resolved by adding jitter and a retry ceiling to the client.

Documented the workaround in the service runbook.

Note that the escalation path for this service differs from the standard paging route and is documented by the owning team.

## INC-71808

**Raised:** 2026-02-26 · **Severity:** S3 · **Owner:** Identity

The metrics aggregator experienced unbounded queue depth growth for roughly 30 minutes during the night traffic peak.

Root cause was an upstream dependency quietly raising its timeout.

Resolved by rotating the certificate and adding an expiry alert.

Requested a capacity review for the next quarter.

Voting node membership was unchanged, so no split-brain risk was assessed for this event.

## INC-71811

**Raised:** 2026-02-03 · **Severity:** S1 · **Owner:** Security Engineering

The tenant provisioning worker experienced repeated leader elections for roughly 40 minutes during the night traffic peak.

Root cause was a certificate that expired without an alert firing.

Resolved by splitting the batch job into smaller windows.

Scheduled a dependency upgrade for the next maintenance window.

## INC-71814

**Raised:** 2026-02-13 · **Severity:** S3 · **Owner:** Billing Systems

The audit log pipeline experienced a slow memory leak in the worker pool for roughly 92 minutes during the morning traffic peak.

Root cause was a bad rollout of the connection pooler.

Resolved by rolling back the offending release.

Added a lint rule to catch the misconfiguration at review time.
