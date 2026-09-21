# AST-1167 — Stytch session in a browser-extension context — validate and decide

<!-- linear-archive: AST-1167 archived 2026-08-14 -->

## Linear archive (AST-1167)

**Archived:** 2026-08-14  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1167/stytch-session-in-a-browser-extension-context-validate-and-decide  
**Status at archive:** Archive  
**Project:** Astral Surfer  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-1170

### Description

## Decision (AST-1167)

**Chosen:** Extension-owned Stytch B2C login on the **same Stytch project** as the web app. Service worker sends `Authorization: Bearer <session_jwt>` on every Astral call.

**Rejected:** Shared web-app session (cookie ride / `chrome.cookies` harvest). Cookie attachment from `chrome-extension://` is cross-site and needs `SameSite=None` backend work AST-1168 assumed unnecessary; depending on a web-app tab fails mid-batch. Joan/Archie preference: fewer moving parts + reliable mid-batch auth.

**Token homes:** `session_jwt` → `chrome.storage.session`; `session_token` → `chrome.storage.local` (refresh via Stytch `sessions.authenticate`). Absent/expired mid-batch → refresh; on failure pause batch + re-auth. No anonymous posts; web app need not be open.

**Backend deltas:** **none** for Bearer on the existing project (`src/ui/auth.py` already prefers Bearer; Stytch validation already wired).

**Proof host:** `https://astral-staging.up.railway.app` — `GET /api/me` no token **401**; Bearer **200**; after `sessions.revoke` Bearer **401**. Script + MV3 shell under local `debug/spikes/AST-1167/` (gitignored). No `src/` changes.

**Dependents (AST-1168 / AST-1170):** plan extension-owned login + SW Bearer only; do not scope CORS or cookie-policy work.

---

## Execution plan

1. **Map the live auth surface** — read `src/external/stytch.py`, `src/core/auth_bootstrap.py`, `src/ui/auth.py` (`Bearer` then `stytch_session_jwt` cookie), and any CORS / cookie-domain wiring. Note what an extension origin can already present vs what the web app presents today.
2. **Stytch + MV3 research** — check Stytch docs/SDK for Manifest V3: session sharing from the web app origin (cookies, `chrome.cookies`, content-script bridge, or Stytch “shared session” patterns) vs extension-owned login (popup/service worker + Stytch B2C + `chrome.storage`). Record what the SDK supports cleanly and what it forbids.
3. **Throwaway prototype under** `debug/` — minimal MV3 shell (no product paths): one path attempt for shared session, one for extension-owned login. Env-only Stytch public token / project id (`astral.config.secrets-and-env-specific-from-environ`). No `src/` product changes unless a one-line probe is unavoidable; revert those before Done.
4. **Prove the request path** — from the extension context, call one existing `@require_auth` Astral endpoint with the chosen token shape; confirm 200 with a valid session and 401 without. Note expiry/refresh when the candidate has not opened the web app recently, and mid-batch expiry behavior.
5. **Backend delta list** — for the winning pattern, name every backend change required (accepted token sources, CORS / cross-origin, cookie scope) so the extension-shell ticket can scope it. Flag stale Auth0 stub text in `docs/ASTRAL_CODE_RULES.md` §2.9 only if this work touches that doc.
6. **Write the decision** — chosen pattern, why the other was rejected, where the token lives, obtain/refresh/absent/expired behavior. If **both** patterns work cleanly → stop and `@susan` per `orch.pipeline.call-susan-for-product-decisions` (open question below); do not pick unilaterally.
7. **Cleanup** — leave only `debug/` artifacts + the written decision on this ticket; no product code left behind.

## Done when

* Written decision names the chosen pattern and why the other was rejected (or records Susan’s pick when both work).
* Decision states token location, obtain path, and expired/absent behavior (including mid-batch).
* Demonstrated authenticated request from an extension context succeeds; same request without a session is rejected.
* Decision lists every backend change the chosen pattern needs.
* Prototype lives under `debug/`; no product code left behind.

## Risks / open questions

* **Bearer is the target; cookie-sharing is the fallback that has to justify itself.** AST-1170 puts every extension network call in the service worker, where declared `host_permissions` make cross-origin fetches free — but that freedom applies to header auth. A cookie-borne session drags in cross-site cookie rules (`SameSite=None`, `Secure`, Chrome's third-party cookie behavior) and would add backend work the project otherwise avoids entirely. The win condition is a pattern that hands the extension a JWT it can send as `Authorization: Bearer`. If only the cookie path works, say so explicitly and enumerate the backend cost, because AST-1168 is currently scoped assuming no CORS or cookie work is needed.
* If both patterns work: prefer fewer moving parts (extension-owned login) or fewer candidate logins (shared session)? — Susan’s call.
* Shared-session may be blocked by cookie SameSite / host-only scope / HttpOnly + no `cookies` permission path from a pure extension origin; that alone can force extension-owned login.
* Extension-owned login still needs the same Stytch project and backend JWT acceptance — confirm no second user base is implied.
* Local vs Railway host differences for CORS and cookie domain — prototype must state which host was proven.

---

## Original brief

## Purpose

Astral Surfer's entire auth module shape rests on an unvalidated assumption: that a browser extension can ride Astral's existing Stytch session rather than inventing a separate login. Two integration patterns are plausible — the extension shares the session the web app already holds, or the extension runs its own Stytch-backed login on install and stores the resulting token in extension storage. They imply different code, different failure modes, and a different candidate-facing install experience. This is the project's one stated open item, and it gates the extension shell, so it gets resolved by a throwaway prototype before anything depends on the answer.

## Functional scope

* Confirm which of the two integration patterns Stytch's SDK actually supports cleanly from a Manifest V3 extension: sharing the web app's session, or an extension-owned Stytch login flow.
* Establish how the resulting token reaches an authenticated Astral request from an extension origin, and how expiry and refresh behave when the candidate has not opened the Astral web app recently.
* Confirm whether the existing backend token path accepts that token unchanged, or whether the accepted token sources have to change.
* Produce a written decision detailed enough that the extension shell can be planned against it: chosen pattern, where the token lives, refresh behavior, and what happens when the session expires mid-batch.

## Architectural definition

**Patterns to reuse:** `no established pattern applies` — no extension client exists today, and this ticket produces a decision rather than product shape.

**New patterns proposed:** none from the spike itself. The chosen pattern may deserve a catalog entry once the extension shell implements it — flag it for Archie then, not now.

**Applicable statutes:**

* `astral.config.secrets-and-env-specific-from-environ` — any Stytch public token or project id the prototype needs comes from environment, never committed.
* `astral.debug.spikes-under-debug-dir` — prototype artifacts live under `debug/`, not in `src/`.
* `astral.debug.no-repo-root-artifacts-dir` — no new top-level output directory.
* `orch.pipeline.call-susan-for-product-decisions` — if both patterns work, choosing between them is Susan's call, not the spike's.

**Notes for planning:** backend session validation is already Stytch (`src/external/stytch.py`, wired by `src/core/auth_bootstrap.py`), and `src/ui/auth.py` reads an `Authorization: Bearer` header first and falls back to the `stytch_session_jwt` cookie — so the shared-session pattern may already be partly supported. Note that `docs/ASTRAL_CODE_RULES.md` §2.9 still describes `require_auth` as an Auth0 stub; that text is stale and worth correcting if this work touches it.

## Boundaries

* Does not ship extension product code — the prototype is throwaway.
* Does not build the extension shell, popup, or service worker.
* Does not change the web app's login flow, and must not break it.
* Does not introduce a second user base, credential store, or auth provider.

## Acceptance criteria

1. A written decision names the chosen integration pattern and why the other was rejected.
2. The decision states where the session token lives, how the extension obtains it, and what the extension does when it is expired or absent.
3. A demonstrated request from an extension context to an authenticated Astral endpoint succeeds using the chosen pattern, and the same request without a session is rejected.
4. The decision names every backend change the chosen pattern requires (accepted token sources, cross-origin handling, cookie scope) so dependent tickets can scope that work instead of discovering it mid-implementation.
5. Prototype artifacts are under `debug/` and no product code is left behind.

## Dependencies and blockers

none.

## Open questions

1. If both patterns work, which do we prefer — fewer moving parts (extension-owned login) or fewer candidate logins (shared session)?
   **Answer (Joan):** Prefer extension-owned Stytch login (fewer moving parts / reliable mid-batch auth), not shared web-app session.

---

## Source

Derived from the **Astral Surfer** project description — see the project overview for the full narrative brief. This ticket resolves the brief's **Remaining open items**.

### Comments

#### chuckles — 2026-08-07T01:34:53.342Z
## Spike complete

**Decision:** extension-owned Stytch login (same project) + SW `Authorization: Bearer`. Shared-session rejected (cross-site cookie cost + mid-batch fragility). Backend deltas: **none**.

**Proof** on `https://astral-staging.up.railway.app`:
- `/api/me` no token → 401
- Bearer → 200
- after revoke → 401

Artifacts (local only, `debug/*` gitignored): `debug/spikes/AST-1167/{DECISION.md,prove_bearer.py,extension/}`.

No product code left behind.

— Chuckles

#### susan — 2026-08-07T01:15:35.049Z
@joan This is perfect.  Please reply in the description with your concise \`**Prefer extension-owned Stytch login (fewer moving parts / reliable mid-batch auth), not shared web-app session.**

#### joan — 2026-08-07T01:11:15.946Z
## Recommended answers (Joan judgment)

Archie asked for a concrete call — not another deferral.

### Open question 1 — if both patterns work, which?

**Prefer extension-owned Stytch login (fewer moving parts / reliable mid-batch auth), not shared web-app session.**

Concrete preference for dependents (AST-1170 / AST-1168):

1. **Same Stytch B2C project** as the web app — one user base, no second credential store.
2. **Login in the extension** (popup or install flow); store the session JWT in extension storage (`chrome.storage.session` preferred for the live token; `local` only if refresh material must survive SW death — spike decides which Stytch artifact needs which).
3. **Every authenticated call from the service worker** sends `Authorization: Bearer <session_jwt>` to Astral. Backend already prefers Bearer over the `stytch_session_jwt` cookie (`src/ui/auth.py`) — treat that as the contract; **do not** plan CORS / `SameSite=None` / third-party cookie work.
4. **Absent / expired mid-batch:** attempt Stytch refresh from extension-held session; if refresh fails, **pause the batch and surface re-auth** — do not invent anonymous posts and do not rely on a web-app tab still being open.
5. **Shared-session (cookie ride)** is the fallback that must justify itself. Use it in the spike only as a comparison. Accept it as the product choice **only if** it yields a JWT the SW can send as Bearer **without** cookie-scope / CORS backend deltas. If it only works as cookie-borne requests, **reject it** for shipping — that fights the AST-1168 assumption and Chrome’s third-party cookie trajectory.

Why not “fewer candidate logins” when both work:

* Manifest V3 workers die constantly; a cookie that only exists in the web-app origin is not a durable mid-batch credential.
* “One fewer login” is a one-time install UX win; “auth works after the laptop slept” is every-run correctness.
* Same Stytch project already keeps identity unified — extension login is not a second account.

### Risks (answers)

* **Bearer target / cookie fallback:** Agreed with the ticket framing. Spike proves Bearer from extension context first. Cookie path must enumerate backend cost explicitly if it “wins”; otherwise dependents stay Bearer-only.
* **SameSite / host-only / HttpOnly blocking shared session:** Treat as expected. That failure alone is sufficient to force extension-owned login — do not stretch the backend to unstick cookies.
* **Second user base:** Forbidden. Extension-owned login must use the existing Stytch project and existing `require_auth` JWT validation.
* **Local vs Railway:** Decision text must name the host that was proven. Prefer **Railway test / staging host** as the authoritative proof; call out local-only quirks separately so AST-1170 does not ship against a lie.

### Spike framing (so the written decision can land)

* Prove: extension context → Bearer → existing `@require_auth` endpoint = 200; no token = 401.
* Write: chosen pattern, reject reason for the other, token location, obtain/refresh/absent/expired (incl. mid-batch), backend delta list (expect **none** for Bearer on same project).
* Artifacts under `debug/` only.

Susan: override only if you want shared-session UX over mid-batch reliability; otherwise treat the above as the planning default.

— Joan

context_tokens≈12000

---

_Implementation detail may live in git history on `origin/dev`._
