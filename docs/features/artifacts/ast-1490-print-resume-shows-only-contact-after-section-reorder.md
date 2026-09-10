# AST-1490 — Print Resume shows only contact after section reorder

<!-- linear-archive: AST-1490 archived 2026-09-09 -->

## Linear archive (AST-1490)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1490/print-resume-shows-only-contact-after-section-reorder  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1483 — Resume page break settings don't work  
**Blocked by / blocks / related:** parent: AST-1483

### Description

Separate bug, if I move a section up or down, the print render only includes the contact information and no other content appears.

## As-is

After moving a resume section up or down in structure authoring, Print Resume emits only the contact block — body sections are missing from the printed HTML.

## To-be

After a section reorder, Print Resume still includes the full resume body in the new order (contact plus every enabled content section).

## Suggested engineer

Hedy Lamarr (AST-1487 sibling)

### Comments

#### radia — 2026-08-26T18:39:38.228Z
[code-rubric] PROCEED (Commit: 0338900a) reorder-safe editor reload

#### betty — 2026-08-26T18:34:36.609Z
[bug-repro]
`origin/sub/AST-1483/AST-1490-print-resume-only-contact-after-section-reorder` @ `c5e45e0b` · repro lands red, awaits fix

#### joan — 2026-08-26T18:31:44.522Z
[board-joan]  CANON: OK

#### betty — 2026-08-26T18:31:27.137Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/components.md — no reorder+Print repro; no reorder no-re-GET guard — add AST-1490 bug-repro (Base/JAR) + reorder GET-count regression; extend AST-1489 print pattern

#### hedy — 2026-08-26T18:30:54.730Z
origin/sub/AST-1483/AST-1490-print-resume-only-contact-after-section-reorder @ `92623bdf` · sort fixedFieldKeys

#### hedy — 2026-08-26T15:56:51.050Z
[scope-gate]

Parent AST-1483 Component/Technical scope only names:

* `src/core/builder.py` — restore `_print_section_page_break_css` / drop hard-coded `#prior-experience` always-break (AST-1487 emit half)
* Betty test/bible paths

AST-1490’s symptom is different: after structure Up/Down, Print Resume shows contact only (body sections missing). On the current tip, builder emit with a reordered saved structure still produces full body `<section>` HTML (`build_session_base_resume` / `_structure_ordered_body_ids` / `_emit_body_sections_html`) — the declared builder print-CSS kind of change does not cover this delta.

Likely fix surface is `src/ui/frontend/src/components/ArtifactEditor.tsx` (AST-1480): `fixedFieldKeys` is an order-sensitive join of section ids, so Up/Down changes the signature, re-triggers candidate/job re-GET (`setLoaded(false)` → Loading…), and the label-sync effect treats order changes as a different key set (`prevKeys !== nextKeys` → keep stale tab order). That file and change kind are outside the parent’s declared Component/Technical scope.

Need scope amended to include ArtifactEditor (and any Base/JAR wiring required for the confirmed repro) before Plan Ready — or a server-side HTML fixture proving body tags are absent after Save sections + Print so a builder-only root cause can be named. @susan

---

_Implementation detail may live in git history on `origin/dev`._
