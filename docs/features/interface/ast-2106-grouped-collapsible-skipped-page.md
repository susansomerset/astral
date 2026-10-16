# AST-2106 — Grouped, collapsible Skipped page

- **Ticket:** [AST-2106](https://linear.app/astralcareermatch/issue/AST-2106) (child of [AST-2102](https://linear.app/astralcareermatch/issue/AST-2102) — Group the Skipped jobs list by Fail, Bot block and Error)
- **Publish ref:** `sub/AST-2102/AST-2106-grouped-skipped-page` (origin only)
- **Canon Scope:** none. The ticket's Citations say "none. No in-force directive governs React pages."

This ticket delivers the React side of Skipped grouping. `StateUiManifest.jobs.skipped` gains the `groups` list that [AST-2105](https://linear.app/astralcareermatch/issue/AST-2105) already emits from `config.py`. The Skipped page's section memo assigns every built section (below-floor, normal, legacy) to a group: an explicit member match first, then the first group with a matching prefix, then the catch-all. The page then renders one collapsible heading per non-empty group, showing the label and total job count, in manifest order (Error, Bot block, Fail, Other). Per-state sections, tables, sort, retry, and row actions are unchanged. No state name or prefix is typed in the page.

## Build base

- The epic worktree ran `sync-child.sh sub/AST-2102/AST-2106-grouped-skipped-page --ftr AST-2102-group-skipped-jobs`, which fast-forwarded this sub to `origin/ftr/AST-2102-group-skipped-jobs` @ `32b2619dd`. That tip carries AST-2105 (`JOBS_SKIPPED_GROUPS` plus the manifest `groups` entry) and AST-2073's renamed states.
- **Builder:** pass `--ftr AST-2102-group-skipped-jobs` (the full parent segment from `epic_registry.py show AST-2102`). `--ftr AST-2102` does not exist on origin, so the script silently skips the parent merge. After syncing, confirm that `git merge-base --is-ancestor 6913fcd98 HEAD` exits 0, which proves AST-2105's code commit is present. If it does not, stop and comment on the parent.
- **Plan-time facts (verified on `32b2619dd`):** `build_state_ui_manifest()["jobs"]["skipped"]["groups"]` is an ordered list of `{key, label, prefixes, members}`: `error` / `bot_block` / `fail` / `other`, with `other` as the catch-all and Fail's members `["CANDIDATE_SKIPPED", "__BELOW_DISPATCH_FLOOR__"]`. `src/ui/frontend` has no committed `node_modules`. After `npm ci`, the baselines are `npm run build` exit 0 and `npm run lint` showing `✖ 29 problems (25 errors, 4 warnings)`. In the two touched files, the only problem is the pre-existing `react-hooks/set-state-in-effect` error at `JobsSkipped.tsx` 151 (`setToast` in the `actions.error` effect). AC 10's `rg` currently returns nothing on `JobsSkipped.tsx`.

## Explicit scope gate

The ticket's `## Scope` covers `src/ui/frontend/src/contexts/StateUiContext.tsx` (the interface gains `groups`) and `src/ui/frontend/src/pages/JobsSkipped.tsx` (the section memo assigns groups, the render emits collapsible group headings keyed for the expand-policy hook, and everything else is unchanged). Every row below is one of those files, and each change is one of those kinds. This ticket does not touch `config.py` (AST-2105), `useSectionExpandPolicy.ts`, `lib/stateUiSections.ts`, CSS, `tests/`, or the bible.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/contexts/StateUiContext.tsx` | Add `groups` to `StateUiManifest.jobs.skipped` | ui |
| `src/ui/frontend/src/pages/JobsSkipped.tsx` | Section memo returns groups of sections; group collapse uses a second expand-policy hook instance; render wraps existing sections in collapsible group headings | ui |
| `docs/features/interface/ast-2106-grouped-collapsible-skipped-page.md` | This plan (plan-child) plus the review stub (build-child) | docs |

## Stage 1: Manifest type, grouped section memo, collapsible group headings

**Done when:** `npm run build` exits 0. `npm run lint` reports exactly the baseline `✖ 29 problems (25 errors, 4 warnings)`. AC 10's `rg` returns nothing. `git diff -w` on `JobsSkipped.tsx` shows no change inside the per-section body.

0. In `src/ui/frontend`, run `npm ci`, then record the baselines: `npm run build` (expect exit 0) and `npm run lint 2>&1 | tail -3` (expect `✖ 29 problems (25 errors, 4 warnings)`). If either differs from the plan-time facts above, record the actual values in the review stub and use them as the bar for step 6.

1. **`StateUiContext.tsx`:** in `StateUiManifest.jobs.skipped`, directly after `bulk_retry_to_state_by_from_state: Record<string, string>`, add exactly:

   ```ts
         /** Ordered group rules, catch-all last: a state joins the first group listing it in `members`,
          *  else the first group with a matching prefix, else the last group. */
         groups: Array<{ key: string; label: string; prefixes: string[]; members: string[] }>
   ```

   ⚠️ **Decision:** This field is an ordered `Array`, not a `Record` keyed by group id. It mirrors what AST-2105's approved manifest emits (a list, because display order and "catch-all is last" are positional). The `key` field still carries each group's id.

   ⚠️ **Decision:** `groups` is required, not optional. The server always emits it, and a missing value is a manifest bug. The page adds no fallback.

2. **`JobsSkipped.tsx` section memo:** rename `const sections = useMemo(() => {` to `const skipGroups = useMemo(() => {`. Keep the memo body unchanged down to and including the `const legacy = …` statement. Then replace the tail, from `const withLegacy = [...normal, ...legacy]` through `}, [rows, manifest])`, with exactly:

   ```ts
       const floor = floorJobs.length
         ? [{ state: belowKey, label: sk.below_dispatch_label, jobs: floorJobs, gradeKey: "" }]
         : []
       const built = [...floor, ...normal, ...legacy]
       // Manifest group rules: explicit member, then first matching prefix, then the catch-all (always last).
       const groupKeyOf = (state: string) => (
         sk.groups.find(g => g.members.includes(state))
         ?? sk.groups.find(g => g.prefixes.some(p => state.startsWith(p)))
         ?? sk.groups[sk.groups.length - 1]
       ).key
       // Manifest order; empty groups dropped; sections keep their built order (floor, normal, legacy) within a group.
       return sk.groups
         .map(g => {
           const secs = built.filter(s => groupKeyOf(s.state) === g.key)
           return { key: g.key, label: g.label, sections: secs, count: secs.reduce((n, s) => n + s.jobs.length, 0) }
         })
         .filter(g => g.sections.length > 0)
     }, [rows, manifest])
   ```

   The early `return []` when `!manifest` stays as is. `floor`, `normal`, and `legacy` objects keep exactly today's fields, so the per-section render reads them unchanged. The below-floor section's `state` is `below_dispatch_key`, which is a Fail member, so it lands in Fail by member match (AC 6). Legacy states go through the same rules, so `ERROR_SOMETHING_OLD` lands in Error by prefix and `MYSTERY_STATE` lands in the catch-all (AC 5).

3. **`JobsSkipped.tsx` expand state:** replace these three lines:

   ```ts
     const sectionKeys = useMemo(() => sections.map(s => s.state), [sections])
     const { isExpanded, onExpandedChange, setExpandedKeys } = useSectionExpandPolicy({ sectionKeys })
     useEffect(() => { setExpandedKeys(new Set()) }, [selectedId, setExpandedKeys])
   ```

   with exactly:

   ```ts
     const sectionKeys = useMemo(() => skipGroups.flatMap(g => g.sections.map(s => s.state)), [skipGroups])
     const { isExpanded, onExpandedChange, setExpandedKeys } = useSectionExpandPolicy({ sectionKeys })
     // Second, expand-all instance for group headings that holds the *collapsed* group keys: groups start
     // open with no seeding effect, and group clicks never touch the sections' Expand One state.
     const groupKeys = useMemo(() => skipGroups.map(g => g.key), [skipGroups])
     const {
       isExpanded: isGroupCollapsed,
       onExpandedChange: setGroupCollapsed,
       setExpandedKeys: setCollapsedGroupKeys,
     } = useSectionExpandPolicy({ expandAll: true, sectionKeys: groupKeys })
     useEffect(() => {
       setExpandedKeys(new Set())
       setCollapsedGroupKeys(new Set())
     }, [selectedId, setExpandedKeys, setCollapsedGroupKeys])
   ```

   ⚠️ **Decision:** Group headings use a **second instance** of `useSectionExpandPolicy`, not the section instance. The section instance is Expand One (at most one key open). If group keys shared it, opening any section would close its own group and hide the section, and a group click would reset the open section. That would break AC 7 ("each section's own expanded state unchanged") and parent Functional scope 6 ("per-section expand … exactly as today"). Switching the shared instance to `expandAll` is also rejected, because it would change today's one-open-section behavior. The second instance is still "keyed for the existing expand-policy hook", per the ticket.

   ⚠️ **Decision:** The group instance stores **collapsed** keys, so an empty set means every group is open. Groups start open, which is the reading of AC 7 ("clicking a group heading hides … clicking again restores"). Existing component tests also click per-section buttons directly, and they keep working without a group click first. Storing open keys instead would need a seeding `useEffect`. That adds a first-frame flash, a signature memo, and effect-driven state of the kind `react-hooks/set-state-in-effect` already flags in this file. Collapsed group keys reset on candidate change in the same effect that already resets section keys. The rule does not flag that effect today, because the setter comes from a custom hook.

4. **`JobsSkipped.tsx` render:**
   - Change `) : sections.length === 0 ? (` to `) : skipGroups.length === 0 ? (`. The `No skipped jobs` line stays as is (AC 8).
   - Replace the single line `        sections.map(sec => {` with exactly:

     ```tsx
             skipGroups.map(grp => {
               const groupOpen = !isGroupCollapsed(grp.key)
               return (
                 <div key={grp.key} style={{ marginBottom: 24 }}>
                   <button
                     type="button"
                     onClick={() => setGroupCollapsed(grp.key, groupOpen)}
                     style={{
                       background: "none", border: "none", borderBottom: "1px solid var(--border)", cursor: "pointer", width: "100%",
                       display: "flex", alignItems: "center", gap: 8, padding: "10px 0", marginBottom: 8,
                       color: "var(--text-primary)", fontSize: 18, fontWeight: 700, fontFamily: "inherit",
                     }}
                   >
                     <span style={{ transform: groupOpen ? "rotate(0deg)" : "rotate(-90deg)", transition: "transform 0.15s", fontSize: 12 }}>&#9660;</span>
                     {grp.label} ({grp.count})
                   </button>
                   {groupOpen && (
                     <div style={{ paddingLeft: 16 }}>
                       {grp.sections.map(sec => {
     ```

   - Keep the whole existing per-section body unchanged except for indentation: from `const sectionOpen = isExpanded(sec.state)` through that section's closing `)` of `return (`. Re-indent it by **10 spaces** and make no other character change.
   - Replace the existing closing line of the old map, `        })` (the line directly before `      )}` and `<JobDetailModal`), with exactly:

     ```tsx
                       })}
                     </div>
                   )}
                 </div>
               )
             })
     ```

   ⚠️ **Decision:** The group heading reuses the section button's chevron and layout, but uses `fontSize: 18`, `fontWeight: 700`, and a `var(--border)` bottom rule. Sections sit in a `paddingLeft: 16` wrapper so the hierarchy reads at a glance. The wrapper sits outside the per-section markup, which stays unchanged. Inline styles match the file's existing idiom, and no CSS file is in scope.

   ⚠️ **Decision:** The group `<div>` uses `key={grp.key}` (`error` / `bot_block` / `fail` / `other`). Group wrappers are siblings only of each other, so they cannot collide with `sec.state` keys.

5. Nothing else in `JobsSkipped.tsx` changes: `handleRetry`, `handleSort`, `sortIndicator`, `sortJobs`, row actions, the modals, and the toast. `handleRetry` still reads `rows`, so a mixed Error/Fail selection still posts once per distinct `bulk_retry_to_state_by_from_state` target (AC 9).

6. Compile and lint (Susan's rule: before commit). Run these in `src/ui/frontend`:
   - `npm run build` → exit 0 (AC 11).
   - `npm run lint 2>&1 | tail -3` → the same count as the step-0 baseline. A higher count means the new lines introduced a problem. Stop and comment on the parent; do not suppress the problem with `eslint-disable`.
   - From the worktree root: `rg -n '"[A-Z]+(_[A-Z]+)*_"|"[A-Z]+(_[A-Z]+)+"' src/ui/frontend/src/pages/JobsSkipped.tsx` → no output (AC 10).
   - `git diff -w src/ui/frontend/src/pages/JobsSkipped.tsx` → its hunks are only the step-2/3/4 replacements. No `-`/`+` line falls inside the per-section body.

7. Commit on the epic worktree with only the two `src/ui/frontend/...` files staged: `code(AST-2106): grouped, collapsible Skipped page`. Publish per build-child (`git push origin HEAD:sub/AST-2102/AST-2106-grouped-skipped-page`).

## Notes for QA (Betty, informational, not builder steps)

- `tests/component/frontend/fixtures/stateUiManifestFixture.ts` is typed `StateUiManifest`, and its `skipped` block has no `groups`. After this change, every `test_JobsSkipped.test.tsx` case that renders rows will throw on `sk.groups.find`, until the fixture gains `groups` mirroring AST-2105's manifest (`error` `["ERROR_"]`, `bot_block` `["BOT_BLOCKED_"]`, `fail` `["FAILED_","METEORITE_FAILED_","JD_SCRAPE_FAIL_"]` plus members `["CANDIDATE_SKIPPED","__BELOW_DISPATCH_FLOOR__"]`, and `other` empty). `tsc -b` covers only `src/`, so the build does not catch the stale fixture.
- Groups start open, so existing cases that click section buttons (`/Below dispatch score floor/`, `/Failed LIKE/`, `/CANDIDATE_SKIPPED/`) need no extra group click. Group button names are `Error (n)`, `Bot block (n)`, `Fail (n)`, and `Other (n)`. `getByRole("button", { name: /Fail/ })` would now be ambiguous with `Failed LIKE`, so anchor it (`/^Fail \(/`).
- AC 4–8 are component-testable with the fixture and a mocked `/api/jobs?view=skipped` response. AC 9's retry POST already has an existing case to extend with a mixed selection.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-2106
**Overall:** APPROVED
**Corpus:** c04b07deda8f5a750afd473ec847d06ed2207065
**Publish ref:** `origin/sub/AST-2102/AST-2106-grouped-skipped-page` @ `089abbe2d`

## Canon scores

(explicit Canon Scope **none**, locked at parent Discussion — no directive ids on the ticket list; R3 has zero rows)

## Traceability

AC **4–8** → Stage 1 steps 2–4 (grouped memo, dual expand-policy, collapsible headings); AC **9** → Stage 1 step 5 (`handleRetry` unchanged); AC **10** → Stage 1 step 6 `rg`; AC **11** → Stage 1 steps 0/6 build+lint baseline; parent AC **1–3** → N/A (AST-2105).

### acceptable — No `## Self-assessment` block

- **Location:** Plan doc structure
- **Finding:** No self-assessment section.
- **Recommendation:** Optional; not blocking for this two-file UI change.

### acceptable — Component tests / fixture out of builder scope

- **Location:** Notes for QA; ticket `## Scope` excludes `tests/`
- **Finding:** `stateUiManifestFixture.ts` lacks `groups`; `test_JobsSkipped.test.tsx` will fail on `sk.groups` until Betty mirrors AST-2105 manifest shape.
- **Recommendation:** Correct partition (engineer ships product; Betty owns bible/tests). Plan documents the fixture shape and query anchoring (`/^Fail \(/`). Not a plan defect.

### discuss — Optional future canon (not scored)

- **Location:** Parent Architectural definition / child Citations
- **Finding:** `astral.ui.frontend-file-placement` and draft UI-config-driven spirit apply in spirit; parent locked **Canon Scope: none** for React.
- **Recommendation:** No plan change; amend Canon Scope only via Discussion if Archie wants enforceable placement law later.

**R6 (adversarial):** Identity OK (`Plan Ready`, assignee Joan). Scope gate limits changes to `StateUiContext.tsx` and `JobsSkipped.tsx`; plan matches ticket technical scope (manifest type, grouped memo, group headings, no literals). Build base documents `sync-child.sh --ftr AST-2102-group-skipped-jobs` and `merge-base --is-ancestor 6913fcd98` (verified on epic worktree; manifest `groups` length 4). Live `JobsSkipped.tsx` structure (lines 154–194 memo, 273+ flat `sections.map`) matches plan splice points. Second `useSectionExpandPolicy({ expandAll: true })` with collapsed-key inversion is consistent with hook semantics (`useSectionExpandPolicy.ts` expandAll branch) and preserves Expand One for sections — addresses AC 7 and parent functional scope #6 without modifying the hook file (in scope). Grouping algorithm matches parent #1 (member → prefix → catch-all) and AST-2105 manifest order. Empty-group filter and `skipGroups.length === 0` preserve AC 8 empty state. Per-section render body (including inner rubric `groups` variable) stays inside unchanged block per step 4 / `git diff -w` gate. Lint baseline pinned (29 problems); no new `eslint-disable`. AC 10 `rg` already clean on current file.

context_tokens≈52000

```
[plan-rubric] PROCEED (Commit: 089abbe2d) Grouped Skipped page ready
```


## Review (build stub)

**Built:** `origin/sub/AST-2102/AST-2106-grouped-skipped-page` @ `7673e3216`.

**Stages delivered:**
- Stage 1: `groups` on `StateUiManifest.jobs.skipped`. The section memo (now `skipGroups`) assigns floor/normal/legacy sections to manifest groups (member → prefix → catch-all) and drops empty groups. A second `useSectionExpandPolicy` instance (`expandAll`) holds collapsed group keys, reset with section keys on candidate change. The render wraps the unchanged per-section body in collapsible group headings. Code is verbatim from the plan: `7673e3216`.

**Notes:**
- Build base: synced with `--ftr AST-2102-group-skipped-jobs`; AST-2105's `6913fcd98` is an ancestor of HEAD.
- `npx tsc -b --noEmit` exit 0; `npm run build` exit 0; `npm run lint` 29 problems (25 errors, 4 warnings) before and after; AC 10 `rg` returns nothing; `git diff -w` shows no change inside the per-section body.
- For Betty: `tests/component/frontend/fixtures/stateUiManifestFixture.ts` still lacks `skipped.groups`, so `test_JobsSkipped.test.tsx` cases that render rows will throw until the fixture gains it (see Notes for QA above).

## Radia review

[code-rubric]
**Ticket:** AST-2106
**Publish ref:** `a571f0d8bb2fb7eee96760955e27c70bfb3efa58` (`origin/sub/AST-2102/AST-2106-grouped-skipped-page`)
**Corpus:** `c04b07deda8f5a750afd473ec847d06ed2207065`
**Overall:** CLEAN

## Canon scores

Frozen list empty (Description **Citations:** none; parent **Canon Scope:** none). No directive ids to score.

| (none) | — | — | — |

## Column diff vs plan stage

(aligned) — Joan recorded the same empty canon column; no per-id grades to compare.

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Sibling carry vs `origin/dev`:** Three-dot diff also includes AST-2105 product and QA (`src/utils/config.py`, `tests/component/utils/test_config.py`, `docs/test-bible/utils/config.md`, `ast-2105` issue doc) because this sub is built on `ftr/AST-2102-group-skipped-jobs` before AST-2105 is on `origin/dev`. Expected merge-base behavior — not AST-2106 scope creep. AST-2106’s own commits touch only the two frontend files (`7673e3216`) and Betty’s fixture/tests/bible (`a571f0d8b`).
- **Build stub staleness:** Review stub still says the manifest fixture lacks `groups`; the test commit added `groups` mirroring AST-2105. Product and tests are aligned; Chuckles may refresh the stub when appending this review.
- **Canon Scope (intentional):** UI placement / manifest-driven UI spirit applies in principle; frozen list correctly stays empty — not **ESCALATE**.

## What's solid

- **Plan fidelity:** `StateUiContext` `groups` type matches Stage 1; `skipGroups` memo implements member → prefix → catch-all, manifest order, empty groups dropped; below-floor section uses `below_dispatch_key` (Fail member per manifest).
- **AC 7 design:** Second `useSectionExpandPolicy({ expandAll: true })` with inverted semantics (collapsed keys in the set, groups start open) keeps Expand One for sections; candidate change resets both key sets in one effect — matches plan and hook behavior.
- **AC 9:** No `handleRetry` / `bulk_state` hunks in the page diff; **AC9** test asserts two distinct POST bodies for mixed Error + Fail selection.
- **AC 10:** Ticket `rg` on `JobsSkipped.tsx` returns no matches at publish tip.
- **Tests:** Eight new cases cover AC 4–9 with `GROUP_TEXT` anchoring to avoid `Fail` vs `Failed LIKE` ambiguity; fixture `groups` matches AST-2105 manifest shape; bible documents manifest and commands.

## Recommended actions (Chuckles / downstream — not Radia)

- Append this artifact to `docs/features/interface/ast-2106-grouped-collapsible-skipped-page.md`; commit `docs(AST-2106): Radia review — clean`; push `origin/sub/AST-2102/AST-2106-grouped-skipped-page`.
- Post slim upshot via `linear_proxy.py --as radia save-comment`; move to **Review Posted**; **PROCEED** → **User Testing** (no **resolve-child** unless Susan wants build-stub wording updated).

context_tokens≈22000

```
[code-rubric] PROCEED (Commit: a571f0d8b) Grouped Skipped page clean
```
