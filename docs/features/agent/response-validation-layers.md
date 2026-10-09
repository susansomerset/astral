# Agent response validation layers

Investigation plan — not a Linear child. Traces where a model answer is parsed, schema-checked, and then judged as product-good enough. Prompted by meteorite qualify failing `empty company_job_id` after schema already said the field was optional.

## What “validate” means here

Three different jobs share the word:

| Job | Question it answers | Failure looks like |
| --- | --- | --- |
| **Parse** | Is this bytes JSON / an envelope we can unwrap? | `do_task` `success: False`, whole chunk to `error_state` |
| **Schema** | Does the unwrapped payload match `TASK_CONFIG[task].response_schema` types / required keys? | same — envelope reject, no per-row apply |
| **Apply** | Is this row *good enough to graduate*? | per-row `fail_state` / `pass_state`; chunk still `success: True` |

`required: False` on a schema field only answers the middle question. Empty string `""` is a valid `str`. Apply can still fail the row.

## Pipeline (happy path, JSON task)

```
DeepSeek HTTP body
  → src/external/deepseek.py  send_to_deepseek
      hollow / max_tokens / json.loads (+ heal)
  → src/core/agent.py         do_task
      coerce types → envelope + response_schema → unwrap agent_payload
      (grades / confidence when the task has them)
  → src/core/consult.py       _run_batch_consult
      bind slot ids → process_fn per claimed job
  → src/core/tracker.py       initialize_job  (qualify_meteorite pass path only)
```

Anthropic is the same parse/heal contract (`src/external/anthropic.py` mirrors DeepSeek). Provider choice does not change schema or apply.

---

## Layer 0 — Instruction, not a gate

**Config:** `TASK_CONFIG[task_key]["response_schema"]`  
**Renderer:** `stringify_response_schema` in `src/utils/config.py`  
**Consumer:** prompt token `RESPONSE_SCHEMA` (`TOKEN_SOURCES`)

This inserts an *example envelope* into the agent_task prompt. It does not run at response time. `required` flags are not restated as “must be non-empty.” Optional string fields render as `"<company_job_id>"`.

Catalog copy in `agent_task` (Ruth’s TASK / SYSTEM) can tell her to omit unknown ids. That is also instruction, not a gate.

---

## Layer 1 — External provider (`src/external/deepseek.py`)

`send_to_deepseek` does **not** read `response_schema`. It only decides whether there is a usable JSON object.

| Check | Config / helper | On fail |
| --- | --- | --- |
| Call budget / HTTP timeout / balance refusal | `PROVIDER_CALL_BUDGET`, `PROVIDER_BALANCE_REFUSAL` | `success: False`, `failure_class` set |
| Hollow body (no stop, zero tokens, no text) | `PROVIDER_EMPTY_RESPONSE` + `is_unusable_provider_response` | `failure_class=provider_empty_response` |
| JSON `stop_reason == max_tokens` | hardcoded in send | `failure_class=max_tokens` — no heal |
| Extract text | `extract_api_response_text` (skips thinking blocks) | raise → parse fail |
| `json.loads` after fence strip | `_parse_json_response` | try `heal_agent_payload_envelope`, then `heal_json`, then encoded-grades wrap |
| `response_format` enum | `"text" \| "json" \| "python"` from TASK_CONFIG | ValueError |

Healing (`src/utils/formatting.py`) is liberal ingest: truncated `agent_payload` strings, messy JSON. It is not field-level business rules.

`do_task` sees this as `result.success`. False → consult never calls `process_fn`. For Pattern A batch (`_run_batch_consult`) the **whole claimed set** goes to `error_state` (or holds state on balance refusal).

---

## Layer 2 — Agent (`src/core/agent.py` `do_task`)

Statute in `docs/ASTRAL_CODE_RULES.md` §2.3: JSON tasks are validated here; core receives a shape or an error. The statute still says “Anthropic validates”; the code path is provider-agnostic after `send_to_*`.

Order after a successful send (JSON, non-encoded consult):

1. **Soft coerce** — `_coerce_schema_str_fields_from_list`  
   list-of-lines → `"\n".join`; int (not bool) → `str` (AST-1289). Schema types stay `str`.
2. **Envelope + schema** — `_validate_response_schema(parsed, schema, task_key)`  
   - Expects `{agent_performance, agent_payload}`. Legacy flat dict: both pointers fall back to `parsed`.  
   - `agent_performance.status == "failure"` → hop fail (`Agent failure: …`).  
   - Conversational tasks use `CONVERSATIONAL_PERFORMANCE_SCHEMA` (`concern` needs `admin_aside`).  
   - Then `_validate_schema_object_fields(payload, TASK_CONFIG schema)`.
3. **Task-specific extras (not meteorite qualify)**  
   draft-resume catalog check; `_validate_grade_confidence_in_payload`; `_validate_grades` vs `vectors`.
4. **Unwrap** — `parsed_response` becomes `agent_payload` so consult sees task fields only.

### What schema `required` actually means

`_validate_schema_object_fields`:

- `required and val is None` → `"Missing required field '…'"`
- `val is None` and not required → skip (omit / JSON `null` both OK)
- otherwise type / enum / nested `items_schema`

Empty string is **not** None. `company_job_id: ""` passes `required: False` and would also pass `required: True`.

`required: "when_task_success"` is a special case for some payloads; qualify_meteorite does not use it.

### qualify_meteorite schema (config)

`TASK_CONFIG["qualify_meteorite"]["response_schema"]["jobs"]["items_schema"]`:

| Field | required | Why |
| --- | --- | --- |
| `astral_job_id` | False | land-enrich / slot echo |
| `company_job_id` | False | AST-1127 — omit/null must reach UUID fallback |
| `job_title` | False | AST-1195 |
| `job_link` | False | AST-1195 |
| `jd_text` | **True** | presence only — length is apply |
| `employer_name` | False | |
| `company_stem` | False | AST-1494 |

Asserts at `config.py` ~1042 lock those False flags. Flipping `company_job_id` to `required: True` would **not** have failed this morning’s batch: Ruth returned `""`, not omit.

Encoded consult tasks skip this first schema pass (`rubric_encoded`), decode the pipe string, then schema-check the decoded shape. qualify_meteorite `output_type` is `"fields"` — no decode hop.

---

## Layer 3 — Consult apply (`src/core/consult.py`)

`_run_batch_consult` after `do_task` success:

1. `parsed["jobs"]` must exist (KeyError → not a schema miss; schema already required the list).
2. `_bind_response_jobs_to_claimed` — `"000"` / `"001"` → claimed UUIDs (AST-1076).
3. qualify_meteorite only: `_bind_response_jobs_by_job_link` (AST-1133). Empty links do nothing.
4. Missing claimed ids → per-row `error_state` / retry holding (`omitted from response`). Fabricated ids dropped.
5. **`process_fn(input_job, response_job, cfg)` per row** — this is where product gates live.

### qualify_meteorite `process` (the mandate you can see)

Reads knobs from the same TASK_CONFIG dict: `email_link_prefix`, `min_job_title_length`, `min_jd_chars`, `fail_state`, `pass_state`, `bot_blocked_state`.

Then **hardcoded** order:

1. Resolve `job_link`: Ruth `http` → input `http` → Ruth `email-` → else Ruth’s value (often `""`).  
   **No fallback to an input `email-` link.** Land currently stores `job_link=None` when meteorite `link` is not HTTP, so input is empty too.
2. `_resolve_company_job_id(ai, job_link)` — AI string wins; else UUID path segment from `job_link` via `TRACKER_CONFIG["uuid_path_segment_pattern"]`; else `""`.
3. Bot / challenge on stored JD or Ruth `jd_text` (`gazer._classify_jd`, signals on `TRACKER_CONFIG["jd_classifier"]`) → `BOT_BLOCKED`.
4. **If not `company_job_id` and `job_link` does not start with `email_link_prefix` → `empty company_job_id` → `METEORITE_FAILED_QUALIFY`.**
5. Else title length / jd length floors from config.
6. Pass → `tracker.initialize_job` then `pass_state`.

Chunk still counts as consult success: this morning `pass:1 fail:6 error:0`. Schema passed; apply failed six rows.

Title and JD floors are config-driven. The empty-id rule is **not** a schema `required` and **not** a named config gate — only the waiver prefix is.

Other Pattern A tasks have their own `process` (evaluate binary grades, etc.). `render_verdict` is a different hop: missing `grades` is a `ValueError` → technical fail, after agent schema already required them on encoded decode.

---

## Layer 4 — Tracker persist (`src/core/tracker.py` `initialize_job`)

Only reached on qualify **pass**.

- `_JOB_REQUIRED_COLUMN_FIELDS = {"job_title", "job_link"}` — keys must be **present** in `parsed_job`. Values may be `""`. `company_job_id` is optional at this layer (identity triple needs id+title to dedupe).
- Unique `(company, job_title, company_job_id)` collision deletes the current row; consult treats that as fail (`identity collision`).

This is persistence / identity, not “Ruth left a field blank.”

Land (`run_land_meteorite`) writes `company_job_id=None` and `job_link` only when meteorite `link` is HTTP. That is create policy (AST-1061 / AST-1119 boundaries), not response validation.

---

## Worked example — 2026-09-14 Somerset qualify

Batch `qualify_meteorite-7ff37eab-…`: 7 email meteorites, empty `meteorite.link`.

| Layer | What happened |
| --- | --- |
| 1 DeepSeek | JSON parsed; three RESPONSE chunks |
| 2 Schema | `company_job_id: ""`, `job_link: ""`, titles + `jd_text` present → hop success |
| 3 Bind | `"000"`/`"001"`/`"002"` → claimed UUIDs |
| 3 Apply | 6× `empty company_job_id` (no id, no UUID in link, link not `email-`) |
| 3 Apply | 1× pass — Ruth found `179378-1` in the Amazon body |

Ruth followed optional-id schema. Apply still demanded an id or an `email-` token she never emitted.

---

## Where the rules live (honest map)

| Rule | Lives in config? | Enforced where |
| --- | --- | --- |
| Field may be omitted / null | **Yes** — `response_schema.*.required` | `agent._validate_schema_object_fields` |
| Field type / enum | **Yes** — same schema | same |
| Envelope success/failure | **Yes** — `BASE_SCHEMA` / conversational schema | `agent._validate_response_schema` |
| Grade letters / vector set | **Yes** — `vectors`, `valid_grades` | `agent._validate_grades` |
| Confidence 0 vs 1–5 | **Yes** — multipliers; bounds in agent | `agent._validate_grade_confidence_*` |
| Hollow provider body | **Yes** — `PROVIDER_EMPTY_RESPONSE` | `llm_external` + send_to_* |
| Title / JD length floors | **Yes** — `min_job_title_length`, `min_jd_chars` | consult `process` |
| `email-` waiver | **Yes** — `email_link_prefix` | consult `process` (hardcoded `startswith`) |
| **Must populate `company_job_id` unless waived** | **No** | consult `process` literal |
| UUID fallback pattern | **Yes** — `TRACKER_CONFIG["uuid_path_segment_pattern"]` | `consult._resolve_company_job_id` |
| Bot interstitial | **Yes** — `jd_classifier.bot_signals` | consult + gazer classify |
| `job_title`/`job_link` keys on save | hardcoded sets in tracker | `initialize_job` |

`docs/ASTRAL_CODE_RULES.md` §2.3 stops at schema + grades. Apply gates are per-task `process` functions. That split is why optional schema + failing qualify can both be “correct.”

---

## Options (do not implement until you pick)

These are the plausible consolidations; they are not equivalent.

1. **Leave layers; fix land/apply for email.** Stamp `job_link = email-{source_id}` at land when there is no HTTP URL, and teach qualify’s link cascade to keep an input `email-` token when Ruth returns `""`. Schema stays optional. Matches AST-1197’s waiver as written.
2. **Move the empty-id rule into TASK_CONFIG** (e.g. a named apply-gate list consult reads). Same behavior, one place to look. Does not by itself qualify email rows with empty links.
3. **Tighten schema `company_job_id.required` to True.** Would **not** catch `""`. Would re-break AST-1127 omit/null + UUID-in-link. Wrong tool.
4. **Prompt-only: tell Ruth to emit `email-…` when there is no ATS id.** This morning 6/7 she returned empty anyway. Instruction layer is not a gate.
5. **Waive empty id whenever input `job_link` is empty.** Broad; would also pass gazed jobs that lost their URL.

Recommend talking through (1) vs (2) before code. (1) is the product hole; (2) is the “I wanted this in config.py” housekeeping.

---

## Bug: AST-2093 — batch-unique row index so every grade reply maps to its own job

Parent: AST-2012 (orphaned Bug mini-parent). Affects Layer 2 decode (`agent._decode_payload` pos → id) and Layer 3 bind for the encoded Do/Get/Like grade path.

### As-is

Somerset `meteorite_grade_get` batch `meteorite_grade_get-a4ec9af6…` claimed 27 jobs and ended `pass:4 fail:0 error:23`. Each ~20-job LLM call (`stop=end_turn`) produced one `job consult completed`. Every other claimed id was logged `omitted from response`, routed to `METEORITE_PASSED_DO_RETRY`, omitted again on the retry run, and landed in `METEORITE_FAILED_TECHNICAL_GET`. The Somerset alert subject's `M processed` counted retry-run entities a second time.

Row labels are chunk-local, and lone calls are always `000`:

- `consult._consult_scored_dispatch_batch_encoded` calls `_prep_live_content(..., position=len(eligible))`, which stamps `[index=NNN]: <jd>`. Its `assemble` then prefixes `NNN: ` again from `range(len(rows))`, so each row reads `000: [index=000]: …`.
- The dispatcher's parallel chunks (`_run_unified` → `_consult_chunk(ci, …)`) each restart at `000`.
- A one-entity grade run (per-job `_one(e)` path, or a chunk with a single leftover row) goes `run_consult_task` → `render_verdict` → `_prep_live_content(job, …)` with the default `position=0`. Every lone call is `[index=000]`.
- `grade_do` / `grade_get` / `grade_like` / `meteorite_like` prompts (`data/admin/agent_task.json`) say "zero-based row index (e.g. `000:`)". Alias rows `meteorite_grade_do` / `meteorite_grade_get` have empty prompts and inherit `grade_do` / `grade_get` via `master_task_key`.
- `agent._decode_payload` maps each line through `batch_entities[pos]` with no uniqueness check.

### To-be

Every entity in a claimed batch is sent with its own index, unique across the whole claim. The index is the entity's claimed position (zero-padded, at least 3 digits), stable across chunks and on single-entity calls (a lone row can be `024`). Each row carries exactly one label: `[index=NNN]: …`.

Decode resolves each reply line's leading index through an explicit index → entity map. Two failure cases are handled per entity:

- An index that appears on more than one line becomes one `decode_failures` entry for that index's entity. All of its lines are dropped.
- An index that isn't in the map is skipped with a warning. The entities it might have meant fall out as `omitted from response`.

Only those entities go to retry or error. Everything else still grades. Tasks that pass no map keep today's positional decode. The dispatch rollup counts each entity once across the runs of one dispatch.

### Repro

Fixture, no DB. The decode context is what `_run_batch_consult` builds for chunk 1 of a 40-job claim with `batch_size=20` (global indexes 20–39). Grade segment shape is `_GRADE_SEG` (2-char code + letter + digit):

```python
from src.core.agent import _decode_payload
jobs = [{"astral_job_id": f"J{i:02d}"} for i in range(20, 40)]
ctx = {"batch_entities": jobs, "vector_labels": {}}
payload = "\n".join(f"000|THA4|QQB3" for _ in jobs)   # model labels every line 000
_decode_payload("grade_get", "grades_encoded_notes", payload, ctx)
# today: 20 rows, all {"astral_job_id": "J20", ...}. J20 "completed", J21..J39 "omitted from response"
```

After the fix, with `ctx["batch_index_map"] = {20 + k: jobs[k] for k in range(20)}`:

- The same payload yields `{"jobs": []}` with no `decode_failures`, because `000` is unknown in this chunk. `_run_batch_consult` routes all 20 to retry as omitted, and none is mis-graded.
- With chunk 0's map (`{0..19}`), the payload yields one `decode_failures` row for index `000` / `J00` (duplicate index, 20 lines) and no `jobs`.
- A correct payload (`020|…` … `039|…`) yields 20 rows mapped `J20`…`J39`.

Assemble repro: chunk 1 currently renders `000: [index=000]: <jd>` for its first row. It must render `[index=020]: <jd>`.

### Root cause

Position is the only identity binding between a reply line and an entity. That position restarts at `000` per chunk and per lone call, and is printed twice. Decode trusts it blindly (`batch_entities[pos]`, last-wins by append order, no duplicate check). A model that echoes `000` on every line therefore collapses the whole chunk onto entity 0, and nothing in the reply can tell a correct grade from a mislabeled one.

Separately, `dispatcher._run_dispatch_loop` adds each run's `total_processed` into `accumulated`. A retry run that re-claims the same ids counts them again.

### Proposed change

**`src/core/dispatcher.py` — `_run_unified`**

1. Chunk path, in `_consult_chunk(ci, chunk_rows)`: pass `batch_index_offset=ci * chunk_sz` to `consult.run_consult_task`.
2. Full-batch non-chunk path: pass nothing (offset defaults to `0`, and claimed order is already global).
3. Per-entity path: before `_warm_then_gather`, build `idx_of = {id(e): i for i, e in enumerate(entities)}`. In `_one(e)`, pass `batch_index_offset=idx_of[id(e)]`.
4. Retry double count:
   - Immediately before `ctx["dispatch_partial"] = …`, compute `ids = [e.get("astral_job_id") or e.get("company_id") or e.get("astral_candidate_id") for e in entities]`.
   - Take `seen = ctx.setdefault("dispatch_seen_ids", set())` and `repeats = sum(1 for i in ids if i and i in seen)`, then `seen.update(i for i in ids if i)`.
   - On the normal return path, after `s` is fully summed, set `s["repeat_processed"] = min(repeats, s["total_processed"])`. The `min` only prevents a negative add when an outage zeroes a chunk. It is not a cap on work.
   - `repeat_processed` is not a `_SUMMARY_ZERO` key. The existing `for k in s` merges and the `**accumulated` ledger write never see it.

**`src/core/dispatcher.py` — `_run_dispatch_loop`**

5. After the `for k in accumulated` add, subtract `summary.get("repeat_processed", 0)` from `accumulated["total_processed"]`. The `summary.get("total_processed", 0) == 0` stop check keeps reading the raw per-run value, so loop termination is unchanged.

**`src/core/consult.py`**

6. `run_consult_task`: new kwarg `batch_index_offset: int = 0`. Forward it only in the grade branch: to `grade_do_batch` / `grade_get_batch` / `grade_like_batch` / `meteorite_like_batch`, to the alias call to `_consult_scored_dispatch_batch_encoded`, and to `render_verdict` in the `len(entities) == 1` branch as `batch_index=batch_index_offset`. Other branches ignore it.
7. `grade_do_batch` / `grade_get_batch` / `grade_like_batch` / `meteorite_like_batch`: accept `batch_index_offset: int = 0` and forward it.
8. `_consult_scored_dispatch_batch_encoded`: new kwarg `batch_index_offset: int = 0`.
   - The prep loop becomes `for pos, job in enumerate(jobs):` with `idx = batch_index_offset + pos`, the claimed position. Skipped rows leave gaps, which is fine because indexes only need to be unique.
   - Call `_prep_live_content(row, company, scoring_task_key=agent_tk, position=idx)`.
   - Keep a parallel `row_indexes: List[int]` appended next to `eligible` and `live_rows`.
   - `assemble` becomes `body = "\n".join(live_rows)`, which drops the `f"{i:03d}: "` prefix.
   - Pass `row_indexes=row_indexes` to `_run_batch_consult`.
9. `_prep_live_content`: the label stays `[index={position:03d}]: …`. `:03d` widens past 999 on its own, so no limit is added. Update the docstring: `position` is the batch-unique index, and decode maps it via `batch_index_map`.
10. `_run_batch_consult`: new kwarg `row_indexes: Optional[List[int]] = None`. When it is supplied, add `task_ctx["batch_index_map"] = dict(zip(row_indexes, jobs))`. `batch_entities` stays as-is for the positional consumers (`_normalize_rubric_task_response`, `_ensure_*_ids`, the admin replay). Callers that don't pass it (evaluate_jd, qualify, analysis assemblers) are unchanged.
11. `render_verdict`: new kwarg `batch_index: int = 0`. Pass `position=batch_index` to `_prep_live_content`, and add `"batch_index_map": {batch_index: job_row}` to `task_ctx`. CLI and other callers default to `0`, which behaves as today.

**`src/core/agent.py` — `_decode_payload`** (job/company branch only; the `grades_encoded_vet_meta` branch is untouched)

12. `index_map = (ctx or {}).get("batch_index_map")`. When it is truthy:
    - Run a pre-pass over `lines` that parses `int(fields[0])` with the same `ValueError` message on a bad field as today, and counts occurrences per index.
    - In the main loop, look up `ent = index_map.get(pos)`.
    - If `ent is None`: `logger.warning("%s skipped — index %s not in this batch\n  This line is not being graded", task_key, pos)`, then `continue`.
    - If the count for `pos` is greater than 1: on first sight only (track a `reported` set), append `{id_key: ent[id_key], "pos": pos, "reason": f"[{task_key}] duplicate row index {pos:03d} on {n} lines"}` to `decode_failures`, then `continue`.
13. When there is no map, keep the existing range check and set `ent = batch_entities[pos]`.
14. Replace the three `batch_entities[pos][id_key]` reads with `ent[id_key]`, and extend the docstring with the map rule.
15. `_run_batch_consult` already routes `decode_failures` per entity to `_transition_batch_consult_failures` (retry holding), and treats unmatched ids as `omitted from response`. No change is needed there.

**`data/admin/agent_task.json`** — the `cache_prompt` of `grade_do`, `grade_get`, `grade_like`, `meteorite_like`

16. Replace "Each JD row in --- CONTENT --- carries its own zero-based index; use the index as provided." with: "Each JD row in --- CONTENT --- carries its own unique index (`[index=NNN]`). Indexes are not sequential from 000 and may start anywhere; start each encoded line with that row's exact index."
17. Replace "The live task uses a zero-based row index (e.g. `000:`) in --- CONTENT ---, same pattern as evaluate. Your encoded line must start with that index as provided…" with: "The live task labels each row `[index=NNN]` in --- CONTENT --- (e.g. `[index=024]`). Your encoded line must start with that row's exact index (`024|…`). Never renumber and never reuse an index. Match indexes only; do not echo external job identifiers into the payload."
18. The edit is text only: no key, order, or other field changes. `grade_like` / `meteorite_like` are included because they share `_consult_scored_dispatch_batch_encoded` and carry the same `000:` sentence.

**Decisions (explicit, within declared scope):**

- `render_verdict` and the `run_consult_task` / wrapper plumbing are in `consult.py`. They carry the same "stamp batch-unique index + index map" change. Without them, a one-row tail chunk collides with chunk 0 at `000`.
- Line-prefix leniency (accepting `[index=024]` or `024:` as `fields[0]`) is not added. A bad prefix still raises as today.
- The timeout-partial fold (`dispatch_partial` on `INTERRUPTED`) still counts raw. Only normal-return runs dedupe.

### Blast radius

- **Hot-file overlap with AST-2015 / AST-2089 (in flight, Hedy):** those tickets change `do_task` envelope salvage and `_run_batch_consult` in `agent.py` / `consult.py`.
  - This diff touches `_run_batch_consult` in one kwarg plus one `task_ctx` line, and does not touch `do_task`.
  - The salvage decode (`consult._normalize_rubric_task_response` → `_decode_payload(…, ctx)`) receives `batch_index_map` automatically through the same `ctx`.
  - Expect a small textual conflict at `_run_batch_consult`'s signature and `task_ctx` line on refresh-ftr.
- `_decode_payload` other callers: `api_admin.py:1715` replay passes only `batch_entities`, so it stays positional and unchanged. The `grades_encoded_vet_meta` branch is untouched.
- `_bind_response_jobs_to_claimed`: decoded rows already carry real ids, so it is a no-op here (it only rewrites empty / digit echoes).
- Positional consumers of `batch_entities` (`_ensure_jobs_astral_ids`, `_ensure_companies_company_ids`, single-entity fills) are unchanged.
- Model behavior: prompts now show non-zero starting indexes. A model that still emits `000…` gets those rows retried rather than mis-graded. Expect more `omitted` / `decode:` retries until it complies, but no false grades.
- Ledger / UI: `dispatch_ledger.total_processed` and `entity_cost` (`total_cost / total_processed`) drop to unique counts on multi-run dispatches, so per-entity cost rises accordingly. The Somerset alert subject uses the same number.
- Tests likely asserting the old shape (Betty's call at fix-board):
  - assembled content `000: [index=000]:`
  - `render_verdict` content `[index=000]`
  - positional decode under a batch ctx
  - `total_processed` summed across runs

### What must still hold

- Rubric / grade semantics, `{letter}0 → {letter}1` normalisation (AST-2053), `X` must be `X0`, and duplicate vector codes still raising are all unchanged.
- Per-line malformed content still goes to `decode_failures`, not a batch kill (AST-1996). A clean row for the same entity still wins over a decode failure.
- Retry-holding routing for missing or bad entities is unchanged (AST-642 / AST-1839). Provider balance / rate-limit holds are unchanged (AST-1867 / AST-2010).
- `qualify_meteorite` link / order binds (AST-1076 / AST-1133) and the evaluate_jd / qualify assemblers are untouched.
- Tasks with no `batch_index_map` decode exactly as today.
- `do_task` RESPONSE dedupe suffix `_c{batch_chunk_index}` (AST-502) is unchanged.
- Chunk 0 still runs first for cache warm, and the rest still run in parallel.
- Dispatch loop termination (`0 processed` stop, `max_runs`, drain) behaves as today.
- Jobs already stranded in `METEORITE_FAILED_TECHNICAL_GET` by the reported run are not reset.


## Joan fix-board — AST-2093

[board-joan]  CANON: OK

AST-2093 board-joan done — CANON: OK.

**Rationale:** Read the `## Bug: AST-2093` plan-fix block on `origin/sub/AST-2012/AST-2093-grade-batch-unique-index` (As-is through What must still hold). No frozen **Canon Scope** on the orphaned AST-2012 mini-parent; triage is roster overlap only, not R1–R7.

**Overlap skim:** **`patt.entity.batch-processing`** — claim/process/release and `batch_id` as ledger join key are unchanged; deduping `total_processed` across retry runs in one dispatch loop aligns counts with unique entities worked, not a new claim shape. **`astral.seed.agent-tables-in-repo-json`** — `agent_task.json` `cache_prompt` text-only edits for grade tasks are normal repo-owned seed content. **`stat.logging.warning`** — unknown-index skips and duplicate-index handling fit per-item who/why (decode failures still route per entity; no new ERROR rollup). **`astral.agent.grade-vector-validation`** and encoded-grade semantics called out in **What must still hold** stay intact. **`patt.agent.response-decode`** / **`patt.consult.encoded-line`** exist in the taxonomy as decode-shape docs, not active rules that mandate chunk-local `000` or forbid `batch_index_map`; the fix tightens Layer 2 binding described in `response-validation-layers.md` without contradicting in-force statute text.

No directive needs amending and nothing here is an Archie-only precedent call (**ESCALATE** not warranted). If product wants a formal pattern for global batch row indexes later, that would be optional documentation outside this bug’s blast radius—not a gate for `make-fix`.

**Chuckles routing (orphaned bug-fix):** Betty TESTS: REVISE → sibling test gap child; Joan CANON: OK. AST-2093 proceeds to make-fix on product only.


## Radia review — AST-2093

[code-rubric]
**Ticket:** AST-2093
**Publish ref:** `2856ad2634ee00b03a434b22f38555d2ec8c6115` (`origin/sub/AST-2012/AST-2093-grade-batch-unique-index`)
**Diff base:** `origin/ftr/AST-2012-grade-batch-unique-index...origin/sub/AST-2012/AST-2093-grade-batch-unique-index` (6 files; product + plan doc + 5 `test_dispatcher.py` handoff nodes)
**Corpus:** `2d1b73da19cf1d14276e5c26f52b37aa8047d159`
**Overall:** CLEAN

## Fix-specific checks

**[bug-repro]** not applicable — clean board opt-out. `[board-betty] TESTS: REVISE` routed new coverage + `[bug-repro]` to **AST-2095**; **qa-fix (F4) did not run** on this ticket. No `[bug-repro]` tag in the fix diff (only pre-existing tags elsewhere in the repo).

**## What must still hold — OK** (traced against `response-validation-layers.md` § Bug: AST-2093)

| Item | Verdict |
|------|---------|
| Rubric / grade semantics, `{letter}0→{letter}1`, `X`→`X0`, duplicate vector codes still raise | Unchanged decode body after `ent` resolution (`agent.py` job/company branch). |
| Per-line malformed → `decode_failures`, not batch kill; clean row wins | Same `decode_failures` append paths; now use `ent[id_key]`. |
| Retry-holding / provider holds | No edits to transition or hold paths. |
| `qualify_meteorite` / evaluate_jd / qualify assemblers | Out of diff. |
| No `batch_index_map` → positional decode | `elif pos < 0 or pos >= len(batch_entities)` branch preserved. |
| `do_task` `_c{batch_chunk_index}` dedupe (AST-502) | `batch_chunk_index` still forwarded on chunk path only. |
| Chunk 0 warm, then parallel tails | Chunk loop structure unchanged; only `batch_index_offset=ci * chunk_sz` added. |
| Loop termination (`0 processed`, `max_runs`, drain) | Stop still uses raw `summary.get("total_processed", 0)`; dedupe applies only to `accumulated["total_processed"]`. |
| Stranded `METEORITE_FAILED_TECHNICAL_GET` jobs not reset | No migration/reset code. |

## Canon scores

(no frozen Canon Scope / directive ids on AST-2093 or orphaned AST-2012 mini-parent — **zero ids to score**; `[board-joan] CANON: OK` was overlap triage only, not per-directive plan-stage grades)

## Column diff vs plan stage

`no plan-stage scores attached` (no F3 `validate-plan` fix-mode column; Joan fix-board narrative only)

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Sibling test gap (AST-2095):** Betty’s REVISE list (`batch_index_map`, assemble shape, decode repro, `repeat_processed` dedupe) is **not** on this branch by design; UT should not treat missing those tests as a blocker on AST-2093.
- **Sibling test carry:** `tests/component/core/test_dispatcher.py` changes (`6a2bc960f` / Betty `merge-tests`) are **this ticket’s** qa-handoff alignment for `repeat_processed` + `batch_index_offset` — not AST-2095 product scope.
- **Hot-file overlap:** Same files as in-flight AST-2015 / AST-2089; this diff stays narrow (signature + one `task_ctx` line in `_run_batch_consult`). Expect textual conflict on refresh-ftr — coordinate merge order, not a defect in this fix.
- **Hedy qa-handoff note:** Alternative of carrying `repeat_processed` via `ctx` instead of `_run_unified` return was raised; **implementation matches approved plan** (return dict + loop subtract). No action unless Susan wants the alternate shape before UT.

## What's solid

- Plan steps 1–18 land as described: global indexes via `batch_index_offset`, single `[index=NNN]` labels (no `NNN: ` prefix), `batch_index_map` in decode ctx, map-aware `_decode_payload` (unknown skip + duplicate → one `decode_failures`), prompt text in four grade cache_prompt rows, `dispatch_seen_ids` / `repeat_processed` dedupe without polluting ledger keys.
- Full-batch non-chunk path correctly relies on default `batch_index_offset=0` (global claim order).
- Acceptance criteria in Linear description are marked met and match the diff.

## Chuckles — post-review branching

| Gate | Parent shape |
|------|----------------|
| **PROCEED** (clean, C7 complete) | **Normal** (parent AST-2012 not Done; `ftr/AST-2012-grade-batch-unique-index` base) → **Review Posted** → `do-all-the-things` §3h clean-review shortcut → **User Testing**; `resolve-child` **skipped**. |

(Plan text calls AST-2012 an “orphaned Bug mini-parent” for **documentation/intake**; spawn prompt correctly uses **ftr**, not ORPHANED→`dev` merge.)

context_tokens≈28000
