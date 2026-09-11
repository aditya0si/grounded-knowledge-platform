# Incident Tickets — September 2026

**Document ID:** `tickets-2026-09`  
**Classification:** eng  
**Owner:** Platform Reliability

---

## INC-88421

Elevated p99 latency on the ingest gateway traced to connection pool exhaustion. Resolved by raising the pool ceiling.

## INC-88455

Duplicate embeddings written after a retry storm. Required a full reindex of the affected tenant.

## INC-88490

Relevance regression reported by a customer following a chunking change. Traced to chunk boundaries splitting a pricing table.
