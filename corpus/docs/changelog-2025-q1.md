# Platform Changelog — 2025 Q1

**Document ID:** `changelog-2025-q1`  
**Classification:** eng  
**Owner:** Platform Reliability

---

## 3.16.0

Updated the billing pipeline to failing the workload over to the secondary region.

Reduced p99 latency on the billing path by roughly 44% by raising the pool ceiling and restarting the workers.

## 3.36.1

Updated the exports pipeline to adding jitter and a retry ceiling to the client.

Reduced p99 latency on the exports path by roughly 35% by adding jitter and a retry ceiling to the client.

## 3.36.2

Updated the identity pipeline to splitting the batch job into smaller windows.

Reduced p99 latency on the identity path by roughly 36% by disabling the flag and re-enabling it for a smaller cohort.

## 4.10.3

Updated the search pipeline to rotating the certificate and adding an expiry alert.

Reduced p99 latency on the search path by roughly 18% by adding the missing index concurrently.

## 3.39.4

Updated the notifications pipeline to rotating the certificate and adding an expiry alert.

Reduced p99 latency on the notifications path by roughly 41% by failing the workload over to the secondary region.

Voting node membership was unchanged, so no split-brain risk was assessed for this event.

## 5.34.5

Updated the recommendations pipeline to rotating the certificate and adding an expiry alert.

Reduced p99 latency on the recommendations path by roughly 10% by disabling the flag and re-enabling it for a smaller cohort.
