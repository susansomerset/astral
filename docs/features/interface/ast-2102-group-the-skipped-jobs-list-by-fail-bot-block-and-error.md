# AST-2102 — Group the Skipped jobs list by Fail, Bot block and Error

<!-- linear-archive: AST-2102 archived 2026-10-16 -->

## Linear archive (AST-2102)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2102/group-the-skipped-jobs-list-by-fail-bot-block-and-error  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 3  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

The Skipped list shows one section per terminal state in pipeline order, from late hops to early ones. That mixes three very different kinds of job together. **Errors** are technical breakage that a retry may fix. **Bot blocks** are pages we couldn't read and need a human or a different fetch. **Fails** are honest verdicts where the job didn't make the cut, or it was dropped. Susan has to scan the whole page to find the jobs that need her action. This epic groups the Skipped page under collapsible headings, **Error**, **Bot block**, then **Fail**, so actionable breakage sits on top. Group membership comes from the state-name grammar that [AST-2073](https://linear.app/astralcareermatch/issue/AST-2073) (Revise terminal states) puts in place. Any state the grammar doesn't place lands in an **Other** group, so holes in the process show up instead of hiding.

**Prerequisite:** this epic dispatches only after [AST-2073](https://linear.app/astralcareermatch/issue/AST-2073) is Done. AST-2073 renames every Skipped state and rewrites the same Skipped section, label, and retry blocks in `config.py`, and the prefix rules below only partition cleanly on its names.

## Functional scope

1. **Groups by name pattern.** The group a Skipped section belongs to is decided by its state name, using rules held in config, in this order:
   * **Error**: the name starts with `ERROR_`.
   * **Bot block**: the name starts with `BOT_BLOCKED_`.
   * **Fail**: the name starts with `FAILED_`, `METEORITE_FAILED_`, or `JD_SCRAPE_FAIL_`. Fail also explicitly includes `CANDIDATE_SKIPPED` and the below-dispatch-score-floor virtual section.
   * **Other**: anything that matches none of the rules above. Today, after AST-2073, that is `INVALID_TITLE`, a verdict whose name doesn't follow either grammar.
2. **Fixed group order.** The page renders Error, then Bot block, then Fail, then Other. Each group heading shows its label and total job count.
3. **Groups collapse.** Each group heading expands or collapses its contents. Under a group, today's per-state sections render unchanged: label, count, their own collapse, rubric columns, row actions, checkboxes, and sort. Within a group, states keep their current relative order.
4. **Legacy states too.** Unmapped legacy state sections (states on rows but not in the Skipped list) go through the same rules. Any that match none land in Other.
5. **Empty groups are hidden.** A group with no jobs renders no heading. That includes Other, which shows only when something is unplaced. "No skipped jobs" still shows when everything is empty.
6. **Behavior unchanged.** Bulk Retry across a mixed selection, Resurrect, the detail modal, and per-section expand all work exactly as today.

## Component scope

* `src/utils/config.py` — **modified** — new ordered Skipped-group rule registry (key, label, name prefixes, explicit members); state-UI manifest skipped block carries it.
* `src/ui/frontend/src/contexts/StateUiContext.tsx` — **modified** — manifest TS interface gains the skipped group rules.
* `src/ui/frontend/src/pages/JobsSkipped.tsx` — **modified** — assigns each built section to a group from the manifest rules and renders collapsible group headings around the existing per-state sections.

## Technical scope

* `config.py`
  * **Group rule registry.** A new ordered constant for the Skipped groups. Each entry has a group key, a display label, a list of state-name prefixes, and a list of explicit member states. Explicit members are `CANDIDATE_SKIPPED` and the existing below-dispatch virtual key, both on Fail. The last entry (Other) has neither prefixes nor members: it is the catch-all. Prefixes and members are written once here and nowhere else.
  * **Guard.** A module-level assert checks that every explicit member is a `SKIPPED_STATES` key or the below-dispatch virtual key, and that only the last group is a catch-all.
  * **Manifest.** `build_state_ui_manifest()`'s `jobs.skipped` block gains a `groups` entry emitted from the registry (ordered key, label, prefixes, members). `section_order`, `section_labels`, and the bulk-retry map are unchanged.
* `StateUiContext.tsx` — the `StateUiManifest.jobs.skipped` interface is modified to add `groups`.
* `JobsSkipped.tsx`
  * The section memo is modified to assign each built section (below-floor, normal, legacy) to a group. The rules are applied in this order: an explicit member match, then the first group with a matching prefix, then the catch-all.
  * The render is modified to emit a collapsible group heading (label and total count) before each non-empty group's sections, keyed for the existing expand-policy hook alongside the section keys.
  * Per-state section and table markup, sort, retry, and actions are unchanged. No job-state string literals or prefixes are typed in the page.

## Architectural definition

* **Patterns to reuse** — `no established pattern applies`. None of the 22 in-force directives under `canon/directives/active/` is a UI, config-manifest, or list-grouping pattern. Draft `stat.layers.ui-config-driven-business-logic` and `stat.config.derive-dont-restate` are **not** in force and are not cited as law. This definition follows their spirit: the grouping rules live in config, reach React through the manifest, and are typed once. AST-2073's proposed `patt.state.terminal-naming` (not yet approved) is the naming grammar these prefixes rely on. Once approved, it is the reason the prefixes hold.
* **New patterns proposed** — none.
* **Applicable statutes** — none apply. No route, logging, batch, dispatch, entity, or artifact code changes. The manifest GET route body is untouched; only the dict it returns grows. In-force `stat.logging.*`, `stat.batch.*`, `stat.dispatch.*`, and `stat.entity.*` govern none of the three files' changed units.

**Canon Scope:** none (explicit), locked at Discussion.

## Acceptance criteria

1. **Manifest groups.** `GET /api/state_ui_manifest` → `jobs.skipped.groups[*].label` is exactly `["Error","Bot block","Fail","Other"]`. Error's prefixes are `["ERROR_"]` and Bot block's are `["BOT_BLOCKED_"]`. Fail's prefixes are `["FAILED_","METEORITE_FAILED_","JD_SCRAPE_FAIL_"]`, and its members are `CANDIDATE_SKIPPED` plus `jobs.skipped.below_dispatch_key`. Other has empty prefixes and members. **Fail:** any other label, order, prefix, or member.
2. **Rules partition today's list as intended.** On a tree with AST-2073 merged, run:

```python
python3 -c "
from src.utils import config as c
g = c.build_state_ui_manifest()['jobs']['skipped']['groups']
def grp(s):
    for x in g:
        if s in x['members']: return x['label']
    for x in g:
        if any(s.startswith(p) for p in x['prefixes']): return x['label']
    return g[-1]['label']
print(sorted(s for s in c.SKIPPED_STATES if grp(s) == 'Other'))"
```

**Pass:** prints `['INVALID_TITLE']`. **Fail:** any other list. For example, a `FAILED_TECHNICAL*` or bare `BOT_BLOCKED` still present means AST-2073 hasn't landed, and an `ERROR_`/`BOT_BLOCKED_` name in Other means the rules are wrong.
3\. **Guard bites.** Temporarily adding `"NOT_A_STATE"` to Fail's members makes `python -c "import src.utils.config"` raise `AssertionError`. **Fail:** the import succeeds.
4\. **Page renders groups in order.** For a candidate with one job each in an `ERROR_*` state, a `BOT_BLOCKED_*` state, `FAILED_JD`, and `CANDIDATE_SKIPPED`, the Skipped page shows headings Error (1), Bot block (1), Fail (2), top to bottom, and no Other heading. Each per-state section appears under its own group. **Fail:** wrong heading order, a section under the wrong heading, a wrong count, or an Other heading.
5\. **Other surfaces holes.** Adding one `INVALID_TITLE` job makes an Other (1) heading render last, containing the Invalid Title section. A job on an unmapped legacy state named `ERROR_SOMETHING_OLD` renders under Error, and one on `MYSTERY_STATE` renders under Other. **Fail:** any of the three lands elsewhere, or Other renders above Fail.
6\. **Below floor is Fail.** A `virtual_skip` row renders under the Fail heading. **Fail:** it renders above Error or outside Fail.
7\. **Groups collapse.** Clicking a group heading hides all of its per-state sections, and clicking again restores them, with each section's own expanded state unchanged. **Fail:** the group doesn't collapse, or re-expanding resets its sections.
8\. **Empty groups hidden.** For a candidate whose only skipped job is `FAILED_JD`, only the Fail heading renders. A candidate with no skipped jobs sees "No skipped jobs". **Fail:** an empty heading renders, or the empty-state text is missing.
9\. **Behavior unchanged.** Selecting one job in an `ERROR_*` state and one `FAILED_DO` job, then Retry, sends one `POST /api/jobs/bulk_state` per distinct `bulk_retry_to_state_by_from_state` target, same as `origin/dev`. Section sort and Resurrect behave as before. **Fail:** any changed POST, or lost sort/action behavior.
10\. **No literals in React.** `rg -n '"[A-Z]+(_[A-Z]+)*_"|"[A-Z]+(_[A-Z]+)+"' src/ui/frontend/src/pages/JobsSkipped.tsx` returns nothing. **Fail:** any hit, meaning a prefix or state name hard-coded in the page instead of read from the manifest.
11\. **Builds clean.** `python -c "import src.utils.config"` exits 0. In `src/ui/frontend`, `npm run build` exits 0, and `npm run lint` reports no problem absent on `origin/dev`. **Fail:** non-zero exit, or a new lint problem.

## Open questions

none

## Proposed child tickets

#### 1!: **Skipped group rules in config and manifest - Ada**

After [AST-2073](https://linear.app/astralcareermatch/issue/AST-2073) is Done. Delivers the config side: the ordered Error / Bot block / Fail / Other rule registry (prefixes and explicit members), its guard, and the `groups` entry on the manifest `jobs.skipped` block. Does **not** touch any React file (#2).
**Citations:** none. No in-force directive governs config registries or the manifest dict.
**Scope:** `src/utils/config.py`. Technical scope: group rule registry; guard; manifest (the `config.py` items above, verbatim).
Estimate: 2

#### 2: **Grouped, collapsible Skipped page - Hedy**

After #1. Delivers the page: the manifest type gains `groups`. The Skipped page assigns every section (below-floor, normal, legacy) to a group by the manifest rules. It renders a collapsible heading with a total count per non-empty group, and leaves the per-state sections, retry, and actions unchanged. Does **not** own the rules (#1).
**Citations:** none. No in-force directive governs React pages.
**Scope:** `src/ui/frontend/src/contexts/StateUiContext.tsx`, `src/ui/frontend/src/pages/JobsSkipped.tsx`. Technical scope: the `StateUiContext.tsx` and `JobsSkipped.tsx` items above, verbatim.
Estimate: 2

**Monolith check:** Functional scope N = 6, children M = 2, split by layer (config/manifest vs. React).
**Scope partition check:** `config.py` → #1. `StateUiContext.tsx` and `JobsSkipped.tsx` → #2. No file is unclaimed and none is claimed twice.

---

## Original brief

Put error types on top, then bot block, then fail

**Answers (Susan, define round 1), to Open questions 1–4 in order:**

1. With the revised list of terminal states, this should be made much more straight forward by pattern match. In fact, use that standard for groupings, and put any outliers in the Other list so we can identify any holes in the process. If there are no others, do not show the Other section.
2. These would be under FAIL.
3. Group headings also collapse please.
4. Astral Interface, yes.

### Comments

#### chuckles — 2026-10-09T03:39:13.242Z
Project was unset; assigned **Astral Interface** (per Susan's define answer 4).

#### chuckles — 2026-10-09T02:49:47.533Z
@susan

1. **Bucket mapping.** Please confirm the proposed Error / Bot block / Fail mapping in the Description, especially the judgment calls:
   * Scrape and content misses (`JD_SCRAPE_FAIL`, `JD_SCRAPE_FAIL_MISSING`, `RELATIVE_LINK_FAIL`, `NEED_WEBSITE_CONTENT`, `NEED_CULTURE_CONTENT`, `NO_CULTURE_LINKS`) are filed as **Error**.
   * `JD_SCRAPE_FAIL_CLOSED` (posting closed) is filed as **Error**. Should it be **Fail** instead?
   * `JD_SCRAPE_FAIL_COOKIE` (cookie wall) is filed as **Bot block**.
   * `BUILD_FAILED` is filed as **Error**.
   * `INVALID_TITLE` is filed as **Fail**.
2. **Leftovers.** The below-dispatch-score-floor rows (today at the very top), `CANDIDATE_SKIPPED`, and unmapped legacy states fit none of the three groups. Is a fourth **Other** group at the bottom right, or should they go somewhere else?
3. **Display shape.** The proposal is group headings wrapping today's per-state collapsible sections. Should the group headings also collapse? Or did you want each group flattened into one table, with no per-state sections?
4. **Project.** The ticket has no Linear project. Should it go in **Astral Interface**? Dispatch and plan docs need one.

---

_Implementation detail may live in git history on `origin/dev`._
