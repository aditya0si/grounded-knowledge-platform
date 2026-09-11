# Platform Changelog — 2025 Q3

**Document ID:** `changelog-2025-q3`  
**Classification:** eng  
**Owner:** Platform Reliability

---

## 5.39.0

Updated the audit pipeline to splitting the batch job into smaller windows.

Reduced p99 latency on the audit path by roughly 45% by raising the pool ceiling and restarting the workers.

## 4.14.1

Updated the billing pipeline to failing the workload over to the secondary region.

Reduced p99 latency on the billing path by roughly 47% by rotating the certificate and adding an expiry alert.

## 3.33.2

Updated the identity pipeline to disabling the flag and re-enabling it for a smaller cohort.

Reduced p99 latency on the identity path by roughly 42% by purging and rebuilding the affected cache entries.

A postmortem was not required for this incident because the impact fell below the documented threshold.

## 3.38.3

Updated the exports pipeline to rotating the certificate and adding an expiry alert.

Reduced p99 latency on the exports path by roughly 36% by rolling back the offending release.

The uptime commitment for this component is reported monthly and excludes planned maintenance windows.

## 3.21.4

Updated the reporting pipeline to adding the missing index concurrently.

Reduced p99 latency on the reporting path by roughly 53% by raising the pool ceiling and restarting the workers.

Note that the escalation path for this service differs from the standard paging route and is documented by the owning team.

## 4.26.5

Updated the identity pipeline to purging and rebuilding the affected cache entries.

Reduced p99 latency on the identity path by roughly 14% by splitting the batch job into smaller windows.
