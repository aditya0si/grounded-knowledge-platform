# Platform Changelog — 2026 Q3

**Document ID:** `changelog-2026-q3`  
**Classification:** eng  
**Owner:** Platform Reliability

---

## 4.34.0

Updated the reporting pipeline to raising the pool ceiling and restarting the workers.

Reduced p99 latency on the reporting path by roughly 58% by raising the pool ceiling and restarting the workers.

## 3.18.1

Updated the ingest pipeline to raising the pool ceiling and restarting the workers.

Reduced p99 latency on the ingest path by roughly 31% by failing the workload over to the secondary region.

Note that the escalation path for this service differs from the standard paging route and is documented by the owning team.

## 4.37.2

Updated the reporting pipeline to adding jitter and a retry ceiling to the client.

Reduced p99 latency on the reporting path by roughly 28% by purging and rebuilding the affected cache entries.

## 5.29.3

Updated the audit pipeline to rotating the certificate and adding an expiry alert.

Reduced p99 latency on the audit path by roughly 58% by disabling the flag and re-enabling it for a smaller cohort.

## 4.36.4

Updated the recommendations pipeline to rolling back the offending release.

Reduced p99 latency on the recommendations path by roughly 37% by rotating the certificate and adding an expiry alert.

## 5.18.5

Updated the notifications pipeline to raising the pool ceiling and restarting the workers.

Reduced p99 latency on the notifications path by roughly 6% by rotating the certificate and adding an expiry alert.
