# UAT: AST-801 missing from deploy env User Testing tooltip after prep-uat

**Linear:** [AST-805 — UAT: AST-801 missing from deploy env User Testing tooltip after prep-uat](https://linear.app/astralcareermatch/issue/AST-805/uat-ast-801-missing-from-deploy-env-user-testing-tooltip-after-prep)

**Parent (coordination only):** [AST-801 — Inflow discovery is not recognizing candidate ready for scanning](https://linear.app/astralcareermatch/issue/AST-801/inflow-discovery-is-not-recognizing-candidate-ready-for-scanning)

**Publish ref:** `origin/sub/AST-801/AST-805-uat-merge-ticket-log-missing-after-prep-uat` (origin only)

## Summary

After **AST-801** prep-uat landed **ftr** on **origin/dev**, `data/merge_ticket_log.json` was rebuilt but **AST-801** was omitted from the seven logged parents. Susan's deploy env tooltip (AST-791) therefore did not list **AST-801**, blocking UAT of parent AC #1.

**Root cause (confirmed):** `prep-uat-land.sh` calls `record-landed-parent.sh` → `rebuild_merge_ticket_log.py` **before** Chuckles moves the parent to Linear **User Testing** (`prep-uat` §3). The rebuild CLI only includes ids from `fetch_user_testing_parent_ids()`, so the parent being landed is still **In Progress** in Linear and is skipped even though its **ftr** is already on **origin/dev**. Re-running rebuild today (with **AST-801** in **User Testing**) returns **AST-801** in the list — proving the ftr-on-dev and `recorded_at` paths work; the gap is the Linear state ordering at prep-uat time.

⚠️ **Decision:** Pass the landing parent id from `record-landed-parent.sh` into rebuild via a new **`--landing-parent AST-NNN`** flag. Union that id with the Linear **User Testing** set before ftr-on-dev filtering. Do **not** revert AST-800 full-rebuild semantics; do **not** reorder prep-uat to move Linear before land (Susan must not see **User Testing** before code is on dev).

⚠️ **Decision:** **`--landing-parent`** still requires ftr-on-dev (`git merge-base --is-ancestor`) and a resolvable `recorded_at` (prep-uat grep → merge-parent/finish-up grep → ftr tip fallback per AST-800). It only bypasses the Linear **User Testing** filter for the one parent Chuckles is landing.

**Out of scope:** **inflow_discovery** eligibility logic (**AST-802**); React tooltip UX; runtime deploy-status read path; changing when prep-uat moves Linear status.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `scripts/rebuild_merge_ticket_log.py` | Add `--landing-parent`; union landing id with Linear UAT set | scripts |
| `scripts/git/record-landed-parent.sh` | Pass `"$PARENT_ID"` to rebuild CLI | scripts |

**Tests:** Betty owns **`tests/`** — engineer does **not** edit test files. Stage 2 documents the component scenario for Betty's manifest.

**Verify only (no change expected):**

| File | Role |
|------|------|
| `src/external/linear.py` | `fetch_user_testing_parent_ids` unchanged |
| `src/core/deploy_status.py` | Log-only read unchanged |
| `scripts/git/prep-uat-land.sh` | Still calls `record-landed-parent.sh` after push |

---

## Stage 1: Landing-parent bypass in rebuild CLI

**Done when:** `rebuild_merge_ticket_log.py --landing-parent AST-801` includes **AST-801** in the rebuilt log when **AST-801** is **not** in the mocked/empty Linear UAT set but its ftr ref is an ancestor of `--dev-ref`; `record-landed-parent.sh` passes `--landing-parent "$PARENT_ID"`; `python3 -m py_compile scripts/rebuild_merge_ticket_log.py` passes.

1. In `scripts/rebuild_merge_ticket_log.py`, add argparse option:

   ```python
   parser.add_argument(
       "--landing-parent",
       default=None,
       metavar="AST-NNN",
       help="Parent id being prep-uat landed; included even if not yet User Testing in Linear",
   )
   ```

2. Change `_collect_entries` signature to accept optional `landing_parent: str | None`:

   ```python
   def _collect_entries(
       dev_ref: str,
       uat_state_name: str,
       landing_parent: str | None = None,
   ) -> list[dict]:
   ```

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

5. Extend the JSON summary printed to stdout to include `"landing_parent": "<id or null>"` for prep-uat log forensics.

6. `python3 -m py_compile scripts/rebuild_merge_ticket_log.py`

**Ritual:** `code(AST-805): landing parent bypass in merge ticket log rebuild`

---

## Stage 2: Wire record-landed-parent + manual verification

**Done when:** `record-landed-parent.sh` invokes rebuild with `--landing-parent`; a local dry-run against **origin/dev** with **AST-801** mocked out of Linear UAT (or using a temp repo test Betty adds) still produces a log row for the landing parent when ftr is on dev.

1. In `scripts/git/record-landed-parent.sh`, change the rebuild invocation from:

   ```bash
   python3 "$REBUILD"
   ```

   to:

   ```bash
   python3 "$REBUILD" --landing-parent "$PARENT_ID"
   ```

2. Manual verification on epic worktree (no product commit beyond Stage 1):

   ```bash
   git fetch origin
   /home/susan/astral/.venv/bin/python3 scripts/rebuild_merge_ticket_log.py --dev-ref origin/dev --landing-parent AST-801
   ```

   Confirm stdout JSON `"parents"` contains **AST-801** alongside other User Testing parents whose ftr is on dev.

3. **Betty manifest (document only — do not edit tests):** Add to `docs/test-bible/dev/record_landed_parent.md` coverage map when Betty picks up **AST-805**:

   - Rebuild CLI with `--landing-parent` unions id not returned by mocked empty Linear UAT query when ftr is ancestor of dev-ref.
   - `record-landed-parent.sh` passes `--landing-parent "$PARENT_ID"` (static text guard or stub integration test).

   Suggested pytest module: new `TestRebuildMergeTicketLogLandingParent` in `tests/component/scripts/test_rebuild_merge_ticket_log.py` (or extend `test_record_landed_parent.py` with rebuild stub that asserts argv).

**Ritual:** `code(AST-805): wire landing-parent through record-landed-parent`

---

## Self-Assessment

**Scope:** `minor` — Two script files only (`rebuild_merge_ticket_log.py`, `record-landed-parent.sh`); no core, external, or UI layers.

**Conf:** `high` — Root cause reproduced (prep-uat ordering vs Linear query); fix is a minimal union of one known parent id at land time; AST-800 rebuild semantics preserved.

**Risk:** `low` — Change affects prep-uat log rebuild only; incorrect `--landing-parent` validation could include a bogus id, but ftr-on-dev gate and existing id normalization limit blast radius.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | OK? |
|------|-----|
| §1.3 DRY | Reuses existing `_collect_entries` ftr/timestamp logic; no duplicate Linear query |
| §3.5 naming | `--landing-parent`, `_collect_entries` param `landing_parent` |
| Layer imports | Script may import external/utils per scripts exemption |
| Out of scope | No changes to **AST-802** eligibility or deploy-status read path |

No conflicts flagged.

---

## Review (build)

**Branch:** `origin/sub/AST-801/AST-805-uat-merge-ticket-log-missing-after-prep-uat`

**Commits:**
- `f52d9f3` — `code(AST-805): landing parent bypass in merge ticket log rebuild`
- `06419e3` — `code(AST-805): wire landing-parent through record-landed-parent`

**Manual verify:** `rebuild_merge_ticket_log.py --dev-ref origin/dev --landing-parent AST-801` → JSON includes **AST-801** in `parents` with `landing_parent: "AST-801"`.

---

## Radia review (2026-06-25)

**Diff:** `origin/dev...origin/sub/AST-801/AST-805-uat-merge-ticket-log-missing-after-prep-uat` @ `7ae3670`  
**Product commits:** `f52d9f3` rebuild CLI · `06419e3` record-landed-parent wire  
**Tests:** Betty manifest @ `1cc4dde` / `merge-tests` @ `7ae3670`

### What's solid

| Area | Notes |
|------|-------|
| Root-cause fix | `--landing-parent` unions prep-uat landing id with Linear UAT set; bypasses **User Testing** filter only for that one id at land time. |
| AST-800 preserved | ftr-on-dev gate (`_resolve_ftr_ref`), `recorded_at` resolution, full-log rewrite, sort-by-`recorded_at` unchanged. |
| Wiring | `record-landed-parent.sh` passes `--landing-parent "$PARENT_ID"`; stdout JSON includes `landing_parent` for forensics. |
| Scope | Scripts only — no `deploy_status`, Linear fetch, or **AST-802** eligibility touched. |
| Tests + bible | Union/skip-blank/ftr gate/summary JSON + shell flag guard + integration stub; bible rows in `record_landed_parent.md` and `merge_ticket_log.md`. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| — | — | None. |

### Recommended actions

| Action | Owner |
|--------|-------|
| None blocking | — |

**Counts:** 0 fix-now · 0 discuss · 0 advisory

**Outcome:** Clean — next prep-uat land should include landing parent in deploy-env tooltip.

— Radia
