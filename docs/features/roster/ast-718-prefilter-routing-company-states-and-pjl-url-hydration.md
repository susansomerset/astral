# AST-718 — Prefilter routing, company states, and PJL URL hydration

**Linear:** [AST-718 — Prefilter routing, company states, and PJL URL hydration (find_job_page logic confirmation)](https://linear.app/astralcareermatch/issue/AST-718/prefilter-routing-company-states-and-pjl-url-hydration-find-job-page-logic-confirmation)

**Parent (reference only — do not implement sibling scope):** [AST-716 — find_job_page logic confirmation](https://linear.app/astralcareermatch/issue/AST-716/find-job-page-logic-confirmation)

**Publish ref:** `origin/sub/AST-716/prefilter-routing-and-pjl-url-hydration`

**Summary:** After homepage prefilter on the inflow watch path, route companies to **`NO_PREFILTER_JOBLISTS`**, **`PREFILTER_FAILED`**, or **`PREFILTER_PASSED`** based on dealbreaker rubric and PJL link presence. Hydrate prefilter nav **indices** (AST-697 decode output) into persisted **`possible_joblist_links`** — an ordered list of **normalized URL strings** via new **`normalize_link()`** in `utils/formatting.py` — for circular-link dedupe. **`PREFILTER_PASSED`** replaces **`TO_WATCH`** on this path; **`job_site`** stays unset until a list page is confirmed (AST-673 preserve rules unchanged).

**Depends on (Done on `origin/dev`):** AST-507 (encoded prefilter + `PREFILTER_*` states), AST-697 (`grades_encoded_prefilter_links` + bracket decode in `consult._apply_prefilter_encoded_link_meta`), AST-508 (`PREFILTER_PASSED` dispatch trigger), AST-673 (preserve verified `job_site` on locate failure).

**Out of scope (sibling tickets):** `fetch_job_pages` batch scrape + `PJL_READY` (AST-719), `select_job_page` dispatch refactor (AST-720), `parse_job_list` dispatch refactor (AST-721), prefilter rubric semantics changes, UI, new LLM task shapes.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/formatting.py` | Add `normalize_link()` pure string normalizer | utils |
| `src/utils/config.py` | `NO_PREFILTER_JOBLISTS` state + transitions; `ROSTER_CONFIG["prefilter"]` routing keys; `company_data_keys.possible_joblist_links` | utils |
| `src/core/roster.py` | PJL hydration helper; extend `_apply_prefilter_decoded_company_outcome` routing + persistence; mirror hydration in `_fetch_prefilter_notes` coat-check path | core |

**Verify only (Betty / qa-child — engineer does not edit in build-child):**

| File | Change |
|------|--------|
| `tests/component/core/test_roster.py` | Inflow routing cases: empty PJL → `NO_PREFILTER_JOBLISTS`, hydrated URLs in `possible_joblist_links`, legacy `TO_WATCH` unchanged |
| `tests/component/utils/test_config.py` | Assert `NO_PREFILTER_JOBLISTS` + transitions present |
| `tests/component/utils/test_formatting.py` | `normalize_link()` unit cases (create file if missing) |

**Read-only reuse (do not duplicate logic):**

| Symbol | Location | Use |
|--------|----------|-----|
| `_render_pass_fail` | `src/core/consult.py` | Dealbreaker **F** (confidence ≥ 2) → fail state |
| `_apply_prefilter_encoded_link_meta` | `src/core/consult.py` | Already maps AST-697 bracket tails → `possible_job_links` indices on decode |
| `parse_enumerate_array` | `src/utils/formatting.py` | Resolve nav index → raw URL from scraped `nav_links` |
| `_company_used_inflow_prefilter` | `src/core/roster.py` | Distinguish inflow vs legacy manual path |
| `_normalize_company_url_for_dedupe` | `src/core/roster.py` | **Do not** use for PJL ledger — host-level ingest dedupe only; PJL ledger uses `normalize_link()` |

---

## Stage 1: Config — `NO_PREFILTER_JOBLISTS` and prefilter routing keys

**Done when:** `COMPANY_STATES` and `company_state_transitions` allow prefilter to land in `NO_PREFILTER_JOBLISTS`; `ROSTER_CONFIG["prefilter"]` names the new terminal state and `possible_joblist_links` data key; no dispatch row changes in this ticket.

1. In `src/utils/config.py`, inside `COMPANY_STATES`, add after `"PREFILTER_FAILED"`:

   ```python
   "NO_PREFILTER_JOBLISTS": {},
   ```

   ⚠️ **Decision:** No `batch_criteria` — terminal/holding state (Susan brief: distinct from later scrape failures). Secondary CSE search actions are out of epic scope.

2. In `ASTRAL_CONFIG["company_state_transitions"]`, append (do not remove existing tuples):

   ```python
   ("HOMEPAGE_READY", "NO_PREFILTER_JOBLISTS"),
   ("WEBSITE_FOUND_RETRY", "NO_PREFILTER_JOBLISTS"),
   ("PREFILTER_PASSED", "NO_PREFILTER_JOBLISTS"),  # defensive — should not occur in happy path
   ```

   Keep all existing `HOMEPAGE_READY → PREFILTER_PASSED|PREFILTER_FAILED|TO_WATCH|IGNORE|…` edges.

3. In `ROSTER_CONFIG["prefilter"]`, add routing keys after `"error_state"`:

   ```python
   "no_pjl_state": "NO_PREFILTER_JOBLISTS",
   "pjl_url_data_key": "possible_joblist_links",
   ```

4. In `ROSTER_CONFIG["company_data_keys"]`, add:

   ```python
   "possible_joblist_links": "possible_joblist_links",
   ```

5. **Do not** change `ROSTER_CONFIG["prefilter"]["input_state"]` (remains `HOMEPAGE_READY`), `dispatch_tasks` seeds, or `locate_job_page.dispatch_input_states` in this ticket.

---

## Stage 2: `normalize_link()` in formatting

**Done when:** `normalize_link()` is importable from `src/utils/formatting.py`, has no imports outside `utils`, and produces stable dedupe keys for PJL URL ledger entries.

1. In `src/utils/formatting.py`, after `parse_enumerate_array`, add:

   ```python
   def normalize_link(url: str) -> str:
       """Pure PJL URL key: strip scheme, drop fragment, trim trailing slashes and index filenames."""
   ```

2. Implement literally (no `playwright.normalize_url`, no `urlparse` required — string ops only):

   - Input `url = (url or "").strip()`; return `""` if empty after strip.
   - Remove leading `http://`, `https://`, or `//` (case-insensitive on scheme).
   - Split optional `#fragment` off and discard fragment.
   - Lowercase the remainder.
   - Collapse runs of `/` to a single `/` (except leave `://` alone — scheme already stripped).
   - Strip trailing `/`.
   - If path ends with `/index.html`, `/index.htm`, or `/index.php` (case-insensitive), remove that suffix and re-strip trailing `/`.
   - Return the result.

   Examples (must match in Betty tests):

   | Input | Output |
   |-------|--------|
   | `https://Acme.com/careers/` | `acme.com/careers` |
   | `http://www.acme.com/jobs/index.html` | `www.acme.com/jobs` |
   | `//careers.acme.com/openings//` | `careers.acme.com/openings` |

   ⚠️ **Decision:** Susan requested a **formatting-layer** pure function (parent AST-716 resolved). Host-level ingest dedupe (`roster._normalize_company_url_for_dedupe`) stays separate — PJL circular-link ledger uses `normalize_link()` only.

---

## Stage 3: Hydration helper and prefilter outcome routing

**Done when:** `_apply_prefilter_decoded_company_outcome` routes inflow companies to the three AC states, persists `possible_joblist_links` as deduped normalized URLs on pass, leaves `job_site` untouched, and legacy manual path behavior (`TO_WATCH` / `IGNORE`) is unchanged.

1. In `src/core/roster.py`, add import at top with other formatting imports:

   ```python
   from src.utils.formatting import enumerate_array, normalize_link, parse_enumerate_array, value_to_str
   ```

   (Extend existing `formatting` import line — do not duplicate import block.)

2. Add helper `_hydrate_prefilter_pjl_urls(link_indices: List[int], nav_links_enumerated: str) -> List[str]` in the prefilter section (before `_apply_prefilter_decoded_company_outcome`):

   - If not `link_indices` or not `(nav_links_enumerated or "").strip()`, return `[]`.
   - `url_map = parse_enumerate_array(nav_links_enumerated)`.
   - Iterate `link_indices` in order; for each `idx`, `raw = url_map.get(int(idx))`; skip if `raw` is falsy.
   - `norm = normalize_link(raw)`; skip if falsy.
   - Append to output only if `norm` not already in output (ledger dedupe — first occurrence wins).
   - Return the list.

3. Add helper `_has_dealbreaker_f(grades: List[Dict[str, Any]]) -> bool`:

   ```python
   return any(
       g.get("grade") == "F"
       and isinstance(g.get("confidence"), int)
       and g["confidence"] >= 2
       for g in (grades or [])
   )
   ```

   ⚠️ **Decision:** Mirror `_render_pass_fail` F2+ check explicitly so empty-PJL routing runs only when **no dealbreaker F** — even if other pass_fail branches would also fail (all-X, no confidence > 1).

4. Rewrite `_apply_prefilter_decoded_company_outcome` state selection **after** grade hydration and **before** `save_company_data`:

   **Step A — verdict:**

   - `verdict_state = _render_pass_fail("prefilter_company", grades)` (unchanged).

   **Step B — extract indices** (AST-697 already applied during decode):

   - `link_indices = flat.get("possible_job_links") or []` (list of ints).

   **Step C — inflow vs legacy branch** using `_company_used_inflow_prefilter(short_name)`:

   **Inflow path (`True`):**

   - If `_has_dealbreaker_f(grades)` OR `verdict_state == cfg["fail_state"]` → `new_state = cfg["fail_state"]` (`PREFILTER_FAILED`).
   - Elif not `link_indices` → `new_state = cfg["no_pjl_state"]` (`NO_PREFILTER_JOBLISTS`).
   - Else:
     - `pjl_urls = _hydrate_prefilter_pjl_urls(link_indices, nav_links_from_data)`.
     - If not `pjl_urls` (indices present but none resolve) → `new_state = cfg["no_pjl_state"]`.
     - Else → `new_state = cfg["pass_state"]` (`PREFILTER_PASSED`).

   **Legacy path (`False`) — unchanged semantics:**

   - If `verdict_state == cfg["pass_state"]` → `new_state = cfg["legacy_pass_state"]` (`TO_WATCH`).
   - Else → `new_state = cfg["legacy_fail_state"]` (`IGNORE`).

   **Step D — decision string** (culture-link guard):

   ```python
   decision = "TO_WATCH" if new_state in ("TO_WATCH", "PREFILTER_PASSED") else "IGNORE"
   ```

   **Step E — persist** (extend existing `data_to_save` build):

   - Always save `prefilter_grades`, `prefilter_company_notes`, `nav_links` when present (unchanged).
   - Score on pass: keep existing `_render_score` block when `verdict_state == cfg["pass_state"]` and rubric present.
   - **Dual-write indices (temporary):** `data_to_save["possible_job_links"] = link_indices` — monolithic `find_job_page` / AST-535 dispatch still reads indices until AST-719 switches scrape entry to `possible_joblist_links`. AST-719 removes this dual-write.
   - **New canonical registry:** when `new_state == cfg["pass_state"]` and hydrated list non-empty:
     - `data_to_save[cfg["pjl_url_data_key"]] = pjl_urls` (i.e. `possible_joblist_links`).
   - When `new_state == cfg["no_pjl_state"]`: do **not** set `possible_joblist_links`; set `possible_job_links = []`.
   - Culture links: save `culture_links_to_explore` only when `decision == "TO_WATCH"` or `new_state == cfg["pass_state"]` (unchanged guard).

   **Step F — transition without touching job_site:**

   - Call `save_company_data(short_name, data_to_save)` then `transition_company_state(short_name, new_state)`.
   - **Do not** call `update_company(..., job_site=…)` in this helper.

5. In `_fetch_prefilter_notes` (~line 2256), after building `data_to_save["possible_job_links"]`, when `enumerated_nav_links` and link indices exist, also set:

   ```python
   hydrated = _hydrate_prefilter_pjl_urls(flat.get("possible_job_links") or [], enumerated_nav_links)
   if hydrated:
       data_to_save["possible_joblist_links"] = hydrated
   ```

   Coat-check path does not change company state — hydration only for notes refresh parity.

6. **Do not** modify `find_job_page`, `_fetch_job_links_content`, `run_select_job_page_dispatch`, or dispatcher routing in this ticket.

---

## Stage 4: Debug logging (AST-538) on routing outcome

**Done when:** With `debug=True` on `prefilter_company` / `prefilter_company_batch`, Style D index header and `|` detail lines record routing decision and hydrated PJL URL count without new logging when `debug=False`.

1. In `_apply_prefilter_decoded_company_outcome`, add optional parameter `debug: bool = False` and forward from `prefilter_company` and `_run_batch_company_prefilter` call sites (same pattern as other roster hops).

2. When `debug=True`, after state is chosen, emit via roster logger:

   - `debug_index` header: `prefilter routing short_name={short_name} -> {new_state}` with universal index (batch caller passes `batch_chunk_index` / position — reuse existing batch debug pattern from `_run_batch_company_prefilter`).
   - `debug_detail`: `link_indices={link_indices!r} hydrated_count={len(pjl_urls or [])} inflow={_company_used_inflow_prefilter(short_name)}`.

3. No new `[DEBUG]` `logger.info` strings; no logging in `formatting.normalize_link`.

---

## Self-Assessment

**Scope:** `Single-Component` — Touches config, one formatting helper, and the existing prefilter outcome helper in `roster.py`; no dispatcher, data-layer schema, or UI changes.

**Conf:** `high` — Reuses AST-507/697 decode and `_render_pass_fail`; routing rules are explicit in the ticket AC; hydration mirrors existing culture-link index→URL resolution via `parse_enumerate_array`.

**Risk:** `Medium` — Wrong empty-PJL vs pass routing would mis-classify inflow companies before PJL scrape; dual-write of indices limits blast radius until AST-719; verified `job_site` preservation (AST-673) is untouched because this stage never writes `job_site`.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Hydration centralized in `_hydrate_prefilter_pjl_urls`; routing stays in `_apply_prefilter_decoded_company_outcome` — no parallel state module |
| §2.1 config | New state name + `no_pjl_state` / `pjl_url_data_key` in config; no magic strings in core |
| §2.4 batch | No batch claim changes; prefilter batch reuses existing `_apply_prefilter_decoded_company_outcome` |
| §2.6 state machine | Transitions appended in config; core passes target state to `transition_company_state` only |
| §3.3 imports | `formatting` stays utils-pure; roster imports formatting + consult — allowed |
| §3.5 naming | `possible_joblist_links` snake_case JSON key; state `NO_PREFILTER_JOBLISTS` matches parent naming |

No unresolved conflicts.
