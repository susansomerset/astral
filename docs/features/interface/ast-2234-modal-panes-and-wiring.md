# AST-2234 — Modal panes and wiring (Updates to recommended job modal)

- **Linear:** [AST-2234](https://linear.app/astralcareermatch/issue/AST-2234) · parent [AST-2226](https://linear.app/astralcareermatch/issue/AST-2226)
- **Publish ref:** `origin/sub/AST-2226/AST-2234-modal-panes-and-wiring`
- **Assignee:** Ada

Wires AST-2232 (#1) detail/story/config payload into the Recommended Job Report modal and owns all tab panes: header callbacks (Skip already present; Applied notes; Generate when Artifacts tab hidden); Job Description tab; Discussion `agent_payload` + agent-named headers; per-phase thermometers; job total + gradable %; Artifacts tab visibility / Print / mobile read-only. Consumes #2 (AST-2233) header prop names and CSS class hooks — does not edit `RecommendedJobReportHeader.tsx` or `App.css`.

## UAT fitness

- **AC restored:** Parent AST-2226 functional scope this child owns: (2) Skip/Applied in the action row — Applied uses the same notes + `postCandidateAction(..., "applied")` path as the list **A** action; (3) Print on Artifacts (header has no Print Resume/Cover); (4) Discussion shows unescaped RESPONSE `agent_payload` prose; (5) Discussion headers `<agent_name>'s <task_name> @ m/d/yy hh:mm am/pm` in candidate timezone; (10) mobile artifacts read-only + Print; (11) Job Description top tab between Analysis and Summary, default-expanded JD; (12) hide empty Artifacts tab and show header **Generate Artifacts**; (13) Analysis phase thermometers + job total with gradable %. Child AC 3–12 map 1:1 to those outcomes (Skip/Applied legality server-gated via `can_skip` / `can_apply`).
- **Correct outcome:** Opening a Recommended report shows company_name-driven identity (via header props), Analysis with green thermometers and total+gradable beside it, a Job Description tab with JD expanded, readable Discussion headers/bodies, Artifacts only when content or build-in-progress (else Generate in the header), Applied notes flow that closes+refreshes on success, and at ≤1023px no artifact Edit / no `JobArtifactEditModal` edit path.
- **Sibling check:** #1 contract fields (`company_name`, `company_website`, `discovered_at`, `recommended_at`, `applied_at`, `can_apply`, `can_skip`, `agent_story[].agent_name`, `job_description` tab + no Summary `raw_jd`) remain as shipped on AST-2232 — this ticket only consumes them. #2 owns header chrome/CSS class names; this ticket only passes props and mounts DOM that uses those classes. Verified by Files Changed excluding `RecommendedJobReportHeader.tsx` and `App.css`.
- **Not sufficient:** Hiding a stacktrace, removing Copy buttons in the modal (that is #2), or showing Generate without also hiding the empty Artifacts tab.
- **Wrong fix rejected:** Hard-coding prior-state sets in React for Skip/Applied visibility (must use detail `can_skip` / `can_apply`); pretty-printing whole RESPONSE JSON instead of unescaped `agent_payload`; leaving Print Resume/Cover wired on the header; computing company label from `job.company` when `company_name` is present.

## Explicit scope gate

Ticket **## Scope** (only surfaces this plan may touch):

| File | Kind of change Scope allows |
|------|-----------------------------|
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | **modified** — wire header props/actions (Applied notes, Generate when tab hidden); Job Description pane; filter Artifacts tab; mobile read-only artifacts; Analysis thermometers + total/gradable; `company_name` for title/header |
| `src/ui/frontend/src/components/JobDiscussionPane.tsx` | **modified** — headers use `agent_name` / `task_name` / timestamp; body is unescaped `agent_payload` text |
| `src/ui/frontend/src/lib/recommendedJobReport.tsx` | **modified** — thermometer helper(s); job total + gradable% helpers; shared `agent_payload` extract/unescape; retire unused header print-visibility helpers |
| `src/ui/frontend/src/pages/JobsRecommended.tsx` | **modified** only if page-local `totalScore` moves into `recommendedJobReport.tsx` (list Total output unchanged) |
| `src/ui/frontend/src/components/JobArtifactEditModal.tsx` | **modified** — mobile path does not open edit; read-only drafted text + Print only |
| `src/ui/frontend/src/lib/candidateJobActions.ts` | **modified** only if a small exported Applied helper is required |
| `src/ui/frontend/src/hooks/useCandidateJobActions.ts` | **modified** only if notes-modal helper must be shared |

Every **Files Changed** row and Stage step names only those files / that kind of change. No `RecommendedJobReportHeader.tsx`, no `App.css`, no backend/config.

## Canon Scope (patterns read at plan)

Ticket Citations: `patt.artifact.ui-consistency`, `patt.artifact.read-current`.

- **`patt.artifact.ui-consistency`:** Job Analysis Report Modal / other job tabs may keep legacy props until a job-editor ticket adopts `bodyShape` — this ticket does **not** rewrite Artifacts editors onto `bodyShape`; Print/read-only mobile path reuses existing print HTML / draft display contracts.
- **`patt.artifact.read-current`:** UI must not invent parallel blob readers; Artifacts Print and read-only drafted text continue to use the existing job artifact / print paths already hydrating current bodies (no new client storage keys).

Every other directive id stays **id-only** until build-child §8.

## Prerequisite (build gate, not a stage)

Before Stage 1 product edits, HEAD must expose #1 fields. After `sync-child.sh`, confirm `GET` detail contract names from AST-2232 sibling table exist in `src/ui/api/api_jobs.py` (`company_name`, `company_website`, `discovered_at`, `recommended_at`, `applied_at`, `can_apply`) and story attach includes `agent_name`. If absent (e.g. sync skipped `origin/ftr/AST-2226-updates-to-recommended-job-modal` because `--ftr` segment was abbreviated), **stop** and comment on **AST-2234** — do not invent backend fields in React.

## Sibling #2 header prop contract (Ada calls; Hedy implements)

If `origin/sub/AST-2226/AST-2233-report-header-chrome-triage-actions` plan/code already names different props at build time, **match those names** (ticket Notes) and skip renaming. Otherwise Ada passes / expects:

| Prop | Source / rule |
|------|----------------|
| `jobTitle`, `jobLink`, `jobLinkText` | unchanged |
| `companyName` | `job.company_name` when non-empty; else fall back display only if null (do not prefer `job.company` over a present `company_name`) |
| `companyWebsite` | `job.company_website` (detail field — drop the secondary `/api/companies/...` fetch once detail carries it) |
| `discoveredAt`, `recommendedAt`, `appliedAt` | detail lifecycle fields; Applied strip only when `appliedAt` non-null |
| `onSkip` / `skipBusy` | only when `job.can_skip === true` |
| `onApplied` / `appliedBusy` | only when `job.can_apply === true` — opens notes flow, does not POST immediately |
| `onGenerateArtifacts` / `generateBusy` | only when Artifacts top tab is **hidden** (empty + not build-in-progress) |
| **Omit** | all Copy props, `showPrintResume` / `showPrintCover` / `onPrintResume` / `onPrintCover`, `applicationEmail` / `linkedInUrl` copy wiring |

CSS class hooks Ada mounts (styles land in #2 `App.css`; Ada does not edit CSS):

- Phase thermometer: `recommended-report-thermometer`, `recommended-report-thermometer-track`, `recommended-report-thermometer-fill`
- Total + gradable row: `recommended-report-total-gradable`
- Discussion header (if needed beyond existing section label): leave label string as the formatted header; #2 may style `.recommended-report-section-list` / discussion typography

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/lib/recommendedJobReport.tsx` | Add `totalScore`, phase thermometer model helpers, job-level gradable %, `agent_payload` extract/unescape; stop exporting unused header-only print helpers if nothing else imports them after modal change | ui lib |
| `src/ui/frontend/src/pages/JobsRecommended.tsx` | Import shared `totalScore` from lib; delete page-local copy; list Total display/sort unchanged | ui |
| `src/ui/frontend/src/components/JobDiscussionPane.tsx` | Custom section labels from story; body = unescaped `agent_payload` | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Detail type + header wiring, Applied notes, Generate-when-hidden, tab filter, JD pane, Analysis chrome, Artifacts Print + mobile | ui |
| `src/ui/frontend/src/components/JobArtifactEditModal.tsx` | ≤1023px: no editor; read-only drafted text + Print only | ui |

**Out of scope (do not touch):** `RecommendedJobReportHeader.tsx`, `App.css`, `candidateJobActions.ts`, `useCandidateJobActions.ts` (Decision below), backend, `tests/`.

⚠️ **Decision:** Leave `candidateJobActions.ts` and `useCandidateJobActions.ts` untouched. Modal duplicates the tiny notes open/submit wiring with local state + existing `CandidateActionNotesModal` + `postCandidateAction` (Scope preference).

---

## Stage 1: Shared helpers + list Total share

**Done when:** `recommendedJobReport.tsx` exports `totalScore`, thermometer fill/tooltip helpers, job gradable %, and `agent_payload` extract; `JobsRecommended.tsx` uses the shared `totalScore` with identical list Total numbers; header-only print helpers that nothing imports are removed or kept only if still referenced.

1. In `src/ui/frontend/src/lib/recommendedJobReport.tsx`, move the page-local `totalScore` algorithm from `JobsRecommended.tsx` (sum of `phaseFields` via finite-or-null; `null` if any phase missing) into an exported `totalScore(job: Record<string, unknown>, phaseFields: string[]): number | null`. Keep behavior identical (AST-1968).
2. Add exported helpers (names may vary; behavior fixed):
   - **Phase thermometer:** given list score `score` and breakdown `{ earned, possible, max }` from existing `jobScoreBreakdownForGradesField`:
     - `fillRatio = max > 0 ? clamp(score / max, 0, 1) : 0`
     - `tooltip = \`Score ${formatPhaseScore(score)}, ${Math.round(100 * possible / max)}% gradable\`` when `max > 0` and score is finite; otherwise no thermometer for that phase.
   - **Job gradable %:** over all phase `*_grades` arrays on the job (same four phases as Analysis / list), count vectors `n` and how many have grade `X` (case-sensitive `X` as today elsewhere); return `Math.round(100 * (n - x) / n)` or `null` when `n === 0`.
3. Add `extractAgentPayloadText(responseContent: string): string`:
   - `JSON.parse` the RESPONSE `content` when it is JSON; if `agent_payload` is a string, return it (parse already unescapes `\n` / quotes); if `agent_payload` is a non-null object, return `JSON.stringify(agent_payload, null, 2)`; if parse fails or key missing, return `""`.
   - Do **not** pretty-print the whole RESPONSE envelope as the Discussion body.
4. Grep `printResumeVisible` / `printCoverVisible` / `materialsPreviewVisible` usages. After Stage 3 will move Print to Artifacts, **retire** any helper that becomes unused (delete export + body). Keep helpers still used by Artifacts Print.
5. In `JobsRecommended.tsx`, delete the local `totalScore` function; import from `../lib/recommendedJobReport`. Do not change Total column formatting or sort.
6. `npx tsc --noEmit` (or the repo’s usual frontend typecheck) for the touched TS files; fix only type errors introduced here.
7. Commit: `code(AST-2234): share totalScore + thermometer/payload helpers`. Publish to `origin/sub/AST-2226/AST-2234-modal-panes-and-wiring`.

⚠️ **Decision:** Gradable % counts grade vectors across JD/DO/GET/LIKE only (Analysis phases), not Summary or other tabs — matches parent AC wording “across all phases”.

---

## Stage 2: Discussion pane — headers + `agent_payload` body

**Done when:** For a story hop with `agent_name=Estelle`, `task_name=Contemplate Job`, and `created_at` set, the section header string is `Estelle's Contemplate Job @ m/d/yy hh:mm am/pm` (12-hour, **no seconds**) in the selected candidate’s timezone; body textarea shows unescaped `agent_payload` prose, not pretty-printed full RESPONSE JSON.

1. In `JobDiscussionPane.tsx`, import `extractAgentPayloadText` and `useCandidate` (same tz resolution as `Time.tsx`: `candidate_data.contact.timezone` or `"UTC"`).
2. Replace `formatDiscussionContent` / `responseBodyForTask` so the body is `extractAgentPayloadText(block.content)` for the first non-empty RESPONSE block (keep empty-RESPONSE skip parity with today).
3. Keep filtering sections to hops with non-empty body.
4. When building / rendering each visible section’s `nav_label`, resolve the matching `AgentStoryEntry` and format:
   - `agentLabel = (entry.agent_name || entry.agent_id || "").trim()` — if still empty, fall back to `section.nav_label`’s agent side only via existing manifest label behavior: use `task_key` as agent fallback is N/A; **fallback when `agent_name` blank:** use whatever identity the entry already exposes (`task_key` is not the agent — use blank agent → fall back to full prior `section.nav_label` from manifest for that hop, or `agent_id` if present on entry). Concrete rule: `name = strip(entry.agent_name) || strip(String(entry.agent_id || "")) || "Agent"`; `task = strip(entry.task_name) || strip(entry.task_key) || section.nav_label`; stamp from `entry.created_at` via `Intl.DateTimeFormat("en-US", { timeZone: tz, year: "2-digit", month: "numeric", day: "numeric", hour: "numeric", minute: "2-digit", hour12: true })` joined as `m/d/yy hh:mm am/pm` (comma optional — match AC `Estelle's Contemplate Job @ 3/5/26 4:48 pm` style: one `@` separator, no seconds).
   - Final label: `` `${name}'s ${task} @ ${stamp}` ``; if `created_at` missing, omit ` @ ${stamp}` (still show `name's task`).
5. Pass overridden `nav_label` into `ReportSectionList` (map sections before render). Do not edit `ReportSectionList.tsx` (out of Scope).
6. Typecheck; commit: `code(AST-2234): Discussion agent_payload + named headers`. Publish.

⚠️ **Decision:** Header formatting lives in the pane (not `fmt.ts`) so Scope stays inside listed files; seconds intentionally omitted vs `fmtTime`.

---

## Stage 3: Modal shell — detail fields, header actions, tabs, JD, Analysis chrome, Artifacts

**Done when:** Modal lands on Analysis; Job Description tab shows JD default-expanded; empty Artifacts tab absent with header Generate; populated/in-progress Artifacts tab present without header Generate; Skip/Applied gated by `can_skip`/`can_apply`; Applied notes success closes+refreshes once; Analysis shows thermometers + total+gradable; header Print/Copy props no longer passed; Artifacts Print works on non-mobile when content exists; ≤1023px Artifacts has no Edit and does not open edit.

1. **Extend local `JobDetail`** in `JobAnalysisReportModal.tsx` with optional: `company_name`, `company_website`, `discovered_at`, `recommended_at`, `applied_at`, `can_apply` (keep `can_skip`). Prefer detail `company_website` over the secondary company GET; remove the company GET once unused.
2. **Modal title / header identity:** pass `companyName={job.company_name?.trim() || job.company}` only as last-resort when `company_name` null (payload contract: siblings show `company_name` when present). Pass lifecycle props per #2 contract table.
3. **Stop passing** Copy and header Print props/handlers to `RecommendedJobReportHeader`. Delete dead copy/print state/handlers that become unused in this file.
4. **Skip:** keep `onSkip` only when `job.can_skip` (unchanged success/fail toast behavior).
5. **Applied notes (local state):**
   - State: `appliedNotesOpen: boolean`, `appliedBusy: boolean`.
   - `onApplied` when `job.can_apply`: set `appliedNotesOpen=true`.
   - Render `CandidateActionNotesModal` stacked (`open={appliedNotesOpen}`, `action="applied"`, `busy={appliedBusy}`).
   - On confirm: `postCandidateAction(jobId, "applied", notes)`; on success `setAppliedNotesOpen(false)`, `onRefresh?.()`, `onClose()`; on failure toast error, keep report modal + notes modal open (or notes open — failure must not close the report).
6. **Artifacts tab visibility:** build `topTabs` from manifest as today, but **omit** `artifacts` when `!anyReportArtifactContent(artifacts, artifactTabs) && !isArtifactsBuildInProgress(job.state)`. Keep meteorite omit rule.
7. **Generate in header:** when Artifacts tab omitted, pass `onGenerateArtifacts` that runs the same `generate_artifacts` primary action path as today’s empty Artifacts strip (`runPrimaryAction` / `postGenerateArtifacts` — reuse existing in-modal generate behavior including close-after-generate). When Artifacts tab present, do **not** pass Generate to the header; empty strip inside the tab goes away because the tab is hidden when empty.
8. **Job Description tab:** when `activeTopTab === "job_description"`, render a `ReportSectionList` (or single collapsible) with one section, `default_expanded: true`, body = same JD text as today’s `raw_jd` renderer (`job_data.job_description` normalize). Remove any remaining `raw_jd` handling from Summary section building (Summary must not list `raw_jd` even if an old manifest still sends it — filter it out client-side).
9. **Analysis chrome:**
   - Above or beside the phase section list, render job `totalScore(job, phaseScoreFields)` with `formatPhaseScore`, and immediately to its right the gradable `%` (or `N% gradable` label) inside `recommended-report-total-gradable`. Hide % when helper returns `null`.
   - For each Analysis phase that has a finite list score **and** breakdown `max > 0`, render a thermometer in the section header metadata (or directly under the section title): track + fill width `${fillRatio * 100}%`, `title`/`aria` tooltip per Stage 1. Keep existing grade-confidence metadata row.
10. **Artifacts Print (non-mobile):** in populated Artifacts pane, add a **Print** control that opens the existing print HTML path (`fetchPrintHtml` + `openHtmlInNewTab` for resume and/or cover as appropriate — prefer one Print that prints the drafted artifact text already printable today). Do not put Print on the header.
11. **Mobile band (≤1023px):** `window.matchMedia("(max-width: 1023px)")` with listener (same band as App.css / parent AC). When mobile and Artifacts populated:
    - No Edit button; thumbnail/`PrintPreview` `onClick` must **not** call `setEditTab`.
    - Show read-only drafted text (reuse hydrated artifact body / existing preview read path) + Print.
    - Ensure `editTab` stays `null` on mobile (if a stale tab is set, clear it when entering mobile).
12. Typecheck; commit: `code(AST-2234): modal panes — tabs, actions, Analysis chrome`. Publish.

⚠️ **Decision:** Generate moves to the header only when the Artifacts tab is filtered out; in-progress builds still show the Artifacts tab with Generating…/Cancel (no header Generate duplicate).

⚠️ **Decision:** If #2 header is not merged yet and TypeScript rejects new props, add the props to a **local** temporary type assertion on the JSX spread **only if** the header component props have not been updated — prefer matching Hedy’s landed Props; if build is blocked by missing props on still-old header, stop and comment on AST-2234 naming the mismatch (do not edit `RecommendedJobReportHeader.tsx`).

---

## Stage 4: `JobArtifactEditModal` mobile read-only + Print

**Done when:** At ≤1023px, opening/remaining on this modal never mounts the edit left pane; UI is read-only drafted text + Print only. Desktop path unchanged.

1. In `JobArtifactEditModal.tsx`, detect `(max-width: 1023px)` the same way as Stage 3.
2. When mobile and `tab` is non-null: do **not** render `ResumeContentEditor` / `ArtifactEditor` / `SplitPanePage` edit layout. Render read-only drafted text for that tab’s artifact + a Print control using the same `fetchPrintHtml` / `PrintPreview` target kinds as today (`job_resume` vs `cover`).
3. When desktop: keep current stacked editor + live preview behavior.
4. Typecheck; commit: `code(AST-2234): JobArtifactEditModal mobile read-only Print`. Publish.

⚠️ **Decision:** Stage 3 already prevents opening edit on mobile; Stage 4 is the Scope-required defense inside `JobArtifactEditModal` so a stray open cannot edit.

---

## Execution contract

Binding. Execute stages in order. Do not add files outside Files Changed. Do not edit `RecommendedJobReportHeader.tsx` or `App.css`. When a referenced name/signature drifted, or #2 prop names differ from this plan’s table, stop and comment on **parent AST-2226**:

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

Each stage is one commit on the epic worktree, published to
`origin/sub/AST-2226/AST-2234-modal-panes-and-wiring` before the next stage starts.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-2234
**Overall:** APPROVED
**Corpus:** 65a2864973ecf09fd57732c2cfc9a4e1ff3e0b91 (tree `canon/` at publish tip; no `docs/canon-index.md` on ref)
**Publish ref:** `origin/sub/AST-2226/AST-2234-modal-panes-and-wiring` @ `cd0a58a97f05070f8900a73c4d63a4487622dd65`

## Canon scores

patt.artifact.ui-consistency | A | |
patt.artifact.read-current | A | |

## Traceability

AC 3 → Stage 3 (`can_skip` / `can_apply` gate header callbacks only); AC 4 → Stage 3 Applied notes + `postCandidateAction`; AC 5 → Stage 3 Artifacts Print (non-mobile); AC 6 → Stages 1–2 `extractAgentPayloadText` + Discussion body; AC 7 → Stage 2 header format + tz; AC 8 → Stages 3–4 mobile band ≤1023px no Edit; AC 9 → Stage 3 JD pane + manifest tab (config from #1); AC 10 → Stage 3 tab filter + header Generate mutual exclusion; AC 11 → Stages 1–3 thermometer fill/tooltip vs `jobScoreBreakdownForGradesField`; AC 12 → Stages 1–3 shared `totalScore` + job gradable % over four phase `*_grades`. Parent functional items 2–5, 10–13 (modal slice) addressed; Copy/header chrome strip partially depends on #2 but this plan correctly stops passing Copy/Print props from the modal.

## Findings

**discuss** — Linear assignee is Ada, not Joan; Chuckles should assign Joan before validate spawn convention — review completed per explicit spawn.

**acceptable** — Prerequisite gate on AST-2232 detail fields, #2 prop contract table, UAT fitness (wrong-fix list), and explicit scope gate match parent partition; Files Changed stay inside ticket Scope; decision to duplicate notes wiring in-modal (not hook) matches Scope preference.

**acceptable** — `patt.artifact.ui-consistency` Exception #2 (legacy job modal props) explicitly honored; no `bodyShape` rewrite. Print/mobile/read-only paths reuse existing artifact/print helpers — no parallel client storage (`read-current` intent).

**discuss** — Stage 2 step 4 header fallback prose is tangled before the concrete `name`/`task`/`stamp` rule; executable once builder follows the final bullets — tighten in plan optional, not blocking.

**discuss** — `extractAgentPayloadText` falls back to `JSON.stringify` when `agent_payload` is an object; AC 6 targets string prose — rare shape; note for Betty if fixtures use object payloads.

**discuss** — Build ordering: Stage 3 expects #2 header props/CSS classes; plan documents stop-on-mismatch and temporary assertion escape — parallel landing with AST-2233 remains the main integration risk (execution, not plan gap).

**discuss** — Canon Scope is only the two artifact patterns; `astral.ui.frontend-file-placement` / layer import rules are not frozen on the ticket — all touches stay in listed frontend paths (Archie convention only).

**Definition fidelity (R6):** Stages map to Scope files; no backend/App.css/header component edits. Estimate confirm present. Plan Discuss rounds: 0.

context_tokens≈52000

## Review

- **Publish ref:** `origin/sub/AST-2226/AST-2234-modal-panes-and-wiring`
- **Tip:** `95bf9db39d1b28c844afea3a4a975311b7e039d9`
- **Stages landed:** 1 helpers · 2 Discussion · 3 modal panes · 4 mobile JobArtifactEditModal
- **Note:** Header props cast to AST-2233 contract (`TriageHeader`); #2 not yet on ftr at build time — runtime chrome lands when AST-2233 merges.

## Radia review

[code-rubric]
**Ticket:** AST-2234
**Publish ref:** `origin/sub/AST-2226/AST-2234-modal-panes-and-wiring` @ `0f52cd7cc63bf0296da850210de4e0da89aaf27a`
**Corpus:** `b7ab2203048ce0beb2869a12200ab7fa696c8066`
**Overall:** CLEAN

## Canon scores

patt.artifact.ui-consistency | A | |
patt.artifact.read-current | A | |

## Column diff vs plan stage

(aligned) — Joan: both patterns **A** at plan; code review matches.

## Frame diff

- [ ] **Integration:** Parent / epic UAT assumes AST-2233 header + `App.css` hooks on the same integration line as this tip (`RecommendedJobReportHeader` still legacy Copy/Print on this ref; modal uses `TriageHeader` cast).

## Findings

**fix-now**

(none)

**discuss**

- **Sibling #2 not on this ref:** `RecommendedJobReportHeader.tsx` / `App.css` on the tip are still pre–AST-2233; modal passes `discoveredAt` / `onApplied` / `onGenerateArtifacts` via `TriageHeader = RecommendedJobReportHeader as unknown as ComponentType<TriageHeaderProps>`, so triage chrome and thermometer/date/website CSS do not render until AST-2233 merges into `ftr`. @susan — treat epic UT as blocked on merge order, not as a defect in AST-2234 scope files? **Default:** `merge-child` AST-2233 into `ftr` before parent User Testing; keep AST-2234 as-is (no header/CSS edits here).

**advisory**

- **sibling product carry:** AST-2232 backend/seed/config (`src/core/*`, `database.py`, `api_jobs.py`, `config.py`, `agent.json`) appears in the three-dot diff via `ftr` lineage — expected on a stacked sub; not AST-2234 scope.
- **sibling test carry:** `tests/**` + `docs/test-bible/**` include Betty manifests for 2232/2233/2234 siblings.
- **Company row fetch retained:** `load()` still calls `/api/companies/...` for **company_upshot** only; `company_website` comes from detail (AST-2232) — matches sibling contract intent.
- **Issue doc note:** Engineer already documents `#2 not yet on ftr at build time` under **Review**.

## Plan fidelity (§5.4)

- Scope files only in AST-2234 commits: `JobAnalysisReportModal`, `JobDiscussionPane`, `recommendedJobReport.tsx`, `JobsRecommended.tsx`, `JobArtifactEditModal` — no `RecommendedJobReportHeader`, `App.css`, backend, or `candidateJobActions` / `useCandidateJobActions` (0-line diff).
- Wiring: `can_skip` / `can_apply` gate Skip/Applied; Applied uses notes modal + `postCandidateAction`; Artifacts tab hidden when empty + not build-in-progress with header Generate; JD tab + Summary without `raw_jd`; Discussion uses `agent_name` / `task_name` + candidate-TZ stamp and `extractAgentPayloadText`; Analysis thermometers + `recommended-report-total-gradable`; Artifacts Print in pane; mobile `JobArtifactEditModal` read-only + Print (≤1023px).
- Estimate **3** still fits (five frontend files + tests).

## What's solid

- Pattern exception for Job Analysis Report Modal (no forced `bodyShape` migration); Print/read-only paths reuse `fetchPrintHtml` / existing editors.
- `extractAgentPayloadText` targets RESPONSE `agent_payload` only — not whole-envelope pretty-print.
- Server-gated triage legality — no hard-coded prior-state sets in React.

## Recommended actions (downstream — not taken here)

- Chuckles: append artifact, `docs(AST-2234): Radia review — clean`, push, post slim upshot `--as radia`, **Review Posted**.
- Before parent UT: ensure `ftr` includes AST-2233 so header/CSS match modal props (no `resolve-child` header edits on 2234).
