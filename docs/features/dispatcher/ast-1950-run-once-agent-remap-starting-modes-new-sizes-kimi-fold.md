<!-- linear-archive: AST-1950 archived 2026-10-08 -->

## Linear archive (AST-1950)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1950/run-once-agent-remap-starting-modes-new-sizes-kimi-fold-support-big  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** katherine  
**Priority / estimate:** None / 2  
**Parent:** AST-1946 — Support "Big" brain OpenRouter models  
**Blocked by / blocks / related:** parent: AST-1946

### Description

## What this implements

Ships the operator migration that gives every existing agent its starting mode and moves OpenRouter agent rows to their new sizes, including `kimi-k2.6-openrouter` → `moonshotai/kimi-k2.6`. Rows on removed models are only listed. After #1 and #2: the `mode` column must exist, and remapped rows must pass mode validation. Does **not** touch product code.

## Citations

none. The script lives under `scripts/`, outside every active statute's `src/**` paths, and no active pattern covers operator migrations.

## Scope

* `scripts/migrations/remap_openrouter_agents.py` (**new**): a new CLI. By default it is a dry run that prints each planned change and each agent row on a removed model. With `--apply` it does two things:
  * Sets `mode` on every agent row that has none (Big → Creative, else Deterministic, judged on the row's brain size before remap).
  * Rewrites OpenRouter rows' `brain_setting` to the slug's new size, and moves `kimi-k2.6-openrouter` rows to `moonshotai/kimi-k2.6` / `Little`.

  Removed-model and direct-model rows keep their model and size. The old→new slug map is a literal snapshot table inside the script. It runs **once per environment, right after deploy**, and the docstring says so (same convention as `retarget_artifact_chain_trigger_state.py`).

## Acceptance criteria

All `python -c` checks run from the repo root on the shipped tree. "The brief" means the 95 rows in this ticket's Original brief. `SIZE = {"int4": "Little", "fp4": "Little", "int8": "Medium", "fp8": "Medium", "fp16": "Big", "bf16": "Big"}`.

13. **Migration remaps once.**
    * **Check (component test on a temp DB, rows without** `mode`**):** seed `(qwen/qwen3-32b, Little)`, `(qwen/qwen3-32b, Medium)`, `(gryphe/mythomax-l2-13b, Little)`, `(kimi-k2.6-openrouter, Little)`, `(kimi-k2.6-openrouter, Big)`, `(morph/morph-v3-large, Little)`, `(claude, Big)` and `(deepseek-v4, Medium)`.
      * A dry run writes nothing and lists `morph/morph-v3-large` as removed.
      * `--apply` yields:
        * `(qwen/qwen3-32b, Medium, Deterministic)` for both qwen rows
        * `(gryphe/mythomax-l2-13b, Big, Deterministic)`
        * `(moonshotai/kimi-k2.6, Little, Deterministic)` and `(moonshotai/kimi-k2.6, Little, Creative)`
        * `(morph/morph-v3-large, Little, Deterministic)`
        * `(claude, Big, Creative)` and `(deepseek-v4, Medium, Deterministic)`
      * Every non-removed row then passes model + size + mode validation.
    * **Fails if:** the dry run writes, any row maps differently, or a non-removed row fails validation.

## Boundaries

Does **not** touch product code. Sibling slices: #1 catalog/resolver/config, #2 database/agent/api_admin, #3 Manage Agents UI, #4 remap migration. Blocked by: #1 (AST-1947), #2 (AST-1948).

## Notes for planning

Same `scripts/migrations/` convention as `retarget_artifact_chain_trigger_state.py`. Parent AST-1946 Description (Functional scope, Technical scope, Original brief with all 95 rows) is authoritative.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1946-big-brain-openrouter`, child `sub/AST-1946/AST-1950-remap-migration`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-10-03T03:23:47.727Z
[merge-child] blocked: `validate-sub-log.sh` reports `missing test(AST-1950)` — false positive.

- `test(AST-1950)` `fe41777d9` is already on `origin/ftr/AST-1946-big-brain-openrouter`: on the shared `origin/tests` line, AST-1949's `0f3e3dc9a` sits on top of it, and AST-1949's `merge-tests` `e55b2cf87` carried both into ftr. `tests/component/scripts/test_remap_openrouter_agents.py` + `docs/test-bible/dev/remap_openrouter_agents.md` are present on ftr.
- The sub is stacked on ftr (`cc8253f08`) and still has `merge-tests(AST-1950)` `41d48e82f`. The validator only scans sub-not-on-ftr commits, so it can't see the test commit.
- Dry-run merge into ftr is clean. Not fabricating a noop `test()` commit (forbidden).

@Betty White — tests-line hygiene: needs either a validator rule that accepts a `test(<child>)` already reachable from ftr, or an explicit override for this merge.

#### radia — 2026-10-03T03:21:20.585Z
[code-rubric] PROCEED (Commit: 41d48e82f) Migration CLI + AC13 tests clean

#### betty — 2026-10-03T03:19:26.174Z
`origin/sub/AST-1946/AST-1950-remap-migration` @ `41d48e82f` · remap migration tests ready

#### joan — 2026-10-03T03:15:44.740Z
[plan-rubric] PROCEED (Commit: 2da2a906) Run-once remap CLI

#### katherine — 2026-10-03T03:14:31.228Z
`origin/sub/AST-1946/AST-1950-remap-migration` @ `2da2a906a` · remap CLI plan ready

---

# AST-1950 — Run-once agent remap: starting modes, new sizes, Kimi fold

- **Parent:** [AST-1946 — Support "Big" brain OpenRouter models](https://linear.app/astralcareermatch/issue/AST-1946)
- **Ticket:** [AST-1950](https://linear.app/astralcareermatch/issue/AST-1950)
- **Publish ref:** `origin/sub/AST-1946/AST-1950-remap-migration`
- **Canon Scope:** none. Ticket § Citations: the script lives under `scripts/`, outside every active statute's `src/**` paths, and no active pattern covers operator migrations.

This ticket ships one operator CLI, `scripts/migrations/remap_openrouter_agents.py`, that brings existing agent rows onto the AST-1946 catalog. It runs once per environment, right after deploy. First, every agent row with no `mode` gets a starting mode: Big → Creative, anything else → Deterministic, judged on the row's brain size **before** remap. Second, every row on a pre-epic OpenRouter model moves to that slug's one new brain size, and `kimi-k2.6-openrouter` rows move to `moonshotai/kimi-k2.6` / Little. Rows on the 12 removed models are listed and left alone. Direct-model rows (`claude`, `kimi-k2.6`, `deepseek-v4`) keep their model and size. The default is a dry run, and `--apply` writes. The old→new map is a literal snapshot inside the script, so later catalog edits can't change what this migration does. No product code changes.

## Scope gate

The one row in **Files Changed** is the file this ticket's `## Scope` names, and the stage is the kind of change Scope describes ("a new CLI", dry run by default, `--apply` sets `mode` and rewrites OpenRouter `brain_setting` plus the Kimi fold, literal snapshot table, run-once docstring).

- **Preconditions (ticket § What this implements, "After #1 and #2"):** on this sub, `ftr` already carries AST-1947 (catalog, `AGENT_MODE_*`, `validate_agent_mode`) and AST-1948 (agent `mode TEXT` column, added nullable by `_ensure_agent_schema`, whose comment says *"no mode / brain_setting content backfills on ensure (AST-1950 sets starting modes)"*). This script does no DDL. If the `mode` column is missing, SQLite's own `no such column: mode` error stops it, before any write.
- **Canon:** none in scope. No `logger` is added. The script reports with `print`, like `retarget_artifact_chain_trigger_state.py`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `scripts/migrations/remap_openrouter_agents.py` | **New.** Run-once CLI: `REMAP` snapshot (64 rows), `REMOVED` (12 slugs), `main(argv=None) -> int` | scripts |

No other file is touched. No `tests/` or bible edits; Betty owns those (see **Tests expected to move**).

## Snapshot source (for reviewers)

The pre-epic catalog is `origin/dev:src/utils/config.py` (AST-1938), loaded as a module on 2026-10-03, and compared with this sub's AST-1947 catalog:

- **Pre-epic OpenRouter model ids: 76.** That's 75 `OPENROUTER_MODEL_TABLE` rows plus the hand-written `kimi-k2.6-openrouter`. The table's `moonshotai/kimi-k2.6` row was skipped by the old builder (`kimi-k2.6-openrouter` already priced that SKU), so no pre-epic model id `moonshotai/kimi-k2.6` exists.
- **63 keep their slug.** Each maps to `(slug, <its one AST-1947 size>)`, taken from `model_brain_sizes(slug)[0]` on this sub.
- **1 fold:** `kimi-k2.6-openrouter` → `("moonshotai/kimi-k2.6", "Little")`.
- **12 removed** (no AST-1946 row). These match AST-1947's removed list exactly.
- 63 + 1 + 12 = 76, so every pre-epic OpenRouter id is in exactly one of `REMAP` / `REMOVED`.
- **Direct models:** `claude`, `kimi-k2.6`, `deepseek-v4`. These ids are the same before and after, and they're in neither table.
- **AC 13 spot values in the snapshot:** `qwen/qwen3-32b` → Medium, `gryphe/mythomax-l2-13b` → Big, `morph/morph-v3-large` ∈ `REMOVED`.
- 31 slugs are new in AST-1946. No pre-epic row can sit on them, so they are not in `REMAP`. A row saved on one after deploy is already valid and is passed through untouched.

---

## Stage 1: Run-once remap CLI

**Done when:** `scripts/migrations/remap_openrouter_agents.py` exists. A dry run against a temp DB seeded with AC 13's eight rows prints the planned changes, lists `morph/morph-v3-large` as removed, and writes nothing. `--apply` produces exactly AC 13's rows, and a second `--apply` reports `No agent rows to change.`

1. Create `scripts/migrations/remap_openrouter_agents.py` with **exactly** the content below. Splice the `REMAP` block verbatim. Its 63 kept-slug rows are in alphabetical order, followed by the Kimi fold row.

```python
#!/usr/bin/env python3
"""Remap agent rows onto the AST-1946 catalog: starting modes, new OpenRouter sizes, Kimi fold.

Run once per environment, right after the AST-1946 deploy (needs the agent `mode` column
from AST-1948). Default is a dry run that prints every planned change and every row on a
removed model; --apply writes. Idempotent: a second run finds nothing to change.

  1. mode: every row with no mode gets Big -> Creative, else Deterministic, judged on the
     row's brain_setting before remap.
  2. OpenRouter rows: brain_setting moves to the slug's one new size; kimi-k2.6-openrouter
     rows move to moonshotai/kimi-k2.6 / Little.
Rows on removed models and direct-model rows keep their model and size.

Usage:
  python scripts/migrations/remap_openrouter_agents.py
  python scripts/migrations/remap_openrouter_agents.py --apply
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.data.database import _get_connection
from src.utils.config import AGENT_MODE_CREATIVE, AGENT_MODE_DETERMINISTIC, BRAIN_BIG

# Snapshot 2026-10-03: pre-epic OpenRouter model id -> (AST-1946 model id, its one brain size).
# Literal on purpose: later catalog edits must not change what this one-time remap does.
REMAP = {
    "bytedance-seed/seed-1.6": ("bytedance-seed/seed-1.6", "Medium"),
    "bytedance-seed/seed-1.6-flash": ("bytedance-seed/seed-1.6-flash", "Medium"),
    "bytedance-seed/seed-2-1-turbo": ("bytedance-seed/seed-2-1-turbo", "Medium"),
    "bytedance-seed/seed-2.0-code": ("bytedance-seed/seed-2.0-code", "Medium"),
    "bytedance-seed/seed-2.0-lite": ("bytedance-seed/seed-2.0-lite", "Medium"),
    "bytedance-seed/seed-2.0-mini": ("bytedance-seed/seed-2.0-mini", "Medium"),
    "deepseek/deepseek-chat-v3-0324": ("deepseek/deepseek-chat-v3-0324", "Medium"),
    "deepseek/deepseek-chat-v3.1": ("deepseek/deepseek-chat-v3.1", "Little"),
    "deepseek/deepseek-r1-0528": ("deepseek/deepseek-r1-0528", "Medium"),
    "deepseek/deepseek-v3.1-terminus": ("deepseek/deepseek-v3.1-terminus", "Medium"),
    "deepseek/deepseek-v3.2": ("deepseek/deepseek-v3.2", "Medium"),
    "deepseek/deepseek-v3.2-exp": ("deepseek/deepseek-v3.2-exp", "Medium"),
    "deepseek/deepseek-v4-flash": ("deepseek/deepseek-v4-flash", "Medium"),
    "deepseek/deepseek-v4-flash-0731": ("deepseek/deepseek-v4-flash-0731", "Medium"),
    "deepseek/deepseek-v4-flash-vision-exp": ("deepseek/deepseek-v4-flash-vision-exp", "Medium"),
    "deepseek/deepseek-v4.1-flash": ("deepseek/deepseek-v4.1-flash", "Little"),
    "google/gemma-3-27b-it": ("google/gemma-3-27b-it", "Medium"),
    "google/gemma-4-26b-a4b-it": ("google/gemma-4-26b-a4b-it", "Medium"),
    "google/gemma-4-31b-it": ("google/gemma-4-31b-it", "Little"),
    "gryphe/mythomax-l2-13b": ("gryphe/mythomax-l2-13b", "Big"),
    "meta-llama/llama-3.1-70b-instruct": ("meta-llama/llama-3.1-70b-instruct", "Medium"),
    "meta-llama/llama-3.3-70b-instruct": ("meta-llama/llama-3.3-70b-instruct", "Medium"),
    "meta-llama/llama-4-maverick": ("meta-llama/llama-4-maverick", "Medium"),
    "meta-llama/llama-4-scout": ("meta-llama/llama-4-scout", "Medium"),
    "mistralai/mistral-nemo": ("mistralai/mistral-nemo", "Medium"),
    "mistralai/mistral-small-24b-instruct-2501": ("mistralai/mistral-small-24b-instruct-2501", "Medium"),
    "mistralai/mistral-small-3.2-24b-instruct": ("mistralai/mistral-small-3.2-24b-instruct", "Medium"),
    "moonshotai/kimi-k2-0905": ("moonshotai/kimi-k2-0905", "Medium"),
    "nousresearch/hermes-3-llama-3.1-70b": ("nousresearch/hermes-3-llama-3.1-70b", "Medium"),
    "nvidia/nemotron-3-nano-30b-a3b": ("nvidia/nemotron-3-nano-30b-a3b", "Medium"),
    "nvidia/nemotron-3-super-120b-a12b": ("nvidia/nemotron-3-super-120b-a12b", "Medium"),
    "openai/gpt-oss-120b": ("openai/gpt-oss-120b", "Big"),
    "openai/gpt-oss-20b": ("openai/gpt-oss-20b", "Little"),
    "qwen/qwen-2.5-72b-instruct": ("qwen/qwen-2.5-72b-instruct", "Medium"),
    "qwen/qwen3-14b": ("qwen/qwen3-14b", "Little"),
    "qwen/qwen3-235b-a22b-2507": ("qwen/qwen3-235b-a22b-2507", "Medium"),
    "qwen/qwen3-30b-a3b": ("qwen/qwen3-30b-a3b", "Medium"),
    "qwen/qwen3-30b-a3b-instruct-2507": ("qwen/qwen3-30b-a3b-instruct-2507", "Medium"),
    "qwen/qwen3-32b": ("qwen/qwen3-32b", "Medium"),
    "qwen/qwen3-coder-30b-a3b-instruct": ("qwen/qwen3-coder-30b-a3b-instruct", "Medium"),
    "qwen/qwen3-next-80b-a3b-instruct": ("qwen/qwen3-next-80b-a3b-instruct", "Medium"),
    "qwen/qwen3-vl-235b-a22b-instruct": ("qwen/qwen3-vl-235b-a22b-instruct", "Medium"),
    "qwen/qwen3-vl-30b-a3b-instruct": ("qwen/qwen3-vl-30b-a3b-instruct", "Medium"),
    "qwen/qwen3.5-27b": ("qwen/qwen3.5-27b", "Medium"),
    "qwen/qwen3.5-35b-a3b": ("qwen/qwen3.5-35b-a3b", "Medium"),
    "qwen/qwen3.5-397b-a17b": ("qwen/qwen3.5-397b-a17b", "Medium"),
    "qwen/qwen3.5-9b": ("qwen/qwen3.5-9b", "Big"),
    "qwen/qwen3.6-27b": ("qwen/qwen3.6-27b", "Medium"),
    "qwen/qwen3.6-35b-a3b": ("qwen/qwen3.6-35b-a3b", "Medium"),
    "qwen/qwen3.8-27b": ("qwen/qwen3.8-27b", "Medium"),
    "stepfun/step-3.7-flash": ("stepfun/step-3.7-flash", "Medium"),
    "tencent/hunyuan-a13b-instruct": ("tencent/hunyuan-a13b-instruct", "Medium"),
    "tencent/hy-mt2-30b-a3b": ("tencent/hy-mt2-30b-a3b", "Medium"),
    "tencent/hy-mt2-7b": ("tencent/hy-mt2-7b", "Medium"),
    "thedrummer/skyfall-36b-v2": ("thedrummer/skyfall-36b-v2", "Medium"),
    "undi95/remm-slerp-l2-13b": ("undi95/remm-slerp-l2-13b", "Medium"),
    "xiaomi/mimo-v2.5": ("xiaomi/mimo-v2.5", "Medium"),
    "xiaomi/mimo-v2.6-flash": ("xiaomi/mimo-v2.6-flash", "Medium"),
    "xiaomi/mimo-v2.6-pro": ("xiaomi/mimo-v2.6-pro", "Medium"),
    "z-ai/glm-4.7-flash": ("z-ai/glm-4.7-flash", "Medium"),
    "z-ai/glm-5.2": ("z-ai/glm-5.2", "Medium"),
    "z-ai/glm-5.3": ("z-ai/glm-5.3", "Medium"),
    "z-ai/glm-5.3-flash": ("z-ai/glm-5.3-flash", "Little"),
    "kimi-k2.6-openrouter": ("moonshotai/kimi-k2.6", "Little"),
}
# Pre-epic OpenRouter models with no AST-1946 row: listed for the operator, never rewritten.
REMOVED = (
    "anthracite-org/magnum-v4-72b",
    "deepseek/deepseek-v4-pro",
    "deepseek/deepseek-v4-pro-0813",
    "moonshotai/kimi-k3",
    "morph/morph-v3-large",
    "nousresearch/hermes-3-llama-3.1-405b",
    "qwen/qwen2.5-vl-72b-instruct",
    "qwen/qwen3.8-2.4t-a95b",
    "sao10k/l3.1-euryale-70b",
    "tencent/hy4-preview",
    "z-ai/glm-5",
    "z-ai/glm-5.1",
)


def main(argv=None) -> int:
    apply = "--apply" in (sys.argv[1:] if argv is None else argv)
    conn = _get_connection()
    rows = conn.execute(
        "SELECT agent_id, model_id, brain_setting, mode FROM agent ORDER BY agent_id"
    ).fetchall()
    changes = []
    for agent_id, model_id, brain_setting, mode in rows:
        # Starting mode is judged on the size the row had before the remap below.
        new_mode = mode or (AGENT_MODE_CREATIVE if brain_setting == BRAIN_BIG else AGENT_MODE_DETERMINISTIC)
        # Removed / direct / post-deploy rows are not in REMAP, so they keep model and size.
        new_model_id, new_brain = REMAP.get(model_id, (model_id, brain_setting))
        if model_id in REMOVED:
            print(f"  removed model: {agent_id} on {model_id} ({brain_setting}), left as-is")
        if (new_model_id, new_brain, new_mode) != (model_id, brain_setting, mode):
            print(f"  {agent_id}: {model_id}/{brain_setting}/{mode} -> {new_model_id}/{new_brain}/{new_mode}")
            changes.append((new_model_id, new_brain, new_mode, agent_id))

    if not changes:
        print("No agent rows to change.")
    elif not apply:
        print(f"\n{len(changes)} row(s) would change. Re-run with --apply to commit.")
    else:
        conn.executemany(
            """UPDATE agent SET model_id = ?, brain_setting = ?, mode = ?, updated_at = CURRENT_TIMESTAMP
               WHERE agent_id = ?""",
            changes,
        )
        conn.commit()
        print(f"\nUpdated {len(changes)} row(s).")
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

⚠️ **Decision: DB seam is a module-level `from src.data.database import _get_connection`, not a `--db` flag and not a hard-coded `sqlite3.connect(ASTRAL_CONFIG["db_dir"] / "astral.db")`.** This matches the tested precedent `cleanup_duplicate_and_board_gaze_jobs.py`, whose component test does `monkeypatch.setattr(_mod, "_get_connection", …)` onto a temp DB. AC 13 is a temp-DB component test, so Betty gets that seam without the script adding an operator flag. The module-level-only style of `retarget_artifact_chain_trigger_state.py` would run on import and can't be pointed at a temp DB.

⚠️ **Decision: `main(argv=None)` reads `--apply` from `argv` when given, else `sys.argv[1:]`.** The flag name is `--apply` (ticket Scope), not `--execute`. No argparse: one flag, same as the convention script. The test calls `_mod.main([])` / `_mod.main(["--apply"])`.

⚠️ **Decision: unpack rows by position.** `_get_connection` sets `row_factory = sqlite3.Row`, which unpacks positionally. A test's plain `sqlite3.connect` returns tuples, which unpack the same way.

⚠️ **Decision: "has no mode" means NULL or empty string** (`mode or …`). Rows that already have a mode keep it. Size remap and mode fill are independent: a row with a mode set still gets its size remapped.

⚠️ **Decision: no post-apply validation pass in the script.** The ticket Scope lists two `--apply` effects and no validation step. AC 13's "every non-removed row passes model + size + mode validation" is a test assertion. It holds by construction because every `REMAP` target is checked against the catalog in § Verification step 2.

## Verification (build-child, before the commit)

Run from the repo root on the epic worktree. Write throwaway scripts to `/tmp`, never `tests/`.

1. `python3 -m py_compile scripts/migrations/remap_openrouter_agents.py`. Then lint with ruff (`ruff check --select F,E9 scripts/migrations/remap_openrouter_agents.py`; if ruff isn't on the host, use a throwaway `pip install --target /tmp/ruffenv ruff`).
2. **Snapshot check** (`PYTHONPATH=.`). Load the script with `importlib.util.spec_from_file_location` (no `main()` call) and assert:
   - `len(REMAP) == 64` and `len(REMOVED) == 12`;
   - for every `REMAP` value `(m, b)`: `validate_brain_setting_for_model(m, b)` does not raise and `model_brain_sizes(m) == (b,)`;
   - no `REMOVED` slug is in `LLM_MODEL_CONFIG`;
   - `set(REMAP) | set(REMOVED)` equals the 76 pre-epic OpenRouter ids from `origin/dev:src/utils/config.py`. Load it via `git show origin/dev:src/utils/config.py > /tmp/devcfg.py`, set `ASTRAL_DB_DIR` from this sub's `ASTRAL_CONFIG["db_dir"]` if it's unset, then load it with `spec_from_file_location`. The ids are `{k for k, m in LLM_MODEL_CONFIG.items() if m["server"] == "openrouter"}`.
3. **AC 13 smoke on a temp DB** (`PYTHONPATH=.`, in `/tmp`):
   - Create `agent(agent_id TEXT PRIMARY KEY, content TEXT, model_id TEXT, brain_setting TEXT, mode TEXT, max_tokens INTEGER, updated_at TIMESTAMP)` in a `tempfile` SQLite file.
   - Seed AC 13's eight rows with `mode` NULL, agent ids `a1`…`a8` in AC order.
   - Load the module and set `mod._get_connection = lambda: sqlite3.connect(path)`.
   - `main([])`: the table is byte-for-byte unchanged and stdout contains `morph/morph-v3-large`.
   - `main(["--apply"])`: rows equal AC 13's expected list.
   - Every non-`REMOVED` row passes `validate_brain_setting_for_model` + `validate_agent_mode`.
   - A second `main(["--apply"])` prints `No agent rows to change.`
4. `git diff --name-only` shows only `scripts/migrations/remap_openrouter_agents.py` (new file: `git status --short`).

## Tests expected to move (Betty, `qa-child`)

- **New:** a component test for AC 13 under `tests/component/scripts/`, following `test_cleanup_duplicate_and_board_gaze_jobs.py`: `importlib` load plus `monkeypatch.setattr(_mod, "_get_connection", …)` onto a temp DB. Seed the eight AC rows without `mode`; run the dry run (no writes, `morph/morph-v3-large` listed); run `--apply` (exact rows); validate the non-removed rows.
- **Existing:** none expected to break. No product file changes.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1950
**Overall:** APPROVED
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Publish ref:** `origin/sub/AST-1946/AST-1950-remap-migration` @ `2da2a906ab76b90783cf0dcbb0ab8010f216e1b4`

## Canon scores
(none — ticket § Citations and plan Canon Scope explicitly empty; `scripts/` outside frozen `src/**` statutes)

## Traceability
**AC13** → Stage 1 full script + Verification steps 2–3 (dry run no writes, `morph/morph-v3-large` listed, `--apply` row matrix, idempotent second run, non-removed validation via `validate_brain_setting_for_model` + `validate_agent_mode`); Betty component test per **Tests expected to move**. Parent **AC11** item 1 (starting mode from pre-remap brain size) → `new_mode` before `REMAP.get`; item 2 (OpenRouter size + Kimi fold) → `REMAP`; item 3 (removed listed, model/size untouched) → `REMOVED` branch + Scope. **AC1–12** → N/A — sibling / epic scope.

## Findings

### discuss
- **Severity:** discuss  
  **Location:** Stage 1 — `_get_connection` vs `retarget_artifact_chain_trigger_state.py`  
  **Finding:** Plan deliberately diverges from the older hard-coded `ASTRAL_CONFIG` connect pattern in favor of `cleanup_duplicate_and_board_gaze_jobs.py` monkeypatch seam for AC 13.  
  **Recommendation:** Keep; note for operators: default run uses the same DB as the app, not a path flag.

- **Severity:** discuss  
  **Location:** Stage 1 loop — removed-model rows  
  **Finding:** Parent item 11 “left unchanged” is model/size only; AC 13 still sets `mode` on `morph/morph-v3-large` (Deterministic). Script matches AC, not a literal read of “unchanged” as “no UPDATE”.  
  **Recommendation:** No plan change; operator output should make clear removed slugs are not remapped.

### acceptable
- **Severity:** acceptable  
  **Location:** Verification step 2 — `git show origin/dev:src/utils/config.py`  
  **Finding:** 76-id closure proof depends on dev tip at run time; publish ref alone is insufficient.  
  **Recommendation:** Run snapshot check on the machine that builds; failure there blocks commit per plan.

context_tokens≈56000

## Review

- **Branch:** `origin/sub/AST-1946/AST-1950-remap-migration`
- **Build tip:** `f47ec6df2` (`code(AST-1950)`: new `scripts/migrations/remap_openrouter_agents.py`, spliced verbatim from Stage 1, mode `100644` like 11 of the 12 sibling migration scripts).
- **Verified on the shipped file:** `py_compile` and `ruff check --select F,E9` clean. § Verification step 2: 64 `REMAP` / 12 `REMOVED`, every target passes `validate_brain_setting_for_model` with `model_brain_sizes == (size,)`, no removed slug in the catalog, and `REMAP ∪ REMOVED` equals the 76 OpenRouter ids on `origin/dev`. Step 3: on a temp DB with AC 13's eight rows, the dry run writes nothing and lists `morph/morph-v3-large`, `--apply` yields AC 13's rows exactly, non-removed rows pass model + size + mode validation, and a second `--apply` prints `No agent rows to change.`
- **Joan's discuss items:** both say keep the plan as written; built unchanged. The default run uses the app's DB via `_get_connection` (no path flag). Removed-model rows still get a starting `mode`, and the output prints `removed model: … left as-is` for each.
- **Git note:** this ref also carries `85e7b9026` (`docs(AST-1949)` plan). A sibling agent switched this shared worktree onto AST-1949 between plan-child's sync and commit. It is the same commit already on AST-1949's ref, so the ftr merge is a no-op for it; not force-pushed.
- **For qa-child:** new AC 13 component test under `tests/component/scripts/`, per § Tests expected to move. No existing test should move.

## Radia review

[code-rubric]
**Ticket:** AST-1950
**Publish ref:** `41d48e82f6b919eeb359de467d07855e1522e55e` (`origin/sub/AST-1946/AST-1950-remap-migration`)
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Overall:** CLEAN

## Canon scores
(none — frozen Citations / Canon Scope explicitly empty; no directives to score)

## Column diff vs plan stage
(aligned) — Joan: empty canon list; plan **APPROVED** with two **discuss** items (keep `_get_connection` seam; removed rows still receive starting `mode`). Shipped script matches Stage 1 verbatim; tests encode AC 13 and Joan’s decisions.

## Frame diff
- [ ] **Operator:** After AST-1946 deploy on each environment, run `python scripts/migrations/remap_openrouter_agents.py` (dry run), then `--apply` once; document in runbook that there is no `--db` flag (uses app `_get_connection`).
- [x] **Snapshot closure (build-time):** Before first production apply, confirm `REMAP ∪ REMOVED` equals 76 pre-epic OpenRouter ids from `origin/dev:src/utils/config.py` (plan § Verification step 2; not in component test once epic lands on `dev`).

## Findings

### fix-now
(none)

### discuss
- **Severity:** discuss  
  **Location:** Joan plan finding — removed-model rows  
  **Finding:** Rows on `REMOVED` slugs keep `model_id` / `brain_setting` but still receive a starting `mode` when NULL/empty (AC 13: `morph/morph-v3-large` → Deterministic). Parent “left unchanged” means model/size only; script and tests match AC, not a literal “no UPDATE.”  
  **Default:** Keep behavior; operator stdout already prints `removed model: … left as-is` before any change line.

- **Severity:** discuss  
  **Location:** `_get_connection` seam vs `retarget_artifact_chain_trigger_state.py`  
  **Finding:** Default CLI run mutates the same DB as the running app (no path flag). Matches `cleanup_duplicate_and_board_gaze_jobs.py` precedent and enables AC 13 temp-DB tests via monkeypatch.  
  **Default:** Keep; ops must not run `--apply` against the wrong environment.

### advisory
- **Three-dot diff vs ticket scope:** `origin/dev...origin/sub/AST-1946/AST-1950-remap-migration` includes the full AST-1946 epic (#1–#3 product + tests). AST-1950’s **product** delta is only `scripts/migrations/remap_openrouter_agents.py` (`f47ec6df2`); tip `41d48e82f` adds Betty’s `tests/component/scripts/test_remap_openrouter_agents.py` and `docs/test-bible/dev/remap_openrouter_agents.md`. Not cross-ticket product smuggling.
- **Branch history:** `85e7b9026` (`docs(AST-1949)` plan) sits on this ref from shared worktree timing; no AST-1949 product files in the 1950 code/test delta.
- **Idempotent second run:** stdout still prints the `removed model:` line for rows on `REMOVED` even when `changes` is empty (test `test_second_apply_changes_nothing` locks this). Noisy but intentional.
- **Estimate:** Confirm **2** — script + focused component test; footprint fits.

## What's solid
- **Plan fidelity:** `REMAP` (64) / `REMOVED` (12), mode-before-remap rule (`new_mode` before `REMAP.get`), Kimi fold, dry-run default, `--apply` idempotency, `print`-only reporting, run-once docstring — match Stage 1.
- **AC 13:** Component tests cover dry run (no writes + `morph/morph-v3-large`), apply matrix (including Kimi Big → Creative on pre-remap size), validation on non-removed rows, second apply no-op, kept-mode + blank-mode edge cases, catalog snapshot integrity.
- **Spot checks on workspace:** `py_compile` clean; snapshot loop (`model_brain_sizes`, `validate_brain_setting_for_model`, removed ∉ catalog) passes.

## Recommended actions (downstream — not Radia)
- Chuckles: append artifact, `docs(AST-1950): Radia review — clean`, push, post slim upshot `--as radia`, **Review Posted** → datt **PROCEED**.
- **finish-up / ops:** Run migration once per env after #1–#2 deploy; keep dry-run transcript for removed-model agents.
- **No resolve-child** unless Susan wants runbook rows in Frame diff copied into Description.

context_tokens≈18000

## Resolution

- **Date:** 2026-10-03. **Reviewed tip:** `41d48e82f` (review commit `97a719b98`). No product change in resolve.
- **Fix-now:** none.
- **Discuss (removed-model rows still get a starting `mode`):** no Susan answer in thread, so Radia's `Default:` applies. Behavior kept: model and size untouched, mode filled, and stdout prints `removed model: … left as-is`.
- **Discuss (`_get_connection` seam, no `--db` flag):** Radia's `Default:` applies. Kept. The CLI writes to the app's own DB, so operators must run `--apply` only on the intended environment.
- **Frame diff, snapshot closure:** ticked. Rechecked on this tip: `REMAP ∪ REMOVED` equals the 76 OpenRouter ids in `origin/dev:src/utils/config.py`.
- **Frame diff, operator run:** left unchecked on purpose. It is a post-deploy step (dry run, then `--apply` once per environment) for finish-up / ops, not something this sub can validate.
- **Advisory:** nothing to act on. The noisy `removed model:` line on an idempotent rerun is intentional and locked by `test_second_apply_changes_nothing`.
