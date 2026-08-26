# Estelle coded resume-advice list (Advise resume needs a coded list for clear adherence)

**Linear:** [AST-1507](https://linear.app/astralcareermatch/issue/AST-1507/estelle-coded-resume-advice-list-advise-resume-needs-a-coded-list-for)
**Parent:** [AST-1460](https://linear.app/astralcareermatch/issue/AST-1460/advise-resume-needs-a-coded-list-for-clear-adherence) — Advise resume needs a coded list for clear adherence
**Publish ref:** `origin/sub/AST-1460/AST-1507-estelle-coded-resume-advice-list`

Turn `advise_job_resume` into a coded resume-advice emit: Estelle’s Manage Tasks prompt requires a stable-coded RESUME BRIEF list; config owns section/pattern/artifact keys; core parses and validates that list from Estelle’s **text** response (prompt-enforced, not structured JSON schema); successful hops persist the list as sibling job-artifact metadata for Judith’s downstream adherence (sibling AST-1508). COVER LETTER DIRECTION and ASK CANDIDATE stay uncoded prose. Does **not** own Judith per-code answers, `run_next` order, Approve Artifacts UI, or Resume upshot.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend `TASK_CONFIG["advise_job_resume"]` with coded-advice section/pattern/artifact keys; add `resume_advice` to `JOB_BUILD_ARTIFACT_CLEAR_KEYS` | utils |
| `data/admin/agent_task.json` | Rewrite `advise_job_resume` `user_prompt` RESUME BRIEF block to coded-list contract; leave COVER LETTER DIRECTION + ASK CANDIDATE prose rules unchanged | data/admin |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Whole-file twin of `data/admin/agent_task.json` after prompt edit | docs |
| `src/core/candidate.py` | Parse RESUME BRIEF section; normalize/validate coded items from text; Style D found/recorded when `debug=True` | core |
| `src/core/tracker.py` | Extract/save/persist coded advice list to `job_data.artifacts[resume_advice]`; never merge into resume body | core |
| `src/core/agent.py` | On `advise_job_resume` success path: validate coded list after text unwrap; persist metadata (mirror `draft_job_resume` deviations hook) | core |

**Out of scope (do not touch):** `draft_job_resume` prompt/keys/adherence (sibling Hedy / AST-1508); `deviations` removal (sibling); `run_next`; `tests/**`; UI; builder/HTML; Judith draft validate beyond ensuring resume bodies never receive advice metadata.

## Wire contract (text — prompt-enforced)

Estelle’s response remains **plain text** with three sections (unchanged headers). Only **RESUME BRIEF** becomes a coded list.

**RESUME BRIEF format (one item per line):**

```
[R1] <concrete instruction Judith can act on> — cite: "<verbatim supporting quote>"
[R2] ...
```

Rules enforced in prompt + validate:

- Code = `[R` + positive integer + `]` (e.g. `[R1]`, `[R12]`). Prefix letter `R` and bracket shape come from config (`resume_advice_code_prefix`, `resume_advice_bracket_open`, `resume_advice_bracket_close`).
- Each line after the code bracket must contain non-empty instruction text.
- Citation tail ` — cite: "…"` is **required in the prompt**; validate accepts lines with or without a parseable citation (instruction still required).
- Codes must be **unique** within the hop.
- Section ends at the next top-level header line `COVER LETTER DIRECTION` (exact string from config). Lines before the first coded item after `RESUME BRIEF` may be blank; non-matching non-blank lines inside the section fail validation.

**Persisted artifact shape** (`job_data.artifacts[resume_advice_artifact_key]`):

```json
[
  {"code": "R1", "instruction": "…", "citation": "…"},
  {"code": "R2", "instruction": "…", "citation": ""}
]
```

`citation` is `""` when the line had no parseable cite tail. This list is **metadata only** — never written into `resume_content` or resume section bodies.

⚠️ **Decision:** Stay on **text** response (`response_format` default `"text"`) per parent open question — no new JSON envelope or `response_schema` expansion for advise. Validate runs on the post-unwrap string in `do_task`, not on schema validation.

⚠️ **Decision:** Artifact slot name `resume_advice` (config key `resume_advice_artifact_key`) — sibling to `deviations` / `resume_content`; Hedy’s draft adherence child reads this list without re-parsing Estelle’s raw RESPONSE.

## Stage 1: Config — coded-advice keys + cancel clear membership

**Done when:** `TASK_CONFIG["advise_job_resume"]` carries all keys below; `JOB_BUILD_ARTIFACT_CLEAR_KEYS` includes the same artifact slot literal; module-level asserts tie prefix/bracket keys together; no new inline frozensets of metadata names in core.

1. In `src/utils/config.py`, inside `TASK_CONFIG["advise_job_resume"]` after existing keys, add:

   | Key | Value |
   |-----|-------|
   | `resume_advice_coded_list` | `True` (agent hook gate) |
   | `resume_advice_section_header` | `"RESUME BRIEF"` |
   | `resume_advice_section_end_header` | `"COVER LETTER DIRECTION"` |
   | `resume_advice_code_prefix` | `"R"` |
   | `resume_advice_bracket_open` | `"["` |
   | `resume_advice_bracket_close` | `"]"` |
   | `resume_advice_cite_separator` | `" — cite:"` (split instruction vs citation) |
   | `resume_advice_artifact_key` | `"resume_advice"` |
   | `resume_advice_min_items` | `1` |

2. Append `"resume_advice"` to `JOB_BUILD_ARTIFACT_CLEAR_KEYS` with comment `# AST-1507: same literal as advise_job_resume.resume_advice_artifact_key`.
3. After the config block, add asserts:

   ```python
   _ajr = TASK_CONFIG["advise_job_resume"]
   assert _ajr["resume_advice_artifact_key"] == "resume_advice"
   assert _ajr["resume_advice_code_prefix"] == "R"
   assert isinstance(_ajr["resume_advice_min_items"], int) and _ajr["resume_advice_min_items"] >= 1
   assert "resume_advice" in JOB_BUILD_ARTIFACT_CLEAR_KEYS
   ```

4. Do **not** add keys to `draft_job_resume` in this ticket.

## Stage 2: Manage Tasks prompt — coded RESUME BRIEF only

**Done when:** `advise_job_resume` `user_prompt` instructs the coded RESUME BRIEF line format above; COVER LETTER DIRECTION and ASK CANDIDATE sections retain today’s purpose and uncoded prose shape; HARD RULES block unchanged; `run_next`, cache prompts, agent id, uuids untouched.

1. In `data/admin/agent_task.json`, edit the row with `"task_key": "advise_job_resume"` and `"current": 1`. Change **`user_prompt` only**.
2. Replace the current RESUME BRIEF paragraph:

   > Enumerated, concrete instructions: what to promote, cut, reorder, reframe, each with its citation.

   with explicit coded-list instructions:

   - Header line `RESUME BRIEF` then one line per advised change.
   - Each line: `[R1]`, `[R2]`, … ascending integers, stable for this hop.
   - After the code: concrete instruction Judith can execute (promote/cut/reorder/reframe per role accomplishments only — existing HARD RULES still bind).
   - End each line with ` — cite: "<verbatim quote>"` from base resume, backstory, strengths, priorities, or LinkedIn.
   - No conditional “if they have X” lines (existing rule 3 still applies).
   - Solve Atlas’s #1 objection first (keep that ordering guidance).
3. Leave **COVER LETTER DIRECTION** and **ASK CANDIDATE** section headers and guidance as uncoded prose (ratify/veto thesis; direct questions). Do not require codes in those sections.
4. Do not edit any other `agent_task.json` row in this stage.

## Stage 3: Core parse/validate — extract coded list from text

**Done when:** Given a well-formed Estelle text body, `parse_advise_job_resume_coded_advice(text)` returns a list of dicts; `validate_advise_job_resume_coded_list(text, debug=False)` returns `None`; missing section, zero items, duplicate codes, or bad lines return a clear error string; `debug=True` emits Style D found lines (section found, item count, each code) before persist.

1. In `src/core/candidate.py`, add helpers reading **`TASK_CONFIG["advise_job_resume"]` only** (no hardcoded `"RESUME BRIEF"` / `"R1"` literals in core):

   - `_advise_resume_advice_task_cfg() -> dict` — returns `TASK_CONFIG["advise_job_resume"]`.
   - `_extract_advise_section_text(full_text: str, cfg: dict) -> Optional[str]` — locate text after a line equal to `cfg["resume_advice_section_header"]` (strip/compare case-sensitive whole line) until a line equal to `cfg["resume_advice_section_end_header"]`; return stripped section body or `None` if headers missing.
   - `_parse_advise_coded_line(line: str, cfg: dict) -> Optional[dict]` — if line matches `^[[]R\d+[]]\s+.+` built from cfg bracket/prefix keys, return `{"code": "R<n>", "instruction": str, "citation": str}`:
     - Strip code brackets to produce `code` (e.g. `R1`).
     - Split remainder on `cfg["resume_advice_cite_separator"]` once: left → instruction (strip); right → citation (strip surrounding quotes if present).
     - Return `None` for blank lines or non-matching lines.
   - `parse_advise_job_resume_coded_advice(full_text: str) -> Optional[list[dict]]` — public extract used by validate + tracker:
     - Coerce input: if `full_text` is not a non-empty string, return `None`.
     - Extract section; iterate non-blank lines; parse each; skip blank; **reject** section if any non-blank line fails parse (return `None` — caller maps to validation error).
     - Enforce unique codes; duplicate → validation error path.
     - Return list (may be empty only when section has no non-blank lines).

2. Add `validate_advise_job_resume_coded_list(full_text: str, *, debug: bool = False) -> Optional[str]`:
   - Call parse helper; on `None` section → `"RESUME BRIEF section missing or incomplete"`.
   - On unparseable line inside section → `"RESUME BRIEF line is not a coded advice item: …"` (include line truncated to 120 chars).
   - On duplicate code → `"Duplicate resume advice code: R<n>"`.
   - On item count `< cfg["resume_advice_min_items"]` → `"RESUME BRIEF must include at least one coded advice item"`.
   - On success, when `debug=True`, emit Style D via `get_logger` / `debug_index` + `debug_detail`:
     - `func="candidate.validate_advise_job_resume_coded_list"`
     - `found section=RESUME BRIEF item_count=<n>`
     - one `found code=<code> instruction_chars=<len>` per item
   - Return `None` on success.

3. Do **not** mutate `full_text` in validate (CALLER_RESPONSE for Judith stays the full Estelle body including uncoded sections).

## Stage 4: Persist metadata + agent wiring

**Done when:** Successful `advise_job_resume` hops write `job_data.artifacts.resume_advice` as the parsed list; failed validation fails the hop; cancel-build clears `resume_advice`; resume body extractors never see advice codes; debug persist logs `recorded artifact_key=resume_advice item_count=<n>`.

1. In `src/core/tracker.py`, add (lazy-import-safe, mirror AST-1271 deviations shape):

   - `extract_advise_job_resume_coded_advice(full_text: str) -> Optional[list[dict]]` — delegate to `candidate.parse_advise_job_resume_coded_advice`; return `None` when parse would fail validation (same as absent key semantics for persist: do not write).
   - `save_job_artifact_resume_advice(astral_job_id: str, items: list[dict]) -> None` — `save_job_data(..., {"artifacts": {cfg["resume_advice_artifact_key"]: list(items)}})`.
   - `persist_advise_job_resume_coded_advice(astral_job_id: str, full_text: str) -> bool` — extract; if `None`, return `False`; else save and return `True`.

2. In `_resume_payload_body` (or equivalent resume-body extractor if present): ensure `resume_advice_artifact_key` is **not** treated as resume section content (no change needed if function only walks resume section keys — grep and confirm; if a generic dict walk would ingest unknown keys, add skip via `TASK_CONFIG["advise_job_resume"]["resume_advice_artifact_key"]`).

3. In `src/core/agent.py`:

   **Validate hook** — after the existing block that unwraps `agent_payload` to a string (lines ~2812–2831), before SUCCESS storage:

   ```python
   if (
       task_key == "advise_job_resume"
       and TASK_CONFIG["advise_job_resume"].get("resume_advice_coded_list")
       and isinstance(parsed, str)
       and parsed.strip()
   ):
       from src.core.candidate import validate_advise_job_resume_coded_list
       advice_err = validate_advise_job_resume_coded_list(parsed, debug=debug)
       if advice_err:
           # same failure path as draft_job_resume cat_err: log, store failure block, close hop ledger, return success=False
   ```

   Also handle `isinstance(parsed, str)` after unwrap; if parsed is still a dict with stringifiable content, do **not** add a new coerce path — advise remains text-first.

   **Persist hook** — adjacent to AST-1271 `draft_job_resume` deviations block (~3068):

   ```python
   if task_key == "advise_job_resume" and result.get("success") and index:
       try:
           from src.core.tracker import persist_advise_job_resume_coded_advice
           persisted = persist_advise_job_resume_coded_advice(index, parsed if isinstance(parsed, str) else "")
           if debug and persisted:
               _do_task_debug_logger(debug).debug_detail(
                   f"recorded artifact_key={TASK_CONFIG['advise_job_resume']['resume_advice_artifact_key']} "
                   f"item_count={len(extract…)}"
               )
       except Exception:
           logger.error(..., exc_info=False)  # best-effort; do not fail hop after success
   ```

   Use item count from extract result variable — do not parse twice without need (persist return bool + count or re-use extract output).

4. Do **not** add advise keys to `draft_job_resume` `payload_metadata_keys`. Do **not** change `run_next` or hop transition logic.

## Stage 5: UAT fixture twin sync

**Done when:** `docs/uat-fixtures/AST-756/expected-agent_task.json` is byte-identical to `data/admin/agent_task.json`.

1. After Stage 2:

   ```bash
   cp data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json
   cmp -s data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json && echo OK
   ```

2. Whole-file `cp` only — no surgical dual-edit.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Review (build stub)

- **Publish ref:** `sub/AST-1460/AST-1507-estelle-coded-resume-advice-list`
- **Tip:** `5e9759306cccef89e510de944df810f37f0c6c82`
- **Stages:** S1 config keys + clear slot; S2 coded RESUME BRIEF prompt; S3 text parse/validate; S4 tracker persist + do_task validate/persist hooks; S5 UAT fixture twin

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric.v1
**Ticket:** AST-1507
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1460/AST-1507-estelle-coded-resume-advice-list` @ `aed09ec2ed439ed5474bf1a2571336874d66aa44`

## Traceability

AC1→S2–S4; AC2→S3–S4 (metadata-only persist); AC3→S2; AC4→S3–S4 (Style D validate + persist); AC5→S4 + explicit AST-1270 boundary (no draft nest/body change).

## Findings

### discuss

- **Location:** Stage 4 — `agent.py` validate hook  
  **Finding:** Gate includes `parsed.strip()`; whitespace-only or empty string skips validation while `resume_advice_coded_list` is True.  
  **Recommendation:** When the gate is on and `isinstance(parsed, str)`, always call `validate_advise_job_resume_coded_list` (let min-items / missing-section errors fail the hop).

- **Location:** Stage 4 — persist debug pseudo-code  
  **Finding:** `item_count={len(extract…)}` is an ellipsis placeholder.  
  **Recommendation:** At build, reuse the extract result from `persist_advise_job_resume_coded_advice` (or return count) so debug does not parse twice.

### acceptable

- **Location:** Plan structure  
  **Finding:** No `## Self-Assessment`; `## Estimate` (`Confirm Chuckles estimate: 3 — agree`) satisfies current `plan-child` gate.  
  **Recommendation:** None — optional Scope/Conf note for Radia later.

- **Location:** Parent Architectural definition — new pattern flag  
  **Finding:** Daisy-chain coded advice → per-code adherence is consumer work (sibling AST-1508); this child correctly owns advise emit only.  
  **Recommendation:** None.

- **Location:** Stage 4 step 2 — `_resume_payload_body`  
  **Finding:** Confirm-only grep; advise is text → `job_data.artifacts`, not draft body extraction.  
  **Recommendation:** Grep-and-confirm as staged; no body-path change expected.

## R6 checklist (summary)

Definition fidelity: files and stages match child `## Scope`; draft keys/rows explicitly out. Layer/config/placement: utils keys, core validate/persist, seed + fixture twin — all conform. Pattern `pattern.config.config-block` cited and followed (AST-1271 deviations mirror). DRY: tracker delegates to `candidate.parse_*` — appropriate. Boundaries: no `run_next`, no `tests/**`, no Judith adherence.

**Considered (in-session):** 18 universal (orchestration/git — conform); scoped product statutes on touched layers/paths — conform, including cited config/no-hardcoded-sets/in-scope-only/do-task-delegation/seed trio/run-next authority/test-tree ban/debug-contract-gated/dry/names-not-ticket-ids/entity-agent-responses-latest-only/import-direction/logging.

## Radia review

[code-rubric] revision=2  
**Rubric:** code-rubric.v2  
**Ticket:** AST-1507  
**Publish ref:** `origin/sub/AST-1460/AST-1507-estelle-coded-resume-advice-list` @ `23f3ab795147e61dd5236abc87808708253af505`  
**Overall:** DISCUSS

## Findings

### discuss

- **Location:** `merge-tests(AST-1507)` publish tip — test tree + bible bundles AST-1505/AST-1498 deltas while product `src/` is AST-1507-only.  
  **Finding:** Sibling manifests would fail on this tip until sibling product branches land.  
  **Recommendation:** Flag for merge-child / ftr rollup — not a product defect for AST-1507; manifest-only green is expected.

### advisory

- **Location:** `src/core/candidate.py` — `_advise_coded_line_re(cfg)` recompiled per line — optional cache later.  
- **Location:** Error strings hardcode `"RESUME BRIEF"` — matches plan wire contract.

Product implementation matches all five plan stages; Joan discuss items addressed. Boundaries held.

## Resolution

**Date:** 2026-08-26  
**Review ref:** Radia `[code-rubric] revision=2` @ `23f3ab79` — **Overall: DISCUSS** (no fix-now).

- **Fix-now:** none — product matches plan; Betty manifest (17 tests) green on publish tip.
- **Discuss (sibling tests on merge-tests tip):** acknowledged — AST-1505/AST-1498 test deltas bundled on shared `origin/tests` line; not an AST-1507 product defect; merge-child/ftr rollup concern only.
- **Advisory:** `_advise_coded_line_re` per-line compile — acceptable; no change this pass.
- **§9a:** `origin/sub/AST-1460/AST-1507-estelle-coded-resume-advice-list` merges cleanly into `origin/dev` (2026-08-26).

