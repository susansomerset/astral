<!-- linear-archive: AST-1495 archived 2026-09-09 -->

## Linear archive (AST-1495)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1495/email-land-paths-apply-stem-to-company-attach-create-meteorite  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** katherine  
**Priority / estimate:** None / 5  
**Parent:** AST-1484 — Create meteorite companies per email address  
**Blocked by / blocks / related:** parent: AST-1484

### Description

## What this implements

Inbox + gaze_email (+ gazer if needed) supply CONTENT, take Ruth stem, call #1 ensure, attach job under that company in create/`land_meteorite`. Optional thin METEORITE company list/nav if needed for UAT. After #1 and #2.

## Citations

pattern.layers.import-discipline, pattern.ui.admin-endpoint; astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions.

## Scope

- [X] src/core/inbox.py — modified — CONTENT + stem → ensure/attach.
- [X] src/core/gaze_email.py — modified — same. *(file absent; inbox covers path — plan resolution)*
- [X] src/core/gazer.py — modified — only if still creating on this path. *(no production callers — no changes)*
- [X] src/core/meteorite.py — modified — create/`land_meteorite` attach when stem present (shared file; units not owned by #1).
- [X] src/ui/api/api_companies.py / src/ui/api/api_system.py / NAV+routes — modified — METEORITE company list/count shipped.

## Acceptance criteria

- [X] 5. Email-bound create/land attaches the job’s `company` to that ensured short_name.
- [X] 6. Slack/Contact lands without email sender still use `meteorite-{candidate_id}` in METEORITE.
- [X] 7. With `debug=True`, ensure/land emit Style D for stem and company; with `debug=False`, no new debug-contract noise.

## Boundaries

- [X] Does not own COMPANY_STATES / ensure / track predicate (#1). Does not own Ruth stem prompts/schema (#2).

## Notes for planning

Estimate 5. Unmarked — after #2.

## Git branch (authoritative)

Per orientation § Branch law: parent ftr/AST-1484-create-meteorite-companies-per-email-address, child sub/AST-1484/<this-id>-email-land-paths-apply-stem-company-attach. Created at dispatch-parent.

## QA test manifest

**Publish: **`origin/sub/AST-1484/AST-1495-email-land-paths-apply-stem-company-attach` @ `776866b5` (`merge-tests(AST-1495): origin/tests 1d33cb91`)

**Bible shasums (publish ref):**

* `docs/test-bible/core/meteorite.md`: `fd5abdc2446301dc6de4d5c67494bb46d8e9a35db7fdbc2ad40707f999612925`
* `docs/test-bible/core/inbox.md`: `75d77c203e444eddacfe59da21d12f0ec85ca40bd6e4107723b38894d92ae6ab`
* `docs/test-bible/ui/api/api_companies.md`: `90e86c5fddc04c1ff962c0bbce7798199ae9e734f15cdb8548b652c7fe493588`
* `docs/test-bible/frontend/pages.md`: `b52ba79897af77e95721880c3bd84ced7160ad6f3c7f8dbec3029a755a9cb6f9`
* `docs/test-bible/utils/config.md`: `18c07503d8c9f63b8589ad8e243f750ddb17e7fb1eeec729a8740e83b55aba30`

### 1. Existing coverage (revised)

| # | Path | Notes |
| -- | -- | -- |
| 1 | `tests/component/core/test_meteorite.py::TestAst1470LandMeteorite` | enrich-fail `company is None`; land debug `stem=`/`company=` |
| 2 | `tests/component/core/test_inbox.py::TestAst1049CreateMeteoriteJobFromInboxMessage` | land_meteorite path + post-land `company=` debug |
| 3 | `tests/component/core/test_inbox.py::TestAst1313FromThenToBind::test_create_rematch_uses_to_when_from_misses` | same |
| 4 | `tests/component/ui/api/test_api_companies.py::TestCompaniesRoutes` | `meteorite_list` view + counts key |
| 5 | `tests/component/utils/test_config.py::TestAst1041MeteoriteConfig` | restore METEORITE company_state (AST-1493 regression from AST-1494) |
| 6 | `tests/component/utils/test_config.py::TestAst1493MeteoriteCompanyStateConfig` | restore stem template asserts |

### 2. Broken / obsolete (fixed this pass)

* AST-1470 enrich-failure expected pre-enrich default company
* AST-1049/1061 gazer ingest mocks and `mode=body` return shape
* AST-1494 commit accidentally reverted AST-1493 config test class

### 3. Gaps (new)

| # | Path | Notes |
| -- | -- | -- |
| 1 | `tests/component/core/test_meteorite.py::TestAst1495LandStemAttach` | per-row stem attach + empty stem default |
| 2 | `tests/component/core/test_meteorite.py::TestAst1042CreateMeteoriteJob::test_optional_stem_forwards_to_ensure` | create `stem=` |
| 3 | `tests/component/utils/test_config.py::TestAst1495MeteoriteCompaniesNav` | NAV Meteorite item |
| 4 | `tests/component/frontend/pages/test_CompaniesMeteorite.test.tsx` | §6c routed page |

### Narrowed run

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_meteorite.py::TestAst1495LandStemAttach \
  tests/component/core/test_meteorite.py::TestAst1470LandMeteorite \
  tests/component/core/test_meteorite.py::TestAst1042CreateMeteoriteJob::test_optional_stem_forwards_to_ensure \
  tests/component/core/test_inbox.py::TestAst1049CreateMeteoriteJobFromInboxMessage \
  tests/component/core/test_inbox.py::TestAst1313FromThenToBind::test_create_rematch_uses_to_when_from_misses \
  tests/component/ui/api/test_api_companies.py::TestCompaniesRoutes \
  tests/component/utils/test_config.py::TestAst1495MeteoriteCompaniesNav \
  tests/component/utils/test_config.py::TestAst1041MeteoriteConfig \
  tests/component/utils/test_config.py::TestAst1493MeteoriteCompanyStateConfig \
  -q
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CompaniesMeteorite.test.tsx
```

**Integration:** no existing scenarios revised.

### Comments

#### katherine — 2026-08-26T17:56:25.531Z
Sub republished on ftr — forbidden sibling merges dropped; validate-sub-log ok @ aa8db8fe.

#### chuckles — 2026-08-26T17:09:59.667Z
[merge-child] blocked: git pull merge on sub — Merge remote-tracking branch commits 2cd2d1df/614c7389; republish with merge-resume(AST-1495) per validate-sub-log.

#### radia — 2026-08-26T17:09:22.220Z
[code-rubric] PROCEED (Commit: 776866b5) Stem land attach clean

#### betty — 2026-08-26T17:06:17.477Z
origin/sub/AST-1484/AST-1495-email-land-paths-apply-stem-company-attach @ `776866b5` · stem attach manifest ready

#### joan — 2026-08-26T16:56:51.968Z
[plan-rubric] PROCEED (Commit: 4059b632ca56e81af574c7eb07ef4b61fb3de638) stem attach land wired

#### katherine — 2026-08-26T16:54:24.682Z
origin/sub/AST-1484/AST-1495-email-land-paths-apply-stem-company-attach @ 4059b632ca56e81af574c7eb07ef4b61fb3de638 · stem attach wired

---

# AST-1495 — Email land paths apply stem → company attach

**Linear:** [AST-1495](https://linear.app/astralcareermatch/issue/AST-1495/email-land-paths-apply-stem-company-attach-create-meteorite-companies-per)  
**Parent:** [AST-1484](https://linear.app/astralcareermatch/issue/AST-1484/create-meteorite-companies-per-email-address) — Create meteorite companies per email address  
**Publish ref:** `sub/AST-1484/AST-1495-email-land-paths-apply-stem-company-attach`

Wire email-bound meteorite land/create so Ruth’s `company_stem` (AST-1494) drives `ensure_meteorite_company(stem=…)` (AST-1493) and each saved job’s `company` column points at that ensured short_name — not the generic `meteorite-{candidate_id}` bucket when a stem is known. Slack/Contact paths without email sender keep default stem. Optional thin METEORITE company list/nav for UAT provenance. Does **not** own COMPANY_STATES / ensure API (#1) or Ruth prompts/schema (#2).

## UAT fitness

- **AC restored:** Parent AC5 — “Email-bound create/land attaches the job’s `company` to that ensured short_name.” Ticket AC5–7 (attach, default stem for non-email, Style D when `debug=True`).
- **Correct outcome:** After landing a bound inbox message whose Ruth stem is `alice@example.com`, the created job’s `company` is `alice@example.com-{candidate_id}` (config template form) in **METEORITE**; operator can trace sender from company short_name (and optional Meteorite companies nav).
- **Sibling check:** AST-1493 `ensure_meteorite_company(stem=)` + `is_meteorite_company` unchanged; AST-1494 `enrich_meteorite_land_packet` still maps `company_stem` only — this ticket consumes it, does not re-prompt Ruth. Slack/Contact `land_meteorite` with empty stem still ensures `meteorite-{candidate_id}` via `default_stem`.
- **Not sufficient:** Land succeeds but job remains on `meteorite-{candidate_id}` when enrich returned a non-empty `company_stem`; or stem ensure happens but `save_meteorite_job` uses a different short_name.
- **Wrong fix rejected:** Parsing Gmail From/forward headers in `inbox.py` to invent stem — parent law: Ruth decides from CONTENT only (AST-1494).

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/core/inbox.py` — modified — CONTENT + stem → ensure/attach.
- `src/core/gaze_email.py` — modified — same.
- `src/core/gazer.py` — modified — only if still creating on this path.
- `src/core/meteorite.py` — modified — create/`land_meteorite` attach when stem present (shared file; ensure/track units not owned here).
- `src/ui/api/api_companies.py` / `src/ui/api/api_system.py` / NAV+routes — modified — only if METEORITE company list/count sibling ships in this epic.

**Resolved scope notes (planner):**

- **`gaze_email.py`:** File **absent** on tip (retired AST-1134 / AST-1472). All email land paths run through **`inbox.py` → `land_meteorite`** — no separate module to edit.
- **`gazer.py`:** `ingest_meteorite_jobs_from_email_html` has **no production callers** (inbox retargeted AST-1472; only component tests). **No gazer.py changes** — stem attach is centralized in `land_meteorite`.
- **UI files:** Stage 3 optional; when included, add `src/ui/frontend/src/pages/CompaniesMeteorite.tsx` + `src/ui/frontend/src/routes.tsx` route (NAV+routes in ticket scope). Inline list columns on the page — **do not** edit `DATA_SHAPES` / `config.py` (not in this ticket’s Scope).

**Depends on (build gate):** AST-1493 + AST-1494 tips on the epic worktree before product edits — `ensure_meteorite_company(stem=)`, `METEORITE` state, and `enrich_meteorite_land_packet` → `company_stem` on each job. If `sync-child.sh` alone lacks them, merge:

```bash
git fetch origin \
  sub/AST-1484/AST-1493-meteorite-company-state-stem-ensure-track \
  sub/AST-1484/AST-1494-ruth-company-stem-discernment
git merge origin/sub/AST-1484/AST-1493-meteorite-company-state-stem-ensure-track --no-edit
git merge origin/sub/AST-1484/AST-1494-ruth-company-stem-discernment --no-edit
```

Re-run `sync-child.sh` after merges; stop if conflicts need Chuckles.

**AC partition (this ticket):** Parent AC5 + ticket AC5 (email attach). AC6 (Slack/Contact default stem) → `land_meteorite` empty-stem path. AC7 (Style D) → ensure (sibling) + land/inbox debug detail here. Parent AC2–AC4 proven end-to-end only after this ticket + UAT.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/meteorite.py` | `land_meteorite`: enrich-first, per-row stem → ensure → attach; `create_meteorite_job`: optional `stem=`; land Style D stem/company | core |
| `src/core/inbox.py` | Debug Style D: land outcome includes ensured `company` short_name on email paths | core |
| `src/ui/api/api_companies.py` | Optional `view=meteorite_list` + counts key | ui |
| `src/ui/api/api_system.py` | Optional nav badge count `/companies/meteorite_list` | ui |
| `src/utils/config.py` | Optional NAV item only (`NAV_CONFIG` Companies group) — no DATA_SHAPES | utils |
| `src/ui/frontend/src/routes.tsx` | Optional route `companies/meteorite_list` | ui |
| `src/ui/frontend/src/pages/CompaniesMeteorite.tsx` | Optional read-only list page (inline columns) | ui |

## Stage 1: Core — stem attach on `land_meteorite` and `create_meteorite_job`

**Done when:** `land_meteorite` no longer pre-ensures default company before enrich. After successful `enrich_meteorite_land_packet`, each enriched row with non-empty `company_stem` ensures `{stem}-{candidate_id}` and `tracker.save_meteorite_job` uses that short_name; empty/missing stem uses `default_stem` (`meteorite-{candidate_id}`). `create_meteorite_job` accepts optional `stem=` forwarded to `ensure_meteorite_company`. Top-level return `company` / `company_inserted` reflect the **first** saved row’s ensure. Enrich failure returns `company: None` (no orphan default ensure). With `debug=True`, land save loop detail includes `stem=` and `company=`; `debug=False` adds no new contract lines.

1. In `src/core/meteorite.py`, update module docstring: AST-1495 stem attach on land/create; land ensures **after** enrich using Ruth `company_stem`.

2. **`land_meteorite` — remove pre-enrich ensure.** Delete the block that calls `ensure_meteorite_company(cid, debug=debug)` and sets `short_name` **before** the link-scrape / enrich section (~lines 261–262 on pre-1493 tip). Do not ensure until enrich succeeds.

3. **`land_meteorite` — enrich failure path.** In the `if not enrich.get("success") or not enrich.get("jobs"):` return, set `"company": None` and `"company_inserted": False` (remove references to pre-enrich `short_name` / `ensured`).

4. **`land_meteorite` — per-row stem ensure + attach.** Replace the save loop body:

   a. `row_stem = (row.get("company_stem") or "").strip() if isinstance(row.get("company_stem"), str) else ""`  
   b. `ensured_row = ensure_meteorite_company(cid, stem=row_stem or None, debug=debug)`  
   c. `row_company = ensured_row["short_name"]`  
   d. Pass `company=row_company` into `tracker.save_meteorite_job(...)` (not a batch-level `short_name`).  
   e. Track `first_company` / `first_company_inserted` from the first iteration for the top-level return dict.  
   f. When `debug=True`, extend the existing `log.debug_detail(...)` in the save loop with `stem={row_stem!r} company={row_company!r}` (keep existing found/recorded fields).

   ⚠️ **Decision:** Per-row ensure (not one stem per land call) — Ruth returns `company_stem` per jobs item; a single email with multiple link-scrape rows may differ. `ensure_meteorite_company` is idempotent; no cross-row cache required.

   ⚠️ **Decision:** Empty `company_stem` → pass `stem=None` so ensure uses `default_stem` (Slack/Contact / no discernible sender) — satisfies ticket AC6 without a separate code path.

5. **`land_meteorite` — return dict.** Set `"company": first_company` and `"company_inserted": first_company_inserted` (may be `None` / `False` when save loop never runs).

6. **`create_meteorite_job` — optional stem.**

   a. Add parameter `stem: Optional[str] = None` after `job_link`.  
   b. Change ensure call to `ensure_meteorite_company(candidate_id, stem=stem, debug=debug)`.  
   c. Docstring: optional stem for callers that already know it; email-bound land uses `land_meteorite`, not this helper.

7. Do **not** edit `consult.py`, `ensure` implementation, TASK_CONFIG, inbox, or UI in this stage.

## Stage 2: Inbox — email path observability (CONTENT already flows)

**Done when:** Email land helpers still pass full stripped HTML to `land_meteorite(text=…)` (unchanged). With `debug=True`, `_land_bound_inbox_message` and `create_meteorite_job_from_inbox_message` emit Style D detail `company={…}` from the land result after `await land_meteorite`. No new Gmail or header parsing.

1. In `src/core/inbox.py`, **`_land_bound_inbox_message`**: in the existing post-land `if debug:` block (after `html_len=…`), add:

   ```python
   logger.debug_detail(f"company={land.get('company')!r}")
   ```

2. In **`create_meteorite_job_from_inbox_message`**, step-4 debug block: add the same `company={land.get('company')!r}` detail line after the existing `created=/skipped=` detail.

3. Confirm **`run_fetch_email`** / **`land_inbox_message_ids`** still route through `_land_bound_inbox_message` only — no import of gazer ingest (already true AST-1472).

4. Do **not** add `gaze_email.py` (file does not exist). Do **not** change strip/bind logic or call `ensure_meteorite_company` from inbox — land owns ensure+attach.

## Stage 3 (optional): Thin METEORITE companies list for UAT provenance

**Done when:** Operators see a **Meteorite** entry under Companies nav listing companies in state **METEORITE** for the selected candidate (read-only; no bulk state change). Count badge works. AC5 still verifiable via job row; this stage is for sender-level tracing per parent epic.

⚠️ **Decision:** Include this stage — parent Functional scope #1 and UAT tracing require visibility of stem-keyed short_names that do not match `meteorite-` prefix or Recommended partition (AST-1493 plan deferral). Skip entire stage only if Susan confirms job-detail inspection alone is enough (stop → Plan Discuss, do not partial-ship API without nav).

1. **`src/ui/api/api_companies.py`**

   a. Import `METEORITE_CONFIG` from `src.utils.config`.  
   b. In `list_view()`, add branch before final `else`:

   ```python
   elif view == "meteorite_list":
       rows = list_companies(
           states=[METEORITE_CONFIG["company_state"]],
           candidate_id=candidate_id,
       )
   ```

   c. In `counts()`, add:

   ```python
   "/companies/meteorite_list": count_companies(
       states=[METEORITE_CONFIG["company_state"]],
       candidate_id=candidate_id,
   ),
   ```

2. **`src/ui/api/api_system.py`** — in `_get_company_counts`, add the same `/companies/meteorite_list` entry using `METEORITE_CONFIG["company_state"]` (mirror `api_companies.counts`).

3. **`src/utils/config.py`** — in `NAV_CONFIG` Companies `items`, after Ignored:

   ```python
   {"label": "Meteorite", "path": "/companies/meteorite_list"},
   ```

   NAV comment only — no DATA_SHAPES / METEORITE_CONFIG block edits.

4. **`src/ui/frontend/src/pages/CompaniesMeteorite.tsx`** — new page modeled on `CompaniesIgnored.tsx`:

   - Title `"Meteorite"`.
   - Fetch `GET /api/companies?view=meteorite_list&candidate_id=…`.
   - **Inline columns** (do not add DATA_SHAPES): `short_name`, `company_name`, `state`, `state_updated_at`.
   - Row click → `CompanyDetailModal`; **no** bulk actions (METEORITE is roster-inert).

5. **`src/ui/frontend/src/routes.tsx`** — add `{ path: "companies/meteorite_list", element: <CompaniesMeteorite /> }` next to `companies/ignored`; import the page component.

## Execution contract

- Stages in order; steps in order within a stage.
- One commit per stage on epic worktree; push `git push origin HEAD:sub/AST-1484/AST-1495-email-land-paths-apply-stem-company-attach` after each.
- No files outside Files Changed (Stage 3 skippable as a whole).
- Ambiguity / missing AST-1493–1494 APIs after merge → stop, comment on **parent** AST-1484 with Stage blocked format, wait.
- Test tree / bible: Betty only — engineer does not edit `tests/` or `docs/test-bible/**`.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Review (build stub)

**Publish ref:** `origin/sub/AST-1484/AST-1495-email-land-paths-apply-stem-company-attach`
**Plan path:** `docs/features/meteorite/ast-1495-email-land-paths-apply-stem-company-attach.md`

**Built tip:** `a49319ffb4af6ce024838b21f62632a596e67a00` (`a49319ff`)

| Stage | Commit | Summary |
|-------|--------|---------|
| merge | `94ca7657` | stack AST-1493 + AST-1494 dependency merges |
| 1 | `625acfa7` | `land_meteorite` per-row stem ensure+attach; `create_meteorite_job` optional `stem=` |
| 2 | `787ad5c2` | inbox debug `company=` on email land paths |
| 3 | `a49319ff` | METEORITE companies API view, nav, read-only list page |

**Betty note:** component tests for land stem attach, inbox debug, meteorite_list API deferred to qa-child.

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1495
**Overall:** APPROVED
**Publish ref:** `sub/AST-1484/AST-1495-email-land-paths-apply-stem-company-attach` @ `4059b632ca56e81af574c7eb07ef4b61fb3de638`

## Traceability
AC5→S1 enrich-first per-row `company_stem`→`ensure_meteorite_company(stem=)`→`save_meteorite_job(company=…)`; AC6→S1 empty stem→`default_stem` via `stem=None`; AC7→S1 land debug `stem=`/`company=` + S2 inbox post-land `company=` detail (ensure Style D from AST-1493); parent AC2–AC4 end-to-end→requires AST-1493+1494 merge gate then this wire; parent AC1/AC8 UI trace→S3 optional Meteorite nav/list.

## Findings

### discuss
- **Location:** Scope gate — `meteorite_email` AUTO dispatch
- **Finding:** `src/core/meteorite_email.py` still calls `create_meteorite_job` without `land_meteorite` / `company_stem` enrich; not in Files Changed.
- **Recommendation:** Acceptable child partition (inbox land paths only per AST-1472 retarget); flag for epic completeness if AUTO mailbox ingest should also stem-key — follow-on, not this ticket.

### discuss
- **Location:** Plan doc (top-level sections)
- **Finding:** No `## Self-Assessment` (conf / blast-radius).
- **Recommendation:** Optional add; UAT fitness + scope gate + stage decisions are otherwise explicit.

### acceptable
- **Location:** Scope gate — `gaze_email.py` / `gazer.py`
- **Finding:** Ticket lists both; planner correctly resolves gaze_email absent (AST-1472) and gazer ingest has no production callers — stem attach centralized in `land_meteorite`.
- **Recommendation:** No gazer edits required.

### acceptable
- **Location:** Stage 3 — `CompaniesMeteorite.tsx`
- **Finding:** Inline columns instead of `DATA_SHAPES` (differs from `CompaniesIgnored.tsx` shapes fetch).
- **Recommendation:** Plan explicitly forbids DATA_SHAPES edits — consistent with ticket NAV-only config scope.

### acceptable
- **Location:** Depends on (build gate)
- **Finding:** Publish-ref tip still pre–AST-1493/1494 product APIs; plan documents merge commands before build.
- **Recommendation:** Engineer must run merge gate — plan blocks correctly if APIs missing.

## Radia review

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1495  
**Publish ref:** `origin/sub/AST-1484/AST-1495-email-land-paths-apply-stem-company-attach` @ `776866b590919db420d287786371a090eafe54f1`  
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.do-task-delegation | scoped | conforms | land still delegates enrich to existing `do_task` / consult path |
| astral.config.config-source-of-truth | scoped | conforms | METEORITE list uses `METEORITE_CONFIG["company_state"]`; NAV entry in `NAV_CONFIG` |
| astral.layers.core-vs-external-bright-line | scoped | conforms | no new external I/O; land/enrich/tracker flow unchanged in layer shape |
| astral.layers.import-direction | scoped | conforms | core→consult/tracker; ui/api→roster+utils config |
| astral.standards.debug-contract-gated | scoped | conforms | inbox `company=` and land `stem=`/`company=` detail only inside existing `debug=True` blocks |
| astral.standards.dry-and-focused-functions | scoped | conforms | stem attach localized to land save loop + thin API/list additions |
| astral.standards.in-scope-only | scoped | conforms | engineer footprint matches Files Changed |
| astral.standards.no-cross-contamination | scoped | conforms | consumes AST-1493 ensure + AST-1494 enrich map |
| astral.standards.no-hardcoded-sets | scoped | conforms | METEORITE state from `METEORITE_CONFIG` |
| orch.git.betty-merge-tests-one-sha | universal | conforms | tip `776866b5` is `merge-tests(AST-1495)` |
| orch.pipeline.plan-is-bible | universal | conforms | three stages match plan |

## Findings

### fix-now

(none)

### discuss

- **Location:** Joan validate — `meteorite_email` AUTO dispatch
- **Finding:** `meteorite_email` path may still call `create_meteorite_job` without Ruth `company_stem` enrich / `land_meteorite`.
- **Recommendation:** Acceptable child partition (inbox land paths only per AST-1472). Epic follow-on if AUTO mailbox ingest should stem-key — not blocking this ticket.

## What's solid

- Parent AC5 wire is correct: enrich-first → per-row stem ensure → `save_meteorite_job(company=…)` attaches stem-keyed short_name.
- Empty/missing `company_stem` correctly falls through to `default_stem` via `stem=None`.
- METEORITE companies list gives UAT provenance without touching `DATA_SHAPES`.
