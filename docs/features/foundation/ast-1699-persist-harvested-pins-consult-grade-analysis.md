# Persist harvested pins on consult grade/analysis writes

**Linear:** [AST-1699](https://linear.app/astralcareermatch/issue/AST-1699)
**Parent:** [AST-1579](https://linear.app/astralcareermatch/issue/AST-1579) — Capture deduped source-artifact-id array on derived-artifact write
**Publish ref:** `sub/AST-1579/AST-1699-persist-harvested-pins-consult-grade-analysis`

After AST-1698’s `do_task` harvest (`result["source_artifact_ids"]`), consult grade and analysis persists must write that whole-run array as a **sibling job_data key** next to `{prefix}_grades` / `analysis_upshot` (empty list when harvest was empty). Does not re-own harvest; does not thread artifact-table `source_artifact_ids` (AST-1700).

## UAT fitness

- **AC restored:** Parent AC3 — “After a consult grading run that saves `{prefix}_grades`, job_data also contains a sibling source-artifact-id array for that prefix/set whose contents equal the harvest for that run (empty list when harvest was empty).” Parent AC4 — “After `analysis_upshot` (or meteorite upshot equivalent) persist, the same sibling-array rule holds next to that analysis set.”
- **Correct outcome:** After a successful grade or analysis persist, reading job_data shows both the result set and a sibling pin array whose UUIDs match that run’s harvest (or `[]`), so later read-operative explainability can pin the bodies that seeded the prompt — not “whatever is current now.”
- **Sibling check:** AST-1698 harvest attach on `do_task` still holds — consult only **reads** `result["source_artifact_ids"]` (missing → treat as `[]`); no second parse. AST-1700 artifact-table threading stays untouched (no `save_artifact` / `save_job_artifact` / `save_candidate_data` source wiring here).
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Storing pins only inside individual grade objects (or omitting the sibling key when the grades/upshot set is written) fails AC3/AC4. Re-parsing prompts in consult duplicates AST-1698 and drifts from the run’s actual harvest. Writing pins only on success paths that skip empty harvest (omit key vs `[]`) invents omit-vs-null divergence the parent forbids.

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/core/consult.py` — **modified** — when persisting `*_grades` / `analysis_upshot` (and existing sibling keys) via `tracker.save_job_data`, also write the sibling source-artifact-id array harvested for that run. Grade/analysis payloads gain one sibling key beside `{prefix}_grades` / `analysis_upshot`; empty harvest → empty list.
- `src/core/agent.py` — **modified** — only as needed so consult can read the run’s harvest list (no second parse).

Every row in **Files Changed** is one of those paths. Technical kinds covered: consult `save_job_data` sibling key write; optional agent handoff only if AST-1698’s `result["source_artifact_ids"]` is insufficient for a consult caller. No harvest re-implementation, no artifact-table `source_artifact_ids` threading, no tracker/candidate/config/canon edits.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | Normalize harvest from `do_task` result; on every `*_grades` / `analysis_upshot` `save_job_data` that writes the set, also write sibling `*_source_artifact_ids` (always a `list`, `[]` when empty/missing) | core |

**Out of this ticket (do not touch unless a Stage step explicitly requires a one-line agent gap fix):** re-implement `harvest_source_artifact_ids`; `save_candidate_data` / `save_job_artifact` / `database.save_artifact` call sites; `src/core/tracker.py`; `src/utils/config.py`; `canon/directives/draft/patt.artifact.traceability.md`; `tests/` / `docs/test-bible/**` (Betty).

⚠️ **Decision (agent.py):** AST-1698 already attaches `source_artifact_ids` on `do_task` returns after harvest. **Default: do not edit `agent.py`.** Consult reads `list(result.get("source_artifact_ids") or [])`. If a consult path somehow calls an agent entry that never harvested, empty list is correct. Only open `agent.py` if build discovers a consult-used return path that runs after prompts exist but omits the key **and** omitting it would make empty-vs-missing diverge from sibling saves — then add the same `_with_harvest` attach Ada used; do not invent a second harvest API.

## Stage 1: Sibling key helpers + normalize harvest list

**Done when:** `consult.py` has a single helper that maps a grades/upshot set key to its sibling pin key, and a single normalizer that turns `do_task`’s raw harvest field into a `list[str]` (missing/`None`/non-list → `[]`; copy list so callers cannot mutate the result dict’s list in place). No `save_job_data` call sites changed yet.

1. Near `_analysis_phase_rubric_snapshot_key` (~line 950), add:

```python
def _source_artifact_ids_job_data_key(set_key: str) -> str:
    """Sibling job_data key for a grades/upshot set key (AST-1699).

    ``{prefix}_grades`` → ``{prefix}_source_artifact_ids`` (same stem rule as
    ``_analysis_phase_rubric_snapshot_key``). Any other set key (e.g.
    ``analysis_upshot``) → ``{set_key}_source_artifact_ids``.
    """
```

2. Implementation:
   - If `set_key` is a `str` ending with `"_grades"`, return `set_key[:-7] + "_source_artifact_ids"` (same stem rule as rubric’s `[:-7] + "_rubric"`).
   - Else return `f"{set_key}_source_artifact_ids"`.
   - Do not special-case meteorite: `meteorite_upshot` already persists under job_data key `analysis_upshot` (existing comment at ~1200); sibling key is therefore `analysis_upshot_source_artifact_ids` for that path too.

3. Add:

```python
def _normalize_harvested_source_artifact_ids(raw) -> list:
    """Always a new list[str] for job_data sibling writes (empty when absent)."""
```

   - If `raw` is a `list`, return `[str(x) for x in raw if isinstance(x, str) and x.strip()]` (drop non-strings / blanks; do **not** re-dedupe — Ada’s harvest already did).
   - Else return `[]`.

⚠️ **Decision:** Key stem matches existing `{prefix}_*` siblings (`_grades`, `_score`, `_notes`, `_rubric`). Analysis uses the literal set key `analysis_upshot` + `_source_artifact_ids` suffix. Do **not** invent a global `source_artifact_ids` job_data key shared across prefixes.

4. Do not change `_analysis_phase_rubric_snapshot_key` or ANALYSIS_* token maps in config.

## Stage 2: Wire `_apply_render_verdict_decoded_job` + single-job `render_verdict`

**Done when:** Every save through `_apply_render_verdict_decoded_job` that writes `{prefix}_grades` also writes `{prefix}_source_artifact_ids` to the same `save_data` dict (always present when grades are written). `render_verdict` passes the harvest from its `do_task` result into that helper.

1. Extend `_apply_render_verdict_decoded_job` signature with an optional keyword-only argument after existing params:

```python
*,
source_artifact_ids=None,
```

   (Keep positional call sites working; add the kw-only at the end of the signature beside any existing `debug=` if present — match the function’s current keyword style.)

2. In the block that builds `save_data` (~1267–1283), after the existing `{prefix}_grades` / score / notes / rubric keys are set and **before** `tracker.save_job_data(...)`:

```python
save_data[_source_artifact_ids_job_data_key(f"{prefix}_grades")] = (
    _normalize_harvested_source_artifact_ids(source_artifact_ids)
)
```

3. In `render_verdict`, after a successful `do_task` and before calling `_apply_render_verdict_decoded_job` (~1391), compute:

```python
harvested = _normalize_harvested_source_artifact_ids(result.get("source_artifact_ids"))
```

   Pass `source_artifact_ids=harvested` into `_apply_render_verdict_decoded_job`.

4. Do **not** write the sibling key on incomplete-grade / fail paths that never call `save_job_data` for grades.

## Stage 3: Analysis upshot persist

**Done when:** `_run_analysis_upshot_batch`’s successful `tracker.save_job_data(aid, {"analysis_upshot": parsed})` also includes `analysis_upshot_source_artifact_ids` equal to that iteration’s `do_task` harvest (or `[]`).

1. In `_run_analysis_upshot_batch`, after a successful `do_task` with a dict `parsed_response` (~1192–1201), replace the bare save with:

```python
harvested = _normalize_harvested_source_artifact_ids(result.get("source_artifact_ids"))
tracker.save_job_data(aid, {
    "analysis_upshot": parsed,
    _source_artifact_ids_job_data_key("analysis_upshot"): harvested,
})
```

2. Apply to both `analysis_upshot` and `meteorite_upshot` task_key values of this function (same job_data set key today). Fail paths that do not save `analysis_upshot` must not invent a lone sibling key.

## Stage 4: Batch consult — share one run harvest with every grade save

**Done when:** One `do_task` inside `_run_batch_consult` yields one harvest list; every per-job process that saves `*_grades` (`joblist_grades`, `jd_grades`, and `_apply_render_verdict_decoded_job` from encoded scored batches) writes that same list as the sibling key. Jobs that skip grade save (e.g. JD readiness skip writing only `jd_readiness_skip`) do not get a pin sibling.

1. In `_run_batch_consult`, after a successful `do_task` (once `parsed` / `response_jobs` are available, ~1542+), normalize once:

```python
batch_harvest = _normalize_harvested_source_artifact_ids(result.get("source_artifact_ids"))
```

2. Before the per-job `process_fn` loop (~1602), wrap so every process sees the harvest without changing every assemble/process call site signature:

```python
_inner_process = process_fn

def process_fn(input_job, response_job, cfg):
    cfg_with_harvest = dict(cfg)
    cfg_with_harvest["_source_artifact_ids"] = batch_harvest
    return _inner_process(input_job, response_job, cfg_with_harvest)
```

   (Shadowing the parameter name is fine locally; or use a differently named wrapper — pick one style and keep it readable.)

⚠️ **Decision:** Whole-batch one harvest array (parent: whole-run array, not per grade line). All jobs in that `do_task` share the same sibling pin list. Do not re-harvest per job.

3. In `qualify_job_listings`’s `_save_joblist_result` (~1786–1794), when building `save_data` with `joblist_grades`, also set:

```python
save_data[_source_artifact_ids_job_data_key("joblist_grades")] = (
    _normalize_harvested_source_artifact_ids(cfg.get("_source_artifact_ids"))
)
```

   (`process` already receives `cfg`; pass `cfg` into `_save_joblist_result` if it is nested without cfg in scope — adjust the nested def to close over `cfg` from `process(input_job, response_job, cfg)`.)

4. In `evaluate_jd` / evaluate_meteorite `process` (~2333–2344), when building `save_data` with `jd_grades`, add the same sibling via `_source_artifact_ids_job_data_key("jd_grades")` from `cfg.get("_source_artifact_ids")`.

5. In `_consult_scored_dispatch_batch_encoded`’s `process` (~2450–2455), pass harvest into `_apply_render_verdict_decoded_job`:

```python
to_state, _, _grades = _apply_render_verdict_decoded_job(
    dispatch_task_key, aid, response_job, cfg_dispatch, ctx, debug=debug,
    source_artifact_ids=_orch_cfg.get("_source_artifact_ids"),
)
```

   Use the process_fn’s third argument (the cfg wrapper from step 2) — today the param is `_orch_cfg`; read harvest from that dict. Do **not** read from the outer `cfg_dispatch` alone (it never received the wrapper keys).

6. Leave `jd_readiness_skip` `save_job_data` (~2289) unchanged — not a grades/upshot set write.

⚠️ **Decision (run_next):** AST-1698 advisory — `do_task` returns the **terminal hop’s** `source_artifact_ids` only. Consult grade / analysis TASK_CONFIG rows for this ticket have `run_next=None`; persist the terminal (only) hop’s list. Do **not** merge parent-hop pins in this ticket.

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish to `origin/sub/AST-1579/AST-1699-persist-harvested-pins-consult-grade-analysis`.
- Do not add files outside **Files Changed**.
- Do not re-parse prompts or call `harvest_source_artifact_ids` from consult.
- When a step is ambiguous or the codebase drifted — stop, comment on parent AST-1579 with the Stage blocked template, wait.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Review

**Publish tip:** `51b94c280db6bb53539630ce62fa66977cb7394c` on `sub/AST-1579/AST-1699-persist-harvested-pins-consult-grade-analysis`

- Stage 1: `_source_artifact_ids_job_data_key` + `_normalize_harvested_source_artifact_ids` in `src/core/consult.py`
- Stage 2: `_apply_render_verdict_decoded_job` / `render_verdict` write `{prefix}_source_artifact_ids`
- Stage 3: `_run_analysis_upshot_batch` writes `analysis_upshot_source_artifact_ids`
- Stage 4: `_run_batch_consult` shares batch harvest; joblist / jd / encoded scored batch grade saves


## Joan validate

[plan-rubric]
**Ticket:** AST-1699
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref:** `sub/AST-1579/AST-1699-persist-harvested-pins-consult-grade-analysis` @ `c2a3224bed2b11712248fec99f10e7edf4079c00`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.traceability | A | | |
| patt.artifact.read-operative | A | | |
| astral.standards.in-scope-only | A | | |
| astral.standards.dry-and-focused-functions | A | | |
| astral.standards.debug-contract-gated | X | | consult persist only; no new debug surfaces |

## Traceability

AC3→S2§2-3, S4§3-5; AC4→S3§1-2; parent AC1–2 N/A (AST-1698 harvest); parent AC5–7 N/A (AST-1700 artifact-table + job_resume auto-cite).

## Findings

### discuss

- **Gate assignee:** Status `Plan Ready` but assignee is Hedy, not Joan — Chuckles should flip assignee for validate-plan protocol; review proceeded per spawn request.
- **Normalizer strictness (S1§3):** `_normalize_harvested_source_artifact_ids` keeps only `isinstance(x, str)` elements; if AST-1698 ever returns UUID objects, they'd be dropped to `[]`. Low risk given Ada's str contract — builder may widen to `str(x).strip()` on list elements if paranoid.

### acceptable

- **AST-1698 ordering:** Plan reads `result.get("source_artifact_ids")` with missing→`[]`; safe to build before #1 lands on ftr, though AC3/AC4 verification needs #1 merged or stubbed.
- **Whole-batch harvest (S4§2):** One `do_task` harvest shared across all jobs in `_run_batch_consult` matches parent whole-run array semantics.
- **`cfg_dispatch` vs `_orch_cfg` (S4§5):** Plan correctly reads harvest from the wrapped process_fn cfg, not outer `cfg_dispatch` — matches `_consult_scored_dispatch_batch_encoded` closure today.

### R6 — Definition fidelity (checklist)

- **Explicit scope gate** present; **Files Changed** is `consult.py` only; agent.py default no-touch rule is explicit and bounded.
- All five `tracker.save_job_data` grade/upshot sites in `consult.py` are covered (render_verdict / `_apply_render_verdict_decoded_job`, analysis upshot, joblist, jd_grades, encoded grade_* via batch wrapper); `jd_readiness_skip` correctly excluded.
- Sibling key stem mirrors existing `{prefix}_grades` / `{prefix}_rubric` convention; `analysis_upshot` → `analysis_upshot_source_artifact_ids` consistent with meteorite sharing `analysis_upshot` job_data key.
- No re-parse / no `harvest_source_artifact_ids` in consult; empty harvest → `[]` not omit.
- Self-assessment `Confirm Chuckles estimate: 2 — agree` is honest for four focused stages in one file.
- Plan Discuss rounds completed: **0** (status Plan Ready).

context_tokens≈78000

## Radia review

[code-rubric]
**Ticket:** AST-1699
**Publish ref:** `17225b7e3631f5f8d6b2ab3ea1060d34fb3978dc` (`origin/sub/AST-1579/AST-1699-persist-harvested-pins-consult-grade-analysis`)
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.traceability | A | | |
| patt.artifact.read-operative | A | | |
| astral.standards.in-scope-only | A | | |
| astral.standards.dry-and-focused-functions | A | | |
| astral.standards.debug-contract-gated | X | | |

Draft `patt.*` resolved from `canon/directives/draft/` mirrors (same path Joan used).

## Column diff vs plan stage

(aligned)

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Normalizer strictness (Joan carry-forward):** `_normalize_harvested_source_artifact_ids` keeps only `isinstance(x, str)` list elements; non-string UUID objects would drop to `[]`. Low risk given AST-1698’s str contract — widen to `str(x).strip()` only if Ada ever changes harvest element types.
- **Branch diff vs AST-1699 product scope:** Three-dot diff vs `origin/dev` includes AST-1698 harvest stack (`agent.py`, `candidate.py`, `config.py`) plus Betty `merge-tests` sibling manifests/tests (AST-1700 test commit on tip, meteorite, etc.). **AST-1699 product commits touch `consult.py` only** (`4fed1f82` → `51b94c28`); dependency rollup is expected on the sub ref, not scope creep by this ticket.
- **Batch path test depth:** `TestAst1699PersistHarvestedPinsConsult` covers helpers, `_apply_render_verdict_decoded_job`, analysis upshot, and `render_verdict` integration; Betty revised existing analysis exact-save tests for empty `analysis_upshot_source_artifact_ids`. **No dedicated component test** asserts `joblist_source_artifact_ids` / `jd_source_artifact_ids` / encoded `grade_*` batch wrapper — wiring mirrors the tested render_verdict path structurally; acceptable given manifest, but a future Betty row could pin one batch save if regressions worry Susan.

## What's solid

- **Stage 1:** `_source_artifact_ids_job_data_key` uses the same `{prefix}_grades` → `{prefix}_source_artifact_ids` stem as rubric; `analysis_upshot` → `analysis_upshot_source_artifact_ids`. Normalizer returns a fresh `list[str]`, missing/non-list → `[]`, strips blanks, no re-dedupe.
- **Stage 2:** `_apply_render_verdict_decoded_job` always writes sibling beside `{prefix}_grades` before `save_job_data`; `render_verdict` forwards normalized harvest from `do_task` result.
- **Stage 3:** `_run_analysis_upshot_batch` saves upshot + sibling in one dict (meteorite shares `analysis_upshot` key).
- **Stage 4:** `_run_batch_consult` normalizes once, injects `_source_artifact_ids` via process_fn wrapper; `qualify_job_listings` / `evaluate_jd_batch` / `_consult_scored_dispatch_batch_encoded` read harvest from wrapped `cfg` / `_orch_cfg` (not bare `cfg_dispatch`). `jd_readiness_skip` save unchanged (no sibling).
- **Boundaries:** No `harvest_source_artifact_ids` / prompt re-parse in consult; no artifact-table `source_artifact_ids` threading; no `agent.py` edits in AST-1699 commits (reads existing `result["source_artifact_ids"]` only).
- **Contrast with AST-1700 tip review:** This branch includes the helper defs that were missing on the AST-1700 sub ref’s partial consult smuggle — AST-1699 product slice is complete here.

## Recommended actions (downstream — not Radia lane)

- Chuckles: append artifact, commit `docs(AST-1699): Radia review — clean`, push sub ref, post slim upshot `--as radia`, → **Review Posted** → datt PROCEED (no `resolve-child` canon work expected).
- Optional Betty follow-up (advisory only): one batch consult test for `joblist_grades` or `jd_grades` sibling if Susan wants explicit AC3 batch-path lock.

---

## Resolution

**2026-09-17** — Radia **CLEAN** / Linear **PROCEED** (`17225b7e`); no fix-now / discuss items.

- Stacked sub onto `origin/ftr/AST-1579-capture-deduped-source-artifact-id-array` via `sync-child` + conflict resolve on `docs/features/foundation/ast-1700-thread-harvest-generative-artifact-writes.md` (took ftr full plan; HEAD side was a truncated worktree-race stub).
- Product: AST-1699 `consult.py` harvest sibling pins unchanged; ftr brought AST-1700 agent/candidate/draft-traceability rollup.
- Advisory normalizer widen: not applied (AST-1698 still returns `list[str]`).
- §9a dry-run: clean vs `origin/dev` and vs `origin/ftr/AST-1579-capture-deduped-source-artifact-id-array`.
