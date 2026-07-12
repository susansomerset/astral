# AST-880 — Encoded A–F link-type vet for inflow discovery

**Linear:** [AST-880](https://linear.app/astralcareermatch/issue/AST-880/encoded-a-f-link-type-vet-for-inflow-discovery-vet-inflow-discovery)  
**Parent:** [AST-879](https://linear.app/astralcareermatch/issue/AST-879/vet-inflow-discovery-prompt-redraft)  
**Publish ref:** `origin/sub/AST-879/AST-880-encoded-af-link-type-vet`

Redraft `vet_inflow_discovery` so each discovery hit is graded with an A–F link-type Result Finding rubric, returned as a compact encoded `agent_payload` (one line per hit), always carrying a company homepage URL (including on F). Decode maps grades to company outcomes: A/B/C/D → `WEBSITE_FOUND` with website recorded; F → `VET_FAILED`. Update Admin Task Prompt (repo JSON + local DB migration) so UAT sees the new contract. Mechanical-only scope preserved (no candidate-fit). Debug when `debug=True` shows per-hit grade, website, and recorded state.

Does **not** change `inflow_discovery` CSE/ingest, short_name rename, prefilter/candidate-fit, `inflow_resolve_website` / `fetch_website` redesign, or new company states. Parent locked: F-only fail; website required on every grade including F; short_name rename out of scope.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `TASK_CONFIG["vet_inflow_discovery"]` → encoded output_type + `results` schema with `grade`/`website`; `INFLOW_CONFIG["vet"]` pass/fail grade sets; new `ASTRAL_CONFIG["output_types"]` entry | utils |
| `src/core/agent.py` | Decode branch for the new output_type → `{results: [{hit_index, grade, website, confidence}]}` | core |
| `src/core/roster.py` | `_apply_vet_inflow_result_row` grade→state; batch_entities normalize for decode; debug shows grade/website/state | core |
| `src/data/database.py` | AST-880 prompt migration seed + `_apply_ast880_*` (supersedes AST-776/822 prose) | data |
| `data/admin/agent_task.json` | Current `vet_inflow_discovery` `user_prompt` → A–F encoded contract | data |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Same bytes as updated `agent_task.json` (AST-786 identity) | docs |

**Out of scope:** `src/core/dispatcher.py`, `inflow_discovery` / ingest, `inflow_resolve_website`, `fetch_website`, Betty `tests/` / `docs/test-bible/**` (manifest only at qa-child), UI beyond Admin prompt text already stored in `agent_task`.

---

## Stage 1: Config — encoded vet contract + grade outcome sets

**Done when:** `TASK_CONFIG["vet_inflow_discovery"]` has `output_type` pointing at the new registry key, `response_schema.results` items use `grade` + required `website` (no `action`); `INFLOW_CONFIG["vet"]` exposes pass/fail grade frozensets; `ASTRAL_CONFIG["output_types"]` documents the line format; `python3 -c` import asserts those keys.

1. In `src/utils/config.py`, extend `INFLOW_CONFIG["vet"]` (keep existing keys) with:

   ```python
   "pass_grades": frozenset({"A", "B", "C", "D"}),
   "fail_grades": frozenset({"F"}),
   "grade_vector_code": "LT",  # fixed 2-char segment code in encoded lines
   ```

2. Replace `TASK_CONFIG["vet_inflow_discovery"]` body fields (keep `context_format`, `entity_type`, `requires_candidate_key`, `trigger_state`, `response_format: "json"`):

   - Add `"output_type": "grades_encoded_vet_meta"`.
   - Do **not** set `rubric_artifact` or `scored` (not a rubric-backed / scored consult task).
   - Set `response_schema` to:

     ```python
     "results": {
         "type": "list",
         "required": True,
         "items_schema": {
             "hit_index": {"type": "int", "required": True},
             "grade": {"type": "str", "required": True},
             "website": {"type": "str", "required": True},
             "confidence": {"type": "int", "required": False},
         },
     },
     ```

3. In `ASTRAL_CONFIG["output_types"]`, after `grades_encoded_meta`, add `"grades_encoded_vet_meta"` with `payload_instructions` that state exactly:

   - Outer envelope: top-level keys exactly `"agent_performance"` and `"agent_payload"`.
   - `agent_payload` is a single string of newline-separated lines (not a JSON `results[]`).
   - One line per input hit: `{pos}|LT{grade}{conf}|{website}`
     - `{pos}`: 0-based index, zero-padded to 3 digits (matches live-content `000`/`001`/…)
     - `LT`: fixed vector code (link-type)
     - `{grade}`: exactly one of `A` `B` `C` `D` `F`
     - `{conf}`: confidence digit `1`–`5` (use `5` when the page type is clear)
     - `{website}`: absolute company homepage URL — **required on every grade including F**
   - Example lines:

     ```
     000|LTA5|https://www.acme.com
     001|LTF5|https://www.otherco.com
     ```

⚠️ **Decision:** New output_type `grades_encoded_vet_meta` (not reuse of `grades_encoded_meta`) so decode returns `results[]` with `hit_index`/`grade`/`website` instead of job `jobs[]` + listing meta slots. Keeps prefilter/qualify decode paths untouched. Fixed code `LT` satisfies the existing 4-char `_GRADE_SEG` family without a rubric artifact.

4. Verify:

   ```bash
   python3 -c "
   from src.utils import config as c
   t = c.TASK_CONFIG['vet_inflow_discovery']
   assert t['output_type'] == 'grades_encoded_vet_meta'
   assert 'action' not in t['response_schema']['results']['items_schema']
   assert 'grade' in t['response_schema']['results']['items_schema']
   v = c.INFLOW_CONFIG['vet']
   assert v['pass_grades'] == frozenset({'A','B','C','D'})
   assert v['fail_grades'] == frozenset({'F'})
   assert 'grades_encoded_vet_meta' in c.ASTRAL_CONFIG['output_types']
   print('ok')
   "
   ```

---

## Stage 2: Decode — `grades_encoded_vet_meta` → `results[]`

**Done when:** `_decode_payload(..., "grades_encoded_vet_meta", …)` returns `{"results": […]}` with `hit_index`/`grade`/`website`/`confidence`; bad lines raise `ValueError` with `task_key` prefix; missing website or illegal grade fails the line.

1. In `src/core/agent.py` `_decode_payload`, after the existing `with_notes` / `with_meta` setup and **before** the job-oriented loop body that always builds `result_jobs`, branch when `output_type == "grades_encoded_vet_meta"`:

   - Require `batch_entities` length for pos bounds (same skip-on-OOR warning pattern as today).
   - For each non-empty line after `clean_encoded_agent_payload`:
     - Split on `|`; `pos = int(fields[0])`.
     - Require at least 3 fields: pos, grade segment, website.
     - Normalize grade segment with the same ASCII space/hyphen/colon strip used for `_GRADE_SEG`; require `_GRADE_SEG.match(norm)` and `norm[:2] == "LT"` (or compare to `INFLOW_CONFIG["vet"]["grade_vector_code"]` via a late import from config — prefer reading code from config once at function start).
     - `grade = norm[2]`, `confidence = int(norm[3])`; validate conf with existing non-X rules (`1`–`5`).
     - `website = "|".join(fields[2:]).strip()` (allow `|` inside URL only if present — prefer single field; strip).
     - If `website` empty → `raise ValueError(f"[{task_key}] missing website on vet line: {line!r}")`.
     - If `grade` not in `ASTRAL_CONFIG["valid_grades"]` or not in pass∪fail sets from `INFLOW_CONFIG["vet"]` → `raise ValueError(...)`.
     - Append `{"hit_index": pos, "grade": grade, "website": website, "confidence": confidence}`.
   - `return {"results": result_rows}` (do **not** build `jobs`).

2. Do **not** add `vet_inflow_discovery` to `_STRICT_ENCODED_BATCH_CONSULT_KEYS` unless a later stage discovers bare-line responses in UAT — leave the frozenset unchanged in this ticket.

3. Smoke (no DB):

   ```bash
   python3 -c "
   from src.core.agent import _decode_payload
   ctx = {'batch_entities': [{'astral_job_id': 'a'}, {'astral_job_id': 'b'}]}
   out = _decode_payload('vet_inflow_discovery', 'grades_encoded_vet_meta',
       '000|LTA5|https://a.example\n001|LTF4|https://b.example', ctx)
   assert out['results'][0]['grade']=='A' and out['results'][0]['website']=='https://a.example'
   assert out['results'][1]['grade']=='F' and out['results'][1]['hit_index']==1
   print('ok')
   "
   ```

⚠️ **Decision:** Website is validated at decode (schema `required: True` + empty-string reject) so Admin/response view and roster never see a graded row without a homepage string — including F.

---

## Stage 3: Roster — grade outcomes + batch_entities for decode

**Done when:** Single and batch vet paths pass `batch_entities` so `do_task` can decode; `_apply_vet_inflow_result_row` maps A/B/C/D → `WEBSITE_FOUND` + `update_company(company_website=…)`, F → `VET_FAILED` without writing `company_website`; debug per-hit lines include `grade`, `website`, and recorded state; unknown grade / missing website → no transition (error dict).

1. In `src/core/roster.py`, rewrite `_apply_vet_inflow_result_row` to read **`grade`** (not `action`):

   - `grade = (row.get("grade") or "").strip().upper()`
   - `website = (row.get("website") or "").strip()`
   - If not `website`: debug detail `grade=… missing website`; return `{success: False, state: None, error: "missing website"}`.
   - If `grade in cfg["fail_grades"]`: `transition_company_state(short_name, cfg["fail_state"])`; debug outcome `recorded VET_FAILED grade=F website=…` (include website in debug / detail only — **do not** `update_company` website on F).
   - Elif `grade in cfg["pass_grades"]`: `update_company(short_name, company_website=website)`; `transition_company_state(short_name, cfg["pass_state"])`; debug with grade + website + pass state.
   - Else: warning + `{success: False, error: f"unknown grade {grade!r}"}`.

2. In `vet_inflow_discovery_company`, before `do_task`, set:

   ```python
   task_ctx = {
       **(ctx or {}),
       "batch_entities": [{"astral_job_id": short_name, "short_name": short_name}],
       "batch_size": 1,
   }
   ```

   Pass `ctx=task_ctx` into `do_task`. Keep live_content header/body unchanged (AST-822 renumber already on stored blurb for single-hit).

3. In `vet_inflow_discovery_company_batch`, before `do_task`, normalize ready companies the same way prefilter does:

   ```python
   ready_for_decode = [
       {
           "astral_job_id": c.get("short_name") or "?",
           "short_name": c.get("short_name") or "?",
           "company_data": c.get("company_data") or {},
           "state": c.get("state"),
       }
       for c in ready
   ]
   ```

   Pass `batch_entities=ready_for_decode` and `batch_size=len(ready_for_decode)` in the `do_task` ctx. Keep `_renumber_vet_blurb_line` live content assembly unchanged.

4. Keep `hit_index` → company mapping: `index_by_hit[hi] = r` from `parsed["results"]` (decoded shape). No `action` field.

5. Confirm `consult.py` batch branch for `vet_inflow_discovery` still calls `vet_inflow_discovery_company_batch` — no consult change unless the ctx shape requires it (it should not).

⚠️ **Decision:** On F, website appears in decode + debug only; company row keeps empty `company_website` and `VET_FAILED`. Rejected discovery URL remains in `inflow_discovery_notes` so AST-776/775 dedupe still blocks re-ingest (AC #5).

---

## Stage 4: Prompt seed — DB migration + repo `agent_task.json`

**Done when:** Local DB open versions current `vet_inflow_discovery` `user_prompt` to the AST-880 seed when the AST-880 marker is absent; `data/admin/agent_task.json` and `docs/uat-fixtures/AST-756/expected-agent_task.json` are byte-identical and contain the A–F encoded rubric (no `action: slug|ignore`).

1. In `src/data/database.py`, after the AST-822 constants block, add:

   - `_AST880_VET_INFLOW_ENCODED_MARKER = "ENCODED A-F LINK-TYPE VET (AST-880)"`
   - `_AST880_VET_INFLOW_USER_PROMPT_SEED` — multiline string that includes the marker and states:

     - Live content: header `Discovery hit(s) (index|title|url|snippet)` plus `000|title|url|snippet` lines (multi-hit AST-822 behavior preserved).
     - **Result Finding** rubric (mechanical only):
       - **A** — hit URL is a company homepage
       - **B** — deeplink on a company site (e.g. product page)
       - **C** — company-hosted blog/post on that company's site
       - **D** — external to any one company but may still be worth parsing for a company pointer
       - **F** — unrelated / information-only / unlikely pointer (wiki, directories, news-only, BBB, job boards, social profiles, similar)
     - Forbidden: candidate-fit, industry preference, company quality, role match (later pipeline / prefilter for D).
     - Response: standard two-key envelope; `agent_payload` is newline-separated encoded lines — **not** JSON `results[]` of `action` objects.
     - Line format: `{pos}|LT{grade}{conf}|{website}` with website required on **every** grade including F.
     - One line per input hit; `pos` matches `000`→0, `001`→1, …

2. Add `_apply_ast880_vet_inflow_discovery_prompt_migration(conn)` mirroring `_apply_ast822_*`:

   - Load current `agent_task` row `task_key = 'vet_inflow_discovery' AND current = 1`.
   - If no row or `user_prompt` already contains `_AST880_VET_INFLOW_ENCODED_MARKER`, return.
   - Else version forward via `_save_agent_task_on_connection` with `_AST880_VET_INFLOW_USER_PROMPT_SEED` (preserve other prompt fields / `run_next` / `agent_id`; same agent_id fallback to `find_company_website` as AST-776/822).

3. Call `_apply_ast880_vet_inflow_discovery_prompt_migration(conn)` from `_ensure_agent_task_schema` **immediately after** `_apply_ast822_vet_inflow_discovery_prompt_migration(conn)` so AST-880 supersedes 776/822 prose on existing DBs.

4. Update the current (`"current": 1`) `vet_inflow_discovery` object in `data/admin/agent_task.json`: set `user_prompt` to the same seed text as `_AST880_VET_INFLOW_USER_PROMPT_SEED` (identical string). Leave other fields unchanged.

5. Copy that file over the fixture so they stay identical:

   ```bash
   cp data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json
   cmp -s data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json && echo identical
   ```

6. Compile:

   ```bash
   python3 -m py_compile src/utils/config.py src/core/agent.py src/core/roster.py src/data/database.py
   ```

⚠️ **Decision:** Repo JSON + DB migration both carry the new prompt — Admin UAT and fresh local DBs see the same contract. Marker-gated migration replaces AST-822 text even when the 822 marker is present (880 marker absent → rewrite).

---

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree, then publish to `origin/sub/AST-879/AST-880-encoded-af-link-type-vet`.
- Do not add files outside the table above.
- Do not edit `tests/` or `docs/test-bible/**`.
- On ambiguity or codebase drift → stop and comment on **AST-879** with the Stage N blocked template.

---

## Self-Assessment

**Scope:** Single-Component — `vet_inflow_discovery` config/decode/roster apply + prompt seed; no dispatcher or discovery ingest changes.

**Conf:** high — reuses AST-776/822 vet batch paths, prefilter `astral_job_id=short_name` decode trick, and established `output_types` / `_decode_payload` / agent_task migration patterns.

**Risk:** Medium — wrong grade→state mapping or dropping website-on-F validation would mis-route NEW companies or break Admin UAT of the encoded contract; decode bugs would fail the whole vet batch.

## Self-review vs ASTRAL_CODE_RULES

- **§1.3 DRY:** Shared `_apply_vet_inflow_result_row` stays the single outcome helper; decode specialization is one output_type branch.
- **§1.4 / §2.1:** Pass/fail grades and vector code live in `INFLOW_CONFIG["vet"]`; line-format instructions in `ASTRAL_CONFIG["output_types"]`; no inline magic grade sets in roster beyond reading config.
- **§1.5.1:** Debug continues to use `debug_index` / `debug_detail` with per-hit grade, website, recorded state when `debug=True`.
- **§2.4 / §2.6:** No new company states; transitions remain NEW → WEBSITE_FOUND | VET_FAILED via existing helpers.
- **§3.3:** `agent.py` may import config for vector code / grade sets; roster stays core→agent via `do_task` only.
- **§3.5:** Names stay `vet_inflow_discovery` / existing function names; new symbols use `ast880` / `grades_encoded_vet_meta` prefixes consistently.
)

---

## Build complete

- **Publish ref:** `origin/sub/AST-879/AST-880-encoded-af-link-type-vet`
- **Tip:** `7f1a642eb51e74be8d39845d9f50f16662ab85aa`
- **Stages:** config → decode → roster → prompt seed (4 `code(AST-880)` commits after plan)

---

## Radia review

**Diff:** `origin/dev...origin/sub/AST-879/AST-880-encoded-af-link-type-vet` @ `5fcb929`

### What’s solid

- Stages 1–4 match the plan: `grades_encoded_vet_meta` + `INFLOW_CONFIG["vet"]` pass/fail/`LT`; decode → `results[{hit_index, grade, website, confidence}]`; roster A/B/C/D → `WEBSITE_FOUND` (+ website) / F → `VET_FAILED` (website debug-only); AST-880 marker migration after AST-822; repo JSON ≡ UAT fixture ≡ seed.
- Grade sets and vector code live in config (§1.4 / §2.1); single `_apply_vet_inflow_result_row` outcome helper (§1.3); no new company states; transitions via existing helpers (§2.6).
- Debug: per-hit `debug_index` / `debug_detail` include grade + website + recorded state when `debug=True` (§1.5.1 / §5f).
- Boundaries held: no dispatcher / discovery ingest / `fetch_website` / UI; Betty tests + bible on publish-ref are expected post-qa.
- Self-Assessment Scope Single-Component matches footprint; Conf high still fits.

### Issues

None.

### Recommended actions

| Action | Item |
|--------|------|
| none (ship) | 0 fix-now · 0 discuss · 0 advisory |

**Outcome:** Clean — ready for `resolve-child`.
