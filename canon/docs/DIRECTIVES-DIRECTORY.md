# Proposed canon taxonomy (derived from `src/`)

Draft for Archie. Derived by reading the codebase, **not** by reorganising the
existing corpus — the current canon is where the drift lives, so reorganising it
would only reproduce its own mistakes. Existing directives cross-referenced
throughout.

Naming: `{p|s}.<scope>.<string-index>`. Orchestration is a separate corpus.

---

## 1. Scope taxonomy

Scope is "the noun this governs." Three families.

### Construct scopes — universal, repo-agnostic (the base template)

| Scope | Governs |
|---|---|
| `variables` | locals, constants, magic values |
| `functions` | naming, signatures, DRY, helper extraction |
| `component` | file organisation, comment hygiene |
| `errors` | who raises, who catches, who logs |
| `logging` | the debug contract, minimum viable info logging |

Nothing here mentions Astral. This is what ships as a template into any repo.

### Architecture scopes — the `src/` folders, which are already discrete

| Scope | Governs |
|---|---|
| `src` | applies across every layer of code |
| `core` | business orchestration |
| `data` | the SQL surface |
| `external` | I/O and its failure classification |
| `config` | the registry — `utils/config.py`. See below |
| `utils` | logging, formatting, auth, network — the leaf helpers |
| `api` | api resolution + React |
| `admin` | superuser features, tools, dashboards, operations |
| `docs` | rules for document use, structure, lifecycle |
| `frontend` | rules for UI/UX reliability and reuse, Typescript component frameworks |
| `devops` | rules pertaining to mirrored instances in the same environment, race conditions |

**NOTE:** `scripts` and`debug` are all explicitly OUT OF SCOPE for all directives.  They are not obliged to comply with canon directives.

**Filing rule:** scope is *where the violation occurs*, not where the fix lives.
"Don't hardcode allowed-value sets" is `general` (you can do it anywhere) even
though the fix always lands in `utils/config.py`.

**`config` is a scope without being a folder, and that needs no exception.**
Scope was never defined as "the directory" — it's "the noun this governs," which
is why `variables` and `functions` sit beside `core` and `data` already. Folder
correspondence is a convenience, not a rule, so `config` doesn't except anything.
It earns its own scope on merit: 5,790 lines, second-largest file in the repo,
imported by all five layers, and governed by rules that don't apply to the rest
of `utils`.

Promoting it to a sibling package would make things worse, for now.
`config.py` and `formatting.py` are mutually dependent, and both sides already
work around it — `formatting.py:143` carries the comment *"this module must not
import config at load — config imports us,"* and `config.py:5679` defers its
`value_to_str` import 5,600 lines into the file to break the cycle. Today that's
`utils → utils`, which the import rules allow. As a sibling package it becomes
`config → utils` *and* `utils → config` — a cross-layer cycle `stat.layers.import-rules`
would have to bless by name, plus an import change in the ~39 files across all
five layers that do `from src.utils.config import …`.

Breaking the `config` ↔ `formatting` cycle is worth its own ticket regardless of
canon. Until it's broken, the physical move trades a contained wart for an
architectural one. **§8 shows the cycle has a single cause and a small fix** —
once that lands, promoting `config` to a package is a rename.

### Subsystem scopes — where the arcs cluster (patterns mostly)

`entity` (shapes shared by candidate/company/job and potentially others in future scope), `agent`, `dispatch`,
`consult`, `artifact`, and `task`

Reserve `candidate` / `company` / `job` for the rare genuinely single-entity
rule — only three current directives name `company` at all, and each names all
three.

---

## 2. Patterns

Multi-step arcs with ownership per step. Evidence names the real functions —
these become `canonical_refs`.

### `logical-scope` — one per layer

What belongs here and why. Six files, and the per-module map lives *inside* the
layer's entry rather than in a file each. These are the ones worth keeping
resident during planning, because they answer the placement question that a plan
otherwise has to discover by hitting a wall.

| Pattern | Contents |
|---|---|
| `patt.python.logical-scope` | how the backend layers divide; what makes something core vs external vs utils vs config |
| `patt.typescript.logical-scope` | how the frontend divides — 94 `.tsx` + 34 `.ts` under `src/ui/frontend`; components vs pages vs contexts vs lib. **Under-derived — see open question 5** |
| `patt.core.logical-scope` | core owns orchestration and decides transitions. Module map: `roster` (entity agent story), `tracker` (job + artifacts), `candidate` (candidate lifecycle), `agent` (AI calls), `dispatcher` (scheduling), `consult` (verdicts), `builder`, `gazer`, `intake`, `contact`, `inbox` |
| `patt.data.logical-scope` | data owns SQL and raises; never logs, never decides state |
| `patt.external.logical-scope` | external performs all I/O, classifies its own failures, returns data |
| `patt.utils.logical-scope` | leaf helpers — logging, formatting, auth, network; no business logic |
| `patt.config.logical-scope` | the registry: what belongs in `config.py` vs a `*_data` blob vs a DB table |
| `patt.ui.logical-scope` | `ui/api/` resolves; React renders what it's handed |

### `data`

| Pattern | Arc / contents | Evidence |
|---|---|---|
| `patt.data.entity-definition` | **What is a root column, what goes in the `*_data` JSON, what lives elsewhere.** Root ⟺ the database must query, filter, sort, lock, or transition on it. See §4 for the rubric the schema already follows | `job`, `company`, `candidate` tables; `agent_data` |
| `patt.data.save-vs-update` | full upsert vs partial allowlisted update — two writers per entity | `save_company`/`update_company`, `save_agent`/`update_agent`, `save_dispatch_task`/`update_dispatch_task` |

### `entity`

| Pattern | Arc | Evidence |
|---|---|---|
| `patt.entity.batch-claim-release` | claim under one `batch_id` → process only claimed rows → clear in `finally` | `claim_{company,job,candidate}_batch`, `clear_*_batch`, `release_job_dispatch_claim`, `_assert_valid_job_batch_claim_state` |
| `patt.entity.state-transition` | core picks target from registry → tracker validates `prior_states` → data writes | `transition_job_state`, `_job_state_matches_prior`, `JOB_STATES` |
| `patt.entity.artifact-updates` | tag RESPONSE with `entity_id` on write → read latest-per-`task_key` via helper | `list_entity_latest_agent_refs` |

### `artifact`

| Pattern | Arc | Evidence |
|---|---|---|
| `patt.artifact.build-lifecycle` | start → cancel → clear, build state on the entity | `start_artifact_build`, `cancel_artifact_build`, `clear_job_build_artifacts`, `BUILD_ARTIFACTS_BASE_STATE` |
| `patt.artifact.parse-validate-persist` | shape-check parsed → slice to shape → persist → pin `agent_data` id → hydrate for display | `parsed_matches_artifact_shape`, `slice_parsed_for_artifact_shape`, `persist_job_artifact_from_parsed`, `pin_job_artifact_agent_data_id`, `hydrate_job_artifacts_for_display` |

### `agent`

| Pattern | Arc | Evidence |
|---|---|---|
| `patt.agent.prompt-resolution` | task system + task prompts + agent content resolved before the call | `resolved_task_system`, `_resolve_task_prompts`, `resolved_agent_content` |
| `patt.agent.chain-context` | caller tokens in → merge for next hop → carry forward | `_incoming_chain_context`, `_chain_context`, `_chain_tokens_for_next_hop`, `_merge_chain_context_for_next_hop`, `_referenced_caller_tokens` |
| `patt.agent.response-decode` | stored response text → block by type → inner payload → parsed | `_parsed_response_from_stored_response_text`, `_block_text_by_type`, `_decode_payload`, `_inner_task_payload` |
| `patt.agent.grade-validation` | vector names checked → unexpected rejected → grade + confidence validated | `_validate_grade_confidence_list`, `GRADE_VALUES`, `CONFIDENCE_MULTIPLIERS` |

### `dispatch`

| Pattern | Arc | Evidence |
|---|---|---|
| `patt.dispatch.ensure-provision` | `ensure_X` idempotent for one entity; `provision_X` seeds template then backfills all | `ensure_meteorite_dispatch_tasks`/`provision_meteorite_dispatch_tasks`, `ensure_gaze_email_dispatch_task`/`provision_gaze_email_dispatch_tasks` |
| `patt.dispatch.chain-hop` | `run_next` decides succession → hop label written → graduate at terminal | `write_job_dispatch_hop_label`, `graduate_job_from_dispatch_chain`, `DISPATCH_CHAIN_TERMINAL_GRADUATION` |
| `patt.dispatch.scheduler-loop` | tick → circuit breaker → thread target → run/drain/cancel | `_tick_loop`, `start_scheduler`, `_check_circuit_breaker`, `run_task`, `drain_task`, `cancel_task` |
| `patt.dispatch.score-floor` | one floor on the `dispatch_task` row governs eligibility *and* soft-fail | existing pattern — keep |
| `patt.dispatch.retry-batch` | *(your list — no distinct retry arc found in `src/`; AST-1319 in flight?)* | — |

### `consult`

| Pattern | Arc | Evidence |
|---|---|---|
| `patt.consult.verdict-render` | dispatcher loops → `render_verdict` owns per-job lifecycle → tracker never called directly | `_consult_orchestration`, `_render_pass_fail` — **currently a statute with no pattern** |
| `patt.consult.rubric-hydration` | criteria from cfg → find criterion → reason for grade → hydrate → snapshot onto job_data | `_rubric_criteria_for_cfg`, `_find_rubric_criterion`, `_lookup_rubric_reason_for_grade`, `_hydrate_grade_reasons_from_rubric`, `_rubric_snapshot_for_job_data` |
| `patt.consult.encoded-line` | detect encoded line → parse link index → apply prefilter meta | `_should_decode_as_encoded_line`, `_parse_link_index_field`, `_apply_prefilter_encoded_link_meta` |

### `bootstrap`

How seed data gets in, and how agent tasks and prompts migrate.

| Pattern | Arc | Evidence |
|---|---|---|
| `p.bootstrap.repo-json-roundtrip` | **the agent/prompt migration path.** `data/admin/*.json` is source of truth → applied repo-wins at startup → divergence against the DB is detectable → revert-to-file, or export DB back to file when an operator edit should become canon | `apply_repo_admin_json_at_startup`, `get_repo_admin_json_divergence_status`, `revert_repo_admin_json_table`, `export_repo_admin_json_to_files`, `_sorted_normalized_rows` |
| `p.bootstrap.prompt-versioning` | never edit in place: retire the prior row, insert a new `current=1` | `agent_task` (all seven prompt segments); `rubric_vector` follows the same shape |
| `p.bootstrap.one-off-migration` | a dated, single-purpose script that backfills and is never called from runtime | `scripts/migrations/backfill_*.py` — nine of them |

Seeding *dispatch rows* is `patt.dispatch.ensure-provision` above; this scope covers
the repo-owned tables and the prompt corpus.

### `ui` / `utils`

| Pattern | Arc | Evidence |
|---|---|---|
| `patt.ui.endpoint` | blueprint route → `@require_auth` → resolve in api → JSON error shape | `api_jobs.py`, `flask.g.user` |
| `patt.ui.dirty-leave-save-then-navigate` | existing, still `proposed` — approve it | — |
| `patt.config.block` | a `*_CONFIG` dict per feature, registered in `config.py` | `TASK_CONFIG`, `CANDIDATE_CONFIG`, `ROSTER_CONFIG`, ~40 more |

---

## 3. Statutes

| Statute | Rule | From |
|---|---|---|
| `stat.variables.local-if-one-off` | single-use values stay local | new |
| `stat.variables.named-constants` | magic numbers get named constants with documented meaning | `standards.no-hardcoded-sets` (split) |
| `stat.functions.clear-names` | name what it does in stable domain language | `standards.names-not-ticket-ids` |
| `stat.functions.non-specific-names` | no ticket ids or ticket-shaped names | same (split) |
| `stat.functions.dont-repeat-yourself` | read the whole file before adding; extract shared logic | `standards.dry-and-focused-functions` (split) |
| `stat.functions.helper-functions` | complex logic goes to a helper; keep functions focused | same (split) |
| `stat.component.file-organization` | public functions first, then helpers, grouped by responsibility | `standards.public-then-helpers` |
| `stat.component.comment-hygiene` | — | **new** |
| `stat.errors.data-raises-caller-logs` | data raises and never logs; core raises domain; dispatcher catches and logs at batch; UI returns JSON | `standards.data-raises-caller-logs` |
| `s.logging.via-utils` | backend logging goes through `utils/logging.py` | `standards.logging-via-utils` |
| `s.logging.debug-gated` | debug lines only under `debug_flag`; use the `_PrefixedLogger` helpers and `truncate_debug_content` | `standards.debug-contract-gated` |
| `stat.layers.import-rules` | ui → core+utils; core → data+external+utils; external → utils; data → utils | `layers.import-direction` |
| `stat.general.no-cross-contamination` | nothing outside the five `src/` layers | `standards.no-cross-contamination` |
| `stat.general.registry-not-literals` | state lists, enums, allowed sets live in `config.py`; validate against it | `config.config-source-of-truth` + `standards.no-hardcoded-sets` |
| `stat.core.entity-save` | **save through the core entity module — `roster` / `tracker` / `candidate`. Do not reach into `data.database` to write, and do not add a new writer** | **new — the seven-bridges rule** |
| `stat.core.decides-transitions` | core picks the target state; data/tracker accept it as a parameter | `state.core-decides-transitions` |
| `stat.data.table-inventory` | the data layer may use only tables listed in the `database.py` header; changing usage updates the header | `standards.database-header-inventory`, renamed for legibility |
| `stat.data.partial-update-allowlist` | `update_X` sets only passed columns, allowlist enforced, returns rowcount | new, from `update_company` |
| `stat.data.batch-id-first` | `batch_id` is the first parameter on claim/get/clear helpers | `batch.batch-id-first` |
| `stat.data.no-mirror-columns` | no entity-row JSON mirror of `agent_data`; latest refs are read, not stored | `batch.entity-agent-responses-latest-only`, and `company.agent_responses_legacy` is the scar |
| `stat.external.io-only-here` | external owns all I/O and returns data | `layers.core-vs-external-bright-line` |
| `stat.config.secrets-from-environ` | `os.environ["KEY"]` — no `.get`, no fallback, crash at startup; never a secret in `config.py` | `config.secrets-and-env-specific-from-environ` |
| `stat.utils.data-late-import-only` | the one approved `utils → data` path is the log-handler flush | `standards.utils-data-late-import-only` |
| `stat.scripts.exempt-from-layer-rules` | `scripts/` may import any layer | `layers.scripts-exempt-from-layer-rules` |
| `stat.dispatch.seed-auto-false` | seed paths leave `auto_mode` false | `dispatch.seed-auto-false` |
| `stat.dispatch.provision-idempotent` | `ensure_*` is safe to run repeatedly; boot or explicit script only, never per-request | `seed.boot-only-not-hot-path` + your `idempotent-as-default` |
| `stat.config.no-shadow-chain` | config must not restate membership or succession already encoded in `agent_task.run_next` | `dispatch.run-next-is-chain-authority` |
| `stat.config.single-home` | configuration lives in `config.py` and nowhere else. A module does not define its own public constants — see §12 for the full form | **new** |
| `s.bootstrap.seed-is-repo-owned` | `agent` and `agent_task` content lives in `data/admin/*.json`, Archie-approved, non-empty; `[]` is not a valid seed | `seed.agent-tables-in-repo-json` |
| `s.bootstrap.catalog-wins` | the committed catalog is authoritative — lasting change is an edit and a commit, never a live DB edit alone | `seed.archie-catalog-wins` |
| `s.bootstrap.operator-rows-stay-deleted` | rows outside a named seed catalog are operator-owned; deleted stays deleted across restart and schema-ensure | `seed.operator-rows-stay-deleted` |
| `s.bootstrap.coverage-by-join` | seed targets derive from joining extant tables; hardcoded entity ids never define coverage | `seed.other-via-coverage-join` |
| `s.bootstrap.flat-rows-only` | repo-admin JSON rows are flat scalars — no nested JSON, so file and DB stay comparable | `_reject_nested_json`, `_normalize_repo_json_row` (new) |
| `stat.state.prior-states-enforced` | transitions raise if the current state is not an allowed predecessor | `state.job-prior-states-enforced` |
| `stat.state.one-transition-per-run` | one claim, one process, one transition per cycle; documented `run_next` hops are the carve-out | `state.no-daisy-chain-in-run` |
| `stat.agent.confidence-bounds` | integer `confidence` 1–5 with letter grades, 0 with `X`; confidence 1 is no signal | `agent.confidence-bounds` |
| `stat.agent.vector-validation` | required vector names present, unexpected rejected, grades in the allowed set | `agent.grade-vector-validation` |
| `stat.data.batch-id-format` | `batch_id` is `f"{task_key}-{uuid}"` | `batch.batch-id-format` |
| `stat.core.coat-check-never-stores-empty` | a coat-check handler returns `None` rather than storing an empty or failed value, so the next attempt re-fetches | `idioms.coat-check-never-store-empty` |
| `stat.ui.icon-control` | compact glyph actions use the shared icon-control class, not one-off buttons or abbreviated text | `pattern.ui.icon-control` — a ui statute, not a pattern |
| `stat.ui.shared-button-roles` | labeled buttons use the shared role classes; no parallel families | `pattern.ui.shared-button-roles` — same |
| `stat.ui.single-gunicorn-worker` | one gunicorn worker; the dispatch scheduler runs per-worker | `ui.single-gunicorn-worker` |
| `stat.scripts.spikes-under-debug` | spike output goes to `debug/spikes/<issue-id>/`, gitignored; findings go on the ticket | `debug.spikes-under-debug-dir` |
| `stat.scripts.no-root-artifacts-dir` | no top-level `artifacts/` directory | `debug.no-repo-root-artifacts-dir` |
| `stat.agent.core-delegates-io` | core calls `do_task`; config informs; external performs I/O | `agent.do-task-delegation` |
| `stat.ui.require-auth` | protected endpoints carry `@require_auth`; identity is `flask.g.user` | `idioms.require-auth-on-protected-endpoints` |
| `stat.ui.config-driven-logic` | conditional frontend behaviour resolves in `ui/api/` before serving | `layers.ui-config-driven-business-logic` |
| `stat.ui.file-placement` | the prescribed flat frontend locations | `ui.frontend-file-placement` |
| `stat.ui.naming-conventions` | PascalCase components; snake_case routes and Python | `ui.naming-conventions` |

---

## 4. `patt.data.entity-definition` — the rubric the schema already follows

`job`, `company`, and `candidate` are consistent, so the rule can be stated
rather than invented:

**A field is a root column if and only if the database must act on it.**

| Root because | `job` | `company` | `candidate` |
|---|---|---|---|
| identity / PK | `astral_job_id` | `short_name` | `astral_candidate_id` |
| state machine — claimed *by* state | `state`, `state_history`, `state_changed_at` | `state`, `state_history`, `state_updated_at` | `state`, `state_history`, `state_changed_at` |
| claim lock — filtered *by* batch | `batch_id`, `batch_created_at` | `batch_id`, `batch_created_at` | `batch_id`, `batch_created_at` |
| audit | `created_at`, `updated_at` | `created_at`, `updated_at` | `created_at`, `updated_at` |
| indexed lookup / list filter | `company`, `company_job_id`, `job_title`, `job_link` | `company_name`, `job_site`, `company_website` | `first`, `last`, `full`, `pronouns` |
| poll cursor | — | `last_scan_at` | `last_email_check` |
| credential | — | — | `candidate_api_key` |

**Everything descriptive goes in the `*_data` JSON** — `job_data`,
`company_data`, `candidate_data`. If nothing queries it, it isn't a column.

**Anything large, historical, or per-task lives in `agent_data`**, keyed
`(entity_type, entity_id, task_key, batch_id, created_at)` with
`block_type` / `block_data` and `ref_agent_data_id` for chaining. The index on
`(entity_type, entity_id, task_key, created_at)` is what makes
`list_entity_latest_agent_refs` possible.

**Counterexample in the schema:** `company.agent_responses_legacy` is a mirror
column of exactly the kind `stat.data.no-mirror-columns` now forbids. Worth citing
in the pattern as the thing that went wrong.

---

## 5. Notes

**`header-inventory` renamed.** It's now `stat.data.table-inventory` — the same
existing rule (`database.py`'s header lists the tables the layer may touch), with
a name that says what it does. The broader "what belongs here" need is served by
the `p.<layer>.logical-scope` patterns, which is the legible version.

**Idempotency is dispatch, not config.** The real shape is the `ensure_X` /
`provision_X` twin in `dispatcher.py`.

**Two of your patterns are already-duplicated statutes** and merge rather than
move: batch management and artifact updates.

**Retire on sight:** `pattern.layers.import-discipline`; `pattern.config.config-block`
survives only as `patt.config.block` (the registry *rule* is
`stat.general.registry-not-literals`, a statute); and the three
`stat.patterns.*` duplicates with their `stat.idioms.*` twins.

---

## 6. Open questions

1. **`src/ui/api/api_admin.py` makes 44 direct `database.*` calls.** That's a
   `ui → data` import, which `stat.layers.import-rules` forbids. It's the only UI
   file doing it. Sanctioned exception, or a real violation to fix?

This is an explicit exception until database.py is refactored.

2. `patt.data.save-vs-update` — pattern to follow or wart to remove? It reads
   deliberate (full upsert vs allowlisted partial), but it's the shape that grows
   a third writer.

Also an explicit exception until the database.py refactor.

3. `patt.dispatch.retry-batch` — no distinct retry arc found in `src/`. AST-1319
   still in flight?

Task is now a recognized subsystem, where retry is specified.

4. `core/roster.py` (3,635 lines) and `core/candidate.py` (3,417) are larger than
   `agent.py`. I found no arcs in them distinct from the entity/dispatch
   families, but they're big enough that I may have missed a subsystem.

Roster, candidate and tracker all fall under entity, but entity-type specifics may call for subsystems of roster, candidate and tracker.

---

## 7. Migration coverage

Checked every live directive against this doc with `canon_clerk.py`, so nothing
is dropped silently. Of 73 live directives:

**Absorbed under a new name** — no action beyond the rename:

| Current | Becomes |
|---|---|
| `batch.claim-process-release` + `pattern.batch.entity-claim-process-release` | `patt.entity.batch-claim-release` (the merge) |
| `batch.entity-agent-responses-latest-only` + `pattern.batch.entity-agent-responses` | `patt.entity.artifact-updates` (the merge) |
| `pattern.state.entity-state-transitions` | `patt.entity.state-transition` |
| `idioms.render-verdict-orchestrates-consult` | `patt.consult.verdict-render` |
| `pattern.ui.admin-endpoint` | `patt.ui.endpoint` |
| `pattern.config.config-block` | `patt.config.block` |
| `agent.do-task-delegation` | `stat.agent.core-delegates-io` |

**Moves to the orchestration corpus** — out of scope here, but must land there or
it's lost: `standards.in-scope-only`, `seed.define-approved`,
`docs.features-single-file-per-ticket`, `git.betty-no-src-or-features`,
`git.engineer-test-tree-ban`. The last two are duplicates of
`orch.roles.pre-commit-path-bans` and `orch.roles.betty-owns-test-tree` and
should collapse into them rather than move.

**Retired, no successor:** the three `astral.patterns.*` duplicates (superseded by
their `astral.idioms.*` twins), `config.pass-threshold-vs-score-floor`,
`pattern.layers.import-discipline`, and `pattern.config.config-block` *as a
pattern*.

**Still `proposed` and needing an Archie decision before migration:**
`pattern.dispatch.run-next-chain-authority` and
`pattern.ui.dirty-leave-save-then-navigate`. Under the new rule that retires the
`proposed` status, these can't carry over undecided.

Re-run the check after any edit:

```bash
python3 canon-v2/canon_clerk.py index --json
```

---

## 8. `config.py` is not config — decomposition argument

`utils/config.py` holds **75 functions** across 5,790 lines. That is not a
registry; it's a module with a registry inside it. The circular import is the
symptom, not the disease.

### The cycle, precisely

Two late imports, each working around the other:

| Edge | Where | Used by |
|---|---|---|
| `config → formatting` | `config.py:5679`, deferred 5,600 lines in | only `resolve_tokens` |
| `formatting → config` | `formatting.py:148`, inside the function | only `normalize_pasted_list_email_html` |

**The edges are not equally legitimate, and that resolves it.**
`formatting → config` is the *correct* direction — a formatting helper reading
`METEORITE_EMAIL_INGEST_CONFIG` is exactly what a registry is for. That edge
should be an ordinary top-level import.

`config → formatting` is the wrong direction, and it exists for one reason:
`resolve_tokens` is a **template engine**. It compiles `{$TOKEN}` against
`_TOKEN_RE`, walks dot-paths, dispatches through `_CONFIG_RESOLVERS`, and
stringifies results with `value_to_str`. Rendering is not storage.

### The minimal fix

Extract the token engine to `src/utils/prompt_tokens.py` — the block from line
5679 to the end of the file, four public functions plus `_TOKEN_RE` and
`_CONFIG_RESOLVERS`, together with their upstream helpers (`get_tokens`,
`get_manage_tasks_chain_tokens`, `get_manage_agents_tokens`, `_walk_dot_path`,
`stringify_response_schema`, `_schema_to_example`).

Resulting edges, both one-way and both already legal:

```
prompt_tokens → config      (reads the token specs)
prompt_tokens → formatting  (value_to_str)
formatting    → config      (top-level now, no workaround)
```

`config` imports nothing from `utils` but `logging`. The cycle is gone, the
comment at `formatting.py:143` is deleted, and **the config package promotion
becomes a rename** rather than an architecture change.

### What else is in there

Sorting all 75 by what they actually do:

| Family | ~n | Examples | Belongs |
|---|---|---|---|
| Accessors over config dicts | 15 | `grade_value`, `get_task_keys`, `get_model`, `template_candidate_id` | **stays** — this is config |
| Dispatch / state policy | 11 | `effective_dispatch_score_floor`, `dispatch_claim_states`, `dispatch_chain_graduation_target`, `is_valid_job_batch_claim_state` | `core` — these are decisions, and `stat.core.decides-transitions` says core makes them |
| Token / template engine | 12 | `resolve_tokens`, `get_tokens`, `_walk_dot_path`, `stringify_response_schema` | `utils/prompt_tokens.py` — **the cycle** |
| Codecs and labels | 9 | `dispatch_hop_label` / `parse_dispatch_hop_label` (an encode/decode pair), `dispatch_task_key_retired_message` | `utils` — a codec is not a value |
| UI manifest builders | 4 | `build_state_ui_manifest`, `jobs_ui_rubric_for_state`, `admin_hidden_dispatch_task_keys` | `ui/api/` — `stat.ui.config-driven-logic` already says resolve there |
| Env / provider validation | 9 | `validate_llm_provider_environment`, `get_active_llm_provider`, `_parse_csv_env` | a startup/env module |

Only the first family is config. Roughly **60 of 75 functions** are behaviour
that found a home in the registry because the registry is what everything
already imports.

### The statute this produces

| Statute | Rule |
|---|---|
| `stat.config.data-not-behaviour` | config holds values and plain accessors over them. Decisions, codecs, templating, and response shaping live in the layer that owns them. If a config function needs to import a peer to do its job, it isn't config |

That last clause is a mechanical test, and it's the one that would have caught
this: `config.py` importing `formatting` was the tell, five thousand lines ago.

---

## 9. Added to open questions

5. **The TypeScript half is under-derived.** My first survey globbed `*.py` and
   `*.jsx` and reported "17 UI files" — the frontend is actually 94 `.tsx` and
   34 `.ts`, none of which I read. Every `ui` entry above is derived from
   `src/ui/api/` (the Python side) only. `patt.typescript.logical-scope`,
   `stat.ui.icon-control`, and `stat.ui.shared-button-roles` need a pass over the real
   frontend before they're trustworthy.
6. **Does splitting `general` into `python` / `typescript` split the construct
   statutes too?** `stat.functions.clear-names` and `stat.component.file-organization`
   read as language-neutral, but `stat.ui.naming-conventions` currently straddles
   both ("PascalCase components; snake_case routes and Python") — which is one
   directive doing two languages' work, and an argument that the split should go
   all the way down.

---

## 10. Config is a free-for-all — the consolidation case

**128 top-level constants, 254,687 characters.** Grouping by prefix, **69 of them
(54%) belong to 11 families** that were never given a home. A further 37 prefixes
appear exactly once.

| Family | n | chars | What it is |
|---|---:|---:|---|
| `JOBS_*` | 18 | 16,327 | jobs-page view config — sections, tabs, labels, grade fields, per-view rubric overrides |
| `RESUME_*` | 13 | 4,718 | one feature's shape spec, shattered into 13 top-level names |
| `CANDIDATE_*` | 8 | 11,483 | states, lookup, library, legacy maps, uniqueness |
| `RUBRIC_*` | 5 | 3,562 | feedback config, artifact-key maps, totals |
| `CRAFT_*` | 4 | 2,843 | token caps, nav paths, task→artifact maps |
| `JOB_*` | 4 | 12,325 | states, tokens, artifact pins/clears |
| `METEORITE_*` | 4 | 8,312 | ingest, parse, dispatch tasks, general |
| `BRAIN_*` | 4 | 611 | `BRAIN_SETTINGS` plus three 8-char constants that are its own keys |
| `DISPATCH_*` | 3 | 16,860 | retired keys, score-floor values, chain graduation |
| `PROVIDER_*` | 3 | 1,563 | call budget, balance refusal, empty response |
| `PRONOUN_*` | 3 | 1,122 | forms, options, default |

### The tell

`CANDIDATE_CONFIG` is **210 characters — the smallest member of its own family**,
while `CANDIDATE_STATES` beside it is 3,479. The block that carries the feature's
name holds almost none of the feature's config. That is the free-for-all in one
line: nobody was wrong to add a constant, and nobody could tell where it went.

`JOBS_*` is the worst case — eighteen peers, every one of them UI view
configuration for the same set of pages, none of them nested. And by
`stat.ui.config-driven-logic` most of it shouldn't be in `config.py` at all; it
should resolve in `ui/api/`.

### Two structural findings

**48 of 128 constants are non-literal** — built from other constants or function
calls rather than written down. Config isn't storing values; nearly 40% of it is
computing them. That is §8's `stat.config.data-not-behaviour` measured from a
different angle.

**Named state subsets are built two different ways.**
`RECOMMENDED_JOB_STATES`, `PASSED_SCORE_GATED_STATES`, and
`CANDIDATE_LEGACY_TRIGGER_STATES` are derived at runtime from the registry.
`IN_REVIEW_STATES` (28 entries) and `SKIPPED_STATES` (31) are typed out as
literals. Same kind of thing, same file, two methods — and the derived form is
the one `stat.general.registry-not-literals` is asking for.

### Target

128 → roughly 25 top-level blocks. Each family collapses to one named block with
the members as keys; the 37 singletons mostly stay.

### The directives that prevent recurrence

| Directive | Rule |
|---|---|
| `stat.config.every-block-states-its-scope` | every top-level block carries a one-line scope statement saying what belongs in it. A new value goes in the block whose scope covers it; if none does, it goes in `ASTRAL_CONFIG`. Adding a *new* top-level block requires Archie |
| `stat.config.derive-dont-restate` | a subset of a registry is derived from it, never typed out again. `IN_REVIEW_STATES` and `SKIPPED_STATES` are the current violations |
| `patt.config.task-config` | one file, two sections. `# Logical scope`: what belongs in `TASK_CONFIG`. `# Data coupling`: what the scorer compares — `TASK_CONFIG` keys against `agent_task` rows, kept in sync by `data/admin/agent_task.json` — and what each band means. **Measured today: 47 config keys vs 52 JSON keys, 44 shared** |

**`ASTRAL_CONFIG` is not a symptom.** It's the designated island of misfit toys —
a value with no clear home is *supposed* to rest there. What makes it work is
that every other block states its scope, so "no clear home" is a determination
rather than a shrug. See §11 for the homes.

---

## 11. Eviction, then homes
 
Consolidation was the wrong first move. **29% of `config.py` isn't configuration
at all** — 43 constants, 76,149 characters, that belong somewhere else entirely.
Grouping them into tidier config blocks would have preserved the mistake.

| Destination | n | chars | Exists today? |
|---|---:|---:|---|
| **frontend / `ui/api`** — view layout, labels, column specs | 26 | 36,918 | yes — `src/ui/frontend` (94 `.tsx`), `src/ui/api/` |
| **`agent_task` prompt corpus** — criteria and schema content | 5 | 11,019 | yes — `agent_task` rows + `data/admin/agent_task.json` |
| **legacy maps** — delete, or `scripts/migrations/` | 4 | 1,005 | yes |
| **EVICTED** | **35** | **48,942 (19%)** | |
| **remains — real config, 10 root nodes** | 93 | 205,745 (81%) | |

**Everything that is configuration stays in `config.py`.** An earlier draft sent
`PLAYWRIGHT_CONFIG`, `GOOGLE_CSE_CONFIG`, and `DEEPSEEK_MODEL_PRICING` to their
owning modules. That was wrong twice over: it creates a second place config can
live — "is it in `config.py` or in the module?" becomes unanswerable — and the
readers don't support it. `PLAYWRIGHT_CONFIG` is read by `core/gazer`,
`core/roster`, *and* `external/playwright`; `DEEPSEEK_MODEL_PRICING` by four
modules across four layers. They live in a new `EXTERNAL_CONFIG` root node.

The three surviving eviction categories are all **"this is not configuration"** —
not "configuration somewhere else." That distinction is what keeps the boundary
answerable.

> **Note on `utils/prompt_tokens.py`:** it does **not** exist. It is the proposed
> destination for the token *engine* extraction in §8, and nothing should be
> filed against it until that refactor is scoped. The token *registries*
> (`CALLER_HOP_TOKEN_NAMES`, `TOKEN_SOURCES`, `JOB_TOKEN_CONFIG`) are config data
> and stay, under `AGENT_CONFIG.PROMPT_CONFIG`.

The sharpest one is the prompt corpus. `EMBEDDED_*_CRITERIA` is rubric content
living as a Python literal, next to a system that already has versioned prompt
storage with retire-and-insert semantics and a repo-JSON sync path. Two homes for
the same kind of thing, and the worse one won by being easier to import.

**Not evictable, contrary to first read:** `DISPATCH_RETIRED_TASK_KEYS` (12,413)
is live — `api_admin.py` filters rows against it and `dispatcher.py:288` derives
its wrapper subset from it with the comment *"not a second literal set."* That's
`stat.config.derive-dont-restate` already being obeyed. It's large because there are
many retired keys, which is a data question, not a placement one.

### The homes, each with a stated scope

The scope line is the whole point: an agent adding a value reads these and picks,
instead of dropping it at root.

| Block | Belongs here |
|---|---|
| `AGENT_CONFIG` | how we call an LLM — providers, brains, models, token budgets, pricing, refusal handling |
| `TASK_CONFIG` | per-`task_key` definitions: vectors, prompts wiring, scoring. **Coupled** — see below |
| `JOB_CONFIG` | the job entity: states, transitions, claim states, artifact pins and clears |
| `COMPANY_CONFIG` | the company entity: states, roster scan and discovery behaviour |
| `CANDIDATE_CONFIG` | the candidate entity: states, contact, intake, preamble, topic menu, pronouns |
| `CONSULT_CONFIG` | rubrics and grading: grade values, confidence, feedback, totals |
| `BUILD_CONFIG` | artifact construction: resume structure, cover blocks, craft caps, build states |
| `DISPATCH_CONFIG` | scheduling: score floors, chain graduation, retired keys, stage dispatch |
| `METEORITE_CONFIG` | the meteorite feature end to end |
| `ASTRAL_CONFIG` | **the island of misfit toys, by design.** Env, paths, runtime, and anything whose home is genuinely unclear. It works *because* every block above states its scope — "no clear home" becomes a determination rather than a shrug |

Adding a new top-level block is an Archie decision. Adding a key inside one is not.

### `patt.config.task-config` — the coupling worth writing down

`TASK_CONFIG` is the one with a real data coupling, and it's already drifting:

- **47** keys in `TASK_CONFIG`
- **52** task_keys in `data/admin/agent_task.json`
- **44** in both — 3 config-only, 8 JSON-only

A `task_key` must exist in `TASK_CONFIG` *and* as an `agent_task` row; code
resolves task identity from table content; `data/admin/agent_task.json` is the
mechanism that keeps the two in sync. Adding a key in one place alone is a live
defect.

The `# Data coupling` section is written for the **scorer**, not for a script:
it says what to compare and what the bands mean. When this pattern is in an
issue's Canon Scope, Joan checks it against the plan and Radia against the diff,
every time — that is the check. A key added to one side only is a **2**; a second
sync path invented alongside `data/admin/*.json` is a **1**. No separate
mechanism: the corpus is scored by the rubric, and anything that verifies canon
outside that pass is a second bridge.

Whether all 11 of those divergences are wrong is a question for Archie — the
JSON-only set is mostly fetch/scrape tasks (`fetch_jd`, `fetch_website`, `gaze`)
that may legitimately have no `TASK_CONFIG` entry. But `parse_meteorite_email`
(JSON) against `meteorite_email` (config) looks like a half-landed rename.

---

## 12. `stat.config.single-home` — worked example of the beefy format

The first directive written in the full shape: preamble, scenario, literal
Do/Don't. Everything above is a one-line summary table; this is what the file
itself looks like. No `# Scoring` — the grade scale is universal and lives once in
the clerk's `USAGE` preamble.

---

### Preamble

Configuration has exactly one home. The moment a second home exists — a module
that keeps "just its own" settings — the question *where is this configured?*
stops having an answer, and the two homes drift. This is the same failure as two
sync paths or two review mechanisms: not that either place is wrong, but that
there are two.

**The test is mutability, not naming.** Config means what it says: values that
are ultimately ours to change, held in one place for consistent consumption.

> **Would the code still work if Archie swapped this for a different value of the
> same datatype?**
> **Yes → config.** It is a knob.
> **No → owner-hosted.** It is a contract with something outside our discretion,
> and it belongs beside the code that honours it.

A timeout of 30,000ms could be 45,000ms; nothing breaks. A string that must match
a vendor's exception text, a DB column name, or another function's return value
cannot be changed freely — those are not knobs, and hoisting them into `config.py`
would advertise a freedom that does not exist.

Private mechanics stay local regardless of the test: a `_`-prefixed compiled
regex or punctuation set is one function's business, not a setting.

### Statement

Behaviour-driving values live in `src/utils/config.py`, under the root node whose
stated scope covers them. Modules import config; they do not define it. A module
may define `_`-prefixed private constants for its own mechanics.

### Scenario

You are adding Playwright retry behaviour. The natural move is a constant at the
top of `external/playwright.py` — it is the only file that uses it, and the
import is one line shorter.

Six weeks later `core/gazer` needs the same retry budget. Now `core` imports a
constant out of an external module, or copies it. `PLAYWRIGHT_CONFIG` in
`config.py` today has exactly this history: three readers across two layers
(`core/gazer`, `core/roster`, `external/playwright`). `DEEPSEEK_MODEL_PRICING`
has four readers across four layers. Neither would have survived as module-local.

### Do

```python
# src/utils/config.py
EXTERNAL_CONFIG = {
    "playwright": {
        "nav_timeout_ms": 30_000,
        "retry_attempts": 3,
    },
}

# src/external/playwright.py
from src.utils.config import EXTERNAL_CONFIG

_TRAILING_PUNCT = ",.;)]"        # implementation detail — correctly local

def navigate(url: str):
    timeout = EXTERNAL_CONFIG["playwright"]["nav_timeout_ms"]
```

### Don't

```python
# src/external/playwright.py
NAV_TIMEOUT_MS = 30_000          # public, behaviour-driving, not in config.py
RETRY_ATTEMPTS = 3               # the second home starts here
```

```python
# src/core/gazer.py — and this is how it spreads
from src.external.playwright import NAV_TIMEOUT_MS   # core reading config out of external
```

### The test applied — `PLAYWRIGHT_INFRA_FAILURE_CLASSES`

`external/playwright.py:29` holds a public frozenset of failure classes. It looks
like config. It is not.

`classify_playwright_failure` returns those exact strings as hardcoded literals
(`return "channel_error"`), and `is_playwright_infra_failure` matches the returned
value against the set. Change `"channel_error"` to `"channel_fault"` in the set
and the two silently stop agreeing. **It breaks — owner-hosted, correctly where it
already is.**

Contrast `PLAYWRIGHT_CONFIG["nav_timeout_ms"]`: any integer works. Knob. Config.

### The exception — `TASK_CONFIG`

`TASK_CONFIG` fails the test and is config anyway. Archie cannot add a `task_key`
by editing config alone — it needs a matching `agent_task` row and the code that
recognises it. It is the one block where a value change is not self-contained.

That is precisely why it carries `patt.config.task-config` with a `# Data coupling`
section: the exception is documented rather than smoothed over, and the scorer is
told what to compare. Any *other* block that starts failing the mutability test is
a defect, not a second exception.
