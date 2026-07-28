# UAT: parse validation false-missing candidate_name after job-array

**Linear:** [AST-1005](https://linear.app/astralcareermatch/issue/AST-1005/uat-parse-validation-false-missing-candidate-name-after-job-array)
**Parent:** [AST-994](https://linear.app/astralcareermatch/issue/AST-994/parse-resume-json-output-is-incomplete) — Parse resume json output is incomplete
**Publish ref:** `origin/sub/AST-994/AST-1005-uat-parse-validation-false-missing-candidate-name`

After AST-996/997 experience job-array contracts, Session Resume Paste craft-base validation can fail with `Missing required field 'candidate_name'` even when the name is present as `agent_payload.resume_structure.candidate_name` beside a well-formed experience job array. Admin surfaces that server error as a toast. Root cause (reproduced): `_flatten_craft_resume_section_strings` promotes from `resume_structure.content` and content-block nests, but **not** from direct keys on `resume_structure`; and when `sections` is missing, normalize replaces `resume_structure` with `default_resume_structure()` **after** flatten, wiping sibling section values before they can be lifted. Schema still requires top-level `candidate_name`. Secondary: `_validate_response_schema` recursively validates `items_schema` list elements with the same envelope helper. Fix: promote known section ids from direct `resume_structure` keys (preserving experience job arrays) before any default-structure replace; validate list items with a dedicated non-envelope field checker. Do not loosen required `candidate_name` or drop job-array `items_schema`.

## UAT fitness

- **AC restored:** Parent AC (quoted on bug): after craft-base parse of a multi-job resume paste, Experience is an ordered list of jobs with company/title/dates/location/accomplishments observable in parse JSON; task response contracts for craft-base (and shared job-array shape) accept the new form without silently flattening Experience back to a string.
- **Correct outcome:** Valid craft-base parse JSON with `candidate_name` present under `resume_structure` (direct key and/or existing content-map paths) **plus** experience as a job array passes response validation; user can accept/use the parse without a false-missing `candidate_name` popup.
- **Sibling check:** AST-996/997 keep experience as required/optional list of objects with `items_schema` (company, title, dates, location, accomplishments); AST-998 HTML builders unchanged. Verify by normalize+schema on a payload with job-array experience after promote — experience remains a list of dicts, not a string.
- **Not sufficient:** Hiding the Admin toast / swallowing the validation error string without making nested-name + job-array payloads actually pass schema.
- **Wrong fix rejected:** Removing `candidate_name` from required fields; accepting empty name; flattening Experience back to a single string; skipping schema validation when experience is a list; UI-only toast suppression.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Promote known section ids from direct keys on `resume_structure` (incl. `candidate_name`, experience job arrays) before default-structure replace; do not early-return flatten solely because `sections` is missing | core |
| `src/core/agent.py` | Validate `items_schema` list elements with a dedicated item-field helper (not full envelope recurse) | core |

**Out of scope:** `tests/`, bible; Admin toast UI rewrite; AST-993 chrome; cover-letter HTML; inventing candidate fields; changing `_EXPERIENCE_JOB_ITEM_SCHEMA` field set.

## Stage 1: Promote direct `resume_structure` section keys before wipe

**Done when:** A craft-base `agent_payload` with `candidate_name` only as a direct key on `resume_structure` (with or without `sections`) and top-level experience as a job array normalizes so top-level `candidate_name` is set; subsequent schema validation does not return `Missing required field 'candidate_name'` when other required fields are present. Replacing missing `sections` with `default_resume_structure()` no longer discards sibling section values that should have been promoted.

1. In `src/core/candidate.py`, update `_flatten_craft_resume_section_strings`:
   - If `resume_structure` is not a dict, return (unchanged).
   - **Do not** return early solely because `sections` is missing or not a dict — still run promotions below. Keep the existing `sections`-enabled nested-content loop only when `sections` is a dict (skip that loop when absent).
   - After the existing `content` map and `_CRAFT_RESUME_CONTENT_DICT_KEYS` promotions, add a pass over `RESUME_STRUCTURE_KNOWN_SECTION_IDS`: for each `sid`, if `sid` is a key on `resume_structure` (direct), call the existing `_promote(sid, raw_struct[sid])` (same rules: experience job-array preserve via `_is_experience_job_array`; string coerce for other ids; never overwrite non-empty top-level).
   - ⚠️ **Decision:** Promote only known section ids from direct keys — not arbitrary `resume_structure` keys (avoids lifting `sections`/`content` metadata).
2. In `normalize_craft_resume_base_agent_payload`, keep order: call `_flatten_craft_resume_section_strings(payload)` **before** any `payload["resume_structure"] = default_resume_structure()` when sections are missing. After Stage 1.1, sibling values are already on the payload top-level, so the default replace is safe.
3. Do not change `TASK_CONFIG` / experience `items_schema` / required `candidate_name`.

**Verification:** Local normalize + `_validate_response_schema(…, TASK_CONFIG["craft_resume_base"]["response_schema"], …)` for: (a) `resume_structure.candidate_name` + `sections` + job-array experience, other required fields top-level → ok; (b) same without `sections` → ok after promote then default struct; (c) name absent everywhere → still `Missing required field 'candidate_name'`.

## Stage 2: Harden list `items_schema` validation

**Done when:** List fields with `items_schema` (craft-base `experience`) validate each element's fields without treating the element as an `{agent_performance, agent_payload}` envelope; path-prefixed item errors remain (`experience[i]: …`).

1. In `src/core/agent.py`, near `_validate_response_schema`, add a helper (e.g. `_validate_schema_object_fields(obj, fields_schema, path_prefix)`) that for a dict `obj` walks `fields_schema` with the same required / type / enum checks already used for payload fields (str/bool/int/list/dict), returning the first error string or `None`. Do **not** look for `agent_payload` / `agent_performance` / failure envelopes inside this helper.
2. In `_validate_response_schema`, when `items_schema` is present and the value is a list: keep the non-dict item type error; replace the recursive `_validate_response_schema(item, items_schema, task_key)` call with the new helper, prefixing failures as `f"{field_name}[{idx}]: {item_err}"`.
3. Do not change envelope validation for the top-level parse object.

**Verification:** Valid job-array experience still passes; an experience item missing `company` yields an `experience[0]: …` missing-field error (not an envelope message); Stage 1 cases (a)–(c) unchanged.

## Stage 3: Regression sanity (no new files)

**Done when:** Engineer has exercised normalize+validate for nested-name + job-array (pass), missing name (fail), experience string (fail list type); experience remains a list of job objects after success — AC #1 shape intact.

1. No additional product files. Optional one-off local Python exercise only (do not add `tests/` or bible edits).
2. Confirm job-tailored paths that share flatten only if they call `_flatten_craft_resume_section_strings` / craft-base normalize — do not broaden into draft/finalize schema edits unless a shared helper change forces a one-line call-site note (prefer craft-base-only).

**Verification:** (pass/fail matrix above); Admin toast no longer shows false-missing name for the UAT repro payload shape.

## Self-Assessment

**Scope:** `Single-Component` — craft-base normalize in `candidate.py` plus list-item schema validation in `agent.py`; no UI, config schema, or builder changes.

**Conf:** `high` — false-missing reproduced with nested-only `resume_structure.candidate_name`; promote gap and sections-wipe order are explicit in current code; fix reuses existing `_promote` rules.

**Risk:** `Medium` — sits on the craft-base validate path used by paste-resume; wrong overwrite of good top-level fields or incorrect experience coerce would regress parses. Mitigated by known-id-only promote and skip-if-top-level-non-empty rules already in `_promote`.

## Code-rules check

- **Relevant statutes:** schema-and-contracts; agent-payload-contract; error-propagation (Admin toast shows server `data.error`); single normalize-before-validate write path for craft-base.
- **Compliance:** Lift nested section values into the existing required top-level contract rather than weakening schema; keep experience `list` + `items_schema`; do not swallow validation failures.
- **Challenges / exclusions:** No new HTTP route; no `tests/` or bible (Betty); no UI toast rewrite — fixing the server validation path removes the false popup; do not invent candidate fields when truly absent.

## Plan Completeness Checklist

- [x] Every stage has a concrete verification step
- [x] Files Changed table lists all files expected to touch
- [x] No stage depends on a file or function that isn't created in a prior stage or already in the codebase
- [x] Self-assessment Scope/Conf/Risk with justifications
- [x] Scope is AST-1005 only (not parent epic remainder)
- [x] UAT fitness filled from bug Description (parent Description not fetched)
- [x] Code-rules check completed
