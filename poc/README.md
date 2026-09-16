# Proof-of-Concept material

PoC code in this repository is **deliberately bounded** and demonstrates the
documented issues on an **authorized device** only. Weaponized exploit
tooling is intentionally withheld while vendor coordination is in progress.

## Availability

| Advisory | PoC | Status |
|---|---|---|
| RC-0001 (session fixation) | — | Documented in the advisory; reproduction is a single crafted URL, no script required |
| RC-0002 (persistent XSS) | [`RC-0002/safe_validate_rc0002.py`](RC-0002/safe_validate_rc0002.py) | Inert validator published; language-pack builder **withheld** during coordination |
| RC-0003 (NEAP HMAC fail-open) | — | Withheld during coordination |
| RC-0005 (stats reset) | — | Withheld during coordination |
| RC-0006 (LLMNR OOB read) | — | Withheld during coordination |

## Usage policy

Only run this code against devices **you own or have explicit written
permission to test**. The validators enforce private, non-loopback targets
inside an explicit laboratory CIDR and refuse anything else.
