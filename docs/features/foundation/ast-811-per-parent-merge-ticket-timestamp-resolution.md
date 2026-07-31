<!-- linear-archive: AST-811 archived 2026-07-22 -->

## Linear archive (AST-811)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-811/per-parent-merge-ticket-timestamp-resolution-timestamps-for-issues  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-810 — timestamps for issues merged do not differentiate across branch merges  
**Blocked by / blocks / related:** parent: AST-810

### Description

## What this implements

Fix merge-ticket log rebuild so each parent epic in `data/merge_ticket_log.json` gets a `recorded_at` timestamp that reflects when that parent's own `ftr/*` branch merged onto `origin/dev` — not a shared timestamp from an unrelated dev commit or a bulk rebuild triggered by another parent. The rebuild CLI and prep-uat wiring must assign distinct per-parent timestamps when land times differ.

## Acceptance criteria

1. On a deploy built from `origin/dev` where `data/merge_ticket_log.json` lists at least two parent epics whose ftr branches merged onto dev at different times, hovering the admin env label shows **different** formatted timestamps for those parents (not all identical).
2. For a given parent epic AST-NNN in the log, `recorded_at` corresponds to the commit timestamp of the merge that brought that parent's `ftr/*` onto `origin/dev` — verifiable by inspecting dev git history for that parent — rather than the timestamp of an unrelated commit that merely touched the log file or refreshed the list for another parent.
3. Susan can identify the most recently landed parent in the tooltip by timestamp alone when multiple parents are listed.
4. After a prep-uat rebuild on dev, parents that previously shared an incorrect identical timestamp receive corrected distinct values where their actual land times differ.
5. Existing deploy-status payload shape and AST-691 tooltip behavior (empty list, non-admin, missing env) remain unchanged.

## Boundaries

* Does not change tooltip interaction, styling, line cap, or poll interval (AST-691 / AST-798).
* Does not change eligibility rules for which parent ids appear in the log (AST-791 / AST-800 / AST-805).
* Does not add ticket titles, child ids, or SHA display to the tooltip.
* Does not add runtime Linear filtering on deploy-status poll.
* Sibling scope: parent epic only — no unrelated foundation work.

## Notes for planning

* Primary touch: `scripts/rebuild_merge_ticket_log.py` timestamp resolution (`_resolve_recorded_at` and fallbacks per AST-800).
* Existing tests: `tests/component/scripts/test_rebuild_merge_ticket_log.py`, `test_record_landed_parent.py`.
* AST-800 established grep chain: `prep-uat(PARENT):` → `merge-parent(PARENT):` → `finish-up(PARENT):` → ftr merge fallback. Bug symptom: multiple parents share identical `recorded_at` when grep misses and fallback resolves to the same dev tip commit.
* Utils read path (`merge_ticket_log`, `deploy_status`) should remain unchanged unless a thin helper improves testability.

## Git branch (authoritative)

Per `orientation` **§ Branch law**: parent `ftr/ast-810-timestamps-for-issues-merged-do-not-differentiate-across-branch-merges`, child `sub/AST-810/<child-segment>`, standalone `ftr/<segment>`. Created at **dispatch-parent**. Engineers cherry-pick to `origin/<ftr-ref>` or `origin/<sub-ref>` — never Linear `gitBranchName` when it disagrees.

### Comments

#### chuckles — 2026-06-26T00:51:52.516Z
### Radia review — AST-811

**Diff:** `origin/dev...origin/sub/AST-810/AST-811-per-parent-merge-ticket-timestamp-resolution` @ `0e58a27`
**Doc:** `docs/features/foundation/ast-811-per-parent-merge-ticket-timestamp-resolution.md` (Radia review section)

**What's solid**
- `_resolve_recorded_at`: ritual grep chain preserved; ftr land greps (`merge origin/{ftr}`, remote-tracking variant) inserted before walk; dev-HEAD `git log dev ftr -1` fallback removed.
- `_first_ftr_land_on_dev`: merge-base..dev walk with merge-first stop when ftr tip is not on first parent; non-merge fallback to first inclusion commit.
- Plan fidelity: single-script scope; `_collect_entries` / CLI / utils read path unchanged.
- §1.3 / §3.3: DRY helpers; no layer violations.
- Smoke on `origin/dev`: AST-716 / AST-752 / AST-753 → three distinct ISO timestamps.
- Betty manifest: 8/8 pytest green (`TestRebuildMergeTicketLogTimestampResolution` + AST-805 regression).

**Counts:** 0 fix-now · 0 discuss · 0 advisory

**Outcome:** Clean — proceed with `resolve-child`.

#### betty — 2026-06-26T00:49:28.861Z
## QA test manifest — AST-811

**Publish:** `origin/sub/AST-810/AST-811-per-parent-merge-ticket-timestamp-resolution` @ `bf9e88d` (`merge-tests(AST-811): origin/tests 79120c6`)

**Bible shasum:** `docs/test-bible/dev/record_landed_parent.md` → `61d98aa2f69d77a8a929eea74db75fffdeaaaa6a`

### Manifest (test-child)

1. **`TestRebuildMergeTicketLogTimestampResolution::test_resolve_recorded_at_prefers_prep_uat_grep`** — prep-uat grep wins; `_first_ftr_land_on_dev` not invoked.
2. **`::test_resolve_recorded_at_ftr_land_grep_before_walk`** — empty ritual greps; ftr `merge origin/{ftr}` grep returns ISO timestamp.
3. **`::test_collect_entries_distinct_recorded_at_when_walk_fallback`** — all greps empty; walk fallback yields distinct `recorded_at` per parent.
4. **`::test_main_rebuild_summary_no_dev_head_timestamp_collapse`** — rebuild summary: two parents, unequal timestamps (no dev-HEAD collapse).

**Regression:** AST-805 landing-parent union tests in same module remain green.

```bash
.venv/bin/python -m pytest \
  tests/component/scripts/test_rebuild_merge_ticket_log.py \
  -q
```

**Pass criterion:** pytest green on items 1–4 + AST-805 regression — not zero-arg harness / branch-lock gate.

— Betty

#### hedy — 2026-06-26T00:45:01.458Z
Plan: `https://github.com/susansomerset/astral/blob/sub/AST-810/AST-811-per-parent-merge-ticket-timestamp-resolution/docs/features/foundation/ast-811-per-parent-merge-ticket-timestamp-resolution.md`

**Scope:** Single-Component — `scripts/rebuild_merge_ticket_log.py` timestamp resolution only; utils/core/tooltip read paths unchanged.

**Conf:** high — broken fallback confirmed (`git log dev ftr -1` → identical dev HEAD for all merged ftrs); ftr land greps + merge-base walk validated on live `origin/dev`.

**Risk:** Medium — git walk edge cases could still mis-order; grep chain preserved for ritual commits; Betty manifest covers mocked resolution in Stage 2.

---

# Per-parent merge ticket timestamp resolution

**Linear:** [AST-811 — Per-parent merge ticket timestamp resolution](https://linear.app/astralcareermatch/issue/AST-811/per-parent-merge-ticket-timestamp-resolution-timestamps-for-issues-merged-do-not-differentiate-across-branch-merges)

**Parent (coordination only):** [AST-810 — timestamps for issues merged do not differentiate across branch merges](https://linear.app/astralcareermatch/issue/AST-810/timestamps-for-issues-merged-do-not-differentiate-across-branch-merges)

**Publish ref:** `origin/sub/AST-810/AST-811-per-parent-merge-ticket-timestamp-resolution` (origin only)

## Summary

After AST-800 full rebuild at prep-uat, multiple parent epics appear in the admin deploy env tooltip but often share **identical** `recorded_at` values. Root cause: when the AST-800 grep chain (`prep-uat` → `merge-parent` → `finish-up`) misses for a parent, `_resolve_recorded_at` falls back to `git log <dev-ref> -1 --format=%cI <ftr-ref>`, which returns **origin/dev HEAD** for every fully merged ftr — not per-parent land time.

This child fixes timestamp resolution in `scripts/rebuild_merge_ticket_log.py` so each parent gets the commit time of the merge that brought **that** parent's `ftr/*` onto `origin/dev`. Utils read path (`merge_ticket_log`, `deploy_status`) and tooltip UX stay unchanged.

⚠️ **Decision:** Keep the AST-800 grep order for explicit ritual commits (`prep-uat(PARENT):` → `merge-parent(PARENT):` → `finish-up(PARENT):`). Insert **ftr land greps** before the git-walk fallback (not before prep-uat) so a parent with its own prep-uat record keeps that timestamp; parents without grep hits get ftr-specific resolution instead of dev HEAD.

⚠️ **Decision:** Replace the broken `git log dev ftr -1` fallback with (a) ftr merge-subject greps, then (b) a walk of `merge-base(dev,ftr)..dev` for the **first** commit where `ftr` tip is an ancestor, preferring the earliest **merge** commit on that path. This matches Susan's brief ("create date of the SHA merged into dev from the ftr branch") and yields distinct timestamps for UAT parents on current `origin/dev` (verified locally: AST-716, AST-752, AST-753, AST-754 resolve differently).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `scripts/rebuild_merge_ticket_log.py` | Fix `_resolve_recorded_at`; add `_grep_land_timestamp`, `_first_ftr_land_on_dev` helpers | scripts |

**Tests:** Betty owns **`tests/`** — engineer does **not** edit test files. Stage 2 documents component scenarios for Betty's manifest.

**Verify only (no change expected):**

| File | Role |
|------|------|
| `src/utils/merge_ticket_log.py` | Read/write API unchanged |
| `src/core/deploy_status.py` | Log-only read unchanged |
| `src/ui/frontend/src/components/AdminDeployFooter.tsx` | AST-691 tooltip unchanged |
| `scripts/git/record-landed-parent.sh` | Still calls rebuild CLI; no flag changes |

**Out of scope:** Eligibility rules (AST-800/805), tooltip UX, runtime Linear filtering, `data/merge_ticket_log.json` backfill on dev (corrects on next prep-uat rebuild or manual rebuild run).

---

## Stage 1: Per-parent timestamp resolution in rebuild CLI

**Done when:** `_resolve_recorded_at(parent_id, dev_ref, ftr_ref)` returns distinct ISO timestamps for parents whose ftr branches landed on dev at different times (local smoke against `origin/dev` for at least AST-716 vs AST-752); no caller uses `git log dev ftr -1` as fallback; `python3 -m py_compile scripts/rebuild_merge_ticket_log.py` passes.

1. In `scripts/rebuild_merge_ticket_log.py`, add helper `_grep_land_timestamp(dev_ref: str, grep: str) -> str`:
   - Return `_git_log_timestamp(dev_ref, f"--grep={grep}")` (existing subprocess wrapper).
   - Return `""` when stdout is empty.

2. Add helper `_ftr_tip_sha(ftr_ref: str) -> str`:
   - Run `git rev-parse origin/{ftr_ref}` via `_run_git`.
   - On non-zero exit, return `""`.

3. Add helper `_first_ftr_land_on_dev(dev_ref: str, ftr_ref: str) -> str`:
   - `ftr_tip = _ftr_tip_sha(ftr_ref)`; if empty, return `""`.
   - `base = git merge-base dev_ref origin/ftr_ref`; if command fails, return `""`.
   - Run `git rev-list --reverse {base}..{dev_ref}`; for each `sha` in order (oldest → newest on dev since merge-base):
     1. Skip unless `git merge-base --is-ancestor ftr_tip sha` succeeds (exit 0).
     2. Read `git cat-file -p sha` and count lines starting with `parent ` — if count ≥ 2, this is a merge commit: return `git log -1 --format=%cI sha` and **stop** (first merge that included ftr tip).
   - If the loop finishes with no merge commit but at least one ancestor hit, return `git log -1 --format=%cI` of the **first** ancestor hit (non-merge inclusion commit).
   - If no hit, return `""`.

4. Rewrite `_resolve_recorded_at(parent_id: str, dev_ref: str, ftr_ref: str) -> str` to try, in order, returning the first non-empty timestamp:

   | Step | Grep / source |
   |------|----------------|
   | 1 | `prep-uat({parent_id}):` |
   | 2 | `merge-parent({parent_id}):` |
   | 3 | `finish-up({parent_id}):` |
   | 4 | `merge origin/{ftr_ref}` |
   | 5 | `Merge remote-tracking branch 'origin/{ftr_ref}'` |
   | 6 | `_first_ftr_land_on_dev(dev_ref, ftr_ref)` |

   **Delete** the final `return _git_log_timestamp(dev_ref, ftr_ref)` line (the dev-HEAD bug).

5. Do **not** change `_collect_entries`, `_resolve_ftr_ref`, `_ftr_refs_for_parent`, `_ftr_on_dev`, CLI args, or `main()` beyond what the helpers require.

6. Local smoke (manual, on epic worktree with fetched `origin/dev`):

   ```bash
   python3 - <<'PY'
   import importlib.util
   from pathlib import Path
   spec = importlib.util.spec_from_file_location("m", Path("scripts/rebuild_merge_ticket_log.py"))
   m = importlib.util.module_from_spec(spec)
   spec.loader.exec_module(m)
   pairs = [
       ("AST-716", "ftr/AST-716-find-job-page-logic-confirmation"),
       ("AST-752", "ftr/AST-752-agent-data-caller-content"),
   ]
   ts = {p: m._resolve_recorded_at(p, "origin/dev", f) for p, f in pairs}
   assert ts["AST-716"] and ts["AST-752"] and ts["AST-716"] != ts["AST-752"], ts
   print("ok", ts)
   PY
   ```

7. `python3 -m py_compile scripts/rebuild_merge_ticket_log.py`

**Ritual:** `code(AST-811): per-parent merge ticket timestamp resolution in rebuild CLI`

---

## Stage 2: Betty test manifest (engineer documents only — no test commits)

**Done when:** Linear comment or plan note lists manifest rows for Betty; engineer does **not** commit under `tests/`.

Betty adds to **`tests/component/scripts/test_rebuild_merge_ticket_log.py`** (same importlib load pattern as AST-805):

| # | Scenario | Mock target | Assertion |
|---|----------|-------------|-----------|
| 1 | Grep chain returns prep-uat hit | `_grep_land_timestamp` or `_resolve_recorded_at` partial mock | First parent gets prep-uat timestamp; `_first_ftr_land_on_dev` not called |
| 2 | Grep chain empty; ftr land grep hits | Mock `_grep_land_timestamp` to return `""` for steps 1–3, then `"2026-06-18T02:08:22Z"` for step 4 | `_resolve_recorded_at("AST-716", "origin/dev", "ftr/AST-716-…")` returns that ISO string |
| 3 | All greps empty; walk fallback | Mock `_grep_land_timestamp` → `""`; mock `_first_ftr_land_on_dev` → distinct values per parent | `_collect_entries` with two mocked parents yields two entries with **different** `recorded_at` |
| 4 | Regression: no dev-HEAD collapse | Mock greps empty; mock `_first_ftr_land_on_dev` to return `"2026-06-18T02:08:22Z"` and `"2026-06-23T20:17:09Z"` | Two-entry rebuild summary has unequal timestamps |

Update **`docs/test-bible/dev/record_landed_parent.md`** AST-811 row when Betty runs **qa-child** (engineer does not edit bible).

---

## Self-Assessment

**Scope:** `Single-Component` — one script module (`scripts/rebuild_merge_ticket_log.py`) owns timestamp resolution; no utils/core/UI changes.

**Conf:** `high` — root cause confirmed on live `origin/dev` (broken fallback returns identical dev HEAD); replacement algorithm validated locally for multiple UAT parents.

**Risk:** `Medium` — incorrect git walk could still collapse timestamps or skip parents; mitigated by grep chain preserved for ritual commits, explicit smoke in Stage 1, and Betty manifest for mocked resolution paths.

---

## ASTRAL_CODE_RULES self-review

| Rule | Assessment |
|------|------------|
| §1.3 DRY | New helpers colocated in rebuild script; no duplicate grep subprocess logic beyond thin `_grep_land_timestamp` wrapper. |
| §2.1 Config | No new config keys; `MERGE_TICKET_LOG_CONFIG` / uat state unchanged. |
| §2.4 Batch | N/A — script iterates parent ids, not entity batch locks. |
| §2.6 State machine | N/A — no entity states. |
| §3.3 Imports | Script continues importing external linear + utils merge_ticket_log only; no layer violations. |
| §3.5 Naming | `_first_ftr_land_on_dev`, `_grep_land_timestamp` follow existing `_resolve_*` private script helpers. |

No conflicts requiring plan revision.

---

## Build review stub

**Built:** `origin/sub/AST-810/AST-811-per-parent-merge-ticket-timestamp-resolution` @ `989f94b`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `989f94b` | `_resolve_recorded_at` ftr land greps + merge-intro walk; `_commit_timestamp` for per-sha ISO times |

**Hand-verify:** rebuild smoke — AST-716 / AST-752 / AST-753 resolve to three distinct `recorded_at` values on `origin/dev`.

---

## Radia review (2026-06-26)

**Diff:** `origin/dev...origin/sub/AST-810/AST-811-per-parent-merge-ticket-timestamp-resolution` @ `bf9e88d`  
**Product commit:** `989f94b` (`scripts/rebuild_merge_ticket_log.py`)  
**Tests:** `79120c6` (Betty manifest on `origin/tests`; merged via `merge-tests`)

### What's solid

| Area | Notes |
|------|-------|
| Grep chain | `_resolve_recorded_at` preserves prep-uat → merge-parent → finish-up order; adds ftr land greps before walk; **removed** dev-HEAD `git log dev ftr -1` fallback. |
| Walk fallback | `_first_ftr_land_on_dev` walks `merge-base..dev` oldest-first; `_commit_timestamp` isolates per-sha ISO lookup; merge commits require ftr tip **not** on first parent before stopping (avoids false land on unrelated merges). |
| Plan scope | Single script change; `_collect_entries`, CLI, utils read path untouched per plan. |
| §1.3 DRY | `_grep_land_timestamp` thin wrapper over `_git_log_timestamp`; helpers colocated with existing `_resolve_*` pattern. |
| §3.3 | Script imports `src.external.linear` + `src.utils` only — no layer violations. |
| Self-Assessment | Scope `Single-Component` matches product diff; Conf `high` supported by live smoke. |
| Smoke (origin/dev) | AST-716 `2026-06-18T02:08:22Z`, AST-752 `2026-06-23T20:17:09Z`, AST-753 `2026-06-23T19:35:12Z` — three distinct values. |
| Tests + bible | `TestRebuildMergeTicketLogTimestampResolution` (4 cases) + AST-805 regression; 8/8 pytest green; bible AST-811 rows in `record_landed_parent.md`. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| — | — | None. |

### Recommended actions

| Action | Owner |
|--------|-------|
| None blocking | — |

**Counts:** 0 fix-now · 0 discuss · 0 advisory

**Outcome:** Clean — Hedy may proceed with `resolve-child` (§9a dry-run).

**Advisory (non-blocking):** `_first_ftr_land_on_dev` merge-stop rule is stricter than the plan prose (skips merge commits where ftr tip is already ancestor of the first parent). Live smoke and mocked tests pass; behavior is an improvement, not a regression.

---

## Resolution (2026-06-26)

**Publish ref:** `origin/sub/AST-810/AST-811-per-parent-merge-ticket-timestamp-resolution` @ `0e58a27` (Radia `docs(AST-811): Radia review — clean`)

Radia review clean — 0 fix-now, 0 discuss, 0 advisory. No product code changes beyond `code(AST-811)` @ `989f94b`. §9a dry-run clean vs `origin/dev` and `origin/ftr/ast-810-timestamps-for-issues-merged-do-not-differentiate-across-branch-merges`.

**Outcome:** Per-parent `recorded_at` resolution in `rebuild_merge_ticket_log.py` ready for sibling merge and prep-uat rebuild on dev.
