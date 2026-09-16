<!-- linear-archive: AST-1294 archived 2026-09-09 -->

## Linear archive (AST-1294)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1294/html-links-completeness-all-payload-job-links-land-only-32-of-34-jobs  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** AST-1290 — Only 32 of 34 jobs were loaded by parse_meteorite_email  
**Blocked by / blocks / related:** parent: AST-1290

### Description

## What this implements

Own the end-to-end fix so `html_links` meteorite email parse cannot silently drop payload-enumerated job links before ingest. Product guarantee is a post-parse completeness reconcile on the gaze_email path (null titles OK). Observable outcome: the 34-link UAT class loads 34 jobs. Does **not** own Avail/dispatch (AST-1282), int→str coerce (AST-1289), or seed rename.

## In scope

- [X] `pattern.config.config-block` / `astral.config.config-source-of-truth` — reuse existing `METEORITE_EMAIL_INGEST_CONFIG` / `METEORITE_EMAIL_PARSE_CONFIG` (no new magic sets); Ruth payload excludes stay config-owned
- [X] `astral.agent.do-task-delegation` — Ruth still via `do_task` / `_ruth_parse`; completeness is gaze_email post-parse, not a second LLM call
- [X] `astral.standards.debug-contract-gated` — Style D found/recorded/missing link ids when Ruth’s `jobs` is incomplete vs payload links and `debug=True`
- [X] `astral.standards.in-scope-only` / `astral.standards.dry-and-focused-functions` — one helper + `html_links` call site in `src/core/gaze_email.py` only

## Considered but excluded

* AST-1282 Avail / `min_count` / scheduler skip — separate Discussion on Astral Meteorite; not this failure mode
* AST-1289 int→str soft-coerce — adjacent LLM-response family; different path (`src/core/agent.py`)
* Seed rename (`parse_meteorite_email` → `meteorite_email`) / Admin picker contracts — AST-1212 / AST-1214
* Ruth `agent_task` prompt rewrite / fixture sync — prompt alone insufficient per parent; product guarantee is reconcile; AST-1213 payload shape stays
* `subject_url` / `subject_body` redesign — those shapes do not drive a multi-job list from the payload enumeration; reconcile is `html_links`-only
* Re-widen Ruth excludes / Playwright exclude merge — would break AST-1213 click-tracking visibility
* Playwright create/dedupe / archive rule redesign — only ensure omitted links still get an ingest attempt via completed `jobs`

## Acceptance criteria

1. [x] Replaying the UAT message shape (34 Dice `job-detail` links in the Ruth payload enumeration) yields 34 jobs in the parse result used for ingest — including `3628bf85-8915-4525-93ff-2f05e09f9e39` and `add50803-2af1-4f26-aba5-3997c9db8905`.
2. [x] A successful parse no longer silently returns fewer jobs than payload job links for `html_links`; if the model omits links, the product still covers those links for ingest (stub/null title allowed).
3. [x] With `debug=True`, an incomplete Ruth `jobs` list vs payload links is visible as found vs recorded (and missing link ids) under Style D; with `debug=False`, this path adds no new debug lines.
4. [x] Existing null-title job rows still validate and ingest; required `job_link` remains required.
5. [x] AST-1282 Avail/scheduler behavior and AST-1289 datatype coercion are unchanged by this epic.

## Boundaries

* Does **not** fix AST-1282 (Avail vs `min_count` / scheduler skip).
* Does **not** absorb AST-1289 (int→str soft-coerce).
* Does **not** rename seed keys or change Admin picker contracts.
* Does **not** redesign `subject_url` / `subject_body` shapes unless a shared helper is the only safe place for completeness.
* Must not break AST-1213 Ruth payload shape or re-widen Ruth excludes.

## Notes for planning

Single vertical slice: payload assembly (already AST-1213), Ruth result, completeness enforce, and Style D found/recorded ship together. Completeness set = `_ruth_live_parts` link enumeration; match with `normalize_link`; stub missing rows with `job_title: None`.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1290-only-32-of-34-jobs-were-loaded-by-parse_meteorite_email`, child `sub/AST-1290/AST-1294-html-links-completeness-all-payload-job-links-land`. Created at dispatch-parent.

### Comments

#### radia — 2026-08-10T00:44:32.138Z
[code-rubric] revision=2
**Overall:** CLEAN
64 statutes scored, 0 fix-now, 0 discuss.
— Radia

#### betty — 2026-08-10T00:37:41.287Z
## QA test manifest — AST-1294

**Publish:** `origin/sub/AST-1290/AST-1294-html-links-completeness-all-payload-job-links-land` @ `2321dfb9` (`merge-tests(AST-1294): origin/tests 4ccfaddb1f986cb5c8875105fd4181d10f3efa36`)

### Existing coverage (bible-backed)

None sufficient alone — new post-parse reconcile helper needs dedicated cases. Related payload assembly remains:

1. `tests/component/core/test_gaze_email.py::TestAst1213RuthLivePayload` (revised — see broken list)

### Broken / obsolete (revised this pass)

2. `TestAst1213RuthLivePayload::test_html_links_live_content_shape` — empty Ruth `jobs` + payload links now stub-then-ingest; mock `_ingest_link` so the case stays on live_content shape
3. `TestAst1213RuthLivePayload::test_debug_true_emits_ruth_payload_detail` — same ingest stub isolation

### Gaps (new)

4. `tests/component/core/test_gaze_email.py::TestAst1294HtmlLinksJobsComplete::test_uat_34_payload_stubs_two_missing_null_titles` — UAT 34→34 including `3628bf85-…` / `add50803-…` with null titles
5. `…::test_normalize_link_avoids_duplicate_stub` — scheme/slash variants do not double-stub
6. `…::test_preserves_ruth_extras_and_drops_junk_rows` — extras kept; non-dict / empty `job_link` dropped
7. `…::test_debug_true_emits_found_recorded_missing_ids` — Style D found/recorded/missing path-tails when incomplete
8. `…::test_debug_false_or_complete_skips_style_d` — silence when complete or `debug=False`
9. `…::test_html_links_call_site_ingests_stubbed_links` — `_handle_bound` html_links path ingests stubbed payload links

**Integration:** none revised (no existing scenarios assert this path).

### Run

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_gaze_email.py::TestAst1294HtmlLinksJobsComplete \
  tests/component/core/test_gaze_email.py::TestAst1213RuthLivePayload::test_html_links_live_content_shape \
  tests/component/core/test_gaze_email.py::TestAst1213RuthLivePayload::test_debug_true_emits_ruth_payload_detail \
  -q
```

### Bible

`docs/test-bible/core/gaze_email.md` shasum on publish tip: `7334ef9e9aa877488ec04d4575f252c2caa4ba3b`

— Betty

#### joan — 2026-08-10T00:31:49.508Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1294
**Overall:** APPROVED
**Publish-ref tip:** `d54820e881a917d3bdf3003d612904a5b9a44f75` (`origin/sub/AST-1290/AST-1294-html-links-completeness-all-payload-job-links-land`)

## Traceability
AC1→S1; AC2→S1; AC3→S1; AC4→S1; AC5→S1

No fix-now findings. Plan is a single-file `html_links` post-parse reconcile on the existing Ruth payload enumeration (`normalize_link` coverage + null-title stubs + Style D found/recorded/missing when incomplete), faithful to parent AST-1290 boundaries (no Avail/dispatch, no int→str coerce, no seed/prompt/payload reshape).

— Joan
context_tokens≈55000

#### ada — 2026-08-10T00:29:35.883Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1290/AST-1294-html-links-completeness-all-payload-job-links-land/docs/features/agent/ast-1294-html-links-completeness-all-payload-job-links-land.md

`origin/sub/AST-1290/AST-1294-html-links-completeness-all-payload-job-links-land` @ `d54820e8`

**Scope:** Single-Component — one private helper + one `html_links` call site in `src/core/gaze_email.py`; no config/prompt/UI/data edits.

**Conf:** high — payload `links` enumeration and ingest loop already exist; this is a deterministic set-diff + stub append with Style D found/recorded when incomplete.

**Risk:** Medium — bad `normalize_link` matching could stub-duplicate or force ingest of non-job payload hrefs; mitigated by existing Ruth payload excludes and keeping Ruth rows + original payload hrefs on stubs.

---

# html_links completeness — all payload job links land

- **Linear:** [AST-1294](https://linear.app/astralcareermatch/issue/AST-1294/html-links-completeness-all-payload-job-links-land-only-32-of-34-jobs)
- **Parent:** [AST-1290](https://linear.app/astralcareermatch/issue/AST-1290/only-32-of-34-jobs-were-loaded-by-parse-meteorite-email)
- **Publish ref:** `sub/AST-1290/AST-1294-html-links-completeness-all-payload-job-links-land`

Bound `html_links` meteorite email parse can silently drop trailing Dice (and other) links when Ruth’s `jobs` list is shorter than the `--- LINKS ---` enumeration already assembled for the live payload. This ticket hardens the gaze_email ingest path with a post-parse completeness reconcile so every payload-enumerated link is present in the jobs list used for ingest (null titles allowed). Observable UAT class: 34 payload links → 34 jobs including `3628bf85-…` and `add50803-…`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/gaze_email.py` | Add `_ensure_html_links_jobs_complete`; call it on the `html_links` branch after Ruth returns and before `_ingest_link`; Style D found/recorded/missing when incomplete and `debug=True` | core |

No `src/utils/config.py` edits — existing `METEORITE_EMAIL_INGEST_CONFIG` / `METEORITE_EMAIL_PARSE_CONFIG` already own link excludes and parse-mode literals. No `agent_task` prompt rewrite (product guarantee is reconcile; prompt alone is insufficient per parent). No `subject_url` / `subject_body` redesign. No Avail/dispatch (AST-1282), no int→str coerce (AST-1289), no seed rename.

## Stages

### Stage 1: Post-parse html_links completeness reconcile + Style D

**Done when:** Given payload links `L` (length 34) and a Ruth `jobs` list missing the last two Dice URLs, `_ensure_html_links_jobs_complete` returns a list of length 34 that includes those two URLs with `job_title` null; the `html_links` branch in `_handle_bound` ingests from that completed list (not the raw Ruth list). When `debug=True` and Ruth omitted any payload link, Style D shows found vs recorded plus missing link ids; when `debug=False` or the Ruth list already covers every payload link, this helper emits no new debug-contract lines. `subject_url` / `subject_body` / ignore shapes unchanged. `python3 -m py_compile` succeeds for `src/core/gaze_email.py` (repo venv: `~/astral/.venv/bin/python`).

1. In `src/core/gaze_email.py`, add `from src.utils.formatting import normalize_link` next to the other utils imports.

2. Add this private helper immediately above `_ruth_parse` (public functions stay above; helpers stay grouped with Ruth payload helpers):

```python
def _ensure_html_links_jobs_complete(
    jobs: list,
    payload_links: list[str],
    *,
    debug: bool,
) -> list:
    """Ensure every Ruth --- LINKS --- href appears in jobs used for ingest.

    Keeps Ruth rows (order preserved). Appends stub rows ``{job_link, job_title: None}``
    for payload links not covered under ``normalize_link``. Style D only when
    ``debug`` and at least one payload link was missing from Ruth's list.
    """
```

   Implementation rules (binding):

   a. Build `out: list` by iterating `jobs`: keep only items that are `dict` with a non-empty stripped `job_link`. Preserve Ruth order. Do **not** drop Ruth rows whose links are absent from `payload_links` (extras stay).

   b. Build `covered: set[str]` = `{normalize_link(job_link) for each kept row}` (skip empty normalize results).

   c. `missing: list[str]` = payload links (in payload enumeration order) whose `normalize_link(link)` is non-empty and not in `covered`. When appending a stub, also add that norm key to `covered` so duplicate payload hrefs do not double-stub.

   d. For each URL in `missing`, append `{"job_link": <original payload href>, "job_title": None}` to `out`. Do **not** invent titles or metadata.

   e. **Style D** (`astral.standards.debug-contract-gated`): if `debug` is True **and** `missing` is non-empty, emit exactly one index header + one detail line via the module `logger` (same Style D helpers already used in this file — `logger.set_debug_flag` is already applied by callers when `debug=True`; use `logger.debug_index` / `logger.debug_detail` directly, gated by `if debug:`):

      - `debug_index(func="gaze_email._ensure_html_links_jobs_complete", index=1, total=1, identifier="html_links", outcome="reconciled")`
      - `debug_detail(f"found={len(payload_links)} recorded={len(payload_links) - len(missing)} missing={missing_ids}")` where `missing_ids` is a comma-joined list of the **final path segment** of each missing URL (strip trailing `/`, take text after last `/`; if empty segment, fall back to the full URL). For the UAT pair that is `3628bf85-8915-4525-93ff-2f05e09f9e39,add50803-2af1-4f26-aba5-3997c9db8905`.

      `found` = `len(payload_links)`. `recorded` = count of payload links already covered by Ruth before stubs (`len(payload_links) - len(missing)`). Do **not** emit when `missing` is empty. When `debug` is False, emit nothing from this helper.

   f. Return `out`.

⚠️ **Decision:** Product completeness is a post-parse reconcile on the already-enumerated `links` list from `_ruth_live_parts`, not a Ruth prompt rewrite. Parent AC requires ingest coverage even when the model truncates long lists; prompt tightening alone is explicitly insufficient. Leave `data/admin/agent_task.json` / fixtures untouched (AST-1213 payload shape + prompts stay).

⚠️ **Decision:** Match coverage with `normalize_link` (same key as PJL / consult job_link binding) so scheme/trailing-slash variants do not create duplicate stubs when Ruth echoes a normalized form of a payload href. Stub `job_link` values still use the **original** payload enumeration string so Playwright ingest sees the same href Ruth was shown.

⚠️ **Decision:** Apply reconcile only on the `html_links` branch. `subject_body` returns `jd_link` / `content_text` (not a multi-job list from the payload enumeration); `subject_url` has no Ruth jobs list. Parent allows leaving those shapes alone when a shared multi-job completeness check is not required.

3. In `_handle_bound`, `html_links` branch only (the `if not subject and not empty_body:` block), immediately after:

```python
jobs = parsed.get("jobs") if isinstance(parsed.get("jobs"), list) else []
```

   insert:

```python
jobs = _ensure_html_links_jobs_complete(jobs, links, debug=debug)
parsed["jobs"] = jobs
```

   Then keep the existing `for job in jobs:` ingest loop unchanged (still skip non-dicts / empty `job_link`; still call `_ingest_link`). Do **not** change `_finalize_archive`, scrape/dedupe/`min_jd_chars`, archive rules, shape routing, `_ruth_parse`, `_ruth_candidate_links`, `_format_ruth_live_body`, or `subject_body` / `subject_url` branches.

4. Compile check (builder ritual): `~/astral/.venv/bin/python -m py_compile src/core/gaze_email.py`.

## Self-Assessment

**Scope:** `Single-Component` — one private helper + one call site in `src/core/gaze_email.py` (core mailbox ingest); no config, agent, UI, or data-layer changes.

**Conf:** `high` — payload enumeration (`_ruth_live_parts` → `links`) and the html_links ingest loop already exist; this is a deterministic set-diff + stub append with the same Style D `found`/`recorded` habit as AST-1293.

**Risk:** `Medium` — wrong matching could stub-duplicate links or force ingest of every payload href Ruth intentionally skipped as non-job; mitigated by `normalize_link` coverage and by Ruth payload excludes already filtering unsubscribe/prefs/namespace noise before enumeration.

## Code-rules check

- §1.3 DRY: one helper; html_links call site only; no parallel completeness module.
- §1.4 / §2.1: no new hardcoded exclude sets; reuse `normalize_link` and existing config-owned Ruth excludes.
- §1.5.1 debug-contract-gated: Style D only when `debug=True` and incomplete; no new ungated debug lines.
- §2.2 do-task-delegation: Ruth still via `do_task` / `_ruth_parse`; reconcile is gaze_email post-parse, not a second LLM call.
- §3.3 imports: `normalize_link` from `src.utils.formatting` is an allowed core→utils import.
- In-scope-only: no AST-1282 Avail/scheduler, no AST-1289 coerce, no seed rename, no AST-1213 payload reshape.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1290/AST-1294-html-links-completeness-all-payload-job-links-land`
**Tip (pre-review):** `f75e80e1`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `f75e80e1` | `_ensure_html_links_jobs_complete` + html_links call site; Style D found/recorded/missing when incomplete |

## Radia review

[code-rubric] revision=2

**Rubric:** code-rubric.v2
**Publish ref tip:** `2321dfb9`
**Overall:** CLEAN

**Full-set sweep:** all 64 active statutes scored in-session (18 universal + 46 scoped) against `git diff origin/dev...origin/sub/AST-1290/AST-1294-html-links-completeness-all-payload-job-links-land`. Diff layers: `core`, `docs`. No `violates`, no `discuss`.

**What's solid:** `_ensure_html_links_jobs_complete` keeps Ruth rows verbatim (order preserved, extras kept) and only appends null-title stubs for payload hrefs `normalize_link` can't match to a kept row — same key already used for PJL/consult `job_link` binding (`roster.py`, `consult.py`), so scheme/trailing-slash variants don't double-stub. Stub `job_link` keeps the **original** payload enumeration string (not the normalized form), matching the plan's Decision so Playwright ingest sees the href Ruth was shown. Style D (`astral.standards.debug-contract-gated`) fires exactly once — one `debug_index` + one `debug_detail` — only when `debug` is True **and** `missing` is non-empty; `found`/`recorded`/`missing` counts match the plan's formula and `missing_ids` correctly falls back to the full URL when the path-tail split is empty. `logger.set_debug_flag(True)` is already applied by every entry point (`process_gaze_email_messages`, `run_gaze_email_selected_ids`, `run_gaze_email`) before `_handle_bound` runs, so the new helper's direct `debug_index`/`debug_detail` calls are correctly gated without re-deriving the flag. `func="gaze_email._ensure_html_links_jobs_complete"` matches the hardcoded-literal-label convention used everywhere else in this file and in `roster.py`/`meteorite.py`/`inbox.py` — not a `no-hardcoded-sets` concern (labels, not domain data). No `src/utils/config.py` edit — `METEORITE_EMAIL_INGEST_CONFIG`/`METEORITE_EMAIL_PARSE_CONFIG` untouched, matching `pattern.config.config-block`. `subject_url`/`subject_body` branches, `_finalize_archive`, scrape/dedupe/archive rules, and `_ruth_parse`/`_ruth_candidate_links`/`_format_ruth_live_body` are all byte-unchanged. Helper is grouped with the other Ruth-payload private helpers immediately above `_ruth_parse`, matching the plan's explicit placement instruction and the file's existing private-helpers-then-public-entrypoints shape (pre-existing structure, not a new violation). Commit hygiene is clean: `code(AST-1294)` touches only `src/core/gaze_email.py`; the single `merge-tests(AST-1294)` SHA carries Betty's `test(AST-1294)` commit touching only `tests/` + `docs/test-bible/` (`orch.git.betty-merge-tests-one-sha`, `astral.git.engineer-test-tree-ban`, `astral.git.betty-no-src-or-features` all conform). `~/astral/.venv/bin/python -m py_compile src/core/gaze_email.py` clean; `pytest tests/component/core/test_gaze_email.py` — 29 passed, including the new `TestAst1294HtmlLinksJobsComplete` suite (UAT 34→34, normalize dedupe, junk/extras, Style D on/off, call-site stub ingest) and both AST-1213 cases Betty revised for the new ingest-stub isolation.

No fix-now findings. No discuss findings. No stragglers — Joan's `[plan-rubric] revision=1` verdict (**APPROVED**) lists no Excluded statutes to cross-check.

**Pattern conformance:**

| id | verdict | one-line |
|----|---------|----------|
| `pattern.config.config-block` | conforms | No new inline magic set; existing `METEORITE_EMAIL_*_CONFIG` blocks untouched |

**Plan adherence:** Diff matches the Files Changed table and the single stage exactly, including all three `⚠️ Decision` notes (post-parse reconcile not a Ruth prompt rewrite; `normalize_link` coverage with original-href stubs; `html_links` branch only). Self-Assessment `Scope: Single-Component` / `Conf: high` matches the diff's real footprint; `Risk: Medium` mitigation (normalize_link coverage, Ruth excludes already filtering non-job noise) holds — no stub-duplication or over-ingest observed in the UAT/junk-row tests. All 5 parent AC map to Stage 1 per Joan's traceability; AC5 (AST-1282/AST-1289 unchanged) confirmed — this diff touches only `gaze_email.py`.

**Cross-ticket boundary:** Relations: none. No `src/utils/config.py`, `agent_task` prompt, `subject_url`/`subject_body`, Avail/dispatch (AST-1282), int→str coerce (AST-1289), or seed-rename edits — matches parent Boundaries exactly.

## Frame diff

(none — ticket description AC/scope table already accurate)

context_tokens≈62000

— Radia

## Resolution

**2026-08-10** — Radia `[code-rubric] revision=2` **CLEAN** (0 fix-now / 0 discuss). No product changes after review. Publish tip before resolve commit: `c3a4a441` (`docs(AST-1294): Radia review — clean`). Advancing to User Testing.
