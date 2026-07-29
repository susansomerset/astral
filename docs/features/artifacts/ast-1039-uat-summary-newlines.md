# UAT: Summary newlines collapse to spaces (Experience ok)

**Linear:** [AST-1039](https://linear.app/astralcareermatch/issue/AST-1039/uat-summary-newlines-collapse-to-spaces-experience-ok)
**Parent:** [AST-1019](https://linear.app/astralcareermatch/issue/AST-1019/take-2-resume-render-format-discrepancies) — Take 2: Resume Render Format discrepancies
**Publish ref:** `origin/sub/AST-1019/AST-1039-uat-summary-newlines`

In Session Resume Paste → Open HTML, Experience already treats `\n` as structural breaks (accomplishment lines / bullets), but Professional Summary only splits on blank lines (`\n\s*\n`). Single newlines stay inside one `.summary-intro` `<p>`; the browser collapses them to spaces. Align Summary paragraph splitting with the existing cover-letter blank-line-then-single-`\n` fallback so paste newlines yield multiple `.summary-intro` paragraphs.

## UAT fitness

- **AC restored:** Parent AC (quoted on the bug): *“Professional Summary as multiple `.summary-intro` paragraphs; … nested `__` / `~~` markers end-to-end.”* / *“Susan can verify by eye against the desired HTML for every laundry-list item; no judgment call on ‘close enough.’”* / *“Fixture-driven UAT: Original-brief input paste → Open HTML matches desired structure + cosmetics (eye + HTML source). No ‘close enough.’”*
- **Correct outcome:** Paste newlines in Professional Summary produce separate `.summary-intro` `<p>` elements; Experience newline → bullet/paragraph behavior stays unchanged.
- **Sibling check:** AST-1020 stylesheet unchanged. AST-1021 residual emit / title-meta unchanged. AST-1027–1030 marker / keywords / competencies / `<no bullet>` contracts unchanged. AST-1035 View Parsed JSON chrome unchanged. AST-993/1010 structural summary contracts: still emit `.summary-intro` paragraphs — this restores multi-paragraph when the payload uses single `\n` (not only `\n\n`).
- **Not sufficient:** Fewer visual spaces inside one paragraph, or CSS `white-space` tricks — multi-paragraph Summary DOM must match desired HTML.
- **Wrong fix rejected:** Changing Experience newline rules to match broken Summary; CSS-only visual fakes; rewriting summary *content* in the prompt; treating this as stylesheet-only; inventing a second Summary fetch path.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/builder.py` | Summary paragraph split: blank lines first, then single-`\n` fallback (reuse existing cover-letter helper pattern) so each chunk becomes its own `.summary-intro` `<p>` | core |

**Out of scope (do not touch):** embedded golden CSS; Experience `_split_role_accomplishments`; `data/admin/agent_task.json` (prompt); Session Resume Paste UI; document title/meta; competencies; `<no bullet>`; `tests/` / bible (Betty).

## Root cause (plan-time)

In `_emit_body_sections_html`, the `professional_summary` branch does:

```python
paras = [p.strip() for p in re.split(r"\n\s*\n", str(text)) if p.strip()]
```

That only breaks on **blank lines**. A fixture / parse payload with single `\n` between summary paragraphs yields **one** `paras` entry containing embedded newlines; `html.escape` preserves those `\n` characters inside a single `<p class="summary-intro">`, and HTML whitespace collapsing turns them into spaces. Experience is fine because `_split_role_accomplishments` iterates `accomplishments.split("\n")`. Cover letter already solved the same asymmetry via `_session_cover_letter_paragraphs` (blank-line split, then if a single chunk still contains `\n`, split on `\n`).

**Git hygiene:** Keep `origin/sub/AST-1019/AST-1039-uat-summary-newlines` rooted on current `origin/ftr/ast-1019-take-2-resume-render-format-discrepancies` with only AST-1039 vocabulary commits in the `ftr..sub` range. Do **not** leave subjects matching `Merge remote-tracking branch`.

## Stage 1: Summary paragraph split honors single `\n`

**Done when:** Given `professional_summary` text with single `\n` between paragraphs (no blank line), `_emit_body_sections_html` / session Open HTML emits **two or more** `<p class="summary-intro">` elements (one per non-empty line/paragraph chunk). Blank-line-separated input (`Para one\n\nPara two`) still emits multiple paragraphs (existing behavior preserved). Experience emit path and `_split_role_accomplishments` are untouched. No CSS or prompt edits.

1. In `src/core/builder.py`, replace the inline `re.split(r"\n\s*\n", …)` in the `professional_summary` branch of `_emit_body_sections_html` with the **same** blank-line-then-single-`\n` semantics already used for session cover letters.
2. Prefer **reuse** of `_session_cover_letter_paragraphs(str(text))` (or a one-line rename to a shared helper e.g. `_paragraphs_blank_or_newline` called from both cover letter and summary) — do **not** duplicate a third split dialect.
3. Keep each non-empty chunk as `html.escape(p)` inside `<p class="summary-intro">` (markers still applied upstream via existing deep marker walk — do not invent a new marker pass here).
4. Do **not** change Experience branches, stylesheet CSS, parse API, or `craft_resume_base` prompts.
5. Do **not** edit `tests/` or bible — Betty owns assertions after Code Complete (existing blank-line case `"Para one\n\nPara two"` must keep passing; expect Betty to add a single-`\n` case).
   ⚠️ **Decision:** Builder emit fix only (reuse cover-letter paragraph helper). Prompt-only “emit `\n\n`” is **not** sufficient — Session Resume Paste fixtures and model output commonly use single `\n`, and Experience already treats `\n` as structural; Summary must match that contract in HTML structure. Always-split-on-every-`\n` without blank-line preference is acceptable only if reuse of the existing helper is blocked — default to the helper’s proven order (blank lines first, then `\n` fallback) so intentional multi-sentence paragraphs separated by `\n\n` stay intact when a paragraph itself has no internal newlines.

## Stage 2: Compile check (build verification)

**Done when:** `python3 -m py_compile src/core/builder.py` succeeds after Stage 1. Manual/build smoke: feed `build_session_base_resume` (or `_emit_body_sections_html`) a structure-enabled summary `"First para\nSecond para"` → two `.summary-intro` tags; `"First\n\nSecond"` still two; Experience job array with `\n` accomplishments unchanged. Spikes only under `debug/spikes/AST-1039/` if used — never commit; never repo-root `artifacts/`.

1. During **build-child**, run `python3 -m py_compile` on the changed builder file.
2. Confirm `git diff` does not touch CSS strings, Experience split helpers, prompts, or test-tree paths.
3. Note for UAT: Session Resume Paste fixture with multi-line Professional Summary → Open HTML → multiple `.summary-intro` paragraphs; Experience still correct.

## Self-Assessment

**Scope:** `Single-Component` — `src/core/builder.py` summary paragraph split only (reuse existing cover-letter helper semantics).

**Conf:** `high` — emit path is explicit; cover-letter helper already encodes the correct blank-line / `\n` contract; Experience contrast confirms diagnosis.

**Risk:** `low` — additive split fallback; blank-line behavior preserved; Experience/CSS/prompt untouched.

## Code Rules self-review

- §1.3 DRY: reuse `_session_cover_letter_paragraphs` (or shared rename) — no third newline dialect.
- §1.1 / scope isolation: no Experience/CSS/prompt/UI edits.
- Engineer test-tree ban: no `tests/` or bible edits.
- §3.6: spikes under `debug/spikes/AST-1039/` only if used.
