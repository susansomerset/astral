# AST-1238 — Off-switch and pre-consent no-op

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1238/off-switch-and-pre-consent-no-op-consent-install-disclosure  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1173/consent-install-disclosure-affirmative-opt-in-and-off-switch  

**Publish ref (origin):** `sub/AST-1173/AST-1238-off-switch-and-pre-consent-no-op`  
**Parent integration ref:** `ftr/AST-1173-consent-install-disclosure-affirmative-opt-in-and-off-switch`

Ship the **findable Surfer off-switch** (Astral web + extension consent slice) plus the rule that **capture is a no-op until `is_current` is true on the server record**. Reuses AST-1235's `GET`/`PUT` `/api/candidates/<id>/surfer/consent` and `is_surfer_consent_current` — does not invent a second consent store. Parent AC4 (off-switch → extension no-ops) and the capture half of parent AC2 (nothing captured without affirmative opt-in) land here.

Boundaries (do **not** implement): disclosure copy / install opt-in chrome (**AST-1237**); consent record schema / opt-in-opt-out core API (**AST-1235**, already shipped); full extension Manifest/WXT shell / capture handlers (**AST-1170**); page_intake HTTP surface (**AST-1168** / AST-1228). Soft dependency: AST-1170 must wire this ticket's `src/ui/extension/consent/` gate into its background capture path when the shell lands.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend `SURFER_CONSENT_CONFIG` with off-switch / uninstall / capture-denied copy; assert new keys; add Candidate nav item | utils |
| `src/core/candidate.py` | `require_current_surfer_consent`; extend `surfer_consent_dto` with off-switch UI strings from config | core |
| `src/ui/frontend/src/pages/CandidateSurfer.tsx` | New Candidate > Surfer page: status, off-switch, uninstall guidance | ui |
| `src/ui/frontend/src/routes.tsx` | Route `candidate/surfer` → `CandidateSurfer` | ui |
| `src/ui/frontend/src/App.css` | Minimal Surfer page section styles (numbered section + TOC entry) | ui |
| `src/ui/extension/consent/gate.ts` | Pre-capture gate helper: allow only when consent DTO `is_current === true` | ui (extension consent slice) |
| `src/ui/extension/consent/offSwitch.ts` | Extension opt-out helper (`PUT` `action: opt_out`) + uninstall copy consumer | ui (extension consent slice) |
| `src/ui/extension/consent/WIRING.md` | Mandatory AST-1170 wiring notes (background gate + popup off-switch) | docs (extension slice) |

No new Flask routes (reuse AST-1235). No `tests/` / bible edits (Betty after Code Complete). Do **not** create WXT `package.json`, `wxt.config`, manifest, or capture handlers.

---

## Stage 1: Off-switch / uninstall copy on `SURFER_CONSENT_CONFIG`

**Done when:** `SURFER_CONSENT_CONFIG` exposes non-empty `off_switch_heading`, `off_switch_button_label`, `off_switch_confirm`, `status_off_label`, `status_on_label`, `uninstall_guidance`, and `capture_denied_message` strings; module asserts fail loudly if any are missing/blank; NAV has Candidate > Surfer.

1. In `src/utils/config.py`, inside the existing `SURFER_CONSENT_CONFIG` dict (after `default_status`), add:

```python
    # AST-1238: off-switch + uninstall guidance (web + extension; same server record).
    "off_switch_heading": "Astral Surfer",
    "off_switch_button_label": "Turn Surfer off",
    "off_switch_confirm": (
        "Turn Surfer off? The extension will stop capturing pages until you opt in again."
    ),
    "status_on_label": "Surfer is on — the extension may capture pages you choose.",
    "status_off_label": "Surfer is off — nothing will be captured.",
    "uninstall_guidance": (
        "To remove the extension entirely: open chrome://extensions, find Astral Surfer, "
        "and click Remove. Turning Surfer off here keeps the extension installed but idle."
    ),
    # Returned when a capture path refuses work without current consent (server authority).
    "capture_denied_message": (
        "Surfer is not enabled for this account. Turn it on from the extension disclosure "
        "or your Astral Surfer page before capturing pages."
    ),
```

2. After the existing `SURFER_CONSENT_CONFIG` asserts, add asserts that each new key is a non-empty `str` after strip.

3. In `NAV_CONFIG` under the Candidate group's `items` list, after Profile, add:

```python
{"label": "Surfer", "path": "/candidate/surfer"},
```

⚠️ **Decision:** Off-switch / uninstall / denied-capture copy live in `SURFER_CONSENT_CONFIG` (same block as disclosure version/copy from AST-1235), not a second config block and not hardcoded in React/extension. AST-1237 may refine `disclosure_copy`; this ticket owns the off-switch keys only.

---

## Stage 2: Core gate helper + DTO UI fields

**Done when:** `require_current_surfer_consent(candidate_id)` raises when consent is not current; `surfer_consent_dto` includes the Stage 1 UI strings; callers can enforce "no capture without opt-in" without reading config themselves.

1. In `src/core/candidate.py`, immediately after `is_surfer_consent_current`, add:

```python
def require_current_surfer_consent(candidate_id: str) -> dict:
    """Return the consent DTO when current; raise ValueError if capture must no-op."""
    dto = surfer_consent_dto(candidate_id)
    if not dto["is_current"]:
        raise ValueError(str(SURFER_CONSENT_CONFIG["capture_denied_message"]))
    return dto
```

2. Extend `surfer_consent_dto` return dict with these keys (values from `SURFER_CONSENT_CONFIG`):

   - `off_switch_heading`
   - `off_switch_button_label`
   - `off_switch_confirm`
   - `status_on_label`
   - `status_off_label`
   - `uninstall_guidance`
   - `capture_denied_message`

   Keep existing keys (`status`, `accepted_version`, `updated_at`, `current_version`, `disclosure_copy`, `is_current`) unchanged.

3. Do **not** call `require_current_surfer_consent` from the consent GET/PUT routes — those remain readable/writable without current consent (she must be able to opt out and to read status when off).

⚠️ **Decision:** Server authority for pre-consent no-op is `require_current_surfer_consent`. Every future Surfer capture entry (page_intake HTTP when AST-1228 lands; any batch ingest that creates jobs from extension pages) **must** call this helper before creating work. This ticket does not invent those routes — they are absent on this branch. The helper is the enforceable contract; client gates are defense in depth.

⚠️ **Decision:** Gate on `is_current` (opted_in **and** matching `current_version`), not merely `status == opted_in`, so a disclosure version bump (AST-1235 re-consent rule) also no-ops capture until she affirms again. Opt-in UI remains AST-1237.

---

## Stage 3: Astral web off-switch (`CandidateSurfer`)

**Done when:** Authenticated Candidate > Surfer page loads consent via GET, shows on/off status from `is_current`, offers Turn Surfer off when status is `opted_in` (including stale version), PUTs `action: opt_out` on confirm, and always shows `uninstall_guidance` from the DTO. No disclosure / opt-in chrome.

1. Create `src/ui/frontend/src/pages/CandidateSurfer.tsx`:

   - Use `useCandidate()` for `selectedId` (same pattern as `CandidateProfile.tsx`).
   - If no `selectedId`, render a short empty state: "Select a candidate."
   - On `selectedId` change, `GET /api/candidates/${selectedId}/surfer/consent` via `api()`; on failure toast error (reuse `ApiError` / `errorToastFromApiError` / `readApiError` from `toastDiagnostics`).
   - Type the DTO fields this page reads: `status`, `is_current`, `off_switch_heading`, `off_switch_button_label`, `off_switch_confirm`, `status_on_label`, `status_off_label`, `uninstall_guidance`.
   - Heading: `off_switch_heading` from DTO.
   - Status line: if `is_current` → `status_on_label`; else → `status_off_label`.
   - Off-switch button: render **only** when `status === "opted_in"` (she can turn off even if version is stale). Label = `off_switch_button_label`. On click, `window.confirm(off_switch_confirm)`; if confirmed, `PUT` same path with body `{"action":"opt_out"}`, then refresh DTO and success toast "Surfer turned off".
   - Always render `uninstall_guidance` below (whitespace-preserving / multi-line OK via CSS `white-space: pre-wrap`).
   - Do **not** render `disclosure_copy`, opt-in buttons, or version bump prompts — AST-1237 owns those.

2. In `src/ui/frontend/src/routes.tsx`, import `CandidateSurfer` and add under the Candidate routes block:

```tsx
{ path: "candidate/surfer", element: <CandidateSurfer /> },
```

3. In `src/ui/frontend/src/App.css`, add a small numbered section (update the TOC comment) for `.surfer-page` / `.surfer-page-status` / `.surfer-page-uninstall` — match existing page spacing patterns; no new design system.

⚠️ **Decision:** Web off-switch is a dedicated Candidate nav page (`/candidate/surfer`), not buried only on Profile. Parent required a place she would actually look later; Candidate group matches Profile / Intake.

---

## Stage 4: Extension consent slice (gate + off-switch helpers)

**Done when:** `src/ui/extension/consent/` contains gate + off-switch TypeScript helpers and `WIRING.md` that AST-1170 must follow; no WXT scaffold invented here.

1. Create directory `src/ui/extension/consent/` (first product files under `extension/` — AST-1170 still owns Manifest/WXT/`package.json`/entrypoints).

2. Create `src/ui/extension/consent/gate.ts`:

   - Export type `SurferConsentDto` with at least `is_current: boolean` and `capture_denied_message: string`.
   - Export `function mayCapture(dto: SurferConsentDto): boolean` returning `dto.is_current === true`.
   - Export `async function fetchConsent(apiBase: string, candidateId: string, authHeader: string): Promise<SurferConsentDto>` that `fetch`es `GET ${apiBase}/api/candidates/${candidateId}/surfer/consent` with `Authorization: Bearer ${authHeader}` (and `credentials: "omit"` — extension Bearer, not cookie), parses JSON, throws on non-OK.
   - Export `async function assertMayCapture(...): Promise<SurferConsentDto>` — fetch then if `!mayCapture(dto)` throw `Error(dto.capture_denied_message)`.

3. Create `src/ui/extension/consent/offSwitch.ts`:

   - Export `async function optOutSurfer(apiBase, candidateId, authHeader): Promise<SurferConsentDto>` — `PUT` same path with `Content-Type: application/json`, body `JSON.stringify({ action: "opt_out" })`, Bearer auth; return parsed DTO; throw on non-OK.
   - Do not hardcode button labels — callers render from the DTO fields added in Stage 2.

4. Create `src/ui/extension/consent/WIRING.md` with exactly these mandatory AST-1170 requirements (builder of 1170 must not skip):

   - Background (or whatever context owns network): before any page_intake / capture POST, call `assertMayCapture`; on throw, show the error message via the toast primitive and **do not** POST capture.
   - Popup / action UI: when consent `status === "opted_in"`, show off-switch using DTO labels; on confirm call `optOutSurfer`; after success, subsequent captures must no-op via the gate.
   - Always re-check server before capture — local storage is not authority.
   - Do not duplicate consent API paths; import these helpers.

⚠️ **Decision:** Soft dependency on AST-1170. This ticket lands the **consent slice** under the settled path `src/ui/extension/` (Susan-approved placement on AST-1170) without building the shell. If at **build-child** time `src/ui/extension/` already has WXT entrypoints, additionally wire `assertMayCapture` into the existing capture handler and mount the off-switch in the existing popup — stop and comment on the parent only if those entry files exist but their shapes do not match this plan's assumptions (do not invent a second popup framework).

⚠️ **Decision:** Extension TypeScript here is source for AST-1170's bundler. Do not add a second frontend build, Vitest project, or gitignore rows in this ticket — AST-1170 owns toolchain.

---

## Self-Assessment

**Scope:** Single-Component — frontend Surfer page + thin core helper/DTO extension + extension consent-slice helpers; no new HTTP API and no schema migration.

**Conf:** Medium — AST-1235 API and DTO patterns are known; AST-1170 shell is still Discussion so extension AC4 is delivered as a wire-ready slice plus WIRING.md rather than a loadable popup, which is the soft-dep the ticket already names.

**Risk:** Medium — a wrong `is_current` gate would either block legitimate capture or allow capture without consent; web opt-out bugs would leave Surfer "on" after she thinks she turned it off. Server helper + shared DTO reduce drift between web and extension.

---

## CODE_RULES self-review

- **§1.3 DRY:** Reuses AST-1235 GET/PUT and `is_surfer_consent_current`; no parallel consent store.
- **§2.1 config:** Off-switch / uninstall / denied messages in `SURFER_CONSENT_CONFIG`; no hardcoded sets in UI.
- **§2.4 batch / §2.6 state machine:** N/A — no batch claim, no `CANDIDATE_STATES` change.
- **§3.3 imports:** Core helper stays in `candidate.py`; UI calls HTTP only; extension consent slice does not import Python.
- **§3.5 naming / placement:** `CandidateSurfer.tsx`, route `candidate/surfer`, nav label Surfer; extension consent under `src/ui/extension/consent/` per AST-1170 placement settlement.
- **§1.1 in-scope-only:** No disclosure UI (1237), no WXT shell (1170), no page_intake route (1168).
