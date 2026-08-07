# AST-1238 — Off-switch and pre-consent no-op

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1238/off-switch-and-pre-consent-no-op-consent-install-disclosure  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1173/consent-install-disclosure-affirmative-opt-in-and-off-switch  

**Publish ref (origin):** `sub/AST-1173/AST-1238-off-switch-and-pre-consent-no-op`  
**Parent integration ref:** `ftr/AST-1173-consent-install-disclosure-affirmative-opt-in-and-off-switch`

Ship the **findable Surfer off-switch** (Astral web + extension consent helpers) plus the rule that **capture is a no-op until `is_current` is true on the server record**. Reuses AST-1235's `GET`/`PUT` `/api/candidates/<id>/surfer/consent` and `is_surfer_consent_current` — does not invent a second consent store. Parent AC4 (off-switch → extension no-ops) and the capture half of parent AC2 (nothing captured without affirmative opt-in) land here.

Boundaries (do **not** implement): disclosure copy / install opt-in chrome (**AST-1237**); consent record schema / opt-in-opt-out core API (**AST-1235**, already shipped); full extension Manifest/WXT shell / capture handlers (**AST-1170**); page_intake HTTP surface (**AST-1168** / AST-1228). Soft dependency: AST-1170 must wire this ticket's helpers under `src/ui/extension/src/lib/` into its background capture path when the shell lands.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend `SURFER_CONSENT_CONFIG` with off-switch / uninstall / capture-denied / stale-status copy; assert new keys; add Candidate nav item | utils |
| `src/core/candidate.py` | `require_current_surfer_consent`; extend `surfer_consent_dto` with off-switch UI strings from config | core |
| `src/ui/frontend/src/pages/CandidateSurfer.tsx` | New Candidate > Surfer page: status, off-switch, uninstall guidance | ui |
| `src/ui/frontend/src/routes.tsx` | Route `candidate/surfer` → `CandidateSurfer` | ui |
| `src/ui/frontend/src/App.css` | Minimal Surfer page section styles (numbered section + TOC entry) | ui |
| `src/ui/extension/src/lib/surferConsentGate.ts` | Pre-capture gate helper: allow only when consent DTO `is_current === true` | ui (extension lib) |
| `src/ui/extension/src/lib/surferOffSwitch.ts` | Extension opt-out helper (`PUT` `action: opt_out`) | ui (extension lib) |
| `docs/features/surfer/ast-1238-extension-consent-wiring.md` | Mandatory AST-1170 wiring notes (background gate + popup off-switch) | docs |

No new Flask routes (reuse AST-1235). No `tests/` / bible edits (Betty after Code Complete). Do **not** create WXT `package.json`, `wxt.config`, manifest, or capture handlers.

---

## Stage 1: Off-switch / uninstall copy on `SURFER_CONSENT_CONFIG`

**Done when:** `SURFER_CONSENT_CONFIG` exposes non-empty `off_switch_heading`, `off_switch_button_label`, `off_switch_confirm`, `status_off_label`, `status_on_label`, `status_stale_label`, `uninstall_guidance`, and `capture_denied_message` strings; module asserts fail loudly if any are missing/blank; NAV has Candidate > Surfer.

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
    # opted_in but accepted_version != current_version (AST-1235 re-consent).
    "status_stale_label": (
        "Surfer was on under an older disclosure — capture is paused until you opt in "
        "again from the extension. You can also turn Surfer off below."
    ),
    "uninstall_guidance": (
        "To remove the extension entirely: open chrome://extensions, find Astral Surfer, "
        "and click Remove. Turning Surfer off here keeps the extension installed but idle."
    ),
    # Returned when a capture path refuses work without current consent (server authority).
    # Opt-in lives on the extension disclosure (AST-1237) — not on Candidate > Surfer.
    "capture_denied_message": (
        "Surfer is not enabled for this account. Turn it on from the extension disclosure "
        "before capturing pages."
    ),
```

2. After the existing `SURFER_CONSENT_CONFIG` asserts, add asserts that each new key is a non-empty `str` after strip.

3. In `NAV_CONFIG` under the Candidate group's `items` list, after Profile, add:

```python
{"label": "Surfer", "path": "/candidate/surfer"},
```

⚠️ **Decision:** Off-switch / uninstall / denied-capture / stale-status copy live in `SURFER_CONSENT_CONFIG` (same block as disclosure version/copy from AST-1235), not a second config block and not hardcoded in React/extension. AST-1237 may refine `disclosure_copy`; this ticket owns the off-switch keys only.

⚠️ **Decision:** `capture_denied_message` points only at the extension disclosure (AST-1237). Candidate > Surfer is an off-switch / status page and must not claim it can turn Surfer on.

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
   - `status_stale_label`
   - `uninstall_guidance`
   - `capture_denied_message`

   Keep existing keys (`status`, `accepted_version`, `updated_at`, `current_version`, `disclosure_copy`, `is_current`) unchanged.

3. Do **not** call `require_current_surfer_consent` from the consent GET/PUT routes — those remain readable/writable without current consent (she must be able to opt out and to read status when off).

⚠️ **Decision:** Server authority for pre-consent no-op is `require_current_surfer_consent`. Every future Surfer capture entry (page_intake HTTP when AST-1228 lands; any batch ingest that creates jobs from extension pages) **must** call this helper before creating work. This ticket does not invent those routes — they are absent on this branch. The helper is the enforceable contract; client gates are defense in depth. See `docs/features/surfer/ast-1238-extension-consent-wiring.md` for the self-check AST-1170 / AST-1228 must leave in place.

⚠️ **Decision:** Gate on `is_current` (opted_in **and** matching `current_version`), not merely `status == opted_in`, so a disclosure version bump (AST-1235 re-consent rule) also no-ops capture until she affirms again. Opt-in UI remains AST-1237.

---

## Stage 3: Astral web off-switch (`CandidateSurfer`)

**Done when:** Authenticated Candidate > Surfer page loads consent via GET, shows on / off / stale status without contradiction, offers Turn Surfer off when status is `opted_in` (including stale version) via `useUserConfirm`, PUTs `action: opt_out` on confirm, and always shows `uninstall_guidance` from the DTO. No disclosure / opt-in chrome.

1. Create `src/ui/frontend/src/pages/CandidateSurfer.tsx`:

   - Use `useCandidate()` for `selectedId` (same pattern as `CandidateProfile.tsx`).
   - `const confirm = useUserConfirm()` from `../components/UserPrompt` (`UserPromptProvider` is already mounted in `NavigationShell`).
   - If no `selectedId`, render a short empty state: "Select a candidate."
   - On `selectedId` change, `GET /api/candidates/${selectedId}/surfer/consent` via `api()`; on failure toast error (reuse `ApiError` / `errorToastFromApiError` / `readApiError` from `toastDiagnostics`).
   - Type the DTO fields this page reads: `status`, `is_current`, `off_switch_heading`, `off_switch_button_label`, `off_switch_confirm`, `status_on_label`, `status_off_label`, `status_stale_label`, `uninstall_guidance`.
   - Heading: `off_switch_heading` from DTO.
   - Status line (exactly one):
     - if `is_current` → `status_on_label`
     - else if `status === "opted_in"` → `status_stale_label` (opted in at an older disclosure; capture paused)
     - else → `status_off_label`
   - Off-switch button: render **only** when `status === "opted_in"` (she can turn off even if version is stale). Label = `off_switch_button_label`. Click handler is **async**: `if (!(await confirm(dto.off_switch_confirm))) return;` then `PUT` same path with body `{"action":"opt_out"}`, then refresh DTO and success toast "Surfer turned off". Do **not** use `window.confirm`.
   - Always render `uninstall_guidance` below (whitespace-preserving / multi-line OK via CSS `white-space: pre-wrap`).
   - Do **not** render `disclosure_copy`, opt-in buttons, or version bump prompts — AST-1237 owns those.

2. In `src/ui/frontend/src/routes.tsx`, import `CandidateSurfer` and add under the Candidate routes block:

```tsx
{ path: "candidate/surfer", element: <CandidateSurfer /> },
```

3. In `src/ui/frontend/src/App.css`, add a small numbered section (update the TOC comment) for `.surfer-page` / `.surfer-page-status` / `.surfer-page-uninstall` — match existing page spacing patterns; no new design system.

⚠️ **Decision:** Web off-switch is a dedicated Candidate nav page (`/candidate/surfer`), not buried only on Profile. Parent required a place she would actually look later; Candidate group matches Profile / Intake.

⚠️ **Decision:** Confirm uses `useUserConfirm()` (themed dialog), not `window.confirm` — same pattern as the rest of the authenticated app shell.

---

## Stage 4: Extension consent helpers under `src/ui/extension/src/lib/`

**Done when:** `src/ui/extension/src/lib/` contains `surferConsentGate.ts` and `surferOffSwitch.ts`, and `docs/features/surfer/ast-1238-extension-consent-wiring.md` lists mandatory AST-1170 / capture-route wiring; no WXT scaffold invented here.

1. Create directory `src/ui/extension/src/lib/` if missing (same layout already named for pacing helpers in `docs/test-bible/frontend/lib.md`: `pacingConfig.ts` / `dwell.ts` — consent helpers sit beside those, not under a top-level `consent/` sibling of `src/`).

2. Create `src/ui/extension/src/lib/surferConsentGate.ts`:

   - Export type `SurferConsentDto` with at least `is_current: boolean` and `capture_denied_message: string`.
   - Export `function mayCapture(dto: SurferConsentDto): boolean` returning `dto.is_current === true`.
   - Export `async function fetchConsent(apiBase: string, candidateId: string, authHeader: string): Promise<SurferConsentDto>` that `fetch`es `GET ${apiBase}/api/candidates/${candidateId}/surfer/consent` with `Authorization: Bearer ${authHeader}` (and `credentials: "omit"` — extension Bearer, not cookie), parses JSON, throws on non-OK.
   - Export `async function assertMayCapture(...): Promise<SurferConsentDto>` — fetch then if `!mayCapture(dto)` throw `Error(dto.capture_denied_message)`.

3. Create `src/ui/extension/src/lib/surferOffSwitch.ts`:

   - Export `async function optOutSurfer(apiBase, candidateId, authHeader): Promise<SurferConsentDto>` — `PUT` same path with `Content-Type: application/json`, body `JSON.stringify({ action: "opt_out" })`, Bearer auth; return parsed DTO; throw on non-OK.
   - Do not hardcode button labels — callers render from the DTO fields added in Stage 2.

4. Create `docs/features/surfer/ast-1238-extension-consent-wiring.md` (survives package layout; not buried under extension build output) with exactly these mandatory requirements:

   - **AST-1170 background** (or whatever context owns network): before any page_intake / capture POST, call `assertMayCapture` from `src/ui/extension/src/lib/surferConsentGate.ts`; on throw, show the error message via the toast primitive and **do not** POST capture.
   - **AST-1170 popup / action UI:** when consent `status === "opted_in"`, show off-switch using DTO labels; on confirm call `optOutSurfer` from `surferOffSwitch.ts`; after success, subsequent captures must no-op via the gate.
   - Always re-check server before capture — local storage is not authority.
   - Do not duplicate consent API paths; import these helpers.
   - **AST-1228 (or whichever ticket owns the page_intake HTTP route):** the route handler **must** call `require_current_surfer_consent(candidate_id)` before enqueueing classification / ingest; map `ValueError` → 403 (or 400) JSON `{"error": str(e)}`. Leave a one-line code comment at the call site: `# AST-1238: consent gate — do not remove`.
   - **Self-check when capture route lands:** grep the route module for `require_current_surfer_consent`; if absent, that ticket is incomplete relative to parent AC2 — do not ship the route without the call.

⚠️ **Decision:** Soft dependency on AST-1170. Consent TypeScript lives under `src/ui/extension/src/lib/` — the extension package source root already claimed for pacing helpers on this epic's integration line — not under `src/ui/extension/consent/`. Wiring notes live under `docs/features/surfer/` so they are not orphaned when the bundler treats `src/` as the package root. If at **build-child** time WXT entrypoints already exist, additionally wire `assertMayCapture` into the existing capture handler and mount the off-switch in the existing popup — stop and comment on the parent only if those entry files exist but their shapes do not match this plan's assumptions (do not invent a second popup framework).

⚠️ **Decision:** Extension TypeScript here is source for AST-1170's bundler. Do not add a second frontend build, Vitest project, or gitignore rows in this ticket — AST-1170 owns toolchain.

---

## Self-Assessment

**Scope:** Single-Component — frontend Surfer page + thin core helper/DTO extension + extension `src/lib` consent helpers; no new HTTP API and no schema migration.

**Conf:** Medium — AST-1235 API and DTO patterns are known; AST-1170 shell is still Discussion so extension AC4 is delivered as wire-ready helpers plus a docs wiring file rather than a loadable popup, which is the soft-dep the ticket already names.

**Risk:** Medium — a wrong `is_current` gate would either block legitimate capture or allow capture without consent; web opt-out bugs would leave Surfer "on" after she thinks she turned it off. Server helper + shared DTO reduce drift between web and extension.

---

## CODE_RULES self-review

- **§1.3 DRY:** Reuses AST-1235 GET/PUT and `is_surfer_consent_current`; no parallel consent store.
- **§2.1 config:** Off-switch / uninstall / denied / stale messages in `SURFER_CONSENT_CONFIG`; no hardcoded sets in UI.
- **§2.4 batch / §2.6 state machine:** N/A — no batch claim, no `CANDIDATE_STATES` change.
- **§3.3 imports:** Core helper stays in `candidate.py`; UI calls HTTP only; extension helpers do not import Python.
- **§3.5 naming / placement:** `CandidateSurfer.tsx`, route `candidate/surfer`, nav label Surfer; extension helpers under `src/ui/extension/src/lib/` (alongside pacing helpers named on this epic's ftr).
- **§1.1 in-scope-only:** No disclosure UI (1237), no WXT shell (1170), no page_intake route (1168).

---

## Revisions

Revision 1 — 2026-08-07  
Driven by: Joan `[plan-discuss] round=1 concern` (fix-now: extension path under `src/ui/extension/src/lib/`; fix-now: `useUserConfirm` instead of `window.confirm`; discuss: stale status label; discuss: capture_denied_message must not point at Candidate Surfer for opt-in; discuss: stronger capture-route self-check in wiring doc).  
Changes: Moved Stage 4 files to `src/ui/extension/src/lib/surferConsentGate.ts` + `surferOffSwitch.ts`; wiring notes to `docs/features/surfer/ast-1238-extension-consent-wiring.md`; Stage 3 uses `useUserConfirm`; added `status_stale_label` + three-way status line; trimmed `capture_denied_message`; added AST-1228 call-site + grep self-check to wiring doc.

---

## Build review stub

| Stage | Commit | Summary |
|-------|--------|---------|
| plan | `eef627f0` | Joan round=1 plan |
| 1–4 | `81353be0cb0720dc1f3aad6b31119e0da1a97e23` | Config copy + nav; `require_current_surfer_consent` + DTO fields; Candidate Surfer page; extension `src/lib` gate/off-switch + wiring doc |

**Tip:** `81353be0cb0720dc1f3aad6b31119e0da1a97e23` on publish ref (no PR yet).

---

## Radia review — [code-rubric] revision=1

**Publish ref tip:** `origin/sub/AST-1173/AST-1238-off-switch-and-pre-consent-no-op` @ `97c876b1`
**Overall:** FIX-NOW

**Plan adherence:** Stages 1–4 as authored in this plan (post Joan round-1 revision) are implemented faithfully in isolation — three-way status line, `useUserConfirm`, trimmed `capture_denied_message`, extension gate/off-switch helper signatures, wiring doc content all match. The defect below is not a plan-fidelity gap in what this ticket added; it is what the branch's merge history did to a sibling's already-shipped work.

**fix-now — `orch.git.merge-on-checkout`:** commit `ce3ef40b` ("Merge … origin/sub/AST-1173/AST-1237-install-disclosure-and-affirmative-opt-in …", 03:17:38) pulled in only AST-1237's plan doc (AST-1237's `code`/`test` commits landed afterward, 03:21–03:54). This sub was never re-merged against AST-1237's real tip. Confirmed on the publish-ref tip tree: `src/ui/frontend/src/pages/CandidateSurferConsent.tsx`, the `/candidate/surfer_consent` route + nav entry, `src/ui/extension/src/lib/surferConsent.ts` / `surferDisclosureDom.ts`, and `SURFER_CONSENT_CONFIG`'s five AST-1237 chrome keys (plus the `current_version` "2" bump and the longer disclosure copy) are all **absent** — reverted by the merge, not by any commit in this ticket's own Files Changed list. Concrete proof it's already broken: `tests/component/frontend/pages/test_CandidateSurferConsent.test.tsx` and `tests/component/frontend/lib/test_surferConsent.test.ts` (still present on this branch via a later `test(AST-1237)` commit) import product modules that no longer exist on this tree — they will fail at import resolution. Neither file is in Betty's AST-1238 manifest, so `Tests Passed` never actually ran them. Shipping this branch as-is silently reverts the just-reviewed-clean AST-1237 feature; parent AC1/AC2 would have no reachable opt-in surface.

**fix-now — `astral.standards.in-scope-only`:** the plan's Files Changed table authorizes only additions; nothing in this plan calls for deleting `CandidateSurferConsent.tsx`, its route/nav entry, its extension libs, or AST-1237's config/DTO keys. Same root cause as above, flagged separately because the plan itself never scoped touching those files.

**Fix:** merge AST-1237's current tip (or `origin/ftr/AST-1173-...` once it rolls up) into this sub; reconcile `SURFER_CONSENT_CONFIG` / `surfer_consent_dto` to union both tickets' keys (`current_version` stays `"2"`); restore `CandidateSurferConsent.tsx` + route + nav + extension libs + `App.css` §10b2 alongside this ticket's own `CandidateSurfer.tsx` + route + nav + extension libs; re-run both tickets' tests.

**Straggler (C4):** Joan's plan-rubric verdict (revision=1, APPROVED, `eef627f0`) excludes `astral.git.engineer-test-tree-ban` (plan has no test paths). This sweep scores it against the real diff (which carries Betty's `merge-tests` cumulative `tests/**` paths) — advisory only; content check confirms no engineer commit touches `tests/` or `docs/test-bible/**` (`81353be0` touches only `src/` + `docs/features/`). Mechanical divergence (plan Files Changed vs full diff), not a role-separation violation.

**Frame diff:** (none) — this ticket's own Description (AC/In-scope/Boundaries) is accurate to its own plan; the defect is an execution/merge error, not a scope-definition problem.

**What's solid:** `require_current_surfer_consent`, the three-way status line, `useUserConfirm` usage, and the extension `surferConsentGate.ts` / `surferOffSwitch.ts` signatures all match the Joan-approved plan exactly — this ticket's own code is ready once it stops erasing AST-1237's.

context_tokens≈145000
— Radia
