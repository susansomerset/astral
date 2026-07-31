# AST-1089 — Ruth little-brain meteorite email parse task

**Linear:** [AST-1089](https://linear.app/astralcareermatch/issue/AST-1089/ruth-little-brain-meteorite-email-parse-task-add-gaze-email-as-a)
**Parent:** [AST-1087](https://linear.app/astralcareermatch/issue/AST-1087/add-gaze-email-as-a-dispatch-task) — Add gaze_email as a dispatch task
**Publish ref:** `origin/sub/AST-1087/AST-1089-ruth-little-brain-meteorite-email-parse-task`

Register Ruth (Little) `TASK_CONFIG` + repo `agent_task` for **`parse_meteorite_email`**: accept email HTML (and related shape inputs) and return meteorite job links/metadata and/or a likely JD link + content for the subject+body path. Config owns the task-key and parse-mode literals. **`requires_candidate_key: True`** so callers must supply the bound candidate’s API key via `ctx`. Does **not** own gaze_email dispatch shell / Gmail mutate (AST-1088), does **not** scrape URLs / create jobs / archive (AST-1090).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `TASK_CONFIG["parse_meteorite_email"]`; add `METEORITE_EMAIL_PARSE_CONFIG` (task key + parse-mode literals); inventory comment | utils |
| `data/admin/agent_task.json` | Add current Ruth `parse_meteorite_email` row (prompts + Job Review grouping) | data/admin |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Byte-identical copy of repo `agent_task.json` after the new row (AST-786 seed gate) | docs |

**No changes expected:** `src/core/consult.py`, `src/core/agent.py`, `src/core/dispatcher.py`, `src/core/gazer.py`, `src/core/inbox.py`, `src/core/meteorite.py`, Gmail external, frontend, `tests/` / bible (Betty after Code Complete). Do **not** add a `dispatch_task` / `METEORITE_DISPATCH_TASKS` row for this key.

## Stage 1: `METEORITE_EMAIL_PARSE_CONFIG` + `TASK_CONFIG["parse_meteorite_email"]`

**Done when:** Config imports expose `METEORITE_EMAIL_PARSE_CONFIG["task_key"] == "parse_meteorite_email"` and that key exists in `TASK_CONFIG` with the response schema / meta below; `requires_candidate_key is True`; no dispatch trigger / pass_state wiring; `python3 -m py_compile src/utils/config.py` succeeds.

1. In `src/utils/config.py`, update the top-of-file config inventory comment block: add one line for `METEORITE_EMAIL_PARSE_CONFIG` next to the meteorite / email ingest bullets (Ruth email-HTML parse task key + parse-mode literals for gaze_email / AST-1089).

2. Immediately after the existing `METEORITE_EMAIL_INGEST_CONFIG` block (and its surrounding comments; before `METEORITE_DISPATCH_TASKS`), add:

```python
# AST-1087 / AST-1089: Ruth little-brain parse of bound meteorite email HTML.
# Callers (AST-1090 gaze_email runner) pass live_content shaped per parse_modes and
# must supply ctx with the bound candidate’s candidate_api_key (requires_candidate_key).
METEORITE_EMAIL_PARSE_CONFIG = {
    "task_key": "parse_meteorite_email",
    # live_content first line: "PARSE_MODE: <mode>" — see Stage 2 prompts.
    "parse_modes": ("html_links", "subject_body"),
}
```

3. Immediately after that dict, assert the task key will exist once `TASK_CONFIG` is defined — **or** place the assert after `TASK_CONFIG` is fully assigned (same pattern as other late `assert … in TASK_CONFIG` checks). Prefer a late assert near other task-key asserts:

```python
assert METEORITE_EMAIL_PARSE_CONFIG["task_key"] in TASK_CONFIG
assert set(METEORITE_EMAIL_PARSE_CONFIG["parse_modes"]) == {"html_links", "subject_body"}
```

Do **not** invent additional modes. Do **not** put Astral inbox account address or unbound retention days here (AST-1088).

4. In `TASK_CONFIG`, immediately after the `"qualify_meteorite"` block, add:

```python
    # AST-1087 / AST-1089: Ruth parse of bound meteorite email HTML (not a dispatch claim task).
    # AST-1090 calls do_task with METEORITE_EMAIL_PARSE_CONFIG["task_key"] + candidate ctx.
    "parse_meteorite_email": {
        "response_format": "json",
        "output_type": "fields",
        "scored": False,
        "response_schema": {
            "parse_mode": {"type": "str", "required": True},
            "jobs": {
                "type": "list",
                "required": True,
                "items_schema": {
                    "job_link": {"type": "str", "required": True},
                    "job_title": {"type": "str", "required": False},
                    "metadata": {"type": "str", "required": False},
                },
            },
            "jd_link": {"type": "str", "required": False},
            "content_text": {"type": "str", "required": False},
        },
        "context_format": "parse_meteorite_email_{index}",
        "entity_type": None,
        "requires_candidate_key": True,
        "trigger_state": None,
        "agent_task": "parse_meteorite_email",
    },
```

⚠️ **Decision — task key `parse_meteorite_email`:** Matches the Ruth “meteorite email parse” slice (parallel to `qualify_meteorite` / `simple_resume_parse` naming). AST-1090 must call `METEORITE_EMAIL_PARSE_CONFIG["task_key"]` (or this literal via that config) — do not invent a second catalog key.

⚠️ **Decision — one task, two parse modes:** Parent Functional scope needs (a) pure-HTML → multi job links/metadata and (b) subject+body → content + optional likely JD link. One Ruth task with `parse_mode` in schema + live_content avoids duplicate prompts and keeps sibling #3 on a single `do_task` call site.

⚠️ **Decision — unified response schema:**
- **`html_links`:** populate `jobs` (one item per meteorite job URL found); set `parse_mode` to `html_links`; leave `jd_link` / `content_text` empty string or omit (optional fields).
- **`subject_body`:** set `parse_mode` to `subject_body`; put usable email subject+body text into `content_text`; put the single most likely job-description URL into `jd_link` when present (else omit / empty); `jobs` may be `[]` or a one-element list mirroring `jd_link` — prefer `jobs: []` when only `jd_link`/`content_text` apply so the runner does not double-scrape.
- Do **not** invent grade vectors, `astral_job_id`, or qualify fields — this is pre-create parse only.

⚠️ **Decision — `requires_candidate_key: True`:** Parent AC6 / Boundaries — Ruth invocations for bound mail use **that candidate’s** API key. `do_task` reads `ctx["candidate_api_key"]` when this flag is set (see `src/core/agent.py`). Session-style synthetic ctx without a key is **not** a valid caller for this task.

⚠️ **Decision — not a dispatch claim task:** `entity_type: None`, `trigger_state: None`, no `pass_state` / `fail_state` / `error_state`, do **not** add to `METEORITE_DISPATCH_TASKS`, `_DISPATCH_BATCH_CALL_MODE_ONE`, or `_dispatch_trigger_state_for_task_key`. The parent `gaze_email` row is AST-1088; the runner that calls this parse is AST-1090.

⚠️ **Decision — `scored: False` + `output_type: "fields"`:** Same pattern as `qualify_meteorite` — structured extract, not grades-encoded.

5. Do **not** edit `agent.py` normalize gates, consult routes, or dispatcher. Do **not** add Gmail / retention / account keys.

**Done when (recheck):**

```bash
python3 -c "from src.utils import config as c; assert c.METEORITE_EMAIL_PARSE_CONFIG['task_key']=='parse_meteorite_email'; t=c.TASK_CONFIG['parse_meteorite_email']; assert t['requires_candidate_key'] is True; assert t['entity_type'] is None; assert t['agent_task']=='parse_meteorite_email'; assert set(c.METEORITE_EMAIL_PARSE_CONFIG['parse_modes'])=={'html_links','subject_body'}"
python3 -m py_compile src/utils/config.py
```

## Stage 2: Repo `agent_task.json` Ruth row + AST-756 fixture sync

**Done when:** `data/admin/agent_task.json` has a `current: 1` row for `task_key == "parse_meteorite_email"` (`college_intern_ruth`); prompts document both parse modes and the response schema; `docs/uat-fixtures/AST-756/expected-agent_task.json` is byte-identical to the repo file; JSON still parses as a flat-row array.

1. Append one object to `data/admin/agent_task.json` (flat scalars only — no nested JSON objects/arrays as field values), modeled on the existing `qualify_meteorite` / `simple_resume_parse` Ruth rows:

| Field | Value |
|-------|--------|
| `task_key_uuid` | new random UUID4 string |
| `task_key` | `parse_meteorite_email` |
| `current` | `1` |
| `agent_id` | `college_intern_ruth` |
| `task_group_order` | `"4000"` |
| `task_group_name` | `Job Review` |
| `task_seq` | place near meteorite qualify (e.g. `2.4` or next free seq before `qualify_meteorite`’s `2.5`) |
| `task_name` | `Parse Meteorite Email` |
| `system_prompt` / `cache_prompt_b` / `c` / `d` / `nocache_prompt` / `run_next` | `""` |
| `updated_at` | current UTC `YYYY-MM-DD HH:MM:SS` (or ISO-ish UTC string matching neighboring rows) |

2. **`user_prompt`** (short, Ruth-addressed): parse the email CONTENT per `PARSE_MODE`; return JSON matching the schema (`parse_mode`, `jobs`, optional `jd_link` / `content_text`); no scrape, no inventing URLs that are not in the HTML; no grade vectors.

3. **`cache_prompt`** must include all of the following (concrete instruction block):

- This is a **meteorite email parse** for a bound candidate’s inbound mail — mechanical extract, not qualify / grade / rewrite.
- Live CONTENT always starts with a line `PARSE_MODE: html_links` or `PARSE_MODE: subject_body` (literals from `METEORITE_EMAIL_PARSE_CONFIG["parse_modes"]`). Echo that value into response `parse_mode`.
- **`html_links`:** HTML body is the job source (often no useful subject). Extract every distinct http(s) meteorite **job** link worth scraping as its own JD. Skip obvious non-job noise (unsubscribe, mailto, tracking) when clearly not a job posting. For each kept link return `{job_link, job_title?, metadata?}` in `jobs`. Prefer empty `jd_link` / `content_text`.
- **`subject_body`:** CONTENT includes a `SUBJECT:` line and HTML/body after. Return `content_text` = usable subject + body text the runner may use as JD text when no link exists. If the message includes one likely job-description URL, set `jd_link` to that URL; otherwise omit/empty. Prefer `jobs: []` on this mode (runner uses `jd_link` / `content_text`).
- Always return valid JSON only (no markdown fences). Do not invent employer culture, company sites, or links absent from the email HTML.
- Do **not** copy `qualify_meteorite`’s `astral_job_id` / `company_job_id` / `jd_text` enrichment contract — create/scrape/dedupe belong to AST-1090.

⚠️ **Decision — prompts only in `agent_task.json`:** Same as AST-1037 / AST-1055 / AST-1060; startup `apply_repo_admin_json` ships the row. No parallel `_taskprompts` file. Do **not** hand-edit the live DB.

⚠️ **Decision — live_content contract for AST-1090 (document in prompts, not code here):**

```text
PARSE_MODE: html_links

<html>…email body…</html>
```

```text
PARSE_MODE: subject_body
SUBJECT: <subject text>

<html>…email body…</html>
```

Caller builds that string, then:

```python
await do_task(
    task_key=METEORITE_EMAIL_PARSE_CONFIG["task_key"],
    live_content=live,
    index=<message_id or candidate_id>,
    ctx=<candidate row with candidate_api_key>,
    debug=debug,
)
```

This ticket does **not** implement that call site.

4. Sync the UAT fixture byte-for-byte:

```bash
cp data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json
cmp -s data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json && echo OK
python3 -c "import json; json.load(open('data/admin/agent_task.json')); assert any(r.get('task_key')=='parse_meteorite_email' for r in json.load(open('data/admin/agent_task.json')))"
```

**Done when (recheck):** both JSON files identical; Ruth row present; `agent_id` is `college_intern_ruth`; `cache_prompt` mentions both `html_links` and `subject_body` and forbids inventing URLs.

## Out of scope (do not implement here)

- `gaze_email` `TASK_CONFIG` / null-`candidate_id` dispatch_task / Gmail archive+trash / Astral account + retention config (AST-1088).
- Core runner: bind, shape routing, Playwright scrape, per-candidate dedupe, `create_meteorite_job` / **METEORITE_NEW**, mailbox archive/trash, Style D on the runner (AST-1090).
- Calling `do_task` from gazer/inbox/dispatcher in this ticket.
- Editing `qualify_meteorite` / `simple_resume_parse` / Manage Email Create paths.
- `tests/` / `docs/test-bible/**` (Betty after Code Complete).

## Self-Assessment

**Scope:** `Single-Component` — `config.py` TASK_CONFIG + named parse config block, one Ruth `agent_task.json` row, AST-756 fixture sync; no core runner / Gmail / dispatch shell.

**Conf:** `high` — mirrors AST-1037 (Ruth TASK_CONFIG + agent_task seed) and AST-1060 (meteorite Ruth fields task); API-key contract is the existing `requires_candidate_key` + `ctx["candidate_api_key"]` path in `do_task`.

**Risk:** `low` — catalog-only until AST-1090 calls it; wrong schema would block the runner, not mutate mailbox or jobs in this ticket. Mitigation: mode/schema spelled literally for Joan + sibling handoff.

## Code rules self-review

- **§1.3 DRY:** One task + shared schema for both email shapes; no duplicate Ruth keys.
- **§1.4 / no-hardcoded-sets:** Task key and parse-mode strings live in `METEORITE_EMAIL_PARSE_CONFIG` / `TASK_CONFIG` only; prompts reference those literals.
- **§2.1 / config-source-of-truth:** Parse task key + modes in named config; prompts in repo `agent_task.json`.
- **§2.1 / secrets-and-env-specific-from-environ:** No Gmail secrets here; candidate API key remains on candidate row / environ-backed crypto — consumed at call time via `requires_candidate_key`.
- **§2.4 / §2.6:** No batch claim / state machine on this key (not a dispatch task).
- **§3.3 imports:** No new cross-layer imports in this ticket.
- **§3.5 naming:** `parse_meteorite_email` / `METEORITE_EMAIL_PARSE_CONFIG` match meteorite naming.
- **in-scope-only:** Explicitly excludes AST-1088 shell and AST-1090 runner.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1087/AST-1089-ruth-little-brain-meteorite-email-parse-task`
**Plan path:** `docs/features/meteorite/ast-1089-ruth-little-brain-meteorite-email-parse-task.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `66edd249` | `METEORITE_EMAIL_PARSE_CONFIG` + `TASK_CONFIG["parse_meteorite_email"]` |
| 2 | `8d6eefe7` | Ruth `agent_task.json` + AST-756 fixture (+ inventory comment) |

**Tip:** `8d6eefe7a8bd998190d000f8cccd43723b6ef1db` on `origin/sub/AST-1087/AST-1089-ruth-little-brain-meteorite-email-parse-task`

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1089
**Publish ref tip (at review):** `1ae256abc40f6df55a8e32985026d48c238c49ca`
**Overall:** FIX-NOW

### What’s solid

- Stage 1–2 Ruth slice matches plan: `METEORITE_EMAIL_PARSE_CONFIG`, `TASK_CONFIG["parse_meteorite_email"]` with `requires_candidate_key: True`, Ruth `agent_task` row, AST-756 fixture byte-identical.
- Parse modes / schema / prompts align with Decisions; not added to `METEORITE_DISPATCH_TASKS`.
- Betty `test` + single `merge-tests` SHA on the sub.

### Issues

**fix-now:** `src/utils/config.py` `dispatch_task_admin_defaults` early-return references `GAZE_EMAIL_CONFIG["task_key"]` but **`GAZE_EMAIL_CONFIG` is not defined** on this tip (and `gaze_email` is not in `TASK_CONFIG`). Introduced in `8d6eefe7` (AST-1089 code). Every successful call to `dispatch_task_admin_defaults` will `NameError`. Also AST-1088 shell scope smuggled into this ticket (`astral.standards.in-scope-only` / plan Out of scope).

**discuss (straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` at plan time; three-dot tip includes `docs/features/**` + Betty test-tree — scored in-scope on diff (verdicts still conforms).

### Recommended actions

1. Remove the `GAZE_EMAIL_CONFIG` early-return from this sub (belongs on AST-1088 with the config definition), or do not land that hunk here.
2. Re-run a quick import/`dispatch_task_admin_defaults` smoke after the delete.
3. Straggler discuss rows need no product change unless resolve wants Joan re-ack.

### Statutes checked (summary)

56 active statutes swept vs `origin/dev...origin/sub/AST-1087/AST-1089-…`. One **violates** (`astral.standards.in-scope-only`). Full table in Linear review comment.
