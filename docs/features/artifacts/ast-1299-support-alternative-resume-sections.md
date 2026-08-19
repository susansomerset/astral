# AST-1299 — Support alternative resume sections

<!-- linear-archive: AST-1299 archived 2026-08-19 -->

## Linear archive (AST-1299)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1299/support-alternative-resume-sections  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1201; related: AST-1205

### Description

## Purpose

Candidates do not all share the Somerset ten-section catalog. Abrams-style resumes need extra titled blocks (Highlights, Publications, and whatever else the person actually has) while still printing with the Somerset treatments we already ship. Today unknown section ids are rejected and extra legacy labels are dropped, so those resumes cannot be stored or rendered. This epic makes section title + format a first-class property of the candidate’s structure, keeps seven sections required, and lets the builder emit any additional section by choosing one existing format.

## Functional scope

* **Required sections stay seven.** Every valid structure includes Candidate Name, Candidate Title, Candidate Tagline, Candidate Contact Detail, Summary (or Professional Summary), Core Competencies, and Experience. Those seven keep today’s stable ids. “Summary” vs “Professional Summary” is a display title on the same summary section — not a second id.
* **Additional sections are allowed.** A candidate may add any number of extra sections (Highlights, Publications, Prior Experience, Education, Technical Skills, or new titles). Each extra section has a stable id, a display title the operator or craft hop can set, enabled/order flags, and exactly one format from the closed format list.
* **Format is a section property, not an id.** The builder chooses a visual treatment from the section’s format, not from the section’s name. The closed formats and their Somerset treatments:
  * `free_prose` — Summary-style paragraphs
  * `bullet_list` — a standalone section of lines as bullets (Highlights uses this; any other extra section may pick it)
  * `word_cloud` — Core Competencies pipe line
  * `dual_column` — Technical Skills category grid
  * `indented_bold_single` — Education bold-lead rows
  * `experience_detail` — Experience role articles from today’s job-array fields (title, company, dates, location, accomplishments)
* **Required sections have implied formats.** Header fields keep the existing header emit (they are not one of the six body formats). Summary defaults to `free_prose`. Core Competencies defaults to `word_cloud`. Experience is required as `experience_detail` (an array). Publications is a `bullet_list` section, not `experience_detail`. Today’s optional catalog slugs, when present, keep their historical treatments: Prior Experience → `word_cloud`, Education → `indented_bold_single`, Technical Skills → `dual_column`.
* **Emphasis in body text.** Section bodies honor a small closed set of html-style italic and bold tags so Publications (and other body formats) can emphasize titles and names. This is not a free HTML surface — only italic and bold.
* **Content and hops follow the structure.** Base resume and job resume bodies may include extra section keys. Job artifacts remain a subset of the candidate’s enabled structure ids — they must not invent sections the structure does not define. Craft-base and draft-job hops accept those extra keys; they must not reject a key solely because it is outside the old ten-id list. Draft whitelist stays “this candidate’s current base resume keys,” now including extras. Experience content is an `experience_detail` array; leftover prose Experience is regenerated, not kept as a valid shape.
* **Operators can author extras.** Title, format, enabled, and order are editable for optional sections. Required sections cannot be removed. New extras default to job-agent-editable unless the operator turns that off.
* **Legacy label/content arrays keep extra titles.** A pasted Abrams-style list whose labels are not in the old catalog becomes extra structure sections (id slugged from the title) instead of being silently dropped.
* **Debug (backend** `debug=True` **only).** On builder (and any touched normalize/validate `debug=` path): Style D index headers with universal `index N/M`, section id, title, format, and emit outcome; working detail under `|`; long HTML truncated per the AST-538 contract (first 15 / omitted / last 15).

## Architectural definition

* **Patterns to reuse** — `pattern.config.config-block`: required section ids, the closed format list, default format-per-required-section, and the allowed emphasis-tag set live in config; callers do not invent inline sets. `pattern.layers.import-discipline`: structure/normalize in core, emit in the builder, UI remains a thin consumer. `pattern.ui.admin-endpoint`: format catalog and structure edits are resolved in the API from config; React does not own the allowed-format list.
* **New patterns proposed** — none. Format dispatch is a config extension of the existing structure + builder, not a new catalog method package.
* **Applicable statutes** — `astral.config.config-source-of-truth` (format list, required ids, emphasis-tag set); `astral.standards.no-hardcoded-sets` (no leftover known-id reject lists in core/builder); `astral.standards.in-scope-only`; `astral.standards.debug-contract-gated`; `astral.standards.dry-and-focused-functions` (reuse existing Somerset emit; do not fork a second visual language); `astral.layers.import-direction`; `astral.layers.ui-config-driven-business-logic`; `astral.agent.do-task-delegation` on hops that persist structure or section bodies.

## Boundaries

* Does **not** invent new visual styles, accent/style settings, or typography knobs beyond the closed italic/bold emphasis set.
* Does **not** own [AST-1201](https://linear.app/astralcareermatch/issue/AST-1201/we-need-a-daisy-chain-to-generate-the-base-resume-content) (base-resume daisy chain that will later generate Highlights / special sections). This epic is the contract that chain must honor.
* Does **not** own [AST-1205](https://linear.app/astralcareermatch/issue/AST-1205/approve-artifacts-task) (approve artifacts) or [AST-1268](https://linear.app/astralcareermatch/issue/AST-1268/draft-job-resume-response-schema-is-wrong) (nested draft envelope / deviations). [AST-1268](https://linear.app/astralcareermatch/issue/AST-1268/draft-job-resume-response-schema-is-wrong) is User Testing; this epic only extends the section-key whitelist so extras are not treated as unknown.
* Does **not** change cover-letter shape or emit.
* Does **not** strip Prior Experience / Education / Technical Skills from candidates who already have them — those remain valid optional sections.
* Does **not** require a global closed catalog of extra section ids. Extras are per-candidate. The format list is closed; the extra-id list is not.
* Does **not** keep a prose-Experience render fallback. Regenerate to an `experience_detail` array.
* Does **not** treat Publications as `experience_detail`. Publications is `bullet_list`.
* Job hops still must not add section keys the structure does not enable.

## Acceptance criteria

 1. A candidate whose structure is only the seven required sections renders a complete resume; absent optional sections do not fail the builder.
 2. Adding Highlights as `bullet_list` and Publications as `bullet_list` (titles + bodies) prints those headings and bulleted lines in structure order.
 3. Changing a required section’s title (e.g. Professional Summary → Summary) changes the printed heading and does not change the section id.
 4. Changing an optional section’s format changes the HTML treatment without creating a new section id.
 5. Craft-base and draft-job hops accept extra keys that exist on that candidate’s base resume / structure; they do not fail with “unknown section” merely because the key is outside the old ten-id list.
 6. A job resume cannot introduce a section the candidate structure does not enable.
 7. Required sections cannot be removed from structure.
 8. An Abrams-style label/content array that includes Highlights and Publications does not drop those labels on ingest or token serialize.
 9. Html-style italic and bold tags in a `bullet_list` body (and other body formats) render as italic and bold; other tags are not a raw HTML hole.
10. A leftover prose Experience string is not rendered as the required Experience section; Experience counts only as an `experience_detail` array (regenerate).
11. With `debug=True` on the builder, each enabled section logs id, title, format, and whether it emitted, under Style D headers and `|` detail.

## Dependencies and blockers

none. Adjacent, not blocking: [AST-1268](https://linear.app/astralcareermatch/issue/AST-1268/draft-job-resume-response-schema-is-wrong) (User Testing — nested draft envelope); [AST-1201](https://linear.app/astralcareermatch/issue/AST-1201/we-need-a-daisy-chain-to-generate-the-base-resume-content) (Discussion — daisy chain that will generate extra-section content later).

## Open questions

none.

## Proposed child tickets

#### 1!: **Section format catalog and open extra ids - Ada**

Owns the config contract: required seven ids, closed format list (including `bullet_list` and `experience_detail`), default formats for required/historical optional slugs, allowed italic/bold emphasis tags, and structure normalize that accepts extra titled sections instead of rejecting unknown ids. Observable: a structure with Highlights + Publications as `bullet_list` persists; required sections still cannot be omitted. Does not own HTML emit, hops, or the editor UI.
**Citations:** `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`.

#### 2: **Builder emit by section format - Hedy**

After #1: render enabled sections in structure order by format, reusing the existing Somerset treatments; Highlights and Publications print as `bullet_list`; `experience_detail` uses today’s job-array fields; html-style italic/bold in body text render; leftover prose Experience is not treated as the required Experience section. When `debug=True`, log id / title / format / emit outcome per section (Style D). Does not own hop schemas or the structure editor.
**Citations:** `pattern.config.config-block`; `astral.standards.dry-and-focused-functions`; `astral.standards.debug-contract-gated`.

#### 3: **Hops, content blobs, and legacy extra labels - Katherine**

After #1: craft-base and draft-job accept extra section keys; draft whitelist is the candidate’s current base resume keys (including extras), not the old ten-id intersection. Legacy label/content arrays keep unmatched titles as extra sections. Experience persists as an `experience_detail` array (regenerate prose). Does not own HTML chrome or [AST-1201](https://linear.app/astralcareermatch/issue/AST-1201/we-need-a-daisy-chain-to-generate-the-base-resume-content) generation order.
**Citations:** `pattern.config.config-block`; `astral.standards.no-hardcoded-sets`; `astral.agent.do-task-delegation`.

#### 4: **Author extra sections (title and format) - Ada**

After #1: operators can add, title, format, enable, and reorder optional sections; required seven cannot be removed. Format choices come from the config catalog via the API (not a hardcoded React list). Does not own print CSS or hop prompts.
**Citations:** `pattern.ui.admin-endpoint`; `astral.layers.ui-config-driven-business-logic`.

---

## Original brief

Accommodate resume sections.  Allow the section title to be made, and a formatting option to use one of the existing ways we format the somerset resume.

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

[candidate-abrams.json](https://uploads.linear.app/6d08b154-c90f-497b-8dae-9a0bb7b7b5cd/34975bd0-aab8-4bec-990f-f0405965b76d/efce7002-da13-44c7-83a4-6c7bfef6d5fa)

## Git (authoritative — ignore Linear `gitBranchName`)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Ticket | `origin/…` |
| -- | -- |
| [AST-1299](https://linear.app/astralcareermatch/issue/AST-1299/support-alternative-resume-sections) (parent) | ftr/AST-1299-support-alternative-resume-sections |
| [AST-1303](https://linear.app/astralcareermatch/issue/AST-1303/section-format-catalog-and-open-extra-ids-support-alternative-resume) | sub/AST-1299/AST-1303-section-format-catalog-and-open-extra-ids |
| [AST-1304](https://linear.app/astralcareermatch/issue/AST-1304/builder-emit-by-section-format-support-alternative-resume-sections) | sub/AST-1299/AST-1304-builder-emit-by-section-format |
| [AST-1305](https://linear.app/astralcareermatch/issue/AST-1305/hops-content-blobs-and-legacy-extra-labels-support-alternative-resume) | sub/AST-1299/AST-1305-hops-content-blobs-and-legacy-extra-labels |
| [AST-1306](https://linear.app/astralcareermatch/issue/AST-1306/author-extra-sections-title-and-format-support-alternative-resume) | sub/AST-1299/AST-1306-author-extra-sections-title-and-format |

**Epic worktree:** `astral-AST-1299/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/384aa3b51a34365db9e143e387122623/8fb511d9-bf1b-4e2e-b03f-01b193daf8f2/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/384aa3b51a34365db9e143e387122623/93227902-6efa-4640-84d5-7b156608583c/store.db` |
| Katherine | engineer | `/home/susan/.cursor/chats/384aa3b51a34365db9e143e387122623/4cd9e6f8-62fc-4982-ba3f-5b3152183635/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/ea953b54-e724-42dc-bc5e-9a1196a20699/store.db` |
| Radia | review | `/home/susan/.cursor/chats/384aa3b51a34365db9e143e387122623/fb4d5589-a26f-48a0-a42e-f908de8ebe28/store.db` |

### Comments

#### chuckles — 2026-08-12T01:55:20.459Z
[merge-child] blocked: AST-1324 and AST-1325 sub not rollup-safe (Merge remote-tracking / pull merges).

@Ada Lovelace — rebuild clean linear tips on origin/ftr/AST-1299-support-alternative-resume-sections; force-with-lease OK; no origin/dev pull merges.

#### susan — 2026-08-12T01:04:10.803Z
\[bug\] Likewise 1323 was a partial fix, but I want the header row to lay out like this:

```
[SECTION NAME           ] [STYLE    V] Enabled:[X] Job Edit:[ ]  [up][down]
```

#### susan — 2026-08-12T00:45:26.237Z
\[bug\] Sorry, Chuckles, I think I wasn't clear enough about this.  It's not the SAVE that is the issue.  It's the RENDER of the existing base_resume artifact.  The base_resume_content page should render FREELY based on the information in the base_resume artifact, setting the style to "prose" by default if it's missing.  I'm asking you to LOAD from what is already in candidate_data, which I artificially applied and correctly has all the sections I want.  Does that clear things up?

#### chuckles — 2026-08-12T00:17:44.764Z
[refresh-ftr] blocked: docs/test-bible/frontend/pages.md

@Betty White — merge origin/dev into origin/ftr/AST-1299-support-alternative-resume-sections; resolve bible conflict; push ftr.

#### susan — 2026-08-11T20:48:34.450Z
\[bug\] Put the section labels, type select, enabled, job-edit (instead of job agent editable) and the up/down buttons on a single collapsible header row with the text for that section appearing between the headers (instead of the bottom of the page).

#### susan — 2026-08-11T20:46:28.633Z
\[bug\] This did not parse the actual content of the candidate_data.artifacts.base_resume content.  The example provided included a section called Highlights, but when I saved the object to the candidate_data, it gave me the original set of content, not Highlights.

#### chuckles — 2026-08-11T07:08:33.679Z
[merge-child] blocked: AST-1304 sub not rollup-safe.

@Hedy Lamarr — duplicate merge-tests + Merge remote-tracking (including sibling subs) on AST-1304 publish ref.
@Betty White — one merge-tests after the sub log is linear.

— Chuckles

#### chuckles — 2026-08-11T03:20:58.917Z
@susan

1. Confirm the format → existing Somerset emit mapping in the Description (Functional scope). In particular: is `bullet_list` a standalone section of lines as bullets, and should Abrams Highlights use that vs `free_prose`?
2. `experience_detail` persisted shape — keep today’s job-array fields (title, company, dates, location, accomplishments) so Experience does not migrate twice, or switch Experience and Publications to the flatter header / sub-header / bullets object named in the brief?
3. Live candidates whose Experience is still a prose string, not an array: keep a temporary `free_prose` render fallback, or regenerate-only?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
