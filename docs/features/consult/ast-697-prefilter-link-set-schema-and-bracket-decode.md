# Prefilter link_set schema example and bracket decode (Prefilter output with links)

**Linear:** [AST-697](https://linear.app/astralcareermatch/issue/AST-697/prefilter-link-set-schema-and-bracket-decode-prefilter-output-with-links)  
**Parent:** [AST-696](https://linear.app/astralcareermatch/issue/AST-696/prefilter-output-with-links)  
**Publish ref:** `origin/sub/AST-696/AST-697-prefilter-link-set-schema-and-bracket-decode`  
**Summary:** Production prefilter runs lose link metadata because the rendered **{$RESPONSE_SCHEMA}** example shows a grades-only compact encoded line and `_decode_payload` ignores positional bracket **link_set** tails (`[13]`, `[3,6,19]`) on encoded rows. This ticket fixes the prompt contract and teaches the decode path to map those tails into `possible_job_links` and `culture_links_to_explore` without regressing **AST-603** alternate shapes.

**Root cause (current code):**

1. **`stringify_response_schema("prefilter_company")`** — `output_type == "grades_encoded_prefilter_links"` falls through the generic `_encoded` branch and emits `"000|ERC2|MEA3|PGA2"` (no link tails). Only types with `"_meta"` in the name get a meta example; prefilter links use a dedicated output type without `_meta` in the string.
2. **`_decode_payload`** — for `grades_encoded_prefilter_links`, meta fields after grade segments are parsed only when prefixed with **`JOB:`** or **`CULT:`**. Bare bracket tails like `[59,60]` land in `meta` but are never mapped to job dict keys.
3. **Roster persist** — `prefilter_company` already writes `possible_job_links` / `culture_links_to_explore` from flattened decode output (**AST-603**). No roster change expected once decode is fixed.

**Out of scope:** Rubric vector definitions, **AST-507** pass/fail/score semantics, UI, new company states, other encoded consult tasks (qualify/evaluate/DO/GET/LIKE).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `stringify_response_schema`: bracket **link_set** example for `grades_encoded_prefilter_links`; update `output_types["grades_encoded_prefilter_links"].payload_instructions` to document positional bracket tails as canonical | utils |
| `src/core/consult.py` | New `_apply_prefilter_encoded_link_meta(job, meta)` helper — positional bracket/comma tails + existing `JOB:`/`CULT:` prefixes via `_parse_link_index_field` | core |
| `src/core/agent.py` | `_decode_payload`: call shared helper for `grades_encoded_prefilter_links` instead of prefix-only loop | core |

Betty adds manifest rows in **astral-tests** for bracket decode + schema example assertions — engineer does **not** edit `tests/` or the bible.

---

## Stage 1: Prompt schema example and output-type instructions

**Done when:** Resolved **{$RESPONSE_SCHEMA}** for **prefilter_company** shows Susan's canonical compact encoded example with two bracket **link_set** tails; `{$OUTPUT_INSTRUCTIONS}` documents the same shape.

1. In `src/utils/config.py`, function **`stringify_response_schema`**, inside the `if "_encoded" in output_type:` block, add an **`elif output_type == "grades_encoded_prefilter_links":`** branch **before** the `elif "_meta" in output_type:` branch:
   - Set `example = "000|ERC2|MEA3|PGA2|[13]|[3,6,19]"`.
   - Do **not** change examples for `grades_encoded_notes`, `grades_encoded` + `_meta`, or the generic grades-only fallback used by other encoded tasks.

2. In `src/utils/config.py`, block **`ASTRAL_CONFIG["output_types"]["grades_encoded_prefilter_links"]["payload_instructions"]`**:
   - After the grade-segment paragraph, add explicit **link_set** documentation: after all grade segments, append **two optional positional bracket fields** — first tail → possible job page indices (1–5 ints from the enumerated nav list), second tail → culture link indices (1–5 ints). Use Susan's canonical example line: `000|ERC2|MEA3|PGA2|[13]|[3,6,19]`.
   - Keep existing **`JOB:<indices>`** / **`CULT:<indices>`** prefix form and JSON keys `possible_job_links` / `culture_links_to_explore` as alternate shapes software still accepts (**AST-603** repro).
   - Replace the current example-only line `000|RCA3|MPB3|USA3|JOB:59,60|CULT:51,46,53,50,45` with **both** examples: bracket canonical first, then prefixed alternate: `000|RCA3|MPB3|USA3|[59,60]|[51,46,53]` and `000|RCA3|MPB3|USA3|JOB:59,60|CULT:51,46,53`.

   ⚠️ **Decision:** Bracket positional tails are the **primary** documented shape (Susan's UAT expectation); prefixed tails remain supported for models that already emit **AST-603** format.

3. Manual verification (no test edits in this stage): in a Python shell on the epic worktree, run:
   ```python
   import json
   from src.utils.config import stringify_response_schema
   env = json.loads(stringify_response_schema("prefilter_company"))
   assert env["agent_payload"] == "000|ERC2|MEA3|PGA2|[13]|[3,6,19]"
   ```

---

## Stage 2: Bracket link_set decode in `_decode_payload`

**Done when:** Compact encoded `agent_payload` lines with bracket tails decode to the correct link lists; existing `JOB:`/`CULT:` tails unchanged; grades-only lines still decode without error.

1. In `src/core/consult.py`, add module-level helper **`_apply_prefilter_encoded_link_meta(job: dict, meta: list[str]) -> None`** immediately after **`_parse_link_index_field`** (reuse existing parser — it already handles `[7]`, `[3,6,19]`, comma lists, and `JOB:`/`CULT:` prefixes):
   - Initialize empty lists `possible: list[int] = []`, `culture: list[int] = []`, and `positional: list[str] = []`.
   - For each string `m` in `meta` (preserve order):
     - If `re.match(r"^JOB:", m, re.I)`: extend `possible` with `_parse_link_index_field(m)`; **continue**.
     - If `re.match(r"^CULT:", m, re.I)`: extend `culture` with `_parse_link_index_field(m)`; **continue**.
     - Else: append `m` to `positional`.
   - **Positional tails** (no prefix): if `positional` is non-empty and `possible` is still empty, set `possible = _parse_link_index_field(positional[0])`.
   - If `len(positional) > 1`, for each `lf` in `positional[1:]`, extend `culture` with `_parse_link_index_field(lf)`.
   - If `possible`: `job["possible_job_links"] = possible`.
   - If `culture`: `job["culture_links_to_explore"] = culture`.
   - Empty bracket tails (`[]`) produce no keys on `job` (same as absent tails) — roster already normalizes with `or []`.

   ⚠️ **Decision:** Prefixed fields take precedence over positional mapping when both appear on one line (e.g. `JOB:16|[51,46]` → job links from prefix; second positional field still maps to culture). Matches **AST-603** `_job_from_letter_pipe` ordering (first link field → job, rest → culture).

2. In `src/core/agent.py`, function **`_decode_payload`**, replace the `grades_encoded_prefilter_links` meta loop (the block that only checks `^JOB:` / `^CULT:`) with:
   ```python
   from src.core.consult import _apply_prefilter_encoded_link_meta
   _apply_prefilter_encoded_link_meta(job, meta)
   ```
   Do **not** change meta handling for other `with_meta` output types (`grades_encoded_meta`, etc.).

3. Manual verification (no test edits in this stage): in a Python shell with a one-company batch entity in ctx:
   ```python
   from src.core.agent import _decode_payload
   ctx = {"batch_entities": [{"astral_job_id": "acme"}]}
   ot = "grades_encoded_prefilter_links"

   j1 = _decode_payload("prefilter_company", ot, "000|ERC2|MEA3|PGA2|[13]|[3,6,19]", ctx)["jobs"][0]
   assert j1["possible_job_links"] == [13]
   assert j1["culture_links_to_explore"] == [3, 6, 19]

   j2 = _decode_payload("prefilter_company", ot, "000|RCA3|MPB3|USA3|[59,60]|[51,46,53]", ctx)["jobs"][0]
   assert j2["possible_job_links"] == [59, 60]
   assert j2["culture_links_to_explore"] == [51, 46, 53]

   j3 = _decode_payload("prefilter_company", ot, "000|RCA3|MPB3|USA3|JOB:16|CULT:38,3,27", ctx)["jobs"][0]
   assert j3["possible_job_links"] == [16]
   assert j3["culture_links_to_explore"] == [38, 3, 27]

   j4 = _decode_payload("prefilter_company", ot, "000|RCA3|MPB3|USA3", ctx)["jobs"][0]
   assert "possible_job_links" not in j4
   assert "culture_links_to_explore" not in j4
   ```

4. End-to-end via normalizer (confirms **AST-603** encoded path):
   ```python
   from src.core.consult import _normalize_rubric_task_response
   from src.utils.config import TASK_CONFIG
   # reuse _ast603_prefilter_ctx() rubric width (3 vectors) from test_agent fixtures conceptually:
   ctx = {"batch_entities": [{"astral_job_id": "acme"}], "candidate_data": {"artifacts": {"company_prefilter": [
       {"code": "RC", "label": "Reality Check"}, {"code": "MP", "label": "Mission & Product"},
       {"code": "US", "label": "US Presence"}]}}}
   tc = TASK_CONFIG["prefilter_company"]
   out = _normalize_rubric_task_response("prefilter_company", tc,
       "000|RCA3|MPB3|USA3|[59,60]|[51,46,53]", ctx)
   job = out["jobs"][0]
   assert job["possible_job_links"] == [59, 60]
   assert job["culture_links_to_explore"] == [51, 46, 53]
   ```

5. **Roster persist (verify only — no code change unless manual check fails):** Read `prefilter_company` in `src/core/roster.py` — confirm lines that set `data_to_save["possible_job_links"]` and `culture_links_to_explore` from `flat.get(...)` are unchanged. If manual decode works but persist still drops links, stop with 🛑 comment on **AST-696** citing the exact gap — do not improvise roster changes outside this plan.

6. Before publish, run component tests Betty will extend (should stay green — no product regressions):
   ```bash
   ./scripts/testing/run_component_tests.sh \
     tests/component/core/test_agent.py \
     tests/component/core/test_roster.py \
     tests/component/utils/test_config.py
   ```

---

## Self-Assessment

**Scope:** `Single-Component` — Two core files plus config prompt/decode strings; no dispatcher, UI, or roster state machine changes unless Stage 2 step 5 reveals a persist bug.

**Conf:** `high` — **AST-603** already built link parsing helpers and prefilter persist; this ticket closes a known gap (schema example + positional bracket tails in `_decode_payload`) with a small shared helper.

**Risk:** `Medium` — `_decode_payload` is on the hot path for all rubric encoded prefilter runs; incorrect positional mapping would drop or mis-assign link indices, but grades-only responses and prefixed tails must remain unchanged per AC #4 and #6.

---

## Self-review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Single `_apply_prefilter_encoded_link_meta` in `consult.py`; `_decode_payload` delegates instead of duplicating prefix/bracket logic. |
| §2.1 Config | Schema example and output-type instructions live in `config.py`; no inline magic strings in core beyond decode. |
| §2.4 Batch | No change to claim/clear; `batch_entities` / ctx unchanged. |
| §2.6 State machine | Transitions unchanged; link fields are data persisted on existing pass/fail paths. |
| §3.3 Imports | `agent` → `consult` for helper (existing pattern from **AST-603**). |
| §3.5 Naming | Keys stay `possible_job_links` / `culture_links_to_explore`. |

No `conf-!!-NONE` conflicts.

---

## Execution contract (developer)

- Execute stages in order; **one commit per stage** on **`astral-AST-696`**, then publish each commit to **`origin/sub/AST-696/AST-697-prefilter-link-set-schema-and-bracket-decode`** via `git push origin HEAD:sub/AST-696/AST-697-prefilter-link-set-schema-and-bracket-decode` with **`--session astral-AST-696`** per build-child publish ritual.
- Do **not** add roster-only parse functions — bracket tolerance belongs in shared decode helper + existing `_normalize_rubric_task_response` → `_decode_payload` path.
- Do **not** edit `tests/`, `docs/ASTRAL_TEST_BIBLE.md`, or `docs/test-bible/**` — request Betty manifest for bracket tails + `stringify_response_schema("prefilter_company")` assertion.
- If a repro payload category from **AST-603** fails after Stage 2, stop with 🛑 comment on **AST-696** (parent) citing payload line and failing assertion — do not broaden scope to other tasks.

---

## Review

**Branch:** `origin/sub/AST-696/AST-697-prefilter-link-set-schema-and-bracket-decode`  
**Build tip:** `12f848d` (product + Betty manifest merge)

---

## Radia review (review-child 2026-06-16)

**Diff:** `origin/dev...origin/sub/AST-696/AST-697-prefilter-link-set-schema-and-bracket-decode`

### What's solid

- **Plan fidelity:** Stage 1 (`stringify_response_schema` bracket example + `payload_instructions`) and Stage 2 (`_apply_prefilter_encoded_link_meta` + `_decode_payload` delegate) match the combined plan; roster untouched as scoped.
- **§1.3 DRY:** Link parsing stays in `consult._parse_link_index_field`; encoded decode delegates via one helper instead of duplicating prefix/bracket logic in `agent.py`.
- **§2.1 config:** Canonical example `000|ERC2|MEA3|PGA2|[13]|[3,6,19]` and positional-tail docs live in `config.py` — verified in shell against `stringify_response_schema("prefilter_company")`.
- **§3.3 layer compliance:** `agent` → `consult` lazy import matches existing `_normalize_rubric_task_response` pattern (line ~1845); no UI/external/data layer bends.
- **Regression coverage:** Manifest rows cover Susan canonical brackets, RCA/MPB/USA brackets, `JOB:`/`CULT:` prefix tails, grades-only omission, and normalizer path via `TestAst603RubricNormalize::test_lovable_encoded_line_with_bracket_tails`.
- **§5f / §5g:** Not applicable — no new `debug=` surfaces or LLM external changes.

### Issues

| Severity | Item | Location |
|----------|------|----------|
| **discuss** | Plan decision text says `JOB:16\|[51,46]` should map the bracket tail to culture when a prefix fills job links, but `_apply_prefilter_encoded_link_meta` only reads culture from `positional[1:]` when `len(positional) > 1`, so a lone bracket tail after `JOB:` is still dropped. Same as pre-697 prefix-only `_decode_payload` (not a regression); `_job_from_letter_pipe` would assign it to culture. Confirm whether mixed encoded lines need parity or bracket-after-prefix remains out of scope. | `src/core/consult.py` `_apply_prefilter_encoded_link_meta` |
| **advisory** | `_apply_prefilter_encoded_link_meta` inlines `re.match(r"^JOB:"…)` / `^CULT:` while `_LINK_PREFIX_RE` sits one function above — minor duplication only. | `src/core/consult.py` |

### Recommended actions

| Action | Owner |
|--------|-------|
| Resolve **discuss** on mixed `JOB:` + lone bracket tail (parity vs out-of-scope) before UAT if production models emit that shape | Susan / Ada |
| None blocking for merge | — |

**Counts:** 0 fix-now · 1 discuss · 1 advisory

— Radia
