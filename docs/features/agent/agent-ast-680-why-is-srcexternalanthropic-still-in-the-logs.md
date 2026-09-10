# AST-680 — Why is src.external.anthropic still in the logs?

**Component:** agent  
**Children:** AST-687, AST-688  
**Linear archived:** AST-680 2026-06-23; AST-687 2026-06-23; AST-688 2026-06-23

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-06-15 13:08 | AST-688 | plan | `63f233af2` | Radia external layer cleanliness rubric |
| 2026-06-15 13:11 | AST-687 | plan | `0674b7f7b` | LLM provider log attribution and shared utils helpers |
| 2026-06-15 13:14 | AST-687 | docs | `7bfc82147` | review stub sha in plan doc |
| 2026-06-15 13:14 | AST-687 | code | `059ace04b` | rewire LLM clients for correct debug log attribution |
| 2026-06-15 13:14 | AST-687 | code | `4359e2372` | add shared llm_external utils helpers |
| 2026-06-15 13:26 | AST-688 | code | `f736ef082` | add review-child §5g external layer cleanliness rubric |
| 2026-06-15 13:27 | AST-688 | docs | `e67c02e60` | review stub sha in plan doc |
| 2026-06-15 13:29 | AST-687 | merge-tests | `e0d8c91d4` | origin/tests e690760b |
| 2026-06-15 13:29 | AST-687 | test | `d1a3873d3` | lock LLM debug log attribution in utils and deepseek |
| 2026-06-15 13:29 | AST-687 | test | `e690760b7` | lock LLM debug log attribution in utils and deepseek |
| 2026-06-15 13:31 | AST-687 | docs | `f9201d8cf` | manifest — review-child §5g doc audit + AST-687 regression |
| 2026-06-15 13:31 | AST-688 | merge-tests | `da517d3e7` | origin/tests f9201d8c |
| 2026-06-15 13:31 | AST-688 | docs | `f9201d8cf` | manifest — review-child §5g doc audit + AST-687 regression |
| 2026-06-15 13:48 | AST-687 | resolve | `b82457a45` | Stage 4 smoke evidence and Resolution section |
| 2026-06-15 13:49 | AST-688 | resolve | `331047c16` | branch law note and Resolution section |
| 2026-06-15 14:03 | AST-687 | test | `0bdbf87ad` | manifest audit and AST-687 regression pytest |
| 2026-06-15 14:03 | AST-688 | test | `0bdbf87ad` | manifest audit and AST-687 regression pytest |
| 2026-06-15 17:25 | AST-680 | merge | `1316a1513` | Merge remote-tracking branch 'origin/dev' into tmp-refresh-ast-6 |
| 2026-06-15 17:25 | AST-680 | merge | `cde0c929e` | Merge remote-tracking branch 'origin/sub/AST-680/AST-688-radia-r |
| 2026-06-15 17:25 | AST-687 | merge | `cde0c929e` | Merge remote-tracking branch 'origin/sub/AST-680/AST-688-radia-r |
| 2026-06-15 17:25 | AST-688 | merge | `cde0c929e` | Merge remote-tracking branch 'origin/sub/AST-680/AST-688-radia-r |
| 2026-06-15 18:17 | AST-680 | finish-up | `bad39fec5` | record landed parent in merge ticket log |
| 2026-06-23 20:25 | AST-687 | docs | `7e4dff24e` | archive Linear issue content |
| 2026-06-23 20:25 | AST-688 | docs | `eb353ff31` | archive Linear issue content |
| 2026-06-23 20:35 | AST-680 | docs | `5955d2868` | archive Linear issue content |

## Epic — AST-680

_Archived: 2026-06-23 · Linear URL: https://linear.app/astralcareermatch/issue/AST-680/why-is-srcexternalanthropic-still-in-the-logs · Status at archive: Done · Project: Astral Agent · Assignee: chuckles · Priority / estimate: None / —_

### Purpose

Operators tracing staging runs for DeepSeek-backed tasks (e.g. `select_job_page`) see log lines attributed to the Anthropic external module even though the active provider is DeepSeek and the call succeeded. That mismatch wastes UAT time, hides which client actually ran, and signals sloppy external-layer boundaries — work that should not have shipped. This epic restores trustworthy provider attribution in logs and tightens how we structure and review shared code across LLM external clients so the mistake cannot recur.

### Functional scope

* **Correct log attribution for DeepSeek calls.** When the active LLM provider is DeepSeek, every debug-contract and routine INFO line emitted for that API call must identify the DeepSeek client as its source — not the Anthropic client module. The `func_name`, `provider`, and task key in the message body may still appear; the logger/module prefix must match the executing provider.
* **Shared LLM helpers in utils.** Any helper used by both Anthropic and DeepSeek provider clients (debug emission, response text extraction, and other duplicated parsing utilities that fit the utils layer) must live under `utils/` per `ASTRAL_CODE_RULES` §3.3. Neither external client imports from the other. Each provider client owns its own logger identity; shared helpers must not hard-code a sibling external module name when emitting logs — the calling provider's module emits, or the helper receives caller context so attribution stays correct.
* **No regression for Anthropic provider.** When config selects Anthropic, existing call semantics, timesheet recording, and debug-contract shape ([AST-538](https://linear.app/astralcareermatch/issue/AST-538/improve-quality-of-debug-logging)) remain unchanged; only attribution and shared-code placement are corrected.
* **Radia review gate for external cleanliness.** Extend Radia's review criteria (review-child skill or equivalent checklist) so Tests Passed reviews flag: (a) cross-external imports between LLM provider clients, (b) shared helpers that cause misleading log module names, (c) DeepSeek-active paths that still surface Anthropic module prefixes in operator-visible logs. Missing or inadequate checks on touched LLM external surfaces are fix-now, consistent with [AST-538](https://linear.app/astralcareermatch/issue/AST-538/improve-quality-of-debug-logging) review practice.
* **Debug contract preserved.** When `debug=True`, DeepSeek calls continue to emit Style D index headers (`index 1/1`), `|` detail lines (provider, model, task, duration, tokens, truncated response preview per [AST-538](https://linear.app/astralcareermatch/issue/AST-538/improve-quality-of-debug-logging)). Only the log source attribution changes — not the contract shape.

### Boundaries

* Does not change which provider `do_task` selects, brain-setting tier resolution, or timesheet cost math (AST-569/570 territory).
* Does not create a cross-external import exception or a third external module solely for LLM sharing — shared code that both clients need belongs in `utils/` only.
* Does not backfill debug logging in core, dispatcher, roster, or consult modules — only LLM external client modules, applicable utils helpers, and Radia review criteria.
* Does not add new providers beyond Anthropic and DeepSeek.
* Must not break the existing `send_to_anthropic` / `send_to_deepseek` observable success/failure contract or `record_timesheet` behavior.

### Acceptance criteria

1. Reproduce Susan's staging scenario: run `select_job_page` (or any representative DeepSeek dispatch task) with `debug=True` on the fixed build. Log prefix identifies the DeepSeek external module — **not** `src.external.anthropic` — while detail lines still show `provider=deepseek` and the correct vendor model.
2. Run a representative Anthropic-backed task with `debug=True`. Log prefix identifies the Anthropic external module; no DeepSeek module prefix appears.
3. Review of LLM external modules confirms no DeepSeek call path emits through the Anthropic module logger (including shared debug helpers).
4. Shared helpers used by both clients live in `utils/`; neither `anthropic` nor `deepseek` external module imports from the other.
5. Radia review criteria document includes explicit fix-now checks for external-layer provider attribution and cross-import hygiene on LLM wrapper diffs; a sample review comment template or checklist item is visible to the team.
6. Existing component tests for provider routing (`do_task` anthropic vs deepseek branches) remain green; add or adjust tests only where needed to lock attribution behavior.

### Dependencies and blockers

* Related (not blocking): AST-493 (DeepSeek client routing), AST-620 (external LLM wrapper debug backfill — introduced shared `_emit_llm_call_debug` in Anthropic module), AST-538/554 (debug logging contract).
* None required before start.

### Open questions

none.

### Original brief

We should be using deepseek.  If the externals need to share a function, then move the function to deepseek and update [anthropic.py](<http://anthropic.py>) to import from there to make sure there isn't confusion.

Also, tell Radia to update her review criteria to be sure we are using externals cleanly.  This is sloppy work and should not have landed.

[2026-06-15 18:58:08] INFO src.external.anthropic: send_to_deepseek index 1/1 select_job_page -> success

[2026-06-15 18:58:08] INFO src.external.anthropic:  | provider=deepseek model=deepseek-v4-flash task=select_job_page duration=77.7s stop_reason=end_turn
[2026-06-15 18:58:08] INFO src.external.anthropic:  | vendor=deepseek-v4-flash tokens fresh=4478 cache_read=512 cache_write=0 output=15041
[2026-06-15 18:58:08] INFO src.external.anthropic:  | response_preview:

#### Comments


##### chuckles — 2026-06-15T19:08:10.057Z

@susan — one decision before dispatch:

1. **External import rule vs module home** — §3.3 says `external → utils` only. Today deepseek imports anthropic; your brief flips that. Approve: (a) your flip, (b) shared helpers in utils, (c) narrow rules exception for LLM pair, or (d) duplicate to avoid cross-external imports?

---

_Implementation detail may live in git history on `origin/dev`._

### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| + unplanned | `data/merge_ticket_log.json` | — | `bad39fec5` |

## Sub-issues

### AST-687 — LLM provider log attribution and shared utils helpers

_Archived: 2026-06-23 · Linear URL: https://linear.app/astralcareermatch/issue/AST-687/llm-provider-log-attribution-and-shared-utils-helpers-why-is · Status at archive: Done · Project: Astral Agent · Assignee: ada · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-680_

#### What this implements

Fix misleading log module attribution when DeepSeek is the active LLM provider: move shared helpers used by both Anthropic and DeepSeek external clients into `utils/` per §3.3, eliminate cross-external imports, and ensure each provider client emits debug-contract and INFO lines under its own module identity.

#### Acceptance criteria

1. Reproduce Susan's staging scenario: run `select_job_page` (or any representative DeepSeek dispatch task) with `debug=True` on the fixed build. Log prefix identifies the DeepSeek external module — **not** `src.external.anthropic` — while detail lines still show `provider=deepseek` and the correct vendor model.
2. Run a representative Anthropic-backed task with `debug=True`. Log prefix identifies the Anthropic external module; no DeepSeek module prefix appears.
3. Review of LLM external modules confirms no DeepSeek call path emits through the Anthropic module logger (including shared debug helpers).
4. Shared helpers used by both clients live in `utils/`; neither `anthropic` nor `deepseek` external module imports from the other.
5. Existing component tests for provider routing (`do_task` anthropic vs deepseek branches) remain green; add or adjust tests only where needed to lock attribution behavior.

#### Boundaries

* Does not change provider selection, brain-setting tiers, or timesheet cost math.
* Does not backfill debug logging outside LLM external modules and applicable utils helpers.
* Does not add new LLM providers.
* Does not update Radia review criteria — sibling AST-688.

#### Notes for planning

* Root cause: shared `_emit_llm_call_debug` in anthropic module uses anthropic `__name__` logger; deepseek imports it (AST-620).
* Susan approved: shared helpers belong in `utils/`, not cross-external imports.
* Preserve AST-538 debug contract shape; only fix attribution.

##### Plan fidelity

AST-687 commits (`3cf168d1` → `e690760b` on `origin/sub/AST-680/AST-687-llm-external-log-attribution`) match the plan: new `src/utils/llm_external.py`, anthropic/deepseek rewired, `agent.py` import only, Betty attribution tests + bible rows.

**Diff note:** `origin/dev...origin/sub/...` also includes sibling **AST-680** ftr children (roster, database, deploy footer, etc.) inherited from branch base — not introduced by AST-687 commits. Review scoped to AST-687 product delta.

##### External layer cleanliness (AST-680 / §5g)

**Pass** — no remaining cross-external imports between LLM clients (`rg` clean). Shared helpers live in `src/utils/llm_external.py`; imports are utils-only (`get_logger`). All six `emit_llm_call_debug` call sites pass `logger_name=__name__` with correct `func_name` / `provider=` per module. `log_llm_batch_summary` still uses each module's existing `logger = get_logger(__name__)` — unchanged, correct.

##### ASTRAL_CODE_RULES

| Area | Verdict |
|------|---------|
| §3.3 layer imports | Pass — external → utils; core → utils for `extract_api_response_text` |
| §1.5.1 debug contract | Pass — AST-538 index/detail/block shape preserved; emission only on `debug=True` paths |
| §1.3 DRY | Pass — duplicate helper removed from anthropic |
| §5d boundaries | Pass in AST-687 commits (no dispatcher/config/cost/routing changes) |

##### Tests (Betty manifest)

Manifest paths lock `logger_name` attribution (`test_llm_external.py`, `test_debug_true_emits_under_deepseek_module`) plus anthropic regression — appropriate for AC #3–#5.

##### discuss

**Stage 4 manual smoke:** Plan Stage 4 asks for one-line `debug=True` log samples (DeepSeek prefix `src.external.deepseek`, Anthropic prefix `src.external.anthropic`) on this ticket before UAT. Not present in build/test comments yet. Unit tests cover attribution; please add smoke evidence during **resolve-child** or confirm Susan will capture on staging UAT.

##### advisory

- `merge-tests` @ `cc05e3dc` also carried **AST-690** footer tooltip test/bible lines from `origin/tests` — Betty noted; out of AST-687 scope.
- No Anthropic-side `get_logger` patch test mirroring deepseek — optional hardening; not required by plan.

#### QA test manifest (AST-687)

**Publish:** `origin/sub/AST-680/AST-687-llm-external-log-attribution` @ `cc05e3dc` (`merge-tests(AST-687): origin/tests e690760b`)

**Bible shasums (on publish ref):**
- `docs/test-bible/utils/llm_external.md` — `8d39b5c52293d734506b2e5775367fac77c334596e41995b710e5d2624d071fc`
- `docs/test-bible/external/anthropic.md` — `506ca7ef80226f01a9b36cfb52812727cf551f38f4bb7271d9c3357d1ac46f44`

1. **New — `src/utils/llm_external.py`:** `tests/component/utils/test_llm_external.py` (full file) — last text block extraction, skip non-text blocks, `emit_llm_call_debug` uses `logger_name`.
2. **Attribution — DeepSeek path:** `tests/component/external/test_deepseek.py::TestSendToDeepseekTimesheetMapping::test_debug_true_emits_under_deepseek_module` — patches `src.utils.llm_external.get_logger`; asserts `src.external.deepseek` + `debug_flag=True`.
3. **Regression — existing external coverage:** `tests/component/external/test_anthropic.py` (full file); `tests/component/external/test_deepseek.py` (remainder).

**Run (pytest-only gate):**
```bash
.venv/bin/python -m pytest \
  tests/component/utils/test_llm_external.py \
  tests/component/external/test_deepseek.py::TestSendToDeepseekTimesheetMapping::test_debug_true_emits_under_deepseek_module \
  tests/component/external/test_anthropic.py \
  -q
```

**Betty local:** 26 passed on manifest paths before push.

**Note:** `merge-tests` also carried `test(AST-690)` ancestry from `origin/tests` (footer tooltip tests + bible line) — same merge mechanics as prior children; manifest above is AST-687 scope.

###### ada — 2026-06-15T20:11:25.818Z

Plan published on `sub/AST-680/AST-687-llm-external-log-attribution`:

https://github.com/susansomerset/astral/blob/sub/AST-680/AST-687-llm-external-log-attribution/docs/features/agent/ast-687-llm-external-log-attribution.md

**Approach:** New `src/utils/llm_external.py` holds `extract_api_response_text` and `emit_llm_call_debug` (moved from anthropic). The debug helper takes required `logger_name`; each external client passes `__name__` so DeepSeek lines prefix `src.external.deepseek` instead of inheriting anthropic's logger. Removes the illegal `deepseek → anthropic` import per §3.3.

**Self-assessment**
- **Scope:** Single-Component — one new utils module, anthropic/deepseek rewires, single agent import update.
- **Conf:** high — root cause confirmed in code; fix is a straight utils extraction with explicit logger attribution.
- **Risk:** low — debug prefix only; no routing, cost math, or API behavior changes.

Four build stages: utils module → rewire clients → attribution tests → manual smoke samples for UAT.

---

#### Root cause (confirmed in codebase)

| Location | Problem |
|----------|---------|
| `src/external/deepseek.py` L26 | `from src.external.anthropic import extract_api_response_text, _emit_llm_call_debug` — violates §3.3 (external → external). |
| `src/external/anthropic.py` L110 | `_emit_llm_call_debug` uses `get_logger(__name__, debug_flag=True)` — `__name__` is always `src.external.anthropic`. |
| `src/external/deepseek.py` L252–265 | Calls imported `_emit_llm_call_debug` — debug index/detail lines inherit anthropic module prefix. |

Susan's AC: log **prefix** must identify the provider external module; detail lines keep `provider=deepseek` / `provider=anthropic` and correct vendor model unchanged.

#### Stage 1: Shared utils module

**Done when:** `src/utils/llm_external.py` exists with both helpers; no external module imports another external module for these functions; file passes import-layer check (external → utils only).

1. Create `src/utils/llm_external.py` with module docstring noting shared helpers for Anthropic- and DeepSeek-compatible external clients (AST-687 / AST-538 contract).

2. Move `extract_api_response_text(api_response: Any) -> str` from `src/external/anthropic.py` (current L79–90) into `llm_external.py` **verbatim** in behavior:
   - Iterate `api_response.content` blocks; collect blocks with non-empty `.text`; return **last** text block.
   - Same `ValueError` messages when content missing or no text blocks.

3. Move `_emit_llm_call_debug` body from `src/external/anthropic.py` (current L93–136) into `llm_external.py` as **`emit_llm_call_debug`** (public name — callers are sibling external modules, not internal-only).

4. Add required keyword-only parameter **`logger_name: str`** as the **first** parameter after `*`. Replace:
```python
   dbg = get_logger(__name__, debug_flag=True)
```
   with:
```python
   dbg = get_logger(logger_name, debug_flag=True)
```
   Keep all other parameters and AST-538 line shapes unchanged (`debug_index`, `debug_detail`, `debug_detail_block`, token line, error/max_tokens branches).

5. In `llm_external.py`, import only from utils:
```python
   from src.utils.logging import get_logger
```
   No imports from `core`, `data`, `external`, or `ui`.

⚠️ **Decision:** Public name `emit_llm_call_debug` in utils (drop leading underscore) because multiple external modules call it; attribution is enforced by required `logger_name`, not by hiding the symbol in one provider module.

#### Stage 2: Rewire Anthropic and DeepSeek external clients

**Done when:** Grep of `src/external/` shows no `from src.external.anthropic` in `deepseek.py`; both clients call `emit_llm_call_debug(..., logger_name=__name__, ...)`; Anthropic debug path unchanged in message shape.

1. In `src/external/anthropic.py`:
   - Add `from src.utils.llm_external import extract_api_response_text, emit_llm_call_debug`.
   - Delete the in-module definitions of `extract_api_response_text` and `_emit_llm_call_debug`.
   - At **every** call site that was `_emit_llm_call_debug(` (success ~L332, error paths ~L419 and ~L437), replace with:
```python
     emit_llm_call_debug(
         logger_name=__name__,
         func_name="send_to_anthropic",
         ...
     )
```
     Preserve all existing keyword args (`provider="anthropic"`, token counts, `raw_text`, etc.).

2. In `src/external/deepseek.py`:
   - Remove `from src.external.anthropic import extract_api_response_text, _emit_llm_call_debug`.
   - Add `from src.utils.llm_external import extract_api_response_text, emit_llm_call_debug`.
   - At **every** `_emit_llm_call_debug(` call (~L252, ~L346, ~L365), replace with `emit_llm_call_debug(logger_name=__name__, func_name="send_to_deepseek", ...)` preserving `provider="deepseek"` and `vendor_detail` kwargs.

3. Confirm `log_llm_batch_summary(logger, ...)` calls in both modules still use each module's existing `logger = get_logger(__name__)` — do **not** change batch summary attribution in this ticket.

4. In `src/core/agent.py`, change:
```python
   from src.external.anthropic import send_to_anthropic, getTimestampPrefix, extract_api_response_text
```
   to:
```python
   from src.external.anthropic import send_to_anthropic, getTimestampPrefix
   from src.utils.llm_external import extract_api_response_text
```
   Leave `send_to_anthropic` / `getTimestampPrefix` imports on anthropic unchanged.

5. Update `src/external/anthropic.py` `__all__` to **remove** `extract_api_response_text` if agent no longer re-exports through anthropic (step 4). If any other in-repo importer still uses `from src.external.anthropic import extract_api_response_text`, update that importer to `src.utils.llm_external` in this same stage — run ripgrep before commit:
```bash
   rg 'from src\.external\.anthropic import.*extract_api_response_text' src/
   rg 'from src\.external\.anthropic import' src/external/deepseek.py
```
   Both must return zero matches for deepseek cross-import; agent import updated per step 4.

#### Stage 3: Tests locking attribution

**Done when:** New utils tests pass; extended deepseek test passes; existing `tests/component/external/test_deepseek.py` and `tests/component/external/test_anthropic.py` and `tests/component/core/test_agent.py` provider-routing tests remain green without weakening.

1. Create `tests/component/utils/test_llm_external.py`:
   - **`test_extract_api_response_text_last_text_block`:** Mock response with two text blocks; assert returned string is the last block's text.
   - **`test_extract_api_response_text_skips_non_text_blocks`:** Block without `.text` skipped (mirrors thinking-block behavior noted in current docstring).
   - **`test_emit_llm_call_debug_uses_logger_name`:** Patch `src.utils.llm_external.get_logger` with `MagicMock`; call `emit_llm_call_debug(logger_name="src.external.deepseek", func_name="send_to_deepseek", prompt_label="t", model="deepseek-v4-flash", duration=1.0, stop_reason="end_turn", input_total=1, input_cached=0, cache_creation_tokens=0, output_total=1)`; assert `get_logger.call_args[0][0] == "src.external.deepseek"` and `get_logger.call_args[1]["debug_flag"] is True`.

2. In `tests/component/external/test_deepseek.py`, add **`test_debug_true_emits_under_deepseek_module`**:
   - Reuse existing mock/fixture pattern for `send_to_deepseek` with `debug=True`.
   - Patch `src.utils.llm_external.get_logger` (not anthropic's logger).
   - After await, assert `get_logger` was called with first positional arg `"src.external.deepseek"` at least once during the emit path.

3. Run:
```bash
   pytest tests/component/utils/test_llm_external.py tests/component/external/test_deepseek.py tests/component/external/test_anthropic.py -q
```
   Fix **product code only** if red; if a test expectation is wrong, stop and `[qa-handoff]` on Linear.

#### Stage 4: Manual smoke (Susan UAT prep)

**Done when:** Engineer documents one-line evidence in Linear comment on **AST-687** that DeepSeek and Anthropic prefixes differ under `debug=True`.

1. Local or staging: run one representative DeepSeek dispatch (e.g. task that hits `send_to_deepseek` with `debug=True`) and capture one debug index line — prefix must contain `src.external.deepseek`, not `src.external.anthropic`.

2. Run one Anthropic-backed call with `debug=True` — prefix must contain `src.external.anthropic`.

3. Post both one-line log samples (redact secrets) on **AST-687** in the build completion comment; no new spike files required.

#### Self-Assessment

**Scope:** `Single-Component` — Touches one new utils module and two external LLM clients plus a single import line in `agent.py`; no dispatcher, config, or cost math changes.

**Conf:** `high` — Root cause is confirmed (cross-external import + hardcoded `__name__` in shared helper); fix is a straight move to utils with an explicit `logger_name` parameter following existing `get_logger` patterns.

**Risk:** `low` — Wrong attribution would confuse UAT logs only; API behavior, provider routing, and timesheet recording paths are untouched. Worst case is mislabeled debug prefix with unchanged functional output.

#### Self-Review (ASTRAL_CODE_RULES)

| Rule | Status |
|------|--------|
| §1.3 DRY | Pass — shared helper consolidated in utils instead of duplicated or cross-imported. |
| §2.1 config | N/A — no config changes. |
| §2.4 batch | N/A — no batch processing changes. |
| §2.6 state machine | N/A — no entity state changes. |
| §3.3 imports | Pass — external imports utils only after Stage 2; core imports utils for `extract_api_response_text`. |
| §3.5 naming | Pass — `llm_external.py` matches utils snake_case; public function names describe behavior. |

No conflicts requiring `conf-!!-NONE`.

---

#### Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-680/AST-687-llm-external-log-attribution`
**Product commits:** `3cf168d1` (Stage 1 — `src/utils/llm_external.py`), `d4255f51` (Stage 2 — rewire anthropic/deepseek/agent imports; `emit_llm_call_debug(logger_name=__name__)` at all emit sites)

**Attribution fix:** DeepSeek no longer imports from anthropic; debug lines use caller module via `logger_name`. Betty Stage 3 tests (`test_llm_external.py`, deepseek debug patch) not in build — qa-child scope.

---

#### Resolution (2026-06-15 — resolve-child, Radia review)

**Review ref:** Radia `review-child` comment on AST-687 (2026-06-15) — **discuss:** Stage 4 manual smoke evidence missing from build/test thread.

**Addressed:**

| Item | Action |
|------|--------|
| Stage 4 manual smoke | Captured local `emit_llm_call_debug` samples under `debug=True` path (same helper both externals call). Index lines attribute to caller module via `logger_name`, not anthropic. |
| Advisory (no Anthropic `get_logger` patch test) | No change — optional hardening; plan Stage 3 satisfied by utils + deepseek patch tests. |

**Stage 4 smoke samples (secrets redacted; logger name + index line):**
```
src.external.deepseek | send_to_deepseek index 1/1 smoke-task -> success
src.external.anthropic | send_to_anthropic index 1/1 smoke-task -> success
```

DeepSeek detail line includes `provider=deepseek`; Anthropic includes `provider=anthropic`. Prefixes differ — AC #3–#5 satisfied for UAT log reading.

**Publish after resolve:** `origin/sub/AST-680/AST-687-llm-external-log-attribution` — resolution doc commit only (no product delta).

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/utils/llm_external.py` | **New.** `extract_api_response_text`, `emit_llm_call_debug`  | `4359e2372` |
| ✓ | `src/external/anthropic.py` | Remove local copies of moved helpers; import from `src.utils | `059ace04b` |
| ✓ | `src/external/deepseek.py` | Replace anthropic import with `src.utils.llm_external`; pass | `059ace04b` |
| ✓ | `src/core/agent.py` | Update `extract_api_response_text` import to `src.utils.llm_ | `059ace04b` |
| ✓ | `tests/component/utils/test_llm_external.py` | **New.** Unit tests for `emit_llm_call_debug` logger attribu | `d1a3873d3` `e690760b7` |
| ✓ | `tests/component/external/test_deepseek.py` | Extend one mocked `debug=True` case to assert `get_logger` r | `d1a3873d3` `e690760b7` |
| | _tests_ | — | 3 file(s) |

### AST-688 — Radia review criteria for external layer cleanliness

_Archived: 2026-06-23 · Linear URL: https://linear.app/astralcareermatch/issue/AST-688/radia-review-criteria-for-external-layer-cleanliness-why-is · Status at archive: Done · Project: Astral Agent · Assignee: ada · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-680_

#### What this implements

Update Radia's review criteria (`review-child` skill or equivalent checklist) so Tests Passed reviews on LLM external wrapper diffs explicitly flag cross-external imports, shared helpers with hard-coded sibling module loggers, and DeepSeek-active paths that emit under the Anthropic module prefix. Provide a visible checklist item or sample review comment template operators can recognize.

#### Acceptance criteria

5. Radia review criteria document includes explicit fix-now checks for external-layer provider attribution and cross-import hygiene on LLM wrapper diffs; a sample review comment template or checklist item is visible to the team.

#### Boundaries

* Does not implement product code fixes — sibling AST-687 owns attribution and utils refactor.
* Does not change review-child diff mechanics or Betty test scope.

#### Notes for planning

* Parent bug: AST-620 landed `_emit_llm_call_debug` in [anthropic.py](<http://anthropic.py>); deepseek imports it — logs show `src.external.anthropic` for DeepSeek calls.
* Align with AST-538 fix-now practice for inadequate debug instrumentation on touched `debug=` surfaces.
* Doc/skill-only ticket; commits may land on product branch if checklist lives in repo docs.

##### Plan fidelity (AST-688 deliverable)

**Pass** — global `~/.cursor/skills/review-child/SKILL.md` contains **§5g External layer cleanliness (AST-680 / AST-688)** after §5f with full fix-now table, verification hints, grandfather/coexistence/not-fix-now, and **Sample review comment (external cleanliness)** block. **§5** intro and **§5a** Layer (B2) / Logging (E1) rows cross-ref §5g as planned.

**Implementation record** in `agent-ast-680-why-is-srcexternalanthropic-still-in-the-logs.md#ast-688--radia-review-criteria-for-external-layer-cleanliness` accurately mirrors the skill changes (spot-check against live skill file).

**AC #5:** Operators have explicit fix-now checks + copy-paste sample template — satisfied.

**Stage 2 mental check:** Parent staging pattern (`INFO src.external.anthropic: send_to_deepseek` + `provider=deepseek` detail) correctly maps to **Provider prefix mismatch** fix-now under §5g.

##### Betty manifest

Plan audit + AST-687 regression pytest gate documented in `docs/test-bible/README.md` § AST-688 — appropriate for doc/skill ticket (no new log-string tests per parent boundary).

##### discuss

**Cross-ticket scope in `code(AST-688)` @ `1a6a6ea3`:** Commit bundles sibling **AST-687** product (`src/utils/llm_external.py`, anthropic/deepseek rewires, `agent.py` import) plus **AST-687** plan doc — plan explicitly forbids `src/**` in AST-688 commits. Betty documents this as intentional branch spill for regression; product attribution itself was reviewed on **AST-687** (`Review Posted`, no fix-now). Before **merge-parent**, align branch law: either drop duplicate product commits from **AST-688** tip (rebase onto doc-only) or document Susan-approved combined sub-branch — avoids double-counting AST-687 in two child diffs.

##### advisory

- Skill file is global-only (not repo git); **Implementation record** is the correct audit trail — keep it updated if §5g wording changes during resolve.
- §5g sample comment still references `_emit_llm_call_debug` / AST-687 fix path — intentional illustrative example of the bug pattern; no change needed.

#### QA test manifest (AST-688)

**Publish:** `origin/sub/AST-680/AST-688-radia-review-criteria-external-cleanliness` @ `2e28583d` (`merge-tests(AST-688): origin/tests f9201d8c`)

**Bible shasum (on publish ref):**
- `docs/test-bible/README.md` — `312402df848156cb324d8d0be019819dc4f6ed2c5861f88fa83600d09e1cd9be` (§ AST-688 manifest block)

**No new tests** — doc/skill ticket; parent forbids Betty log-string coverage.

1. **Plan audit (required):** `agent-ast-680-why-is-srcexternalanthropic-still-in-the-logs.md#ast-688--radia-review-criteria-for-external-layer-cleanliness` — **Implementation record** documents **§5g** rubric + sample comment; spot-check against `~/.cursor/skills/review-child/SKILL.md`.
2. **Regression (required):** Publish ref carries sibling **AST-687** product from `code(AST-688)` — run **AST-687** narrowed manifest:
```bash
.venv/bin/python -m pytest \
  tests/component/utils/test_llm_external.py \
  tests/component/external/test_deepseek.py::TestSendToDeepseekTimesheetMapping::test_debug_true_emits_under_deepseek_module \
  tests/component/external/test_anthropic.py \
  -q
```

**Betty local:** 26 passed on item 2 before push.

###### ada — 2026-06-15T20:08:11.423Z

Plan: [agent-ast-680-why-is-srcexternalanthropic-still-in-the-logs.md#ast-688--radia-review-criteria-for-external-layer-cleanliness](https://github.com/susansomerset/astral/blob/sub/AST-680/AST-688-radia-review-criteria-external-cleanliness/docs/features/agent/ast-688-radia-review-criteria-external-cleanliness.md) @ `eb441a67`

**Scope:** `minor` — global `review-child` §5g + this plan doc only; no `src/**`.

**Conf:** `high` — mirrors parent AST-680 AC #5 and ASTRAL_CODE_RULES §3.2/§3.3; follows AST-556 skill-update pattern.

**Risk:** `low` — rubric-only; wrong wording affects review signal, not runtime.

**Stages:** (1) Add §5g external-layer cleanliness table + sample review comment to `~/.cursor/skills/review-child/SKILL.md`, cross-refs from §5 intro and §5a Layer/Logging rows. (2) Verification + Implementation record mirror in plan on build.

---

#### Summary

Extend Radia's **`review-child`** skill so **Tests Passed** reviews on LLM external wrapper diffs explicitly flag **fix-now** when: (a) one external provider module imports from another, (b) shared helpers live in a sibling external module instead of **`utils/`**, or (c) DeepSeek-active call paths emit operator-visible logs under the **Anthropic** module prefix (e.g. `INFO src.external.anthropic: send_to_deepseek …` while detail lines say `provider=deepseek`). Include a copy-paste **sample review comment** template in the skill and mirrored here so operators recognize the gate. No product code, no **`review-child`** diff mechanics changes, no Betty test scope.

#### Dependency note

Parent **AST-680** AC **5** requires this rubric; sibling **AST-687** implements the actual refactor (`_emit_llm_call_debug` / `extract_api_response_text` → **`utils/`**, remove `deepseek` → `anthropic` import). **AST-688** ships the review gate **before or in parallel** with **AST-687** so the regression cannot re-land. During review of **AST-687**, Radia applies **§5g** against the fixed diff; during review of any future LLM external ticket, same bar.

Known bad pattern on **`origin/dev`** at plan time (illustrative — **AST-687** removes it):
```python
# src/external/deepseek.py
from src.external.anthropic import extract_api_response_text, _emit_llm_call_debug
```
```python
# src/external/anthropic.py — helper uses caller module's __name__
dbg = get_logger(__name__, debug_flag=True)  # always src.external.anthropic when defined here
```

#### Out of scope (explicit)

| Item | Owner |
|------|--------|
| Moving shared LLM helpers to **`utils/`** | **AST-687** |
| Changing log output in **`anthropic.py`** / **`deepseek.py`** | **AST-687** |
| **`docs/ASTRAL_CODE_RULES.md`** body edits | Not this ticket (rules already state external → utils only) |
| Betty manifest / component tests for log prefixes | Forbidden per parent |
| Renaming **`review-astral`** → **`review-child`** | Done (**AST-664**); this ticket patches **`review-child`** only |

#### Stage 1: Add §5g — External layer cleanliness (AST-680 / AST-688) to `review-child`

**Done when:** `~/.cursor/skills/review-child/SKILL.md` contains **#### 5g. External layer cleanliness (AST-680 / AST-688)** immediately after **#### 5f. Backend debug logging (AST-538 / AST-554)** and before **### 6. Combined doc**, and **§5**'s opening paragraph references §5g when the diff touches LLM external wrappers.

1. In **`~/.cursor/skills/review-child/SKILL.md`**, locate **### 5. Perform the review** (paragraph after the three lenses). After the existing sentence that references **§5f** for **`debug=`** paths, append:

   > When the diff adds or changes **`src/external/anthropic.py`**, **`src/external/deepseek.py`**, other LLM provider modules under **`src/external/`**, or **`utils/`** helpers shared by multiple LLM provider clients, also apply **§5g** explicitly.

2. Insert **#### 5g. External layer cleanliness (AST-680 / AST-688)** with this content (if §5g already exists from a partial edit, replace in full):

   **When to apply:** Any changed file under **`src/external/`** whose name or diff indicates an LLM provider client (**`anthropic.py`**, **`deepseek.py`**, future `*_llm.py` peers), plus any **`src/utils/`** module added or edited primarily to share parsing or debug emission between those clients.

   **Contract source:** **`docs/ASTRAL_CODE_RULES.md` §3.2** (external layer boundaries), **§3.3 Rule 1** (external may import **utils only**), **§1.5** / **§1.5.1** when debug emission is involved.

   **Severity:** Map violations below to **fix-now** in the Linear comment unless a documented exception in **`ASTRAL_CODE_RULES.md`** or an approved plan explicitly allows the pattern (today: **no** cross-external import between LLM provider clients).

   | Check | fix-now when |
   |-------|----------------|
   | **Cross-external import** | New or retained **`from src.external.<other>`** or **`import src.external.<other>`** between LLM provider modules (e.g. **`deepseek`** importing **`anthropic`**). **Exception (do not flag):** pre-existing documented paths unrelated to LLM peers (e.g. **`playwright`**, **`gmail`**) and the **timesheet callback** pattern in **`anthropic.py`** per §3.2 — not provider-to-provider sharing. |
   | **Shared helper placement** | A function used by **both** Anthropic and DeepSeek (or two LLM externals) remains defined in one external module and imported by the other — belongs in **`src/utils/`** per §3.3. |
   | **Hard-coded sibling logger** | A shared helper in external module **A** calls **`get_logger(__name__, …)`** (or equivalent) and is invoked from external module **B** — operator logs show module **A**'s prefix for **B**'s active provider. **fix-now:** move helper to **`utils/`** with caller-owned logger, or pass explicit logger / module name from the calling provider module. |
   | **Provider prefix mismatch** | Active call path is DeepSeek (e.g. **`send_to_deepseek`**, **`provider=deepseek`** in detail lines) but log prefix is **`src.external.anthropic`** (or vice versa for Anthropic-only paths showing DeepSeek prefix). Includes debug-contract index lines and routine INFO when **`debug=True`**. |
   | **Misleading func_name** | Index header **`func=`** names the wrong entrypoint (e.g. **`send_to_deepseek`** in the message while the emitting module is **`anthropic`**) **and** module prefix does not match the executing provider — flag with **Provider prefix mismatch**. |
   | **Debug contract on touched paths** | LLM external diff adds/changes **`debug=`** emission — also apply **§5f**; insufficient instrumentation remains **fix-now** per AST-538. |

   **Verification hints (review diff + mental log walkthrough, no pytest):**

   - Grep the diff for **`from src.external.`** inside **`src/external/`** LLM files.
   - If a helper moved to **`utils/`**, confirm **neither** LLM external imports the other's module for that helper.
   - For DeepSeek scenarios, expect prefix **`src.external.deepseek`**, not **`src.external.anthropic`**, when **`provider=deepseek`** in detail lines.

   **Grandfather (advisory, not fix-now):** Unchanged lines outside the diff that still violate the old pattern — note in comment if the ticket claims to fix attribution but leaves adjacent paths; do not block unrelated tickets solely for pre-existing debt unless the diff touches the same helper or import.

   **Coexistence (do not flag):** **`provider=anthropic`** detail field inside Anthropic module logs; HTTP library suppression in **`anthropic.py`** at import time per §3.2; timesheet callback injection without **`external` → `data`** import.

   **Not fix-now:** Betty lacking log-string tests; core/dispatcher attribution; provider **selection** logic in **`do_task`** (routing is **AST-493** territory unless the diff changes external modules).

3. At the end of **§5g**, add subsection **Sample review comment (external cleanliness)** — copy this block verbatim into the skill:
```markdown
   ### External layer cleanliness (AST-680)

   **fix-now:** Cross-external import — `src/external/deepseek.py` imports `_emit_llm_call_debug` from `src/external/anthropic.py`. Per §3.3, shared LLM helpers belong in `src/utils/`; each provider module must emit with its own logger identity.

   **fix-now:** Provider prefix mismatch — DeepSeek call path (`send_to_deepseek`, detail `provider=deepseek`) emits with log prefix `src.external.anthropic`. Operators cannot trust module attribution.

   **Recommended:** Move shared debug/parsing helpers to `src/utils/` (see AST-687); calling module passes `get_logger(__name__, debug_flag=True)` or equivalent so prefix matches executing provider.
```

4. In **§5a** table row **Layer compliance (B2)**, append to the cell (after the existing **`src/external/`** bullet):

   > For **LLM provider** modules (**`anthropic`**, **`deepseek`**, peers), also **§5g** (cross-external imports, shared-helper placement, provider log prefix).

5. In **§5a** table row **Logging (E1)**, append (after the existing **§5f** reference):

   > For **LLM external** diffs, also **§5g** (module prefix vs active provider).

6. Do **not** change **§7** (Linear status), assignee rules, or doc-only commit workflow in **§6**.

⚠️ **Decision:** Rubric lives in the **global** skill path (`~/.cursor/skills/review-child/SKILL.md`), not a repo copy under **`astral/.cursor/`**, per **orientation** § Cursor skills (global only). **Implementation record** in this plan doc is the auditable mirror for UAT.

#### Stage 2: Verification and handoff

**Done when:** A reader can run **`review-child`** on an LLM external wrapper diff and know exactly when cross-import / attribution issues are **fix-now**; plan published to **`origin/sub/AST-680/AST-688-radia-review-criteria-external-cleanliness`**; Linear **Plan Ready** with GitHub plan link and self-assessment in comment.

1. Re-read **`review-child/SKILL.md`** end-to-end: confirm **§5g** is referenced from **§5** intro and **§5a** rows; confirm **Sample review comment** block is present; confirm no contradictory text (e.g. "cross-external import OK for shared debug") remains elsewhere in the skill.

2. **Manual check (no pytest):** Using parent **AST-680** staging log excerpt (`INFO src.external.anthropic: send_to_deepseek …` with `provider=deepseek` detail lines), confirm §5g would flag **Provider prefix mismatch** as **fix-now** — mental walkthrough only.

3. On **`epic worktree`** (`astral-AST-680`), commit **only** `agent-ast-680-why-is-srcexternalanthropic-still-in-the-logs.md#ast-688--radia-review-criteria-for-external-layer-cleanliness` with message:

   `docs(AST-688): plan — Radia external layer cleanliness rubric`

4. Publish to **`origin/sub/AST-680/AST-688-radia-review-criteria-external-cleanliness`**:

   `git push origin HEAD:sub/AST-680/AST-688-radia-review-criteria-external-cleanliness`

   Confirm tip on GitHub matches the plan commit SHA.

5. **build-child** (this ticket): implement **Stage 1** on the global skill file, then one commit on **`epic worktree`** that appends **## Implementation record** at the bottom of **this** plan file documenting the exact §5g text added (same pattern as **AST-556**). If the skill file is outside git, the builder posts a short skill-diff summary in a Linear comment; the **Implementation record** in the plan doc is the canonical audit trail.

⚠️ **Decision:** Skill file is not versioned in **`astral`** git; **Implementation record** subsection is required in the build commit so Susan/Chuckles can verify §5g during UAT without opening `~/.cursor/`.

#### Self-Assessment

**Scope:** `scope-minor` — Only the global **`review-child`** skill (~one new subsection, two §5a cross-refs, sample comment template) and this plan doc; no application modules.

**Conf:** `conf-high` — Parent **AST-680** AC **5** and **ASTRAL_CODE_RULES** §3.2/§3.3 are fixed; the work is editorial alignment of the review rubric with the shipped bug and existing layer rules.

**Risk:** `risk-low` — Wrong rubric wording could cause false **fix-now** or missed cross-imports in review, but does not change runtime behavior or merge integration.

#### Self-review against ASTRAL_CODE_RULES

| Rule area | Plan alignment |
|-----------|----------------|
| §3.2 External layer | Plan references external boundaries; does not alter rules. |
| §3.3 Import rules | §5g encodes external → utils only for shared LLM helpers; no new exceptions. |
| §1.5 / §1.5.1 | Cross-ref to §5f for debug emission; no duplicate contract text. |
| §1.3 DRY | Single §5g table; §5a cross-refs avoid duplicating full rules. |
| §3.6 debug/ | No spike or `debug/` repo output. |

No conflicts requiring `conf-!!-NONE`.

---

#### Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-680/AST-688-radia-review-criteria-external-cleanliness`
**Product commits:** `1a6a6ea37474248bd9455feb4423af5495ecff66` — global `~/.cursor/skills/review-child/SKILL.md` §5g + §5/§5a cross-refs; **Implementation record** below (skill not in repo git)

---

#### Implementation record (AST-688 build)

**Skill path:** `~/.cursor/skills/review-child/SKILL.md` (global; not versioned in `astral` git)

**Changes applied:**

1. **§5 intro** — sentence added: when diff touches LLM external modules or shared utils helpers, apply **§5g**.
2. **§5a Layer compliance (B2)** — appended LLM provider cross-ref to **§5g**.
3. **§5a Logging (E1)** — appended LLM external module-prefix cross-ref to **§5g**.
4. **§5g External layer cleanliness (AST-680 / AST-688)** — inserted after **§5f**, before **§6**, containing:
   - When to apply / contract source / severity
   - fix-now table: cross-external import, shared helper placement, hard-coded sibling logger, provider prefix mismatch, misleading func_name, debug contract on touched paths
   - Verification hints, grandfather, coexistence, not fix-now
   - **Sample review comment (external cleanliness)** block (verbatim per plan Stage 1 step 3)

**Verification:** Parent AST-680 staging pattern (`INFO src.external.anthropic: send_to_deepseek` + `provider=deepseek` detail) maps to **Provider prefix mismatch** fix-now under §5g.

---

#### Resolution (2026-06-15 — resolve-child, Radia review)

**Review ref:** Radia `review-child` comment on AST-688 (2026-06-15) — **discuss:** `code(AST-688)` @ `1a6a6ea3` bundles sibling **AST-687** product commits on the AST-688 publish ref.

**Addressed (branch law):**

| Item | Resolution |
|------|------------|
| Cross-ticket scope on publish ref | **AST-688 deliverable** remains doc/skill-only (§5g + Implementation record). All `src/**` changes are owned by **AST-687** (`origin/sub/AST-680/AST-687-llm-external-log-attribution`); reviewed separately with no fix-now. |
| Why product appears on AST-688 tip | Epic worktree build order landed AST-687 product on the shared integration line before AST-688 `code()` commit; Betty documented intentional spill so AST-688 regression manifest could run AST-687 pytest gate on the same publish ref. |
| merge-parent / ftr rollup | **No double-count:** `merge-child` merges each `sub/*` into `ftr/*` once; duplicate ancestry dedupes at merge. Review scope for AST-688 is §5g + plan doc commits only (`eb441a67`, `1a6a6ea3` doc portions, `ae8bf703`, `f9201d8c`, `2e28583d`). |
| Future builds | Doc/skill-only tickets should not re-commit sibling `src/**` — keep product on the owning child sub-branch (lesson from this spill). |

**Advisory (no change):** Global skill file is correct audit trail via Implementation record; §5g sample comment referencing `_emit_llm_call_debug` is intentional bug-pattern illustration.

**Publish after resolve:** `origin/sub/AST-680/AST-688-radia-review-criteria-external-cleanliness` — resolution doc commit only.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `docs/features/agent/ast-688-radia-review-criteria-external-cleanliness.md` | This plan + **Implementation record** mirror | `eb353ff31` `331047c16` `e67c02e60` `f736ef082` |
| + unplanned | `src/core/agent.py` | — | `f736ef082` |
| + unplanned | `src/external/anthropic.py` | — | `f736ef082` |
| + unplanned | `src/external/deepseek.py` | — | `f736ef082` |
| + unplanned | `src/utils/llm_external.py` | — | `f736ef082` |
| | _tests_ | — | 3 file(s) |
