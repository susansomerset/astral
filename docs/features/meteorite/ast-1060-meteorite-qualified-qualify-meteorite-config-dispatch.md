# AST-1060 — METEORITE_QUALIFIED + qualify_meteorite config/dispatch

**Linear:** [AST-1060](https://linear.app/astralcareermatch/issue/AST-1060/meteorite-qualified-qualify-meteorite-configdispatch-qualify-meteorite)
**Parent:** [AST-1058](https://linear.app/astralcareermatch/issue/AST-1058/qualify-meteorite) — Qualify Meteorite
**Publish ref:** `origin/sub/AST-1058/AST-1060-meteorite-qualified-qualify-meteorite-config-dispatch`

Registers **METEORITE_QUALIFIED** / **METEORITE_FAILED_QUALIFY** / **METEORITE_ERROR_QUALIFY**, updates UI manifests, reframes **METEORITE_NEW** as pre-AI entry, retargets meteorite `evaluate_jd` claim from **METEORITE_NEW** → **METEORITE_QUALIFIED**, and adds `TASK_CONFIG` + `agent_task` shell + meteorite `dispatch_task` row for `qualify_meteorite` claiming **METEORITE_NEW**. Does **not** own gazer Playwright ingest (AST-1061) or core/consult batch apply (AST-1062).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | New qualify states + UI; retarget GDL priors/`METEORITE_DISPATCH_TASKS` evaluate_jd trigger; `TASK_CONFIG["qualify_meteorite"]`; dispatch helper rules | utils |
| `data/admin/agent_task.json` | `qualify_meteorite` shell row (Ruth) | data/admin |

No `consult.py` / `meteorite.py` apply path, no gazer, no frontend TS, no `tests/` / bible (Betty after Code Complete).

## Stage 1: Qualify states, UI, GDL retarget, `qualify_meteorite` TASK_CONFIG + dispatch

**Done when:** Config imports with the three new states; GDL `evaluate_jd` meteorite dispatch claims **METEORITE_QUALIFIED**; `TASK_CONFIG["qualify_meteorite"]` and a `METEORITE_DISPATCH_TASKS` row claim **METEORITE_NEW**; Jobs In Review / Skipped manifests include the new states; non-meteorite qualify/`JOB_STATES` priors unchanged.

1. In `src/utils/config.py` `JOB_STATES`, **replace** the meteorite GDL block comment and entries so the chain is:

```python
    # AST-1052 / AST-1053 / AST-1058: parallel meteorite track (no CULTURE_READY hop).
    # METEORITE_NEW = pre-AI landing (create / gazer ingest). Ruth qualify_meteorite →
    # METEORITE_QUALIFIED (GDL entry). evaluate_jd claims METEORITE_QUALIFIED only (AST-1060).
    "METEORITE_NEW":                  {"prior_states": None},
    "METEORITE_QUALIFIED":            {"prior_states": ["METEORITE_NEW"]},
    "METEORITE_FAILED_QUALIFY":       {"prior_states": ["METEORITE_NEW"]},
    "METEORITE_ERROR_QUALIFY":        {"prior_states": ["METEORITE_NEW"]},
    "METEORITE_PASSED_JD":            {"prior_states": ["METEORITE_QUALIFIED"]},
    "METEORITE_FAILED_JD":            {"prior_states": ["METEORITE_QUALIFIED"]},
    "METEORITE_ERROR_EVALUATE_JD":    {"prior_states": ["METEORITE_QUALIFIED"]},
    "METEORITE_PASSED_DO":            {"prior_states": ["METEORITE_PASSED_JD"]},
    # … keep DO/GET/LIKE meteorite siblings exactly as today (priors unchanged beyond JD hop)
```

Keep **METEORITE_NEW** `prior_states: None` (create / ingest unrestricted entry). Do **not** remove or rename existing METEORITE_* GDL/LIKE states.

⚠️ **Decision — three qualify outcomes:** Pass = **METEORITE_QUALIFIED**; content/bogus/404 = **METEORITE_FAILED_QUALIFY** (parent AC6 / Jobs skipped); technical = **METEORITE_ERROR_QUALIFY** (mirrors `METEORITE_ERROR_EVALUATE_JD` naming + `ERROR_QUALIFY_JOB_LISTINGS` role). AST-1062 maps Ruth outcomes onto these three.

2. Update ordered Jobs UI lists in the same file:

- **`IN_REVIEW_STATES`:** insert `"METEORITE_QUALIFIED"` immediately after `"METEORITE_NEW"` (before `METEORITE_PASSED_JD`).
- **`JOBS_IN_REVIEW_UI_SECTIONS`:** after the `METEORITE_NEW` row, insert  
  `{"state": "METEORITE_QUALIFIED", "label": "Meteorite Qualified"}`.  
  Change the `METEORITE_NEW` label to `"Meteorite New (pre-AI)"`.
- **`SKIPPED_STATES`:** append `"METEORITE_FAILED_QUALIFY", "METEORITE_ERROR_QUALIFY"` next to the other meteorite fails (before or with the evaluate_jd fail pair is fine — both must appear exactly once).
- **`JOBS_SKIPPED_SECTION_ORDER`:** insert both near the FAILED_JOBLIST / ERROR_QUALIFY_JOB_LISTINGS cluster (after `METEORITE_ERROR_EVALUATE_JD` or before `FAILED_JOBLIST` — keep meteorite qualifies readable together).
- **`JOBS_SKIPPED_SECTION_LABELS`:**  
  `"METEORITE_FAILED_QUALIFY": "Meteorite Failed Qualify"`,  
  `"METEORITE_ERROR_QUALIFY": "Meteorite Error Qualify"`.
- Do **not** add grade-field maps for these states (no rubric grades until AST-1062 persists fields; same as bare `METEORITE_NEW` today).

3. Retarget meteorite GDL entry in `METEORITE_DISPATCH_TASKS`: change the `evaluate_jd` entry’s `"trigger_state"` from `"METEORITE_NEW"` to `"METEORITE_QUALIFIED"`. Keep `"score_floor": None` (ungated GDL entry, mirrors prior METEORITE_NEW / normal JD_READY).

⚠️ **Decision — do not mutate existing DB rows in this ticket:** `ensure_meteorite_dispatch_tasks` only **inserts** missing `(task_key, trigger_state)` pairs. After this change, provisioning adds `evaluate_jd` @ **METEORITE_QUALIFIED**; a stale `evaluate_jd` @ **METEORITE_NEW** row may remain until ops/admin clears it. That is acceptable for AST-1060 — do **not** add a one-shot migrator here. Document in Linear if Chuckles wants a cleanup task later.

4. Append a new first entry to `METEORITE_DISPATCH_TASKS` (before `evaluate_jd`):

```python
    {
        "task_key": "qualify_meteorite",
        "trigger_state": "METEORITE_NEW",
        "score_floor": None,
        "auto_mode": False,
        "batch_size": 30,
        "min_count": 1,
        "freq_hrs": 0,
    },
```

Existing `ensure_meteorite_dispatch_tasks` already seeds every `METEORITE_DISPATCH_TASKS` entry whose `task_key` is in `TASK_CONFIG` — no `dispatcher.py` body change required once Step 5 lands.

5. In `TASK_CONFIG`, immediately after `"qualify_job_listings"`, add:

```python
    # AST-1058 / AST-1060: Ruth meteorite qualify (pre-AI → METEORITE_QUALIFIED).
    # Same claim/batch shape as qualify_job_listings; apply wiring is AST-1062.
    "qualify_meteorite": {
        "response_format": "json",
        "output_type": "fields",
        "scored": False,
        "response_schema": {
            "jobs": {
                "type": "list",
                "required": True,
                "items_schema": {
                    "astral_job_id":   {"type": "str", "required": True},
                    "company_job_id":  {"type": "str", "required": True},  # external job UUID
                    "job_title":       {"type": "str", "required": True},
                    "job_link":        {"type": "str", "required": True},
                    "jd_text":         {"type": "str", "required": True},  # visible JD content
                },
            },
        },
        "fallback_batch_size": 30,
        "pass_state": "METEORITE_QUALIFIED",
        "fail_state": "METEORITE_FAILED_QUALIFY",
        "error_state": "METEORITE_ERROR_QUALIFY",
        "context_format": "qualify_meteorite_{index}",
        "entity_type": "job",
        "requires_candidate_key": True,
        "trigger_state": None,
        "agent_task": "qualify_meteorite",
    },
```

⚠️ **Decision — `scored: False` + `output_type: "fields"`:** Parent AC is enrichment (UUID/title/link/JD), not grade vectors. Do **not** reuse `grades_encoded_meta` / `joblist_rubric`. AST-1062 owns persist + transition; schema keys above are the contract.

⚠️ **Decision — do not edit `qualify_job_listings` TASK_CONFIG or normal `NEW`/`PASSED_JOBLIST` priors:** Non-meteorite path must stay byte-stable (parent AC7 smoke).

6. Wire dispatch defaults for the new task key:

- In `_dispatch_trigger_state_for_task_key`, add `if task_key == "qualify_meteorite": return "METEORITE_NEW"` (near the `qualify_job_listings` → `"NEW"` branch).
- In `_dispatch_entity_type_for_task_key`, add `"qualify_meteorite"` to the job-entity tuple that already lists `"qualify_job_listings", "evaluate_jd", …`.
- Add `"qualify_meteorite"` to `_DISPATCH_BATCH_CALL_MODE_ONE` (next to `"qualify_job_listings"`).

7. Do **not** edit `consult.py`, `agent.py`, `dispatcher.py` runners, `meteorite.py`, gazer, or frontend. Do **not** set `auto_mode: True`. Do **not** change `METEORITE_CONFIG["job_create_state"]` (stays **METEORITE_NEW**).

**Done when (recheck):** `JOB_STATES["METEORITE_PASSED_JD"]["prior_states"] == ["METEORITE_QUALIFIED"]`; `METEORITE_DISPATCH_TASKS` has `qualify_meteorite`@`METEORITE_NEW` and `evaluate_jd`@`METEORITE_QUALIFIED`; `TASK_CONFIG["qualify_meteorite"]["pass_state"] == "METEORITE_QUALIFIED"`; `_dispatch_trigger_state_for_task_key("qualify_meteorite") == "METEORITE_NEW"`; import/asserts on `METEORITE_DISPATCH_TASKS` / `JOB_STATES` pass; `python3 -m py_compile src/utils/config.py` succeeds.

## Stage 2: `agent_task.json` shell for `qualify_meteorite`

**Done when:** `data/admin/agent_task.json` has a `current: 1` row for `task_key == "qualify_meteorite"` (Ruth, Job Review grouping); JSON still parses as a flat-row array; prompts describe enrichment (UUID / title / link / visible JD) without inventing a new batch pattern.

1. Append one object to `data/admin/agent_task.json` (flat scalars only), modeled on the existing `qualify_job_listings` row:

| Field | Value |
|-------|-------|
| `task_key` | `qualify_meteorite` |
| `task_key_uuid` | new UUID4 string |
| `current` | `1` |
| `agent_id` | `college_intern_ruth` (same as `qualify_job_listings`) |
| `task_group_order` | `4000` |
| `task_group_name` | `Job Review` |
| `task_name` | `Qualify Meteorite` |
| `task_seq` | place after listing qualify (e.g. `2.5` or next free seq in that group) |
| `system_prompt` / `cache_prompt_b|c|d` / `nocache_prompt` / `run_next` | `""` |
| `updated_at` | ISO-ish UTC timestamp string |

2. **`user_prompt` / `cache_prompt` shell** (keep short; AST-1062 / future prompt polish may refine):

- Instruct Ruth that each item is a **meteorite** job already holding raw / visible text (email body, forward, or Playwright-fetched page text) — **not** a normal job-board listing row.
- Require a JSON jobs list matching `TASK_CONFIG["qualify_meteorite"]["response_schema"]` keys: `astral_job_id`, `company_job_id` (employer external job UUID for dedupe), `job_title`, `job_link` (primary URL), `jd_text` (authoritative visible JD).
- Success path assumes usable extract; unusable / 404 / bogus pages are a fail outcome for the apply layer (do not invent grade vectors).
- Do **not** copy the seven-step joblist grading / vector rubric from `qualify_job_listings` — this key is enrichment-only.

⚠️ **Decision — prompts only in `agent_task.json`:** Same as AST-1055; startup `apply_repo_admin_json` ships the row. No parallel `_taskprompts` file.

3. Do **not** hand-edit the live DB; do **not** invent consult routes.

**Done when (recheck):** `qualify_meteorite` present in the JSON array; `agent_id` is Ruth; prompts mention meteorite enrichment + the five schema fields; `python3 -c "import json; json.load(open('data/admin/agent_task.json'))"` succeeds.

## Out of scope (do not implement here)

- Gazer email → Playwright → create / dedupe (AST-1061).
- `qualify_meteorite` consult/core batch apply, Style D on apply, persist of UUID/title/link/JD (AST-1062).
- Editing non-meteorite `qualify_job_listings` behavior or prompts.
- Frontend React enums (manifest is config-driven).
- `tests/` / `docs/test-bible/**` (Betty after Code Complete).
- One-shot deletion of stale `evaluate_jd`@`METEORITE_NEW` dispatch rows.

## Self-Assessment

**Scope:** `Single-Component` — `config.py` state/dispatch/TASK_CONFIG + one `agent_task.json` row; no core apply / gazer / UI TS.

**Conf:** `high` — mirrors AST-1053/1054/1055 meteorite state + dispatch + agent_task shell patterns; retarget is a literal prior/`trigger_state` swap already named on the parent.

**Risk:** `Medium` — wrong prior retarget would leave `evaluate_jd` claiming unenriched **METEORITE_NEW** or block lawful GDL transitions; mitigated by explicit `JOB_STATES` + `METEORITE_DISPATCH_TASKS` edits and left `auto_mode: False` until AST-1062.

## Rules self-review

- **§2.1 / no-hardcoded-sets / config-source-of-truth:** All states, task keys, schema, dispatch triggers in config / repo agent_task JSON.
- **§2.6 / job-prior-states-enforced:** GDL outcomes only from **METEORITE_QUALIFIED**; qualify outcomes only from **METEORITE_NEW**.
- **§3.3 imports:** No new core↔UI edges; dispatcher already imports `METEORITE_DISPATCH_TASKS` / `TASK_CONFIG`.
- **In-scope only:** No gazer / consult apply / tests / bible.
