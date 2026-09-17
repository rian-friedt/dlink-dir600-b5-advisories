# RC-0002 — bounded validator

`safe_validate_rc0002.py` is the restoration-first validator used to verify
[RC-0002](README.md) on
an owned D-Link DIR-600 B5.

## What it does

1. Enforces the target to be a **private, non-loopback** address inside an
   explicit `--allowed-cidr` range (refuses anything else).
2. Requires the original verified inert marker language pack, checked
   against its known SHA-256 (`7a39e043…`), bounded at 512 KiB.
3. Uploads the inert marker pack (`rc0002=1` — a non-executing marker
   string, no payload) unauthenticated via the multipart endpoint.
4. Checks whether the marker is reflected by the management interface.
5. Restores the device's prior state afterwards.

## What is withheld

The **language-pack builder** (pack construction/packaging) is withheld
while vendor coordination is in progress. Without the pack artifact this
validator is inert by design.

## Usage

```text
python3 safe_validate_rc0002.py --help
```

The script prints its exact argument contract via `--help` and aborts on any
policy violation (target range, file size, artifact hash).
