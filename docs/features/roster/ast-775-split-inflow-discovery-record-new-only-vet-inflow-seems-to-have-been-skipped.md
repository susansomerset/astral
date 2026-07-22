<!-- linear-archive: AST-775 archived 2026-07-22 -->

## Linear archive (AST-775)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-775/split-inflow-discovery-to-record-new-only-vet-inflow-seems-to-have  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-754 — vet_inflow seems to have been skipped?  
**Blocked by / blocks / related:** parent: AST-754; blocks: AST-776

### Description

## What this implements

Refactor **inflow_discovery** so it only runs CSE per stale term, URL-dedupes hits against the candidate's existing company URLs, and records each unique hit as a **NEW** company row with the deduped CSE blurb stored on the company record. Remove the hardcoded inline **vet_inflow_discovery** call from the discovery batch. Register **VET_FAILED** as a terminal company state for downstream vet rejects. Zero deduped hits after CSE is a successful discovery run with explicit nothing-to-record reporting.

## Acceptance criteria

1. **inflow_discovery** creates **NEW** rows from deduped CSE hits (candidate URL dedupe applied) and does **not** call **vet_inflow_discovery** inside that batch (no shared batch id, no inline **do_task**).
2. Susan's example class (`inflow_discovery-24004a9a-8835-4733-97ba-64cce70fde38`) cannot recur: discovery batch logs must not show **vet_inflow_discovery** LLM activity under the discovery batch id.
3. Zero deduped hits → **inflow_discovery** success with explicit nothing-to-record semantics.

## Boundaries

* Does not implement **vet_inflow_discovery** as a separate company dispatch (sibling ticket).
* Does not update vet Admin prompts (sibling ticket).
* Does not change Phase 0 search-term artifacts (AST-504) or per-term staleness cadence (AST-525).
* Does not change manual **IMPORTED** import paths.

## Notes for planning

Primary files: `src/core/roster.py`, `src/utils/config.py` (**VET_FAILED** in **COMPANY_STATES**), `src/core/consult.py` / `src/core/dispatcher.py` if dispatch reporting changes. Debug: AST-538 Style D on discovery path only.

## Git branch (authoritative)

Per **orientation** § Branch law: parent **ftr/AST-754-vet-inflow-discovery-split**, child **sub/AST-754/<child-segment>**. Created at dispatch-parent.

### Comments

#### betty — 2026-06-23T21:07:21.306Z
[check-linear]

Republished \`origin/sub/AST-754/AST-775-split-inflow-discovery-record-new-only\` @ \`34a95c6\` — linear history on \`origin/ftr/AST-754-vet-inflow-discovery-split\` (no tests-branch merge ancestry).

**\`validate-sub-log.sh\`:** \`RESULT: ok\` (sub-only vs ftr).

**Delivery:** cherry-picked test patch from \`origin/tests\` \`6ac4e24\` as single-parent \`merge-tests(AST-775)\` (not \`git merge\` of tests SHA — avoids \`Merge remote-tracking branch\` / AST-773 bleed).

**Sub-only commits (9):** \`plan\` → \`code\`×2 → \`docs\` stub → \`merge-tests\` → \`test\` → \`docs\` Radia → \`resolve\` → \`docs\` resolution.

**Note:** first commit reworded to \`plan(AST-775):\` (was \`docs(AST-775): plan\`). Added bookkeeping \`resolve(AST-775): — clean\` (was missing on prior tip; ticket already User Testing).

Status unchanged (**User Testing**). Chuckles may re-run \`merge-child\`.

— Betty

#### chuckles — 2026-06-23T21:02:59.083Z
**[merge-child] blocked:** `validate-sub-log.sh` rejects `origin/sub/AST-754/AST-775-split-inflow-discovery-record-new-only` — **Merge remote-tracking branch** subjects in sub-only range (from `merge-tests(AST-775)` pulling `origin/tests` history). Republish sub from `origin/ftr/AST-754-vet-inflow-discovery-split` with a clean single `merge-tests(AST-775)` (no pull-merge subjects in range).

@Betty White — tests/bible hygiene on **AST-775** publish ref.

— Chuckles

#### radia — 2026-06-23T21:01:25.634Z
### Plan fidelity

Diff `origin/dev...origin/sub/AST-754/AST-775-split-inflow-discovery-record-new-only` @ `8e78c56` (product) + review doc `bbca4da`.

Stages 1–3 land as planned: **`VET_FAILED`** + **`(NEW, VET_FAILED)`**; **`record_inflow_discovery_hit`** with mechanical hostname slug, **`inflow_discovery_blurb`** / **`inflow_discovery_notes`**, expanded URL dedupe, slug suffix **`_2`…`_9`**; **`run_inflow_discovery_batch`** is record-only — no inline **`do_task(vet_inflow_discovery)`**, no **`vet_task_key`** in function; zero deduped hits is success with updated debug outcome string.

### ASTRAL_CODE_RULES

| Bucket | Result |
| --- | --- |
| §2.6 state machine | Discovery creates **`NEW`** only — never **`WEBSITE_FOUND`** from this path |
| §1.5.1 debug | Per-hit **`debug_index`** + **`debug_detail`** when **`debug=True`**; batch summary via **`debug_detail`** |
| §3.3 / layer | **`hashlib`** at module top; no new cross-layer violations |
| Cross-ticket | No **`consult`**, **`dispatcher`**, or vet dispatch seed — correctly deferred to **AST-776** |

### Issues

**fix-now:** none

**discuss:** none

**Advisory:** **`_candidate_company_urls`** is rebuilt on each **`record_inflow_discovery_hit`** call — fine for typical hit counts.

### Doc

Review table: `docs/features/roster/ast-775-split-inflow-discovery-record-new-only-vet-inflow-seems-to-have-been-skipped.md` (Review section).

**Verdict:** Clean — **`resolve-child`** may advance per §9a.

#### betty — 2026-06-23T20:59:03.338Z
## QA test manifest (AST-775)

**Publish ref:** `origin/sub/AST-754/AST-775-split-inflow-discovery-record-new-only` @ `8e78c56` (`merge-tests` + bleed revert)

**Bible shasum (publish ref):**
- `docs/test-bible/core/roster.md` — `9f4bfdffb6802f465a531bdc36e2720f900c38a7`
- `docs/test-bible/utils/config.md` — `c640f9b76ac35868911e72476b0d90e3735a8c45`

**Broken / revised (this pass):**
- `TestAst505InflowDiscovery::test_run_batch_happy_path` — removed inline `do_task` / vet ingest mocks; asserts mechanical `co_example` **NEW** record (**AST-775**).
- `TestAst505InflowDiscovery::{test_run_batch_cse_failure_continues,test_run_batch_searches_only_stale_terms}` — dropped obsolete `do_task` mocks.

**Manifest (test-child):**

1. **Config — VET_FAILED terminal state**
   `tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_vet_failed_state_and_transition`

2. **Discovery hit helpers — slug, blurb, record NEW, dedupe, slug suffix**
   `tests/component/core/test_roster.py::TestAst775InflowDiscoveryRecordNew`

3. **Batch record-only path (no inline vet) + consult routing**
   `tests/component/core/test_roster.py::TestAst505InflowDiscovery`

**Narrowed run:**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_roster.py::TestAst505InflowDiscovery \
  tests/component/core/test_roster.py::TestAst775InflowDiscoveryRecordNew \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_vet_failed_state_and_transition \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless widened.

— Betty

#### hedy — 2026-06-23T20:55:56.585Z
[qa-handoff] tests/component/core/test_roster.py inflow discovery tests mock do_task(vet_inflow_discovery) — update for record-only discovery batch (record_inflow_discovery_hit, no inline vet). origin/sub/AST-754/AST-775-split-inflow-discovery-record-new-only @ 23fb0b2

#### hedy — 2026-06-23T20:52:54.463Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-754/AST-775-split-inflow-discovery-record-new-only/docs/features/roster/ast-775-split-inflow-discovery-record-new-only-vet-inflow-seems-to-have-been-skipped.md

**Scope:** Single-Component — config.py VET_FAILED registration plus roster.py discovery batch (remove inline do_task(vet_inflow_discovery), record NEW rows with inflow_discovery_blurb).

**Conf:** Medium — mechanical hostname slug and expanded URL dedupe replace vet-assigned slugs at discovery time; sibling AST-776 completes vet dispatch.

**Risk:** Medium — dedupe/slug collision bugs could duplicate or skip roster rows; contained to inflow discovery for one candidate, no IMPORTED or job consult impact.

---

# AST-775 — Split inflow_discovery to record NEW only

- **Linear:** [AST-775](https://linear.app/astralcareermatch/issue/AST-775/split-inflow-discovery-to-record-new-only-vet-inflow-seems-to-have)
- **Parent:** [AST-754](https://linear.app/astralcareermatch/issue/AST-754/vet-inflow-seems-to-have-been-skipped)
- **Publish ref:** `origin/sub/AST-754/AST-775-split-inflow-discovery-record-new-only`

Discovery today runs Google CSE per stale search term, dedupes hits, then calls **`do_task(vet_inflow_discovery)`** inside the same candidate batch — so vet LLM activity shares the discovery **`batch_id`**. This ticket removes that inline vet hop. **`run_inflow_discovery_batch`** records each URL-deduped CSE hit as a **`NEW`** company row with the hit blurb stored on the company record, and registers **`VET_FAILED`** as a terminal company state for the sibling vet dispatch (**AST-776**). Zero deduped hits after CSE is a successful discovery run with explicit nothing-to-record reporting.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add **`VET_FAILED`** to **`COMPANY_STATES`**; add **`("NEW", "VET_FAILED")`** to **`ASTRAL_CONFIG["company_state_transitions"]`** | utils |
| `src/core/roster.py` | Mechanical slug + **`record_inflow_discovery_hit`**; expand URL dedupe; refactor **`run_inflow_discovery_batch`** (no **`do_task`**) | core |

**Out of scope (this ticket):** `src/core/consult.py`, `src/core/dispatcher.py`, dispatch seed rows for **`vet_inflow_discovery`**, Admin prompt text, Betty tests.

## Stage 1: Register VET_FAILED terminal state

**Done when:** **`VET_FAILED`** is a valid company state key; **`transition_company_state(..., "VET_FAILED")`** from **`NEW`** is allowed by config (no batch criteria — terminal like **`IGNORE`** / **`PREFILTER_FAILED`**).

1. In **`src/utils/config.py`**, inside **`COMPANY_STATES`**, after **`PREFILTER_FAILED`**, add:
   ```python
   "VET_FAILED": {},
   ```
2. In **`ASTRAL_CONFIG["company_state_transitions"]`**, after the existing **`("NEW", "NO_WEBSITE")`** pair, add:
   ```python
   ("NEW", "VET_FAILED"),
   ```
3. Do **not** add **`vet_inflow_discovery`** dispatch seed, change **`TASK_CONFIG["vet_inflow_discovery"].entity_type`**, or touch **`INFLOW_CONFIG["discovery"]["vet_task_key"]`** — sibling **AST-776** owns vet dispatch wiring.

⚠️ **Decision:** **`VET_FAILED`** is registered here so **AST-776** can transition rejects without a follow-on config ticket; this ticket does not implement vet transitions.

## Stage 2: Discovery hit recording helpers

**Done when:** A single CSE hit can be recorded as **`NEW`** with blurb persisted on **`company_data`**, without calling **`ingest_new_companies`** (which may still set **`WEBSITE_FOUND`** when a website is supplied — vet path in **AST-776** may reuse it later).

1. In **`src/core/roster.py`**, after **`_normalize_company_url_for_dedupe`**, add **`_slug_from_discovery_url(url: str) -> str`**:
   - Normalize with **`_normalize_company_url_for_dedupe(url)`**; parse netloc.
   - Strip leading **`www.`** from netloc if present.
   - Build slug: lowercase netloc, replace **`.`** with **`_`**, keep only **`[a-z0-9_]`** (drop other chars).
   - If result empty after sanitize, set slug to **`f"inflow_{hashlib.sha256(norm.encode()).hexdigest()[:12]}"`** (import **`hashlib`** at module top if not already present).
   - Return slug.

2. Add **`_discovery_blurb_line(hit: dict, *, index: int = 0) -> str`**:
   - Return **`f"{index:03d}|{title}|{url}|{snippet}"`** where **`title`**, **`url`**, **`snippet`** come from hit keys (empty string if missing); truncate snippet to **500** chars (same cap as current discovery vet assembly).

3. Expand **`_candidate_company_urls(candidate_id: str) -> Set[str]`**:
   - Keep existing collection from **`company_website`** and **`job_site`** on **`list_companies(candidate_id=candidate_id)`** rows.
   - Also, for each row, read **`company_data`** (dict on row or via existing accessor pattern in this file). If **`inflow_discovery_notes`** is a non-empty string, add **`_normalize_company_url_for_dedupe(notes)`** when non-empty.
   - Also add normalized URL from **`inflow_discovery_blurb`** when present: parse the **third pipe segment** (index **`2`** after split on **`|`, max 4 parts**) as the hit URL and normalize it — if segment missing, skip.

4. Add **`record_inflow_discovery_hit(candidate_id: str, hit: dict) -> tuple[bool, str]`** returning **`(recorded: bool, outcome: str)`** for debug:
   - **`url = (hit.get("url") or "").strip()`**; if empty, return **`(False, "skipped empty url")`**.
   - **`norm = _normalize_company_url_for_dedupe(url)`**; if empty or **`norm in _candidate_company_urls(candidate_id)`**, return **`(False, f"skipped duplicate url {url!r}")`**.
   - Derive **`slug = _slug_from_discovery_url(url)`**; if invalid per **`_INFLOW_SLUG_RE`**, return **`(False, f"invalid slug from url {url!r}")`**.
   - **Slug collision:** if **`get_company(slug)`** exists:
     - Same **`candidate_id`** → return **`(False, f"duplicate slug {slug!r}")`**.
     - Different **`candidate_id`** → try **`{slug}_2`**, **`{slug}_3`**, … up to **`{slug}_9`**; if all taken globally, return **`(False, f"slug collision for {url!r}")`**.
   - Call **`save_company(short_name=slug, state="NEW", company_website="", candidate_id=candidate_id, company_name=slug)`** — always **`NEW`**, never **`WEBSITE_FOUND`** from discovery.
   - Call **`save_company_data(slug, {"inflow_discovery_blurb": _discovery_blurb_line(hit), "inflow_discovery_notes": url})`** — blurb is what **AST-776** vet reads; notes keeps the CSE hit URL for dedupe and Susan's existing UAT filters.
   - Return **`(True, f"recorded NEW slug={slug}")`**.

⚠️ **Decision:** Mechanical hostname slug replaces AI-assigned slug at discovery time; **AST-776** vet may refine **`company_website`** / display name but does not re-slug the row.

⚠️ **Decision:** Store both **`inflow_discovery_blurb`** (full pipe line for vet prompt assembly) and **`inflow_discovery_notes`** (URL only) — extends existing **AST-505** notes key without breaking UAT queries that filter on notes.

## Stage 3: Refactor run_inflow_discovery_batch — record only, no vet

**Done when:** A discovery dispatch run executes CSE + dedupe + per-hit **`record_inflow_discovery_hit`**; never imports or calls **`do_task`** for **`vet_inflow_discovery`**; zero deduped hits returns success with explicit nothing-to-record semantics; debug logs show record outcomes only (AST-538 Style D).

1. In **`run_inflow_discovery_batch`**, keep the existing stale-term loop, CSE calls, cross-term URL dedupe into **`all_hits`**, and **`update_company_search_term_last_scan_at`** after each successful CSE — unchanged from current **AST-525** behavior.

2. **Remove entirely** (lines ~501–604 today):
   - Building **`live_content`** for vet.
   - **`do_task(task_key=cfg["vet_task_key"], ...)`** and all vet failure / parsed **`results`** handling.
   - The vet results loop that calls **`ingest_new_companies`** with vet **`action`/`short_name`/`website`**.

3. **Replace** post-CSE logic with:
   - If **`not all_hits`**: when **`debug`**, emit one **`debug_index`** with **`outcome="no deduped hits — nothing to record"`** (replace current **`"no deduped hits after CSE — vet skipped"`** wording). Return **`{total_processed: 1, total_passed: 0, total_failed: 0, total_errors: errors}`** — **not** an error; zero hits is success per AC #3.
   - Else iterate **`all_hits`** with enumerate; for each hit call **`record_inflow_discovery_hit(candidate_id, hit)`**.
   - When **`debug`**, one **`debug_index`** per hit (**`index=i+1`**, **`total=len(all_hits)`**, identifier = normalized URL or slug from outcome, **`outcome=`** from helper return string); **`debug_detail`** with **`title`**, **`url`**, record vs skip reason.
   - Count **`recorded`** vs **`skipped`** from helper booleans.
   - When **`debug`**, batch-end **`debug_detail`** summary: **`terms_searched`**, **`deduped_hits`**, **`recorded`**, **`skipped`**, **`errors`**.
   - Return **`{total_processed: 1, total_passed: recorded, total_failed: skipped, total_errors: errors}`**.

4. Do **not** reference **`cfg["vet_task_key"]`** anywhere in this function after refactor ( **`INFLOW_CONFIG`** key may remain for **AST-776** ).

5. Do **not** change **`consult.run_consult_task`** candidate branch — it already delegates to **`run_inflow_discovery_batch`** only.

### Self-review (Stage 3)

| Rule | OK? |
|------|-----|
| §2.6 state machine | Discovery never transitions to **`WEBSITE_FOUND`**; only creates **`NEW`** rows |
| §1.5.1 debug | Contract lines only when **`debug=True`**; no vet LLM under discovery batch id |
| §2.5 bright line | No new external I/O; CSE unchanged |

## Stage 4: Verification (build-child handoff)

**Done when:** Product code matches stages 1–3; engineer confirms no **`do_task`** / **`vet_inflow_discovery`** references remain in **`run_inflow_discovery_batch`**.

1. Grep **`src/core/roster.py`** for **`vet_task_key`** inside **`run_inflow_discovery_batch`** — must be zero matches.
2. Run targeted component tests if green without test edits; if **`tests/component/core/test_roster.py`** inflow discovery tests fail (they mock **`do_task`** today), post **`[qa-handoff]`** on **AST-775** assigning Betty — **do not** patch **`tests/`** locally (pre-commit hook).

## Execution contract (developer agent)

- Execute stages **1 → 4** in order; one commit per stage on epic worktree, publish each to **`origin/sub/AST-754/AST-775-split-inflow-discovery-record-new-only`** via **`build-child`** publish ritual.
- Do **not** implement **AST-776** vet dispatch, Admin prompts, or dispatch seed for **`vet_inflow_discovery`** on **`NEW`**.
- Do **not** add files beyond the table above.
- Blocking ambiguity → comment on parent **AST-754** with 🛑 format from **plan-child**.

## Self-Assessment

**Scope:** `Single-Component` — **`config.py`** state registration plus **`roster.py`** inflow discovery path only; no dispatcher or consult wiring changes expected.

**Conf:** `Medium` — mechanical slug derivation and expanded URL dedupe are new behavior, but the refactor boundary (remove inline vet, record **`NEW`**) is explicit and mirrors the parent epic table.

**Risk:** `Medium` — wrong dedupe or slug collision handling could duplicate companies or skip valid hits; contained to inflow discovery ingest for one candidate at a time, does not affect **`IMPORTED`** or job consult pipelines.

### Justifications

- **Scope:** Two product files, one cohesive discovery-batch behavior change.
- **Conf:** Slug-from-hostname is a deliberate replacement for vet-assigned slugs at discovery time; sibling **AST-776** completes the funnel.
- **Risk:** Incorrect URL dedupe affects roster rows for a candidate only; no cross-candidate dispatch side effects beyond global slug PK collisions (handled by suffix loop).

## Self-review (ASTRAL_CODE_RULES)

| Rule | Notes |
|------|-------|
| §1.3 DRY | Reuse **`_normalize_company_url_for_dedupe`**, **`list_companies`**, **`save_company`**, **`save_company_data`** |
| §1.4 no magic numbers | **500** snippet cap matches existing discovery assembly; suffix cap **`_9`** is local collision bound |
| §2.1 config | **`VET_FAILED`** only in **`COMPANY_STATES`** / transitions — no inline state strings elsewhere |
| §2.6 state machine | No daisy-chain; discovery does not call vet or **`run_next`** |
| §3.3 imports | **`hashlib`** stdlib only; no new cross-layer violations |
| §3.5 naming | **`record_inflow_discovery_hit`**, **`inflow_discovery_blurb`** align with existing inflow keys |

No **`conf-!!-NONE`** conflicts identified.

## Review stub (Hedy / build)

**Publish ref:** `origin/sub/AST-754/AST-775-split-inflow-discovery-record-new-only`  
**Product tip:** `23fb0b2` — `6037df1` (VET_FAILED config) + `23fb0b2` (discovery record-only batch)

**Built:** Removed inline `do_task(vet_inflow_discovery)` from `run_inflow_discovery_batch`; added `record_inflow_discovery_hit`, mechanical hostname slug, expanded URL dedupe (`inflow_discovery_notes` / `inflow_discovery_blurb`).

**QA note:** `tests/component/core/test_roster.py` inflow discovery tests mock `do_task` — Betty manifest update expected at Code Complete.

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-754/AST-775-split-inflow-discovery-record-new-only` @ `8e78c56`

### What's solid

| Area | Notes |
| --- | --- |
| Plan fidelity | Stages 1–3 match: **`VET_FAILED`** + **`(NEW, VET_FAILED)`** in config; **`record_inflow_discovery_hit`**, mechanical hostname slug, expanded URL dedupe (**notes** / **blurb** pipe URL), slug suffix collision **`_2`…`_9`**; **`run_inflow_discovery_batch`** record-only — no **`do_task`** / **`vet_task_key`** / vet ingest loop; zero deduped hits returns success with updated debug wording. |
| §2.6 state machine | Discovery creates **`NEW`** rows only; never **`WEBSITE_FOUND`** from this path; no daisy-chain vet under discovery **`batch_id`**. |
| §1.5.1 debug | Per-hit **`debug_index`** + **`debug_detail`** when **`debug=True`**; batch-end summary via **`debug_detail`**; contract gated by **`log.set_debug_flag(debug)`**. |
| Layer / imports | **`hashlib`** stdlib at module top; core→data via existing **`save_company`** / **`list_companies`** pattern; no new cross-layer violations. |
| Cross-ticket boundary | No **`consult.py`**, **`dispatcher.py`**, dispatch seed, or **`vet_inflow_discovery`** wiring — correctly deferred to **AST-776**. |
| Tests / bible | Betty manifest (**`TestAst775InflowDiscoveryRecordNew`**, revised **`TestAst505InflowDiscovery`**, config transition test) aligns with AC table; test-bible rows updated. |

### Issues

| Severity | Item | Location |
| --- | --- | --- |
| — | None | — |

### Recommended actions

| Severity | Action |
| --- | --- |
| **Advisory** | **`record_inflow_discovery_hit`** rebuilds **`_candidate_company_urls`** per hit — acceptable for typical hit counts; revisit only if discovery batches grow large. |
| **Advisory** | Empty/unparseable URL after normalize reports **`skipped duplicate url`** (same branch as true duplicates) — edge case only; optional clearer outcome string if operators ask. |

**Verdict:** Clean — no **fix-now**; **`resolve-child`** may advance per §9a when thread is quiet.

---

## Resolution (Hedy / resolve)

**Date:** 2026-06-23  
**Review ref:** Radia @ `bbca4da` on `origin/sub/AST-754/AST-775-split-inflow-discovery-record-new-only`

No **fix-now** or **discuss** items — product unchanged from **`8e78c56`** / **`23fb0b2`**. Advisory notes (per-hit **`_candidate_company_urls`** rebuild; duplicate-url outcome string) accepted as-is.

**§9a dry-run:** publish ref merges cleanly into **`origin/dev`** and **`origin/ftr/AST-754-vet-inflow-discovery-split`**.

**Outcome:** Ticket advanced to **User Testing**; **AST-776** owns separate vet company dispatch.
