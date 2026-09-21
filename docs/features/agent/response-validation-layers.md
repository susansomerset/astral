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
