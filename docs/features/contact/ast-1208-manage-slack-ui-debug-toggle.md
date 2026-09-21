<!-- linear-archive: AST-1208 archived 2026-08-17 -->

## Linear archive (AST-1208)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1208/manage-slack-ui-debug-toggle-need-to-be-able-to-set-the-debug-flag-for  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1203 — Need to be able to set the "Debug" flag for Slack messages  
**Blocked by / blocks / related:** parent: AST-1203

### Description

## What this implements

After foundation sibling: Manage Slack page shows Debug on/off beside listen, loads/saves via the admin API from foundation sibling, and does not alter listen or activity table behavior. No React debug-contract logging.

## Acceptance criteria

- [X] On Manage Slack, an admin can turn **Debug** on and off; after refresh or process restart on that environment, the page still shows the last saved Debug state.
- [X] Listen toggle, Estelle activity list, and non-prod reply prefix behavior are unchanged when toggling Debug.

## Boundaries

Does not own durable persist / core / admin API (foundation sibling) or Events ingress Style D wiring (Events sibling).

## In scope

- [X] `pattern.ui.admin-endpoint` — React calls existing thin admin GET/PUT `/api/admin/contact/debug` only
- [X] `astral.layers.ui-config-driven-business-logic` — UI renders/toggles resolved `debug_enabled`; no React-invented debug rules
- [X] `astral.patterns.require-auth-on-protected-endpoints` — uses shared `api()` client against `@require_admin` endpoints (no new routes)
- [X] `astral.ui.frontend-file-placement` / `astral.ui.naming-conventions` — edit existing `AdminManageSlack.tsx` only
- [X] `astral.standards.in-scope-only` — UI-only; no foundation/Events/listen-file edits
- [X] `astral.standards.debug-contract-gated` (UI clause) — no React debug-contract logging

## Considered but excluded

* `pattern.config.config-block` / durable JSON / core get-set — AST-1206 foundation (`src/utils/config.py`, `src/data/contact_debug.py`, `src/core/contact.py`, `src/ui/api/api_contact.py`)
* Events ingress Style D + `debug` pass-through — AST-1207
* Listen durable file / listen API behavior — AST-1067; must remain unchanged
* Estelle activity API / table columns — AST-1094; must remain unchanged
* `astral.standards.logging-via-utils` backend Style D — not a React concern on this ticket

## Notes for planning

After AST-1206. UI only.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1203-need-to-be-able-to-set-the-debug-flag-for-slack-messages`, child `sub/AST-1203/AST-1208-manage-slack-ui-debug-toggle`. Created at dispatch-parent.

### Comments

#### radia — 2026-08-06T06:14:40.915Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1208
**Publish ref:** `origin/sub/AST-1203/AST-1208-manage-slack-ui-debug-toggle` @ `428e2689d3e566dc1e96aba1bf33ae91bd785960`
**Overall:** CLEAN

## Plan adherence
- AST-1208's own commit (`8625077b`) touches only `AdminManageSlack.tsx` — single-file scope exactly per plan, no `api_contact.py`/core/data/config/listen/Events edits.
- Implements both Joan `[plan-discuss] round=1` fix-nows from the plan's Revisions log: isolated `.catch(() => null)` on the debug leg of `Promise.all` (so a debug network failure can't hide Listen/activity), and three-state status render (`—` / On / Off) instead of defaulting unknown to "Off".
- `toggleDebug` mirrors `toggleListen` structurally (shared `busy` flag, same toast conventions) without duplicating logic; no React debug-contract logging added (correct per §1.5.1 UI exception).

Full active statute corpus (65 leaves — 18 universal + 47 scoped) scored in-session against the full three-dot diff: zero fix-now, zero discuss.

**Notes:** The three-dot diff vs `origin/dev` also carries (a) the already Review-Posted AST-1206 foundation — expected, since AST-1208 is `blockedBy` AST-1206 and neither has landed on `dev` yet (already reviewed clean, not re-litigated here), and (b) two unrelated test commits (`test(AST-1212)`, `test(AST-1209)`) swept in by the single `merge-tests(AST-1208)` pull from the shared `origin/tests` tip — confined to `tests/` + `docs/test-bible/` only, no boundary violation. No separate Joan verdict attachment on the ticket; the plan doc's own `## Revisions` section documents round=1 inline.

**Pattern conformance:** `pattern.ui.admin-endpoint` cited — not a registered `canon/patterns/` id; covered by `astral.patterns.require-auth-on-protected-endpoints` (conforms — calls existing `@require_admin` endpoints via shared `api()`, no new routes).

## Frame diff
(none) — description AC/Boundaries/In-scope/Excluded checkboxes already reflect the shipped diff.

context_tokens≈8500

— Radia

#### betty — 2026-08-06T06:10:51.262Z
Tests Ready — Manage Slack Debug toggle (§6c).

**Publish:** `origin/sub/AST-1203/AST-1208-manage-slack-ui-debug-toggle` @ `428e2689`
**merge-tests:** `merge-tests(AST-1208): origin/tests 1d42f2938de63c42223399b4c0f4a0767cda2902`

## QA test manifest

1. `tests/component/frontend/pages/test_AdminManageSlack.test.tsx` — revised §6c suite:
   - first paint: Debug Off + `GET /api/admin/contact/debug` beside Listen
   - toggle PUT → Debug On + "Slack debug enabled"; Listen unchanged
   - debug load failure → status `—`, Debug button disabled, Listen + empty activity still shown
   - prior AST-1067/1094/1105 cases kept (listen assertions scoped — no ambiguous Off/On)

**Broken / obsolete (revised this pass):** default mocks missing `/debug` GET; `getByText("Off")` / `"On"` ambiguous once Debug shares the panel.

**Integration:** none asserting Manage Slack debug — no revision.

```bash
cd src/ui/frontend && npm run test:component -- AdminManageSlack
```

**Bible shasum** (`origin/sub/AST-1203/AST-1208-manage-slack-ui-debug-toggle`):
- `docs/test-bible/frontend/pages.md` `21c64838aa83922578f935bc69304efd31b5e2e7`

— Betty

#### joan — 2026-08-06T06:03:35.411Z
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1208
**Overall:** APPROVED
**Round:** 2 — round=1 REVISE, both fix-now items resolved
**Publish ref tip:** `sub/AST-1203/AST-1208-manage-slack-ui-debug-toggle` @ `de9d37b7`

**Considered:** full active corpus swept — 66 leaf statutes (18 universal + 48 scoped), scoped relevance matched on this child's ui/React + admin-endpoint predicates. Zero `violates`. Per-statute verdicts scored in-session (slim comment; no attachment).

## Round=1 fix-now items — both resolved

**fix-now 1 (debug leg could reject the mount `Promise.all`) — resolved.** Stage 1 step 2 now reads `api("/api/admin/contact/debug").catch(() => null)`, which puts the failure boundary on the one leg that needed it, and `null` is handled identically to `!ok`: toast only when a Response exists, `debugEnabled = null`, no page-level `error`. I checked that against the precedent the plan invokes and it is a true match — the activity leg at `AdminManageSlack.tsx:62-70` toasts and empties the table without ever touching `error`, so the render guard at `:151` (`!loading && !error && state`) keeps Listen and the @Estelle table on screen. Listen's own short-circuit at `:43-52` is untouched. Child AC2 / parent AC #5 are safe from this path now.

**fix-now 2 (unknown state rendered as "Off") — resolved.** The step 4 snippet is three-state, `{debugEnabled === null ? "—" : debugEnabled ? "On" : "Off"}`, so it now agrees with the prose bullet below it, and the button carries `disabled={busy || debugEnabled === null}`. An admin can no longer be told debug is off when we merely failed to read it.

## Traceability

AC1 (toggle + survives refresh/restart) → Stage 1 steps 1-4: mount `GET` seeds `debugEnabled`, `toggleDebug` `PUT`s `{debug_enabled}`, durability comes from the AST-1206 file I confirmed present on this ref (`src/core/contact.py:316` `slack_debug_enabled`, `CONTACT_CONFIG["debug_enabled"]` default `False` at `src/utils/config.py:1580`). AC2 (listen/activity/prefix unchanged) → step 2's isolation plus step 5's explicit no-change list. No unmapped AC, no orphan stage.

## Discuss — non-blocking, for the builder

**1. Guard the debug `.json()` the way the rest of the effect does.** The revision closes the rejection path at the `api()` boundary, but the parse is a second one: a bare `await debugRes.json()` on a 200 with an unparseable body would reject, land in the page `catch` at `:93`, and hide Listen + activity again. I am not calling this a fix-now because the plan says to follow the activity-failure pattern, and that pattern *is* the guarded form — every parse in this file already reads `.json().catch(() => ({} as Record<string, unknown>))` (`:42`, `:62`, `:118`). Worth writing the `.catch` into step 2 explicitly so the guarantee does not depend on the builder noticing the convention.

**2. Derive the three-state from the payload type, not `Boolean()`.** Step 2's ok-branch is `setDebugEnabled(Boolean(debugData.debug_enabled))`. Combined with a `{}` fallback from item 1, a missing or unreadable field becomes `false`, which renders "Off" — the same misleading label fix-now 2 removed, entering by a different door. `typeof debugData.debug_enabled === "boolean" ? debugData.debug_enabled : null` closes both. Note the listen precedent at `:55` / `:126` is bare `Boolean(...)`, but listen has no unknown state to represent, so that precedent does not carry here. Reachability is low (the foundation's `_debug_payload` always emits the bool), which is why this is discuss and not fix-now.

**3. `if (!cancelled)` around the new setters.** Every state write in the mount effect is guarded (`:47`, `:53`, `:67`, `:71`, `:95`, `:100`) so a fast unmount cannot write to a dead component. Step 2 describes setting `debugEnabled` on both branches without mentioning the guard; mirror it.

## Acceptable, noted so review is not surprised

- **Inline styles over `App.css`** — unchanged from my round=1 read: the whole panel including the Listen button is inline-styled, and converting the page is out of scope per `astral.standards.in-scope-only`.
- **Shared `busy`** — the Listen button at `:175` will also be disabled for the duration of a debug `PUT`. Strictly that is a transient change to listen while toggling Debug, but it is one request long, it keeps the page's single-mutator posture, and the plan names it as a decision rather than letting it happen silently.

Placement (Debug status after the Listen `<p>` at `:158-163` and before the prefix copy at `:164`; Debug button after the Listen button at `:173-184`, inside the same `maxWidth: 480` div), the separate `debugEnabled` state, the `debug_enabled` field name, Bearer via the shared `api()` client against `@require_admin`, and the no-React-debug-logging clause all check out against the file and the shipped foundation. Approved.

— Joan

context_tokens≈34000

#### katherine — 2026-08-06T06:00:12.160Z
[plan-discuss] round=1 reply

Both fix-now items landed on the plan tip.

1. **Debug isolation:** Stage 1 step 2 third `Promise.all` leg is now `api("/api/admin/contact/debug").catch(() => null)`; `null` treated like `!ok` (toast when Response exists, `debugEnabled = null`, no page-level `error`). Listen short-circuit unchanged.
2. **Null label:** Status snippet is three-state `{debugEnabled === null ? "—" : debugEnabled ? "On" : "Off"}` so unknown never reads as Off.

Publish: `origin/sub/AST-1203/AST-1208-manage-slack-ui-debug-toggle` @ `de9d37b7` — ## Revisions Revision 1.

Ready for round 2.

#### joan — 2026-08-06T05:58:22.557Z
[plan-discuss] round=1 concern

**Verdict: REVISE** — `plan-rubric.v1` on plan tip `2d50b017`, publish ref `origin/sub/AST-1203/AST-1208-manage-slack-ui-debug-toggle`.

The shape of this plan is right and I verified the premise the whole thing rests on: AST-1206 really has landed on `origin/ftr/AST-1203-…` and is contained in this publish ref (`src/core/contact.py:316` `slack_debug_enabled`, `api_contact.py:65` `"debug_enabled"`, GET/PUT under the `@require_admin` blueprint). The URL and field name in the plan match the shipped contract, the `AdminManageSlack.tsx` anchors the plan names all exist (`ListenState`, the 2-request mount `Promise.all`, `toggleListen`, `busy`, the `maxWidth: 480` panel, the Listen `<p>`/button, the toast-only activity failure path), and every statute in the ticket's In-scope list conforms — no new files or routes, Bearer via the shared `api()` client, no React-invented debug rules, no React debug-contract logging.

Two fix-now items, both in Stage 1's error handling, and both are places where the plan contradicts a guarantee it makes itself. Each remedy is one line.

---

**fix-now 1 — `Promise.all` cannot deliver the debug-failure isolation the plan promises (risks AC2).**

Stage 1 step 2 adds `api("/api/admin/contact/debug")` as a third element of the existing mount `Promise.all`, and then promises: "do not set page-level `error` / block Listen or the activity table." The prescribed mechanism cannot honor that. `api()` does not catch — it is `const response = await fetch(...)` with no try/catch (`src/ui/frontend/src/lib/api.ts:25`), so a network-level failure on the debug request *rejects*. `Promise.all` rejects with it, control lands in the page-level `catch`, which does `setError(msg)`, and the render guard `{!loading && !error && state && …}` then hides **both** the Listen controls and the @Estelle table. That is exactly the outcome child AC2 / parent AC #5 forbid ("Listen toggle, Estelle activity list … unchanged"), triggered by the new control the ticket is adding.

To be fair about blast radius: an HTTP 404/500 from `/debug` does *not* reject — `fetch` resolves with `ok: false`, so the plan's `!debugRes.ok` branch covers the deploy-skew case correctly. The exposed case is a debug-specific network/abort failure while listen succeeds. Narrow, but it is the one failure mode the plan explicitly claims to have handled, and it is the reason the isolation sentence is in the plan at all.

Give the debug request its own failure boundary so it can never reject the group, e.g. `api("/api/admin/contact/debug").catch(() => null)` as the third element (then treat `null` the same as `!ok`), or fetch debug in a separate `useEffect`. Either keeps listen's existing short-circuit semantics untouched.

**fix-now 2 — the step 4 snippet renders "Off" for the unknown state its own prose says must render "—".**

The JSX in step 4 is `{debugEnabled ? "On" : "Off"}`, which prints **Off** when `debugEnabled === null`. The bullet immediately below it says: "When `debugEnabled === null` (load failed), show the Debug status line as `—`." Those disagree, and a builder copying the code block ships the wrong one. The consequence is not cosmetic: it tells an admin that Slack debug is off on that environment when the truth is that we failed to read it and it may well be on — a misleading admin control on the exact page this epic exists to make trustworthy.

Make the snippet three-state so the code and the prose say the same thing:

```tsx
{debugEnabled === null ? "—" : debugEnabled ? "On" : "Off"}
```

---

**Noted, no action:** the plan adds inline `style={{…}}` objects rather than `src/App.css` classes. I read that as correct here — the entire panel including the adjacent Listen button is inline-styled, so matching the sibling control beats consistency with the stylesheet rule, and converting this page is out of scope per `astral.standards.in-scope-only`.

Everything else — Stage 1 placement ordering (Debug status after the Listen `<p>` and before the prefix copy; Debug button after the Listen button, mirroring how Listen's own status and button are already separated), the separate `debugEnabled` state rather than folding into `ListenState`, the shared `busy` flag, and the explicit no-change list in step 5 — checked out against the file and is sound. Fix the two items above and I expect this to approve on round 2.

— Joan

context_tokens≈21000

#### katherine — 2026-08-06T05:54:20.719Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1203/AST-1208-manage-slack-ui-debug-toggle/docs/features/contact/ast-1208-manage-slack-ui-debug-toggle.md

**Scope:** minor — one React admin page (`AdminManageSlack.tsx`); no API/core/data.

**Conf:** high — mirror of shipped listen toggle against landed AST-1206 `GET`/`PUT` `/api/admin/contact/debug` (`debug_enabled`).

**Risk:** low — debug load failures toast-only; listen + activity paths structurally unchanged.

---

# AST-1208 — Manage Slack UI Debug toggle

**Linear:** [AST-1208](https://linear.app/astralcareermatch/issue/AST-1208/manage-slack-ui-debug-toggle-need-to-be-able-to-set-the-debug-flag-for)  
**Parent:** [AST-1203](https://linear.app/astralcareermatch/issue/AST-1203/need-to-be-able-to-set-the-debug-flag-for-slack-messages) — Need to be able to set the "Debug" flag for Slack messages  
**Publish ref:** `origin/sub/AST-1203/AST-1208-manage-slack-ui-debug-toggle`

After AST-1206 foundation: Manage Slack shows a **Debug** on/off control beside Listen, loads and saves via admin `GET`/`PUT` `/api/admin/contact/debug`, and leaves listen + Estelle activity behavior unchanged. No React debug-contract logging.

**Depends on:** AST-1206 on `origin/ftr/AST-1203-need-to-be-able-to-set-the-debug-flag-for-slack-messages` (`GET`/`PUT` `/api/admin/contact/debug`, `debug_enabled` payload). Merge that tip before build (already on this publish-ref tip at plan time).

---

## UAT fitness

- **AC restored:** Parent AC #1 — "On Manage Slack, an admin can turn **Debug** on and off; after refresh or process restart on that environment, the page still shows the last saved Debug state." Parent AC #5 — "Listen toggle, Estelle activity list, and non-prod reply prefix behavior are unchanged when toggling Debug."
- **Correct outcome:** Admin sees Debug On/Off beside Listen; toggle persists across refresh (and across restart via foundation durable file); Listen controls and @Estelle activity table still load and behave as today.
- **Sibling check:** AST-1206 owns durable persist + admin API (already shipped on ftr — do not edit). AST-1207 owns Events/inbound Style D wire (do not edit). Verified by touching only `AdminManageSlack.tsx` and calling the existing `/debug` endpoints.
- **Not sufficient:** Removing a stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Hardcoding debug in React or inventing a second SoT; editing `api_contact.py` / core / data (foundation sibling); adding React Style D / debug-contract logging (§1.5.1 UI has no debug-logging requirement).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminManageSlack.tsx` | Load/save Debug beside Listen; keep activity table + listen path unchanged | ui |

No edits to `src/ui/api/api_contact.py`, `src/core/contact.py`, `src/data/contact_debug.py`, `src/utils/config.py`, Events ingress, listen durable file, Estelle activity API, or routes. Do **not** add React debug-contract logging.

---

## Stage 1: Manage Slack Debug toggle (UI only)

**Done when:** Admin Manage Slack shows Debug On/Off beside Listen; refresh shows the last saved `debug_enabled` from `GET /api/admin/contact/debug`; Listen toggle + @Estelle activity table behavior and API calls are unchanged.

1. In `src/ui/frontend/src/pages/AdminManageSlack.tsx`, add state for the durable debug flag parallel to listen (do **not** fold into `ListenState`):

```tsx
const [debugEnabled, setDebugEnabled] = useState<boolean | null>(null)
```

⚠️ **Decision — separate `debugEnabled` state, not a combined type:** Listen payload and debug payload are separate foundation endpoints. Keep types/state independent so a debug load failure cannot clear listen state (and vice versa for PUT). Environment / production copy stays sourced from the existing listen `state` only.

2. In the existing mount `useEffect` `Promise.all`, add a third request with its **own** rejection boundary so a debug network failure cannot reject the group and trip the page-level `catch` / `setError` (which would hide Listen + activity — AC2):

```tsx
api("/api/admin/contact/debug").catch(() => null),
```

⚠️ **Decision — `.catch(() => null)` on the debug leg only:** `api()` does not catch (`fetch` rejection = network/abort). Bare `Promise.all` would then hit the page `catch` and `setError`, blocking Listen/activity. Isolating debug keeps listen’s existing short-circuit semantics untouched.

Parse it after the listen success path (listen failure still short-circuits the page as today). On debug response:

- If `debugRes == null` **or** `!debugRes.ok`: toast the error when a Response exists (same pattern as activity load failure); always set `debugEnabled` to `null` — **do not** set page-level `error` / block Listen or the activity table.
- If ok: `setDebugEnabled(Boolean(debugData.debug_enabled))`.
- Ignore `environment` / `is_production` on the debug payload for display (listen remains the env label SoT on this page).

3. Add `toggleDebug` mirroring `toggleListen`:

- Guard: `if (debugEnabled === null || busy) return`
- `const next = !debugEnabled`
- `PUT /api/admin/contact/debug` with body `JSON.stringify({ debug_enabled: next })` and `Content-Type: application/json`
- On `!r.ok`: toast error; leave `debugEnabled` unchanged
- On ok: `setDebugEnabled(Boolean(data.debug_enabled))`; toast success `"Slack debug enabled"` / `"Slack debug disabled"`
- Share the existing `busy` flag with listen (disable both buttons while either PUT is in flight)

⚠️ **Decision — shared `busy`:** One in-flight admin mutator at a time on this page avoids interleaved listen/debug PUTs without inventing a second busy flag or changing listen’s disable semantics beyond “also disabled while debug PUT runs.”

4. In the controls panel (the `maxWidth: 480` block), immediately after the Listen On/Off `<p>` and **before** the production / non-production prefix copy, render Debug status + button beside the listen control visually (same column, immediately under Listen status):

```tsx
<p style={{ margin: "0 0 16px", fontSize: 14, color: "var(--text-secondary)" }}>
  Debug:{" "}
  <strong style={{ color: "var(--text-primary)" }}>
    {debugEnabled === null ? "—" : debugEnabled ? "On" : "Off"}
  </strong>
</p>
```

Place the Debug toggle button immediately after the existing Listen button (same panel):

```tsx
<button
  type="button"
  disabled={busy || debugEnabled === null}
  onClick={() => void toggleDebug()}
  style={{
    padding: "8px 14px",
    fontSize: 14,
    cursor: busy ? "wait" : "pointer",
    marginLeft: 8,
  }}
>
  {debugEnabled ? "Disable debug" : "Enable debug"}
</button>
```

When `debugEnabled === null` (load failed / unknown), the status line shows `—` (three-state, not `"Off"`) and the button stays disabled (Listen still usable).

5. Do **not** change: listen GET/PUT URLs or payload field `listen_enabled`; activity GET / table columns; env / non-prod prefix copy; toast / loading chrome beyond the additions above. Do **not** call `console.debug` / invent React Style D logging.

**Done when (recheck):** With foundation API live, Manage Slack shows Listen and Debug; Enable/Disable debug flips the label; full page refresh still shows the saved Debug state; Enable/Disable listen and the @Estelle table still work; network tab shows `GET`/`PUT` `/api/admin/contact/debug` only for the new control.

---

## Self-Assessment

**Scope:** `minor` — one React admin page file; no API/core/data/config.

**Conf:** `high` — literal mirror of the shipped listen toggle against the already-landed AST-1206 `/debug` contract (`debug_enabled` bool).

**Risk:** `low` — failure modes are toast-only for debug load; listen and activity paths stay structurally intact; wrong endpoint/field would be obvious in the network tab.

---

## Code rules check

| Rule | Plan compliance |
|------|-----------------|
| §1.5.1 UI/React debug | No React debug-contract logging added |
| §2.1 / config SoT | UI does not invent flag names; uses foundation `debug_enabled` |
| §2.9 / require_admin | Calls existing admin endpoints (Bearer via shared `api()`); no new routes |
| §3.2 UI thin | React only renders/toggles resolved state from API |
| §3.5 naming | Existing `AdminManageSlack.tsx` / `/admin/manage_slack` unchanged |
| §1.1 in-scope-only | No foundation / Events / listen-file edits |

---

## Revisions

Revision 1 — 2026-08-06
Driven by: Joan `[plan-discuss] round=1 concern` (REVISE) — fix-now 1 (`Promise.all` debug isolation) and fix-now 2 (null status must render `—`, not `Off`).
Changes: Stage 1 step 2 uses `api(.../debug).catch(() => null)` and treats `null` like `!ok`; step 4 status snippet is three-state `{debugEnabled === null ? "—" : debugEnabled ? "On" : "Off"}`.

---

## Review (build stub)

| Field | Value |
|-------|-------|
| Status | Code Complete |
| Publish ref | `origin/sub/AST-1203/AST-1208-manage-slack-ui-debug-toggle` |
| Tip | `8625077b` |
| Branch | `sub/AST-1203/AST-1208-manage-slack-ui-debug-toggle` |

Stage 1 landed: Manage Slack Debug beside Listen via admin `GET`/`PUT` `/api/admin/contact/debug` (`AdminManageSlack.tsx` only).

---

## Radia review

[code-rubric] revision=1

| Field | Value |
|-------|-------|
| Rubric | code-rubric.v1 |
| Publish ref tip | `428e2689d3e566dc1e96aba1bf33ae91bd785960` |
| Overall | CLEAN |

Full active statute corpus (65 leaves — 18 universal + 47 scoped) scored in-session against the full three-dot diff — zero `violates`, zero `needs-discussion`.

**AST-1208's own commit (`8625077b`) touches only `AdminManageSlack.tsx`** — matches the plan's single-file scope exactly, including both Joan `[plan-discuss] round=1` fix-nows (separate `.catch(() => null)` isolation on the debug `Promise.all` leg; three-state `—`/On/Off status render). No React debug-contract logging added (correct per §1.5.1 UI exception). No edits to `api_contact.py` / core / data / config / listen file / Events.

**Notes:** The three-dot diff vs `origin/dev` also carries (a) the already-reviewed, already Review-Posted AST-1206 foundation (expected — AST-1208 is `blockedBy` AST-1206 and neither has landed on `dev` yet), and (b) two unrelated test commits (`test(AST-1212)`, `test(AST-1209)`) swept in by the single `merge-tests(AST-1208)` pull from the shared `origin/tests` tip — both confined to `tests/` + `docs/test-bible/`, no product code, no boundary violation. No separate Joan verdict attachment on the ticket; the plan doc's own `## Revisions` section documents the round=1 concern and its resolution inline.

**Pattern conformance:** `pattern.ui.admin-endpoint` cited — not a registered `canon/patterns/` id; functionally covered by `astral.patterns.require-auth-on-protected-endpoints` (conforms — calls existing `@require_admin` endpoints via shared `api()`, no new routes).

## Frame diff
(none) — description AC/Boundaries/In-scope/Excluded checkboxes already reflect the shipped diff.

**What's solid:** `toggleDebug` mirrors `toggleListen` structurally (shared `busy` flag, same toast/error conventions) without duplicating logic. Debug load failure is isolated so it cannot mask Listen/activity load or trip the page-level error boundary — exactly the Joan-mandated isolation.

context_tokens≈8500

— Radia

---

## Resolution

2026-08-06 — Radia `[code-rubric] revision=1` **CLEAN** (zero fix-now, zero discuss). No product changes. Publish tip after resolve docs: see `resolve(AST-1208): — clean`.
