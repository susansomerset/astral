<!-- linear-archive: AST-800 archived 2026-07-22 -->

## Linear archive (AST-800)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-800/uat-tooltip-shows-only-ast-791-not-all-user-testing-parents-on-dev  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-791 — List of UAT issues in environment tooltip is not updating  
**Blocked by / blocks / related:** parent: AST-791

### Description

## What failed

On staging after AST-798 fix-uat, hovering the admin deploy footer environment label tooltip shows **only AST-791**, not every parent epic that has been landed on `origin/dev` and is in Linear **User Testing**.

## Expected

The tooltip lists **all** parent issue ids that (a) are in Linear **User Testing** at prep-uat time and (b) have their `ftr/*` branch merged into `origin/dev`, each with the timestamp of the latest dev commit for that feature. Parents whose `ftr` has **not** been merged to `origin/dev` are omitted.

## Repro

1. Log in as admin on staging (deploy from current `origin/dev`).
2. Hover the deploy footer environment label for ≥0.5s.
3. **Observed:** tooltip shows only **AST-791** (one line).
4. **Expected:** every User Testing parent whose feature is on `origin/dev` (e.g. other active UAT epics), not just this epic.

## Parent AC (quoted inline)

> 1. After deploy from current `origin/dev`, hovering the admin environment label on staging shows **no** parent ids that are **Done** in Linear (including **AST-741** and other previously logged finished epics).
> 2. Every parent id shown in the tooltip is in Linear state **User Testing** at the time of the deploy-status request.
> 3. A parent prep-uat'd to staging while in **User Testing** appears in the tooltip with an updated timestamp; re-prep-uat of the same parent updates timestamp only (no duplicate lines).

## Boundaries

* This bug does **not** change: admin nav outside deploy footer, non-admin routes, or AST-798 cursor/CSS fixes.
* **prep-uat** rebuilds the log at land time per Susan's 2026-06-25 comment (pull log from dev → Linear User Testing parents → verify ftr merged to dev → rewrite log → commit to dev); runtime deploy-status may read the log without per-request Linear filtering if prep-uat maintains the list correctly.

### Comments

#### radia — 2026-06-25T02:00:03.449Z
### Radia review — AST-800

**Diff:** `origin/dev...origin/sub/AST-791/ast-800-uat-tooltip-shows-only-ast-791-not-all-user-testing-parents-on-dev` @ `680a822`
**Doc:** `docs/features/foundation/ast-800-uat-tooltip-shows-only-ast-791-not-all-user-testing-parents-on-dev.md` (§ Radia review)

**What's solid**
- `fetch_user_testing_parent_ids()` (paginated, top-level only); `rebuild_merge_ticket_log.py` with ftr-on-dev gate + timestamp heuristics; `record-landed-parent.sh` rebuild wiring; core log-only `merge_tickets` (AST-792 runtime filter removed per Susan prep-uat semantics).
- §3.3 layers correct; no frontend changes.
- Betty manifest: Linear query, deploy_status read path, record-landed-parent shell tests.

**advisory:** Tooltip refreshes on prep-uat rebuild, not every poll (documented AC 4 tradeoff). Rebuild git logic untested beyond shell stub. `ls-remote` per parent per plan.

**fix-now:** none
**discuss:** none

**Post-merge:** prep-uat rebuild on dev needed so log lists all UAT parents on integration line.

#### betty — 2026-06-25T01:58:12.726Z
## QA test manifest (AST-800)

**Publish:** `origin/sub/AST-791/ast-800-uat-tooltip-shows-only-ast-791-not-all-user-testing-parents-on-dev` @ `3bf7ec1` (`merge-tests(AST-800): origin/tests 74d0bf2`)

**Broken / revised (AST-792 → AST-800):** `tests/component/core/test_deploy_status.py` — removed runtime Linear filter / fail-closed tests; log-only read path. `tests/component/scripts/test_record_landed_parent.py` — rebuild wiring replaces append-only.

### Manifest (test-child)

1. **Linear UAT parent query** — `tests/component/external/test_linear.py::TestFetchUserTestingParentIds` (2 tests): sorted top-level parents + pagination.

2. **Log-only deploy payload** — `tests/component/core/test_deploy_status.py::TestCoreGetDeployStatusPayload` (2 tests): `merge_tickets` from log most-recent-first; empty log → `[]`.

3. **Prep-uat rebuild wiring** — `tests/component/scripts/test_record_landed_parent.py`:
   - `TestRecordLandedParentShell::test_record_landed_parent_wires_rebuild_not_append`
   - `TestRecordLandedParent::test_record_landed_parent_rebuilds_and_commits`
   - `TestRecordLandedParent::test_record_landed_parent_missing_rebuild_script_blocks`

```bash
.venv/bin/python -m pytest \
  tests/component/external/test_linear.py \
  tests/component/core/test_deploy_status.py \
  tests/component/scripts/test_record_landed_parent.py \
  -q
```

**Pass criterion:** pytest green on manifest (16 tests) — not zero-arg harness / branch-lock gate.

**Bible shasums (`origin/sub/...` @ `3bf7ec1`):**
- `docs/test-bible/core/deploy_status.md`: `8acb5763ae2729914d5e13f4799707d803dcb1f1ada223256beaf1a38b5ab358`
- `docs/test-bible/dev/record_landed_parent.md`: `90246762a116bd80f5dbfb6b1ab596c85bf2eb543a015bb4ee936b24a638c2c2`
- `docs/test-bible/external/linear.md`: `eb3ab028c2d0442806176a17bda01f688ed7850867c15c8e93c2777527f18f5e`
- `docs/test-bible/utils/merge_ticket_log.md`: `e25ea5819c69de46d60a271f58dd3589b14c952f0646a740316880fc41f789d9`

— Betty

#### chuckles — 2026-06-25T01:53:15.757Z
Plan doc: https://github.com/susansomerset/astral/blob/sub/AST-791/ast-800-uat-tooltip-shows-only-ast-791-not-all-user-testing-parents-on-dev/docs/features/foundation/ast-800-uat-tooltip-shows-only-ast-791-not-all-user-testing-parents-on-dev.md

**Approach:** Replace prep-uat append-only `merge_ticket_log.json` with a full **rebuild** at land time — query Linear for all top-level **User Testing** parents, verify each has an `origin/ftr/*` ancestor on `origin/dev`, stamp `recorded_at` from latest prep-uat/merge-parent/finish-up commit on dev, rewrite log. Runtime `deploy_status` reads log only (drops AST-792 per-poll Linear filter per Susan 2026-06-25 boundary).

**Self-assessment**
- **Scope:** Single-Component — Linear helper, rebuild CLI + git subprocesses, record-landed-parent wiring, deploy_status simplification; no frontend.
- **Conf:** Medium — ftr discovery and timestamp heuristics need careful subprocess wiring; prep-uat rebuild supersedes AST-792 runtime filter (documented tradeoff on AC 4).
- **Risk:** Medium — wrong ftr/timestamp matching could omit valid UAT parents; mitigated by explicit git gates and Betty manifest tests.

---

# UAT: tooltip shows only AST-791 not all User Testing parents on dev

**Linear:** [AST-800 — UAT: tooltip shows only AST-791 not all User Testing parents on dev](https://linear.app/astralcareermatch/issue/AST-800/uat-tooltip-shows-only-ast-791-not-all-user-testing-parents-on-dev)

**Parent:** [AST-791 — List of UAT issues in environment tooltip is not updating](https://linear.app/astralcareermatch/issue/AST-791/list-of-uat-issues-in-environment-tooltip-is-not-updating) (AC reference only)

**Publish ref:** `origin/sub/AST-791/ast-800-uat-tooltip-shows-only-ast-791-not-all-user-testing-parents-on-dev` (origin only)

## Summary

After AST-798, staging tooltip UX works but lists **only AST-791** because `record-landed-parent.sh` **appends** a single parent id per prep-uat land. Susan’s corrected semantics (2026-06-25): the tooltip must list **every** parent epic that is in Linear **User Testing** **and** whose `ftr/*` is merged into `origin/dev`, each with a timestamp from the latest relevant dev commit for that feature — not a deploy-scoped append-only history filtered at runtime.

This bug replaces per-land **append** with a **full log rebuild** at prep-uat time (Linear query + git ftr-on-dev verification + dev commit timestamps), and simplifies runtime `GET /api/deploy_status` to read the rebuilt log (most recent first) without per-request Linear state filtering.

⚠️ **Decision:** **Prep-uat land** calls `rebuild_merge_ticket_log.py` (replacing single-id `append_merge_ticket_log` in `record-landed-parent.sh`). Rebuild is authoritative; runtime **drops** AST-792 per-poll Linear filter. Parent AC 4 (parent leaves **User Testing** without redeploy) is satisfied on the **next** prep-uat rebuild or manual rebuild — not on every 30s poll — per Susan’s prep-uat–maintained list comment.

⚠️ **Decision:** **Ftr-on-dev gate:** include parent **AST-NNN** only when **some** `origin/ftr/*` ref whose name contains that id (case-insensitive) is an ancestor of `origin/dev` (`git merge-base --is-ancestor`). Parents in **User Testing** on Linear but not yet on dev are omitted (not a global Linear inbox).

⚠️ **Decision:** **`recorded_at`** for each included parent = ISO timestamp of the latest `prep-uat(AST-NNN):` commit on `origin/dev` (`git log --grep`). If none, fall back to latest commit on dev whose subject matches `merge-parent(AST-NNN):` or `finish-up(AST-NNN):`. If still none, use `git log -1 --format=%cI` on the merge commit that brought that parent’s ftr onto dev (first parent merge commit found via `git log origin/dev --grep=ftr/` — see Stage 1 step 6 fallback).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/external/linear.py` | Add `fetch_user_testing_parent_ids()` — top-level issues in **User Testing** | external |
| `src/utils/merge_ticket_log.py` | Add `rebuild_merge_ticket_log(entries)` wrapper (alias `rewrite_merge_ticket_log` or thin public name) | utils |
| `scripts/rebuild_merge_ticket_log.py` | New CLI: Linear + git → rewrite log | scripts |
| `scripts/git/record-landed-parent.sh` | Call rebuild script instead of append; commit message `prep-uat(<id>): rebuild merge ticket log` | scripts |
| `src/core/deploy_status.py` | Remove runtime Linear filter; `merge_tickets` = log entries most-recent-first | core |
| `env.example` | Note rebuild-at-prep-uat semantics (optional comment tweak) | docs |
| `tests/component/external/test_linear.py` | Tests for `fetch_user_testing_parent_ids` (Betty manifest) | test |
| `tests/component/core/test_deploy_status.py` | Update/remove Linear-filter tests; log-read-only payload tests (Betty manifest) | test |
| `tests/component/scripts/test_record_landed_parent.py` | Expect rebuild wiring, not append-only (Betty manifest) | test |

**Verify only (no change expected):**

| File | Role |
|------|------|
| `src/ui/frontend/src/components/AdminDeployFooter.tsx` | AST-691/798 UX unchanged |
| `scripts/git/prep-uat-land.sh` | Still calls `record-landed-parent.sh` after push |
| `scripts/prune_merge_ticket_log.py` | Maintenance tool; unchanged |

**Out of scope:** AdminDeployFooter/CSS; Chuckles **team-chuckles** prep-uat skill doc-only updates; child ticket ids in tooltip; ticket titles; listing parents not on `origin/dev`.

---

## Stage 1: Linear parent discovery + rebuild CLI

**Done when:** `fetch_user_testing_parent_ids()` returns sorted `AST-NNN` ids for top-level **User Testing** issues; `rebuild_merge_ticket_log.py` rewrites `data/merge_ticket_log.json` with all qualifying parents on `origin/dev`; `python3 -m py_compile` on touched modules passes.

1. In `src/external/linear.py`, add to `__all__`: `fetch_user_testing_parent_ids`.

2. Implement `fetch_user_testing_parent_ids() -> list[str]`:
   - GraphQL (paginate if `pageInfo.hasNextPage`):

     ```graphql
     query UserTestingParents($teamKey: String!, $state: String!, $after: String) {
       issues(
         filter: {
           team: { key: { eq: $teamKey } }
           state: { name: { eq: $state } }
           parent: { null: true }
         }
         first: 100
         after: $after
       ) {
         pageInfo { hasNextPage endCursor }
         nodes { identifier }
       }
     }
     ```

   - Variables: `teamKey: "AST"`, `state: MERGE_TICKET_LOG_CONFIG["uat_state_name"]` passed from caller (script imports config) — **external must not import config**; pass `uat_state_name: str` parameter default `"User Testing"`.
   - Return sorted unique identifiers (`AST-NNN`).

3. Create `scripts/rebuild_merge_ticket_log.py`:
   - Docstring: rebuild merge ticket log for all User Testing parents whose ftr is on dev (AST-800).
   - Args: optional `--dev-ref` default `origin/dev` (for tests/local).
   - Steps:
     1. `parent_ids = fetch_user_testing_parent_ids()` (import from external).
     2. For each `parent_id`, resolve ftr ref: run `git ls-remote origin 'refs/heads/ftr/*'` (subprocess), keep refs whose path contains `parent_id` case-insensitive (e.g. `ftr/ast-791-...`).
     3. If no matching ftr ref → **skip** parent (not on dev track).
     4. If multiple ftr refs match same parent, use the one that **`git merge-base --is-ancestor <ftr> <dev-ref>`** succeeds; if none ancestor → skip.
     5. Resolve `recorded_at` via subprocess `git log <dev-ref> -1 --format=%cI --grep="prep-uat(<parent_id>):"` (grep fixed string with id). If empty, try `--grep="merge-parent(<parent_id>):"` then `--grep="finish-up(<parent_id>):"`. If still empty, use `git log <dev-ref> -1 --format=%cI <ftr-ref>` (tip of merged ftr).
     6. Collect `{ticket_id, recorded_at}` entries; sort by `recorded_at` ascending (file order oldest-first, same as existing log convention).
     7. Call `rewrite_merge_ticket_log(entries)` from `merge_ticket_log.py`.
   - Exit 0; print JSON summary `{"count": N, "parents": [...]}` to stdout.

4. In `src/utils/merge_ticket_log.py`, add public alias if helpful:

   ```python
   def rebuild_merge_ticket_log(entries: list[dict]) -> None:
       rewrite_merge_ticket_log(entries)
   ```

5. `python3 -m py_compile src/external/linear.py src/utils/merge_ticket_log.py scripts/rebuild_merge_ticket_log.py`

**Ritual:** `code(AST-800): rebuild merge ticket log from Linear UAT parents on dev`

---

## Stage 2: Wire prep-uat record + simplify deploy-status read path

**Done when:** `record-landed-parent.sh` invokes rebuild (not append); `get_deploy_status_payload()` returns `merge_tickets` from log only (no Linear API on poll); `python3 -m py_compile src/core/deploy_status.py` passes.

1. In `scripts/git/record-landed-parent.sh`:
   - Replace `append_merge_ticket_log.py` block with:

     ```bash
     REBUILD="${REPO_ROOT}/scripts/rebuild_merge_ticket_log.py"
     if [ ! -f "$REBUILD" ]; then
       echo "BLOCKED: rebuild script missing at ${REBUILD} — AST-800 must be on dev before record (AST-683)" >&2
       exit 1
     fi
     python3 "$REBUILD"
     git -C "$MAIN" add data/merge_ticket_log.json
     if git -C "$MAIN" diff --cached --quiet; then
       echo "BLOCKED: merge ticket log unchanged after rebuild for ${PARENT_ID}" >&2
       exit 1
     fi
     git -C "$MAIN" commit -m "prep-uat(${PARENT_ID}): rebuild merge ticket log"
     git -C "$MAIN" push origin dev
     ```

   - Remove append-only path. Keep `PARENT_ID` arg for commit message (landed parent trigger).

2. In `src/core/deploy_status.py`:
   - Remove imports of `fetch_parent_issue_states`, `LinearApiError`, `MERGE_TICKET_LOG_CONFIG`, `filter_merge_tickets_by_state`.
   - Replace body with:

     ```python
     payload = utils_ds.get_deploy_status_payload()
     entries = read_merge_ticket_log()
     payload["merge_tickets"] = utils_ds.merge_tickets_recent_first(entries)
     return payload
     ```

   - Always include `merge_tickets` key (empty list when log empty).

3. Do **not** change `AdminDeployFooter.tsx` or `App.css`.

4. `python3 -m py_compile src/core/deploy_status.py`

**Ritual:** `code(AST-800): prep-uat rebuild wiring and log-only deploy status`

---

## Stage 3: Component tests (Betty manifest — engineer runs in test-child)

**Done when:** Betty manifest passes; rebuild + deploy-status read path covered.

1. **`tests/component/external/test_linear.py`** — add `TestFetchUserTestingParentIds` with mocked GraphQL returning two parent identifiers; paginate not required in first test if mock returns `hasNextPage: false`.

2. **`tests/component/core/test_deploy_status.py`** — replace Linear-filter tests with:
   - `test_payload_merge_tickets_from_log_most_recent_first` — monkeypatch `read_merge_ticket_log` only
   - `test_payload_empty_merge_tickets_when_log_empty`
   - Remove tests that mock `fetch_parent_issue_states` / `LinearApiError` for deploy payload (obsolete).

3. **`tests/component/scripts/test_record_landed_parent.py`** — update static guard / integration test to expect `rebuild_merge_ticket_log.py` in `record-landed-parent.sh` (not append-only).

4. Pytest gate:

   ```bash
   .venv/bin/python -m pytest \
     tests/component/external/test_linear.py \
     tests/component/core/test_deploy_status.py \
     tests/component/scripts/test_record_landed_parent.py \
     -q
   ```

**Ritual:** `test(AST-800): rebuild log and deploy-status read coverage`

---

## Execution contract (for the developer agent)

Execute stages in order. Do not change tooltip UX timing/format/cap. Do not list child ids.

Blocking questions use parent **AST-791** with standard 🛑 format.

---

## Self-Assessment

**Scope:** `scope-Single-Component` — Linear query helper, rebuild CLI with git subprocesses, record-landed-parent wiring, deploy_status simplification; no frontend changes.

**Conf:** `Medium` — Git ftr discovery + timestamp heuristics need careful subprocess wiring; Susan’s prep-uat rebuild semantics supersede AST-792 runtime filter (documented decision).

**Risk:** `risk-Medium` — Wrong ftr/timestamp matching could omit valid UAT parents or show wrong order; mitigated by explicit git gates and Betty manifest tests with mocked git/Linear.

---

## Self-review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Rebuild delegates to `rewrite_merge_ticket_log`; deploy_status reuses `merge_tickets_recent_first` |
| §2.1 config | `uat_state_name` remains in `MERGE_TICKET_LOG_CONFIG`; passed into Linear helper as arg |
| §3.3 imports | external → stdlib only; core → utils; scripts may import all layers |
| §3.5 naming | `fetch_user_testing_parent_ids`, `rebuild_merge_ticket_log` |

No conflicts requiring `conf-!!-NONE`.

---

## Revisions

*(none — initial FIX-UAT plan)*

## Parent plan delta (AST-792 superseded in part)

AST-792 runtime Linear filter on every admin poll is **replaced** by prep-uat **full log rebuild** + log-only read. AST-792 remove/prune utilities remain for maintenance; `prune_merge_ticket_log.py` is not wired to prep-uat.

---

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-791/ast-800-uat-tooltip-shows-only-ast-791-not-all-user-testing-parents-on-dev`

**Product commits:** `dab4f20` (Linear UAT parent query, rebuild CLI, log rewrite alias), `b5dfa9b` (record-landed-parent rebuild wiring, log-only deploy status, env.example)

**Note for Betty (Stage 3):** Component tests per plan Stage 3 — manifest at Code Complete.

---

## Radia review (2026-06-25)

**Diff:** `origin/dev...origin/sub/AST-791/ast-800-uat-tooltip-shows-only-ast-791-not-all-user-testing-parents-on-dev` @ `3bf7ec1`  
**Product commits:** `dab4f20`, `b5dfa9b`, `74d0bf2` (tests)

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity (Stages 1–2) | `fetch_user_testing_parent_ids()` with pagination + `parent: { null: true }`; `rebuild_merge_ticket_log.py` (Linear + git ftr-on-dev gate + timestamp heuristics); `record-landed-parent.sh` rebuild wiring; core log-only read path (AST-792 runtime filter removed per Susan decision). |
| Susan semantics | Full prep-uat rebuild replaces append-only log; runtime poll reads rebuilt file — matches parent comment superseding AST-792 per-poll filter. |
| Layer compliance (§3.3) | external takes `uat_state_name` arg (no config import); core → utils only; scripts may import all layers. |
| Ftr-on-dev gate | `ls-remote` + `merge-base --is-ancestor` + skip when no matching ftr — matches plan. |
| Scope boundaries | No frontend/CSS changes; `src/` diff scoped to linear, core deploy_status, merge_ticket_log alias, scripts. |
| Tests | Linear UAT-parent query (+ pagination), deploy_status log-read tests, record-landed-parent rebuild wiring per Betty manifest. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **advisory** | Runtime / prep-uat | Tooltip list refreshes on **prep-uat rebuild**, not every 30s poll — parent AC 4 deferred to next prep-uat (documented plan decision). Staging won't show all UAT parents until next `record-landed-parent` rebuild runs on dev. |
| **advisory** | `scripts/rebuild_merge_ticket_log.py` | Git subprocess / ftr-matching logic has no dedicated component test (plan manifest omits); covered only indirectly via shell stub in `test_record_landed_parent.py`. |
| **advisory** | `_ftr_refs_for_parent` | `git ls-remote` once per parent id (plan-conformant step 3.2); could cache per rebuild if latency becomes an issue. |

### Recommended actions

| Action | Owner |
|--------|-------|
| None required for resolve | — |
| After merge: run prep-uat / manual `rebuild_merge_ticket_log.py` on dev so log reflects all UAT parents on integration line | Chuckles / Susan |
| Optional: add mocked-git component test for rebuild CLI | Betty / engineer |

---

## Resolution (2026-06-25)

**Publish ref:** `origin/sub/AST-791/ast-800-uat-tooltip-shows-only-ast-791-not-all-user-testing-parents-on-dev` @ `680a822` (Radia `docs(AST-800): Radia review — clean`)

Radia review clean — no fix-now or discuss items. No product code changes. Advisory prep-uat refresh semantics and rebuild CLI test coverage deferred per review. §9a dry-run clean vs `origin/dev` and `origin/ftr/ast-791-list-of-uat-issues-in-environment-tooltip-is-not-updating`.

**Outcome:** Prep-uat full merge ticket log rebuild (all User Testing parents with ftr on dev) + log-only deploy-status read ready for Susan UAT; next prep-uat land on dev refreshes tooltip list for all qualifying parents.
