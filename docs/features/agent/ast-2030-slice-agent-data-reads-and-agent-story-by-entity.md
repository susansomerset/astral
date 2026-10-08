# AST-2030 — Slice agent-data reads and agent story by entity

- **Parent:** [AST-2028 — Technical fail modals must filter by entity_id](https://linear.app/astralcareermatch/issue/AST-2028)
- **Ticket:** [AST-2030](https://linear.app/astralcareermatch/issue/AST-2030)
- **Publish ref:** `origin/sub/AST-2028/AST-2030-slice-agent-data-reads-by-entity`
- **Canon Scope:** `patt.entity.batch-processing`, `stat.logging.debug`
- **Depends on:** [AST-2029](https://linear.app/astralcareermatch/issue/AST-2029) (`hydrate_entity_labels` / `split_entity_segments` in `src/utils/formatting.py`, already on `origin/ftr/AST-2028-technical-fail-modals-filter-by-entity-id`)

Sibling AST-2029 now stores batch `NO_CACHE` and `RESPONSE` rows with `[entity_id=<id>]`
labels instead of positions, and provides `split_entity_segments(text) -> {id: segment}`
(`{}` means there are no id-keyed segments, i.e. the row is legacy or single-entity). This ticket
moves the two **read** paths onto that split. The first is `get_agent_data(batch_id, entity_id=…)`, which backs
`GET /api/agent_data/<batch>?entity_id=…`. It cuts `NO_CACHE` / `TASK` / `RESPONSE` rows down to one
entity and drops rows that came from another chunk's call. The second is `get_entity_agent_story`, which cuts
`NO_CACHE` / `RESPONSE` blocks to one entity for **every** task, not only scored tasks.
Legacy rows are returned whole. Storage, API, schema and UI are not touched.

## Decisions (read before Stages)

⚠️ **Decision D1 — one shared slice helper with three outcomes.** A new private
`_slice_entity_block(content, entity_id) -> Optional[str]` in `src/core/agent.py` calls
`split_entity_segments(content)` and returns:

| Split result | Return | Meaning |
|--------------|--------|---------|
| `{}` | `content` (whole) | Legacy positional row, single-entity row, or shared prompt text (AC7) |
| has `entity_id` | `segments[entity_id]` | This entity's slice (AC4, AC6) |
| non-empty, no `entity_id` | `None` | Another chunk's call (AC5) |

Both read paths use it, so the run modal and the story apply the same rule.

⚠️ **Decision D2 — what `None` means on each path.** `get_agent_data` **drops** the row
(that's what the ticket Scope asks for: "rows with segments but none for this id dropped"). `get_entity_agent_story` keeps
the block with `content = ""`. That is the existing `_filter_response_block` no-match result, and the
frontend already skips empty blocks, so the `NO_CACHE (2)` style counter labels stay stable.

⚠️ **Decision D3 — `_filter_response_block` is deleted, `_extract_entity_segment` stays.**
The Scope says the scored-only `_filter_response_block` "folds in". Its only caller is the story, so it is
removed. `_extract_entity_segment` keeps working for `get_entity_response` (the `/entity/<id>` route
and `candidate.py:3594`), which is outside this ticket's Scope. Only `get_agent_data` stops calling it.

⚠️ **Decision D4 — behaviour changes we accept, both coming straight from the parent ACs.**
- Story, scored task, old encoded `jobs[]` with no ids: previously returned `""`. It now returns the
  whole block, because `split_entity_segments` gives `{}` (parent §6 says "never an empty pane", AC7).
- `get_agent_data`, JSON `results[]` / `entities[]` arrays and flat JSON: these were sliced or kept by
  `_extract_entity_segment`. They now go through the split, which only keys `companies[]` / `jobs[]`, so they come back whole.
  No do_task path currently writes `results[]` / `entities[]` RESPONSE rows keyed by id.

⚠️ **Decision D5 — the story only slices job and company entities.** The slice runs only when the existing
`entity_ref_id = entity.get("astral_job_id") or entity.get("short_name")` is set. This is the same guard
the scored path uses today. Candidate stories stay whole. Company ids match because roster/consult
store `company_id == short_name` in `batch_entities`. We match on the block's raw `type`
(`NO_CACHE` / `RESPONSE`), not the counter-suffixed label.

⚠️ **Decision D6 — shared prompt-text `NO_CACHE` rows stay whole.** AST-2029 D4 left the
token-resolved `nocache_content` row unhydrated. It has no `[entity_id=…]` tags, so it hits the `{}` branch
and is returned whole. This follows the Scope rule literally ("rows with no id-keyed segments returned whole").
It is the shared prompt, and no chunk owns it: when the prompt text is identical across chunks,
`save_agent_data` dedupes it to one row, because its id is a hash of `batch_id:block_type:content`. AC5 is therefore judged on the
live (tagged) `NO_CACHE` and `RESPONSE` rows. `TASK` rows are covered the same way: they are passed through the helper
(as the Scope requires), and they come back whole unless they carry tags.

⚠️ **Decision D7 — debug logging (`stat.logging.debug`).** The helper logs its full return value
(`Response from _slice_entity_block: …`, not truncated). `split_entity_segments` already logs
its own loop. The two loops this ticket rewrites (`get_agent_data` row loop and the story's
`entries` loop) get begin/end lines. Nothing is gated on a flag.

## Explicit scope gate

Ticket `## Scope` covers exactly `src/core/agent.py`:
- Agent-data read with `entity_id`: `NO_CACHE` / `TASK` / `RESPONSE` are cut via the split, rows with segments but
  none for this id are dropped, rows with no id-keyed segments are returned whole, and this replaces the `_extract_entity_segment`
  scan for these types. ✔ Stage 1 (`_slice_entity_block`) + Stage 2 (`get_agent_data`).
- Agent-story builder: `NO_CACHE` and `RESPONSE` for every task are cut via the same split, and the scored-only
  `_filter_response_block` folds in. ✔ Stage 3 (`get_entity_agent_story`, delete `_filter_response_block`).

Not touched: `src/utils/formatting.py` (sibling AST-2029 owns hydrate/split), storage
(`_store_prompt_blocks`, `_store_response_block`, `do_task`), `get_entity_response`,
`_extract_entity_segment`, `src/ui/api/` (the route already forwards `entity_id`), `src/data/`, all UI,
`tests/` and the test bible (Betty).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | Import `split_entity_segments`; add `_slice_entity_block`; rewrite the `get_agent_data` entity branch; slice `NO_CACHE` / `RESPONSE` for every task in `get_entity_agent_story`; delete `_filter_response_block` | core |

## Stage 1: Slice helper

**Done when:** `_slice_entity_block("[entity_id=A]: a\n[entity_id=B]: b", "B") == "[entity_id=B]: b"`,
`_slice_entity_block("[entity_id=D]: d", "B") is None`, and `_slice_entity_block("000: x", "B") == "000: x"`.

1. In `src/core/agent.py`, add `split_entity_segments,` to the existing
   `from src.utils.formatting import (…)` block (line ~82), after `hydrate_entity_labels,`.
2. Replace the whole `_filter_response_block` function (from `def _filter_response_block(content: str, entity_id: str) -> str:`
   through its final `return json.dumps(match, indent=2) if match else ""`, line ~3586) with:
   ```python
   def _slice_entity_block(content: str, entity_id: str) -> Optional[str]:
       """One entity's slice of a stored NO_CACHE / TASK / RESPONSE block (AST-2030).

       Whole block when it has no id-keyed segments (legacy positional, single-entity, shared prompt);
       None when it has segments but none for entity_id (another chunk's call in the same batch).
       """
       segments = split_entity_segments(content)
       out = segments.get(entity_id) if segments else content
       logger.debug("Response from _slice_entity_block: %s", out)
       return out
   ```

## Stage 2: Agent-data read with `entity_id`

**Done when:** on a batch holding chunk 1 (`[A,B,C]`, hydrated) and chunk 2 (`[D,E]`, hydrated),
`get_agent_data(batch, entity_id="B")` returns the chunk-1 live `NO_CACHE` row as B's segment only. It returns
no live `NO_CACHE` / `RESPONSE` row from chunk 2. `SYSTEM` / `CACHE_*` rows are returned unchanged, and a
`000:` legacy row is returned whole.

1. In `get_agent_data` (line ~3620), replace the docstring with:
   ```python
   """Retrieve agent_data blocks for a batch.
   With entity_id, NO_CACHE / TASK / RESPONSE rows are cut to that entity via _slice_entity_block
   (AST-2030): other chunks' rows are dropped, rows without id-keyed segments return whole.
   SYSTEM / CACHE_A–D are shared prompt and pass through."""
   ```
2. Replace everything after `if not entity_id:\n        return rows` (the `result = []` loop through
   `return result`) with:
   ```python
   result = []
   logger.debug("Beginning get_agent_data slice loop on %s items", len(rows))
   for row in rows:
       if row.get("block_type") not in ("NO_CACHE", "TASK", "RESPONSE"):
           result.append(row)
           continue
       segment = _slice_entity_block(row.get("block_data") or "", entity_id)
       if segment is None:
           continue  # another chunk's call — carries only other entities
       result.append({**row, "block_data": segment})
   logger.debug("End get_agent_data slice loop after %s items", len(result))
   return result
   ```
3. Leave `get_entity_response` and `_extract_entity_segment` unchanged (**D3**).

## Stage 3: Agent story sliced for every task

**Done when:** `get_entity_agent_story` for job B, on an **unscored** batch task whose live
`NO_CACHE` was stored as `[entity_id=A]: …\n[entity_id=B]: …\n[entity_id=C]: …`, returns that block
as B's segment only. A `000:` legacy block is returned whole. A block holding only other ids comes back as `""`.

1. In `get_entity_agent_story` (line ~3482), replace the docstring paragraph that starts
   `For scored tasks (TASK_CONFIG[task_key].scored == True):` and ends with
   `yields an empty content string so the frontend skips rendering.` with:
   ```
   For job / company entities, NO_CACHE and RESPONSE blocks of every task are cut to this
   entity via _slice_entity_block (AST-2030): a block carrying only other entities becomes ""
   (frontend skips it); a block with no id-keyed segments (legacy) shows whole.
   Scored tasks also attach vector_grades and rubric_artifact for display.
   ```
2. Directly before `for e in entries:` (the enrichment loop after `enriched = []`), add
   `logger.debug("Beginning get_entity_agent_story loop on %s items", len(entries))`. Directly before
   the function's final `return enriched`, add
   `logger.debug("End get_entity_agent_story loop after %s items", len(enriched))`.
3. Replace
   ```python
   if is_scored and btype == "RESPONSE" and entity_ref_id:
       content = _filter_response_block(content, entity_ref_id)
   ```
   with
   ```python
   if btype in ("NO_CACHE", "RESPONSE") and entity_ref_id:
       # AST-2030: every task, not only scored; another chunk's block → "" (D2)
       content = _slice_entity_block(content, entity_ref_id) or ""
   ```
   Keep `is_scored`, because it still drives `vector_grades` / `rubric_artifact`.
4. Confirm `rg -n "_filter_response_block" src/` returns nothing.
5. Compile and lint: `python -m py_compile src/core/agent.py`, then the repo linter on `src/core/agent.py`.
   The only new findings allowed are the file's existing typing-style ones (`UP045` on `Optional[str]`).
   Then confirm `git diff origin/dev...HEAD -- src/ui/api/ src/data/` is empty (AC8).

## For QA (Betty)

- `tests/component/core/test_agent.py:9045` calls `agent_mod._filter_response_block`, which is removed (**D3**).
  That test is now obsolete, and its intent (non-JSON RESPONSE stays as-is) is covered by the `{}` branch of `_slice_entity_block`.
- Existing `get_agent_data(..., entity_id=…)` tests that expected `results[]` / `entities[]` / flat-JSON
  slicing through `_extract_entity_segment` will now get the whole row (**D4**). `_extract_entity_segment`'s own
  unit tests are unaffected.
- Any story test that expects `""` for scored old-encoded `jobs[]` without ids now gets the whole block (**D4**, AC7).

## Execution contract

Run the steps in order, and don't add files beyond **Files Changed**. If a line reference has drifted,
find the code by the quoted text. If the quoted code is gone or different, stop and post
`🛑 Stage N blocked: …` on [AST-2028](https://linear.app/astralcareermatch/issue/AST-2028).
Make one commit per stage (`code(AST-2030): …`) and publish it to the publish ref.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

```text
[plan-rubric]
**Ticket:** AST-2030
**Overall:** APPROVED
**Corpus:** 8fa9f84d0e775852bc529f67faadf7e6f12cd904 (canon/ tree at publish tip)
**Publish ref:** b75afb62c0b378cd33855a1b4113fb1c4daceaa6

## Canon scores
patt.entity.batch-processing | A |
stat.logging.debug | B |

## Traceability
4→Stages 1–2 (`_slice_entity_block` + `get_agent_data` on tagged live `NO_CACHE`); 5→Stages 1–2 (`None` drops other-chunk rows); 6→Stage 3 (every-task `NO_CACHE`/`RESPONSE` slice); 7→Stage 1 `{}` → whole + Stage 3 legacy `000:`; 8→Stage 3 §5 (`src/ui/api/`, `src/data/` diff empty).

## Findings
- **discuss** | Procedure | Ticket is **Plan Ready** but assignee is Hedy, not Joan. Validation proceeded per spawn; Chuckles should assign Joan before inbox `validate-plan` gates if watchers enforce assignee.
- **acceptable** | Decisions D4 | Documented read-path behavior change for old `jobs[]` without ids (`""` → whole) and for `results[]`/`entities[]` rows; matches parent AC7 “never an empty pane” and no current writer for those JSON shapes.
- **acceptable** | Stage 1 helper | `_slice_entity_block` omits a `Calling _slice_entity_block: …` inbound debug line; outbound `Response from …` plus loop begin/end elsewhere is slight variance under `stat.logging.debug`, not a plan blocker.

context_tokens≈28000
```

## Review

- **Branch:** `origin/sub/AST-2028/AST-2030-slice-agent-data-reads-by-entity`
- **Build commits:** `7e0ad85f0` (Stage 1: `_slice_entity_block`, which replaces `_filter_response_block`), `868497f7d` (Stage 2: `get_agent_data` slices `NO_CACHE` / `TASK` / `RESPONSE` and drops other chunks' rows), `aa944fcd1` (Stage 3: the story slices `NO_CACHE` / `RESPONSE` for every task, plus loop begin/end debug lines).
- **Build notes:**
  - `py_compile` is clean.
  - `ruff` before/after on `src/core/agent.py`: the only new finding is `UP045` on `Optional[str]`, which matches the file's existing typing style.
  - Stage 1's interim commit carried one F821, because the story still called the deleted `_filter_response_block`. Stage 3 removed that call as the plan sequenced it.
  - `rg _filter_response_block src/` returns nothing.
  - `git diff origin/dev...HEAD -- src/ui/api/ src/data/` is empty (AC8).
  - Called against stubbed rows: `get_agent_data(entity_id="B")` returns `SYSTEM` whole, chunk 1's live `NO_CACHE` as `[entity_id=B]: b` only, and the `000:` legacy row whole. It drops chunk 2's `[D,E]` `NO_CACHE` and `RESPONSE` rows (AC4, AC5, AC7). `get_entity_agent_story` for job B on an unscored task returns B's `NO_CACHE` slice and the legacy block whole, and returns `""` for the other-chunk `RESPONSE` (AC6, AC7).
- **Existing tests:** `test_agent.py` + `test_agent_ast2029.py` fail 51 on the pre-build tree and 56 after it. The 5 new failures are all intended behaviour changes, and none of them is a regression:
  - `TestFilterResponseBlock::test_batch_response_filters_matching_job` and `::test_non_json_and_single_job_responses` call the deleted `_filter_response_block` (D3).
  - `TestAgentDataAccess::test_get_agent_data_keeps_row_when_segment_missing` and `TestEntitySegmentAccess::test_get_agent_data_keeps_rows_without_matching_segment` expect a row whose `jobs[]` only holds another id to be kept. AC5 / D1 now drop it.
  - `TestEntityAgentStoryBranches::test_scored_response_without_job_id_keeps_content` expects `""` for old `jobs[]` with no ids. AC7 / D4 now return it whole.
- **Deviation:** none.
- **For QA:** see `## For QA (Betty)` above. The two `get_agent_data` "keeps row" tests (AC5) are the case that section didn't list by name.

## Radia review

```text
[code-rubric]
**Ticket:** AST-2030
**Publish ref:** 9b73ea9d1f567a13d7625e1cef7dae2de66a1a6e
**Corpus:** 2344ae3265b15125a8f4a655946fcfe66b3e1def
**Overall:** CLEAN

## Canon scores
patt.entity.batch-processing | A |
stat.logging.debug | B |

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
- **advisory** | sibling product + test carry | Publish ref `origin/sub/AST-2028/AST-2030-slice-agent-data-reads-by-entity` three-dot diff vs `origin/dev` also contains AST-2029 storage (`src/utils/formatting.py` hydrate/split, `do_task` `entity_ids`, `test_agent_ast2029.py`, expanded `ast-2029` plan doc). Expected while #1 is not on `dev` and this branch stacks the dependency (`blockedBy` AST-2029). AST-2030-owned read changes remain confined to `_slice_entity_block`, `get_agent_data`, and `get_entity_agent_story` in `src/core/agent.py`.
- **advisory** | `src/utils/formatting.py` | On this tip, `hydrate_entity_labels` logs full `out` (`Response from hydrate_entity_labels: %s`), addressing the count-only pattern noted on the AST-2029 line in the prior review thread.
- **advisory** | `stat.logging.debug` | `_slice_entity_block` has outbound `Response from …` (full `out`, per plan D7) but no `Calling _slice_entity_block: [entity_id=…]` inbound line — Joan flagged this as slight variance at plan; unchanged in code.
- **advisory** | `tests/component/core/test_consult.py` | Diff removes consult tests unrelated to AST-2030 manifest; treat as merge-tests / bible hygiene carry unless Betty’s manifest calls them out.

## What's solid
- Stage 1–3 match plan: `_filter_response_block` removed; `_slice_entity_block` implements D1 three-way semantics (`{}` → whole, match → segment, other ids → `None`).
- `get_agent_data` slices `NO_CACHE` / `TASK` / `RESPONSE`, passes `SYSTEM` / `CACHE_*`, drops `None` rows (AC5), copies rows with `{**row, …}` (no mutation — tested).
- `get_entity_agent_story` slices `NO_CACHE` / `RESPONSE` for every task when `entity_ref_id` set; `None` → `""` (D2); candidates stay whole (D5).
- `test_agent_ast2030.py` covers AC4–AC7, D6 shared prompt, chunk isolation, company `short_name`, candidate whole; `test_agent.py` retargets obsolete `_filter_response_block` tests to `_slice_entity_block` and AC5 drop behavior.
- AC8: `src/ui/api/` and `src/data/` diff empty; `rg _filter_response_block` clean on `src/`.

## Recommended actions (downstream only — not executed in this session)
- Chuckles: append artifact, `docs(AST-2030): Radia review — clean`, post slim upshot `--as radia`, **Review Posted** → datt may route **PROCEED** toward User Testing once AST-2029 dependency is satisfied in the epic merge order.
- Optional: add `Calling _slice_entity_block: …` debug if Susan wants strict callee-in symmetry (effort 2); not gated on current **B** grade.

context_tokens≈22000
```

## Bug: AST-2052 — Job run modal should read like a single Each-mode call

Modal wiring (job → `entityId` → `?entity_id=`) is unchanged; see
`docs/features/agent/ast-2031-job-run-modal-requests-entity-scoped-agent-data.md`. All of this fix
lands in this ticket's read path: `get_agent_data` with `entity_id` in `src/core/agent.py`.

### As-is

A job's run modal on a batched (`batch_call_mode` = 1) run calls
`GET /api/agent_data/<batch>?entity_id=<job>`. `get_agent_data` then returns the batch's rows with
`NO_CACHE` / `TASK` / `RESPONSE` passed through `_slice_entity_block`, which returns only the **bare
segment** that `split_entity_segments` produces:
- **Success RESPONSE:** stored as `json.dumps(parsed)`, e.g. `{"jobs":[{…A…},{…B…}],"agent_performance":{…}}`.
  For B it comes back as just `{…B…}` (pretty JSON). The `jobs` wrapper and every other top-level key are lost.
- **Tagged text (failure RESPONSE, encoded `agent_payload`, live NO_CACHE):** everything before the first
  `[entity_id=…]` tag is dropped. That includes the `Provider failed: …\n\n--- model response ---\n` banner,
  the `{"agent_payload":"` opener, and any header above the first row. For B the modal shows only
  `[entity_id=B]|DTA5…`.
- **Blank rows:** any row whose content is blank or whitespace-only still gets a tab.

None of this looks like the same job's run in Each mode (`batch_call_mode` = 0, one `do_task` per job).
There, the same rows hold that job's whole call: the full response envelope with one item, and the
banner/opener intact.

### To-be

For `get_agent_data(batch_id, entity_id=X)`:
- **SYSTEM, CACHE_A–D, TASK** and the shared prompt-text `NO_CACHE`: returned whole. This is already true and must stay true.
- **Live `NO_CACHE` and `RESPONSE`:** returned as an Each-mode call would have stored them for X alone:
  - JSON with `companies[]` / `jobs[]`: the **same object** with that array filtered to X's item only, serialized
    with `json.dumps` (compact, same as `do_task` storage).
  - Tagged text: the **preamble** (text before the first `[entity_id=` tag) followed by X's segment.
- **Other ids only:** rows carrying only other ids are still dropped (AST-2030 AC5).
- **No id-keyed segments:** rows with no id-keyed segments are still returned whole (AST-2030 AC7).
- **Blank rows:** any row whose resulting `block_data` is blank after `.strip()` is omitted, so an empty
  CACHE_C gets no tab.

The modal needs no frontend change. It already orders tabs SYSTEM → CACHE_A–D → NO_CACHE → TASK → RESPONSE.

### Repro

Fixture rows for `get_agent_data_by_batch` (stub), `entity_id="B"`:

```python
rows = [
  {"block_type": "SYSTEM",   "block_data": "sys"},
  {"block_type": "CACHE_A",  "block_data": "cache a"},
  {"block_type": "CACHE_C",  "block_data": "   "},
  {"block_type": "NO_CACHE", "block_data": "Jobs to grade:\n[entity_id=A]: jd a\n[entity_id=B]: jd b"},
  {"block_type": "TASK",     "block_data": "grade them"},
  {"block_type": "RESPONSE", "block_data": '{"jobs":[{"astral_job_id":"A","g":1},{"astral_job_id":"B","g":2}],"agent_performance":{"status":"ok"}}'},
  {"block_type": "RESPONSE", "block_data": 'Provider failed: x\n\n--- model response ---\n{"agent_payload":"[entity_id=A]|DTA5\\n[entity_id=B]|GCA4"}'},
]
```

| Row | Today | Expected |
|-----|-------|----------|
| CACHE_C | returned (`"   "`) | omitted |
| NO_CACHE | `[entity_id=B]: jd b` | `Jobs to grade:\n[entity_id=B]: jd b` |
| JSON RESPONSE | `{\n  "astral_job_id": "B",\n  "g": 2\n}` | `{"jobs": [{"astral_job_id": "B", "g": 2}], "agent_performance": {"status": "ok"}}` |
| Failure RESPONSE | `[entity_id=B]\|GCA4"}` | `Provider failed: x\n\n--- model response ---\n{"agent_payload":"[entity_id=B]\|GCA4"}` |

### Root cause

AST-2030 D1 made `get_agent_data` and the agent story share `_slice_entity_block`. That helper returns
`split_entity_segments`'s bare per-entity segment: the JSON item alone, or the text from the entity's tag to
the next tag. That was right for the story's hop panes. The run modal, though, is meant to show **one
call**, and a bare segment strips that call's envelope and preamble. Separately, the entity read never
drops blank rows.

### Proposed change

All in `src/core/agent.py`. No change to `src/utils/formatting.py`, the API, the schema or the frontend.

1. Directly after `_slice_entity_block`, add:
   ```python
   def _entity_call_view(content: str, entity_id: str) -> Optional[str]:
       """Block as a one-entity (Each-mode) call would have stored it (AST-2052).

       JSON companies[] / jobs[] → same object with only this entity's item; tagged text → preamble
       before the first [entity_id=…] tag + this entity's segment. Whole / None exactly as _slice_entity_block.
       """
       seg = _slice_entity_block(content, entity_id)
       if seg is None or seg == content:
           return seg  # other chunk's call, or no id-keyed segments (legacy / shared prompt)
       try:
           data = json.loads(content)
       except (json.JSONDecodeError, TypeError):
           data = None
       # Same array precedence as split_entity_segments: companies[] first, else jobs[]
       arr_key, id_key = next(
           ((k, i) for k, i in (("companies", "company_id"), ("jobs", "astral_job_id"))
            if isinstance(data, dict) and isinstance(data.get(k), list)),
           (None, None),
       )
       if arr_key:
           items = [it for it in data[arr_key] if isinstance(it, dict) and str(it.get(id_key)) == entity_id]
           out = json.dumps({**data, arr_key: items})
       else:
           out = content[: max(content.find("[entity_id="), 0)] + seg
       logger.debug("Response from _entity_call_view: %s", out)
       return out
   ```
   ⚠️ **Decision D1-2052 — preamble = text before the first literal `[entity_id=`.** We don't re-use
   `formatting._ENTITY_LABEL` (it's private to another module). Stored tags only ever come from
   `hydrate_entity_labels`, so the first literal occurrence is the first tag.
   ⚠️ **Decision D2-2052 — no trailing envelope suffix.** For a non-last entity in a JSON-enveloped
   tagged response, the view keeps the opener (`{"agent_payload":"`) but not the closing `"}`, which belongs
   to the last segment (AST-2029 D7). We accept this; there is no suffix heuristic.
2. In `get_agent_data`'s entity branch:
   - Replace `segment = _slice_entity_block(row.get("block_data") or "", entity_id)` with
     `segment = _entity_call_view(row.get("block_data") or "", entity_id)`.
   - Change the pass-through for non-sliced types from `result.append(row)` to:
     ```python
     if (row.get("block_data") or "").strip():
         result.append(row)
     continue
     ```
     That is: keep the `if row.get("block_type") not in (...)` guard and only append when non-blank.
   - Change the sliced-row branch so that after the `if segment is None: continue` line, it skips blank
     segments with `if not segment.strip(): continue  # AST-2052: skip empty prompt content`, before the
     `result.append({**row, "block_data": segment})` line.
   - Update the docstring's second line to: `With entity_id (AST-2030 / AST-2052), rows read as one Each-mode call for that entity: NO_CACHE / TASK / RESPONSE via _entity_call_view (other chunks' rows dropped, rows without id-keyed segments whole), blank rows omitted.`
3. Leave `get_entity_agent_story` on `_slice_entity_block` (bare segment). Leave `_slice_entity_block`,
   `get_entity_response` and `_extract_entity_segment` unchanged.
4. Compile and lint `src/core/agent.py`. The only new ruff finding allowed is the file's existing typing
   style (`UP045` on `Optional[str]`). `git diff origin/dev...HEAD -- src/ui/api/ src/data/ src/ui/frontend/ src/utils/` must be empty.

### Blast radius

- **`get_agent_data(entity_id=…)` callers:** only `GET /api/agent_data/<batch>?entity_id=` (`api_system.py`), and
  only the job run modal sends `entity_id` (AST-2031). Execution History, Vector Feedback and Ad Hoc send none,
  so their path (`if not entity_id: return rows`) is untouched, blank rows included.
- **Agent story / `JobDiscussionPane` / `AgentStoryTab`:** unchanged. They still get the bare slice.
- **Tests pinning the AST-2030 read shape:** `tests/component/core/test_agent_ast2030.py::TestAst2030GetAgentDataSlice`
  (e.g. the AC4 case asserting the NO_CACHE row equals exactly `[entity_id=B]: …`, and any JSON RESPONSE item-only
  assertion). These change wherever the fixture has a preamble or a JSON envelope. Betty's call (`fix-board`).
- **`tests/component/core/test_agent.py`:** `TestAgentDataAccess` / `TestEntitySegmentAccess` entity-read cases with
  blank `block_data` or JSON envelopes.

### What must still hold

- AST-2030 AC4: the slice holds no other entity's text. The preamble is shared batch text and the JSON keeps
  only X's item.
- AST-2030 AC5: a row carrying only other ids is dropped.
- AST-2030 AC7: legacy `000:` rows are returned whole. Blank-row skipping never applies to a non-blank legacy row.
- AST-2030 AC6 / parent §4: the story stays sliced per task and is not changed by this fix.
- Parent §3: SYSTEM and CACHE_A–D show as today, except that blank rows are now omitted in the entity view only.
- Parent §7 / AC9: batch-wide views (no `entity_id`) are byte-identical to before.
- AST-2030 AC8 / parent AC10: no change under `src/ui/api/` or `src/data/`.

## Joan fix-board (AST-2052)

[board-joan]  CANON: OK

The fix stays on the existing `batch_id` + optional `entity_id` read path in `src/core/agent.py`: it reshapes what `get_agent_data` returns for the run modal (envelope + preamble via `_entity_call_view`, blank-row drop) and explicitly leaves `get_entity_agent_story` on `_slice_entity_block`. That matches **patt.entity.batch-processing** — `batch_id` remains the join key; ids only refine which slice of stored blocks you see, with no new claim key or storage shape. **stat.logging.debug** adds an ungated `Response from _entity_call_view` with the full string; no new `debug=` plumbing and no statute carve-out. D1/D2-2052 (literal `[entity_id=` preamble, accepted partial JSON envelope suffix) are product read-path choices, not conflicts with in-force directive text; nothing in canon needs amending for this patch.

## Radia review-fix (AST-2052) — round 1

[code-rubric]
**Ticket:** AST-2052
**Publish ref:** 2c7b93bf44abae6fd49ae43b486149e37eb91c79
**Corpus:** 2344ae3265b15125a8f4a655946fcfe66b3e1def
**Overall:** FIX-NOW
**Parent shape:** Normal (bug on AST-2028; not orphaned)

## Canon scores
patt.entity.batch-processing | A |
stat.logging.debug | B |

## Column diff vs plan stage
no plan-stage canon scores attached (Joan fix-board **CANON: OK** on patch intent)

## Frame diff
(none)

## [bug-repro]
**OK** — `tests/component/core/test_agent_ast2052.py::TestAst2052EntityCallView::test_bug_repro_entity_read_is_one_each_mode_call` is tagged `[bug-repro]` and asserts the plan § Repro table verbatim: CACHE_C omitted; NO_CACHE keeps `Jobs to grade:\n` preamble + B segment; JSON RESPONSE keeps `jobs[]` wrapper + `agent_performance`; failure RESPONSE keeps provider banner + `{"agent_payload":"` opener + B segment. Would fail on pre-fix `_slice_entity_block`-only read (bare item, bare tag, blank CACHE_C tab).

## ## What must still hold
**FAIL** — Traced against `origin/ftr/AST-2028-technical-fail-modals-filter-by-entity-id...origin/sub/AST-2028/AST-2052-run-modal-each-mode-layout`:
- **AST-2030 AC8 / parent AC10 (no `src/ui/api/` or `src/data/` change):** **broken on publish ref** — `src/ui/api/api_system.py` adds `logo_background` / AST-2040 `ui_config` field (unrelated to AST-2052).
- **In-agent behavior** (AC4–AC7, story AC6, batch-wide AC9): **OK** in code — `get_entity_agent_story` still uses `_slice_entity_block`; `get_agent_data` without `entity_id` returns rows unchanged (`TestAst2052StillHolds::test_no_entity_id_batch_view_byte_identical`); guards cover AC5/AC7 and bare story slice.

## Findings

### fix-now
- **fix-now** | Cross-ticket scope on publish ref | Three-dot diff vs `origin/ftr/AST-2028-…` includes product/docs outside AST-2052: `src/core/contact.py`, `src/core/meteorite.py`, `src/utils/config.py`, `src/utils/deploy_status.py`, `src/ui/frontend/.../NavigationShell.tsx`, `src/ui/api/api_system.py`, canon `patt.contact.command-intercept.md`, feature docs AST-2034/2035, and large `test_contact` / `test_meteorite` additions. Plan § Proposed change limits the fix to `src/core/agent.py` (+ Betty tests). **resolve-child / Chuckles:** rebase or reset `sub/AST-2028/AST-2052-run-modal-each-mode-layout` so only AST-2052 commits (agent read path + `test_agent_ast2052.py` + `test_agent_ast2030.py` / bible rows for 2052) remain on top of ftr.
- **fix-now** | `## What must still hold` | Item “no change under `src/ui/api/`” is violated while `api_system.py` rides this branch (see above).

### discuss
(none)

### advisory
- **advisory** | `stat.logging.debug` | `_entity_call_view` logs full `out` per plan; no `Calling _entity_call_view: …` inbound line (same slight variance Joan accepted at fix-board for similar helpers).
- **advisory** | `test_agent_ast2052.py` | `TestAst2052StillHolds` documents regression guards for AC5/AC7/AC6/AC9 beyond the single `[bug-repro]` node — aligned with manifest “22 passed”.

## What's solid
- `_entity_call_view` matches plan: JSON array filter with `companies` before `jobs`, `str()` id match; tagged text uses literal `[entity_id=` preamble + segment; `None` / whole-block paths delegate to `_slice_entity_block`.
- `get_agent_data` entity branch: pass-through types skip blank `block_data`; sliced path uses `_entity_call_view`, drops `None` and whitespace-only segments.
- D2-2052 non-last entity failure envelope covered by `test_non_last_entity_keeps_opener_not_closing`.

## Recommended actions (downstream — not executed here)
- Chuckles: post **REVIEW** upshot; **Review Posted** → **resolve-child** (branch hygiene, not logic rewrite) → re-run **test-fix** → re-spawn **review-fix** once diff vs ftr is agent.py + AST-2052 tests/docs only.
- Hedy: drop unrelated commits from publish ref (or cherry-pick `7e0ad85`-style fix onto clean ftr tip); confirm `git diff origin/ftr/AST-2028-…...HEAD -- src/ui/api/ src/data/ src/ui/frontend/ src/utils/formatting.py` empty per plan §4.

context_tokens≈24000

[code-rubric] REVIEW (Commit: 2c7b93bf4) branch carries foreign diffs

> Chuckles: both fix-now items are an artifact of the review base — `origin/ftr` lagged `origin/dev`, so `ftr...sub` included dev commits `sync-child` merged in. `merge-tree(ftr, dev)` vs sub = only the 5 AST-2052 files. ftr refreshed from dev; review re-run.

## Radia review-fix (AST-2052) — round 2

[code-rubric]
**Ticket:** AST-2052 (review-fix round 2)
**Publish ref:** 3bf8bd5130aa39d9e252789702741a31127c7fd9
**Ftr base:** 2c01045acfa459bdb941625ab3c5ace59a6a4d3b (ancestor of publish ref — confirmed)
**Corpus:** 2344ae3265b15125a8f4a655946fcfe66b3e1def
**Overall:** CLEAN
**Parent shape:** Normal (not orphaned)

## Canon scores
patt.entity.batch-processing | A |
stat.logging.debug | B |

## Column diff vs plan stage
no plan-stage canon scores attached (Joan fix-board **CANON: OK** on patch intent)

## Frame diff
(none)

## [bug-repro]
**OK** — `test_agent_ast2052.py::TestAst2052EntityCallView::test_bug_repro_entity_read_is_one_each_mode_call` (`[bug-repro]`) asserts plan § Repro outcomes: CACHE_C omitted; NO_CACHE with preamble + B segment; compact JSON envelope with filtered `jobs[]` and retained `agent_performance`; failure RESPONSE with banner + JSON opener + B segment. Fails pre-fix `_slice_entity_block`-only entity read.

## ## What must still hold
**OK** — Traced on isolated diff `origin/ftr/AST-2028-technical-fail-modals-filter-by-entity-id...origin/sub/AST-2028/AST-2052-run-modal-each-mode-layout` (5 paths: `agent.py`, `test_agent_ast2052.py`, `test_agent_ast2030.py`, plan patch + bible):
- **AST-2030 AC4/AC5/AC7:** repro + `TestAst2052StillHolds::test_other_chunk_dropped_and_legacy_whole`
- **AST-2030 AC6 / story:** `test_story_keeps_bare_slice` — `get_entity_agent_story` still on `_slice_entity_block`
- **Parent §7 / batch-wide (AC9):** `test_no_entity_id_batch_view_byte_identical` — `get_agent_data` without `entity_id` unchanged
- **AST-2030 AC8 / no api/data/frontend/utils product change on this diff:** empty vs ftr for `src/ui/api/`, `src/data/`, `src/ui/frontend/`, `src/utils/`, other core modules

## Findings

### fix-now
(none)

### discuss
(none)

### advisory
- **advisory** | Round 1 retracted | Foreign diffs (`contact`, `meteorite`, `api_system`, etc.) were base-artifact from stale `origin/ftr`; refreshed ftr + sync-child yields the intended 5-file fix surface only. Product logic unchanged from `2c7b93bf4` per spawn brief.
- **advisory** | `stat.logging.debug` | `_entity_call_view` logs full `out`; no `Calling _entity_call_view: …` — slight variance, aligned with Joan fix-board.

## What's solid
- `_entity_call_view` + `get_agent_data` entity branch match plan § Proposed change (blank skip on pass-through and sliced rows; story path untouched).
- `test_agent_ast2030.py` trimmed blank-row expectations (moved to AST-2052); remaining AC4/AC5/AC7 cases still valid for Each-mode NO_CACHE where preamble is empty at first tag.

## Chuckles branching (read-only)
**PROCEED** + normal parent → **Review Posted** → fix-lane clean-review shortcut → **User Testing** (`resolve-child` skipped).

context_tokens≈12000

[code-rubric] PROCEED (Commit: 3bf8bd513) Each-mode entity read OK
