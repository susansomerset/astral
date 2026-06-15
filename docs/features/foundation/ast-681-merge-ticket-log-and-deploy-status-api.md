# Merge ticket log and deploy-status API

**Linear:** [AST-681 — Merge ticket log and deploy-status API](https://linear.app/astralcareermatch/issue/AST-681/merge-ticket-log-and-deploy-status-api-create-a-ticket-log-in-utils)

**Parent:** [AST-675 — Create a ticket log in utils](https://linear.app/astralcareermatch/issue/AST-675/create-a-ticket-log-in-utils) (definition reference only)

**Publish ref:** `origin/sub/AST-675/ast-681-merge-ticket-log-and-deploy-status-api` (origin only)

## Summary

Administrators need a durable, repo-shipped history of which Linear parent epics have landed on `dev`, surfaced through the existing admin `GET /api/deploy_status` payload. This ticket adds an append-only JSON log under `data/`, a utils module that is the sole writer, a small CLI script for finish-up to invoke (wired in sibling AST-683), and a read-only `merge_tickets` field on `get_deploy_status_payload()` (most recent first). No SHA, no Linear API, no git mining, no UI tooltip (sibling AST-682), no finish-up wiring (sibling AST-683).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `MERGE_TICKET_LOG_CONFIG` with log path under `data_dir` | utils |
| `data/merge_ticket_log.json` | New shipped seed file: `[]` (append-only history accumulates here) | data |
| `src/utils/merge_ticket_log.py` | New module: read log, append entry, validate ticket id | utils |
| `src/utils/deploy_status.py` | Import read helper; add `merge_tickets` to payload (most recent first) | utils |
| `scripts/append_merge_ticket_log.py` | New CLI: `python3 scripts/append_merge_ticket_log.py AST-675` | scripts |
| `tests/component/utils/test_merge_ticket_log.py` | Read/append/validation tests (Betty manifest — engineer runs in test-child) | test |
| `tests/component/utils/test_deploy_status.py` | Assert `merge_tickets` on payload (Betty manifest — engineer runs in test-child) | test |
| `tests/component/ui/api/test_api_system.py` | Extend `TestDeployStatus` expected JSON with `merge_tickets` (Betty manifest) | test |

**Verify only (no change expected):**

| File | Role |
|------|------|
| `src/ui/api/api_system.py` | Already returns `jsonify(get_deploy_status_payload())` — shape change is sufficient |
| `.gitignore` | Must **not** ignore `data/merge_ticket_log.json` (only `**/_*.json` and listed runtime dirs are ignored) |

**Out of scope:** admin nav environment tooltip (AST-682), finish-up script hook (AST-683), backfill from git history, SHA per entry, Linear API lookups, frontend changes.

---

## Stage 1: Config, seed log file, and merge_ticket_log utils module

**Done when:** `MERGE_TICKET_LOG_CONFIG` resolves to `data/merge_ticket_log.json`; shipped seed is `[]`; `read_merge_ticket_log()` returns stored entries oldest-first; `append_merge_ticket_log(ticket_id)` appends one `{ticket_id, recorded_at}` entry without truncating prior rows; invalid ticket ids raise `ValueError`; `python3 -m py_compile src/utils/merge_ticket_log.py src/utils/config.py` passes.

1. In `src/utils/config.py`, after the `ASTRAL_CONFIG` block opening paths section (~line 1646), add a dedicated block **before** `ASTRAL_CONFIG` closes (or immediately after path keys inside `ASTRAL_CONFIG` — prefer a top-level sibling block like other feature configs):

   ```python
   # ---------------------------------------------------------------------------
   # MERGE_TICKET_LOG_CONFIG: append-only parent epic land history (AST-675/681).
   # Shipped in-repo; finish-up appends via scripts/append_merge_ticket_log.py.
   # ---------------------------------------------------------------------------
   MERGE_TICKET_LOG_CONFIG = {
       "log_path": _PROJECT_ROOT / "data" / "merge_ticket_log.json",
   }
   ```

   Add `MERGE_TICKET_LOG_CONFIG` to the module header comment list (~lines 12–26).

2. Create `data/merge_ticket_log.json` with exact contents (no trailing newline required, but file must be valid JSON):

   ```json
   []
   ```

3. Create `src/utils/merge_ticket_log.py` with module docstring: append-only merge ticket log for deploy status (AST-681). Imports: `json`, `re`, `tempfile`, `datetime`, `timezone`, `Path`; `MERGE_TICKET_LOG_CONFIG` from `src.utils.config`.

4. In `merge_ticket_log.py`, define module-level pattern and helpers:

   ```python
   _TICKET_ID_RE = re.compile(r"^AST-\d+$")

   def _log_path() -> Path:
       return Path(MERGE_TICKET_LOG_CONFIG["log_path"])

   def _normalize_ticket_id(raw: str) -> str:
       ticket_id = (raw or "").strip().upper()
       if not _TICKET_ID_RE.match(ticket_id):
           raise ValueError(f"invalid ticket id: {raw!r} (expected AST-<number>)")
       return ticket_id
   ```

5. Implement `read_merge_ticket_log() -> list[dict]`:
   - `path = _log_path()`
   - If `not path.exists()`: return `[]`.
   - Read text, `json.loads`; require top-level JSON **array**; each element must be a `dict` with string keys `ticket_id` and `recorded_at` (if an entry lacks either key, still return it — do not filter; corrupt **file** shape raises `ValueError`).
   - Return the list in **file order** (oldest entry first).

6. Implement `append_merge_ticket_log(ticket_id: str) -> dict`:
   - `normalized = _normalize_ticket_id(ticket_id)`.
   - `recorded_at = datetime.now(timezone.utc).isoformat()` (UTC, offset-aware ISO string).
   - `entry = {"ticket_id": normalized, "recorded_at": recorded_at}`.
   - `entries = read_merge_ticket_log()` (may be empty).
   - `entries.append(entry)` — **never** slice, replace, or dedupe; full history retained.
   - Write atomically: create `path.parent` if missing; write JSON to a temp file in the same directory (`tempfile.NamedTemporaryFile(..., delete=False, dir=path.parent)`), `json.dump(entries, f, indent=2)` plus trailing newline, `flush` + `os.fsync`, then `Path.replace` onto `path`.
   - Return `entry`.

   ⚠️ **Decision:** JSON array file under `data/` (not SQLite) so finish-up can commit the updated file to git without a DB migration; matches parent “ships with each release.”

   ⚠️ **Decision:** Sole writer is `append_merge_ticket_log` (and the CLI script that calls it). API and deploy status are read-only via `read_merge_ticket_log`.

7. `python3 -m py_compile src/utils/merge_ticket_log.py src/utils/config.py`

**Ritual:** `code(AST-681): merge ticket log config and utils module`

---

## Stage 2: Deploy-status payload and append CLI

**Done when:** `get_deploy_status_payload()` includes `merge_tickets` (list, most recent first, empty list when log empty); `GET /api/deploy_status` returns the new key for admins; `python3 scripts/append_merge_ticket_log.py AST-675` appends one entry and exits 0; invalid argv exits 1 with usage message; `python3 -m py_compile src/utils/deploy_status.py scripts/append_merge_ticket_log.py` passes.

1. In `src/utils/deploy_status.py`, add import:

   ```python
   from src.utils.merge_ticket_log import read_merge_ticket_log
   ```

2. In `get_deploy_status_payload()`, after building `payload` with uptime fields and optional `environment`, add:

   ```python
   entries = read_merge_ticket_log()
   payload["merge_tickets"] = list(reversed(entries))
   ```

   Always include `merge_tickets` key (use `[]` when log empty — not omitted).

   ⚠️ **Decision:** Return **full** stored history in API payload; sibling AST-682 UI bounds display to 20. No server-side slice in this ticket.

3. Do **not** change `format_uptime_seconds`, `_resolve_environment`, `get_deploy_label`, `is_local_deploy_env`, or `ui_llm_debug`.

4. Do **not** change `src/ui/api/api_system.py`.

5. Create `scripts/append_merge_ticket_log.py`:

   ```python
   #!/usr/bin/env python3
   """Append one parent Linear ticket id to the merge ticket log (AST-681).

   Usage:
       python3 scripts/append_merge_ticket_log.py AST-675
   """
   ```

   - `sys.path.insert(0, str(Path(__file__).resolve().parent.parent))` (same depth as other scripts).
   - Require exactly one positional arg after script name; on missing arg print usage to stderr and `sys.exit(1)`.
   - Call `append_merge_ticket_log(argv_ticket_id)` from `src.utils.merge_ticket_log`.
   - On success: print `json.dumps(entry)` to stdout (single line) and `sys.exit(0)`.
   - On `ValueError` (invalid id) or I/O/JSON errors: print message to stderr and `sys.exit(1)`.

6. `python3 -m py_compile src/utils/deploy_status.py scripts/append_merge_ticket_log.py`

**Ritual:** `code(AST-681): expose merge_tickets on deploy status and append CLI`

---

## Stage 3: Component tests (Betty manifest — engineer runs in test-child)

**Done when:** Betty’s manifest tests pass; empty log yields `merge_tickets: []` on payload; append persists across read; deploy status API test expects the new key.

1. In `tests/component/utils/test_merge_ticket_log.py` (new file), use `tmp_path` monkeypatch on `MERGE_TICKET_LOG_CONFIG["log_path"]` (or monkeypatch `_log_path`) so tests never touch repo `data/merge_ticket_log.json`:
   - `test_read_empty_when_missing` — no file → `[]`.
   - `test_append_and_read_preserves_order` — append `AST-100` then `AST-200`; read returns oldest-first with both entries and ISO timestamps.
   - `test_append_rejects_invalid_id` — `append_merge_ticket_log("foo")` raises `ValueError`.
   - `test_append_never_truncates` — append three ids; read length 3.

2. In `tests/component/utils/test_deploy_status.py`, class `TestGetDeployStatusPayload`:
   - Monkeypatch `read_merge_ticket_log` to return `[{"ticket_id": "AST-100", "recorded_at": "2026-01-01T00:00:00+00:00"}, {"ticket_id": "AST-200", "recorded_at": "2026-01-02T00:00:00+00:00"}]`.
   - Assert `payload["merge_tickets"][0]["ticket_id"] == "AST-200"` (most recent first).
   - Monkeypatch returning `[]` → `payload["merge_tickets"] == []`.

3. In `tests/component/ui/api/test_api_system.py`, class `TestDeployStatus`:
   - Add `merge_tickets: []` to admin expected payload dicts (or monkeypatched expected) so 200 JSON shape includes the key.

**Ritual:** `test(AST-681): merge ticket log and deploy status coverage`

---

## Execution contract (for the developer agent)

The plan is binding. Execute stages in order. Do not wire finish-up, admin tooltip, or backfill. When `read_merge_ticket_log` finds invalid top-level JSON (not an array), stop and escalate — do not silently reset the file.

Blocking questions use parent **AST-675** with:

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

---

## Self-Assessment

**Scope:** `scope-Single-Component` — New utils module, one config block, one shipped JSON seed, deploy_status payload extension, and one scripts CLI; no UI, finish-up, or database changes.

**Conf:** `conf-high` — Append-only JSON log and admin deploy-status extension follow existing `deploy_status.py` / `config.py` patterns; sibling tickets own wiring and tooltip display.

**Risk:** `risk-low` — Worst case is wrong or missing ticket history in admin footer data; uptime/environment behavior and non-admin paths are unchanged.

---

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-675/ast-681-merge-ticket-log-and-deploy-status-api`  
**Product commits:** `612386bf` (config + `merge_ticket_log` utils + seed `data/merge_ticket_log.json`), `d0258f33` (`merge_tickets` on deploy-status payload + `scripts/append_merge_ticket_log.py`)

---

## Self-review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Single read/append module; deploy_status only reverses for API order |
| §1.4 magic numbers | Ticket id pattern and log path live in config/module constants |
| §2.1 config | `MERGE_TICKET_LOG_CONFIG["log_path"]` is source of truth for file location |
| §2.4 batch | N/A — no claim/get batch |
| §2.6 state machine | N/A |
| §3.3 imports | `utils` → stdlib + `config` only; `deploy_status` → `merge_ticket_log`; `ui` unchanged |
| §3.5 naming | `merge_ticket_log`, `append_merge_ticket_log`, `merge_tickets` match domain |
| §3.6 local debug | Log is shipped `data/`, not `debug/` — intentional per parent AC |

No conflicts requiring `conf-!!-NONE`.

---

## Radia review (2026-06-15)

**Diff:** `origin/dev...origin/sub/AST-675/ast-681-merge-ticket-log-and-deploy-status-api` @ `61482c0f`  
**Verdict:** Clean — no fix-now items.

### What's solid

| Stage | Check |
|-------|-------|
| 1 | `MERGE_TICKET_LOG_CONFIG` + shipped `data/merge_ticket_log.json` seed `[]`; append-only read/write in `merge_ticket_log.py`; atomic write via temp file + `replace`; ticket id normalized to `AST-<n>` |
| 2 | `get_deploy_status_payload()` always includes `merge_tickets` (most recent first); `api_system.py` unchanged — shape flows through existing route |
| 3 | `scripts/append_merge_ticket_log.py` — single arg, stderr usage on bad argv, JSON line stdout on success |
| Tests | Betty manifest covers empty/missing log, order, non-array rejection, invalid id, no truncation, deploy payload order, API expected keys |

**Rules:** utils → stdlib + `config` only; no logging in new paths; temp-file cleanup re-raises (not silent failure); sibling scope (AST-682 tooltip, AST-683 finish-up) not smuggled.

### Advisory

- Malformed JSON (syntax) on read raises `JSONDecodeError`; non-array top-level raises `ValueError` — both fail the admin deploy-status path rather than resetting the file, matching plan escalation intent.
- Read-modify-write without file lock assumes single-writer (finish-up CLI); concurrent append could interleave — acceptable per parent AC until proven otherwise.

### Recommended actions

None — **resolve-child** may proceed (no product changes required).

---

## Resolution (2026-06-15)

**Publish ref:** `origin/sub/AST-675/ast-681-merge-ticket-log-and-deploy-status-api` @ `08ded1c0` (Radia `docs(AST-681): Radia review — clean`)

Radia review clean — no fix-now, discuss, or product changes. Merged `origin/dev`, `origin/ftr/ast-675-create-a-ticket-log-in-utils`, and publish ref on epic worktree; §9a dry-run clean against `origin/dev` and `origin/ftr/ast-675-create-a-ticket-log-in-utils`.

**Outcome:** Append-only merge ticket log, deploy-status `merge_tickets` payload, and append CLI ready for sibling wiring (AST-682 tooltip, AST-683 finish-up).
