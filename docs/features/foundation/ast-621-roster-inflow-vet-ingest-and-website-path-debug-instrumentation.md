<!-- linear-archive: AST-621 archived 2026-06-23 -->

## Linear archive (AST-621)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-621/roster-inflow-vet-ingest-and-website-path-debug-instrumentation-debug  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-542 — Debug logging backfill: roster  
**Blocked by / blocks / related:** parent: AST-542

### Description

## What this implements

Backfill the **AST-538** debug logging contract across **roster** inflow paths in `src/core/roster.py`: `vet_inflow_discovery`, `ingest_new_companies`, website resolution, and related batch loops. Per **index N/M** header lines, `|` detail for CSE hits, vet/ingest outcomes, and warnings (e.g. slug owned by another candidate) under the matching index header.

## Acceptance criteria

1. Debug inflow batch logs Google CSE result summary and vet/ingest record outcome per index N/M.
2. Matches sample shape documented on **AST-538**.
3. `debug=False` unchanged.

## Boundaries

* No change to roster state machine or ingest rules.
* **AST-540** (dispatcher) and **AST-541** (agent) own their layers — roster only.

## Notes for planning

* Use `src/utils/logging.py` helpers (`debug_index`, `debug_detail`, `debug_detail_block`) per **ASTRAL_CODE_RULES** §1.5.
* Grandfather untouched `[DEBUG]` lines only where file is not otherwise touched.

## Git branch (authoritative)

Per `orientation` **§ Branch law**: parent `ftr/ast-542-debug-logging-backfill-roster`, child `sub/AST-542/<child-segment>`. Created at **dispatch-parent**.

### Comments

#### radia — 2026-06-14T04:43:23.332Z
**Diff:** `origin/dev...origin/sub/AST-542/AST-621-roster-inflow-vet-ingest-debug` (5 commits; product focus `src/core/roster.py` + merge-clean `src/core/agent.py`).

### What's solid

- **Plan fidelity (Stages 1–3):** `_ingest_failure_reason`, vet-row outcome strings, `resolve_company_website` contract debug (CSE → vet block → state outcomes), empty-dedupe header, and `debug=debug` on `do_task` — all match the approved plan.
- **§1.5.1 gating:** New contract emission is `if debug:` throughout; `log.set_debug_flag(debug)` at `resolve_company_website` entry; helpers are `debug_index` / `debug_detail` / `debug_detail_block` (no new hand-rolled `[DEBUG]` in touched roster paths).
- **§2.6 / boundaries:** No state-machine or ingest-rule changes; `_ingest_failure_reason` is read-only and aligns with `ingest_new_companies` pre-checks.
- **AST-557 baseline:** Discovery term/vet-row instrumentation preserved; only the planned empty-dedupe block added.

### fix-now

| Location | Issue |
|----------|--------|
| `src/core/roster.py` ~563–575 (`run_inflow_discovery_batch` vet-row loop) | `log.debug_detail(f"ingest failed: {fail_reason}")` runs **before** the row's `debug_index`. §1.5.1 requires working detail **under** the matching index header (same pattern as the `action=` line below). **Move** the ingest-failed detail **after** `debug_index`, before or combined with the existing `action=` detail line. |

### discuss

| Location | Issue |
|----------|--------|
| `src/core/agent.py` (commit `3357bb6c`, merge-clean) | Conflict resolution keeps ftr `run_next dispatch` `debug_detail` and drops origin/dev `caller_hydration=live_llm` (resume-artifact-only) line. Documented as merge hygiene, but file is **AST-541/618** scope. On **`ftr/AST-542` integration**, confirm the broader `run_next dispatch` line satisfies AST-618 intent and that dropping the dev-side resume-only line is intentional — not a roster ticket fix unless integration still needs both. |

### advisory

- **`resolve_company_website` zero-hit path:** Two consecutive `index 1/1` headers (`0 CSE hit(s)` then `NO_WEBSITE — zero CSE hits`) — acceptable for UAT traceability; optional dedupe later if noisy.
- **Scope note:** Self-Assessment says roster-only; branch also carries Betty bible §7.13zzf + agent merge-clean — expected publish artifacts, not roster logic creep.
- **`agent.py`:** Pre-existing `logger.info("[DEBUG] … literal encoded agent_payload` unchanged in merge-clean file — grandfather per §1.5.1; not introduced by AST-621.

**Handoff:** Hedy — address **fix-now** via `resolve-child`; reply on **discuss** if agent merge needs Susan/Chuckles on ftr before closing.

#### betty — 2026-06-14T04:40:24.502Z
## QA test manifest (AST-621)

**Publish ref:** `origin/sub/AST-542/AST-621-roster-inflow-vet-ingest-debug` @ `be1cc505` (`merge-tests(AST-621): origin/tests fe3a3126`)

**Bible:** `docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref: `dc5a7d5f00bd00d182904dd8aac2bdf674180423`

**Classification:** manifest-only — no new tests. Parent + plan forbid Betty log-string assertions; **`debug=False`** unchanged is the automated gate.

### 1. Existing coverage (bible-backed)

1. **`tests/component/core/test_roster.py`** — full file (**`LOCKED_AT_100`**); manifest focus **`TestAst505InflowDiscovery`** + **`TestAst506InflowResolve`**
2. **`tests/component/utils/test_debug_logging.py`** — **§7.13zt** contract regression (gating + truncation math only)
3. **`tests/component/utils/test_logging_batch.py`** — **§7.13zt** contract regression

### 2. Broken / obsolete tests

None identified — instrumentation is **`debug=True`**-gated only; no state machine or ingest rule changes.

### 3. Gaps

None — manual UAT spot-check per plan Stage 4 (Susan / post-**Tests Passed**).

### Run command

```bash
.venv/bin/python -m pytest tests/component/core/test_roster.py tests/component/utils/test_debug_logging.py tests/component/utils/test_logging_batch.py -q
```

Equivalent harness:

```bash
./scripts/testing/run_component_tests.sh tests/component/core/test_roster.py
```

— Betty

#### hedy — 2026-06-14T04:33:45.845Z
Plan doc: [ast-621-roster-inflow-vet-ingest-and-website-path-debug-instrumentation.md](https://github.com/susansomerset/astral/blob/sub/AST-542/AST-621-roster-inflow-vet-ingest-debug/docs/features/foundation/ast-621-roster-inflow-vet-ingest-and-website-path-debug-instrumentation.md)

**Scope:** `Single-Component` — `src/core/roster.py` only; builds on AST-557 discovery instrumentation already on ftr, adds `resolve_company_website` contract debug, ingest failure ` | ` detail under vet-row headers, and empty-dedupe header.

**Conf:** `high` — Same file/patterns as AST-557; `resolve_company_website` mirrors discovery CSE/vet structure at index 1/1.

**Risk:** `Medium` — Inflow paths are production-critical, but all new emission is `debug=True`-gated with no state/ingest rule changes.

Four stages: (1) `_ingest_failure_reason` + row detail, (2) full `resolve_company_website` contract + `do_task(debug=)`, (3) empty dedupe header, (4) manual spot-check only (no Betty log tests).

---

# AST-621 — Roster inflow vet, ingest, and website path debug instrumentation (Debug logging backfill: roster)

- **Linear (this ticket):** [AST-621](https://linear.app/astralcareermatch/issue/AST-621/roster-inflow-vet-ingest-and-website-path-debug-instrumentation-debug)
- **Parent:** [AST-542](https://linear.app/astralcareermatch/issue/AST-542/debug-logging-backfill-roster)
- **Publish ref:** `origin/sub/AST-542/AST-621-roster-inflow-vet-ingest-debug` (child of AST-542; not Linear `gitBranchName`)
- **Depends on:** [AST-538](https://linear.app/astralcareermatch/issue/AST-538/improve-quality-of-debug-logging) / [AST-554](https://linear.app/astralcareermatch/issue/AST-554/debug-logging-contract-and-shared-helper) — shared helper + §1.5.1 on integration line.

## Summary

Complete the **AST-538** debug logging contract for **roster inflow** paths still missing UAT-grade traceability in `src/core/roster.py`. The **`run_inflow_discovery_batch`** / **`vet_inflow_discovery`** loop is **already instrumented** on `origin/ftr/ast-542-debug-logging-backfill-roster` (landed via [AST-557](https://linear.app/astralcareermatch/issue/AST-557/inflow-discovery-representative-debug-instrumentation)). This ticket adds: (1) **`resolve_company_website`** contract debug for **`inflow_resolve_website`** dispatch, (2) **specific ingest failure reasons** as ` | ` detail under each vet-row index header, and (3) a **no deduped hits** contract header when terms ran but dedupe yielded zero hits. No roster state machine or ingest rule changes.

## Out of scope (explicit)

| Item | Owner / note |
|------|----------------|
| `run_inflow_discovery_batch` term/vet-row/batch-summary contract (baseline) | **AST-557** — verify present; do not rewrite |
| `src/core/dispatcher.py` | **AST-540** / **AST-615** |
| `src/core/agent.py` `do_task` global debug migration | **AST-541** / **AST-618** |
| Betty log-string tests | Forbidden per parent |
| `ingest_new_companies` public signature change | Outcomes logged from caller; optional read-only reason helper only |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/roster.py` | `resolve_company_website` contract debug; `_ingest_failure_reason` + row `debug_detail`; empty-dedupe header in `run_inflow_discovery_batch` | core |

## Stage 1: Ingest failure reason helper and vet-row detail (`src/core/roster.py`)

**Done when:** With `debug=True`, each vet result row that fails ingest logs a ` | ` line naming the specific failure (invalid slug, slug owned by another candidate, duplicate URL, duplicate slug for same candidate) under that row's existing `debug_index` header; with `debug=False`, behavior unchanged.

1. Add a module-private read-only helper **above** `ingest_new_companies` (no DB writes):

```python
def _ingest_failure_reason(
    candidate_id: str,
    slug: str,
    website: Optional[str],
) -> Optional[str]:
    """Return human-readable ingest failure reason, or None if ingest would succeed."""
    slug = (slug or "").strip().lower()
    if not slug or not _INFLOW_SLUG_RE.match(slug):
        return f"invalid slug {slug!r}"
    existing = get_company(slug)
    if existing:
        if (existing.get("candidate_id") or "") != candidate_id:
            return f"slug {slug!r} owned by another candidate"
        return f"duplicate slug {slug!r} for candidate {candidate_id}"
    site = (website or "").strip()
    if site:
        norm = _normalize_company_url_for_dedupe(site)
        if norm and norm in _candidate_company_urls(candidate_id):
            return f"duplicate URL {site!r} for candidate {candidate_id}"
    return None
```

⚠️ **Decision:** Read-only duplicate of ingest pre-checks — avoids changing `ingest_new_companies` return type while giving UAT-specific ` | ` detail per AST-538.

2. In `run_inflow_discovery_batch`, in the vet result row loop (where `outcome` is computed today ~lines 418–454), after `ingest_new_companies(...)` returns `False` and **before** `log.debug_index(...)`:

```python
if debug and action == "slug" and slug and not outcome.startswith("recorded"):
    reason = _ingest_failure_reason(candidate_id, slug, site)
    if reason:
        log.debug_detail(f"ingest failed: {reason}")
```

3. Narrow the generic failure outcome string when a reason exists — replace:

```python
outcome = (
    "not recorded (duplicate slug, other candidate, invalid slug, or duplicate URL)"
)
```

with:

```python
fail_reason = _ingest_failure_reason(candidate_id, slug, site)
outcome = (
    f"not recorded — {fail_reason}"
    if fail_reason
    else "not recorded (unknown)"
)
```

Only when `action == "slug"` and ingest returned `False`. Keep `"ignored"`, `"skipped unknown action"`, and `"skipped empty slug"` paths unchanged.

4. Do **not** remove existing `logger.warning` / `logger.info` lines inside `ingest_new_companies` — they remain for non-debug monitoring; contract detail satisfies AC under the row header when `debug=True`.

## Stage 2: `resolve_company_website` contract debug (`src/core/roster.py`)

**Done when:** With `debug=True`, a single-company **`inflow_resolve_website`** run logs CSE query/hits, `find_company_website` task bundle, and final recorded state (`WEBSITE_FOUND`, `NO_WEBSITE`, or error) using index **1/1** headers and ` | ` detail; with `debug=False`, no new contract lines (existing WARNING on CSE failure unchanged).

1. Remove line `_ = debug` (~250).

2. At function entry after `cfg = INFLOW_CONFIG["resolve"]`:

```python
log = logger
log.set_debug_flag(debug)
```

3. **Existing website short-circuit** — when `site` is non-empty (early return ~253–254), before `return`:

```python
if debug:
    log.debug_index(
        func="roster.resolve_company_website",
        index=1,
        total=1,
        identifier=short_name,
        outcome="skipped — company_website already set",
    )
    log.debug_detail(f"company_website={site!r}")
```

4. **CSE resolution search** — after building `query = f"{name} official website"`:

   - On **CSE exception** (~264–266): before existing `logger.warning` and `return`, when `debug`:

```python
log.debug_index(
    func="roster.resolve_company_website",
    index=1,
    total=1,
    identifier=short_name,
    outcome=f"CSE failed: {exc!s}",
)
log.debug_detail(f"query={query!r}")
```

   - On **success** after `hits = search_google_cse(...)`:

```python
if debug:
    log.debug_index(
        func="roster.resolve_company_website",
        index=1,
        total=1,
        identifier=short_name,
        outcome=f"{len(hits)} CSE hit(s)",
    )
    log.debug_detail(f"query={query!r} raw_hits={len(hits)}")
    for hi, hit in enumerate(hits):
        if hi >= 20:  # UAT cap — same as discovery
            log.debug_detail(f"... {len(hits) - 20} more hits omitted from log")
            break
        log.debug_detail(
            f"hit title={hit.get('title', '')!r} url={hit.get('url', '')!r}"
        )
```

   - On **empty hits** (~267–269): before `transition_company_state(short_name, "NO_WEBSITE")`:

```python
if debug:
    log.debug_index(
        func="roster.resolve_company_website",
        index=1,
        total=1,
        identifier=short_name,
        outcome="NO_WEBSITE — zero CSE hits",
    )
    log.debug_detail(f"query={query!r}")
```

5. **find_company_website vet step** — after building `live_content` (~275), before `do_task`:

```python
if debug:
    log.debug_index(
        func="roster.resolve_company_website",
        index=1,
        total=1,
        identifier=short_name,
        outcome=f"vet {cfg['ai_task_key']} {len(hits)} hit(s)",
    )
    log.debug_detail_block(live_content)
```

6. Pass `debug` into `do_task`:

```python
api_result = await do_task(
    task_key=cfg["ai_task_key"],
    live_content=live_content,
    index=short_name,
    ctx=ctx,
    debug=debug,
)
```

7. **After `do_task` returns:**

   - Task failure (~282–283):

```python
if debug:
    log.debug_index(
        func="roster.resolve_company_website",
        index=1,
        total=1,
        identifier=short_name,
        outcome="find_company_website task failed",
    )
    log.debug_detail(f"error={api_result.get('error')!r}")
```

   - AI decline / empty website (~286–288): before `transition_company_state(..., "NO_WEBSITE")`:

```python
if debug:
    log.debug_index(
        func="roster.resolve_company_website",
        index=1,
        total=1,
        identifier=short_name,
        outcome="NO_WEBSITE — task_success false or empty website",
    )
    log.debug_detail(
        f"task_success={parsed.get('task_success')!r} website={website!r}"
    )
```

   - Success (~289–291): after `update_company` + `transition_company_state(..., "WEBSITE_FOUND")`:

```python
if debug:
    log.debug_index(
        func="roster.resolve_company_website",
        index=1,
        total=1,
        identifier=short_name,
        outcome=f"recorded WEBSITE_FOUND website={website!r}",
    )
```

⚠️ **Decision:** Single entity per dispatch call → always `index 1/1` with `identifier=short_name` (matches dispatcher per-company batch item). CSE hit cap **20** inline — same UAT cap as discovery; no new config keys.

## Stage 3: Empty dedupe header in `run_inflow_discovery_batch` (`src/core/roster.py`)

**Done when:** When `debug=True`, terms ran CSE but dedupe produced zero hits, one contract header explains skip before early return (~368–369); vet step still skipped.

1. Replace:

```python
if not all_hits:
    return {**zero, "total_errors": errors}
```

with:

```python
if not all_hits:
    if debug:
        log.debug_index(
            func="roster.run_inflow_discovery_batch",
            index=1,
            total=1,
            identifier=candidate_id,
            outcome="no deduped hits after CSE — vet skipped",
        )
        log.debug_detail(
            f"terms_searched={term_total} errors={errors} deduped_hits=0"
        )
    return {**zero, "total_errors": errors}
```

## Stage 4: Manual verification (build agent / Susan UAT)

**Done when:** Spot-check confirms AC 3 (`debug=False` unchanged) and AC 1–2 shape.

1. **`debug=False`:** Run existing component tests `tests/component/core/test_roster.py::TestAst505InflowDiscovery` and `::TestAst506InflowResolve` — must stay green; no new `index N/M` lines when tests pass with `debug=False`.
2. **`debug=True` (manual):** One `inflow_discovery` run with ≥2 stale terms and one failed ingest row — confirm row header + ` | ingest failed: slug 'x' owned by another candidate` (or equivalent).
3. **`debug=True` (manual):** One `inflow_resolve_website` company with empty `company_website` — confirm CSE hit detail, vet block, and `recorded WEBSITE_FOUND` or `NO_WEBSITE` header.

(No new automated log-string tests — parent forbids.)

## Self-Assessment

**Scope:** `Single-Component` — Only `src/core/roster.py`; three focused edits (ingest reason helper, `resolve_company_website`, one early-return branch in existing discovery batch).

**Conf:** `high` — Reuses AST-557 patterns already on the integration line in the same file; `resolve_company_website` mirrors discovery CSE/vet structure one entity at a time.

**Risk:** `Medium` — Inflow ingest and website resolution are production paths, but all new lines are gated on `debug=True` and do not alter state transitions or ingest acceptance rules.

## Self-review (ASTRAL_CODE_RULES)

| Rule | Compliance |
|------|------------|
| §1.3 DRY | `_ingest_failure_reason` mirrors ingest checks once; discovery hit-cap pattern reused in resolve |
| §1.5.1 | `debug_index` / `debug_detail` / `debug_detail_block` only when `debug=True`; `set_debug_flag` at path entry |
| §2.1 config | Uses existing `INFLOW_CONFIG["resolve"]` keys; no new config blocks |
| §2.6 state machine | No transition or ingest rule changes — logging only |
| §3.3 imports | No new cross-layer imports |
| §3.5 naming | `func=` strings use `roster.resolve_company_website` / `roster.run_inflow_discovery_batch` |

## Execution contract (for build-child)

- Execute stages **in order**; one commit per stage on epic worktree, publish to `origin/sub/AST-542/AST-621-roster-inflow-vet-ingest-debug` after each stage.
- Do **not** rewrite AST-557 discovery instrumentation except Stage 3 empty-dedupe block.
- Blocking questions → comment on **AST-542** with 🛑 template from **plan-child**.

## Review (build-child)

**Built:** `sub/AST-542/AST-621-roster-inflow-vet-ingest-debug` → `origin/sub/AST-542/AST-621-roster-inflow-vet-ingest-debug`

| Commit | Summary |
|--------|---------|
| `3357bb6c` | Merge-clean `agent.py` do_task debug (ftr conflict markers) |
| `a8139771` | Stages 1–3: ingest reason helper, `resolve_company_website` contract debug, empty-dedupe header |

**Verification:** `python3 -m py_compile src/core/roster.py src/core/agent.py`; `run_component_tests.sh` — `TestAst505InflowDiscovery` + `TestAst506InflowResolve` (18 passed).

## Resolution (resolve-child)

**Radia review (2026-06-14):** [Linear comment](https://linear.app/astralcareermatch/issue/AST-621)

### fix-now (landed)

| Item | Resolution |
|------|------------|
| Vet-row `ingest failed` detail before `debug_index` | Moved `log.debug_detail(f"ingest failed: {fail_reason}")` **after** row `debug_index`, before `action=` detail — §1.5.1 working detail under the index header. |

### discuss (closed — no product change)

| Item | Resolution |
|------|------------|
| `agent.py` merge-clean (`3357bb6c`) drops dev `caller_hydration=live_llm` resume-artifact line | **AST-618** scope on ftr integration. Kept ftr `run_next dispatch` `debug_detail` (broader AST-618 contract). Dropping dev-only resume line is intentional merge hygiene for this publish ref; not an AST-621 roster fix. |

### advisory (accepted as-is)

- Dual `index 1/1` headers on zero CSE hits — acceptable UAT traceability.
- Betty bible §7.13zzf + agent merge-clean on publish ref — expected artifacts.

**Verification:** manifest re-run 181 passed; §9a dev + ftr dry-runs clean.
