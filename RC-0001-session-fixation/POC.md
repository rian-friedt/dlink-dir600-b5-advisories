# RC-0001 — PoC: CRLF header injection → session fixation

**Policy:** documented, non-weaponized reproduction of the chain observed on
an owned device. Full exploit tooling is withheld during vendor coordination.

## Demonstrated chain

```text
unauthenticated CRLF response-header injection (REPORT parameter, /session.cgi)
-> attacker-selected uid cookie is set in the victim's browser
-> victim administrator login binds authorization to that (known) uid
-> reuse of the known uid obtains the authenticated web session
```

## Step by step (as observed)

1. **Inject.** An unauthenticated request supplies CRLF sequences (`%0D%0A`)
   inside the `REPORT` parameter of `/session.cgi`. Illustrative form
   (parameter position and encoding are the essential parts, not the exact
   byte string):

   ```http
   POST /session.cgi HTTP/1.1
   Host: <device>
   Content-Type: application/x-www-form-urlencoded

   REPORT=A%0D%0ASet-Cookie:%20uid=<ATTACKER-CHOSEN>;%20Path=/
   ```

2. **Observed:** the device's response contains a separate,
   attacker-controlled `Set-Cookie: uid=…; Path=/` header — the CRLF split
   the response header. The device does not rotate the `uid` on login.

3. **Fixation check (before login).** A request carrying the fixed cookie
   answered `Authenticate(-1, 600)` — unauthenticated, as expected.

4. **Victim login.** One authorized administrator login was performed on
   the owned device: `RESULT=SUCCESS`, `AUTHORIZED_GROUP=0`, and the
   response kept the pre-set `uid` (no rotation).

5. **Reuse.** A separate request with the attacker-known `uid` now answers
   `Authenticate(0, 600)` on the protected system page — the session is
   hijacked.

6. **Negative control.** A cookie chosen *after* login (not known to the
   attacker) remained `Authenticate(-1, 600)` — proving the effect comes
   from the pre-set identifier, not from a general auth bypass.

## Impact

An attacker who can make an administrator's browser follow the crafted
request (e.g. via a link from any co-located host) later reuses the known
`uid` to access the management interface with administrative privileges.

## Withheld

No ready-made delivery page or weaponized chain builder is published during
coordination. Reproduction requires an owned device.
