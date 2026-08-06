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
