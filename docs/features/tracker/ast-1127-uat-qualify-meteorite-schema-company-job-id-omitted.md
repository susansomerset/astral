# AST-1127 — UAT: qualify_meteorite still fails schema when company_job_id omitted

**Linear:** [AST-1127](https://linear.app/astralcareermatch/issue/AST-1127/uat-qualify-meteorite-still-fails-schema-when-company-job-id-omitted)
**Parent:** [AST-1119](https://linear.app/astralcareermatch/issue/AST-1119/fallback-for-company-job-id) — Fallback for company job id
**Publish ref:** `origin/sub/AST-1119/AST-1127-uat-qualify-meteorite-schema-company-job-id-omitted`

UAT bug: Ruth omit/`null` `company_job_id` still dies in `do_task` RESPONSE schema validation (`Missing required field 'company_job_id'`) before `qualify_meteorite` can run AST-1120’s `_resolve_company_job_id`. Fix is config-only: mark that field optional in `TASK_CONFIG["qualify_meteorite"]["response_schema"]` so missing/`null`/empty reach the existing consult resolve (AI wins; else UUID path segment from `job_link`; else empty-id fail). Does **not** swallow schema errors, rewrite prompts, touch create paths, `job_site`, or `qualify_job_listings`.

## UAT fitness

- **AC restored:** Parent AC2 — *Empty/missing AI `company_job_id` + `job_link` containing a UUID path segment … records that UUID as `company_job_id` and does not hit the empty-id fail gate.* Also preserves AC1 (non-empty AI unchanged) and AC3 (no UUID still empty-id fail).
- **Correct outcome:** omit/`null`/empty AI id + UUID in `job_link` → recorded UUID and continue past schema; non-empty AI id still wins; no UUID still fails empty-id after resolve (not `Missing required field` for omit alone when link may supply it).
- **Sibling check:** AST-1120 `_resolve_company_job_id` + wire before empty-id gate must remain and actually run; AST-1121 Style D found-source labels (`AI` / `UUID-from-job_link` / `neither`) still classify after the real path runs. Verified by not editing consult resolve/debug — only unblocking schema entry.
- **Not sufficient:** Removing the stacktrace / `Missing required field` alone is **not** done.
- **Wrong fix rejected:** catch-all swallow of schema errors; delete schema validation; prompt-only “always return company_job_id”; remove consult fallback; invent host allowlists — hypothesis matches AC; flip `required` to `False` (same pattern as `qualify_job_listings` optional metadata fields).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | In `TASK_CONFIG["qualify_meteorite"]["response_schema"]["jobs"]["items_schema"]`, set `company_job_id` `required: False` (keep `type: "str"`) | utils |

No consult/agent/meteorite-create edits. No tests/bible. Do **not** change other `qualify_meteorite` required fields (`astral_job_id`, `job_title`, `job_link`, `jd_text`).

## Stage 1: Allow omit/`null` company_job_id through RESPONSE schema

**Done when:** A RESPONSE job object missing `company_job_id` or with `company_job_id: null` passes `_validate_response_schema` for `qualify_meteorite`; present non-str values still fail type check; consult resolve path is unchanged and remains the empty-id authority.

1. In `src/utils/config.py`, locate `TASK_CONFIG["qualify_meteorite"]["response_schema"]["jobs"]["items_schema"]["company_job_id"]` (currently `{"type": "str", "required": True}` with comment `# external job UUID`).

2. Change **only** that field to:

```python
"company_job_id":  {"type": "str", "required": False},  # AST-1127: omit/null → consult UUID fallback
```

Keep sibling item fields (`astral_job_id`, `job_title`, `job_link`, `jd_text`) `required: True`.

3. Add a one-line assert near other TASK_CONFIG / qualify_meteorite asserts if the file already asserts this block; otherwise add after the `TASK_CONFIG` definition (or immediately after the qualify_meteorite dict closes if that is the local pattern):

```python
assert TASK_CONFIG["qualify_meteorite"]["response_schema"]["jobs"]["items_schema"]["company_job_id"]["required"] is False
```

⚠️ **Decision — config `required: False` only, no agent.py fork:** `_validate_schema_object_fields` already treats `required=False` + `val is None` (missing key or JSON null) as skip; type `str` still rejects wrong types when present. Matches `qualify_job_listings` optional `company_job_id`. Consult already uses `(response_job.get("company_job_id") or "").strip()` before `_resolve_company_job_id` — no consult change in this bug.

⚠️ **Decision — do not weaken other required fields:** Title/link/JD gates stay schema-required; only the external id may be recovered from `job_link` per parent AC2.

**Done when (recheck):**

```python
from src.utils.config import TASK_CONFIG
from src.core.agent import _validate_response_schema

schema = TASK_CONFIG["qualify_meteorite"]["response_schema"]
# envelope shape used by do_task — agent_performance success + jobs payload
base = {
    "agent_performance": "success",
    "agent_payload": {
        "jobs": [{
            "astral_job_id": "j1",
            "job_title": "Engineer",
            "job_link": "https://www.dice.com/company-profile/9f704ad3-7a18-506a-bd5e-6a84e73b7c00",
            "jd_text": "x" * 50,
        }]
    },
}
# omit company_job_id
assert _validate_response_schema(base, schema, "qualify_meteorite") is None
# null
base["agent_payload"]["jobs"][0]["company_job_id"] = None
assert _validate_response_schema(base, schema, "qualify_meteorite") is None
# empty string still allowed through schema (consult resolve owns empty)
base["agent_payload"]["jobs"][0]["company_job_id"] = ""
assert _validate_response_schema(base, schema, "qualify_meteorite") is None
```

Adjust the envelope keys if `_validate_response_schema` expects a different payload shape on this tip — read `do_task` / `_validate_response_schema` once and use the same envelope the production path builds; do **not** invent a second validator. `python3 -m py_compile src/utils/config.py` succeeds. No edits under `src/core/consult.py` / `src/core/agent.py` unless the recheck proves the envelope helper needs a trivial import-only smoke (still no behavior change there).

## Self-Assessment

**Scope:** `minor` — one `TASK_CONFIG` boolean on `qualify_meteorite.response_schema`; no new helpers, no apply-surface rewrite.

**Conf:** `high` — diagnosis matches `_validate_schema_object_fields` (`required and val is None`); AST-1120 resolve already handles empty AI id; `qualify_job_listings` already uses optional `company_job_id`.

**Risk:** `Medium` — loosening schema could let bad types through if mis-set, but `type: "str"` remains; empty-id gate + resolve still fail when no UUID. Wrong if someone also flips other required fields (explicitly forbidden).

## Rules check (ASTRAL_CODE_RULES)

| Rule | Status |
|------|--------|
| §2.1 config SoT | Schema required flag lives in `TASK_CONFIG` only |
| §1.1 in-scope-only | Bug surface = schema gate blocking consult resolve; no create/`job_site`/listings |
| §2.2 do-task delegation | No new validation path; existing `_validate_response_schema` + consult apply |
| AST-1120 pattern | Resolve helper untouched; this ticket only unblocks entry |

No plan conflicts requiring `conf-!!-NONE`.
