# UAT: raw model response missing from debug logs on prefilter runs

**Linear:** [AST-698](https://linear.app/astralcareermatch/issue/AST-698/uat-raw-model-response-missing-from-debug-logs-on-prefilter-runs)  
**Parent:** [AST-696](https://linear.app/astralcareermatch/issue/AST-696/prefilter-output-with-links) (AC #5 reference only)  
**Publish ref:** `origin/sub/AST-696/AST-698-uat-raw-response-missing-from-debug-logs-prefilter`  
**Summary:** Susan UAT on **prefilter_company** with **debug=True** shows no raw model response in execution history / app log. Two gaps: the roster dispatch path never forwards **debug** into **do_task**, so contract debug in **do_task** and **send_to_anthropic** stays off; and **do_task** only emits **raw_response** contract lines when `raw_text` exceeds 50 lines — prefilter JSON envelopes are short (typically 1–10 lines). This UAT bug wires debug through prefilter and restores short-response raw logging under **AST-538** §1.5.1. No decode, rubric, scoring, or UI changes.

**Root cause (current code):**

1. **`run_company_task` → `prefilter_company`** — `WEBSITE_FOUND` / `WEBSITE_FOUND_RETRY` calls `prefilter_company(..., ctx=ctx)` with no **debug** argument; `prefilter_company` has no **debug** parameter and calls `do_task(...)` without **debug**, so **debug=False** for the LLM hop even when the dispatcher batch runs with **debug=True**.
2. **`do_task` raw_response gate** — after `raw_text = extract_api_response_text(api_resp)` (~1669), emission is gated on `len(raw_text.splitlines()) > 50` (~1672). Prefilter compact JSON envelopes are under that threshold, so **raw_response** contract lines never emit at the **do_task** hop.
3. **Legacy encoded block** — the `if debug and "_encoded" in output_type:` block (~1828) still uses `logger.info("[DEBUG] do_task('%s'): literal encoded agent_payload …")` instead of **debug_detail** / **debug_detail_block** (AST-618 Stage 4 incomplete). Execution history surfaces contract lines, not grandfathered `[DEBUG]` **logger.info**.

**Out of scope:** **AST-697** link_set decode, rubric vectors, pass/fail scoring, roster persist rules, React/UI, `_fetch_prefilter_notes` coat-check path (no dispatcher **debug** today).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/roster.py` | Add **debug** param to **prefilter_company**; pass **debug** from **run_company_task**; forward **debug** to **do_task** | core |
| `src/core/agent.py` | Remove 50-line gate on **raw_response** contract emission; replace encoded-payload **logger.info** with **debug_detail** + **debug_detail_block** | core |

Betty may add manifest rows in **astral-tests** for debug passthrough + short **raw_response** emission — engineer does **not** edit `tests/` or the bible.

---

## Stage 1: Wire debug through prefilter_company

**Done when:** A dispatcher batch with **debug=True** on **WEBSITE_FOUND** / **WEBSITE_FOUND_RETRY** passes **debug=True** into **do_task** for **prefilter_company**; **debug=False** behavior unchanged.

1. In `src/core/roster.py`, function **`prefilter_company`**, extend the signature to match sibling roster entry points:
   ```python
   async def prefilter_company(
       short_name: str,
       company_website: str,
       ctx: Optional[Dict[str, Any]] = None,
       debug: bool = False,
       browser_context=None,
   ) -> Dict[str, Any]:
   ```
   Update the docstring **Args** line to note **debug** is forwarded to **do_task**.

2. In the same function, at the **`do_task`** call (~1061), add **`debug=debug`**:
   ```python
   api_result = await do_task(
       task_key="prefilter_company",
       live_content=live_content,
       index=short_name,
       ctx=task_ctx,
       debug=debug,
   )
   ```

3. In **`run_company_task`**, **`WEBSITE_FOUND` / `WEBSITE_FOUND_RETRY`** branch (~637–638), pass **debug** through:
   ```python
   result = await prefilter_company(short_name, company_website, ctx=ctx, debug=debug)
   ```

4. Manual verification (no test edits): in a Python shell on the epic worktree, inspect signatures only:
   ```python
   import inspect
   from src.core import roster
   sig = inspect.signature(roster.prefilter_company)
   assert "debug" in sig.parameters
   ```

⚠️ **Decision:** Do **not** add **debug** to **`_fetch_prefilter_notes`** or coat-check **do_task** calls — out of scope; dispatcher UAT path is **run_company_task** → **prefilter_company**.

---

## Stage 2: Emit raw_response and encoded payload under debug contract

**Done when:** With **debug=True** and a non-empty API body, **do_task** emits **raw_response** summary + **debug_detail_block** for short prefilter JSON envelopes; encoded consult tasks emit **encoded_payload** via contract helpers instead of **logger.info("[DEBUG] …")**; **debug=False** unchanged.

1. In `src/core/agent.py`, block ~1672–1677 that gates **raw_response** logging — **remove** the `len(raw_text.splitlines()) > 50` condition. Replace with:
   ```python
   if debug and raw_text and raw_text.strip():
       _dbg = _do_task_debug_logger(debug)
       _dbg.debug_detail(
           f"raw_response task_key={task_key} lines={len(raw_text.splitlines())} chars={len(raw_text)}"
       )
       _dbg.debug_detail_block(raw_text)
   ```
   **Do not** change capture logic for **raw_text** (~1664–1671).

2. In the same file, block ~1828–1839 (`if debug and "_encoded" in output_type:`) — **delete** the **`logger.info("[DEBUG] do_task('%s'): literal encoded agent_payload …")`** call. Replace with:
   ```python
   if debug and "_encoded" in output_type:
       literal = parsed if isinstance(parsed, str) else raw_text
       if isinstance(literal, str) and literal.strip():
           dbg = _do_task_debug_logger(debug)
           lines = [ln for ln in literal.splitlines() if ln.strip()]
           dbg.debug_detail(
               f"encoded_payload task_key={task_key} lines={len(lines)} chars={len(literal)}"
           )
           dbg.debug_detail_block(literal)
   ```

3. Manual verification (no test edits): confirm **truncate_debug_content** still applies inside **debug_detail_block** for content >50 lines — read `src/utils/logging.py` **`debug_detail_block`**; no code change expected.

4. Manual verification script (epic worktree, mocked provider — do **not** commit):
   - Patch **send_to_anthropic** to return success with a short JSON envelope (~3 lines) for **prefilter_company**.
   - Call **prefilter_company** with **debug=True** and capture log buffer / **debug_detail** output.
   - Assert a line matching **`raw_response task_key=prefilter_company`** and body containing the mock envelope text appears.

⚠️ **Decision:** Supersedes AST-618 Stage 4 optional “>50 lines only” gate for **raw_response** — Susan UAT requires short prefilter envelopes in hop logs. **truncate_debug_content** still caps long blobs; short bodies log in full per §1.5.1.

⚠️ **Decision:** **encoded_payload** block logs the extracted **agent_payload** string (post-envelope unwrap); **raw_response** logs the full API text. Both may appear for encoded tasks — intentional for UAT (envelope vs payload line).

---

## Execution contract

- Execute stages in order; **one commit per stage** on **`astral-AST-696`**, then publish each commit to **`origin/sub/AST-696/AST-698-uat-raw-response-missing-from-debug-logs-prefilter`** via `git push origin HEAD:sub/AST-696/AST-698-uat-raw-response-missing-from-debug-logs-prefilter` with **`--session astral-AST-696`** per build-child publish ritual.
- Do **not** edit `tests/`, `docs/ASTRAL_TEST_BIBLE.md`, or `docs/test-bible/**`.
- Blocking ambiguity → 🛑 comment on **AST-696** per plan-child execution contract.

---

## Self-Assessment

**Scope:** `minor` — Two product files (`roster.py` signature + one call site; `agent.py` two debug-emission blocks); no config, data, or UI layers.

**Conf:** `high` — Root causes are localized and match Susan's repro; pattern mirrors existing roster **debug** passthrough (**resolve_company_website**) and AST-618 contract helpers already in **do_task**.

**Risk:** `low` — Changes affect **debug=True** paths only; **debug=False** gates unchanged; no decode or persist behavior touched.

---

## Code rules self-review

| Rule | Assessment |
|------|------------|
| §1.5.1 debug contract | Removes `[DEBUG] logger.info` encoded block; emits via **debug_detail** / **debug_detail_block**; **debug=False** unchanged. |
| §1.3 DRY | Reuses **`_do_task_debug_logger(debug)`** — no new helpers. |
| §3.3 imports | No new imports or cross-layer violations. |
| §2.1 config | No config changes. |

No conflicts requiring **Conf: !!-NONE**.

---

## Review

**Branch:** `origin/sub/AST-696/AST-698-uat-raw-response-missing-from-debug-logs-prefilter`  
**Build tip:** `9dfe83e` (`b471bd6` Stage 1 roster debug passthrough; `9dfe83e` Stage 2 agent debug contract)
