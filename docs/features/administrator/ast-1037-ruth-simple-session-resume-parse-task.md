# AST-1037 — Ruth simple session-resume parse task

**Linear:** [AST-1037](https://linear.app/astralcareermatch/issue/AST-1037/ruth-simple-session-resume-parse-task-simple-resume-parse-function)  
**Parent:** [AST-1036](https://linear.app/astralcareermatch/issue/AST-1036/simple-resume-parse-function) — Simple Resume Parse function  
**Publish ref:** `sub/AST-1036/AST-1037-ruth-simple-session-resume-parse-task`

Add a dedicated Ruth (Little) agent task and matching `TASK_CONFIG` entry whose only job is paste→JSON mechanical field mapping for the Admin Session Resume Paste contract. Seed the repo `agent_task` row so Manage Tasks / startup apply pick it up. Do **not** wire `run_session_resume_parse` / Admin parse (sibling **AST-1038**). Do **not** change Judith `craft_resume_base` persona, prompts, or candidate craft path.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extract shared craft-resume response schema constant; add `TASK_CONFIG["simple_resume_parse"]` with identical schema and session-oriented meta | utils |
| `data/admin/agent_task.json` | Add current `simple_resume_parse` row (`college_intern_ruth`, mechanical prompt, paste-faithful rules) | data |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Byte-identical copy of repo `agent_task.json` after the new row (AST-786 seed gate) | docs |
| `src/core/agent.py` | Apply `normalize_craft_resume_base_agent_payload` for `simple_resume_parse` as well as `craft_resume_base` (same JSON shape before schema validation) | core |

**No changes expected:** `src/core/candidate.py` (`run_session_resume_parse`, `parse_candidate_resume`, Judith craft path), `src/ui/api/api_admin.py`, React Session Resume Paste / Open HTML, `data/admin/agent.json` (Ruth already exists), Judith `craft_resume_base` `agent_task` row.

## Stage 1: Shared schema + `TASK_CONFIG["simple_resume_parse"]`

**Done when:** `TASK_CONFIG` exposes `simple_resume_parse` with the same response field set as `craft_resume_base`, keyed from one shared schema constant; `craft_resume_base` behavior/meta unchanged except the schema dict is referenced via that constant.

1. In `src/utils/config.py`, immediately above the `TASK_CONFIG = {` assignment (after `_RESUME_ARTIFACT_HOP_TASK_KEYS`), introduce a module-level constant named `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA` whose value is **exactly** the current `craft_resume_base["response_schema"]` dict body (same keys, types, required flags, and `experience: _EXPERIENCE_JOB_ARRAY_FIELD`).

2. Change `TASK_CONFIG["craft_resume_base"]["response_schema"]` to reference `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA` (no field edits; no meta edits — keep `response_format`, `context_format`, `entity_type`, `requires_candidate_key`, `trigger_state` as they are today).

3. Insert a new `TASK_CONFIG` entry **immediately after** `"craft_resume_base"`:

```python
"simple_resume_parse": {
    "response_schema": _CRAFT_RESUME_BASE_RESPONSE_SCHEMA,
    "response_format": "json",
    "context_format": "simple_resume_parse_{index}",
    "entity_type": None,
    "requires_candidate_key": False,
    "trigger_state": None,
},
```

⚠️ **Decision:** `task_key` is **`simple_resume_parse`** (matches epic “Simple Resume Parse function”). Sibling **AST-1038** will call this key from `run_session_resume_parse`.

⚠️ **Decision:** `requires_candidate_key: False` — this task is for the Admin session sentinel path (no candidate bind). Callers still may pass synthetic `ctx.candidate_data` for token resolution; they are not required to supply `astral_candidate_key`. Judith `craft_resume_base` stays `requires_candidate_key: True`.

⚠️ **Decision:** Share one schema object with `craft_resume_base` so the session paste / Open HTML contract cannot drift between the two catalog keys (§1.3 DRY / §2.1).

## Stage 2: Repo `agent_task` seed + AST-756 fixture sync

**Done when:** `data/admin/agent_task.json` contains a current `simple_resume_parse` row for Ruth; `docs/uat-fixtures/AST-756/expected-agent_task.json` is byte-identical to the repo file; Judith `craft_resume_base` row is unchanged.

1. In `data/admin/agent_task.json`, append one new object (keep existing rows untouched) with these fields:

| Field | Value |
|-------|--------|
| `task_key_uuid` | `046ffb1c-9708-49af-9380-56d85136066b` |
| `task_key` | `simple_resume_parse` |
| `current` | `1` |
| `agent_id` | `college_intern_ruth` |
| `run_next` | `""` |
| `system_prompt` | `""` |
| `cache_prompt_b` / `c` / `d` | `""` |
| `task_group_order` | `"2000"` |
| `task_group_name` | `Candidate Artifacts` |
| `task_seq` | `6` |
| `task_name` | `Simple Resume Parse` |
| `updated_at` | ISO UTC timestamp at edit time |

2. Write **`user_prompt`** (short, Ruth-addressed) that states: map the pasted resume text into the JSON schema only; no rewrite, enrichment, LinkedIn synthesis, or “improve the resume”; respond with valid JSON only (no markdown fences / preamble).

3. Write **`cache_prompt`** as the mechanical instruction block. It **must** include all of the following paste-faithful rules (lift wording from the current `craft_resume_base` `cache_prompt` where those rules already live — do not invent new markers):

   - Preserve typography digraphs `__` and `~~` literally in every section string (including nested experience fields); do not expand/replace them (HTML builder expands later).
   - `core_competencies` (and `prior_experience` when present): single string; separators are `•` / paste forms such as `__•__` — **never** `|` pipes.
   - Specialty / keyword / focus lines → `candidate_tagline`, **not** folded into `candidate_title`.
   - When the paste has a `<no bullet>…` role lead, copy that line into `accomplishments` **including** the literal `<no bullet>` prefix; do not invent the prefix when absent.
   - Field inventory matches the shared schema: `resume_structure`, `candidate_name`, `candidate_title`, `candidate_contact_detail`, optional `candidate_tagline`, `professional_summary`, `core_competencies`, `experience` (job array), optional `prior_experience`, optional `education_certifications`, optional `technical_skills`.
   - For `resume_structure`: if the paste does not imply a custom catalog, return the default structure shape the session path already uses (same keys the craft-base prompt expects) — do not invent unrelated section ids.
   - Explicitly **forbid** synthesis behaviors that belong to Judith craft-base: do not blend LinkedIn/bio/backstory; do not invent competencies, roles, or taglines; empty string / omit optional fields when the paste has no material.

4. Write **`nocache_prompt`** as:

```text
RESUME PASTE TEXT:
{$STARTING_RESUME_TEXT}
```

(Callers / sibling wire pass `starting_resume_text` via synthetic `ctx` the same way session parse already does for craft-base; `live_content` may also carry the paste — prompt truth is the nocache block.)

5. Sync the UAT fixture byte-for-byte:

```bash
cp data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json
cmp -s data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json && echo OK
```

⚠️ **Decision:** Group under **Candidate Artifacts** / order `2000` / seq `6` (sits next to `craft_resume_base` seq `5`) so Manage Tasks shows the pair together without inventing a new task group.

## Stage 3: `do_task` normalize hook for the new key

**Done when:** Both `agent.py` sites that special-case `task_key == "craft_resume_base"` before schema validation also run `normalize_craft_resume_base_agent_payload` when `task_key == "simple_resume_parse"`.

1. In `src/core/agent.py`, find every occurrence of:

```python
if task_key == "craft_resume_base":
    from src.core.candidate import normalize_craft_resume_base_agent_payload
    normalize_craft_resume_base_agent_payload(parsed)
```

(There are two today — sync + async validation paths around the craft-base normalize calls.)

2. Change each condition to:

```python
if task_key in ("craft_resume_base", "simple_resume_parse"):
```

Keep the same import and function call. Do **not** rename `normalize_craft_resume_base_agent_payload` in this ticket.

⚠️ **Decision:** This is catalog usability for the shared JSON shape, **not** Admin Session Resume Parse wiring. `run_session_resume_parse` still calls `craft_resume_base` until **AST-1038**.

## Stage 4: Compile check (plan-owned files only)

**Done when:** Touched Python modules compile; no edits under `tests/` (Betty owns the test tree).

1. From the epic worktree root:

```bash
python3 -m compileall -q src/utils/config.py src/core/agent.py
```

2. Confirm `craft_resume_base` still present in `TASK_CONFIG` and that `simple_resume_parse` is listed via a one-liner import check (venv if needed):

```bash
python3 -c "from src.utils import config as c; assert 'simple_resume_parse' in c.TASK_CONFIG; assert c.TASK_CONFIG['simple_resume_parse']['response_schema'] is c.TASK_CONFIG['craft_resume_base']['response_schema']"
```

## Self-Assessment

**Scope:** `Single-Component` — utils `TASK_CONFIG` + repo `agent_task` seed/fixture + a two-line `agent.py` normalize gate; no Admin route or Judith craft path edits.

**Conf:** `high` — reuses the existing craft-base response contract, Ruth agent row, AST-786 fixture sync pattern, and the established normalize hook; sibling owns the parse wire.

**Risk:** `low` — new catalog key is unused until AST-1038; shared schema reference cannot silently diverge; Judith `craft_resume_base` prompts and meta stay put.

## Code Rules check

- **§1.1 / in-scope-only:** No Admin wire, no Open HTML, no Judith prompt edits.
- **§1.3 DRY:** One `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA` shared by both task keys; normalize function reused.
- **§1.4 / no-hardcoded-sets:** Task key lives in `TASK_CONFIG` + `agent_task` seed — no new inline frozensets for membership.
- **§2.1 config source of truth:** Schema and task meta in `config.py`; prompts in `agent_task` seed.
- **§2.2 / do-task delegation:** Task is only reachable via `do_task` once a caller (sibling) invokes it — no new direct LLM calls.
- **§3.3 imports:** `agent.py` keeps the existing lazy import of `normalize_craft_resume_base_agent_payload`.
