# UAT: AST-788 missing from deploy env User Testing tooltip after prep-uat

**Linear:** [AST-806 — UAT: AST-788 missing from deploy env User Testing tooltip after prep-uat](https://linear.app/astralcareermatch/issue/AST-806/uat-ast-788-missing-from-deploy-env-user-testing-tooltip-after-prep)

**Parent (coordination only):** [AST-788 — BUILD_ARTIFACTS substates do not graduate](https://linear.app/astralcareermatch/issue/AST-788/build-artifacts-substates-do-not-graduate)

**Publish ref:** `origin/sub/AST-788/AST-806-uat-merge-ticket-log-missing-after-prep-uat` (origin only)

## Summary

After **AST-788** prep-uat landed **ftr** on **origin/dev**, Susan restarted from **origin/dev** and hovered the deploy env label. **AST-788** was absent from the User Testing tooltip because **`record-landed-parent.sh`** failed during rebuild: bare **`python3`** cannot import **`python-dotenv`** (pulled in via `src/utils/config.py`), so **`data/merge_ticket_log.json`** was never updated on **dev**.

**Root cause (confirmed):** `scripts/git/record-landed-parent.sh` invokes `python3 "$REBUILD"` with no venv resolution. On Susan's machine (and CI-less prep-uat shell), system Python lacks project deps → `ModuleNotFoundError: dotenv` → rebuild aborts → log commit/push never runs.

**Secondary gap (same class as AST-805):** Even with a working interpreter, `rebuild_merge_ticket_log.py` only queries Linear **User Testing** parents, but prep-uat calls rebuild **before** Chuckles moves the parent to **User Testing**. The landing parent must be unioned explicitly at rebuild time.

⚠️ **Decision:** Resolve Python in `record-landed-parent.sh` as **`${ASTRAL_PYTHON:-$REPO_ROOT/.venv/bin/python}`**; exit **BLOCKED** if that binary is missing. Matches `scripts/testing/run_component_tests.sh` — no new env var required beyond existing **`ASTRAL_PYTHON`** override.

⚠️ **Decision:** Add **`--landing-parent AST-NNN`** to `rebuild_merge_ticket_log.py` and pass **`"$PARENT_ID"`** from `record-landed-parent.sh` (AST-805 pattern). Landing id still requires ftr-on-dev and resolvable `recorded_at`; only bypasses Linear **User Testing** filter for the parent being landed.

⚠️ **Decision:** Stage 3 commits a **one-time log repair** on this branch: run the fixed rebuild against **origin/dev** and commit **`data/merge_ticket_log.json`** including **AST-788** (and other User Testing parents whose ftr is on dev). Chuckles lands that file on **dev** with the script fix — Susan should not run manual log surgery.

**Out of scope:** **BUILD_ARTIFACTS CHAIN** product logic (**AST-803**); React tooltip UX; runtime deploy-status read path; reordering prep-uat Linear status before land.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `scripts/git/record-landed-parent.sh` | Venv python resolution; pass `--landing-parent "$PARENT_ID"` | scripts |
| `scripts/rebuild_merge_ticket_log.py` | Add `--landing-parent`; union landing id with Linear UAT set | scripts |
| `data/merge_ticket_log.json` | One-time rebuild including **AST-788** (Stage 3) | data |

**Tests:** Betty owns **`tests/`** — engineer does **not** edit test files. Stage 2 documents Betty manifest additions.

**Verify only (no change expected):**

| File | Role |
|------|------|
| `src/external/linear.py` | `fetch_user_testing_parent_ids` unchanged |
| `src/core/deploy_status.py` | Log-only read unchanged |
| `scripts/git/prep-uat-land.sh` | Still calls `record-landed-parent.sh` after push |

---

## Stage 1: Venv python in record-landed-parent

**Done when:** `record-landed-parent.sh` uses repo venv (or `ASTRAL_PYTHON`) instead of bare `python3`; missing interpreter exits **BLOCKED**; shell still wires rebuild (not append).

1. In `scripts/git/record-landed-parent.sh`, after `REPO_ROOT=…` and before the rebuild existence check, add:

   ```bash
   if [[ -n "${ASTRAL_PYTHON:-}" ]]; then
     PYTHON="$ASTRAL_PYTHON"
   else
     PYTHON="${REPO_ROOT}/.venv/bin/python"
   fi
   if [ ! -x "$PYTHON" ]; then
     echo "BLOCKED: repo venv python missing at ${PYTHON} — run setup_dev.sh or set ASTRAL_PYTHON (AST-806)" >&2
     exit 1
   fi
   ```

2. Replace the rebuild invocation:

   ```bash
   python3 "$REBUILD"
   ```

   with:

   ```bash
   "$PYTHON" "$REBUILD"
   ```

   (Stage 2 adds `--landing-parent`; do not add the flag in this stage unless combining stages in one commit is required for compile — prefer separate commits per stage ritual.)

3. Manual verify on epic worktree:

   ```bash
   git fetch origin
   /home/susan/astral/.venv/bin/python scripts/rebuild_merge_ticket_log.py --dev-ref origin/dev
   ```

   Must exit 0 with JSON stdout (no `ModuleNotFoundError`).

**Ritual:** `code(AST-806): venv python for prep-uat merge ticket log rebuild`

---

## Stage 2: Landing-parent bypass in rebuild CLI

**Done when:** `rebuild_merge_ticket_log.py --landing-parent AST-788` includes **AST-788** when it is **not** in the mocked Linear UAT set but its ftr ref is an ancestor of `--dev-ref`; `record-landed-parent.sh` passes `--landing-parent "$PARENT_ID"`; `python3 -m py_compile scripts/rebuild_merge_ticket_log.py` passes.

1. In `scripts/rebuild_merge_ticket_log.py`, add argparse option:

   ```python
   parser.add_argument(
       "--landing-parent",
       default=None,
       metavar="AST-NNN",
       help="Parent id being prep-uat landed; included even if not yet User Testing in Linear",
   )
   ```

2. Change `_collect_entries` signature to accept optional `landing_parent: str | None = None`.

3. At the start of `_collect_entries`, build the parent id set:

   ```python
   parent_ids: set[str] = set(fetch_user_testing_parent_ids(uat_state_name=uat_state_name))
   if landing_parent:
       normalized = landing_parent.strip().upper()
       if normalized:
           parent_ids.add(normalized)
   ```

   Iterate `for parent_id in sorted(parent_ids):` — keep existing ftr-on-dev gate, `recorded_at` resolution, and sort-by-`recorded_at` behavior unchanged.

4. In `main()`, pass `args.landing_parent` into `_collect_entries`.

5. Extend the JSON summary printed to stdout to include `"landing_parent": "<id or null>"`.

6. In `scripts/git/record-landed-parent.sh`, change rebuild invocation to:

   ```bash
   "$PYTHON" "$REBUILD" --landing-parent "$PARENT_ID"
   ```

7. Manual verify:

   ```bash
   /home/susan/astral/.venv/bin/python scripts/rebuild_merge_ticket_log.py \
     --dev-ref origin/dev --landing-parent AST-788
   ```

   Confirm stdout JSON `"parents"` contains **AST-788**.

8. **Betty manifest (document only — do not edit tests):** Extend `docs/test-bible/dev/record_landed_parent.md` when Betty picks up **AST-806**:

   - Shell resolves venv python (`ASTRAL_PYTHON` or `.venv/bin/python`); static text guard on `record-landed-parent.sh`.
   - Rebuild CLI `--landing-parent` unions id not returned by mocked empty Linear UAT query when ftr is ancestor of dev-ref.
   - `record-landed-parent.sh` passes `--landing-parent "$PARENT_ID"`.

**Ritual:** `code(AST-806): landing-parent bypass and record-landed-parent wiring`

---

## Stage 3: One-time log repair for AST-788 on dev

**Done when:** `data/merge_ticket_log.json` on this branch includes **AST-788** with a valid `recorded_at`; file is committed on **`origin/sub/AST-788/AST-806-uat-merge-ticket-log-missing-after-prep-uat`**. After Chuckles merges to **dev**, Susan's tooltip lists **AST-788** without manual steps.

1. On epic worktree (after Stages 1–2):

   ```bash
   git fetch origin
   /home/susan/astral/.venv/bin/python scripts/rebuild_merge_ticket_log.py \
     --dev-ref origin/dev --landing-parent AST-788
   ```

2. Confirm `data/merge_ticket_log.json` contains a row `"ticket_id": "AST-788"` with non-empty `recorded_at`.

3. `git add data/merge_ticket_log.json` only.

4. Do **not** run `record-landed-parent.sh` push from the epic worktree — this stage commits the repaired log on the **sub** branch for normal merge/prep-uat land to **dev**.

**Ritual:** `code(AST-806): rebuild merge ticket log — include AST-788`

---

## Self-Assessment

**Scope:** `minor` — Two script files plus one data file; no core, external, or UI product layers.

**Conf:** `high` — Failure reproduced (`python3` vs venv); AST-805 landing-parent pattern applies; manual rebuild with venv already returns **AST-788** in `parents`.

**Risk:** `low` — Prep-uat shell path only; venv guard prevents silent bare-python failure; ftr-on-dev gate limits bogus landing ids.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | OK? |
|------|-----|
| §1.3 DRY | Reuses AST-805 landing-parent union; venv pattern matches test harness scripts |
| §3.5 naming | `--landing-parent`, `landing_parent` param |
| Layer imports | Scripts may import external/utils |
| Out of scope | No **AST-803** consult/dispatcher changes |

No conflicts flagged.
