<!-- linear-archive: AST-1215 archived 2026-08-17 -->

## Linear archive (AST-1215)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1215/admin-ui-grouping-honesty-alphabetical-dropdowns-ui-groupingssequences  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1185 — UI groupings/sequences + alphabetical task key/alias dropdowns (data-driven)  
**Blocked by / blocks / related:** parent: AST-1185

### Description

## What this implements

After AST-1214 (or against the fixed catalog contract): Scheduled Actions / Manage Tasks (and any other in-scope Admin pages) render sections from grouping metadata only, populate task-key dropdowns from the alphabetical catalog covering all agent_task keys (including fetch_* and aliases when present), and drop any remaining React-side hard-coded membership/order lists for those surfaces. Does **not** invent alias→master maps in the frontend. Does **not** own seed section rename or config alias contract.

## Acceptance criteria

- [X] Scheduled Actions and Manage Tasks (and any other in-scope Admin surfaces) show section headers and within-section row order that match live agent_task grouping metadata for the keys they display.
- [X] Every in-scope Admin task-key dropdown lists catalog keys alphabetically by task_key string; after AST-1184 lands, alias keys appear in that same alphabetical list as first-class options.
- [X] Touched Admin frontend paths related to this epic contain no hard-coded task-key membership lists or hard-coded section/sequence inventories that restate grouping already on agent_task / config catalogs.
- [X] Alias → master resolution is not reimplemented in React; UI shows the alias key and relies on backend/config for execution identity.

## Boundaries

Does not invent alias→master maps in the frontend. Does not own seed section rename (AST-1183) or config alias contract (AST-1184). Does not own API/catalog hardcode audit (AST-1214). Does not own Vector Feedback rubric-owner task filter or non-Admin Jobs UI section configs.

## In scope

- [X] `astral.layers.ui-config-driven-business-logic` — section headers / within-section order / dropdown membership from API/`agent_task` metadata; React renders only
- [X] `astral.ui.frontend-file-placement` — changes stay in flat `pages/` + `lib/taskKeySort.ts`
- [X] `astral.standards.no-hardcoded-sets` — no React membership or section-order inventories on touched Admin paths
- [X] `astral.standards.in-scope-only` — React Admin honesty only; no API/seed/alias-resolve
- [X] `orch.pipeline.plan-is-bible` — shared lexicographic helper matches AST-1214 catalog sort contract

## Considered but excluded

- [X] `pattern.ui.admin-endpoint` / Admin API catalog membership — owned by AST-1214
- [X] `astral.config.config-source-of-truth` / `master_task_key` resolve — owned by AST-1184
- [X] `astral.seed.agent-tables-in-repo-json` — Gaze/Meteorite grouping seed owned by AST-1183
- [X] `AdminVectorFeedback.tsx` / `GET …/vector_feedback/task_keys` — intentional rubric-owner subset (same exclusion as AST-1214)
- [X] Jobs UI section configs (`JOBS_*_UI_SECTIONS`, etc.) — non-Admin product surfaces
- [X] `astral.layers.import-direction` — no Python layer changes; frontend-only

## Notes for planning

After AST-1214. Also blocked by AST-1183 and AST-1184 per Archie (all User Testing at plan time). Sort by task_key string (lexicographic, not localeCompare). In-scope Admin task-key dropdowns: Scheduled Actions Add/Edit, Manage Tasks run_next options, Agent Ad Hoc Task Key + Save As.

## Git branch (authoritative)

Parent `ftr/AST-1185-ui-groupingssequences-alphabetical-task-keyalias-dropdowns`; child `sub/AST-1185/AST-1215-admin-ui-grouping-honesty-alphabetical-dropdowns`.

### Comments

#### radia — 2026-08-07T11:47:13.017Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1215
**Publish ref:** `6b35b1e06b5e30595d1a72e288e1c82f26662222` (tip `6b35b1e0`; doc append at `3ba46f32`)
**Overall:** CLEAN

**Scope note:** the mechanical `origin/dev...origin/sub/AST-1215` diff includes AST-1214's already-reviewed `api_admin.py`/`config.py` hunks (carried unchanged from the ftr stack-resume merge `009baedd`). Verified byte-identical for both files across AST-1215's own commit range (`ab191901..6b35b1e0`) — findings below are scoped to AST-1215's actual work: `taskKeySort.ts` + three Admin page wire-ups.

## Plan adherence

- Stage 1 `taskKeySort.ts` matches the plan snippet byte-for-byte.
- Stage 2/3 wire-ups on `AdminScheduledActions.tsx`, `AdminTaskPrompts.tsx`, `AdminAnthropicAdHoc.tsx` match plan steps precisely, including both explicit "leave alone" instructions (section composite sorts, `runNextSelectKeysForUi` cycle-guard exception).
- Final grep across all four Files Changed paths for task-key literal prefixes / section inventories — zero hits, confirming the plan's Stage 3 step 4 done-when.

**Findings:** none fix-now. One **discuss** (see below).

**Full active-set sweep:** all 63 `status: active` statutes scored in-session — zero `violates`. Diff layers are `{ui, docs}` only (no Python core/data/external/utils files touched by AST-1215's own commits) so most non-ui/docs-scoped statutes are `not-applicable`.

**discuss — `ui`-layer predicate over-match (mechanical, not a real gap):** `astral.layers.import-direction`, `astral.config.config-source-of-truth`, `astral.config.secrets-and-env-specific-from-environ`, `astral.patterns.require-auth-on-protected-endpoints` all list `ui` in `applies_when.layers` with `src/**`/`src/ui/**` paths — written with the Flask blueprint layer in mind but also matches pure-React `src/ui/frontend/**` changes. All four score trivial `conforms` here (no Python imports/config/secrets/routes exist in these `.tsx` files). Joan's plan-rubric verdict already excluded three of these four for the same real-world reasoning ("no core/data/external/utils/API paths") — this is the mechanical predicate catching up to that reasoning, not a disagreement. Flagging per C4 for whoever next tightens these `applies_when` blocks; not a block on this ticket.

**Pattern conformance:** none cited for this ticket's own scope (`pattern.ui.admin-endpoint` explicitly excluded — owned by sibling AST-1214).

**Also verified:** git role separation (engineer commits `71ca7dfd`/`3200f29a`/`7e6db2fb` touch only `src/ui/frontend/**`; Betty's `491fab1f` touches only `tests/`+`docs/test-bible/**`; single `merge-tests(AST-1215)` commit) all conform. `npx tsc -b --noEmit` clean at tip. No ticket-id-embedded identifiers.

## Frame diff

(none — ticket description/AC unchanged; findings are diff-only)

context_tokens≈85000

— Radia

#### betty — 2026-08-07T11:41:17.254Z
## QA test manifest — AST-1215

**Publish:** `origin/sub/AST-1185/AST-1215-admin-ui-grouping-honesty-alphabetical-dropdowns` @ `6b35b1e0`
**Betty delivery:** `merge-tests(AST-1215): origin/tests 491fab1f5834e534cb9493a98e7d3227255e97d5`

### Classification
1. **Existing:** SA / Manage Tasks / Ad Hoc page suites remain green; grouping stays data-driven (no obsolete reorder asserts).
2. **Broken / obsolete (revised):** Ad Hoc `vi.mock(api)` missing AuthContext named exports → `importOriginal`.
3. **Gaps (added):** `test_taskKeySort.test.ts`; §6c alphabetical option-order cases on Scheduled Actions, Manage Tasks run_next, Agent Ad Hoc Task Key + Save As.

**Integration:** none revised.

### Manifest (test-child)

```bash
cd src/ui/frontend && npx tsc -b --noEmit && npm run test:component -- \
  ../../../tests/component/frontend/lib/test_taskKeySort.test.ts \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminAnthropicAdHoc.test.tsx
```

**Pass criterion:** tsc + Vitest green on manifest — not zero-arg harness / branch-lock gate.

### Bible shasum (on publish tip)
- `docs/test-bible/frontend/pages.md` — `a85040cc705829587559f63af5eaea558fdf564b`
- `docs/test-bible/frontend/lib.md` — `e58486a720009c6c3935811d37683f286703f604`

— Betty

#### joan — 2026-08-07T11:35:05.071Z
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1215
**Overall:** APPROVED
**Publish ref tip:** `sub/AST-1185/AST-1215-admin-ui-grouping-honesty-alphabetical-dropdowns` @ `ab191901`

## Traceability

AC1→S2 (grouping preserved + verified); AC2→S1–S3; AC3→S3.4 audit; AC4→S2/S3 constraints. No orphan stages — S1 exists only to serve AC2. Files Changed are four `ui` paths, all frontend, so no Python layer statutes match.

**Considered:** `astral.layers.ui-config-driven-business-logic`, `astral.ui.frontend-file-placement`, `astral.ui.naming-conventions`, `astral.standards.no-hardcoded-sets`, `astral.standards.dry-and-focused-functions`, `astral.standards.in-scope-only`, `orch.pipeline.plan-is-bible` — all `conforms`. Excluded: Python-layer statutes (`astral.layers.import-direction`, `astral.config.*`, `astral.batch.*`, `astral.state.*`, `astral.patterns.require-auth-on-protected-endpoints`, `astral.dispatch.*`) — no `core`/`data`/`external`/`utils`/API paths in Files Changed (verdicts + considered-and-excluded scored in-session per R7 slim).

## Audit verified independently — every anchor is exact

I checked the planner audit against the branch rather than taking it on trust, and every cited call site matches:

| Plan step | Real location |
|---|---|
| S2.2 Add/Edit options `Object.keys(allTaskKeys).sort()` | `AdminScheduledActions.tsx:884` |
| S2.3 `taskKeys` memo `[...new Set(…)].sort()` | `:372` |
| S2.4 `sortRowsWithinSection` task_key `localeCompare` | `:393` (fn), `:399` (compare) |
| S2.5 section composite sorts to leave alone | `:382`, `:466` |
| S2.6 `taskKeyOptions` / within-section tie-break | `AdminTaskPrompts.tsx:258`, `:233` |
| S2.7 `runNextSelectKeysForUi` exception to keep | `:278` (render `:498`) |
| S3.3 both Ad Hoc renders "~273 / ~358" | `AdminAnthropicAdHoc.tsx:273`, `:358` |

**The "None found" hard-coded-list claim holds.** I searched all three files for task-key string literals across every known prefix (`grade_`, `fetch_`, `craft_`, `parse_`, `meteorite_`, `qualify_`, `inflow_`, `recheck_`, and fifteen more) and for section-name / `GROUPS` / `SECTIONS` inventories — zero hits in all three. Dropdown data really does come from the API: `allTaskKeys` from `GET /api/admin/dispatch_tasks/task_keys` (`:339`), and both `tasks` arrays from `GET /api/admin/tasks`.

**The surface list is complete.** The `origin/dev` merge added `AdminScheduledQueries.tsx` since this epic was defined, so I checked it and `AdminAgentPrompts.tsx` — both have **zero** `task_key` references, so neither is a missed in-scope dropdown. The four surfaces in the audit table are the whole set.

**One near-miss you got right:** `AdminTaskPrompts.tsx:80` is a `[...s].sort((a,b) => a.localeCompare(b))` that the plan does not touch. It is inside `mergedAdminTokenAutocomplete`, sorting `{$TOKEN}` prompt-autocomplete names — not task keys. Correctly out of scope, and worth having on record so nobody later reads it as a missed site.

**Placement and style are right.** §3.5's frontend table sanctions `src/lib/` for "API client, future hooks, utilities", `taskKeySort.ts` does not exist yet, and the nineteen existing `lib/` modules use exactly the no-semicolon / 2-space / `export function` style the Stage 1 snippet is written in. `sortedTaskKeys(keys: Iterable<string>)` also accepts the `Set` that steps 3 and 6 hand it, since `[...keys]` covers it.

## Findings

### discuss — the sort swap is contract-hardening, not a visible reorder; say so for Betty

I built the full live key list (57 keys — `agent_task` ∪ `TASK_CONFIG`) and sorted it both ways in node. **Lexicographic and `localeCompare` produce byte-identical order, zero differing positions.** So on today's catalog this change moves nothing an operator would see.

That is not an argument against it — it is the argument *for* it, stated more precisely than the plan states it. `localeCompare` is locale-dependent by contract, so today's agreement is a property of the machine I ran it on, not a guarantee; a client in another locale, or the first task key containing a digit, hyphen, or capital, can diverge from the Python `sorted()` / SQLite `ORDER BY task_key` contract AST-1214 establishes. The helper removes that latent client-locale dependency.

Worth one line in the plan (and in the Stage 3 handoff to Betty) because a test author told "make dropdowns alphabetical" will go looking for an order diff to assert and find none. The assertion that has teeth is that the option order equals the API payload order — not that it changed.

### acceptable — section ordering stays on `localeCompare`, and that is the right call

Step 5 leaves the `task_group_order\u0000name` composite sorts at `:382` / `:466` alone. Same locale caveat applies in principle, but AC2's alphabetical requirement is scoped to **task_key** catalogs, and AC1 only requires section headers and order to *derive from* `task_group_order` / `task_group_name`, which they do. Keeping the blast radius to task-key comparisons is the correct reading of `astral.standards.in-scope-only`; I am recording it so it does not get flagged as an inconsistency at code review.

### acceptable — the AST-1214 dependency line overstates Linear status but understates the code

The out-of-scope table says "AST-1214 (done / UT)". AST-1214 is at **Plan Approved** in Linear, not User Testing. The substance is fine though, and I confirmed it rather than assuming: `_admin_dispatch_task_key_catalog` is present on this branch (`api_admin.py:972`, wired at `:999`) along with `is_meteorite_email_mailbox_task_key`, so the live alphabetical catalog the intro relies on genuinely is there via `009baedd`. No step or Done-when depends on the status label, so nothing to change — but if Betty reads "UT" as "merged and stable," set expectations accordingly.

### nit — stray `)` at end of plan doc

Line 126 of the plan is a bare `)` after the CODE_RULES check. Cosmetic; sweep it whenever the doc is next touched.

## Verdict

No `fix-now` findings. Self-assessment is honest and unusually well-calibrated: `Single-Component` is accurate for three pages plus one `lib/` helper, `high` conf is earned because the audit's claims are checkable and check out, and `low` risk is right — display ordering only, with dispatch, claim, and alias-resolve paths untouched, and the one genuine hazard (inventing a React alias→master map) explicitly fenced in the execution contract. R1–R6 pass; R7 satisfied by this comment. Status → **Plan Approved**.

The audit table up front is what made this a single-pass review — it gave me claims specific enough to falsify, and they survived.

— Joan

context_tokens≈175000

#### katherine — 2026-08-07T11:29:50.763Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1185/AST-1215-admin-ui-grouping-honesty-alphabetical-dropdowns/docs/features/meteorite/ast-1215-admin-ui-grouping-honesty-alphabetical-dropdowns.md

`origin/sub/AST-1185/AST-1215-admin-ui-grouping-honesty-alphabetical-dropdowns` @ `ab191901`

**Scope:** Single-Component — Admin React (`AdminScheduledActions`, `AdminTaskPrompts`, `AdminAnthropicAdHoc`) + shared `lib/taskKeySort.ts`; API/config/seed/Vector Feedback/Jobs excluded.

**Conf:** high — tip audit shows Scheduled Actions / Manage Tasks already group from `task_group_*` / `task_seq`; remaining work is one lexicographic helper (match AST-1214/`sorted`) and wiring Ad Hoc so client sort is explicit.

**Risk:** low — display/sort only; no dispatch, claim, or alias→master changes. Wrong sort affects option order only.

---

# Admin UI grouping honesty + alphabetical dropdowns

**Linear:** [AST-1215](https://linear.app/astralcareermatch/issue/AST-1215/admin-ui-grouping-honesty-alphabetical-dropdowns-ui-groupingssequences)  
**Parent:** [AST-1185](https://linear.app/astralcareermatch/issue/AST-1185/ui-groupingssequences-alphabetical-task-keyalias-dropdowns-data-driven)  
**Publish ref:** `sub/AST-1185/AST-1215-admin-ui-grouping-honesty-alphabetical-dropdowns`

After AST-1214’s live alphabetical Admin catalog (`GET /api/admin/dispatch_tasks/task_keys`) and with Gaze/Meteorite grouping + alias catalog keys already live (AST-1183 / AST-1184 at User Testing), this ticket owns the **React** honesty pass: Scheduled Actions and Manage Tasks must render section headers and within-section row order only from `agent_task` grouping metadata (`task_group_order`, `task_group_name`, `task_seq`), every in-scope Admin **task-key** dropdown must list keys alphabetically by **task_key string** (including alias identities when present in the payload), and touched Admin frontend paths must not restate grouping membership or section order in hard-coded React lists. Alias → master resolution stays backend/config — the UI shows the alias key as-is.

### Planner audit (tip stacked on `origin/ftr/AST-1185-…` after AST-1214)

| Surface | Grouping | Task-key dropdown | Hard-coded membership/order lists |
|---------|----------|-------------------|-----------------------------------|
| `AdminScheduledActions.tsx` | Sections keyed by `task_group_order` + `task_group_name` from catalog meta; within-section default sort by `task_seq` then task_key | Add/Edit modal: `Object.keys(allTaskKeys).sort()` from `GET …/dispatch_tasks/task_keys` | None found |
| `AdminTaskPrompts.tsx` (Manage Tasks) | Same composite section key from row fields; within-section by `task_seq` then task_key | run_next options from loaded `tasks` via `localeCompare` | None found |
| `AdminAnthropicAdHoc.tsx` | N/A (no section chrome) | Task Key select + Save As list: `tasks.map` with **no** client sort (array order today follows `list_candidate_tasks` `ORDER BY task_key`, but AC wants an explicit client contract) | None found |
| `AdminVectorFeedback.tsx` | N/A | Rubric-owner subset via `GET …/vector_feedback/task_keys` | **Out of scope** (same exclusion as AST-1214) |
| Jobs / non-Admin | — | — | **Out of scope** (parent Admin-only default) |

This ticket therefore **preserves** existing grouping behavior on Scheduled Actions / Manage Tasks, **unifies** lexicographic task_key sorting behind one helper (match Python/`sorted` / SQLite `ORDER BY task_key` ordinal compare — not locale-sensitive `localeCompare`), and **applies** that helper to Ad Hoc so every in-scope Admin task-key picker has the same explicit contract.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/lib/taskKeySort.ts` | New: `compareTaskKeys` + `sortedTaskKeys` (lexicographic task_key string order) | ui |
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Use helper for catalog picker keys + filter task-key option list; leave section/`task_seq` grouping logic intact | ui |
| `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` | Use helper for `taskKeyOptions` and task_key tie-break after `task_seq`; leave section grouping intact | ui |
| `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx` | Sort Task Key `<select>` and Save As list via helper by `task_key` | ui |

**Out of scope (do not edit):**

| Owner | What |
|-------|------|
| AST-1214 (done / UT) | Admin API catalog membership, write gates, form-meta |
| AST-1183 / AST-1184 | Seed grouping rename; `master_task_key` resolve |
| AST-1182 | `parse_meteorite_email` → `meteorite_email` seed rename |
| Betty | Any `tests/` / bible — engineer does not edit test-tree |
| This ticket explicitly excludes | `AdminVectorFeedback.tsx` task filter; Jobs UI section configs; inventing React alias→master maps; API/config/`src/data` |

## Execution contract

The plan is binding. Execute stages in order. Do not edit API/config/seed/tests. Do not add React alias→master maps. When blocked — comment on **AST-1185** with the Stage N template from plan-child.

---

## Stage 1: Shared lexicographic task_key sort helper

**Done when:** `src/ui/frontend/src/lib/taskKeySort.ts` exports `compareTaskKeys(a, b)` and `sortedTaskKeys(keys)` that order strings by plain lexicographic compare (`a < b` / `a > b`), matching Python `sorted()` / SQLite `ORDER BY task_key` for ASCII snake_case keys. No `localeCompare`. No other files changed yet.

1. Create `src/ui/frontend/src/lib/taskKeySort.ts` with exactly:

```ts
/** Lexicographic task_key order (Python sorted() / SQLite ORDER BY task_key). Not locale-sensitive. */
export function compareTaskKeys(a: string, b: string): number {
  return a < b ? -1 : a > b ? 1 : 0
}

export function sortedTaskKeys(keys: Iterable<string>): string[] {
  return [...keys].sort(compareTaskKeys)
}
```

⚠️ **Decision:** One shared helper instead of three slightly different `.sort()` / `localeCompare` call sites, so dropdown order cannot drift from the AST-1214 catalog contract. Rejected: leave Ad Hoc relying only on API array order.

---

## Stage 2: Scheduled Actions + Manage Tasks — wire helper; keep grouping data-driven

**Done when:**

- `AdminScheduledActions.tsx` Add/Edit Task `<select>` options are `sortedTaskKeys(Object.keys(allTaskKeys))` (still driven by `GET /api/admin/dispatch_tasks/task_keys`; still shows alias keys when present in that payload).
- Filter chip / task-key filter option list built from loaded rows also uses `sortedTaskKeys` (or `[...set].sort(compareTaskKeys)`).
- Section headers still come only from catalog/row `task_group_order` + `task_group_name`; default within-section order still `task_seq` then `compareTaskKeys` (replace the existing `localeCompare` / default `.sort()` tie-breaks for **task_key** only).
- `AdminTaskPrompts.tsx` `taskKeyOptions` uses `sortedTaskKeys`; within-section tie-break after `task_seq` uses `compareTaskKeys`.
- No new hard-coded task-key arrays, section-name arrays, or phase/seq inventories added. No edits that invent alias→master mapping.

1. In `AdminScheduledActions.tsx`, import `{ compareTaskKeys, sortedTaskKeys }` from `../lib/taskKeySort`.
2. Replace the Add/Edit modal options line  
   `Object.keys(allTaskKeys).sort().map(...)`  
   with  
   `sortedTaskKeys(Object.keys(allTaskKeys)).map(...)`.
3. Replace `taskKeys` memo  
   `[...new Set(data.map(d => d.task_key))].sort()`  
   with  
   `sortedTaskKeys(new Set(data.map(d => d.task_key)))`.
4. In `sortRowsWithinSection`, when comparing task_key strings, use `compareTaskKeys(a.task_key, b.task_key)` instead of `a.task_key.localeCompare(b.task_key)`.
5. Leave section composite-key sorts (`task_group_order\u0000name`.localeCompare) unchanged — those order **sections**, not the task-key catalog.
6. In `AdminTaskPrompts.tsx`, import the same helpers; set  
   `taskKeyOptions` to `sortedTaskKeys(new Set(tasks.map(t => t.task_key)))`;  
   in within-section sort after `task_seq`, use `compareTaskKeys(a.task_key, b.task_key)`.
7. Do **not** change run_next cycle-filter logic except that it continues to consume `taskKeyOptions` (already alphabetical after step 6). Keep the “prepend current invalid run_next” UI exception in `runNextSelectKeysForUi` — that is edit-state honesty, not catalog order.

⚠️ **Decision:** Sentinel `task_seq ?? 999` for missing seq stays — it is a missing-value fallback, not a membership/order inventory. Do not replace with a hard-coded seq table.

---

## Stage 3: Agent Ad Hoc — explicit alphabetical task_key lists

**Done when:** Agent Ad Hoc Task Key `<select>` options and Save As menu entries appear in lexicographic `task_key` order via `sortedTaskKeys` / `compareTaskKeys`, even if `/api/admin/tasks` order changes later. No alias→master UI. No Vector Feedback / Jobs edits.

1. In `AdminAnthropicAdHoc.tsx`, import `{ compareTaskKeys, sortedTaskKeys }` from `../lib/taskKeySort`.
2. Add a memo (or inline once)  
   `const taskKeysSorted = useMemo(() => [...tasks].sort((a, b) => compareTaskKeys(a.task_key, b.task_key)), [tasks])`  
   — or derive `sortedTaskKeys(tasks.map(t => t.task_key))` and look up rows; prefer sorting the task objects with `compareTaskKeys` so labels stay attached.
3. Replace both `tasks.map(t => …)` option/menu renders (Task Key select ~line 273 and Save As list ~line 358) to iterate the sorted list.
4. Final grep on the four Files Changed paths for hard-coded task-key membership arrays (e.g. string-literal lists of `grade_do`, `fetch_jd`, section title inventories). Expected: **zero** removals beyond the sort wiring. If a hard-coded membership/order list is found in those paths, delete it and keep using API/catalog data — do not leave parallel lists. If a list is found **outside** Files Changed that this ticket’s AC requires, stop and comment on **AST-1185** (do not silently expand Files Changed).

---

## Self-Assessment

**Scope:** `Single-Component` — Admin React pages + one shared `lib/` sort helper; no API/config/seed; Vector Feedback and Jobs excluded.

**Conf:** `high` — planner audit shows grouping already data-driven on the two primary surfaces; remaining work is an explicit alphabetical contract helper plus Ad Hoc wiring against known payloads.

**Risk:** `low` — sort-order / display-only; dispatch, claim, and alias resolve paths untouched. Wrong sort would only affect option order; wrong grouping edit would mis-order Admin chrome but this plan preserves existing grouping formulas.

## Self-review vs ASTRAL_CODE_RULES

- §1.3 DRY — shared `taskKeySort` helper for three call sites.
- §1.4 / `astral.standards.no-hardcoded-sets` — no new membership sets; audit expects none to remove on tip.
- §3.2 / `astral.layers.ui-config-driven-business-logic` — grouping/order from API/`agent_task` metadata; React only renders.
- §3.5 / `astral.ui.frontend-file-placement` — pages stay flat under `pages/`; helper under `lib/`.
- `astral.standards.in-scope-only` — no API, seed, alias resolve, Vector Feedback, or Jobs UI.
- §2.1 / §2.4 / §2.6 / §3.3 — N/A (no config blocks, batch claim, state machine, or Python import-direction changes).

## Review

**Publish ref:** `sub/AST-1185/AST-1215-admin-ui-grouping-honesty-alphabetical-dropdowns`  
**Code tip:** `7e6db2fb` (Stage 1 `taskKeySort` → Stage 2 Scheduled Actions + Manage Tasks → Stage 3 Ad Hoc).

Note for Betty: lexicographic vs prior `localeCompare` is contract-hardening — on today’s ASCII catalog the option order is unchanged; assert option order equals API/`sorted` payload order, not a visible reorder.

## Radia review — [code-rubric] revision=1

**Rubric:** code-rubric.v1 · **Ticket:** AST-1215 · **Publish ref tip:** `6b35b1e0`

**Overall: CLEAN**

**Scope note:** `origin/dev...origin/sub/AST-1185/AST-1215-...` mechanically includes AST-1214's already-reviewed `api_admin.py` / `config.py` hunks (carried over unchanged from the ftr stack-resume merge, `009baedd`) plus the AST-1214 plan-doc/review content. This review scores the full statute sweep against that complete diff but the findings below are scoped to AST-1215's own commits (`ab191901..6b35b1e0`, verified byte-identical for the two Python files via `git diff 009baedd..6b35b1e0 -- src/ui/api/api_admin.py src/utils/config.py` = empty).

**What's solid:**

- `taskKeySort.ts` is exactly the plan's Stage 1 snippet, byte-for-byte (`compareTaskKeys` / `sortedTaskKeys`, no `localeCompare`).
- All three page wire-ups match plan steps precisely: `AdminScheduledActions.tsx` (Add/Edit options, `taskKeys` memo, within-section `compareTaskKeys` tie-break, section composite sorts left untouched), `AdminTaskPrompts.tsx` (`taskKeyOptions`, within-section tie-break), `AdminAnthropicAdHoc.tsx` (sorts task objects with `compareTaskKeys` so labels stay attached, per the plan's stated preference — both the Task Key `<select>` and Save As list render off `taskKeysSorted`).
- Grep across all four Files Changed paths for task-key string-literal prefixes (`grade_`, `fetch_`, `meteorite_`, etc.) and section/`GROUPS`/`SECTIONS` inventories — zero hits. No new hardcoded membership or order lists.
- Git hygiene: engineer commits `71ca7dfd` / `3200f29a` / `7e6db2fb` touch only `src/ui/frontend/**`; Betty's `491fab1f` touches only `tests/` + `docs/test-bible/**`; single `merge-tests(AST-1215)` commit `6b35b1e0`. Commit vocabulary correct throughout.
- `npx tsc -b --noEmit` clean at tip.
- No new identifiers embed the ticket id (`compareTaskKeys`, `sortedTaskKeys`, `taskKeysSorted` — all domain language).

**Full active-set sweep (63 statutes, in-session):** zero `violates`. One **discuss** straggler cluster below; everything else `conforms` or `not-applicable` (most `src/core`/`data`/`external`/batch/state/dispatch/seed statutes are `not-applicable` — this diff's layers are `{ui, docs}` only, no Python core/data/external/utils files touched by AST-1215's own commits).

**discuss — `ui`-layer statute predicates over-match on frontend-only diffs (mechanical, not a real gap):** `astral.layers.import-direction`, `astral.config.config-source-of-truth`, `astral.config.secrets-and-env-specific-from-environ`, and `astral.patterns.require-auth-on-protected-endpoints` all list `ui` in `applies_when.layers` with `paths: ["src/**"]` / `["src/ui/**"]` — a predicate written with the Flask `src/ui/api/**` blueprint layer in mind, but it also matches pure-React `src/ui/frontend/**` changes. All four score `conforms` trivially here (no Python imports, no config blocks, no secrets, no Flask routes exist in these three `.tsx` files) — there's nothing to violate, just nothing to *not-applicable* either under the letter of the Full-set sweep algorithm. Joan's plan-rubric verdict (`e577b3f5`, 2026-08-07) excluded three of these four (`import-direction`, `config.*` via "no core/data/external/utils/API paths") using the same real-world reasoning; this is the mechanical predicate catching up to that reasoning, not a disagreement with it. No fix — just flagging per C4 so the gap between "predicate matches" and "statute's actual subject exists in the diff" is on record for whoever tightens these `applies_when` blocks next.

**Pattern conformance:** none cited for this ticket's own scope (`pattern.ui.admin-endpoint` is explicitly excluded in the plan — owned by sibling AST-1214).

**Plan adherence:** Stages 1–3 match the plan's own code snippets essentially verbatim, including the two explicit "leave alone" instructions (section composite sorts, `runNextSelectKeysForUi` cycle-guard exception). Self-Assessment (`Single-Component` / `high` conf / `low` risk) holds — matches Joan's plan-rubric APPROVED verdict, which independently re-verified every line-number anchor in the planner audit table.

## Frame diff

(none — ticket description/AC unchanged; findings are diff-only)

context_tokens≈85000

— Radia

## Resolution

**Date:** 2026-08-07  
**Outcome:** clean — Radia `[code-rubric] revision=1` Overall **CLEAN**; no fix-now. Discuss item (ui-layer statute predicate over-match on frontend-only diffs) is C4 record for statute `applies_when` tightening — no product or plan change on this ticket.

**Publish tip after resolve:** `resolve(AST-1215): — clean` on `origin/sub/AST-1185/AST-1215-admin-ui-grouping-honesty-alphabetical-dropdowns` (this commit).
