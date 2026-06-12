# Consult-parity hydration for prefilter_company (Prefilter Company Failing)

**Linear:** [AST-603](https://linear.app/astralcareermatch/issue/AST-603/consult-parity-hydration-for-prefilter-company-prefilter-company)  
**Parent:** [AST-602](https://linear.app/astralcareermatch/issue/AST-602/prefilter-company-failing) (context only — do not implement sibling scope here)  
**Publish ref:** `origin/sub/AST-602/AST-603-consult-parity-prefilter-hydration`  
**Summary:** Production prefilter runs fail decode/validation in `do_task` even when `agent_performance.status` is `success`, leaving every company in **PREFILTER_UNKNOWN**. This ticket restores prefilter by routing **prefilter_company** responses through the same shared rubric **normalize → decode → hydrate reasons → verdict/score** path consult uses — without a prefilter-only parse matrix. **AST-507** pass/fail/score semantics and inflow vs legacy state mapping stay unchanged.

**Root cause (from AST-602 repro):**

1. **Early schema validation** in `do_task` validates the outer envelope / raw `agent_payload` dict **before** encoded decode, so dict JSON responses fail with `Missing required field 'jobs'` (karbon, moonvalley, outreach, fictiv).
2. **`_decode_payload` runs only on strings**; dict `agent_payload` never reaches a normalized `{"jobs": [...]}` shape.
3. **Legacy pipe lines** like `A|B|A|59,60|51,46,53,50,45` are not compact encoded rows (`000|ERCA|MEAC|...`), so decode raises `bad position field`.
4. **Roster never hydrates reasons** from the rubric artifact (`_hydrate_grade_reasons_from_rubric`), so even successful encoded decodes produce empty `prefilter_company_notes` until consult-parity hydration runs.

**Out of scope:** Rubric vector definitions, dealbreaker thresholds, **AST-508** locate dispatch, website scrape timeouts (**CANNOT_READ_WEBSITE**), new DB columns, Manage Tasks prompt copy refresh (optional follow-up comment only).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | New shared `_normalize_rubric_task_response` + helpers (JSON / letter-pipe / link-index aliases → `jobs[]`); export `_hydrate_grade_reasons_from_rubric` usage pattern for roster | core |
| `src/core/agent.py` | Skip pre-decode schema validation for `_encoded` tasks; call shared normalizer before/alongside `_decode_payload`; post-normalize hydration hook for rubric tasks | core |
| `src/core/roster.py` | `prefilter_company` + `_fetch_prefilter_notes`: hydrate grades after flatten; persist empty link lists when absent; culture links on inflow pass + legacy **TO_WATCH** | core |
| `src/utils/config.py` | Optional `output_types` entry for prefilter link-tail grammar; ensure `prefilter_company` `response_schema` includes optional `reason` on grade rows (post-hydrate validation only) | utils |
| `tests/component/core/test_agent.py` | Normalizer + do_task ordering tests for repro payload categories | tests |
| `tests/component/core/test_roster.py` | Hydration + dict-JSON prefilter success path (extends **AST-507** class) | tests |

Betty adds manifest rows in **qa-astral** for full repro replay per AC #6 — engineer does **not** edit `docs/ASTRAL_TEST_BIBLE.md`.

---

## Stage 1: Shared rubric response normalization (consult + agent)

**Done when:** Any `TASK_CONFIG` entry with both `output_type` containing `_encoded` and `rubric_artifact` can turn AST-602 repro shapes into `{"jobs": [{"astral_job_id", "grades", optional link fields}]}` before schema validation; `do_task` no longer fails prefilter on `Missing required field 'jobs'` for dict envelopes.

1. In `src/core/consult.py`, add **`_normalize_rubric_task_response(task_key, task_config, parsed, ctx) -> dict`** (module-level, used by `agent.py`):
   - **Input `parsed` shapes to accept** (mirror parent Original brief — one code path, not per-company branches):
     - Already **`{"jobs": [...]}`** with at least one job dict → return unchanged (ensure each job has `astral_job_id` from `ctx["batch_entities"][0]` when batch_size=1 and missing).
     - Envelope **`{"agent_performance": ..., "agent_payload": ...}`** → unwrap `agent_payload` first (reuse `_inner_task_payload` semantics from `agent.py`).
     - **`agent_payload` JSON string** → `json.loads`; on failure, treat as compact encoded string and delegate to `_decode_payload`.
     - **`agent_payload` dict** → build one job row (no `jobs` wrapper required from model).
     - **`agent_payload` str** not matching `^\d{3}\|` → attempt letter-pipe parse (Category A below), then JSON parse, then `_decode_payload`.
   - **Category A — letter pipe** (`A|B|A|59,60|51,46,53,50,45`, `[7]`, `JOB:16`, `CULT:38,3,...`):
     - Load rubric criteria: `_rubric_criteria_from_cd(ctx.get("candidate_data") or {}, task_config.get("rubric_artifact"))`.
     - Let **`n = len(rubric_criteria)`**. Walk pipe fields left-to-right after optional `000|` pos prefix (strip leading `000|` or `0|` if present).
     - First **`n`** fields that are a single letter in `ASTRAL_CONFIG["valid_grades"]` become grade rows: `{"vector": criterion[i]["label"], "grade": letter, "confidence": 3}`.
     - ⚠️ **Decision:** Default **confidence = 3** for letter-only pipe responses (no model-supplied confidence digit). This matches consult pass rules (confidence > 1) and makes dealbreaker **F** with default 3 a fail — consistent with production intent.
     - Remaining fields → link indices via **`_parse_link_index_field(field) -> list[int]`**:
       - Comma-separated ints (`59,60`).
       - Bracket lists (`[7]`, `[2,7]`).
       - Prefixed tokens **`JOB:`** / **`CULT:`** (case-insensitive) → strip prefix, parse int list.
       - First link field → `possible_job_links`; second → `culture_links_to_explore`. Additional link fields append to culture list.
   - **Category B — JSON object** (all key casings in repro: `reality_check`, `RealityCheck`, `Mission_Product_Orientation`, `culture_links`, etc.):
     - For each rubric criterion (in list order), resolve grade letter from **`_grade_letter_for_criterion(obj, criterion)`** trying, in order: `criterion["code"]`, snake_case of `label`, PascalCase, screaming snake, and the alias table in step 2.
     - Each matched grade row: `{"vector": criterion["label"], "grade": letter, "confidence": 3}` unless the JSON value is a dict with `grade` + `confidence` keys.
     - Link keys (any casing): `possible_job_links`, `PossibleJobLinks`, `POSSIBLE_JOB_LINKS` → `possible_job_links`; `culture_links_to_explore`, `CultureLinksToExplore`, `culture_links`, `CULTURE_LINKS_TO_EXPLORE` → `culture_links_to_explore`. Coerce values to `list[int]` (flatten single int).
   - **Category C — compact encoded string** → call existing **`_decode_payload(task_key, output_type, payload, ctx)`** from `agent.py` (import at function scope to avoid cycle: `from src.core.agent import _decode_payload`).
   - Return **`{"jobs": [job_dict]}`** with **`astral_job_id`** set from `ctx["batch_entities"][0]["astral_job_id"]` when `batch_size == 1`.
   - On unrecoverable shape, raise **`ValueError`** with task_key prefix (same pattern as decode errors).

2. In `src/core/consult.py`, add private helpers (keep in same file, no new modules):
   - **`_parse_link_index_field(field: str) -> list[int]`** — handles comma lists, bracket lists, `JOB:`/`CULT:` prefixes; ignore empty tokens.
   - **`_grade_letter_for_criterion(obj: dict, criterion: dict) -> Optional[str]`** — returns single letter or None.
   - **`_RUBRIC_JSON_GRADE_ALIASES: Dict[str, tuple]`** — optional static aliases for company_prefilter vectors only if dynamic label/code match fails; keep minimal (document in code comment that rubric criterion order is authoritative).

3. In `src/core/agent.py`, **`do_task`** encoded pipeline (after `coerce_grades_encoded_json_parse`, before success storage):
   - If **`"_encoded" in output_type`** and **`task_config.get("rubric_artifact")`**:
     - **Skip** the block at ~1369–1470 that calls **`_validate_response_schema(parsed, ...)`** on the raw envelope (schema validation runs only after normalization below).
     - Call **`parsed = _normalize_rubric_task_response(task_key, task_config, parsed, ctx or {})`** inside try/except; on **`ValueError`**, same failure path as decode failed (log, store RESPONSE with agent_payload snippet, return `success: False`).
     - Set **`result["parsed_response"] = parsed`**.
   - Keep existing string **`_decode_payload`** branch as fallback when normalizer delegates to it (do not duplicate decode logic).
   - After normalization, run existing post-decode steps: **`_validate_response_schema`**, **`_validate_grade_confidence_in_payload`**, vector validation if configured.

4. In `src/utils/config.py`, extend **`prefilter_company`** `response_schema` `grades` `items_schema` with optional **`"reason": {"type": "str", "required": False}`** so post-hydration payloads validate.

5. Add **`tests/component/core/test_agent.py`** cases (new class `TestAst603RubricNormalize`):
   - Dict envelope karbon shape → `jobs[0].grades` length equals rubric criteria count; no `Missing required field 'jobs'`.
   - Letter pipe `A|B|A|15|13,16,14` → grades + link lists.
   - JSON string berry shape → grades + links.
   - Encoded line `000|ERCA|MEAC|PGAA|JOB:16|CULT:38,3,27,37,34` → passes through decode/normalize without trailing-content error.

⚠️ **Decision:** Normalizer lives in **`consult.py`** (not `roster.py`) so consult batch tasks can reuse it later; **prefilter_company** does not get roster-local parse helpers.

---

## Stage 2: Roster hydration and persistence parity

**Done when:** Successful prefilter runs hydrate grade reasons from **company_prefilter** rubric before `_render_pass_fail` / notes; link fields persist as empty lists when absent; coat-check uses the same path.

1. In `src/core/roster.py`, import **`_hydrate_grade_reasons_from_rubric`** from `src.core.consult` (same import block as `_render_pass_fail`).

2. In **`prefilter_company`**, immediately after **`flat = _flatten_prefilter_parsed(parsed)`** and **`grades = flat.get("grades") or []`**:
   ```python
   rubric_list = _rubric_criteria_from_cd((ctx or {}).get("candidate_data") or {}, "company_prefilter")
   if grades and rubric_list:
       _hydrate_grade_reasons_from_rubric(grades, rubric_list)
   ```
   - On **`ValueError`** from hydration → **`WEBSITE_FOUND_RETRY`** (retryable), set `result["error"]`, return (do not transition to pass/fail without reasons when rubric exists).

3. Update link persistence (replace current truthy-only guards):
   - **`possible_job_links`**: `data_to_save["possible_job_links"] = flat.get("possible_job_links") or []` — always persist key after successful prefilter (empty list when absent) per AC #5.
   - **`culture_links_to_explore`**: persist when **`decision == "TO_WATCH"`** OR **`new_state == "PREFILTER_PASSED"`** (inflow pass); use `flat.get("culture_links_to_explore") or []`. Legacy **IGNORE** / **PREFILTER_FAILED** may omit culture links (keep existing guard intent: only explore culture on watch/pass paths).

4. In **`_fetch_prefilter_notes`**, after **`_flatten_prefilter_parsed`**:
   - Build **`rubric_list`** from `_vector_labels_from_ctx` / `_rubric_criteria_from_cd` (pass candidate ctx when available; today handler passes `None` — load rubric from company’s candidate if coat-check ctx lacks `candidate_data`; if still empty, skip hydration and keep current notes behavior).
   - Call **`_hydrate_grade_reasons_from_rubric(grades, rubric_list)`** when both non-empty.
   - Mirror link field persistence from step 3.

5. **`_flatten_prefilter_parsed`**: no change required if Stage 1 always returns `jobs[0]` from `do_task`; keep top-level `grades` fallback for unit mocks.

6. Add **`tests/component/core/test_roster.py`**:
   - Mock `do_task` returning dict-envelope karbon-style payload **through real normalizer** (integration-style: patch only scrape + `do_task` wrapper calling normalize) OR mock post-normalize `parsed_response` with grades lacking `reason`, assert **`prefilter_company_notes`** contains hydrated text after run.
   - Assert **`prefilter_score`** still persisted on pass (**AST-507** regression).

---

## Stage 3: Config — prefilter output instructions (optional tail grammar)

**Done when:** `{$OUTPUT_INSTRUCTIONS}` for **prefilter_company** documents encoded row format **and** states that JSON grade objects are accepted; link index fields documented once.

1. In `src/utils/config.py`, add **`output_types["grades_encoded_prefilter_links"]`** (or extend **`grades_encoded`** instructions if Susan prefers one key — prefer **new key** to avoid changing consult prompts):
   - Copy **`grades_encoded`** payload instructions.
   - Append one paragraph: after grade segments, optional **`JOB:<indices>`** and **`CULT:<indices>`** pipe fields **OR** JSON keys **`possible_job_links`** / **`culture_links_to_explore`** (int lists). State software normalizes all listed shapes (AST-602 repro).
   - Example line: `000|RCA3|MPB3|USA3|JOB:59,60|CULT:51,46,53,50,45`

2. Set **`TASK_CONFIG["prefilter_company"]["output_type"]`** to **`"grades_encoded_prefilter_links"`**.

3. In **`_decode_payload`**, treat **`grades_encoded_prefilter_links`** like **`grades_encoded`** with **`with_meta = True`** for tail fields, **and** teach meta parser to map fields starting with **`JOB:`** / **`CULT:`** into job dict keys (not listing meta). Implement in Stage 1 normalizer link parser — decode may pass through raw meta to normalizer when `_meta` accepts tail.

   ⚠️ **Decision:** **`with_meta = True`** only for the new output type so **`grades_encoded`** consult tasks stay strict; prefilter link tails no longer raise `unexpected trailing content`.

4. Run before publish:
   ```bash
   ./scripts/testing/run_component_tests.sh \
     tests/component/core/test_agent.py \
     tests/component/core/test_roster.py \
     tests/component/utils/test_config.py
   ```

---

## Self-Assessment

**Scope:** `Single-Component` — Shared rubric normalization in `consult.py` + `do_task` ordering fix in `agent.py`, prefilter hydration/persistence in `roster.py`, small config/output_type addition; no dispatcher or UI changes.

**Conf:** `Medium` — Consult decode/hydrate patterns are established (**AST-351**, **AST-507**, **AST-500**), but normalizing six repro payload families without a prefilter-only matrix requires careful alias handling and test coverage.

**Risk:** `Medium` — Incorrect default confidence on letter-pipe grades could shift pass/fail rates; wrong hydration would empty notes but should not block state transitions; `do_task` ordering change affects all rubric encoded tasks — must gate normalizer on `rubric_artifact` presence.

---

## Self-review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Single `_normalize_rubric_task_response` shared by agent layer; roster reuses `_hydrate_grade_reasons_from_rubric` / `_render_*` — no duplicate F2+ logic. |
| §2.1 Config | Output type + schema optional `reason` in `config.py`; behavior flags unchanged for **AST-507** states. |
| §2.4 Batch | No change to claim/clear; `batch_entities` / `vector_labels` ctx unchanged. |
| §2.6 State machine | Transitions unchanged; still **PREFILTER_PASSED/FAILED** vs **TO_WATCH/IGNORE** via `_company_used_inflow_prefilter`. |
| §3.3 Imports | `agent` → `consult` for normalizer; `roster` → `consult` for hydration (existing pattern). |
| §3.5 Naming | Link keys stay `possible_job_links` / `culture_links_to_explore` per **AST-507**. |

No `conf-!!-NONE` conflicts.

---

## Execution contract (developer)

- Execute stages in order; one commit per stage on **`dev-hedy`**, then Joan **`store-code-commit`** to **`origin/sub/AST-602/AST-603-consult-parity-prefilter-hydration`** with **`--session dd7666a7-4335-4d30-96b1-d067f5e0ffd1`**.
- Do **not** add roster-only parse functions — all shape tolerance belongs in **`consult._normalize_rubric_task_response`**.
- If a repro payload category cannot be normalized without guessing vector order, stop with 🛑 comment on **AST-603** (not parent) citing the exact payload line and proposed alias rule.
- After Stage 3, request **qa-astral** manifest entries for each repro category; do not patch **`ASTRAL_TEST_BIBLE.md`** yourself.

---

## Review

**Branch:** `origin/sub/AST-602/AST-603-consult-parity-prefilter-hydration`  
**Build tip:** `eb19f6e3` (3 product commits: normalizer/do_task, roster hydration, config output type)

## Radia review (AST-603)

**Diff:** `origin/dev...origin/sub/AST-602/AST-603-consult-parity-prefilter-hydration` (9 files, +794 / −31)

### What's solid

- **Plan fidelity:** All three stages landed — `_normalize_rubric_task_response` in `consult.py`, `do_task` skips pre-decode schema when `rubric_artifact` + `_encoded`, post-normalize validation via `post_rubric_decode`, roster hydrates reasons and persists link lists per AC #5. `grades_encoded_prefilter_links` output type with `JOB:`/`CULT:` tails matches Stage 3.
- **§1.3 DRY / §2.6:** Single normalizer shared by agent; roster reuses `_hydrate_grade_reasons_from_rubric` and existing `_render_pass_fail` / `_render_score` — no duplicate F2+ matrix. State transitions unchanged (**PREFILTER_*** vs **TO_WATCH**/**IGNORE**).
- **§2.4 batch:** Claim/clear untouched; `batch_entities` ctx used for `astral_job_id` backfill on batch_size=1.
- **§2.1 config:** Optional `reason` on grade rows; new output type documented in `ASTRAL_CONFIG["output_types"]`.
- **Self-Assessment alignment:** Footprint matches `scope-Single-Component`; no dispatcher/UI drift; `conf-Medium` / `risk-Medium` mitigations (normalizer gated on `rubric_artifact`, letter-pipe confidence=3 documented in plan) present in code.
- **Tests:** Betty manifest §7.13zw — 13/13 passed on `dev-hedy` (normalize repro categories, hydration notes, **AST-507** score regression).

### Issues

| Severity | Location | Finding |
| --- | --- | --- |
| **discuss** | `src/core/consult.py` — `_job_from_rubric_json` / `_job_from_letter_pipe` | Partial vector coverage (model omits a criterion) yields fewer grade rows than rubric length; `_render_pass_fail` fails closed (not **PREFILTER_UNKNOWN**). Confirm Susan accepts fail-over-unknown for sparse JSON/pipe payloads vs requiring full rubric width before verdict. |
| **discuss** | Plan Stage 1 — letter-pipe default `confidence: 3` | Documented plan decision; dealbreaker **F** at default 3 still fails. Worth noting in parent **AST-602** UAT if production letter-only responses were historically graded with explicit confidence digits. |
| **advisory** | `src/core/consult.py` — `_parse_link_index_field` | Non-integer tokens in link fields are skipped silently (`continue` on `ValueError`); tolerant for repro aliases but may drop bad indices without a decode error. |
| **advisory** | `src/core/agent.py` / `consult.py` — function-scoped cross-imports | `agent` ↔ `consult` lazy imports break cycles (plan §Self-review); no in-code comment on each import — matches existing consult lazy-import style elsewhere. |
| **advisory** | `src/core/roster.py` — `_fetch_prefilter_notes` | Hydration `ValueError` → `return None` (coat-check path only); main `prefilter_company` correctly routes hydration failure to **PREFILTER_UNKNOWN**. |

### Recommended actions

| Item | Action | Owner |
| --- | --- | --- |
| Partial rubric rows | **discuss** — fail vs unknown when grade count < rubric criteria | Hedy / Susan |
| Letter-pipe confidence=3 | **discuss** — acknowledge at **AST-602** UAT if pass rates shift | Susan |
| Silent link token drop | **advisory** — optional log at debug if link field parses empty after non-empty input | Hedy (defer) |

**Verdict:** No **fix-now** items. Ready for **resolve-astral** once discuss rows are acknowledged (or accepted as intentional per plan).

---

## Resolution (2026-06-11)

**fix-now:** None — no product changes.

**discuss (acknowledged, no code change):**

1. **Sparse JSON/pipe grades** — Intentional per plan: partial criterion coverage yields fewer grade rows; `_render_pass_fail` applies dealbreaker rules on present rows (fail closed to **PREFILTER_FAILED** / **IGNORE**, not **PREFILTER_UNKNOWN**). **PREFILTER_UNKNOWN** remains for decode/hydration failures only (AC #1).
2. **Letter-pipe `confidence: 3`** — Plan Stage 1 decision; flagged for **AST-602** parent UAT if pass rates shift vs historical letter-only responses.

**advisory:** Deferred — silent link token skip and lazy-import comments accepted as-is.
