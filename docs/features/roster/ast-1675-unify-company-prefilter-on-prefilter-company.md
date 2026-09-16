# AST-1675: Unify company prefilter on prefilter_company

**Linear:** [AST-1675](https://linear.app/astralcareermatch/issue/AST-1675/unify-company-prefilter-on-prefilter-company-unify-company-prefilter-on)
**Parent:** [AST-1671](https://linear.app/astralcareermatch/issue/AST-1671) — Unify company prefilter on prefilter_company and delete the dual-key shims
**Publish ref:** `sub/AST-1671/AST-1675-unify-company-prefilter-on-prefilter-company`

Company prefilter is one hop with two catalog identities: Scheduled Actions / `dispatch_task` use bare `prefilter`, while Manage Tasks / `TASK_CONFIG` / consult use `prefilter_company`. Dual-key shims (`dispatch_row_task_key`, `dispatch_task_grouping_catalog_key`, consult’s dual branch) hide the split. This ticket collapses the lasting catalog string onto `prefilter_company`, retargets company dispatch rows, deletes the shims, and ships a one-release leftover alias then drops it. Python callables (`prefilter_company_batch`), `company_data` key `prefilter_company_notes`, and the `ROSTER_CONFIG["prefilter"]` hop-policy block key stay. Somerset (and peers) live `dispatch_task` UPDATE is ops after deploy — not a product deliverable here.

## Explicit scope gate

Ticket **## Scope** names only these four files and the kinds of change listed under Technical scope. Every Files Changed row and every Stage step stays inside:

- `src/utils/config.py` — frozenset / helper retarget; delete dual-key shim special cases (and helpers if they exist only for this hop); one-release alias introduce then drop
- `src/core/consult.py` — single `prefilter_company` company-batch route; score-floor / row lookup without shim rename
- `src/ui/api/api_admin.py` — adhoc live-content and hard-coded company-prefilter checks on `prefilter_company`; form/meta follows retargeted helpers
- `src/data/database.py` — idempotent schema-ensure company `task_key` `prefilter` → `prefilter_company`; never rewrite `craft_prefilter_rubric`

Out of scope (do not add files or kinds): renaming callables / `prefilter_company_notes` / `ROSTER_CONFIG["prefilter"]` block key; Somerset live UPDATE; AST-1670 inflow website-resolve keys; `tests/` / bible (Betty); `roster.py` evaluate body (already keyed `prefilter_company`).

**Canon (plan-stage read):** `patt.entity.batch-criteria` — claim shape stays criteria on the `dispatch_task` row after the key retarget; do not re-literalize prefilter eligibility (state / floor / batch size) in callers. Applicable statutes: none uniquely constrain this catalog-identity cutover (parent Architectural definition).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Retarget company-prefilter membership in `_DISPATCH_BATCH_CALL_MODE_ONE`, `_DISPATCH_COMPANY_ENTITY_TASK_KEYS`, `_dispatch_trigger_state_for_task_key`, `_dispatch_entity_type_for_task_key`; delete `dispatch_row_task_key` / `dispatch_task_grouping_catalog_key` (or leave pure identity with no prefilter branch); add then remove one-release `prefilter` → `prefilter_company` alias helper | utils |
| `src/core/consult.py` | Company batch branch matches `prefilter_company` only; stop importing/using `dispatch_row_task_key` for score-floor lookup (identity / alias during window) | core |
| `src/ui/api/api_admin.py` | `_build_adhoc_live_content` homepage+nav branch on `prefilter_company`; drop `dispatch_task_grouping_catalog_key` special-case usage (identity grouping key); wire alias at catalog-input edges while live | ui |
| `src/data/database.py` | In `_ensure_dispatch_task_schema`, idempotent company-only UPDATE `task_key='prefilter'` → `'prefilter_company'` with unique-collision guard (AST-823 reverse / AST-703 collision precedent); never touch `craft_prefilter_rubric` | data |

## Stages

## Stage 1: Config — retarget helpers, introduce alias, delete dual-key shims

**Done when:** Company-prefilter membership in dispatch helper frozensets and `_dispatch_*_for_task_key` / `dispatch_task_admin_defaults` resolves under `prefilter_company`; `dispatch_row_task_key` / `dispatch_task_grouping_catalog_key` are gone or pure identity with no `prefilter` ↔ `prefilter_company` special case; a temporary alias maps leftover catalog input `prefilter` → `prefilter_company`; `ROSTER_CONFIG["prefilter"]` block key and `TASK_CONFIG["prefilter_company"]` are unchanged.

1. In `src/utils/config.py`, replace bare `"prefilter"` with `"prefilter_company"` in:
   - `_DISPATCH_BATCH_CALL_MODE_ONE` (today first member is `"prefilter"`)
   - `_DISPATCH_COMPANY_ENTITY_TASK_KEYS` (today first member is `"prefilter"`)
2. In `_dispatch_trigger_state_for_task_key`, change the company-prefilter branch from `if task_key == "prefilter":` to `if task_key == "prefilter_company":` still returning `ROSTER_CONFIG["prefilter"]["input_state"]` (HOMEPAGE_READY). Do **not** rename the `ROSTER_CONFIG["prefilter"]` dict key.
3. In `_dispatch_entity_type_for_task_key`, remove the redundant `task_key == "prefilter" or` prefix once `_DISPATCH_COMPANY_ENTITY_TASK_KEYS` contains `"prefilter_company"` — membership alone returns `"company"`.
4. Add a temporary one-release helper (name it exactly):
   ```python
   def alias_company_prefilter_catalog_key(task_key: str) -> str:
       """AST-1675 one-release: leftover catalog input `prefilter` → `prefilter_company`."""
       tk = (task_key or "").strip()
       if tk == "prefilter":
           return "prefilter_company"
       return tk
   ```
   Call it at the start of `dispatch_task_admin_defaults` (normalize `tk` before retired/TASK_CONFIG gates) so leftover Admin submit/resolve of `prefilter` does not KeyError / 400 during the cutover window.
5. Delete `dispatch_task_grouping_catalog_key` and `dispatch_row_task_key` entirely (they exist only for this hop’s dual identity). Do **not** leave a prefilter special-case body. Call sites are updated in Stages 2–3; if a compile break appears mid-stage, land Stage 2–3 in the same build session before publishing (same commit window as AST-1603 precedent — stages may be one commit or back-to-back before push).
6. Grep gate after this stage’s intended end-state (may wait until Stages 2–3 if helpers still imported):  
   `rg -n 'def dispatch_row_task_key|def dispatch_task_grouping_catalog_key' src/utils/config.py` → nothing, **or** pure identity with no prefilter branch (AC2).
7. Do **not** rename `prefilter_company_batch`, `prefilter_company_notes`, or `ROSTER_CONFIG["prefilter"]`. Do **not** add Somerset UPDATE SQL outside schema-ensure (Stage 4).

⚠️ **Decision:** Alias is a named one-release helper, not a permanent second identity and not a revival of `dispatch_row_task_key` (which mapped *to* bare `prefilter`). Direction is leftover `prefilter` → lasting `prefilter_company` only. Stage 5 removes the helper.

## Stage 2: Consult — single-route company prefilter; score floor without shim

**Done when:** `run_consult_task` company branch matches `prefilter_company` only (no dual tuple); `_dispatch_score_floor_for_task` looks up the candidate’s `dispatch_task` row by `prefilter_company` (via identity / alias), not by shim-renamed bare `prefilter`; `prefilter_company_batch` call body unchanged.

1. In `src/core/consult.py`, remove `dispatch_row_task_key` from the `src.utils.config` import list. Import `alias_company_prefilter_catalog_key` instead (while Stage 1 alias is live).
2. In `_dispatch_score_floor_for_task`, replace:
   ```python
   dispatch_tk = dispatch_row_task_key((task_key or "").strip())
   ```
   with:
   ```python
   dispatch_tk = alias_company_prefilter_catalog_key((task_key or "").strip())
   ```
   Keep the rest of the row match / `effective_dispatch_score_floor` logic unchanged. Do **not** hard-code score floors or claim predicates (canon: `patt.entity.batch-criteria`).
3. In `run_consult_task`’s `entity_type == "company"` block, replace:
   ```python
   if task_key in ("prefilter", "prefilter_company"):
   ```
   with normalization then single match:
   ```python
   task_key = alias_company_prefilter_catalog_key(task_key)
   if task_key == "prefilter_company":
   ```
   Leave the `roster.prefilter_company_batch(...)` body and skipped/error math unchanged.
4. Grep gate: `rg -n 'prefilter", "prefilter_company"|prefilter_company", "prefilter' src/core/consult.py` → nothing (AC3).
5. Run `python3 -m py_compile src/core/consult.py`.

⚠️ **Decision:** Normalize `task_key` once at the company prefilter branch (and in score-floor) rather than keeping a dual tuple “for safety.” Schema ensure (Stage 4) makes lasting rows `prefilter_company`; the alias covers leftover input / tests for one release only.

## Stage 3: Admin — live-content and form/meta on prefilter_company

**Done when:** Adhoc live-content for `prefilter_company` still builds homepage+nav; `_dispatch_task_key_form_meta("prefilter_company")` yields `entity_type` `company` and `trigger_state` `HOMEPAGE_READY` via retargeted helpers; no lasting hard-coded company-prefilter catalog check remains on bare `prefilter`; grouping meta uses identity (no shim).

1. In `src/ui/api/api_admin.py`, remove `dispatch_task_grouping_catalog_key` from imports. Import `alias_company_prefilter_catalog_key` (while live).
2. In `_dispatch_task_key_form_meta`, replace:
   ```python
   grouping_key = dispatch_task_grouping_catalog_key(task_key)
   ```
   with identity after alias:
   ```python
   catalog_key = alias_company_prefilter_catalog_key(task_key)
   grouping_key = catalog_key
   ```
   Use `catalog_key` consistently for `TASK_CONFIG.get(catalog_key)` / defaults resolution in this function (today it already has a `catalog_key` local — keep one normalized value; do not leave a second un-normalized path that still KeyErrors on leftover `prefilter`).
3. In `create_dtask` (POST `/dispatch_tasks`) and any sibling update path that validates `task_key` before save, normalize with `alias_company_prefilter_catalog_key` **before** `dispatch_task_key_retired_message` / `_dispatch_task_key_trigger_error` / `save_dispatch_task` so leftover submit of `prefilter` does not 400 during the alias window (AC6). Persist the **normalized** key (`prefilter_company`), not bare `prefilter`.
4. In `_build_adhoc_live_content`, change:
   ```python
   if task_key == "prefilter":
   ```
   to operate on the normalized key:
   ```python
   task_key = alias_company_prefilter_catalog_key(task_key)
   ...
   if task_key == "prefilter_company":
   ```
   Keep the homepage_text / website_content / nav_links assembly body identical.
5. Grep gate (lasting catalog identity — after Stage 5 alias drop this must still hold for hard-coded sites):  
   `rg -n '"prefilter"' src/ui/api/api_admin.py` → no company-prefilter **catalog** hard-code left (comments OK). During Stages 1–4, alias helper references to the string `"prefilter"` inside `alias_company_prefilter_catalog_key` live in `config.py` only.
6. Run `python3 -m py_compile src/ui/api/api_admin.py`.

## Stage 4: Database — idempotent company row retarget

**Done when:** After `_ensure_dispatch_task_schema` on a DB that had company `task_key='prefilter'`, those rows read `task_key='prefilter_company'`; `craft_prefilter_rubric` rows (and any non-company `prefilter` rows) are unchanged; unique triple collisions do not abort schema ensure.

1. In `src/data/database.py`, inside `_ensure_dispatch_task_schema` (after table/column migrations, before setting `_dispatch_task_schema_ensured = True`), append an idempotent block commented `# AST-1675: company prefilter catalog retarget prefilter → prefilter_company`.
2. Implementation (literal intent — builder may use equivalent SQL as long as behavior matches):
   - Select company rows still on the old key:
     `SELECT id, candidate_id, trigger_state FROM dispatch_task WHERE entity_type = 'company' AND task_key = 'prefilter'`
   - For each row: if another row already exists for the same `(candidate_id, 'prefilter_company', trigger_state)` (NULL-safe `candidate_id` / `trigger_state` compare, same pattern as AST-973 dispatch trigger remaps ~`existing = conn.execute(... id != ?)`), **DELETE** the old `prefilter` row (prefer keeping the already-correct `prefilter_company` companion — reverse of AST-823’s collision discuss).
   - Else `UPDATE dispatch_task SET task_key = 'prefilter_company' WHERE id = ?`. On `sqlite3.IntegrityError`, DELETE the old row (AST-703 / AST-973 collision drop).
   - `conn.commit()` once after the loop.
3. **Do not** `UPDATE` / `DELETE` rows where `task_key = 'craft_prefilter_rubric'` (or any non-company entity). The `entity_type = 'company' AND task_key = 'prefilter'` predicate is the guard.
4. **Do not** reintroduce AST-823’s reverse direction (`prefilter_company` → `prefilter`) if any remnant still exists — if found, stop and comment on the parent; do not silently keep both directions.
5. Run `python3 -m py_compile src/data/database.py`.

⚠️ **Decision:** Prefer keeping an existing `prefilter_company` companion and deleting the leftover `prefilter` row on collision — lasting identity wins. Do not merge column values across the two rows in this ticket.

**Ops gate (not code):** Description / handoff still states Somerset (and peers) must not manually UPDATE live `dispatch_task` to `prefilter_company` until this code is deployed. This stage’s schema-ensure is the product retarget for DBs the app opens; it is **not** a substitute for ops runbooks on hosts that never boot this build.

## Stage 5: Drop the one-release alias

**Done when:** `alias_company_prefilter_catalog_key` is gone from `src/`; leftover bare `prefilter` is no longer accepted as a catalog identity at Admin create/validate or consult normalization; lasting company-prefilter catalog sites use `prefilter_company` only; AC1 grep is clean for lasting catalog identity (frozenset membership, trigger/entity helpers, consult branch, admin live-content) while `ROSTER_CONFIG["prefilter"]` block key may remain.

1. Remove `def alias_company_prefilter_catalog_key` from `src/utils/config.py`.
2. In `src/utils/config.py`, `src/core/consult.py`, and `src/ui/api/api_admin.py`, delete every import and call of that helper. After removal:
   - `dispatch_task_admin_defaults` uses the submitted key as-is (no `prefilter` map).
   - `_dispatch_score_floor_for_task` uses `(task_key or "").strip()` directly.
   - `run_consult_task` company branch is exactly `if task_key == "prefilter_company":` with no preceding alias assign (or keep a local strip only).
   - Admin form meta / create / live-content use `prefilter_company` / identity only.
3. Final grep gates (AC1–3, AC7):
   - `rg -n '"prefilter"' src/utils/config.py src/core/consult.py src/ui/api/api_admin.py` — no lasting company-prefilter **catalog** identity still keyed as bare `prefilter` (frozenset membership, trigger/entity helpers, consult branch, admin live-content). `ROSTER_CONFIG["prefilter"]` block key and comments may remain.
   - `rg -n 'def dispatch_row_task_key|def dispatch_task_grouping_catalog_key' src/utils/config.py` — nothing, or pure identity with no prefilter branch.
   - `rg -n 'prefilter", "prefilter_company"|prefilter_company", "prefilter' src/core/consult.py` — nothing.
   - `rg -n 'def prefilter_company_batch|prefilter_company_notes' src/` — still finds callable and company_data key.
   - `rg -n 'alias_company_prefilter_catalog_key' src/` — nothing.
4. Compile: `python3 -m py_compile src/utils/config.py src/core/consult.py src/ui/api/api_admin.py src/data/database.py`. Lint the touched files per repo habit before publish.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Traceability

- **AC1** → Stages 1, 3, 5 (helpers + admin + final grep)
- **AC2** → Stage 1 step 5 + Stage 5 grep
- **AC3** → Stage 2 + Stage 5 grep
- **AC4** → Stages 1 + 3 (form meta / live-content on `prefilter_company`)
- **AC5** → Stage 4
- **AC6** → Stage 1 alias introduce + Stage 3 wire + Stage 5 drop
- **AC7** → Boundaries enforced every stage; Stage 5 grep
- **AC8** → Ops gate note in Stage 4 + summary (no child does Somerset UPDATE)

## Joan validate

```
[plan-rubric]
**Ticket:** AST-1675
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref tip:** 0416f88673605a0e7fcab8ba3d8773a5e6ee402e (`sub/AST-1671/AST-1675-unify-company-prefilter-on-prefilter-company`)

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-criteria | A | | |

## Traceability

AC1→S1,S3,S5 · AC2→S1,S5 · AC3→S2,S5 · AC4→S1,S3 · AC5→S4 · AC6→S1,S3,S5 · AC7→boundaries+S5 · AC8→S4,summary — all eight child ACs mapped; no orphan stages.

## Findings

### acceptable

- **Location:** Linear assignee
- **Finding:** Ticket status `Plan Ready` but assignee is Ada Lovelace, not Joan — Chuckles handoff gap; validation proceeded per spawn.
- **Recommendation:** Chuckles restores implementer after posting upshot per §8.

### acceptable

- **Location:** Stage ordering (Stages 2–3 vs Stage 4)
- **Finding:** Consult/admin normalize to `prefilter_company` for row lookup while live DB rows may still read `prefilter` until boot-time schema-ensure (Stage 4); safe only when Stages 1–4 publish atomically and `_ensure_dispatch_task_schema` runs before consult paths — plan’s “same commit window” / inseparable-cutover language covers this.
- **Recommendation:** Engineer must not push Stages 1–3 without Stage 4 in the same publish; no plan edit required.

context_tokens≈19500
```

## Review (build)

**Built @ `f6dbe417`** — `origin/sub/AST-1671/AST-1675-unify-company-prefilter-on-prefilter-company`

Stages 1–5 landed: helpers/admin/consult on `prefilter_company`; dual-key shims deleted; schema-ensure retargets company `prefilter` → `prefilter_company`; one-release alias introduced in `c10754a5` then dropped in `f6dbe417`. Callables / `prefilter_company_notes` / `ROSTER_CONFIG["prefilter"]` unchanged. Somerset live UPDATE remains ops-after-deploy. Test path remains Betty `qa-child`.

## Radia review

```
[code-rubric]
**Ticket:** AST-1675
**Publish ref:** `e68aaa8e2ea407d07b37a3fa674d040eae0cbb91` (`origin/sub/AST-1671/AST-1675-unify-company-prefilter-on-prefilter-company`)
**Corpus:** `fc0c368e5927a57f1561c057ce9a0ff4abe1fb13`
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-criteria | A | | |

## Column diff vs plan stage

(aligned) — Joan `A`; code review `A` on `patt.entity.batch-criteria`.

## Frame diff

(none)

## Findings

### discuss

- **Location:** Branch history — commit `adc287cd` (`test(AST-1672): DISCOVERED resolve registry SSOT coverage`)
- **Finding:** The AST-1675 publish ref carries sibling AST-1672 test/bible edits (`TestAst505InflowDiscoveryConfig`, new `TestAst1672DiscoveredResolveRegistrySsot`) without AST-1672 product code (`DISCOVERED` is absent from `src/utils/config.py` at tip). Manifest-green does not cover those nodes; a full `test_config.py` run would red until AST-1672 lands.
- **Recommendation:** Chuckles strips or re-homes `adc287cd` before ftr rollup, or ensures AST-1672 product precedes/merges with this sub — not an AST-1675 canon fix, but branch hygiene before parent UAT.

### advisory

- **Location:** `tests/component/utils/test_config.py` — `TestAst1214DispatchAdminDefaultsWidened::test_helper_resolvable_and_mailbox_defaults`
- **Finding:** The `meteorite_email` mailbox-default assertion bundled in `adc287cd` matches current product (`entity_type`/`trigger_state` `None`) and is harmless; it is unrelated to the prefilter cutover.
- **Recommendation:** No AST-1675 action; keep the correction when AST-1672 branch is reconciled.

## What's solid

- **Scope discipline:** Product diff stays inside the four planned files (`config.py`, `consult.py`, `api_admin.py`, `database.py`); callables, `prefilter_company_notes`, and `ROSTER_CONFIG["prefilter"]` block key untouched.
- **Cutover completeness:** Dual-key shims removed; one-release alias introduced (`c10754a5`) and dropped (`f6dbe417`); lasting catalog identity is `prefilter_company` across helpers, consult route, admin live-content, and form meta.
- **Batch-criteria:** Score-floor lookup uses identity row match on `dispatch_task` (`_dispatch_score_floor_for_task`); no new eligibility literals in consult/dispatcher paths — catalog-key normalization only.
- **Schema ensure:** Idempotent company-only retarget with companion-row DELETE-on-collision and `craft_prefilter_rubric` guard; bind tuple counts match placeholders.
- **Tests:** Manifest-aligned coverage (shim removal, lasting identity, consult bare-key reject, admin grouping/live-content, dispatcher union claim, schema retarget) matches the plan stages.
```

## Resolution

**2026-09-16** — `resolve(AST-1675): — clean` @ tip after Radia intake `d85593f9`.

- **fix-now:** none (Overall CLEAN).
- **discuss:** Sibling `adc287cd` (AST-1672 test/bible on this publish tip without AST-1672 product) — Chuckles branch hygiene before ftr rollup; not an AST-1675 product change. Left as-is on this sub.
- **advisory:** `TestAst1214` meteorite_email assertion unrelated to cutover — no AST-1675 action.
- Product tip unchanged from Tests Passed / review tip (`e68aaa8e` product+tests; Radia docs `d85593f9`).
