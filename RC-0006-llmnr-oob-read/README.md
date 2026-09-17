# RC-0006 — One-Byte Heap Out-of-Bounds Read in the LLMNR Responder (D-Link DIR-600 rev. B5)

- **CWE:** CWE-125 (Out-of-bounds Read — heap-based, one byte)
- **Product:** D-Link DIR-600 wireless router, hardware revision B5 — LLMNR responder daemon (`llmnresp`)
- **Confirmed on:** firmware 2.11DE B06 / 2.11WWb11 through 2.18 (`llmnresp` byte-identical in these images); firmware 2.10 contains a related binary classified as probably affected
- **Evidence type:** AddressSanitizer report on **unmodified vendor GPL source** (`rec_op.c`), compiled in isolation
- **CVE:** requested 2026-09-15, pending
- **Severity (self-assessed):** Low (memory-safety violation in a network-facing parser; DoS/infoleak not demonstrated and not claimed)

## Summary

The LLMNR responder in DIR-600 rev. B5 firmware receives each IPv4 UDP
datagram into a bounded **1472-byte** allocation but passes the
question-name parser **no received-length bound**. The vendor's
`get_name_size` routine (GPL source file `rec_op.c`) follows
attacker-controlled DNS label lengths until a zero label — without checking
the end of the datagram.

## Proof of concept

The unchanged parser helper was compiled in isolation with
AddressSanitizer:

- a **valid 25-byte LLMNR query** exits cleanly,
- a deterministic **1472-byte boundary query** triggers a **one-byte heap
  out-of-bounds read twelve bytes past the allocation**.

No fixed firmware is known. The demonstrable impact is the memory-safety
violation itself; denial of service on the device or information disclosure
was **not demonstrated and is not claimed**.

## Attack prerequisites

- A host able to send LLMNR (UDP/5355) datagrams to the device

## Mitigation / workarounds

- Filter LLMNR traffic toward embedded devices at the network boundary
- No vendor fix is available at the time of writing

## Disclosure timeline

| Date | Event |
|---|---|
| 2026-09-08 | Included in the regional (EU) submission context |
| 2026-09-14 | Vendor acknowledgement received (merged support case, tier-1 response) |
| 2026-09-15 | CVE ID requested from MITRE |
| pending | CVE assignment |
