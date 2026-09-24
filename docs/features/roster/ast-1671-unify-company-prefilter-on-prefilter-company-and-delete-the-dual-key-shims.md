# AST-1671 — Unify company prefilter on prefilter_company and delete the dual-key shims

<!-- linear-archive: AST-1671 archived 2026-09-24 -->

## Linear archive (AST-1671)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1671/unify-company-prefilter-on-prefilter-company-and-delete-the-dual-key  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** chuckles  
**Priority / estimate:** None / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Company prefilter is one hop with two catalog identities — Scheduled Actions / `dispatch_task` say `prefilter`, while Manage Tasks / `TASK_CONFIG` / consult say `prefilter_company`. Shims hide the split and every scored or admin path pays for the rename. This epic collapses the catalog string onto `prefilter_company` (matching Manage Tasks), retires the dual-key helpers, and leaves function names and `company_data` keys alone. Outcome: one greppable identity for the hop end-to-end, with a one-release alias so leftover rows do not 400 during cutover.

## Functional scope

1. **Single catalog identity** — Company prefilter’s dispatch / Scheduled Action / admin catalog string is `prefilter_company` only. `prefilter` is not a lasting second identity for that hop.
2. **Retarget live company rows** — Company `dispatch_task` rows keyed `prefilter` become `prefilter_company` (entity_type company only). `craft_prefilter_rubric` is untouched.
3. **Admin and dispatch helpers agree** — Admin defaults and the shared entity/trigger/batch_call_mode helpers resolve company prefilter under `prefilter_company`, not `prefilter`.
4. **Shims gone; consult single-routes** — Dual-key shims (`dispatch_row_task_key` / `dispatch_task_grouping_catalog_key` special cases and consult’s dual branch) are deleted. Consult’s company prefilter branch keys on `prefilter_company` only.
5. **One-release alias, then drop** — A temporary `prefilter` → `prefilter_company` alias keeps leftover rows and tests from 400ing for one release, then the alias is removed.
6. **Ops gate unchanged** — Somerset (or any candidate) `dispatch_task` UPDATE to the new key waits until this code is live — product ships the ability; ops applies the UPDATE after.

Out of scope: renaming Python callables (`prefilter_company_batch`, etc.), renaming `company_data` key `prefilter_company_notes`, renaming the `ROSTER_CONFIG["prefilter"]` config-block key (hop policy bag, not a catalog identity), and AST-1670 inflow website-resolve work.

## Component scope

* `src/utils/config.py` — **modified** — retarget company-prefilter membership in dispatch helper frozensets and admin/default resolvers to `prefilter_company`; delete dual-key shim functions/special cases; add then remove the one-release `prefilter` → `prefilter_company` alias.
* `src/core/consult.py` — **modified** — company prefilter batch branch routes on `prefilter_company` only; scored-floor / row lookup no longer depends on dual-key shims for this hop.
* `src/ui/api/api_admin.py` — **modified** — adhoc live-content and any hard-coded company-prefilter task_key checks use `prefilter_company`; form/meta path follows the retargeted helpers.
* `src/data/database.py` — **modified** — idempotent schema-ensure (or equivalent one-time) retarget of company `dispatch_task.task_key` `prefilter` → `prefilter_company`; do not touch `craft_prefilter_rubric`.

## Technical scope

* `config` dispatch helper frozensets / `_dispatch_*_for_task_key` / `dispatch_task_admin_defaults` — replace bare `prefilter` membership with `prefilter_company` for company entity, trigger state, and batch_call_mode resolution.
* `config` shim surface — delete `dispatch_row_task_key` / `dispatch_task_grouping_catalog_key` prefilter special cases (and the helpers themselves if they exist only for this hop); callers use identity / `prefilter_company`.
* `config` one-release alias — temporary accept/map of leftover `prefilter` catalog input onto `prefilter_company`; remove after the retarget window.
* `consult` company branch — single `prefilter_company` route into `prefilter_company_batch`; drop `("prefilter", "prefilter_company")` dual match.
* `consult` score-floor / dispatch-row lookup — resolve the company prefilter row by `prefilter_company` without shim rename.
* `api_admin` live-content / catalog meta — company homepage+nav preview and picker defaults keyed on `prefilter_company`.
* `database` schema ensure — idempotent UPDATE company rows `task_key='prefilter'` → `'prefilter_company'`; guard unique-collision the same way AST-823’s reverse direction did; never rewrite `craft_prefilter_rubric`.

## Architectural definition

* **Patterns to reuse**
  * [`patt.entity.batch-criteria`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.entity.batch-criteria.md>) — claim shape (state, floors, ordering) stays criteria on the `dispatch_task` row after the key retarget; callers must not re-literalize prefilter eligibility.
* **New patterns proposed** — none.
* **Applicable statutes** — none of the in-force logging statutes uniquely constrain this catalog-identity cutover; say so explicitly. (Draft config/catalog directives exist under `canon/directives/draft/` but are **not** in force — do not score against them.)

## Acceptance criteria

1. **Single lasting catalog string** — `rg -n '"prefilter"' src/utils/config.py src/core/consult.py src/ui/api/api_admin.py` shows no lasting company-prefilter **catalog** identity (frozenset membership, trigger/entity helpers, consult branch, admin live-content) still keyed as bare `prefilter`; failing = any of those sites still treat `prefilter` as the hop’s permanent task_key. (`ROSTER_CONFIG["prefilter"]` block key and comments may remain.)
2. **Shims deleted** — `rg -n 'def dispatch_row_task_key|def dispatch_task_grouping_catalog_key' src/utils/config.py` returns nothing **or** those helpers are pure identity with no prefilter branch; failing = a special-case still maps `prefilter` ↔ `prefilter_company`.
3. **Consult single-routes** — `rg -n 'prefilter", "prefilter_company"|prefilter_company", "prefilter' src/core/consult.py` returns nothing; company batch entry matches `prefilter_company` only. Failing = dual tuple/branch still present.
4. **Admin agrees** — Admin picker / `_dispatch_task_key_form_meta("prefilter_company")` yields entity_type `company` and trigger_state `HOMEPAGE_READY`; adhoc live-content for `prefilter_company` still builds homepage+nav. Failing = KeyError, empty defaults, or live-content only wired under bare `prefilter`.
5. **Rows retargeted (company only)** — After schema ensure on a DB that had company `task_key='prefilter'`, those rows read `prefilter_company`; `craft_prefilter_rubric` rows unchanged. Failing = company `prefilter` rows remain, or rubric rows were rewritten.
6. **Alias then gone** — While the one-release alias is live, submitting/resolving leftover `prefilter` does not 400; after the drop commit, `prefilter` is rejected or ignored as a catalog identity and no alias helper remains. Failing = permanent alias left in tree, or cutover 400s on leftover rows before drop.
7. **Non-catalog names preserved** — `rg -n 'def prefilter_company_batch|prefilter_company_notes' src/` still finds the callable and the company_data key. Failing = those were renamed as part of this epic.
8. **Ops gate** — Description / handoff still states Somerset (and peers) must not UPDATE `dispatch_task` to `prefilter_company` until this code is deployed; no child “does the Somerset UPDATE.” Failing = ops UPDATE treated as a product deliverable inside a child.

## Open questions

none

## Proposed child tickets

**Monolith check:** Functional scope has 6 capabilities; one child is intentional — helpers, consult, admin, schema retarget, and alias introduce/drop are one cutover. Splitting them leaves Admin showing a key the picker rejects (Susan’s ops warning) or a permanent shim. AST-1670 (inflow website resolve) is adjacent on Astral Roster but does not share this catalog string.

#### 1: **Unify company prefilter on prefilter_company - Ada**

Owns the full cutover: retarget helper frozensets and admin defaults to `prefilter_company`, delete dual-key shims, consult single-route, schema-ensure company row retarget, one-release alias then drop. Does not rename callables or `prefilter_company_notes`. Does not apply Somerset’s live UPDATE (ops after deploy). Does not touch AST-1670 inflow keys.
**Citations:** `patt.entity.batch-criteria`
**Scope:** `src/utils/config.py` — **modified** — retarget company-prefilter membership in dispatch helper frozensets and admin/default resolvers to `prefilter_company`; delete dual-key shim functions/special cases; add then remove the one-release `prefilter` → `prefilter_company` alias. · `src/core/consult.py` — **modified** — company prefilter batch branch routes on `prefilter_company` only; scored-floor / row lookup no longer depends on dual-key shims for this hop. · `src/ui/api/api_admin.py` — **modified** — adhoc live-content and any hard-coded company-prefilter task_key checks use `prefilter_company`; form/meta path follows the retargeted helpers. · `src/data/database.py` — **modified** — idempotent schema-ensure (or equivalent one-time) retarget of company `dispatch_task.task_key` `prefilter` → `prefilter_company`; do not touch `craft_prefilter_rubric`. · `config` dispatch helper frozensets / `_dispatch_*_for_task_key` / `dispatch_task_admin_defaults` — replace bare `prefilter` membership with `prefilter_company` for company entity, trigger state, and batch_call_mode resolution. · `config` shim surface — delete `dispatch_row_task_key` / `dispatch_task_grouping_catalog_key` prefilter special cases (and the helpers themselves if they exist only for this hop); callers use identity / `prefilter_company`. · `config` one-release alias — temporary accept/map of leftover `prefilter` catalog input onto `prefilter_company`; remove after the retarget window. · `consult` company branch — single `prefilter_company` route into `prefilter_company_batch`; drop `("prefilter", "prefilter_company")` dual match. · `consult` score-floor / dispatch-row lookup — resolve the company prefilter row by `prefilter_company` without shim rename. · `api_admin` live-content / catalog meta — company homepage+nav preview and picker defaults keyed on `prefilter_company`. · `database` schema ensure — idempotent UPDATE company rows `task_key='prefilter'` → `'prefilter_company'`; guard unique-collision the same way AST-823’s reverse direction did; never rewrite `craft_prefilter_rubric`.
**Estimate: 5**

---

## Original brief

Company prefilter is one hop with two catalog strings. Dispatch/Scheduled Actions use `prefilter` (AST-823 migrated live rows onto that name). Consult, `TASK_CONFIG`, `agent_task`, and `do_task` use `prefilter_company`. Shims paper over it: `dispatch_row_task_key`, `dispatch_task_grouping_catalog_key`, consult routing (`prefilter` or `prefilter_company`), admin trigger/entity helpers keyed on `prefilter`.

Canonical string: `prefilter_company`. Matches Manage Tasks. Do not keep `prefilter` as a second identity.

Need:

1. Retarget company `dispatch_task` rows: `prefilter` → `prefilter_company` (entity_type company only; do not touch `craft_prefilter_rubric`).
2. Point admin defaults / `_dispatch_entity_type_for_task_key` / `_dispatch_trigger_state_for_task_key` / `_DISPATCH_COMPANY_ENTITY_TASK_KEYS` / batch_call_mode at `prefilter_company`.
3. Delete the shims. Consult company branch routes on `prefilter_company` only.
4. One-release alias `prefilter` → `prefilter_company` so leftover dispatch rows and tests do not 400, then drop it.

Leave Python function names (`prefilter_company_batch`) and the company_data key `prefilter_company_notes` — those are not catalog identities.

Do not apply the Somerset `dispatch_task` UPDATE until this code lands, or Admin will show a key the picker still treats as `prefilter`.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
