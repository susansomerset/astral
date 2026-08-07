# AST-1237 — Install disclosure and affirmative opt-in

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1237/install-disclosure-and-affirmative-opt-in-consent-install-disclosure  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1173/consent-install-disclosure-affirmative-opt-in-and-off-switch  

**Publish ref (origin):** `sub/AST-1173/AST-1237-install-disclosure-and-affirmative-opt-in`  
**Parent integration ref:** `ftr/AST-1173-consent-install-disclosure-affirmative-opt-in-and-off-switch`

Ship the **candidate-facing disclosure** that shows config-driven copy + version, an **affirmative opt-in** that records consent via the AST-1235 API (dismiss / decline does **not** call opt-in), and **optional framing** already carried in that copy. Off-store install means this wording is the only warning she gets — refine `SURFER_CONSENT_CONFIG` so the prose carries session use, terms risk, account-level consequence, and that Surfer is optional. Parent AC1 / AC2 / AC6 for this child; re-consent when `is_current` is false (version bump) reuses the same surfaces.

Boundaries (do **not** implement): consent record schema / core helpers beyond DTO chrome fields (**AST-1235** owns them); off-switch / capture-path no-op gate (**AST-1238**); WXT Manifest V3 scaffold, background worker, icon-click capture, or auth session wiring (**AST-1170**); legal review of copy; packaging / install instructions (**AST-1187**).

⚠️ **Decision (surfaces):** Primary UAT-able disclosure + opt-in lands in the **Astral web app** (`/candidate/surfer_consent`) so friends-and-family can record consent without waiting on **AST-1170**. Extension-side disclosure ships as **`src/ui/extension/src/lib/`** modules (same pattern as AST-1236 pacing libs on sibling Surfer lines): injected authenticated fetch helpers, plain-DOM renderer, no WXT entry points. **AST-1170** / **AST-1238** wire those modules into install / pre-capture. Parent AC1's "before any page can be captured" is jointly enforced: this ticket records consent and shows disclosure; **AST-1238** no-ops capture until `is_current`.

⚠️ **Decision (decline):** **Not now** / dismiss / navigate away performs **no** `PUT`. Status stays whatever it was (`none` or stale). Explicit opt-out is **AST-1238** only — declining must not write `opted_out`.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Refine `SURFER_CONSENT_CONFIG` disclosure copy; bump `current_version`; add UI chrome strings + asserts; add Candidate nav item | utils |
| `src/core/candidate.py` | Extend `surfer_consent_dto` with chrome fields from config | core |
| `src/ui/extension/src/lib/surferConsent.ts` | New — DTO types, `needsDisclosure`, fetch/opt-in via injected helpers | ui/extension |
| `src/ui/extension/src/lib/surferDisclosureDom.ts` | New — plain-DOM disclosure panel (affirmative + decline) | ui/extension |
| `src/ui/frontend/src/pages/CandidateSurferConsent.tsx` | New — web disclosure + affirmative opt-in page | ui |
| `src/ui/frontend/src/routes.tsx` | Register `/candidate/surfer_consent` | ui |
| `src/ui/frontend/src/App.css` | Styles for Surfer consent disclosure page | ui |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Note AST-1237 UI + DTO chrome fields on the consent subsection | docs |

No new Python blueprints, no `tests/` / bible edits (Betty after Code Complete), no WXT `package.json` / manifest / background entry (AST-1170), no opt-out control on the web page (AST-1238).

---

## Stage 1: Config copy weight + chrome strings + DTO

**Done when:** `SURFER_CONSENT_CONFIG` has non-empty chrome strings and a disclosure copy that explicitly covers session use, terms risk, account-level consequence, and optional framing; `current_version` is bumped when copy changes; `surfer_consent_dto` returns those chrome fields; module asserts fail on empty chrome keys.

1. In `src/utils/config.py`, update `SURFER_CONSENT_CONFIG` as follows (keep `candidate_data_key`, `statuses`, `default_status` unchanged):

   - Set `"current_version": "2"` (bump because disclosure wording changes for off-store weight).
   - Replace `disclosure_copy` with this exact multi-paragraph string (preserve `\n\n` paragraph breaks):

```python
    "disclosure_copy": (
        "Astral Surfer is a browser extension that uses your own logged-in session on "
        "LinkedIn and Indeed. When you ask it to, it can read the job pages you are "
        "looking at and send that page content into Astral so we can pull postings we "
        "cannot otherwise reach.\n\n"
        "That use is not sanctioned by those sites' terms of service. We have designed "
        "Surfer to behave like ordinary manual browsing to keep the risk low, but we "
        "cannot promise a site will never notice. If it does, any account-level "
        "consequence (warning, suspension, or similar) is yours, not Astral's.\n\n"
        "Surfer is optional — the rest of Astral works without it. You can turn Surfer "
        "off later from the extension or your Astral account."
    ),
```

   - Add chrome keys (non-empty strings after strip):

```python
    "disclosure_title": "Before you use Astral Surfer",
    "opt_in_label": "I understand — turn on Surfer",
    "decline_label": "Not now",
    "current_ok_title": "Surfer is on",
    "current_ok_body": (
        "You already opted in to the current Surfer disclosure for this account. "
        "Capture stays available until you turn Surfer off or we change the disclosure."
    ),
```

2. Immediately after the existing `SURFER_CONSENT_CONFIG` asserts, add asserts that each of `disclosure_title`, `opt_in_label`, `decline_label`, `current_ok_title`, `current_ok_body` is a non-empty `str` after strip.

3. In `src/core/candidate.py`, extend `surfer_consent_dto` so the returned dict **also** includes:

   - `"disclosure_title": SURFER_CONSENT_CONFIG["disclosure_title"]`
   - `"opt_in_label": SURFER_CONSENT_CONFIG["opt_in_label"]`
   - `"decline_label": SURFER_CONSENT_CONFIG["decline_label"]`
   - `"current_ok_title": SURFER_CONSENT_CONFIG["current_ok_title"]`
   - `"current_ok_body": SURFER_CONSENT_CONFIG["current_ok_body"]`

   Keep existing keys (`status`, `accepted_version`, `updated_at`, `current_version`, `disclosure_copy`, `is_current`) unchanged in meaning.

⚠️ **Decision:** Chrome labels live in the same `SURFER_CONSENT_CONFIG` block and ride the consent GET DTO — no second config block, no hardcoded button strings in React or extension DOM. AST-1235 already put copy + version on the DTO for this reason.

⚠️ **Decision:** Bump `current_version` to `"2"` with the copy change so any prior `"1"` opt-in correctly fails `is_current` and re-prompts (parent Open question 1 / Joan).

---

## Stage 2: Extension consent lib + plain-DOM disclosure

**Done when:** `src/ui/extension/src/lib/surferConsent.ts` and `surferDisclosureDom.ts` exist; callers can detect need for disclosure, fetch/opt-in via injected authenticated helpers, and mount a plain-DOM panel whose only consent write path is the affirmative button; no WXT scaffold, no background/content entry points, no capture calls.

1. Create directory `src/ui/extension/src/lib/` if missing (AST-1236 pacing libs may land from sibling ftrs later — create only what this ticket needs).

2. Create `src/ui/extension/src/lib/surferConsent.ts`:

```typescript
/** Surfer consent — server DTO + helpers (AST-1237). Shell/gate wire these (AST-1170 / AST-1238). */

export type SurferConsentDto = {
  status: string;
  accepted_version: string | null;
  updated_at: string | null;
  current_version: string;
  disclosure_copy: string;
  is_current: boolean;
  disclosure_title: string;
  opt_in_label: string;
  decline_label: string;
  current_ok_title: string;
  current_ok_body: string;
};

/** True when capture must not proceed until she affirms the current wording. */
export function needsDisclosure(dto: SurferConsentDto): boolean {
  return dto.is_current !== true;
}

/**
 * GET /api/candidates/<id>/surfer/consent via caller-supplied authenticated fetch.
 * Background context owns network I/O (AST-1170) — this module does not hardcode base URL or credentials.
 */
export async function fetchSurferConsent(
  candidateId: string,
  getJson: (path: string) => Promise<SurferConsentDto>,
): Promise<SurferConsentDto> {
  return getJson(`/api/candidates/${encodeURIComponent(candidateId)}/surfer/consent`);
}

/**
 * PUT opt_in with the DTO's current_version (the wording she was shown).
 * Does not accept a free-form version from the UI — always send dto.current_version.
 */
export async function optInSurferConsent(
  candidateId: string,
  dto: SurferConsentDto,
  putJson: (path: string, body: unknown) => Promise<SurferConsentDto>,
): Promise<SurferConsentDto> {
  return putJson(`/api/candidates/${encodeURIComponent(candidateId)}/surfer/consent`, {
    action: "opt_in",
    accepted_version: dto.current_version,
  });
}
```

3. Create `src/ui/extension/src/lib/surferDisclosureDom.ts`:

   - Export `mountSurferDisclosure(host: HTMLElement, dto: SurferConsentDto, handlers: { onOptIn: () => void | Promise<void>; onDecline: () => void }): { unmount: () => void }`.
   - Clear `host` and build a simple panel (no React): title from `dto.disclosure_title`, body text from `dto.disclosure_copy` (preserve paragraph breaks — split on `\n\n`, one `<p>` per paragraph; within a paragraph, turn single `\n` into `<br>`), primary button labeled `dto.opt_in_label`, secondary button labeled `dto.decline_label`.
   - Primary click → call `handlers.onOptIn` only (caller runs `optInSurferConsent` then unmounts / continues). Do **not** call any network API inside this module.
   - Secondary click → call `handlers.onDecline` only (no opt-in).
   - Clicking outside / Esc is **not** required; if the host is torn down without opt-in, that is decline-equivalent (no write).
   - Prefer attaching into a **shadow root** on `host` when `host.attachShadow` is available (`mode: "open"`), so host-page CSS cannot restyle the panel; otherwise render as direct children of `host`.
   - `unmount()` removes the shadow root / children and clears listeners.

⚠️ **Decision:** Extension modules stay lib-only (AST-1236 pacing precedent). Do **not** add `manifest.json`, WXT config, popup HTML, or `chrome.runtime.onInstalled` here — that is AST-1170. Document in a one-line file header that the shell must call `needsDisclosure` → `mountSurferDisclosure` before capture.

---

## Stage 3: Web disclosure page + route + nav

**Done when:** Authenticated candidate can open `/candidate/surfer_consent`, see server-supplied title/copy/labels, record opt-in only via the affirmative button, and leave via **Not now** without any consent PUT; when `is_current`, the page shows the current-ok chrome (no opt-out control); NAV_CONFIG and `routes.tsx` stay in sync.

1. Create `src/ui/frontend/src/pages/CandidateSurferConsent.tsx`:

   - Import `useCandidate` for `selectedId`; import `api` from `../lib/api`; use `readApiError` / toast patterns already used on candidate pages when a request fails.
   - If `selectedId` is null, render a short empty state: ask to select a candidate (same spirit as other candidate pages) — do **not** invent a consent write.
   - On mount / when `selectedId` changes: `GET /api/candidates/${selectedId}/surfer/consent` via `api(...)`, parse JSON into a local typed object matching the DTO keys from Stage 1.
   - When `dto.is_current === true`: render `dto.current_ok_title` and `dto.current_ok_body` only. **Do not** render an opt-out button (AST-1238).
   - When `needs disclosure` (`!dto.is_current`): render `dto.disclosure_title`, `dto.disclosure_copy` (paragraphs as above), button `dto.opt_in_label`, button `dto.decline_label`.
   - Affirmative click: `PUT` with `JSON.stringify({ action: "opt_in", accepted_version: dto.current_version })`, `Content-Type: application/json`. On success, replace local state with the response DTO (should show current-ok). On failure, toast the API error; do **not** flip UI to opted-in.
   - Decline click: `navigate("/jobs/recommended")` via React Router `useNavigate` — **no** PUT. Do not call opt-out.
   - While loading, show a simple loading line; do not enable the opt-in button until the DTO is loaded.
   - All visible strings for the disclosure / buttons / current-ok state come from the DTO — no parallel hardcoded English for those controls in the TSX (loading / empty-candidate / error toast helpers may use ordinary page chrome).

2. In `src/ui/frontend/src/routes.tsx`:

   - Import `CandidateSurferConsent` (name the default export `SurferConsent` or `CandidateSurferConsent` — file is `CandidateSurferConsent.tsx`).
   - Under the Candidate routes block, add `{ path: "candidate/surfer_consent", element: <CandidateSurferConsent /> }` after `candidate/writing_preferences`.

3. In `src/utils/config.py` `NAV_CONFIG`, under the Candidate group's `items`, append:

   `{"label": "Surfer Consent", "path": "/candidate/surfer_consent"}`

   after Writing Preferences (keep SYNC comment with `routes.tsx` honest).

⚠️ **Decision:** Nav is always visible under Candidate (no new `visible`/`enabled` gate). Declining or never visiting leaves every other nav/route unchanged — satisfies parent AC6 without gating Jobs/Companies/etc. on consent.

⚠️ **Decision:** Web page is the friends-and-family / install-instructions target until AST-1170 mounts the extension disclosure. Do not add a global login modal that blocks the whole app.

---

## Stage 4: App.css for the disclosure page

**Done when:** The Surfer consent page has readable layout styles under a numbered `App.css` section; no new CSS file.

1. In `src/ui/frontend/src/App.css`, add a new section after the Candidate Profile block (e.g. `/* === 10b2. Surfer consent disclosure (AST-1237) === */` — pick the next free number that matches the TOC comment at the top of the file; if the TOC lists sections, add a matching TOC line).

2. Style a wrapper class used by `CandidateSurferConsent` (e.g. `.surfer-consent-page`) with: constrained content width, title hierarchy, paragraph spacing for disclosure body, primary vs secondary button distinction. Reuse existing button / content-area tokens where they already exist — do not invent a second design system. Keep styling minimal and local to this page.

3. If `surferDisclosureDom.ts` uses class names, prefix them with `astral-surfer-consent-` and include a short `<style>` inside the shadow root with the same visual hierarchy (title, body, primary/secondary buttons) so the extension panel is usable without depending on `App.css`. Inline the minimal CSS string in the DOM module — do **not** import React CSS into the extension lib.

---

## Stage 5: Data-model doc note

**Done when:** `CANDIDATE_DATA_MODEL.md` `surfer_consent` subsection names AST-1237 as the install UI owner and lists the extra DTO chrome fields (not stored on the meta record).

1. In `docs/features/candidate/CANDIDATE_DATA_MODEL.md`, under `### surfer_consent (AST-1235 / AST-1173)`:

   - Keep the stored record shape unchanged.
   - Add a short note that `surfer_consent_dto` **also** exposes config chrome: `disclosure_title`, `opt_in_label`, `decline_label`, `current_ok_title`, `current_ok_body` (AST-1237) — display-only, not persisted under `candidate_data.surfer_consent`.
   - Change the install-UI sentence to: Install disclosure UI (web + extension lib) = **AST-1237**; off-switch + capture no-op = **AST-1238**.

---

## Self-Assessment

**Scope:** `Single-Component` — config/DTO chrome + candidate web page + extension lib modules; no new API blueprint, no capture gate, no WXT shell.

**Conf:** `high` — AST-1235 API/DTO already on this line; frontend page patterns (`api` + `useCandidate` + NAV/routes sync) and extension lib injection pattern (AST-1236 pacing) are established; soft wire to AST-1170 is documented, not invented.

**Risk:** `Medium` — wrong decline path that accidentally PUTs opt-in/opt-out would falsify AC2/AC6; mitigated by explicit no-PUT decline steps. Soft dependency on AST-1170 means install-time extension appearance is not fully UAT-able until the shell mounts the lib — web page covers consent recording for friends-and-family in the meantime.

---

## Code rules self-review

| Rule | Plan check |
|------|------------|
| §1.3 DRY | Reuse AST-1235 GET/PUT; no parallel consent writer; shared DTO for web + extension |
| §2.1 / no-hardcoded-sets | Copy, version, button/title chrome only in `SURFER_CONSENT_CONFIG` |
| §2.4 batch | N/A |
| §2.6 state machine | Does not change `CANDIDATE_STATES` |
| §2.9 require-auth | Existing consent routes stay `@require_auth`; page behind `RequireAuth` |
| §3.3 imports | UI → existing API; extension libs take injected fetch (no Python imports) |
| §3.5 naming / placement | `CandidateSurferConsent.tsx`, `/candidate/surfer_consent`, `src/ui/extension/src/lib/` |
| ui-config-driven | Clients render DTO fields; no local copy of disclosure prose |
| in-scope-only | No off-switch, no capture no-op, no WXT scaffold |
| Test tree | No `tests/` / bible edits |

No unresolved conflicts → Conf stays `high`.

---

## Radia review — [code-rubric] revision=1

**Rubric:** code-rubric.v1
**Publish ref tip:** `2d1e2d99` (`sub/AST-1173/AST-1237-install-disclosure-and-affirmative-opt-in`)
**Overall:** CLEAN

Full 65-statute active set scored in-session against `git diff origin/dev...origin/sub/AST-1173/AST-1237-install-disclosure-and-affirmative-opt-in` (this branch stacks on the already-reviewed `AST-1235` tip; incremental review focus was the AST-1237-only delta: `src/core/candidate.py` (+6), `src/utils/config.py` (+41), new `src/ui/extension/src/lib/{surferConsent,surferDisclosureDom}.ts`, new `src/ui/frontend/src/pages/CandidateSurferConsent.tsx`, `routes.tsx` + `App.css` + `CANDIDATE_DATA_MODEL.md` updates). No `violates`, no `needs-discussion`. 3 `not-applicable` (no `src/data/**`, `scripts/**`, or `artifacts/**` touched). No Joan plan-rubric verdict attached — noted, not a block.

**What's solid**

- Chrome strings (`disclosure_title`, `opt_in_label`, `decline_label`, `current_ok_title`, `current_ok_body`) all land in `SURFER_CONSENT_CONFIG` with non-empty-after-strip asserts, and ride the existing GET DTO — no parallel copy source in React or the extension lib (`pattern.config.config-block`, `astral.standards.no-hardcoded-sets`).
- Decline path (web `onDecline` and DOM `handlers.onDecline`) is a pure navigate / callback — no `PUT` call in either surface, matching parent AC2/AC6 and the plan's explicit "no opt-in/opt-out on decline" decision. Opt-in always sends `dto.current_version`, never a free-form client value.
- `mountSurferDisclosure` prefers an existing/attachable shadow root, falls back to plain children, and `unmount()` clears the subtree — matches the plan's isolation requirement without a WXT scaffold.
- `DisclosureParagraphs` (React) defined ahead of the default-exported page component matches this codebase's established `pages/` convention (`PronounSelect`, `CacheMinCell`, `IntakeResumeDialog`, etc. all precede their page's default export) — not a `public-then-helpers` violation.
- `src/ui/extension/src/lib/` is a new tree not yet in `ASTRAL_CODE_RULES.md` §3.1's directory listing; the plan documents this placement decision explicitly (citing the AST-1236 pacing-lib precedent) and it reached Plan Approved — flagged here as a documentation-hygiene note for Archie, not a fix-now/discuss finding.
- Git hygiene clean: one `merge-tests` commit citing one `origin/tests` SHA, correct commit vocabulary, engineer commit (`8a53dc93`) touches only `src/`, test commits touch only `tests/` + `docs/test-bible/`.
- `py_compile` clean on both changed Python modules; standalone `tsc --noEmit --strict` clean on both new extension lib files; full frontend `tsc --noEmit` clean.

**Plan adherence:** Diff matches the five-stage plan file-for-file (config/DTO chrome, extension lib, web page + route + nav, App.css, data-model doc note); no extra `src/` scope. Self-Assessment `Conf: high` holds.

**Pattern conformance:** `pattern.config.config-block` — conforms (as above). `pattern.ui.admin-endpoint` — correctly not-cited/excluded (no new blueprint; reuses AST-1235's `@require_auth` routes).

**Frame diff:** none (description frame unchanged; diff matches plan as written).

context_tokens≈52000
— Radia

---

## Review (build stub)

**Publish ref:** `origin/sub/AST-1173/AST-1237-install-disclosure-and-affirmative-opt-in`  
**Built tip:** `8a53dc93` (`origin/sub/AST-1173/AST-1237-install-disclosure-and-affirmative-opt-in`)
