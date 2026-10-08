# AST-2029 — Store agent data with real entity ids

- **Parent:** [AST-2028 — Technical fail modals must filter by entity_id](https://linear.app/astralcareermatch/issue/AST-2028)
- **Ticket:** [AST-2029](https://linear.app/astralcareermatch/issue/AST-2029)
- **Publish ref:** `origin/sub/AST-2028/AST-2029-store-agent-data-with-entity-ids`
- **Canon Scope:** `patt.entity.batch-processing`, `stat.logging.debug`

When `do_task` stores a batch call's prompt and response in `agent_data`, the batch
live content (stored as a `NO_CACHE` row) and a failed call's raw `RESPONSE` label each
entity by its position in the batch (`000:`, `[index=000]:`, `000|`). The stored
rows can't be matched back to one job or company. This ticket rewrites those
positional labels to the call's real entity ids **at save time only**. The text sent to
the provider is left exactly as it is. It also adds the split helper that sibling
ticket #2 (agent-data read and agent-story slicing) will use to cut a stored block
down to one entity. It does **not** change any read path, API, schema, or UI.

## Decisions (read before Stages)

⚠️ **Decision D1 — the hydrated label format is `[entity_id=<id>]`.** Each positional label
is replaced by a single tag that keeps the original separator:

| Live / raw label | Stored label |
|------------------|--------------|
| `000: …` | `[entity_id=A]: …` |
| `[index=000]: …` | `[entity_id=A]: …` |
| `000|…` | `[entity_id=A]|…` |

Why: sibling #2's read path only knows the one id it's viewing, not the batch's
id list. So the split has to find labels **without** being told the ids. A bare `A:`
would be indistinguishable from ordinary `CONTENT:` / `job_link:` lines. The tag
mirrors `enumerate_array`'s existing keyed `[key=value]` form. It satisfies AC1
(ids appear as labels, with no `000:` prefix), AC2 (no `index=000`) and AC3 (lines are
labeled `A` / `B`, with no `000|`).

⚠️ **Decision D2 — labels are matched at a text boundary, with no JSON parse.** A label
counts when it appears at the start of a line, **or** right after a `"`, **or** right after
a literal two-character `\n` escape. Why: real encoded batch responses are
JSON envelopes such as `{"agent_payload":"000|DTA5\n001|GCA4"}` (see the fixtures
in `tests/component/external/test_anthropic.py`). In that raw text the newlines
are escaped, so a line-start-only match would miss rows 2 and up. Matching at those
boundaries hydrates the envelope in place: the raw audit text stays
byte-for-byte identical apart from the labels, and the same rule covers the list form
`["000|…","001|…"]`. Rejected alternatives: (a) parse the envelope and re-serialize
it, which reformats stored raw text and adds code; (b) line-start only, which means
JSON-enveloped failures never get hydrated.

⚠️ **Decision D3 — it's all or nothing on ids.** Hydration runs only when **every**
`batch_entities` item is a dict carrying a non-empty id under the entity type's id
key (`company_id` when `entity_type == "company"`, else `astral_job_id`, which is the same
rule as `_decode_payload`). Otherwise the stored text is left unchanged. Why:
`qualify_meteorite` passes stub entities with no `astral_job_id`
(`src/core/meteorite.py` ~line 630). A partial mapping would mislabel rows.

⚠️ **Decision D4 — only the live-content `NO_CACHE` row is hydrated.** `_store_prompt_blocks`
writes up to two `NO_CACHE` rows: `nocache_content` (token-resolved agent-task
prompt text) and `live_content` (the caller's batch rows). Batch positions come only
from the caller's live content (`consult.py` / `roster.py` / `meteorite.py` assemble
functions). Hydrating the prompt text would risk rewriting unrelated `NNN:` lines.
`SYSTEM`, `CACHE_A–D` and `TASK` rows are untouched.

⚠️ **Decision D5 — labels with an out-of-range position are left as-is.** If a label's position is
≥ the number of ids (for example, the model 1-indexes `100|` in a batch of 100), that label is not
rewritten. This is the same tolerance `_decode_payload` applies.

⚠️ **Decision D6 — known limitation, not mitigated.** Content text that happens to
start a line (or follow a `"`) with exactly three digits and then `:` or `|` (e.g. a JD
line `100: …`) inside a batch row will also be rewritten to that position's
id. No sequence or ordering guard is added (no heuristics without Susan's say-so).

⚠️ **Decision D7 — what split returns.** `split_entity_segments(text)` returns
`{entity_id: segment}`:
- **JSON first:** if `text` parses as a JSON object with a list under `companies`
  (id key `company_id`) or, failing that, under `jobs` (id key `astral_job_id`), it returns
  `{str(item[id_key]): json.dumps(item, indent=2)}` for each dict item with a truthy
  id. `companies` is preferred over `jobs`, the same as `_filter_response_block`.
- **Else, tags:** each `[entity_id=X]` tag (at the D2 boundaries) starts a segment
  that runs up to the next tag's start, or the end of the text. The segment includes its
  own tag. Trailing whitespace and trailing literal `\n` escapes are stripped.
  Text before the first tag (headers, failure banner) belongs to no segment.
  Repeated tags for the same id are joined with `"\n"`.
- **Nothing found:** returns `{}`. Sibling #2 treats `{}` as "legacy / single-entity,
  show whole".
- In the JSON-envelope case the last segment can keep the envelope's closing `"}`.
  This is accepted for display and is not stripped.

## Explicit scope gate

Ticket `## Scope` covers exactly:
- `src/utils/formatting.py` — new function (hydrate) and new function (split). ✔ Stages 1–2.
- `src/core/agent.py` — prompt-block storage hydrates the stored NO_CACHE from `batch_entities`;
  response storage hydrates the RESPONSE row on the success and failure paths; wire blocks are built
  from unhydrated text. ✔ Stage 3 (`_store_prompt_blocks`, `_store_response_block`,
  and their `do_task` call sites).

Not touched: the agent-data read / `get_agent_data` / `get_entity_response` /
`_extract_entity_segment` / `get_entity_agent_story` / `_filter_response_block`
(sibling #2); UI (sibling #3); `src/ui/api/`, `src/data/` (AC4); `consult.py` / `roster.py`
assemble functions; `run_adhoc_workbench_test` storage (Ad Hoc stays batch-wide per
parent §7); `tests/` and the test bible (Betty).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/formatting.py` | Import `get_logger`; add `_POSITIONAL_LABEL` / `_ENTITY_LABEL` regexes; add `hydrate_entity_labels`, `split_entity_segments` | utils |
| `src/core/agent.py` | Import the two helpers; `entity_ids` kwarg on `_store_prompt_blocks` and `_store_response_block`; compute ids once in `do_task` and pass them to every store call there | core |

## Stage 1: Hydrate helper in `formatting.py`

**Done when:** `hydrate_entity_labels("000: a\n001: b", ["A","B"])` returns
`"[entity_id=A]: a\n[entity_id=B]: b"`, and `hydrate_entity_labels(t, None)` returns `t`
unchanged.

1. In `src/utils/formatting.py`, below the existing `from urllib.parse import …` line, add
   `from src.utils.logging import get_logger` and, after the imports, `logger = get_logger(__name__)`.
   (`src/utils/logging.py` imports only stdlib at module level, so there is no cycle with `config.py`.)
2. Below `_ENCODED_GRADE_LINE`, add:
   ```python
   # Positional batch label at a line start, after a quote, or after a literal "\n" escape
   # (JSON-enveloped agent_payload). Group 1 = [index=NNN] form, group 2 = bare NNN before ':' or '|'.
   _POSITIONAL_LABEL = re.compile(
       r'(?:^|(?<=")|(?<=\\n))(?:\[index=(\d{3})\](?=:)|(\d{3})(?=[:|]))', re.M
   )
   # Hydrated label written by hydrate_entity_labels; same boundaries as _POSITIONAL_LABEL.
   _ENTITY_LABEL = re.compile(r'(?:^|(?<=")|(?<=\\n))\[entity_id=([^\]\s]+)\](?=[:|])', re.M)
   ```
3. Directly after `parse_enumerate_array`, add:
   ```python
   def hydrate_entity_labels(text: str, entity_ids: Optional[List[str]]) -> str:
       """Replace positional batch labels (NNN:, [index=NNN]:, NNN|) with [entity_id=<id>] (AST-2029).
       Position N maps to entity_ids[N]; out-of-range positions and unlabeled text stay unchanged.
       Storage-only — wire text must never be passed through this."""
       if not text or not entity_ids:
           return text
       def _sub(m: "re.Match[str]") -> str:
           pos = int(m.group(1) or m.group(2))
           return f"[entity_id={entity_ids[pos]}]" if pos < len(entity_ids) else m.group(0)
       out, n = _POSITIONAL_LABEL.subn(_sub, text)
       logger.debug("Response from hydrate_entity_labels: %s labels on %s ids", n, len(entity_ids))
       return out
   ```
   `subn` counts every match, including out-of-range ones it leaves alone. That's fine for a debug line.

## Stage 2: Split helper in `formatting.py`

**Done when:** `split_entity_segments("HDR\n[entity_id=A]: a\n[entity_id=B]: b")` returns
`{"A": "[entity_id=A]: a", "B": "[entity_id=B]: b"}`;
`split_entity_segments('{"jobs":[{"astral_job_id":"A","x":1}]}')` returns `{"A": <indent=2 JSON of the item>}`;
`split_entity_segments("000: legacy")` returns `{}`.

1. Directly after `hydrate_entity_labels`, add `split_entity_segments(text: str) -> Dict[str, str]` per
   **D7**, in this order:
   - If `not text`, return `{}`.
   - `try: data = json.loads(text)` / `except (json.JSONDecodeError, TypeError): data = None`.
     If `data` is a dict: for `(arr_key, id_key)` in `(("companies", "company_id"), ("jobs", "astral_job_id"))`,
     if `data.get(arr_key)` is a list, return
     `{str(it[id_key]): json.dumps(it, indent=2) for it in rows if isinstance(it, dict) and it.get(id_key)}`
     (return on the first list key found, even if empty). Comment: `# Success RESPONSE rows are decoded JSON keyed by real ids already`.
   - `matches = list(_ENTITY_LABEL.finditer(text))`; then
     `logger.debug("Beginning split_entity_segments loop on %s items", len(matches))`.
   - `out: Dict[str, str] = {}`; for `i, m in enumerate(matches)`: `end = matches[i+1].start() if i+1 < len(matches) else len(text)`;
     `seg = re.sub(r"(?:\\n)+$", "", text[m.start():end].rstrip())`; `eid = m.group(1)`;
     `out[eid] = f"{out[eid]}\n{seg}" if eid in out else seg`.
   - `logger.debug("End split_entity_segments loop after %s items", len(out))`; return `out`.
2. Docstring: one line stating that it returns per-entity segments keyed by id, that `{}` means
   no id-keyed segments (legacy or single-entity, so the caller shows the whole block), and the `(AST-2029)` tag.

## Stage 3: Hydrate at storage in `agent.py`

**Done when:** a `do_task` call with `ctx["batch_entities"]` `[A,B,C]` (job ids) and live content
`000: …\n001: …\n002: …` stores a live-content `NO_CACHE` row containing `[entity_id=A]` / `B` / `C`
with no `000:` prefix, while `_assemble_blocks_seven_segment`'s `user_blocks` (the wire) still contain
`000:` and no `A`. A failed call stores a `RESPONSE` row whose `000|` / `001|` lines read
`[entity_id=A]|` / `[entity_id=B]|`.

1. In `src/core/agent.py`, extend the existing import at line ~82
   `from src.utils.formatting import clean_encoded_agent_payload, coerce_grades_encoded_json_parse`
   to also import `hydrate_entity_labels`. (`split_entity_segments` is not imported here; sibling #2 imports it.)
2. `_store_prompt_blocks` (line ~1296): add a keyword-only parameter
   `entity_ids: Optional[List[str]] = None,` after `entity_id`. In **both** branches (the `cache_content`
   legacy branch and the `caches_resolved_four` branch), change
   `segments.append(("NO_CACHE", live_content))` to
   `segments.append(("NO_CACHE", hydrate_entity_labels(live_content, entity_ids)))`, with the comment
   `# AST-2029: stored copy only — wire blocks were already built from unhydrated live_content`.
   Do **not** hydrate `nocache_content` (**D4**). Add `entity_ids` to the existing
   `Calling _store_prompt_blocks: [...]` debug line as `n_ids=%s` → `len(entity_ids or [])`.
3. `_store_response_block` (line ~1539): add `entity_ids: Optional[List[str]] = None,` after `debug` (keyword-only,
   after the existing `*`). As the first statement after the opening debug log, add
   `response_text = hydrate_entity_labels(response_text, entity_ids)` with the comment
   `# AST-2029: hash + stored row both use the hydrated text`. This must run **before** the `content_hash` line.
4. In `do_task`, immediately after `_should_store = store_agent_data and batch_id and entity_type`
   (line ~2265), add the id list once (**D3**):
   ```python
   # AST-2029: real ids for stored labels — every batch entity must carry one, else store positional text
   _ents = (ctx or {}).get("batch_entities") or []
   _id_key = "company_id" if entity_type == "company" else "astral_job_id"
   _store_ids = [str(e.get(_id_key) or "") if isinstance(e, dict) else "" for e in _ents]
   _store_ids = _store_ids if _store_ids and all(_store_ids) else None
   ```
5. In `do_task`, pass `entity_ids=_store_ids` to the `_store_prompt_blocks` call (line ~2270, add after
   `entity_id=…`) and to **every** `asyncio.to_thread(_store_response_block, …)` call in `do_task`:
   current lines ~2366, 2421, 2453, 2476, 2498, 2521, 2544, 2597, 2629, 2655, 2677, 2697, 2741 (13 failure
   or validation paths plus the success store, 14 calls in total — `rg -n "to_thread\(_store_response_block" src/core/agent.py`
   inside `do_task` must list each with `entity_ids=_store_ids`). Add it as a keyword next to `debug=debug`.
   Do **not** change `_store_prompt_blocks` / `_store_response_block` calls in `run_adhoc_workbench_test`
   (lines ~3235, 3324, 3341).
6. Do **not** change `_assemble_blocks_seven_segment`, `_send_to_server`, or what is passed to them. The
   wire stays positional by construction, because hydration only happens inside the two store helpers.
7. Compile and lint: `python -m py_compile src/utils/formatting.py src/core/agent.py` and the repo
   linter on both files. Then confirm `git diff origin/dev -- src/ui/api/ src/data/` is empty (AC4).

## Execution contract

Run the steps in order, and don't add files beyond **Files Changed**. If a line reference
has drifted, find it by the quoted code. If the quoted code itself is gone or different,
stop and post `🛑 Stage N blocked: …` on [AST-2028](https://linear.app/astralcareermatch/issue/AST-2028).
One commit per stage (`code(AST-2029): …`), published to the publish ref.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-2029
**Overall:** APPROVED
**Corpus:** 7dcc6f40d09a317028a72f0c5b31e80bcf9cdc1e (canon/ tree at publish tip)
**Publish ref:** a010cb8fe3907488843462a04244aa1ed4b966ec

## Canon scores
patt.entity.batch-processing | A |
stat.logging.debug | B |

## Traceability
1→Stage 3 (wire unhydrated, live NO_CACHE + RESPONSE stored with ids); 2→Stages 1+3 (`[index=NNN]` → `[entity_id=…]`); 3→Stages 1+3 (`NNN|` on failure RESPONSE); 4→Explicit scope gate + Stage 3 §7 (`src/ui/api/`, `src/data/` untouched).

## Findings
- **acceptable** | Stage 3 §5 call-site inventory | Plan cites “14” `to_thread(_store_response_block` sites inside `do_task`; current tree has **13** (lines ~2366–2741). Stage already requires `rg` verification before land — count typo only.
- **acceptable** | Decisions D6 | Documented false-positive risk on `NNN:`/`NNN|` inside row text; aligned with parent “no heuristics without Susan” and explicit non-mitigation.

context_tokens≈22000

## Review

- **Branch:** `origin/sub/AST-2028/AST-2029-store-agent-data-with-entity-ids`
- **Build commits:** `ae2579970` (Stage 1: `hydrate_entity_labels`), `37fa489cf` (Stage 2: `split_entity_segments`), `8f30a32d6` (Stage 3: `entity_ids` on `_store_prompt_blocks` / `_store_response_block`, ids computed once in `do_task`, passed to the prompt store + all 13 `to_thread(_store_response_block` sites; Ad Hoc stores untouched).
- **Build notes:** `py_compile` clean on both files. `ruff` before/after: the only new findings are `UP006`/`UP045` on the new `Optional[List[str]]` / `Dict[str, str]` annotations, matching each file's existing typing style. `re.M` spelled `re.MULTILINE` (FURB167) — same flag as the plan's code. `git diff origin/dev -- src/ui/api/ src/data/` is empty (AC4). Through the real helpers with `save_agent_data` stubbed: live `000:/001:/002:` with ids `[A,B,C]` stores `[entity_id=A|B|C]:` with no `000:`, while `_assemble_blocks_seven_segment` user blocks still carry `000:` and no `entity_id` (AC1); a failure body with `000|DTA5\n001|GCA4` stores `[entity_id=A]|DTA5` / `[entity_id=B]|GCA4` (AC3).
- **Existing tests:** `tests/component/utils/test_formatting.py` + `tests/component/core/test_agent.py` → 40 failed / 444 passed, and the identical 40 fail on pure `origin/dev` code (failure-list diff empty). Pre-existing, not introduced here.
- **Deviation:** none (call-site count is 13 per Joan; `re.MULTILINE` vs `re.M` is lint-only).
- **For QA:** AC2 (`[index=000]:` → `[entity_id=A]:`) is covered by the hydrate regex but was only exercised in the helper, not through `do_task`. A JSON-enveloped failure (`{"agent_payload":"000|…\n001|…"}`) hydrates in place; its last split segment keeps the envelope's closing `"}` (D7).

## Radia review

[code-rubric]
**Ticket:** AST-2029
**Publish ref:** b69f8dbe6ffcb0e9d87842936dcbfb6117e04ce5
**Corpus:** 2344ae3265b15125a8f4a655946fcfe66b3e1def
**Overall:** DISCUSS

## Canon scores
patt.entity.batch-processing | A |
stat.logging.debug | C | 2 | `hydrate_entity_labels` logs label count, not full `out`

## Column diff vs plan stage
stat.logging.debug — Joan **B**, code review **C** (plan Stage 1 specifies count-only `Response from hydrate_entity_labels`; statute wants the full return string)

## Frame diff
(none)

## Findings

### fix-now
(none)

### discuss
- **discuss** | `src/utils/formatting.py` — `hydrate_entity_labels` | `stat.logging.debug` callee-out contract is `Response from <fn>: <full return>` with no truncation; the helper logs `n` labels and `len(entity_ids)` instead of hydrated `out`. @susan: Is count-only debug acceptable for multi-megabyte stored blocks, or should resolve-child log the full string per statute? **Default:** resolve-child changes the line to `logger.debug("Response from hydrate_entity_labels: %s", out)`.

### advisory
- **advisory** | sibling test carry | Three-dot diff includes many `tests/**` and `docs/test-bible/**` paths outside AST-2029 product scope (e.g. `test_telescope.py`, `test_gazer.py`, `test_consult.py`, `test_dispatcher.py`, `test_config.py`, `test_timesheets.py`, `test_openrouter.py`, `test_api_admin.py`, `test_repo_admin_json.py`, related bible rows). Expected `merge-tests` carry; product diff is only `src/utils/formatting.py` and `src/core/agent.py`.
- **advisory** | `tests/component/core/test_agent_ast2029.py` | D2 JSON-enveloped failure (`{"agent_payload":"000|…\\n001|…"}`) is covered in `TestAst2029HydrateEntityLabels` but not through `do_task`; storage path still calls the same helper on failure bodies.
- **advisory** | `src/core/agent.py` ~3251–3363 | Ad Hoc workbench `_store_prompt_blocks` / `_store_response_block` correctly omit `entity_ids` (positional storage per plan boundaries).

## What's solid
- Plan Stages 1–3 land as specified: `hydrate_entity_labels` / `split_entity_segments` in `formatting.py`; `_store_ids` from `batch_entities` with D3 all-or-nothing; live `NO_CACHE` only hydrated (D4); all 13 `do_task` `_store_response_block` paths pass `entity_ids=_store_ids`; hash uses hydrated RESPONSE text.
- AC4: `git diff origin/dev...origin/sub/AST-2028/AST-2029-store-agent-data-with-entity-ids -- src/ui/api/ src/data/` is empty.
- `test_agent_ast2029.py` pins AC1–AC3, company `company_id`, D3 guards, wire-vs-stored separation, and hash-over-hydrated-text; formatting tests cover D2 boundaries and split (D7).
- `run_adhoc_workbench_test` store paths unchanged.

## Recommended actions (downstream only — not executed in this session)
- Chuckles: append this artifact to `docs/features/agent/ast-2029-store-agent-data-with-real-entity-ids.md`, commit `docs(AST-2029): Radia review — findings`, post slim upshot `--as radia`, move to **Review Posted**.
- If Susan accepts **Default** on logging: Ada via **resolve-child** — one-line debug fix in `hydrate_entity_labels`.
- Optional (no canon gate): add `do_task` JSON-envelope failure storage test if sibling UAT wants end-to-end proof beyond helper tests.

context_tokens≈28000
