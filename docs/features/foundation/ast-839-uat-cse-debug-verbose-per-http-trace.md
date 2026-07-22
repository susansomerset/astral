<!-- linear-archive: AST-839 archived 2026-07-22 -->

## Linear archive (AST-839)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-839/uat-cse-debug-verbose-per-http-trace-pacing-request-outcome  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-835 — Rate limit queries for a config-driven pause  
**Blocked by / blocks / related:** parent: AST-835

### Description

## What failed

With `debug=True` on inflow discovery, CSE pacing lines appear in a burst at one log timestamp (many `pacing: sleeping …` lines at 6:52:48 PM with no HTTP outcome between them). Susan cannot tell whether the process slept 12s between every CSE call or what each HTTP request returned.

## Expected

When `debug=True`, each Google CSE HTTP request emits verbose debug under the current Style D index: pacing sleep (if any) **at the time it happens**, then the HTTP outcome (status code, pagination start, item count or rate-limit signal) before the next request — so UAT can correlate timing and results without guessing.

## Repro

1. Run inflow discovery with `debug=True` for a candidate with stale search terms (e.g. manual dispatch on staging).
2. Open logs for `roster.run_inflow_discovery_batch`.
3. Observe multiple `pacing: sleeping …` lines sharing the same timestamp and no per-request HTTP result lines.

## Parent AC (quoted inline)

> 2. On HTTP 429, the system pauses for the configured duration before retrying; with `debug=True`, each pause and retry is visible under the current index header.

(AST-538 contract: when `debug=True`, log what was **found** and what was **recorded** per step — not only pass/fail counts.)

## Boundaries

* This bug does **not** change: inter-query delay / pause config literals, 429 retry semantics, or non-debug production logging.
* Does **not** add admin UI knobs.

### Comments

#### radia — 2026-07-02T23:18:50.402Z
### AST-839 review — clean (FIX-UAT)

**Diff:** `origin/dev...origin/sub/AST-835/AST-839-uat-cse-debug-verbose-per-http-trace` @ `7d33e50`
**Doc:** `docs/features/foundation/ast-839-uat-cse-debug-verbose-per-http-trace.md` § Review (Radia)

**Root cause / fix:** AST-837 buffered `pace_lines` and flushed after `debug_index`. Fix streams `log.debug_detail` as live `pace_detail` (pre-search index outcome `CSE search`) and adds per-HTTP `CSE HTTP start=… status=… items=…` / `rate_limited=…` outcome lines from `_http_get_with_pacing_and_retry`.

**Rules (no fix-now):**
- §1.5.1 — debug-only emission; real-time detail under pre-emitted index; hit count moved to `search complete:` detail line (documented UAT decision)
- §2.5 — external layer callback-only; no logging in `google_cse.py`
- AST-837 boundary — pacing/retry semantics and config unchanged

**Tests:** `TestGoogleCseAst839HttpOutcomeLines`, roster streaming order tests (discovery + resolve), bible AST-839 manifest.

**Advisory:** FIX-UAT clean — no `resolve-child` product work expected; re-test CSE debug trace in browser for Susan sign-off.

**Verdict:** Clean — no Radia fix-now items.

#### betty — 2026-07-02T23:17:22.027Z
## QA test manifest (AST-839)

**Publish:** `origin/sub/AST-835/AST-839-uat-cse-debug-verbose-per-http-trace` @ `b3d925a` (`merge-tests(AST-839): origin/tests c54a6c2`)

**Bible shasum:** `docs/test-bible/external/google_cse.md` → `79f7a2fddd7591cd3f622805dac9cc5449a6e9ce`

1. **Regression (required):** full CSE module (AST-489 + AST-837 pacing unchanged):
```bash
./scripts/testing/run_component_tests.sh tests/component/external/test_google_cse.py
```

2. **AST-839 per-HTTP outcome lines (required):**
```bash
./scripts/testing/run_component_tests.sh tests/component/external/test_google_cse.py::TestGoogleCseAst839HttpOutcomeLines
```

3. **Roster debug streaming — discovery + resolve (required):**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_roster.py::TestAst837CsePaceDebug \
  tests/component/core/test_roster.py::TestAst839CseDebugStreaming
```

**Pass criterion:** pytest green on items 1–3 — not zero-arg harness / branch-lock gate.

**Existing coverage (bible):** `docs/test-bible/external/google_cse.md` § AST-837 + § AST-839.

**Broken / obsolete (Betty revision):** `TestAst837CsePaceDebug::test_discovery_debug_flushes_pace_detail` → renamed/revised to `test_discovery_debug_streams_pace_detail_during_search` (AST-839 streaming; no `pace_lines` buffer).

— Betty

#### hedy — 2026-07-02T23:15:16.909Z
Plan: `docs/features/foundation/ast-839-uat-cse-debug-verbose-per-http-trace.md`

https://github.com/susansomerset/astral/blob/sub/AST-835/AST-839-uat-cse-debug-verbose-per-http-trace/docs/features/foundation/ast-839-uat-cse-debug-verbose-per-http-trace.md

Published @ `bcdf72d` (+ `plan(AST-839)` marker `bffe0e3`).

**Self-assessment**
- **Scope:** Single-Component — `google_cse.py` per-HTTP `pace_detail` outcome lines + roster streaming debug at the two existing CSE call sites (remove `pace_lines` buffer).
- **Conf:** high — Root cause is AST-837 buffered flush after `debug_index`; fix is direct `log.debug_detail` callback + explicit HTTP outcome strings in the helper.
- **Risk:** low — Debug-only when `debug=True`; pacing config, retry semantics, and non-debug logging unchanged.

---

# AST-839 — UAT: CSE debug verbose per-HTTP trace (pacing + request outcome)

- **Linear (this ticket):** [AST-839 — UAT: CSE debug verbose per-HTTP trace](https://linear.app/astralcareermatch/issue/AST-839/uat-cse-debug-verbose-per-http-trace-pacing-request-outcome)
- **Parent (reference only):** [AST-835 — Rate limit queries for a config-driven pause](https://linear.app/astralcareermatch/issue/AST-835/rate-limit-queries-for-a-config-driven-pause)
- **Shipped sibling (context):** [AST-837 — Google CSE query pacing and rate-limit pause](https://linear.app/astralcareermatch/issue/AST-837/google-cse-query-pacing-and-rate-limit-pause-rate-limit-queries-for-a) — pacing/retry behavior unchanged by this bug fix
- **Publish ref:** `origin/sub/AST-835/AST-839-uat-cse-debug-verbose-per-http-trace`

## Summary

AST-837 wired CSE pacing/retry trace through a **`pace_lines` buffer** in roster and flushed it **after** the Style D **`debug_index`** header. A paginated term (up to 10 HTTP pages) therefore logs every `pacing: sleeping …` line at one timestamp with no per-request HTTP outcome between them — Susan cannot tell whether 1.2s pacing actually ran between calls. This UAT bug fix streams **`pace_detail`** to **`log.debug_detail` in real time** (after a pre-search index header) and adds one **HTTP outcome** detail line per request from **`google_cse.py`**. Pacing config, retry semantics, and non-debug logging are unchanged.

## Root cause (AST-837 Stage 3)

```python
pace_lines: list[str] = []
pace_detail = pace_lines.append if debug else None
hits = search_google_cse(..., pace_detail=pace_detail)
# … then debug_index … then for line in pace_lines: log.debug_detail(line)
```

Buffered messages accumulate across all pagination pages, then flush in a burst under a single timestamp.

## Out of scope (explicit)

| Item | Reason |
|------|--------|
| `GOOGLE_CSE_CONFIG` literals or env overrides | Ticket boundaries |
| 429 retry / inter-query delay semantics | AST-837 — unchanged |
| Non-debug production logging | No new lines when `debug=False` |
| Admin UI | Unchanged |
| Betty test / bible edits | **qa-child** after build |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/external/google_cse.py` | Emit per-HTTP **`pace_detail`** outcome lines from `_http_get_with_pacing_and_retry` (status, `start`, item count or rate-limit flag) | external |
| `src/core/roster.py` | Discovery + resolve: pre-search **`debug_index`**, stream **`log.debug_detail`** as **`pace_detail`**, remove **`pace_lines`** buffer; adjust post-search detail lines | core |

## Stage 1: Per-HTTP outcome lines in `google_cse.py`

**Done when:** With a non-**`None`** **`pace_detail`** callback, each HTTP attempt inside **`_http_get_with_pacing_and_retry`** invokes **`pace_detail`** for pacing sleep, rate-limit pause (existing), and a new outcome line **before returning or continuing retry**; with **`pace_detail=None`**, behavior is identical to today aside from the new helper logic paths (no extra work).

1. In **`_http_get_with_pacing_and_retry`**, after **`last_parsed = _parse_cse_json(last_response)`** and **before** the rate-limit retry branch, compute item count for the outcome line:

```python
items = last_parsed.get("items") if isinstance(last_parsed, dict) else None
item_count = len(items) if isinstance(items, list) else 0
```

2. When **`_is_rate_limit_response(last_response.status_code, last_parsed)`** is true and **`attempt < max_retries`**, **before** the existing rate-limit pause **`_pace_detail_emit`**, add:

```python
_pace_detail_emit(
    pace_detail,
    f"CSE HTTP start={params['start']} status={last_response.status_code} rate_limited=true",
)
```

Keep the existing `rate limit: … pausing …` line unchanged immediately after.

3. When the response is **not** rate-limited (the branch that **`return last_response, last_parsed`**), **immediately before** that **`return`**, emit:

```python
_pace_detail_emit(
    pace_detail,
    f"CSE HTTP start={params['start']} status={last_response.status_code} items={item_count}",
)
```

4. When rate-limit retries are **exhausted** (fall through to **`RuntimeError`** raise at end of helper), **before** **`raise RuntimeError`**, emit:

```python
_pace_detail_emit(
    pace_detail,
    f"CSE HTTP start={params['start']} status={last_response.status_code} rate_limited=exhausted",
)
```

5. Do **not** add logging in the external module — only **`pace_detail`** callbacks (§2.5). Do **not** change pacing sleep math, retry counts, or **`search_google_cse`** public signature.

⚠️ **Decision:** Outcome lines use Google's **`start`** request param (pagination index) so UAT can correlate pages within one term. **`items=`** is organic hit count from parsed JSON (0 when absent or empty).

---

## Stage 2: Stream roster debug — discovery + resolve

**Done when:** With **`debug=True`**, inflow discovery logs **`debug_index`** **before** each term's **`search_google_cse`** call; pacing sleeps, rate-limit pauses, and HTTP outcome lines appear as **` | `** details **as they happen** (distinct log timestamps when sleeps occur); post-search summary/hit lines remain under the same index header without a second burst of buffered pacing lines. **`debug=False`** unchanged.

### 2a. `run_inflow_discovery_batch` term loop

1. **Remove** the **`pace_lines`** list and **`pace_lines.append`** callback pattern entirely for this loop.

2. **Before** the **`try:`** that calls **`search_google_cse`**, when **`debug`**:

```python
log.debug_index(
    func="roster.run_inflow_discovery_batch",
    index=term_i,
    total=term_total,
    identifier=term,
    outcome="CSE search",
)
pace_detail = log.debug_detail
```

When **`not debug`**, set **`pace_detail = None`**.

3. Pass **`pace_detail=pace_detail`** into **`search_google_cse(...)`** (unchanged kwargs otherwise).

4. In the **`except (RuntimeError, ValueError) as exc:`** block when **`debug`**:
   - **Remove** the **`log.debug_index(...)`** call (index already emitted in step 2).
   - **Remove** the **`for line in pace_lines`** loop.
   - **Add** **`log.debug_detail(f"CSE failed: {exc!s}")`** only.

5. In the **`try`** success path when **`debug`**:
   - **Remove** the **`log.debug_index(..., outcome=f"{len(hits)} hit(s)")`** call.
   - **Remove** the **`for line in pace_lines`** loop.
   - **Keep** as the first post-search detail line: **`log.debug_detail(f"search complete: {len(hits)} hit(s)")`**
   - **Keep** existing **`search_term=`**, hit listing, and **`last_scan_at bumped`** detail lines unchanged after that.

### 2b. `resolve_company_website`

Apply the same streaming pattern:

1. Remove **`pace_lines`** / buffer.

2. After building **`query`**, before **`try:`**, when **`debug`**:

```python
log.debug_index(
    func="roster.resolve_company_website",
    index=1,
    total=1,
    identifier=short_name,
    outcome="CSE search",
)
pace_detail = log.debug_detail
```

When **`not debug`**, **`pace_detail = None`**.

3. **`except`** path when **`debug`**: remove second **`debug_index`** and buffer flush; **`log.debug_detail(f"CSE failed: {exc!s}")`** and **`log.debug_detail(f"query={query!r}")`**.

4. Success path when **`debug`**: remove post-search **`debug_index`** with hit count; remove buffer flush; first detail **`log.debug_detail(f"search complete: {len(hits)} CSE hit(s)")`**, then existing **`query=`** and hit listing lines.

5. **`NO_WEBSITE`**, vet, and other downstream **`debug_index`** blocks — **do not change**.

⚠️ **Decision:** Pre-search index outcome **`"CSE search"`** is intentional — Susan's UAT need is real-time HTTP trace under one header per term/company, not a post-hoc index outcome. Final hit count moves to a **`search complete:`** detail line.

---

## Self-Assessment

**Scope:** `Single-Component` — Touches **`google_cse.py`** outcome callbacks and roster debug wiring at the two existing CSE call sites only.

**Conf:** `high` — Root cause is the AST-837 buffer flush; fix is reorder + direct **`log.debug_detail`** callback plus explicit HTTP outcome strings.

**Risk:** `low` — Debug-only path when **`debug=True`**; production and pacing/retry semantics unchanged.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Plan compliance |
|------|-----------------|
| §1.5.1 debug | Emission only when **`debug=True`** via existing **`set_debug_flag`**; streaming **`debug_detail`** under pre-emitted index header |
| §2.5 external | No logging in **`google_cse.py`**; **`pace_detail`** only |
| §2.6 state machine | No transition changes |
| §1.3 DRY | HTTP outcome strings centralized in **`_http_get_with_pacing_and_retry`**; roster pattern mirrored at two call sites only |

No **`Conf: !!-NONE`** conflicts.

---

## Betty / qa-child (after build — engineer does not edit tests)

Expect manifest updates for:

- Roster discovery test: assert **`pace_detail`** is invoked during mock CSE (streaming), not only after return.
- Optional: assert mocked multi-page search produces interleaved pacing + **`CSE HTTP start=`** outcome lines in call order.
- Regression: existing **`TestGoogleCseAst837PacingAndRateLimit`** + AST-489 module tests remain green.

---

## Review (build)

**Built:** `origin/sub/AST-835/AST-839-uat-cse-debug-verbose-per-http-trace` @ `5ce1c46`

**Stages delivered:**
- Stage 1: per-HTTP `pace_detail` outcome lines in `google_cse.py` — `f65f6ff`
- Stage 2: stream `log.debug_detail` as `pace_detail` in discovery + resolve — `5ce1c46`

**Betty / qa-child:** Roster discovery streaming callback assertions; optional multi-page interleaved pacing + `CSE HTTP start=` order; regression on AST-837 + AST-489 CSE tests.

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-835/AST-839-uat-cse-debug-verbose-per-http-trace` @ `b3d925a`

### What's solid

| Area | Notes |
| --- | --- |
| Root cause / fix | AST-837 `pace_lines` buffer removed; `log.debug_detail` passed as live `pace_detail` callback — pacing sleeps and HTTP outcomes stream with real timestamps during `search_google_cse`. |
| Plan fidelity | Stage 1 outcome lines in `_http_get_with_pacing_and_retry` (`items=`, `rate_limited=true`, `rate_limited=exhausted`); Stage 2 pre-search `debug_index` + streaming at discovery and resolve call sites. |
| §1.5.1 debug | Emission gated on `debug=True` via existing `set_debug_flag`; pre-search index per term/company; `search complete:` detail replaces post-search index hit-count outcome (documented UAT decision). |
| §2.5 external | No logging added in `google_cse.py`; `pace_detail` callback only. |
| AST-837 boundary | Pacing config, retry semantics, and `GOOGLE_CSE_CONFIG` untouched — debug wiring only. |
| Tests / bible | `TestGoogleCseAst839HttpOutcomeLines` (success, multi-page, retry, exhausted); roster streaming order tests for discovery + resolve; bible AST-839 manifest rows. |

### Issues

None.

### Recommended actions

| Severity | Action |
| --- | --- |
| **Advisory** | FIX-UAT clean — no `resolve-child` product work expected; Chuckles may advance bug to **User Testing** after Susan re-tests per fix-uat lane. |
| **Advisory** | Resolve path now emits two `debug_index` headers when CSE succeeds then vet runs (pre-search `CSE search` + downstream vet index) — pre-existing multi-phase pattern; acceptable for UAT HTTP trace focus. |

**Verdict:** Clean — no Radia fix-now items.

---

## Resolution (2026-07-02)

**Review @ `7d33e50`** — Radia **fix-now: none**. No product commits required.

| Item | Resolution |
|------|------------|
| fix-now | N/A — shipped Stages 1–2 unchanged (`f65f6ff`, `5ce1c46`). |
| advisory — FIX-UAT clean | Accepted — no resolve product work; Susan re-tests CSE debug trace on staging. |
| advisory — dual `debug_index` on resolve success (CSE search + vet) | Accepted — pre-existing multi-phase pattern; UAT focus is per-HTTP trace under pre-search index. |

**§9a dry-run:** `origin/sub/AST-835/AST-839-uat-cse-debug-verbose-per-http-trace` → `origin/dev` **clean**; → `origin/ftr/AST-835-rate-limit-queries-for-a-config-driven-pause` **clean**.
