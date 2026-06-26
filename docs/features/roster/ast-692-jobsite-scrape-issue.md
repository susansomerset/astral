<!-- linear-archive: AST-692 archived 2026-06-23 -->

## Linear archive (AST-692)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-692/jobsite-scrape-issue-response-and-terminal-roster-flow-job-site-scrape  
**Status at archive:** Done  
**Project:** Astral Roster  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-684 — Job Site scrape is too fast?  
**Blocked by / blocks / related:** parent: AST-684

### Description

## What this implements

Extend **select_job_page** with response type **JOBSITE_SCRAPE_ISSUE** for incomplete careers-list scrapes (shell-only text after bounded readiness wait). When Grace returns **JOBSITE_SCRAPE_ISSUE**, transition the company to **JOBSITE_SCRAPE_ISSUE** state and **do not** invoke downstream **parse_job_list** or further AI analysis on that run. Structured payload fields for Execution History inspection.

## Acceptance criteria

3. When listings never render within configured bounds (or scraped text is shell-only), **select_job_page** returns **JOBSITE_SCRAPE_ISSUE** — not **JOBLIST_TITLES** with fabricated titles — and the company lands in **JOBSITE_SCRAPE_ISSUE** state with **no** downstream **parse_job_list** hop on that run.
4. Susan can verify fix via Execution History on a staging **select_job_page** batch: **no_cache** page sections contain the job titles visible in the browser for the repro case, or **JOBSITE_SCRAPE_ISSUE** with a clear agent report when they do not.

## Boundaries

* Does **not** implement Playwright readiness waits — sibling AST-689 (blocked upstream).
* Does **not** change **select_job_page** prompt prose beyond what Susan authors in Manage Tasks.
* Does **not** fix AST-666 hang class or gazer-only paths unless wired into roster discovery.

## Notes for planning

* Hot files: `src/utils/config.py` (COMPANY_STATES, TASK_CONFIG), `src/core/roster.py`, `src/core/tracker.py`.
* Depends on AST-689 readiness gate feeding honest scrape text.
* Follow ASTRAL_CODE_RULES state machine and batch patterns.

## Git branch (authoritative)

Per **orientation** § Branch law: parent `ftr/AST-684-job-site-scrape-is-too-fast`, child `sub/AST-684/<child-id>-jobsite-scrape-issue`. Created at dispatch-parent.

### Comments

#### radia — 2026-06-16T00:49:09.435Z
**Diff:** `origin/dev...origin/sub/AST-684/AST-692-jobsite-scrape-issue` @ `98011ad`
**Doc:** `docs/features/roster/ast-692-jobsite-scrape-issue.md` (Radia review section)

**Verdict:** Clean — no **fix-now** or **discuss**.

### Plan fidelity
- Stage 1: `JOBSITE_SCRAPE_ISSUE` state, three inbound transitions, `select_job_page` schema fields, `ROSTER_CONFIG` scrape_issue_state + company_data_keys.
- Stage 2: `_check_parse_results` terminal branch (after JOBLIST_NO_JOBS); `_save_company` persists summary/evidence; `job_list_visible` stripped; `_PERSIST_PAGE_OPTION_URL_STATES` includes new terminal state.
- `_find_job_page_from_assembled` routes non-JOBLIST_TITLES to `_check_parse_results` — no premature branch added.
- `agent.py` unchanged; AST-469 parse_job_list suppression verified + Betty agent test.

### Advisory
- E2E staging repro waits on Susan's Manage Tasks prompt + AST-689 ftr rollup — expected per plan prerequisite.
- Sub tip includes AST-689 test commits from `origin/tests` merge; product commits stay scoped.

**resolve-child** may proceed.

#### betty — 2026-06-16T00:46:35.499Z
## QA test manifest (AST-692)

**Publish ref:** `origin/sub/AST-684/AST-692-jobsite-scrape-issue` @ `13d7d1e`
**Tests SHA:** `7271e5f`

1. `tests/component/core/test_roster.py::TestAst692JobsiteScrapeIssue::test_check_parse_results_jobsite_scrape_issue` — terminal **JOBSITE_SCRAPE_ISSUE** state + persisted summary/evidence
2. `tests/component/core/test_roster.py::TestAst692JobsiteScrapeIssue::test_find_job_page_from_assembled_jobsite_scrape_issue_no_chain` — **`_check_parse_results`** path, not **`_finalize_joblist_titles_after_chain`**
3. `tests/component/core/test_roster.py::TestAst692JobsiteScrapeIssue::test_unknown_response_type_still_no_joblist` — unknown types remain **NO_JOBLIST**
4. `tests/component/core/test_agent.py::TestAst692JobsiteScrapeIssueAgent::test_select_job_page_suppresses_parse_chain_for_jobsite_scrape_issue` — **parse_job_list** chain suppressed (AST-469 guard)

**Narrowed run:**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_roster.py::TestAst692JobsiteScrapeIssue \
  tests/component/core/test_agent.py::TestAst692JobsiteScrapeIssueAgent
```

**Bible shasum (publish ref):**
- `docs/test-bible/core/roster.md` → `7f3910f79eaf60a4847bdc33f6420d6a0de849fc`

— Betty

#### ada — 2026-06-16T00:43:17.037Z
Plan: `docs/features/roster/ast-692-jobsite-scrape-issue.md`
https://github.com/susansomerset/astral/blob/sub/AST-684/AST-692-jobsite-scrape-issue/docs/features/roster/ast-692-jobsite-scrape-issue.md

**Scope:** Single-Component — `config.py` state/schema + `roster.py` `_check_parse_results` terminal branch; mirrors **JOBLIST_NO_JOBS** pattern.

**Conf:** high — AST-469 already suppresses `parse_job_list` for non-**JOBLIST_TITLES**; this ticket adds config + persistence only.

**Risk:** Medium — wrong fallback could still route shell-only pages to **NO_JOBLIST** if Grace returns an unexpected type; mitigated by explicit **JOBSITE_SCRAPE_ISSUE** branch and Susan's prompt update (out of engineer scope).

Prerequisite: end-to-end staging repro needs AST-689 on `origin/ftr` after merge-child; AST-692 does not import readiness code.

---

# AST-692 — JOBSITE_SCRAPE_ISSUE response and terminal roster flow (Job Site scrape is too fast?)

**Linear:** [AST-692 — JOBSITE_SCRAPE_ISSUE response and terminal roster flow (Job Site scrape is too fast?)](https://linear.app/astralcareermatch/issue/AST-692/jobsite-scrape-issue-response-and-terminal-roster-flow-job-site-scrape)

**Parent (reference only — orchestration AC):** [AST-684 — Job Site scrape is too fast?](https://linear.app/astralcareermatch/issue/AST-684/job-site-scrape-is-too-fast)

**Publish ref:** `origin/sub/AST-684/AST-692-jobsite-scrape-issue` (origin only)

## Summary

When roster **select_job_page** receives careers-page text that is shell-only (filters, headers, empty listing region) after sibling [AST-689](https://linear.app/astralcareermatch/issue/AST-689) readiness waits, Grace must return **JOBSITE_SCRAPE_ISSUE** — not **JOBLIST_TITLES** with fabricated titles. This ticket wires that response type through config and **roster.py**: persist structured inspection fields, transition the company to terminal state **JOBSITE_SCRAPE_ISSUE**, and ensure **no** downstream **parse_job_list** hop runs on that dispatch. Playwright readiness waits and **select_job_page** prompt prose are out of scope (AST-689 and Susan's Manage Tasks, respectively).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `COMPANY_STATES`, `company_state_transitions`, `TASK_CONFIG["select_job_page"].response_schema`, `ROSTER_CONFIG` keys | utils |
| `src/core/roster.py` | `_PERSIST_PAGE_OPTION_URL_STATES`, `_save_company`, `_check_parse_results` — terminal **JOBSITE_SCRAPE_ISSUE** path | core |

**Verify only (no code change expected):**

| File | Role |
|------|------|
| `src/core/agent.py` | Already suppresses `run_next` **parse_job_list** when `response_type != "JOBLIST_TITLES"` (AST-469) — confirm unchanged |

**Verify only (Betty / qa-child — engineer does not edit in build-child):**

| File | Change |
|------|--------|
| `tests/component/core/test_roster.py` | New **JOBSITE_SCRAPE_ISSUE** terminal + no-chain tests per Stage 3 spec |
| `tests/component/core/test_agent.py` | Optional: assert **parse_job_list** chain suppressed for **JOBSITE_SCRAPE_ISSUE** (reuse AST-469 pattern) |

**Out of scope:** Playwright readiness (`wait_for_careers_list_readiness` — [AST-689](https://linear.app/astralcareermatch/issue/AST-689)), **select_job_page** prompt/task prose edits (Susan via Manage Tasks), **gazer** JD scrape paths, **AST-666** hang class, UI, dispatch row changes, unbounded waits.

---

## Prerequisite (integration)

**build-child** must merge `origin/ftr/AST-684-job-site-scrape-is-too-fast` on epic worktree checkout per orientation. End-to-end staging repro (PagerDuty shell-only → Grace emits **JOBSITE_SCRAPE_ISSUE**) requires [AST-689](https://linear.app/astralcareermatch/issue/AST-689) on `origin/ftr` (Chuckles `merge-child(AST-689)`). AST-692 code does **not** import readiness helpers; it can land before 689 merges, but Susan's AC 3/4 verification waits for ftr rollup of both siblings.

Susan must add **JOBSITE_SCRAPE_ISSUE** instructions to the **select_job_page** task prompt in Manage Tasks (when to emit vs **JOBLIST_TITLES** / **JOBLIST_NO_JOBS**). Engineer does **not** edit prompt rows or `agent_task` content.

---

## Stage 1: Config — state, transitions, response schema

**Done when:** `JOBSITE_SCRAPE_ISSUE` is a valid company state with transitions from locate input states; **select_job_page** schema accepts structured scrape-issue fields; roster config names the terminal state string.

1. In `src/utils/config.py`, inside `COMPANY_STATES` (after `"ERROR_LOCATE_JOB_PAGE": {}`), add:

```python
"JOBSITE_SCRAPE_ISSUE": {},
```

2. In `ASTRAL_CONFIG["company_state_transitions"]`, after the existing `("PREFILTER_PASSED", "BOT_BLOCK")` tuple, append:

```python
("TO_WATCH", "JOBSITE_SCRAPE_ISSUE"),
("JOBS_FOUND", "JOBSITE_SCRAPE_ISSUE"),
("PREFILTER_PASSED", "JOBSITE_SCRAPE_ISSUE"),
```

3. In `TASK_CONFIG["select_job_page"]["response_schema"]`, after `"try_links": {"type": "list", "required": False},`, add:

```python
"scrape_issue_summary": {"type": "str", "required": False},
"scrape_issue_evidence": {"type": "str", "required": False},
```

4. In `ROSTER_CONFIG["locate_job_page"]`, after `"error_state": "ERROR_LOCATE_JOB_PAGE",`, add:

```python
"scrape_issue_state": "JOBSITE_SCRAPE_ISSUE",
```

5. In `ROSTER_CONFIG["company_data_keys"]`, after `"job_list_visible": "job_list_visible",`, add:

```python
"jobsite_scrape_issue_summary": "jobsite_scrape_issue_summary",
"jobsite_scrape_issue_evidence": "jobsite_scrape_issue_evidence",
```

⚠️ **Decision:** Terminal state has **no** `batch_criteria` (same as **NO_JOBLIST**) — companies land here for human/prompt inspection, not automatic re-dispatch.

---

## Stage 2: Roster terminal handling — persist, transition, no parse chain

**Done when:** `_check_parse_results` maps **JOBSITE_SCRAPE_ISSUE** → company state **JOBSITE_SCRAPE_ISSUE** with `job_site` = attempted careers URL, structured fields in `company_data`, `job_list_visible` stripped, and `raw_response` preserved for Execution History; unknown response types still fall through to **NO_JOBLIST**; **JOBLIST_TITLES** / **JOBLIST_NO_JOBS** paths unchanged.

1. In `src/core/roster.py`, extend `_PERSIST_PAGE_OPTION_URL_STATES` (≈ line 1687) to include the new terminal state:

```python
_PERSIST_PAGE_OPTION_URL_STATES = frozenset({
    "WATCH", "NO_OPENINGS", "CANNOT_PARSE_JOB_SITE", "JOBSITE_SCRAPE_ISSUE",
})
```

2. Extend `_save_company` signature and body (≈ lines 1707–1760):

   - Add optional kwargs: `jobsite_scrape_issue_summary: Optional[str] = None`, `jobsite_scrape_issue_evidence: Optional[str] = None`.
   - In the `cd` dict builder, after the `no_jobs_message` block:

```python
if jobsite_scrape_issue_summary:
    cd["jobsite_scrape_issue_summary"] = jobsite_scrape_issue_summary
if jobsite_scrape_issue_evidence:
    cd["jobsite_scrape_issue_evidence"] = jobsite_scrape_issue_evidence
```

   - Update the docstring **Args** to document the two new optional fields.

3. In `_check_parse_results` (≈ lines 1620–1654), insert a new branch **after** the `JOBLIST_NO_JOBS` block and **before** the `JOBLIST_TITLES` deprecated block:

```python
if response_type == "JOBSITE_SCRAPE_ISSUE":
    summary = str(result.get("scrape_issue_summary") or "").strip()
    evidence = str(result.get("scrape_issue_evidence") or "").strip()
    _strip_company_data_keys(short_name, ("job_list_visible",))
    _save_company(
        short_name=short_name,
        company_website=company_website,
        state=ROSTER_CONFIG["locate_job_page"]["scrape_issue_state"],
        page_option_url=job_site_url,
        raw_response=result,
        jobsite_scrape_issue_summary=summary or None,
        jobsite_scrape_issue_evidence=evidence or None,
    )
    if debug:
        logger.test(
            f"[find_job_page] JOBSITE_SCRAPE_ISSUE: summary={summary!r} job_site={job_site_url}"
        )
    return {
        "short_name": short_name,
        "state": ROSTER_CONFIG["locate_job_page"]["scrape_issue_state"],
        "job_site": job_site_url,
        "response_type": response_type,
    }
```

4. Do **not** add a `JOBSITE_SCRAPE_ISSUE` branch in `_find_job_page_from_assembled` before the `JOBLIST_TITLES` check (≈ line 1223). Non-**JOBLIST_TITLES** responses already fall through to `_check_parse_results` — the new branch handles terminal mapping.

5. Read `src/core/agent.py` lines 2001–2006 and confirm **no edit**: `effective_next` is cleared when `response_type != "JOBLIST_TITLES"`, so **parse_job_list** never runs for **JOBSITE_SCRAPE_ISSUE**. If that guard were removed or narrowed, stop and comment on parent **AST-684**.

6. Do **not** change `_fetch_job_links_content`, `wait_for_careers_list_readiness`, or readiness abort logic — AST-689 owns scrape timing; AST-692 only classifies Grace's response after best-effort extract.

⚠️ **Decision:** Persist `scrape_issue_*` fields in `company_data` (mirrors **no_jobs_message** for **NO_OPENINGS**) **and** full `parsed_response` in `agent_responses` via existing `do_task` storage — Susan inspects Execution History on the LLM payload; `company_data` supports admin/DB inspection without re-fetching agent blocks.

---

## Stage 3: Regression test contract (Betty manifest — qa-child)

**Done when:** Component tests assert terminal state mapping and no **parse_job_list** chain; `pytest` slice green in test-child.

Betty adds to `tests/component/core/test_roster.py` (engineer does not commit test file):

1. **`TestAst692JobsiteScrapeIssue.test_check_parse_results_jobsite_scrape_issue`**
   - Monkeypatch `_save_company` with `MagicMock` (pattern from `test_check_parse_results_logs_no_jobs`).
   - Call `_check_parse_results` with `response_type="JOBSITE_SCRAPE_ISSUE"`, `result={"response_type": "JOBSITE_SCRAPE_ISSUE", "selected_page": 1, "scrape_issue_summary": "Listing region empty", "scrape_issue_evidence": "Filters visible, zero titles"}, `job_site_url="https://acme.com/jobs"`.
   - Assert return `state == "JOBSITE_SCRAPE_ISSUE"`, `job_site == "https://acme.com/jobs"`, `response_type == "JOBSITE_SCRAPE_ISSUE"`.
   - Assert `_save_company` called once with `state="JOBSITE_SCRAPE_ISSUE"`, `page_option_url="https://acme.com/jobs"`, `jobsite_scrape_issue_summary="Listing region empty"`, `raw_response` containing `scrape_issue_summary`.

2. **`TestAst692JobsiteScrapeIssue.test_find_job_page_from_assembled_jobsite_scrape_issue_no_chain`**
   - Monkeypatch `do_task` to return `{"success": True, "parsed_response": {"response_type": "JOBSITE_SCRAPE_ISSUE", "selected_page": 1, "scrape_issue_summary": "shell only"}}` (no `run_next_parent_parsed`).
   - Monkeypatch `_check_parse_results` with `AsyncMock` returning terminal dict.
   - Call `_find_job_page_from_assembled` with minimal maps (`assembled_content` non-empty, `page_url_map={1: "https://acme.com/jobs"}`, `chain_parse=True`).
   - Assert `_check_parse_results` awaited (not `_finalize_joblist_titles_after_chain`); assert `do_task` called once with task `"select_job_page"` only.

3. **`TestAst692JobsiteScrapeIssue.test_unknown_response_type_still_no_joblist`**
   - Reuse existing `test_check_parse_results` unknown-type pattern; confirm **JOBSITE_SCRAPE_ISSUE** branch does not absorb other types.

Optional in `tests/component/core/test_agent.py`:

4. **`test_select_job_page_suppresses_parse_chain_for_jobsite_scrape_issue`**
   - Mirror AST-469 **JOBLIST_NO_JOBS** / non-titles chain-suppression test; `parsed_response.response_type = "JOBSITE_SCRAPE_ISSUE"` → no `parse_job_list` hop.

---

## Self-Assessment

**Scope:** `Single-Component` — `config.py` state/schema additions and `roster.py` terminal mapping in `_check_parse_results` / `_save_company`; no Playwright or agent chain edits.

**Conf:** `high` — mirrors the established **JOBLIST_NO_JOBS** → **NO_OPENINGS** pattern; **agent.py** already blocks **parse_job_list** for non-**JOBLIST_TITLES** responses.

**Risk:** `Medium` — mis-wiring could send shell-only pages to **NO_JOBLIST** instead of **JOBSITE_SCRAPE_ISSUE** (losing Susan's inspection signal) or accidentally chain **parse_job_list**; mitigated by explicit branch before the **NO_JOBLIST** fallback and read-only verification of AST-469 guard in **agent.py**.

---

## Self-review vs ASTRAL_CODE_RULES

| Rule | Assessment |
|------|------------|
| **§1.3 DRY** | Single terminal branch in `_check_parse_results`; state string from `ROSTER_CONFIG["locate_job_page"]["scrape_issue_state"]`. |
| **§2.1 config** | State list, transitions, response schema, and terminal state name in `config.py` — no inline state strings in roster except via `ROSTER_CONFIG` lookup. |
| **§2.4 batch processing** | No claim/release or dispatcher semantics change. |
| **§2.6 state machine** | New terminal state + three inbound transitions from locate input states only; core calls `transition_company_state` via `_save_company`. |
| **§3.3 imports** | `roster` → `utils` only; no new cross-layer imports. |
| **§3.5 naming** | snake_case fields; UPPERCASE state constant. |
| **§1.5 debug** | Optional `logger.test` in new branch when `debug=True` only. |

No unresolved conflicts.

---

## Execution contract (for the developer agent)

- Execute stages **1 → 2 → 3** in order; one commit per stage on epic worktree; publish each to `origin/sub/AST-684/AST-692-jobsite-scrape-issue` per **build-child** §6.
- Do **not** implement Playwright readiness, prompt prose, or **gazer** paths.
- Do **not** add files beyond the table above.
- Blocking ambiguity → comment on parent **AST-684** with 🛑 template from **plan-child** §6.

---

## Boundary echo (ticket)

- Implements parent AC **3** and **4** (terminal **JOBSITE_SCRAPE_ISSUE**, no **parse_job_list** on that run, Execution History inspectable payload).
- Does **not** implement parent AC **1** / **2** (honest scrape text + readiness debug) — [AST-689](https://linear.app/astralcareermatch/issue/AST-689).
- Does **not** change **select_job_page** prompt prose — Susan owns Manage Tasks update teaching Grace **JOBSITE_SCRAPE_ISSUE**.

---

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-684/AST-692-jobsite-scrape-issue`  
**Product commits:** `e59dfa0` (Stage 1 — config state/transitions/schema), `8ee1887` (Stage 2 — roster terminal handling)

---

## Radia review (2026-06-16)

**Diff:** `origin/dev...origin/sub/AST-684/AST-692-jobsite-scrape-issue` @ `13d7d1e`  
**Verdict:** Clean — no fix-now items.

### What's solid

| Stage | Check |
|-------|-------|
| 1 | `COMPANY_STATES`, `company_state_transitions` (TO_WATCH / JOBS_FOUND / PREFILTER_PASSED → JOBSITE_SCRAPE_ISSUE), `select_job_page` schema fields, `ROSTER_CONFIG` scrape_issue_state + company_data_keys — match plan Stage 1 |
| 2 | `_check_parse_results` branch after JOBLIST_NO_JOBS, before JOBLIST_TITLES; strips `job_list_visible`; persists summary/evidence via `_save_company`; `JOBSITE_SCRAPE_ISSUE` in `_PERSIST_PAGE_OPTION_URL_STATES` so `job_site` = attempted careers URL |
| 3 | `_find_job_page_from_assembled` unchanged routing — non-JOBLIST_TITLES (including JOBSITE_SCRAPE_ISSUE) falls through to `_check_parse_results` per plan Stage 2 §4 |
| 4 | `agent.py` unchanged; AST-469 guard (`response_type != "JOBLIST_TITLES"` → clear `effective_next`) verified; Betty agent test confirms single-hop |

**§2.6 state machine:** Terminal state with no batch_criteria (human inspection) — per plan decision.

### Advisory

- Sub tip ancestry includes **AST-689** test-bible commits from `origin/tests` merge — tests/docs only; AST-692 product commits (`e59dfa0`, `8ee1887`) stay within plan file table.
- End-to-end staging repro (PagerDuty shell-only → Grace emits JOBSITE_SCRAPE_ISSUE) still depends on Susan's Manage Tasks prompt update + **AST-689** ftr rollup — out of scope for this ticket's code review.
- `test_check_parse_results_jobsite_scrape_issue` asserts summary but not evidence kwarg — harmless; evidence path is wired in `_save_company`.

### Recommended actions

None — **resolve-child** may proceed.

---

## Resolution (Ada / resolve — 2026-06-16)

**Radia verdict:** Clean — no fix-now or discuss items.

**Product changes:** None. Review confirmed plan fidelity; AST-469 parse suppression and Betty manifest already green at `13d7d1e`.

**§9a dry-run:** `origin/sub/AST-684/AST-692-jobsite-scrape-issue` merges cleanly into `origin/dev` and `origin/ftr/AST-684-job-site-scrape-is-too-fast`.

**Publish ref @ resolve:** `origin/sub/AST-684/AST-692-jobsite-scrape-issue` @ `98011ad` (includes Radia `docs(AST-692): Radia review — clean`).
