<!-- linear-archive: AST-697 archived 2026-06-23 -->

## Linear archive (AST-697)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-697/prefilter-link-set-schema-example-and-bracket-decode-prefilter-output  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-696 — Prefilter output with links  
**Blocked by / blocks / related:** parent: AST-696

### Description

## What this implements

Fix the **prefilter_company** prompt contract and runtime parsing so compact encoded `agent_payload` responses include and decode **link_set** metadata — bracket tail indices for `possible_job_links` and `culture_links_to_explore`. Update the **{$RESPONSE_SCHEMA}** example and output-type payload instructions to show Susan's canonical shape `000|ERC2|MEA3|PGA2|[13]|[3,6,19]`. Teach `_decode_payload` (and shared helpers if needed) to map positional bracket **link_set** tails after grade segments into the decoded job row. Existing **AST-603** alternate response shapes must not regress.

## Acceptance criteria

1. Resolved **{$RESPONSE_SCHEMA}** for **prefilter_company** shows `agent_payload` example `000|ERC2|MEA3|PGA2|[13]|[3,6,19]` (or equivalent with bracket **link_set** tails documented in the same block) — not grades-only `000|ERC2|MEA3|PGA2`.
2. A model response `000|RCA3|MPB3|USA3|[59,60]|[51,46,53]` (matching live rubric vector count) decodes to `possible_job_links == [59, 60]` and `culture_links_to_explore == [51, 46, 53]`.
3. Susan's exact proposed example `000|ERC2|MEA3|PGA2|[13]|[3,6,19]` decodes with the same link field mapping (first tail → job links, second → culture links).
4. **AST-603** normalization paths still pass existing component tests — dict JSON, letter-pipe, `JOB:`/`CULT:` tails, and JSON-string payloads unchanged.
5. On prefilter pass (inflow or legacy watch path), `company_data` persisted after a successful run includes the parsed link lists when the model supplied them; UAT on a company with enumerated nav links shows non-empty `possible_job_links` when the model returns bracket tails.
6. Grades-only encoded responses (no link tails) still pass/fail prefilter and persist empty link lists — no new validation failures.

## Boundaries

* **prefilter_company only** — no unrelated encoded consult tasks unless a one-line shared-helper fix is required.
* No rubric vector redesign, no UI, no new company states.
* Sibling scope: none (single child epic).

## Notes for planning

* Hot files: `src/utils/config.py` (`stringify_response_schema`, `grades_encoded_prefilter_links` output type), `src/core/agent.py` (`_decode_payload` meta parsing), possibly `src/core/consult.py` (`_parse_link_index_field` reuse).
* Roster persist path already writes link fields when present — verify AC #5 but likely no roster changes if decode is fixed.
* Feature doc folder: `docs/features/consult/`.
* plan-child §3 maps **Astral Consult** → `docs/features/consult/`.

## Git branch (authoritative)

Per **orientation** § Branch law: parent `ftr/AST-696-prefilter-output-with-links`, child `sub/AST-696/<child-id>-prefilter-link-set-schema-and-bracket-decode`. Created at dispatch-parent.

### Comments

#### radia — 2026-06-16T02:42:13.739Z
### Radia review — `origin/dev...origin/sub/AST-696/AST-697-prefilter-link-set-schema-and-bracket-decode`

**Doc:** `docs/features/consult/ast-697-prefilter-link-set-schema-and-bracket-decode.md` @ `d30f25b`

**What's solid**
- Stage 1 + 2 match plan: bracket schema example + `payload_instructions` in `config.py`; `_apply_prefilter_encoded_link_meta` in `consult.py`; `_decode_payload` delegates. Roster unchanged.
- §1.3 DRY — single helper reuses `_parse_link_index_field`; no duplicated prefix/bracket logic in `agent.py`.
- §2.1 config — verified `stringify_response_schema("prefilter_company")` → `000|ERC2|MEA3|PGA2|[13]|[3,6,19]`.
- §3.3 — `agent`→`consult` lazy import matches existing pattern (~L1845); no layer violations.
- Manifest covers canonical brackets, RCA/MPB/USA tails, `JOB:`/`CULT:` prefix regression, grades-only omission, normalizer path.

**discuss:** Plan decision cites `JOB:16|[51,46]` → culture from bracket tail when prefix fills job links, but `_apply_prefilter_encoded_link_meta` only assigns culture from `positional[1:]` when `len(positional) > 1`, so a lone bracket after `JOB:` is still dropped (same as pre-697 encoded decode; `_job_from_letter_pipe` would map it). Confirm parity needed vs out-of-scope before UAT if models emit that mixed shape. (`src/core/consult.py`)

**advisory:** Inline `^JOB:`/`^CULT:` regex duplicates `_LINK_PREFIX_RE` one function above — cosmetic only.

**Counts:** 0 fix-now · 1 discuss · 1 advisory

#### betty — 2026-06-16T02:39:27.052Z
**Bible shasums** (`origin/sub/AST-696/AST-697-prefilter-link-set-schema-and-bracket-decode`):
- `docs/test-bible/core/consult.md` — `81027a61fe8487b0a62a2060c2f4fe9524707d3032da819d3bdf827d1e689eb8`
- `docs/test-bible/core/agent.md` — `38de54af8efcc7102fc6c03361e323d9315819fa994a2f0cac47bf58cb9a55a2`
- `docs/test-bible/utils/config.md` — `bfea9a1ec17e87f2c363ba940997e9ba93408fb4d2a1f920d0e75ffe4d95016e`

#### betty — 2026-06-16T02:39:17.256Z
**QA test manifest (AST-697)**

Publish: `origin/sub/AST-696/AST-697-prefilter-link-set-schema-and-bracket-decode` @ `12f848d` (`merge-tests(AST-697): origin/tests d5c47e8`)

1. **Schema example (new):** `tests/component/utils/test_config.py::TestStringifyResponseSchema::test_prefilter_company_schema_shows_bracket_link_set_tails` — `stringify_response_schema("prefilter_company")` → `000|ERC2|MEA3|PGA2|[13]|[3,6,19]`.

2. **Bracket decode via `_decode_payload` (new):** `tests/component/core/test_agent.py::TestAst697PrefilterBracketLinkDecode` — Susan canonical line, RCA/MPB/USA bracket tails, grades-only omits link keys.

3. **Consult normalizer bracket path (new):** `tests/component/core/test_agent.py::TestAst603RubricNormalize::test_lovable_encoded_line_with_bracket_tails` — `000|RCA3|MPB3|USA3|[59,60]|[51,46,53]` end-to-end.

4. **AST-603 prefix-tail regression (existing):** `tests/component/core/test_agent.py::TestAst603RubricNormalize::test_lovable_encoded_line_with_job_cult_tails` — `JOB:`/`CULT:` unchanged.

5. **Roster persist smoke (existing):** `tests/component/core/test_roster.py::TestAst603ConsultParityHydration` — hydration + link list persistence unchanged.

6. **Output type registry (existing):** `tests/component/utils/test_config.py::TestAst507EncodedPrefilterConfig::test_prefilter_company_grades_encoded`.

**Narrowed run:**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestStringifyResponseSchema::test_prefilter_company_schema_shows_bracket_link_set_tails \
  tests/component/core/test_agent.py::TestAst697PrefilterBracketLinkDecode \
  tests/component/core/test_agent.py::TestAst603RubricNormalize \
  tests/component/core/test_roster.py::TestAst603ConsultParityHydration \
  tests/component/utils/test_config.py::TestAst507EncodedPrefilterConfig::test_prefilter_company_grades_encoded
```

**Bible shasums (publish ref):**
- `docs/test-bible/core/consult.md` — see publish ref
- `docs/test-bible/core/agent.md` — see publish ref
- `docs/test-bible/utils/config.md` — see publish ref

— Betty

#### ada — 2026-06-16T02:30:47.450Z
Plan doc: https://github.com/susansomerset/astral/blob/sub/AST-696/AST-697-prefilter-link-set-schema-and-bracket-decode/docs/features/consult/ast-697-prefilter-link-set-schema-and-bracket-decode.md

**Self-assessment**
- **Scope:** Single-Component — config schema example + output instructions, shared link-meta helper in consult.py, one-line hook in agent._decode_payload; roster persist verified only.
- **Conf:** high — AST-603 already owns normalization and persist; this closes the known bracket-tail + schema-example gap with minimal surface area.
- **Risk:** Medium — wrong positional mapping would drop link indices on encoded prefilter runs; grades-only and JOB:/CULT: tails must stay green (AC #4/#6).

Two stages: (1) stringify_response_schema + output_types bracket link_set docs, (2) _apply_prefilter_encoded_link_meta + _decode_payload wiring. Betty manifest for bracket decode tests — no engineer test-tree edits.

#### ada — 2026-06-16T02:29:51.675Z
test

---

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

---

## Resolution (resolve-child 2026-06-16)

**Discuss (mixed `JOB:` + lone bracket tail):** Plan Stage 2 decision required `JOB:16|[51,46]` → job links from prefix, bracket tail → culture. `_apply_prefilter_encoded_link_meta` now routes all positional fields to culture when a prefix already filled `possible_job_links` (matches `_job_from_letter_pipe` ordering). No test-tree edits — Betty may extend manifest if Susan wants explicit coverage.

**Advisory (regex duplication):** Left inline `^JOB:`/`^CULT:` checks — distinct from `_LINK_PREFIX_RE` strip path; cosmetic only.

**Product commit:** `fix(AST-697): review feedback — mixed JOB prefix + bracket culture tail`

---

## Bug: AST-2138 — JOB:/CULT: link fields never decode as grade segments

**Linear:** [AST-2138](https://linear.app/astralcareermatch/issue/AST-2138) · **Mini-parent:** [AST-2136](https://linear.app/astralcareermatch/issue/AST-2136) (Prefilter errors) · **Publish ref:** `origin/sub/AST-2136/AST-2138-job-link-prefix-decode` · **Target:** `origin/ftr/AST-2136-job-link-prefix-decode`

**Canon (id-only; resolved by fix-board / make-fix):** ASTRAL_CODE_RULES §1.3 DRY (one link-prefix pattern, one grade-field classifier), §3.3 Imports (`consult` → `agent` at module level already exists; `agent` → `consult` stays lazy-only). `docs/canon-index.md` is not present in this worktree; neither ticket carries a Canon Scope list.

### As-is

The prefilter model emits the documented AST-603/AST-697 prefixed link tail, e.g. `000|RCA5|HEA5|MLA3|PFA5|SOA5|JOB:3|CULT:7,27`. In `_decode_payload` (`src/core/agent.py`, the `for f in fields[1:]` grade/meta split), every field has space, hyphen and colon stripped before the `_GRADE_SEG` test (AST-483). `JOB:3` becomes `JOB3`, which matches `^[A-Z]{2}[ABCDFX][0-5]$` as vector `JO`, grade `B`, confidence `3`. It lands in `grade_segs`, not `meta`. So `possible_job_links` is lost, and `_hydrate_response_jobs_grade_reasons` → `_lookup_rubric_reason_for_grade` raises `ValueError: No rubric criterion matching vector 'JO'`. Under AST-1828 routing the company goes to `ERROR_PREFILTER_COMPANY` (13 of 15 errors in Somerset batch `prefilter_company-1cdeac6e-…`). This hits every `JOB:0`–`JOB:5`. `JOB:6`+ and multi-digit/list forms fail `_GRADE_SEG` and decode correctly. `CULT:…` never matches because `L` is not a grade letter, but it is guarded the same way for symmetry. `_should_decode_as_encoded_line` (`src/core/consult.py`) has the same strip-then-match test, so a line whose only "grade-looking" field is `JOB:3` routes as encoded.

### To-be

A pipe field that starts with `JOB:` or `CULT:` (case-insensitive, exactly the AST-697 `_LINK_PREFIX_RE` contract) is always link meta and never a grade segment, whatever `n` is. `000|RCA5|HEA5|MLA3|PFA5|SOA5|JOB:3|CULT:7,27` decodes to the five rubric grades plus `possible_job_links == [3]` and `culture_links_to_explore == [7, 27]`. No `JO` vector reaches hydrate. Routing detection (`_should_decode_as_encoded_line`) and decoding (`_decode_payload`) use one shared classifier, so they agree on what a grade segment is.

### Repro

No DB needed. Fixture is a one-entity ctx on the current ftr tip (verified 2026-10-12 @ `a1af5cf6a`):

```python
from src.core.agent import _decode_payload
from src.core import consult
ctx = {"batch_entities": [{"company_id": "acme", "astral_job_id": "acme"}]}
ot = "grades_encoded_prefilter_links"

r = _decode_payload("prefilter_company", ot, "000|RCA5|HEA5|MLA3|PFA5|SOA5|JOB:3|CULT:7,27", ctx)
row = (r.get("companies") or r.get("jobs"))[0]
# As-is: grade vectors end [..., 'SO', 'JO']; possible_job_links None; culture [7, 27]
r = _decode_payload("prefilter_company", ot, "000|RCF5|HEX0|MLX0|PFX0|SOX0|JOB:1|CULT:[]", ctx)
# As-is: 'JO' grade; possible_job_links None
consult._should_decode_as_encoded_line("000|JOB:3|CULT:7")
# As-is: True (should be False — no real grade segment on the line)
```

Controls that already decode correctly and must stay so: `…|JOB:17|CULT:20,19,21` → `[17]` / `[20, 19, 21]`; `…|JOB:6|CULT:1` → `[6]` / `[1]`.

### Root cause

AST-483's normalization (strip `' -:'` before `_GRADE_SEG`) runs on **every** pipe field, link fields included. Once the colon is removed, a `JOB:<0-5>` link field is indistinguishable from a 4-char grade token. The link-prefix check only happens later, in `_apply_prefilter_encoded_link_meta`, and only on fields that already landed in `meta`. A field misclassified as a grade never gets there. `_should_decode_as_encoded_line` copies the same strip-then-match logic, so the two sites share the defect.

### Proposed change

1. **`src/core/agent.py`: shared pattern and classifier, placed directly below `_GRADE_SEG` (~L176).**
   - Move `_LINK_PREFIX_RE = re.compile(r"^(?:JOB|CULT):(.+)$", re.I)` here from `consult.py`, same pattern and same flags. Comment: AST-697 link-tail prefix; a field matching it is link meta, never a grade (AST-2138).
   - Add `_grade_segment(field: str) -> Optional[str]`:
     - If `_LINK_PREFIX_RE.match(field)` → return `None`.
     - Otherwise `norm = "".join(ch for ch in field if ch not in " -:")` (the AST-483 normalization, unchanged) and return `norm` if `_GRADE_SEG.match(norm)`, else `None`.
     - Docstring: normalized grade token or `None`; JOB:/CULT: link fields never count as grades (AST-2138); strip of space/hyphen/colon is AST-483.
2. **`src/core/agent.py`, `_decode_payload`: field-classification loop (current L370–376).** Replace the inline `norm` + `_GRADE_SEG.match(norm)` with:
   ```python
   for f in fields[1:]:
       seg = _grade_segment(f)
       if seg:
           grade_segs.append(seg)
       else:
           meta.append(f)
   ```
   Keep the existing AST-483 comment, moved onto `_grade_segment`. `meta` still receives the pipe-stripped original `f`, so `_apply_prefilter_encoded_link_meta` sees `JOB:3` exactly as before. Do **not** touch the `grades_encoded_vet_meta` branch (L286–287, single `LT` segment, no link fields).
3. **`src/core/consult.py`: share instead of redefine.**
   - Delete the module-level `_LINK_PREFIX_RE = re.compile(...)` line (L387). Keep `_ENCODED_LINE_RE` and the AST-603 comment.
   - Extend the existing module-level import `from src.core.agent import do_task` to `from src.core.agent import _LINK_PREFIX_RE, _grade_segment, do_task`. That makes `_parse_link_index_field` keep using the same name, now one definition. No cycle: `consult` → `agent` at module level already exists, and `agent` never imports `consult` at module level.
4. **`src/core/consult.py`, `_should_decode_as_encoded_line`.** Drop the lazy `from src.core.agent import _GRADE_SEG` and the inline `norm` strip. Inner test becomes `if _grade_segment(f): return True`. The AST-1996 "any line" loop and the leading-index skip stay unchanged.
5. **Manual verification (no test-tree edits):** the Repro block must give `possible_job_links == [3]`, `culture_links_to_explore == [7, 27]`, grade vectors `RC/HE/ML/PF/SO` only, for each of `JOB:0`…`JOB:5`. `JOB:1|CULT:[]` must give `[1]` with no `JO`. `_should_decode_as_encoded_line("000|JOB:3|CULT:7")` must be `False`, and `_should_decode_as_encoded_line("000|RCA3|MPB3|USA3|[59,60]|[51,46,53]")` must still be `True`. Then run `./scripts/testing/run_component_tests.sh tests/component/core/test_agent.py tests/component/core/test_consult.py tests/component/core/test_roster.py` to confirm it stays green.

⚠️ **Decision (link prefix wins):** the guard uses the exact `_LINK_PREFIX_RE` contract: literal `JOB:`/`CULT:` followed by at least one character. Suppose a candidate rubric ever had vector code `JO` (or `CU`) **and** the model prettified that grade with a colon as `JOB:3`. It would now go to meta, and the batch would take the existing `IncompleteGradeSetError` retry → error path instead of scoring. An unprettified `JOB3` is still a grade. The alternative, letting a rubric code `JO` override the prefix, would need `vector_labels` inside the classifier and is not justified by any observed payload.

⚠️ **Decision (no fuzzier prefix):** `JOB :3` and `JOB-3` are **not** treated as link prefixes. `_apply_prefilter_encoded_link_meta` would not parse them as links either, and widening the contract is a heuristic not approved here. Only the observed `JOB:<n>` / `CULT:<n>` shapes are in scope.

### Blast radius

- **`_decode_payload` callers:** every encoded task goes through the shared loop. For `with_meta` types, a `JOB:`/`CULT:` field now always reaches `meta` (the intended change). For grades-only types, such a field now becomes "unexpected trailing content" (`decode_failures`, AST-1996 retry) instead of a bogus 2-char grade. For `grades_encoded_notes`, it rejoins `notes` instead of becoming a grade. None of those tasks' prompts emit link prefixes, so no behavior change is expected in practice.
- **`_should_decode_as_encoded_line` → `_normalize_rubric_task_response` (consult L790):** lines whose only "grade" was `JOB:<0-5>` now fall through to the letter-pipe / other AST-603 normalizers. Real encoded lines are unaffected.
- **`_parse_link_index_field` / `_apply_prefilter_encoded_link_meta`:** same `_LINK_PREFIX_RE` object, now imported from `agent`. Behavior unchanged. Radia's AST-697 advisory (inline `^JOB:`/`^CULT:` in `_apply_prefilter_encoded_link_meta`) stays out of scope.
- **Tests that pin current behavior:** `test_agent.py` AST-483 normalization case (~L335), `TestAst603RubricNormalize::test_lovable_encoded_line_with_job_cult_tails`, `test_should_decode_as_encoded_line_routing` (~L708), `TestAst697PrefilterBracketLinkDecode`, `test_consult.py` ~L2374. These should stay green, but none reference `consult._LINK_PREFIX_RE` directly (grep 2026-10-12). Regression rows for `JOB:0`–`JOB:5` and `JOB:1|CULT:[]` are Betty's call (qa-fix).
- **Out of scope (per AST-2138 Boundaries):** the `SOFA5` malformed-segment errors (2 of 15), AST-1828 retry/error routing, and the rubric hydrate `ValueError`.

### What must still hold

- AST-697 AC #2/#3/#6: bracket tails `[13]|[3,6,19]` and `[59,60]|[51,46,53]` map positionally, and grades-only lines omit link keys.
- AST-603 / AST-697 AC #4: `JOB:16|CULT:38,3,27`, multi-digit `JOB:17`/`JOB:106`, and lists `JOB:2,13,17,21,28` decode exactly as today. The mixed `JOB:16|[51,46]` → culture rule (AST-697 resolution) is unchanged.
- AST-483: real grade tokens prettified with spaces, hyphens or colons (`RC A3`, `RC-A-3`, `RC:A3`) still decode as grades. `meta` keeps the pipe-stripped original text.
- AST-1996 / AST-2124 / AST-2126 / AST-2093 decode semantics (decode_failures, X0 storage, notes-only failure, index map) are untouched. Only the grade-vs-meta classification of link-prefixed fields changes.
- `_should_decode_as_encoded_line` routing examples: `0|A|B|A|[35]|[22,34,39,52,53]` → `False`, `000|RCA3|MPB3|USA3|[59,60]|[51,46,53]` → `True`, `A|B|A|15|13,16,14` → `False`.

### Joan fix-board — AST-2138

**Question:** Does the plan-fix patch require touching canon (statutes/patterns)?

**Read:** AST-2138 section in `docs/features/consult/ast-697-prefilter-link-set-schema-and-bracket-decode.md` on `origin/sub/AST-2136/AST-2138-job-link-prefix-decode` (commit `317409812`). Roster overlap: `astral.standards.dry-and-focused-functions`, `astral.layers.import-direction`, plus skim of agent decode statutes (`astral.agent.confidence-bounds` — classification-only change; X0 / decode-failure semantics explicitly preserved in **What must still hold**).

**Judgment:** **CANON: OK.** The fix is product code that **implements** the cited rules (one `_LINK_PREFIX_RE`, one `_grade_segment` shared by `_decode_payload` and `_should_decode_as_encoded_line`; `consult` → `agent` module import already allowed). It does not contradict an in-force statute or pattern, and it does not need a new statute carve-out: the “link prefix wins” / “no fuzzier prefix” bullets are bounded precedence on the existing AST-697 `JOB:`/`CULT:` contract, not a new architectural precedent. No F3 `validate-plan` fix mode for canon.

---


### Radia review-fix — AST-2138

[code-rubric]
**Ticket:** AST-2138
**Publish ref:** `3ddbcbf7c` (`origin/sub/AST-2136/AST-2138-job-link-prefix-decode`)
**Corpus:** `0d01e20d2b313a4e35cf3d07434b6cd69f615768` (tree `canon/` at worktree; no `docs/canon-index.md` on this ref)
**Overall:** CLEAN

**Diff reviewed:** `origin/ftr/AST-2136-job-link-prefix-decode...origin/sub/AST-2136/AST-2138-job-link-prefix-decode` — `src/core/agent.py`, `src/core/consult.py`, plan-fix block in `docs/features/consult/ast-697-prefilter-link-set-schema-and-bracket-decode.md` (product delta only in the two core modules).

## Canon scores

*(Frozen Canon Scope on Linear description: **none** — `## Citations: none at intake`. Scored Joan fix-board **overlap skim** ids from the plan-fix patch § Joan fix-board — AST-2138; off-list statutes not graded per §5.3.)*

| id | grade | effort | one-line |
|----|-------|--------|----------|
| astral.standards.dry-and-focused-functions | A | | Single `_LINK_PREFIX_RE` + `_grade_segment` shared by `_decode_payload` and `_should_decode_as_encoded_line`; duplicate strip/match removed from consult |
| astral.layers.import-direction | A | | `consult` → `agent` module import extended; `agent` → `consult` remains lazy-only (`_apply_prefilter_encoded_link_meta`, `_normalize_rubric_task_response`) |

## Column diff vs plan stage

`no plan-stage scores attached` (Joan **fix-board** `[board-joan] CANON: OK` only; no `validate-plan` fix-mode score table in the issue doc).

## Frame diff

(none)

## Fix-specific checks

**`[bug-repro]`** — **not applicable — board REVISE with sibling ownership.** Betty `[board-betty] TESTS: REVISE` on AST-2138; spawn prompt and Relations name sibling **AST-2139** for the gap manifest / `[bug-repro]` rows. No `qa-fix` on this tip; no `[bug-repro]` in the diff — expected, not fix-now.

**`## What must still hold`** — **OK**

| Item | Verdict |
|------|---------|
| AST-697 AC #2/#3/#6: bracket tails positional; grades-only omit link keys | OK — `_grade_segment` only short-circuits `JOB:`/`CULT:`; bracket/meta fields unchanged |
| AST-603/697 AC #4: `JOB:16`, multi-digit, lists, mixed `JOB:16\|[51,46]` culture rule | OK — prefixed fields route to `meta` with original `f`; downstream `_apply_prefilter_encoded_link_meta` / `_parse_link_index_field` unchanged |
| AST-483: prettified grade tokens (`RC A3`, `RC-A-3`, `RC:A3`) still grades; meta keeps pipe-stripped original | OK — guard runs before colon strip; `meta.append(f)` unchanged |
| AST-1996 / AST-2124 / AST-2126 / AST-2093 decode semantics | OK — classification-only delta in the shared loop; no edits to failure storage, X0, notes-only, or index-map branches |
| `_should_decode_as_encoded_line` routing examples in plan | OK — `test_should_decode_as_encoded_line_routing` cases still satisfied; `000\|JOB:3\|CULT:7` correctly becomes non-encoded per **To-be** |

## Findings

**fix-now:** (none)

**discuss:** (none)

**advisory:**

- **Sibling test carry:** Product fix on AST-2138; Betty’s JOB:0–5 / `CULT:[]` / routing repro coverage belongs on **AST-2139** — do not expect test-tree changes on this sub.
- **Canon Scope process gap:** Fix bug has no frozen Canon Scope block on Linear (same pattern as other fix children); Archie may add explicit frozen lists later for comparability — not product **ESCALATE**.
- **Test baseline noise:** Hedy’s Tests Passed note — `TestAst697PrefilterBracketLinkDecode` / fixture `KeyError` failures identical pre/post fix; 119 baseline failures match ftr; not introduced by this diff.
- **AST-697 cosmetic carry:** Inline `^JOB:`/`^CULT:` in `_apply_prefilter_encoded_link_meta` remains (plan explicitly out of scope); unchanged by this tip.

## What’s solid

- Diff matches plan-fix **Proposed change** steps 1–4: pattern relocation, `_grade_segment`, loop swap, consult import share, routing classifier alignment.
- **To-be** behavior for `JOB:3` / `CULT:7,27` and link-only encoded-line detection is implemented at the only two sites that shared the defect.
- Scope stays within **Component scope** / **Technical scope** on the ticket; no dispatcher/roster/UI; estimate **1** fits the footprint.
- Boundaries honored: no AST-1828 / hydrate / `SOFA5` work in diff.

## Recommended actions (Chuckles)

| Gate | Parent shape | Next action |
|------|----------------|-------------|
| **PROCEED** (C7 complete) | **AST-2136 mini-parent with live `origin/ftr/AST-2136-job-link-prefix-decode`** (spawn did **not** flag `ORPHANED — target dev`) | **Review Posted** → clean-review shortcut → **User Testing** (`resolve-child` skipped). Land via parent **ftr** / sibling merge story — **not** finish-up straight-to-`dev` for this bug alone. |
| | | Append this artifact to the issue doc; post slim upshot `--as radia`. Keep **AST-2139** on its branch for tests. |

`context_tokens≈28000`

---


**Test delivery (docs-acceptance):** AST-2138 carries no test-tree commit. Its [bug-repro] and bible rows land on gap sibling AST-2139 (fix-board [board-betty] TESTS: REVISE).

---

## Bug: AST-2139 — repro tests for single-digit JOB:/CULT: link fields

**Linear:** [AST-2139](https://linear.app/astralcareermatch/issue/AST-2139) · **Mini-parent:** [AST-2136](https://linear.app/astralcareermatch/issue/AST-2136) · **Fix sibling:** [AST-2138](https://linear.app/astralcareermatch/issue/AST-2138) (its `## Bug: AST-2138` section lives on `origin/sub/AST-2136/AST-2138-job-link-prefix-decode` and reaches this doc on ftr via merge-child) · **Publish ref:** `origin/sub/AST-2136/AST-2139-job-link-prefix-tests` · **Origin:** fix-board `[board-betty] TESTS: REVISE` on AST-2138.

Test-tree and bible only. **Betty lands everything below via qa-fix. Engineers do not edit `tests/` or `docs/test-bible/**`.** No `src/` change; AST-2138 owns the product fix.

### As-is

No test exercises a single-digit `JOB:0`–`JOB:5` link field. The existing prefix-tail cases (`TestAst603RubricNormalize::test_lovable_encoded_line_with_job_cult_tails`, `TestAst697PrefilterBracketLinkDecode::test_decode_payload_job_cult_prefix_unchanged`) use `JOB:16`, which never matches `_GRADE_SEG`. So the AST-2136 misparse passes the suite before the fix and after it.

### To-be

Three `[bug-repro]` assertions are red on the pre-fix tree and green once AST-2138 is merged. Both bible pages list them.

### Repro

Verified red on this branch's pre-fix tip (`a1af5cf6a`, identical to `origin/ftr/AST-2136-job-link-prefix-decode` before AST-2138 merges):

```python
_decode_payload("prefilter_company", "grades_encoded_prefilter_links",
                "000|RCA5|HEA5|MLA3|PFA5|SOA5|JOB:3|CULT:7,27",
                {"batch_entities": [{"company_id": "acme"}]})["companies"][0]
# pre-fix: grades vectors RC,HE,ML,PF,SO,JO (JO grade B conf 3); no possible_job_links; culture [7, 27]
consult._should_decode_as_encoded_line("000|JOB:3|CULT:7")   # pre-fix: True
```

### Root cause

This is a coverage gap: link-prefix fixtures only used multi-digit indices. The product root cause is in the AST-2138 section.

### Proposed change (qa-fix: Betty)

1. **Fixture shape (mandatory).** `prefilter_company` decodes as a **company** entity (AST-1723). The ctx must carry `batch_entities: [{"company_id": "acme"}]`, and the row must be read from `result["companies"][0]`. Do **not** copy `TestAst697PrefilterBracketLinkDecode._prefilter_decode_ctx` (`astral_job_id` / `["jobs"]`). That shape is the cause of the existing `KeyError: 'company_id'` / `'jobs'` baseline failures in that class and in `TestAst603RubricNormalize`. Include `vector_labels` for `RC/HE/ML/PF/SO` or assert on raw 2-char codes. Either works, because without a label `vector` falls back to the code.
2. **New class** in `tests/component/core/test_agent.py`, e.g. `TestAst2138JobLinkPrefixNotGrade`, tagged `[bug-repro]` in the qa-fix handoff:
   - **(a) Primary repro, parametrized over `n in 0..5`:** `000|RCA5|HEA5|MLA3|PFA5|SOA5|JOB:{n}|CULT:7,27`. Assert grade vectors are exactly `RC, HE, ML, PF, SO` (no `JO`), `possible_job_links == [n]`, and `culture_links_to_explore == [7, 27]`. The `n == 3` case is the literal production payload; it is the one to name in the `[bug-repro]` line.
   - **(b)** `000|RCF5|HEX0|MLX0|PFX0|SOX0|JOB:1|CULT:[]`: assert `possible_job_links == [1]`, five grades, no `JO`, and no `culture_links_to_explore` key (an empty bracket tail yields no key, per AST-697).
   - **(c)** `consult._should_decode_as_encoded_line("000|JOB:3|CULT:7") is False`. This could also live beside `TestAst699LetterPipePositionPrefix::test_should_decode_as_encoded_line_routing` as a new method. Betty's call; do not edit the existing method.
3. **Red/green gate:** (a) for `n` in 0–5, (b) and (c) must fail on `a1af5cf6a` (pre-fix) and pass on a tree with AST-2138's `3ddbcbf7c` merged. Run them with `ASTRAL_PYTHON=/home/susan/astral/.venv/bin/python ./scripts/testing/run_component_tests.sh tests/component/core/test_agent.py::<NewClass>`. The system `python3` lacks `nh3`/`asyncpg`, and the script's version check rejects 3.14 without `ASTRAL_PYTHON`.
4. **Bible:**
   - `docs/test-bible/core/consult.md`: add an `### AST-2138 · AST-2136` block after the AST-697 / AST-699 entries. Rows: link-prefix guard → `src/core/agent.py` (`_LINK_PREFIX_RE`, `_grade_segment`) → new class (a)/(b); routing guard → `src/core/consult.py` (`_should_decode_as_encoded_line`) → (c). Add the narrowed run command.
   - `docs/test-bible/core/agent.md`: a matching row for `_decode_payload`'s field classification via `_grade_segment`, pointing at (a)/(b).

### Blast radius

Test tree and bible only. Betty's board verdict found no existing test broken by AST-2138: the AST-483 whitespace test, `test_should_decode_as_encoded_line_routing`, the `JOB:16|CULT:38,3,27` cases, and `test_consult.py` ~L2374 stay as-is. Repairing the stale `astral_job_id`/`jobs` fixtures in `TestAst697PrefilterBracketLinkDecode` / `TestAst603RubricNormalize` is **out of scope** here (pre-existing baseline failures, not caused by AST-2136). That is a separate ticket if Susan wants it.

### What must still hold

- No `src/` edits on this ref.
- The existing tests named under Blast radius are unchanged.
- The new assertions encode the AST-2138 **What must still hold** list rather than contradict it: multi-digit/list `JOB:` forms and bracket tails still map as before, and prettified real grades still decode.

**Merge note for Chuckles:** this section and AST-2138's both append at the end of this doc. When both subs reach ftr, expect an end-of-file add/add hunk. Resolve by keeping both sections, AST-2138 first.

### Joan fix-board — AST-2139

**Question:** Does the plan-fix patch require touching canon (statutes/patterns)?

**Read:** `## Bug: AST-2139` in `docs/features/consult/ast-697-prefilter-link-set-schema-and-bracket-decode.md` on `origin/sub/AST-2136/AST-2139-job-link-prefix-tests`. Scope is explicit: **test tree + `docs/test-bible/**` only**, Betty via **qa-fix**, **no `src/`**; product behavior is owned by merged AST-2138 on ftr.

**Judgment:** **CANON: OK.** New `[bug-repro]` rows and bible traceability document already-merged decode/routing behavior (`_grade_segment`, `_LINK_PREFIX_RE`, `_should_decode_as_encoded_line`). That does not contradict, amend, or carve out any in-force statute or pattern; it does not introduce a new architectural precedent. No F3 `validate-plan` fix mode for canon.

---


### Radia review-fix — AST-2139

[code-rubric]
**Ticket:** AST-2139
**Publish ref:** `ad3659514` (`origin/sub/AST-2136/AST-2139-job-link-prefix-tests`)
**Diff base:** `origin/ftr/AST-2136-job-link-prefix-decode` … `origin/sub/AST-2136/AST-2139-job-link-prefix-tests` (ftr already carries AST-2138 product fix per spawn; this sub is test/bible-only)
**Corpus:** `0d01e20d2b313a4e35cf3d07434b6cd69f615768` (tree `canon/` at worktree; no `docs/canon-index.md` on this ref)
**Overall:** CLEAN

**Diff reviewed:** `docs/features/consult/ast-697-prefilter-link-set-schema-and-bracket-decode.md` (AST-2139 plan block), `docs/test-bible/core/agent.md`, `docs/test-bible/core/consult.md`, `tests/component/core/test_agent.py` (+30 lines, additions only). **No `src/**`.**

## Canon scores

*(Frozen Canon Scope on Linear description: **none**. Test/bible-only gap; Joan fix-board **CANON: OK** — no directive rows to score; off-list statutes not graded per §5.3.)*

| # | id | grade | effort | one-line |
|---|-----|-------|--------|----------|
| — | *(empty list)* | — | — | Gap delivery documents merged AST-2138 behavior only |

## Column diff vs plan stage

`no plan-stage scores attached` (Joan **fix-board** `[board-joan] CANON: OK` only).

## Frame diff

(none)

## Fix-specific checks

**`[bug-repro]`:** **OK**

- **Tag:** Class docstring `TestAst2138JobLinkPrefixNotGrade` carries `[bug-repro]`; Betty’s qa-fix thread names `test_single_digit_job_link_is_meta_not_grade[3]` as the repro node (production payload `JOB:3`).
- **(a) Primary repro:** Parametrized `n in 0..5` on `000|RCA5|HEA5|MLA3|PFA5|SOA5|JOB:{n}|CULT:7,27` with **company-shaped** ctx (`company_id`, `result["companies"][0]`) per plan — not the stale `astral_job_id` / `jobs` fixture. Asserts concrete **To-be** values from AST-2138: exactly five grade vectors `RC…SO` (no `JO`), `possible_job_links == [n]`, `culture_links_to_explore == [7, 27]`. Not tautological (outcome assertions on decode, not reimplementation of `_grade_segment`). Pre-fix failure is real: extra `JO` grade and missing `possible_job_links` (Betty/Hedy: 8/8 red on `a1af5cf6a`, green on post–AST-2138 tip).
- **(b)** `JOB:1|CULT:[]` → `[1]`, five grades, no `culture_links_to_explore` key — matches plan AST-697 empty-tail rule.
- **(c)** `_should_decode_as_encoded_line("000|JOB:3|CULT:7") is False` — pins routing **To-be**; pre-fix was `True`.
- **Not fix-now:** `culture_links_to_explore == [7, 27]` may already hold pre-fix (CULT tail parsed); red gate still fails on grades / `possible_job_links` (and on (b)/(c)).

**`## What must still hold`:** **OK**

| Item | Verdict |
|------|---------|
| No `src/` edits on this ref | OK — diff has zero product files |
| Blast-radius tests unchanged | OK — only insert after `TestAst699LetterPipePositionPrefix`; no edits to AST-483 routing, `JOB:16`, or `test_consult.py` ~L2374 |
| New assertions align with AST-2138 contract, not contradict multi-digit/bracket/AST-483 behavior | OK — scope is single-digit `JOB:0`–`5` + link-only routing only |

## Findings

**fix-now:** (none)

**discuss:** (none)

**advisory:**

- **Sibling product:** AST-2138 is **User Testing** on ftr; this sub completes Betty’s `[board-betty] TESTS: REVISE` from AST-2138 board.
- **Baseline noise:** Stale `TestAst697PrefilterBracketLinkDecode` / `TestAst603RubricNormalize` fixtures remain failing (documented out of scope); 119 baseline failures identical to ftr — not introduced here.
- **Doc EOF:** Plan merge note — keep AST-2138 and AST-2139 sections both at end of feature doc when rolling subs to ftr.

## What’s solid

- Plan fidelity: `TestAst2138JobLinkPrefixNotGrade` implements proposed (a)/(b)/(c); bible blocks `### AST-2138 · AST-2136` in `agent.md` and `consult.md` with table rows + narrowed run command.
- Repro-first bar met per Betty qa-fix comment (red `a1af5cf6a`, green synced ftr with AST-2138).
- Cross-ticket scope clean: test/bible only; no smuggled product work.
- Estimate **1** matches footprint.

## Recommended actions (Chuckles)

| Gate | Parent shape | Next action |
|------|----------------|-------------|
| **PROCEED** (C7 complete) | **AST-2136 mini-parent with live ftr** (not `ORPHANED → dev`) | **Review Posted** → clean-review shortcut → **User Testing** (`resolve-child` skipped). Merge this sub to ftr when rollup-safe alongside AST-2138 UT closure. |
| | | Append artifact; post slim upshot `--as radia`. |

`context_tokens≈22000`

---

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Hedy | engineer | `/home/susan/.cursor/chats/7f678ae3e742906d86b46cbaabc2d943/249e00bf-23fc-4226-a279-4f42d7385629/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/7f678ae3e742906d86b46cbaabc2d943/2d0294de-cc0a-481b-ac29-3d0f10b47e14/store.db` |
| Radia | review | `/home/susan/.cursor/chats/7f678ae3e742906d86b46cbaabc2d943/7cfbe4bf-bb71-49ff-a9b3-6c5d6f48b19d/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-2136 (parent) | ftr/AST-2136-job-link-prefix-decode |
| AST-2138 | sub/AST-2136/AST-2138-job-link-prefix-decode |
| AST-2139 | sub/AST-2136/AST-2139-job-link-prefix-tests |

**Epic worktree:** `astral-AST-2136/` — one active sub checked out at a time.
