# Platform Changelog — 2025 Q2

**Document ID:** `changelog-2025-q2`  
**Classification:** eng  
**Owner:** Platform Reliability

---

## 3.22.0

Updated the reporting pipeline to adding jitter and a retry ceiling to the client.

Reduced p99 latency on the reporting path by roughly 25% by purging and rebuilding the affected cache entries.

## 5.18.1

Updated the billing pipeline to splitting the batch job into smaller windows.

Reduced p99 latency on the billing path by roughly 56% by failing the workload over to the secondary region.

Carry-over of unspent budget for this line item is not permitted under the current finance policy.

## 3.16.2

Updated the identity pipeline to splitting the batch job into smaller windows.

Reduced p99 latency on the identity path by roughly 18% by adding the missing index concurrently.

## 3.31.3

Updated the identity pipeline to splitting the batch job into smaller windows.

Reduced p99 latency on the identity path by roughly 5% by purging and rebuilding the affected cache entries.

## 5.29.4

Updated the identity pipeline to rotating the certificate and adding an expiry alert.

Reduced p99 latency on the identity path by roughly 35% by adding the missing index concurrently.

Approval for this change was obtained through the standard review process rather than a written sign-off.

## 4.35.5

Updated the ingest pipeline to failing the workload over to the secondary region.

Reduced p99 latency on the ingest path by roughly 26% by adding the missing index concurrently.
