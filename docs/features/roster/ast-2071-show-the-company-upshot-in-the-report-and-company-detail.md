# AST-2071 — Show the company upshot in the report and company detail

- **Ticket:** [AST-2071](https://linear.app/astralcareermatch/issue/AST-2071)
- **Parent:** [AST-2054 — Company Upshot - new task](https://linear.app/astralcareermatch/issue/AST-2054)
- **Publish ref:** `sub/AST-2054/AST-2071-upshot-display` (origin only)

Read-only display of Estelle's prose company upshot. The company API lifts
`company_data.company_upshot` to the top level of the company payload (default
`""`). The Recommended report's **Company Upshot** section renders that prose
only — the `prefilter_company_notes` read and display are removed from the
report modal. The company detail modal gets an **Upshot** row when the upshot
is non-empty; its existing **Notes** row (grade notes) is unchanged. This
ticket writes nothing: generation is [AST-2070](https://linear.app/astralcareermatch/issue/AST-2070) (#2) and the
`company_upshot` storage key registration is [AST-2069](https://linear.app/astralcareermatch/issue/AST-2069) (#1). It only reads the
`company_data.company_upshot` key, so it does not depend on either landing first —
before they do, every company simply shows the empty state.

## Scope check

Every row below is a file named in this ticket's `## Scope`, and every change is
the kind Technical scope describes for it. No other files are touched.

## Canon

Citations: `stat.logging.debug`, `stat.logging.error` (only if the API change adds
a handler).

- `stat.logging.error` — **not triggered.** Stage 1 adds no handler, no `try`,
  and no new route; it adds one dict assignment inside an existing helper.
- `stat.logging.debug` — **backend only, no new logic joints.** The change has no
  loop, no callee call, and no branch, so there is no begin/end or call/response
  joint to log. No `logger` is added to `api_companies.py` (it has none today).
  The statute's Notes exclude React, so Stages 2–3 carry no logging duty.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_companies.py` | `_flatten_for_view` also lifts `company_data.company_upshot` (default `""`) | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Company fetch reads `company_upshot`; `company_upshot` section and its default-expanded use it; `prefilter_company_notes` removed | ui (frontend) |
| `src/ui/frontend/src/components/CompanyDetailModal.tsx` | `company_upshot` on `CompanyDetail`; **Upshot** row when non-empty | ui (frontend) |

No files are created or deleted. No config, CSS, or manifest changes — the
`company_upshot` report section row already exists in
`src/utils/config.py` (`report_summary_sections`, `"section_id": "company_upshot"`).

## Stage 1: API lifts `company_upshot`

**Done when:** `GET /api/companies/<short_name>` returns a top-level
`company_upshot` string — the stored value when `company_data.company_upshot`
exists, `""` otherwise — and `prefilter_company_notes` is still returned exactly
as before.

1. In `src/ui/api/api_companies.py`, in `_flatten_for_view`, directly after the
   existing line
   `company["prefilter_company_notes"] = cd.get("prefilter_company_notes", "")`,
   add:
   `company["company_upshot"] = cd.get("company_upshot", "")`
2. Replace the `_flatten_for_view` docstring with:
   `"""Lift prefilter_company_notes and company_upshot from company_data to top-level for display."""`
3. Change nothing else in the file. Both `list_view` and `detail` already call
   `_flatten_for_view`, so list rows gain the field too.

⚠️ **Decision:** Keep `prefilter_company_notes` in the payload. Parent Functional
scope §5–6 keeps the grades and shows them separately; `CompanyDetailModal`'s
Notes row and the companies list columns still read it.

⚠️ **Decision:** No `str()` coercion or `.strip()` server-side — mirror the
existing `prefilter_company_notes` line exactly. The frontend owns trimming
(Stages 2–3), matching how the report modal already treats notes.

**Commit:** `code(AST-2071): api lifts company_upshot to top level`

## Stage 2: Report Company Upshot section shows prose only

**Done when:** In the Recommended report Summary tab, the Company Upshot section
shows `company_upshot` when it is a non-empty (trimmed) string, and
"No company upshot on file." otherwise; the section is default-expanded only when
an upshot exists; and
`grep -n prefilter_company_notes src/ui/frontend/src/components/JobAnalysisReportModal.tsx`
returns nothing.

All edits in `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`:

1. Rename the state hook
   `const [companyNotes, setCompanyNotes] = useState<string | null>(null)` to
   `const [companyUpshot, setCompanyUpshot] = useState<string | null>(null)`.
2. In `load`, rename the reset call `setCompanyNotes(null)` (before the `try`) to
   `setCompanyUpshot(null)`.
3. In `load`'s company fetch `.then(co => { … })`, replace
   ```ts
   const notes = co?.prefilter_company_notes
   setCompanyNotes(typeof notes === "string" && notes.trim() ? notes.trim() : null)
   ```
   with
   ```ts
   const companyUpshotText = co?.company_upshot
   setCompanyUpshot(
     typeof companyUpshotText === "string" && companyUpshotText.trim() ? companyUpshotText.trim() : null,
   )
   ```
   Leave the `company_website` lines above it unchanged.
4. In the same fetch's `.catch(() => { … })`, rename `setCompanyNotes(null)` to
   `setCompanyUpshot(null)`.
5. In `summarySections`' `useMemo`, change
   `else if (s.section_id === "company_upshot") default_expanded = !!companyNotes`
   to
   `else if (s.section_id === "company_upshot") default_expanded = !!companyUpshot`
   and in that `useMemo`'s dependency array replace `companyNotes` with
   `companyUpshot` (same position).
6. In `renderSummarySection`, change the `company_upshot` branch body line
   `if (companyNotes) return <p className="job-analysis-upshot-body">{companyNotes}</p>`
   to
   `if (companyUpshot) return <p className="job-analysis-upshot-body">{companyUpshot}</p>`.
   The empty-state line `No company upshot on file.` stays exactly as is.
7. Run the grep from **Done when**; it must return nothing. Also
   `grep -n companyNotes` on the file must return nothing (no leftover
   references).

⚠️ **Decision:** Rename `companyNotes` → `companyUpshot` rather than only swapping
the field read. The variable would otherwise name the grade notes it no longer
holds. The local is `companyUpshotText` (not `upshot`) because `upshot` is
already the job `analysis_upshot` memo in this component.

**Commit:** `code(AST-2071): report company upshot renders company_upshot only`

## Stage 3: Company detail modal Upshot row

**Done when:** Opening a company whose `company_upshot` is non-empty (after
trim) from the Watch list shows an **Upshot** row with that text in the Summary
tab; a company with an empty, whitespace-only, or missing upshot shows no Upshot
row; and the **Notes** row still renders from `prefilter_company_notes` exactly
as before.

All edits in `src/ui/frontend/src/components/CompanyDetailModal.tsx`:

1. In `interface CompanyDetail`, directly after
   `prefilter_company_notes?: string`, add `company_upshot?: string`.
2. In `SummaryTab`'s left column, directly **before** the existing
   `{data.prefilter_company_notes && ( … Notes … )}` block, add:
   ```tsx
   {data.company_upshot?.trim() && (
     <DetailRow label="Upshot"><span>{data.company_upshot.trim()}</span></DetailRow>
   )}
   ```
3. Do not modify the Notes block, `DetailRow`, the form, or any other row.

⚠️ **Decision:** Row placement is after **Last Scanned**, before **Notes** — the
prose take reads before the grade dump it replaces as the primary summary.

⚠️ **Decision:** Gate on `.trim()` so a whitespace-only upshot shows no row
(AC 14 fail case "a row shown when the upshot is empty"), consistent with the
report modal's trimmed check in Stage 2. Same `<span>` markup as the Notes row —
no new CSS (CSS is not in Scope).

**Commit:** `code(AST-2071): company detail modal upshot row`

## Verification (before each commit)

Per Susan's standing rule — compile and lint before every commit:

- Stage 1: `python3 -m py_compile src/ui/api/api_companies.py` must pass, and
  `ruff check src/ui/api/api_companies.py` must report **only** the pre-existing
  `I001` (import block un-sorted, lines 3–17) — no new findings.
- Stages 2–3: `src/ui/frontend/node_modules` is not installed in the epic
  worktree (gitignored). Before the first frontend verification, run `npm ci`
  in `src/ui/frontend/` (uses the committed `package-lock.json`; produces no
  tracked changes). Then from `src/ui/frontend/`, `npm run build` (runs `tsc -b`)
  and
  `npx eslint src/components/JobAnalysisReportModal.tsx src/components/CompanyDetailModal.tsx`.
  Both must be clean for the touched files. If either reports findings on lines
  this plan did not touch, record them in the stage's Linear comment and do not
  fix them.

⚠️ **Decision:** Do not fix the pre-existing `ruff` `I001` in
`api_companies.py`. Reordering imports is not a change Technical scope describes
for that file (it names only `_flatten_for_view`), and it was red on
`origin/dev` @ `2fd5c63e7` before this ticket.

Tests are Betty's (`qa-child`); this plan touches no `tests/` or bible paths.

## Acceptance criteria map

| AC | Satisfied by |
|----|--------------|
| 12 — API exposes `company_upshot` (`""` when absent) | Stage 1 |
| 13 — Report shows prose only; grep for `prefilter_company_notes` empty | Stage 2 |
| 14 — Detail modal Upshot row only when non-empty | Stage 3 |

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

**Ticket:** AST-2071
**Overall:** APPROVED
**Corpus:** 2d1b73da19cf1d14276e5c26f52b37aa8047d159
**Publish ref:** `origin/sub/AST-2054/AST-2071-upshot-display` @ `8ef3f6b2abf0060bda8c236abcef534636e91a07`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.debug | A | | |
| stat.logging.error | A | | |

## Traceability

AC 12 → Stage 1; AC 13 → Stage 2; AC 14 → Stage 3. Parent AC 1–11 N/A (generation, config, pipeline — AST-2069/2070).

## Findings

**acceptable** — Plan §Canon correctly reasons that Stage 1 adds no loop/callee/branch joints and Stages 2–3 are React (`stat.logging.debug` Notes: backend only). No new `try`/handlers, so `stat.logging.error` is not engaged.

**acceptable** — Lifting `company_upshot` in `_flatten_for_view` also exposes the field on list endpoints (same as `prefilter_company_notes` today). Not required by child AC 12 (detail `GET`) but consistent and low blast radius.

**discuss** — Parent display work often implicates `astral.layers.import-direction` and `astral.ui.frontend-file-placement`; they are not on this child’s frozen Citations list. The plan touches only in-scope existing UI paths and creates no new files — no scoring gap, but Archie may still want those on display children by convention.

**Definition fidelity (R6):** Plan matches child Scope and parent Functional scope §6 (prose in report + detail; grades separate). Files/stages stay inside ticket `## Scope`. Stages are executable (field rename, grep gates, trim parity). Estimate confirm present. No Plan Discuss rounds on thread.

## Review

- **Branch:** `sub/AST-2054/AST-2071-upshot-display`
- **Stage 1:** `bfcda3f58` — `_flatten_for_view` lifts `company_upshot` (default `""`)
- **Stage 2:** `f5dd62458` — report Company Upshot section reads `company_upshot`; `prefilter_company_notes` / `companyNotes` gone from the modal
- **Stage 3:** `3ad69d8b7` — `CompanyDetailModal` `company_upshot` type field + trimmed **Upshot** row before Notes
- **Build notes:**
  - `ruff check src/ui/api/api_companies.py`: only the pre-existing `I001` (unchanged, per plan).
  - `npm run build` clean. `eslint` on both components: 0 errors; one pre-existing warning on an untouched line,
    `JobAnalysisReportModal.tsx:286` `react-hooks/exhaustive-deps` (`persistStructureRows`) — not fixed, per plan.
  - No tests touched; coverage is Betty's `qa-child`.

## Radia review

**Ticket:** AST-2071  
**Publish ref:** `491c7610adce32a416e1a0381307b9931a783144` (`origin/sub/AST-2054/AST-2071-upshot-display`)  
**Corpus:** `2d1b73da19cf1d14276e5c26f52b37aa8047d159`  
**Overall:** CLEAN  

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.debug | A | | |
| stat.logging.error | A | | |

## Column diff vs plan stage

(aligned) — Joan: `stat.logging.debug` A, `stat.logging.error` A; same here.

## Frame diff

(none)

## Findings

**fix-now** — (none)

**discuss** — (none)

**advisory**

- **sibling test carry:** `merge-tests(AST-2071)` brings non–AST-2071 paths into the three-dot diff (`tests/component/core/test_contact.py`, `test_meteorite.py`, `tests/component/external/test_slack.py`, assorted `tests/component/frontend/pages/*`, `test_ArtifactEditor.test.tsx`, `test_config.py`, and matching `docs/test-bible/**` deltas). Expected per §5.4; **no sibling `src/**` product scope** beyond `api_companies.py`, `JobAnalysisReportModal.tsx`, `CompanyDetailModal.tsx`.
- **Canon Scope (carry-forward from Joan):** `astral.layers.import-direction` / `astral.ui.frontend-file-placement` are not on the frozen list; this diff only extends existing modules and adds no new files — not scored, not ESCALATE.

### Plan fidelity (§5.4)

- **Stage 1:** `_flatten_for_view` lifts `company_upshot` with `cd.get("company_upshot", "")`; docstring updated; `prefilter_company_notes` unchanged.
- **Stage 2:** Report modal uses `companyUpshot` / `company_upshot`; `prefilter_company_notes` and `companyNotes` absent from `JobAnalysisReportModal.tsx`; empty copy and `default_expanded` follow trimmed presence.
- **Stage 3:** `CompanyDetail` type + trimmed **Upshot** row before **Notes**; Notes block untouched.
- **Tests/bible:** Betty manifest paths match plan AC 12–14 (`test_api_companies.py` lift + detail `""`, AST-949 Summary cases retargeted with decoy grade notes, new AST-2071 detail case).

### Estimate footprint (§5.4)

Confirm **2** — three small product files plus targeted component tests; fits.

## What's solid

- Clear separation of prose upshot vs grade notes (decoy assertions in report tests).
- API lift mirrors existing `prefilter_company_notes` pattern (list + detail).
- Plan-stage logging reasoning holds on the actual diff (no new joints, no handlers).

## Recommended actions (downstream — not Radia)

- Chuckles: append this block to `docs/features/roster/ast-2071-show-the-company-upshot-in-the-report-and-company-detail.md`, commit `docs(AST-2071): Radia review — clean`, post slim upshot, move to **Review Posted**; datt **PROCEED** → **User Testing** per gate.
- No `resolve-child` canon work required.
