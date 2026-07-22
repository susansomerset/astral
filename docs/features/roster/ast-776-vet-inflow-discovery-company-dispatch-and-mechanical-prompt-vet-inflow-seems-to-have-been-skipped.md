<!-- linear-archive: AST-776 archived 2026-07-22 -->

## Linear archive (AST-776)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-776/vet-inflow-discovery-company-dispatch-and-mechanical-prompt-vet-inflow  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-754 — vet_inflow seems to have been skipped?  
**Blocked by / blocks / related:** parent: AST-754

### Description

## What this implements

Make **vet_inflow_discovery** a schedulable **company** dispatch on **trigger_state NEW**: read the stored discovery blurb, run through Admin **vet_inflow_discovery** prompts (not an in-batch call), transition pass → **WEBSITE_FOUND** or reject → **VET_FAILED**. Update the **vet_inflow_discovery** prompt text to mechanical-only link-type rejection (articles, wiki, directories, BBB, job boards — no candidate-fit filtering). Seed/update the local dev prompt row.

## Acceptance criteria

2. **vet_inflow_discovery** runs only as a company dispatch on **NEW** rows, using Admin **vet_inflow_discovery** prompts (observable as a distinct dispatch batch on the company entity).
3. Vet pass → **WEBSITE_FOUND**; vet reject → **VET_FAILED**; rejected URLs are not re-recorded on later discovery runs.
4. **vet_inflow_discovery** prompt text (Admin Task Prompts / local dev row) explicitly limits vetting to mechanical link-type rejection — articles, wiki, directories, BBB listings, job boards, etc. — and forbids candidate-fit filtering at this stage.
5. After vet **WEBSITE_FOUND**, **fetch_website** dispatch can run and the downstream Scheduled Actions chain remains reachable.
6. With `debug=True`, Susan can trace discovery record → separate vet dispatch → **WEBSITE_FOUND** / **VET_FAILED** per AST-538.

## Boundaries

* Assumes sibling has already split discovery (no inline vet).
* Does not use **run_next** between **inflow_discovery** and **vet_inflow_discovery**.
* **inflow_resolve_website** is out of scope.
* Candidate-fit filtering belongs in **prefilter_company**, not here.

## Notes for planning

Primary files: `src/core/roster.py`, `src/core/consult.py`, `src/core/dispatcher.py`, `src/utils/config.py`, `src/data/database.py` dispatch seed. Vet task entity_type company, trigger NEW.

## Git branch (authoritative)

Per **orientation** § Branch law: parent **ftr/AST-754-vet-inflow-discovery-split**, child **sub/AST-754/<child-segment>**.

### Comments

#### betty — 2026-06-24T05:07:29.619Z
[check-linear]

Republished `origin/sub/AST-754/AST-776-vet-inflow-company-dispatch-mechanical-prompt` @ `46ad8dc` — linear cherry-pick chain on `origin/ftr/AST-754-vet-inflow-discovery-split` (no `Merge remote-tracking branch` / no polluted `merge-resume` dev merge).

**Dropped:** `merge-resume(AST-776)` (was a dev merge that re-introduced wrong `vet_inflow_discovery` → `run_inflow_discovery_batch` routing).

**validate-sub-log:** `RESULT: ok` (sub-only vs ftr).

**merge-tests:** `origin/tests` `17cd9b6` unchanged.

— Betty

#### radia — 2026-06-24T05:01:25.385Z
### Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-754/AST-776-vet-inflow-company-dispatch-mechanical-prompt` @ `60df32a`
**Doc:** `docs/features/roster/ast-776-vet-inflow-discovery-company-dispatch-and-mechanical-prompt-vet-inflow-seems-to-have-been-skipped.md` (Review section)

#### What's solid

- Plan stages 1–4: **`INFLOW_CONFIG["vet"]`**, company/**`NEW`** schedulable **`vet_inflow_discovery`**, eligibility split on **`inflow_discovery_blurb`**, **`vet_inflow_discovery_company`**, **`run_company_task`** routing by **`dispatch_task_key`**, consult company vet → **`run_company_task`** (not discovery batch), mechanical prompt migration.
- §2.6 / §2.2: state transitions and **`do_task`** path match plan; discovery batch stays record-only (AST-775).
- §1.5.1: debug contract in **`vet_inflow_discovery_company`** gated correctly.
- **`TestAst776VetInflowDiscoveryCompany`** + **`TestAst776InflowVetEligible`** green on publish ref.

#### fix-now

1. **`tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_inflow_config_discovery_literals`** — still asserts **`INFLOW_CONFIG["discovery"]["vet_dispatch_trigger_state"]`**, but Stage 1 removed that key (trigger lives in **`INFLOW_CONFIG["vet"]`**). **`KeyError`** on publish ref. Point at **`INFLOW_CONFIG["vet"]["dispatch_trigger_state"]`** or drop redundant assertion (**`test_inflow_config_vet_literals`** already covers vet block).

2. **`src/utils/config.py`** — three-dot diff vs **`origin/dev`** deletes **`DISPATCH_SCORE_FLOOR_VALUES`** / **`dispatch_score_floor_option_labels()`** (dev-owned AST-750). Not AST-776 scope. Restore from **`origin/dev`** at **`resolve-child`** merge-clean gate.

#### Advisory

- AST-775 rollup in diff vs **`origin/dev`** is expected (sibling not on dev yet).
- **`run_company_task`** **`terminal_ok`** duplicates **`WEBSITE_FOUND`** literal alongside config pass state — harmless.

**Verdict:** Findings — **`resolve-child`** after test fix + dev merge-clean restore.

#### betty — 2026-06-24T04:58:22.664Z
## Tests Ready manifest (AST-776)

**Publish:** `origin/sub/AST-754/AST-776-vet-inflow-company-dispatch-mechanical-prompt` @ `0c0b8db` (`merge-tests(AST-776): origin/tests 17cd9b6`)

**Bible shasum (publish ref):**
- `docs/test-bible/core/roster.md` → `d0e5718a1f8427e926b63f6d2e48a45a1c6f5020a87d5f08f5e4bc54fc38b632`
- `docs/test-bible/utils/config.md` → `503a4670b0ff8fb3961117690515523e2eda58a58fa7800e8fcccb2aedd9de9e`

1. **Config — `INFLOW_CONFIG["vet"]` + schedulable company/`NEW`:** `tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_inflow_config_vet_literals`; `::test_vet_inflow_discovery_task`; `::test_vet_inflow_discovery_dispatch_admin_defaults`; `::test_vet_failed_state_and_transition`

2. **Database — vet vs resolve eligibility split:** `tests/component/data/database/test_dispatch_tasks.py::TestAst776InflowVetEligible`

3. **Roster — `vet_inflow_discovery_company` + `run_company_task` NEW routing + consult path:** `tests/component/core/test_roster.py::TestAst776VetInflowDiscoveryCompany`

4. **Regression (AST-775 record-only discovery):** `tests/component/core/test_roster.py::TestAst775InflowDiscoveryRecordNew`; `::TestAst505InflowDiscovery::test_run_batch_happy_path`; `::TestAst505InflowDiscovery::test_run_batch_cse_failure_continues`

**Narrowed run:**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_inflow_config_vet_literals \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_vet_inflow_discovery_task \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_vet_inflow_discovery_dispatch_admin_defaults \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_vet_failed_state_and_transition \
  tests/component/data/database/test_dispatch_tasks.py::TestAst776InflowVetEligible \
  tests/component/core/test_roster.py::TestAst775InflowDiscoveryRecordNew \
  tests/component/core/test_roster.py::TestAst776VetInflowDiscoveryCompany \
  tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_happy_path \
  tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_cse_failure_continues \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Obsolete (Betty):** `TestAst774VetInflowDiscoveryDispatch` removed — AST-776 routes vet to `vet_inflow_discovery_company`, not `run_inflow_discovery_batch`.

— Betty

#### hedy — 2026-06-23T21:13:45.573Z
origin/sub/AST-754/AST-776-vet-inflow-company-dispatch-mechanical-prompt @ 3ca4eb8 — Betty: update `test_vet_inflow_discovery_task` entity_type to company; add roster/database coverage per plan AC.

#### hedy — 2026-06-23T21:10:12.042Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-754/AST-776-vet-inflow-company-dispatch-mechanical-prompt/docs/features/roster/ast-776-vet-inflow-discovery-company-dispatch-and-mechanical-prompt-vet-inflow-seems-to-have-been-skipped.md

**Scope:** Single-Component — config vet dispatch wiring, database eligibility split (blurb vs resolve), roster vet_inflow_discovery_company, agent_task mechanical prompt migration.

**Conf:** Medium — NEW-state routing between vet and inflow_resolve_website is the delicate piece; AST-775 blurb contract is on ftr.

**Risk:** Medium — wrong eligibility could starve vet or double-route NEW rows; mitigated by json_extract blurb filter and dispatch_task_key gate.

---

# AST-776 — vet_inflow_discovery company dispatch and mechanical prompt

- **Linear:** [AST-776](https://linear.app/astralcareermatch/issue/AST-776/vet-inflow-discovery-company-dispatch-and-mechanical-prompt-vet-inflow-seems-to-have)
- **Parent:** [AST-754](https://linear.app/astralcareermatch/issue/AST-754/vet-inflow-seems-to-have-been-skipped)
- **Publish ref:** `origin/sub/AST-754/AST-776-vet-inflow-company-dispatch-mechanical-prompt`
- **Depends on:** [AST-775](https://linear.app/astralcareermatch/issue/AST-775) — discovery records **`NEW`** rows with **`inflow_discovery_blurb`** / **`inflow_discovery_notes`** (no inline vet).

Make **`vet_inflow_discovery`** a schedulable **company** dispatch on **`trigger_state NEW`**: read the stored discovery blurb, run through Admin **`vet_inflow_discovery`** prompts under the **company** dispatch **`batch_id`**, transition pass → **`WEBSITE_FOUND`** (with **`company_website`** set) or reject → **`VET_FAILED`**. Update the mechanical-only prompt text in a local-dev **`agent_task`** migration. Split eligibility from **`inflow_resolve_website`** so discovery-path rows vet first; legacy **`NEW`** rows without a blurb keep the Phase 2 resolve path.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | **`INFLOW_CONFIG["vet"]`**; **`TASK_CONFIG["vet_inflow_discovery"]`** → company + **`trigger_state NEW`**; add to **`DISPATCH_SCHEDULABLE_TASK_KEYS`** / **`_DISPATCH_COMPANY_ENTITY_TASK_KEYS`**; dispatch trigger helper | utils |
| `src/data/database.py` | Eligibility counters (**`count_company_new_pending_inflow_vet`**, narrow **`count_company_new_without_website`**); **`count_eligible_for_dispatch_task`** branch; **`agent_task`** prompt migration seed | data |
| `src/core/roster.py` | **`vet_inflow_discovery_company`**; **`run_company_task`** NEW routing by **`dispatch_task_key`** | core |
| `src/core/consult.py` | Optional explicit **`vet_inflow_discovery`** company branch (if batch wrapper needed) | core |

**Out of scope:** **`inflow_discovery`** candidate batch changes (**AST-775**), **`run_next`** wiring, **`inflow_resolve_website`** CSE logic, Betty tests, **`fetch_website`** / downstream chain behavior.

## Stage 1: Config — company vet dispatch wiring

**Done when:** **`dispatch_task_admin_defaults("vet_inflow_discovery")`** returns **`entity_type=company`**, **`trigger_state=NEW`**, **`batch_call_mode=0`**; bootstrap coupling accepts the key; **`TASK_CONFIG`** reflects company entity.

1. In **`INFLOW_CONFIG`**, add a **`"vet"`** block after **`"resolve"`**:

   ```python
   "vet": {
       "task_key": "vet_inflow_discovery",
       "dispatch_trigger_state": "NEW",
       "pass_state": "WEBSITE_FOUND",
       "fail_state": "VET_FAILED",
       "blurb_data_key": "inflow_discovery_blurb",
   },
   ```

2. In **`TASK_CONFIG["vet_inflow_discovery"]`**, update:
   - **`entity_type`**: **`"company"`** (replace **`"candidate"`**)
   - **`trigger_state`**: **`"NEW"`**
   - Keep **`requires_candidate_key`**: **`True`** (candidate context still required for dispatch rows and token resolution)
   - Keep **`response_schema.results`** list shape (one row per company vet) — **`action`**, optional **`website`**, optional **`hit_index`** (default **0**)

3. Add **`"vet_inflow_discovery"`** to **`DISPATCH_SCHEDULABLE_TASK_KEYS`** (after **`inflow_resolve_website`**).

4. Add **`"vet_inflow_discovery"`** to **`_DISPATCH_COMPANY_ENTITY_TASK_KEYS`**.

5. In **`_dispatch_trigger_state_for_task_key`**, before the generic **`TASK_CONFIG.trigger_state`** fallback, add:

   ```python
   if task_key == "vet_inflow_discovery":
       return INFLOW_CONFIG["vet"]["dispatch_trigger_state"]
   ```

6. Do **not** remove **`INFLOW_CONFIG["discovery"]["vet_task_key"]`** (documentation / future); discovery batch must not call it (**AST-775**).

⚠️ **Decision:** Keep **`results`** list schema so existing Admin JSON envelope docs stay valid; company vet returns exactly **one** result object with **`hit_index: 0`**.

## Stage 2: Dispatch eligibility — vet vs resolve on NEW

**Done when:** **`vet_inflow_discovery`** dispatch shows **`available_count ≥ 1`** only for unclaimed **`NEW`** companies with a non-empty **`inflow_discovery_blurb`**; **`inflow_resolve_website`** counts only **`NEW`** rows **without** a discovery blurb (legacy Phase 2 path).

1. In **`src/data/database.py`**, add **`count_company_new_pending_inflow_vet(candidate_id: str) -> int`**:
   - Same unclaimed filter as **`count_company_new_without_website`**: **`state = 'NEW'`**, matching **`candidate_id`**, **`batch_id`** null/empty, **`company_website`** null/empty trim.
   - Additionally require **`json_extract(company_data, '$.inflow_discovery_blurb')`** IS NOT NULL AND **`TRIM(...)`** ≠ **`''`**.

2. Narrow **`count_company_new_without_website`**: add to the **`WHERE`** clause:

   ```sql
   AND (
     json_extract(company_data, '$.inflow_discovery_blurb') IS NULL
     OR TRIM(json_extract(company_data, '$.inflow_discovery_blurb')) = ''
   )
   ```

   so discovery-path rows are **not** eligible for Phase 2 resolve.

3. In **`count_eligible_for_dispatch_task`**, company branch — before the **`inflow_resolve_website`** check, add:

   ```python
   if task_key == INFLOW_CONFIG["vet"]["task_key"]:
       return count_company_new_pending_inflow_vet(candidate_id)
   ```

4. Leave existing **`inflow_resolve_website`** branch calling narrowed **`count_company_new_without_website`**.

⚠️ **Decision:** Eligibility split uses **`inflow_discovery_blurb`** presence — matches **AST-775** record path; **`VET_FAILED`** rows retain **`inflow_discovery_notes`** URL so **AST-775** dedupe prevents re-recording rejected links (AC #3).

## Stage 3: Company vet execution — roster + consult routing

**Done when:** A **`vet_inflow_discovery`** dispatch run claims a **`NEW`** company, calls **`do_task(vet_inflow_discovery)`** with blurb live content under the **company** **`batch_id`**, transitions **`WEBSITE_FOUND`** or **`VET_FAILED`**, and never runs from the discovery candidate batch.

1. In **`src/core/roster.py`**, add **`async def vet_inflow_discovery_company(...)`** returning **`{success: bool, state: Optional[str], error: Optional[str]}`**:
   - Args: **`short_name`**, **`entity`**, **`batch_id`**, **`ctx`**, **`debug`** (mirror **`resolve_company_website`**).
   - Read **`blurb = (entity.get("company_data") or {}).get("inflow_discovery_blurb") or ""`**. If empty after strip, log warning and return **`{success: False, state: None, error: "missing inflow_discovery_blurb"}`** — no state transition.
   - Build **`live_content`**:

     ```
     Discovery hit (index|title|url|snippet)
     {blurb}
     ```

     (single line from **`inflow_discovery_blurb`** — already pipe-formatted by **AST-775**)

   - **`log.set_debug_flag(debug)`**; when **`debug`**, **`debug_index`** outcome **`vet vet_inflow_discovery 1 blurb`**, **`debug_detail_block(live_content)`**.
   - Call **`do_task(task_key="vet_inflow_discovery", live_content=live_content, index=short_name, ctx=ctx, debug=debug)`** — **`index`** is company slug (company dispatch entity).
   - On **`do_task`** failure: return **`success=False`**, no transition (dispatcher counts **`total_errors`**).
   - Parse **`parsed_response.results`**: take first dict row (or empty → failure).
   - **`action`** lowercased: **`ignore`** / **`reject`** → **`transition_company_state(short_name, "VET_FAILED")`**, return **`success=True, state=VET_FAILED`**.
   - **`action`** **`slug`** or **`accept`**: require non-empty **`website`** after strip → **`update_company(short_name, company_website=website)`**, **`transition_company_state(short_name, "WEBSITE_FOUND")`**, return **`success=True, state=WEBSITE_FOUND`**. If **`website`** missing on pass action, treat as task failure (no transition).
   - When **`debug`**, **`debug_index`** per outcome with **`identifier=short_name`**.

2. In **`run_company_task`**, replace the unconditional **`input_state == "NEW"` → `resolve_company_website`** branch with **`dispatch_task_key`** routing:

   ```python
   if input_state == "NEW":
       tk = (dispatch_task_key or "").strip()
       if tk == INFLOW_CONFIG["vet"]["task_key"]:
           r = await vet_inflow_discovery_company(short_name, entity, batch_id, ctx=ctx, debug=debug)
           ...
       if tk == INFLOW_CONFIG["resolve"]["task_key"]:
           r = await resolve_company_website(short_name, entity, ctx=ctx, debug=debug)
           ...
       logger.warning("run_company_task: NEW requires dispatch_task_key %r or %r", ...)
       return {**zero, "total_errors": 1}
   ```

   Map **`success`/`state`** to **`_SUMMARY_ZERO`** like existing **`resolve_company_website`** branch (**`WEBSITE_FOUND`** / **`VET_FAILED`** → **`total_passed=1`**; hard error → **`total_errors=1`**).

3. In **`src/core/consult.py`**, **no change required** if **`run_company_task`** handles **`vet_inflow_discovery`** via existing company fallback — verify dispatcher passes **`dispatch_task_key`** on company runs (it does today for **`inflow_resolve_website`**). If consult early-returns before **`run_company_task`** for unknown keys, add **`vet_inflow_discovery`** only if a code path blocks — inspect during build; default plan is **`run_company_task`** only.

4. Do **not** add **`run_next`** from discovery to vet.

### Self-review (Stage 3)

| Rule | OK? |
|------|-----|
| §2.2 do_task | Vet LLM only via **`do_task`** — Admin prompts assembled |
| §2.6 state machine | Pass **`NEW→WEBSITE_FOUND`**, reject **`NEW→VET_FAILED`** only from this function |
| §1.5.1 debug | Contract lines gated by **`debug=True`** |

## Stage 4: Mechanical prompt — local dev agent_task migration

**Done when:** Fresh or migrated local DB has **`vet_inflow_discovery`** current row with mechanical-only prompt text; idempotent re-run skips when marker present.

1. In **`src/data/database.py`**, add module constant **`_AST776_VET_INFLOW_MECHANICAL_MARKER = "MECHANICAL LINK-TYPE VET ONLY (AST-776)"`** and **`_AST776_VET_INFLOW_USER_PROMPT_SEED`** (multiline string) stating:
   - Input: one line **`index|title|url|snippet`** from discovery (**`Live content`** / TASK block).
   - Task: mechanical link-type rejection only — reject news/articles, Wikipedia, directories/listicles, BBB, job-board listings, social profiles; **do not** filter for candidate fit, industry, or company quality.
   - Output JSON envelope per product rules; **`agent_payload.results`** is a **one-element** array: **`{ "hit_index": 0, "action": "slug"|"ignore", "website": "<homepage when slug>" }`**.
   - **`action: "ignore"`** for wrong page types; **`action: "slug"`** only when the URL plausibly refers to a company site worth fetching for job listings, with **`website`** set to the best company homepage URL (may differ from the discovery hit URL).

2. Add **`_apply_ast776_vet_inflow_discovery_prompt_migration(conn)`** (pattern **`_apply_ast561_analysis_upshot_take_jd_migration`**):
   - Load current **`agent_task`** row for **`task_key = 'vet_inflow_discovery' AND current = 1`**.
   - If no row, return.
   - If **`user_prompt`** already contains **`_AST776_VET_INFLOW_MECHANICAL_MARKER`**, return (idempotent).
   - If **`user_prompt`** and **`system_prompt`** both empty/whitespace → set **`user_prompt`** to seed (with marker).
   - Else → version forward via **`_save_agent_task_on_connection`** replacing **`user_prompt`** with seed (preserve other prompt fields, **`run_next`**, existing **`agent_id`**).
   - If **`agent_id`** empty after load, copy **`agent_id`** from current **`find_company_website`** row when that row has a non-empty **`agent_id`** (local-dev convenience only).

3. Call **`_apply_ast776_vet_inflow_discovery_prompt_migration(conn)`** from **`_ensure_agent_task_schema`** alongside existing **`_apply_ast561_*`** migrations.

4. Do **not** edit **`tests/`** or ship production prompt pushes — local migration only.

⚠️ **Decision:** Prompt migration replaces legacy multi-hit candidate-batch wording; Susan can still refine prose in Manage Tasks after seed lands.

## Stage 5: Verification (build-child handoff)

**Done when:** Manual smoke path documented; grep confirms discovery batch has no vet call; company vet uses distinct task key.

1. Grep **`run_inflow_discovery_batch`** — no **`vet_inflow_discovery`** / **`do_task`** (regression guard from **AST-775**).
2. Grep **`run_company_task`** — **`NEW`** branch requires **`dispatch_task_key`**, routes **`vet_inflow_discovery`**.
3. Admin UAT (document in build review stub, not automated): for a candidate with **`inflow_discovery`** + **`vet_inflow_discovery`** Scheduled Actions rows — run discovery → confirm **`NEW`** + blurb → run vet dispatch → confirm separate **`batch_id`**, **`WEBSITE_FOUND`** or **`VET_FAILED`**, then **`fetch_website`** eligible only after **`WEBSITE_FOUND`**.

## Execution contract (developer agent)

- Execute stages **1 → 5** in order; one commit per stage on epic worktree; publish each to **`origin/sub/AST-754/AST-776-vet-inflow-company-dispatch-mechanical-prompt`**.
- Do **not** modify **`inflow_discovery`** batch logic.
- Blocking ambiguity → comment on parent **AST-754** with 🛑 format from **plan-child**.

## Self-Assessment

**Scope:** `Single-Component` — config + database eligibility/migration + roster vet path; consult change only if routing gap found in Stage 3 step 3.

**Conf:** `Medium` — NEW-state routing split between vet and resolve is the delicate part; patterns exist (**`inflow_resolve_website`**, **`prefilter_company_batch`**).

**Risk:** `Medium` — wrong eligibility split could starve vet or double-route **`NEW`** rows; mitigated by explicit **`inflow_discovery_blurb`** SQL filter and **`dispatch_task_key`** gate in **`run_company_task`**.

### Justifications

- **Scope:** Four product files, one cohesive dispatch hop — no UI or dispatcher loop rewrite.
- **Conf:** **AST-775** blurb contract is landed on **`ftr`**; this ticket wires the schedulable hop Susan expected in **AST-754**.
- **Risk:** Mis-routing affects inflow companies only; **`IMPORTED`** and job consult paths untouched.

## Self-review (ASTRAL_CODE_RULES)

| Rule | Notes |
|------|-------|
| §2.1 config | Vet pass/fail states and task key in **`INFLOW_CONFIG["vet"]`** + **`TASK_CONFIG`** |
| §2.4 batch | Company claim uses existing dispatcher **`batch_id`**; no custom claim API |
| §2.6 state machine | No daisy-chain; vet is separate dispatch invocation |
| §3.3 imports | Roster **`do_task`** only; database JSON extract for eligibility |
| §3.5 naming | **`vet_inflow_discovery_company`**, **`count_company_new_pending_inflow_vet`** |

No **`conf-!!-NONE`** conflicts identified.

## Review stub (Hedy / build)

**Publish ref:** `origin/sub/AST-754/AST-776-vet-inflow-company-dispatch-mechanical-prompt`  
**Product tip:** `4dc3a36` — `fe61510` (config) + `4152de9` (eligibility + prompt migration) + `4dc3a36` (roster vet path)

**Built:** `vet_inflow_discovery` registered as company dispatch on **NEW**; eligibility split via `inflow_discovery_blurb` (vet vs resolve); mechanical prompt seed migration; `vet_inflow_discovery_company` + `run_company_task` NEW routing by `dispatch_task_key`. Discovery batch unchanged (no inline vet).

**QA note:** `tests/component/utils/test_config.py` `test_vet_inflow_discovery_task` expects `entity_type == "candidate"` — Betty manifest update expected at Code Complete.

**Smoke (Admin UAT):** discovery → NEW + blurb → vet dispatch → separate `batch_id`, `WEBSITE_FOUND` or `VET_FAILED`; `fetch_website` only after `WEBSITE_FOUND`.

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-754/AST-776-vet-inflow-company-dispatch-mechanical-prompt` @ `60df32a`

### What's solid

| Area | Notes |
| --- | --- |
| Plan fidelity | Stages 1–4 delivered: **`INFLOW_CONFIG["vet"]`**, company/**`NEW`** **`TASK_CONFIG`** + schedulable keys; eligibility split (**`count_company_new_pending_inflow_vet`** / narrowed **`count_company_new_without_website`**); **`vet_inflow_discovery_company`** + **`run_company_task`** **`dispatch_task_key`** routing; consult no longer redirects company vet to **`run_inflow_discovery_batch`**; mechanical **`agent_task`** migration with idempotent marker. |
| §2.6 state machine | Vet transitions **`NEW→WEBSITE_FOUND`** (with **`company_website`**) or **`NEW→VET_FAILED`** only from **`vet_inflow_discovery_company`**; discovery batch record-only (AST-775 dependency) — no inline vet under discovery **`batch_id`**. |
| §1.5.1 debug | **`vet_inflow_discovery_company`** gates contract lines on **`debug=True`**; per-index headers + **`debug_detail_block`** for blurb; outcome index on pass/fail/reject. |
| §2.2 do_task | Vet LLM only via **`do_task(vet_inflow_discovery)`** with company slug as **`index`**. |
| Tests / bible | **`TestAst776VetInflowDiscoveryCompany`** and **`TestAst776InflowVetEligible`** pass on publish ref; test-bible rows updated for AST-776 manifest. |

### Issues

| Severity | Item | Location |
| --- | --- | --- |
| **fix-now** | **`test_inflow_config_discovery_literals`** asserts **`INFLOW_CONFIG["discovery"]["vet_dispatch_trigger_state"]`**, but Stage 1 moved trigger to **`INFLOW_CONFIG["vet"]`** and removed that discovery key. Test fails on publish ref (`KeyError`). Update assertion to **`INFLOW_CONFIG["vet"]["dispatch_trigger_state"]`** (or drop redundant discovery assertion — **`test_inflow_config_vet_literals`** already covers vet block). | `tests/component/utils/test_config.py` |
| **fix-now** | Three-dot diff vs **`origin/dev`** **deletes** **`DISPATCH_SCORE_FLOOR_VALUES`** and **`dispatch_score_floor_option_labels()`** from **`config.py`** — dev-owned AST-750 product not in AST-776 scope. **`merge-resume(AST-776)`** did not preserve these symbols. Restore from **`origin/dev`** at **`resolve-child`** merge-clean gate; do not ship sub rollup that strips them. | `src/utils/config.py` |

### Recommended actions

| Severity | Action |
| --- | --- |
| **fix-now** | Fix **`test_inflow_config_discovery_literals`** before **`resolve-child`** publish; re-run **`TestAst505InflowDiscoveryConfig`** (not only the narrowed AST-776 slice). |
| **fix-now** | On **`git merge origin/dev`**, restore **`DISPATCH_SCORE_FLOOR_*`** / **`dispatch_score_floor_option_labels`** if conflict resolution dropped them. |
| **Advisory** | Diff includes AST-775 discovery record-only rollup — expected vs **`origin/dev`** where sibling is not landed yet; not scope smuggle. |
| **Advisory** | **`terminal_ok`** in **`run_company_task`** lists both **`INFLOW_CONFIG["vet"]["pass_state"]`** and literal **`"WEBSITE_FOUND"`** — redundant but harmless. |

**Verdict:** Findings — two **fix-now** items; **`resolve-child`** after test + merge-clean fixes.

---

## Resolution (Hedy / resolve)

**Publish ref:** `origin/sub/AST-754/AST-776-vet-inflow-company-dispatch-mechanical-prompt` @ `97d5c43`

| Radia fix-now | Fix |
| --- | --- |
| **`DISPATCH_SCORE_FLOOR_*` stripped by merge-resume** | Restored **`DISPATCH_SCORE_FLOOR_VALUES`** and **`dispatch_score_floor_option_labels()`** from **`origin/dev`** in **`config.py`**. |
| **`test_inflow_config_discovery_literals` KeyError** | Dropped stale **`vet_dispatch_trigger_state`** discovery assertion — **`test_inflow_config_vet_literals`** covers **`INFLOW_CONFIG["vet"]`**. Betty: mirror same one-line drop on **`origin/tests`**. |

**Verification:** **`TestAst505InflowDiscoveryConfig`** + Betty AST-776 manifest (27 tests) green; §9a dry-run vs **`origin/dev`** clean; vs **`origin/ftr/AST-754-vet-inflow-discovery-split`** clean (no merge-tree **`CONFLICT`** hunks).
