# AST-1202 — Extend stytch timeout window

<!-- linear-archive: AST-1202 archived 2026-08-14 -->

## Linear archive (AST-1202)

**Archived:** 2026-08-14  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1202/extend-stytch-timeout-window  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** susan  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Execution plan

1. **Dashboard max (Susan already did)** — Stytch Frontend SDK **max session duration** was **60**, so sessions hit a hard wall even while active. Susan raised it to **10,080** (7 days) on the test project. First verify on the test platform that active use no longer drops at ~60 min.
2. **Diagnose residual drop-offs** — If timeouts remain: separate **JWT (\~5 min)** refresh failures / project mismatch (`STYTCH_*` vs `VITE_STYTCH_PUBLIC_TOKEN`) from the **underlying session** clock. Leave backend `max_token_age_seconds=0` (AST-831) alone unless diagnosis proves it.
3. **Activity-driven extend (SPA, if still needed)** — No `stytch.session.authenticate({ session_duration_minutes })` on activity today; create-time `session_duration_minutes: 60` in Login / `stytchAuthenticateHandoff.ts` is still a wall from login unless Dashboard max + extend cooperate. On activity (debounced), call `session.authenticate` with **N ≥ 20, prefer 60**, so expiry resets from **now** (true inactivity window). Test-platform only per Susan.
4. **Single duration source** — One shared frontend constant (optional `VITE_` override for test) for Login, authenticate handoff, and keepalive — stop the duplicated 60s.
5. **Verify** — Active use past former 60-min wall stays signed in; after **\~60 min inactivity** (once SPA extend lands) → log-off path; smoke `/api/me` after JWT rollover. Light component tests only if keepalive surface needs them.

## Done when

* Test platform no longer kills active sessions at the old 60-min Dashboard cap (Susan's 10,080 change confirmed in practice).
* If SPA keepalive ships: **\~60 min inactivity** ends the session; activity keeps it alive (extend ≥20, prefer 60).
* Login + `/authenticate` (+ keepalive if added) share one duration source.
* AST-831 remote JWT validation unchanged unless explicitly required.

## Risks / open questions

* Is **60 min inactivity** the permanent product rule for **live** as well, or test-only for now?
  * **Answered (Susan):** test only.
* Prefer **activity-driven** extend only, or also a quiet interval while the tab stays open with no input?
  * **Answered (Susan):** activity-driven; extend the short window to **at least 20 minutes, preferably 60**.
* Dashboard max → 10,080 may already fix the “expires very quickly / at 60” symptom for active use; SPA keepalive is only required if we still want a **60-min inactivity** soft timeout under the longer Dashboard ceiling.
* Susan asked in comments to move this to **Done** after the Dashboard change — confirm after a quick live check, or Todo Chuckles if SPA keepalive is still wanted.

---

## Original brief

It seems like the stytch token expires very quickly.  How can we set it to refresh with activity and also not timeout for say, 60 minutes of inactivity, at least on the testing platform?

### Comments

#### susan — 2026-08-06T02:36:30.293Z
I figured it out.  The max session duration was set to 60 minutes, which I assume means active or not, so I kept hitting the session limit.  I updated the value to 10,080 (24 \* 7 \* 60).  We'll see if that sorts it.  Move this ticket to Done, please.

---

_Implementation detail may live in git history on `origin/dev`._
