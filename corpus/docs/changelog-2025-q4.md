# Platform Changelog — 2025 Q4

**Document ID:** `changelog-2025-q4`  
**Classification:** eng  
**Owner:** Platform Reliability

---

## 3.11.0

Updated the identity pipeline to disabling the flag and re-enabling it for a smaller cohort.

Reduced p99 latency on the identity path by roughly 49% by failing the workload over to the secondary region.

## 3.10.1

Updated the audit pipeline to adding jitter and a retry ceiling to the client.

Reduced p99 latency on the audit path by roughly 51% by adding the missing index concurrently.

Note that the escalation path for this service differs from the standard paging route and is documented by the owning team.

## 4.36.2

Updated the identity pipeline to rotating the certificate and adding an expiry alert.

Reduced p99 latency on the identity path by roughly 53% by adding the missing index concurrently.

This change does not alter the classification of the data the service handles, which remains Internal.

## 3.12.3

Updated the exports pipeline to purging and rebuilding the affected cache entries.

Reduced p99 latency on the exports path by roughly 31% by purging and rebuilding the affected cache entries.

## 4.25.4

Updated the reporting pipeline to adding the missing index concurrently.

Reduced p99 latency on the reporting path by roughly 42% by rotating the certificate and adding an expiry alert.

## 5.30.5

Updated the audit pipeline to splitting the batch job into smaller windows.

Reduced p99 latency on the audit path by roughly 24% by splitting the batch job into smaller windows.

Voting node membership was unchanged, so no split-brain risk was assessed for this event.
