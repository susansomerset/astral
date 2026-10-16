<!-- linear-archive: AST-1960 archived 2026-10-08 -->

## Linear archive (AST-1960)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1960/record-the-serving-host-on-the-dispatch-ledger-add-host-discovery  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** katherine  
**Priority / estimate:** None / 2  
**Parent:** AST-1954 — Add host-discovery probe ahead of warm/gather; pin the batch to one provider  
**Blocked by / blocks / related:** parent: AST-1954

### Description

## What this implements

`do_task` records the host returned with each response on the active batch's `dispatch_ledger` row, using the server label for Anthropic-direct calls. The ledger table gains the host column. This child comes after #1, whose `llm_compat` result supplies `host`. It does **not** touch the external layer (#1) or `dispatcher.py`.

## Citations

`patt.entity.batch-processing` (host recorded on the claim's ledger row); `stat.logging.debug`.

## Scope

* `src/core/agent.py` (**modified**): **modified call path** (`do_task` via `_send_to_server`). After each call it writes the result's host, or the server label for the Anthropic-direct client, to the `dispatch_ledger` row for `log_batch_id` when one is set.
* `src/data/database.py` (**modified**):
  * **Modified** `dispatch_ledger` schema-ensure: adds the host column (DDL only, per AST-1497).
  * **Modified** `_LEDGER_UPDATE_COLS`: includes it.
  * **Modified readers:** return it.
* Tests and bibles (Betty in `qa-child`):
  * `tests/component/core/test_agent.py`
  * `tests/component/data/database/test_dispatch_ledger.py`
  * `docs/test-bible/core/agent.md`
  * `docs/test-bible/data/database/dispatch_ledger.md`

## Acceptance criteria

1. **The host is recorded (this child's part).**
   * **Check (component test, temp DB):** after `do_task` runs under a `log_batch_id` with a saved ledger row, `get_dispatch_ledger(<id>)` returns that host.
   * **Check:** for an Anthropic-direct agent, the ledger row's host is the `anthropic` server label.
   * **Fails if:** the host is missing from the ledger row, or it is wrong for direct.
2. **Live lock works (UAT).**
   * **Check:** run one live `anticipate_scan` batch of at least 3 entities on an OpenRouter agent. The batch log shows one probe. Every call's INFO line names the same host, and the batch's `dispatch_ledger` row shows it. Timesheet `inputcached` is greater than 0 on every call after the warm call.
   * **Fails if:** the warm call returns 404 (meaning `only` didn't accept the response's provider name), the hosts differ, the ledger host is empty, or `inputcached` is 0 after the warm call.

## Boundaries

* Does **not** touch `config.py`, `openrouter.py`, `llm_compat.py` or `logging.py`: that is #1 (Per-batch probe and host lock on the OpenRouter path - Hedy).
* Does **not** change `dispatcher.py`. The host reaches the ledger through `agent.py`, because `ctx` copies and summed dispatch results don't carry it back to the dispatcher (parent As-built facts).

## Notes for planning

* Cite `patt.entity.batch-processing` and `stat.logging.debug`.
* `agent.py` already writes ledger rows for chained hops (`_open_run_next_hop_ledger` / `_finalize_run_next_hop_ledger`). Writing to the `log_batch_id` row covers dispatcher batches and hop rows alike.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

### Comments

#### radia — 2026-10-04T00:52:13.139Z
[code-rubric] PROCEED (Commit: c432cea62) ledger host on batch row

#### betty — 2026-10-04T00:49:46.971Z
`origin/sub/AST-1954/AST-1960-ledger-host` @ `c432cea62` · ledger host tests, 67 manifest

#### joan — 2026-10-04T00:40:44.351Z
[plan-rubric] PROCEED (Commit: a0b5d2fdf) ledger host plan solid

#### katherine — 2026-10-04T00:39:39.554Z
`origin/sub/AST-1954/AST-1960-ledger-host` @ `a0b5d2fdf` · ledger host plan ready

---

# AST-1960 — Record the serving host on the dispatch ledger

- **Parent:** [AST-1954 — Add host-discovery probe ahead of warm/gather; pin the batch to one provider](https://linear.app/astralcareermatch/issue/AST-1954)
- **Ticket:** [AST-1960](https://linear.app/astralcareermatch/issue/AST-1960)
- **Publish ref:** `sub/AST-1954/AST-1960-ledger-host` (origin only)
- **Built on:** `origin/ftr/AST-1954-host-probe` @ `3942222a5` (AST-1959 merged: every `send_to_llm_compat` result carries `host`)

`dispatch_ledger` gains a `host` column. After each successful `_send_to_server` call inside `do_task`, when
`log_batch_id` is set, `do_task` writes the served host onto that batch's ledger row. The host is the
result's `host` (AST-1959 sets it on every `llm_compat` result: OpenRouter's response `provider`, else the
compat server's label). Anthropic-direct results carry no `host`, so the `anthropic` server's own label
(`"Anthropic"`) stands in. `log_batch_id` is the dispatcher's batch id, or the hop row's id when
`_open_run_next_hop_ledger` has opened one, so one write covers dispatcher batches and chained hops alike.
`dispatcher.py`, `llm_compat.py`, `openrouter.py`, `config.py` and `logging.py` do not change.

## Canon (this ticket's Citations)

| Id | How this plan honours it |
|----|--------------------------|
| `patt.entity.batch-processing` | The host goes onto the `dispatch_ledger` row keyed by the claim's own `batch_id`, read from the `log_batch_id` contextvar the dispatcher (or `_open_run_next_hop_ledger`) already set. No batch id is minted here, and claim/release is untouched. The ledger is the permanent audit row the pattern names ("Dispatch ledger and cost … keyed by `batch_id`"). |
| `stat.logging.debug` | One ungated `logger.debug("Calling database.update_dispatch_ledger: [...]")` callee-in line before the write, with the batch id and host. No `if debug` gate, nothing truncated, and no logging added in `src/data/`. |

## Files Changed (planned)

Every row is named in this ticket's `## Scope`. Tests and bibles are Betty's (`qa-child`); the engineer does not touch `tests/` or `docs/test-bible/`.

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | `dispatch_ledger` schema-ensure adds `host TEXT` (CREATE + migrate list, DDL only); `_LEDGER_UPDATE_COLS` gains `"host"` | data |
| `src/core/agent.py` | `do_task`: after `_send_to_server` returns success under a `log_batch_id`, write the result's host (or the server label for Anthropic-direct) to that ledger row | core |

⚠️ **Decision:** The ledger readers (`get_dispatch_ledger`, `list_dispatch_ledger`) are **not edited**. Both already run `SELECT * FROM dispatch_ledger …` through `_row_to_dict`, so they return `host` as soon as the column exists. That satisfies the Scope line "Modified readers: return it" with no code change. Stage 1's verify step proves it. `get_recent_ledger_summaries` selects three count columns on purpose and is not a row reader, so it stays as is.

## Stage 1: `host` column on `dispatch_ledger`

**Done when:** On a fresh temp DB and on a pre-existing `dispatch_ledger` without the column, `update_dispatch_ledger(<id>, host="DeepInfra")` succeeds and `get_dispatch_ledger(<id>)["host"] == "DeepInfra"`. `list_dispatch_ledger()` rows carry a `host` key. `update_dispatch_ledger(<id>, hots="x")` still raises `ValueError`.

1. In `src/data/database.py`, in `_ensure_dispatch_ledger_schema`, in the `CREATE TABLE dispatch_ledger (` statement, change the last column line from:
   ```python
                prompt_blocks     TEXT
   ```
   to:
   ```python
                prompt_blocks     TEXT,
                host              TEXT
   ```
2. In the same function, in the `migrations = [` list, add this as the last entry, directly after `("prompt_blocks",     "TEXT"),`:
   ```python
            # AST-1960: served LLM host for the batch. AST-1497: DDL only — old rows stay NULL, no backfill.
            ("host",              "TEXT"),
   ```
3. In `src/data/database.py`, change `_LEDGER_UPDATE_COLS` to add `"host"` to its last line:
   ```python
   _LEDGER_UPDATE_COLS = {
       "completed_at", "status",
       "total_processed", "total_passed", "total_failed", "total_errors",
       "agent_performance", "agent_note", "total_cost", "entity_cost", "prompt_blocks",
       "batch_size", "host",
   }
   ```
4. In the module docstring line `- dispatch_ledger — Dispatcher run history (save/update/get/list_dispatch_ledger).`, change it to:
   ```
   - dispatch_ledger — Dispatcher run history incl. served LLM host (save/update/get/list_dispatch_ledger).
   ```
5. Verify:
   - `python3 -m py_compile src/data/database.py`
   - Fresh DB:
     ```bash
     ASTRAL_DB_DIR=$(mktemp -d) python3 -c "
     from src.data import database as d
     d.save_dispatch_ledger('b1', 't', 'c', '2026-10-04 00:00:00')
     d.update_dispatch_ledger('b1', host='DeepInfra')
     assert d.get_dispatch_ledger('b1')['host'] == 'DeepInfra'
     assert 'host' in d.list_dispatch_ledger()[0]
     try:
         d.update_dispatch_ledger('b1', hots='x'); raise SystemExit('typo accepted')
     except ValueError:
         pass
     print('ok')"
     ```
     prints `ok`.
   - Migration path (a pre-existing table without `host` gets the column on ensure):
     ```bash
     T=$(mktemp -d) && python3 -c "
     import sqlite3, sys
     c = sqlite3.connect(sys.argv[1] + '/astral.db')
     c.execute('CREATE TABLE dispatch_ledger (batch_id TEXT PRIMARY KEY, task_key TEXT, candidate_id TEXT, entity_type TEXT, batch_size INTEGER, started_at TIMESTAMP, completed_at TIMESTAMP, status TEXT, total_processed INTEGER DEFAULT 0, total_passed INTEGER DEFAULT 0, total_failed INTEGER DEFAULT 0, total_errors INTEGER DEFAULT 0, agent_performance TEXT, agent_note TEXT, total_cost REAL DEFAULT 0.0, entity_cost REAL DEFAULT 0.0, prompt_blocks TEXT)')
     c.commit()" "$T" && ASTRAL_DB_DIR="$T" python3 -c "
     from src.data import database as d
     d.save_dispatch_ledger('b1', 't', 'c', '2026-10-04 00:00:00')
     d.update_dispatch_ledger('b1', host='DeepInfra')
     assert d.get_dispatch_ledger('b1')['host'] == 'DeepInfra'
     print('ok')"
     ```
     prints `ok`.

Commit: `code(AST-1960): stage 1 — host column on dispatch_ledger`

## Stage 2: `do_task` records the served host on the batch ledger row

**Done when:** A `do_task` under `log_batch_id = "b1"` whose `_send_to_server` returns `{"success": True, "host": "DeepInfra", ...}` calls `database.update_dispatch_ledger("b1", host="DeepInfra")` exactly once. With an Anthropic-direct server and no `host` key, the call is `update_dispatch_ledger("b1", host="Anthropic")`. A failed result, or no `log_batch_id`, makes no host write. A raising `update_dispatch_ledger` does not fail `do_task`. `git diff origin/dev...HEAD --stat -- src/core/dispatcher.py` is empty.

1. In `src/core/agent.py`, in `do_task`, directly after:
   ```python
       logger.debug("Response from _send_to_server: %s", result)
   ```
   and **before** `result["runtime_prompt"] = runtime_prompt`, insert:
   ```python
       # AST-1960: served host onto the active batch's ledger row — dispatcher batch, or the hop row
       # _open_run_next_hop_ledger set log_batch_id to. Successful calls only: a call that never reached
       # a host carries the server label, which must not overwrite the real host a sibling call wrote.
       ledger_batch_id = log_batch_id.get()
       if ledger_batch_id and result.get("success"):
           # Anthropic-direct results carry no host; that server is its own host, so its label stands in.
           host = result.get("host") or get_llm_server(server_id)["label"]
           logger.debug("Calling database.update_dispatch_ledger: [batch_id=%s, host=%s]", ledger_batch_id, host)
           try:
               # Off the loop like the agent_data writes: a locked DB must not stall provider timers (AST-1842).
               await asyncio.to_thread(database.update_dispatch_ledger, ledger_batch_id, host=host)
           except Exception:
               # The paid call already succeeded; a ledger hiccup must not turn it into a failure.
               logger.exception(
                   "%s | %s\n  Ledger host write failed for batch %s\n  Continuing without the host on that ledger row",
                   index or "-",
                   task_key,
                   ledger_batch_id,
               )
   ```
   `asyncio`, `database`, `get_llm_server`, `log_batch_id` and `logger` are already in scope in `agent.py`. Add no imports.

   ⚠️ **Decision — write on success only.** The Scope says "after each call it writes the result's host". Options considered: (a) write after every call; (b) write only when a response came back (`api_response is not None`); (c) write only on `success`. (a) is rejected: AST-1959's exception and failed-probe results carry the server label (`"OpenRouter"`), so a 429 on the locked host would overwrite `"DeepInfra"` with `"OpenRouter"` and break UAT AC 2 ("the batch's `dispatch_ledger` row shows it"). (b) is truthful but depends on stub shapes. Most existing `test_agent.py` stubs return `api_response: None` even on success, so AC 1's test would be fragile. (c) is chosen: every successful call in a locked batch shares one host, so the row ends up with the batch's host. A batch where every call fails leaves `host` NULL, which is accurate because nothing was served.

   ⚠️ **Decision — `log_batch_id.get()`, not the local `batch_id`.** The Scope names "the `dispatch_ledger` row for `log_batch_id`". Inside a chain hop, `_open_run_next_hop_ledger` has already set `log_batch_id` to the hop id, so this is the same value as the local `batch_id` and covers both kinds of row (parent As-built facts).

   ⚠️ **Decision — one write per successful call, no "already set" check.** Concurrent calls in a batch each write the same host. Skipping repeat writes would be an optimization this ticket doesn't ask for.
2. Verify:
   - `python3 -m py_compile src/core/agent.py src/data/database.py`
   - `python3 -c "import src.core.agent"` exits 0
   - `git diff origin/dev...HEAD --stat -- src/core/dispatcher.py` prints nothing
   - `git diff origin/ftr/AST-1954-host-probe...HEAD --stat -- src/external src/utils` prints nothing
   - `python3 -m pytest tests/component/core/test_agent.py tests/component/data/database/test_dispatch_ledger.py -q` passes on the existing (pre-Betty) tests. A failure that comes only from the new host write is not fixed in `tests/`. Record it under `## For Betty (qa-child)` below and continue to the commit. Any other failure: stop per the execution contract.

Commit: `code(AST-1960): stage 2 — do_task records served host on the batch ledger row`

## For Betty (`qa-child`)

- `TestAst531RunNextHopLedger` (and any other fixture that collects every `update_dispatch_ledger` call into a list) now sees one extra `(hop_batch_id, {"host": …})` entry per successful hop, ahead of the finalize update. Assertions that index `updates[0]` or count updates need to account for it.
- AC 1 check: under a `log_batch_id` with a saved ledger row on a temp DB, stub `_send_to_server` to return `success: True` with `host: "DeepInfra"`; then `get_dispatch_ledger(<id>)["host"] == "DeepInfra"`.
- AC 1 direct check: route to the `anthropic` server and stub a success result with no `host` key; the row's host is `"Anthropic"` (`LLM_SERVER_CONFIG["anthropic"]["label"]`).
- Build result (Stage 2 verify): `TestAst531RunNextHopLedger::test_two_hop_chain_creates_distinct_ledger_rows` now fails at `assert len(updates) == 2` (two host writes join the two finalize updates). This is the only new failure. The other 40 failures in `test_agent.py` fail the same way on the pre-Stage-2 tree and are unrelated to this diff. `test_dispatch_ledger.py` passes.

## Out of scope (do not touch)

- `src/core/dispatcher.py`: the host reaches the ledger through `agent.py` (parent As-built facts; AC 5).
- `src/external/llm_compat.py`, `src/external/openrouter.py`, `src/utils/config.py`, `src/utils/logging.py`: AST-1959 (Hedy).
- `run_adhoc` / workbench Test (`_run_workbench_*` wrapper in `agent.py`): not `do_task`, and not in this ticket's Scope.
- Any UI or API surface for the new column.
- `tests/**`, `docs/test-bible/**`: Betty.

## Execution contract

Run stages in order and steps in order. Do not add files, helpers, imports or dependencies beyond this doc. If a step is ambiguous, the code has drifted from the anchors quoted above, or a verify step fails when executed literally, stop and comment on the parent AST-1954 using the `🛑 Stage N blocked:` format. Each stage ends in one `code(AST-1960): …` commit on the epic worktree, published with `git push origin HEAD:sub/AST-1954/AST-1960-ledger-host`.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1960
**Overall:** APPROVED
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Publish ref:** `sub/AST-1954/AST-1960-ledger-host` @ `a0b5d2fdff1ee6fd4737947eb1593ae06f3c4e19`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-processing | A | | |
| stat.logging.debug | A | | |

## Traceability

1 → Stage 1 (`host` DDL + `_LEDGER_UPDATE_COLS`) · Stage 2 (`do_task` write under `log_batch_id`) · Betty AC 1 stubs · parent epic functional item 5 (ledger host) → Stages 1–2 · 2 → UAT gate (live `anticipate_scan`; depends on AST-1959 probe/lock + this write — no build stage, Susan at parent UAT)

## Findings

### discuss

- **Location:** Plan Files Changed decision (readers)
- **Finding:** Ticket Scope says “Modified readers: return it” while Stage 1 edits schema and `_LEDGER_UPDATE_COLS` only. Plan argues `SELECT *` + `_row_to_dict` already expose new columns once migrated, with verify proving `get_dispatch_ledger` / `list_dispatch_ledger`.
- **Recommendation:** Accept for build; if Technical scope was meant to require explicit reader diffs, Archie can clarify wording — behavior is covered.

- **Location:** Stage 2 — ledger write failure path
- **Finding:** `logger.exception` on a failed host write is appropriate operator signal but `stat.logging.error` is not on this child’s Canon Scope.
- **Recommendation:** Optional Canon Scope add at Discussion for parity with other agent paths; not blocking — pattern matches existing “swallow DB hiccup, don’t fail the paid call” intent (AST-1842 comment in plan).

### acceptable

- **Location:** Plan structure — no `## Self-assessment`
- **Finding:** Two stages, explicit decisions (success-only write, hop `log_batch_id`, Betty hop-fixture note), estimate confirm present.
- **Recommendation:** None blocking.

- **Location:** Stage 2 verify / `## For Betty`
- **Finding:** Pre-Betty pytest may fail on extra `update_dispatch_ledger` calls in hop ledger tests; plan directs record-not-fix in build.
- **Recommendation:** None blocking.

- **Location:** Boundaries / verify
- **Finding:** Empty diffs required for `dispatcher.py` and `src/external` + `src/utils` vs `origin/ftr/AST-1954-host-probe` keep this child off AST-1959’s surface.
- **Recommendation:** None.

context_tokens≈48000

Slim upshot: `[plan-rubric] PROCEED (Commit: a0b5d2fdf) ledger host plan solid`

## Review

- **Publish ref:** `sub/AST-1954/AST-1960-ledger-host`
- **Build commits:** `edfe7c643` (stage 1), `f576947c7` (stage 2)
- **For Betty (`qa-child`):** see `## For Betty (qa-child)` above. One expected break (`TestAst531RunNextHopLedger` update count); 40 unrelated pre-existing `test_agent.py` failures.

## Radia review

[code-rubric]
**Ticket:** AST-1960
**Publish ref:** `c432cea62f04c873447f8400fb55dc911c19e40b` (`origin/sub/AST-1954/AST-1960-ledger-host`)
**Corpus:** `bd68954dc854ca80fca1fc391821dff9ff288a7a` (canon tree at publish tip; `docs/canon-index.md` absent on ref — ids resolved from `canon/directives/active/*.md`)
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-processing | A | | |
| stat.logging.debug | A | | |

## Column diff vs plan stage

(aligned) — Joan graded both **A**; code review matches.

## Frame diff

(none) — AC 1 is covered by `TestAst1960LedgerHost` and `TestAst1960LedgerHostColumn`; AC 2 remains parent UAT (live `anticipate_scan`), not a build-stage checkbox.

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Location:** Three-dot diff `origin/dev...origin/sub/AST-1954/AST-1960-ledger-host`
- **Finding:** **Sibling product + test carry from AST-1959** (`src/external/llm_compat.py`, `src/external/openrouter.py`, `src/utils/config.py`, `src/utils/logging.py`, plus matching component tests and test-bible rows). AST-1960’s own product delta vs `origin/ftr/AST-1954-host-probe` is only `src/core/agent.py` (+19) and `src/data/database.py` (+6/−3).
- **Recommendation:** Expected stacked sub-branch shape; score AST-1960 against its two citations on the combined tip, not as scope creep.

- **Location:** `src/core/agent.py` — ledger write failure path
- **Finding:** `logger.exception(...)` on failed `update_dispatch_ledger` (not gated debug). `stat.logging.error` is not on this ticket’s frozen list; Joan flagged the same at plan as optional Canon Scope parity.
- **Recommendation:** No change required for this review; Archie may add `stat.logging.error` at Discussion if operator signal should be canon-scored on future agent DB paths.

- **Location:** Linear Scope vs plan “readers” decision
- **Finding:** No explicit reader diffs; `SELECT *` + `_row_to_dict` exposes `host` after DDL/migration — verified in `test_dispatch_ledger.py::TestAst1960LedgerHostColumn`.
- **Recommendation:** Accept behavior; wording on the ticket is descriptive, not a missing implementation.

## What's solid

- **Stage 1:** `dispatch_ledger` CREATE + migration add `host TEXT`; `_LEDGER_UPDATE_COLS` includes `"host"`; dynamic `UPDATE` bind tuple (`vals = list(kwargs.values()) + [batch_id]`) stays consistent with column count.
- **Stage 2:** After `_send_to_server`, writes `host` only when `log_batch_id` is set and `result["success"]`; uses `result.get("host") or get_llm_server(server_id)["label"]` for Anthropic-direct; `asyncio.to_thread` for the DB write; failures swallowed without failing the paid call.
- **Batch-processing:** Host is persisted on the ledger row keyed by the active `log_batch_id` (dispatcher batch or hop row), with no new batch id or claim/release logic.
- **Debug:** Ungated `logger.debug("Calling database.update_dispatch_ledger: [batch_id=%s, host=%s]", ...)` before the write; no new logging in `src/data/`.
- **Boundaries:** `src/core/dispatcher.py` unchanged vs `origin/dev`; vs `origin/ftr/AST-1954-host-probe`, no edits under `src/external` or `src/utils`.

## Recommended actions (downstream only — not executed in this session)

1. Chuckles: append artifact, `docs(AST-1960): Radia review — clean`, push `sub/AST-1954/AST-1960-ledger-host`, post slim upshot `--as radia`, **Review Posted**.
2. datt: **PROCEED** → **User Testing** (parent UAT still owns AC 2 live lock).

```
[code-rubric] PROCEED (Commit: c432cea62) ledger host on batch row
```
