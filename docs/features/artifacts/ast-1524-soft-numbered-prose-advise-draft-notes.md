# Soft numbered-prose advise + draft notes prompts (Advise resume needs a coded list for clear adherence)

**Linear:** [AST-1524](https://linear.app/astralcareermatch/issue/AST-1524/soft-numbered-prose-advise-draft-notes-prompts-advise-resume-needs-a-coded)
**Parent:** [AST-1460](https://linear.app/astralcareermatch/issue/AST-1460/advise-resume-needs-a-coded-list-for-clear-adherence) — Advise resume needs a coded list for clear adherence (redefined: revert + soft prompts)
**Publish ref:** `origin/sub/AST-1460/AST-1524-soft-numbered-prose-advise-draft-notes`

After sibling **AST-1523** restores pre-hard-contract product + baseline prompts with freeform `notes`, this ticket soft-tightens **Manage Tasks prompt text only**: Estelle’s RESUME BRIEF becomes a readable numbered prose list (A/B/C-style); Judith’s draft prompt asks her to use freeform `notes` to say whether/how she incorporated each listed item. **No** new config keys, validation, normalize, persist hooks, or JSON schema beyond the existing `notes: string[]` sibling. COVER LETTER DIRECTION and ASK CANDIDATE stay uncoded.

**Build prerequisite:** Merge sibling **AST-1523** (`origin/sub/AST-1460/AST-1523-revert-hard-coded-advice-adherence`) into this publish ref before **build-child** — baseline prompts must show `"notes"` (not `advice_adherence`) and core must have no `resume_advice_*` / `advice_adherence_*` keys. **Prompt merge:** Preserve AST-1465 accomplishments wording (`ordered **array of strings** — bare text, no list-marker prefixes`); do not reintroduce instructional `•`/`-`/`*` glyphs.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `data/admin/agent_task.json` | Rewrite `advise_job_resume` + `draft_job_resume` `user_prompt` only (numbered prose + notes response) | data/admin |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Whole-file twin after prompt edits | docs |

**Out of scope (do not touch):** `src/utils/config.py`, `src/core/candidate.py`, `src/core/tracker.py`, `src/core/agent.py`, `run_next`, `tests/**`, UI/builder/HTML.

## Wire contract (prompt-only — no validation)

**Estelle (`advise_job_resume`) — RESUME BRIEF section shape (prose text, not JSON):**

```
RESUME BRIEF
A. <concrete instruction Judith can act on> — cite: "<verbatim quote>"
B. <next instruction> — cite: "..."
C. ...
```

Rules in prompt (not enforced in code):

- Use letter labels **A.**, **B.**, **C.**, … ascending for this hop (readable list — not `[R#]` machine codes).
- Each item: promote/cut/reorder/reframe per role accomplishments only (existing HARD RULES still bind).
- Citation tail ` — cite: "…"` encouraged; Estelle may omit only when no quote applies (route to ASK CANDIDATE instead).
- No conditional “if they have X” lines (existing rule 3 still applies).
- Solve Atlas’s #1 objection first (keep existing ordering guidance).

**Judith (`draft_job_resume`) — freeform `notes` response (existing JSON envelope):**

```json
"notes": [
  "A: incorporated by …",
  "B: skipped because …",
  "General: …"
]
```

Rules in prompt (not enforced in code):

- `notes` remains a **string array** sibling of nested `resume` — same metadata slot AST-1523 restored.
- Judith must address **each** lettered RESUME BRIEF item in her notes (incorporated how, or skipped and why).
- Skips for unsupported materials still belong in `notes`, not in resume body.
- No `advice_adherence` objects, no per-code status schema, no new payload keys.

⚠️ **Decision:** Use **A./B./C.** letter labels (not `[R1]`) — matches parent “numbered IN PROSE” brief and avoids confusion with the withdrawn hard-code contract.

⚠️ **Decision:** Do **not** add prompt language that implies validation will reject missing notes entries — soft tighten only; hop success stays on existing resume whitelist + schema, not note completeness.

## Stage 1: Estelle prompt — numbered prose RESUME BRIEF

**Done when:** `advise_job_resume` `user_prompt` RESUME BRIEF block instructs A./B./C. prose list; COVER LETTER DIRECTION and ASK CANDIDATE blocks unchanged in purpose and uncoded shape; no other rows edited.

1. In `data/admin/agent_task.json`, edit the row with `"task_key": "advise_job_resume"` and `"current": 1`. Change **`user_prompt` only**.
2. Replace the current RESUME BRIEF paragraph (post-AST-1523 baseline):

   > Enumerated, concrete instructions: what to promote, cut, reorder, reframe, each with its citation. Reframing means new emphasis on true content, not new content. Solve Atlas's #1 objection first.

   with numbered-prose instructions:

   - Header line `RESUME BRIEF` then one item per advised change.
   - Each line starts with **A.**, **B.**, **C.**, … (ascending letters for this hop).
   - After the label: concrete instruction Judith can execute (promote/cut/reorder/reframe accomplishments per role — HARD RULES still bind).
   - End each line with ` — cite: "<verbatim quote>"` when support exists; otherwise route unsupported claims to ASK CANDIDATE, not RESUME BRIEF.
   - No conditional “if {$THEY} has X” lines (rule 3 unchanged).
   - Solve Atlas’s #1 objection first.
3. Leave **COVER LETTER DIRECTION** and **ASK CANDIDATE** section headers and guidance **unchanged** (no coded-adherence contract for those sections).
4. Do **not** edit `draft_job_resume` or any other row in this stage.

## Stage 2: Judith prompt — notes respond to Estelle’s list

**Done when:** `draft_job_resume` `user_prompt` asks Judith to use freeform `notes` to respond to each lettered RESUME BRIEF item; example JSON shows `"notes": [...]` only; experience / nested `resume` / job-array rules unchanged; AST-1465 bare-string accomplishments wording preserved.

1. In `data/admin/agent_task.json`, edit the row with `"task_key": "draft_job_resume"` and `"current": 1`. Change **`user_prompt` only**.
2. Replace the skip/notes rule (post-AST-1523 baseline):

   > If a brief instruction lacks support in {$FIRST_NAME}'s materials, skip it and record it under notes. Do not improvise a compromise claim.

   with:

   - For **each** lettered item in Estelle’s RESUME BRIEF (A., B., C., …), add a note saying whether and how you incorporated it, or why you did not (unsupported in materials, conflicts with these rules, etc.).
   - Use the existing **`notes`** string array — freeform prose entries, not a structured adherence object.
   - Do not improvise a compromise claim.
3. Add one sentence before the JSON example block:

   > Your `notes` should make it obvious you considered every RESUME BRIEF item — one entry may cover multiple letters if that reads naturally.

4. Ensure the example JSON tail remains:

   ```json
   "notes": ["A: how incorporated or why skipped", "B: …"]
   ```

   — **not** `advice_adherence`, **not** `deviations`.
5. Preserve the Experience bullet with `ordered **array of strings** — bare text, no list-marker prefixes` (AST-1465 — do not reintroduce `` `•`/`-`/`*` `` instructional glyphs).
6. Do **not** edit `advise_job_resume` or any other row in this stage.

## Stage 3: UAT fixture twin sync

**Done when:** `docs/uat-fixtures/AST-756/expected-agent_task.json` is byte-identical to `data/admin/agent_task.json`.

1. After Stages 1–2:

   ```bash
   cp data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json
   cmp -s data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json && echo OK
   ```

2. Whole-file `cp` only — no surgical dual-edit.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Review

**Publish ref:** `origin/sub/AST-1460/AST-1524-soft-numbered-prose-advise-draft-notes` @ `0c7492dd`
**Built:** Merged AST-1523 prerequisite; Stages 1–3 — Estelle A./B./C. RESUME BRIEF prose; Judith `notes` respond to lettered items; UAT twin sync. Prompt-only — no `src/**` changes this ticket.


[plan-rubric]
**Rubric:** plan-rubric.v1
**Ticket:** AST-1524
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1460/AST-1524-soft-numbered-prose-advise-draft-notes` @ `ba19403ccc9032e1bd757fc093b668659f94cd2e`

## Traceability

AC3→S1; AC4→S2; AC5→S1–S2 (COVER LETTER / ASK CANDIDATE untouched); AC6→S3. Parent AC1–2 N/A — sibling AST-1523 revert.

## Findings

### discuss

- **Location:** Build prerequisite (header)  
  **Finding:** Plan assumes AST-1523 baseline prompts (`notes`, no hard keys); epic tip still carries `advice_adherence` / coded-contract wording.  
  **Recommendation:** Chuckles/merge-child must land AST-1523 before build-child; engineer should verify Stage 2 “replace” target text matches post-1523 baseline, not current tip.

- **Location:** Wire contract / Stage 2  
  **Finding:** Prompt asks Judith to address every A./B./C. item, but decision correctly states no new validation — hop success stays on existing whitelist only.  
  **Recommendation:** None for build; ensure prompt prose does not imply machine rejection of incomplete `notes` (already flagged in plan).

- **Location:** Out of scope — `tests/**`  
  **Finding:** AST-1507/1508 prompt-assertion tests on ftr may still expect hard-contract or pre-soft RESUME BRIEF copy after this lands.  
  **Recommendation:** Betty alignment on ftr rollup if manifest fails — not engineer scope; optional Code Complete flag if grep hits `test_advise_prompt` / AST-1349 contract classes.

### acceptable

- **Location:** Files Changed  
  **Finding:** Prompt-only footprint (`agent_task.json` + UAT twin) matches child Scope and “no new schema/validation/artifact keys” boundary.  
  **Recommendation:** None.

- **Location:** Stage 2 step 5 — AST-1465  
  **Finding:** Bare-string accomplishments / no bullet-glyph instruction preserved — adjacency with Done AST-1465.  
  **Recommendation:** None.

- **Location:** Decision — A./B./C. vs `[R#]`  
  **Finding:** Explicitly avoids withdrawn hard-code contract; aligns with parent “numbered in prose” direction.  
  **Recommendation:** None.

## R6 checklist (summary)

Definition fidelity: implements soft prompt child only; no core/config creep. Layer compliance: data/admin + docs only. Seed statutes: repo JSON + fixture twin whole-file `cp` — conform. In-scope-only: no `src/**` touch. Pattern: no config-block changes needed (prompt-only). DRY/scope: two rows, three stages — proportionate.

**Considered (in-session):** 18 universal (orchestration/git — conform); cited scoped seed/in-scope/run-next/test-tree-ban — conform.

context_tokens≈68000

## Radia review

[code-rubric] revision=2  
**Rubric:** code-rubric.v2  
**Ticket:** AST-1524  
**Publish ref:** `origin/sub/AST-1460/AST-1524-soft-numbered-prose-advise-draft-notes` @ `2ceb2cff69c1371789e25e58b7745a50bc3f99da`  
**Overall:** CLEAN

## Statutes checked

Full statute sweep — all scoped/universal statutes conform or not-applicable. Prompt-only ticket; no `src/**` changes on AST-1524 commits.

## Pattern conformance

none cited — prompt-only ticket

## Plan adherence

All three stages delivered (S1 Estelle A./B./C., S2 Judith notes, S3 UAT twin). AST-1523 prerequisite merged.

## Findings

### advisory

- Draft prompt asks Judith to address each lettered item — soft wording, no machine rejection implied.
- Publish ref composite bundles AST-1523 revert + AST-1524 prompts — expected for epic rollup.

No fix-now / discuss findings.

## What's solid

- Surgical prompt edit: one commit, two files.
- Advise: A./B./C. labels, no `[R#]` / `advice_adherence`.
- Draft: lettered-notes contract, `notes` string array.
- Betty manifest aligned; COVER LETTER / ASK CANDIDATE uncoded.

context_tokens≈75000

## Radia review

[code-rubric] revision=2  
**Rubric:** code-rubric.v2  
**Ticket:** AST-1524  
**Publish ref:** `origin/sub/AST-1460/AST-1524-soft-numbered-prose-advise-draft-notes` @ `2ceb2cff69c1371789e25e58b7745a50bc3f99da`  
**Overall:** CLEAN

## Statutes checked

Full statute sweep — all scoped/universal statutes conform or not-applicable. Prompt-only ticket; no `src/**` changes on AST-1524 commits.

## Pattern conformance

none cited — prompt-only ticket

## Plan adherence

All three stages delivered (S1 Estelle A./B./C., S2 Judith notes, S3 UAT twin). AST-1523 prerequisite merged.

## Findings

### advisory

- Draft prompt asks Judith to address each lettered item — soft wording, no machine rejection implied.
- Publish ref composite bundles AST-1523 revert + AST-1524 prompts — expected for epic rollup.

No fix-now / discuss findings.

## What's solid

- Surgical prompt edit: one commit, two files.
- Advise: A./B./C. labels, no `[R#]` / `advice_adherence`.
- Draft: lettered-notes contract, `notes` string array.
- Betty manifest aligned; COVER LETTER / ASK CANDIDATE uncoded.

context_tokens≈75000
