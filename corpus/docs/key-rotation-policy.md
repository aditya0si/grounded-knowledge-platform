# Key Rotation Policy

**Document ID:** `key-rotation-policy`  
**Classification:** sec  
**Owner:** Security Engineering

---

## Rotation intervals

Service API keys must be rotated at least every 90 days.

Root account access keys must be rotated every 270 days and may not be used for programmatic access.

## Emergency rotation

A key suspected of exposure must be rotated immediately, regardless of its position in the rotation schedule.
