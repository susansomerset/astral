# AST-827 — Title handoff and DOM culling for parse_job_list

**Linear:** [AST-827 — Title handoff and DOM culling for parse_job_list (Get parse_job_list to work)](https://linear.app/astralcareermatch/issue/AST-827/title-handoff-and-dom-culling-for-parse-job-list-get-parse-job-list)

**Parent (reference only):** [AST-824 — Get parse_job_list to work](https://linear.app/astralcareermatch/issue/AST-824/get-parse-job-list-to-work)

**Publish ref:** `origin/sub/AST-824/AST-827-title-handoff-dom-cull`

**Summary:** After AST-720/721 split **select_job_page** and **parse_job_list** into separate dispatch hops, Susan's medicarerights.org repro shows **parse_job_list** receiving a single job `<a>` instead of a listing fragment covering **all** titles Grace returned on **PJL_READY → JOBLIST_IDENTIFIED**. This ticket restores the decomposed handoff: every title from **select_job_page** persists in company data for the parse hop, and **run_parse_job_list_dispatch** uses those titles to trim the rescraped careers-list DOM before the parsing agent runs — with AST-538 debug traceability and unchanged retry/terminal failure semantics.

**Build gate (siblings):** None blocking — parent **AST-824** is **In Progress**; **AST-720** / **AST-721** context is on `origin/ftr/AST-824-get-parse-job-list-to-work`.

**Out of scope:** Agent prompt prose for **select_job_page** / **parse_job_list**; monolithic **find_job_page**; **fetch_job_pages** batch scrape; AST-689 readiness timing changes; unrelated roster states.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/roster.py` | Shared title→DOM cull helper; post-cull coverage validation; debug on select finalize + parse dispatch; wire **JOBS_FOUND** / chain resolver through same helper | core |
| `src/utils/formatting.py` | Harden `find_job_containers` for sibling job-link listings (medicarerights-style `<a>` rows) when no single parent covers all titles | utils |

**Verify only (Betty / qa-child):**

| File | Change |
|------|--------|
| `tests/component/core/test_roster.py` | Two-title **JOBLIST_IDENTIFIED** persistence; parse dispatch passes multi-title culled DOM to `do_task`; coverage failure → `PARSE_DISPATCH_NO_CONTAINERS`; **JOBS_FOUND** chain smoke unchanged |
| `tests/component/utils/test_formatting.py` | Sibling `<a>` two-title cull case mirroring medicarerights repro |

**Read-only reuse (do not duplicate):**

| Symbol | Location | Use |
|--------|----------|-----|
| `_finalize_joblist_identified` | `src/core/roster.py` | Extend debug + title list normalization at save |
| `run_parse_job_list_dispatch` | `src/core/roster.py` | Primary parse-hop fix |
| `make_locate_parse_resolver` | `src/core/roster.py` | **JOBS_FOUND** chained select→parse — must call same cull helper |
| `find_job_containers` | `src/utils/formatting.py` | Title-driven trim |
| `_scrape_list_page_dom_for_parse` | `src/core/roster.py` | Rescrape + AST-689 readiness — do not alter waits |
| `_save_parse_dispatch_failure` | `src/core/roster.py` | Existing retry/terminal paths |

**Spike / Playwright / investigation output:** optional repro script under `debug/spikes/ast-827-medicarerights-cull/` (gitignored defaults only).

---

## Stage 1: Shared cull helper and title normalization

**Done when:** One function in `roster.py` performs title list normalization, `find_job_containers`, join, and coverage check; both decomposed parse dispatch and chain resolver call it; no behavior change yet beyond centralization.

1. In `src/core/roster.py`, after `make_locate_parse_resolver` (≈ line 102), add:

   ```python
   def _normalize_job_titles(raw: Any) -> List[str]:
       """Strip blanks; preserve order from select/company_data."""
       if not isinstance(raw, list):
           return []
       return [str(t).strip() for t in raw if str(t).strip()]

   def _dom_text_covers_titles(dom_html: str, job_titles: List[str]) -> bool:
       blob = (dom_html or "").lower()
       return all(t.lower() in blob for t in job_titles if t.strip())

   def _culled_dom_for_parse(
       dom_html: str, job_titles: List[str]
   ) -> Tuple[str, List[str], str]:
       """Returns (dom_joined, containers, outcome_label).
       outcome_label: no_titles | full_dom | culled | cull_miss."""
       titles = _normalize_job_titles(job_titles)
       if not titles:
           return ("", [], "no_titles")
       if len(titles) < 2:
           return ((dom_html or "").strip(), [dom_html or ""], "full_dom")
       containers = find_job_containers(dom_html or "", titles)
       dom_joined = "\n".join(containers).strip()
       if not dom_joined:
           return ("", containers, "cull_miss")
       if _dom_text_covers_titles(dom_joined, titles):
           return (dom_joined, containers, "culled")
       # find_job_containers fallback [dom_html] may not cover all titles on partial rescrape
       if _dom_text_covers_titles(dom_html or "", titles):
           return ((dom_html or "").strip(), containers, "full_dom")
       return ("", containers, "cull_miss")
   ```

2. In `make_locate_parse_resolver`, replace inline `find_job_containers` / join with `_culled_dom_for_parse(dom_full, titles)` — use `dom_joined` and `outcome_label`; when `outcome_label == "cull_miss"`, return `("", vis)` so agent chain suppression (AST-469) still applies.

3. Do **not** change public signatures of exported roster entry points in this stage.

⚠️ **Decision:** Coverage validation lives in roster (orchestration), not inside `find_job_containers` (pure formatting). Formatting keeps returning best-effort containers; roster rejects culls that omit a saved title.

---

## Stage 2: Select finalize — persist full title list + debug

**Done when:** After decomposed **PJL_READY → JOBLIST_TITLES**, company data holds the exact normalized title list Grace returned; `debug=True` on select dispatch logs title count and selected URL under AST-538 index header.

1. In `_finalize_joblist_identified` (`src/core/roster.py`), replace:

   ```python
   job_titles = select_parsed.get("job_titles", [])
   ```

   with:

   ```python
   job_titles = _normalize_job_titles(select_parsed.get("job_titles"))
   ```

2. Keep the existing `save_company_data` call keys (`job_titles`, `selected_pjl_url` via `sel_cfg["selected_pjl_url_key"]`) — only the normalized list value changes.

3. After the first `save_company_data` in `_finalize_joblist_identified`, when `debug=True`:

   ```python
   log = logger
   log.set_debug_flag(True)
   log.debug_index(
       func="roster._finalize_joblist_identified",
       index=1,
       total=1,
       identifier=short_name,
       outcome=f"titles={len(job_titles)} url={job_site_url}",
   )
   log.debug_detail(f"titles={job_titles!r}")
   ```

4. Grep `src/core/roster.py` for other `job_titles = select_parsed.get("job_titles"` assignments in `_finalize_joblist_titles_after_chain` and `_finalize_joblist_titles_select_only` — apply `_normalize_job_titles` there too for **JOBS_FOUND** parity (same save shape, no new states).

---

## Stage 3: Parse dispatch — title-driven cull, coverage gate, debug

**Done when:** `run_parse_job_list_dispatch` loads normalized titles from company data, rescrapes `selected_pjl_url`, culls via `_culled_dom_for_parse`, rejects partial culls with existing `PARSE_DISPATCH_NO_CONTAINERS` failure, and logs title count + pre/post DOM sizes when `debug=True`.

1. In `run_parse_job_list_dispatch`, replace:

   ```python
   job_titles = cdata.get("job_titles") or []
   ```

   with:

   ```python
   job_titles = _normalize_job_titles(cdata.get("job_titles"))
   ```

2. After `dom_html = await _scrape_list_page_dom_for_parse(...)` and before calling the parse agent, add:

   ```python
   pre_cull_chars = len(dom_html or "")
   dom_joined, containers, cull_outcome = _culled_dom_for_parse(dom_html, job_titles)
   post_cull_chars = len(dom_joined or "")
   if debug:
       log = logger
       log.set_debug_flag(True)
       log.debug_detail(
           f"titles={len(job_titles)} pre_cull_chars={pre_cull_chars} "
           f"post_cull_chars={post_cull_chars} containers={len(containers)} "
           f"cull_outcome={cull_outcome!r}"
       )
   if cull_outcome == "cull_miss" or not dom_joined.strip():
       return _save_parse_dispatch_failure(
           short_name, company_website, list_url, input_state,
           notes="containers not found for titles", response_type="PARSE_DISPATCH_NO_CONTAINERS",
       )
   ```

3. Remove the old inline block:

   ```python
   containers = find_job_containers(dom_html, job_titles)
   if not containers:
       return _save_parse_dispatch_failure(...PARSE_DISPATCH_NO_CONTAINERS...)
   dom_joined = "\n".join(containers)
   ```

4. Extend the existing `debug_index` on `run_parse_job_list_dispatch` (≈ line 1191) **outcome** string to include `cull_outcome` after parse completes successfully or on failure paths that already emit debug_index — append `cull={cull_outcome}` to the outcome fragment.

5. Leave `_fetch_parse_job_list(dom_joined, ...)` unchanged — it already passes culled DOM as `live_content`.

6. Do **not** change `_save_parse_dispatch_failure` state transitions or `parse_job_list_notes` shapes.

---

## Stage 4: `find_job_containers` — sibling job-link listings

**Done when:** Two-title DOM made of sibling `<a href="…">Title</a>` elements returns outerHTML containing **both** titles (not a single anchor); existing formatting tests stay green.

1. In `src/utils/formatting.py`, inside `find_job_containers`, after Phase 1 fails and Phase 2 begins (≈ line 249), add **Phase 2b** before the final `return [dom_html]`:

   - Collect leaf tags from `partial` whose `_titles_in(el)` is non-empty (reuse existing `leaves` computation).
   - If `len(titles_set) >= 2` and the union of `_titles_in(leaf)` across all leaves equals `titles_set`, return `[str(leaf) for leaf, _ in leaves]` (one outerHTML per title-bearing leaf).
   - This covers medicarerights-style flat job link rows where no single parent is the narrowest all-titles container but each title lives in its own anchor sibling.

2. In `tests/component/utils/test_formatting.py`, add `test_sibling_anchor_links_two_titles`:

   ```python
   dom = (
       '<div class="careers-list">'
       '<a href="https://example.com/job-a">Client Services Associate: Bilingual Spanish and English</a>'
       '<a href="https://example.com/job-b">Policy Analyst</a>'
       '</div>'
   )
   titles = [
       "Client Services Associate: Bilingual Spanish and English",
       "Policy Analyst",
   ]
   out = fmt.find_job_containers(dom, titles)
   joined = "\n".join(out)
   assert "Client Services Associate" in joined
   assert "Policy Analyst" in joined
   assert joined.count("<a ") >= 2
   ```

3. Run `tests/component/utils/test_formatting.py::TestFindJobContainers` locally after edit — must pass before stage commit.

⚠️ **Decision:** Phase 2b is additive; Phase 1 deepest-container wins when a single wrapper already covers all titles (existing `test_phase_one_deepest_container` behavior preserved).

---

## Stage 5: JOBS_FOUND chain parity (no regression)

**Done when:** `jobs_found_process_job_site` / `make_locate_parse_resolver` still produce multi-title culled DOM for chained select→parse; existing AST-469/721 component tests for **JOBS_FOUND** and resolver tuple contract remain green without test edits unless Betty's manifest adds Stage 4 cases only.

1. In `_finalize_joblist_titles_select_only` and `_finalize_joblist_titles_after_chain`, replace inline `find_job_containers` + join with `_culled_dom_for_parse` — same `cull_miss` → `CANNOT_PARSE_JOB_SITE` / `NO_JOBLIST` behavior as today (empty containers → existing failure branches).

2. Do **not** add new company states or transitions.

3. **build-child stops** if `tests/component/core/test_roster.py` classes covering **TestParseJobListDispatch** (AST-721), **TestSelectJobPageDispatch** (AST-720), and **TestMakeLocateParseResolver** (AST-469) fail after Stage 1–4 — fix product code only; do not edit tests.

---

## Self-Assessment

**Scope:** `Single-Component` — roster parse/select handoff in `src/core/roster.py` plus one formatting helper; no config, UI, or agent prompt changes.

**Conf:** `Medium` — root cause matches missing/ineffective title-driven cull on decomposed parse hop; `_culled_dom_for_parse` + Phase 2b directly address Susan's single-anchor repro, but live medicarerights DOM may need spike confirmation during build Stage 3.

**Risk:** `Medium` — incorrect cull validation could increase `PARSE_DISPATCH_NO_CONTAINERS` retries on edge-case pages; mitigated by keeping single-title full-DOM behavior and unchanged failure state machine.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Shared `_culled_dom_for_parse` replaces three duplicated cull call sites. |
| §2.1 config | No new inline state lists; uses existing `ROSTER_CONFIG` keys and `job_titles` / `selected_pjl_url`. |
| §2.4 batch | Parse dispatch remains per-entity in existing batch runner — no batch shape change. |
| §2.6 state machine | Failure paths reuse `PARSE_DISPATCH_NO_CONTAINERS`, `JOBLIST_IDENTIFIED_RETRY`, `COULD_NOT_PARSE_JOBLIST` — no new transitions. |
| §3.3 imports | Helper stays in roster; formatting import unchanged (roster already imports `find_job_containers`). |
| §3.5 naming | `_culled_dom_for_parse`, `_normalize_job_titles`, `_dom_text_covers_titles` follow existing roster private helper style. |
| §1.5.1 debug | New lines gated on `debug=True` only; uses `debug_index` / `debug_detail`. |

No conflicts requiring escalation.

---

## Execution contract (for the developer agent)

- Execute stages 1→5 in order; one commit per stage on epic worktree; publish each to `origin/sub/AST-824/AST-827-title-handoff-dom-cull` before the next stage.
- Do not edit `tests/` or `docs/test-bible/**` — Betty owns test manifest in **qa-child**.
- If medicarerights live repro still fails after Stage 4 with `cull_outcome=culled` and both titles in `dom_joined`, stop and comment on **AST-824** with execution-history snippet — do not change AST-689 readiness waits without Susan.
