# AST-1299 — Support alternative resume sections
**Component:** artifacts  
**Children:** AST-1303, AST-1304, AST-1305, AST-1306, AST-1322, AST-1323, AST-1324, AST-1325  
**Linear archived:** AST-1299 2026-08-19; AST-1303 2026-08-19; AST-1304 2026-08-19; AST-1305 2026-08-19; AST-1306 2026-08-19; AST-1322 2026-08-19; AST-1323 2026-08-19; AST-1324 2026-08-19; AST-1325 2026-08-19

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-10 22:38 | AST-1303 | docs | `4531e0b0d` | docs(AST-1303): plan — section format catalog and open extra ids |
| 2026-08-10 22:42 | AST-1303 | docs | `e026be768` | docs(AST-1303): Joan validate — plan approved |
| 2026-08-10 22:43 | AST-1303 | code | `3d744e02e` | code(AST-1303): add resume section format catalog |
| 2026-08-10 22:44 | AST-1303 | code | `3ab84c5e0` | code(AST-1303): normalize extras and required section formats |
| 2026-08-10 22:45 | AST-1303 | docs | `bfb61dd72` | docs(AST-1303): review stub — stages 1–2 |
| 2026-08-10 22:53 | AST-1303 | merge-tests | `2fd325386` | merge-tests(AST-1303): origin/tests 69d0ae6af0aa01b845a0580838ca2fe26421e6ae |
| 2026-08-10 22:53 | AST-1303 | test | `69d0ae6af` | test(AST-1303): resume section catalog + open extra-id normalize coverage |
| 2026-08-10 23:01 | AST-1303 | docs | `e14e4da86` | docs(AST-1303): Radia review — clean |
| 2026-08-10 23:03 | AST-1303 | resolve | `f037cfe38` | resolve(AST-1303): — clean |
| 2026-08-10 23:12 | AST-1306 | docs | `2ea93a93b` | docs(AST-1306): plan — author extra sections title and format |
| 2026-08-10 23:13 | AST-1304 | docs | `622211d43` | docs(AST-1304): plan — builder emit by section format |
| 2026-08-10 23:15 | AST-1305 | docs | `1cc15431d` | docs(AST-1305): plan — hops content blobs and legacy extra labels |
| 2026-08-10 23:18 | AST-1304 | docs | `586f02da2` | docs(AST-1304): Joan validate — plan approved |
| 2026-08-10 23:18 | AST-1306 | docs | `13a49e953` | docs(AST-1306): Joan validate — APPROVED |
| 2026-08-10 23:20 | AST-1303/1306 | code | `04dcb32db` | code(AST-1306): merge ftr after AST-1303 catalog |
| 2026-08-10 23:20 | AST-1305 | docs | `f32999d45` | docs(AST-1305): Joan validate — APPROVED |
| 2026-08-10 23:20 | AST-1306 | code | `bf147fb6b` | code(AST-1306): expose structure catalog and replace PUT sections |
| 2026-08-10 23:21 | AST-1304 | code | `044001664` | code(AST-1304): emit resume sections by format |
| 2026-08-10 23:23 | AST-1306 | docs | `3d63ce24f` | docs(AST-1306): review stub — stages 1–2 |
| 2026-08-10 23:23 | AST-1306 | code | `cc00324c9` | code(AST-1306): add resume structure editor on base resume page |
| 2026-08-10 23:25 | AST-1304 | code | `b39d6b759` | code(AST-1304): Style D per-section emit trail |
| 2026-08-10 23:25 | AST-1305 | code | `98bb5bbe9` | code(AST-1305): ingest legacy labels and keep extras in token JSON |
| 2026-08-10 23:26 | AST-1304 | docs | `a587c42f2` | docs(AST-1304): review stub — stages 1–2 |
| 2026-08-10 23:27 | AST-1305 | code | `2fb7a993f` | code(AST-1305): persist experience only as experience_detail array |
| 2026-08-10 23:27 | AST-1305 | code | `71c603853` | code(AST-1305): accept extra section keys on craft flatten and draft whitelist |
| 2026-08-10 23:28 | AST-1305 | docs | `4e33d3be5` | docs(AST-1305): review stub — stages 1–3 |
| 2026-08-10 23:35 | AST-1306 | merge-tests | `b67ac6c6e` | merge-tests(AST-1306): origin/tests c4b7adbb6338de40da53e5cf11abf9a47242b010 |
| 2026-08-10 23:35 | AST-1306 | test | `c4b7adbb6` | test(AST-1306): extra-section authoring — slug/prepare, GET catalog, PUT replace, editor |
| 2026-08-10 23:37 | AST-1306 | test | `1e405f2c4` | test(AST-1306): bind GET structure sort key to kv[0] |
| 2026-08-10 23:39 | AST-1304 | test | `6e51cf514` | test(AST-1304): builder emit by format + leftover Experience skip |
| 2026-08-10 23:40 | AST-1305 | test | `f27148fd5` | test(AST-1305): hops accept extras; Abrams labels stay; Experience is job-array only |
| 2026-08-10 23:42 | AST-1306 | docs | `f3381453e` | docs(AST-1306): Radia review — FIX-NOW |
| 2026-08-10 23:43 | AST-1306 | resolve | `518fba3fb` | resolve(AST-1306): — findings addressed |
| 2026-08-10 23:44 | AST-1305 | test | `98921eec7` | test(AST-1305): keep colliding labels and promote nested job arrays |
| 2026-08-10 23:47 | AST-1304 | test | `921dfe9da` | test(AST-1304): keep extras missing format on session emit; pair emphasis tags |
| 2026-08-10 23:48 | AST-1304 | test | `2670b28d3` / `cfe6433a6` | test(AST-1304): expect html.escape quote entity on attributed emphasis tags |
| 2026-08-10 23:48 | AST-1305 | test | `06ace6fec` | test(AST-1305): [qa-handoff] raw_resume ctx + drop Judith prompt from manifest |
| 2026-08-10 23:53 | AST-1304/1305 | test | `8f90dfddf` / `f9d3b69a6` | test(AST-1304): keep AST-1305 extra-format import off test_candidate module |
| 2026-08-10 23:59 | AST-1305 | docs | `ef75a0923` | docs(AST-1305): Radia review — CLEAN |
| 2026-08-11 00:00 | AST-1304 | docs | `1e8421539` | docs(AST-1304): Radia review — clean |
| 2026-08-11 00:00 | AST-1305 | resolve | `640683b3c` | resolve(AST-1305): — clean |
| 2026-08-11 00:03 | AST-1305 | merge-tests | `9db60c79c` | merge-tests(AST-1305): origin/tests 06ace6fec904d9c17c099dbff5ea21f01097cbbf |
| 2026-08-11 00:06 | AST-1305/1306 | resolve | `ff5aeda33` | resolve(AST-1305): merge origin/ftr after AST-1306 |
| 2026-08-11 00:11 | AST-1304 | resolve | `8577bd5fd` | resolve(AST-1304): — clean |
| 2026-08-11 00:11 | AST-1304 | merge-tests | `896ba6197` | merge-tests(AST-1304): origin/tests 8f90dfddf475163fb0c5baf775b9263623a5083e |
| 2026-08-11 16:37 | AST-1322 | docs | `621de231b` | docs(AST-1322): plan-fix — title-keyed Highlights drop on PUT |
| 2026-08-11 16:37 | AST-1323 | docs | `83db7e70d` | docs(AST-1323): plan-fix — collapsible structure header with body between |
| 2026-08-11 16:40 | AST-1322 | test | `8a91b8771` / `c3d5795e0` | test(AST-1322): bug-repro — title-keyed Highlights survive ingest/PUT |
| 2026-08-11 16:42 | AST-1323 | test | `89acd3bad` / `bef854d1b` | test(AST-1323): bug-repro — structure controls on collapsible header row |
| 2026-08-11 16:43 | AST-1322 | code | `788ec269b` | code(AST-1322): resolve title-keyed base_resume extras on ingest |
| 2026-08-11 16:49 | AST-1323 | code | `faf8740cf` | code(AST-1323): put structure controls on collapsible section headers |
| 2026-08-11 16:52 | AST-1322 | docs | `f10582f51` | docs(AST-1322): Radia review — clean |
| 2026-08-11 16:53 | AST-1323 | docs | `32cd7c756` | docs(AST-1323): Radia review — obsolete ResumeStructureEditor test |
| 2026-08-11 17:07 | AST-1322 | merge-tests | `27116b8e8` | merge-tests(AST-1322): origin/tests c3d5795e0659f98fec72b6125d896d9b0b4ba824 |
| 2026-08-11 17:08 | AST-1323 | test | `8884b932c` / `e5b5710ae` | test(AST-1323): drop flat ResumeStructureEditor suite; migrate catalog asserts |
| 2026-08-11 17:10 | AST-1323 | resolve | `2ecd734c0` | resolve(AST-1323): — findings addressed |
| 2026-08-11 17:14 | AST-1323 | merge-tests | `e2efdd89e` | merge-tests(AST-1323): origin/tests e5b5710ae8c5042af0d4f2659542e795a908cad8 |
| 2026-08-11 17:18 | AST-1299 | merge | `79613db2a` | merge: origin/dev into ftr/AST-1299-support-alternative-resume-sections |
| 2026-08-11 18:09 | AST-1324 | docs | `2bd635eb1` | docs(AST-1324): plan-fix — load/render base_resume sections default free_prose |
| 2026-08-11 18:10 | AST-1325 | docs | `5ced2a6d2` | docs(AST-1325): plan-fix — header row name\|style\|Enabled\|Job Edit\|up/down |
| 2026-08-11 18:15 | AST-1324 | test | `1b2e38f38` / `e4709d3f2` | test(AST-1324): bug-repro — GET resume_structure hydrates from base_resume |
| 2026-08-11 18:17 | AST-1325 | test | `7f715a986` / `9c6100a40` | test(AST-1325): bug-repro — structure header name\|style\|Enabled:\|Job Edit: |
| 2026-08-11 18:44 | AST-1324 | code | `fd7b7849c` | code(AST-1324): hydrate GET resume_structure from base_resume (free_prose) |
| 2026-08-11 18:47 | AST-1325 | code | `fc3f4456c` | code(AST-1325): structure header name\|style\|Enabled:\|Job Edit:\|up/down |
| 2026-08-11 18:51 | AST-1325 | test | `3b4a7726a` / `c1c8ebd7d` | test(AST-1325): fix [qa-handoff] — drop duplicate headers; Job Edit: |
| 2026-08-11 18:53 | AST-1324 | docs | `52213f568` | docs(AST-1324): Radia review — clean |
| 2026-08-11 18:54 | AST-1325 | docs | `36c901f2f` | docs(AST-1325): Radia review — clean |
| 2026-08-11 18:56 | AST-1324 | merge-tests | `3cadcc078` | merge-tests(AST-1324): origin/tests e4709d3f21bbee052002f9f64976ece10b51883d |
| 2026-08-11 18:58 | AST-1325 | merge-tests | `7a091a8dd` | merge-tests(AST-1325): origin/tests 3b4a7726a5392a12bcd54e0de4c947b05878d07b |
| 2026-08-11 19:00 | AST-1299 | merge | `e3fe2c557` | Merge remote-tracking branch 'origin/dev' into tmp-refresh-AST-1299-support-alternative-resume-sections |
| 2026-08-11 19:49 | AST-1299 | docs | `46433fa0e` | docs(AST-1299): mirror epic registry Threads |
| 2026-08-19 12:50 | AST-1303 | docs | `a2ecfd85d` | docs(AST-1303): archive Linear issue content |
| 2026-08-19 12:50 | AST-1304 | docs | `dc12b31bd` | docs(AST-1304): archive Linear issue content |
| 2026-08-19 12:51 | AST-1305 | docs | `f38b26b2d` | docs(AST-1305): archive Linear issue content |
| 2026-08-19 12:51 | AST-1306 | docs | `d5a4ab870` | docs(AST-1306): archive Linear issue content |
| 2026-08-19 12:51 | AST-1322 | docs | `5999168cf` | docs(AST-1322): archive Linear issue content |
| 2026-08-19 12:51 | AST-1323 | docs | `c906af832` | docs(AST-1323): archive Linear issue content |
| 2026-08-19 12:52 | AST-1324 | docs | `15fa09b68` | docs(AST-1324): archive Linear issue content |
| 2026-08-19 12:52 | AST-1325 | docs | `55aff9c01` | docs(AST-1325): archive Linear issue content |
| 2026-08-19 12:54 | AST-1299 | docs | `cc2196590` | docs(AST-1299): archive Linear issue content |

_Several commits above appear under two tickets — not misattribution but the same commit's body mentioning both (the AST-1303→AST-1306 `ftr` merge; a shared test-import fixup jointly needed by AST-1304 and AST-1305; a `resolve(AST-1305)` that also merged AST-1306's `ftr` state). AST-1322/1323/1324/1325 are UAT bug tickets filed against this epic (parent AST-1299) after the four proposed children shipped — their full build narrative lives embedded in the AST-1305 (AST-1322) and AST-1306 (AST-1323/1324/1325) host docs, not in their own thin standalone files, per this epic's `[board-*]`/`plan-fix` bug-lane convention (lighter than the Stage/Decision plan convention used by the four numbered children). No cross-folder inbound references were found for any ticket in this family._

## Epic — AST-1299
_Archived: 2026-08-19 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1299/support-alternative-resume-sections · Status at archive: Archive · Project: Astral Artifacts · Assignee: chuckles · Priority / estimate: Urgent / — · Blocked by / blocks / related: related: AST-1201; related: AST-1205_

### Purpose

Candidates do not all share the Somerset ten-section catalog. Abrams-style resumes need extra titled blocks (Highlights, Publications, and whatever else the person actually has) while still printing with the Somerset treatments we already ship. Today unknown section ids are rejected and extra legacy labels are dropped, so those resumes cannot be stored or rendered. This epic makes section title + format a first-class property of the candidate's structure, keeps seven sections required, and lets the builder emit any additional section by choosing one existing format.

### Functional scope

* **Required sections stay seven.** Every valid structure includes Candidate Name, Candidate Title, Candidate Tagline, Candidate Contact Detail, Summary (or Professional Summary), Core Competencies, and Experience. Those seven keep today's stable ids. "Summary" vs "Professional Summary" is a display title on the same summary section — not a second id.
* **Additional sections are allowed.** A candidate may add any number of extra sections (Highlights, Publications, Prior Experience, Education, Technical Skills, or new titles). Each extra section has a stable id, a display title the operator or craft hop can set, enabled/order flags, and exactly one format from the closed format list.
* **Format is a section property, not an id.** The builder chooses a visual treatment from the section's format, not from the section's name. The closed formats and their Somerset treatments: `free_prose` (Summary-style paragraphs); `bullet_list` (a standalone section of lines as bullets — Highlights uses this; any other extra section may pick it); `word_cloud` (Core Competencies pipe line); `dual_column` (Technical Skills category grid); `indented_bold_single` (Education bold-lead rows); `experience_detail` (Experience role articles from today's job-array fields).
* **Required sections have implied formats.** Header fields keep the existing header emit. Summary defaults to `free_prose`. Core Competencies defaults to `word_cloud`. Experience is required as `experience_detail` (an array). Publications is a `bullet_list` section, not `experience_detail`. Today's optional catalog slugs keep their historical treatments: Prior Experience → `word_cloud`, Education → `indented_bold_single`, Technical Skills → `dual_column`.
* **Emphasis in body text.** Section bodies honor a small closed set of html-style italic and bold tags so Publications (and other body formats) can emphasize titles and names. Not a free HTML surface — only italic and bold.
* **Content and hops follow the structure.** Base resume and job resume bodies may include extra section keys. Job artifacts remain a subset of the candidate's enabled structure ids — they must not invent sections the structure does not define. Craft-base and draft-job hops accept those extra keys. Draft whitelist stays "this candidate's current base resume keys," now including extras. Experience content is an `experience_detail` array; leftover prose Experience is regenerated, not kept as a valid shape.
* **Operators can author extras.** Title, format, enabled, and order are editable for optional sections. Required sections cannot be removed. New extras default to job-agent-editable unless the operator turns that off.
* **Legacy label/content arrays keep extra titles.** A pasted Abrams-style list whose labels are not in the old catalog becomes extra structure sections (id slugged from the title) instead of being silently dropped.
* **Debug (backend `debug=True` only).** On builder (and any touched normalize/validate `debug=` path): Style D index headers with universal `index N/M`, section id, title, format, and emit outcome; working detail under `|`; long HTML truncated per the AST-538 contract.

### Architectural definition

* **Patterns to reuse** — `pattern.config.config-block` (required section ids, closed format list, default format-per-required-section, allowed emphasis-tag set live in config); `pattern.layers.import-discipline` (structure/normalize in core, emit in the builder, UI stays a thin consumer); `pattern.ui.admin-endpoint` (format catalog and structure edits resolved in the API from config; React does not own the allowed-format list).
* **New patterns proposed** — none. Format dispatch is a config extension of the existing structure + builder, not a new catalog method package.
* **Applicable statutes** — `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.standards.in-scope-only`; `astral.standards.debug-contract-gated`; `astral.standards.dry-and-focused-functions`; `astral.layers.import-direction`; `astral.layers.ui-config-driven-business-logic`; `astral.agent.do-task-delegation` on hops that persist structure or section bodies.

### Boundaries

* Does **not** invent new visual styles, accent/style settings, or typography knobs beyond the closed italic/bold emphasis set.
* Does **not** own AST-1201 (base-resume daisy chain that will later generate Highlights / special sections). This epic is the contract that chain must honor.
* Does **not** own AST-1205 (approve artifacts) or AST-1268 (nested draft envelope / deviations). AST-1268 is User Testing; this epic only extends the section-key whitelist so extras are not treated as unknown.
* Does **not** change cover-letter shape or emit.
* Does **not** strip Prior Experience / Education / Technical Skills from candidates who already have them — those remain valid optional sections.
* Does **not** require a global closed catalog of extra section ids. Extras are per-candidate. The format list is closed; the extra-id list is not.
* Does **not** keep a prose-Experience render fallback. Regenerate to an `experience_detail` array.
* Does **not** treat Publications as `experience_detail`. Publications is `bullet_list`.
* Job hops still must not add section keys the structure does not enable.

### Acceptance criteria

1. A candidate whose structure is only the seven required sections renders a complete resume; absent optional sections do not fail the builder.
2. Adding Highlights as `bullet_list` and Publications as `bullet_list` (titles + bodies) prints those headings and bulleted lines in structure order.
3. Changing a required section's title (e.g. Professional Summary → Summary) changes the printed heading and does not change the section id.
4. Changing an optional section's format changes the HTML treatment without creating a new section id.
5. Craft-base and draft-job hops accept extra keys that exist on that candidate's base resume / structure; they do not fail with "unknown section" merely because the key is outside the old ten-id list.
6. A job resume cannot introduce a section the candidate structure does not enable.
7. Required sections cannot be removed from structure.
8. An Abrams-style label/content array that includes Highlights and Publications does not drop those labels on ingest or token serialize.
9. Html-style italic and bold tags in a `bullet_list` body (and other body formats) render as italic and bold; other tags are not a raw HTML hole.
10. A leftover prose Experience string is not rendered as the required Experience section; Experience counts only as an `experience_detail` array (regenerate).
11. With `debug=True` on the builder, each enabled section logs id, title, format, and whether it emitted, under Style D headers and `|` detail.

### Dependencies and blockers

none. Adjacent, not blocking: AST-1268 (User Testing — nested draft envelope); AST-1201 (Discussion — daisy chain that will generate extra-section content later).

### Open questions

none.

### Proposed child tickets

**1!: Section format catalog and open extra ids — Ada** — Owns the config contract: required seven ids, closed format list (including `bullet_list` and `experience_detail`), default formats for required/historical optional slugs, allowed italic/bold emphasis tags, and structure normalize that accepts extra titled sections instead of rejecting unknown ids. Observable: a structure with Highlights + Publications as `bullet_list` persists; required sections still cannot be omitted. Does not own HTML emit, hops, or the editor UI.
**Citations:** `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`.

**2: Builder emit by section format — Hedy** — After #1: render enabled sections in structure order by format, reusing the existing Somerset treatments; Highlights and Publications print as `bullet_list`; `experience_detail` uses today's job-array fields; html-style italic/bold in body text render; leftover prose Experience is not treated as the required Experience section. When `debug=True`, log id / title / format / emit outcome per section (Style D). Does not own hop schemas or the structure editor.
**Citations:** `pattern.config.config-block`; `astral.standards.dry-and-focused-functions`; `astral.standards.debug-contract-gated`.

**3: Hops, content blobs, and legacy extra labels — Katherine** — After #1: craft-base and draft-job accept extra section keys; draft whitelist is the candidate's current base resume keys (including extras), not the old ten-id intersection. Legacy label/content arrays keep unmatched titles as extra sections. Experience persists as an `experience_detail` array (regenerate prose). Does not own HTML chrome or AST-1201 generation order.
**Citations:** `pattern.config.config-block`; `astral.standards.no-hardcoded-sets`; `astral.agent.do-task-delegation`.

**4: Author extra sections (title and format) — Ada** — After #1: operators can add, title, format, enable, and reorder optional sections; required seven cannot be removed. Format choices come from the config catalog via the API (not a hardcoded React list). Does not own print CSS or hop prompts.
**Citations:** `pattern.ui.admin-endpoint`; `astral.layers.ui-config-driven-business-logic`.

### Original brief

Accommodate resume sections. Allow the section title to be made, and a formatting option to use one of the existing ways we format the somerset resume.

The only REQUIRED sections are now:

* Candidate Name
* Candidate Title
* Candidate Tagline
* Candidate Contact Detail
* Summary (or Professional Summary)
* Core Competencies
* Experience (array)

The rest of the sections may or may not be there, but the resume builder will know how to build them with section properties like "free_prose", "bullet_list", "word_cloud", "dual_column", "indented_bold_single", "experience_detail" (which would be used for things like the job experiences, but also publications and such, with Header text, sub-header text, and an array of strings to show as bullets).

See the file attached for examples of additional resume sections, but not (yet) the style settings.

[candidate-abrams.json] (Linear attachment — see original ticket for the download link.)

#### Comments

##### chuckles — 2026-08-11T03:20:58.917Z
@susan

1. Confirm the format → existing Somerset emit mapping in the Description (Functional scope). In particular: is `bullet_list` a standalone section of lines as bullets, and should Abrams Highlights use that vs `free_prose`?
2. `experience_detail` persisted shape — keep today's job-array fields (title, company, dates, location, accomplishments) so Experience does not migrate twice, or switch Experience and Publications to the flatter header / sub-header / bullets object named in the brief?
3. Live candidates whose Experience is still a prose string, not an array: keep a temporary `free_prose` render fallback, or regenerate-only?

— Chuckles

##### chuckles — 2026-08-11T07:08:33.679Z
[merge-child] blocked: AST-1304 sub not rollup-safe.

@Hedy Lamarr — duplicate merge-tests + Merge remote-tracking (including sibling subs) on AST-1304 publish ref.
@Betty White — one merge-tests after the sub log is linear.

— Chuckles

##### susan — 2026-08-11T20:46:28.633Z
\[bug\] This did not parse the actual content of the candidate_data.artifacts.base_resume content. The example provided included a section called Highlights, but when I saved the object to the candidate_data, it gave me the original set of content, not Highlights.

##### susan — 2026-08-11T20:48:34.450Z
\[bug\] Put the section labels, type select, enabled, job-edit (instead of job agent editable) and the up/down buttons on a single collapsible header row with the text for that section appearing between the headers (instead of the bottom of the page).

##### chuckles — 2026-08-12T00:17:44.764Z
[refresh-ftr] blocked: docs/test-bible/frontend/pages.md

@Betty White — merge origin/dev into origin/ftr/AST-1299-support-alternative-resume-sections; resolve bible conflict; push ftr.

##### susan — 2026-08-12T00:45:26.237Z
\[bug\] Sorry, Chuckles, I think I wasn't clear enough about this. It's not the SAVE that is the issue. It's the RENDER of the existing base_resume artifact. The base_resume_content page should render FREELY based on the information in the base_resume artifact, setting the style to "prose" by default if it's missing. I'm asking you to LOAD from what is already in candidate_data, which I artificially applied and correctly has all the sections I want. Does that clear things up?

##### susan — 2026-08-12T01:04:10.803Z
\[bug\] Likewise 1323 was a partial fix, but I want the header row to lay out like this:

```
[SECTION NAME           ] [STYLE    V] Enabled:[X] Job Edit:[ ]  [up][down]
```

##### chuckles — 2026-08-12T01:55:20.459Z
[merge-child] blocked: AST-1324 and AST-1325 sub not rollup-safe (Merge remote-tracking / pull merges).

@Ada Lovelace — rebuild clean linear tips on origin/ftr/AST-1299-support-alternative-resume-sections; force-with-lease OK; no origin/dev pull merges.

### Files changed (plan vs actual)

_No direct product commit trail on the parent — the epic worktree only carries two `merge origin/dev` housekeeping commits, an epic-registry Threads mirror commit, and the `docs(AST-1299)` archive commit. Implementation landed entirely via the four proposed children and the four UAT bug tickets below._

## Sub-issues

### AST-1303 — Section format catalog and open extra ids
_Archived: 2026-08-19 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1303/section-format-catalog-and-open-extra-ids-support-alternative-resume · Status at archive: Archive · Project: Astral Artifacts · Assignee: ada · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1299; blocks: AST-1306; blocks: AST-1305; blocks: AST-1304_

#### What this implements

Owns the config contract: required seven ids, closed format list (including `bullet_list` and `experience_detail`), default formats for required/historical optional slugs, allowed italic/bold emphasis tags, and structure normalize that accepts extra titled sections instead of rejecting unknown ids. Observable: a structure with Highlights + Publications as `bullet_list` persists; required sections still cannot be omitted. Does not own HTML emit, hops, or the editor UI.

#### Acceptance criteria

- [X] A candidate whose structure is only the seven required sections is a valid persisted structure; absent optional sections do not fail normalize (builder render of that structure is AST-1304).
- [X] Changing a required section's title (e.g. Professional Summary → Summary) changes the stored heading and does not change the section id.
- [X] Required sections cannot be removed from structure (must be present and `enabled=True`).

#### Boundaries

Does not own HTML emit (sibling AST-1304). Does not own hops/content blobs or legacy label ingest (sibling AST-1305). Does not own the editor UI or format picker API (sibling AST-1306).

#### Notes for planning

`RESUME_STRUCTURE_KNOWN_SECTION_IDS` stays the same ten historical ids (composed, not extended). Extra ids are per-candidate. Format list is closed. Experience id is locked to `experience_detail`. Contact ids have no body format.

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Required / historical-optional id tuples; compose `RESUME_STRUCTURE_KNOWN_SECTION_IDS` (same ten ids, same order); body-format tuple, default-format map, extra-id pattern, reserved extra-id tuple, emphasis tag names; `format` on each non-contact DEFAULT entry | utils |
| `src/core/candidate.py` | `normalize_resume_structure`: require the seven ids (present + `enabled=True`); accept extra slug ids; persist `format` from config defaults / closed list; lock `experience` to `experience_detail`; drop `format` on contact ids | core |

#### Stage 1 & 2 — Config catalog + normalize rewrite

⚠️ **Decision:** `RESUME_STRUCTURE_KNOWN_SECTION_IDS` stays the closed **historical** ten-id tuple, composed from required + historical optional so it cannot drift. Extra ids are **not** appended to KNOWN. Hop whitelist (`base_resume` ∩ KNOWN) stays AST-1305.

⚠️ **Decision:** Emphasis allowlist is HTML tag **names** (`i`, `em`, `b`, `strong`), not bracketed tokens and not a free attribute surface. AST-1304 is the only consumer; this ticket only declares the set.

⚠️ **Decision:** Contact/header sections are not one of the six body formats. They have no `format` in DEFAULT and normalize strips `format` if a caller sends one.

⚠️ **Decision:** Required sections must be **present and `enabled=True`**. `enabled=False` on a required id is treated as removal. Title may change; id stays the key.

⚠️ **Decision:** `experience` is locked to `experience_detail`. Other required/historical slugs may carry a different closed format if the caller sends one. Missing format on those slugs uses the default map so current persisted blobs keep working.

⚠️ **Decision:** PUT already merges incoming `sections` onto `resolve_resume_structure` then calls `normalize_resume_structure`. That overlay stays additive. Seven-only and extras-only **wholesale** dicts are the normalize contract (craft `split_craft_resume_base_payload` replaces structure from the agent blob). Do not change the PUT merge in this ticket (AST-1306).

⚠️ **Decision:** Extra sections may choose **any** of the six body formats, including `experience_detail`. Content-array filtering for non-`experience` `experience_detail` extras is AST-1304 / AST-1305 — this ticket only persists the structure row.

Section-loop rules, in order, for each `(sid, spec)`: keep today's dict/id/title/enabled/order checks; `job_agent_editable` defaults `True` for unknown-slug extras when the field is missing; required-missing check runs once before the loop (`ValueError: resume_structure missing required section(s): […]`); a required id with `enabled is False` raises `required section {sid} cannot be disabled`; an id outside KNOWN that is reserved or fails the extra-id regex raises `invalid extra section id: {sid}`; format resolution differs by class — contact ids never carry `format`; `experience` locks to `experience_detail`; every other id backfills from the default map when format is missing/blank, else must be a member of the closed `RESUME_STRUCTURE_BODY_FORMATS` list.

#### Plan review — Joan (plan-rubric.v1, APPROVED)

**discuss** — `astral.layers.ui-config-driven-business-logic` cited; API serve is AST-1306. Child cites UI-config-driven business logic, but this ticket only lands `RESUME_STRUCTURE_*` constants. Non-blocking — config-first placement is correct; sibling contract section already names AST-1306 as the API consumer.

#### QA test manifest — Betty

Existing (bible-backed): `TestAst517ResumeStructureConfig`, `TestAst1010CandidateTaglineConfig`, revised `TestAst517ResumeStructure` (required-seven reject cases + persist fixtures), `TestParseCandidateResume(Extended)`, `TestRunCandidateArtifactGeneration::test_persists_artifacts_on_craft_resume_base_success`, AST-996 split/persist/session methods. Broken/obsolete revised this pass: AST-517 `unknown resume section id` and three-id blobs through normalize/split/parse — required-seven now fires first; valid extras no longer unknown; slim `_three_section_structure` kept only for projection helpers. Gaps (new): `TestAst1303ResumeStructureCatalog` (config + candidate) — required/historical compose KNOWN; closed formats; DEFAULT format from the map; seven-only + Highlights/Publications `bullet_list`; title keeps id; omit/disable required; reserved/invalid extra ids; format lock / extras.

#### Radia review — code-rubric.v1, CLEAN

Full 65-statute active-set sweep (scoped ticket delta `3d744e02` + `3ab84c5e`, `src/utils/config.py` + `src/core/candidate.py`): all `conforms` / `not-applicable`, no violations. `KNOWN` tuple preserved for AST-1270 / AST-1305 hop intersection stability; required-seven + open-extra contract explicit and config-driven; `experience` format lock and contact `format` omission match parent decisions. Merged `origin/dev` into this sub for §9a on resolve (prep-uat dry-run was dirty on the pre-merge tip, including `candidate.py`); catalog + normalize contract unchanged after the merge.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/utils/config.py` | `RESUME_STRUCTURE_*` catalog family + DEFAULT formats | `3d744e02e` — +39/-2 |
| ✓ | `src/core/candidate.py` | `normalize_resume_structure` rewrite (required seven, open extras, format) | `3ab84c5e0` — +45/-6 |
| | _tests_ | resume section catalog + open extra-id normalize coverage | `69d0ae6af`; bible `docs/test-bible/core/candidate.md` @ `fbc7d2cdecdca0b59fa9c9648f6d0973320912a8` |

### AST-1304 — Builder emit by section format
_Archived: 2026-08-19 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1304/builder-emit-by-section-format-support-alternative-resume-sections · Status at archive: Archive · Project: Astral Artifacts · Assignee: hedy · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1299_

#### What this implements

After #1: render enabled sections in structure order by format, reusing the existing Somerset treatments; Highlights and Publications print as `bullet_list`; `experience_detail` uses today's job-array fields; html-style italic/bold in body text render; leftover prose Experience is not treated as the required Experience section. When `debug=True`, log id / title / format / emit outcome per section (Style D). Does not own hop schemas or the structure editor.

#### Acceptance criteria

- [X] Adding Highlights as `bullet_list` and Publications as `bullet_list` prints those headings and bulleted lines in structure order.
- [X] Changing an optional section's format changes the HTML treatment without creating a new section id.
- [X] Html-style italic and bold tags in a `bullet_list` body render as italic and bold; other tags are not a raw HTML hole.
- [X] A leftover prose Experience string is not rendered as the required Experience section; Experience counts only as an `experience_detail` array.
- [X] With `debug=True`, each enabled section logs id, title, format, and emit outcome under Style D headers and `|` detail.

#### Boundaries

Does not own hop schemas (sibling AST-1305) or the structure editor (sibling AST-1306). Does not change cover-letter shape or emit. Does not edit `BUILD_CONFIG["supported_sections"]` or invent new visual styles beyond reusing Somerset list chrome for `bullet_list`. Does not drop leftover Experience prose in `filter_content_to_resume_structure` (persist/regenerate is AST-1305); builder emit only skips it. Does not slug titles or accept extra keys on craft/draft hops (AST-1305).

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/builder.py` | Dispatch body emit by `format`; add `bullet_list` treatment; skip leftover prose Experience; restore allowlisted italic/bold in body text; Style D per-section trail when `debug=True` | core |
| `src/core/candidate.py` | Widen `filter_content_to_resume_structure` so extra `experience_detail` job arrays and extra list-of-scalars bodies reach the builder; does **not** drop leftover Experience prose | core |

#### Stage 1 & 2 — Emit by format + Style D trail

⚠️ **Decision:** Escape-then-restore via exact no-attribute tags (not a general HTML sanitizer) — the closed italic/bold surface AST-1303 declared. `<I>` becomes `<i>`; `<i class="x">` stays escaped.

⚠️ **Decision:** Extra `experience_detail` job arrays must survive the filter or emit cannot show them. Extra `bullet_list` list-of-scalars must coerce to a newline string. Dropping Experience prose in this shared filter would change tracker persist — that regenerate is AST-1305.

⚠️ **Decision:** Highlights bullets share Experience list chrome — reuse of the Somerset treatment, not a new visual language.

⚠️ **Decision:** Required Experience has no prose render fallback. Extra sections may use `experience_detail` and then must be a job array to print. Format, not id, chooses the treatment so AST-1306 format edits change HTML without minting a new id.

⚠️ **Decision:** Per-section `debug_index` (Style D headers) rather than only `|` lines under the document header. Contact ids are enabled sections and must appear in the `N/M` walk even though they are not body formats.

Format dispatch table: `free_prose` → today's `professional_summary` paragraph path; `bullet_list` → new `_emit_bullet_list_html`, skip if empty; `word_cloud` → today's Core Competencies/Prior Experience pipe path; `dual_column` → `_emit_skills_grid_html` (escape swapped for emphasis-safe); `indented_bold_single` → `_emit_education_list_html` (same swap); `experience_detail` → job-array emit if `is_experience_job_array`, else skip (no `div.prose-block`, no `json.dumps`). Style D outcomes: `emitted`, `skipped — empty`, `skipped — leftover prose`, `skipped — not job array`, `skipped — missing format`.

#### Plan review — Joan (plan-rubric.v1, APPROVED)

**discuss** — Traceability table uses parent AC numbers (2–6), not child checkbox order (1–5). Non-blocking. **discuss** — `filter_content_to_resume_structure` widens the persist path before AST-1305 hop ingest lands; end-to-end Highlights/Publications from craft hops needs AST-1305 on the rollup line. Non-blocking for this child — plan correctly scopes emit vs persist and names AST-1305 for regenerate.

#### QA test manifest — Betty

Hedy hit a genuine cross-branch collision mid-build: `merge-tests(AST-1304)` had pulled in AST-1305's not-yet-landed `test(AST-1305)` commits, adding a module-level `from src.utils.config import RESUME_STRUCTURE_EXTRA_DEFAULT_FORMAT` to `test_candidate.py` — an AST-1305 product name not on AST-1304's tree — which broke collection of **every** `test_candidate.py` node on this branch including AST-1304's own `TestAst1304FilterContentToResumeStructure`. Hedy declined to add the sibling constant on this ticket and asked Betty to either scope `merge-tests` to AST-1304 only or move the import into AST-1305's own test classes; Betty moved it. A second, unrelated test-layer fix followed: an emphasis-helper assertion expected `&#34;` but CPython `html.escape(quote=True)` emits `&quot;` — a test bug, not a product hole (confirmed: attributed open + orphan `</i>` both already escaped correctly). New: `TestAst1304BuilderEmitByFormat` (bullet_list Highlights/Publications in order; format swap keeps `id="education"`; emphasis tags render/other tags escaped; leftover Experience prose skipped; job array still emits; extra `experience_detail` + `_render_content_keys`; Style D per enabled section; `debug=False` quiet; cover debug has no resume-section trail); `TestAst1304FilterContentToResumeStructure` (leftover Experience prose kept; extra job array kept; scalar list coerced; mixed dict-list dropped).

#### Radia review — code-rubric.v1, CLEAN

Full 65-statute sweep (scoped ticket delta `6c6e7dd5` + `757f2cda`): all conforms/not-applicable. Format-driven dispatch preserves historical Somerset treatments via the AST-1303 default map; `bullet_list` is the only new visual helper. Closed emphasis surface: escape-then-restore exact no-attribute tags; attributed/script tags stay escaped. Leftover Experience prose skipped at emit while filter keeps it for tracker persist — matches the explicit plan decision vs AST-1305 regenerate.

#### Resolution (2026-08-11)

CLEAN. No fix-now. Advisory (sibling ancestry): publish ref rebuilt onto `origin/ftr` — AST-1304 commits only, one `merge-tests(AST-1304)`. Advisory (filter vs AST-1305): leftover Experience prose stays in `filter_content_to_resume_structure` per plan; emit still skips it.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/core/builder.py` | Emit dispatch by format, `bullet_list`, emphasis restore, skip leftover prose | `044001664` (Stage 1, with `candidate.py`) — +118/-87 net; `b39d6b759` (Stage 2, Style D) — +52/-2 |
| ✓ | `src/core/candidate.py` | Widen `filter_content_to_resume_structure` | `044001664` — see above |
| | _tests_ | builder emit by format + leftover Experience skip coverage | `6e51cf514`; bible `docs/test-bible/core/builder.md` @ `59faa635c09d437be64fd5fc592867f92db9b171` |

### AST-1305 — Hops, content blobs, and legacy extra labels
_Archived: 2026-08-19 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1305/hops-content-blobs-and-legacy-extra-labels-support-alternative-resume · Status at archive: Archive · Project: Astral Artifacts · Assignee: katherine · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1299_

#### What this implements

After #1: craft-base and draft-job accept extra section keys; draft whitelist is the candidate's current base resume keys (including extras), not the old ten-id intersection. Legacy label/content arrays keep unmatched titles as extra sections. Experience persists as an `experience_detail` array (regenerate prose). Does not own HTML chrome or AST-1201 generation order.

#### Acceptance criteria

- [X] Craft-base and draft-job hops accept extra keys that exist on that candidate's base resume / structure; no "unknown section" merely because the key is outside the old ten-id list.
- [X] A job resume cannot introduce a section the candidate structure does not enable.
- [X] An Abrams-style label/content array that includes Highlights and Publications does not drop those labels on ingest or token serialize.
- [X] A leftover prose Experience string is not persisted as the required Experience section; Experience counts only as an `experience_detail` array.

#### Boundaries

Does not own HTML chrome (sibling AST-1304). Does not own AST-1201 generation order. Does not own the structure editor or format picker API (sibling AST-1306). After AST-1303.

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `RESUME_STRUCTURE_EXTRA_DEFAULT_FORMAT = "bullet_list"` next to the AST-1303 family | utils |
| `src/core/candidate.py` | Legacy label ingest + slug; token serialize keeps unmatched titles; flatten/split/filters accept extra ids and job arrays; draft whitelist drops the KNOWN intersection; draft validate rejects prose Experience | core |
| `src/core/tracker.py` | `_resume_section_has_body` / `_resume_payload_body`: a non-empty job array is a body for any section id | core |
| `src/ui/api/api_candidate.py` | PUT `/data`: when `artifacts.base_resume` is a label/content list or dict, call the core ingest helper before filter/save | ui |

#### Stage 1–3 — Ingest, whitelist, prose-Experience omission

Root of the family's own bug (fixed here, before AST-1322 re-broke the dict path): `format_base_resume_for_token` dropped unmatched labels on a `title_to_id` miss; `draft_job_resume_allowed_section_keys` was `base ∩ RESUME_STRUCTURE_KNOWN_SECTION_IDS`, so extras never validated; `_flatten_craft_resume_section_strings` gated on the same closed KNOWN set.

New public `ingest_legacy_label_content_base_resume(raw_base, structure) -> (content, structure)` — the single ingest function later shared by token serialize, PUT, and draft whitelist: handles both a **dict** (title-keyed or id-keyed) and a **list** (`{label, content}` items) shape; resolves each key/label to a section id via `_title_to_structure_section_id` (title match against live or default structure) or mints one via `_slug_resume_extra_section_id` (slugify + collision-suffix `_2`, `_3`, …); appends a new structure row with `format` from the default map or `RESUME_STRUCTURE_EXTRA_DEFAULT_FORMAT` (`bullet_list`) when minting; omits prose `experience` entirely (regenerate, not stub); re-normalizes via `normalize_resume_structure` before returning.

⚠️ **Decision:** Unmatched Abrams titles become extras with `format` from `RESUME_STRUCTURE_EXTRA_DEFAULT_FORMAT` (`bullet_list`), not `experience_detail`. Historical titles that match `RESUME_STRUCTURE_DEFAULT` titles reuse those ids instead of minting a parallel extra.

⚠️ **Decision:** Slug collisions and reserved ids take `_2`, `_3`, … so a label is never dropped.

⚠️ **Decision:** Whitelist = this candidate's current base section keys after label ingest, including extra slugs. It is **not** `base ∩ KNOWN` and **not** "all enabled structure ids" — a job still cannot invent a section that is only on structure and not on base.

⚠️ **Decision:** Do not invent a stub job object from leftover prose Experience. Omit on persist/token and fail draft validate so the hop regenerates a real `experience_detail` array.

#### Plan review — Joan (plan-rubric.v1, APPROVED)

**discuss** — Stage 2 §6 (`tracker._prepare_job_resume_content`) re-injects base-whitelist keys dropped by enabled-only `filter_content_to_resume_structure`, so Abrams extras can persist before structure is saved on disk. Deliberate, but tensions with strict "does not enable" wording if a base key exists while the persisted structure row is disabled or absent. Confirm product intent: keep the bridge for un-ingested extras (adopted), or intersect with `enabled_resume_section_ids` first. **acceptable** — plan doc labels child work as parent AC 5–8 while Linear child ACs are 1–4; cosmetic, mapping correct. **acceptable** — AST-1304 sibling also widens `filter_content_to_resume_structure` for format emit; merge-order coordination, not a plan defect.

#### QA test manifest — Betty

New: `TestAst1305ResumeStructureExtraDefault`, `TestAst1305HopsContentBlobsAndLegacyLabels`, `TestAst1305LegacyLabelIngestApi`, `TestAst1305JobResumeExtras`. Revised existing: `TestAst517ResumeStructure` (job-array Experience fixtures); `TestAst594DraftJobResumePayload`; `TestAst996ExperienceJobArray::test_split_still_keeps_legacy_string_experience` (asserts omit); `TestAst997JobTailoredExperience` (prose Experience → `experience_detail` reject); `TestAst1270NestedDraftJobResumeContract` (whitelist includes extras; reserved/`123bad` dropped); `TestAst986SessionResumeParse` (`context.raw_resume`, not stale `starting_resume_text`); `TestAst519ResumeStructureApi::test_put_base_resume_strips_orphan_keys`. Broken/obsolete this pass (revised in-tree): AST-996 kept leftover prose Experience; AST-997 accepted prose on draft validate; AST-1270 intersected `base ∩ KNOWN`; AST-517/session/craft-persist stored `"Jobs"` strings; AST-519 PUT `orphan_section` would become an extra. Katherine flagged two test-layer-only reds during `[qa-handoff]` (a Judith `agent_task.json` prompt-contract assertion that is AST-996's own scope, and the `raw_resume` vs stale `starting_resume_text` naming) — Betty retargeted both, not product bugs.

#### Radia review — code-rubric.v1, CLEAN

Full 65-statute sweep (scoped ticket delta `98bb5bbe` + `71c60385` + `2fb7a993`, four planned files): all conforms/not-applicable. AC7 fix confirmed: unmatched Abrams labels (`highlights`, `publications`) survive ingest and `{$BASE_RESUME}` token JSON. Extra hop keys accepted via `_is_resume_content_section_id` without reopening the closed KNOWN catalog. Draft whitelist per-candidate base keys post-ingest; unknown-key gate preserved. Prose Experience omitted on ingest/token/split/filter, rejected on draft validate.

Advisories (all accepted as-is on resolve, no code change): tracker bridge vs strict "enabled structure" wording — left as approved Stage 2 §6, base-whitelist re-inject intentional until extra structure rows exist on disk; `filter_content` scalar-list coercion — non-dict list coercion via `_coerce_resume_section_string` stays, covered by tests; ftr merge coordination on `filter_content_to_resume_structure` (also touched by AST-1304/1306 on sibling branches) — merge-child's problem, not this tip.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/utils/config.py` | `RESUME_STRUCTURE_EXTRA_DEFAULT_FORMAT = "bullet_list"` | `98bb5bbe9` (Stage 1, with others) |
| ✓ | `src/core/candidate.py` | Ingest helper + token serialize + flatten/whitelist/filters | `98bb5bbe9` (Stage 1) + `71c603853` (Stage 2) + `2fb7a993f` (Stage 3) |
| ✓ | `src/core/tracker.py` | Any-key job-array body helpers + persist bridge | `71c603853` |
| ✓ | `src/ui/api/api_candidate.py` | PUT calls ingest helper before filter/save | `98bb5bbe9` — three-file commit +139/-26 net |
| | _tests_ | hops accept extras; Abrams labels stay; Experience job-array only | `f27148fd5`, `98921eec7`, `06ace6fec`; bible `docs/test-bible/core/candidate.md` @ `c719f089bb4b8f102de9198fe6b84d04085c4dba` |

### AST-1306 — Author extra sections (title and format)
_Archived: 2026-08-19 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1306/author-extra-sections-title-and-format-support-alternative-resume · Status at archive: Archive · Project: Astral Artifacts · Assignee: ada · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1299_

#### What this implements

After #1: operators can add, title, format, enable, and reorder optional sections; required seven cannot be removed. Format choices come from the config catalog via the API (not a hardcoded React list). Does not own print CSS or hop prompts.

#### Acceptance criteria

- [X] Changing a required section's title persists the new title and does not change the section id. Printed heading is AST-1304 reading that stored title.
- [X] Changing an optional section's format persists the new format on the same section id. HTML treatment is AST-1304.
- [X] Required sections cannot be removed from structure (must be present and `enabled=True`).

#### Boundaries

Does not own print CSS / HTML emit (sibling AST-1304). Does not own hop prompts or legacy label ingest (sibling AST-1305). After AST-1303.

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `RESUME_STRUCTURE_NEW_EXTRA_DEFAULT_FORMAT = "bullet_list"` next to the AST-1303 family | utils |
| `src/core/candidate.py` | `slug_resume_section_id` + `prepare_resume_structure_sections_for_save`; do **not** change `normalize_resume_structure` / `enabled_resume_structure_sections` | core |
| `src/ui/api/api_candidate.py` | GET returns `all_sections` + `catalog` (keep `sections` as enabled `{id, label}`); PUT replaces `sections` when that key is present (no longer additive overlay) | ui |
| `src/ui/frontend/src/components/ResumeStructureEditor.tsx` | New editor: title/format/enable/reorder/remove optional/add extra; format `<select>` options from `catalog.body_formats` only | ui |
| `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` | Render the editor above the accent bar; refetch tabs after structure save | ui |
| `src/ui/frontend/src/App.css` | Structure editor styles | ui |

#### Stage 1 & 2 — Catalog/slug/GET/PUT replace + editor component

⚠️ **Decision:** Catalog is served on this GET, not on `/api/system/ui_config` — one fetch already loads structure; duplicating the list would be a second source. ⚠️ **Decision:** `sections` stays enabled `{id, label}` so `ArtifactEditor` and `JobAnalysisReportModal` do not change; authoring uses `all_sections` + `catalog`. ⚠️ **Decision:** When `sections` is present, PUT **replaces** the map (then normalize) — additive overlay cannot drop optionals; accent-only PUT has no `sections` key and must not wipe sections. ⚠️ **Decision:** Keys that are not known and not a valid extra slug (`_pending_0`) are slugged from `title` in core — React must not implement a slug algorithm. ⚠️ **Decision:** `format_locked` is `experience` or a contact id; required body ids may still change format.

Editor: one row per section (read-only id, title input, format select from `catalog.body_formats` only, Enabled checkbox disabled when required, Job-agent-editable checkbox, Up/Down reindexing `order`, Remove only on non-required). Add-extra row appends a local `_pending_N` row (no PUT until Save). `Save sections` PUTs the full local `rows` array; core slugs pending ids on save.

#### Plan review — Joan (plan-rubric.v1, APPROVED)

**discuss** — Traceability table uses parent AC numbers, not child checkbox ids. Non-blocking. **discuss** — `pattern.ui.admin-endpoint` canonical refs cite `api_admin.py`; plan correctly keeps `@require_auth` on existing candidate routes and documents why (candidate-scoped artifacts, no duplicate catalog). Acceptable — do not add `/api/admin` routes for this child.

#### QA test manifest — Betty

Found a real one-line product bug during check: `get_candidate_resume_structure`'s GET sort used `key=lambda kv: (…, sid)` where `sid` was an unbound closure variable (`NameError`) — every GET `/resume_structure` test 500'd. Ada fixed `sid` → `kv[0]`. Manifest: `TestAst1306ResumeStructureCatalog` (config `RESUME_STRUCTURE_NEW_EXTRA_DEFAULT_FORMAT == "bullet_list"`), `TestAst1306ResumeStructureSavePrep` (slug + prepare — pending rekey, reserved/empty reject, duplicate slug), `TestAst1306ResumeStructureAuthorApi` (GET catalog + all_sections; PUT replaces sections, drops omitted optional, keeps required; accent-only PUT leaves sections; omit `experience` → 400; `_pending_*` slugs from title), `TestAst519ResumeStructureApi` (revised fixture; PUT invalid-sections 400 now asserts `"missing required"`), plus Vitest `test_ArtifactsBaseResumeContent` / `test_ResumeStructureEditor` (format `<option>`s from catalog; no Remove on required; add pending extra; page renders editor from GET catalog).

#### Radia review — code-rubric.v1, FIX-NOW

**fix-now — out-of-plan `filter_content_to_resume_structure` change.** Stage 1 step 3 limited `candidate.py` edits to `slug_resume_section_id` and `prepare_resume_structure_sections_for_save`, explicitly leaving `filter_base_resume_to_structure` alone; Files Changed did not list content filtering. The diff (`bf147fb6`) widened job-array preservation to any key, added a string-`experience` fallback, and coerced non-dict lists — content-shape behavior owned by AST-1305 (legacy label/content arrays), not structure authoring. **Recommendation:** revert the hunk on this sub-branch; land equivalent behavior on the sibling ticket that owns content ingest/filtering.

Full 65-statute sweep otherwise scored conforms/not-applicable on the remaining four files (config key, two core helpers, GET/PUT, editor component + page + CSS) — no other violations. Advisory (non-blocking): plan specified inline TSX types; implementation exported `Catalog`/`SectionRow` for page import — harmless DRY improvement.

#### Resolution (2026-08-11)

FIX-NOW cleared. Reverted the out-of-plan `filter_content_to_resume_structure` hunk in `src/core/candidate.py` back to the AST-1303 loop (job-array only on `experience`; string values otherwise) — that content-shape widening landed properly on AST-1305 instead. Advisory exported editor types left as-is.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/utils/config.py` + `src/core/candidate.py` | `RESUME_STRUCTURE_NEW_EXTRA_DEFAULT_FORMAT`; slug + prepare-for-save helpers | `bf147fb6b` (Stage 1, with `api_candidate.py`) — +85/-5 net across three files; out-of-plan `filter_content_to_resume_structure` hunk reverted at resolve |
| ✓ | `src/ui/api/api_candidate.py` | GET `all_sections`+`catalog`; PUT replace; GET sort-key `NameError` fix | `bf147fb6b` + `1e405f2c4` (sort-key fix, tagged `test(AST-1306)` but a product one-liner) |
| ✓ | `ResumeStructureEditor.tsx` / `ArtifactsBaseResumeContent.tsx` / `App.css` | New structure editor + page wiring + CSS | `cc00324c9` — +295/-4 across three files |
| | _tests_ | slug/prepare, GET catalog, PUT replace/drop-optional, editor, page integration | `c4b7adbb6`, `1e405f2c4`; bible `docs/test-bible/frontend/pages.md` |

### AST-1322 — Saving base_resume drops Highlights / extra sections
_Archived: 2026-08-19 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1322/saving-base-resume-drops-highlights-extra-sections-support-alternative · Status at archive: Archive · Project: Astral Artifacts · Assignee: katherine · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1299_

#### UAT report (verbatim)

[bug] This did not parse the actual content of the candidate_data.artifacts.base_resume content. The example provided included a section called Highlights, and when I saved the object to the candidate_data, it gave me the original set of content, not Highlights.

#### As-is

`PUT /api/candidates/<id>/data` with `artifacts.base_resume` that includes a Highlights (or other extra) section as a **title-keyed dict** (e.g. `{"Highlights": "…", "professional_summary": "…"}`) persists only the pre-existing fixed section ids. Highlights / Publications disappear from the saved `base_resume`. Label/content **list** Abrams payloads already kept those extras (AST-1305).

#### To-be

Saving that object keeps Highlights and other extra sections present in the payload on the candidate's `base_resume` (id-keyed, e.g. `highlights`) and adds matching enabled rows on `artifacts.resume_structure` when missing — same outcome the list ingest path already produces.

#### Repro

Fixture (seven-required-only or default structure on disk; no `highlights` row yet):

```python
base_resume = {
    "professional_summary": "Summary body",
    "Highlights": "Won awards",
    "Publications": "Paper one",
}
# PUT artifacts={"base_resume": base_resume}  (no resume_structure in body)
```

Observed after save: `base_resume` has `professional_summary` only; no `highlights` / `publications`. Expected: `base_resume["highlights"] == "Won awards"`, `base_resume["publications"] == "Paper one"`, and `resume_structure.sections` includes those ids with `enabled=True`, `format=bullet_list`. Contrast (already green): same titles as `[{"label": "Highlights", "content": "Won awards"}, …]` survive PUT today.

#### Root cause

`ingest_legacy_label_content_base_resume` **dict** branch only mints an extra structure row when the key already matches `RESUME_STRUCTURE_EXTRA_ID_PATTERN` (`^[a-z][a-z0-9_]*$`). Display-label keys such as `"Highlights"` / `"Publications"` are copied into `content` under those raw keys but never get a section row. PUT then rebuilds `section_ids` from `enabled_resume_structure_sections(ingested_struct)` and `filter_base_resume_to_structure` drops every key not in that set — so the title-case extras vanish. The **list** branch already resolves titles via `_title_to_structure_section_id` / `_slug_resume_extra_section_id`; the dict branch did not.

#### Proposed change

In `src/core/candidate.py` `ingest_legacy_label_content_base_resume`, the dict-branch loop now resolves each key to a section **id** the same way list labels do, then writes `content[sid]` (not the raw title key): skip reserved extra ids and `accent_color` (unchanged); if `k` is already a usable id, keep it (minting the row if missing and a valid extra id); else treat `k` as a display label — resolve via `_title_to_structure_section_id`, or slug + mint via `_slug_resume_extra_section_id`; apply the existing Experience rules to `v`; on a slug collision, re-slug the same way the list path does; do **not** mint extras for lowercase keys that fail the extra-id pattern and are not title-matched (e.g. `123bad`) — those stay un-rowed so the existing filter still drops them (AST-519 orphan strip preserved). No PUT / editor / builder call-site changes — they already call this ingest helper and filter on post-ingest enabled ids.

⚠️ **Decision:** Title-keyed dicts are first-class Abrams cousins of `{label, content}` lists — resolve via title-match then slug. Do not invent a second ingest helper. Do not change ArtifactEditor in this bug (editor already saves structure **ids** as keys when the section exists on structure).

#### Blast radius

Shared `ingest_legacy_label_content_base_resume`: PUT, `format_base_resume_for_token`, `draft_job_resume_allowed_section_keys` — title-keyed base blobs start surviving all three. AST-1305 list ingest / collision / prose Experience omit must still hold. AST-1306 `slug_resume_section_id` / `prepare_resume_structure_sections_for_save` / editor PUT path unchanged.

#### Radia review — code-rubric.v1, PROCEED (bug-fix lane)

Ticket-scoped product delta: `8f537d4f` (`src/core/candidate.py`, dict branch only). Full 65-statute sweep: all conforms/not-applicable — reuses AST-1305 private helpers, no parallel ingest helper, single-function surgical fix, collision handling mirrors the list path. `[bug-repro]` tests: `TestAst1322TitleKeyedBaseResumeDict::test_ingest_title_keyed_dict_keeps_highlights_and_publications` (pins `content["highlights"]`/`["publications"]`, structure rows, `bullet_list` format, absence of title-case keys — would fail pre-fix); `TestAst1305LegacyLabelIngestApi::test_put_title_keyed_dict_keeps_highlights_and_publications` (end-to-end PUT). "What must still hold" all confirmed OK: AST-1305 list ingest + prose Experience omit untouched; draft still cannot invent disallowed sections; `RESUME_STRUCTURE_EXTRA_DEFAULT_FORMAT` (`bullet_list`) still used for mints; no builder/editor TSX in the delta.

**Notes:** parent shape normal, stacked on `origin/ftr/AST-1299` → Chuckles clean-review shortcut to User Testing (skip resolve-child). `merge-tests` @ `4c13304c` bundles unrelated sibling test/bible commits (AST-1311/1317/1318/…) on the `ftr...sub` diff; engineer product scope remains `8f537d4f` only.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/core/candidate.py` | Dict-branch title resolution in `ingest_legacy_label_content_base_resume` | `788ec269b` — +32/-11 |
| | _tests_ | title-keyed Highlights survive ingest/PUT | `8a91b8771` / `c3d5795e0` |

### AST-1323 — Structure editor: controls on collapsible header row with body between
_Archived: 2026-08-19 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1323/structure-editor-controls-on-collapsible-header-row-with-body-between · Status at archive: Archive · Project: Astral Artifacts · Assignee: ada · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1299_

#### UAT report (verbatim)

[bug] Put the section labels, type select, enabled, job-edit (instead of job agent editable) and the up/down buttons on a single collapsible header row with the text for that section appearing between the headers (instead of the bottom of the page).

#### As-is

On Base Resume Content, structure fields (title, format select, enabled, "Job agent editable", up/down, Remove) live in a flat `ResumeStructureEditor` panel above the accent bar. Section body text is edited separately in `ArtifactEditor` collapsible panels lower on the page, so structure controls and body text are not interleaved.

#### To-be

Per section, one `CollapsiblePanel` header row holds: section title (label), format type select, enabled, **Job edit** (short label, same `job_agent_editable` field), and up/down. That section's body text appears in the panel body between headers. Add-section / required-cannot-remove / catalog-driven formats still hold from AST-1306.

#### Root cause

AST-1306 Stage 2 shipped structure authoring as a standalone flat list (`ResumeStructureEditor`) stacked above an unchanged `ArtifactEditor`. The page never placed structure controls on `CollapsiblePanel` headers that already wrap each section body.

#### Proposed change

UI-only — no GET/PUT/slug/normalize/config catalog changes. `ArtifactEditor.tsx` gains optional authoring props (`structureCatalog`, `structureRows`, `onStructureRowsChange`, `onStructureSave`, `structureSaving`, `structureError`), used only by Base Resume Content — `JobAnalysisReportModal` never passes them, so its read-only structure tabs are unchanged. When those props are present, each `CollapsiblePanel` header becomes a single row: title input, format select (catalog-driven, locked for contact/`experience`), Enabled checkbox (disabled when required), **Job edit** checkbox (same `job_agent_editable` field, short label), Up/Down (reindexing `order`), Remove only when not required. Section body `LabeledTextArea` stays between headers, unchanged. `ArtifactsBaseResumeContent.tsx` drops the standalone `<ResumeStructureEditor>` above the accent bar and instead passes the same props into `ArtifactEditor`; Add-section + `Save sections` move below the collapsible stack. `ResumeStructureEditor.tsx` is reduced to a thin type-export module (`Catalog`, `SectionRow`) — no default-exported UI left on the page.

⚠️ **Decision:** Authoring lives on `ArtifactEditor` headers when catalog props are passed — not a second collapsible stack. ⚠️ **Decision:** Content save (base_resume) stays ArtifactEditor Save/autosave; structure persist stays the existing PUT replace via `Save sections`.

#### Blast radius

`ArtifactEditor` structureMode is also used by `JobAnalysisReportModal` — must remain unchanged unless catalog/authoring props are passed. Betty Vitest suites assuming a standalone editor need revision. API/core/config contracts from AST-1306 are untouched.

#### Radia review — code-rubric.v1, REVIEW → cleared

Ticket-scoped product delta: `21986a9e` (`ArtifactEditor.tsx`, `ArtifactsBaseResumeContent.tsx`, `ResumeStructureEditor.tsx` types-only, `App.css`). Full 65-statute sweep: all conforms/not-applicable — UI-only, no API/core/config/hop edits, `structureAuthoring` gate correctly prevents accidental authoring chrome on the job modal.

**fix-now — obsolete `test_ResumeStructureEditor.test.tsx` after default export removed.** Plan step 4 removed the flat editor UI; the component test still imported and rendered the `ResumeStructureEditor` default export (AST-1306 cases) — import/render would fail on full frontend tier even though the AST-1323 page bug-repro was green. **Recommendation:** delete or rewrite the file; migrate any still-needed catalog assertions into `test_ArtifactsBaseResumeContent` (page test already covers header authoring). **advisory** — dead CSS for the removed flat editor (`.base-resume-structure-editor` / `-title` / `-row` / `-row-id`) left unused; `.base-resume-structure-add` / `-save` still used. Optional cleanup, non-blocking.

**What's solid:** correct UX target (structure authoring interleaved with section bodies on one collapsible stack); bug-repro page test directly encodes the reported layout defect and To-be.

#### Resolution (2026-08-11)

REVIEW fix-now cleared: Betty dropped the obsolete `test_ResumeStructureEditor.test.tsx` and migrated catalog asserts into the page suite. Module remains types-only; product tip unchanged.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `ArtifactEditor.tsx` / `ArtifactsBaseResumeContent.tsx` / `ResumeStructureEditor.tsx` / `App.css` | Authoring props on collapsible headers; standalone editor removed; page wiring; CSS | `faf8740cf` — +203/-175 across four files |
| | _tests_ | structure controls on collapsible header row + drop obsolete flat-editor suite | `89acd3bad`/`bef854d1b`, `8884b932c`/`e5b5710ae` |

### AST-1324 — base_resume_content must load/render existing artifact sections (default prose)
_Archived: 2026-08-19 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1324/base-resume-content-must-loadrender-existing-artifact-sections-default · Status at archive: Archive · Project: Astral Artifacts · Assignee: ada · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1299_

#### Susan comment (verbatim)

[bug] Sorry, Chuckles, I think I wasn't clear enough about this. It's not the SAVE that is the issue. It's the RENDER of the existing base_resume artifact. The base_resume_content page should render FREELY based on the information in the base_resume artifact, setting the style to "prose" by default if it's missing. I'm asking you to LOAD from what is already in candidate_data, which I artificially applied and correctly has all the sections I want. Does that clear things up?

#### As-is

On `/artifacts/base_resume_content`, collapsible section tabs and structure chrome come only from `GET /api/candidates/<id>/resume_structure` → `resolve_resume_structure` (reads `artifacts.resume_structure`, else the default seven/ten). `ArtifactEditor` then loads `candidate_data.artifacts.base_resume`, but `mapFixedFieldsFromRaw` only fills tabs for structure ids. Section keys that already exist on `base_resume` but are missing from `resume_structure` never appear. Body sections present in structure with no `format` surface as `catalog.new_extra_default_format` (`bullet_list`), not prose.

#### To-be

Opening Base Resume Content loads and renders freely from what is already in `candidate_data.artifacts.base_resume`: every usable content section key on that artifact gets a collapsible panel with its stored body. When a section's format/style is missing, the load path defaults it to `free_prose` (Susan: "prose"). This is a **load/render** fix — not a change to the content Save contract from AST-1322.

#### Repro

Fixture: `candidate_data.artifacts.base_resume` is an id-keyed dict already including `professional_summary` plus an extra such as `highlights` with a nonempty string body, while `artifacts.resume_structure.sections` either omits that extra or lists it with `format` absent/null. Opening the page (no Save first): **broken** — the extra's body is not shown as its own panel, or format does not read as prose when missing; **fixed** — every content key present on `base_resume` appears with its body, missing format shows/selects `free_prose`.

#### Root cause

Read path never unioned `artifacts.base_resume` keys into the structure served to the page. PUT already ran `ingest_legacy_label_content_base_resume` (which can append missing ids), but GET / `resolve_resume_structure` did not — so the content page could not render an artificially applied `base_resume` until structure caught up. Separately, missing format fell through to `RESUME_STRUCTURE_NEW_EXTRA_DEFAULT_FORMAT` / `bullet_list` in the authoring select, not Susan's load default of prose (`free_prose`).

#### Proposed change

Scope: hydrate on the **read** path only. Do not change AST-1322 PUT title-key ingest, AST-1306 Save-sections replace semantics, or AST-1323 header layout. New read-only `hydrate_resume_structure_from_base_resume(resolved, base_resume) -> dict` in `src/core/candidate.py`: deep-copies `resolved`; for each usable content-section key already on `base_resume` that is missing from `sections`, appends an enabled row (title-cased id, `job_agent_editable=True`, next order, `format` from the default map else **`free_prose`** — explicitly **not** `RESUME_STRUCTURE_EXTRA_DEFAULT_FORMAT` / `bullet_list`); for a key already in `sections` whose body-section format is missing or invalid, backfills the same `free_prose`-or-mapped default; supports a `{label, content}` list shape via the same title→id / slug rules, structure rows only. Does not write candidate_data. `get_candidate_resume_structure` calls the hydrate helper right after `resolve_resume_structure` and before building `sections`/`all_sections`/`catalog`. Frontend needs no change once GET returns hydrated enabled sections (existing `mapFixedFieldsFromRaw` already shows each hydrated id's body).

⚠️ **Decision:** Hydrate is read-time for GET `/resume_structure` only. Persisting the merged structure remains the operator's Save sections (or a later PUT that runs ingest) — content Save must not be required to "discover" sections already on `base_resume`. ⚠️ **Decision:** "Prose" means catalog format `free_prose`, not a new style string and not `bullet_list`.

#### Blast radius

`GET /resume_structure` callers: Base Resume Content, `JobAnalysisReportModal` structure fetch, any other `sections`/`all_sections` consumer. `resolve_resume_structure` itself stays as today (hydrate is GET-only so builder/token paths stay unchanged until structure is saved). PUT ingest / `filter_base_resume_to_structure` / AST-1322 title-keyed save — untouched.

#### Radia review — code-rubric.v1, PROCEED (bug-fix lane)

Ticket-scoped product delta: `e0825092` (`src/core/candidate.py`, `src/ui/api/api_candidate.py` only). Full sweep: conforms/not-applicable throughout — reuses `_is_resume_content_section_id`, `_title_to_structure_section_id`, `_slug_resume_extra_section_id`, no second eligibility table. `[bug-repro]`: `TestAst1324HydrateResumeStructureFromBaseResumeGet::test_get_includes_base_resume_extra_with_free_prose_default` pins `highlights` in `all_sections`/`sections`, `format == "free_prose"` (not `bullet_list`) — would fail pre-fix. "What must still hold" all OK: AST-1306 catalog/Save-sections/content-Save separation untouched (GET-only hydrate); AST-1323 header authoring unaffected; AST-1322 title-keyed PUT ingest untouched; AST-1305 list-ingest `bullet_list` extra default unchanged; required seven preserved (hydrate additive only); no React format allowlist added.

**Advisory:** plan's list-branch hydrate has API coverage only via the dict repro; an optional core unit test for an Abrams list on GET was not required for this bug's stated repro. **Advisory:** bible flags a possible follow-up on the AST-519 "orphan hide" page mock if client filtering diverges from hydrated GET — not a defect in this diff.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/core/candidate.py` | `hydrate_resume_structure_from_base_resume` (read-only, `free_prose` default) | `fd7b7849c` — +74 (with `api_candidate.py`) |
| ✓ | `src/ui/api/api_candidate.py` | GET calls hydrate before building response | `fd7b7849c` — +80/-1 total across both files |
| | _tests_ | GET resume_structure hydrates from base_resume | `1b2e38f38` / `e4709d3f2` |

### AST-1325 — Structure header row: name \| style \| Enabled \| Job Edit \| up/down
_Archived: 2026-08-19 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1325/structure-header-row-name-style-enabled-job-edit-updown-support · Status at archive: Archive · Project: Astral Artifacts · Assignee: ada · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1299_

#### Susan comment (verbatim)

[bug] Likewise 1323 was a partial fix, but I want the header row to lay out like this:

```
[SECTION NAME           ] [STYLE    V] Enabled:[X] Job Edit:[ ]  [up][down]
```

#### As-is

AST-1323 put structure controls on each `CollapsiblePanel` header with body text between panels, but the header still does not match the requested single-row shape. Today's `structure-authoring-header` uses checkbox-then-label (`[X] Enabled`, `[X] Job edit`), allows `flex-wrap` so controls break onto multiple lines, and does not size the name vs style fields like the mock. Optional **Remove** also sits in that same flex group.

#### To-be

Each section header is one horizontal row in this order and labeling: `[SECTION NAME           ] [STYLE    V] Enabled:[X] Job Edit:[ ]  [up][down]`. Section body text remains in the panel body between headers (AST-1323). Catalog-driven style `<select>`, required cannot disable/remove, Add section + Save sections unchanged.

#### Root cause

AST-1323 delivered "controls on the header" without locking the **visual contract** Susan specified: label-before-checkbox copy (`Enabled:` / `Job Edit:`), single-line flex (no wrap for the primary controls), and name/style field widths. Partial fix left markup/CSS that still reads as a wrapped control cluster.

#### Proposed change

UI-only in `ArtifactEditor` + `App.css`. No GET/PUT, slug, normalize, catalog, or config changes. Control order inside `.structure-authoring-header`: (1) section name input bound to title, id unchanged; (2) style select, options from `structureCatalog.body_formats` only, same locked rules as before for contact/`experience`; (3) Enabled — literal label text `Enabled:` then the checkbox (DOM order text-then-input so it reads `Enabled:[X]`), disabled when required; (4) Job Edit — literal label `Job Edit:` then the checkbox bound to `job_agent_editable`, same DOM order; (5) Up/Down, kept as the last primary pair; (6) Remove for non-required rows, placed after Up/Down (not between Job Edit and up/down) — outside Susan's ASCII mock but still required for optional extras. CSS: `.structure-authoring-header` becomes `flex-wrap: nowrap` with horizontal scroll preferred over wrapping the primary five controls onto a second line; `.structure-authoring-name` flex-grows as the wide slot; `.structure-authoring-style` gets a compact width; Enabled/Job-Edit labels stay nowrap.

⚠️ **Decision:** This bug is layout/label polish on the AST-1323 header — not another move of controls off/on the panel; body-between-headers stays. ⚠️ **Decision:** Literal label strings are `Enabled:` and `Job Edit:` (Susan's mock); format option values still come only from `catalog.body_formats`.

#### Blast radius

`ArtifactEditor.tsx` structure-authoring header markup + related CSS only. Component/page tests asserting the old header checkbox label text or order (AST-1323 bug-repro / AST-1306 migrated asserts) needed Betty updates. No API, builder, or structure persist changes.

#### Radia review — code-rubric.v1, PROCEED (bug-fix lane)

Product delta: `33c11a9e` — `ArtifactEditor.tsx` + `App.css` only. Full sweep: conforms on in-scope-only, ui-config-driven (catalog formats unchanged), frontend placement, import-direction, dry/no-hardcoded format arrays; not-applicable elsewhere; no violations. `[bug-repro]`: `AST-1325: header row is name | style | Enabled: | Job Edit: | up/down` asserts `.structure-authoring-name`/`.structure-authoring-style`, `Enabled:`/`Job Edit:` (not `Job edit`), and label order — would fail pre-fix. Betty also fixed the AST-1323/1306 test cases that still asserted the old `Job edit` copy. During `[qa-handoff]`, Ada also flagged a genuine test-file bug (not product): the page test suite failed to load with esbuild's "symbol `headers` already declared" — a duplicate `const headers` left over in the AST-1323 test case, plus stale `Job edit` assertions — Betty fixed both.

**Advisory:** bug-repro does not assert Up/Down button presence or `flex-wrap: nowrap` computed style — cosmetic gap only; markup/CSS do implement the mock.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `ArtifactEditor.tsx` / `App.css` | Header control order + literal `Enabled:`/`Job Edit:` labels; nowrap single-row CSS | `fc3f4456c` — +30/-7 |
| | _tests_ | header name\|style\|Enabled:\|Job Edit: layout + duplicate-`headers`/stale-copy test-file fix | `7f715a986`/`9c6100a40`, `3b4a7726a`/`c1c8ebd7d` |
