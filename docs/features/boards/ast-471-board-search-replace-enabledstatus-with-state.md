# board_search: replace enabled/status with state ACTIVE|INACTIVE|ERROR

- **Linear (this ticket):** [AST-471](https://linear.app/astralcareermatch/issue/AST-471/board-search-replace-enabledstatus-with-state-activeinactiveerror-24-claim-pattern)
- **Parent (UI epic / coordination):** [AST-457](https://linear.app/astralcareermatch/issue/AST-457/manage-candidate-board-searches)
- **Program parent:** AST-379
- **Publish ref (Git — authoritative):** `origin/sub/AST-379/AST-471-board-search-replace-enabledstatus-with-state`

This ticket replaces parallel **`enabled`** (user pause) and **`status`** (batch lifecycle **`active`|`running`|`error`**) columns on **`board_search`** with a single workflow column **`state`** whose values **`ACTIVE`**, **`INACTIVE`**, and **`ERROR`** are config literals. **`batch_id`** remains the sole claim lock; **`ACTIVE`** replaces “eligible for **`gaze_board`** when unclaimed”; **`clear_board_search_batch`** clears **`batch_id`** only — success/failure update **`state`** in **`process_gaze_board_batch`**, not in clear.

⚠️ **Coordination:** [AST-457](https://linear.app/astralcareermatch/issue/AST-457/manage-candidate-board-searches) (Katherine) may touch the same screens; reconcile merge order vs **`ftr/AST-457`** / **`origin/dev`** early so **`CandidateBoardSearches.tsx`** stays conflict-free.

## Files Changed (planned)

Spike/work output belongs under **`debug/spikes/`** only (ignored); no repo **`artifacts/`**.

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add authoritative tuple/list **`BOARD_SEARCH_STATES`** **`("ACTIVE", "INACTIVE", "ERROR")`**. Optionally group under **`BOARDS_CONFIG["board_search"]`** keyed **`workflow_states`** (same literals) — single source referenced by **`boards.py`** serialization checks and **`database`** migration comments. Remove obsolete **`BOARDS_CONFIG["gaze_board"]["claim_status"]`** / **`running_status`** (no longer semantic once SQL stops writing **`running`**); keep **`batch_size`**. Document that **`ACTIVE`** aligns with **`dispatch_task.trigger_state`** for **`gaze_board`**. | utils |
| `src/data/database.py` | (**1**) Inventory docstring for **`board_search`**: **`state`** only; **`batch_id`**; no **`enabled`**, no batch **`status`**. (**2**) Migrate schema: introduce **`state TEXT NOT NULL`**, map legacy rows (**see Stage 1**), then **`DROP`** legacy **`enabled`** and **`status`** columns (SQLite table-rebuild migrations if **`DROP COLUMN`** unavailable — match existing **`dispatch_task`** rebuild style in this module). (**3**) **`save_board_search_row`** / **`update_board_search_row`**: **`state`** instead of **`enabled`**; **`INSERT`/`UPDATE`** column lists and **`?` counts** audited across all writers. (**4**) **`_parse_board_search_row`**: expose **`state`** as uppercase string normalized from DB; **`default ACTIVE`**. (**5**) **`claim_board_search_batch`**: **`SELECT`** eligible ids with **`WHERE state = 'ACTIVE'`** (bind from **`BOARD_SEARCH_STATES`** first element **`imported as constant`**, never a magic undocumented string scattered in SQL literals — **⚠️ Decision:** **`from src.utils.config import BOARD_SEARCH_STATES`** in **`database.py`** and use **`BOARD_SEARCH_ACTIVE = BOARD_SEARCH_STATES[0]`** at module tail after config import OK, or **`assert BOARD_SEARCH_ACTIVE == 'ACTIVE'`** once). **`AND (batch_id IS NULL OR batch_id = '')`** and optional **`candidate_id`** filter — **no other predicates.** **`UPDATE`** assigns **`batch_id`** + **`updated_at` only** (remove **`SET status='running'`** — mirrors **`company`**: claim sets lock column only). Docstring cites **§2.4**. (**6**) **`clear_board_search_batch`**: unchanged — clear **`batch_id`** only (**mirror **`clear_company_batch`** / **`clear_job_batch`**). (**7**) Replace **`set_board_search_status`** with **`set_board_search_state(board_search_id: str, state: str)`** that validates **`state in BOARD_SEARCH_STATES`** before **`UPDATE`**. (**8**) **`count_eligible_for_dispatch_task`** **`board_search`** branch: identical **`WHERE`** to **`claim_board_search_batch`** (**`ACTIVE`**, unclaimed **`batch_id`**, required **`candidate_id`** from **`task`** row — same projection as today's branch). (**9**) **`_DISPATCH_TASK_SEED`**: add **`gaze_board`**: **`{"entity_type": "board_search", "trigger_state": "ACTIVE", "sort_by": "updated_at", "batch_call_mode": 0}`**. (**10**) **Idempotent seed migration** after dispatch schema bootstrap: **`INSERT OR IGNORE`** (or equivalent guarded loop) **`gaze_board`** rows — for each **`candidate_id`** with a **`gaze`** **`dispatch_task`**, copy **`min_count`, `freq_hrs`, `batch_size`, `auto_mode`, `debug`, `skip_cache`, `max_runs`** from that **`gaze`** row onto the new **`gaze_board`** row; **fallback** for **`candidate_id`** appearing in **`board_search`** **without** **`gaze`**: insert with **`min_count=1`**, **`batch_size`** from **`BOARDS_CONFIG["gaze_board"]["batch_size"]`**, **`auto_mode=0`**, **`freq_hrs=0`**. **⚠️ Decision:** One-time migration only; **`UNIQUE(candidate_id, trigger_state)`** means **`OR IGNORE`** is safe idempotently. Import **`BOARDS_CONFIG`** in **`database.py`** (already imports **`config`**). | data |
| `src/core/gazer.py` | **`process_gaze_board_batch`**: remove unconditional **`set_board_search_status(..., "active")`** at row start (**that conflates batch lifecycle with user workflow**). On **`except`**, call **`set_board_search_state(sid, "ERROR")`**. On success path, **either** omit write **or** **`set_board_search_state(sid, "ACTIVE")`** (**idempotent** where row already ACTIVE). **⚠️ Decision:** Prefer **explicit **`ACTIVE`** after success so ERROR→fixed path does not rely on PATCH alone.** | core |
| `src/core/boards.py` | Replace **`enabled`** kw-only parameters on **`save_board_search`** / **`update_board_search`** / **`PATCH`** internals with **`state`** (defaults **`ACTIVE`** on create per AC “defaults to active”). **`_PATCH_UNSET`**: **`state`** instead of **`enabled`**. Preserve duplicate/deeplink/mode logic untouched. **`update_board_search`** must pass through **`database.update_board_search_row`**. Validation: **`save`** default **`ACTIVE`**; **`PATCH`** rejects client attempts to set **`ERROR`** (**`400`** from API layer catches ValueError emitted here). Allowed user transitions: **`ACTIVE`↔`INACTIVE`**; **`ERROR`→`ACTIVE`** (**resume after failure**); never **`*`→`ERROR`** from API. **`INACTIVE`** row remains saved and editable. | core |
| `src/ui/api/api_boards.py` | **`_serialize_board_search`**: emit **`state`**, **`drop `enabled`** from wire. **`POST`**: accept **`state`** optional (default ACTIVE); **`enabled`** absent — if body still sends **`enabled`**, return **`400`** with message naming **`state`** migration (**⚠️ Decision:** backward-incompatible rename per ticket AC). **`PATCH`**: **`state`** only (no **`enabled`**). Raise **`ValueError`** for **`ERROR`** from client (**map to **`400`**). | ui |
| `src/ui/frontend/src/pages/CandidateBoardSearches.tsx` | **`BoardSearchRow`**: **`state: "ACTIVE"|"INACTIVE"|"ERROR"`** (**TypeScript union** literal). Replace **`enabled` boolean** **`useState`/forms** with **`state`** (**two-option control for ACTIVE/INACTIVE** in modal; **`ERROR`** show read-only badge or disabled toggle + “Resume” (**sets ACTIVE**) per product taste — **⚠️ Decision:** Checkbox replaced by segmented control OR select: **Inactive** vs **Active**; **`ERROR`** row shows copy + **`Set active`** button that **`PATCH`** **`state:ACTIVE`**). **`POST`**/**`PATCH`** JSON uses **`state`**. | ui |
| **`tests/`**, **`docs/ASTRAL_TEST_BIBLE.md`** | **Not edited in `build-astral`** (engineer **test-tree ban**). AC8 (**tests + bible + `run_component_tests.sh`** green): at **Code Complete**, Linear comment enumerates brittle tests (**paths + expected deltas**) for Betty **`qa-astral`**. Implementer verifies **`python3 -m py_compile`** and **`npx tsc -b --noEmit`** on touched trees only.

## Stage 1: Config + `board_search` / `dispatch_task` migrations and claim/count/clear/state helpers

**Done when:** Fresh DB and upgraded DB (**with legacy **`enabled`/`status`** columns**) both **`PRAGMA table_info(board_search)`** show **`state`** and **no **`enabled`** / legacy batch **`status`**,** **`BOARD_SEARCH_STATES`** in **`config.py`**, **`claim_board_search_batch`** predicates match AC3 (**`ACTIVE`**, unclaimed **`batch_id`**, optional **`candidate_id`**), **`count_eligible`** matches **`claim`**, **`clear_board_search_batch`** still **`batch_id`-only**, **`set_board_search_state`** exists (**`set_board_search_status` deleted**).

1. In **`src/utils/config.py`**, add **`BOARD_SEARCH_STATES`** (or **`BOARDS_CONFIG["board_search"]["workflow_states"]`** per table above — **⚠️ Decision:** Prefer top-level **`BOARD_SEARCH_STATES = ("ACTIVE","INACTIVE","ERROR")`** for flat import from **`boards.py`**/`database.py` consistent with **`COMPANY_KEYS` style** clusters). Trim **`BOARDS_CONFIG["gaze_board"]`** to **`batch_size`** (and harmless keys if Susan relies on extras — grep **`BOARDS_CONFIG["gaze_board"]`** usages first; **`dispatcher.py`** uses **`batch_size`** only).

2. In **`database.py`** module header inventory (lines **`board_search`** bullet), rewrite to describe **`state`**, **`batch_id`**, **`criteria`**, **`search_mode`**, **`deeplink_url`**.

3. In **`_ensure_board_search_table`**:
   - **Fresh CREATE**: define **`board_search`** with **`state TEXT NOT NULL DEFAULT 'ACTIVE'`** and **no **`enabled`** / legacy batch **`status`**** columns**.
   - **Legacy upgrade path** (tables already on disk **`enabled`** + **`status`**): **`ALTER`** add **`state`** nullable once; **`UPDATE`** all rows **`SET state = CASE WHEN COALESCE(enabled,1) = 0 THEN 'INACTIVE' WHEN LOWER(TRIM(COALESCE(status,''))) = 'error' THEN 'ERROR' ELSE 'ACTIVE' END`**; **`ALTER`** enforce **`NOT NULL`** if needed via rebuild; **`rebuild` table** (**`CREATE board_search_next`**, copy columns **`board_search_id, candidate_id, board_key, label, criteria, state, batch_id, search_mode, deeplink_url, created_at, updated_at`**) and swap names — mirrors other rebuild migrations in **`database.py`**. **`running`/`active`** legacy **`status`** values carry **only** **`ERROR`** inference above; **`batch_id`** on disk is unchanged through migration (clear path still clears locks).

4. Replace **`save_board_search_row`** / **`update_board_search_row`** signatures to **`state`**; remove **`enabled`**.

5. Implement **`claim_board_search_batch`** as ** §AC3** + **`updated_at`** on claim only.

6. Replace **`set_board_search_status`** with **`set_board_search_state`**.

7. Update **`count_eligible_for_dispatch_task`** **`entity_type=="board_search"`** branch predicates.

8. Add **`gaze_board`** to **`_DISPATCH_TASK_SEED`** and **INSERT-migration loop** (**§ Files table** bullet 10).

9. **`python3 -m py_compile src/utils/config.py src/data/database.py`**.

## Stage 2: Core — `boards.py` + `gazer.py`

**Done when:** **`save_board_search`** / **`update_board_search`** use **`state`**, **`gazer`** success/failure mutates **`board_search.state`** correctly, **no callers reference **`enabled`**/`set_board_search_status`**.

10. **`src/core/boards.py`**: refactor **`save_board_search`** / **`update_board_search`** (**§ Files table**) — **`default state ACTIVE`** on create.

11. **`src/core/gazer.py`**: **`process_gaze_board_batch`** transitions (**§ Files table**).

12. **`rg`** (**ripgrep**) over **`src/`** for **`set_board_search_status`**, **`enabled=`** **`board_search`**, **`"enabled"`** in **`api_boards`/`boards`**; fix residual **production** refs (**tests**/Betty-owned).

13. **`python3 -m py_compile src/core/boards.py src/core/gazer.py`**.

## Stage 3: API + candidate UI (`state` wire)

**Done when:** REST accepts/returns **`state`** only (**no **`enabled`**), UI toggles **`ACTIVE`**/**`INACTIVE`**, **`ERROR`** recoverable via **`ACTIVE`**, **`npm tsc`** clean if `.tsx` changed.

14. **`api_boards.py`**: (**§ Files table**) — tighten error messages.

15. **`CandidateBoardSearches.tsx`**: (**§ Files table**) — wire **`PATCH`/`POST`**.

16. **`cd src/ui/frontend && npx tsc -b --noEmit`** if `.tsx`/`.ts` touched.

17. **`python3 -m py_compile src/ui/api/api_boards.py`**.

## Stage 4: Verification + QA handoff list (no `tests/` edits)

**Done when:** **`rg`** over **`src/`** shows **`set_board_search_status`** gone; **`enabled`**/`board_search` pairing gone from API/core layers; lingering comments cleaned. **`Code Complete`** (**build-astral**) comment lists **`tests/component/data/database/test_board_search_integration.py`**, **`tests/component/core/test_gazer.py`**, **`tests/component/core/test_dispatcher.py`**, **`tests/component/ui/api/test_api_boards.py`**, **`ASTRAL_TEST_BIBLE`** §§7.13q–7.13r wording (**`ACTIVE`/`state`**) for Betty.

18. Repo-wide **`rg`** on **`src/`**: **`enabled` + `board_search`**, **`set_board_search_status`**.

19. **Code Complete manifest** (**build-astral**): enumerate expected assertion/SQL diff per file for Betty (**no engineer edits **`tests/`**).

## Execution contract (for the developer agent)

Follow **`build-astral`** + this plan literally. Blocking ambiguity → **`🛑`** comment on **[AST-471](https://linear.app/astralcareermatch/issue/AST-471/board-search-replace-enabledstatus-with-state-activeinactiveerror-24-claim-pattern)** (this ticket) unless step explicitly requires Katherine's UI (**then @** Katherine on **AST-457** thread per team habit).

```
🛑 Stage N blocked: <one-line summary>
Step: <step number>
Issue: ...
Proposed resolutions: ...
```

## Self-Assessment

**Scope:** **MAJOR-CHANGE** — `board_search` schema + dispatcher seed + gaze core + Flask +React contract shift in one coordinated ticket (**not** ingest/deeplink/duplicate logic internals).

**Conf:** **conf-high** — **`claim`/`clear`/`count`** pattern copies **`company`/§2.4`; literals centralized in **`config.py`**.

**Risk:** **risk-HIGH** — incorrect **`WHERE`** on **`claim`/`count`** double-runs **`gaze_board`** or freezes ERROR rows wrongly; **`dispatch_task`** seed gaps (**no row**) starve BOARD searches silently.

Justification (**Scope**): Multi-layer (**data core UI**) with destructive SQLite migration qualifies as major surface area even if line count stays moderate.

Justification (**Conf**): Mirrors documented batch patterns **`ASTRAL_CODE_RULES` §§2.1 2.4** and dispatcher seeds already exercised for **`gaze`.

Justification (**Risk**): Wrong **`WHERE`** clauses or missing **`dispatch_task`** rows silently starve or double **`gaze_board`** work for adopters.


## Rules self-check (**`ASTRAL_CODE_RULES.md`**)

| Rule | Conflict? |
|------|-----------|
| §1.3 DRY | None — consolidate board_search helpers; no parallel boolean + status. |
| §2.1 config | **`BOARD_SEARCH_STATES`** lives only **`config.py`**. **`dispatch_task`** uses **`ACTIVE`** string seeded from seed dict consistent with literals. |
| §2.4 batch | **`batch_id` lock** retained; **`clear`** does not flip **`state`**; **`claim`** avoids extra columns. |
| §2.6 state machine | board_search **`state`** transitions originate in **`gazer`** + PATCH + create default (**data** applies verbatim updates only). OK. |
| §3.3 imports | **`database → config`** unchanged; **`gazer → boards/database`** lawful. **`api_boards`** unchanged layers. |
| §3.5 naming | Stored/API values **`ACTIVE`|`INACTIVE`|`ERROR`** (**uppercase literals** matching job/company style). Functions snake_case. |

No **`conf-!!-NONE`** — plan actionable for **`build-astral`**.

---

## Review stub (build agent)

Built by Hedy Lamarr.

- **Publish ref:** `origin/sub/AST-379/AST-471-board-search-replace-enabledstatus-with-state`
- **Integration line:** **`dev-hedy`** (`astral-hedy`).
- **Implementation commits:** `bc5e9679` (feat: config + `database`), `8f73cf70` (feat: `boards` + `gazer`), `ee658437` (feat: `api_boards` + `CandidateBoardSearches.tsx`).

Handoff (**build-astral §7:** no test edits in this pass): Betty **`qa-astral`** — update brittle tests patching **`set_board_search_status`** / **`enabled`** on board_search wire shape (**e.g.** `tests/component/core/test_gazer.py`, **`test_dispatcher`** expectations for **`gaze_board`** / **`WATCH`** vs **`ACTIVE`**, **`test_api_boards`**, **`test_board_search_integration`**) plus **`docs/ASTRAL_TEST_BIBLE.md`** if manifests list board_search fields.

## Review

**Radia (Tests Passed)** — three-dot **`origin/dev…origin/sub/AST-379/AST-471-board-search-replace-enabledstatus-with-state`**, reviewed tip **`f36b4e5d`** (Susan publish ref).

### What’s solid

- **§2.4 / AC3 claim parity (`database.py`):** **`claim_board_search_batch`** restricts eligibility to **`state = BOARD_SEARCH_STATES[0]`** (**`ACTIVE`** from **`config.py`**) **`AND`** **`(batch_id IS NULL OR batch_id = '')`**, **`AND`** optional **`candidate_id`** filter only — **no** extra predicates (no **`enabled`**, no batch **`status`**). **`UPDATE`** assigns **`batch_id`** + **`updated_at`** only (lock column-only claim, analogous to **`set_company_batch` / claim_job`** pattern).
- **Dispatch count parity:** **`count_eligible_for_dispatch_task`** **`board_search`** branch uses the same **`ACTIVE`** + uncleared **`batch_id`** + **`candidate_id`** predicates as **`claim`** (required **`candidate_id`** on **`dispatch_task`** row → matches scheduler path).
- **Clear parity:** **`clear_board_search_batch`** clears **`batch_id`** only (**AC4** mirror **`clear_job_batch` / `clear_company_batch`**).
- **`BOARD_SEARCH_STATES`** lives in **`config.py`** (**§2.1**); data layer binds **`ACTIVE`** from that tuple (**no** undocumented SQL literals for claim).

### Issues

_None (happy path)._ **fix-now:** 0 · **discuss:** 0 · **advisory:** 2 (below).

### Recommended actions

| Sev | Bucket | Finding |
| --- | ------ | ------- |
| advisory | Scope | **`agent.py` / `consult.py`** (large) ship with **`fix(AST-471): restore AST-469 dispatch chain with Betty parity merge`** messaging — bundles non-board_search surface with this ticket’s publish tip. **Confirm intentional** rollup for **`AST-471`** integration (no action if already agreed between Hedy/Katherine/Chuckles). |
| advisory | **G1** | **`CandidateBoardSearches.tsx`** hardcodes **`WorkflowState`** literals matching API — mirrors **`BOARD_SEARCH_STATES`**; acceptable if wire remains authoritative; escalate only if Susan wants server-driven enums on the SPA. |

**Cherry-pick:** take the **`docs(AST-471): Radia review …`** commit from branch **`radia-review-docs-471`** onto **`dev-hedy`** and republish **`origin/sub/…`** per **`orientation-astral`** branch law (**no** **`git merge radia-review`** handoffs).

**Handoff (**`review-astral`** step 6):** `origin/ftr/AST-471` at **`b4c73285544d4a8d5c2453a3c41c3a4c8cb57de9`** diverges parallel from this **`origin/sub`** tip (non-fast-forward merge). **`radia-review-docs-471`** is cut from **`f36b4e5d`** plus this doc-only commit — use **cherry-pick** of Radia **`docs(AST-471): …`** SHA; do not reset remote **`ftr/AST-471`** without coordinator approval.

## Resolution — 2026-05-23 (Hedy / `resolve-astral`)

- **Radia handoff:** Cherry-picked **`docs(AST-471): Radia review — §2.4 …`** from **`9a8a1e8f`** (`radia-review-docs-471`) onto **`dev-hedy`**; review thread recorded **fix-now: 0** / **discuss: 0** — no product or plan-text changes beyond that doc ingest.
- **Advisory findings:** Left **as reviewed** — dispatch-related commits bundled at publish tip (**AST-469** parity) coordinated with rollout; **`CandidateBoardSearches.tsx`** **`WorkflowState`** literals remain client-side mirror of server contract unless Susan escalates (**G1**).
- **Next:** **`origin/sub/AST-379/AST-471-board-search-replace-enabledstatus-with-state`** bears this Resolution commit for **`prep-uat`** (**parent AST-457**).
