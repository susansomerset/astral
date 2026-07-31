# Anomaly — JOB_ARTIFACT_ENTRY_TASK_KEYS + cover-letter carve-out

**Linear:** [AST-1111](https://linear.app/astralcareermatch/issue/AST-1111/anomaly-job-artifact-entry-task-keys-cover-letter-carve-out-hard-coded)  
**Parent:** [AST-1109](https://linear.app/astralcareermatch/issue/AST-1109/hard-coded-daisy-chain-in-configpy) — Hard-coded daisy chain in config.py  
**Publish ref:** `sub/AST-1109/AST-1111-anomaly-job-artifact-entry-task-keys`

Delete the config shadow `JOB_ARTIFACT_ENTRY_TASK_KEYS` and its wrapper `build_artifacts_chain_task_keys()` (cover-letter frozenset carve-out) end-to-end against statute `astral.dispatch.run-next-is-chain-authority` (AST-1110). Product chain membership for this surface already comes from `agent_task.run_next` via §2.6.0 helpers — do not invent a replacement membership frozenset. Leave hop_task_keys / craft_task_keys / AST-1108 to siblings.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Delete `JOB_ARTIFACT_ENTRY_TASK_KEYS` and `build_artifacts_chain_task_keys()` (comment + frozenset + wrapper) | utils |

## Stage 1: Delete job-artifact entry shadow + cover-letter carve-out

**Done when:** Neither `JOB_ARTIFACT_ENTRY_TASK_KEYS` nor `build_artifacts_chain_task_keys` exists in `src/`; `rg` over `src/` for both names returns zero matches; `python3 -m py_compile src/utils/config.py` succeeds; §2.6.0 helpers (`_agent_task_parents_with_run_next`, `dispatch_chain_row_matches_job`, `dispatch_chain_claim_states_for_row`, `is_dispatch_chain_trigger`, `is_valid_job_batch_claim_state`) are unchanged by this stage.

1. In `src/utils/config.py`, locate the block immediately after `is_conversational_task` (currently ~lines 932–949):

   - Comment: `# Dispatch consult hops that enter the job-artifact chain…` / `# Excludes draft_cover_letter…`
   - Constant: `JOB_ARTIFACT_ENTRY_TASK_KEYS = frozenset({…})`
   - Function: `build_artifacts_chain_task_keys()` whose body is `frozenset(JOB_ARTIFACT_ENTRY_TASK_KEYS) - frozenset({"draft_cover_letter"})`

2. Delete that entire block (comment + constant + function). Leave the preceding `is_conversational_task` and the following `CONFIDENCE_*` section adjacent with a single blank line between them (match neighboring style).

3. Do **not** add a replacement frozenset, helper, or cached set of “entry keys” derived from `run_next`. Membership authority for this surface is already:

   - `is_dispatch_chain_trigger` + `task_key in TASK_CONFIG` → `_run_dispatch_chain_job_batch` in `src/core/consult.py`
   - `dispatch_chain_row_matches_job` / `dispatch_chain_claim_states_for_row` / `_agent_task_parents_with_run_next` (read live `agent_task.run_next`)
   - `_current_agent_task_run_next` for hop succession inside `do_task`

4. Do **not** edit `src/core/consult.py`, `src/core/dispatcher.py`, `src/core/agent.py`, or any other `src/**` file in this stage unless step 5 forces a stop.

5. Verify on epic worktree:

   ```bash
   rg -n 'JOB_ARTIFACT_ENTRY_TASK_KEYS|build_artifacts_chain_task_keys' src/
   python3 -m py_compile src/utils/config.py
   ```

   Expect zero `rg` hits under `src/`. If any `src/` consumer still imports either name, **stop** and comment on parent AST-1109 with the Stage N blocked template (do not invent a shim).

6. Do **not** touch:

   - `BUILD_CONFIG.resume_artifact_chain.hop_task_keys` / `_RESUME_ARTIFACT_HOP_TASK_KEYS` / `resume_artifact_hop_task_keys` (AST-1112)
   - `CANDIDATE_STAGE_DISPATCH` `craft_task_keys` or boot SQL (AST-1113)
   - `_dispatch_trigger_state_for_task_key` defaults for `draft_cover_letter` / cover hops (admin Save defaults — not this frozenset carve-out)
   - `tests/**`, `docs/test-bible/**`, `docs/ASTRAL_TEST_BIBLE.md` (Betty owns; expect existing assertions on these symbols to fail until Betty revises)
   - Statute / pattern / CODE_RULES files (already landed by AST-1110)

⚠️ **Decision:** Delete-only remediation. Tip survey shows both symbols are defined in `config.py` and referenced only from `tests/component/utils/test_config.py` — consult already routes job-artifact / cover hops through `is_dispatch_chain_trigger` + `TASK_CONFIG` (AST-848/849), so “wire membership to `run_next`” is already the live path; replacing the frozenset with another config set would re-violate `astral.dispatch.run-next-is-chain-authority`. Cover-letter special exclusion lives only in that dead comment + wrapper subtraction — deleting the block eradicates it without a new carve-out.

## Execution contract

- Stages in order; one commit per stage on the epic worktree sub branch; publish to `origin/<publish-ref>` after each stage per build-child.
- No files outside the Files Changed table.
- Ambiguity or codebase drift → stop and comment on **parent** AST-1109 with the Stage N blocked template.
- Leave hop_task_keys, craft_task_keys, boot SQL, Manage Tasks UI, AST-1108, and Betty’s test tree untouched.

## Self-Assessment

**Scope:** `minor` — delete one unused frozenset and its cover-letter-subtraction wrapper in `src/utils/config.py`; no core/UI routing edits required on tip.

**Conf:** `high` — symbols have zero `src/` consumers after AST-849; statute + parent AC name this exact shadow; sibling surfaces are explicitly out of scope.

**Risk:** `low` — product path already ignores these symbols; wrong delete would only matter if a hidden consumer appears (step 5 stop gate). Betty must revise tests that still assert membership / carve-out — engineer must not patch `tests/`.

## Self-review vs ASTRAL_CODE_RULES

- **§2.6.0 / `astral.dispatch.run-next-is-chain-authority`:** Removes the named violating example; does not replace it with another hop-membership list; leaves claim/graduation helpers that read `run_next` intact.
- **§1.4 / no-hardcoded-sets:** Does not “fix” by moving the set elsewhere in config — deletes the shadow.
- **§1.1 / in-scope-only:** No hop_task_keys, craft_task_keys, boot SQL, or AST-1108.
- **§1.3 DRY:** No new parallel membership helper.
- **§3.3 imports:** No new imports; unused import cleanup N/A (symbols were not imported elsewhere under `src/`).
- **Betty test-tree ban:** Plan forbids engineer edits under `tests/` / bible.
- **No conflict requiring conf-!!-NONE.**

## Review

**Publish ref:** `origin/sub/AST-1109/AST-1111-anomaly-job-artifact-entry-task-keys`
**Tip:** `88ab9675`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `88ab9675` | delete JOB_ARTIFACT_ENTRY_TASK_KEYS + build_artifacts_chain_task_keys |

### Radia — code-rubric.v1 (AST-1111)

`[code-rubric] revision=1` · tip reviewed `230c0f4c` · **Overall: DISCUSS** (C4 stragglers only; deliverable conforms)

**What's solid**

- Delete-only: `JOB_ARTIFACT_ENTRY_TASK_KEYS` + `build_artifacts_chain_task_keys()` gone; zero `src/` hits; no replacement membership list.
- §2.6.0 helpers untouched; hop_task_keys / craft_task_keys / boot SQL left to siblings.
- Betty owns test/bible retirement of frozenset asserts; engineer Stage 1 is `config.py` only.

**Discuss (C4 stragglers)** — Joan excluded many scoped statutes via plan `change_types={delete}`; three-dot git status is `modify`/`add`, so they are in-scope here (scores themselves `conforms`). See Linear comment for the full list.
