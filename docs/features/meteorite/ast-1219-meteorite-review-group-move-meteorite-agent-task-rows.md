# AST-1219 — Meteorite Review group + move meteorite agent_task rows

**Linear:** [AST-1219](https://linear.app/astralcareermatch/issue/AST-1219/meteorite-review-group-move-meteorite-agent-task-rows-gaze-review)
**Parent:** [AST-1183](https://linear.app/astralcareermatch/issue/AST-1183/gaze-review-rename-meteorite-review-sibling-agent-task-grouping) — Gaze Review rename + Meteorite Review sibling + agent_task grouping
**Publish ref:** `origin/sub/AST-1183/AST-1219-meteorite-review-group-move-meteorite-agent-task-rows`

Create the sibling **Meteorite Review** section (`task_group_order` **`4500`**) and move the Archie-confirmed meteorite-track `agent_task` membership onto it with coherent within-section `task_seq`, then surgically sync the matching AST-756 fixture fields. Classic Gaze Review rows (sibling **AST-1218**, already on tip) stay untouched. Does **not** implement `master_task_key` (**AST-1184**), UI hardcode audit (**AST-1185**), or parse-key rename (**AST-1182** / live key is already `meteorite_email`).

## Merge base (build inventory)

Before measuring or editing seed/fixture, **`sync-child.sh`** on this publish ref has already run (plan-child / build-child): fetch → checkout publish ref → merge **`origin/dev`** → merge **`origin/ftr/AST-1183-gaze-review-rename-meteorite-review-sibling`** when that ref exists on origin → merge **`origin/<publish-ref>`**. File counts and lockstep below are **post-sync**. Do not invent a second merge ritual in Stage 1.

**`--ftr` segment:** use the full parent slug `AST-1183-gaze-review-rename-meteorite-review-sibling` (epic registry `parent_ftr`), not bare `AST-1183`.

Post-sync baseline (verified after attaching `origin/ftr/AST-1183-gaze-review-rename-meteorite-review-sibling` + `origin/dev`):

- Both `data/admin/agent_task.json` and `docs/uat-fixtures/AST-756/expected-agent_task.json` have **53** current rows.
- Classic frozenset (nine keys) already has `task_group_name == "Gaze Review"` and `task_group_order == "4000"` (AST-1218 landed; status User Testing).
- Meteorite frozenset (six keys below) still has `task_group_name == "Job Review"` and `task_group_order == "4000"` with interleaved seqs `2.3`, `2.4`, `2.5`, `4.5`, `10`, `11`.
- Live parse key is **`meteorite_email`** (`parse_meteorite_email` absent from current catalog).
- `craft_evaluate_meteorite_rubric` remains **Candidate Artifacts** / `"2000"` (not in membership — do not move).
- AST-1211 pair (`evaluate_meteorite`, `craft_evaluate_meteorite_rubric`) is object-equal catalog↔fixture. Other meteorite rows may differ in prompts (`meteorite_like` already drifts) — this child does **not** reconcile prompt drift.
- Zero current rows use `Meteorite Review` yet. After this child, zero current rows should still use `Job Review`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `data/admin/agent_task.json` | Set `task_group_name` / `task_group_order` / `task_seq` on the six meteorite current rows only | data |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Surgical sync of the same three grouping fields on those six keys — **no** whole-file `cp` | docs |

**No changes expected:** `src/**`, frontend, dispatch/config, classic Gaze Review rows, `craft_evaluate_meteorite_rubric`, `tests/` / bible (Betty after Code Complete).

## Stage 1: Meteorite Review seed move + surgical AST-756 sync

**Done when:** Every current meteorite-track row in the membership table below has `task_group_name == "Meteorite Review"`, `task_group_order == "4500"`, and the listed `task_seq` in both `data/admin/agent_task.json` and the AST-756 fixture; every current classic Gaze Review row still has `task_group_name == "Gaze Review"` and `task_group_order == "4000"` with unchanged `task_seq`; `craft_evaluate_meteorite_rubric` is still Candidate Artifacts / `"2000"`; no current row still has `task_group_name == "Job Review"`; JSON remains a flat-row array; both files still have 53 current rows; the AST-1211 pair remains object-equal catalog↔fixture. Do **not** require whole-row equality for other meteorite keys (pre-existing prompt drift is out of scope).

**Meteorite membership (move to Meteorite Review — exact mapping):**

| `task_key` | `task_group_name` | `task_group_order` | `task_seq` |
|------------|-------------------|--------------------|------------|
| `gaze_email` | `Meteorite Review` | `"4500"` | `1` |
| `meteorite_email` | `Meteorite Review` | `"4500"` | `2` |
| `qualify_meteorite` | `Meteorite Review` | `"4500"` | `3` |
| `evaluate_meteorite` | `Meteorite Review` | `"4500"` | `4` |
| `meteorite_like` | `Meteorite Review` | `"4500"` | `5` |
| `meteorite_upshot` | `Meteorite Review` | `"4500"` | `6` |

**Classic keys (do not edit — exact frozenset):**

`gaze`, `qualify_job_listings`, `fetch_jd`, `evaluate_jd`, `grade_do`, `grade_get`, `fetch_culture_pages`, `grade_like`, `analysis_upshot`

1. Snapshot before edit (local `/tmp` only — do not commit):

```bash
cp data/admin/agent_task.json /tmp/agent_task.pre-ast-1219.json
cp docs/uat-fixtures/AST-756/expected-agent_task.json /tmp/expected-agent_task.pre-ast-1219.json
```

2. In `data/admin/agent_task.json`, for each object with `current == 1` and `task_key` in the membership table above, set **only**:

   - `task_group_name` → `"Meteorite Review"`
   - `task_group_order` → `"4500"` (string, same type as existing `"4000"` / `"5000"` values)
   - `task_seq` → the integer from the table (`1`…`6`)

   Do **not** change prompts, `agent_id`, `run_next`, `task_key_uuid`, `task_name`, or any other field. Do **not** bump `updated_at` unless an existing seed tooling path already requires it for apply — prefer leaving timestamps untouched so the diff is grouping metadata only.

3. Do **not** edit any row whose `task_key` is in the classic frozenset. Those rows must still read `task_group_name: "Gaze Review"` and `task_group_order: "4000"` after this stage with their pre-edit `task_seq` values.

4. Do **not** move `craft_evaluate_meteorite_rubric` (stays Candidate Artifacts). Do **not** rename classic Gaze Review back to Job Review. Do **not** invent hard-coded Meteorite Review membership lists under `src/`.

5. In `docs/uat-fixtures/AST-756/expected-agent_task.json`, apply the **same** three-field edits for matching `current == 1` meteorite rows. Surgical per-row edits only — **no** `cp data/admin/agent_task.json docs/uat-fixtures/...`. Do **not** delete, add, or reshape non-membership rows. When editing `evaluate_meteorite`, keep the rest of that object identical so AST-1211 lockstep with catalog remains.

6. Verify with (assert only what this child controls + the two AST-1211 keys — **not** global catalog↔fixture equality):

```bash
python3 - <<'PY'
import json
from pathlib import Path

CLASSIC = {
    "gaze", "qualify_job_listings", "fetch_jd", "evaluate_jd", "grade_do",
    "grade_get", "fetch_culture_pages", "grade_like", "analysis_upshot",
}
METEORITE_SEQ = {
    "gaze_email": 1,
    "meteorite_email": 2,
    "qualify_meteorite": 3,
    "evaluate_meteorite": 4,
    "meteorite_like": 5,
    "meteorite_upshot": 6,
}
AST1211 = {"evaluate_meteorite", "craft_evaluate_meteorite_rubric"}

def check(path: str) -> dict:
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    by = {r["task_key"]: r for r in rows if r.get("current") == 1}
    assert len(by) == 53, (path, len(by))
    for k in CLASSIC:
        assert k in by, f"{path}: missing classic {k}"
        assert by[k]["task_group_name"] == "Gaze Review", (path, k, by[k]["task_group_name"])
        assert by[k]["task_group_order"] == "4000", (path, k, by[k]["task_group_order"])
    for k, seq in METEORITE_SEQ.items():
        assert k in by, f"{path}: missing meteorite {k}"
        assert by[k]["task_group_name"] == "Meteorite Review", (path, k, by[k]["task_group_name"])
        assert by[k]["task_group_order"] == "4500", (path, k, by[k]["task_group_order"])
        assert by[k]["task_seq"] == seq, (path, k, by[k]["task_seq"], seq)
    craft = by["craft_evaluate_meteorite_rubric"]
    assert craft["task_group_name"] == "Candidate Artifacts", craft["task_group_name"]
    assert craft["task_group_order"] == "2000", craft["task_group_order"]
    for k, r in by.items():
        assert r.get("task_group_name") != "Job Review", (path, k)
        if k not in METEORITE_SEQ and r.get("task_group_name") == "Meteorite Review":
            raise AssertionError(f"{path}: unexpected Meteorite Review on {k}")
    print("ok", path)
    return by

cat = check("data/admin/agent_task.json")
fix = check("docs/uat-fixtures/AST-756/expected-agent_task.json")
for k in AST1211:
    assert cat[k] == fix[k], k
# Grouping fields lockstep for membership (prompts may still drift elsewhere)
for k in METEORITE_SEQ:
    for field in ("task_group_name", "task_group_order", "task_seq"):
        assert cat[k][field] == fix[k][field], (k, field)
print("ast-1219 seed checks passed")
PY
```

⚠️ **Decision — renumber meteorite `task_seq` to `1`…`6`:** Parent requires coherent within-section sequence. The old fractional/interleaved values (`2.3`…`11`) existed only to sit inside Job Review beside classic rows. Inside a dedicated Meteorite Review section, integer pipeline order matches Gaze Review’s `1`…`9` pattern and sorts mailbox → parse → qualify → evaluate → like → upshot.

⚠️ **Decision — `task_group_order` `"4500"` (string):** Archie closed open questions on parent; Gaze Review keeps `"4000"`, Meteorite Review is peer `"4500"` (between Gaze Review and Job Artifacts `"5000"`). Store as string like every other `task_group_order` in seed.

⚠️ **Decision — surgical fixture sync, no whole-file cp:** Edit only the three grouping fields on the six membership keys in each file. A whole-file `cp` would overwrite unrelated fixture prompt drift (`meteorite_like` and others) and is forbidden. Keep AST-1211 pair object-equal; do not assert or “fix” non-AST-1211 catalog↔fixture inequality.

⚠️ **Decision — no `tests/` / bible edits:** Engineer pre-commit ban (`astral.git.engineer-test-tree-ban`). Betty updates meteorite Job Review assertions and seq pins at Code Complete — including `TestAst1218GazeReviewClassicGroupLabel` (meteorite half), `TestAst1055MeteoriteCatalogRows`, `TestAst1060QualifyMeteoriteCatalogRow`, `TestAst1089ParseMeteoriteEmailCatalogRow`, `TestAst1106GazeEmailCatalogRow`, and any Scheduled Actions fixture still hardcoding Job Review for these keys. Classic Gaze Review asserts from AST-1218 stay.

⚠️ **Decision — seed-only (no `src/`):** UI Admin surfaces already read `task_group_name` / `task_group_order` / `task_seq` from applied seed. Inventing parallel Meteorite Review lists in product code would violate `astral.standards.no-hardcoded-sets` and is owned by **AST-1185** if anything remains hardcoded.

**Ritual:** `code(AST-1219): Meteorite Review agent_task group + membership move`

## Self-Assessment

**Scope:** `minor` — two JSON files; grouping fields on six current meteorite rows (+ matching fixture rows); no product code layers.

**Conf:** `high` — membership, order `4500`, and live key `meteorite_email` are Archie-confirmed and verified on tip after AST-1218; same surgical seed/fixture pattern as sibling; seq renumber is the only judgment call and is pinned in the membership table.

**Risk:** `low` — display/grouping metadata only; dispatch triggers, prompts, and run_next unchanged; worst case is wrong section label/order until corrected. Betty’s assertion updates are required before Tests Passed (same handoff shape as AST-1218).

## Code rules check

- §1.1 in-scope-only: seed + fixture grouping fields only; no AST-1218 classic rename, AST-1184 aliases, AST-1185 UI audit, or AST-1182 parse rename.
- `astral.seed.agent-tables-in-repo-json`: change ships in repo `agent_task` JSON (`data` layer).
- `astral.standards.names-not-ticket-ids`: product label **Meteorite Review**, not a ticket-scoped string.
- `astral.standards.no-hardcoded-sets`: no parallel hard-coded Meteorite Review lists in `src/`; membership stays on seed rows.
- `astral.git.engineer-test-tree-ban`: plan forbids engineer edits under `tests/` / `docs/test-bible/**`.
- `orch.git.merge-on-checkout` / `orch.pipeline.plan-is-bible`: inventory and Done when bind to post-`sync-child` state with full ftr slug; verify asserts only tip-true predicates (labels/order/seq + AST-1211 pair), not global object equality.
- §2.1 / §2.4 / §2.6: N/A — no config blocks, batch claim, or state machine changes.
- §3.3 imports: N/A — no Python/TS edits.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1183/AST-1219-meteorite-review-group-move-meteorite-agent-task-rows`
**Plan path:** `docs/features/meteorite/ast-1219-meteorite-review-group-move-meteorite-agent-task-rows.md`

**Built tip:** `39e6a911f6a506afc5991604e9bae83bf73549f2` (`39e6a911`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `39e6a911` | Meteorite Review agent_task group + membership move (+ surgical AST-756 fixture) |

## Review (Radia)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1219
**Publish ref:** `origin/sub/AST-1183/AST-1219-meteorite-review-group-move-meteorite-agent-task-rows` @ `eee01238`
**Overall:** CLEAN

**Scope of diff swept:** this ticket's own contribution, isolated as `git diff origin/ftr/AST-1183-gaze-review-rename-meteorite-review-sibling...origin/sub/AST-1183/AST-1219-…` (sibling AST-1218's already-reviewed content is inherited via the `ftr` merge at `ab0cc6b4` and not re-litigated here). 6 changed files: `data/admin/agent_task.json` M, `docs/uat-fixtures/AST-756/expected-agent_task.json` M, `docs/test-bible/core/repo_admin_json.md` M, `tests/component/core/test_repo_admin_json.py` M, `tests/component/frontend/pages/test_AdminScheduledActions_AST1106.test.tsx` M, `docs/features/meteorite/ast-1219-….md` A.

**Full-set sweep:** 65 active statutes (18 universal + 47 scoped) scored in-session. All 18 universal `conforms` (single `merge-tests(AST-1219)` commit; commit vocabulary respected; sub explicitly merges `origin/ftr/AST-1183-gaze-review-rename-meteorite-review-sibling` at `ab0cc6b4` per `orch.git.merge-on-checkout`; one epic worktree; assignee stays engineer Hedy). 6 scoped statutes matched the diff and all score `conforms`: `astral.seed.agent-tables-in-repo-json` (53-row non-empty JSON array intact), `astral.seed.define-approved` (Archie-confirmed membership + order `4500` per parent notes / Joan Plan Approved), `astral.git.engineer-test-tree-ban` (the `code(AST-1219)` commit touches only `data/admin/agent_task.json` + `docs/uat-fixtures/AST-756/expected-agent_task.json` — confirmed via `git show --stat`; all `tests/`/`docs/test-bible/` edits landed via Betty's `test(AST-1219)`→`merge-tests(AST-1219)` commits), `astral.git.betty-no-src-or-features` (Betty's commit touches neither `src/` nor `docs/features/`), `astral.docs.features-single-file-per-ticket` (one new file for this ticket), `astral.debug.spikes-under-debug-dir` (plan doc, not spike notes). Remaining 41 scoped statutes `not-applicable` (diff has no `src/**` paths). Zero `Job Review`/`Gaze Review`/`Meteorite Review` literals under `src/` on this tip.

**Independently verified (not taken on trust):** ran the six-key membership + classic-preservation + AST-1211-pair checks against both `data/admin/agent_task.json` and the AST-756 fixture (53 current rows each; six meteorite keys → `Meteorite Review`/`"4500"`/seq `1`…`6`; nine classic keys still `Gaze Review`/`"4000"`; `craft_evaluate_meteorite_rubric` still `Candidate Artifacts`/`"2000"`; zero rows left `Job Review`; `evaluate_meteorite` object-equal catalog↔fixture) — all pass. Also confirmed the `TestAst1055…`/`TestAst1060…` revised `meteorite_like` cache_prompt assertion (`"be liberal"`) matches the actual tip text, replacing a stale pre-existing-drift assertion — legitimate Betty fix, not scope creep.

**Joan's plan-rubric discuss note** ("Done when asserts unchanged classic `task_seq` but step 6 script doesn't check it") did not surface a real defect: diffed `data/admin/agent_task.json` directly and confirmed zero classic-row hunks (only the six meteorite keys changed) — no stray classic `task_seq` edit occurred.

**Straggler (C4):** Joan plan-rubric verdict attached (revision=1, APPROVED, "18 universal + 10 scoped … all conforms"); slim artifact names no Excluded list to cross-check — no straggler flagged.

**Pattern conformance:** none cited.

**Frame diff:** (none) — diff footprint matches Description In-scope / Files Changed exactly.

context_tokens≈100000

— Radia

## Resolution

**Date:** 2026-08-06
**Review:** Radia `[code-rubric] revision=1` — **Overall: CLEAN** (findings: none). Tip at intake: `f122db09` (`docs(AST-1219): Radia review — clean`).

**Fix-now / discuss / advisory:** none — no product or plan changes required beyond this resolution stub.

**Outcome:** `resolve(AST-1219): — clean`; advance to **User Testing** (assignee Hedy).
