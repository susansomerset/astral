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
