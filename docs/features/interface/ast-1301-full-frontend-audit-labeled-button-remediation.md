# AST-1301 — Full frontend audit + labeled-button remediations (Button consistency)

- **Linear:** [AST-1301](https://linear.app/astralcareermatch/issue/AST-1301/full-frontend-audit-labeled-button-remediation-button-consistency)
- **Parent:** [AST-1166](https://linear.app/astralcareermatch/issue/AST-1166/button-consistency)
- **Publish ref:** `sub/AST-1166/AST-1301-full-frontend-audit-labeled-button-remediation`

After AST-1300 landed `pattern.ui.shared-button-roles` and unused `.btn` / `.icon-control` CSS, this ticket maps every labeled `<button>` (and button-styled labeled action) in `src/ui/frontend` to a catalog class or a named exception, then remediates call sites onto `btn primary` / `btn secondary` / `btn danger` / `btn primary in-flight`. It does not land pattern docs and does not remediates list icon-controls (AST-1302).

## Traceability

| Parent / child item | This plan |
|---------------------|-----------|
| Parent AC2 — inventory of every labeled button | Inventory + Named exceptions (this doc is the inventory) |
| Parent AC3 — Manage Email, list bulk/toolbar, modal footers, detail/edit save bars, exports on shared classes | Stages 1–4 |
| Parent AC4 — retire `dep-btn` vs `modal-btn` and gold-bulk vs green-save as separate systems | Stages 1–4 (call sites) + Stage 5 (delete leftover CSS) |
| Parent AC5 — list row icon-controls only | N/A — AST-1302. Labeled text that happens to sit in a row is class-swapped here, not converted to icons |
| Parent AC6 — one gold in-flight treatment wherever busy already exists | Stage 2 in-flight className swaps only; do not add `in-flight` where it is absent today |
| Parent AC7 — no enablement / action regression | Hard rule on every stage: do not change `onClick`, `disabled`, `type`, labels, or gating expressions |
| Child AC 2–6 (same sentences as parent AC2–4, AC6–7) | Same rows |
| Child boundary — does not land pattern docs | Do not edit `canon/patterns/**` |
| Child boundary — does not own list icon-control remediations | Do not edit `CandidateJobRowActions.tsx`, `CollapsiblePanel.tsx`, `list-page-edit-btn`, `modal-close`, `job-list-icon-btn`, `sql-hist-btn` |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/Modal.tsx` | Footer Cancel/Save → catalog classes; leave `modal-close` | ui |
| `src/ui/frontend/src/components/ListPage.tsx` | Bulk actions → catalog classes | ui |
| `src/ui/frontend/src/components/DetailsEditPage.tsx` | Cancel/Save → catalog classes | ui |
| `src/ui/frontend/src/components/ProfileTextPage.tsx` | Cancel/Save → catalog classes | ui |
| `src/ui/frontend/src/components/ContextTextPage.tsx` | Cancel/Save → catalog classes | ui |
| `src/ui/frontend/src/components/FormFields.tsx` | Remove/Add string-list buttons → catalog classes | ui |
| `src/ui/frontend/src/components/UserPrompt.tsx` | Confirm footer → catalog classes | ui |
| `src/ui/frontend/src/components/RepoJsonDivergenceBanner.tsx` | Revert → `btn secondary`; drop size override | ui |
| `src/ui/frontend/src/components/SectionExpandChrome.tsx` | Expand/Collapse all → `btn secondary` | ui |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Generate/Cancel/Save/confirm → catalog; drop `#ff6b6b` override | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Generate / in-flight / cancel-build → catalog | ui |
| `src/ui/frontend/src/components/JobDetailModal.tsx` | Skip This Job → `btn secondary` | ui |
| `src/ui/frontend/src/components/IntakeChatModal.tsx` | Send / Generate Profile / New session → catalog | ui |
| `src/ui/frontend/src/components/IntakePreamblePanel.tsx` | Cancel / Continue / Submit → catalog | ui |
| `src/ui/frontend/src/components/IntakeTopicMenuPanel.tsx` | Done / Cancel / Send / Accept → catalog | ui |
| `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx` | Copy links + Print → catalog | ui |
| `src/ui/frontend/src/pages/AdminManageEmail.tsx` | Toolbar three actions → catalog | ui |
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Run/Stop/Stop All/Add/modals → catalog; drop color overrides | ui |
| `src/ui/frontend/src/pages/AdminManageCandidates.tsx` | Labeled actions only → catalog; leave `list-page-edit-btn` | ui |
| `src/ui/frontend/src/pages/AdminAgentPrompts.tsx` | Add/Delete/Preview → catalog | ui |
| `src/ui/frontend/src/pages/AdminAgentTimesheets.tsx` | Export CSV → `btn primary` | ui |
| `src/ui/frontend/src/pages/AdminCostReconciliation.tsx` | Export CSV → `btn primary` | ui |
| `src/ui/frontend/src/pages/AdminDataManagement.tsx` | Update/Run/Copy → catalog; leave `sql-hist-btn` | ui |
| `src/ui/frontend/src/pages/AdminScheduledQueries.tsx` | Bare `dep-btn` → role per inventory | ui |
| `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx` | Preview/Test/Save As/confirms → catalog | ui |
| `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` | Preview Resolved → `btn secondary` | ui |
| `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx` | Parse/view/open → catalog | ui |
| `src/ui/frontend/src/pages/AdminSessionCoverLetter.tsx` | Open HTML → `btn primary` | ui |
| `src/ui/frontend/src/pages/AdminManageSlack.tsx` | Listen/debug toggles → `btn secondary` | ui |
| `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` | Copy logs → `btn secondary` | ui |
| `src/ui/frontend/src/pages/JobsSkipped.tsx` | Retry → `btn primary`; leave section headers | ui |
| `src/ui/frontend/src/pages/CompaniesNewList.tsx` | Import CSV → `btn primary` | ui |
| `src/ui/frontend/src/pages/CandidateIntake.tsx` | Start over / Continue → catalog | ui |
| `src/ui/frontend/src/pages/CandidateProfile.tsx` | Clear / Cancel / Save → catalog | ui |
| `src/ui/frontend/src/pages/CandidateSurfer.tsx` | Opt-out → `btn secondary` | ui |
| `src/ui/frontend/src/pages/CandidateSurferConsent.tsx` | Opt-in / Decline → catalog | ui |
| `src/ui/frontend/src/pages/ArtifactsCompanySearchTerms.tsx` | Generate/Cancel/Save/Yes → catalog | ui |
| `src/ui/frontend/src/pages/LogOffScreen.tsx` | Refresh → `btn primary` | ui |
| `src/ui/frontend/src/App.css` | Delete leftover labeled-family rules listed in Stage 5 | ui |

**Do not touch:** `canon/patterns/**`; `CandidateJobRowActions.tsx`; `CollapsiblePanel.tsx`; `NavigationShell.tsx`; `SideTabPanel.tsx`; `TabbedTextArea.tsx`; `AgentAnalysisHeader.tsx`; `ArtifactsBaseResumeContent.tsx`; `AdminVectorFeedback.tsx`; `JobsInReview.tsx`; `src/ui/api/**`; `src/utils/config.py`; `docs/ASTRAL_CODE_RULES.md`; `tests/**`; `docs/test-bible/**`. Do not add `Button.tsx` or a second stylesheet. Do not edit `.btn` / `.icon-control` rules landed by AST-1300 (including `#fff` on `.btn.danger`).

## Hard rules (every stage)

1. Presentation only. Do not change `onClick`, `disabled={…}`, `type`, visible label text, `aria-label`, `title`, or gating expressions (including `disabled={!landEnabled}` on Land Meteorite and Scheduled Actions `opacity` / `pointerEvents` / `disabled` that encode auto-mode / running).
2. Markup is space-separated catalog classes only: `btn primary`, `btn secondary`, `btn danger`, `btn primary in-flight`. Never BEM (`btn--primary`). Never bare `btn`. Never keep `modal-btn` / `dep-btn` / `list-page-bulk-btn` / `timesheet-export-btn` / `entity-skip-btn` / `dispatch-log-copy-btn` on a remediates control.
3. Layout-only extras may remain when they are not a second look: `dep-string-list-add`, `intake-generate-btn`, `style={{ marginTop: 8 }}`, `style={{ marginRight: 8 }}`, `style={{ marginLeft: 8 }}`, Stop overlay `position` / `inset` / `whiteSpace`.
4. Delete theme/size overrides that recreate a parallel family: `style={{ background: … }}`, `style={{ color: "var(--danger)" }}` on a labeled button, `padding` / `fontSize` / `minWidth` on labeled actions. Shared `.btn` size/weight is the catalog.
5. Add `in-flight` only where that class (or `save in-flight`) already exists. Text swaps like `"Running..."` / `"Parsing…"` without `in-flight` stay text-only.
6. Do not convert any control to `icon-control`. That is AST-1302.

## Class swap cheat sheet

| Old | New |
|-----|-----|
| `modal-btn save` / `dep-btn save` | `btn primary` |
| `modal-btn save in-flight` / `dep-btn save in-flight` / `` `… save${cond ? " in-flight" : ""}` `` | `btn primary` + ` in-flight` when `cond` |
| `modal-btn cancel` / `dep-btn cancel` | `btn secondary` |
| `modal-btn danger` / `dep-btn danger` / `list-page-bulk-btn danger` | `btn danger` |
| `list-page-bulk-btn` (no danger) / `timesheet-export-btn` | `btn primary` |
| `entity-skip-btn` | `btn secondary` |
| `dispatch-log-copy-btn` / `recommended-report-copy-link` | `btn secondary` |
| Bare `dep-btn` | Role from Inventory — never leave bare `btn` |
| `modal-btn save` + `style={{ background: "#c0392b" }}` or `"#ff6b6b"` | `btn danger` and **delete** the background style |
| `` `list-page-bulk-btn${action.variant === "danger" ? " danger" : ""}` `` | `action.variant === "danger" ? "btn danger" : "btn primary"` |
| `` `modal-btn${pending.variant === "danger" ? " danger" : " save"}` `` | `pending.variant === "danger" ? "btn danger" : "btn primary"` |

⚠️ **Decision:** Gold `list-page-bulk-btn` becomes green `btn primary`. Parent retired gold-bulk vs green-save as two systems. Idle bulk is a page action, not a busy state. Gold is only `btn primary in-flight`.

⚠️ **Decision:** Modal labeled Skip ("Skip This Job") is `btn secondary`, not `btn danger` and not `icon-control`. Skip is reversible (Retry on Skipped). Parent: use secondary or danger by product meaning; AST-1300 Notes: modal labeled Skip stays a labeled `btn`.

⚠️ **Decision:** Destructive confirms that today fake danger with a red `background` on `save` become `btn danger`: Kill All, confirm-regen Yes/Regenerate, Yes Replace/Overwrite. Stop All (header) is always `btn danger` (disabled when no threads) — it is a kill action, not a primary that turns red.

⚠️ **Decision:** Compact per-row Run/Stop on Scheduled Actions still remediates to `btn primary` / `btn danger`. There is no compact labeled size in the catalog. Keep overlay layout (`position`, `inset`, `whiteSpace`) and enablement (`opacity`, `pointerEvents`, `disabled`). Drop `padding` / `fontSize` / `background` / `color` overrides including `#c0392b` and `#7d6608`.

## Inventory (AC2)

Every labeled `<button>` / button-styled labeled action in `src/ui/frontend`. Icon-only and chrome exceptions are in the next table — they are inventoried so the sweep is complete.

| File | Control (visible text / role) | Today | Catalog |
|------|-------------------------------|-------|---------|
| `Modal.tsx` | Cancel | `modal-btn cancel` | `btn secondary` |
| `Modal.tsx` | Save | `modal-btn save` | `btn primary` |
| `ListPage.tsx` | bulk `action.label` | `list-page-bulk-btn` / `… danger` | `btn primary` / `btn danger` |
| `DetailsEditPage.tsx` | Cancel / Save | `dep-btn cancel` / `save` | `btn secondary` / `btn primary` |
| `ProfileTextPage.tsx` | Cancel / Save | same | same |
| `ContextTextPage.tsx` | Cancel / Save | same | same |
| `FormFields.tsx` | Remove | `dep-btn cancel` | `btn secondary` |
| `FormFields.tsx` | Add | `dep-btn cancel dep-string-list-add` | `btn primary dep-string-list-add` |
| `UserPrompt.tsx` | cancelLabel | `modal-btn cancel` | `btn secondary` |
| `UserPrompt.tsx` | confirmLabel | `modal-btn save` or `modal-btn danger` | `btn primary` or `btn danger` |
| `RepoJsonDivergenceBanner.tsx` | Revert to file | `dep-btn cancel` + size style | `btn secondary`; delete size style |
| `SectionExpandChrome.tsx` | Expand all / Collapse all | bare `<button>` + `.section-expand-chrome button` | `btn secondary` on both |
| `ArtifactEditor.tsx` | Generate / Generating… / Regenerate | `dep-btn save` + optional `in-flight` | `btn primary` + `in-flight` when `generating`; keep `marginRight: 8` |
| `ArtifactEditor.tsx` | Cancel / Save | `dep-btn cancel` / `save` | `btn secondary` / `btn primary` |
| `ArtifactEditor.tsx` | confirm No / Cancel | `dep-btn cancel` | `btn secondary` |
| `ArtifactEditor.tsx` | confirm Yes / Regenerate | `dep-btn save` + `#ff6b6b` | `btn danger`; delete background style |
| `JobAnalysisReportModal.tsx` | Generating… (disabled) | `modal-btn save in-flight` | `btn primary in-flight` |
| `JobAnalysisReportModal.tsx` | cancel_build (`action.label`) | `modal-btn save` | `btn secondary` |
| `JobAnalysisReportModal.tsx` | Generate | `modal-btn save` + optional `in-flight` | `btn primary` + `in-flight` when `primaryBusy` |
| `JobDetailModal.tsx` | Skip This Job / Skipping… / Already Skipped | `entity-skip-btn` | `btn secondary` |
| `IntakeChatModal.tsx` | Send | `modal-btn save` | `btn primary` |
| `IntakeChatModal.tsx` | Generate Profile | `modal-btn save intake-generate-btn` | `btn primary intake-generate-btn` |
| `IntakeChatModal.tsx` | New intake session | `modal-btn cancel` | `btn secondary` |
| `IntakePreamblePanel.tsx` | Cancel | `modal-btn cancel` | `btn secondary` |
| `IntakePreamblePanel.tsx` | Continue / Submit | `modal-btn save` | `btn primary` |
| `IntakeTopicMenuPanel.tsx` | Done | `modal-btn save` | `btn primary` |
| `IntakeTopicMenuPanel.tsx` | Cancel | `modal-btn cancel` | `btn secondary` |
| `IntakeTopicMenuPanel.tsx` | Send (`ui.send_label`) | `modal-btn cancel` | `btn secondary` (Accept is the commit) |
| `IntakeTopicMenuPanel.tsx` | Accept (`ui.accept_label`) | `modal-btn save` | `btn primary` |
| `RecommendedJobReportHeader.tsx` | Copy Application Email / Copy LinkedIn Profile | `recommended-report-copy-link` | `btn secondary` |
| `RecommendedJobReportHeader.tsx` | Print Resume / Print Cover Letter | `modal-btn cancel` | `btn secondary` |
| `AdminManageEmail.tsx` | Select all | bare toolbar `button` | `btn primary` |
| `AdminManageEmail.tsx` | Clear selection | bare toolbar `button` | `btn secondary` |
| `AdminManageEmail.tsx` | Land Meteorite | bare toolbar `button` | `btn primary`; keep `disabled={!landEnabled}` |
| `AdminScheduledActions.tsx` | per-row Run | `list-page-bulk-btn` + size/opacity styles | `btn primary`; keep opacity/pointerEvents/disabled/`whiteSpace`; drop padding/fontSize |
| `AdminScheduledActions.tsx` | per-row Stop / Draining… | `list-page-bulk-btn` + `#c0392b` / `#7d6608` | `btn danger`; keep position/inset/whiteSpace/disabled; drop background/color/padding/fontSize |
| `AdminScheduledActions.tsx` | Stop All | `list-page-bulk-btn` + conditional red | `btn danger`; delete the style prop |
| `AdminScheduledActions.tsx` | + Add Task | `list-page-bulk-btn` | `btn primary` |
| `AdminScheduledActions.tsx` | Stop-all modal Cancel / Kill All | `modal-btn cancel` / `save` + `#c0392b` | `btn secondary` / `btn danger`; delete background style |
| `AdminScheduledActions.tsx` | Task modal Cancel / Save | `modal-btn cancel` / `save` | `btn secondary` / `btn primary` |
| `AdminManageCandidates.tsx` | Set dispatch tasks | `dep-btn` + size style | `btn primary`; delete size style. Stays labeled in the row — AST-1302 may iconify later |
| `AdminManageCandidates.tsx` | + Add Candidate | `dep-btn save` + size style | `btn primary`; delete size style |
| `AdminManageCandidates.tsx` | Show / Hide (API key) | `dep-btn` + size style | `btn secondary`; delete size style |
| `AdminManageCandidates.tsx` | Clear (API key) | `dep-btn` + size + danger color | `btn danger`; delete size and color styles |
| `AdminAgentPrompts.tsx` | + Add Agent | `dep-btn save` + size | `btn primary`; delete size style |
| `AdminAgentPrompts.tsx` | row Delete | `dep-btn danger` + size | `btn danger`; delete size style. Stays labeled — AST-1302 may iconify later |
| `AdminAgentPrompts.tsx` | Preview Resolved (edit + add) | `dep-btn cancel` + size | `btn secondary`; delete size style |
| `AdminAgentTimesheets.tsx` | Export CSV | `timesheet-export-btn` | `btn primary` |
| `AdminCostReconciliation.tsx` | Export CSV | `timesheet-export-btn` | `btn primary` |
| `AdminDataManagement.tsx` | Update (upsert) | `dep-btn save` + `fontSize: 12` | `btn primary`; delete fontSize style |
| `AdminDataManagement.tsx` | Run / Running... | `dep-btn save` | `btn primary` (no `in-flight` — class absent today) |
| `AdminDataManagement.tsx` | Copy Output | `dep-btn cancel` | `btn secondary` |
| `AdminScheduledQueries.tsx` | New | bare `dep-btn` | `btn primary` |
| `AdminScheduledQueries.tsx` | Save / Update | bare `dep-btn` | `btn primary` |
| `AdminScheduledQueries.tsx` | Edit | bare `dep-btn` | `btn secondary` |
| `AdminScheduledQueries.tsx` | Deactivate / Activate | bare `dep-btn` | `btn secondary` |
| `AdminScheduledQueries.tsx` | Delete | bare `dep-btn` | `btn danger` |
| `AdminAnthropicAdHoc.tsx` | Preview | `dep-btn cancel` | `btn secondary` |
| `AdminAnthropicAdHoc.tsx` | Test | `dep-btn save` + `minWidth: 100` | `btn primary`; delete minWidth |
| `AdminAnthropicAdHoc.tsx` | Save As toggle | `dep-btn cancel` | `btn secondary` |
| `AdminAnthropicAdHoc.tsx` | Yes, Replace / Yes, Overwrite | `dep-btn save` + size | `btn danger`; delete size style |
| `AdminAnthropicAdHoc.tsx` | confirm Cancel ×2 | `dep-btn cancel` + size | `btn secondary`; delete size style |
| `AdminTaskPrompts.tsx` | Preview Resolved | `dep-btn cancel` + size | `btn secondary`; delete size style |
| `AdminSessionResumePaste.tsx` | Parse / Parsing… | `dep-btn save` | `btn primary` (no `in-flight`) |
| `AdminSessionResumePaste.tsx` | View Parsed JSON | bare `dep-btn` | `btn secondary` |
| `AdminSessionResumePaste.tsx` | Open HTML | bare `dep-btn` | `btn secondary` |
| `AdminSessionCoverLetter.tsx` | Open HTML | `dep-btn save` | `btn primary` |
| `AdminManageSlack.tsx` | Enable/Disable listen | bare + padding/fontSize/cursor | `btn secondary`; delete those styles |
| `AdminManageSlack.tsx` | Enable/Disable debug | same + `marginLeft: 8` | `btn secondary`; keep `marginLeft: 8`; delete padding/fontSize/cursor |
| `AdminPerformanceMonitor.tsx` | ⎘ Copy / ✓ Copied | `dispatch-log-copy-btn` | `btn secondary` |
| `JobsSkipped.tsx` | Retry (N) | `list-page-bulk-btn` | `btn primary` |
| `CompaniesNewList.tsx` | Import CSV | `dep-btn save` + size | `btn primary`; delete size style |
| `CandidateIntake.tsx` | Start over | `modal-btn cancel` | `btn secondary` |
| `CandidateIntake.tsx` | Continue | `modal-btn save` | `btn primary` |
| `CandidateProfile.tsx` | Clear signature image | `dep-btn cancel` + `marginTop: 8` | `btn secondary`; keep marginTop |
| `CandidateProfile.tsx` | Cancel / Save | `dep-btn cancel` / `save` | `btn secondary` / `btn primary` |
| `CandidateSurfer.tsx` | off-switch label | bare `<button>` | `btn secondary` |
| `CandidateSurferConsent.tsx` | opt-in label | `modal-btn save` | `btn primary` |
| `CandidateSurferConsent.tsx` | decline label | `modal-btn cancel` | `btn secondary` |
| `ArtifactsCompanySearchTerms.tsx` | Generate / Requesting… / Regenerate | `dep-btn save` + optional `in-flight` | `btn primary` + `in-flight` when `generating`; keep `marginRight: 8` |
| `ArtifactsCompanySearchTerms.tsx` | Cancel / Save | `dep-btn cancel` / `save` | `btn secondary` / `btn primary` |
| `ArtifactsCompanySearchTerms.tsx` | confirm No | `dep-btn cancel` | `btn secondary` |
| `ArtifactsCompanySearchTerms.tsx` | confirm Yes | `dep-btn save` + `#ff6b6b` | `btn danger`; delete background style |
| `LogOffScreen.tsx` | Refresh | bare `<button>` | `btn primary` |

## Named exceptions (not remediates on this ticket)

| File / selector | Why |
|-----------------|-----|
| `NavigationShell.tsx` — `nav-hamburger`, `sidebar-candidate-menu-*` | Nav chrome — not in catalog |
| `TabbedTextArea.tsx` — `tabbed-ta-tab` | Tabs |
| `SideTabPanel.tsx` — ▲▼× and `side-tab-add` | Side-tab chrome |
| `ArtifactEditor.tsx` — tab ▲▼× and `side-tab-add` | Side-tab chrome (same family) |
| `CollapsiblePanel.tsx` — `collapsible-panel-chevron-btn` | Icon-control — AST-1302 |
| `CandidateJobRowActions.tsx` — `job-list-icon-btn` | Icon-control — AST-1302 |
| `AdminManageCandidates.tsx` — `list-page-edit-btn` View/Edit/Delete | Icon-control — AST-1302 |
| `Modal.tsx` / `AdminScheduledActions.tsx` — `modal-close` × | Icon-control — AST-1302 |
| `AdminDataManagement.tsx` — `sql-hist-btn` ▲▼ | Compact glyph — AST-1302 (`pattern.ui.icon-control`) |
| `JobsSkipped.tsx` / `JobsInReview.tsx` — section header `<button>` with chevron + label | Section chrome (not a toolbar action) |
| `ListPage.tsx` — `expand-toggle` more/less | Cell text chrome |
| `AdminScheduledActions.tsx` — `dispatch-status-badge` ON/OFF | Status-badge toggle, not a labeled action |
| `AdminPerformanceMonitor.tsx` / `AdminVectorFeedback.tsx` — `dispatch-batch-link` | Text link, not a catalog button |
| `AgentAnalysisHeader.tsx` — `analysis-rubric-link` | Rubric text link |
| `ArtifactsBaseResumeContent.tsx` — `base-resume-accent-swatch` | Color-swatch chrome |

---

## Stage 1: Shared shells, confirm, form lists

**Done when:** Modal footer, ListPage bulk bar, Details/Profile/Context save bars, FormFields Add/Remove, UserPrompt confirm, RepoJson revert, and SectionExpandChrome all use catalog classes. `rg -n 'modal-btn|dep-btn|list-page-bulk-btn' src/ui/frontend/src/components/{Modal,ListPage,DetailsEditPage,ProfileTextPage,ContextTextPage,FormFields,UserPrompt,RepoJsonDivergenceBanner,SectionExpandChrome}.tsx` is empty. `modal-close` and `expand-toggle` are unchanged.

1. `Modal.tsx`: `modal-btn cancel` → `btn secondary`; `modal-btn save` → `btn primary`. Leave `modal-close`.
2. `ListPage.tsx`: replace the bulk `className` template with `action.variant === "danger" ? "btn danger" : "btn primary"`.
3. `DetailsEditPage.tsx`, `ProfileTextPage.tsx`, `ContextTextPage.tsx`: Cancel → `btn secondary`, Save → `btn primary`.
4. `FormFields.tsx`: Remove → `btn secondary`. Add → `btn primary dep-string-list-add` (keep `dep-string-list-add`).
5. `UserPrompt.tsx`: cancel → `btn secondary`. Confirm → `pending.variant === "danger" ? "btn danger" : "btn primary"`.
6. `RepoJsonDivergenceBanner.tsx`: `className="btn secondary"`; delete `style={{ fontSize: 12, padding: "4px 12px" }}`. Keep `disabled={reverting}` and the Reverting… label swap.
7. `SectionExpandChrome.tsx`: both buttons `className="btn secondary"`.

## Stage 2: Job, artifact, and intake components

**Done when:** Inventory rows for ArtifactEditor, JobAnalysisReportModal, JobDetailModal, Intake*, RecommendedJobReportHeader are applied. Existing `in-flight` sites still toggle that class on `btn primary` only. `rg -n 'modal-btn|dep-btn|entity-skip-btn|recommended-report-copy-link' src/ui/frontend/src/components/{ArtifactEditor,JobAnalysisReportModal,JobDetailModal,IntakeChatModal,IntakePreamblePanel,IntakeTopicMenuPanel,RecommendedJobReportHeader}.tsx` is empty. Tab ▲▼× / `side-tab-add` in ArtifactEditor are unchanged.

1. `ArtifactEditor.tsx` header Generate: `` className={`btn primary${generating ? " in-flight" : ""}`} ``; keep `marginRight: 8`, `disabled={generating}`, and the Generating…/Requesting…/Regenerate label logic. Cancel → `btn secondary`. Save → `btn primary`. Confirm No/Cancel → `btn secondary`. Confirm Yes and Regenerate → `btn danger` and **delete** `style={{ background: "#ff6b6b" }}`. Do not edit tab-rail buttons.
2. `JobAnalysisReportModal.tsx`: disabled Generating… → `btn primary in-flight`. Each `cancel_build` button → `btn secondary` (keep `disabled={primaryBusy}` and `action.label`). Generate → `` className={`btn primary${primaryBusy ? " in-flight" : ""}`} ``.
3. `JobDetailModal.tsx`: `entity-skip-btn` → `btn secondary`. Keep `disabled={skipping || alreadySkipped}` and the Already Skipped / Skipping… / Skip This Job ternary.
4. `IntakeChatModal.tsx`: Send → `btn primary`. Generate Profile → `btn primary intake-generate-btn`. New intake session → `btn secondary`.
5. `IntakePreamblePanel.tsx`: both Cancels → `btn secondary`. Continue and Submit → `btn primary`.
6. `IntakeTopicMenuPanel.tsx`: Done → `btn primary`. Cancel → `btn secondary`. Send (`ui.send_label`) → `btn secondary`. Accept → `btn primary`.
7. `RecommendedJobReportHeader.tsx`: both `recommended-report-copy-link` → `btn secondary`. Print Resume and Print Cover Letter → `btn secondary`.

## Stage 3: Admin pages

**Done when:** Inventory rows for every `pages/Admin*.tsx` file in Files Changed are applied. `sql-hist-btn`, `list-page-edit-btn`, `modal-close`, and `dispatch-status-badge` / `dispatch-batch-link` are unchanged. Land Meteorite is still `disabled={!landEnabled}`.

1. `AdminManageEmail.tsx`: Select all → `btn primary`. Clear selection → `btn secondary`. Land Meteorite → `btn primary`. Do not change any `disabled` expression.
2. `AdminScheduledActions.tsx`:
   - Run: `className="btn primary"`. Keep `disabled={isRunning || !!row.auto_mode}` and the opacity/pointerEvents/`whiteSpace` styles. Delete `padding` and `fontSize`.
   - Stop / Draining…: `className="btn danger"`. Keep `position: "absolute"`, `inset: 0`, `whiteSpace`, `disabled={isDraining}`. Delete `padding`, `fontSize`, `background`, `color`.
   - Stop All: `className="btn danger"` and **delete** the entire `style={{ background: …, color: … }}` prop. Keep `disabled={activeThreads.length === 0}`.
   - + Add Task: `btn primary`.
   - Stop-all modal: Cancel → `btn secondary`. Kill All → `btn danger`; delete `style={{ background: "#c0392b" }}`. Leave `modal-close`.
   - Task modal: Cancel → `btn secondary`. Save → `btn primary`. Leave `modal-close`.
   - Leave `dispatch-status-badge` ON/OFF toggles.
3. `AdminManageCandidates.tsx`: Set dispatch tasks → `btn primary`; delete padding/fontSize. + Add Candidate → `btn primary`; delete padding/fontSize. Show/Hide → `btn secondary`; delete padding/fontSize. Clear → `btn danger`; delete padding/fontSize/color. Leave all three `list-page-edit-btn` controls.
4. `AdminAgentPrompts.tsx`: + Add Agent → `btn primary`; delete size style. Row Delete → `btn danger`; delete size style. Both Preview Resolved → `btn secondary`; delete size styles.
5. `AdminAgentTimesheets.tsx` and `AdminCostReconciliation.tsx`: `timesheet-export-btn` → `btn primary`.
6. `AdminDataManagement.tsx`: Update → `btn primary`; delete `fontSize: 12`. Run → `btn primary` (leave `"Running..."` text; no `in-flight`). Copy Output → `btn secondary`. Leave both `sql-hist-btn`.
7. `AdminScheduledQueries.tsx`: New → `btn primary`. Save/Update → `btn primary`. Edit → `btn secondary`. Deactivate/Activate → `btn secondary`. Delete → `btn danger`.
8. `AdminAnthropicAdHoc.tsx`: Preview → `btn secondary`. Test → `btn primary`; delete `minWidth`. Save As toggle → `btn secondary`. Yes, Replace and Yes, Overwrite → `btn danger`; delete size styles. Both confirm Cancels → `btn secondary`; delete size styles.
9. `AdminTaskPrompts.tsx`: Preview Resolved → `btn secondary`; delete size style.
10. `AdminSessionResumePaste.tsx`: Parse → `btn primary`. View Parsed JSON → `btn secondary`. Open HTML → `btn secondary`.
11. `AdminSessionCoverLetter.tsx`: Open HTML → `btn primary`.
12. `AdminManageSlack.tsx`: both toggles → `btn secondary`. Delete padding/fontSize/cursor styles. Keep `marginLeft: 8` on debug. Keep `disabled={busy}` / `disabled={busy || debugEnabled === null}`.
13. `AdminPerformanceMonitor.tsx`: `dispatch-log-copy-btn` → `btn secondary`. Leave `dispatch-batch-link`.

## Stage 4: Candidate, jobs, artifacts, and remaining pages

**Done when:** Remaining Inventory rows are applied. Section headers on JobsSkipped / JobsInReview are unchanged. `rg -n 'modal-btn|dep-btn|list-page-bulk-btn|timesheet-export-btn|entity-skip-btn|dispatch-log-copy-btn|recommended-report-copy-link' src/ui/frontend/src --glob '*.tsx'` is empty.

1. `JobsSkipped.tsx`: Retry → `btn primary`. Do not edit the section-header `<button>`.
2. `CompaniesNewList.tsx`: Import CSV → `btn primary`; delete size style.
3. `CandidateIntake.tsx`: Start over → `btn secondary`. Continue → `btn primary`.
4. `CandidateProfile.tsx`: Clear signature → `btn secondary`; keep `marginTop: 8`. Cancel → `btn secondary`. Save → `btn primary`.
5. `CandidateSurfer.tsx`: opt-out button → `btn secondary`. Keep `disabled={busy}` and `dto.off_switch_button_label`.
6. `CandidateSurferConsent.tsx`: opt-in → `btn primary`. Decline → `btn secondary`.
7. `ArtifactsCompanySearchTerms.tsx`: same Generate/Cancel/Save/No/Yes mapping as ArtifactEditor (including `in-flight` on Generate and `btn danger` for Yes; delete `#ff6b6b`).
8. `LogOffScreen.tsx`: Refresh → `btn primary`. Keep `data-testid="logoff-refresh"` and `type="button"`.

## Stage 5: Retire leftover labeled CSS

**Done when:** Leftover labeled-family rules listed below are gone from `App.css`. Layout wrappers remain. AST-1300 `.btn` / `.icon-control` blocks (TOC 14–15) are unchanged. Icon-control leftover families used by AST-1302 remain. Both verify commands at the end of this stage exit 0 with no matches.

Delete these rule blocks only (do not retouch surrounding rules):

1. `.list-page-bulk-btn`, `:hover`, `.danger`, `.danger:hover`. **Keep** `.list-page-bulk-bar`.
2. `.modal-btn` and `.modal-btn.cancel` / `.save` / `.save.in-flight` / `.danger` plus their hover/disabled companions. **Keep** `.modal-close` and `.modal-footer`.
3. `.dep-btn` and `.dep-btn.cancel` / `.save` / `.save.in-flight` / `.danger` plus hover/disabled companions. **Keep** `.dep-actions`, `.dep-input`, `.dep-string-list-add`.
4. `.timesheet-export-btn` and `:hover`.
5. `.dispatch-log-copy-btn` and `:hover`. **Keep** `.dispatch-log-toolbar`.
6. `.manage-email-toolbar button` and `.manage-email-toolbar button:disabled`. **Keep** `.manage-email-toolbar` (flex/gap).
7. The `/* ---- Skip button ---- */` comment and `.entity-skip-btn` plus hover/disabled.
8. `.recommended-report-copy-link` (the look block). **Keep** `.recommended-report-links` and `.recommended-report-copy-feedback`.
9. `.section-expand-chrome button` and `:hover`. **Keep** `.section-expand-chrome` (flex/gap).

Do **not** delete: `.btn` / `.icon-control` (AST-1300), `.sql-hist-btn`, `.job-list-icon-btn`, `.list-page-edit-btn`, `.modal-close`, `.collapsible-panel-chevron-btn`, `.expand-toggle`, `.dispatch-status-badge`, `.dispatch-batch-link`, `.side-tab-add`, `.tabbed-ta-tab`, `.nav-hamburger`, `.intake-generate-btn`.

Verify (must print no matches):

```bash
rg -n 'modal-btn|dep-btn|list-page-bulk-btn|timesheet-export-btn|entity-skip-btn|dispatch-log-copy-btn|recommended-report-copy-link' src/ui/frontend/src --glob '*.tsx'
rg -n '\.modal-btn|\.dep-btn|\.list-page-bulk-btn|\.timesheet-export-btn|\.entity-skip-btn|\.dispatch-log-copy-btn|\.recommended-report-copy-link|\.section-expand-chrome button|\.manage-email-toolbar button' src/ui/frontend/src/App.css
```

⚠️ **Decision:** Do not introduce `--text-on-danger` or change `#fff` on `.btn.danger`. AST-1300 left that literal; this ticket retires the duplicate families, not the token.

## Execution contract

The plan is binding. Execute stages in order; one commit per stage on the epic worktree; publish each stage to `origin/sub/AST-1166/AST-1301-full-frontend-audit-labeled-button-remediation`. Do not edit `tests/`, `docs/test-bible/**`, or `canon/patterns/**`. On ambiguity or codebase drift, stop and comment on the **parent** [AST-1166](https://linear.app/astralcareermatch/issue/AST-1166/button-consistency) with the Stage blocked format from plan-child.

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — labeled `className` swaps across shared components and most pages in `src/ui/frontend`, plus deletion of leftover button-family CSS in `App.css`; no API or config.

**Conf:** `high` — AST-1300 already landed the exact classes; this plan enumerates every labeled control and the exception list; swaps are mechanical.

**Risk:** `Medium` — handlers and enablement stay put, but a wrong role (primary vs danger) would mis-signal Kill All / confirm-regen / Skip, and Scheduled Actions Run/Stop cells will grow to catalog size.

## Rules self-review

| Rule | Status |
|------|--------|
| §1.1 / `astral.standards.in-scope-only` | Labeled remediations only; icon-control files and pattern corpus untouched |
| §1.3 DRY | One leftover family deleted after call sites move; no alias from old selectors onto `.btn` |
| §1.4 / §2.1 config | No `config.py`; no new color enum; `#fff` on danger left as AST-1300 |
| §2.4 / §2.6 | N/A — no batch or state machine |
| §3.3 imports | No new imports |
| §3.5 placement / naming | Styles stay in `App.css`; class names are `btn` + role; no `Button.tsx` |
| `astral.standards.names-not-ticket-ids` | No `ast-1301` in selectors |
| `astral.layers.ui-config-driven-business-logic` | Presentation only; Land Meteorite and other gates unchanged |
| `pattern.ui.shared-button-roles` | Every remediates control pairs `btn` with exactly one role; `in-flight` only on primary |
| `pattern.ui.icon-control` | Cited as out of scope; glyph controls left for AST-1302 |
| Test-tree ban | No `tests/` or bible edits |

No unresolved rule conflicts.
