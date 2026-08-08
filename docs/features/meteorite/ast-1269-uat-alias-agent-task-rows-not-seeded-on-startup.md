# UAT: alias agent_task rows not seeded on startup

**Linear:** [AST-1269](https://linear.app/astralcareermatch/issue/AST-1269/uat-alias-agent-task-rows-not-seeded-on-startup)  
**Parent:** [AST-1184](https://linear.app/astralcareermatch/issue/AST-1184/task-config-aliases-via-master-task-key)  
**Publish ref:** `sub/AST-1184/AST-1269-uat-alias-agent-task-rows-not-seeded-on-startup`

Config already declares `meteorite_grade_do` / `meteorite_grade_get` (`master_task_key` → `grade_do` / `grade_get`) and meteorite dispatch is retargeted to those aliases, but startup seed from `data/admin/agent_task.json` does not materialize the alias catalog identities. Operators never see current `agent_task` rows for the aliases, so Meteorite Review grouping / Admin surfaces cannot host them. Restore the grouping-only seed rows AST-1222 shipped; do **not** invent resolve helpers, prompt bodies on the alias, or a parallel seed path.

## UAT fitness

- **AC restored:**  
  > Alias identities have `agent_task` grouping metadata that can place them under Meteorite Review (or the live meteorite section name) independently of the master's Gaze Review grouping.  
  > Editing the master's prompts changes what the alias runs; the alias has no divergent prompt row.  
  > Admin task-key listings that are config/DB-driven include the new alias keys (alphabetical / catalog behavior refinements remain **AST-1185**).
- **Correct outcome:** After startup (and Revert-to-file), both `meteorite_grade_do` and `meteorite_grade_get` exist as **current** `agent_task` rows under **Meteorite Review** / `"4500"` with empty prompts / empty `run_next` / `agent_id: "n/a"`; prompts stay on the master rows only.
- **Sibling check:** **AST-1220** alias `TASK_CONFIG` + resolve helpers remain on tip (verified `master_task_key` entries present). **AST-1221** runtime resolve remains the prompt path — this ticket does not touch `agent.py` / `consult.py`. **AST-1222** field tables + pinned UUIDs are the seed contract to restore. **AST-1183** Meteorite Review naming — seed aliases into **Meteorite Review** / `"4500"` (same as AST-1222), not Job Review.
- **Not sufficient:** Removing a stacktrace / “missing key” log alone is **not** done — the rows must be present in repo seed so boot materializes them.
- **Wrong fix rejected:** One-off live-DB `INSERT`; inventing a parallel ensure/provision path for alias `agent_task` rows; copying `grade_do` / `grade_get` prompt bodies onto the alias; hardcoding alias labels in React. Config alias contract alone does not create `agent_task` rows — repo JSON is the SoT (`astral.seed.agent-tables-in-repo-json`).

⚠️ **Decision — root cause is catalog wipe, not missing AST-1222 code on ftr:** On `origin/dev`, `resolve(AST-1239): — unify api_surfer pacing+consent (no pull-merge)` (`1da37a40`) replaced `data/admin/agent_task.json` with an older Job Review–shaped catalog and dropped `meteorite_grade_do` / `meteorite_grade_get` (also lost `meteorite_email` and the Meteorite Review / Gaze Review group names). Config + `METEORITE_DISPATCH_TASKS` alias retarget from AST-1220/1222 remain. This UAT child restores **only** the two alias seed identities AST-1222 owns. It does **not** re-run AST-1183/1218/1219 (full Gaze/Meteorite Review membership reshuffle) or rename `parse_meteorite_email` → `meteorite_email` — file a separate UAT if Susan wants that broader seed repair.

⚠️ **Decision — seed under Meteorite Review even though other meteorite twins currently sit under Job Review on land tip:** Parent AC requires alias grouping **independent** of the master's section. Place aliases under **Meteorite Review** / `"4500"` with AST-1222 pinned UUIDs and seq `5`/`6`. Do **not** park them under Job Review next to the regressed twins — that would fail the independence AC. Do **not** move/rename other meteorite rows in this ticket.

⚠️ **Decision — fixture already correct; catalog-only edit:** `docs/uat-fixtures/AST-756/expected-agent_task.json` on land tip already carries the AST-1222 alias rows (UUIDs, Meteorite Review / `"4500"`, seq 5/6, empty prompts). Stage 1 edits **only** `data/admin/agent_task.json`. Verify fixture lockstep for those two keys; do **not** `cp` catalog→fixture and do **not** reconcile unrelated Job Review vs Meteorite Review drift in the fixture.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `data/admin/agent_task.json` | Append current grouping-only `meteorite_grade_do` / `meteorite_grade_get` rows (AST-1222 field tables) | data/admin |

**Out of this ticket’s file list (do not touch):** `src/utils/config.py`, `src/core/dispatcher.py`, `src/core/agent.py`, `src/core/consult.py`, UI / React, `tests/` / bible (Betty), unrelated meteorite twin regrouping / `meteorite_email` rename.

### QA note (Betty — coverage that will break)

| Area | What breaks / revise |
|------|----------------------|
| `tests/component/core/test_repo_admin_json.py` | Any pin of current catalog count `50` → **`52`** after aliases land; classes that assert alias absence or omit aliases from expected key sets |
| `TestAst1222MeteoriteGradeAliasCatalogRows` (or successor) | Should pass once catalog rows match fixture for the two keys; if renamed/removed after AST-1239 wipe, restore or revise to assert grouping-only seed shape |
| `TestAst786…` / `TestAst1211…` / Meteorite membership classes | May still encode pre-wipe (55 / eight-key Meteorite Review) or post-wipe (50 / Job Review) assumptions — revise only what this seed delta invalidates; do **not** treat full Gaze/Meteorite reshuffle as in-scope for this bug |
| AST-756 fixture | Already has aliases — prefer asserts that the two keys lockstep catalog↔fixture; avoid forcing full-file equality while Job Review vs Meteorite Review drift remains |

## Stage 1: Restore alias `agent_task` seed rows

**Done when:** `data/admin/agent_task.json` has current rows for `meteorite_grade_do` and `meteorite_grade_get` matching the field tables below; fixture already matches those two keys (verify only); classic Gaze / Job Review `grade_do` / `grade_get` prompt rows are untouched; no prompt text on the aliases; `json.dump(..., indent=2, ensure_ascii=False)` + trailing newline; current catalog count is **52**.

1. Snapshot before edit (local `/tmp` only — do not commit):

```bash
cp data/admin/agent_task.json /tmp/agent_task.pre-ast-1269.json
```

2. Confirm land-tip preconditions (stop + comment on **AST-1269** if any fail — do not invent rows under a different contract):

```bash
~/astral/.venv/bin/python - <<'PY'
import json
from pathlib import Path
import src.utils.config as c

assert c.is_task_alias("meteorite_grade_do") and c.is_task_alias("meteorite_grade_get")
assert c.resolve_task_key_for_content("meteorite_grade_do") == "grade_do"
assert c.resolve_task_key_for_content("meteorite_grade_get") == "grade_get"
assert ("meteorite_grade_do", "METEORITE_PASSED_JD") in {
    (e["task_key"], e["trigger_state"]) for e in c.METEORITE_DISPATCH_TASKS
}
cat = json.loads(Path("data/admin/agent_task.json").read_text())
keys = {r["task_key"] for r in cat if r.get("current") in (1, "1", True)}
assert "meteorite_grade_do" not in keys and "meteorite_grade_get" not in keys
print("preconditions OK; aliases absent from seed")
PY
```

3. In `data/admin/agent_task.json`, append **two** new objects (same field set as other rows). Use these exact identities (pinned from AST-1222 — do not mint new UUIDs):

**`meteorite_grade_do`:**

| Field | Value |
|-------|-------|
| `task_key_uuid` | `47e47cc0-26b8-4af6-81d6-f9e080b2b712` |
| `task_key` | `meteorite_grade_do` |
| `task_name` | `meteorite_grade_do` |
| `agent_id` | `n/a` |
| `task_group_name` | `Meteorite Review` |
| `task_group_order` | `"4500"` |
| `task_seq` | `5` |
| `current` | `1` |
| `run_next` | `""` |
| `system_prompt` | `""` |
| `cache_prompt` | `""` |
| `cache_prompt_b` | `""` |
| `cache_prompt_c` | `""` |
| `cache_prompt_d` | `""` |
| `nocache_prompt` | `""` |
| `user_prompt` | `""` |
| `updated_at` | `2026-08-06 08:00:00` |

**`meteorite_grade_get`:**

| Field | Value |
|-------|-------|
| `task_key_uuid` | `357b56de-20a6-4360-a98e-d4527db40b7f` |
| `task_key` | `meteorite_grade_get` |
| `task_name` | `meteorite_grade_get` |
| `agent_id` | `n/a` |
| `task_group_name` | `Meteorite Review` |
| `task_group_order` | `"4500"` |
| `task_seq` | `6` |
| `current` | `1` |
| `run_next` | `""` |
| all prompt fields | `""` |
| `updated_at` | `2026-08-06 08:00:00` |

Do **not** add `master_task_key` to the JSON row (that field lives on `TASK_CONFIG` only). Do **not** edit classic `grade_do` / `grade_get` rows. Do **not** bump `meteorite_like` / `meteorite_upshot` seqs (they currently live under Job Review on this tip — out of scope). Do **not** remove or rename `parse_meteorite_email`.

4. Rewrite with a surgical Python edit that loads, appends by exact tables above, and dumps with `json.dump(..., indent=2, ensure_ascii=False)` + trailing newline. Prefer leaving unrelated rows byte-stable aside from necessary re-serialize; **require** `ensure_ascii=False` so this touch does not reintroduce `\u2014` noise (AST-1252 advisory).

5. Verify (catalog + fixture lockstep for the two keys only):

```bash
~/astral/.venv/bin/python - <<'PY'
import json
from pathlib import Path
import src.utils.config as c

ALIAS_UUID = {
    "meteorite_grade_do": "47e47cc0-26b8-4af6-81d6-f9e080b2b712",
    "meteorite_grade_get": "357b56de-20a6-4360-a98e-d4527db40b7f",
}
PROMPT_FIELDS = (
    "system_prompt", "cache_prompt", "cache_prompt_b", "cache_prompt_c",
    "cache_prompt_d", "nocache_prompt", "user_prompt",
)
METEORITE_ALIAS_SEQ = {"meteorite_grade_do": 5, "meteorite_grade_get": 6}

def load(path):
    rows = json.loads(Path(path).read_text())
    cur = [r for r in rows if r.get("current") in (1, "1", True)]
    by = {r["task_key"]: r for r in cur}
    return cur, by

cat_rows, cat = load("data/admin/agent_task.json")
fix_rows, fix = load("docs/uat-fixtures/AST-756/expected-agent_task.json")
assert len(cat) == 52, len(cat)

for key, seq in METEORITE_ALIAS_SEQ.items():
    r = cat[key]
    assert r["task_key_uuid"] == ALIAS_UUID[key]
    assert r["task_name"] == key
    assert r["agent_id"] == "n/a"
    assert r["task_group_name"] == "Meteorite Review"
    assert r["task_group_order"] == "4500"
    assert r["task_seq"] == seq
    assert r.get("run_next") == ""
    assert all((r.get(f) or "") == "" for f in PROMPT_FIELDS)
    # fixture lockstep for alias identity + grouping (prompts already empty both sides)
    f = fix[key]
    for field in (
        "task_key_uuid", "task_name", "agent_id", "task_group_name",
        "task_group_order", "task_seq", "run_next",
    ) + PROMPT_FIELDS:
        assert r.get(field) == f.get(field), (key, field, r.get(field), f.get(field))

# masters still have prompts; aliases do not own content
assert any((cat["grade_do"].get(f) or "").strip() for f in PROMPT_FIELDS)
assert c.resolve_task_key_for_content("meteorite_grade_do") == "grade_do"
assert c.dispatch_task_grouping_catalog_key("meteorite_grade_do") == "meteorite_grade_do"
assert "meteorite_grade_do" in c.get_task_keys() and "meteorite_grade_get" in c.get_task_keys()
print("AST-1269 seed verify OK")
PY
```

**Ritual:** `code(AST-1269): restore meteorite_grade_do/get agent_task seed rows`

## Self-Assessment

**Scope:** `Single-Component` — one data/admin seed file; restores two grouping-only alias identities AST-1222 already defined.

**Conf:** `high` — exact field tables and UUIDs reused from AST-1222; fixture already holds the target rows; config/dispatch alias contract is already live on tip.

**Risk:** `Medium` — wrong grouping (Job Review) would fail Parent AC; minting new UUIDs or copying prompts would break alias/master content sharing and fixture lockstep; touching unrelated meteorite rows would expand into AST-1183/1212 scope.

## Self-review vs ASTRAL_CODE_RULES

- **`astral.seed.agent-tables-in-repo-json`:** aliases land in repo `data/admin/agent_task.json`; startup/Revert-to-file applies them — no live-DB hand seed.
- **`astral.standards.no-hardcoded-sets`:** no new meteorite-only maps in UI/core; uses existing alias keys.
- **`astral.standards.names-not-ticket-ids`:** domain keys `meteorite_grade_do` / `meteorite_grade_get`.
- **`astral.standards.in-scope-only`:** no resolve-helper / overlay / UI / full section reshuffle.
- **`astral.git.engineer-test-tree-ban`:** no `tests/` / bible edits on this ticket.
- **§1.3 DRY:** reuse AST-1222 row shape; do not invent a second seed mechanism.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1184/AST-1269-uat-alias-agent-task-rows-not-seeded-on-startup`  
**Plan path:** `docs/features/meteorite/ast-1269-uat-alias-agent-task-rows-not-seeded-on-startup.md`

**Built tip:** `df7b6bb685d287e084f86e39486ee5d20c7dfe12` (`df7b6bb6`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `df7b6bb6` | restore meteorite_grade_do/get agent_task seed rows |

## Radia review — [code-rubric] revision=1

**Rubric:** code-rubric.v1 · **Publish ref tip:** `2639368d`

**Overall: CLEAN**

**What's solid:**

- Structural diff confirms exactly two rows added (`meteorite_grade_do` seq 5, `meteorite_grade_get` seq 6, both `Meteorite Review` / `"4500"`), zero rows removed, zero non-prompt field diffs, and zero real content diffs on any existing row's prompt fields — verified by decoding both `origin/dev` and this tip's JSON and comparing every row/field programmatically. The large raw-text diff (~300 lines across dozens of unrelated rows) is exactly the "necessary re-serialize" the plan called out: `ensure_ascii=False` unescaped pre-existing `\u2014` sequences to literal em-dashes file-wide, matching AST-1252's advisory direction — not a content change.
- Both new rows byte-match the plan's field tables and AST-1222's pinned UUIDs (`47e47cc0…`, `357b56de…`); `agent_id: "n/a"`, empty `run_next`, all seven prompt fields empty; fixture (`docs/uat-fixtures/AST-756/expected-agent_task.json`) already lockstep for those two keys (verify-only per plan, confirmed no fixture edit in this diff).
- Ran the plan's own Stage 1 precondition + verify scripts live at tip: alias contract still live (`is_task_alias`, `resolve_task_key_for_content`, `METEORITE_DISPATCH_TASKS` trigger membership), catalog count is exactly 52, catalog↔fixture lockstep for the two alias keys, masters (`grade_do`/`grade_get`) still carry real prompt bodies, `dispatch_task_grouping_catalog_key`/`get_task_keys()` include the aliases. All pass.
- Scope discipline: `code(AST-1269)` touches only `data/admin/agent_task.json` (no `src/utils/config.py`, `dispatcher.py`, `agent.py`, `consult.py`, or UI — exactly the plan's "out of ticket's file list"); `test(AST-1269)`/`merge-tests(AST-1269)` touch only `tests/`/`docs/test-bible/**`. `astral.git.engineer-test-tree-ban` and `astral.git.betty-no-src-or-features` both hold. Trailing newline preserved.
- Betty's test diff is honest about wipe drift: revises pinned counts (50→52), skips (with a shared, descriptive reason constant) the eight classes that still encode pre-AST-1239-wipe Gaze/Meteorite Review membership assumptions rather than silently leaving them red or forcing an out-of-scope reshuffle, and adds a scoped `TestAst1269AliasAgentTaskSeedRestore` plus a revised `TestAst1222MeteoriteGradeAliasCatalogRows`. Ran the new/revised classes (`TestAst1269AliasAgentTaskSeedRestore`, `TestAst1222MeteoriteGradeAliasCatalogRows`, `TestAst786AgentTaskRepoJsonSeed`, `TestAst1055MeteoriteCatalogRows`) live — 9 passed.
- Git hygiene: this ticket's own 5 commits on `origin/sub/...` (`plan → code → docs → test → merge-tests`) carry no `Merge remote-tracking branch` subjects. (Found and discarded stray local-only self-merge commits in my own epic-worktree checkout before reviewing — confirmed empty diff vs origin, reset to the clean origin tip; not part of this ticket's published history.)
- `python3 -m py_compile src/utils/config.py` clean (only `src/` file in the transitive precondition/verify scripts, unchanged by this ticket).
- **No plan-rubric verdict attached** (straggler check, C4) — this bug ticket went Todo → Plan Ready → Plan Approved with no Joan comment. Not a block; noting per rubric.

**Full active-set sweep** (66 active statutes: 18 universal + 48 scoped total; this diff's touched paths are `data/admin/agent_task.json`, `docs/features/**`, `docs/test-bible/**`, `tests/**` — no `src/**`, so `src/**`-scoped statutes are not-applicable by path regardless of layer tag): scoped-applicable = `astral.seed.agent-tables-in-repo-json` (conforms — repo JSON is the seed SoT, no live-DB hand seed), `astral.seed.archie-catalog-wins` (conforms — lasting change via committed catalog, not live DB), `astral.seed.define-approved` (conforms — restores AST-1222's already-approved seed shape, invents nothing new), `astral.docs.features-single-file-per-ticket` (conforms — one plan file), `astral.debug.spikes-under-debug-dir` (not-applicable — no spike content), `astral.git.betty-no-src-or-features` (conforms, verified above). Zero `violates`, zero `needs-discussion`.

**Pattern conformance:** none cited (ticket description lists only `astral.*` statute ids, no `pattern.*` ids).

## Frame diff

(none — ticket description/AC unchanged; no findings to fold in)

context_tokens≈62000

— Radia
