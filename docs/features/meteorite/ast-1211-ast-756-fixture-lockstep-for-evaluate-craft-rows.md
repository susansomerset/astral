<!-- linear-archive: AST-1211 archived 2026-08-17 -->

## Linear archive (AST-1211)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1211/ast-756-fixture-lockstep-for-evaluatecraft-rows-evaluate-meteorite  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1186 — evaluate_meteorite: fold recent work into tests + statute/pattern check  
**Blocked by / blocks / related:** parent: AST-1186

### Description

## What this implements

After or with #2: surgical fixture update so expected `agent_task` includes current `evaluate_meteorite` and `craft_evaluate_meteorite_rubric` catalog rows; no blind whole-file absorb of unrelated prompt drift.

## Acceptance criteria

- [X] AST-756 expected fixture includes current `evaluate_meteorite` and `craft_evaluate_meteorite_rubric` rows in lockstep with catalog for those keys (no blind whole-file absorb of unrelated drift).

## Boundaries

Does **not** own twin audit/product fixes (sibling #1 / AST-1209) or bible/component coverage (sibling #2 / AST-1210). Does **not** absorb unrelated prompt drift via whole-file cp. Does **not** edit `data/admin/agent_task.json` (catalog already has both rows).

## In scope

- [X] `astral.seed.agent-tables-in-repo-json` — catalog under `data/admin/agent_task.json` remains SoT (untouched); fixture twin gains the two missing rows by full-row copy; no live-DB hand-edit.
- [X] `astral.standards.in-scope-only` — only `docs/uat-fixtures/AST-756/expected-agent_task.json`; insert `evaluate_meteorite` + `craft_evaluate_meteorite_rubric`; leave ~13 drifted shared rows alone.
- [X] `astral.docs.features-single-file-per-ticket` — plan at `docs/features/meteorite/ast-1211-ast-756-fixture-lockstep-for-evaluate-craft-rows.md`.
- [X] `astral.git.engineer-test-tree-ban` — no `tests/` / `docs/test-bible/**` edits; Betty owns any new fixture-row assert after Code Complete.

## Considered but excluded

* Twin audit / product conformance (`TASK_CONFIG`, consult, dispatch, evaluate_meteorite-related UI) — AST-1209.
* Bible + component fold-in for twin contract — AST-1210.
* Whole-file catalog↔fixture byte-identity / absorbing shared-row prompt drift (`craft_*`, `evaluate_jd`, `grade_*`, `meteorite_like`, …) — parent-labeled campaign only if Archie asks; not this child.
* Catalog prompt / uuid / `updated_at` edits on `data/admin/agent_task.json` — rows already present.
* `qualify_meteorite` / gaze_email / other agent_task rows; classic `evaluate_jd` @ **JD_READY** behavior.
* Universal `orch.*` statutes (pipeline/git orchestration — not product surface for this fixture delta).

## Notes for planning

Parent: AST-1186. After AST-1209; may run with or after AST sibling bible/tests. Tip gap confirmed: catalog 53 keys / fixture 51; only missing keys are the two named above.

## Git branch (authoritative)

`origin/sub/AST-1186/AST-1211-ast-756-fixture-lockstep-for-evaluate-craft-rows` (ignore Linear `gitBranchName`).

### Comments

#### chuckles — 2026-08-06T06:30:21.823Z
[merge-child] blocked: git pull merge on sub — tip `1d7d0e5e` subject is `Merge remote-tracking branch 'origin/dev'…`. validate-sub-log requires `git fetch && git merge origin/ftr/<parent-segment>` (or a `resolve(AST-1211):` subject), not a default pull merge of origin/dev.

@Katherine Johnson — drop or rewrite tip so the range `origin/ftr/AST-1186-…..origin/sub/…/AST-1211-…` has no `Merge remote-tracking branch` subjects; republish; Chuckles will re-run merge-child.

— Chuckles

#### katherine — 2026-08-06T06:29:15.447Z
`origin/sub/AST-1186/AST-1211-ast-756-fixture-lockstep-for-evaluate-craft-rows` @ `1d7d0e5e` · §9a clean · ftr dry-run clean

#### radia — 2026-08-06T06:25:43.913Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1211
**Publish ref:** `origin/sub/AST-1186/AST-1211-ast-756-fixture-lockstep-for-evaluate-craft-rows` @ `c889baa7`
**Overall:** FIX-NOW

## Plan adherence
- Stage 1 done-when met exactly — verified independently (Python object-equality, not just trusting the manifest): fixture is now 53/53 rows, `evaluate_meteorite` and `craft_evaluate_meteorite_rubric` are object-identical to `data/admin/agent_task.json`, and the same 13 shared rows (`craft_*`, `evaluate_jd`, `grade_*`, `meteorite_like`) still differ from catalog only in prompt fields — confirming the plan's refusal to absorb unrelated drift held.
- Insert is a pure addition (+38/−0, zero deletion lines in `git diff`), satisfying Joan's plan-rubric finding #1 gate. Catalog (`data/admin/agent_task.json`) confirmed byte-for-byte untouched.
- Joan's finding #2 (stale `TestAst786AgentTaskRepoJsonSeed` docstring / bible note claiming the fixture is still missing these keys) is closed — correctly by Betty's `test(AST-1211)` commit, not the engineer.
- Commit-role separation clean: `code(AST-1211)` (`ef4b8878`) touches the UAT fixture only; `test(AST-1211)` + one `merge-tests(AST-1211)` SHA land Betty's `tests/` + `docs/test-bible/**` only; `docs(AST-1211)` commits touch only the plan file.

Full active statute corpus (65 leaves — 19 universal + 46 scoped) scored in-session. Diff has zero `src/**` / `scripts/**` / `data/admin/**` paths, so 41 of 46 scoped statutes are not-applicable; the 5 that matched (`astral.docs.features-single-file-per-ticket`, `astral.debug.spikes-under-debug-dir`, `astral.git.betty-no-src-or-features`, `astral.git.engineer-test-tree-ban`, `astral.seed.define-approved`) all conform. Universal: 17 conform, 1 not-applicable (`orch.roles.archie-approves-statutes`), **1 violates**.

**fix-now — `orch.git.merge-on-checkout` not run at checkout.** This sub's merge-base with `origin/ftr/AST-1186-evaluate-meteorite-fold-recent-work-into-tests` is `0d926c08` (a shared `origin/tests` ancestor), not the ftr tip — verified `git merge-base --is-ancestor origin/ftr/AST-1186-... origin/sub/AST-1186/AST-1211-...` → **NO**. Confirmed by content: `src/core/dispatcher.py` on this sub's tip still has the **pre-AST-1209** docstring/logic ("retire stale evaluate_jd@METEORITE_NEW (AST-1060)"), not AST-1209's shipped twin-aware retirement — because this sub branched off `origin/dev` directly and never merged the already-resolved `origin/ftr/AST-1186` tip (AST-1209's `resolve(AST-1209): — clean` landed at 06:03:37, six minutes before this ticket's Plan Ready). No content collision in this diff — it touches only the UAT fixture — but this is exactly the statute's own violating example ("coding on a sub that has not merged an advanced ftr tip with sibling landings"). **Remedy:** `git fetch origin && git merge origin/ftr/AST-1186-evaluate-meteorite-fold-recent-work-into-tests` on this sub before `merge-child` folds it into ftr.

**Pattern conformance:** none cited in the ticket.

## Frame diff
(none) — description AC/In-scope/Boundaries checkboxes already reflect the shipped diff.

**What's solid:** Surgical insert exactly matches the plan's anchor-adjacency placement (`craft_evaluate_meteorite_rubric` after `craft_jobdesc_rubric`; `evaluate_meteorite` after `evaluate_jd`); no whole-file `cp`, no catalog touch, no test-tree edits by the engineer.

context_tokens≈54000

— Radia

#### betty — 2026-08-06T06:19:05.056Z
## QA test manifest (AST-1211)

**Publish:** `origin/sub/AST-1186/AST-1211-ast-756-fixture-lockstep-for-evaluate-craft-rows` @ `9986de44`
**merge-tests:** `origin/tests` `b8696e49e47f517ec7b5bdb4d17ae84893b6fd9f`

### Classification

1. **Existing coverage:** catalog key lock stays **`TestAst786AgentTaskRepoJsonSeed`** (docstring refreshed — no longer claims fixture missing the two keys).
2. **Broken / obsolete (revised):** AST-1196 / AST-786 notes that fixture still lacks `evaluate_meteorite` / `craft_evaluate_meteorite_rubric` or “fixture still 51”.
3. **Gaps (this pass):** **`TestAst1211EvaluateCraftFixtureLockstep`** — fixture length 53; both keys present and object-equal to catalog. Shared-row prompt drift (other keys) still deferred — not whole-file byte-identity.

### Run

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_repo_admin_json.py::TestAst1211EvaluateCraftFixtureLockstep \
  -q
```

### Bible verify

`docs/test-bible/core/repo_admin_json.md` on publish-ref sha256 `f15d3085e3553ea773fafc414074283d660de2a4`

— Betty

#### katherine — 2026-08-06T06:17:05.383Z
`origin/sub/AST-1186/AST-1211-ast-756-fixture-lockstep-for-evaluate-craft-rows` @ `be7524c5` (code `ef4b8878`). Betty: `TestAst786AgentTaskRepoJsonSeed` docstring + `docs/test-bible/core/repo_admin_json.md` still say fixture missing these two keys — gap closed; refresh those notes / any lockstep assert.

#### joan — 2026-08-06T06:12:34.731Z
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1211
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1186/AST-1211-ast-756-fixture-lockstep-for-evaluate-craft-rows` @ `74795d07`

## Traceability

AC1→S1. Single AC, single stage; no unmapped AC, no orphan stage.

**Considered:** all universal active statutes + the four scoped citations (`astral.seed.agent-tables-in-repo-json`, `astral.standards.in-scope-only`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`); scored in-session, all conform. `orch.*` universals considered and non-binding on a docs-layer fixture delta.

## Claims re-verified on tip

I ran the plan's premises as read-only measurements rather than trusting the pre-survey:

- Gap exact — catalog 53 rows / fixture 51, every row `current == 1`, no duplicate `task_key` in either file. Catalog-only keys are precisely `evaluate_meteorite` + `craft_evaluate_meteorite_rubric`; fixture-only keys none.
- Anchors safe — `craft_jobdesc_rubric` and `evaluate_jd` each appear exactly once in the fixture, and neither new key appears anywhere, so both `assert len(idxs) == 1` and the already-present guard hold.
- Drift characterized correctly — 13 shared rows differ, and they differ **only** in `cache_prompt` / `nocache_prompt` / `user_prompt`. The plan's refusal to absorb them is the right call.
- **Full-row copy is shape-safe** — catalog and fixture share one 17-column row schema (identical key sets across both files; 38 shared rows are already object-equal). So copying a whole catalog object cannot introduce a foreign row shape. This was my main concern going in, since `expected-agent.json` needs a column mapping in `test_repo_admin_json.py`; `agent_task` does not.
- **Writer preserves bytes** — `json.dumps(rows, indent=2, ensure_ascii=False) + "\n"` round-trips **both** tip files byte-identically (no `\u` escapes, trailing newline present). The rewrite will therefore be a pure insertion, not a whole-file reformat.
- **Insert won't turn an existing test red** — every fixture reader in `tests/component/core/test_repo_admin_json.py` indexes by `task_key` (dict or `next(...)`), never by array position, so placement is cosmetic as the plan says. And both catalog rows satisfy `task_name == task_key`, which is what keeps `TestAst1107…test_fixture_shares_task_name_equals_task_key` green once the rows land.

## Findings

**1. discuss — the post-edit gate checks objects, not bytes.**
Stage 1's done-when promises pre-existing rows stay byte-identical, but the gate proves it only at parsed-object level (`pre[k] == post[k]`). Byte round-trip happens to hold on tip (I verified), so nothing is at risk today — but the gate would also pass if a future style or non-ASCII change silently reformatted all 51 rows. One line closes the gap exactly: after the edit, `git diff -- docs/uat-fixtures/AST-756/expected-agent_task.json` must show zero deletion lines (pure insertion).

**2. discuss — this child makes an existing test docstring stale and cannot fix it itself.**
`TestAst786AgentTaskRepoJsonSeed` documents the deferred drift by name ("fixture missing `evaluate_meteorite` / `craft_evaluate_meteorite_rubric`"), and `docs/test-bible/core/repo_admin_json.md` carries the same note. Once Stage 1 lands, both describe a gap that no longer exists. The plan is right that the engineer stays out of `tests/` and the bible — so name those two specific spots for Betty / AST-1210 in Stage 1 step 5, rather than leaving the tree documenting a closed gap.

**3. acceptable.**
Full-row insert over a field subset (verified shape-safe above, and the only way to "include the current catalog rows" without inventing a second row shape). Leaving the 13 prompt-drifted rows alone, with the whole-file campaign escalated to parent AST-1186 if Archie ever wants it — textbook `astral.standards.in-scope-only`. Catalog left untouched as source of truth, no live-DB hand-edit (`astral.seed.agent-tables-in-repo-json`). The re-run skip logic is genuinely idempotent: on a second pass both keys short-circuit on the anchor-adjacency check before reaching the absent-key assert.

No `fix-now`. Cleared for build.

— Joan

context_tokens≈130000

#### katherine — 2026-08-06T06:09:18.722Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1186/AST-1211-ast-756-fixture-lockstep-for-evaluate-craft-rows/docs/features/meteorite/ast-1211-ast-756-fixture-lockstep-for-evaluate-craft-rows.md

`origin/sub/AST-1186/AST-1211-ast-756-fixture-lockstep-for-evaluate-craft-rows` @ `74795d07`

Tip gap: catalog 53 / fixture 51 — only missing `evaluate_meteorite` + `craft_evaluate_meteorite_rubric`. Stage 1 inserts full-row catalog copies after `craft_jobdesc_rubric` / `evaluate_jd`; pre/post gates forbid mutating the other 51 fixture rows or touching `data/admin/agent_task.json`. Whole-file `cp` (would absorb ~13 shared-row prompt drifts) stays excluded.

**Scope:** minor — one UAT fixture file; two inserted rows; no `src/` / catalog edits.

**Conf:** high — gap is measured on tip; AST-1196 already established surgical-not-`cp`; parent AC names these two keys.

**Risk:** low — fixture-only twin; gates catch wrong insert or unrelated-row mutation; runtime does not read the UAT fixture.

---

# AST-1211 — AST-756 fixture lockstep for evaluate/craft rows

**Linear:** [AST-1211](https://linear.app/astralcareermatch/issue/AST-1211/ast-756-fixture-lockstep-for-evaluatecraft-rows-evaluate-meteorite)
**Parent:** [AST-1186](https://linear.app/astralcareermatch/issue/AST-1186/evaluate-meteorite-fold-recent-work-into-tests-statutepattern-check) — evaluate_meteorite: fold recent work into tests + statute/pattern check
**Publish ref:** `origin/sub/AST-1186/AST-1211-ast-756-fixture-lockstep-for-evaluate-craft-rows`

Bring the AST-756 expected `agent_task` UAT fixture into **labeled** lockstep for the two catalog rows that are present in `data/admin/agent_task.json` but missing from the fixture — `evaluate_meteorite` and `craft_evaluate_meteorite_rubric` — by surgically inserting full-row copies from the catalog. Does **not** own twin audit/product fixes (AST-1209), bible/component coverage (AST-1210), catalog prompt edits, or a blind whole-file `cp` that would absorb the ~13 shared rows with unrelated prompt drift.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Insert two full rows copied from catalog (`evaluate_meteorite`, `craft_evaluate_meteorite_rubric`); leave every pre-existing fixture row byte-identical | docs |

**No changes expected:** `data/admin/agent_task.json` (already has both keys — catalog is source of truth), `src/**`, `tests/**`, `docs/test-bible/**` (Betty / AST-1210). Do **not** hand-edit the live DB. Do **not** `cp` catalog over the fixture.

## Stage 1: Surgical fixture insert — two missing evaluate/craft rows

**Done when:** `docs/uat-fixtures/AST-756/expected-agent_task.json` contains current `evaluate_meteorite` and `craft_evaluate_meteorite_rubric` rows that are **object-equal** to the matching `current == 1` rows in `data/admin/agent_task.json`; fixture length is 53; every fixture row that existed before the edit is unchanged; the 13 shared rows that already differ from catalog are untouched.

1. **Pre-edit snapshots (gate against silent multi-row edits / whole-file absorb):**

```bash
cp data/admin/agent_task.json /tmp/agent_task.pre-ast-1211.json
cp docs/uat-fixtures/AST-756/expected-agent_task.json /tmp/expected-agent_task.pre-ast-1211.json
```

2. **Confirm the gap before editing** (abort if the tip already closed it — do not invent a different change):

```bash
python3 - <<'PY'
import json
from pathlib import Path

def current_by_key(path):
    return {r["task_key"]: r for r in json.loads(Path(path).read_text(encoding="utf-8")) if r.get("current") == 1}

cat = current_by_key("data/admin/agent_task.json")
fix = current_by_key("docs/uat-fixtures/AST-756/expected-agent_task.json")
need = ("evaluate_meteorite", "craft_evaluate_meteorite_rubric")
assert all(k in cat for k in need), f"catalog missing {need}"
assert all(k not in fix for k in need), f"fixture already has {[k for k in need if k in fix]} — stop and comment on parent"
assert set(cat) - set(fix) == set(need), f"unexpected catalog-only keys: {set(cat)-set(fix)}"
print(f"OK gap confirmed: catalog={len(cat)} fixture={len(fix)} missing={list(need)}")
PY
```

3. **Insert the two catalog rows into the fixture** (Python rewrite — do not hand-edit prompt blobs). Rules:

   - Deep-copy each catalog object with `task_key` in `{evaluate_meteorite, craft_evaluate_meteorite_rubric}` and `current == 1` **as-is** (every field, including `task_key_uuid`, prompts, `updated_at`, grouping, `task_seq`).
   - Placement (match catalog adjacency so humans can find neighbors):
     - Insert `craft_evaluate_meteorite_rubric` **immediately after** the fixture object whose `task_key == "craft_jobdesc_rubric"`.
     - Insert `evaluate_meteorite` **immediately after** the fixture object whose `task_key == "evaluate_jd"`.
   - Do **not** reorder other rows. Do **not** rewrite any existing fixture object. Do **not** change `data/admin/agent_task.json`.
   - Write the array back with `json.dumps(..., indent=2, ensure_ascii=False) + "\n"` (same style as both tip files today).

```bash
python3 - <<'PY'
import copy
import json
from pathlib import Path

KEYS = ("craft_evaluate_meteorite_rubric", "evaluate_meteorite")
AFTER = {
    "craft_evaluate_meteorite_rubric": "craft_jobdesc_rubric",
    "evaluate_meteorite": "evaluate_jd",
}

cat_rows = json.loads(Path("data/admin/agent_task.json").read_text(encoding="utf-8"))
fix_rows = json.loads(Path("docs/uat-fixtures/AST-756/expected-agent_task.json").read_text(encoding="utf-8"))
cat_by = {r["task_key"]: r for r in cat_rows if r.get("current") == 1}
assert all(k in cat_by for k in KEYS)

out = list(fix_rows)
for key in KEYS:
    anchor = AFTER[key]
    idxs = [i for i, r in enumerate(out) if r.get("task_key") == anchor]
    assert len(idxs) == 1, f"anchor {anchor} count={len(idxs)}"
    # Skip if a prior partial run already inserted this key immediately after the anchor.
    insert_at = idxs[0] + 1
    if insert_at < len(out) and out[insert_at].get("task_key") == key:
        continue
    assert all(r.get("task_key") != key for r in out), f"{key} already present elsewhere"
    out.insert(insert_at, copy.deepcopy(cat_by[key]))

Path("docs/uat-fixtures/AST-756/expected-agent_task.json").write_text(
    json.dumps(out, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)
print("OK inserted", list(KEYS))
PY
```

⚠️ **Decision — full-row insert, not field subset:** Parent AC requires the fixture to **include** the current catalog rows for those keys. Copying the entire catalog object (uuid + prompts + metadata) is the only way to lockstep without inventing a second row shape. Catalog remains source of truth (`astral.seed.agent-tables-in-repo-json`); the fixture is the UAT twin for those keys only.

⚠️ **Decision — leave the 13 drifted shared rows alone:** Tip has catalog 53 / fixture 51 with shared-row prompt drift on `craft_*` rubrics, `evaluate_jd`, `grade_*`, `meteorite_like`, etc. A whole-file `cp` would absorb that drift under this ticket’s name and violate Boundaries / `astral.standards.in-scope-only`. This labeled re-baseline closes **only** the two missing keys. Full catalog↔fixture byte-identity for the drifted shared rows stays **out of scope** (escalate on parent AST-1186 if Archie later wants a whole-file campaign).

⚠️ **Decision — do not edit the catalog:** Both rows already exist in `data/admin/agent_task.json` on tip. Editing prompts, `updated_at`, or uuids here would be product/catalog work outside this child’s fixture ownership.

⚠️ **Decision — placement after catalog neighbors:** Array order is not a runtime contract (startup applies by `task_key`), but inserting next to `craft_jobdesc_rubric` / `evaluate_jd` mirrors catalog adjacency and matches how prior meteorite catalog rows were added. Do not sort the whole file.

4. **Post-edit gates** — fixture gains exactly those two keys; catalog unchanged; pre-existing fixture rows unchanged; the two new rows match catalog object-for-object:

```bash
python3 - <<'PY'
import json
from pathlib import Path

def rows(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def current_by_key(path):
    return {r["task_key"]: r for r in rows(path) if r.get("current") == 1}

# Catalog must be untouched.
assert rows("data/admin/agent_task.json") == rows("/tmp/agent_task.pre-ast-1211.json"), "catalog changed — abort"

pre = current_by_key("/tmp/expected-agent_task.pre-ast-1211.json")
post = current_by_key("docs/uat-fixtures/AST-756/expected-agent_task.json")
cat = current_by_key("data/admin/agent_task.json")
need = {"evaluate_meteorite", "craft_evaluate_meteorite_rubric"}

assert set(post) - set(pre) == need, f"unexpected fixture key delta: {set(post)^set(pre)}"
assert set(pre).issubset(set(post))
assert len(post) == 53 and len(pre) == 51
for k in pre:
    assert pre[k] == post[k], f"pre-existing fixture row mutated: {k}"
for k in need:
    assert post[k] == cat[k], f"fixture row not object-equal to catalog: {k}"

# Array placement
keys_in_order = [r["task_key"] for r in rows("docs/uat-fixtures/AST-756/expected-agent_task.json")]
assert keys_in_order.index("craft_evaluate_meteorite_rubric") == keys_in_order.index("craft_jobdesc_rubric") + 1
assert keys_in_order.index("evaluate_meteorite") == keys_in_order.index("evaluate_jd") + 1
print("OK AST-1211 surgical fixture lockstep")
PY
```

5. Do **not** edit `tests/` or `docs/test-bible/**`. Existing tip already documents deferred whole-file byte-identity (AST-1196 comments in `TestAst786AgentTaskRepoJsonSeed` / fixture lockstep helpers). Any new component assert that these two fixture keys exist and match catalog is **Betty** after Code Complete (sibling AST-1210 may already fold twin coverage — do not invent bible work here). If a green-manifest later requires a fixture-row assert and Betty asks via `[qa-handoff]`, stay out of `tests/` as engineer.

6. Do **not** touch twin audit/product surfaces (`TASK_CONFIG`, consult, dispatch, UI) — AST-1209. Do **not** rewrite qualify / gaze_email / other catalog rows.

**Done when (recheck):** the post-edit gate script in step 4 prints `OK AST-1211 surgical fixture lockstep`.

## Self-Assessment

**Scope:** `minor` — one UAT fixture file; two inserted rows copied from existing catalog; no `src/` and no catalog edits.

**Conf:** `high` — tip already proves the exact gap (catalog 53 / fixture 51, only those two keys missing); AST-1196 established the surgical-not-`cp` pattern; parent AC names these two keys and forbids whole-file absorb.

**Risk:** `low` — wrong insert could desync fixture from catalog for those keys or mutate unrelated fixture rows; the pre/post gates catch both. Runtime product path does not read the UAT fixture.

## Rules check (plan vs ASTRAL_CODE_RULES)

- `astral.seed.agent-tables-in-repo-json` — catalog under `data/admin/agent_task.json` stays SoT and untouched; fixture is the UAT twin for the two keys only; no live-DB seed.
- §1.1 / `astral.standards.in-scope-only` — fixture insert only; no twin audit, bible, catalog prompt, or 13-row drift absorb.
- §1.3 DRY — one Python insert script; no new product helpers.
- §1.4 / `astral.standards.no-hardcoded-sets` — N/A (no new Python state sets).
- §2.1 config — N/A (no config edits).
- §2.4 / §2.6 batch/state — N/A.
- §3.3 imports — N/A (no `src/` edits).
- Engineer test-tree ban — no `tests/` / bible edits; Betty owns any new lockstep assert.
- §3.6 spikes — N/A (no spike output).

## Review (build stub)

**Publish ref:** `origin/sub/AST-1186/AST-1211-ast-756-fixture-lockstep-for-evaluate-craft-rows`
**Plan path:** `docs/features/meteorite/ast-1211-ast-756-fixture-lockstep-for-evaluate-craft-rows.md`

**Built tip:** `ef4b88785931a86074559f77ba10e1848052170c` (`ef4b8878`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `ef4b8878` | AST-756 fixture: insert `evaluate_meteorite` + `craft_evaluate_meteorite_rubric` full-row catalog copies (+38/−0) |

### code-rubric.v1 verdict

[code-rubric] revision=1

| Field | Value |
|-------|-------|
| Rubric | code-rubric.v1 |
| Publish ref tip | `9986de4443e1630f6382fcdc4cdc1293a828dd70` |
| Overall | FIX-NOW |

Full active statute corpus (65 leaves — 19 universal + 46 scoped) scored in-session against `git diff origin/dev...origin/sub/AST-1186/AST-1211-ast-756-fixture-lockstep-for-evaluate-craft-rows`. Diff has zero `src/**` / `scripts/**` / `data/admin/**` paths (product touch is `docs/uat-fixtures/AST-756/expected-agent_task.json` only, +38/−0), so 41 of 46 scoped statutes are `not-applicable` (no matching layer/path). Five scoped statutes matched and conform (`astral.docs.features-single-file-per-ticket`, `astral.debug.spikes-under-debug-dir`, `astral.git.betty-no-src-or-features`, `astral.git.engineer-test-tree-ban`, `astral.seed.define-approved`). Universal: 17 conform, 1 not-applicable (`orch.roles.archie-approves-statutes` — no `canon/statutes/**` diff path), **1 violates**.

**fix-now — `orch.git.merge-on-checkout` not run at checkout.** This sub's merge-base with `origin/ftr/AST-1186-evaluate-meteorite-fold-recent-work-into-tests` is `0d926c08` (an `origin/tests` ancestor shared by coincidence), not the ftr tip. Verified independently: `git merge-base --is-ancestor origin/ftr/AST-1186-... origin/sub/AST-1186/AST-1211-...` → **NO**; and `src/core/dispatcher.py` on this sub's tip still carries the **pre-AST-1209** docstring/logic (`retire stale evaluate_jd@METEORITE_NEW (AST-1060)`) rather than AST-1209's shipped twin-aware retirement — because this sub branched off `origin/dev` directly and never merged the already-resolved `origin/ftr/AST-1186` tip (which had AST-1209's `resolve(AST-1209): — clean` landed at 06:03:37, six minutes before this ticket's Plan Ready). No content collision today — this diff touches only the UAT fixture, not `dispatcher.py` — but the sub is stacked on a stale seed per the statute's own example (\"coding on a sub that has not merged an advanced ftr tip with sibling landings\"). **Remedy:** `git fetch origin && git merge origin/ftr/AST-1186-evaluate-meteorite-fold-recent-work-into-tests` on this sub before `merge-child` folds it into ftr, so the rolled-up parent tip (including AST-1209) is actually present.

**Plan adherence:** Stage 1 done-when met exactly — fixture now 53/53 rows matching catalog, verified independently (Python object-equality check, not just trusting the manifest): `evaluate_meteorite` and `craft_evaluate_meteorite_rubric` are byte/object-identical to catalog; the same 13 shared rows (`craft_*`, `evaluate_jd`, `grade_*`, `meteorite_like`) still differ only in prompt fields, confirming the plan's refusal to absorb unrelated drift held. Insert is a pure addition (+38/−0, zero deletion lines) satisfying Joan's finding #1 gate. Joan's finding #2 (stale `TestAst786AgentTaskRepoJsonSeed` docstring / bible note) is closed by Betty's `test(AST-1211)` commit, not the engineer — commit-role separation clean (`code(AST-1211)` → fixture only; `test(AST-1211)` + one `merge-tests(AST-1211)` SHA → `tests/` + `docs/test-bible/` only).

**Pattern conformance:** none cited in the ticket description.

## Frame diff
(none) — description AC/In-scope/Boundaries checkboxes already reflect the shipped diff.

**What's solid:** Surgical insert exactly matches the plan's anchor-adjacency placement (`craft_evaluate_meteorite_rubric` after `craft_jobdesc_rubric`; `evaluate_meteorite` after `evaluate_jd`); catalog (`data/admin/agent_task.json`) confirmed byte-for-byte untouched.

context_tokens≈48000

— Radia

## Resolution

**Date:** 2026-08-06  
**Publish tip after resolve:** see `resolve(AST-1211)` commit(s) on `origin/sub/AST-1186/AST-1211-ast-756-fixture-lockstep-for-evaluate-craft-rows`

| Finding | Action |
|---------|--------|
| **fix-now** — `orch.git.merge-on-checkout`: sub not ancestor of `origin/ftr/AST-1186-evaluate-meteorite-fold-recent-work-into-tests` | Merged `origin/ftr/AST-1186-evaluate-meteorite-fold-recent-work-into-tests` into this sub (`resolve(AST-1211): merge origin/ftr/AST-1186 tip`). Verified `git merge-base --is-ancestor origin/ftr/… HEAD` → yes; `src/core/dispatcher.py` now carries AST-1209 twin-aware `evaluate_jd@METEORITE_*` retirement. Fixture lockstep (53 rows; both evaluate/craft keys object-equal to catalog) re-checked after merge — unchanged. |

No product edits to the UAT fixture or catalog in resolve. Frame diff: none.
