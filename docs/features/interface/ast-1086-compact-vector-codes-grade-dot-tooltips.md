# Compact vector codes and grade-dot tooltips on job lists

**Linear:** [AST-1086](https://linear.app/astralcareermatch/issue/AST-1086/compact-vector-codes-and-grade-dot-tooltips-on-job-lists-small-bug)  
**Parent:** [AST-1078 — Small bug: Headers for Job Lists](https://linear.app/astralcareermatch/issue/AST-1078/small-bug-headers-for-job-lists)  
**Publish ref (origin):** `sub/AST-1078/AST-1086-compact-vector-codes-grade-dot-tooltips`  
**Parent integration ref:** `ftr/AST-1078-headers-for-job-lists`  
**Blocked by:** none

Restore the AST-437 compact header contract on Skipped / In Review after AST-1059 hydration: grade `<th>` visible text is always a short vector **code** (with full name on `title` tooltip), including grades-only groups whose vectors look like `Technical (TE)`. Extend grade-dot hover text so rubric criterion text is followed by a parenthetical confidence description when confidence is present. Does **not** touch rubric snapshot writes, grouping, Recommended phase-score layout, or ConfidenceBullets glyph rendering.

---

## Prerequisite gate (before Stage 1 of build-child)

1. On epic worktree: `git fetch origin`; checkout `sub/AST-1078/AST-1086-compact-vector-codes-grade-dot-tooltips`; `git merge origin/dev`; `git merge origin/ftr/AST-1078-headers-for-job-lists`; merge-clean (`BEHIND=0`, `origin/dev` ancestor of `HEAD`).
2. Confirm current drift (do not “fix” by guessing):
   - `JobsInReview.tsx` already paints `{c.headerCode}` in grade `<th>`; `JobsSkipped.tsx` still paints `{c.code}`.
   - `buildJobListRubricColumnsFromJobGrades` sets `headerCode` to the raw vector / key (so `Technical (TE)` appears as the cell text).
   - `formatGradeDotTooltip` returns reason or `gradeDescriptions[letter]` only — no confidence parenthetical.
3. Do **not** edit `consult.py`, `api_jobs.py`, Recommended pages, or `ConfidenceBullets.tsx` glyph markup.

---

## Contract (AST-437 + this ticket)

| Surface | Visible `<th>` | `<th title>` | Grade-dot `title` |
|---------|----------------|--------------|-------------------|
| Artifact / job-carried `*_rubric` columns | `headerCode` (= vector `code`, else first two letters) | `Label (importance)` via `formatRubricColumnTooltip` | Rubric text (reason else grade description) **+** ` (confidence description)` when confidence 1–5 present |
| Grades-only fallback | Compact code extracted from `Name (XX)` → `XX`; bare short labels (e.g. `Fit`) stay as today | Tooltip uses **stripped** human label + default importance — never `Technical (TE) (5)` | Same grade-dot rule |

Identity / sort keys must keep matching grades under the correct columns (`gradeAndConfidenceForCol` already normalizes `Name (XX)` vs code/label).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/lib/rubricDisplay.ts` | Grades-only compact `headerCode` / clean label; confidence description map + `formatGradeDotTooltip` parenthetical | ui (frontend lib) |
| `src/ui/frontend/src/pages/JobsSkipped.tsx` | Paint `{c.headerCode}` in grade `<th>`; pass confidence into `formatGradeDotTooltip` | ui |
| `src/ui/frontend/src/pages/JobsInReview.tsx` | Pass confidence into `formatGradeDotTooltip` (header already uses `headerCode`) | ui |
| `tests/component/frontend/lib/test_rubricDisplay.test.ts` | Expect compact grades-only `headerCode`; cover confidence parenthetical — **Betty** (engineer hook blocks `tests/`) | ui (Betty) |
| `tests/component/frontend/pages/test_JobsSkipped.test.tsx` | Assert compact header text / title if existing assertions break — **Betty** | ui (Betty) |
| `tests/component/frontend/pages/test_JobsInReview.test.tsx` | Same — **Betty** | ui (Betty) |

Do **not** edit: `recommendedJobReport.tsx` (out of Boundaries), `ConfidenceBullets.tsx`, `api_jobs.py`, grouping helpers (`groupJobsByAlignedRubric`), or artifact editors.

---

## Stage 1: Compact grades-only headers in `rubricDisplay.ts`

**Done when:** `buildJobListRubricColumnsForGroup` / `buildJobListRubricColumnsFromJobGrades` for vector `Technical (TE)` yields `headerCode === "TE"`, `label === "Technical"`, `headerTooltip === "Technical (5)"` (default importance). Bare vector `Fit` still yields `headerCode === "Fit"` (no forced two-letter slice that changes today’s short-label behavior). `cd src/ui/frontend && npx tsc -b --noEmit` passes. No page edits in this stage.

1. In `src/ui/frontend/src/lib/rubricDisplay.ts`, add a small helper (public or file-private — prefer public next to `normalizeRubricVectorKey` if tests need it) that parses a grades vector / object key into `{ code, label }`:
   - If the string matches `/^(.*?)\s*\(([A-Z]{2})\)\s*$/`, `label` = trimmed name group, `code` = the two-letter group.
   - Else `label` = trimmed string, `code` = that same trimmed string (preserve short bare labels like `Fit`).
2. Update **`resolveRubricHeaderCode`** so when `item.code` is absent and `item.label` ends with ` (XX)`, return the `XX` group (same regex). Keep `item.code` preferred when present. Keep `label?.slice(0, 2).toUpperCase()` only when there is no paren code and no `code` (artifact path without stored code).
3. Rewrite **`buildJobListRubricColumnsFromJobGrades`** array branch: for each `{ vector }`, parse with the helper; set `code` to parsed `code`, `label` to parsed `label`, `importance: RUBRIC_DEFAULT_IMPORTANCE`, `headerCode: resolveRubricHeaderCode({ code, label })` (must equal the compact code for `Name (XX)`), `headerTooltip: formatRubricColumnTooltip(label, RUBRIC_DEFAULT_IMPORTANCE)`, `gradeDescriptions: {}`.
4. Rewrite the object-keys branch the same way (parse each key).
5. Do **not** change `buildJobListRubricColumnsFromArtifact` beyond what `resolveRubricHeaderCode` already implies for labels that embed `(XX)`.

⚠️ **Decision:** Keep bare grades vectors without a `(XX)` suffix as their own `headerCode` (e.g. `Fit`), matching today’s test `headerCode === "Fit"`. Only strings with an explicit two-letter paren code become compact two-letter headers — that is the AC3 regression (`Technical (TE)` must not stay in the `<th>`).

---

## Stage 2: Skipped header cell uses `headerCode`

**Done when:** Skipped grade `<th>` visible text is `c.headerCode` (same as In Review); `title={c.headerTooltip}` unchanged; sort still uses `c.code` as the sort column id.

1. In `src/ui/frontend/src/pages/JobsSkipped.tsx`, in the non-floor rubric header map, change the cell text from `{c.code}{sortIndicator(...)}` to `{c.headerCode}{sortIndicator(...)}`.
2. Leave `key={c.code}`, `onClick={() => handleSort(sortKey, c.code)}`, and `title={c.headerTooltip}` unchanged.
3. Run `cd src/ui/frontend && npx tsc -b --noEmit`.

---

## Stage 3: Grade-dot tooltip + confidence parenthetical

**Done when:** Hovering a grade-dot on Skipped and In Review shows rubric criterion text (job `reason` when present, else `col.gradeDescriptions[letter]`) and, when `confidence` is a number in 1–5, appends a space and parenthetical description matching `CONFIDENCE_DESCRIPTIONS` in `src/utils/config.py`. Missing / out-of-range confidence omits the parenthetical. `ConfidenceBullets` markup unchanged.

1. In `rubricDisplay.ts`, add exported constant **`CONFIDENCE_DESCRIPTIONS`** keyed `1`–`5` with **exact** strings from `src/utils/config.py` (`CONFIDENCE_DESCRIPTIONS`):
   - `5`: `The source explicitly states it.`
   - `4`: `The source strongly suggests it.`
   - `3`: `The source hints about it.`
   - `2`: `The source makes a vague reference.`
   - `1`: `The source doesn't say it out loud, but it's possible.`
2. Add exported **`confidenceDescription(confidence?: number): string`** — if `typeof confidence === "number"` and integer (or `Math.floor`) in 1–5, return the map entry; else `""`.
3. Extend **`formatGradeDotTooltip(col, grade, reasonFromJob?, confidence?: number): string`**:
   - Compute `base` exactly as today (trimmed reason, else `gradeDescriptions[letter]`, else `""`).
   - Compute `conf = confidenceDescription(confidence)`.
   - If `conf` and `base`: return `` `${base} (${conf})` ``.
   - If `conf` and no `base`: return `` `(${conf})` ``.
   - Else return `base`.
4. In **`JobsSkipped.tsx`** `gradeAndConfidenceForCol`, pass `row.confidence` (array path) into `formatGradeDotTooltip` as the 4th argument on every call that builds `gradeTooltip`. Object-map path has no confidence — omit / pass `undefined`.
5. Mirror the same 4th-argument wiring in **`JobsInReview.tsx`** `gradeAndConfidenceForCol`.
6. Do **not** change `recommendedJobReport.tsx` (optional 4th arg keeps that call site compiling).
7. Run `cd src/ui/frontend && npx tsc -b --noEmit`.

⚠️ **Decision:** Mirror `CONFIDENCE_DESCRIPTIONS` in the frontend lib rather than extending `/api/state_ui_manifest` (or any API). Ticket Boundaries are UI display only; Python `config.py` already documents intentional duplication for prompt/`output_types` text. UI mirror must stay byte-identical to the five config strings — do not invent alternate copy. If Archie later wants a single API source, that is a separate ticket.

---

## Stage 4: Engineer verify (no `tests/` commits)

**Done when:** Typecheck clean; manual spot-check notes recorded in the Linear stage comment if useful; existing Betty component tests are left for qa-child.

1. Re-run `cd src/ui/frontend && npx tsc -b --noEmit`.
2. Do **not** commit under `tests/` (pre-commit hook). Note for Betty: `test_rubricDisplay.test.ts` currently expects `fallback[0].headerCode === "Technical (TE)"` — that expectation must flip to `"TE"` (and tooltip `"Technical (5)"`); add cases for `formatGradeDotTooltip` + confidence parenthetical.

---

## Self-Assessment

**Scope:** `Single-Component` — one frontend lib module plus the two Jobs list pages that already share `JobListRubricColumn`; no API/core.

**Conf:** `high` — AST-437 / AST-1064 patterns are in-tree; the Skipped `{c.code}` vs In Review `{c.headerCode}` mismatch and grades-only `headerCode: label` assignment are concrete, localized bugs.

**Risk:** `Medium` — wrong headerCode/label parsing could mis-align grade columns or tooltips on Skipped / In Review for pre-snapshot jobs; artifact-backed groups are low risk if Stage 1 stays grades-only focused.

---

## Code-rules check

- **§1.1 / in-scope-only:** Only job-list header + grade-dot tooltip display; no Recommended / hydration / grouping edits.
- **§1.3 DRY:** Fix shared builder + shared tooltip helper once; Skipped converges on `headerCode` like In Review.
- **§1.4 no-hardcoded-sets:** Confidence copy mirrors `config.py` with an explicit Decision (no API in scope); not a new invented vocabulary.
- **§3.5 frontend-file-placement:** Changes stay in `src/lib/rubricDisplay.ts` and existing `src/pages/Jobs*.tsx`.
- **§2.1 / ui-config-driven:** Grade letters and confidence numbers still come from job payload; description text is the approved config mirror.

---

## Review

| Field | Value |
|-------|-------|
| Branch | `sub/AST-1078/AST-1086-compact-vector-codes-grade-dot-tooltips` |
| Build tip | `ec36ef4fb76e73729cc73efafb77c909e62efd3e` |
| Status | Code Complete |

---

## Radia code-rubric review

**Rubric:** code-rubric.v1 (`[code-rubric] revision=1`)  
**Publish ref tip:** `b91f64a42de2fc11442d5ed8b376cbc8a2553d19`  
**Overall:** DISCUSS (straggler callouts only — no product fix-now)

### What’s solid

- Shared `rubricDisplay` grades-only path parses `Name (XX)` → compact `headerCode` + clean label/tooltip; Skipped paints `{c.headerCode}` like In Review; sort keys stay on `c.code`.
- `formatGradeDotTooltip` + `CONFIDENCE_DESCRIPTIONS` mirror matches `src/utils/config.py` byte-for-byte; both Jobs pages pass confidence on the array path.
- Scope stays in frontend lib + two Jobs pages; Betty owns `tests/` / bible; engineer `code(AST-1086)` commit is src-only.

### Issues

**discuss (straggler):** `astral.debug.spikes-under-debug-dir` and `astral.docs.features-single-file-per-ticket` were Joan-excluded at plan time (plan layers `{ui}`) but the three-dot diff adds `docs/features/interface/ast-1086-…md`, so both score in-scope here. Verdict on each: **conforms** (normal plan file, not spike notes; single features file). No product action — belt-and-suspenders C4 only.

### Recommended actions

- Engineer: none for product. Acknowledge stragglers if desired, then resolve-child → User Testing.

---

## Resolution

**Date:** 2026-07-31  
**Status:** User Testing (resolve clean)

Radia **DISCUSS** overall with **no product fix-now**. Straggler callouts on `astral.debug.spikes-under-debug-dir` / `astral.docs.features-single-file-per-ticket` already **conforms** (normal single plan file). Advisory sibling test/bible tips via merge-tests left alone (outside AST-1086 product scope).

No product code changes in resolve. Publish tip after this commit; §9a dry-run vs `origin/dev` and `origin/ftr/AST-1078-headers-for-job-lists` required before UT.
