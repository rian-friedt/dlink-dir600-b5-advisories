# RC-0001 — Session Fixation via CRLF Header Injection in `session.cgi` (D-Link DIR-600 rev. B5)

- **CWE:** CWE-113 (HTTP Request/Response Splitting), leading to CWE-384 (Session Fixation)
- **Product:** D-Link DIR-600 wireless router, hardware revision B5 — web management interface
- **Confirmed on:** firmware 2.11DE B06 (reproduced on owned hardware)
- **Latest firmware 2.18b01:** `session.cgi` and its REPORT handling remain present (shared CGI binary rebuilt; session-handling strings unchanged — statically verified)
- **CVE:** requested 2026-09-15, pending
- **Severity (self-assessed):** High (LAN-adjacent, unauthenticated, leads to administrative access)

## Summary

The `session.cgi` endpoint of the DIR-600 rev. B5 web interface reflects
attacker-controlled data from the `REPORT` parameter into HTTP response
headers without neutralizing CRLF sequences. An unauthenticated LAN-adjacent
attacker can inject arbitrary response headers — including `Set-Cookie` — and
thereby fix a victim browser's session identifier (`uid` cookie) for the
management interface.

## Impact

When the victim subsequently authenticates, the attacker can reuse the
pre-set session identifier to access the device with the victim's
(administrative) privileges. No valid session or credentials are required
at attack time.

## Attack prerequisites

- Attacker on the same LAN segment as the victim's browser and the device
- Victim induced to follow a crafted link (the injection is carried in the
  URL's `REPORT` parameter; no authentication required)

## Novelty

This differs from previously published D-Link session-fixation records: the
injection point is the `REPORT` parameter of `session.cgi` (CRLF header
injection), not an attacker-chosen cookie accepted by design. Related but
distinct public records: CVE-2016-10405, D-Link SAP10151, CVE-2014-100005
(different root cause, different product/revision). No comparable public
record exists for the DIR-600 rev. B5.

## Mitigation / workarounds

- Do not expose the management interface to untrusted LAN clients
- Use a dedicated management VLAN / restrict access at Layer 2–3
- No vendor fix is available at the time of writing

## Disclosure timeline

| Date | Event |
|---|---|
| 2026-09-06 | Reported to D-Link via the US security report form |
| 2026-09-08 | Included in the regional (EU) submission |
| 2026-09-14 | Vendor acknowledgement received (merged support case, tier-1 response) |
| 2026-09-15 | Escalation to D-Link PSIRT requested; CVE ID requested from MITRE |
| pending | CVE assignment |
