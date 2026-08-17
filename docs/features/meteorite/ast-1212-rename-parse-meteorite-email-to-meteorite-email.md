<!-- linear-archive: AST-1212 archived 2026-08-17 -->

## Linear archive (AST-1212)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1212/rename-parse-meteorite-email-to-meteorite-email-rename-task-to  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1182 — Rename task to meteorite_email + AI payload as visible text/links  
**Blocked by / blocks / related:** parent: AST-1182; blocks: AST-1213

### Description

## What this implements

Owns the product rename: config task key and related literals, agent_task seed identity, and every caller that still names `parse_meteorite_email`. Does **not** change the AI live-payload shape (sibling #2) or review groupings / aliases (AST-1183 / AST-1184).

## In scope

- [X] `pattern.config.config-block` — task key + parse-mode literals stay in `METEORITE_EMAIL_PARSE_CONFIG` / `TASK_CONFIG`; callers read config
- [X] `astral.config.config-source-of-truth` — live product key is `meteorite_email` in config only
- [X] `astral.seed.agent-tables-in-repo-json` — Ruth `agent_task` row identity renames with the product key
- [X] `astral.standards.names-not-ticket-ids` — domain key `meteorite_email`
- [X] `astral.standards.no-hardcoded-sets` — no dual old/new key lists or compat shim
- [X] `astral.standards.in-scope-only` — rename only; payload / groupings / aliases out
- [X] `astral.agent.do-task-delegation` — gaze_email keeps invoking Ruth via `do_task` + config `task_key` (no core edit expected)
- [X] `astral.git.engineer-test-tree-ban` — no `tests/` / bible edits on this ticket

## Considered but excluded

- [X] AI live-payload visible text/links + prompt rewrite — **AST-1213** (`src/core/gaze_email.py` payload assembly / prompts)
- [X] Gaze Review → Meteorite Review grouping / section reshuffles — **AST-1183**
- [X] `master_task_key` / task aliases — **AST-1184**
- [X] UI grouping/sequence / alphabetical dropdowns — **AST-1185**
- [X] evaluate_meteorite test / statute fold-in — **AST-1186**
- [X] `METEORITE_DISPATCH_TASKS` / dispatch claim wiring — parse was never a dispatch claim task
- [X] Blind whole-file AST-756 `cp` — catalog 53 vs fixture 51 drift (surgical row sync only)
- [X] Compat alias keeping `parse_meteorite_email` as a live key — conflicts with AC

## Acceptance criteria

- [X] Product config and agent_task seed identify the Ruth meteorite-email parse task as `meteorite_email`; `parse_meteorite_email` is absent as a live task key / agent_task identity.
- [X] All in-repo callers that invoked the old key now invoke `meteorite_email` (via config), and a dry run / known call path does not look up the old key.

## Boundaries

Does **not** change the AI live-payload shape (sibling #2). Does **not** own review groupings / aliases (AST-1183 / AST-1184).

## Notes for planning

Domain rename only — keep parse modes and response schema behavior intact under the new key. `gaze_email._ruth_parse` already uses `METEORITE_EMAIL_PARSE_CONFIG["task_key"]` — config rename flips the call path.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1182-rename-task-to-meteorite-email`, child `sub/AST-1182/AST-1212-rename-parse-meteorite-email-to-meteorite-email`. Created at dispatch-parent.

### Comments

#### radia — 2026-08-06T06:04:51.801Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1212
**Publish ref:** `25fc2c82` (docs-only review append at `75d02df9`)
**Overall:** FIX-NOW

## Plan adherence

- Stage 1 (config rename) matches plan exactly — `TASK_CONFIG` key + `METEORITE_EMAIL_PARSE_CONFIG["task_key"]` renamed, no compat shim, `gaze_email.py` untouched (already config-driven).
- Stage 2 (seed identity rename) matches the *intended* row-level content, but the write mechanism broke the plan's explicit "surgical, no whole-file rewrite" instruction at the byte level.
- Exactly one `merge-tests(AST-1212)` commit; engineer commits never touch `tests/` or `docs/test-bible/**`.

## Pattern conformance

`pattern.config.config-block` — conforms (rename stays inside the existing `TASK_CONFIG` dict; no second source of truth introduced).

## Findings

**fix-now — file-wide re-encoding noise on two seed JSON files:**

`data/admin/agent_task.json` (92 raw diff lines) and `docs/uat-fixtures/AST-756/expected-agent_task.json` (88 raw diff lines) touch far more than the single planned row. A structural diff keyed by `task_key_uuid` confirms only **1 row** actually changed content in each file (`task_key` / `task_name` / `updated_at`) — the remaining ~36 hunks per file are pure re-serialization: the file was re-emitted with `json.dump(..., ensure_ascii=True)` (Python's default) instead of the repo's established `ensure_ascii=False` convention, escaping every em-dash/curly-quote in every untouched prompt row (e.g. `—` → `\u2014`).

Confirmed reproducible: re-dumping the tip's `agent_task.json` with `ensure_ascii=False` collapses the diff against `origin/dev` to exactly 3 lines (`task_key`, `task_name`, `updated_at`) — matching the plan's own Stage 2 intent ("Do not edit any other row"; "no whole-file `cp`"). The plan's structural verification script (comparing loaded Python dicts) passes today only because Python string equality ignores JSON escaping — it does not catch this at the raw-file/git-diff level.

Violates `astral.standards.in-scope-only` (silent scope expansion across ~36 unrelated rows) and undercuts `astral.seed.agent-tables-in-repo-json`'s rationale (repo JSON as the durable, *reviewable* seed source). No functional/behavioral risk — content is semantically identical — but the diff noise must be cleaned up before User Testing: re-save both files preserving `ensure_ascii=False`, touching only the renamed row.

## What's solid

- No stray live `parse_meteorite_email` string anywhere in `src/` (verified — only historical "formerly …" comments remain).
- `astral.standards.no-hardcoded-sets` conforms — no dual old/new key list; test asserts `"parse_meteorite_email" not in cfg.TASK_CONFIG`.
- Commit vocabulary, branch topology (`sub/AST-1182/AST-1212-...`), and Linear status gates all conform.

## Frame diff

(none — ticket description/AC unchanged; findings are diff-only)

context_tokens≈50000
— Radia

#### betty — 2026-08-06T05:55:37.658Z
## QA test manifest (AST-1212)

**Publish:** `origin/sub/AST-1182/AST-1212-rename-parse-meteorite-email-to-meteorite-email` @ `25fc2c82`
**Betty SHA:** `71166aaf` — `merge-tests(AST-1212): origin/tests 71166aafc79d56d85dfa45a0d19ea315eb781d90`

### Classification

1. **Existing coverage (revised):** AST-1089 / AST-1144 / AST-786 / AST-1106 suites — same behaviors under live key `meteorite_email`.
2. **Broken / obsolete (revised this pass):** asserts/skipifs still keyed on `parse_meteorite_email` in `test_config.py`, `test_repo_admin_json.py`, `test_agent.py`.
3. **Gaps:** none beyond rename lockstep — catalog row ↔ `TASK_CONFIG["meteorite_email"]["agent_task"]` assert added on the Ruth shell test.

**Integration:** no existing scenarios pin this task key — none revised.

### Manifest (test-child)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1089ParseMeteoriteEmailConfig \
  tests/component/utils/test_config.py::TestAst1144ParseMeteoriteEmailMetadataDict \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1089ParseMeteoriteEmailCatalogRow \
  tests/component/core/test_repo_admin_json.py::TestAst1106GazeEmailCatalogRow \
  tests/component/core/test_repo_admin_json.py::TestAst1144ParseMeteoriteEmailMetadataPrompt \
  tests/component/core/test_agent.py::TestAst1144ParseMeteoriteEmailMetadataDict \
  -q
```

### Bible shasums (`origin/<publish-ref>`)

- `docs/test-bible/utils/config.md` `b7b0cd8b3863bcfe567487373c09048b85b835ca`
- `docs/test-bible/core/repo_admin_json.md` `c2814588e4a38b92a6c3c92e0ffb3d8dced71f3b`
- `docs/test-bible/core/agent.md` `99b4c3ee35f568deeca5f88b264c0f84b2f63b27`

— Betty

#### joan — 2026-08-06T05:47:34.683Z
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1212
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1182/AST-1212-rename-parse-meteorite-email-to-meteorite-email` @ `8fc8e20f`

## Traceability

AC1→S1+S2; AC2→S1 (config flip) + S2.5 (caller path check).

## Findings

**fix-now:** none.

### discuss (non-blocking)

1. **No cross-check that the two halves of AC1 agree.** `TASK_CONFIG["meteorite_email"]["agent_task"]` (S1) and the catalog row `task_key` (S2) are the config→seed identity link, and they are set in two separate commits with no gate tying them together. S1's import gate passes on the config side alone (`assert METEORITE_EMAIL_PARSE_CONFIG["task_key"] in TASK_CONFIG` only checks TASK_CONFIG membership), and S2.5 verifies each side independently. I found **no** existing guard either — `tests/component/core/test_repo_admin_json.py` has zero `TASK_CONFIG` references. One line in S2's script would close it:

```python
assert any(r["task_key"] == c.TASK_CONFIG["meteorite_email"]["agent_task"] and r.get("current") == 1 for r in cat)
```

2. **Broken-test handoff is stated generically.** The self-review says expected asserts on the old key are "Betty's post–Code Complete work" — correct call, and `tests/` is rightly untouched. But the rename will break specific known files: `tests/component/utils/test_config.py` (indexes `TASK_CONFIG["parse_meteorite_email"]["response_schema"]…` → KeyError), `tests/component/core/test_repo_admin_json.py` (asserts a `current == 1` row with the old `task_key`, plus the AST-786 catalog key-set lock), `tests/component/core/test_agent.py`; bible pages `docs/test-bible/utils/config.md`, `core/repo_admin_json.md`, `core/agent.md`. AST-1196 set the precedent of naming the stale gate explicitly in-plan so the Tests Ready handoff is deterministic rather than discovered.

### acceptable — verified against the tip

- **Call-site inventory is complete.** A repo-wide sweep finds live `parse_meteorite_email` strings only in the three planned files. `src/core/gaze_email.py` has **zero** occurrences, so "leave the caller untouched" is a verified fact, not optimism — the config rename genuinely flips the call path.
- **Every config fact the S1 gate asserts is real.** Dict key at `config.py:530`, immediately after the `qualify_meteorite` block (ends 527) as claimed; `requires_candidate_key: True` / `entity_type: None` / `trigger_state: None` are the current values, so the recheck script passes on a correct implementation rather than failing on a wrong premise; the two asserts quoted at 2392–2393 exist verbatim; `METEORITE_DISPATCH_TASKS` contains no parse key, so "do not add" is consistent with today's state. Exactly four live strings in the file (key, `context_format`, `agent_task`, `METEORITE_EMAIL_PARSE_CONFIG["task_key"]`) — all four are addressed.
- **Catalog/fixture arithmetic is exact.** 53 and 51 rows; one `current == 1` old-key row (`college_intern_ruth`, `task_seq` 2.4); the old key appears **only** in `task_key` + `task_name` — no `master_task_key` field exists on the row, so the AST-1184 alias boundary is structurally safe, not just declared. The 53↔51 delta is precisely `evaluate_meteorite` + `craft_evaluate_meteorite_rubric` with no fixture-only rows, matching the plan's characterization. `task_key_uuid` is present and unique in both files, so the by-uuid pre/post diff script is sound.
- **Runtime propagation holds, for a reason the plan does not state.** Startup apply routes to `database.apply_agent_task_repo_json_startup`, which upserts **by `task_key_uuid`**. Because the plan freezes the uuid, an already-seeded DB gets an in-place UPDATE and the old `task_key` is overwritten — no phantom `parse_meteorite_email` row survives. That is AC1's runtime half. "Do not change `task_key_uuid`" is load-bearing, not cosmetic.
- **The fixture edit is permitted.** `astral.git.engineer-test-tree-ban` lists `tests/**`, `docs/test-bible/**`, `docs/ASTRAL_TEST_BIBLE.md`, `scripts/test_*.py`, `scripts/testing/**` — `docs/uat-fixtures/**` is not in scope, so the surgical sync is engineer work. Declining the inherited 53↔51 drift is the right `in-scope-only` call and matches AST-1196.
- **`context_format` rename is safe.** It is label-only (`agent.py:1147`, "build context string … falls back to task_key") — nothing retrieves by the old label, and `meteorite_email_{index}` matches the sibling convention (`qualify_meteorite_{index}`).
- **No compat alias** is the correct reading of the parent AC; a dual-key list would have tripped `no-hardcoded-sets`.
- **Transient S1 tip inconsistency accepted.** Between the two commits, config points at an `agent_task` row that has not been renamed yet. Fine for a two-commit child that publishes one tip.

**Considered:** scored in-session.

## Verdict

**APPROVED.** Self-assessment is honest: `Single-Component` / `high` / `Medium` matches what I found — a mechanical three-file rename whose only real hazard (a missed live string) I swept for and did not find. Boundaries hold: payload shape (AST-1213), groupings (AST-1183), aliases (AST-1184), dispatch wiring, and the test tree are all untouched.

— Joan

context_tokens≈121000

#### ada — 2026-08-06T05:42:30.329Z
Plan published on `origin/sub/AST-1182/AST-1212-rename-parse-meteorite-email-to-meteorite-email` @ `8fc8e20f`.

[Plan doc](https://github.com/susansomerset/astral/blob/sub/AST-1182/AST-1212-rename-parse-meteorite-email-to-meteorite-email/docs/features/meteorite/ast-1212-rename-parse-meteorite-email-to-meteorite-email.md)

**Scope:** Single-Component — `TASK_CONFIG` / `METEORITE_EMAIL_PARSE_CONFIG` identity + one Ruth `agent_task` row (+ surgical AST-756 fixture sync); `gaze_email` already config-driven, left untouched.

**Conf:** high — mechanical rename; parse modes / schema / prompts frozen for AST-1213; no compat shim.

**Risk:** Medium — a missed live `parse_meteorite_email` string breaks the Ruth gaze_email hop; blast radius is that parse path, not qualify/evaluate GDL.

Call-site inventory: only live product strings were in `src/utils/config.py` + `data/admin/agent_task.json` (+ fixture row). Fixture sync is surgical (53↔51 drift left alone).

---

# AST-1212 — Rename parse_meteorite_email to meteorite_email

**Linear:** [AST-1212](https://linear.app/astralcareermatch/issue/AST-1212/rename-parse-meteorite-email-to-meteorite-email-rename-task-to)
**Parent:** [AST-1182](https://linear.app/astralcareermatch/issue/AST-1182/rename-task-to-meteorite-email-ai-payload-as-visible-textlinks) — Rename task to meteorite_email + AI payload as visible text/links
**Publish ref:** `origin/sub/AST-1182/AST-1212-rename-parse-meteorite-email-to-meteorite-email`

Domain rename only: product config task key, `agent_task` seed identity, and live callers resolve to `meteorite_email`. Parse modes (`html_links` / `subject_body`), response schema, and prompt wording stay intact under the new key. Does **not** change the AI live-payload shape (**AST-1213**), review groupings (**AST-1183**), or task aliases (**AST-1184**).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Rename `TASK_CONFIG` key + `METEORITE_EMAIL_PARSE_CONFIG["task_key"]` + `context_format` / `agent_task` literals to `meteorite_email`; refresh inventory/comments that still name the old live key | utils |
| `data/admin/agent_task.json` | Rename the current Ruth row `task_key` / `task_name` to `meteorite_email` (prompts/grouping/`task_key_uuid` unchanged) | data/admin |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Surgical sync of that same row’s `task_key` / `task_name` (and `updated_at` if bumped) — **no** whole-file `cp` | docs |

**No changes expected:** `src/core/gaze_email.py` (already calls `do_task` with `METEORITE_EMAIL_PARSE_CONFIG["task_key"]`), `src/core/agent.py`, `src/core/consult.py`, `src/core/gazer.py`, dispatcher, Gmail external, frontend, `METEORITE_DISPATCH_TASKS`, `tests/` / bible (Betty after Code Complete). Do **not** add a compat alias or dual old/new key list.

## Stage 1: Config — live task key `meteorite_email`

**Done when:** `METEORITE_EMAIL_PARSE_CONFIG["task_key"] == "meteorite_email"`; that key exists in `TASK_CONFIG` with the same response schema / meta as today (including `requires_candidate_key is True`, `entity_type is None`, `trigger_state is None`); `parse_meteorite_email` is absent from `TASK_CONFIG` and from `METEORITE_EMAIL_PARSE_CONFIG`; `python3 -m py_compile src/utils/config.py` succeeds (use repo venv if needed: `~/astral/.venv/bin/python`).

1. In `src/utils/config.py`, locate the inventory comment line for `METEORITE_EMAIL_PARSE_CONFIG` (near other meteorite / email ingest bullets). Update wording so it describes the Ruth meteorite-email parse task key as `meteorite_email` (may still cite AST-1089 origin + AST-1212 rename). Do **not** invent a second config block name.

2. In `TASK_CONFIG`, rename the dict key `"parse_meteorite_email"` → `"meteorite_email"` (same position: immediately after `"qualify_meteorite"`). Inside that block, set:
   - `"context_format": "meteorite_email_{index}"`
   - `"agent_task": "meteorite_email"`
   - Leave `response_format`, `output_type`, `scored`, `response_schema` (including `parse_mode`, `jobs` / `metadata` dict, `jd_link`, `content_text`), `entity_type`, `requires_candidate_key`, and `trigger_state` **byte-identical** to the pre-rename values (types and required flags unchanged).

3. Update the block’s leading comments so they name `meteorite_email` as the live key (keep AST-1089 / AST-1090 historical pointers; note AST-1212 rename). Do **not** change call-site guidance: AST-1090 / `gaze_email` still uses `METEORITE_EMAIL_PARSE_CONFIG["task_key"]`.

4. In `METEORITE_EMAIL_PARSE_CONFIG`, set `"task_key": "meteorite_email"`. Leave `"parse_modes": ("html_links", "subject_body")` unchanged. Keep the existing asserts:

```python
assert METEORITE_EMAIL_PARSE_CONFIG["task_key"] in TASK_CONFIG
assert set(METEORITE_EMAIL_PARSE_CONFIG["parse_modes"]) == {"html_links", "subject_body"}
```

5. Grep `src/utils/config.py` for `parse_meteorite_email`. Remove or rewrite any remaining **live** identity string (dict keys, `task_key` / `agent_task` / `context_format` values). Historical “formerly …” prose in comments is allowed; a live `"parse_meteorite_email"` string value or `TASK_CONFIG` key is not.

6. Do **not** add `meteorite_email` to `METEORITE_DISPATCH_TASKS`, `_DISPATCH_BATCH_CALL_MODE_ONE`, or `_dispatch_trigger_state_for_task_key`. Do **not** leave a shim key `parse_meteorite_email` alongside the new one.

⚠️ **Decision — no compat alias:** Parent AC requires `parse_meteorite_email` absent as a live product key. Callers already read `METEORITE_EMAIL_PARSE_CONFIG["task_key"]`; a dual-key list would violate `astral.standards.no-hardcoded-sets` and the rename AC.

⚠️ **Decision — leave `gaze_email.py` untouched:** `_ruth_parse` already passes `task_key=METEORITE_EMAIL_PARSE_CONFIG["task_key"]`. Renaming the config value flips the live call path without a core edit (config source of truth).

**Done when (recheck):**

```bash
~/astral/.venv/bin/python -c "
from src.utils import config as c
assert c.METEORITE_EMAIL_PARSE_CONFIG['task_key'] == 'meteorite_email'
assert 'parse_meteorite_email' not in c.TASK_CONFIG
t = c.TASK_CONFIG['meteorite_email']
assert t['agent_task'] == 'meteorite_email'
assert t['context_format'] == 'meteorite_email_{index}'
assert t['requires_candidate_key'] is True
assert t['entity_type'] is None
assert t['trigger_state'] is None
assert set(c.METEORITE_EMAIL_PARSE_CONFIG['parse_modes']) == {'html_links', 'subject_body'}
assert all(e.get('task_key') != 'meteorite_email' for e in c.METEORITE_DISPATCH_TASKS)
"
~/astral/.venv/bin/python -m py_compile src/utils/config.py
```

**Ritual:** `code(AST-1212): config task key meteorite_email`

## Stage 2: Repo `agent_task` identity + surgical AST-756 fixture sync

**Done when:** `data/admin/agent_task.json` has exactly one `current: 1` row with `task_key == "meteorite_email"` and `task_name == "meteorite_email"` (`college_intern_ruth`); no current row still uses `parse_meteorite_email`; prompts / grouping / `task_key_uuid` / `task_seq` / `agent_id` match the pre-rename row except identity fields (+ `updated_at` if bumped); the AST-756 fixture’s matching row has the same `task_key` / `task_name` (/`updated_at`); catalog vs fixture still differ only by the pre-existing missing `evaluate_meteorite` + `craft_evaluate_meteorite_rubric` rows (53 vs 51) — this stage does not absorb that drift.

1. Snapshot before edit (local `/tmp` only — do not commit):

```bash
cp data/admin/agent_task.json /tmp/agent_task.pre-ast-1212.json
cp docs/uat-fixtures/AST-756/expected-agent_task.json /tmp/expected-agent_task.pre-ast-1212.json
```

2. In `data/admin/agent_task.json`, locate the single object with `task_key == "parse_meteorite_email"` and `current == 1`. Set:
   - `task_key` → `"meteorite_email"`
   - `task_name` → `"meteorite_email"` (AST-1107 law: `task_name == task_key`)
   - Optionally bump `updated_at` to current UTC matching neighboring row format (`YYYY-MM-DD HH:MM:SS`)
   - Do **not** change `task_key_uuid`, `agent_id`, `task_group_order`, `task_group_name`, `task_seq`, `cache_prompt`, `user_prompt`, or empty prompt slots (`system_prompt`, `cache_prompt_b/c/d`, `nocache_prompt`, `run_next`).
   - Do **not** edit any other row.

3. **Surgical fixture sync (no whole-file `cp`):** in `docs/uat-fixtures/AST-756/expected-agent_task.json`, find the object with `task_key == "parse_meteorite_email"` and `current == 1` and set its `task_key`, `task_name`, and `updated_at` to the **exact same strings** as the catalog row just edited. Do **not** `cp` the whole catalog over the fixture. Do **not** add missing fixture rows (`evaluate_meteorite`, `craft_evaluate_meteorite_rubric`) or rewrite other tasks.

⚠️ **Decision — leave inherited fixture drift alone:** Catalog has 53 current rows; AST-756 fixture has 51 (missing `evaluate_meteorite` + `craft_evaluate_meteorite_rubric`) plus unrelated shared-row drift. Blind `cp` would absorb that under this ticket. Same stance as AST-1196.

⚠️ **Decision — prompts unchanged:** Prompt body still says “meteorite email parse” in prose; that is fine. Rewriting prompts / live payload for visible text+links is **AST-1213**.

4. Verify only identity fields moved on the target row; no other catalog/fixture rows changed:

```bash
~/astral/.venv/bin/python - <<'PY'
import json
from pathlib import Path

def load(p):
    return json.loads(Path(p).read_text())

def by_uuid(rows):
    return {r["task_key_uuid"]: r for r in rows}

for label, pre, post in (
    ("catalog", "/tmp/agent_task.pre-ast-1212.json", "data/admin/agent_task.json"),
    ("fixture", "/tmp/expected-agent_task.pre-ast-1212.json", "docs/uat-fixtures/AST-756/expected-agent_task.json"),
):
    a, b = by_uuid(load(pre)), by_uuid(load(post))
    assert set(a) == set(b), label
    changed = [u for u in a if a[u] != b[u]]
    assert len(changed) == 1, (label, changed)
    old, new = a[changed[0]], b[changed[0]]
    assert old["task_key"] == "parse_meteorite_email"
    assert new["task_key"] == new["task_name"] == "meteorite_email"
    # prompts / grouping / uuid / seq / agent unchanged
    for k in (
        "task_key_uuid", "agent_id", "task_group_order", "task_group_name",
        "task_seq", "cache_prompt", "user_prompt", "system_prompt",
        "cache_prompt_b", "cache_prompt_c", "cache_prompt_d",
        "nocache_prompt", "run_next", "current",
    ):
        assert old.get(k) == new.get(k), (label, k)

cat = load("data/admin/agent_task.json")
fix = load("docs/uat-fixtures/AST-756/expected-agent_task.json")
assert len(cat) == 53 and len(fix) == 51
assert not any(r.get("task_key") == "parse_meteorite_email" for r in cat)
assert not any(r.get("task_key") == "parse_meteorite_email" for r in fix)
cm = next(r for r in cat if r["task_key"] == "meteorite_email" and r.get("current") == 1)
fm = next(r for r in fix if r["task_key"] == "meteorite_email" and r.get("current") == 1)
assert cm["task_name"] == fm["task_name"] == "meteorite_email"
assert cm["updated_at"] == fm["updated_at"]
assert cm["cache_prompt"] == fm["cache_prompt"]
print("OK")
PY
```

5. Confirm product `src/` has no live old key (comments in historical feature docs / tests are out of scope):

```bash
rg -n 'parse_meteorite_email' src/ data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json
# expect: zero matches (or only historical comment prose if any remain — fix those if they are string literals used as keys)
~/astral/.venv/bin/python -c "
from src.utils import config as c
assert c.METEORITE_EMAIL_PARSE_CONFIG['task_key'] == 'meteorite_email'
# known call path: gaze_email resolves via config (no hardcoded old key)
import ast, pathlib
src = pathlib.Path('src/core/gaze_email.py').read_text()
assert 'parse_meteorite_email' not in src
assert 'METEORITE_EMAIL_PARSE_CONFIG' in src
print('caller path OK')
"
```

**Ritual:** `code(AST-1212): agent_task identity meteorite_email`

## Self-Assessment

**Scope:** `Single-Component` — utils config identity + one Ruth `agent_task` seed row (+ surgical AST-756 fixture sync); core caller already config-driven and stays untouched.

**Conf:** `high` — mechanical rename with an established config→`do_task` path (`gaze_email._ruth_parse`); parse modes / schema / prompts frozen for sibling AST-1213.

**Risk:** `Medium` — a missed live string would break Ruth lookup on the gaze_email hop; blast radius is that parse path, not dispatch claim / qualify / evaluate meteorite GDL.

## ASTRAL_CODE_RULES self-review

- **§1.1 / in-scope-only:** Stages touch only the rename files; payload, groupings, aliases, and `tests/` excluded.
- **§1.4 / no-hardcoded-sets:** No dual old/new key lists; single config `task_key`.
- **§2.1 / config-source-of-truth:** Live key lives in `TASK_CONFIG` + `METEORITE_EMAIL_PARSE_CONFIG`; callers keep reading config.
- **§2.2 / do-task-delegation:** `gaze_email` continues to call `do_task` with the config task key — no new Anthropic assembly in core.
- **§3.5 / names-not-ticket-ids:** Domain key `meteorite_email`, not ticket-scoped names.
- **Seed / agent tables in repo JSON:** Catalog row identity renames with the product key; fixture surgically synced without absorbing 53↔51 drift.
- **§3.3 imports / layers:** No new imports or layer crossings.
- **Betty test-tree ban:** No edits under `tests/` or `docs/test-bible/**` — expected component asserts on the old key are Betty’s post–Code Complete work.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1182/AST-1212-rename-parse-meteorite-email-to-meteorite-email`
**Plan path:** `docs/features/meteorite/ast-1212-rename-parse-meteorite-email-to-meteorite-email.md`

**Built tip:** `099007f539c8ff4b8792247a56f06d34bda20f53` (`099007f5`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `f048dfd4` | config task key meteorite_email |
| 2 | `099007f5` | agent_task identity meteorite_email (+ surgical AST-756 fixture) |

## Radia review — [code-rubric] revision=1

**Rubric:** code-rubric.v1 · **Publish ref tip:** `25fc2c82`

**Overall: FIX-NOW**

**What's solid:**

- `src/utils/config.py`: clean, byte-identical rename of `TASK_CONFIG["parse_meteorite_email"]` → `["meteorite_email"]` and `METEORITE_EMAIL_PARSE_CONFIG["task_key"]`; no compat shim, no stray old-key string left live (verified via `git show :src/utils/config.py | grep parse_meteorite_email` — only historical comments remain).
- `gaze_email.py` untouched as planned — already config-driven via `METEORITE_EMAIL_PARSE_CONFIG["task_key"]`.
- Exactly one `merge-tests(AST-1212)` commit; engineer's own commits (`f048dfd4`, `099007f5`) never touch `tests/` or `docs/test-bible/**`.
- Commit vocabulary, branch topology (`sub/AST-1182/AST-1212-...`), and Linear status gates all conform.

**fix-now — file-wide re-encoding of two seed JSON files:**

Both `data/admin/agent_task.json` (92 raw diff lines) and `docs/uat-fixtures/AST-756/expected-agent_task.json` (88 raw diff lines) touch far more than the single planned row. Structural diff by `task_key_uuid` confirms only **1 row** actually changed content in each file (`task_key`/`task_name`/`updated_at`) — the other ~36 hunks are pure re-serialization noise: the file was re-emitted with `json.dump(..., ensure_ascii=True)` (the default) instead of the original `ensure_ascii=False` convention, escaping every em-dash/curly-quote in every untouched prompt row (e.g. `—` → `\u2014`).

Confirmed reproducible: re-dumping the new file with `ensure_ascii=False` collapses the diff to exactly 3 lines (`task_key`, `task_name`, `updated_at`) — matching plan Stage 2's own verification intent ("Do not edit any other row"; "no whole-file `cp`"). The plan's structural check script passes today only because Python string equality ignores JSON escaping — it doesn't catch this at the raw-file level.

Violates `astral.standards.in-scope-only` (silent scope expansion across ~36 unrelated rows) and undermines `astral.seed.agent-tables-in-repo-json`'s rationale (repo JSON as the durable, reviewable seed source). No functional/behavioral risk (content is semantically identical) but must be fixed before User Testing: re-save both files preserving `ensure_ascii=False`, touching only the one row.

**Pattern conformance:** `pattern.config.config-block` — conforms (rename stays inside existing `TASK_CONFIG` dict; no second source of truth).

**Plan adherence:** Stage 1 (config rename) fully matches plan. Stage 2 (seed identity rename) matches the *intended* row-level change but the implementation's file-write mechanism broke the "surgical, no whole-file rewrite" instruction at the byte level on both the catalog and its fixture twin.

## Frame diff

(none — ticket description/AC unchanged; findings are diff-only)

context_tokens≈45000

— Radia

## Resolution

**2026-08-06** — addressed Radia **fix-now** (file-wide `ensure_ascii` re-encoding).

- Rebuilt `data/admin/agent_task.json` and `docs/uat-fixtures/AST-756/expected-agent_task.json` from `origin/dev` baseline + tip identity fields only (`task_key` / `task_name` / `updated_at` on uuid `577b9ffb-…`), written with `json.dumps(..., indent=2, ensure_ascii=False)`.
- Raw diff vs `origin/dev` is now 6 lines per file (3 fields) — no `\u2014` escaping of untouched prompt rows.
- Config rename (`f048dfd4`) and semantic row content unchanged; no product `.py` edits this resolve.
