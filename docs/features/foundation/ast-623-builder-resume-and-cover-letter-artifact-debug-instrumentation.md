# AST-623 — Builder resume and cover letter artifact debug instrumentation (Debug logging backfill: builder)

- **Linear (this ticket):** [AST-623](https://linear.app/astralcareermatch/issue/AST-623/builder-resume-and-cover-letter-artifact-debug-instrumentation-debug)
- **Parent:** [AST-545](https://linear.app/astralcareermatch/issue/AST-545/debug-logging-backfill-builder)
- **Publish ref:** `origin/sub/AST-545/AST-623-builder-artifact-debug` (child of AST-545; not Linear `gitBranchName`)
- **Depends on:** [AST-538](https://linear.app/astralcareermatch/issue/AST-538/improve-quality-of-debug-logging) / [AST-554](https://linear.app/astralcareermatch/issue/AST-554/debug-logging-contract-and-shared-helper) — shared helper + §1.5.1 on integration line; sibling conventions from [AST-620](https://linear.app/astralcareermatch/issue/AST-620/external-llm-wrapper-debug-instrumentation) (single-call `index 1/1`) and [AST-622](https://linear.app/astralcareermatch/issue/AST-622/gazer-company-gaze-and-job-list-cache-debug-instrumentation).

## Summary

Backfill the **AST-538** debug logging contract across **builder** / artifact HTML generation in `src/core/builder.py`. When `debug=True`, each public render entry point emits one Style D index header (`index 1/1`) plus ` | ` detail for **content source resolution** (job `resume_content` vs candidate `base_resume`, cover letter vs sample text), **enabled structure section keys**, accent/style source, ATS keywords, sections emitted vs skipped, and a **truncated HTML preview** via `debug_detail_block`. Add `debug: bool = False` to all public builder functions and pass it through the internal call chain. **No** HTML output shape changes; `debug=False` emits no new contract lines. **No** `[DEBUG]` grandfather cleanup needed — builder currently has zero logging.

## Out of scope (explicit)

| Item | Owner / note |
|------|----------------|
| `src/ui/api/api_resume_html.py` | Routes do not supply `debug` today — do not add query-param wiring in this ticket |
| `src/core/roster.py`, `consult.py`, `gazer.py`, `dispatcher.py`, `agent.py` | Sibling backfill tickets |
| `src/external/*` LLM wrappers | **AST-546** / **AST-620** |
| Betty log-string tests | Forbidden per parent |
| Builder output HTML, CSS, or artifact schema changes | Forbidden per ticket |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/builder.py` | Module logger; read-only resolution trace helpers; `debug=` on public entry points; contract emission on success and `ValueError` paths | core |

## Stage 1: Module logger, resolution helpers, and `debug` keyword on public APIs

**Done when:** `get_logger(__name__)` exists; read-only helpers return source labels without side effects; all five public functions accept `*, debug: bool = False` and pass `debug` to their delegates; no contract lines emitted yet; existing call sites (no `debug` arg) unchanged.

1. After the existing imports (~line 26), add:

```python
from src.utils.logging import get_logger

_log = get_logger(__name__)
```

2. Add module-private read-only helpers **after** `_coerce_candidate_blob` (~line 64):

```python
def _builder_job_identifier(job: Dict[str, Any]) -> str:
    """Primary debug identifier for a job row (§1.5.1 style D)."""
    return str(job.get("astral_job_id") or job.get("job_title") or "?")


def _resume_content_source_label(job_data: dict, candidate_data: dict) -> str:
    """Read-only label for which blob supplies resume sections (no raises)."""
    artifacts = (job_data or {}).get("artifacts") or {}
    rc = artifacts.get("resume_content")
    if _is_nonempty_resume_dict(rc):
        return "job_data.artifacts.resume_content"
    br = ((candidate_data or {}).get("artifacts") or {}).get("base_resume")
    if _is_nonempty_resume_dict(br):
        return "candidate_data.artifacts.base_resume"
    return "missing"


def _cover_letter_source_label(job_data: dict, candidate_data: dict) -> Optional[str]:
    """Read-only label for cover letter provenance, or None when no cover."""
    artifacts = (job_data or {}).get("artifacts") or {}
    cl = artifacts.get("cover_letter")
    if isinstance(cl, dict) and _cover_letter_nonempty(cl):
        return "job_data.artifacts.cover_letter"
    sample = ((candidate_data or {}).get("context") or {}).get("sample_cover_text")
    if isinstance(sample, str) and sample.strip():
        return "candidate_data.context.sample_cover_text"
    return None


def _accent_source_label(candidate_data: dict) -> str:
    """Read-only label for accent color resolution path."""
    structure = candidate_mod.resolve_resume_structure(candidate_data)
    ac = structure.get("accent_color")
    if isinstance(ac, str) and ac.strip():
        return "resume_structure.accent_color"
    br = ((candidate_data or {}).get("artifacts") or {}).get("base_resume")
    if isinstance(br, dict):
        legacy = br.get("accent_color")
        if isinstance(legacy, str) and legacy.strip():
            return "artifacts.base_resume.accent_color"
    return "BUILD_CONFIG.default_style"


def _emit_builder_failure(
    *,
    func: str,
    identifier: str,
    message: str,
    debug: bool,
) -> None:
    """Emit contract header for a terminal ValueError path."""
    if not debug:
        return
    _log.set_debug_flag(True)
    _log.debug_index(
        func=func,
        index=1,
        total=1,
        identifier=identifier,
        outcome=f"error — {message}",
    )
```

⚠️ **Decision:** Read-only source helpers duplicate existing resolution logic labels only — they do not change `_resolve_resume_sections` / `_resolve_cover_letter` behavior or return types.

3. Update public function signatures and pass-through:

```python
def build_resume(job_id: str, *, debug: bool = False) -> str:
    ...
    return build_resume_from_job(job, _coerce_candidate_blob(row), debug=debug)


def build_resume_from_job(
    job: Dict[str, Any],
    candidate_data: Dict[str, Any],
    *,
    include_cover: bool = False,
    debug: bool = False,
) -> str:
    ...


def build_cover_letter(job_id: str, *, debug: bool = False) -> str:
    ...
    return build_cover_letter_from_job(job, _coerce_candidate_blob(row), debug=debug)


def build_cover_letter_from_job(
    job: Dict[str, Any],
    candidate_data: Dict[str, Any],
    *,
    debug: bool = False,
) -> str:
    ...


def build_base_resume(candidate_id: str, *, debug: bool = False) -> str:
    ...
```

4. Do **not** modify `src/ui/api/api_resume_html.py` — default `debug=False` preserves current API behavior.

## Stage 2: `build_resume_from_job` and `build_resume` contract debug

**Done when:** With `debug=True`, a successful job resume render logs index header + resolution detail (resume source, enabled sections, body section order, keys with content, cover inclusion, accent source, ATS keywords, html length, truncated HTML preview); each `ValueError` in `build_resume` logs a failure header before re-raise; with `debug=False` unchanged.

1. At `build_resume_from_job` entry, after `cd = _coerce_candidate_blob(candidate_data)`:

```python
if debug:
    _log.set_debug_flag(True)
identifier = _builder_job_identifier(job)
```

2. Wrap `_resolve_resume_sections` in try/except — on `ValueError` as `exc`:

```python
_emit_builder_failure(
    func="builder.build_resume_from_job",
    identifier=identifier,
    message=str(exc),
    debug=debug,
)
raise
```

3. After successful resolution and before `return _emit_html_document(...)`, when `debug`:

```python
structure = candidate_mod.resolve_resume_structure(cd)
enabled = candidate_mod.enabled_resume_section_ids(structure)
ordered_body = _structure_ordered_body_ids(structure)
content_keys = sorted(k for k, v in markers.items() if isinstance(v, str) and v.strip())
cover_src = _cover_letter_source_label(job_data, cd)
kw = job_data.get("critical_keywords")
kw_count = len(split_to_list(str(kw), ",")) if isinstance(kw, str) and kw.strip() else (
    len(kw) if isinstance(kw, (list, tuple)) else 0
)

_log.debug_index(
    func="builder.build_resume_from_job",
    index=1,
    total=1,
    identifier=identifier,
    outcome="success — resume html",
)
_log.debug_detail(f"resume_source={_resume_content_source_label(job_data, cd)!r}")
_log.debug_detail(f"enabled_sections={enabled!r}")
_log.debug_detail(f"body_section_ids={ordered_body!r}")
_log.debug_detail(f"render_keys={content_keys!r}")
_log.debug_detail(
    f"include_cover={include_cover} cover_source={cover_src!r} cover_included={include_cover and cover is not None}"
)
_log.debug_detail(f"accent_source={_accent_source_label(cd)!r}")
_log.debug_detail(f"ats_keywords_count={kw_count}")
html_out = _emit_html_document(...)  # assign return value to html_out first
_log.debug_detail(f"html_chars={len(html_out)}")
_log.debug_detail("html_preview:")
_log.debug_detail_block(html_out)
return html_out
```

Refactor the existing `_emit_html_document(...)` call to assign its return value to `html_out` before debug emission (same arguments as today).

4. In `build_resume`, before each `raise ValueError(...)` (~lines 71–83), call `_emit_builder_failure` with `func="builder.build_resume"`, `identifier=job_id` (or `company_key` / `candidate_id` as appropriate to the failure), `message=str(exc)` or the literal message, `debug=debug`. Pattern: emit then raise — do not swallow.

5. Pass `debug=debug` from `build_resume` into `build_resume_from_job` (step 3 signature).

## Stage 3: `build_cover_letter_from_job` and `build_cover_letter` contract debug

**Done when:** With `debug=True`, cover-only render logs index header + cover source, which cover fields are non-empty (re_line/body/signature), signature image accepted/rejected, html length, truncated preview; missing cover raises with failure header when `debug=True`; with `debug=False` unchanged.

1. At `build_cover_letter_from_job` entry after `cd = _coerce_candidate_blob(candidate_data)`:

```python
if debug:
    _log.set_debug_flag(True)
identifier = _builder_job_identifier(job)
```

2. When `cover is None` before `raise ValueError("No cover letter content for job")`:

```python
_emit_builder_failure(
    func="builder.build_cover_letter_from_job",
    identifier=identifier,
    message="No cover letter content for job",
    debug=debug,
)
```

3. After building `markers` / `style` and before return, when `debug` and `cover is not None`:

```python
cover_src = _cover_letter_source_label(job_data, cd)
profile = cd.get("profile") or {}
safe_sig = _safe_image_src(profile.get("cover_letter_signature_image"))
_log.debug_index(
    func="builder.build_cover_letter_from_job",
    index=1,
    total=1,
    identifier=identifier,
    outcome="success — cover letter html",
)
_log.debug_detail(f"cover_source={cover_src!r}")
_log.debug_detail(
    f"fields re_line={bool((cover.get('re_line') or '').strip())} "
    f"body={bool((cover.get('body') or '').strip())} "
    f"signature={bool((cover.get('signature') or '').strip())}"
)
_log.debug_detail(
    f"signature_image={'accepted' if safe_sig else 'absent_or_rejected'}"
)
html_out = _emit_html_document(...)
_log.debug_detail(f"html_chars={len(html_out)}")
_log.debug_detail("html_preview:")
_log.debug_detail_block(html_out)
return html_out
```

4. In `build_cover_letter`, mirror `build_resume` failure `_emit_builder_failure` calls with `func="builder.build_cover_letter"` before each `raise ValueError`.

5. Pass `debug=debug` from `build_cover_letter` into `build_cover_letter_from_job`.

## Stage 4: `build_base_resume` contract debug

**Done when:** With `debug=True`, candidate-only base resume logs index header + structure sections, render keys, accent source, html length, truncated preview; missing candidate/base_resume failures log failure headers; with `debug=False` unchanged.

1. At `build_base_resume` entry:

```python
if debug:
    _log.set_debug_flag(True)
identifier = candidate_id
```

2. Before each `raise ValueError` (missing candidate, missing `artifacts.base_resume`):

```python
_emit_builder_failure(
    func="builder.build_base_resume",
    identifier=identifier,
    message="<same message as raise>",
    debug=debug,
)
```

3. After `markers` / `ordered_body` computed, before return, when `debug`:

```python
structure = candidate_mod.resolve_resume_structure(cd)
enabled = candidate_mod.enabled_resume_section_ids(structure)
content_keys = sorted(k for k, v in markers.items() if isinstance(v, str) and v.strip())
_log.debug_index(
    func="builder.build_base_resume",
    index=1,
    total=1,
    identifier=identifier,
    outcome="success — base resume html",
)
_log.debug_detail("resume_source=candidate_data.artifacts.base_resume")
_log.debug_detail(f"enabled_sections={enabled!r}")
_log.debug_detail(f"body_section_ids={ordered_body!r}")
_log.debug_detail(f"render_keys={content_keys!r}")
_log.debug_detail(f"accent_source={_accent_source_label(cd)!r}")
html_out = _emit_html_document(...)
_log.debug_detail(f"html_chars={len(html_out)}")
_log.debug_detail("html_preview:")
_log.debug_detail_block(html_out)
return html_out
```

4. Confirm `grep '\[DEBUG\]' src/core/builder.py` returns zero matches after all stages.

## Self-Assessment

**Scope:** `scope-Single-Component` — one core module (`builder.py`) at the logging layer only; five public entry points and four small read-only helpers.

**Conf:** `conf-high` — AST-554 helpers and landed sibling backfill plans define the exact emission pattern; builder has no existing debug noise; ticket AC and boundaries are explicit.

**Risk:** `risk-low` — builder is a read-only HTML renderer with no state transitions or dispatch side effects; debug gating only; wrong logging cannot change artifact output shape.

## Self-Review (ASTRAL_CODE_RULES)

| Section | Result |
|---------|--------|
| §1.3 DRY | Shared `_emit_builder_failure` and source-label helpers; no duplicate truncation logic (uses `debug_detail_block`) |
| §1.5.1 | All contract lines gated on `debug=True` via `set_debug_flag`; index 1/1 + ` \| ` detail; HTML via `debug_detail_block` (15+omit+15) |
| §2.1 config | No config changes; accent label references existing resolution order |
| §2.4 batch | N/A — single-render calls use 1/1 index (same as AST-620 external wrapper) |
| §2.6 state machine | No transitions — read-only renderer |
| §3.3 imports | `get_logger` from utils only; no new cycles |
| §3.5 naming | `func=` strings use `builder.<function>` prefix aligned with `gazer.*` / `roster.*` |

No conflicts requiring `conf-!!-NONE`.

## Execution contract (for build-child)

- Execute stages 1–4 in order; one commit per stage on epic worktree; publish to `origin/sub/AST-545/AST-623-builder-artifact-debug`.
- Do not modify `tests/` or `src/ui/api/api_resume_html.py`.
- Blocking questions → comment on **AST-545** with 🛑 template from **plan-child**.

## Review (build stub)

**Built:** `origin/sub/AST-545/AST-623-builder-artifact-debug` @ `3465d507`.

**Stages delivered:**
- Stage 1: module logger, read-only source helpers, `debug=` on five public APIs — `3465d507`.
- Stage 2: `build_resume` / `build_resume_from_job` failure headers + success contract — `3465d507`.
- Stage 3: `build_cover_letter` / `build_cover_letter_from_job` failure headers + success contract — `3465d507`.
- Stage 4: `build_base_resume` failure headers + success contract; zero `[DEBUG]` literals — `3465d507`.

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-545/AST-623-builder-artifact-debug` @ `f9e69620` (includes Betty `test(AST-623)` + bible §7.13zzj).

### What's solid

- Plan stages 1–4 delivered in `src/core/builder.py` only for product code; five public entry points accept `*, debug: bool = False` with pass-through; no HTML/schema changes.
- §1.5.1 contract: `set_debug_flag` + `debug_index` (style D, `index 1/1`) on every success and terminal `ValueError` path; substantive resolution detail via `debug_detail`; HTML via `debug_detail_block` (15+omit+15).
- Read-only source-label helpers match ticket AC (resume/cover/accent provenance) without altering `_resolve_*` behavior.
- Zero `[DEBUG]` literals; `get_logger` only new import from `utils`.
- Betty branch coverage for `debug=True`/`False` pairs aligns with bible §7.13zzj (no golden log-string asserts — correct for this child).

### Issues

| Severity | Location | Issue |
|----------|----------|-------|
| — | — | None |

### Recommended actions

| Priority | Action |
|----------|--------|
| — | Ship via `resolve-child` — no code changes required |

### Advisory

- Module `_log` sets `set_debug_flag(True)` when `debug=True` but never resets to `False` on `debug=False` calls — same pattern as `gazer`/`dispatcher` siblings; emissions remain gated by `if debug` / `_emit_builder_failure`, so no contract leak observed. Optional hygiene: `set_debug_flag(debug)` at entry (as `roster.py`) if we standardize later across the backfill epic.
- `_accent_source_label` re-invokes `resolve_resume_structure` on debug success paths only — acceptable debug-only duplication.

## Resolution

**Date:** 2026-06-14 · **Publish ref:** `origin/sub/AST-545/AST-623-builder-artifact-debug` @ resolve tip after push

Radia review had no fix-now or discuss items. No product code changes in resolve — Radia doc commit `f2c79b18` already on publish ref; product tip `3465d507` (Stages 1–4) + Betty tests `f9e69620`.

**§9a dry-run:** publish ref merges cleanly into `origin/dev` and `origin/ftr/ast-545-debug-logging-backfill-builder`.

**Advisory (no action):** module `_log` `set_debug_flag(True)` without reset on `debug=False` matches gazer/dispatcher siblings; `_accent_source_label` duplicate structure resolve on debug paths only.

**Outcome:** Ready for User Testing — Chuckles `merge-child` rolls `sub/* → ftr/*` when sibling policy allows.
