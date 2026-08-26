# Judith per-code advice adherence (Advise resume needs a coded list for clear adherence)

**Linear:** [AST-1508](https://linear.app/astralcareermatch/issue/AST-1508/judith-per-code-advice-adherence-advise-resume-needs-a-coded-list-for)
**Parent:** [AST-1460](https://linear.app/astralcareermatch/issue/AST-1460/advise-resume-needs-a-coded-list-for-clear-adherence) — Advise resume needs a coded list for clear adherence
**Publish ref:** `origin/sub/AST-1460/AST-1508-judith-per-code-advice-adherence`

Judith’s `draft_job_resume` hop answers **every** Estelle resume-advice code with how the item was incorporated or why it was skipped; config owns adherence metadata/artifact keys; core validates against `job_data.artifacts.resume_advice` (sibling AST-1507); adherence persists as sibling job metadata and **replaces** the freeform `deviations: string[]` contract (AST-1270/1271). Resume section bodies never receive adherence structures. Does **not** re-author Estelle’s coded-list emit, Approve Artifacts UI, Resume upshot, or hop-order rewiring.

**Build prerequisite:** Merge sibling **AST-1507** (`origin/sub/AST-1460/AST-1507-estelle-coded-resume-advice-list`) into this publish ref before **build-child** Stage 1 — Judith validation reads `TASK_CONFIG["advise_job_resume"]["resume_advice_artifact_key"]` and the parsed list shape AST-1507 persists. **Prompt merge:** If `draft_job_resume` prompt on this branch diverges from **AST-1465** (bullet-glyph omit), preserve AST-1465 wording when editing the deviations → adherence block.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend `TASK_CONFIG["draft_job_resume"]` with per-code adherence keys; **replace** `deviations` metadata/artifact/clear-key literals with `advice_adherence` | utils |
| `data/admin/agent_task.json` | Rewrite `draft_job_resume` `user_prompt` only — per-code adherence JSON contract; remove `deviations` | data/admin |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Whole-file twin of `data/admin/agent_task.json` after prompt edit | docs |
| `src/core/candidate.py` | Normalize/validate draft per-code adherence; keep resume-body whitelist free of adherence field | core |
| `src/core/tracker.py` | Load expected codes from `resume_advice` artifact; extract/save/persist `advice_adherence`; replace deviations helpers/call sites | core |
| `src/core/agent.py` | Wire adherence validate (post schema + resume whitelist) and success-path persist on `draft_job_resume` | core |

**Out of scope (do not touch):** `advise_job_resume` prompt/parse/persist (AST-1507); `run_next`; `tests/**`; UI/builder/HTML; COVER LETTER DIRECTION / ASK CANDIDATE sections (unchanged — not in draft prompt today).

## Wire contract (JSON — replaces deviations)

Judith’s response stays the existing nested envelope; **`deviations` is removed**; sibling metadata becomes **`advice_adherence`**.

**Payload shape** (inside `agent_payload`, sibling of `resume`):

```json
"advice_adherence": [
  {"code": "R1", "status": "applied", "note": "How this item was incorporated in the resume"},
  {"code": "R2", "status": "skipped", "note": "Why this item was not applied"}
]
```

Rules enforced in prompt + validate (status literals from config):

- **One object per code** in `job_data.artifacts.resume_advice` (Estelle’s persisted coded list from AST-1507). Codes must match exactly — no extras, no omissions, no duplicates.
- `status` must be config `advice_adherence_status_applied` (`"applied"`) or `advice_adherence_status_skipped` (`"skipped"`).
- `note` is a non-empty string in both cases: applied → how incorporated; skipped → why not (materials conflict, unsupported claim, etc.).
- `code` matches advise prefix shape (e.g. `R1`, `R2`) — same strings as `resume_advice[].code`.

**Persisted artifact shape** (`job_data.artifacts[advice_adherence_artifact_key]`): same list as payload (normalized dicts). Metadata only — never merged into `resume_content` or resume section bodies.

⚠️ **Decision:** **Replace** `deviations` (parent open question #3) — remove `deviations` from `payload_metadata_keys`, `deviations_artifact_key`, and `JOB_BUILD_ARTIFACT_CLEAR_KEYS`; do not dual-write or accept both keys on draft.

⚠️ **Decision:** Expected codes come from **`job_data.artifacts.resume_advice`** (durable advise artifact), not re-parsing `CALLER_RESPONSE` at validate time — matches AST-1507 persist contract and survives mid-chain latest-RESPONSE reads.

⚠️ **Decision:** Missing or empty `resume_advice` on the job → **fail** draft validation with a clear error (`advise_job_resume must run first`) rather than optional adherence — parent AC #2 requires an answer per code.

## Stage 1: Config — adherence keys; retire deviations on draft

**Done when:** `TASK_CONFIG["draft_job_resume"]` names adherence metadata/artifact/status literals; `deviations` is gone from draft config and `JOB_BUILD_ARTIFACT_CLEAR_KEYS`; asserts tie artifact key to clear-key tuple; no new inline frozensets of metadata names in core.

1. In `src/utils/config.py`, inside `TASK_CONFIG["draft_job_resume"]`:

   - **Remove** `"deviations"` from `payload_metadata_keys` and remove `"deviations_artifact_key"`.
   - **Add** to `payload_metadata_keys` tuple: `"advice_adherence"` (replace `"deviations"` slot — keep other keys unchanged).
   - **Add** keys:

     | Key | Value |
     |-----|-------|
     | `advice_adherence_required` | `True` (agent validate hook gate) |
     | `advice_adherence_artifact_key` | `"advice_adherence"` |
     | `advice_adherence_status_applied` | `"applied"` |
     | `advice_adherence_status_skipped` | `"skipped"` |
     | `advice_adherence_code_key` | `"code"` |
     | `advice_adherence_status_key` | `"status"` |
     | `advice_adherence_note_key` | `"note"` |

2. In `JOB_BUILD_ARTIFACT_CLEAR_KEYS`: **remove** `"deviations"`; **add** `"advice_adherence"` with comment `# AST-1508: same literal as draft_job_resume.advice_adherence_artifact_key`.
3. After the block, add asserts:

   ```python
   _djr = TASK_CONFIG["draft_job_resume"]
   assert _djr["advice_adherence_artifact_key"] == "advice_adherence"
   assert "deviations" not in _djr["payload_metadata_keys"]
   assert "advice_adherence" in _djr["payload_metadata_keys"]
   assert "advice_adherence" in JOB_BUILD_ARTIFACT_CLEAR_KEYS
   assert "deviations" not in JOB_BUILD_ARTIFACT_CLEAR_KEYS
   ```

4. Do **not** add keys to `TASK_CONFIG["advise_job_resume"]` in this ticket.

## Stage 2: Manage Tasks prompt — per-code adherence (draft row only)

**Done when:** `draft_job_resume` `user_prompt` requires `advice_adherence` with one entry per Estelle `[R#]` code; skip/deviation prose references per-code accountability; example JSON matches wire contract; experience / job-array / nested `resume` rules unchanged; no edits to other rows.

1. In `data/admin/agent_task.json`, edit the row with `"task_key": "draft_job_resume"` and `"current": 1`. Change **`user_prompt` only**.
2. Replace the deviations rule:

   > If a brief instruction lacks support in {$FIRST_NAME}'s materials, skip it and record it under deviations.

   with: for **each** coded item in Estelle’s RESUME BRIEF (`[R1]`, `[R2]`, …), Judith must emit one `advice_adherence` object — `status: "applied"` with how she incorporated it, or `status: "skipped"` with why not (unsupported in materials, conflicts with HARD RULES, etc.). No freeform skip list outside per-code entries.
3. Replace the example JSON tail — remove `"deviations": [...]`; add `"advice_adherence": [{"code": "R1", "status": "applied|skipped", "note": "..."}, ...]` with a one-line note that **every** RESUME BRIEF code must appear exactly once.
4. Keep COVER LETTER DIRECTION / ASK CANDIDATE **out of scope** (they are not in this prompt today — do not add coded adherence for them).
5. Preserve any AST-1465 bullet-glyph omit wording already on the branch when editing bullets prose — do not reintroduce `•`/`-`/`*` marker instructions.
6. Do not edit `advise_job_resume` or any other row in this stage.

## Stage 3: Core normalize/validate — per-code adherence

**Done when:** Given expected codes from `resume_advice` artifact and a well-formed payload, `validate_draft_job_resume_advice_adherence` returns `None`; wrong count, unknown code, bad status, empty note, or missing key returns a clear error string; normalize coerces list shape before validate; `debug=True` emits Style D found lines for expected codes and each adherence row; resume whitelist still rejects adherence keys as section bodies.

1. In `src/core/candidate.py`, add helpers reading **`TASK_CONFIG["draft_job_resume"]` only** for field/status names (expected codes passed in — no hardcoded `"R1"` / `"applied"` literals in core):

   - `_draft_advice_adherence_task_cfg() -> dict`
   - `normalize_draft_job_resume_advice_adherence(parsed: dict) -> None` — idempotent:
     - Locate envelope (`agent_payload` or flat dict) same as existing normalize.
     - If `advice_adherence` absent, return.
     - Coerce to `list[dict]`; drop non-dict entries; strip string fields for `code`, `status`, `note` using config key names.
     - Write normalized list back on envelope.
   - Call `normalize_draft_job_resume_advice_adherence(parsed)` at end of `normalize_draft_job_resume_agent_payload` (after nest unwrap / alias pass).

2. Add `validate_draft_job_resume_advice_adherence(parsed: dict, expected_codes: list[str], *, debug: bool = False) -> Optional[str]`:
   - Run normalize helper first.
   - Read envelope; **`advice_adherence` key must be present** (absent → `"advice_adherence is required on draft_job_resume"`).
   - Parse list; each item must be dict with non-empty `code`, `status` ∈ `{applied, skipped}` from config, non-empty `note`.
   - Build set of returned codes; compare to `expected_codes`:
     - Missing code → `"Missing advice adherence for code: R<n>"`
     - Extra code → `"Unknown advice adherence code: R<n>"`
     - Duplicate → `"Duplicate advice adherence code: R<n>"`
   - On success with `debug=True`, Style D via `logger.set_debug_flag` + `debug_index` / `debug_detail`:
     - `func="candidate.validate_draft_job_resume_advice_adherence"`
     - `found expected_codes=<comma-separated>`
     - per row: `found code=<code> status=<status> note_chars=<len>`

3. Confirm `validate_draft_job_resume_payload` still treats `advice_adherence` as metadata via updated `payload_metadata_keys` (no plan change if tuple already gates it — grep and fix only if `deviations` was hardcoded anywhere in candidate).

4. Do **not** import `tracker` from `candidate.py` — expected codes are supplied by caller.

## Stage 4: Tracker load + persist; agent wiring

**Done when:** Successful `draft_job_resume` hops write `job_data.artifacts.advice_adherence`; failed adherence validation fails the hop; cancel-build clears `advice_adherence`; `_resume_payload_body` never ingests adherence; deviations extract/persist paths are replaced (not duplicated); debug persist logs `recorded artifact_key=advice_adherence item_count=<n>`.

1. In `src/core/tracker.py`:

   - Add `get_job_resume_advice_codes(astral_job_id: str) -> tuple[Optional[list[str]], Optional[str]]`:
     - `job = get_job(astral_job_id)`; if missing → `(None, "Job not found")`.
     - Read `artifacts[TASK_CONFIG["advise_job_resume"]["resume_advice_artifact_key"]]`.
     - If key absent or not a non-empty list → `(None, "No coded resume advice on job; advise_job_resume must run first")`.
     - Extract `str(item["code"]).strip()` for each dict item with non-empty code; if any item lacks code → `(None, "resume_advice artifact has invalid item")`.
     - Return `(codes, None)`.

   - Add (mirror former deviations shape, config-key driven):

     ```python
     def extract_draft_job_resume_advice_adherence(parsed: Any) -> Optional[list[dict]]:
     def save_job_artifact_advice_adherence(astral_job_id: str, items: list[dict]) -> None:
     def persist_draft_job_resume_advice_adherence(astral_job_id: str, parsed: Any) -> bool:
     ```

     - Extract uses `advice_adherence_artifact_key` from draft config; absent key → `None` (no write); present empty list → write `[]`.
     - Normalize via `candidate.normalize_draft_job_resume_advice_adherence` before read if parsed is dict.

   - **Remove** (or fully replace call sites, leave no live deviations draft path): `extract_draft_job_resume_deviations`, `save_job_artifact_deviations`, `persist_draft_job_resume_deviations`.

   - In `persist_job_artifact_from_parsed`: replace `persist_draft_job_resume_deviations(...)` call with `persist_draft_job_resume_advice_adherence(...)` (still ungated on `allow_resume`).

   - Confirm `_resume_payload_body` skips `advice_adherence` via `payload_metadata_keys` (same as former `deviations` — grep; add skip only if a gap exists).

2. In `src/core/agent.py`:

   **Validate hook** — immediately after existing `validate_draft_job_resume_payload` block (~2744–2767), before grade validation:

   ```python
   if (
       task_key == "draft_job_resume"
       and task_config.get("advice_adherence_required")
       and index
   ):
       from src.core.tracker import get_job_resume_advice_codes
       from src.core.candidate import validate_draft_job_resume_advice_adherence

       expected, load_err = get_job_resume_advice_codes(index)
       adherence_err = load_err or validate_draft_job_resume_advice_adherence(
           parsed, expected or [], debug=debug
       )
       if adherence_err:
           # same failure path as cat_err (log, store failure block, close hop ledger, return success=False)
   ```

   Duplicate the same block at the post-decode validation site (~2923) where `validate_draft_job_resume_payload` runs today.

   **Persist hook** — replace AST-1271 deviations block (~3068):

   ```python
   if task_key == "draft_job_resume" and result.get("success") and index:
       try:
           from src.core.tracker import persist_draft_job_resume_advice_adherence
           if persist_draft_job_resume_advice_adherence(index, parsed):
               if debug:
                   # Style D recorded line with artifact_key + item_count from extract result
       except Exception:
           logger.error(..., exc_info=False)  # best-effort; do not fail hop after success
   ```

3. Do **not** change advise hooks (AST-1507). Do **not** change `run_next`.

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

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric.v1
**Ticket:** AST-1508
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1460/AST-1508-judith-per-code-advice-adherence` @ `a138e5a70c41efc96ae4dd46fba9181c4372928e`

## Traceability

AC2→S2–S4; AC3→S3–S4 (metadata via `payload_metadata_keys` + `_resume_payload_body`); AC4→S2 (draft prompt only; COVER LETTER / ASK CANDIDATE not in row); AC5→S3–S4 (Style D validate + persist); AC6→S3–S4 (nest unwrap unchanged; adherence as sibling metadata). Parent AC1 N/A — sibling AST-1507.

## Findings

### discuss

- **Location:** Stage 4 — `agent.py` validate hook  
  **Finding:** Gate requires truthy `index`; without it, adherence validation is skipped while `advice_adherence_required` is True.  
  **Recommendation:** Treat missing `index` on `draft_job_resume` as a validation failure (same bar as `get_job_resume_advice_codes` load errors), not a silent skip.

- **Location:** Stage 4 — persist debug pseudo-code  
  **Finding:** `item_count` line is an ellipsis placeholder.  
  **Recommendation:** Reuse extract result from `persist_draft_job_resume_advice_adherence` (or return count) — avoid a second parse for Style D.

- **Location:** Stage 1 — `JOB_BUILD_ARTIFACT_CLEAR_KEYS`  
  **Finding:** Removing `"deviations"` means cancel-build stops clearing legacy `deviations` artifacts on in-flight jobs.  
  **Recommendation:** Acceptable per parent OQ #3 (replace); note for UAT that old slot may linger until manual cleanup or a later migration ticket.

- **Location:** Parent Architectural definition — new pattern flag  
  **Finding:** Daisy-chain coded advice → per-code adherence has no `canon/patterns/**` `proposed` file yet; this child is the consumer half.  
  **Recommendation:** None for build — Archie catalog promotion remains out of band; plan shape matches the flagged contract.

- **Location:** Stage 3 step 3 / Stage 4  
  **Finding:** Plan grep-fixes `deviations` hardcoding in `candidate.py` only; product `src/` also has deviations in `config.py`, `tracker.py`, `agent.py` (all staged).  
  **Recommendation:** At build, repo-wide `src/` grep for `deviations` stragglers beyond the six planned files.

### acceptable

- **Location:** Build prerequisite (header)  
  **Finding:** AST-1507 merge before `build-child` Stage 1 is required for `resume_advice_artifact_key` + artifact shape — explicitly documented, not a plan defect.  
  **Recommendation:** Chuckles/merge-child enforces ordering; Joan does not block on sibling plan state.

- **Location:** AST-1465 prompt-merge note  
  **Finding:** Stage 2 step 5 preserves bullet-glyph omit wording when present — good adjacency hygiene.  
  **Recommendation:** None.

- **Location:** Plan structure  
  **Finding:** No `## Self-Assessment`; `## Estimate` (`Confirm Chuckles estimate: 3 — agree`) satisfies current `plan-child` gate.  
  **Recommendation:** None.

- **Location:** Expected codes source  
  **Finding:** `job_data.artifacts.resume_advice` (not CALLER_RESPONSE re-parse) aligns with `astral.batch.entity-agent-responses-latest-only` and AST-1507 persist contract.  
  **Recommendation:** None.

## R6 checklist (summary)

Definition fidelity: implements child Scope only; deviations replace matches parent OQ #3; no advise-row re-authoring. Layer/config: utils keys + draft metadata tuple; core validate/persist; seed + fixture twin. Pattern `pattern.config.config-block` followed. DRY: mirrors AST-1271 deviations extract/persist shape. Boundaries: no UI, no `tests/**`, no `run_next`, AST-1465 merge note only.

**Considered (in-session):** 18 universal (orchestration/git — conform); scoped product statutes on touched layers/paths — conform, including cited config/no-hardcoded-sets/in-scope-only/do-task-delegation/seed trio/debug-contract-gated/test-tree ban/entity-agent-responses-latest-only/import-direction/logging.
