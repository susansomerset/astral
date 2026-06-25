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
