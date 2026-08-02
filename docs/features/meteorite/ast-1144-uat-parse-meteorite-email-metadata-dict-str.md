# AST-1144 — UAT: parse_meteorite_email rejects jobs[].metadata dict (expects str)

**Linear:** [AST-1144](https://linear.app/astralcareermatch/issue/AST-1144/uat-parse-meteorite-email-rejects-jobsmetadata-dict-expects-str)
**Parent:** [AST-1128](https://linear.app/astralcareermatch/issue/AST-1128/gaze-email-candidate-bound-dispatch-redesign) — gaze_email — candidate-bound dispatch (redesign)
**Publish ref:** `origin/sub/AST-1128/AST-1144-uat-parse-meteorite-email-metadata-dict-str`

UAT bug: candidate-bound `gaze_email` for somerset hit Ruth `parse_meteorite_email` validation `jobs[0]: Field 'metadata' must be str, got dict` when the model returned structured company/location metadata. Align the TASK_CONFIG schema (and prompt wording) with the live object shape so html_links ingest can reach METEORITE_NEW / archive again. Does **not** change bind/Avail/unbound retention/Land Meteorite/qualify hops.

## UAT fitness

- **AC restored:** “Bound in-scope message shapes still produce the AST-1087 ingest outcomes for that candidate (**METEORITE_NEW** / archive / ignore rules as already established for bound mail); a single run does not advance jobs into qualify/GDL.” Also: “With `debug=True`, each candidate run, each considered message, and each create/skip/archive/trash/ignore outcome is visible in Style D (found + recorded); with `debug=False`, no new debug noise from this path.”
- **Correct outcome:** Bound html_links mail whose Ruth parse yields job links (with optional company/location metadata objects) validates, scrapes/creates **METEORITE_NEW** (or per-candidate dedupe skip), and archives; debug shows found + recorded, not `ruth_fail` validation.
- **Sibling check:** AST-1136 runner three-way filter / unbound Trash / `last_email_check` stamp unchanged — only the parse contract for `jobs[].metadata` changes so `_handle_bound` can consume a successful `parsed_response`. AST-1089 task key / modes / `requires_candidate_key` stay. AST-1129 Land Meteorite reuse path benefits from the same schema fix (same `do_task`). Verify by running somerset `gaze_email` (or component fixture with dict metadata) without touching Avail/provision.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Swallowing validation and continuing with empty `jobs`; deleting/loosening all schema checks; leaving the message forever without fixing the contract; “no more stacktrace” without successful ingest when links are present.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `TASK_CONFIG["parse_meteorite_email"].response_schema.jobs.items_schema.metadata` type `str` → `dict` | utils |
| `data/admin/agent_task.json` | Clarify `html_links` prompt: `metadata` is optional object `{company?, location?}` | data/admin |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Byte-identical copy after prompt edit (AST-786 seed gate) | docs |

No `src/core/gaze_email.py` / dispatcher / Avail / React / Gmail changes. No engineer edits under `tests/` / bible (Betty adds dict-metadata regression at Code Complete per Diagnosis).

## Stage 1: Schema + prompt contract for dict metadata

**Done when:** `do_task` validation accepts a `parse_meteorite_email` payload whose `jobs[].metadata` is a dict (e.g. `{"company":"…","location":"…"}`); prompt documents that object shape; AST-756 fixture matches repo `agent_task.json`; runner still only needs `job_link` for scrape/create (metadata remains optional advisory).

1. In `src/utils/config.py` inside `TASK_CONFIG["parse_meteorite_email"]["response_schema"]["jobs"]["items_schema"]`, change:

   ```python
   "metadata": {"type": "str", "required": False},
   ```

   to:

   ```python
   "metadata": {"type": "dict", "required": False},
   ```

   ⚠️ **Decision — type `dict`, not loosen/remove:** `src/core/agent.py` `_validate_schema_object_fields` already accepts `type` in `("object", "dict")` for mapping values. Live Ruth returns structured company/location objects; AST-1089’s `str` typing was the mismatch. Prefer `dict` (same literal as `resume_structure` / `job_data` peers). Do **not** accept both str and dict in one field (validator is single-type). Do **not** skip schema validation.

2. Do **not** change `job_link` / `job_title` / top-level `parse_mode` / `jd_link` / `content_text` types. Do **not** add nested `items_schema` on `metadata` (validator does not recurse object field maps today; optional free-form dict is enough for company/location).

3. In `data/admin/agent_task.json`, on the `current: 1` row `task_key == "parse_meteorite_email"`, edit **only** the `cache_prompt` html_links sentence that currently says `return \`{job_link, job_title?, metadata?}\` in \`jobs\`` so it documents the object shape, e.g. return `{job_link, job_title?, metadata?}` where optional `metadata` is an object with optional string fields `company` / `location` (omit `metadata` when unknown). Keep subject_body section and “JSON only / no qualify fields” rules unchanged.

   ⚠️ **Decision — prompt clarity, not a second parse mode:** Prompt already invited unstructured `metadata?`; Ruth filled objects. Document the object so the catalog matches the schema; do not invent a new TASK_CONFIG key or PARSE_MODE.

4. Copy the updated `data/admin/agent_task.json` bytes to `docs/uat-fixtures/AST-756/expected-agent_task.json` so they remain identical (same AST-786 / catalog gate as AST-1089 Stage 2).

5. Do **not** edit `src/core/gaze_email.py` — `_handle_bound` already uses only `job.get("job_link")` for html_links ingest; once validation passes, create/archive resumes. Do **not** coerce/stringify metadata in `agent.py`. Do **not** change From-bind, Avail, unbound retention, or Land Meteorite UI.

**Done when (recheck):**

```bash
python3 -c "from src.utils import config as c; m=c.TASK_CONFIG['parse_meteorite_email']['response_schema']['jobs']['items_schema']['metadata']; assert m['type']=='dict' and m.get('required') is False"
python3 -c "import json; a=open('data/admin/agent_task.json','rb').read(); b=open('docs/uat-fixtures/AST-756/expected-agent_task.json','rb').read(); assert a==b"
python3 -m py_compile src/utils/config.py
```

Betty (post Code Complete): add a regression that feeds a realistic Ruth payload with `jobs[].metadata` as a dict through `do_task` / gaze_email path so this cannot regress to `type: str` silently (Diagnosis — engineer does not invent that test here).

## Self-Assessment

**Scope:** `minor` — one schema field type + prompt/fixture sync for `parse_meteorite_email`; no runner/Avail/UI surfaces.

**Conf:** `high` — failure string names the exact schema field; agent already validates `dict`; runner ignores metadata content and only needs validation to pass.

**Risk:** `Medium` — wrong type flip could reject string metadata if any caller still emits str; mitigated by live UAT evidence (dict) + prompt documenting object. Ingest path unblocked when links present.

## Rules check (plan vs ASTRAL_CODE_RULES)

- §2.1 / `astral.config.config-source-of-truth` — response schema stays in `TASK_CONFIG`.
- §2.2 / `astral.agent.do-task-delegation` — still `do_task`; no new Anthropic assembly in core.
- `astral.standards.in-scope-only` — schema/prompt/fixture only; no Avail/bind/Land Meteorite.
- `astral.state.no-daisy-chain-in-run` — still METEORITE_NEW only after parse succeeds.
- Seed/catalog: prompt edit stays on Archie-named `parse_meteorite_email`; fixture byte-lock preserved.

## Review

**Publish ref:** `origin/sub/AST-1128/AST-1144-uat-parse-meteorite-email-metadata-dict-str`
**Tip:** `32434707dbab3e758d082da1fbaee4b01682a17c`
**Overall:** DISCUSS

[code-rubric] revision=1 — Radia full-set sweep vs `origin/dev...origin/sub/AST-1128/AST-1144-uat-parse-meteorite-email-metadata-dict-str`.

### What's solid

- Stage 1 matches plan: `jobs[].metadata` type `str` → `dict` on `TASK_CONFIG["parse_meteorite_email"]`; html_links prompt documents optional `{company?, location?}` object; AST-756 fixture byte-identical to `data/admin/agent_task.json`.
- Betty added dict-metadata regression (`do_task` validates dict; rejects str). No runner/Avail/UI creep in `code(AST-1144)`.

### Issues

**discuss:** Linear assignee is Radia at Tests Passed (`orch.roles.engineer-assignee-through-resolve`). Implementer should usually remain assignee through Review Posted / resolve. Confirm handoff (leave Radia vs restore engineer) before resolve-child.

### Recommended actions

- No fix-now on the schema/prompt fix. Restore engineer assignee for resolve if that was unintentional.
