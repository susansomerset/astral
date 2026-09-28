<!-- linear-archive: AST-827 archived 2026-07-22 -->

## Linear archive (AST-827)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-827/title-handoff-and-dom-culling-for-parse-job-list-get-parse-job-list-to  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-824 — Get parse_job_list to work  
**Blocked by / blocks / related:** parent: AST-824

### Description

## What this implements

Restore the decomposed roster handoff between **select_job_page** and **parse_job_list**: job titles Grace returns on the **PJL_READY** path must persist in company data for the parse hop, and **parse_job_list** dispatch must use those titles to trim rescraped careers-list DOM so the parsing agent receives a structurally complete listing fragment (all titles), not an isolated job link. Include backend debug traceability on the parse dispatch path and preserve existing failure/retry semantics.

## Acceptance criteria

1. Susan re-runs the [medicarerights.org](<http://medicarerights.org>) careers repro (**PJL_READY → select_job_page → JOBLIST_IDENTIFIED → parse_job_list**): after **JOBLIST_IDENTIFIED**, company data contains **both** job titles returned by select; Execution History for the **parse_job_list** hop shows live content that includes listing markup for **both** titles (not a lone `<a>` for the first job only).
2. On that repro, **parse_job_list** succeeds: company reaches **WATCH**, `job_site` is the selected careers URL, and `parse_instructions` (container, job_tag, container_index) is persisted and validates against the culled DOM.
3. A `debug=True` parse dispatch on the same repro logs title count, pre-cull and post-cull DOM sizes, and a clear cull outcome under the parse dispatch index header.
4. Existing component coverage for decomposed **select_job_page** / **parse_job_list** dispatch (AST-720/721) remains green; add or extend tests that lock title persistence and multi-title cull input when two titles are saved.
5. **JOBS_FOUND** re-parse smoke: a company with stored **job_site** that previously completed select→parse chaining still reaches **WATCH** when listings are present (no regression).

## Boundaries

* Does **not** change **select_job_page** or **parse_job_list** agent prompt prose.
* Does **not** reintroduce monolithic **find_job_page** dispatch or alter **fetch_job_pages** scrape batch behavior.
* Does **not** change careers-list readiness waits (AST-689) beyond existing parse DOM reload wiring.
* Does **not** broaden scope to unrelated roster states (**vet_inflow_discovery**, prefilter, gaze JD scrape).

## Notes for planning

* Primary files: `src/core/roster.py` (decomposed select finalize + `run_parse_job_list_dispatch`), possibly `src/utils/formatting.py` (`find_job_containers`).
* Susan's repro: [medicarerights.org](<http://medicarerights.org>) careers — two titles in select response, parse hop received only first job anchor.
* AST-720/721 shipped the decomposed hops; this fixes the title/cull handoff gap.
* Debug contract: AST-538 / Code Rules §1.5.1 on touched `debug=` paths.

## Git branch (authoritative)

Per **orientation** § Branch law: parent `ftr/AST-824-get-parse-job-list-to-work`, child `sub/AST-824/<child-id>-title-handoff-dom-cull`. Created at dispatch-parent.

### Comments

#### radia — 2026-06-26T18:31:06.950Z
### Review — `origin/dev...origin/sub/AST-824/AST-827-title-handoff-dom-cull` @ `40e774a`

**fix-now:** none — clean sign-off for `resolve-child`.

**discuss:** Plan Self-Assessment Conf **Medium** — medicarerights live DOM still needs parent **AST-824** UAT on staging; component sibling-anchor repro is green but is not a substitute for live listing confirmation.

**advisory:**
- `run_parse_job_list_dispatch` (~1234–1290): plan Stage 3 asked for `cull={cull_outcome}` on the **debug_index** outcome; implementation adds `cull=` only on terminal **debug_detail** (index header still url/titles/state only).
- `_culled_dom_for_parse` (~126–134): single-title path runs `find_job_containers` vs plan stub’s raw full-DOM shortcut — matches pre-ticket parse behavior; improvement, not regression.

**Solid:** shared `_culled_dom_for_parse` + `_normalize_job_titles`; post-cull coverage gate; Phase 2b sibling anchors; JOBS_FOUND chain parity; §1.5.1 debug gated on `debug=True`; failure ladder unchanged.

**Doc:** `docs/features/roster/ast-827-title-handoff-dom-cull.md` § Radia review (2026-06-26)

#### betty — 2026-06-26T18:28:07.522Z
## QA test manifest (AST-827)

**Publish ref:** `origin/sub/AST-824/AST-827-title-handoff-dom-cull` @ `fe754bb` (`merge-tests(AST-827): origin/tests 0a2890d`)

**Bible shasum (publish ref):**
- `docs/test-bible/core/roster.md`: `696477ca0264ba1ba1fd916a0f49c71bac49ce24bd0ed6a1f0dde82766f7d3db`
- `docs/test-bible/utils/formatting.md`: `fa1d00ec20c4d1c1944c105766e2f3598e05aacbb647249135f7836560e2e130`

1. **Two-title JOBLIST_IDENTIFIED persistence** — `tests/component/core/test_roster.py::TestAst827TitleHandoffDomCull::test_finalize_joblist_identified_persists_two_titles` (`_normalize_job_titles` strips blanks; saves full list + `selected_pjl_url`).

2. **Parse dispatch multi-title culled DOM** — `::TestAst827TitleHandoffDomCull::test_parse_dispatch_passes_multi_title_culled_dom` (sibling-anchor DOM; both titles in DOM passed to `_fetch_parse_job_list`).

3. **Coverage failure → PARSE_DISPATCH_NO_CONTAINERS** — `::TestAst827TitleHandoffDomCull::test_parse_dispatch_cull_miss_no_containers`; helper `::test_culled_dom_for_parse_cull_miss_when_titles_absent`.

4. **JOBS_FOUND chain / resolver regression** — `::TestAst827TitleHandoffDomCull::test_make_locate_parse_resolver_two_title_sibling_cull`; existing `TestAst469LocateParseResolver`, `TestMakeLocateParseResolver469`.

5. **Formatting Phase 2b sibling anchors** — `tests/component/utils/test_formatting.py::TestFindJobContainers::test_sibling_anchor_links_two_titles`.

**Narrowed run (test-child):**

```bash
./scripts/testing/run_component_tests.sh   tests/component/core/test_roster.py::TestAst827TitleHandoffDomCull   tests/component/core/test_roster.py::TestAst469LocateParseResolver   tests/component/core/test_roster.py::TestMakeLocateParseResolver469   tests/component/utils/test_formatting.py::TestFindJobContainers::test_sibling_anchor_links_two_titles   -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

#### hedy — 2026-06-26T18:23:14.032Z
Plan: `https://github.com/susansomerset/astral/blob/sub/AST-824/AST-827-title-handoff-dom-cull/docs/features/roster/ast-827-title-handoff-dom-cull.md`

**Scope:** Single-Component — `roster.py` title→DOM cull handoff plus `formatting.find_job_containers` sibling-anchor fix; no config/UI/prompt changes.

**Conf:** Medium — shared `_culled_dom_for_parse` + post-cull title coverage directly targets Susan's single-anchor medicarerights repro; live DOM may need spike confirmation during build.

**Risk:** Medium — stricter cull-miss rejection could increase `PARSE_DISPATCH_NO_CONTAINERS` on edge pages; single-title full-DOM path unchanged.

---

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

---

## Review stub (build-child)

**Built:** `code(AST-827)` on `origin/sub/AST-824/AST-827-title-handoff-dom-cull` — shared `_culled_dom_for_parse` / title normalization, select finalize debug, parse dispatch coverage gate, `find_job_containers` Phase 2b sibling anchors, JOBS_FOUND chain parity.

---

## Radia review (2026-06-26)

**Diff:** `origin/dev...origin/sub/AST-824/AST-827-title-handoff-dom-cull` (`fe754bb`)

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity | Stages 1–5: `_normalize_job_titles` at finalize + parse load; shared `_culled_dom_for_parse` with post-cull `_dom_text_covers_titles` gate; `make_locate_parse_resolver`, `run_parse_job_list_dispatch`, and JOBS_FOUND finalize paths all route through the helper; Phase 2b sibling-anchor cull in `find_job_containers`. |
| State machine (§2.6) | No new transitions — `PARSE_DISPATCH_NO_CONTAINERS` / `JOBLIST_IDENTIFIED_RETRY` / `CANNOT_PARSE_JOB_SITE` / `NO_JOBLIST` reuse existing branches. |
| DRY (§1.3) | Three duplicated cull call sites collapsed; orchestration vs formatting split matches plan (coverage in roster, best-effort containers in utils). |
| Debug (§1.5.1) | New emission gated on `debug=True`; `debug_index` on select finalize and parse dispatch entry; `debug_detail` for title list, pre/post cull sizes, terminal `cull=` on success path. |
| Layering (§3.3) | Helpers stay in `roster.py` / `formatting.py`; no UI or external imports. |
| Tests / bible | Betty manifest (`TestAst827TitleHandoffDomCull`, formatting sibling-anchor case) matches plan AC matrix; AST-469/721 regression classes listed in bible narrowed run. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **advisory** | `run_parse_job_list_dispatch` ~1234–1290 | Plan Stage 3 asked for `cull={cull_outcome}` on the **debug_index** outcome string; implementation adds `cull=` only on terminal **debug_detail**. Index header still shows url/titles/state only — operators scanning headers miss cull outcome without scrolling detail. |
| **discuss** | Plan Self-Assessment | Conf **Medium** — medicarerights live DOM may still need parent **AST-824** UAT even when component repro is green. Not a code defect; confirm on staging before closing parent. |
| **advisory** | `_culled_dom_for_parse` ~126–134 | Single-title path runs `find_job_containers` (plan stub showed raw full DOM). Matches pre-ticket parse dispatch behavior and is safer than blind full-DOM pass — intentional improvement, not regression. |

### Recommended actions

| Item | Action |
|------|--------|
| fix-now | None — ready for `resolve-child`. |
| discuss | Parent UAT on medicarerights (or equivalent two-title sibling-anchor listing) after merge to staging. |
| advisory | Optional: append `cull={cull_outcome}` to parse dispatch `debug_index` outcome when touching debug again. |

**Publish tip:** `fe754bb` (product `703fd35` + tests `0a2890d` + merge-tests `fe754bb`)

---

## Resolution (2026-06-26)

**Radia:** clean sign-off — no fix-now items.

| Item | Outcome |
|------|---------|
| fix-now | None applied — product unchanged at resolve. |
| discuss | medicarerights / two-title live listing confirmation deferred to parent **AST-824** UAT on staging. |
| advisory | `debug_index` `cull=` omission left as-is (Radia advisory only); single-title `_culled_dom_for_parse` path retained. |

**Publish tip at resolve:** `origin/sub/AST-824/AST-827-title-handoff-dom-cull` @ Radia review `40e774a`; §9a dry-run clean vs `origin/dev` and `origin/ftr/AST-824-get-parse-job-list-to-work`.

---

## Bug: AST-1840 — parse_job_list DOM cull blocks event loop on oversized pages; snip long attributes

**Parent:** AST-1838 (orphaned bug mini-parent, `ftr/AST-1838-parse-job-list-event-loop-block`). **Publish ref:** `origin/sub/AST-1838/AST-1840-parse-job-list-event-loop-block`. **Scope:** AST-1840 `## Scope`, amended by Susan 2026-09-28 ("amend as written") after the `[scope-gate]` finding below.

### As-is

A production `parse_job_list` batch (candidate abrams, 20 companies) froze the dispatcher's event loop for 2h05m. Telescope returned `jobs.volvogroup.com` (raw HTML ≈ 7.4MB, `visible_chars` 3,149,938) at 10:28:04, and the next log line was at 12:33:26. The 3600s dispatch `wait_for` fired an hour late at 12:34:30, and the batch ended INTERRUPTED with 0 processed. Volvo's first `Response from _culled_dom_for_parse` is logged at 12:33:26, so the block sits between `scrape_page` returning and the end of the title cull.

### To-be

One oversized careers page cannot freeze the dispatcher. Neither the html cull (`_cull_html`) nor the title cull (`_culled_dom_for_parse` → `find_job_containers`) runs on the event loop, and both are roughly linear on large DOMs. Dispatch timeouts and provider budgets (AST-1189) fire on schedule, and the rest of the batch still gets processed. The heavy company either culls or fails through the existing `_save_parse_dispatch_failure` / retry-strike path (AST-891). Attribute values longer than 500 chars are replaced with `(snipped)`. **No DOM-size guard** (Susan, 2026-09-28).

### Repro

No stored Volvo HTML exists; the log omits the 7.4MB body. Use a synthetic listing fixture (bs4 4.15, real `html_cull` config):

```python
row = ('<li class="job-row" data-automation-id="job"><div class="c1"><div class="c2">'
       '<h3><a href="/job/E_%d" data-x="%s">Engineer %d</a></h3></div>'
       '<button><i>x</i></button><span class="loc">Pittsburgh</span>'
       '<svg viewBox="0 0 10 10"><g><path d="M0 0L10 10"></path></g></svg></div></li>')
html = ('<html><body><div id="app"><ul>'
        + ''.join(row % (i, 'A' * 200, i) for i in range(N)) + '</ul></div></body></html>')
_cull_html(html)
```

| N rows | chars | `_cull_html` today | after the `_in_preserved_svg` fix |
|---|---|---|---|
| 100 | ~45K | 1.5s | — |
| 400 | ~180K | 23.5s | — |
| 1,000 | 450K | **144s** | 0.57s |
| ~14,000–16,000 | ~7MB | **> 15 min (killed)** | 9.6s |

`find_job_containers` on a 1.1MB listing takes 1.4s today (about the same at depth 5 or depth 30). Estimated about 10s for Volvo: slow and on the loop, but not the 2h.

### Root cause

1. **`_cull_html` is quadratic, and it runs on the event loop.** `_in_preserved_svg` (AST-1745, `a830d0f0`) tests `elem in preserve_root_svgs` and `p in preserve_root_svgs for p in elem.parents`. bs4's `Tag.__hash__` is `hash(str(self))`, so every membership test serializes that ancestor's whole subtree, the document root included, **even when the set is empty**. It is called once per `<svg>` and once per non-allowed tag in each of the up-to-10 unwrap passes, so a page with thousands of icons or buttons pays O(document size) for each one. Profile: ~99% of the time is in `Tag.decode`. It runs synchronously inside async `extract_page_dom`, which is called from `_scrape_list_page_dom_for_parse` before `_culled_dom_for_parse`. **This is the 2h freeze.**
2. **`_culled_dom_for_parse` runs synchronously inside three coroutines.** `find_job_containers` calls `el.get_text()` for every descendant in Phase 1 and Phase 2, plus descendant scans for "deepest" and "leaves", costing O(n × depth). That is seconds per MB on the loop.
3. Contributing: large inline attribute payloads inflate the DOM that both culls walk and that reaches the LLM (Susan's read, 2026-09-28).

### Proposed change

Five edits, all inside AST-1840 `## Scope`. `make-fix` runs them in order and compiles and lints after each.

**1. `src/utils/config.py` — `ASTRAL_CONFIG["html_cull"]`:** add two keys after `"strip_on_attrs": True,`:

```python
        "max_html_tag_length": 500,            # AST-1840: attribute values longer than this are snipped
        "max_length_placeholder": "(snipped)", # AST-1840: replacement text, so snipped spots stay visible
```

**2. `src/external/telescope.py` — `_cull_html`:**

- (a) Fail fast, same pattern as the existing required keys (no in-code defaults):
  ```python
  if "max_html_tag_length" not in html_cull_config:
      raise ValueError("ASTRAL_CONFIG['html_cull']['max_html_tag_length'] is missing")
  if "max_length_placeholder" not in html_cull_config:
      raise ValueError("ASTRAL_CONFIG['html_cull']['max_length_placeholder'] is missing")
  ```
  Read both into locals next to `strip_on_attrs`: `max_attr_len = int(html_cull_config["max_html_tag_length"])` and `snip_placeholder = html_cull_config["max_length_placeholder"]`.
- (b) Identity-based `_in_preserved_svg`. Keep `preserve_root_svgs` as the collection of root svg Tags, but build `preserve_root_ids = {id(s) for s in preserve_root_svgs}` right after it is filled, and replace the helper body:
  ```python
  def _in_preserved_svg(elem) -> bool:
      # id() only: bs4 Tag.__hash__ serializes the subtree, which made this quadratic
      if not preserve_root_ids:
          return False
      if id(elem) in preserve_root_ids:
          return True
      return any(id(p) in preserve_root_ids for p in getattr(elem, "parents", []))
  ```
  Using ids is safe because preserved roots stay attached to the tree for the whole call, and are never decomposed or unwrapped. The output was verified byte-identical to today on a 150-row listing and on the AST-1745 root `svg.logo` fragment.
- (c) Snip. In the final `for elem in elements_to_process:` loop, directly after `for attr in attrs_to_strip: del elem.attrs[attr]`:
  ```python
  # AST-1840: over-long values (inline binary/base64 payloads) → visible placeholder
  for attr, val in list(elem.attrs.items()):
      flat = " ".join(val) if isinstance(val, list) else str(val)
      if len(flat) > max_attr_len:
          elem.attrs[attr] = snip_placeholder
  ```
  Multi-valued attributes (bs4 lists, e.g. `class`) are measured by their serialized `" "`-joined length and replaced by the plain placeholder string. The check is strictly greater than: a 500-char value is kept, a 501-char value is snipped.

**3. `src/external/telescope.py` — `extract_page_dom`:** replace `return _cull_html(raw_html)` with:

```python
        return await asyncio.to_thread(_cull_html, raw_html)
```

`asyncio` is already imported. The global name is looked up at call time, so monkeypatched `_cull_html` in tests still applies. The admin workbench `_cull_html` calls (~lines 629/631) **stay out of scope** (Susan, 2026-09-28).

**4. `src/core/roster.py` — three call sites.** `_culled_dom_for_parse` stays a pure sync function. Each call becomes:

- `run_parse_job_list_dispatch._scrape_and_parse`: `dom_joined, containers, cull_outcome = await asyncio.to_thread(_culled_dom_for_parse, dom_html, job_titles)`. The `nonlocal cull_outcome` still binds through tuple unpacking.
- `_finalize_joblist_titles_after_chain`: `dom_joined, _, cull_outcome = await asyncio.to_thread(_culled_dom_for_parse, dom_html, job_titles)`
- `_finalize_joblist_titles_select_only`: same as the previous line.
- `make_locate_parse_resolver.resolve_run_next_live` **stays sync** (it's a sync callback inside `agent.do_task`, per scope).

**5. `src/utils/formatting.py` — `find_job_containers`:** same signature, same docstring contract, same return values. Add `from bisect import bisect_left` to the module imports, and extend the lazy import to `from bs4 import BeautifulSoup, CData, NavigableString, Tag`. The body is replaced as follows. Everything from the `if not job_titles` guard through `titles_set` is unchanged, as is everything from `checked: set = set()` (the Phase 2 walk-up) through the final `return [dom_html]`, Phase 2b included. The only change inside the walk-up is that `_titles_in` is now a cached lookup. Keep the existing `# pragma: no cover` markers on the Phase 2 / 2b lines.

```python
    # One ordered walk: every stripped main-content string, lowercased, " "-joined into `text`.
    # Each Tag gets a [start, end) char span so text[start:end] == el.get_text(" ", strip=True).lower().
    # Tags whose own get_text reads a special string type (script/style/template/rt/rp) fall back below.
    special = set(getattr(soup.builder, "string_containers", {}) or {})
    pieces: List[str] = []
    offset = 0
    span: dict = {}
    stack: list = [("enter", soup)]
    while stack:
        op, node = stack.pop()
        if op == "exit":
            span[id(node)] = (span[id(node)], offset)
            continue
        if op == "str":
            txt = node.strip().lower()
            if txt:
                if pieces:
                    offset += 1  # the joining " "
                pieces.append(txt)
                offset += len(txt)
            continue
        span[id(node)] = offset + (1 if pieces else 0)  # where this tag's first piece would start
        stack.append(("exit", node))
        for child in reversed(node.contents):
            if isinstance(child, Tag):
                stack.append(("enter", child))
            elif type(child) in (NavigableString, CData):  # exact types: get_text's default filter
                stack.append(("str", child))
    text = " ".join(pieces)

    # Every (overlapping) occurrence start of each title in `text`, ascending.
    occ = {}
    for t in titles_set:
        hits, p = [], text.find(t)
        while p != -1:
            hits.append(p)
            p = text.find(t, p + 1)
        occ[t] = hits

    cache: dict = {}

    def _titles_in(el: Tag) -> set:
        key = id(el)
        if key in cache:
            return cache[key]
        if el.name in special:
            txt = el.get_text(" ", strip=True).lower()
            found = {t for t in titles_set if t in txt}
        else:
            s, e = span[key]
            found = set()
            for t, hits in occ.items():
                i = bisect_left(hits, s)
                if i < len(hits) and hits[i] + len(t) <= e:
                    found.add(t)
        cache[key] = found
        return found

    tags = [el for el in soup.descendants if isinstance(el, Tag)]

    # Reverse pre-order visits every descendant before its ancestor → O(n) "any match below" flags.
    all_below: dict = {}
    any_below: dict = {}
    for el in reversed(tags):
        kids = [ch for ch in el.children if isinstance(ch, Tag)]
        all_below[id(el)] = any(_titles_in(ch) == titles_set or all_below[id(ch)] for ch in kids)
        any_below[id(el)] = any(bool(_titles_in(ch)) or any_below[id(ch)] for ch in kids)

    # Phase 1: single element containing ALL titles → filter to deepest
    all_match = [el for el in tags if _titles_in(el) == titles_set]
    if all_match:
        deepest = [c for c in all_match if not all_below[id(c)]]
        if deepest:  # pragma: no branch
            return [str(el) for el in deepest]

    # Phase 2: accumulate across siblings
    partial = [(el, _titles_in(el)) for el in tags if _titles_in(el)]  # pragma: no cover
    if not partial:  # pragma: no cover
        return [dom_html]  # pragma: no cover
    leaves = [(el, ts) for el, ts in partial if not any_below[id(el)]]  # pragma: no cover
    # ... existing walk-up + Phase 2b unchanged from `checked: set = set()` onward ...
```

Why this is exact, not an approximation:
- `get_text(" ", strip=True)` joins the stripped, non-empty strings of the allowed types in document order. A tag's strings are a contiguous run of that document-wide sequence, so its text is exactly `text[start:end]`.
- Substring membership (`t in text`) becomes "some occurrence starts at or after `start` and ends at or before `end`". Titles that span child boundaries or contain spaces still match.
- Lowercasing each piece separately equals lowercasing the joined text, because pieces are space-separated. This also avoids offset drift from characters whose lowercase form is longer, such as `İ`.
- The "deepest" and "leaves" checks use exact descendant flags, not a monotonicity shortcut. `template`, `rt`, and `rp` can match titles their parent's text excludes, and a children-only shortcut failed 19 of 6,000 fuzz cases because of that.

Verified with a `/tmp` prototype of exactly this body:
- 30,000 random DOMs (nested `script`/`style`/`template`/`rt`/`rp`, comments, CDATA, Unicode such as `İ`/`ΟΔΟΣ`/`Straße`, blank titles, overlapping titles): **0 mismatches** against today's function.
- The medicarerights sibling-anchor shape and a 4.5MB depth-30 listing return identical containers.
- The existing `TestFindJobContainers` tests: 6/6 pass with the prototype swapped in.

⚠️ **Decision — the gain is modest; being off the loop is what matters.** On shallow synthetic DOMs, today's function is already about 1.3–1.6s per MB, and the rewrite is about 1.2s per MB (both dominated by bs4 parsing). The rewrite removes the O(n × depth) term, which matters on deep real-world DOMs. The actual protection is edit 4 (`to_thread`).

### Blast radius

- **`extract_page_dom` callers:** `roster._scrape_list_page_dom_for_parse` (parse hop), `roster.py` ~2560, `gazer.py` ~875 (JD body scrape), and telescope's own `get_page_dom` wrappers (~997–1009). All are async and already `await` it, so offloading the cull changes nothing about their contract. They all get the linear `_cull_html` and the snip.
- **Every `_cull_html` consumer gets the snip,** including the gazer JD DOM and the admin path (the admin *call sites* are untouched, but the function is shared). Any stored or cached culled HTML produced before the fix differs from what new culls produce, only where an attribute value was longer than 500 chars.
- ⚠️ **Decision (applied as Susan specified, not exempted):** AST-1745 preserved root `svg.logo` fragments also go through the attribute loop. A real logo whose `<path d="…">` is longer than 500 chars will have that `d` replaced with `(snipped)`, and the logo will no longer render from the captured outerHTML. The AST-1745 test fixtures only use short paths, so those tests stay green. I have **not** added an exemption for preserved-svg subtrees, because Susan's rule is "any tag attribute value" and no-heuristics-without-confirmation applies. If fix-board or Susan wants logos kept whole, the one-line exemption is `if _in_preserved_svg(elem): continue` before the snip loop.
- **Threads:** a timed-out dispatch cancels the awaiting coroutine immediately. The worker thread keeps running until the cull returns (Python threads can't be killed). With both culls linear, that's seconds, and the GIL switch interval keeps the loop responsive meanwhile. `_cull_html` and `_culled_dom_for_parse` share no mutable state across calls, so running them concurrently in threads is safe.
- **Tests that may need Betty** (not touched here):
  - `tests/component/core/test_roster.py`: tests that monkeypatch `find_job_containers` / `_culled_dom_for_parse` keep working, because names are resolved at call time inside the thread. Scope also asks for one new non-blocking assertion there.
  - `tests/component/utils/test_formatting.py`: needs the large-DOM equivalence/performance case.
  - `tests/component/external/test_telescope.py`: may need snip coverage; `extract_page_dom` tests that assert a sync call to `_cull_html` would need awaiting.
- **Out of scope — poller "Task was destroyed but it is pending" (investigate-only):** this **survives** this fix. It fired at 10:25:55, *before* the freeze, together with an orphaned `to_thread` task. `dispatcher._task_thread_target` calls `loop.close()` without cancelling pending tasks, so the per-loop `telescope-result-poller` (`telescope.py:278`) and any AST-1189 budget-timeout orphan (`llm_external.py` deliberately doesn't await it) are garbage-collected while still pending. Chuckles files this separately.

### What must still hold

- **AST-827:** `_culled_dom_for_parse` return shape `(dom_joined, containers, outcome_label)` and labels `no_titles | full_dom | culled | cull_miss` are unchanged. Coverage gate, `PARSE_DISPATCH_NO_CONTAINERS`, `CANNOT_PARSE_JOB_SITE` / `NO_JOBLIST` branches, and the JOBS_FOUND chain via `make_locate_parse_resolver` are all unchanged.
- **`find_job_containers` returns the same containers as today** on every existing fixture: Phase 1 deepest, Phase 2 sibling union, Phase 2b sibling anchors, and the `[dom_html]` fallback. Only cost changes, not semantics (AST-1840 scope).
- **AST-1745:** a root `svg.logo` class-scoped fragment keeps its outerHTML (short attributes). Nested decorative svgs under page content are still stripped.
- **AST-891:** a batch finishes every claimed company. A slow or failing company fails through `_save_parse_dispatch_failure` / retry-strike, and the dispatch timeout never sits an extra hour.
- **AST-1189:** per-call provider budgets fire on schedule, because the loop is never held by a cull.
- **No DOM/page size cap, no truncation, no limit** beyond the 500-char attribute snip (Susan, 2026-09-28). The existing `max_passes = 10` unwrap loop in `_cull_html` is pre-existing and untouched.
- `html_cull` keys stay required config. Missing `max_html_tag_length` / `max_length_placeholder` raises `ValueError`, same as the other keys.


## Joan fix-board (AST-1840)

Fix-board Joan triage for **AST-1840** against the plan-fix patch on `origin/sub/AST-1838/AST-1840-parse-job-list-event-loop-block` and the in-force corpus via `canon/docs/DIRECTIVES-DIRECTORY.md` (no `docs/canon-index.md` on this ref).

**Assessment:** The change adds `html_cull` keys in `config.py` with required-key `ValueError` checks (`astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`). DOM work moves to `asyncio.to_thread` in external/core without crossing the core/external I/O line. `find_job_containers` semantics stay a product/plan contract (AST-827 / AST-1840 scope), not a harvested statute. HARVEST notes §3.4 html-cull has no statute beyond config-source-of-truth. AST-1745 SVG behavior is feature AC in “What must still hold,” not an active directive; Susan already chose global attribute snip over a preserved-svg carve-out in the patch. No statute update or Archie precedent gate.

BEGIN-VERDICT
```
[board-joan]  CANON: OK
```
END-VERDICT

```text
AST-1840 board-joan done — CANON: OK.
```


## Radia review-fix (AST-1840)

Review for **AST-1840** — diff `origin/ftr/AST-1838-parse-job-list-event-loop-block...origin/sub/AST-1838/AST-1840-parse-job-list-event-loop-block`, tip `fb472a989b21bc372118bf3b310a45d89c525ef8`. Status gate: **Tests Passed** (trusted). Product-only diff (no `tests/**`); qa-fix did not run; `[bug-repro]` deferred to sibling **AST-1844**.

---

```
[code-rubric]
**Ticket:** AST-1840
**Publish ref:** `fb472a989b21bc372118bf3b310a45d89c525ef8` (`origin/sub/AST-1838/AST-1840-parse-job-list-event-loop-block`)
**Corpus:** `edcd401473615509c180c015cd18b4472dfba94a` (tree at publish ref; no `docs/canon-index.md` on this ref — resolved ids from `canon/statutes/**` on same tip)
**Overall:** CLEAN

## Canon scores

Scored list: Linear Description has **no** `Canon Scope (frozen at plan)` block. Per fix-lane precedent (e.g. AST-1821), scored **fix-board Joan overlap** from the plan-fix patch / `## Joan fix-board (AST-1840)`:

| # | slug | grade | effort | one-line |
|---|------|-------|--------|----------|
| 1 | `astral.config.config-source-of-truth` | A | | `max_html_tag_length` / `max_length_placeholder` added to `ASTRAL_CONFIG["html_cull"]`; `_cull_html` reads them with same required-key `ValueError` pattern as existing `html_cull` keys |
| 2 | `astral.standards.no-hardcoded-sets` | A | | 500 / `"(snipped)"` not inlined in `telescope.py`; snip threshold and placeholder come from config |

**Notes (Canon Scope):** Missing frozen list on the bug ticket is a **process gap for Archie** (comparability with feature children), not a product defect on this tip. No off-list statute plainly violated without being named by Joan; no **ESCALATE** for scope gap.

## Column diff vs plan stage

`no plan-stage scores attached` (no `validate-plan` fix-mode column in issue doc or comments; only `[board-joan] CANON: OK`).

## Frame diff

(none)

## Fix-specific checks

- **`[bug-repro]`:** not applicable — clean board opt-out for this tip; Betty’s **TESTS: REVISE** and repro coverage owned by sibling **AST-1844**; no `[bug-repro]` on this diff.
- **`## What must still hold`:** **OK** — traced against diff:
  - **AST-827:** `_culled_dom_for_parse` body untouched; three async call sites use `await asyncio.to_thread(...)` only; return shape / outcome labels / downstream branches unchanged; `make_locate_parse_resolver` stays sync (not in diff).
  - **`find_job_containers`:** signature, fallbacks, Phase 2 walk-up / 2b from `checked: set = set()` onward unchanged; Phase 1/2 “deepest” / “leaves” refactored via span cache + `all_below` / `any_below` per plan (semantics contract; equivalence not re-proven in-repo on this tip).
  - **AST-1745:** identity `_in_preserved_svg` matches plan; **global** attribute snip (no preserved-SVG exemption) per Susan 2026-09-28 — long `d` on preserved logo may snip; plan documents that tradeoff.
  - **AST-891 / AST-1189:** `_cull_html` and `_culled_dom_for_parse` off event loop via `extract_page_dom` + roster `to_thread` — matches to-be.
  - **No DOM-size guard:** no cap added.
  - **Required config keys:** fail-fast `ValueError` for missing new keys.
  - **Admin workbench ~629/631:** still synchronous `_cull_html` (out of scope; verified on tip).

## Findings

**fix-now:** none

**discuss:** none

**advisory:**
- **Test debt / sibling carry:** Linear `## Scope` still lists `test_formatting` / `test_roster` changes; this tip is **product-only**; fix-board **TESTS: REVISE** → **AST-1844**. Radia does not block product on absent tests here.
- **Semantic proof for `find_job_containers`:** plan-fix documents 30k fuzz / prototype parity; touched-area pytest **30/30** per engineer comment; no landed repro test on this branch until AST-1844.
- **AST-1745 vs snip:** preserved root `svg.logo` with attribute values **>500** chars will show `(snipped)` in captured HTML — accepted per Susan binding; fixtures use short paths.
- **Blast radius:** all `extract_page_dom` consumers get linear `_cull_html` + snip in thread; gazer JD path included (intended).
- **Poller “Task was destroyed but it is pending”:** plan correctly leaves investigate-only; not fixed here.

## What's solid

- Root-cause fix landed: `_in_preserved_svg` `id()` set ends quadratic `Tag.__hash__` / `decode` behavior; matches scope-gate measurements narrative.
- `asyncio.to_thread` at the three roster parse-finalize sites and in `extract_page_dom` — minimal, consistent with plan order.
- Snip loop runs on **every** attribute after strip pass (`> max_html_tag_length`, strict `>`), lists joined with space — matches plan and Susan’s “every attribute” rule.
- `asyncio` already imported in `roster.py`; monkeypatch-friendly `to_thread` lookup for `_culled_dom_for_parse` / `_cull_html`.

## Chuckles — post-review branching

| Gate | Parent shape | Next action |
|------|----------------|-------------|
| **PROCEED** (this review) | **Orphaned mini-parent AST-1838** (per intake) | **Review Posted** → **do-all-the-things §3h** clean shortcut → **User Testing**; **skip `resolve-child`**. Do **not** `merge-child` / `prep-uat`; when UT-ready, land **`sub/AST-1838/AST-1840-…` → `origin/dev`** finish-up-style. |
| If findings later | same | **Review Posted** → `resolve-child` on sub → then dev merge |

context_tokens≈N
```

#### Chuckles disposition (AST-1840)

Clean review: Review Posted → User Testing (resolve-child skipped). Docs-acceptance on this tip: the test/bible delivery is sibling gap AST-1844 (Betty's `[board-betty] TESTS: REVISE`). merge-child goes into this bug's own `ftr/AST-1838-parse-job-list-event-loop-block` (orphaned mini-parent), not straight to dev.

---

## Bug: AST-1844 — test gap: `_cull_html` linear-time repro, attribute snip, `find_job_containers` equivalence, off-loop culls

**Parent:** AST-1838. **Answers:** `[board-betty] TESTS: REVISE` on AST-1840. **Product under test:** AST-1840 @ `fb472a98` on `origin/sub/AST-1838/AST-1840-parse-job-list-event-loop-block` (its plan section `## Bug: AST-1840` lands in this doc when that sub merges to ftr). **Publish ref:** `origin/sub/AST-1838/AST-1844-parse-job-list-event-loop-block-tests`. **Test and bible only:** Betty lands every node at qa-fix; no product code here.

### As-is

Nothing in the component suite exercises the 2h event-loop freeze or the new attribute snip. `TestCullHtmlDefault`, AST-1745, AST-827, and `TestFindJobContainers` all pass on both the pre-fix and post-fix trees, so they can't tell the fix happened. On `fb472a98`, three branches of the rewritten `find_job_containers` are uncovered in `src/utils/formatting.py` (a LOCKED_AT_100 file): `345→350` (whitespace-only string), `356→353` (comment / non-main string node), and `375→376/377` (special-string-container fallback).

### To-be

A deterministic `[bug-repro]` set that is **red on the pre-fix product** (`origin/ftr/AST-1838-parse-job-list-event-loop-block` @ `31846c28`) and **green on `fb472a98`**. It pins the root cause (Tag hashing in `_cull_html`) and all four off-loop call sites. Snip and missing-key behavior are covered. `find_job_containers` equivalence fixtures are **green on both trees** (same containers, cost-only change) and close the three uncovered branches. No timing or wall-clock assertions, and no size caps.

### Repro

Every node below was verified with a throwaway probe (`/tmp`, not a test file) that ran the planned assertions against both trees, using `/home/susan/astral/.venv/bin/python` (bs4 4.15):

| Probe check | `31846c28` (pre-fix) | `fb472a98` |
|---|---|---|
| Full-page `_cull_html` with `Tag.__hash__` patched to raise | FAIL (`Tag.__hash__ called`) | PASS |
| Snip 500 kept / 501 snipped / list `class` snipped | FAIL | PASS |
| Missing `max_html_tag_length` / `max_length_placeholder` → `ValueError` | FAIL (`KeyError` at `delitem`) | PASS |
| `extract_page_dom` runs `_cull_html` off the loop thread | FAIL | PASS |
| `run_parse_job_list_dispatch` runs `_culled_dom_for_parse` off the loop thread | FAIL | PASS |
| `_finalize_joblist_titles_after_chain` off the loop thread | FAIL | PASS |
| `_finalize_joblist_titles_select_only` off the loop thread | FAIL | PASS |
| 6 `find_job_containers` fixtures + 8,000-row DOM | same output | same output |
| `formatting.py` 330–400 coverage from those fixtures | — | 0 missing lines, 0 missing branches |

### Root cause

The test gap follows from the fix, as the board noted. The two things that caused the freeze, bs4 `Tag.__hash__` = `hash(str(self))` inside `_in_preserved_svg` and synchronous culls inside coroutines, both only show up as wall-clock cost. Existing tests are tiny and stub the culls, so none of them can observe either one. `_cull_html` and the two finalize functions carry whole-function `# pragma: no cover`, so the coverage gate never forced tests there.

### Proposed change

The test nodes are exact. Follow the existing class and fixture idioms in each file (`pw_mod`, `roster_mod`, `fmt`, `_company`, `TestAst827TitleHandoffDomCull._browser_cm` / `_SIBLING_DOM` / `_TWO_TITLES`). The `[bug-repro]` tag marks the nodes that must flip red→green.

**1. `tests/component/external/test_telescope.py` — new class `TestAst1840CullHtmlLinearAndSnip`**, placed after `TestAst1745CullPreservesRootSvgLogo`:

- `test_cull_html_full_page_never_hashes_tag` **[bug-repro]**
  - Fixture: `'<html><body><div id="app"><ul>' + ''.join(ROW % (i, i) for i in range(40)) + '</ul></div></body></html>'`, where `ROW = '<li class="job-row" data-automation-id="job"><div class="c1"><h3><a href="/job/E_%d">Engineer %d</a></h3></div><button><i>x</i></button><span class="loc">Pittsburgh</span><svg viewBox="0 0 10 10"><g><path d="M0 0L10 10"></path></g></svg></li>'`.
  - `monkeypatch.setattr(bs4.element.Tag, "__hash__", boom)`, where `boom` raises `AssertionError("Tag.__hash__ called during _cull_html")`.
  - Assert `"Engineer 39" in out` and `"<svg" not in out`.
  - Why it's the linear-time guard: any Tag hash serializes a subtree, and zero hashes on a `<body>` page means no O(document) work per element. It's deterministic and needs no timer. The fixture must include `<body>`, because root-svg fragments legitimately `add()` their root svg to the preserve set.
- `test_cull_html_snips_attr_over_max_length`
  - Input: `'<div data-a="%s" data-b="%s" class="%s">Job</div>' % ("x"*500, "y"*501, " ".join(["c"*50]*11))`.
  - Assert `'data-a="' + "x"*500 + '"' in out`, `'data-b="(snipped)"' in out`, `'class="(snipped)"' in out` (list-valued attribute measured by its joined length, 560), and `"y"*501 not in out`.
- `test_cull_html_missing_snip_key_raises` parametrized over `["max_html_tag_length", "max_length_placeholder"]`: `monkeypatch.delitem(pw_mod.ASTRAL_CONFIG["html_cull"], key)`, then `pytest.raises(ValueError, match=key)` on `pw_mod._cull_html("<div>x</div>")`.
- `test_extract_page_dom_culls_off_event_loop` **[bug-repro]** (`@pytest.mark.asyncio`)
  - Setup as in `TestCullHtmlDefault`: `cull_html_default=True`; `_ensure_html` is an `AsyncMock` returning `"<body>hi</body>"`.
  - `_cull_html` is replaced by a plain function that records `threading.get_ident()` and returns `"<p>hi</p>"`.
  - Assert `out == "<p>hi</p>"` and that the recorded thread id `!= threading.get_ident()` of the test coroutine.
- Existing `TestCullHtmlDefault::test_extract_page_dom_culls_when_default_on` stays **unchanged**. It already passes through `to_thread`, because the `MagicMock` is resolved at call time.

**2. `tests/component/core/test_roster.py` — new class `TestAst1840CullOffEventLoop`**, placed after `TestAst827TitleHandoffDomCull`. Each test is `@pytest.mark.asyncio`, records `threading.get_ident()` inside a replacement `_culled_dom_for_parse`, and asserts that the id differs from the coroutine's thread:

- `test_parse_dispatch_culls_off_event_loop` **[bug-repro]**
  - Same scaffold as `TestAst827TitleHandoffDomCull::test_parse_dispatch_passes_multi_title_culled_dom`: `_company(state="JOBLIST_IDENTIFIED", …, job_titles=_TWO_TITLES)`, with `_scrape_list_page_dom_for_parse` returning `_SIBLING_DOM` and `_fetch_parse_job_list` / `_validate_parse_job_list_raw_job_listings` stubbed.
  - The replacement wraps the **real** `_culled_dom_for_parse`, so the result stays real.
  - Assert `out["state"] == "WATCH"`.
- `test_finalize_after_chain_culls_off_event_loop` **[bug-repro]**
  - Stub `save_company_data` and `_save_company` with `MagicMock`; the replacement returns `("", [], "cull_miss")`.
  - Call `_finalize_joblist_titles_after_chain({"job_titles": ["A", "B"], "selected_page": 0}, {"parsed_response": {}}, "acme", "https://acme.com", "https://acme.com/jobs", {0: "<div>A B</div>"}, {0: "A B"}, 0, "JOBLIST_TITLES", False, None)`.
  - Assert `out["state"] == "CANNOT_PARSE_JOB_SITE"`.
- `test_finalize_select_only_culls_off_event_loop` **[bug-repro]**
  - Same stubs.
  - Call `_finalize_joblist_titles_select_only({"job_titles": ["A", "B"], "selected_page": 0}, "acme", "https://acme.com", "https://acme.com/jobs", {0: "<div>A B</div>"}, 0, "JOBLIST_TITLES", False, None, {0: "A B"})`.
  - Assert `CANNOT_PARSE_JOB_SITE`.
- This is the board's "non-blocking assertion": off-loop is proven by thread identity, which is deterministic and needs no sleeps or tick counters. Existing AST-827 / AST-469 / parse-dispatch tests stay **unchanged**.

**3. `tests/component/utils/test_formatting.py` — new class `TestAst1840FindJobContainersEquivalence`**, placed after `TestFindJobContainers`. Titles are always `["Senior Engineer", "Nurse"]` except in the large-DOM case. The asserts are structural (count, prefix, substring) rather than full-string, because bs4 whitespace serialization varies across the `>=4.12` floor. Every row gives identical output on the pre- and post-fix trees:

| Node (parametrize id) | DOM | Assert | Branch it pins |
|---|---|---|---|
| `comment_ws` | `'<div id="w"><section>\n  <!-- Nurse -->\n  <p>Senior Engineer</p>\n</section><p>Nurse</p></div>'` | 1 container, starts `'<div id="w">'` (comment text doesn't count, so `<section>` is not all-match) | `345→350`, `356→353` |
| `script` | `'<main><div><p>Senior Engineer</p><script>Nurse</script></div><p>Nurse</p></main>'` | 1 container, starts `'<main>'` | `375→377` |
| `style` | same shape with `<style>Nurse</style>` | 1 container, starts `'<main>'` | `375→377` |
| `template` | `'<ul><li>Senior Engineer</li><template><li>Nurse</li></template></ul>'` | 2 containers: `'<li>Senior Engineer</li>'` and one starting `'<template>'` (Phase 2 sibling union) | `375→377`, Phase 2 |
| `ruby_rt` | `'<div id="r"><p><ruby>Senior Engineer<rt>Nurse</rt></ruby></p><p>Nurse</p></div>'` | 1 container, starts `'<div id="r">'` | `375→377` |
| `ruby_rp` | `'<div id="q"><p><ruby>Lead<rp>(Nurse)</rp></ruby> Senior Engineer</p><p>Nurse</p></div>'` | 1 container, starts `'<div id="q">'` | `375→377` |
| `test_large_dom_same_containers` | `'<div id="app"><ul>' + ''.join('<li class="job-row"><div class="c1"><h3><a href="/job/E_%d">Engineer %d</a></h3></div><span>Pittsburgh</span></li>' % (i, i) for i in range(8000)) + '</ul></div>'`, titles `["Engineer 7999", "Engineer 12"]` | 1 container, starts `'<ul><li class="job-row">'` (deepest all-match is the `<ul>`) | large-DOM equivalence |

No timing assertion on the large DOM: equivalence only (no heuristics or limits without Susan's say-so).

**4. Bible entries**, each a new `### AST-1840 · AST-1844 (…)` block with a `**Board REVISE:**` line and an `Area | Component tests` table, in the same shape as the existing AST-1745 block in `external/telescope.md`:

- `docs/test-bible/external/telescope.md`, "(qa-fix bug-repro — linear `_cull_html`, attribute snip, off-loop cull)": the four telescope nodes, with the two **bug-repro** nodes marked.
- `docs/test-bible/core/roster.md`, "(qa-fix bug-repro — `_culled_dom_for_parse` off the event loop)": the three roster nodes, all **bug-repro**.
- `docs/test-bible/utils/formatting.md`, "(`find_job_containers` linear rewrite equivalence)": the parametrized class plus the large-DOM node, noting the three branch ids it closes.

**Narrowed run for test-fix** (manifest):

```bash
/home/susan/astral/.venv/bin/python -m pytest \
  tests/component/external/test_telescope.py::TestAst1840CullHtmlLinearAndSnip \
  tests/component/core/test_roster.py::TestAst1840CullOffEventLoop \
  tests/component/utils/test_formatting.py::TestAst1840FindJobContainersEquivalence \
  tests/component/external/test_telescope.py::TestCullHtmlDefault \
  tests/component/external/test_telescope.py::TestAst1745CullPreservesRootSvgLogo \
  tests/component/core/test_roster.py::TestAst827TitleHandoffDomCull \
  tests/component/utils/test_formatting.py::TestFindJobContainers -q
```

Pass criterion: green on `fb472a98` (merged into this sub). The **[bug-repro]** nodes are red on `31846c28`.

### Blast radius

- Test and bible files only. No product, config, or fixture tables (scope: "new test cases only").
- **Doc merge:** this branch was seeded from ftr before AST-1840's plan section merged, so both `## Bug: AST-1840` and `## Bug: AST-1844` are appended at the end of this doc. Expect a trivial keep-both conflict at merge-child; resolve with AST-1840 first, AST-1844 second.
- `monkeypatch.setattr(bs4.element.Tag, "__hash__", …)` is class-wide but test-scoped; monkeypatch restores it on teardown. Don't use it in a module-scoped fixture.
- `monkeypatch.delitem` on `ASTRAL_CONFIG["html_cull"]` mutates the shared config dict and is restored on teardown.
- **Out of scope:** the 54 tests already failing on `origin/dev` (stale references to removed functions such as `roster.get_page` and `telescope._TelescopePool`). That includes the three near the parse path (`TestFinalize469BranchCoverage::test_after_chain_empty_containers_debug_true_logs`, `TestAst891ParseJobListBatch::{test_debug_emits_per_company_index, test_scrape_timeout_labeled_infra_and_counts_passed}`). This gap does not fix them.

### What must still hold

- `TestCullHtmlDefault`, `TestAst1745CullPreservesRootSvgLogo`, `TestAst827TitleHandoffDomCull`, `TestFindJobContainers`, and the AST-469 resolver tests all stay unchanged and green.
- The `[bug-repro]` nodes are red on the pre-fix product and green on `fb472a98`. The equivalence nodes are green on both.
- No wall-clock or timeout assertions, and no DOM-size caps (Susan, 2026-09-28).
- LOCKED_AT_100: after these nodes land, `src/utils/formatting.py` has no uncovered lines or branches inside AST-1840's hunks. The `telescope.py` and `roster.py` hunks sit in lines that are already covered or `# pragma: no cover`, so they add no new gate debt.


## Joan fix-board (AST-1844)

AST-1844 is Betty’s gap child (qa-fix): **test + `docs/test-bible` only**, no `src/` or `config.py`. Joan’s fix-board question is whether that work **conflicts with or requires updating** any in-force statute/pattern.

**Findings**

- **Scope:** New component tests (`TestAst1840CullHtmlLinearAndSnip`, `TestAst1840CullOffEventLoop`, `TestAst1840FindJobContainersEquivalence`) plus three bible blocks mirroring the AST-1745 telescope bible shape. Product behavior under test is already defined on AST-1840 @ `fb472a98`; this pass only pins it (red on pre-fix ftr `31846c28`, green on fix tip).
- **Corpus:** Adds no directives, no statute text, no pattern ids, no carve-outs. It exercises existing law-friendly shapes: `html_cull` keys and required-key `ValueError` (aligns with `astral.config.config-source-of-truth` / `astral.standards.no-hardcoded-sets` on the **product** tree, not amended here), layer boundaries unchanged, no new logging/debug contract in product code.
- **Test mechanics:** `Tag.__hash__` monkeypatch and `delitem` on `ASTRAL_CONFIG["html_cull"]` are scoped test patterns; they don’t imply a canon edit. LOCKED_AT_100 / branch coverage goals are bible/CI discipline, not the statute corpus.
- **Susan constraints** (no wall-clock asserts, no DOM-size caps) live in the plan and test design; they don’t need a new statute for this gap child.

No architectural call for Archie; no F3 (`validate-plan` fix mode) canon landing required for AST-1844.

BEGIN-VERDICT
```
[board-joan]  CANON: OK
```
END-VERDICT

```text
AST-1844 board-joan done — CANON: OK.
```


## Radia review-fix (AST-1844)

[code-rubric] PROCEED (Commit: 59b7b03d)

**Overall:** CLEAN

## Canon scores

No `Canon Scope (frozen at plan)` on Linear. Gap child: tests + bible only; Joan **`[board-joan] CANON: OK`** — no product or statute landing. No scored product violations.

**Notes:** Missing frozen list = Archie process gap, not **ESCALATE** on this tip.

## Column diff vs plan stage

`no plan-stage scores attached`

## Frame diff

(none)

## Fix-specific checks

### `[bug-repro]` — **OK**

Betty thread (`[bug-repro]` @ `c1838b28`, 8 nodes red→green `31846c28` → AST-1840 product). Assertions match plan **`## To-be`**, not tautologies:

| Repro node | What it asserts | Why it fails pre-fix |
|------------|-----------------|----------------------|
| `TestAst1840CullHtmlLinearAndSnip::test_cull_html_full_page_never_hashes_tag` | `Tag.__hash__` raises; 40-row `<body>` page; `"Engineer 39"`, no `<svg` | `elem in preserve_root_svgs` hashes Tags |
| `::test_cull_html_snips_attr_over_max_length` | 500 kept, 501 + list `class` → `(snipped)` | No snip pre-AST-1840 |
| `::test_cull_html_missing_snip_key_raises` (×2 keys) | `ValueError` matching key name after `delitem` | Missing keys / wrong error pre-fix |
| `::test_extract_page_dom_culls_off_event_loop` | `_cull_html` runs on thread `!=` asyncio thread | Sync cull on loop |
| `TestAst1840CullOffEventLoop::test_parse_dispatch_culls_off_event_loop` | Real `_culled_dom_for_parse` wrapper; `WATCH`; off-loop | Sync cull in dispatch |
| `::test_finalize_after_chain_culls_off_event_loop` | `CANNOT_PARSE_JOB_SITE`; off-loop | Sync finalize cull |
| `::test_finalize_select_only_culls_off_event_loop` | same | Sync finalize cull |

**Four off-loop cull sites:** `extract_page_dom` + three roster async call sites — covered.

`TestAst1840FindJobContainersEquivalence`: **green both trees** by design; structural pins (comment/script/style/template/rt/rp, 8k DOM) per plan — closes LOCKED_AT_100 branches, not the freeze repro.

**Advisory:** class docstrings say `AST-1840 bug-repro` vs first-line `# [bug-repro]`; bible + Betty thread name repro nodes — sufficient.

### `## What must still hold` — **OK**

- `TestCullHtmlDefault`, AST-1745, AST-827, `TestFindJobContainers` — not modified (additions only).
- No wall-clock or DOM-size caps in new tests.
- Plan **`### Proposed change`** + three bible `### AST-1840 · AST-1844` blocks match landed nodes/manifest.
- Sub ancestry includes ftr sync (`8e4b53d4`) after Betty’s “merge ftr first” note.

### Carry-over (`resolve(AST-1844)` `7ade973a`) — **OK**

Three-dot diff **only** the seven AST-1844 paths. No reintroduction of stripped carry-over (`test_dispatcher`, `test_agent`, frontend tests, extra bible modules, etc.). `test_roster.py` vs ftr: additive `TestAst1840CullOffEventLoop` + `threading` import.

## Findings

**fix-now:** none

**discuss:** none

**advisory:**
- Equivalence tests don’t dual-call old vs new `find_job_containers`; plan probe table + structural asserts are the contract.
- Stale 54-test debt elsewhere remains out of scope per plan blast radius.

## What's solid

- Board REVISE on AST-1840 addressed: linear-time guard, snip 500/501 + keys, equivalence branches, off-loop at all four sites.
- Parse-dispatch repro uses AST-827 scaffold with real cull to `WATCH`.
- Diff isolated; product remains on ftr via AST-1840.

## Chuckles — post-review branching

**PROCEED** + orphaned mini-parent **AST-1838** → **Review Posted** → clean §3h shortcut → **User Testing** (skip **resolve-child**). Land gap sub into **`ftr/AST-1838-parse-job-list-event-loop-block`** per parent shape (not dev until finish-up).

context_tokens≈N

