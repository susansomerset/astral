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
