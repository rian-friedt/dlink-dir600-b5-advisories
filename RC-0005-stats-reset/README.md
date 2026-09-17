# RC-0005 — Unauthenticated Traffic-Statistics Reset (D-Link DIR-600 rev. B5)

- **CWE:** CWE-306 (Missing Authentication for Critical Function); impact class CWE-471 (Modification of Assumed-Immutable Data)
- **Product:** D-Link DIR-600 wireless router, hardware revision B5 — web management interface (`st_stats.php`)
- **Confirmed on:** firmware 2.11DE B06 (reproduced twice on owned hardware with target-only packet captures)
- **Affected range:** vulnerable semantics present in all locally analyzed B5 images from 2.10WWb06 through 2.18
- **CVE:** requested 2026-09-15, pending
- **Severity (self-assessed):** Low–Medium (integrity of monitoring data only; no control-plane access)

## Summary

The DIR-600 rev. B5 web interface exposes a traffic-statistics reset action
that can be invoked **without authentication**. A cookie-free POST request
to `/st_stats.php` containing any nonempty `act` value selects a
server-side branch that resets the volatile WAN, LAN, and Wi-Fi packet
counters by writing the corresponding XMLDB statistics/reset nodes.

## Impact

An unauthenticated local-network attacker can repeatedly clear the interface
statistics, degrading traffic monitoring, accounting, and anomaly visibility
for the operator. Notably, the web UI renders an **authentication-failure
message while the reset is still performed** — the error output masks the
successful action, which makes the behavior easy to misread as harmless.

## Attack prerequisites

- LAN-adjacent attacker; no credentials, cookies, or CSRF token required

## Mitigation / workarounds

- Restrict management-interface access at the network layer
- No vendor fix is available at the time of writing

## Disclosure timeline

| Date | Event |
|---|---|
| 2026-09-08 | Included in the regional (EU) submission context |
| 2026-09-14 | Vendor acknowledgement received (merged support case, tier-1 response) |
| 2026-09-15 | CVE ID requested from MITRE |
| pending | CVE assignment |
