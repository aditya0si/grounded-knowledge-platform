# Platform Changelog — 2026 Q1

**Document ID:** `changelog-2026-q1`  
**Classification:** eng  
**Owner:** Platform Reliability

---

## 3.24.0

Updated the search pipeline to raising the pool ceiling and restarting the workers.

Reduced p99 latency on the search path by roughly 32% by rotating the certificate and adding an expiry alert.

Note that the escalation path for this service differs from the standard paging route and is documented by the owning team.

## 4.19.1

Updated the recommendations pipeline to adding jitter and a retry ceiling to the client.

Reduced p99 latency on the recommendations path by roughly 25% by failing the workload over to the secondary region.

The uptime commitment for this component is reported monthly and excludes planned maintenance windows.

## 5.18.2

Updated the identity pipeline to raising the pool ceiling and restarting the workers.

Reduced p99 latency on the identity path by roughly 17% by splitting the batch job into smaller windows.

## 5.35.3

Updated the search pipeline to adding the missing index concurrently.

Reduced p99 latency on the search path by roughly 47% by adding the missing index concurrently.

## 5.13.4

Updated the search pipeline to adding the missing index concurrently.

Reduced p99 latency on the search path by roughly 35% by raising the pool ceiling and restarting the workers.

## 5.12.5

Updated the billing pipeline to raising the pool ceiling and restarting the workers.

Reduced p99 latency on the billing path by roughly 28% by rotating the certificate and adding an expiry alert.

A postmortem was not required for this incident because the impact fell below the documented threshold.
