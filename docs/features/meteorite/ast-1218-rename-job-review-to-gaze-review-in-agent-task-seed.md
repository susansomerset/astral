# AST-1218 — Rename Job Review to Gaze Review in agent_task seed

**Linear:** [AST-1218](https://linear.app/astralcareermatch/issue/AST-1218/rename-job-review-to-gaze-review-in-agent-task-seed-gaze-review-rename)
**Parent:** [AST-1183](https://linear.app/astralcareermatch/issue/AST-1183/gaze-review-rename-meteorite-review-sibling-agent-task-grouping) — Gaze Review rename + Meteorite Review sibling + agent_task grouping
**Publish ref:** `origin/sub/AST-1183/AST-1218-rename-job-review-to-gaze-review-in-agent-task-seed`

Rename the classic gaze/GDL `agent_task` section label from **Job Review** to **Gaze Review** in repo seed (and the locked AST-756 fixture rows for those same keys). Retain shared `task_group_order` **`4000`**. Leave meteorite-track rows on **Job Review** for sibling **AST-1219**. Does **not** create Meteorite Review, move meteorite membership, touch aliases (**AST-1184**), UI hardcode audit (**AST-1185**), or `meteorite_email` rename (**AST-1182** / already landed as `meteorite_email`).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `data/admin/agent_task.json` | Set `task_group_name` to `Gaze Review` on the nine classic current rows only; keep `task_group_order` `"4000"` and all other fields | data/admin |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Surgical sync of the same nine classic rows’ `task_group_name` only — **no** whole-file `cp` | docs |

**No changes expected:** `src/**`, frontend, dispatch/config, `tests/` / bible (Betty after Code Complete), meteorite-track seed rows (`gaze_email`, `meteorite_email`, `qualify_meteorite`, `evaluate_meteorite`, `meteorite_like`, `meteorite_upshot`).

## Stage 1: Classic seed rename + surgical AST-756 sync

**Done when:** Every current classic gaze/GDL row listed below has `task_group_name == "Gaze Review"` and `task_group_order == "4000"` in both `data/admin/agent_task.json` and the AST-756 fixture (where that key exists); every current meteorite-track row listed below still has `task_group_name == "Job Review"` and `task_group_order == "4000"`; no other `task_group_name` values elsewhere in the catalog were rewritten; JSON remains a flat-row array; fixture vs catalog still differ only by the pre-existing missing `evaluate_meteorite` (+ any other pre-existing catalog-only rows) — this stage does not absorb that drift.

**Classic keys (rename to Gaze Review — exact frozenset):**

`gaze`, `qualify_job_listings`, `fetch_jd`, `evaluate_jd`, `grade_do`, `grade_get`, `fetch_culture_pages`, `grade_like`, `analysis_upshot`

**Meteorite keys (leave `task_group_name` as Job Review — exact frozenset):**

`gaze_email`, `meteorite_email`, `qualify_meteorite`, `evaluate_meteorite`, `meteorite_like`, `meteorite_upshot`

1. Snapshot before edit (local `/tmp` only — do not commit):

```bash
cp data/admin/agent_task.json /tmp/agent_task.pre-ast-1218.json
cp docs/uat-fixtures/AST-756/expected-agent_task.json /tmp/expected-agent_task.pre-ast-1218.json
```

2. In `data/admin/agent_task.json`, for each object with `current == 1` and `task_key` in the classic frozenset above, set **only**:

   - `task_group_name` → `"Gaze Review"`

   Leave `task_group_order` as `"4000"`. Do **not** change `task_seq`, prompts, `agent_id`, `run_next`, `task_key_uuid`, `task_name`, or any other field. Do **not** bump `updated_at` unless an existing seed tooling path already requires it for apply — prefer leaving timestamps untouched so the diff is the label only.

3. Do **not** edit any row whose `task_key` is in the meteorite frozenset. Those rows must still read `task_group_name: "Job Review"` after this stage.

4. Do **not** invent a `Meteorite Review` label, change any `task_group_order` to `4500`, or reorder `task_seq` values. Sibling **AST-1219** owns that move.

5. In `docs/uat-fixtures/AST-756/expected-agent_task.json`, apply the **same** classic-only `task_group_name` → `"Gaze Review"` edits for matching `current == 1` rows. Surgical per-row edits only — **no** `cp data/admin/agent_task.json docs/uat-fixtures/...`. Do not add missing `evaluate_meteorite` (or other catalog-only rows) to close pre-existing drift.

6. Verify with:

```bash
python3 - <<'PY'
import json
from pathlib import Path

CLASSIC = {
    "gaze", "qualify_job_listings", "fetch_jd", "evaluate_jd", "grade_do",
    "grade_get", "fetch_culture_pages", "grade_like", "analysis_upshot",
}
METEORITE = {
    "gaze_email", "meteorite_email", "qualify_meteorite", "evaluate_meteorite",
    "meteorite_like", "meteorite_upshot",
}

def check(path: str, require_all_meteorite: bool) -> None:
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    by = {r["task_key"]: r for r in rows if r.get("current") == 1}
    for k in CLASSIC:
        assert k in by, f"{path}: missing classic {k}"
        assert by[k]["task_group_name"] == "Gaze Review", (path, k, by[k]["task_group_name"])
        assert by[k]["task_group_order"] == "4000", (path, k, by[k]["task_group_order"])
    for k in METEORITE:
        if k not in by:
            if require_all_meteorite:
                raise AssertionError(f"{path}: missing meteorite {k}")
            continue
        assert by[k]["task_group_name"] == "Job Review", (path, k, by[k]["task_group_name"])
        assert by[k]["task_group_order"] == "4000", (path, k, by[k]["task_group_order"])
    # No classic row still labeled Job Review
    for k, r in by.items():
        if k in CLASSIC:
            assert r["task_group_name"] != "Job Review"
    print("ok", path)

check("data/admin/agent_task.json", require_all_meteorite=True)
check("docs/uat-fixtures/AST-756/expected-agent_task.json", require_all_meteorite=False)
# Fixture may still omit evaluate_meteorite — do not fail that path for absence
assert "evaluate_meteorite" not in {
    r["task_key"] for r in json.loads(Path("docs/uat-fixtures/AST-756/expected-agent_task.json").read_text())
    if r.get("current") == 1
} or True
print("ast-1218 seed checks passed")
PY
```

⚠️ **Decision — leave meteorite rows on Job Review:** Child #1 AC is classic rename only. Parent’s “no Job Review remains” AC is the epic rollup after **AST-1219** moves meteorite membership to Meteorite Review. Renaming meteorite rows here would either invent Meteorite Review early or leave them under Gaze Review, both out of scope.

⚠️ **Decision — keep `task_group_order` `4000`:** Parent open questions closed; Archie approved Gaze Review order `4000` and Meteorite Review `4500` for sibling #2. This child retains the existing Job Review order identity as Gaze Review’s section order.

⚠️ **Decision — surgical fixture sync, no whole-file cp:** Catalog currently has 15 Job Review rows (9 classic + 6 meteorite including `evaluate_meteorite`); AST-756 fixture has 14 (missing `evaluate_meteorite`). Blind `cp` would absorb that drift and violate the same rule used on AST-1212.

⚠️ **Decision — no `tests/` / bible edits:** Engineer pre-commit ban (`astral.git.engineer-test-tree-ban`). Betty updates classic-row assertions (e.g. `TestAst878FetchCulturePagesCatalogRow` expecting Job Review → Gaze Review) at Code Complete; meteorite-row Job Review assertions stay until AST-1219.

**Ritual:** `code(AST-1218): Gaze Review classic agent_task group label`

## Self-Assessment

**Scope:** `minor` — two JSON files; `task_group_name` string on nine classic current rows (+ matching fixture rows); no product code layers.

**Conf:** `high` — exact key frozensets from parent Functional scope; live seed inventory matches; Archie already approved membership and `4000`/`4500` orders; same surgical seed/fixture pattern as AST-1212.

**Risk:** `low` — display/grouping metadata only; dispatch triggers, prompts, and run_next unchanged; meteorite rows intentionally still Job Review until sibling #2; worst case is a wrong label on classic rows until corrected.

## Code rules check

- §1.1 in-scope-only: seed + fixture label only; no AST-1219 / AST-1184 / AST-1185 / AST-1182 work.
- `astral.seed.agent-tables-in-repo-json`: change ships in repo `agent_task` JSON.
- `astral.standards.names-not-ticket-ids`: product label **Gaze Review**, not a ticket-scoped string.
- `astral.standards.no-hardcoded-sets`: no parallel hard-coded Gaze/Job Review lists in `src/`; membership stays on seed rows.
- `astral.git.engineer-test-tree-ban`: plan forbids engineer edits under `tests/` / `docs/test-bible/**`.
- §2.1 / §2.4 / §2.6: N/A — no config blocks, batch claim, or state machine changes.
- §3.3 imports: N/A — no Python/TS edits.
