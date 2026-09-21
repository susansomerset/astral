# AST-1755 — stage_meteorite job_title prompts

**Linear:** [AST-1755](https://linear.app/astralcareermatch/issue/AST-1755/stage-meteorite-job-title-prompts-stage-email-meteorite-enhancements)  
**Parent:** [AST-1753](https://linear.app/astralcareermatch/issue/AST-1753/stage-email-meteorite-enhancements) — stage_email_meteorite enhancements  
**Publish ref:** `sub/AST-1753/AST-1755-stage-meteorite-job-title-prompts`

Teach `stage_meteorite` agent_task prompts to ask Ruth for optional `job_title` on each landable jobs item (prefer subject when it names the role; omit when unknown; never invent). Keep `$RESPONSE_SCHEMA` out of those prompts. Confirm `TASK_CONFIG` already has optional `job_title` — do not invent or edit schema. Does **not** own stage content fallback (**AST-1756**) or land → job title wiring (**AST-1757**).

## Scope gate

Ticket **## Scope** (verbatim partition):

- `data/admin/agent_task.json` — **modified** — `stage_meteorite` cache/user prompts instruct optional `job_title` (subject-prefer); do not add `$RESPONSE_SCHEMA`. Technical: update `stage_meteorite` prompt text so each landable jobs item may include optional `job_title`, preferring subject-line titles when present; keep the six closed outcomes and existing electronic-contact / breadcrumb instructions; leave `$RESPONSE_SCHEMA` absent from those prompts.

All Files Changed / Stages stay inside that set.

**Out of scope (siblings / other epics):**

- `src/core/meteorite.py` stage map `jd_text` → ingress-blob fallback — **AST-1756**
- `src/core/meteorite.py` land paths passing `job_title=` into `tracker.save_meteorite_job` — **AST-1757**
- `src/utils/config.py` / `TASK_CONFIG["stage_meteorite"]["response_schema"]` — schema field already present and optional; **confirm only**, do not invent or edit
- Changing the six closed outcome literals
- Logging edits (`stat.logging.debug` / `stat.logging.info.entity` are id-only for this child)

**Depends on:** none (Bang `!` with sibling #2). Sibling **AST-1757** is after this child for full end-to-end title UAT.

**AC partition (this ticket):** Parent AC1–AC4 only (AC5–6 → AST-1756; AC7–9 → AST-1757).

**Canon Scope (read at plan):** `patt.task.daisy-chain` (full — title must be askable at stage so the meteorite row can carry it through later hops; this ticket only teaches the ask, does not invent a parallel extract). `stat.logging.debug`, `stat.logging.info.entity` — **id-only** (no logging code in this ticket’s file).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `data/admin/agent_task.json` | Extend `stage_meteorite` `cache_prompt` (+ `user_prompt` touch) for optional subject-prefer `job_title`; forbid invention; keep six outcomes + electronic-contact / breadcrumb sections; never insert `$RESPONSE_SCHEMA` | catalog |

## Stage 1: Confirm schema (read-only) + prompt text

**Done when:** `TASK_CONFIG["stage_meteorite"]["response_schema"]["jobs"]["items_schema"]["job_title"]["required"] is False` (no config edit); `stage_meteorite` `cache_prompt` / `user_prompt` instruct optional `job_title` with subject preference and never-invent; neither prompt field contains `$RESPONSE_SCHEMA`; six outcome names and existing electronic-contact / breadcrumb instructions remain; JSON remains valid.

1. **Confirm only (no file edit):** from the epic worktree, run:

```bash
python3 -c 'from src.utils.config import TASK_CONFIG; s=TASK_CONFIG["stage_meteorite"]["response_schema"]["jobs"]["items_schema"]["job_title"]; assert s.get("required") is False; print(s)'
```

If this assert fails, **stop** and comment on the Linear **parent** with the Stage-blocked template — do not invent a schema field in this ticket (Scope does not include `config.py`).

2. In `data/admin/agent_task.json`, locate the object with `"task_key": "stage_meteorite"`. Edit **`cache_prompt`** only by **appending** a new section after the existing `## ELECTRONIC CONTACT (resume send)` block (do not rewrite OUTCOMES, HEADER / BREADCRUMB FIELDS, or ELECTRONIC CONTACT). Append exactly this section (literal text):

```
## JOB TITLE (optional)

For every jobs item you return on landable outcomes (single_jd_no_link, single_jd_with_more, multi_jd_inline, link_list), include optional job_title when you can tell what the role is called.

Prefer the email (or ingress) subject line when it names the role. If the subject does not name a role, use an explicit title already present in the JD/body. If the title is unknown, omit job_title or return an empty string.

Never invent titles. Never guess a role name from vague marketing copy.
```

3. Update the same row’s **`user_prompt`** to (replace the whole string):

```
Read CONTENT. Return JSON with outcome (exactly one closed outcome literal) and jobs (scrap fields per outcome; empty list for not_job_content and not_original_posting). For single_jd_no_link and multi_jd_inline, each jobs item must include from_email, to_email, and sent_at (bare emails; peel inner headers on forwards). Include optional electronic_contact per item (prefer metadata; never invent addresses). Include optional job_title per landable jobs item when the role name is known (prefer subject when it names the role; omit when unknown; never invent). Do not emit grade vectors.
```

4. Leave `nocache_prompt`, `system_prompt`, and `cache_prompt_b`/`_c`/`_d` unchanged (empty). Do **not** insert `$RESPONSE_SCHEMA` (or any full schema dump) into any `stage_meteorite` prompt field.

5. Verify acceptance gates from the epic worktree:

```bash
rg -n 'job_title' data/admin/agent_task.json
# Expect matches inside the stage_meteorite prompt text (cache_prompt / user_prompt), not only unrelated tasks.

python3 - <<'PY'
import json
from pathlib import Path
row = next(r for r in json.loads(Path("data/admin/agent_task.json").read_text()) if r.get("task_key") == "stage_meteorite")
for k in ("cache_prompt", "user_prompt", "nocache_prompt"):
    t = row.get(k) or ""
    assert "$RESPONSE_SCHEMA" not in t, k
    if k in ("cache_prompt", "user_prompt"):
        assert "job_title" in t, k
print("stage_meteorite prompts OK")
PY

python3 -c 'from src.utils.config import TASK_CONFIG; s=TASK_CONFIG["stage_meteorite"]["response_schema"]["jobs"]["items_schema"]["job_title"]; assert s.get("required") is False'
python3 -c 'import json; json.load(open("data/admin/agent_task.json"))'
```

⚠️ **Decision:** Prompt-only change; reuse the existing optional `job_title` schema key already on `items_schema`. Do not rename, require, or relocate the field — parent AC3 and Scope both say confirm, not invent.

⚠️ **Decision:** Append a dedicated `## JOB TITLE (optional)` section rather than folding title rules into OUTCOME bullets — mirrors AST-1688’s electronic-contact section pattern and keeps the six outcome definitions untouched.

**AC4 note (no code in this ticket):** Existing stage→row map in `src/core/meteorite.py` already copies Ruth `job_title` onto the meteorite row (`row["job_title"] = _stage_field(job, "job_title")`). After this prompt change, a landable classify that returns `"job_title": "Senior Widget Engineer"` is expected to persist that string on the meteorite column via that existing map. Do **not** edit `meteorite.py` here; if the map is missing at build time, stop and escalate (Scope boundary / sibling ownership).

## Estimate

Confirm Chuckles estimate: 2 — agree
