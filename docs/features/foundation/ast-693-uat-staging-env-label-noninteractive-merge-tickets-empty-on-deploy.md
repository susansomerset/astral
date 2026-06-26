<!-- linear-archive: AST-693 archived 2026-06-23 -->

## Linear archive (AST-693)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-693/uat-staging-env-label-non-interactive-merge-tickets-empty-on-deploy  
**Status at archive:** Done  
**Project:** Astral Foundation (inherited from AST-675)  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-675 — Create a ticket log in utils  
**Blocked by / blocks / related:** parent: AST-675

### Description

## What failed

After **AST-691** landed on staging (deployment notes cite `merge-tests(AST-691)`), Susan UAT on staging shows the admin deploy footer rendering **non-interactive** markup — no `nav-deploy-env-interactive` class, no pointer cursor, no hover tooltip:

```html
<div class="nav-deploy-footer" aria-label="Deploy status"><span class="nav-deploy-env-wrap"><span class="nav-deploy-env">staging</span></span><span class="nav-deploy-sep">·</span><span class="nav-deploy-uptime">11m</span></div>
```

Current code only enables pointer + 0.5s tooltip when `merge_tickets` from `GET /api/deploy_status` is non-empty. Staging appears to return an empty/missing ticket list (or the log is not populated on the deployed instance), so Susan still sees the pre-fix static env label.

## Expected

With `ASTRAL_DEPLOY_ENV` set and admin session on staging, hovering the environment label shows **pointer** cursor and, after **0.5 seconds**, a tooltip with up to **20** ticket lines (most recent first).

**Exact line format** (each line):

```
AST-675 6/15/26, 1:23:45 PM
AST-646 6/14/26, 3:45:12 PM
```

Pattern: `{TICKET_ID} {fmtTime(recorded_at)}` — ticket id, space, locale datetime from existing `fmtTime` (en-US, admin timezone).

Susan must see this on staging after fix — either by ensuring `merge_tickets` is populated on staging deploy-status, and/or by making the env label interactive when tickets exist (verify end-to-end on Railway, not local-only).

## Repro

1. Log in as admin on **staging** after AST-691 deploy.
2. Open left nav deploy footer; inspect DOM for env label.
3. **Observed:** plain `nav-deploy-env` with text `staging`; no interactive class; no tooltip on hover.
4. **Expected:** pointer cursor; after 0.5s hover, tooltip lines as above when tickets are logged.

## Parent AC (quoted inline)

> 4. With `ASTRAL_DEPLOY_ENV` set and admin session, hovering the environment label shows up to **20** ticket lines (id + timestamp), most recent first, separated by line breaks.

## Boundaries

* Does not change merge log storage format or finish-up wiring unless required to surface entries on staging.
* Does not revert AST-691 hover-delay tooltip UX.
* Fix must be verifiable on **staging** (Susan pasted production DOM).

### Comments

#### betty — 2026-06-16T01:09:28.788Z
## QA handoff fix (AST-693)

**Issue:** `test_includes_uptime_without_environment` and `test_includes_environment_when_set` read seeded `data/merge_ticket_log.json` on disk — asserted `merge_tickets == []` without monkeypatch.

**Fix:** Added `monkeypatch.setattr(ds, "read_merge_ticket_log", lambda: [])` to both tests (same pattern as `test_merge_tickets_empty_when_log_empty`). Updated `docs/test-bible/utils/deploy_status.md` AST-679 rows.

**Republished:** `origin/sub/AST-675/ast-693-uat-staging-env-label-noninteractive-merge-tickets-empty-on-deploy` @ `432c79f` (`merge-tests(AST-693): origin/tests 0229567`)

**Bible shasums:**
- `docs/test-bible/utils/deploy_status.md` → see publish ref
- `docs/test-bible/dev/record_landed_parent.md` → unchanged from prior manifest

**Re-run (test-child):**
```bash
.venv/bin/python -m pytest \
  tests/component/utils/test_deploy_status.py \
  tests/component/utils/test_merge_ticket_log.py \
  tests/component/scripts/test_record_landed_parent.py \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_AdminDeployFooter.test.tsx
```

— Betty

#### katherine — 2026-06-16T01:08:12.889Z
[qa-handoff]

@Betty White — manifest red on seeded log (test/manifest, not product).

**Command:**
```
.venv/bin/python -m pytest tests/component/utils/test_deploy_status.py tests/component/utils/test_merge_ticket_log.py tests/component/scripts/test_record_landed_parent.py -q
```

**Failures (2/32):**
- `TestGetDeployStatusPayload::test_includes_uptime_without_environment`
- `TestGetDeployStatusPayload::test_includes_environment_when_set`

Both assert `payload["merge_tickets"] == []` without monkeypatching `read_merge_ticket_log`. AST-693 ships non-empty `data/merge_ticket_log.json` (bootstrap AST-675), so disk reads return 4 entries.

**Fix:** Add `monkeypatch.setattr(ds, "read_merge_ticket_log", lambda: [])` to those two tests (same pattern as `test_merge_tickets_empty_when_log_empty`). Re-publish manifest @ origin/sub tip.

Prep-uat shell test + merge_ticket_log + record_landed_parent: **30 passed**.

#### betty — 2026-06-16T01:04:10.658Z
## QA test manifest (AST-693)

**Publish ref:** `origin/sub/AST-675/ast-693-uat-staging-env-label-noninteractive-merge-tickets-empty-on-deploy` @ `e3b9bde` (`merge-tests(AST-693): origin/tests 2ed645f8`)

**Bible shasum:** `docs/test-bible/dev/record_landed_parent.md` → `6fd784fe650e63eb20f8a61b14a8ac7cb2c1d350b4e97ae6909bf4294bb21fcb`

### 1. New coverage (this pass)
- **`TestPrepUatLandShell::test_prep_uat_land_shell_wires_record_helper_after_push`** — `prep-uat-land.sh` calls `record-landed-parent.sh` after land push, before `RESULT:` echo; parent-id extraction + `BLOCKED` guard

### 2. Existing coverage (bible-backed, rerun)
- **`test_deploy_status.py`** — `test_merge_tickets_most_recent_first`, `test_merge_tickets_empty_when_log_empty`
- **`test_merge_ticket_log.py`** — AST-681 append/read (full module)
- **`TestRecordLandedParent::test_record_landed_parent_appends_and_commits`** — record helper
- **`test_AdminDeployFooter.test.tsx`** — AST-691 hover tooltip regression when API returns `merge_tickets`

### 3. Run gate (test-child)

```bash
.venv/bin/python -m pytest \
  tests/component/utils/test_deploy_status.py \
  tests/component/utils/test_merge_ticket_log.py \
  tests/component/scripts/test_record_landed_parent.py \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_AdminDeployFooter.test.tsx
```

— Betty

#### katherine — 2026-06-16T01:01:29.470Z
Plan doc: https://github.com/susansomerset/astral/blob/sub/AST-675/ast-693-uat-staging-env-label-noninteractive-merge-tickets-empty-on-deploy/docs/features/foundation/ast-693-uat-staging-env-label-noninteractive-merge-tickets-empty-on-deploy.md

**Self-assessment**

- **Scope:** Single-Component — bootstrap `data/merge_ticket_log.json` with AST-675 plus wire `prep-uat-land.sh` to call existing `record-landed-parent.sh`; no AST-691 UI changes.
- **Conf:** high — root cause is empty log on origin/dev while prep-uat never records; reuses AST-681/683 append path.
- **Risk:** low — admin deploy footer display only; duplicate prep-uat lines possible but harmless.

---

# UAT: staging env label non-interactive — merge_tickets empty on deploy

**Linear:** [AST-693 — UAT: staging env label non-interactive — merge_tickets empty on deploy](https://linear.app/astralcareermatch/issue/AST-693/uat-staging-env-label-noninteractive-merge-tickets-empty-on-deploy)

**Parent:** [AST-675 — Create a ticket log in utils](https://linear.app/astralcareermatch/issue/AST-675/create-a-ticket-log-in-utils) (AC reference only — do not implement sibling scope)

**Publish ref:** `origin/sub/AST-675/ast-693-uat-staging-env-label-noninteractive-merge-tickets-empty-on-deploy` (origin only)

## Summary

After **AST-691** shipped, Susan’s staging UAT shows a **static** deploy env label (`nav-deploy-env` only — no `nav-deploy-env-interactive`, no pointer cursor, no hover tooltip). DOM matches the branch where `GET /api/deploy_status` returns **empty** `merge_tickets`. AST-691 correctly gates interactivity on non-empty `merge_tickets`; the bug is that **`data/merge_ticket_log.json` on `origin/dev` is still `[]`**. Finish-up (`merge-parent.sh` → `record-landed-parent.sh`) appends only after ship; **prep-uat** lands `ftr` on `dev` for Railway staging but **does not** record the parent (AST-683 intentional gap). While AST-675 is in **User Testing**, staging never receives log entries, so parent AC 4 cannot pass. This bug **seeds the log for AST-675** and **wires prep-uat to append the parent id** after each successful land push so staging UAT can exercise the AST-691 hover tooltip. No AST-691 UI revert, no log format change, no deploy-status API shape change.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `data/merge_ticket_log.json` | Bootstrap one `AST-675` entry so staging deploy-status returns non-empty `merge_tickets` | data |
| `scripts/git/prep-uat-land.sh` | After successful `push origin dev`, extract parent id and invoke `record-landed-parent.sh` | scripts |

**Verify only (no change expected):**

| File | Role |
|------|------|
| `src/utils/deploy_status.py` | Already exposes `merge_tickets` from `read_merge_ticket_log()` |
| `src/utils/merge_ticket_log.py` | Append/read unchanged — sole writer remains append CLI |
| `scripts/git/record-landed-parent.sh` | Reused by prep-uat wiring (shipped AST-683) |
| `scripts/append_merge_ticket_log.py` | CLI invoked by record helper |
| `src/ui/frontend/src/components/AdminDeployFooter.tsx` | AST-691 hover tooltip — unchanged |
| `src/ui/frontend/src/App.css` | AST-691 tooltip styles — unchanged |
| `scripts/git/merge-parent.sh` | Finish-up path unchanged (already calls record helper) |

**QA manifest (Betty — not engineer commits):** Betty extends `tests/component/scripts/test_record_landed_parent.py` or adds prep-uat subprocess coverage at **Code Complete** (`qa-child`). Engineer does not commit under `tests/` or `docs/test-bible/**` (pre-commit hook).

**Out of scope:** AST-691 UI/CSS changes, deploy-status API contract, log entry format, SHA in entries, Linear API, git-history backfill, child ticket ids in log, changes to `merge-parent.sh` / finish-up semantics beyond reusing existing record helper.

---

## Stage 1: Bootstrap merge ticket log with AST-675

**Done when:** `data/merge_ticket_log.json` contains at least one entry `{"ticket_id": "AST-675", "recorded_at": "<ISO-8601 UTC>"}`; `get_deploy_status_payload()["merge_tickets"]` is non-empty with `AST-675` most recent first; `python3 -m py_compile` on touched paths passes; local smoke confirms deploy-status shape.

1. From repo root (`astral-AST-675/`), confirm log is empty or missing entry for AST-675:

   ```bash
   python3 -c "from src.utils.merge_ticket_log import read_merge_ticket_log; print(read_merge_ticket_log())"
   ```

   Expected before append: `[]` (matches current `origin/dev`).

2. Append the parent epic id using the existing AST-681 CLI (sole writer path — do **not** hand-edit JSON):

   ```bash
   python3 scripts/append_merge_ticket_log.py AST-675
   ```

   ⚠️ **Decision:** One bootstrap entry for the epic under UAT — not git-history backfill (parent AC 8). Timestamp is tool-run time at build, same as finish-up would record.

3. Verify read + deploy-status payload:

   ```bash
   python3 -c "
   from src.utils.merge_ticket_log import read_merge_ticket_log
   from src.utils.deploy_status import get_deploy_status_payload
   entries = read_merge_ticket_log()
   assert len(entries) >= 1 and entries[-1]['ticket_id'] == 'AST-675', entries
   payload = get_deploy_status_payload()
   assert payload['merge_tickets'][0]['ticket_id'] == 'AST-675', payload
   print('ok', payload['merge_tickets'][0])
   "
   ```

4. Stage and commit **only** `data/merge_ticket_log.json`:

   ```bash
   git add data/merge_ticket_log.json
   git commit -m "code(AST-693): bootstrap merge ticket log with AST-675 for staging UAT"
   ```

5. Publish via build-child ritual after stage commit.

   ⚠️ **Decision:** Data file ships in-repo (AST-681); Railway staging reads the same path via `MERGE_TICKET_LOG_CONFIG["log_path"]`. No runtime env override needed.

**Ritual:** `code(AST-693): bootstrap merge ticket log with AST-675 for staging UAT`

---

## Stage 2: Wire prep-uat-land to record landed parent

**Done when:** `scripts/git/prep-uat-land.sh` invokes `record-landed-parent.sh` after a successful `git push origin dev`; parent id extraction matches `merge-parent.sh`; `bash -n scripts/git/prep-uat-land.sh` passes; script still exits non-zero on land failure; `record-landed-parent.sh` failure surfaces as prep-uat failure (Chuckles sees `BLOCKED:`).

1. Open `scripts/git/prep-uat-land.sh`. After the existing land push block:

   ```bash
   git -C "$MAIN" push origin dev

   echo "RESULT: prep-uat-land status=ok dev=$(git -C "$MAIN" rev-parse --short HEAD)"
   ```

   Insert **before** the final `echo "RESULT: prep-uat-land status=ok …"` (record helper performs its own push when log changes):

   ```bash
   PARENT_ID="$(printf '%s' "$PARENT" | grep -oiE 'AST-[0-9]+' | head -1 || true)"
   if [ -z "$PARENT_ID" ]; then
     echo "BLOCKED: parent segment must contain AST-NNN — got: $PARENT" >&2
     exit 1
   fi
   SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
   "$SCRIPT_DIR/record-landed-parent.sh" "$MAIN" "$PARENT_ID"
   ```

2. Keep the existing `RESULT: prep-uat-land status=ok` echo **after** the record call so Chuckles still sees prep-uat success only when both land and record succeed.

3. Run syntax check:

   ```bash
   bash -n scripts/git/prep-uat-land.sh
   bash -n scripts/git/record-landed-parent.sh
   ```

   ⚠️ **Decision:** Reuses AST-683 `record-landed-parent.sh` verbatim — append + commit + push on `dev`. Overrides AST-683 “prep-uat must not append” because User Testing staging cannot satisfy parent AC 4 without a log entry; finish-up runs after UAT, too late for Susan’s hover tooltip check.

   ⚠️ **Decision:** Re-running prep-uat for the same parent may append **duplicate** `AST-675` lines (append-only, no dedup). Acceptable — tooltip still lists history; Susan sees multiple timestamps if Chuckles re-lands.

4. Do **not** change `scripts/git/merge-parent.sh`, `record-landed-parent.sh`, or utils modules.

5. Commit:

   ```bash
   git add scripts/git/prep-uat-land.sh
   git commit -m "code(AST-693): prep-uat records landed parent in merge ticket log"
   ```

**Ritual:** `code(AST-693): prep-uat records landed parent in merge ticket log`

---

## QA expectations (Betty manifest — test-child gate)

| Behavior | Suggested test updates |
| --- | --- |
| Non-empty log → deploy_status `merge_tickets` includes entries | existing `test_deploy_status.py` — may add fixture reading seeded log shape |
| prep-uat-land invokes record helper after push | extend `test_record_landed_parent.py` or new subprocess test with mocked git |
| Admin footer interactive when API returns merge_tickets | existing AST-691 `test_AdminDeployFooter.test.tsx` rows — unchanged if API returns data |

Suggested manifest pytest gate after Betty lands tests:

```bash
python3 -m pytest tests/component/utils/test_deploy_status.py \
  tests/component/utils/test_merge_ticket_log.py \
  tests/component/scripts/test_record_landed_parent.py -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_AdminDeployFooter.test.tsx
```

---

## Execution contract (for the developer agent)

The plan is binding. Execute **Stage 1 → Stage 2** in order. Do not modify frontend files. Do not hand-edit JSON except via `append_merge_ticket_log.py`. When `read_merge_ticket_log()` or deploy-status shape differs from `{ ticket_id, recorded_at }`, stop and comment on AST-675.

Blocking comment format (parent issue):

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

---

## Self-Assessment

**Scope:** `Single-Component` — `data/merge_ticket_log.json` bootstrap plus one shell script change in `prep-uat-land.sh`; closes staging data gap for AST-691 hover tooltip without UI edits.

**Conf:** `high` — Root cause confirmed (`origin/dev` log is `[]`); reuses AST-681 append CLI and AST-683 record helper; parent id extraction copied from `merge-parent.sh`.

**Risk:** `low` — Admin-only deploy footer display; worst case is duplicate log lines on repeated prep-uat or wrong parent id in log; does not affect auth, dispatch, or merge-child sequencing.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses `append_merge_ticket_log.py` and `record-landed-parent.sh`; no duplicate append logic |
| §2.1 Config | No new config keys; `MERGE_TICKET_LOG_CONFIG` path unchanged |
| §3.3 Imports | No Python layer changes in Stage 2; Stage 1 data-only |
| §3.5 Naming | `merge_tickets` / `AST-675` match parent epic and API |
| §3.6 Data files | `data/merge_ticket_log.json` is shipped in-repo per AST-681 — not gitignored |

No conflicts requiring `conf-!!-NONE`.

---

## Review (build)

**Built:** `sub/AST-675/ast-693-uat-staging-env-label-noninteractive-merge-tickets-empty-on-deploy` @ `51f6c001f46214245ad476f2031b882d26276f36`

**Stage 1:** Bootstrapped `data/merge_ticket_log.json` with AST-675 via append CLI; deploy_status returns non-empty `merge_tickets`.

**Stage 2:** `prep-uat-land.sh` calls `record-landed-parent.sh` after land push (same parent-id extraction as `merge-parent.sh`).
