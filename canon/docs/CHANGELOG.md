# Canon changelog

Every change to directive content, in one place. **Not** loaded at runtime — the
clerk never reads this, and it appears in no index or payload. It exists so a
human can answer "when did this rule change, and why" without walking git log
across 80 files.

Two halves. **Requested** is a queue of change requests filed by audits, none of
them in force. **Executed** is the record of what actually changed. A request
that Archie approves loses its block and gains a row.

---

## Requested

Change requests, filed by audits. **A request is not a change.** Archie approves;
Chuckles or Joan draft the wording; nothing here is in force.

An auditing agent files one when the *same* problem recurs across files — a
directive that is ambiguous, over-broad, or silently unenforceable produces the
same grade for the same reason again and again, and that pattern is evidence a
single confused file is not. One awkward file is a `C`, not a request.

**The requester states the problem, never the fix.** Drafting is Chuckles' and
Joan's; an audit agent is neither. A request that arrives as proposed wording is
a draft that skipped the gate.

### Shape

```markdown
### 2026-08-14 · `stat.layers.import-rules` · audit-stat.layers.import-rules-97699c9e.tsv
**Problem:** "Deferring an import into a function body does not exempt it" reads
as banning all late imports. Half the late imports in `core` are cycle-breaking
within one layer, which the rule permits but does not say.
**Evidence:** 24 of 63 rows graded `C` for this reason; 9 more marked `X` after
manual inspection that the wording should have made unnecessary.
**Cost of not fixing:** plan-stage and code-review passes hit the same ambiguity
every run, and each resolves it differently.
**Status:** pending
```

`Status` is `pending`, `declined <date> — <why>`, or the block is deleted once
executed and a row appears in the log below.

**Declined requests stay.** Deleting one guarantees the next audit rediscovers
the same thing and files it again. The record of a deliberate "no" is what stops
the loop.

### 2026-08-23 · `patt.entity.batch-processing` · audit-patt.entity.batch-processing-97699c9e.tsv
**Problem:** The "UI-driven actions" exemption describes only two shapes — a UI
bulk write, and a UI "run these now" that hands off to the real dispatcher claim
— framed as if a bulk action is always either one call for the whole selection
or a hand-rolled per-entity loop. It says nothing about the common middle shape:
a UI action that groups a selection into a handful of calls (e.g. one POST per
destination state, or a component that collects `selectedIds` and hands the
array to a caller-supplied callback without dictating call shape) rather than
one call for the whole batch or one call per row. Grading these required
inventing a rule the directive doesn't state: that a call carrying an array
counts as compliant so long as it isn't one call per entity.
**Evidence:** Six files needed this same unstated distinction: `JobsSkipped.tsx`
(one `/api/jobs/bulk_state` POST per destination-state group, explicitly noted
as a judgment call), `CompaniesIgnored.tsx` / `CompaniesInactiveList.tsx` /
`CompaniesWatchList.tsx` (row selection → single `bulk_state` POST), `AdminManageEmail.tsx`
("Land Meteorite" → single POST with a `message_ids` array), and
`ListPage.tsx` (defines a generic `BulkAction` interface that only forwards
`selectedIds` to a caller-supplied `onClick`, pushing the one-call-vs-many-calls
decision to whichever page instantiates it — i.e. the shared component itself
carries no shape the directive could check).
**Cost of not fixing:** Every future audit of a bulk-selection UI action re-derives
the same array-vs-loop line from scratch, and a shared component like `ListPage`
has no crisp rule to hold its callers to.
**Status:** pending

### 2026-08-23 · `stat.component.public-then-helpers` · audit-stat.component.public-then-helpers-97699c9e.tsv
**Problem:** The directive's Do/Don't example is drawn from a multi-function
Python module, where moving a public function above its private helpers is a
pure, costless reorder. It does not address the single-export React/TSX
component shape that dominates `src/ui/frontend`: one exported component per
file, backed by local `const`-bound helper functions. Those helpers are not
hoisted (unlike `function` declarations) — a `const` helper used inside the
component must be lexically declared before it, or the reference throws in the
temporal dead zone. The idiom of "one exported component last, small pure
helpers above it" is not authoring-order laziness; it is close to the only
shape that both (a) keeps helpers as `const` and (b) keeps the file to one
export. Grading these files against "public first" produced the same verdict
— clean, fully-grouped, but reversed — over and over, for a reason the
directive never anticipates: the reversal isn't optional here the way it is in
the canonical example.
**Evidence:** 27 of the 132 audited `src/ui/frontend` and `src/ui/extension`
TS/TSX files graded `C` for this identical shape (single default export,
preceded by a clean, non-interleaved block of local helper functions, no other
violation): `components/AdminDeployFooter.tsx`, `components/AgentAnalysisHeader.tsx`,
`components/ArtifactEditor.tsx`, `components/BatchAgentDataModal.tsx`,
`components/ContextTextPage.tsx`, `components/ExperienceJobsEditor.tsx`,
`components/IntakeChatModal.tsx`, `components/IntakePreamblePanel.tsx`,
`components/ListPage.tsx`, `components/NavigationShell.tsx`,
`components/SideTabPanel.tsx`, `components/TokenTextarea.tsx`,
`lib/useListTableColumnMeasure.ts`, `pages/AdminAnthropicAdHoc.tsx`,
`pages/AdminCostReconciliation.tsx`, `pages/AdminManageCandidates.tsx`,
`pages/AdminManageEmail.tsx`, `pages/AdminScheduledActions.tsx`,
`pages/AdminTaskPrompts.tsx`, `pages/AdminVectorFeedback.tsx`,
`pages/ArtifactsBaseResumeContent.tsx`, `pages/CandidateIntake.tsx`,
`pages/CandidateProfile.tsx`, `pages/CandidateSurferConsent.tsx`,
`pages/JobsInReview.tsx`, `pages/JobsRecommended.tsx`, `pages/JobsSkipped.tsx`,
plus `extension/src/lib/surferDisclosureDom.ts`.
**Cost of not fixing:** Every future audit of `src/ui/frontend` recomputes the
same C for the same non-issue across dozens of files, diluting the signal for
files with a real, fixable violation (the four sandwiched-component pages
graded `D` in this same audit, where a helper block appears on *both* sides of
the export — that shape has no hoisting justification and is a genuine miss).
**Status:** pending

---

## Executed

| Date | Directive | Change | Why | Ticket |
|---|---|---|---|---|
| 2026-08-14 | `stat.variables.named-constants` | created | first of five portable statutes | — |
| 2026-08-14 | `stat.functions.clear-names` | created | first of five portable statutes | — |
| 2026-08-14 | `stat.functions.dont-repeat-yourself` | created | first of five portable statutes | — |
| 2026-08-14 | `stat.component.public-then-helpers` | created | first of five portable statutes | — |
| 2026-08-14 | `stat.errors.raise-once-log-once` | created | first of five portable statutes | — |
| 2026-08-14 | `patt.entity.batch-processing` | created | replaces v1 `pattern.batch.entity-claim-process-release`; written from the implementation, arc corrected to release unconditionally in `finally` | — |
| 2026-08-14 | `patt.layers.import-discipline` | rewritten | v1 body restated its own `related_statutes`; now carries the placement decision and cites instead | — |
| 2026-08-14 | `stat.layers.import-rules` | created | the layer direction rule, extracted from v1 `astral.layers.import-direction` | — |
| 2026-08-14 | *all* | `# Scoring` removed | the 1-5 scale is universal and lives in the clerk `USAGE` preamble; per-directive bands break min-wins | — |
| 2026-08-14 | *all* | `status:` removed | status is now the directory a file lives in, not a field | — |
| 2026-08-14 | `stat.layers.import-rules` | amended | added: within `core`, entity data goes through `roster` / `tracker` / `candidate`, never `data.database` directly | — |

## What counts as a change worth a row

Creating, amending, retiring, or renaming a directive. Moving one between
`canon-v2/`, `canon-v2/directives/draft/`, and `canon-v2/directives/archive/` — because that move
*is* the status change. Fixing a typo is not.
| 2026-08-14 | *all* | grade scale changed 1–5 → `A B C D F X` | matches the product's own grade set (`GRADE_VALUES`, `astral.agent.grade-vector-validation`); `X` makes not-applicable a first-class answer | — |
| 2026-08-14 | *all* | effort rating 1–5 added to findings | grades say whether to act; effort says what acting costs | — |
| 2026-08-14 | *structure* | canon made self-contained | `canon/docs`, `canon/directives/{active,archive,draft}`, `canon/audit`, clerk and `instruction_preamble.md` at root. Nothing under `docs/` — the corpus is too tightly coupled to team-chuckles to live in two trees | — |
| 2026-08-14 | *all* | id prefixes `s.`/`p.`/`o.` → `stat.`/`patt.`/`orch.` | kind is legible in a directory listing; subfolders per kind removed | — |
| 2026-08-14 | `directive-readiness-prompt` | renamed `directive-audit-prompt` | readiness is moot — the sweep is an audit, and it now emits grades and effort | — |
| 2026-08-14 | *audit* | output is one TSV per directive per commit — `file`, `grade`, `loe` | sorts and sums are the reader's job; a prose verdict answers one question badly and goes stale | — |
| 2026-08-14 | *audit* | READY/REMEDIATE/BLOCKED verdict and `LARGEST_SINGLE_FILE_CHANGE` removed | readiness is moot; the coarse three-step cost duplicated the 1–5 loe scale | — |
| 2026-08-22 | `patt.entity.batch-processing` | split → `patt.entity.batch-processing` (lock/claim/release only) + new `patt.entity.batch-criteria` (absorbs the never-committed `patt.entity.time-based-batches`); old pre-split file deleted outright, never committed | resolves the pending request above directly: the "single-row primary-key" exemption meant one interactively-addressed row, not "small batch" — three F's in the same audit read it as the latter. Splitting separates the mandatory claim/lock/release arc from everything about what gets claimed and why — state, limit, sort, score floor, recheck frequency — which is all criteria now, sourced from `dispatch_task` alone (company's `COMPANY_STATES` registry fallback is a confirmed violation of this as of the split, not yet fixed in code). The surviving `batch-processing` directive briefly went through the name `patt.entity.state-batch-processing` before reverting: state turned out not to be the only criteria dimension gating a claim (score floor also does), so foregrounding "state" in the name was misleading | — |
