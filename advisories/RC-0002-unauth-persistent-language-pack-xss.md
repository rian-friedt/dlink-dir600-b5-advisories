# RC-0002 — Unauthenticated Persistent XSS via Language-Pack Upload (D-Link DIR-600 rev. B5)

- **CWE:** CWE-79 (Cross-site Scripting); contributing: CWE-345 (Insufficient Verification of Data Authenticity)
- **Product:** D-Link DIR-600 wireless router, hardware revision B5 — web management interface (`seama.cgi` / SEALPAC language-pack path)
- **Confirmed on:** firmware 2.11DE B06 (reproduced on owned hardware)
- **Latest firmware 2.18b01:** unauthenticated language-pack handling present (statically verified)
- **CVE:** requested 2026-09-15, pending
- **Severity (self-assessed):** High (unauthenticated, persistent, no user interaction)

## Summary

The DIR-600 rev. B5 web management interface allows an **unauthenticated**
LAN-adjacent attacker to upload a crafted device language pack. The upload
path does not verify the authenticity of the pack and stores
attacker-controlled content **persistently** on the device. The uploaded
content is later served from the web interface **without neutralization**,
resulting in persistent (stored) cross-site scripting that executes in the
browser context of any user visiting the management interface.

## Impact

- Persistent JavaScript execution in the management interface context of
  every visitor — including the administrator
- No valid session, no credentials, and no victim interaction beyond
  visiting the interface are required at any point
- As the payload survives reboots (stored), a single upload provides a
  durable foothold in the browser context of the management UI

## Attack prerequisites

- Attacker reachable the device's LAN (unauthenticated; any host on the
  same network segment)

## PoC

[`poc/RC-0002/`](../poc/RC-0002/) contains a **bounded validator** used for
verification on an authorized device. It:

- enforces a private, non-loopback target inside an explicit laboratory CIDR,
- requires the original verified language-pack artifact (SHA-256-checked) and
  refuses to construct or ship the pack itself,
- uploads the inert marker pack, checks the reflected marker, and restores
  the device's prior state.

The language-pack builder and payload details are **withheld** while vendor
coordination is in progress.

## Mitigation / workarounds

- Do not expose the management interface to untrusted LAN clients
- Treat any DIR-600 B5 on a network with untrusted hosts as affected
- No vendor fix is available at the time of writing

## Disclosure timeline

| Date | Event |
|---|---|
| 2026-09-08 | Reported to D-Link via the regional (EU) security form |
| 2026-09-09 | Accidental duplicate submission (self-reported here for accuracy) |
| 2026-09-14 | Vendor acknowledgement received (merged support case, tier-1 response) |
| 2026-09-15 | Escalation to D-Link PSIRT requested; persistence in latest firmware statically verified; CVE ID requested from MITRE |
| pending | CVE assignment |
