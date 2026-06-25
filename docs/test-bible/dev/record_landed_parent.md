# Record Landed Parent (prep-uat)

**Test module:** `tests/component/scripts/test_record_landed_parent.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `scripts/git/record-landed-parent.sh` | `tests/component/scripts/test_record_landed_parent.py` | no |
| `scripts/git/prep-uat-land.sh` (wiring) | static text guard in same module | no |
| `scripts/git/merge-parent.sh` | must **not** call record helper | static guard in same module |

**Existing coverage (no rerun required for AST-683 manifest):** `scripts/append_merge_ticket_log.py` and `src/utils/merge_ticket_log.py` — see `utils/merge_ticket_log.md` (AST-681).

---

### AST-683 / AST-693

After successful **`prep-uat-land.sh`** ftr land push, **`record-landed-parent.sh`** appends the parent epic id via AST-681 CLI, commits `data/merge_ticket_log.json`, and pushes `dev`. **Re-prep-uat** of the same parent updates **`recorded_at`** only (no duplicate row). **`merge-parent.sh` / finish-up** does **not** record — Susan needs the deploy env label during UAT, not after ship.

| Behavior | Tests |
| --- | --- |
| Append + commit in temp repo | `TestRecordLandedParent::test_record_landed_parent_appends_and_commits` |
| Missing append CLI → `BLOCKED` | `TestRecordLandedParent::test_record_landed_parent_missing_append_script_blocks` |
| `prep-uat-land.sh` invokes helper after push | `TestPrepUatLandShell::test_prep_uat_land_shell_wires_record_helper_after_push` |
| `merge-parent.sh` does not invoke helper | `TestMergeParentShell::test_merge_parent_shell_does_not_record_merge_ticket_log` |
| Same ticket id → timestamp update, no duplicate | `TestAppendMergeTicketLog::test_append_same_id_updates_timestamp_no_duplicate` |

---

### AST-800

Prep-uat **`record-landed-parent.sh`** invokes **`scripts/rebuild_merge_ticket_log.py`** (full log rebuild) — replaces append-only path (AST-683). See **`dev/record_landed_parent.md`**.

| Behavior | Tests |
| --- | --- |
| Shell wires rebuild, not append | `TestRecordLandedParentShell::test_record_landed_parent_wires_rebuild_not_append` |
| Rebuild stub + commit in temp repo | `TestRecordLandedParent::test_record_landed_parent_rebuilds_and_commits` |
| Missing rebuild CLI → `BLOCKED` | `TestRecordLandedParent::test_record_landed_parent_missing_rebuild_script_blocks` |

**Manifest pytest gate:**

```bash
.venv/bin/python -m pytest \
  tests/component/external/test_linear.py \
  tests/component/core/test_deploy_status.py \
  tests/component/scripts/test_record_landed_parent.py \
  -q
```

---

### AST-805 · AST-801

**UAT fix:** Prep-uat **`record-landed-parent.sh`** runs rebuild **before** Linear parent moves to **User Testing**, so the landing parent was omitted from **`fetch_user_testing_parent_ids()`**. **`--landing-parent AST-NNN`** unions the landing id with the Linear UAT set; ftr-on-dev and **`recorded_at`** gates unchanged (**AST-800**).

| # | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| 1 | Union landing parent not in mocked Linear UAT set | `scripts/rebuild_merge_ticket_log.py` | **`TestRebuildMergeTicketLogLandingParent::test_collect_entries_unions_landing_parent_not_in_linear_uat`** |
| 2 | Landing parent still requires ftr-on-dev | same | **`::test_collect_entries_skips_landing_parent_without_ftr_on_dev`** |
| 3 | Blank `--landing-parent` ignored | same | **`::test_collect_entries_ignores_blank_landing_parent`** |
| 4 | stdout JSON includes **`landing_parent`** | same | **`::test_main_json_summary_includes_landing_parent`** |
| 5 | Shell passes **`--landing-parent "$PARENT_ID"`** | `scripts/git/record-landed-parent.sh` | **`TestRecordLandedParentShell::test_record_landed_parent_passes_landing_parent_flag`** |
| 6 | Temp-repo integration stub receives flag | same + rebuild stub | **`TestRecordLandedParent::test_record_landed_parent_rebuilds_and_commits`** |

**Regression (required):** **AST-800** rebuild wiring tests in same module remain green.

**AST-805** narrowed run:

```bash
.venv/bin/python -m pytest \
  tests/component/scripts/test_rebuild_merge_ticket_log.py \
  tests/component/scripts/test_record_landed_parent.py \
  -q
```

**Pass criterion:** pytest green on items 1–6 + AST-800 regression in **`test_record_landed_parent.py`** — not zero-arg harness / branch-lock gate.

---

### AST-806

**UAT fix:** Prep-uat **`record-landed-parent.sh`** used bare **`python3`**, so rebuild failed with missing **`dotenv`** and **`data/merge_ticket_log.json`** never landed on **dev** (e.g. **AST-788** absent from deploy env tooltip). Resolve **`${ASTRAL_PYTHON:-$REPO_ROOT/.venv/bin/python}`**; **BLOCKED** when not executable. **`--landing-parent`** wiring unchanged (**AST-805**).

| # | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| 1 | Venv python resolution + no bare `python3 "$REBUILD"` | `scripts/git/record-landed-parent.sh` | **`TestRecordLandedParentShell::test_record_landed_parent_resolves_venv_python`** |
| 2 | Missing `.venv/bin/python` → **BLOCKED** (AST-806) | same | **`TestRecordLandedParent::test_record_landed_parent_missing_venv_python_blocks`** |
| 3 | **`ASTRAL_PYTHON`** override runs rebuild | same | **`TestRecordLandedParent::test_record_landed_parent_honors_astral_python_override`** |
| 4 | Missing rebuild CLI still **BLOCKED** after venv gate | same | **`TestRecordLandedParent::test_record_landed_parent_missing_rebuild_script_blocks`** |

**Regression (required):** **AST-805** landing-parent union + **AST-800** rebuild wiring tests in same module remain green.

**AST-806** narrowed run:

```bash
.venv/bin/python -m pytest \
  tests/component/scripts/test_rebuild_merge_ticket_log.py \
  tests/component/scripts/test_record_landed_parent.py \
  -q
```

**Pass criterion:** pytest green on items 1–4 + AST-805/AST-800 regression — not zero-arg harness / branch-lock gate.

---

### AST-807 · AST-799

**UAT fix (prep-uat land):** **`record-landed-parent.sh`** invoked bare **`python3`**, so **`rebuild_merge_ticket_log.py`** failed with missing **`dotenv`** and **AST-799** never appeared in the deploy env tooltip merge-ticket list. Resolve **`${ASTRAL_PYTHON:-$REPO_ROOT/.venv/bin/python}`**; **BLOCKED** with **`setup_dev.sh`** hint when interpreter not executable. **`--landing-parent`** wiring unchanged (**AST-805**).

| # | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| 7 | Shell uses repo venv Python (not bare `python3 "$REBUILD"`) | `scripts/git/record-landed-parent.sh` | **`TestRecordLandedParentShell::test_record_landed_parent_uses_venv_python`** |
| 8 | Missing venv → **BLOCKED** before rebuild | same | **`TestRecordLandedParent::test_record_landed_parent_blocks_without_venv`** |

**Regression (required):** **AST-805** landing-parent union, **AST-800** rebuild wiring, **`test_record_landed_parent_honors_astral_python_override`**, **`test_record_landed_parent_missing_rebuild_script_blocks`**.

**AST-807** narrowed run:

```bash
.venv/bin/python -m pytest \
  tests/component/scripts/test_rebuild_merge_ticket_log.py \
  tests/component/scripts/test_record_landed_parent.py \
  -q
```

**Pass criterion:** pytest green on items 7–8 + AST-805/AST-800/806 regression in **`test_record_landed_parent.py`** — not zero-arg harness / branch-lock gate.
