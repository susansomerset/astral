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
