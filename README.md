# D-Link DIR-600 rev. B5 — Security Research Advisories

Security research on the **D-Link DIR-600 wireless router, hardware revision B5**.
All findings were reproduced **only on an owned device** in an isolated laboratory
network and are disclosed following the principles of **coordinated disclosure**.

> **Status: CVE IDs pending.** CVE IDs were requested from MITRE (CNA of Last
> Resort) on **2026-09-15**. This repository is currently **private** and will be
> published once coordination allows. CVE identifiers will be added to the
> advisories as soon as they are assigned.

## Advisories

| ID | Title | CWE class | Affects latest firmware (2.18b01) | CVE |
|---|---|---|---|---|
| RC-0001 | Session fixation via CRLF header injection in `session.cgi` (REPORT) | CWE-113 → CWE-384 | Yes (statically verified) | pending |
| RC-0002 | Unauthenticated persistent cross-site scripting via language-pack upload | CWE-79 (CWE-345) | Yes (statically verified) | pending |
| RC-0003 | NEAP daemon (`neaps`, UDP/64512) HMAC verification fails open | CWE-347 → CWE-306 | Yes (binary byte-identical) | pending |
| RC-0005 | Unauthenticated traffic-statistics reset (`st_stats.php`) | CWE-306, CWE-471 | Yes | pending |
| RC-0006 | One-byte heap out-of-bounds read in LLMNR responder (`llmnresp`) | CWE-125 | Yes (binary byte-identical) | pending |

## Affected product

- **Product:** D-Link DIR-600 wireless router, hardware revision **B5**
- **Confirmed on:** firmware 2.11DE B06 (hardware testing)
- **Latest firmware:** 2.18b01 (distributed 2015-04-24) — affected components
  statically verified where noted; for RC-0003 and RC-0006 the affected daemon
  binaries are **byte-identical** across the official B5 firmware line.
- **Attack prerequisites:** all issues are reachable by an **unauthenticated
  LAN-adjacent attacker**. No issue in this set requires internet exposure of
  the management interface.

## Coordinated disclosure timeline

| Date | Event |
|---|---|
| 2026-09-06 – 2026-09-08 | Findings reported to D-Link via the vendor's security/reporting channels (US form and regional EU form) |
| 2026-09-14 | Vendor acknowledgement received (EU support portal; case merged, initial tier-1 response) |
| 2026-09-15 | Vendor reply filed: affected components verified statically against the vendor-recommended latest firmware (2.18b01); escalation to D-Link PSIRT requested |
| 2026-09-15 | CVE IDs requested from MITRE (CNA of Last Resort) for RC-0001, RC-0002, RC-0003, RC-0005, RC-0006 |
| pending | CVE assignment; vendor security-tier response; publication |

This repository will be updated as the process advances.

## Publication policy

- PoC material in [`poc/`](poc/) is **deliberately bounded**: it demonstrates
  the issues on an authorized device without providing a weaponized toolchain.
  Exploit primitive details are documented in the advisories.
- Two additional findings (NEAP heap-write candidate, UPnP `NewRemoteHost`
  rule omission) are **withheld**: they are pending runtime validation and are
  not part of this publication set.

## Responsible use

The provided code may only be used against devices **you own or have explicit
written permission to test**. The validators enforce private, non-loopback
target addresses inside an allowed laboratory range and refuse to run against
anything else.

## Contact

Rian Friedt — <rian.security@rian-friedt.de>
