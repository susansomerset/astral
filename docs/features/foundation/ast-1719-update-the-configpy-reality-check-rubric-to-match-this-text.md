# AST-1719 — Update the config.py reality check rubric to match this text.

<!-- linear-archive: AST-1719 archived 2026-09-24 -->

## Linear archive (AST-1719)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1719/update-the-configpy-reality-check-rubric-to-match-this-text  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Execution plan

1. In `src/utils/config.py`, update `EMBEDDED_COMPANY_PREFILTER_CRITERIA` RC row `content` to match the brief exactly (including `==` separators and the new **X** line).
2. Align `grade_descriptions` A–F with the brief wording; add **X** = could not read the page (bot blocked or other network issue). Mirror the GC pattern for an X grade entry.
3. Update `TestAst707EmbeddedPrefilterConfig` in `tests/component/utils/test_config.py` so expected grades include **X** (currently A–F only).
4. Grep for other hard-coded RC grade sets / copy that would disagree with the new rubric; touch only what this constant change requires.
5. Compile/lint and run the touched config test(s) before commit.

## Done when

* RC `content` and `grade_descriptions` in `config.py` match the brief (A–F + X).
* Registry test expects A–F + X.
* No unrelated rubric owners (QC/GC/etc.) changed.

## Risks / open questions

* `ASTRAL_CONFIG["valid_grades"]` already includes **X** (and omits **E** today while RC already uses E) — confirm no pass/fail / agent validation follow-on is needed for RC **X** beyond the constant + test.
* Confirm whether `==` vs `=` is intentional for RC only (brief uses `==`; QC/GC still use `=`).

---

## Original brief

```
Reality Check — assess whether the company is real and operating as represented.
A == clearly real and verifiable
B == appears real with minor gaps
C == mixed signals; legitimacy uncertain
D == significant doubt about reality or representation
E == strong evidence of misrepresentation
F == not a real company or clearly fraudulent
X == could not read the page (bot blocked or other network issue)
```

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
