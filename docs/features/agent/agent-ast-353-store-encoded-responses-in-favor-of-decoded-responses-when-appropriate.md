# AST-353 — Store Encoded Responses in Favor of Decoded Responses When Appropriate

**Component:** agent  
**Children:** — (single ticket)  
**Linear archived:** AST-353 2026-06-03

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-04-24 15:40 | AST-353 | chore | `25c02422a` | append review stub |
| 2026-04-24 15:40 | AST-353 | feat | `69ff0494a` | store decoded response in agent_data on success, raw on failure |
| 2026-04-24 16:39 | AST-353 | chore | `6c4ee3d23` | add encoded agent_data migration script and document block_data  |

## Epic — AST-353

_Archived: 2026-06-03 · Linear URL: https://linear.app/astralcareermatch/issue/AST-353/store-encoded-responses-in-favor-of-decoded-responses-when-appropriate · Status at archive: Done · Project: Astral Agent · Assignee: susan · Priority / estimate: Urgent / —_

#### Description

I believe we currently save agent_data before any validation.  I want instead to store the parsed, decoded and validated data in the success case, and in ANY failure case, store the raw response.

That way, the data in agent_data is only ever fully hydrated content for core component use, with no need for additional decoding downstream.

#### Comments

_No comments._

---

### Plan


#### Problem Statement

In `do_task` (agent.py), the RESPONSE block is stored in `agent_data` **before** validation and
decoding. This means the `block_data` column always contains the raw, encoded API text — even
on a successful run where a fully decoded, validated result is available. Downstream readers
(UI, audit tooling) must re-decode to use the data, which contradicts the intent of the table.

**Goal:**
- **Success path:** store the decoded, validated `parsed_response` (i.e., the final value of
  `result["parsed_response"]` after envelope-unwrapping and encoded-payload decoding).
- **Any failure path** (schema fail, grade fail, decode fail, post-decode schema fail): store
  the raw API response text, so the failure is always auditable.

> The API-level failure path (where `send_to_anthropic` returns `success: False`) currently
> stores nothing in `agent_data`; this plan leaves that unchanged — there is no Anthropic
> response text to store when the call itself failed.

---

#### Step 1 — Restructure `do_task` in `agent.py`

**File:** `src/core/agent.py` (modify — `do_task` function only)

**What changes:**

Currently `_store_response_block` is called once at line 530, immediately after a successful API
call and before any validation or decoding. The block gets raw API text. The `agent_ref` is then
built at lines 557–573, before payload unwrapping or encoded-payload decoding.

**New execution order inside `do_task` (success branch only):**
```
1.  Extract raw_text from api_response — store in variable, do NOT persist yet.
2.  Validate response schema → FAIL: store raw_text, return {success: False}.
3.  Validate grades (if vectors configured) → FAIL: store raw_text, return {success: False}.
4.  Unwrap agent_payload from envelope (lines 577–582, unchanged logic).
5.  Decode encoded payload if output_type has "_encoded" → FAIL: store raw_text, return.
6.  Post-decode schema validation → FAIL: store raw_text, return {success: False}.
7.  SUCCESS: serialize parsed as JSON string (if dict/list) or use as-is (if str).
    Call _store_response_block with decoded content, append {type, id} to prompt_blocks.
8.  Build agent_ref with prompt_blocks (now includes RESPONSE block with decoded content).
9.  append_agent_response, _store_agent_response, return result.
```

**Concrete changes:**

- **Remove** the current `_store_response_block` block at lines 524–533 (stored before validation).
- **Add** `raw_text` extraction immediately after the API-call section (same location, just
  capture the value without storing it).
- **At each failure return** (schema, grades, decode, post-decode-schema): add a guard:
```python
  if _should_store and raw_text:
      _store_response_block(entity_type, task_key, batch_id, raw_text)
```
  No `prompt_blocks.append` needed — failures return before `agent_ref` is built, so the
  block is auditable in `agent_data` but not referenced from `agent_responses`.
- **Before building `agent_ref`** (currently lines 557–573, relocated to after decode step):
```python
  if _should_store and raw_text:
      store_content = json.dumps(parsed) if isinstance(parsed, (dict, list)) else (parsed or raw_text)
      resp_id = _store_response_block(entity_type, task_key, batch_id, store_content)
      prompt_blocks.append({"type": "RESPONSE", "id": resp_id})
```
  Then build `agent_ref`, `append_agent_response`, etc. — unchanged logic.
- **Update** the `_store_response_block` docstring: "Store the API response as a RESPONSE block.
  On success, block_data is the decoded/validated payload; on failure, it is the raw API text."

**Affected functions:** `do_task` and the docstring of `_store_response_block`. No other
functions in `agent.py` change. No other files change.

---

#### Trade-offs and Flags

| Decision | Notes |
|---|---|
| Failure paths don't link RESPONSE block into `agent_responses` | Acceptable — failures don't produce an `agent_ref`. The raw block is still in `agent_data` and queryable by `batch_id`. |
| Decoded content stored as `json.dumps(parsed)` | Consistent with how callers read it: `json.loads(block_data)` or display as text. |
| `agent_ref` build moves to after decoding | For encoded tasks, this runs ~milliseconds later. No functional impact. |
| API-level failures still store nothing | No raw text available when Anthropic call itself failed. Out of scope for this ticket. |

---

### Review

**Commit:** `69ff049`
**Branch:** `dev`

### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| + unplanned | `scripts/migrate_encoded_agent_data.py` | — | `6c4ee3d23` |
| + unplanned | `src/core/agent.py` | — | `69ff0494a` |
