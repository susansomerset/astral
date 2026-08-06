# AST-1218 — Rename Job Review to Gaze Review in agent_task seed

**Linear:** [AST-1218](https://linear.app/astralcareermatch/issue/AST-1218/rename-job-review-to-gaze-review-in-agent-task-seed-gaze-review-rename)
**Parent:** [AST-1183](https://linear.app/astralcareermatch/issue/AST-1183/gaze-review-rename-meteorite-review-sibling-agent-task-grouping) — Gaze Review rename + Meteorite Review sibling + agent_task grouping
**Publish ref:** `origin/sub/AST-1183/AST-1218-rename-job-review-to-gaze-review-in-agent-task-seed`

Rename the classic gaze/GDL `agent_task` section label from **Job Review** to **Gaze Review** in repo seed (and the locked AST-756 fixture rows for those same keys). Retain shared `task_group_order` **`4000`**. Leave meteorite-track rows on **Job Review** for sibling **AST-1219**. Does **not** create Meteorite Review, move meteorite membership, touch aliases (**AST-1184**), UI hardcode audit (**AST-1185**), or `meteorite_email` rename (**AST-1182** / already landed as `meteorite_email`).

## Merge base (build inventory)

Before measuring or editing seed/fixture, **`sync-child.sh`** on this publish ref has already run (plan-child / build-child): fetch → checkout publish ref → merge **`origin/dev`** → merge **`origin/ftr/AST-1183-…`** when that ref exists on origin → merge **`origin/<publish-ref>`**. File counts and lockstep below are **post-sync**. Do not invent a second merge ritual in Stage 1.

Post-sync baseline (verified on tip after `origin/dev` attach): both `data/admin/agent_task.json` and `docs/uat-fixtures/AST-756/expected-agent_task.json` have **53** current rows; both include `evaluate_meteorite` and `craft_evaluate_meteorite_rubric` (AST-1211 lockstep already closed on `origin/dev`). This child does **not** reopen or “close” that lockstep — classic-label edits only; `TestAst1211EvaluateCraftFixtureLockstep` stays green without engineer `tests/` edits. Betty updates classic **Job Review → Gaze Review** assertions (e.g. `TestAst878FetchCulturePagesCatalogRow`) at Code Complete.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `data/admin/agent_task.json` | Set `task_group_name` to `Gaze Review` on the nine classic current rows only; keep `task_group_order` `"4000"` and all other fields | data |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Surgical sync of the same nine classic rows’ `task_group_name` only — **no** whole-file `cp` | docs |

**No changes expected:** `src/**`, frontend, dispatch/config, `tests/` / bible (Betty after Code Complete), meteorite-track seed rows (`gaze_email`, `meteorite_email`, `qualify_meteorite`, `evaluate_meteorite`, `meteorite_like`, `meteorite_upshot`).

## Stage 1: Classic seed rename + surgical AST-756 sync

**Done when:** Every current classic gaze/GDL row listed below has `task_group_name == "Gaze Review"` and `task_group_order == "4000"` in both `data/admin/agent_task.json` and the AST-756 fixture; every current meteorite-track row listed below still has `task_group_name == "Job Review"` and `task_group_order == "4000"`; no other `task_group_name` values elsewhere in the catalog were rewritten; JSON remains a flat-row array; both files still have 53 current rows including `evaluate_meteorite` / `craft_evaluate_meteorite_rubric`; meteorite-row objects (including `evaluate_meteorite`) remain object-equal between catalog and fixture (this stage only rewrites classic `task_group_name`).

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

5. In `docs/uat-fixtures/AST-756/expected-agent_task.json`, apply the **same** classic-only `task_group_name` → `"Gaze Review"` edits for matching `current == 1` rows. Surgical per-row edits only — **no** `cp data/admin/agent_task.json docs/uat-fixtures/...`. Do **not** delete, add, or reshape `evaluate_meteorite` / `craft_evaluate_meteorite_rubric` (or any other non-classic row).

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

def check(path: str) -> dict:
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    by = {r["task_key"]: r for r in rows if r.get("current") == 1}
    assert len(by) == 53, (path, len(by))
    for k in CLASSIC:
        assert k in by, f"{path}: missing classic {k}"
        assert by[k]["task_group_name"] == "Gaze Review", (path, k, by[k]["task_group_name"])
        assert by[k]["task_group_order"] == "4000", (path, k, by[k]["task_group_order"])
    for k in METEORITE:
        assert k in by, f"{path}: missing meteorite {k}"
        assert by[k]["task_group_name"] == "Job Review", (path, k, by[k]["task_group_name"])
        assert by[k]["task_group_order"] == "4000", (path, k, by[k]["task_group_order"])
    assert "craft_evaluate_meteorite_rubric" in by, path
    print("ok", path)
    return by

cat = check("data/admin/agent_task.json")
fix = check("docs/uat-fixtures/AST-756/expected-agent_task.json")
# Meteorite rows (incl. evaluate_meteorite) stay lockstep between catalog and fixture
for k in METEORITE | {"craft_evaluate_meteorite_rubric"}:
    assert cat[k] == fix[k], k
print("ast-1218 seed checks passed")
PY
```

⚠️ **Decision — leave meteorite rows on Job Review:** Child #1 AC is classic rename only. Parent’s “no Job Review remains” AC is the epic rollup after **AST-1219** moves meteorite membership to Meteorite Review. Renaming meteorite rows here would either invent Meteorite Review early or leave them under Gaze Review, both out of scope.

⚠️ **Decision — keep `task_group_order` `4000`:** Parent open questions closed; Archie approved Gaze Review order `4000` and Meteorite Review `4500` for sibling #2. This child retains the existing Job Review order identity as Gaze Review’s section order.

⚠️ **Decision — surgical fixture sync, no whole-file cp:** Post-sync, catalog and fixture are already lockstep at 53 current rows (AST-1211). This stage still edits only the nine classic `task_group_name` values in each file so the diff stays reviewable; a whole-file `cp` is unnecessary and would hide the classic-only intent. Do not reopen AST-1211 lockstep.

⚠️ **Decision — no `tests/` / bible edits:** Engineer pre-commit ban (`astral.git.engineer-test-tree-ban`). `TestAst1211EvaluateCraftFixtureLockstep` is already satisfied by the post-sync fixture (not this child’s job). Betty updates classic-row assertions (e.g. `TestAst878FetchCulturePagesCatalogRow` expecting Job Review → Gaze Review) at Code Complete; meteorite-row Job Review assertions stay until AST-1219.

**Ritual:** `code(AST-1218): Gaze Review classic agent_task group label`

## Self-Assessment

**Scope:** `minor` — two JSON files; `task_group_name` string on nine classic current rows (+ matching fixture rows); no product code layers.

**Conf:** `high` — exact key frozensets from parent Functional scope; post-sync seed inventory matches; Archie already approved membership and `4000`/`4500` orders; same surgical seed/fixture pattern as AST-1212; Joan round=1 drift contradiction resolved by binding to post-`sync-child` tip.

**Risk:** `low` — display/grouping metadata only; dispatch triggers, prompts, and run_next unchanged; meteorite rows intentionally still Job Review until sibling #2; worst case is a wrong label on classic rows until corrected.

## Code rules check

- §1.1 in-scope-only: seed + fixture label only; no AST-1219 / AST-1184 / AST-1185 / AST-1182 work.
- `astral.seed.agent-tables-in-repo-json`: change ships in repo `agent_task` JSON (`data` layer).
- `astral.standards.names-not-ticket-ids`: product label **Gaze Review**, not a ticket-scoped string.
- `astral.standards.no-hardcoded-sets`: no parallel hard-coded Gaze/Job Review lists in `src/`; membership stays on seed rows.
- `astral.git.engineer-test-tree-ban`: plan forbids engineer edits under `tests/` / `docs/test-bible/**`.
- `orch.git.merge-on-checkout` / `orch.pipeline.plan-is-bible`: inventory and Done when bind to post-`sync-child` state (includes `origin/dev`), not a stale pre-merge tip.
- §2.1 / §2.4 / §2.6: N/A — no config blocks, batch claim, or state machine changes.
- §3.3 imports: N/A — no Python/TS edits.

## Revisions

Revision 1 — 2026-08-06
Driven by: Joan `[plan-discuss] round=1 concern` — fix-now on Stage 1 Done when / surgical-sync decision pinning stale “missing `evaluate_meteorite`” drift that contradicts `TestAst1211EvaluateCraftFixtureLockstep`; discuss on undeclared merge base; discuss on Files Changed Layer `data/admin` false-excluding seed statute; acceptable no-op verify assert.
Changes: Added **Merge base (build inventory)** binding counts to post-`sync-child` (origin/dev + ftr when present); rewrote Done when / step 5 / surgical-sync decision for lockstep-at-53 (AST-1211 already closed; this child does not reopen); named Betty for classic Gaze Review assertion updates and clarified TestAst1211 is not this child’s close-out; Layer `data/admin` → `data`; verify script requires all meteorite keys + 53 rows + meteor lockstep equality; removed `assert … or True` no-op.
