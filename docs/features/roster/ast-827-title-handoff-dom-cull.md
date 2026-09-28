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
