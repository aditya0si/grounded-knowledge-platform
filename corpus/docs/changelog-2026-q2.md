# Platform Changelog — 2026 Q2

**Document ID:** `changelog-2026-q2`  
**Classification:** eng  
**Owner:** Platform Reliability

---

## 4.18.0

Introduced connection pooler support for the read replica path. This release reduced failover duration by roughly half.

## 4.19.0

Added structured logging for escalation events and a dashboard for unacknowledged pages.

## 4.20.0

Deprecated the legacy vector ingestion endpoint. It returns HTTP 410 as of this release and will be removed in 5.0.0.
