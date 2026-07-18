# UAT: Get rubric Save still failing (Do/Like OK)

**Parent:** [AST-900 — craft get rubric did not populate the rubric content for candidate](https://linear.app/astralcareermatch/issue/AST-900/craft-get-rubric-did-not-populate-the-rubric-content-for-candidate)

**Linear:** [AST-906](https://linear.app/astralcareermatch/issue/AST-906/uat-get-rubric-save-still-failing-dolike-ok)

**Publish ref:** `origin/sub/AST-900/AST-906-uat-get-rubric-save-still-failing`

**Summary (FIX-UAT):** On `/artifacts/get_job_criteria` for `karfo`, Get criteria can appear for review but **Save still fails**, while Do/Like Save appear to work. AST-904 already surfaces the server error toast and re-stashes on failure — it did **not** change grade-table validation. This ticket fixes the Get Save reject itself so a successful Generate → review → Save path persists Get vectors the same way Do/Like do. Empty-only recovery (AST-905) stays untouched.

---

## Root cause (code + UAT)

| Fact | Implication |
|------|-------------|
| Save path: `normalize_rubric_artifacts_on_save` → `ensure_criterion_grade_table` → `parse_trailing_grade_table_lines` → then `sync_rubric_vectors_from_criteria` | Any criterion that fails trailing grade-table grammar → `ValueError` → HTTP 400 before vectors write. |
| Grammar requires **≥2 real newline-separated** trailing lines matching `A\|B\|C\|D\|E\|F\|X` + `==`/`=`/`:` | One physical line (even if it contains the characters `\` + `n` + more grades) fails with *"rubric text must end with at least two lines…"*. |
| `craft_get_rubric` / do / like prompts show `content` examples as one quoted string with **literal `\n` escapes** (Get example ~1237 chars, 5× `\n`, 0 real newlines) | Models often copy that shape into JSON `content`. After JSON parse, `content` can be a **single line** with embedded `\n` text — displays fine in the textarea, **fails Save**. |
| Get content is longer and typically has more vectors than Do/Like | One bad criterion fails the whole `get_rubric` PUT; Do/Like more often land real newlines and pass. Matches UAT “Get fails, Do/Like OK”. |
| Local `grade_get` `agent_task` current=1 exists; sync has no Get-only unique constraint | Missing owner task is unlikely for this UAT host; do not lead with that fix. |
| AST-904 deferred grade grammar / prompts | Opaque “Save failed” + lost recovery were fixed; the underlying 400 remains. |

**Conclusion:** Primary product defect is Save-time grade-table parse rejecting craft Get `content` that uses embedded `\n` (or otherwise lacks a real trailing multiline grade block). Heal at parse time (shared helper used by all rubric Saves) so Get Save succeeds without changing Do/Like prompt bodies. If Stage 1 repro shows a **different** 400 string (not grade-table), stop and comment on parent — do not invent a second fix.

**Out of scope:** AST-905 empty-only recovery overwrite rule; Do/Like prompt text (unless Stage 1 proves a shared non-content bug); craft max_tokens / JSON truncation (AST-903); pending clear/re-stash (AST-904).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/rubric_text.py` | Coerce embedded `\n` / `\r\n` escapes to real newlines before trailing grade-table parse; persist healed `content` on the criterion dict | utils |
| `src/core/candidate.py` | No logic change expected — keep calling `ensure_criterion_grade_table` from `normalize_rubric_artifacts_on_save` (heal lives in utils). Touch only if Stage 1 proves normalize must call a new helper by name | core |

**Not in scope:** `ArtifactEditor.tsx` (toast already fixed in AST-904); `api_candidate.py` Save ordering; craft `agent_task` prompts unless Stage 1 fails and parent comment directs a Get-only prompt patch; `tests/` / test-bible (Betty).

---

## Stage 1: Prove the 400 is grade-table parse (Get-shaped content)

**Done when:** On epic worktree, a Get-shaped criterion whose `content` matches the craft prompt example style (literal `\n`, no real newlines) raises the known grade-table `ValueError` today, and the same payload with real newlines (or after Stage 2 heal) passes `normalize_rubric_artifacts_on_save`.

1. In a short-lived spike under `debug/spikes/ast-906/` (gitignored — do not commit), build two criterion lists for artifact key `get_rubric`:
   - **Literal-escapes:** one criterion with `content` equal to a shortened form of the craft_get prompt example: grades joined by the two-character sequence `\` + `n` (no real `\n`), plus `code`/`label`/`importance`.
   - **Real-newlines:** same text with real newlines between grade lines.
2. Call `normalize_rubric_artifacts_on_save({"get_rubric": literal_list})` — expect `ValueError` whose message contains `must end with at least two lines` (or `Rubric 'get_rubric'` prefix from `candidate.normalize_rubric_artifacts_on_save`).
3. Call the same with `real-newlines` — expect success (mutates `grade_descriptions`).
4. If a captured post-AST-904 UAT toast / `response_body.error` for Get Save is available in Linear or staging logs and is **not** this grade-table message (e.g. `No current agent_task for 'grade_get'`, empty content, importance errors): **stop**, comment on **parent AST-900** with the exact string and 2–3 options — do not proceed to Stage 2 with a mismatched fix.

⚠️ **Decision:** Lead with literal-`\n` heal because it is reproducible from the live `craft_*_rubric` prompt examples and explains Get-vs-Do/Like without prompt edits. Do not change prompts in this ticket unless Stage 1 falsifies that hypothesis.

---

## Stage 2: Heal embedded newline escapes in `rubric_text` (Save path)

**Done when:** `ensure_criterion_grade_table` accepts criterion `content` that embeds grade lines with literal `\n` / `\r\n` escapes; after success, `item["content"]` stores **real** newlines so `rubric_vector` rows are grader-friendly; real-newline content still passes unchanged.

1. In `src/utils/rubric_text.py`, add a small helper (same module, used only by grade-table parse/ensure):
   ```python
   def coerce_embedded_newline_escapes(content: str) -> str:
       """If content has few real newlines but contains \\n / \\r\\n escapes, expand them."""
       raw = content or ""
       if raw.count("\n") >= 2:
           return raw
       if "\\n" not in raw and "\\r\\n" not in raw:
           return raw
       # Expand \r\n before \n so a single pass does not leave stray \r.
       return raw.replace("\\r\\n", "\n").replace("\\n", "\n")
   ```
2. In `ensure_criterion_grade_table`:
   - Set `content = coerce_embedded_newline_escapes(item.get("content") or "")`.
   - If `content` differs from the original, set `item["content"] = content` **before** parse (so sync/fingerprint see healed text).
   - Then `rows = parse_trailing_grade_table_lines(content)` and set `grade_descriptions` as today.
3. Do **not** loosen the “≥2 trailing grade lines” rule; do **not** accept markdown bullets (`- A ==`) or mid-body grade lines in this ticket.
4. Re-run the Stage 1 literal-escapes payload through `normalize_rubric_artifacts_on_save` — must succeed; confirm `item["content"]` contains real `\n` and `grade_descriptions` length ≥ 2.
5. Sanity: a deliberately bad payload (empty content / single `A == only`) still raises `ValueError` (no silent accept).

⚠️ **Decision:** Heal in `rubric_text` (utils), not in the API layer — one place for Save normalize and any future callers of `ensure_criterion_grade_table`. Shared across get/do/like artifacts so Do/Like stay correct if they ever emit the same escape shape; **no Do/Like prompt edits**.

⚠️ **Decision:** Only coerce when `count("\n") < 2` — avoids rewriting long prose that happens to mention the two-character sequence `\n` after a valid multiline grade table already exists.

---

## Stage 3: Candidate Save smoke (Get artifact key only)

**Done when:** A `PUT /api/candidates/<id>/data` with `artifacts.get_rubric` whose criteria use literal-`\n` content returns 200 after Stage 2 (component test style or local Flask client against a throwaway candidate). Do/Like PUT paths are not required to change.

1. Using existing candidate API component-test patterns (or a local spike script under `debug/spikes/ast-906/`), PUT `{"artifacts": {"get_rubric": [<criterion with healed-capable content>]}}` with mocks **or** real `normalize` + mocked/real DB as already used in `test_api_candidate.py`.
2. Expect HTTP 200 when content is literal-`\n` grade tables (post-heal). Expect HTTP 400 with grade-table message when content is still empty / single grade line.
3. Do **not** edit `tests/` in this ticket — note the cases for Betty’s manifest. If the spike is the only verification, leave a one-line note in the Code Complete Linear comment pointing Betty at Stage 1/2 payloads.

---

## Execution contract (for build-child)

- Stages in order; one `code(AST-906):` commit per stage (Stage 1 spike may be uncommitted/gitignored; Stage 2 is the product commit; Stage 3 may fold into Stage 2 if it is only a local verify — prefer one product commit for Stage 2+3 if Stage 3 adds no repo files).
- Publish to `origin/sub/AST-900/AST-906-uat-get-rubric-save-still-failing`.
- Merge `origin/ftr/AST-900-craft-get-rubric-populate` before coding.
- If Stage 1 shows a non-grade-table error — stop, comment on **parent AST-900**, wait.
- Do **not** edit `tests/` or `docs/test-bible/**`.
- Do **not** change AST-905 recovery gating or Do/Like prompts unless parent comment redirects.

---

## Self-Assessment

**Scope:** `Single-Component` — `rubric_text` heal used by existing `normalize_rubric_artifacts_on_save`; optional core touch only if helper wiring requires it.

**Conf:** `Medium` — literal-`\n` failure is proven against live craft prompt examples and matches Get-vs-Do/Like; post-AST-904 UAT did not paste the exact toast string, so Stage 1 must falsify alternate 400s before coding.

**Risk:** `Medium` — grade-table parse is on the shared rubric Save path; over-eager `\n` expansion could alter rare prose. Mitigated by coercing only when real newline count `< 2` and keeping the ≥2 grade-line rule.

---

## Review

_(Radia fills after Tests Passed)_
