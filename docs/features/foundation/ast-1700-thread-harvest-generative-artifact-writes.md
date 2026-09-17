# Thread harvest into generative artifact-table writes

**Linear:** [AST-1700](https://linear.app/astralcareermatch/issue/AST-1700)
**Parent:** [AST-1579](https://linear.app/astralcareermatch/issue/AST-1579) — Capture deduped source-artifact-id array on derived-artifact write
**Publish ref:** `sub/AST-1579/AST-1700-thread-harvest-generative-artifact-writes`

After sibling [AST-1698](https://linear.app/astralcareermatch/issue/AST-1698) attaches `source_artifact_ids` on `do_task`, thread that harvest into generative artifact-table lands: pass it through non-`job_resume` `tracker.save_job_artifact` and operative `save_candidate_data` (str path) → `database.save_artifact`. Leave `job.artifacts.job_resume` auto-cite untouched. Align draft `patt.artifact.traceability` Implementation with this epic’s persist surfaces. Does **not** own consult job_data siblings ([AST-1699](https://linear.app/astralcareermatch/issue/AST-1699)).

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/core/agent.py` — **modified** — on generative `save_job_artifact` / `save_candidate_data` lands from this run, pass the harvest list (except job_resume auto-cite remains authoritative).
- `src/core/candidate.py` — **modified** — operative `save_candidate_data` str-path accepts and passes optional `source_artifact_ids` through to `database.save_artifact`.
- `src/core/tracker.py` — **modified** — only if a thin pass-through is required for non-`job_resume` generative writes; do **not** weaken job_resume auto-cite.
- `canon/directives/draft/patt.artifact.traceability.md` — **modified** — Implementation alignment note for this epic’s surfaces.

Every row in **Files Changed** is one of those paths. Technical kinds covered: agent craft-land pass-through of the existing harvest list; candidate operative save optional sources + forward on insert; optional tracker touch; draft Implementation one-liner. No consult job_data siblings, no re-own of harvest helper, no new `ARTIFACT_CONFIG` keys, no versioned agent/agent_task lineage columns, no `tokens_ready` claim changes.

⚠️ **Decision (tracker):** On the synced ftr tip, `tracker.save_job_artifact` already accepts `source_artifact_ids: Optional[Sequence[str]] = None`, auto-cites current `base_resume` for `job.artifacts.job_resume`, and passes caller sources for every other job catalog key. **No `src/core/tracker.py` edit in this ticket** — agent call-site pass-through is enough. If build discovers that signature missing or job_resume ignore broken, stop and comment on parent AST-1579 (scope said “only if needed”; do not invent a different tracker change).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Operative `save_candidate_data` str-path: optional `source_artifact_ids`; forward to `database.save_artifact` on insert; identical-to-current short-circuit unchanged | core |
| `src/core/agent.py` | In `do_task` generative land sites, pass `list(source_artifact_ids)` into `save_job_artifact` and str-path `save_candidate_data` | core |
| `canon/directives/draft/patt.artifact.traceability.md` | Implementation alignment: AST-1579 harvest + generative `source_artifact_ids` wiring (this child) / consult siblings out of band; still draft | canon |

**Out of this ticket (do not touch):** `src/core/consult.py` / AST-1699 job_data siblings; `src/utils/config.py` harvest parse; re-implement `harvest_source_artifact_ids`; `src/core/tracker.py` (see Decision above); `src/data/database.py` `save_artifact` signature (already accepts sources); new `ARTIFACT_CONFIG` / `TOKEN_SOURCES` rows; promote draft → active; `tests/` / `docs/test-bible/**` (Betty).

## Stage 1: Candidate operative save accepts optional sources

**Done when:** `save_candidate_data(candidate_id, artifact_key, blob, source_artifact_ids=[...])` on the str path forwards that list to `database.save_artifact(..., source_artifact_ids=...)`. Omitting the kwarg still inserts with default empty sources (same as today). Identical-to-current still returns the existing uuid without calling `save_artifact`. Dict/library merge path unchanged (no sources kwarg effect).

1. In `src/core/candidate.py`, extend typing imports if needed: add `Sequence` to the existing `typing` import (`Any, Dict, List, Optional, Tuple` → include `Sequence`).

2. Change the `save_candidate_data` signature to:

```python
def save_candidate_data(
    candidate_id: str,
    data_or_artifact_key: Any,
    blob: Any = None,
    replace: bool = False,
    *,
    source_artifact_ids: Optional[Sequence[str]] = None,
    debug: bool = False,
) -> Optional[str]:
```

Keep `source_artifact_ids` keyword-only (same style as `debug`) so positional callers stay valid.

3. On the **str path only**, after the identical-to-current short-circuit (do **not** change that compare or early return), update the `database.save_artifact` call from:

```python
new_uuid = database.save_artifact(
    entry["entity_type"], candidate_id, artifact_type, blob
)
```

to:

```python
new_uuid = database.save_artifact(
    entry["entity_type"],
    candidate_id,
    artifact_type,
    blob,
    source_artifact_ids=source_artifact_ids,
)
```

Passing `None` is correct — `database.save_artifact` already normalizes `None` → `[]`.

4. Do **not** thread `source_artifact_ids` on the dict/library merge branch. Do **not** change identical-to-current behavior (sources are irrelevant when no insert happens). Do **not** validate that source uuids exist (data layer does not; matches write-operative / AST-1591).

5. Docstring: one line noting optional `source_artifact_ids` on the str path only (generative / caller-supplied seed pins).

## Stage 2: Agent generative lands pass the harvest list

**Done when:** After a successful `do_task` generative land through (a) non-`job_resume` `save_job_artifact` or (b) str-path `save_candidate_data`, when the run’s harvest list was non-empty, the new artifacts row’s `source_artifact_ids` equals that list. A `job.artifacts.job_resume` land still stores only the auto-cited current `base_resume` id (or `[]`), ignoring the harvest list (tracker rule unchanged).

1. In `src/core/agent.py` `do_task`, at the **job catalog land** site (~line where `landed = save_job_artifact(index, catalog_key, body)`), change to:

```python
landed = save_job_artifact(
    index,
    catalog_key,
    body,
    source_artifact_ids=list(source_artifact_ids),
)
```

Use the local `source_artifact_ids` already computed earlier in `do_task` by AST-1698 (always a `list` after harvest). Do **not** re-call `harvest_source_artifact_ids`. Do **not** special-case `job_resume` in agent — tracker ignores caller sources for that key.

2. At the **candidate craft land** str-path site (~line `save_candidate_data(str(index), artifact_key, content)`), change to:

```python
save_candidate_data(
    str(index),
    artifact_key,
    content,
    source_artifact_ids=list(source_artifact_ids),
)
```

Leave the preceding dict-path `save_candidate_data(str(index), {"artifacts": {"resume_structure": structure}})` **without** sources (library merge, not operative insert of the craft body).

3. Do **not** pass sources into `_persist_craft_dispatch_success` / rubric / company-search-terms library saves — those are not the operative str-path / `save_job_artifact` surfaces named by AC5–6.

4. Empty harvest: still pass `list(source_artifact_ids)` (may be `[]`). Do not omit the kwarg on generative lands so behavior is explicit and matches consult sibling empty-list contract spirit.

5. Sanity greps the builder must satisfy before Code Complete:

```bash
# Job land must pass sources; job_resume ignore remains in tracker
grep -n 'save_job_artifact(' src/core/agent.py
grep -n 'job_resume\|source_artifact_ids' src/core/tracker.py
# Candidate str-path land must pass sources
grep -n 'save_candidate_data(' src/core/agent.py
# No new ARTIFACT_CONFIG keys; no agent/agent_task lineage columns
grep -n 'ARTIFACT_CONFIG\[' src/core/agent.py src/core/candidate.py || true
```

Fail if agent invents a job_resume-specific source override that bypasses tracker auto-cite, or if harvest is re-parsed at land time instead of using the `do_task` local list.

## Stage 3: Draft traceability Implementation alignment

**Done when:** Draft `patt.artifact.traceability.md` Implementation notes that AST-1579 implements prompt-time harvest + generative `source_artifact_ids` wiring on operative artifact writes (and names consult sibling persist as the other persist surface), without promoting the draft or adding agent/task lineage as live product.

1. In `canon/directives/draft/patt.artifact.traceability.md`, under `# Implementation`, amend the existing “Capture at generative write” / related bullets so they record this epic’s **seed-id** slice only. Concrete edit (rewrite the numbered Implementation items that currently say generic “implement ticket” for seed capture — keep Draft / AST-1588 / Manual inheritance / Consumers / Non-goal structure):

   - Keep item **Draft** and **AST-1588** as-is (column already landed).
   - Replace or extend the **Capture at generative write** bullet to state: **AST-1579** — prompt-time token harvest ([AST-1698](https://linear.app/astralcareermatch/issue/AST-1698)) + generative operative writes pass the harvest as `source_artifact_ids` via `save_candidate_data` str-path / non-`job_resume` `save_job_artifact` ([AST-1700](https://linear.app/astralcareermatch/issue/AST-1700)); consult grade/analysis sibling job_data array is [AST-1699](https://linear.app/astralcareermatch/issue/AST-1699). Versioned `agent_id` / `agent_task_id` lineage remains implement-later.
   - Keep **Manual edit inheritance**, **Consumers**, **Non-goal** — do not claim UI/Estelle inheritance as done.

2. In `# Examples`, if the live example still only mentions job_resume→base_resume, add one prose clause that generative agent lands may also pass the harvested list for non-`job_resume` keys — still draft documentation, not a new API fence. Do **not** invent versioned agent/task columns in the example.

3. Do **not** move the file out of `canon/directives/draft/`. Do **not** flip `status` / promote to active.

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1579/AST-1700-thread-harvest-generative-artifact-writes`.
- Do not add files outside **Files Changed**.
- Ambiguity or codebase drift → stop and comment on parent AST-1579 with the Stage blocked template from plan-child.
- Test-tree ban: no edits under `tests/` or `docs/test-bible/**`.
- Depends on AST-1698 harvest attach (`result["source_artifact_ids"]` / local `source_artifact_ids` in `do_task`) already present on the synced ftr tip — do not re-implement harvest.

## Estimate

Confirm Chuckles estimate: 3 — agree
