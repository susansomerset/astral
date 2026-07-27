# AST-984 — Retire entity agent_responses columns

**Linear:** [AST-984 — Retire entity agent_responses columns (Decommission table AGENT_RESPONSES)](https://linear.app/astralcareermatch/issue/AST-984/retire-entity-agent-responses-columns-decommission-table-agent)

**Parent:** [AST-975 — Decommission table AGENT_RESPONSES](https://linear.app/astralcareermatch/issue/AST-975/decommission-table-agent-responses) (AC reference only)

**Publish ref:** `origin/sub/AST-975/AST-984-retire-entity-agent-responses-columns`

**Blocked by:** AST-983 (docs/bible/test table sweep). Build waits until AST-981 + AST-982 + AST-983 are ancestors of `origin/ftr/AST-975-decommission-table-agent-responses`.

Susan confirmed OQ1: drop the entity JSON columns as a separate child. This ticket removes `agent_responses` from company / job / candidate, deletes upsert/read paths, and revises Code Rules §2.4.1 + statute `astral.batch.entity-agent-responses-latest-only` (and its pattern) to the **replacement lookup** named below. Durable blocks stay in `agent_data`. Does not reintroduce the standalone `agent_responses` **table**. Does not implement AST-974 self-reference.

**Cutover order (hard rule):** Code Rules §2.4.1 + Archie-approved statute/pattern amend land **before** any commit that removes `append_agent_response` or drops entity JSON columns. Dual-write (entity JSON upsert + RESPONSE `entity_id`) stays live until that mandate cutover is published. No intermediate publishable HEAD may violate the still-live entity-column statute.

## Replacement lookup (authoritative — decide before any column drop)

**Problem today:** Latest-per-`task_key` pointers live on entity rows as JSON (`append_agent_response`). Callers that need them:

- `_hop_agent_ref_for_parent` / `_hydrate_caller_chain_context` in `src/core/agent.py` (run_next hop tokens)
- `get_entity_agent_story` in `src/core/roster.py` → job/company detail `agent_story` UI

`agent_data` today has `entity_type`, `task_key`, `batch_id` but **no `entity_id`**, so it cannot answer “latest successful run for this entity + task_key” without the entity JSON column.

**Approved replacement (this plan):**

1. Add nullable `entity_id TEXT` to `agent_data` (ensure-time migration + index `(entity_type, entity_id, task_key, created_at)`).
2. On every successful (and failure-audit) **RESPONSE** write from `do_task` when `index` is known, set `entity_id=index` via `save_agent_data`. Shared prompt blocks (SYSTEM / CACHE_* / TASK / NO_CACHE) stay **without** `entity_id` (batch-scoped, shared).
3. New data API `list_entity_latest_agent_refs(entity_type, entity_id) -> List[dict]`:
   - Select RESPONSE rows for that `entity_id` (and matching `entity_type`), order by `created_at` desc.
   - Keep one row per `task_key` (latest wins).
   - For each kept RESPONSE, build a ref shaped like today’s entity entry: `{task_key, batch_id, created_at, prompt_blocks}` where `prompt_blocks` = all non-RESPONSE blocks from `get_agent_data_by_batch(batch_id)` **plus** this RESPONSE’s `{type, id}` only (exclude sibling entities’ RESPONSE rows in the same batch).
4. After mandate cutover (Stage 2): rewrite hop hydration and `get_entity_agent_story` to use that API (load entity id from the row’s PK; do not read `entity["agent_responses"]`).
5. After mandate cutover: stop calling `append_agent_response` from agent / roster / consult; delete `append_agent_response` (data + tracker wrapper).
6. One-time ensure-time **backfill** before column drop: walk existing company/job/candidate `agent_responses` JSON; for each entry’s RESPONSE `prompt_blocks[].id`, `UPDATE agent_data SET entity_id=? WHERE agent_data_id=? AND (entity_id IS NULL OR entity_id='')`. Then drop the entity columns.
7. `entity_cost` on the old JSON refs is **not** required by `AgentStoryEntry` UI — omit from reconstructed refs (do not invent timesheet joins). Before Stage 3 reader cutover, confirm with `rg -n 'entity_cost' src --glob '*.py'` that no non-ledger consumer reads `entity_cost` off entity `agent_responses` JSON entries (dispatcher/ledger `entity_cost` columns are unrelated and stay).

**Rejected alternatives:**

- Explicitly retire latest-per-task lookup with no replacement — breaks hop chains and agent_story; parent AC 5 allows retirement only if approved; Susan asked to drop columns because they are confusing, not to delete hop/UI behavior.
- New parallel audit / refs **table** — parent forbids inventing a replacement audit table.
- Rename entity column (`agent_data_refs`) — still an entity-row JSON mirror; does not remove the confusion Susan called out.
- Depend on AST-974 self-ref — different problem; parent says adjacent, not required.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Add `agent_data.entity_id`; extend `save_agent_data`; add `list_entity_latest_agent_refs` + ensure-time backfill; remove `append_agent_response`; drop `agent_responses` from company/job/candidate CREATE + parse/update paths via table rebuild (same pattern as existing `job_next` rebuilds); strip ADD COLUMN migrations that re-add the JSON column; header inventory | data |
| `src/core/agent.py` | Pass `entity_id=index` into RESPONSE `save_agent_data` path; remove `append_agent_response` import/calls and entity-ref build that only fed the column; rewrite `_hop_agent_ref_for_parent` to use `list_entity_latest_agent_refs` | core |
| `src/core/tracker.py` | Remove `append_agent_response` wrapper | core |
| `src/core/roster.py` | Remove batch `append_agent_response` calls; rewrite `get_entity_agent_story` to use `list_entity_latest_agent_refs`; delete or stop exporting `dedupe_agent_responses_latest` / `normalize_agent_responses_for_backfill` if nothing else needs them after column drop | core |
| `src/core/consult.py` | Remove per-job `append_agent_response` calls after shared batch | core |
| `src/ui/api/api_jobs.py` | Docstring only if it still says “agent_responses attached” → “agent_story” | ui |
| `src/utils/config.py` | ENTITY_TYPES comment: remove entity-column `agent_responses` **in the same commit as** the Code Rules §2.4.1 rewrite (Stage 2) | utils |
| `docs/ASTRAL_CODE_RULES.md` | Rewrite §2.4.1 + batch bullets to the agent_data `entity_id` latest-RESPONSE contract **before** removing entity upserts / dropping columns | docs |
| `canon/statutes/astral/batch/astral.batch.entity-agent-responses-latest-only.md` | Draft amend → Archie/Susan approval → commit only with refreshed `approved_by: Archie` + `approved_at` (keep id unless Archie directs supersede) | docs |
| `canon/patterns/batch/pattern.batch.entity-agent-responses.md` | Update problem/solution + `canonical_refs` in the same Archie-gated canon commit as the statute | docs |
| `scripts/migrations/backfill_latest_only_rubric_entity_data.py` | Retire: CLI exits with AST-984 retired message (no entity-column writes) | scripts |

**Out of scope:**

| Item | Owner |
|------|--------|
| Standalone `agent_responses` **table** drop / ensure removal | AST-982 (must already be gone on ftr before build) |
| Table-only docs/bible/test sweep | AST-983 |
| AST-974 `agent_data` self-reference / dedupe | separate epic |
| Engineer commits under `tests/` / `docs/test-bible/**` | Betty qa-child |

**Betty note:** Expect broad test fallout (`test_agent.py` append mocks, roster story/dedupe tests, database append tests, backfill script tests). Engineer does not edit those trees.

## Stage 0: Merge gate (before any product edit)

**Done when:** `origin/ftr/AST-975-decommission-table-agent-responses` contains AST-981 + AST-982 + AST-983 tips (standalone table gone; mandate already distinguishes retired table). Working tree has merged `origin/dev` and that ftr tip; `BEHIND=0` vs `origin/dev`.

1. `git fetch origin && git merge origin/dev && git merge origin/ftr/AST-975-decommission-table-agent-responses`.
2. Confirm by search that standalone-table I/O / ensure from AST-981/982 is already absent on HEAD (no `add_agent_response_entry`, no `_ensure_agent_responses_schema` CREATE path). If still present, **stop** and comment on AST-984 — do not dual-write or drop entity columns while the table path is live.
3. Confirm Linear `blockedBy` AST-983 is Done / rolled into ftr. If not, **stop** (do not start Stage 1).

## Stage 1: agent_data.entity_id + list API + RESPONSE tagging (dual-write)

**Done when:** New DBs and upgraded DBs have `agent_data.entity_id`; `save_agent_data` accepts optional `entity_id`; RESPONSE writes from `do_task` set it when `index` is set; `list_entity_latest_agent_refs` returns latest-per-task_key refs with prompt_blocks as specified; entity JSON columns still exist and `append_agent_response` **still runs** (dual-write). Dual-write must remain until Stage 2 mandate is published.

1. In `src/data/database.py` `_ensure_agent_data_schema`: on CREATE include `entity_id TEXT`; on existing tables `ALTER TABLE agent_data ADD COLUMN entity_id TEXT` if missing; create index `idx_agent_data_entity_task` on `(entity_type, entity_id, task_key, created_at)` if missing.
2. Extend `save_agent_data(..., entity_id: Optional[str] = None)` to INSERT the column (NULL when omitted).
3. Add `list_entity_latest_agent_refs(entity_type: str, entity_id: str) -> List[Dict[str, Any]]` implementing the replacement algorithm in the header (RESPONSE-only index; attach batch non-RESPONSE blocks + this RESPONSE).
4. In `src/core/agent.py` `_store_response_block`, pass `entity_id=index` into `save_agent_data` when `index` is truthy. Do not set `entity_id` on `_store_prompt_blocks` saves.
5. Leave `append_agent_response` call sites in place (still dual-writing). Do **not** rewrite hop/story readers yet; do **not** delete upserts; do **not** drop columns.

⚠️ **Decision:** Dual-write until mandate cutover (Stage 2) so no publishable HEAD removes entity upserts while statute `astral.batch.entity-agent-responses-latest-only` still requires them.

## Stage 2: Mandate + Archie-gated statute/pattern (before any upsert removal)

**Done when:** `docs/ASTRAL_CODE_RULES.md` §2.4.1 and related bullets describe the `entity_id` / `list_entity_latest_agent_refs` contract (not entity JSON upserts); config ENTITY_TYPES comment matches; canon statute + pattern are committed only after Archie approval with refreshed frontmatter; dual-write code from Stage 1 is still present on HEAD.

1. Draft (worktree only, may be uncommitted or on a local WIP commit that is **not** pushed as the sole tip if it includes statute without approval — prefer keep statute/pattern edits unstaged until step 4): rewrite `docs/ASTRAL_CODE_RULES.md` §2.4.1 to document RESPONSE `entity_id` + `list_entity_latest_agent_refs` as the latest-per-task contract; update §2.4 batch bullets that say “entity agent_responses”; update ENTITY_TYPES / External-layer mentions so they do not list entity-column `agent_responses` as the live upsert target. Keep the statute id citation line.
2. Update `src/utils/config.py` ENTITY_TYPES comment in the **same** product/docs commit as the Code Rules rewrite (comment-only).
3. **Archie approval gate (`orch.roles.archie-approves-statutes`) — hard stop:**
   1. Prepare the intended amend text for `canon/statutes/astral/batch/astral.batch.entity-agent-responses-latest-only.md` (Statement / Examples / title as needed for the replacement contract) and the matching `canon/patterns/batch/pattern.batch.entity-agent-responses.md` (`canonical_refs` → `list_entity_latest_agent_refs` / `_store_response_block` or `save_agent_data`; drop deleted symbols).
   2. Post a Linear comment on **AST-984** assigning **Susan** (Archie) with the draft statute/pattern delta and asking for approval. Explicit ask: keep statute id in place vs supersede with a new id.
   3. **Stop.** Do not commit `canon/statutes/**` (or proceed to Stage 3) until Susan/Archie comments approval on AST-984.
   4. On approval: commit statute + pattern with frontmatter `approved_by: Archie` and a fresh `approved_at` (ISO date of approval). If Archie directs supersede, create the new statute file, set `superseded_by` / `supersedes` links, update Code Rules statute citation, and do **not** leave the old statute active without that linkage.
4. Publish Stage 2 commit(s) to `origin/<publish-ref>`: Code Rules + config comment may land in one commit; canon files only in the post-approval commit. After this stage, the **live mandate** matches the replacement; dual-write code may still exist until Stage 3.

⚠️ **Decision:** In-place statute id rewrite vs supersede is **Archie’s call at this gate** (Joan discuss item). Default draft keeps the same id; implementer follows Archie’s reply literally.

## Stage 3: Cut readers/writers to replacement; stop entity JSON upserts

**Done when:** No core path calls `append_agent_response`; hop hydration and `get_entity_agent_story` use only `list_entity_latest_agent_refs`; `append_agent_response` deleted from data + tracker. Stage 2 mandate is already on `origin/<publish-ref>`.

**Precondition:** Stage 2 published (Code Rules rewritten; Archie-approved statute/pattern on publish-ref). If not, **stop**.

1. Confirm `entity_cost` omission: `rg -n 'entity_cost' src --glob '*.py'` — no reader of entity JSON `agent_responses[].entity_cost` outside the soon-deleted append path; ledger/dispatcher `entity_cost` columns unchanged.
2. Run ensure-time backfill function `_backfill_agent_data_entity_id_from_entity_columns(conn)` once per process (flag like other one-shot migrations): for company/job/candidate rows, parse JSON `agent_responses`, for each RESPONSE block id set `agent_data.entity_id` when empty. Invoke from **agent_data ensure** so it runs before readers rely on it.
3. Rewrite `_hop_agent_ref_for_parent` to iterate `list_entity_latest_agent_refs(entity_type, entity_id)` (pass entity type + id into the helper; stop reading `entity.get("agent_responses")`). Preserve anchor_batch_id filter and failure-prefix skip behavior.
4. Rewrite `get_entity_agent_story(entity)` to take entity type from `astral_job_id` / `short_name` / `astral_candidate_id` presence (same detection as today) and call `list_entity_latest_agent_refs`; keep scored-task RESPONSE filtering via `_filter_response_block`.
5. Delete `append_agent_response` calls in `agent.py`, `roster.py`, `consult.py`; remove imports; delete `database.append_agent_response` and `tracker.append_agent_response`.
6. Delete `dedupe_agent_responses_latest` and `normalize_agent_responses_for_backfill` from `roster.py` if unused after the rewrite; if the backfill script still imports them, retire the script in Stage 5 in the same or prior commit so imports do not break.

## Stage 4: Drop entity columns from schema

**Done when:** `PRAGMA table_info` for company, job, and candidate has no `agent_responses`; CREATE paths never add it; parse/update helpers never read/write it; header inventory no longer lists the column.

**Precondition:** Stage 2 mandate + Stage 3 reader/writer cutover are on `origin/<publish-ref>`. If not, **stop** (parent forbids silent column drop while mandate still requires entity latest-only refs — Stage 2 already moved the mandate; Stage 3 removed the last writers).

1. For each of company / job / candidate ensure paths: if column present, rebuild table excluding `agent_responses` (follow existing `job_next` / `dispatch_task_new` rebuild pattern in `database.py` — copy all columns except `agent_responses`, swap tables, restore indexes that still apply). Do **not** use this rebuild to drop unrelated columns (e.g. leave `agent_responses_legacy` on company alone unless a prior sibling already removed it — out of scope).
2. Remove `agent_responses` from CREATE TABLE column lists, ADD COLUMN migration loops, row parsers (`_parse_*`), `create_*` / `update_*` kwargs / INSERT column lists.
3. Update module header inventory bullets accordingly.
4. Verify with `rg -n "agent_responses" src/data/database.py` — remaining hits must be only historical comments about the retired **table** (if any left after AST-982) or none; zero entity-column SQL.

## Stage 5: Scripts + acceptance

**Done when:** Entity-column backfill script is retired; api docstring fixed if needed; searches below are clean for product/scripts.

1. Retire `scripts/migrations/backfill_latest_only_rubric_entity_data.py` (CLI exits with AST-984 retired message; no entity-column UPDATEs).
2. Fix `api_jobs.py` detail docstring if it still says agent_responses attached.
3. Acceptance searches:

```bash
rg -n "append_agent_response|dedupe_agent_responses_latest|normalize_agent_responses_for_backfill" src scripts --glob '*.py'
rg -n "agent_responses" src/data/database.py src/core src/ui/api src/utils/config.py --glob '*.py'
```

Expected: no append/dedupe/normalize symbols; no entity-column read/write in those trees (UI `agent_story` keys OK; frontend types unchanged). Canon + Code Rules describe the replacement only.

## Self-Assessment

**Scope:** MAJOR-CHANGE — `agent_data` schema + write path, hop/UI story readers, entity DDL drop on three tables, Code Rules + Archie-gated canon statute/pattern, script retirement.

**Conf:** Medium — replacement is concrete and fits parent “no new audit table” boundary; Stage 2 now hard-gates Archie on statute id vs supersede; historical RESPONSE rows without backfillable block ids will lack hop/story until re-run.

**Risk:** HIGH — wrong cutover breaks run_next hop token hydration and job/company agent_story; mitigated by Stage 1 dual-write held through Stage 2 mandate, ensure-time backfill before drop, and preserving failure-prefix / anchor_batch_id behavior.

## Code Rules check

- §2.4.1 / statute: this ticket **revises** them in **Stage 2 before** removing upserts or dropping columns (parent boundary + `astral.batch.entity-agent-responses-latest-only` / `orch.roles.archie-approves-statutes`).
- §2.4 batch / agent_data: durable blocks unchanged; only adds `entity_id` for lookup (parent allows “whatever the replacement lookup needs”).
- §1.3 DRY: one list API for hop + story; do not keep parallel JSON upsert after Stage 3.
- §3.3 imports: remove dead `append_agent_response` imports with call sites in Stage 3.
- Layers: data owns schema/API; core owns hop/story; ui docstring only; no external-layer persistence.
- AST-974: not implemented here (no self-ref key).

## Revisions

### Revision 1 — 2026-07-25

Driven by: Joan `[plan-discuss] round=1 concern` fix-now (1) Stages 2→3→4 order violated live statute / parent “no silent drop while mandate still requires columns”; (2) Stage 4 amended `canon/statutes/**` without Archie approval / `approved_at` refresh (`orch.roles.archie-approves-statutes`).

Changes:

- Reordered cutover: Stage 1 dual-write plumbing → **Stage 2 mandate + Archie-gated statute/pattern** → Stage 3 remove upserts/cut readers → Stage 4 drop columns → Stage 5 scripts/acceptance.
- Added hard rule at top: no publishable HEAD may remove entity upserts or drop columns before mandate cutover.
- Added explicit Archie gate: draft → assign Susan → stop → commit statute/pattern only with refreshed `approved_by` / `approved_at` (id vs supersede = Archie).
- Added `entity_cost` non-UI consumer check before reader cutover (Joan discuss).
- Updated Self-Assessment / Code Rules check to match the new stage order.

## Review (build stub)

**Built:** `origin/sub/AST-975/AST-984-retire-entity-agent-responses-columns` @ `03c5361`.

**Stages delivered:**
- Stage 1: `agent_data.entity_id` + `list_entity_latest_agent_refs` + RESPONSE tagging (dual-write) — `29cc49b`.
- Stage 2: Code Rules §2.4.1 + ENTITY_TYPES; Archie-waived statute/pattern amend (`approved_at: 2026-07-27`) — `ff7f9f7` / `3745d22`.
- Stage 3–5: hop/story → list API; batch entity_id tagging; drop entity JSON columns; retire backfill script — `03c5361`.

**Betty:** broad fallout expected — `test_agent.py` append mocks, roster story/dedupe, database append tests, backfill script tests; cover `list_entity_latest_agent_refs` / `entity_id`.

