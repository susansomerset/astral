# Revert hard coded-advice / adherence landing (Advise resume needs a coded list for clear adherence)

**Linear:** [AST-1523](https://linear.app/astralcareermatch/issue/AST-1523/revert-hard-coded-advice-adherence-advise-resume-needs-a-coded-list)
**Parent:** [AST-1460](https://linear.app/astralcareermatch/issue/AST-1460/advise-resume-needs-a-coded-list-for-clear-adherence) — Advise resume needs a coded list for clear adherence
**Publish ref:** `origin/sub/AST-1460/AST-1523-revert-hard-coded-advice-adherence`

Undo the AST-1460-family **hard** coded-advice / per-code adherence landing on `advise_job_resume` → `draft_job_resume` (config keys, validate/normalize, artifact persist, `do_task` hooks, Manage Tasks prompt wording that requires `[R#]` / `advice_adherence` objects). Restore pre-epic deliverable expectations with freeform draft **`notes`** (Archie: rename from `deviations` if that was the prior metadata field). Does **not** author the soft numbered-prose prompt rewrite (sibling child #2). Does **not** revive canceled AST-1507 / AST-1508 / AST-1514.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Remove all `resume_advice_*` / `advice_adherence_*` keys and asserts; restore draft freeform `notes` metadata + clear-key membership | utils |
| `src/core/candidate.py` | Delete coded-list and advice_adherence normalize/validate helpers and call sites | core |
| `src/core/tracker.py` | Delete resume_advice / advice_adherence extract/save/persist (+ `get_job_resume_advice_codes`); restore freeform `notes` extract/save/persist (AST-1271 shape, renamed) | core |
| `src/core/agent.py` | Remove advise coded-list validate + persist hooks; remove draft advice_adherence validate helper + persist hook; restore draft `notes` persist-on-success (AST-1271 pattern) | core |
| `data/admin/agent_task.json` | Restore `advise_job_resume` / `draft_job_resume` `user_prompt` away from hard `[R#]` / `advice_adherence` contracts to pre-epic freeform baseline (`notes`) | data/admin |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Whole-file twin `cp` after prompt restore | docs |

**Betty-owned (not engineer commits — `astral.git.engineer-test-tree-ban`):** retire or rewrite `tests/**` and `docs/test-bible/**` coverage that asserts AST-1507 / AST-1508 / AST-1514 hard coded-advice / adherence contracts so CI matches the soft product after this tip. Flag in Code Complete comment for qa-child.

**Out of scope:** soft numbered-prose Estelle/Judith prompt rewrite (sibling #2); Approve Artifacts UI; Resume upshot; `run_next` rewiring; reviving canceled children.

⚠️ **Decision — freeform metadata name is `notes`, not `deviations`:** Archie: restore freeform `notes`; if the prior field was `deviations` in RESPONSE_SCHEMA / payload metadata, rename it to `notes`. Tip currently has `advice_adherence` (AST-1508 replaced AST-1271 `deviations`). This revert removes `advice_adherence` and restores the AST-1271 freeform **string-list** sibling metadata path under the name **`notes`** (`notes_artifact_key`, `payload_metadata_keys`, clear-keys, prompt JSON example, persist helpers).

## Stage 1: Config — strip epic keys; restore `notes`

**Done when:** `TASK_CONFIG["advise_job_resume"]` has no `resume_advice_*` / coded-list keys; `TASK_CONFIG["draft_job_resume"]` has no `advice_adherence_*` keys; `payload_metadata_keys` includes `"notes"` and not `"advice_adherence"` / `"deviations"`; `JOB_BUILD_ARTIFACT_CLEAR_KEYS` includes `"notes"` and not `"resume_advice"` / `"advice_adherence"`; epic-specific asserts for those keys are gone; module still imports.

1. In `src/utils/config.py` `TASK_CONFIG["advise_job_resume"]`, **delete** every key added for AST-1507/AST-1514, including (names as present on tip):
   - `resume_advice_coded_list`
   - `resume_advice_section_header` / `resume_advice_section_end_header`
   - `resume_advice_code_prefix` / `resume_advice_bracket_open` / `resume_advice_bracket_close`
   - `resume_advice_cite_separator`
   - `resume_advice_artifact_key` / `resume_advice_min_items`
   - `resume_advice_json_key` if present
2. In `TASK_CONFIG["draft_job_resume"]`:
   - Remove `advice_adherence_required` and every `advice_adherence_*` key.
   - Change `payload_metadata_keys` so `"advice_adherence"` is **replaced by** `"notes"` (keep `astral_job_id`, `company`, `title`, `task_success`).
   - Add `"notes_artifact_key": "notes"` (same role as former `deviations_artifact_key` / `advice_adherence_artifact_key`).
   - Comment: `# AST-1523: freeform draft notes (Archie rename from deviations; replaces advice_adherence)`.
3. In `JOB_BUILD_ARTIFACT_CLEAR_KEYS`: remove `"advice_adherence"` and `"resume_advice"`; add `"notes"` with comment tying it to `draft_job_resume.notes_artifact_key`.
4. Delete module-level asserts that pin `resume_advice_*` / `advice_adherence_*` / `"deviations" not in …`. Add minimal asserts:

   ```python
   _djr = TASK_CONFIG["draft_job_resume"]
   assert _djr["notes_artifact_key"] == "notes"
   assert "notes" in _djr["payload_metadata_keys"]
   assert "advice_adherence" not in _djr["payload_metadata_keys"]
   assert "notes" in JOB_BUILD_ARTIFACT_CLEAR_KEYS
   assert "resume_advice" not in JOB_BUILD_ARTIFACT_CLEAR_KEYS
   assert "advice_adherence" not in JOB_BUILD_ARTIFACT_CLEAR_KEYS
   ```

5. Do **not** add soft-prose config keys for sibling #2.

## Stage 2: Candidate — delete coded-list + adherence validate

**Done when:** no `parse_advise_*` / `validate_advise_*` / `*_advice_adherence*` public helpers remain; `normalize_draft_job_resume_agent_payload` no longer calls adherence normalize; grep of `src/core/candidate.py` for `resume_advice` / `advice_adherence` / `RESUME BRIEF section` is empty (except unrelated comments if any).

1. Delete the entire AST-1507/AST-1514 advise coded-list block: `_advise_resume_advice_task_cfg`, `_extract_advise_section_text`, `_coerce_advise_section_body` (if present), `_advise_coded_line_re`, `_parse_advise_coded_line`, `_collect_advise_coded_advice`, `parse_advise_job_resume_coded_advice`, `validate_advise_job_resume_coded_list`.
2. Delete the entire AST-1508 adherence block: `_draft_advice_adherence_task_cfg`, `normalize_draft_job_resume_advice_adherence`, `validate_draft_job_resume_advice_adherence`.
3. In `normalize_draft_job_resume_agent_payload` (and any other draft normalize path), remove the call to `normalize_draft_job_resume_advice_adherence`. Metadata skip continues via `payload_metadata_keys` (now includes `notes`) — no special adherence coerce.
4. Do **not** add replacement validators for soft prose.

## Stage 3: Tracker — delete epic persist; restore `notes` helpers

**Done when:** no `resume_advice` / `advice_adherence` extract/save/persist / `get_job_resume_advice_codes`; freeform `notes` extract/save/persist exist and are wired like AST-1271 deviations (string or list → `list[str]`; key absent → `None`; present empty → `[]`); `persist_job_artifact_from_parsed` writes notes when present; `_resume_payload_body` still skips metadata via `payload_metadata_keys` (so `notes` never becomes a resume section).

1. Delete: `get_job_resume_advice_codes`, `extract_advise_job_resume_coded_advice`, `save_job_artifact_resume_advice`, `persist_advise_job_resume_coded_advice`, `extract_draft_job_resume_advice_adherence`, `save_job_artifact_advice_adherence`, `persist_draft_job_resume_advice_adherence`.
2. Add (mirror AST-1271 deviations helpers, rename field to notes — read key only from config):

   - `extract_draft_job_resume_notes(parsed) -> Optional[List[str]]` — `meta_key = TASK_CONFIG["draft_job_resume"]["notes_artifact_key"]`; same absent/`None`/str/list normalization as former `extract_draft_job_resume_deviations`.
   - `save_job_artifact_notes(astral_job_id, notes: List[str])` — write `artifacts[notes_artifact_key]`.
   - `persist_draft_job_resume_notes(astral_job_id, parsed) -> bool` — extract; if `None` return `False`; else save and return `True`.

3. In `persist_job_artifact_from_parsed`, replace the advice_adherence persist call with `persist_draft_job_resume_notes` (ungated on `allow_resume`, same as AST-1271).
4. Confirm `_resume_payload_body` still skips nest + `payload_metadata_keys` — no hardcoded `"notes"` literal required beyond config membership.

## Stage 4: Agent — remove hard hooks; restore notes persist

**Done when:** `do_task("advise_job_resume")` no longer validates coded RESUME BRIEF or persists `resume_advice`; `do_task("draft_job_resume")` no longer requires/validates `advice_adherence` against advise codes; on draft success, freeform `notes` persist runs (best-effort, try/except, same placement as former deviations / advice_adherence hook).

1. Delete `_validate_draft_advice_adherence_for_do_task` (or equivalent) and every call site that loads `get_job_resume_advice_codes` / `validate_draft_job_resume_advice_adherence`.
2. Delete the AST-1507/AST-1514 advise block that gates on `resume_advice_coded_list` / `validate_advise_job_resume_coded_list` (failure path + store).
3. Delete the advise success persist block calling `persist_advise_job_resume_coded_advice`.
4. Replace the draft success persist block that calls `persist_draft_job_resume_advice_adherence` with `persist_draft_job_resume_notes` (lazy import; best-effort log on exception; optional Style D `recorded artifact_key=…` when `debug=True` using `notes_artifact_key`).
5. Leave unrelated draft validate (`validate_draft_job_resume_payload`, nest unwrap, experience pin) unchanged.

## Stage 5: Manage Tasks prompts — pre-hard-contract baseline

**Done when:** advise `user_prompt` no longer requires `[R#]` / ` — cite:` machine lines; draft `user_prompt` no longer requires `advice_adherence` objects or “one entry per RESUME BRIEF code”; draft JSON example uses freeform `"notes": ["…"]`; COVER LETTER DIRECTION / ASK CANDIDATE section purpose unchanged; `run_next` / cache prompts / agent ids untouched. Soft numbered-prose rewrite is **not** this stage (sibling #2).

1. In `data/admin/agent_task.json`, edit `"task_key": "advise_job_resume"` / `"current": 1` **`user_prompt` only**. Replace the coded RESUME BRIEF paragraph with the pre-epic freeform wording:

   > RESUME BRIEF  
   > Enumerated, concrete instructions: what to promote, cut, reorder, reframe, each with its citation. Reframing means new emphasis on true content, not new content. Solve Atlas's #1 objection first.

   Keep HARD RULES and COVER LETTER DIRECTION / ASK CANDIDATE blocks as they are aside from removing any coded-list-only sentences.

2. Edit `"task_key": "draft_job_resume"` / `"current": 1` **`user_prompt` only**:
   - Remove lines that require `advice_adherence` / per-code status objects.
   - Restore skip/notes guidance: if a brief instruction lacks support, skip it and record under **`notes`** (not `deviations`, not `advice_adherence`).
   - JSON example sibling of `resume` must be `"notes": ["instruction skipped and why"]` (string array), matching `payload_metadata_keys`.
3. Do not edit other task rows. Do not land sibling #2 soft “A/B/C prose” wording here.

## Stage 6: UAT fixture twin

**Done when:** `docs/uat-fixtures/AST-756/expected-agent_task.json` is byte-identical to `data/admin/agent_task.json`.

```bash
cp data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json
cmp -s data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json && echo OK
```

## Estimate

Confirm Chuckles estimate: 5 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric.v1
**Ticket:** AST-1523
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1460/AST-1523-revert-hard-coded-advice-adherence` @ `238501d481a2043ed25363897c6f665e62f6c716`

### Traceability

AC1→S1–S2,S4–S5 (strip advise validate/persist + pre-epic advise prompt); AC2→S1,S3–S5 (`notes` metadata restore, no adherence gate); AC3→S6; AC4→Betty-owned bible/tests retire (engineer flags at Code Complete per plan header).

### Findings

#### discuss

- **Location:** Stage 4 step 1  
  **Finding:** Plan names `_validate_draft_advice_adherence_for_do_task`; tip has `_draft_job_resume_adherence_validation_err` with call sites ~2797 and ~3035.  
  **Recommendation:** Grep `advice_adherence` / `resume_advice` / `get_job_resume_advice_codes` across `src/core/agent.py` and delete all hooks (both pre- and post-decode paths).

- **Location:** Stage 2 / Stage 4  
  **Finding:** Grep gate is scoped to `candidate.py` only; epic symbols also live in `agent.py` and `tracker.py`.  
  **Recommendation:** Add a final repo-wide `src/` grep for `resume_advice`, `advice_adherence`, `validate_advise`, `parse_advise` after Stage 4 before Code Complete.

- **Location:** Stage 1 — `JOB_BUILD_ARTIFACT_CLEAR_KEYS`  
  **Finding:** Dropping `resume_advice` / `advice_adherence` clear slots leaves stale artifacts on in-flight jobs until manual cleanup or a new cancel cycle.  
  **Recommendation:** Acceptable for revert; note in UAT that pre-revert job rows may still carry old artifact keys.

#### acceptable

- **Location:** Decision block — `notes` vs `deviations`  
  **Finding:** Archie rename to `notes` is explicit; `payload_metadata_keys` / `notes_artifact_key` / prompt example aligned.  
  **Recommendation:** None.

- **Location:** Betty-owned tests/bible  
  **Finding:** Ticket Scope lists `tests/**` but `astral.git.engineer-test-tree-ban` holds; plan correctly assigns AC4 to Betty with engineer handoff comment.  
  **Recommendation:** None.

- **Location:** Stage 1 — `resume_advice_json_key`  
  **Finding:** "If present" covers AST-1514 residue not on current epic tip.  
  **Recommendation:** None.

### R6 checklist (summary)

Definition fidelity: child Scope matches six engineer stages + Betty AC4; no soft-prose sibling work; canceled children not revived. Layer/config: strip epic keys, restore `notes` via config block. Pattern `pattern.config.config-block` still governs metadata naming. DRY: AST-1271 deviations shape reused under `notes`. Boundaries: no UI, `run_next`, or soft prompt rewrite.

**Considered (in-session):** 18 universal (orchestration/git — conform); scoped product statutes on touched layers/paths — conform, including config/no-hardcoded-sets/in-scope-only/do-task-delegation/seed trio/test-tree ban (Betty split).

context_tokens≈62000

[plan-rubric] PROCEED (Commit: 238501d4) revert hard contract plan

## Review

**Branch:** `sub/AST-1460/AST-1523-revert-hard-coded-advice-adherence`  
**Tip:** `8f8f5a1785324b8373e2ad073cea99067f2dbfb3` (code); publish ref HEAD follows
**Notes for Betty:** retire AST-1507 / AST-1508 / AST-1514 hard-contract tests + bible (AC4); product tip no longer emits/validates `[R#]` / `advice_adherence`.

## Radia review

# Radia review — AST-1523

**Ticket:** AST-1523 (parent AST-1460)  
**Publish ref:** `origin/sub/AST-1460/AST-1523-revert-hard-coded-advice-adherence` @ `5d7ec0d4`  
**Baseline:** `origin/dev` (three-dot diff per skill)  
**Status gate:** Tests Passed (spawn prompt — trusted)  
**Internal grade:** **CLEAN**

---

[code-rubric] revision=2  
**Rubric:** code-rubric.v2  
**Ticket:** AST-1523  
**Publish ref:** `origin/sub/AST-1460/AST-1523-revert-hard-coded-advice-adherence` @ `5d7ec0d4db3fe47823a35d4ae59fad4dd740ad21`  
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no confidence/scoring path changes |
| astral.agent.do-task-delegation | scoped | conforms | hard hooks removed; notes persist on draft success |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade-vector changes |
| astral.batch.batch-id-first | scoped | not-applicable | no batch-id ordering changes |
| astral.batch.batch-id-format | scoped | not-applicable | no batch-id format changes |
| astral.batch.claim-process-release | scoped | not-applicable | no claim/process/release paths |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | no CALLER_RESPONSE re-parse; freeform advise text accepted |
| astral.config.config-source-of-truth | scoped | conforms | `notes_*` keys + clear slot; epic keys stripped |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no secrets/env literals |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug artifact paths |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no spike paths |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch seed flags |
| astral.dispatch.run-next-is-chain-authority | scoped | conforms | `run_next` untouched |
| astral.docs.features-single-file-per-ticket | scoped | conforms | plan doc on ticket slug |
| astral.git.betty-no-src-or-features | scoped | not-applicable | Radia read-only review |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer product-only; Betty landed tests via merge-tests |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no render-verdict paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | no new protected routes |
| astral.layers.core-vs-external-bright-line | scoped | conforms | core-only product changes |
| astral.layers.import-direction | scoped | conforms | lazy imports in `do_task` match file precedent |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no `scripts/` changes |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | no `src/ui/` product changes |
| astral.seed.agent-tables-in-repo-json | scoped | conforms | advise/draft prompts restored; UAT twin byte-identical to catalog on tip |
| astral.seed.archie-catalog-wins | scoped | conforms | repo JSON is prompt source |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no bootstrap hot-path edits |
| astral.seed.define-approved | scoped | not-applicable | not a define ticket |
| astral.seed.operator-rows-stay-deleted | scoped | conforms | only advise + draft current rows edited |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no coverage-join seed paths |
| astral.standards.data-raises-caller-logs | scoped | conforms | persist errors logged in `agent.py` caller |
| astral.standards.database-header-inventory | scoped | not-applicable | no DB schema/migration changes |
| astral.standards.debug-contract-gated | scoped | conforms | notes persist debug line only when `debug=True` |
| astral.standards.dry-and-focused-functions | scoped | conforms | AST-1271 deviations shape reused as `notes` |
| astral.standards.in-scope-only | scoped | conforms | revert scope matches plan; no soft-prose sibling work |
| astral.standards.logging-via-utils | scoped | conforms | `get_logger` throughout |
| astral.standards.names-not-ticket-ids | scoped | conforms | `notes` slot naming |
| astral.standards.no-cross-contamination | scoped | conforms | notes metadata never enters resume body |
| astral.standards.no-hardcoded-sets | scoped | conforms | config-owned keys; `payload_metadata_keys` tuple |
| astral.standards.public-then-helpers | scoped | conforms | public extract/persist + `_` helpers removed cleanly |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no utils→data imports |
| astral.state.core-decides-transitions | scoped | not-applicable | no job-state transition edits |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no prior-state logic |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no in-run daisy-chain |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend src changes |
| astral.ui.naming-conventions | scoped | not-applicable | no UI src naming |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no worker config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | `merge-tests(AST-1523)` tip present |
| orch.git.commit-vocabulary | universal | conforms | commit messages match vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | sub branch topology |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1460/...` publish ref |
| orch.git.merge-on-checkout | universal | conforms | n/a to review |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | n/a to review |
| orch.git.no-dev-agent-branches | universal | conforms | n/a to review |
| orch.git.one-epic-worktree-per-parent | universal | conforms | epic worktree AST-1460 |
| orch.git.three-permanent-branches | universal | conforms | diff vs `origin/dev` |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | `notes` rename documented in plan |
| orch.pipeline.plan-is-bible | universal | conforms | all six engineer stages delivered |
| orch.pipeline.project-scoped-queues | universal | conforms | n/a |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed gate satisfied |
| orch.roles.archie-approves-statutes | universal | conforms | n/a |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty retired AST-1507/1508 tests + bible |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | n/a |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada assignee at Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | n/a |

*Corpus registry lists 65 active statutes; table covers full harvested set from `canon/statutes/README.md` § Harvested corpus.*

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.config.config-block | conforms | `notes_artifact_key` + `payload_metadata_keys` + clear-keys + asserts; epic keys removed |

## Plan adherence

All six engineer stages delivered; Betty AC4 satisfied via `merge-tests(AST-1523)`:

- **S1** — `resume_advice_*` / `advice_adherence_*` stripped; `notes` restored in config + clear-keys + asserts
- **S2** — coded-list + adherence validate/normalize blocks deleted from `candidate.py`
- **S3** — epic tracker helpers deleted; `extract/save/persist_draft_job_resume_notes` restored (AST-1271 shape)
- **S4** — `_draft_job_resume_adherence_validation_err` + advise validate/persist hooks deleted; `persist_draft_job_resume_notes` on draft success
- **S5** — advise + draft prompts restored to freeform baseline (`notes` JSON sibling)
- **S6** — UAT twin byte-identical to `data/admin/agent_task.json` on tip (verified)

Joan discuss items addressed:

1. Repo-wide `src/` grep clean — only `deviations`/`advice_adherence`/`resume_advice` references are config comments/asserts (retirement checks).
2. Both pre- and post-decode adherence paths removed via shared helper deletion.
3. Persist debug uses `saved` bool from `persist_draft_job_resume_notes` return.

**Tip-to-tip vs `origin/dev`:** `agent_task.json` differs only on `advise_job_resume` + `draft_job_resume` `user_prompt` lines (two-dot verified). Three-dot diff includes merge-base catalog hunks — not product scope drift on tip.

## Findings

### advisory

- **Location:** Branch vs `origin/dev`  
  **Finding:** Publish ref is **1 commit behind** `origin/dev` (`616ddc8c docs(AST-1520): mirror epic registry Threads`).  
  **Recommendation:** `resolve-child` / merge-child should integrate `origin/dev` before ftr rollup — not a product defect.

- **Location:** Stage 1 — `JOB_BUILD_ARTIFACT_CLEAR_KEYS`  
  **Finding:** `resume_advice` / `advice_adherence` clear slots removed — stale artifacts may linger on in-flight jobs.  
  **Recommendation:** Acceptable per revert plan (Joan flagged); note for UAT.

- **Location:** `src/core/agent.py` — notes persist debug  
  **Finding:** Style D line logs `artifact_key` only (no `item_count`).  
  **Recommendation:** Matches plan optional shape; fine for revert.

## What's solid

- Complete surgical revert: ~486 lines of hard-contract code removed, AST-1271 deviations shape restored under Archie-approved `notes` name.
- `src/core/agent.py` has zero `resume_advice` / `advice_adherence` / `advise_job_resume` hook references.
- `src/core/candidate.py` has zero epic parse/validate helpers.
- Tracker tests cover string/list coercion, absent key → `None`, persist/cancel clear, body skip.
- Agent tests confirm freeform advise succeeds without coded validate and epic persist helpers are gone.
- Betty manifest aligned: AST-1507/1508/1514 hard-contract tests retired; AST-1523 coverage added.

## Frame diff

Plan frame: strip AST-1460 hard `[R#]` / `advice_adherence` contract; restore pre-epic freeform advise RESUME BRIEF + draft `notes` metadata.  
Diff delivers exactly that. No soft-prose sibling work, no UI, no `run_next` changes, canceled children not revived.

## Notes

- Joan plan-rubric verdict attached: **APPROVED**; no Excluded-statute stragglers.
- §5f / §5g not triggered.
- Test diff limited to AST-1523 manifest files (no sibling test-bundle issue seen on prior epic children).

---

```
[code-rubric] PROCEED (Commit: 5d7ec0d4) hard contract reverted cleanly
```

`context_tokens≈85000`

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/85ac6f0fa1af475870fb5e29868d2702/aa381d9d-1c4c-4402-9f6b-0f1d3659bab9/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/85ac6f0fa1af475870fb5e29868d2702/98e428fe-d73f-4bf8-aadc-905ea9059fbc/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/426a3cc3-2f83-4f6a-8ffd-ae96a2ab282d/store.db` |
| Radia | review | `/home/susan/.cursor/chats/85ac6f0fa1af475870fb5e29868d2702/1e8f7c20-baa2-4333-acf3-a550b0c688e3/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1460 (parent) | ftr/AST-1460-advise-resume-coded-list |
| AST-1507 | sub/AST-1460/AST-1507-estelle-coded-resume-advice-list |
| AST-1508 | sub/AST-1460/AST-1508-judith-per-code-advice-adherence |
| AST-1514 | sub/AST-1460/AST-1514-advise-resume-brief-validation |
| AST-1523 | sub/AST-1460/AST-1523-revert-hard-coded-advice-adherence |
| AST-1524 | sub/AST-1460/AST-1524-soft-numbered-prose-advise-draft-notes |

**Epic worktree:** `astral-AST-1460/` — one active sub checked out at a time.
