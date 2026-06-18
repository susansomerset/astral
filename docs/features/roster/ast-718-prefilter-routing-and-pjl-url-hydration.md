# Prefilter routing, company states, and PJL URL hydration (find_job_page logic confirmation)

**Linear:** [AST-718](https://linear.app/astralcareermatch/issue/AST-718/prefilter-routing-company-states-and-pjl-url-hydration-find-job-page)  
**Parent:** [AST-716](https://linear.app/astralcareermatch/issue/AST-716/find-job-page-logic-confirmation) (context only — do not implement sibling hops here)  
**Publish ref:** `origin/sub/AST-716/prefilter-routing-and-pjl-url-hydration`  
**Summary:** After homepage prefilter on the decomposed PJL discovery path, route companies to **NO_PREFILTER_JOBLISTS**, **PREFILTER_FAILED**, or **PREFILTER_PASSED** (replacing **TO_WATCH** on this path), hydrate prefilter nav indices into persisted **`possible_joblist_links`** as deduped normalized URL strings via **`normalize_link()`** in `utils/formatting.py`, and leave **`job_site`** unset until a sibling confirms a list page.

**Depends on:** **AST-507** / **AST-697** (encoded prefilter decode → `possible_job_links` indices), **AST-702** (`HOMEPAGE_READY` prefilter batch), **AST-508** (`PREFILTER_PASSED` locate dispatch row — unchanged here).

**Out of scope (sibling tickets):** `fetch_job_pages` batch (**AST-719**), `select_job_page` dispatch refactor (**AST-720**), `parse_job_list` dispatch refactor (**AST-721**), prefilter rubric semantics (**AST-507** / **AST-697**), verified **`job_site`** preservation (**AST-673**), monolithic **`find_job_page`** behavior changes.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/formatting.py` | Add `normalize_link()` pure string URL normalizer | utils |
| `src/utils/config.py` | `NO_PREFILTER_JOBLISTS` state + transitions; `ROSTER_CONFIG` prefilter keys + `company_data_keys` | utils |
| `src/core/roster.py` | Decomposed-path detection, PJL hydration helper, tri-state routing in `_apply_prefilter_decoded_company_outcome` | core |

**No changes** to `src/core/consult.py`, `src/core/agent.py`, `find_job_page`, dispatch_tasks rows, or DB schema in this ticket.

**Tests:** Betty **`qa-child`** manifest (component roster + config assertions) — not implemented in build stages below.

---

## Stage 1: Config — `NO_PREFILTER_JOBLISTS` and data keys

**Done when:** `COMPANY_STATES` and `company_state_transitions` include **NO_PREFILTER_JOBLISTS** from prefilter input states; `ROSTER_CONFIG` names the new terminal state and documents `possible_joblist_links`.

1. In `src/utils/config.py`, inside `COMPANY_STATES`, add:
   ```python
   "NO_PREFILTER_JOBLISTS": {},
   ```
   Terminal / holding state (no batch criteria — same shape as **PREFILTER_FAILED**).

2. In `ASTRAL_CONFIG["company_state_transitions"]`, append (do not remove existing tuples):
   - `("HOMEPAGE_READY", "NO_PREFILTER_JOBLISTS")`
   - `("WEBSITE_FOUND", "NO_PREFILTER_JOBLISTS")`
   - `("WEBSITE_FOUND_RETRY", "NO_PREFILTER_JOBLISTS")`
   Keep existing `HOMEPAGE_READY → TO_WATCH` for legacy manual path.

3. In `ROSTER_CONFIG["prefilter"]`, add:
   - `"no_pjl_state": "NO_PREFILTER_JOBLISTS"`
   - Do **not** add `NO_PREFILTER_JOBLISTS` to `"pass_states"` — it is not a locate pass (batch pass/fail counters stay correct).

4. In `ROSTER_CONFIG["company_data_keys"]`, add:
   ```python
   "possible_joblist_links": "possible_joblist_links",
   ```
   ⚠️ **Decision:** New persisted key is **`possible_joblist_links`** (hydrated URL strings). Existing **`possible_job_links`** remains the decoded nav **index list** from the agent (**AST-697**) for traceability and legacy `find_job_page` until **AST-719** reads URLs directly.

5. Do **not** change `locate_job_page.dispatch_input_states`, dispatch_tasks seed rows, or **PREFILTER_PASSED** locate row (**AST-508**) in this ticket.

---

## Stage 2: Utils — `normalize_link()` in formatting.py

**Done when:** `normalize_link(url)` exists as a importable pure string helper with no Playwright dependency.

1. In `src/utils/formatting.py`, after `parse_enumerate_array`, add:
   ```python
   def normalize_link(url: str) -> str:
       """Normalize a URL string for PJL ledger dedupe (scheme/host lower, trim path slashes, keep query).
       Pure string helper — no network I/O. Used when hydrating possible_joblist_links."""
   ```
   Implementation requirements (mirror intent of `normalize_url` in `playwright.py` without importing it):
   - Empty / whitespace-only input → return `""`.
   - `urlparse` from `urllib.parse`.
   - Lowercase `scheme` (default `https` when missing).
   - Lowercase `netloc`.
   - `path.rstrip("/")` when path is non-root; preserve query and fragment.
   - Return reconstructed URL string.

2. Do **not** strip `www.` here — host-level dedupe for ingest uses `_normalize_company_url_for_dedupe` in `roster.py`. PJL ledger keys use `normalize_link` only, per parent **AST-716** resolved note #3.

---

## Stage 3: Core — tri-state routing and PJL URL hydration

**Done when:** `_apply_prefilter_decoded_company_outcome` routes decomposed-path companies to **NO_PREFILTER_JOBLISTS** / **PREFILTER_FAILED** / **PREFILTER_PASSED** with hydrated `possible_joblist_links`; legacy manual path still maps pass → **TO_WATCH** and fail → **IGNORE**; **`job_site`** is never written on the decomposed path.

1. In `src/core/roster.py`, add import:
   ```python
   from src.utils.formatting import normalize_link, parse_enumerate_array
   ```
   (merge with existing `enumerate_array` / `parse_enumerate_array` imports if already present — one import line only.)

2. Add helper `_company_on_decomposed_pjl_path(short_name: str, *, input_state: str = "") -> bool`:
   - Return `True` if `_company_used_inflow_prefilter(short_name)` (existing helper — **NEW → WEBSITE_FOUND** inflow).
   - Else if `input_state == "HOMEPAGE_READY"`, return `True`.
   - Else load company via `get_company(short_name)`; return `True` if `(company or {}).get("state") == "HOMEPAGE_READY"`.
   - Otherwise return `False` (legacy **IMPORTED** / manual **WEBSITE_FOUND** path → **TO_WATCH** / **IGNORE** unchanged).
   ⚠️ **Decision:** Decomposed path = inflow companies **or** companies prefilted from **HOMEPAGE_READY** (batch or single). Legacy empty-history / non-inflow pass still lands **TO_WATCH**.

3. Add helper `_hydrate_possible_joblist_links(link_indices: list, nav_links: str) -> list[str]`:
   - `url_map = parse_enumerate_array(nav_links or "")`.
   - Initialize `seen: set[str] = set()`, `out: list[str] = []`.
   - For each `link_id` in `link_indices` (preserve agent order):
     - Resolve `raw = url_map.get(int(link_id))` when `link_id` is int-like; if missing and `str(link_id).startswith("http")`, use `str(link_id)` as raw; else skip.
     - `norm = normalize_link(raw)`; if not `norm` or `norm in seen`, continue.
     - `seen.add(norm)`; `out.append(norm)`.
   - Return `out` (ordered deduped ledger — parent **AST-716** circular-link avoidance for downstream **AST-719**).

4. Refactor `_apply_prefilter_decoded_company_outcome` routing block (replace lines that set `new_state` from `verdict_state` / legacy aliases):

   **Always first:**
   - `grades = flat.get("grades") or []`
   - Hydrate rubric reasons (existing block).
   - `verdict_state = _render_pass_fail("prefilter_company", grades)` — dealbreaker **F** (confidence ≥ 2) yields `cfg["fail_state"]` (**PREFILTER_FAILED**); do not reimplement dealbreaker logic.

   **Then branch on path:**
   ```python
   on_decomposed = _company_on_decomposed_pjl_path(short_name, input_state=cfg.get("input_state") or "")
   link_indices = flat.get("possible_job_links") or []

   if on_decomposed:
       if verdict_state == cfg["fail_state"]:
           new_state = cfg["fail_state"]  # PREFILTER_FAILED
       else:
           hydrated = _hydrate_possible_joblist_links(link_indices, nav_links_from_data)
           if not hydrated:
               new_state = cfg.get("no_pjl_state") or "NO_PREFILTER_JOBLISTS"
           else:
               new_state = cfg["pass_state"]  # PREFILTER_PASSED
   elif verdict_state == cfg["pass_state"]:
       new_state = cfg["legacy_pass_state"]  # TO_WATCH
   else:
       new_state = cfg["legacy_fail_state"]  # IGNORE
   ```

5. Update `decision` assignment:
   ```python
   decision = "TO_WATCH" if new_state in ("TO_WATCH", "PREFILTER_PASSED") else "IGNORE"
   ```
   (**NO_PREFILTER_JOBLISTS** and **PREFILTER_FAILED** → **IGNORE** decision — same as fail/hold semantics today.)

6. Update `data_to_save` persistence:
   - Always save `prefilter_grades`, `prefilter_company_notes`, `nav_links` (when provided), `possible_job_links` (index list from decode — unchanged).
   - When `new_state == cfg["pass_state"]` on decomposed path and `hydrated` is non-empty:
     - `data_to_save["possible_joblist_links"] = hydrated`
   - When `new_state == cfg.get("no_pjl_state")`:
     - `data_to_save["possible_joblist_links"] = []` (explicit empty ledger)
   - When `new_state == cfg["pass_state"]` and rubric_list present, keep existing `prefilter_score` block.
   - When `decision == "TO_WATCH"` or `new_state == "PREFILTER_PASSED"`, keep `culture_links_to_explore` save.
   - Do **not** call `update_company(..., job_site=...)` anywhere in this function.

7. In `_run_batch_company_prefilter`, when calling `_apply_prefilter_decoded_company_outcome`, no signature change required — `cfg` already carries `input_state`.

8. In `prefilter_company` (single-entity path), no scrape/rubric changes — it already delegates to `_apply_prefilter_decoded_company_outcome`. Verify `nav_links_from_data=enumerated_nav_links` is still passed so hydration has the nav map.

9. Do **not** modify `find_job_page`, `_fetch_job_links_content`, or `run_company_task` locate branches — **AST-719** / **AST-720** consume `possible_joblist_links`.

---

## Execution contract (for the developer agent)

- Execute stages in order; **one commit per stage** on **`astral-AST-716`**, then publish each commit to **`origin/sub/AST-716/prefilter-routing-and-pjl-url-hydration`** via `git push origin HEAD:sub/AST-716/prefilter-routing-and-pjl-url-hydration` with **`--session astral-AST-716`** per **build-child** publish ritual.
- Stops and comments on **AST-716** parent per **plan-child** § Execution contract if `nav_links` is empty but indices are present (hydration yields empty → **NO_PREFILTER_JOBLISTS** is correct; do not improvise **PREFILTER_PASSED**).

---

## Self-Assessment

**Scope:** `Single-Component` — Touches config state definitions and one roster outcome helper chain (`_apply_prefilter_decoded_company_outcome` + two small helpers + `normalize_link`).

**Conf:** `high` — Reuses existing `_render_pass_fail`, `parse_enumerate_array`, and `_company_used_inflow_prefilter`; tri-state routing is explicit in parent **AST-716** AC #1.

**Risk:** `Medium` — Wrong path detection would send legacy manual companies to **PREFILTER_PASSED** instead of **TO_WATCH**, or mis-route empty PJL; mitigated by `_company_on_decomposed_pjl_path` gate and existing legacy tests left untouched.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Status |
|------|--------|
| §1.3 DRY | Reuses `parse_enumerate_array`, `_render_pass_fail`, `_company_used_inflow_prefilter`; no parallel state module |
| §2.1 config | New state + transitions + `ROSTER_CONFIG` keys only |
| §2.4 batch | No batch claim changes; `prefilter_company_batch` still calls shared outcome helper |
| §2.6 state machine | All transitions declared in `company_state_transitions`; `transition_company_state` only |
| §3.3 imports | `normalize_link` in utils; roster imports formatting, not Playwright for hydration |
| §3.5 naming | `possible_joblist_links` (URLs) vs `possible_job_links` (indices) per parent glossary |

No conflicts requiring `conf-!!-NONE`.
