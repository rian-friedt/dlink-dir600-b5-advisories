# RC-0003 — NEAP Daemon HMAC Verification Fails Open (D-Link DIR-600 rev. B5)

- **CWE:** CWE-347 (Improper Verification of Cryptographic Signature — HMAC check fails open), leading to CWE-306 (Missing Authentication for Critical Function)
- **Product:** D-Link DIR-600 wireless router, hardware revision B5 — proprietary NEAP daemon (`neaps`, UDP port 64512)
- **Confirmed on:** firmware 2.11DE B06 (reproduced on owned hardware)
- **Affected range:** the `neaps` binary is **byte-identical** (SHA-256 `2cbad5eb…d6ba178`) across official B5 firmware 2.10 through 2.14 **and** in the vendor-recommended latest package 2.18b01 — all shipped B5 versions are affected
- **CVE:** requested 2026-09-15, pending
- **Severity (self-assessed):** Medium–High (unauthenticated access to a proprietary configuration-dispatch path; confirmed on a non-sensitive GET)

## Summary

The proprietary D-Link NEAP service (`neaps`, listening on **UDP/64512**)
protects its GET and SET operations with an HMAC over request attributes.
The verification logic **fails open**: when HMAC validation does not
succeed, request processing continues instead of being rejected. An
unauthenticated local-network attacker can therefore have NEAP requests
accepted and dispatched to the device's XMLDB configuration engine without
possessing the shared secret.

## Impact

- Cryptographic request authentication is effectively absent: the check
  exists in the code but its failure path grants access anyway
- Demonstrated on an owned device: a non-sensitive GET request without a
  valid HMAC was accepted and answered
- The dispatched engine (XMLDB) is the device's configuration store;
  deeper reach into sensitive nodes is plausible but **not claimed** here —
  the confirmed fact is the fail-open authentication boundary

## Attack prerequisites

- LAN-adjacent attacker; the NEAP port (UDP/64512) is reachable without
  authentication

## Mitigation / workarounds

- Block UDP/64512 at the network boundary toward untrusted hosts
- No vendor fix is available at the time of writing; the affected daemon is
  unchanged in the newest available firmware

## Disclosure timeline

| Date | Event |
|---|---|
| 2026-09-08 | Reported to D-Link via the regional (EU) security form |
| 2026-09-14 | Vendor acknowledgement received (merged support case, tier-1 response) |
| 2026-09-15 | Static verification: `neaps` byte-identical in vendor-recommended 2.18b01 — reported to vendor with escalation request; CVE ID requested from MITRE |
| pending | CVE assignment |
