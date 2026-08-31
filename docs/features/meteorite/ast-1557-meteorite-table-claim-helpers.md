# AST-1557 — meteorite table + claim helpers

**Linear:** [AST-1557](https://linear.app/astralcareermatch/issue/AST-1557/meteorite-table-claim-helpers)  
**Parent:** [AST-1555](https://linear.app/astralcareermatch/issue/AST-1555/meteorite-ingress-staging-table-inboxmeteorite-consolidation) — Meteorite ingress: staging table + inbox/meteorite consolidation  
**Publish ref:** `sub/AST-1555/AST-1557-meteorite-table-claim-helpers`

Add the flat `meteorite` staging table, its config state registry (`prior_states` / transition literals), and data-layer claim / insert / update / retention helpers so later children can fan-out classify results, claim one transition at a time, and purge/list stale rows without inventing schema or hardcoded state sets. No inbox verbs, classify runner, Estelle, Manage Email, monitoring format, or dispatch seed/task-key retirements.

## Scope gate

Ticket **## Scope** (verbatim):

`src/data/database.py` (new table + claim/insert/update/retention helpers + header inventory); `src/utils/config.py` (meteorite state registry / transition literals only — not monitoring format or task-key retirements owned by later children)

All Files Changed / Stages stay inside that set.

**Out of scope (siblings):**

- Inbox candidate verbs / Manage Email / `FETCH_EMAIL_CONFIG` / `INBOX_BIND_CONFIG` / `fetch_email` seeds — **AST-1558**
- `check_inbox` + monitoring log format / mailbox task repoint — **AST-1559**
- stage / scrape / land transition runners in `meteorite.py` — **AST-1560**
- BOT_BLOCKED Estelle notify / `apply_paste` — **AST-1561**
- Retention **runner** wiring + delete `meteorite_email.py` — **AST-1562** (this ticket owns select/delete **helpers** only)

**AC partition (this ticket):** Supplies the durable spine for parent AC1 (N `meteorite` rows on successful classify fan-out; zero rows when classify fails — callers in later children). Does **not** implement archive, classify, or Gmail.

**Depends on:** none (Bang !! — first child).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `METEORITE_STATES` registry + retention state-partition literals + header bullet; asserts lockstep | utils |
| `src/data/database.py` | Header inventory + `_ensure_meteorite_schema` + claim/get/clear + insert fan-out + get/update/list-by-state + retention select/delete helpers | data |

## Stage 1: Config — `METEORITE_STATES` registry

**Done when:** `METEORITE_STATES` is importable from `src.utils.config` with exactly the seven staging keys below, each carrying `prior_states`; retention partition tuples name only those keys; `python3 -m py_compile src/utils/config.py` succeeds (repo venv if needed: `~/astral/.venv/bin/python`). No `database.py` changes yet.

1. In `src/utils/config.py` module header inventory (near other `METEORITE_*` bullets), add a bullet:

   - `METEORITE_STATES` — staging-row state registry for the `meteorite` table (`prior_states` per state); distinct from `JOB_STATES` keys like `METEORITE_NEW` (AST-1557).

2. Immediately **after** the existing `METEORITE_CONFIG` assert block (the block that ends with `assert "METEORITE_NEW" in JOB_STATES["BOT_BLOCKED"]["prior_states"]`) and **before** `SURFER_PACING_CONFIG`, insert:

```python
# AST-1557: flat meteorite staging-row states (table spine). Keys are NOT JOB_STATES
# METEORITE_* job lifecycle labels — core transitions decide targets; data accepts state as param.
METEORITE_STATES = {
    "NEW": {
        "prior_states": None,  # insert-only entry from classify fan-out
    },
    "SCRAPE_LINK": {
        "prior_states": ["NEW", "ERROR"],  # link outcomes; retry from ERROR
    },
    "READY": {
        # text fan-out from NEW; scrape success; Estelle paste recovery (sibling)
        "prior_states": ["NEW", "SCRAPE_LINK", "BOT_BLOCKED"],
    },
    "BOT_BLOCKED": {
        "prior_states": ["SCRAPE_LINK"],
    },
    "ERROR": {
        "prior_states": ["SCRAPE_LINK"],  # retry-holding after Playwright / scrape miss
    },
    "LANDED": {
        "prior_states": ["READY"],
    },
    "ABANDONED": {
        "prior_states": ["BOT_BLOCKED", "ERROR"],  # nag limit / terminal stale
    },
}

# Retention partitions (state literals only — day cutoffs are caller/config for AST-1562).
METEORITE_STATES_RETENTION = {
    "purge_states": ("LANDED",),
    "stale_list_states": ("ERROR", "BOT_BLOCKED", "ABANDONED"),
}
```

⚠️ **Decision:** Registry name is `METEORITE_STATES` (entity-parallel to `JOB_STATES` / `CANDIDATE_STATES`). Keys stay short (`NEW`, `READY`, …) per parent functional scope — they collide as **strings** with some `JOB_STATES` keys (`NEW`, `BOT_BLOCKED`) but live in a separate dict; callers must import `METEORITE_STATES`, never reuse `JOB_STATES` for staging rows. No `SKIPPED` state (parent: no-job outcomes leave zero rows; audit is the monitoring log in AST-1559).

3. Immediately after those dicts, add asserts:

- `set(METEORITE_STATES) == {"NEW", "SCRAPE_LINK", "READY", "BOT_BLOCKED", "ERROR", "LANDED", "ABANDONED"}`
- every value has key `"prior_states"`
- `METEORITE_STATES["NEW"]["prior_states"] is None`
- `set(METEORITE_STATES_RETENTION["purge_states"]) | set(METEORITE_STATES_RETENTION["stale_list_states"])` ⊆ `set(METEORITE_STATES)`
- `set(METEORITE_STATES_RETENTION["purge_states"]).isdisjoint(METEORITE_STATES_RETENTION["stale_list_states"])`
- for every state `s` with non-`None` `prior_states`, every prior ∈ `METEORITE_STATES`

4. Do **not** add monitoring format strings, subject sanitize limits, scrape/land/notify/retention **task_key** literals, or retire `FETCH_EMAIL_CONFIG` / `INBOX_BIND_CONFIG` in this stage (sibling Scope).

## Stage 2: `meteorite` table + claim / insert / update / get helpers

**Done when:** Header inventory lists `meteorite`; `_ensure_meteorite_schema` creates the table idempotently; `claim_meteorite_batch` / `get_meteorite_batch` / `clear_meteorite_batch` match the batch-id-first claim pattern; `insert_meteorite_rows` can insert N rows in one transaction at state `NEW`; `get_meteorite` / `list_meteorites_by_state` / `update_meteorite` exist and accept caller-supplied `state` without choosing the next state; `python3 -m py_compile src/data/database.py` succeeds.

1. In `src/data/database.py` module docstring **Tables used (inventory)**, add a bullet (keep alphabetical-ish peer placement near other entity tables — after `job` / before or after `candidate` is fine if the list is not strictly sorted; match existing style):

   - `meteorite` — Ingress staging spine (AST-1557): one row per prospective job after classify fan-out; `state` from `METEORITE_STATES`; claim via `batch_id` / `batch_created_at`; columns id, candidate_id, source_kind, source_id, source_ref, state, content, classify_outcome, link, astral_job_id, estelle_thread_ts, estelle_notified_at, nag_count, error, batch_id, batch_created_at, created_at, updated_at, state_changed_at.

2. Near other `_foo_schema_ensured` flags at module top, add `_meteorite_schema_ensured = False`.

3. Implement `_ensure_meteorite_schema(conn)` (idempotent, same shape as `_ensure_company_job_scan_schema`):

   - `CREATE TABLE IF NOT EXISTS meteorite` with columns:

     | Column | Type | Notes |
     |--------|------|-------|
     | `id` | `INTEGER PRIMARY KEY AUTOINCREMENT` | writers omit id |
     | `candidate_id` | `TEXT NOT NULL` | |
     | `source_kind` | `TEXT NOT NULL` | email / slack / paste (callers; no hardcoded set in SQL) |
     | `source_id` | `TEXT NOT NULL` | e.g. Gmail mid |
     | `source_ref` | `TEXT` | nullable provenance handle |
     | `state` | `TEXT NOT NULL` | must be a `METEORITE_STATES` key at write time (enforced by callers / update helper validation against config keys only — **not** prior_states) |
     | `content` | `TEXT` | JD / visible text payload |
     | `classify_outcome` | `TEXT` | stage_meteorite outcome literal |
     | `link` | `TEXT` | scrape URL when link outcome |
     | `astral_job_id` | `TEXT` | set on LANDED (1:1) |
     | `estelle_thread_ts` | `TEXT` | sibling Estelle |
     | `estelle_notified_at` | `TIMESTAMP` | |
     | `nag_count` | `INTEGER NOT NULL DEFAULT 0` | |
     | `error` | `TEXT` | last error message |
     | `batch_id` | `TEXT` | null/empty = unclaimed |
     | `batch_created_at` | `TIMESTAMP` | |
     | `created_at` | `TIMESTAMP NOT NULL` | |
     | `updated_at` | `TIMESTAMP NOT NULL` | |
     | `state_changed_at` | `TIMESTAMP NOT NULL` | |

   - Index: `CREATE INDEX IF NOT EXISTS idx_meteorite_state_batch ON meteorite(state, batch_id)`
   - Index: `CREATE INDEX IF NOT EXISTS idx_meteorite_source ON meteorite(source_kind, source_id)`
   - Set `_meteorite_schema_ensured = True` after ensure.
   - Do **not** register `meteorite` in `_UPSERT_LAZY_SCHEMA_HANDLERS` / `_UPSERT_SCHEMA_ENSURE_FLAGS` unless an existing upsert path already requires it — this table is claim/insert/update, not admin upsert. ⚠️ **Decision:** skip upsert registry; lazy ensure is called from meteorite helpers only (same pattern as tables that are helper-gated rather than startup-upserted). If `ensure_all_upsert_registry_schemas_at_startup` is later required for empty-DB create, that is a sibling/follow-up — do not invent it here.

4. Add row helper `_meteorite_row_to_dict(row) -> dict` (plain `_row_to_dict` is enough if no JSON columns).

5. Implement claim trio (signatures mirror `claim_candidate_batch` / `get_candidate_batch` / `clear_candidate_batch`; batch_id **first**):

   - `claim_meteorite_batch(batch_id: str, state: str, limit: int, *, states: Optional[List[str]] = None) -> int`  
     Claim unclaimed rows (`batch_id IS NULL OR batch_id = ''`) in `state` or `states`; set `batch_id`, `batch_created_at`; `ORDER BY rowid`; `LIMIT ?`; return count. Call `_ensure_meteorite_schema`. Use `_state_in_sql` like jobs/candidates.
   - `get_meteorite_batch(batch_id: str) -> List[Dict[str, Any]]`  
     `SELECT * FROM meteorite WHERE batch_id = ?`.
   - `clear_meteorite_batch(batch_id: str) -> int`  
     Null out `batch_id` and `batch_created_at` for that batch; return count.

6. Implement insert fan-out:

   - `insert_meteorite_rows(rows: List[Dict[str, Any]]) -> List[int]`  
     Insert each dict in **one** transaction. Required keys per row: `candidate_id`, `source_kind`, `source_id`. Optional: `source_ref`, `content`, `classify_outcome`, `link`, `error`.  
     Force `state` to `"NEW"` on insert (ignore any caller-supplied state) so classify fan-out cannot invent entry states.  
     Set `nag_count=0`, timestamps (`created_at` / `updated_at` / `state_changed_at`) via `_utc_now()`, leave claim columns null, leave `astral_job_id` / Estelle fields null.  
     Return list of new integer `id`s in insert order (`cursor.lastrowid` per row).  
     Empty `rows` → return `[]` with no write.

7. Implement read/update:

   - `get_meteorite(meteorite_id: int) -> Optional[Dict[str, Any]]`
   - `list_meteorites_by_state(state: str, *, limit: Optional[int] = None) -> List[Dict[str, Any]]` — unfiltered by batch; optional LIMIT.
   - `list_meteorites_by_source(source_kind: str, source_id: str) -> List[Dict[str, Any]]` — for sibling source-ref dedup on re-fetch.
   - `update_meteorite(meteorite_id: int, **fields) -> None`  
     Allowed field names (whitelist): `state`, `content`, `classify_outcome`, `link`, `astral_job_id`, `estelle_thread_ts`, `estelle_notified_at`, `nag_count`, `error`, `source_ref`.  
     Always bump `updated_at`. When `state` is present: require `state in METEORITE_STATES` (import from config); set `state_changed_at` to now; **do not** enforce `prior_states` here (core decides — `astral.state.core-decides-transitions`).  
     Raise `ValueError` on unknown kwargs or unknown state string. No-op kwargs-only empty → still allowed but must not clear required columns.

8. Wire every new public helper through `_run_with_retry` like peer claim/update functions. On failure use `_log_db_failure` before re-raise where peers do.

## Stage 3: Retention select / delete helpers

**Done when:** Callers can list purge candidates and stale-list rows by state set + cutoff timestamp, and delete by id list, without embedding day numbers or state sets in SQL string literals outside parameters; `python3 -m py_compile src/data/database.py src/utils/config.py` succeeds.

1. In `src/data/database.py`, add:

   - `list_meteorites_for_retention(*, states: List[str], older_than: str, limit: Optional[int] = None) -> List[Dict[str, Any]]`  
     Select rows where `state` ∈ `states` AND `state_changed_at < older_than` (ISO/UTC string comparable to stored timestamps). Order by `state_changed_at ASC`. Optional LIMIT.  
     Caller (AST-1562) passes `list(METEORITE_STATES_RETENTION["purge_states"])` or `stale_list_states` and a cutoff computed from config days — **this ticket does not hardcode day counts**.

   - `delete_meteorites_by_ids(ids: List[int]) -> int`  
     Delete rows with `id IN (…)`; return rowcount. Empty list → 0, no execute. Use parameterized placeholders only.

⚠️ **Decision:** Retention day thresholds stay out of `config.py` on this ticket (Scope: state registry / transition literals only). `METEORITE_STATES_RETENTION` holds **which states** purge vs list; AST-1562 adds day literals + runner that calls these helpers.

2. Do not add a dispatcher scheduled-query seed, retention task_key, or core runner in this ticket.

3. Compile both touched modules; fix only syntax/import issues introduced by this plan — no drive-by cleanup.

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the plan.
- When a step is ambiguous, contradicts another step, references something that does not exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.**
- Completes each stage on the epic worktree, commits, and publishes to `origin/sub/AST-1555/AST-1557-meteorite-table-claim-helpers` per build-child.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1557
**Overall:** APPROVED
**Publish ref:** `sub/AST-1555/AST-1557-meteorite-table-claim-helpers` @ `9e49433068aba301e42fe41160806c4331f7f44c`

## Traceability
AC1 → Stages 2–3 (`insert_meteorite_rows` N-row fan-out + schema/claim/update/retention helpers); archive/classify/Gmail mid behavior and classify-failure zero-row contract owned by AST-1559 callers on this spine.

## Findings

### acceptable
- **Location:** Stage 1 — `METEORITE_STATES` keys vs `JOB_STATES`
- **Finding:** Short state strings (`NEW`, `BOT_BLOCKED`) collide across registries; plan documents separate-dict import discipline.
- **Recommendation:** Keep the Decision callout; sibling core children must import `METEORITE_STATES` explicitly when touching staging rows.

### acceptable
- **Location:** Stage 2 — `list_meteorites_by_source`
- **Finding:** Helper not named in parent technical-scope bullet but supports parent source-ref dedup and stays inside ticket `## Scope` (`database.py`).
- **Recommendation:** No change — reasonable data-layer affordance for AST-1559.

**In-session statute pass:** Universal orch.* statutes — conforms or N/A (orchestration). Scoped considered (data/utils layers): `astral.standards.database-header-inventory`, `astral.standards.no-hardcoded-sets`, `astral.config.config-source-of-truth`, `astral.state.core-decides-transitions`, `astral.batch.claim-process-release`, `astral.batch.batch-id-first`, `astral.batch.batch-id-format`, `astral.standards.in-scope-only`, `astral.standards.data-raises-caller-logs`, `astral.standards.dry-and-focused-functions`, `astral.layers.import-direction` — all **conforms**. Cited patterns `pattern.state.entity-state-transitions` and `pattern.batch.entity-claim-process-release` match plan shape (config registry + data claim trio, core-owned transitions, no `prior_states` enforcement in data). Remaining scoped statutes excluded by layer/path/change-type predicates.

context_tokens≈42000

## Review

- **Publish tip:** `7ae8111a90cc75c499aaf3126094d8de2aa87849` on `sub/AST-1555/AST-1557-meteorite-table-claim-helpers`
- **Built:** METEORITE_STATES + meteorite table claim/insert/update + retention helpers

## Radia review

# Radia review — AST-1557

`[code-rubric] revision=2`  
**Rubric:** code-rubric.v2  
**Ticket:** AST-1557  
**Publish ref:** `sub/AST-1555/AST-1557-meteorite-table-claim-helpers` @ `a83b8dd517351a6dfe245a4d3abe7d12b9966be7`  
**Overall:** DISCUSS  
**Internal grade:** DISCUSS (product clean; branch hygiene question)

**Baseline:** `git diff origin/dev...origin/sub/AST-1555/AST-1557-meteorite-table-claim-helpers`  
**Status gate:** Tests Passed (spawn prompt — trusted)

---

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no agent/LLM paths in diff |
| astral.agent.do-task-delegation | scoped | not-applicable | no do_task changes |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade-vector paths |
| astral.batch.batch-id-first | scoped | conforms | `claim_meteorite_batch(batch_id, …)` batch_id first; get/clear peers |
| astral.batch.batch-id-format | scoped | conforms | string batch_id; no format violation |
| astral.batch.claim-process-release | scoped | conforms | claim/get/clear trio; unclaimed filter; clear nulls batch columns |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no agent_responses |
| astral.config.config-source-of-truth | scoped | conforms | `METEORITE_STATES` / retention partitions in config with asserts |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no secrets/env |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug artifacts |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no spikes |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch seeds |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no run_next |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single `ast-1557-*.md` plan doc |
| astral.git.betty-no-src-or-features | scoped | not-applicable | Radia scope; Betty test commits expected |
| astral.git.engineer-test-tree-ban | scoped | not-applicable | engineer `src/` only; tests via Betty/test-child |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | data/utils only |
| astral.layers.import-direction | scoped | conforms | `database.py` imports `METEORITE_STATES` from config only |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | no UI |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no consult/render |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | no routes |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed JSON |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no seed catalog edits |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no boot seed |
| astral.seed.define-approved | scoped | not-applicable | child implement, not define |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no seed rows |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no coverage join |
| astral.standards.data-raises-caller-logs | scoped | conforms | `ValueError` on bad fields/state; no data-layer logging |
| astral.standards.database-header-inventory | scoped | conforms | `meteorite` bullet added to module inventory |
| astral.standards.debug-contract-gated | scoped | not-applicable | no debug emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | helpers mirror candidate/job batch shape |
| astral.standards.in-scope-only | scoped | conforms | `src/` footprint is `database.py` + `config.py` only |
| astral.standards.logging-via-utils | scoped | conforms | no new loggers/print in touched `src/` |
| astral.standards.names-not-ticket-ids | scoped | conforms | domain names (`meteorite`, `METEORITE_STATES`) |
| astral.standards.no-cross-contamination | scoped | conforms | no unrelated product modules touched |
| astral.standards.no-hardcoded-sets | scoped | conforms | state keys from config; retention states parameterized |
| astral.standards.public-then-helpers | scoped | conforms | public helpers before `_ensure_*` / row mapper |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | config does not import data |
| astral.state.core-decides-transitions | scoped | conforms | `update_meteorite` validates key ∈ registry, not `prior_states` |
| astral.state.job-prior-states-enforced | scoped | not-applicable | staging registry, not `JOB_STATES` enforcement site |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | data spine only; no runners |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend |
| astral.ui.naming-conventions | scoped | not-applicable | no UI |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no server config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | `merge-tests(AST-1557)` present on tip |
| orch.git.commit-vocabulary | universal | conforms | `code`/`test`/`docs`/`merge-tests` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | sub under AST-1555 parent |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1555/AST-1557-…` |
| orch.git.merge-on-checkout | universal | conforms | no rebase violation observed |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no forbidden git ops in diff |
| orch.git.no-dev-agent-branches | universal | conforms | engineer sub branch only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | epic worktree AST-1555 |
| orch.git.three-permanent-branches | universal | conforms | diff vs `origin/dev` |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | no product-policy invention |
| orch.pipeline.plan-is-bible | universal | conforms | implementation matches Stages 1–3 |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Meteorite child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review |
| orch.roles.archie-approves-statutes | universal | conforms | no new statutes |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty test/bible commits |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Ada assignee |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | implementer still assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | no hook bypass in diff |

**Active set scored:** 64 rows (registry lists 65; all listed corpus ids covered).

---

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.state.entity-state-transitions | conforms | `METEORITE_STATES` registry in config; data accepts `state` param; no data-chosen transitions |
| pattern.batch.entity-claim-process-release | conforms | `claim_meteorite_batch` / `get_meteorite_batch` / `clear_meteorite_batch`; batch_id first; mirrors candidate peers |

Joan validate cites these patterns informally; no invalid/unapproved pattern ids.

---

## Plan adherence

**Product (Stages 1–3):** Matches plan.

- **Stage 1:** `METEORITE_STATES` (7 keys, `NEW` entry-only), `METEORITE_STATES_RETENTION`, header bullet, full assert lockstep — as specified.
- **Stage 2:** Table schema + indexes, claim trio (`batch_id` first, `_state_in_sql`, `ORDER BY rowid`), `insert_meteorite_rows` forces `NEW` in one transaction, read/update/list helpers, `update_meteorite` whitelist + state-key gate without `prior_states`, `_run_with_retry` on all public helpers.
- **Stage 3:** `list_meteorites_for_retention` + `delete_meteorites_by_ids` with parameterized state/cutoff/id lists; no day literals in SQL.
- **Affordance:** `list_meteorites_by_source` — plan-acceptable (Joan flagged in issue doc).
- **Estimate 5:** Honest for ~340 LOC data helpers + config registry + Betty tests.

**Out-of-scope respected in `src/`:** No inbox verbs, classify runner, Estelle, monitoring format, dispatch seeds, retention runner, or `meteorite_email.py` deletion.

---

## Findings

### discuss — sibling AST-1556 test/bible on publish ref

- **Location:** `tests/component/core/test_tracker.py`, `tests/component/ui/api/test_api_jobs.py`, `docs/test-bible/core/tracker.md`, `docs/test-bible/ui/api/api_jobs.md` (commit `4fafcc21` in branch ancestry via `origin/tests` / merge-base with ftr AST-1547 track)
- **Finding:** Three-dot diff vs `origin/dev` includes AST-1556 bug-repro test/bible deltas (artifacts-table SoT) but **no** AST-1556 product changes on tip — `tracker.py` still dual-writes `job_data`. Modified `TestAst1554BodyReplicaPersistHelpers` and new `TestAst1556JobArtifactsTableSoT` expect `save_artifact` calls that product does not make.
- **Recommendation:** Not an AST-1557 product defect. Betty manifest correctly scopes green to meteorite tests only. **Chuckles/datt:** decide whether to revert AST-1556 hunks on this sub tip before ftr merge, or accept as parallel-track carry from shared `origin/tests` ancestry. **Do not** ask resolve-child to implement AST-1556 product here.

### advisory — `NEW` / `BOT_BLOCKED` string collision across registries

- **Location:** `src/utils/config.py` `METEORITE_STATES` vs `JOB_STATES`
- **Finding:** Plan documents separate-dict import discipline; collision is intentional.
- **Recommendation:** Sibling core children (AST-1559+) must import `METEORITE_STATES` explicitly — already in plan Decision callout.

### advisory — `claim_meteorite_batch` does not validate state ∈ registry

- **Location:** `claim_meteorite_batch` in `database.py`
- **Finding:** Plan requires state-key validation on `update_meteorite` only; claim accepts caller-supplied state strings.
- **Recommendation:** Acceptable for data layer; core callers should pass registry keys.

---

## What's solid

- Clean data-layer spine: idempotent schema, batch claim parity with candidate helpers, insert fan-out forces `NEW`, retention helpers parameterized.
- Config registry with startup asserts prevents drift.
- Component tests cover schema, insert, claim/clear/reclaim, read/update gates, retention, and config partitions.
- Layer compliance: data imports config only; no logging in data; no scope creep in `src/`.

---

## Frame diff

| Area | Paths | Verdict |
|------|-------|---------|
| Product | `src/utils/config.py`, `src/data/database.py` | In-scope; plan-faithful |
| AST-1557 tests | `tests/component/data/database/test_meteorites.py`, `tests/component/utils/test_config.py`, data conftest/README | In-scope |
| AST-1557 bible | `docs/test-bible/data/database/meteorites.md`, `utils/config.md`, `data/database.md` | In-scope |
| Sibling bleed | `tests/component/core/test_tracker.py`, `tests/component/ui/api/test_api_jobs.py`, bible tracker/api_jobs | Discuss — not AST-1557 product |
| Plan doc | `docs/features/meteorite/ast-1557-meteorite-table-claim-helpers.md` | Present |

---

## Notes

- Joan plan-rubric APPROVED @ `9e494330`; no Excluded-statute attachment for straggler sweep.
- C6 lenses (imports, layers, silent failure, fallbacks, logging, batch/transitions, debug §5f, external §5g): no violations in touched `src/`.
- `_log_db_failure` satisfied via `_run_with_retry` wrapper (peer pattern).
- No fix-now product findings on AST-1557 scope.

---

## Recommended actions (downstream — not Radia)

1. **Chuckles:** Append this verdict to issue doc; post slim upshot; move to Review Posted.
2. **Chuckles/datt:** Resolve discuss item — strip or document AST-1556 test/bible hunks on sub tip.
3. **resolve-child:** No product changes required for AST-1557; proceed to User Testing after discuss acknowledged.
4. **Sibling implementers:** Use `METEORITE_STATES` import discipline when touching staging rows.

context_tokens≈58000

---

## Resolution

**Date:** 2026-08-31  
**Engineer:** Ada  
**Publish tip before resolve:** `2296d57b` (Radia `docs(AST-1557): Radia review — DISCUSS sibling test bleed`)

### discuss — sibling AST-1556 test/bible on publish ref

**Acknowledged.** Chuckles (2026-08-31 Linear note) accepted AST-1556 test/bible hunks as parallel-track carry from shared `origin/tests` ancestry; Betty's AST-1557 manifest stayed scoped to meteorite tests only. No revert on this sub tip before User Testing; strip only if `merge-child` / ftr conflicts. No AST-1557 product change.

### advisory — `NEW` / `BOT_BLOCKED` string collision

No code change — plan Decision + Radia note stand; siblings import `METEORITE_STATES` explicitly.

### advisory — `claim_meteorite_batch` state not registry-gated

No code change — matches plan (validate on `update_meteorite` only).

### Fix-now

None.

