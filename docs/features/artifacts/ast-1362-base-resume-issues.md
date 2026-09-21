# AST-1362 — Base Resume Issues

<!-- linear-archive: AST-1362 archived 2026-08-31 -->

## Linear archive (AST-1362)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1362/base-resume-issues  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

1. Craft for experience detail still teaches/returns bullet-list prose; the UI/render also bullets those lines, so operators see a double bullet before each accomplishment string.
2. Authoring `|` separators are not converted to `•` in Base Resume Contact header and Core Competencies (they stay as `|` or otherwise fail the resume-wide separator rule).
3. Experience roles on Base Resume Content are not collapsible; there is no collapsed header of the form `<company>, <title> / <from> - <to>`.
4. Changing Prior Experience structure format from `word_cloud` to `free_prose` and saving still prints as `word_cloud`.

## To-be

1. Craft requests an array of strings for experience detail/accomplishments; parse/persist that shape; render/print bullets each string once (no nested bullet markers).
2. Every `|` in resume content (including Contact header and Core Competencies) converts to `•` on emit/print.
3. Each experience role is a collapsible panel whose collapsed header shows `<company name>, <title> / <from> - <to>`.
4. Saving Prior Experience as `free_prose` makes print/HTML use the free-prose treatment, not `word_cloud`.

## Proposed steps

Chosen ancestor (Susan): **AST-1345** (Done) — Clarify `base_resume.experience` node. This bug stays its own mini-parent; bug-fix will related-link AST-1345, not re-parent under it.

1. Against AST-1345’s job-array contract: widen accomplishments/detail from a single string to `string[]` in craft schema/prompts + parse, then stop double-bulleting in UI/render.
2. Extend resume emit so Contact header and Core Competencies apply `|`→`•` (AST-1345 did not own that separator rule).
3. On Base Resume Content, make each experience role collapsible with header `<company>, <title> / <from> - <to>` (beyond AST-1351’s editor cards if still flat).
4. Trace Prior Experience `word_cloud`→`free_prose` Save → print (outside AST-1345’s experience-array scope; still ship in this bug unless you split it).

## Original report

1. The craft prompt is requesting bullet lists, and the bullets are getting bulleted in the render (so it's two bullets before the text).  the craft prompt should just request an array of strings for the experience detail, and the parser should parse it correctly.
2. | bars should ALWAYS convert to **•** characters for any resume content.  This is not happening in the Contact header and Core Competencies.
3. Experience sections should be collapsible in the base resume content view, showing the `<company name>, <title> / <from> - <to>` in the collapsed header.
4. Changing a style for "Prior Experience" from word_cloud to free_prose (and saving it) still renders as word_cloud when I print.

### Comments

#### chuckles — 2026-08-14T21:25:00.532Z
Locked ancestor: **AST-1345** (Done — Clarify `base_resume.experience` node). Description Proposed steps updated to that pick.

Items 2 and 4 sit outside that epic’s experience-array scope; they stay on this bug’s as-is/to-be unless you want them split. Move this ticket to **Todo** (assignee Chuckles) when the reading is good — that is the approve signal for bug-fix.

#### susan — 2026-08-14T21:24:22.410Z
1345, please.

#### chuckles — 2026-08-14T21:02:34.778Z
Ancestor candidates (ranked — pick one, ask about one, or reject all):

1. AST-1345 — Clarify `base_resume.experience` node (parent of 1349/1351) — strongest umbrella for craft array shape + experience UI/print (items 1, 3).
2. AST-1349 — Experience array contract / craft-parse prompts — craft still teaching bullet/prose vs array (item 1).
3. AST-1351 — Experience array UI + render/print parity — Base Resume experience presentation / print (items 1, 3).
4. AST-1299 — Support alternative resume sections (parent of 1303–1306) — section `format` including Prior Experience `word_cloud`/`free_prose` (item 4).
5. AST-1304 — Builder emit by section format — print treatment keyed off `format` (item 4; also `word_cloud` emit path).
6. AST-1306 — Author extra sections title/format — saving format changes on Base Resume Content (item 4).
7. AST-1303 — Section format catalog — defaults `prior_experience`/`core_competencies` to `word_cloud` (item 4 context).
8. AST-993 / AST-1019 — Resume render format discrepancies — separator/`•` + experience layout golden work (item 2, related).
9. AST-1148 — Cover from-block `|`→`•` — documented separator rule, wrong surface (cover not resume contact/competencies) but closest prior contract for item 2.

#### chuckles — 2026-08-14T18:26:28.968Z
[thread-missing] Cursor chat `00cc646b-06b3-4d9d-97dd-d9d869fcc282` has no local `store.db` on **chuckles** (expected `/home/susan/.cursor/chats/40f37617870e538aada0246cb9f8c346/00cc646b-06b3-4d9d-97dd-d9d869fcc282/store.db`; blob-search also empty).

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered).

Replacement UUID: `b81101c7-048f-4865-8064-d74a619f7d78`.

Watcher rule `bug-find` on `AST-1362` (Thread owner `AST-1362`).

#### chuckles — 2026-08-14T18:15:39.961Z
[thread-missing] Cursor chat `8652acc7-bab7-4487-ac8c-c12c9a1df002` has no local `store.db` on **chuckles** (expected `/home/susan/.cursor/chats/40f37617870e538aada0246cb9f8c346/8652acc7-bab7-4487-ac8c-c12c9a1df002/store.db`; blob-search also empty).

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered).

Replacement UUID: `4acca981-bb6c-4c08-8836-f66637fe4110`.

Watcher rule `bug-find` on `AST-1362` (Thread owner `AST-1362`).

---

_Implementation detail may live in git history on `origin/dev`._
