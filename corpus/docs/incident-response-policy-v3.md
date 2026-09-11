# Incident Response Policy

**Document ID:** `incident-response-policy-v3`  
**Version:** 3  
**Supersedes:** `incident-response-policy-v2`  
**Classification:** eng, sec  
**Owner:** Platform Reliability

---

## Retention

Incident tickets are retained for 400 days after closure, after which they are deleted from the incident management system.

Retention is measured from the moment an incident is marked resolved rather than from the moment the page was raised.

## Severity definitions

Severity 1 incidents are defined as outages affecting more than 20% of customers across all regions.

Severity 2 incidents are defined as degradation affecting one service tier without a full outage.

## Acknowledgement targets

Severity 1 incidents must be acknowledged by the on-call engineer within 15 minutes of the page being raised.

## Postmortems

A postmortem document must be published within 2 business days of a Severity 1 incident being resolved.
