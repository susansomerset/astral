# AST-1322 — Saving base_resume drops Highlights / extra sections (Support alternative resume sections)

<!-- linear-archive: AST-1322 archived 2026-08-19 -->

## Linear archive (AST-1322)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1322/saving-base-resume-drops-highlights-extra-sections-support-alternative  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1299 — Support alternative resume sections  
**Blocked by / blocks / related:** parent: AST-1299

### Description

## As-is

Saving `candidate_data.artifacts.base_resume` that includes a Highlights section returns/persists the original fixed section set without Highlights.

## To-be

- [X] Saving that object keeps Highlights (and other extra sections present in the payload) on the candidate's base resume.

## UAT report (verbatim)

[bug] This did not parse the actual content of the candidate_data.artifacts.base_resume content.  The example provided included a section called Highlights, and when I saved the object to the candidate_data, it gave me the original set of content, not Highlights.

## Affected sibling

AST-1305 — Hops, content blobs, and legacy extra labels

## Proposed change (from plan-fix)

- [X] Dict-path `ingest_legacy_label_content_base_resume` resolves display-label keys via title-match / slug (same as list path) and writes `content[sid]`
- [X] Title-keyed Highlights / Publications survive PUT filter; `123bad` orphan strip still drops
- [X] No PUT / editor / builder call-site changes

### Comments

#### radia — 2026-08-11T23:52:05.801Z
[code-rubric] PROCEED (Commit: 8f537d4f) title-keyed dict ingest keeps Highlights extras

#### betty — 2026-08-11T23:40:53.450Z
[bug-repro]
`origin/sub/AST-1299/AST-1322-saving-base-resume-drops-highlights-extra-sections` @ `4c13304c` · repro lands red, awaits fix

#### betty — 2026-08-11T23:39:18.671Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/candidate.md ### AST-1305 — missing title-keyed dict ingest/PUT coverage (`{"Highlights": …}` vs label-list / id-keyed `highlights` already green); Blast radius expects that gap + keep AST-519 `123bad` orphan strip

#### joan — 2026-08-11T23:38:49.309Z
[board-joan]  CANON: OK

Proposed change extends existing `ingest_legacy_label_content_base_resume` dict branch to reuse `_title_to_structure_section_id` / `_slug_resume_extra_section_id` — same shape AST-1305 already landed for list ingest. Reads `RESUME_STRUCTURE_*` from config; no new statute carve-out, no pattern update, no architectural precedent change. AST-519 orphan strip explicitly preserved.

#### katherine — 2026-08-11T23:37:50.381Z
`origin/sub/AST-1299/AST-1322-saving-base-resume-drops-highlights-extra-sections` @ `621de231` · title-keyed ingest gap

---

_Implementation detail may live in git history on `origin/dev`._
