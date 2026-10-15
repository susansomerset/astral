# Grade schema (call-time forced-tool schema + hydrate)

**Test module:** `tests/component/core/test_grade_schema.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/grade_schema.py` | `tests/component/core/test_grade_schema.py` | no (100% branch at AST-2178; not on `LOCKED_AT_100`) |

---

### AST-2178 · AST-2172 (new module — schema builder, hydrate, light check)

`grade_row_ids(ctx)` (`batch_index_map` keys sorted, else `batch_entities` positions, `{i:03d}`); `build_grade_tool_schema(output_type, codes, row_ids)` (closed rows × codes + `agent_performance`; extras required-but-nullable; vet `grade_letters` / `confidence_range`; raises on no codes or a non-`structured_output` type); `hydrate_grade_tool_input(task_key, output_type, tool_input, codes, ctx)` → `jobs[]` / `companies[]` / vet `results[]` + per-entity `decode_failures` (`{id_key, pos, reason}`). Pure functions — nothing calls them until **AST-2179** / **AST-2180** / **AST-2181**. No provider calls.

| Area | Component tests |
| --- | --- |
| Row ids: index map wins + sorted; positions; empty | **`TestGradeRowIds`** (3) |
| AC 1 closed schema (`required` = codes, `additionalProperties: false`, enum = `valid_grades`, confidence 0–5); `agent_performance` shape; AC 2 no codes raises; non-grader / unknown type raises; extras nullable with nested `items` / `additionalProperties` kept; vet A–F / 1–5; full schema at debug (`stat.logging.debug`) | **`TestBuildGradeToolSchema`** (7) |
| AC 3 downstream shape = old `_decode_payload` output for `evaluate_jd` (index map + C0→X0), `grade_do` (notes), `qualify_job_listings` (meta + `job_data`), `prefilter_company` (link arrays), vet; schema rows = hydrated rows; label fallback; row-id order | **`TestHydrateDownstreamShape`** (7) |
| Light check (`stat.agent.grade-vector-validation` / `confidence-bounds`): missing row, non-object row, missing code (never X), extra code, X with nonzero conf, illegal letter, non-object cell, conf 6 / −1 / string / bool → that entity only in `decode_failures`; clean batch has no key; unknown row warned once with the decoder's text (`stat.logging.warning`) and skipped; `"1"` vs `"001"` mangled key; company id key | **`TestHydrateLightCheck`** (16) |
| Extra fields: absent = null; wrong JSON type fails entity (notes int, links string / mixed / bool, `job_data` non-string value / list); strip + blank → dropped, `job_data` blank value → `None`; empty array / object dropped | **`TestHydrateExtraFields`** (9) |
| Vet: confidence 0 out of range (no X0 rewrite), X illegal, missing / blank website fails the hit, website stripped, exactly one code | **`TestHydrateVet`** (6) |
| Non-object tool input `TypeError`; non-grader type `ValueError` | **`TestHydrateContractErrors`** (2) |

**AC 3 oracle:** expected dicts are literals captured from `src.core.agent._decode_payload` on `origin/sub/AST-2172/AST-2178-call-time-schema-hydrate` @ `9b7f68bd7` (plan Appendix C cases). The test does not import the decoder, so it survives **AST-2180** deleting it.

**Broken / obsolete:** none — no existing test imports the module. **Integration:** none.

#### QA test manifest (AST-2178)

1. **Must pass:** `ASTRAL_PYTHON=<venv python> scripts/testing/run_component_tests.sh tests/component/core/test_grade_schema.py` — 50 passed; `src/core/grade_schema.py` 100% statements + branches (116 / 58).
2. **Collection:** `python -m pytest --collect-only -q tests/component/core/test_grade_schema.py` — 50 collected, zero errors.
3. **Scope:** `git diff origin/ftr/AST-2172-structured-output-graders...HEAD -- src/` lists only `src/core/grade_schema.py`; `rg '"grades_encoded' src/core/grade_schema.py` empty (parent AC 9).

**Bible shasum (after publish):** `git show origin/sub/AST-2172/AST-2178-call-time-schema-hydrate:docs/test-bible/core/grade_schema.md | shasum`
