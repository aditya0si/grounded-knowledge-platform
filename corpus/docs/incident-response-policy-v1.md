# Incident Response Policy

**Document ID:** `incident-response-policy-v1`  
**Version:** 1  
**Classification:** eng, sec  
**Owner:** Platform Reliability

---

## Retention

Incident tickets are retained for 180 days after closure, after which they are deleted from the incident management system.

Retention is counted from the moment an incident is marked resolved, not from the moment the page was raised.

## Severity definitions

Severity 1 incidents are defined as outages affecting more than 25% of customers in a single region.

Severity 2 incidents are defined as degraded performance affecting a single service tier without a full outage.

## Acknowledgement targets

Severity 1 incidents must be acknowledged by the on-call engineer within 10 minutes of the page being raised.

## Postmortems

A postmortem document must be published within 5 business days of a Severity 1 incident being resolved.
