# AST-1154 — Rubric completeness contracts (all graded tasks)

**Linear:** [AST-1154](https://linear.app/astralcareermatch/issue/AST-1154/rubric-completeness-contracts-all-graded-tasks-technical-fail-for-do)  
**Parent:** [AST-1150](https://linear.app/astralcareermatch/issue/AST-1150/technical-fail-for-do-prompt) — Technical fail for Do prompt  
**Project:** Astral Consult  
**Publish ref:** `sub/AST-1150/AST-1154-rubric-completeness-contracts-all-graded-tasks`

Harden model-facing instructions so every rubric grading task (Do/Get/Like, JD, qualify, prefilter, meteorite twins) requires a grade segment for **every** expected rubric code. `X`/`0` is the correct no-signal answer; omitting a code is forbidden. This ticket owns the **prompt / `{$OUTPUT_INSTRUCTIONS}` contract** only — retry-state routing and Skipped Retry stay with siblings.

**Non-goals:** Incomplete-grade → retry holding (AST-1155). Skipped Retry landing (AST-1156). Scoring math for complete grade sets. Live-rubric enforcement / `_render_score` missing-vector handling. New debug emission. `qualify_meteorite` (fields extract, not rubric-graded). `vet_inflow_discovery` (single fixed `LT` segment, not a multi-vector rubric set).

---

## Decisions (locked for build)

1. **Shared contract lives in `payload_instructions`.** Completeness language is added once to the four multi-vector `ASTRAL_CONFIG["output_types"]` entries that graded tasks inject via `{$OUTPUT_INSTRUCTIONS}` — not duplicated as four independent rewrites with drift risk.
2. **Task cache prompts reinforce the same rule.** Repo-owned `data/admin/agent_task.json` (and the AST-756 fixture twin) get an identical marker + VALIDATE/Rules line on every multi-vector graded task so Manage Tasks / UAT can see the contract without reading config source.
3. **No `database.py` prompt migration.** AST-1108 made `_apply_ast776/822/880_*` no-ops; startup `apply_agent_task_repo_json_startup` applies repo JSON. Edit the JSON catalog only.
4. **No product validation / retry changes here.** `do_task` / `consult` incomplete-set routing remains AST-1155. This plan must not alter `_validate_grades`, `_render_score`, or error-state maps.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Shared completeness clause on multi-vector encoded `payload_instructions` | utils |
| `data/admin/agent_task.json` | Completeness marker + VALIDATE/Rules lines on graded task `cache_prompt`s | data |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Byte-identical to updated `agent_task.json` (AST-786 identity) | docs |

**Out of scope:** `src/core/agent.py`, `src/core/consult.py`, `src/data/database.py`, `src/ui/**`, `tests/**`, `docs/test-bible/**`, craft-rubric tasks, `qualify_meteorite`, `grades_encoded_vet_meta`.

---

## Stage 1: Shared `{$OUTPUT_INSTRUCTIONS}` completeness clause

**Done when:** All four multi-vector encoded output types include the same completeness paragraph; `grades_encoded_vet_meta` and unused `grades_json` are unchanged; a one-liner import check prints `ok`.

1. In `src/utils/config.py`, immediately above the `ASTRAL_CONFIG["output_types"]` dict (near the existing output-type registry comment ~line 3476), add a module-level string constant:

   ```python
   # AST-1154: injected into multi-vector grades_encoded* payload_instructions (not vet / grades_json).
   _ENCODED_GRADE_SET_COMPLETENESS = (
       "GRADE SET COMPLETENESS (AST-1154) — mandatory:\n"
       "Emit exactly one grade segment for every rubric vector code listed in the grading "
       "instructions for this run. Omitting a code is invalid.\n"
       "When there is no signal for a vector, emit {code}X0 — never skip that segment.\n"
       "Do not invent extra codes beyond the rubric. Do not invent letter grades to fill gaps — "
       "use X with confidence 0 when the source is silent."
   )
   ```

2. Append `"\n\n" + _ENCODED_GRADE_SET_COMPLETENESS` to the end of `payload_instructions` for exactly these keys (leave examples and existing format rules intact; append after the example block):

   - `grades_encoded`
   - `grades_encoded_notes`
   - `grades_encoded_meta`
   - `grades_encoded_prefilter_links`

3. Do **not** append to `grades_encoded_vet_meta` (single `LT` segment) or `grades_json` (unused / not multi-vector encoded).

4. Verify:

   ```bash
   python3 -c "
   from src.utils import config as c
   marker = 'GRADE SET COMPLETENESS (AST-1154)'
   ots = c.ASTRAL_CONFIG['output_types']
   for k in ('grades_encoded', 'grades_encoded_notes', 'grades_encoded_meta', 'grades_encoded_prefilter_links'):
       assert marker in ots[k]['payload_instructions'], k
   assert marker not in ots['grades_encoded_vet_meta']['payload_instructions']
   assert marker not in ots['grades_json']['payload_instructions']
   print('ok')
   "
   ```

⚠️ **Decision:** Append (do not rewrite) existing format prose — token/confidence digit tables stay; completeness is an additive mandatory rule. DRY via one constant so the four types cannot drift.

---

## Stage 2: Repo `agent_task` prompts for all multi-vector graded tasks

**Done when:** Every listed task’s current `cache_prompt` contains the AST-1154 marker and an explicit “every code / X0 / omission forbidden” line; `expected-agent_task.json` is byte-identical to `data/admin/agent_task.json`.

1. In `data/admin/agent_task.json`, for each current (`"current": 1`) row with `task_key` in:

   - `prefilter_company`
   - `qualify_job_listings`
   - `evaluate_jd`
   - `grade_do`
   - `grade_get`
   - `grade_like`
   - `meteorite_like`

   edit **only** `cache_prompt` as follows (leave `user_prompt`, agent_id, grouping, `run_next`, uuids, `updated_at` unchanged):

   a. If the string `GRADE SET COMPLETENESS (AST-1154)` is already present, skip that row (idempotent hand-edit).

   b. Otherwise insert the following block **immediately before** the `## PAYLOAD INSTRUCTIONS` heading (or before `{$OUTPUT_INSTRUCTIONS}` if a task lacks that heading — today all seven have `## PAYLOAD INSTRUCTIONS`):

   ```text
   ## GRADE SET COMPLETENESS (AST-1154)
   Every rubric vector code in {$RUBRIC_VECTORS} (or the rubric listed above) MUST appear as exactly one encoded grade segment on that job's line. Omitting a code is invalid. When the source is silent, emit {code}X0 — never skip the segment. Do not add codes that are not in the rubric.
   ```

   c. Additionally tighten the existing VALIDATE / Rules language on these weaker rows (exact edits — do not rewrite surrounding steps):

   - **`evaluate_jd`** — in STEP 3, after “Check that the codes and grades you used are valid.”, append: ` Confirm every rubric vector code appears exactly once; use X0 when silent — never omit a code.`
   - **`qualify_job_listings`** — after STEP 4’s example line, append a new sentence on its own line: `Every rubric vector code must appear exactly once per job line; use X0 when silent — never omit a code.`
   - **`grade_do` / `grade_get` / `grade_like` / `meteorite_like`** — in STEP 3, after “**every** rubric vector present”, append: ` Omitting a code is invalid; silent vectors must be {code}X0.`
   - **`prefilter_company`** — after Rules item 1 (“Grade every vector in the rubric…”), append: ` Omitting a code is invalid; silent vectors must be X0.`

2. Sync the UAT fixture (AST-786 identity contract):

   ```bash
   cp data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json
   cmp -s data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json && echo identical
   ```

3. Verify marker coverage:

   ```bash
   python3 -c "
   import json
   from pathlib import Path
   keys = {
       'prefilter_company','qualify_job_listings','evaluate_jd',
       'grade_do','grade_get','grade_like','meteorite_like',
   }
   marker = 'GRADE SET COMPLETENESS (AST-1154)'
   for path in (
       Path('data/admin/agent_task.json'),
       Path('docs/uat-fixtures/AST-756/expected-agent_task.json'),
   ):
       rows = json.loads(path.read_text())
       for k in keys:
           r = next(x for x in rows if x.get('task_key')==k and x.get('current')==1)
           assert marker in (r.get('cache_prompt') or ''), f'{path}:{k}'
   print('ok')
   "
   ```

⚠️ **Decision:** Meteorite Do/Get reuse `grade_do` / `grade_get` agent_task rows (dispatch twins share prompts); only `meteorite_like` is a separate twin key — all three meteorite graded hops are covered by the seven-key list. Do **not** invent a new `database.py` migration; repo JSON is authoritative at startup.

---

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each tip to `origin/sub/AST-1150/AST-1154-rubric-completeness-contracts-all-graded-tasks`.
- Do not edit files outside the Files Changed table.
- If a step is ambiguous, contradicts the codebase, or fails when followed literally — stop and comment on **parent AST-1150** with the Stage N blocked template. No improvisation.
- After both stages: hand-confirm Manage Tasks (or a local DB after app start / repo-json apply) shows the AST-1154 marker on `grade_do` `cache_prompt` and that `{$OUTPUT_INSTRUCTIONS}` resolution for `grade_do` includes the completeness paragraph (Ad Hoc prompt preview or debug assemble — optional; config assert in Stage 1 is sufficient for build gate).

---

## Self-Assessment

**Scope:** `Single-Component` — utils `payload_instructions` plus repo-owned graded-task prompt catalog; no core apply/retry path.

**Conf:** `high` — pattern matches AST-880/AST-786 repo-JSON prompt authority and existing `{$OUTPUT_INSTRUCTIONS}` injection; scope excludes the harder retry routing sibling.

**Risk:** `Medium` — prompt wording can change model behavior and token shape; a bad edit to `agent_task.json` would diverge Manage Tasks / fixture identity, but scoring/retry paths are untouched so complete-grade math stays stable.

---

## Self-review vs `ASTRAL_CODE_RULES.md`

| Section | Check |
|---------|--------|
| §1.3 DRY | Completeness prose is one `_ENCODED_GRADE_SET_COMPLETENESS` constant shared by four output types; agent_task block is one identical insert across seven keys |
| §2.1 config | Contract text lives in `ASTRAL_CONFIG["output_types"]`; no hard-coded completeness set in core |
| §2.3.1 grade-vector-validation | Model contract requires full code set; enforcement/retry remains AST-1155 — this plan does not weaken or relocate `_validate_grades` |
| §2.3.2 confidence-bounds | Explicitly requires `X0` for silence; forbids inventing letter grades to fill gaps |
| §1.5.1 debug-contract-gated | No new debug lines |
| §3.3 imports | No new cross-layer imports |
| §3.5 naming | Constant `_ENCODED_GRADE_SET_COMPLETENESS` + marker `AST-1154` |

**Conflicts:** None.

---

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-1150/AST-1154-rubric-completeness-contracts-all-graded-tasks`  
**Product commits:**
- `0c07b966` — Stage 1: `_ENCODED_GRADE_SET_COMPLETENESS` on four multi-vector `payload_instructions`
- `e62fb471` — Stage 2: AST-1154 completeness marker + VALIDATE/Rules on seven graded `agent_task` cache prompts; AST-756 fixture byte-identical

**Local verification:** Stage 1 import assert on marker presence/absence; Stage 2 marker coverage + `cmp` fixture identity.

---

## Radia review

**[code-rubric] revision=1** · **Publish ref:** `5842580113fbc6f228d7cb56b073d47ed54e08e1` · **Overall:** DISCUSS

Full active statute set (65) scored in-session — 0 fix-now. Stage 1 / Stage 2 diffs match the plan verbatim (constant on exactly the 4 planned keys, absent from `grades_encoded_vet_meta` / `grades_json`; all 7 planned `agent_task` rows carry the marker + tighteners; fixture byte-identical on the publish tip).

**discuss — `astral.standards.names-not-ticket-ids`.** Carried from Joan's plan-rubric verdict: `GRADE SET COMPLETENESS (AST-1154)` doubles as the Stage 2 idempotency sentinel and ships in production `cache_prompt` text. Non-blocking (in-file precedent: `AST-723_RUBRIC_VECTORS_TOKEN`); engineer's call, exercised — kept the ticket-id sentinel.

**Notes:** 3 statutes Joan excluded at plan time (`astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`) score `conforms` on the diff-based sweep — the actual diff includes this plan doc and the pipeline's later test/test-bible commits, neither of which sit in the plan's Files-Changed table by convention. Both clean; not scope creep. Per-commit role separation verified: `code()` commits never touch `tests/**` / `docs/test-bible/**`; `test()` / `merge-tests()` commits never touch `src/**` / `docs/features/**`.

— Radia
