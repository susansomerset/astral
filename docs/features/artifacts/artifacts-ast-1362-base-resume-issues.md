# AST-1362 — Base Resume Issues
**Component:** artifacts  
**Children:** AST-1381, AST-1382  
**Linear archived:** AST-1362 2026-08-31; AST-1381 2026-08-31; AST-1382 2026-08-31

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-14 17:48 | AST-1381 | docs | `c739b6521` | docs(AST-1381): plan-fix — base resume craft/UI/print issues |
| 2026-08-14 17:54 | AST-1381 | code | `179f1003d` | code(AST-1381): accomplishments string[], \|→•, collapsible roles, structure Save |
| 2026-08-14 17:57 | AST-1382 | docs | `323ba711f` | docs(AST-1382): plan-fix — gap retarget fixtures + emit/print repro |
| 2026-08-14 18:01 | AST-1362/1382 | sync | `dc240b00f` | sync(publish-ref): origin/sub/AST-1362/AST-1382-gap-base-resume-tests |
| 2026-08-14 18:03 | AST-1382 | test | `4a6b90cdb` | test(AST-1382): bug-repro — string[] emit, pipe markers, format Save fixtures |
| 2026-08-14 18:03 | AST-1382 | merge-tests | `df202bf62` | merge-tests(AST-1382): origin/tests 4a6b90cdb5dfddc28dfe8dcca06bb995bca6545c |
| 2026-08-14 18:09 | AST-1362/1381 | sync | `d2aaad052` | sync(publish-ref): origin/sub/AST-1362/AST-1381-fix-base-resume-issues |
| 2026-08-14 18:09 | AST-1381 | test | `098621fd8` | test(AST-1381): flip AST-1007 markers assert to accomplishments string[] |
| 2026-08-14 18:10 | AST-1381 | merge-tests | `a57be15fc` | merge-tests(AST-1381): origin/tests 098621fd884ec98e839a8595520a037b9a2c6ab8 |
| 2026-08-14 18:14 | AST-1362/1381 | sync | `43fceb3fd` | sync(publish-ref): origin/sub/AST-1362/AST-1381-fix-base-resume-issues |
| 2026-08-14 18:15 | AST-1381 | test | `21136c84d` | test(AST-1381): strip orphan AST-1383 agent test/bible from publish tip |
| 2026-08-14 18:17 | AST-1381 | test | `05cf53c90` | test(AST-1381): fixtures + bug-repro for string[] emit, markers, format Save |
| 2026-08-14 18:17 | AST-1381 | resolve | `4f34e5548` | resolve(AST-1381): — findings addressed |
| 2026-08-14 18:17 | AST-1381 | docs | `977a7b6a9` | docs(AST-1381): Radia review — product clean; orphan tests stripped |
| 2026-08-14 18:17 | AST-1381 | docs | `a837726de` | docs(AST-1381): plan — accomplishments string[] + Base Resume Issues UI/print |
| 2026-08-14 18:17 | AST-1381 | code | `cf874c670` | code(AST-1381): base resume string[] / markers / collapsible / format Save |
| 2026-08-14 18:17 | AST-1381 | merge-tests | `f2b58a2bd` | merge-tests(AST-1381): origin/tests 05cf53c906025ab040a0bfef37e640e412149c62 |
| 2026-08-14 18:18 | AST-1362 | merge | `f49db1070` | Merge remote-tracking branch 'origin/ftr/AST-1362-base-resume-issues' into dev |
| 2026-08-14 18:18 | AST-1381/1382 | code | `0ce78b99e` | code(AST-1382): no product delta — gap is test/bible only (product on AST-1381) |
| 2026-08-14 18:18 | AST-1382 | test | `caba76571` | test(AST-1382): bug-repro — string[] emit, pipe markers, format Save fixtures |
| 2026-08-14 18:18 | AST-1382 | docs | `df3a0300a` | docs(AST-1382): Radia review — gap clean |
| 2026-08-14 18:18 | AST-1382 | merge-tests | `e7d05b165` | merge-tests(AST-1382): origin/tests caba765717f0e07b8c473c8f759d01eee50e262c |
| 2026-08-14 18:18 | AST-1382 | docs | `f6e674449` | docs(AST-1382): plan — gap retarget fixtures + emit/print repro |
| 2026-08-31 14:15 | AST-1381 | docs | `69282b59d` | docs(AST-1381): archive Linear issue content |
| 2026-08-31 14:15 | AST-1382 | docs | `bba1f74ce` | docs(AST-1382): archive Linear issue content |
| 2026-08-31 14:18 | AST-1362 | docs | `a7551469d` | docs(AST-1362): archive Linear issue content |

_AST-1381's own build had a genuine cross-ticket contamination episode: its publish ref picked up an orphaned `TestAst1380CraftRubricThinkingOffAndFailureBanner` test plus a `docs/test-bible/core/agent.md` AST-1380/1383 section with no matching product delta on the branch — caught by Radia's build review and stripped by Betty from `origin/ftr/AST-1362-base-resume-issues`, documented in full below. This family's own build narrative was **discovered embedded across two other families' host files** — the schema/prompt/agent-validate half of both AST-1381 and AST-1382 was appended to `docs/features/artifacts/ast-1349-experience-array-contract-schema-prompts-agent.md` (consumed by the AST-1345 archive), and the UI/emit/print half was appended to `docs/features/artifacts/ast-1351-experience-array-ui-render-print-parity.md` (also consumed by the AST-1345 archive). Both halves are reproduced together below, combined for the first time into one place._

## Epic — AST-1362
_Archived: 2026-08-31 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1362/base-resume-issues · Status at archive: Archive · Project: Astral Artifacts · Assignee: chuckles · Priority / estimate: Urgent / — · Blocked by / blocks / related: —_

### As-is

1. Craft for experience detail still teaches/returns bullet-list prose; the UI/render also bullets those lines, so operators see a double bullet before each accomplishment string.
2. Authoring `|` separators are not converted to `•` in Base Resume Contact header and Core Competencies (they stay as `|` or otherwise fail the resume-wide separator rule).
3. Experience roles on Base Resume Content are not collapsible; there is no collapsed header of the form `<company>, <title> / <from> - <to>`.
4. Changing Prior Experience structure format from `word_cloud` to `free_prose` and saving still prints as `word_cloud`.

### To-be

1. Craft requests an array of strings for experience detail/accomplishments; parse/persist that shape; render/print bullets each string once (no nested bullet markers).
2. Every `|` in resume content (including Contact header and Core Competencies) converts to `•` on emit/print.
3. Each experience role is a collapsible panel whose collapsed header shows `<company name>, <title> / <from> - <to>`.
4. Saving Prior Experience as `free_prose` makes print/HTML use the free-prose treatment, not `word_cloud`.

### Proposed steps

Chosen ancestor (Susan): **AST-1345** (Done) — Clarify `base_resume.experience` node. This bug stays its own mini-parent; bug-fix will related-link AST-1345, not re-parent under it.

1. Against AST-1345's job-array contract: widen accomplishments/detail from a single string to `string[]` in craft schema/prompts + parse, then stop double-bulleting in UI/render.
2. Extend resume emit so Contact header and Core Competencies apply `|`→`•` (AST-1345 did not own that separator rule).
3. On Base Resume Content, make each experience role collapsible with header `<company>, <title> / <from> - <to>` (beyond AST-1351's editor cards if still flat).
4. Trace Prior Experience `word_cloud`→`free_prose` Save → print (outside AST-1345's experience-array scope; still ship in this bug unless you split it).

### Original report

1. The craft prompt is requesting bullet lists, and the bullets are getting bulleted in the render (so it's two bullets before the text). the craft prompt should just request an array of strings for the experience detail, and the parser should parse it correctly.
2. | bars should ALWAYS convert to **•** characters for any resume content. This is not happening in the Contact header and Core Competencies.
3. Experience sections should be collapsible in the base resume content view, showing the `<company name>, <title> / <from> - <to>` in the collapsed header.
4. Changing a style for "Prior Experience" from word_cloud to free_prose (and saving it) still renders as word_cloud when I print.

#### Comments

##### chuckles — 2026-08-14T18:26:28.968Z (ancestor-selection thread)
Posted a ranked list of 9 ancestor candidates for this bug's related-link, with rationale for each: AST-1345 (strongest umbrella for craft array shape + experience UI/print); AST-1349 / AST-1351 (the two half-owners of items 1 and 3); AST-1299 family (AST-1303/1304/1306 — section `format` including Prior Experience `word_cloud`/`free_prose`, item 4); AST-993/AST-1019 (separator/`•` + experience layout golden work, item 2 related); AST-1148 (Cover from-block `|`→`•` — documented separator rule but the wrong surface, closest prior contract for item 2).

##### susan — 2026-08-14T21:24:22.410Z
1345, please.

##### chuckles — 2026-08-14T21:25:00.532Z
Locked ancestor: **AST-1345** (Done — Clarify `base_resume.experience` node). Description Proposed steps updated to that pick. Items 2 and 4 sit outside that epic's experience-array scope; they stay on this bug's as-is/to-be unless split. Move this ticket to Todo (assignee Chuckles) when the reading is good — that is the approve signal for bug-fix.

### Files changed (plan vs actual)

_No direct product commit trail on the parent — the epic worktree carries only sync/merge housekeeping and the `docs(AST-1362)` archive commit. Implementation landed entirely via the two sub-issues below._

## Sub-issues

### AST-1381 — Fix: Base Resume Issues (craft/UI/print)
_Archived: 2026-08-31 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1381/fix-base-resume-issues-craftuiprint · Status at archive: Archive · Project: Astral Artifacts · Assignee: katherine · Priority / estimate: None / 5 · Blocked by / blocks / related: parent: AST-1362_

#### What this fixes

Orphaned Bug AST-1362 (approved as-is/to-be). Ancestor context: AST-1345 (Done) experience-array epic — related-linked, not re-parented.

1. Craft/experience detail double-bullets → request `string[]` for accomplishments/detail; parse + render once.
2. `|` → `•` on Contact header and Core Competencies resume emit.
3. Collapsible experience roles on Base Resume Content with `<company>, <title> / <from> - <to>` collapsed header.
4. Prior Experience format Save `word_cloud`→`free_prose` must print as free_prose.

#### Make-fix checklist

- [X] Schema + prompts: `accomplishments` is `string[]` (config, craft/parse/draft/finalize prompts, AST-756 twin)
- [X] Candidate validate: job accomplishments must be list of strings; Style D lists elements
- [X] Emit: list (or legacy str coerce) → one `<li>` per item; strip residual bullet glyphs
- [X] Resume markers: authoring `|` → emit `•` (contact + competencies + all marker leaves)
- [X] ExperienceJobsEditor: collapsible roles with `{company}, {title} / {dates}` header; accomplishments textarea ↔ `string[]`
- [X] Content Save persists `resume_structure.sections` (formats) with base_resume when structure authoring is on

#### Notes for plan-fix

Parent Description has As-is/To-be/Proposed steps (authoritative for this bug). Seed feature docs from the AST-1345 family under `docs/features/artifacts/` (ast-1349, ast-1351, and related format docs as needed). Publish to `origin/sub/AST-1362/<this-child-segment>` only; parent ftr is AST-1362's own fresh branch off `origin/dev`.

#### As-is / root cause (schema/prompt/agent-validate half)

1. **Accomplishments type + emit:** contract left `accomplishments: str` (AST-1349 as-is); `_split_role_accomplishments` / `_emit_experience_jobs_html` treated every non-lead line as a bullet body and did not strip existing markers. UI textarea round-tripped a single string.
2. **`|`→`•` gap:** `_resume_site_markers` only rewrote `__`, `~~`, and ` • ` → NBSP-bullet; it never mapped authoring `|` → emit `•`. Cover from-block already did `|`→`•`; general resume markers did not. Craft even taught competencies as `" | "`-separated.
3. **Flat editor:** AST-1351 shipped always-visible role cards; collapsible chrome was out of that child's scope.
4. **Split persist paths:** `ArtifactEditor.doSave` PUT'd only `artifacts.base_resume`; format edits sat in `structureRows` until `onStructureSave` / `saveStructure` PUT'd `artifacts.resume_structure`. Print used `GET /candidate/resume/base` → `build_base_resume` → `resolve_resume_structure` from disk, so an unsaved (content-Save-only) format change never reached emit.

#### Repro

1. **Double bullets:** craft/parse with accomplishments string lines already containing `•`; Print base resume → `<li>• …</li>`.
2. **Pipes:** set `candidate_contact_detail` and/or `core_competencies` to `A | B | C`; Print → literal `|` remains.
3. **Collapsible:** Base Resume Content → Experience tab → roles always expanded as `Role N` cards.
4. **Prior format:** set Prior Experience format dropdown to `free_prose`, click the primary content **Save** (not Save sections), click **Print** → Prior Experience still emits as `p.competencies-list` (word_cloud); only clicking **Save sections** and printing again shows `free_prose` — proving the dual-save gap.

#### Proposed change — Part A: accomplishments type + emit (schema/agent half)

⚠️ **Decision:** `_EXPERIENCE_JOB_ITEM_SCHEMA["accomplishments"]` changes from `{"type": "str", "required": True}` to a required list-of-strings field (same list+items pattern used elsewhere in TASK_CONFIG). Keep the other four keys as required strings; no sixth job key; `prior_experience` unchanged. `craft_resume_base` `cache_prompt` `### experience` (and `simple_resume_parse` / job draft/finalize prompts) retarget from "one text block" to "ordered JSON array of strings — bare achievement text only, no leading `•`/`-`/`*`; `<no bullet>…` only when the source has a role-description lead." `src/core/candidate.py` experience validate/normalize now requires `accomplishments` to be a `list` whose elements are strings (after strip, drop empty); rejects string/dict/mixed; Style D found/recorded may list per-element accomplishments when `debug=True`.

⚠️ **Decision (migration for existing data):** existing stored base resumes with string `accomplishments` become unsupported until regenerate/re-edit — same class of gate as AST-1350's non-array `experience` — **unless** the emit/UI path prefers a one-time coerce on read (newline-split string → list) so Print does not break mid-migration, without writing the coerce back unless Save runs. (Resolved into the emit rule below: legacy `str` is still accepted on read via a defense-in-depth split.)

#### Proposed change — Part B: resume-wide `|`→`•`, collapsible roles, format Save→print (UI/emit half)

**B1 — Accomplishments emit + UI:** `_emit_experience_jobs_html` / `_split_role_accomplishments` in `src/core/builder.py` accept `accomplishments` as `list[str]` (primary). For each element: if it starts with `BUILD_CONFIG["experience_role_layout"]["lead_line_prefix"]`, emit as `p.role-description`; else strip one leading bullet glyph/`-`/`*` + whitespace if present, then emit as a single `<li>` — never double-wrap an element that is already only a marker. Defense in depth: a legacy `str` still present is newline-split once into the same pipeline (regenerate is not required to Print). `ExperienceJobsEditor` treats `accomplishments` as `string[]` on the job object (multiline textarea edits one-line-per-element; `onChange` writes a `string[]`, dropping empties); `ArtifactEditor.parseExperienceJobs` / Save payload persists `accomplishments` as a JSON array of strings, never `str()`.

**B2 — Resume-wide `|`→`•`:** extend `_resume_site_markers` so authoring `|` becomes the print bullet separator for all resume string leaves that already deep-walk through `_apply_resume_text_markers` (Contact header text, Core Competencies, technical skills lines, etc.) — matching the cover-from-block intent, preferring config constants over new literals. Naive-replace safety: split on ` | ` / bare `|` with the same empty-segment drop policy cover uses (or document the chosen rule before coding) so intentional `|` inside URLs is not corrupted. Craft prompts that still taught competencies/skills as `" | "` separators get an optional aligned tweak (twin file required if prompts change).

**B3 — Collapsible experience roles:** `ExperienceJobsEditor.tsx` wraps each role in the existing `CollapsiblePanel` component (same one ArtifactEditor already uses). Collapsed label: `{company}, {title} / {dates}` (trimmed, empty segments omitted gracefully) — `dates` already holds the freeform range; no new `from`/`to` schema fields. Move up/down/remove stay in the panel `actions` slot (`stopPropagation` so they don't toggle expand); default collapsed so long resumes scan by header.

**B4 — Prior Experience format Save → print:** when `structureAuthoring` is on, `doSave` (content Save) also PUTs `artifacts.resume_structure.sections` from the current `structureRows` (same payload shape as `saveStructure`), in one request or sequential awaits before the success toast — or equivalently calls `onStructureSave(structureRows)` as part of content Save when any structure row is dirty. The explicit **Save sections** control keeps working (idempotent). `build_base_resume` → `_emit_body_sections_html` already branched `free_prose` vs `word_cloud` from `spec.format`, so no emit change was needed once persistence was fixed — confirmed `prior_experience` retains its saved format through normalize.

#### Blast radius

Shared `_EXPERIENCE_JOB_ITEM_SCHEMA` identity across craft, parse, finalize, `resume_content` shape, ArtifactEditor/ExperienceJobsEditor persistence, job draft pin policy (may still tailor accomplishments only). All resume HTML builders that deep-walk markers (`build_base_resume`, `build_session_base_resume`, `build_resume_from_job`). Operators who author `|` in competencies/skills/contact; golden fixtures asserting literal `|` in HTML needed retargeting to `•`. Base Resume Content Save UX; any test assuming content Save never writes `resume_structure`. AST-1350's unsupported-shape gate still refuses non-array `experience` — legacy string **accomplishments** inside a valid job array should coerce or render without blocking the whole resume (resolved via the read-time coerce above, not a hard refuse).

#### What must still hold

`experience` remains an ordered job array (no prose-string success path, AST-1349). Job objects still have exactly the five keys; no new `highlights` on jobs. Finalize may tailor `accomplishments` only; pin `company`/`title`/`dates`/`location` from base. `prior_experience` stays `str`. AST-756 `expected-agent_task.json` remains a whole-file twin. Experience happy path remains job-array template editing (AST-1351), not a return to JSON textarea. Legacy non-array `experience` stays read-only + unsupported message; Print still refuses non-arrays (AST-1350). `_resume_site_markers` still applies `__`/`~~`/NBSP-bullet tightening. Prior Experience default format in config may stay `word_cloud`; operator override to `free_prose` must survive Save → Print. Cover from-block `|`→`•` behavior unchanged except insofar as shared helpers are reused deliberately.

#### Board review — Joan CANON: OK / Betty TESTS: REVISE

Joan: accomplishments `string[]`, `_resume_site_markers` `|`→`•`, collapsible experience chrome, and content-Save persisting `resume_structure` all stay inside existing canon (config SoT, seed JSON, UI-config-driven UI, import discipline) — no statute/pattern update required; legacy-accomplishments coerce-vs-refuse stays blast-radius scoped, not an ESCALATE case. Betty: flagged that `docs/test-bible/frontend/components.md` (+ core/builder.md, core/candidate.md) still asserted AST-1351/996 fixtures as `accomplishments:str` (would break), with no repro coverage yet for string[] single-bullet emit, contact/competencies `|`→`•`, or content-Save persisting the prior_experience format.

#### QA handoff exchange — incomplete fixture retargets caught before merge

Katherine flagged (2026-08-15T00:55): existing component fixtures still asserted pre-fix `accomplishments: str` while product tip was already `string[]` — both a Python validate/config assert pair and two frontend Vitest suites (`getByText("Role 1")` vs the new `{company}, {title} / {dates}` collapsed header) failed; not a product revert, fixtures were simply obsolete against the plan-fix to-be. Gap sibling AST-1382 was asked to own that retarget. A second, narrower miss surfaced later (2026-08-15T01:08): one single test (`TestAst1007NestedTypographyMarkers::test_apply_markers_deep_walks_job_array_and_list_leaves`) still compared markers-deep-walked list output against a bare string even though its own fixture already used a list — Betty fixed the one remaining assert.

#### Radia review — REVIEW → fix-now cleared, then CLEAN

**fix-now — orphan AST-1383 test/bible contamination.** The publish tip carried `TestAst1380CraftRubricThinkingOffAndFailureBanner` plus a `docs/test-bible/core/agent.md` AST-1380/1383 section (via a `test(AST-1383):` commit and its merge-tests ancestry) with **no matching AST-1380 craft-thinking product delta** versus `origin/ftr/AST-1362-base-resume-issues` — the only real `agent.py` tip↔ftr delta was an unrelated rename (`is_rubric_backed_task` → `is_vector_feedback_task`, synced in from `origin/dev`/AST-1378). **Recommendation:** restore the two alien paths (`tests/component/core/test_agent.py`, `docs/test-bible/core/agent.md`) from `origin/ftr/AST-1362-base-resume-issues` via `git checkout`, without touching AST-1381/AST-1382's own product or repros. **Discuss** — multi-ticket frame on the sub (AST-1382 content also present) — expected sibling ancestry, not a defect.

**Resolution:** Betty restored the two alien paths exactly as recommended (`git checkout origin/ftr/AST-1362-base-resume-issues -- tests/component/core/test_agent.py docs/test-bible/core/agent.md`). Product tip then reviewed CLEAN — orphan tests stripped, AST-1381/1382 product and repros untouched.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `data/admin/agent_task.json` + `docs/uat-fixtures/AST-756/expected-agent_task.json` | Craft/parse/draft/finalize `accomplishments` prompt retarget to `string[]`; fixture twin resync | `cf874c670` — part of the combined commit |
| ✓ | `src/core/candidate.py` | Validate/normalize require `accomplishments` as `list[str]` | `cf874c670` — +33/- |
| ✓ | `src/core/builder.py` | `_emit_experience_jobs_html`/`_split_role_accomplishments` single-bullet-per-element emit + legacy-str coerce; `_resume_site_markers` `\|`→`•` for contact/competencies/all leaves | `cf874c670` — +53/- |
| ✓ | `ExperienceJobsEditor.tsx` | `string[]` accomplishments field; collapsible `CollapsiblePanel` roles with `{company}, {title} / {dates}` header | `cf874c670` — +139/- |
| ✓ | `ArtifactEditor.tsx` | `parseExperienceJobs` widened for `string[]`; content Save bundles `resume_structure.sections` | `cf874c670` — +53/- |
| ✓ | `src/utils/config.py` | `_EXPERIENCE_JOB_ITEM_SCHEMA["accomplishments"]` → list-of-strings field | `cf874c670` — +4/- |
| ✓ | `App.css` | Collapsible role styles | `cf874c670` — +15/- |
| | _tests_ | orphan AST-1383 strip; AST-1007 markers assert flip; string[] emit/markers/format-Save fixtures | `21136c84d`, `098621fd8`, `05cf53c90`; bible per Betty manifest (AST-1383 section reverted) |

### AST-1382 — Gap: Base Resume Issues tests/bible (board-betty REVISE)
_Archived: 2026-08-31 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1382/gap-base-resume-issues-testsbible-board-betty-revise · Status at archive: Archive · Project: Astral Artifacts · Assignee: katherine · Priority / estimate: None / 3 · Blocked by / blocks / related: parent: AST-1362_

#### What this implements

Close the test/bible gap flagged by fix-board `[board-betty] TESTS: REVISE` on AST-1381: retarget `docs/test-bible/frontend/components.md` (+ core/builder.md, core/candidate.md) — AST-1351/996 fixtures asserting `accomplishments:str` (would break under `string[]`); add repro coverage for string[] single-bullet emit, contact/competencies `|`→`•`, and content-Save persisting `prior_experience` format/free_prose print.

#### Acceptance criteria

1. Bible + component fixtures no longer assume accomplishments is a single str where the product contract is string[].
2. At least one [bug-repro]-style coverage path for each of: string[]→single bullet emit, contact/competencies pipe markers, prior_experience format persist→print.
3. Publishes to `origin/sub/AST-1362/<this-child>` only.

#### Make-fix checklist

- [X] No additional product delta required — AST-1381 product already on this sub greens Betty's [bug-repro]
- [X] `TestAst1382BugReproBaseResumeIssues` (4) green
- [X] ArtifactEditor AST-1382 content-Save `resume_structure` bundling green
- [X] ExperienceJobsEditor / ArtifactEditor AST-1351|996 retargets green
- [X] `TestAst996ExperienceJobArrayConfig` + `TestAst1349ExperienceArrayContract` green
- [X] Did not edit `tests/` or `docs/test-bible/**` product beyond what Betty owns

#### Notes

Product fix lands on sibling AST-1381. This gap child owns test/bible only (or test+minimal product test harness), not a second product rewrite.

#### As-is / root cause (schema-fixture half)

Component fixtures and `docs/test-bible/core/candidate.md` / `utils` rows still treated job `accomplishments` as a required `str`. After AST-1381, `_EXPERIENCE_JOB_ITEM_SCHEMA["accomplishments"]` was `type: list`, draft validate rejected string accomplishments, and the shared `_SAMPLE_EXPERIENCE_JOBS` (str bodies) failed `TestAst1349ExperienceArrayContract` / config schema asserts. AST-1381's `[qa-handoff]` was blocked on this retarget. **Root cause:** the fix-board `[board-betty] TESTS: REVISE` on AST-1381 found product had widened accomplishments to `string[]`, but AST-996/AST-1349/AST-1351's fixture spine and bible still encoded the old str contract — the gap was filed as this sibling instead of running qa-fix directly on AST-1381.

#### As-is / root cause (UI-fixture half)

Builder fixtures still fed `"accomplishments": "<prose str>"` into `_emit_experience_jobs_html`/Style D/golden-layout tests, passing only because emit coerced legacy str — they did not prove `string[]` → one `<li>` without double bullets. No focused assert existed that `_resume_site_markers`/session-or-base emit converted authoring `|` to `•` on `candidate_contact_detail` and `core_competencies`. Frontend AST-1351/AST-996 tests expected flat "Role N" labels and string accomplishments in `ExperienceJobsEditor`/`ArtifactEditor`, failing on the new collapsible `{company}, {title} / {dates}` headers and `string[]` wire. No coverage existed that Base Resume Content content Save persisted `resume_structure.sections[].format` (e.g. `prior_experience: free_prose`) so Print used free_prose, not the default word_cloud. `docs/test-bible/frontend/components.md` (+ builder.md rows) still described str accomplishments / Role N chrome.

#### Proposed change — schema-fixture retarget

`tests/component/core/test_candidate.py`: change module `_SAMPLE_EXPERIENCE_JOBS` so each job's `accomplishments` is a `list[str]` (e.g. `["Shipped widgets"]`); fix the type alias; grep the file for other inline `"accomplishments": "<str>"` job literals and retarget the same way — five keys only, no new fields. `tests/component/utils/test_config.py`: in `TestAst996ExperienceJobArrayConfig` (and any twin looping `_JOB_KEYS` expecting every key `type: str`), assert `accomplishments` is `{"type": "list", "required": True}` while the other four keys remain `str`; update `TestAst997FinalizeExperienceJobArray`/stringify examples if they hardcode str accomplishments; leave `TestAst1351ExperienceJobUiFields` key order alone. `docs/test-bible/core/candidate.md` and `docs/test-bible/utils/config.md`: rewrite "accomplishments (string)"/"one text block" wording to ordered `string[]`, note draft validate rejects non-list accomplishments, retarget schema rows from `str` to `list`. No product `src/` change on this gap.

#### Proposed change — UI-fixture retarget + new repro coverage

**A — Retarget existing fixtures (no product edits):** `test_builder.py` — where experience jobs used string `accomplishments`, prefer `list[str]` (split lead/`<no bullet>` + bullets into array elements); update `TestAst1008ExperienceGoldenLayout`'s sample; keep one legacy-str-coerce case labeled explicitly legacy, not the happy path. `test_ExperienceJobsEditor.test.tsx`: fixtures use `accomplishments: ["Did stuff"]`; assert collapsed header text via the job's company/title/dates, not `Role N`; expect `onChange` payloads with `accomplishments` as `string[]`; Add-role empty job includes `accomplishments: []`. `test_ArtifactEditor.test.tsx`: same retarget for AST-1351/AST-996/AST-1375 experience fixtures; drop `Role 1` queries; Save-payload expectations use accomplishments arrays.

**B — New [bug-repro] coverage:** (1) `string[]` single-bullet emit — a job with `accomplishments: ["• Shipped X", "Did Y"]` emits `<li>Shipped X</li>` and `<li>Did Y</li>`, never `<li>• Shipped X</li>`. (2) Contact + competencies `|`→`•` — session or base emit with `candidate_contact_detail`/`core_competencies` text containing `A | B | C` shows bullet separators, no literal `|` in those nodes. (3) `prior_experience` format Save → print — a PUT bundling `artifacts.base_resume` together with `artifacts.resume_structure.sections.prior_experience.format = "free_prose"` (mirroring ArtifactEditor content-Save bundling), then `build_base_resume`/the HTML route emits prior as free_prose (`summary-intro`), not `competencies-list`.

**C — Bible:** `docs/test-bible/frontend/components.md` § AST-1351/AST-996 rewritten for the `string[]` contract and the collapsible header; `docs/test-bible/core/builder.md` gets an AST-1381/1382 row for string[] emit, `|`→`•` markers, and format-driven prior emit; cross-links to the candidate/config bible updates from the schema-fixture half above.

#### Blast radius

Shared `_SAMPLE_EXPERIENCE_JOBS` feeds many candidate tests beyond AST-1349 — retargeting it once should green a whole cluster; re-run `TestAst996ExperienceJobArray`, `TestAst1349ExperienceArrayContract`, and any class that deep-equals sample jobs. Broad builder experience fixtures (AST-998/1007/1008/1030/1350/1351 debug) needed careful retargeting while keeping AST-1350's non-array-refuse tests unchanged. Frontend ArtifactEditor suites beyond AST-1351 that mount experience tabs. AST-1381 stayed Code Complete until this gap's fixtures landed and Betty cleared the `[qa-handoff]`.

#### What must still hold

Experience remains an ordered job array (no prose-string success path, AST-1349). Exactly five job keys; `prior_experience` stays `str`. Finalize may tailor accomplishments only; pin company/title/dates/location. AST-756 twin discipline stays a product/prompt concern already on AST-1381; this gap does not re-open prompt edits unless a fixture asserts the old prompt prose. AST-1351 happy path remains ExperienceJobsEditor (not JSON textarea). AST-1350's unsupported non-array experience refuse + read-only notice unchanged. `_resume_site_markers` still applies `__`/`~~`/NBSP-bullet. Prior default format may stay `word_cloud` in config; operator `free_prose` override is what the repro proves. Cover from-block `|`→`•` stays cover's own path; resume markers reuse the same authoring/emit separators without changing cover tests' intent.

#### Board review — Joan CANON: OK / Betty TESTS: REVISE

Joan: test/bible-only gap — fixture retarget + bible rows for accomplishments string[], collapsible headers, `|`→`•`, format-Save→print; no `src/` edits, no canon statute/pattern update needed. Betty: flagged the same retarget scope (components.md + builder.md + candidate.md + config.md) and the three missing [bug-repro] coverage paths, which this ticket then delivered.

#### Radia review — REVIEW, gap clean; frame discuss

**Discuss (not fix-now):** the publish-ref frame also carried AST-1381's product (expected — sibling dependency) plus an unrelated AST-1383 test commit riding along — merge attribution hygiene only, not a defect on this gap ticket's own deliverable. Gap deliverable (tests + bible) itself confirmed complete.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| | _product_ | none — gap is test/bible only | `0ce78b99e` — explicit no-product-delta commit |
| | _tests_ | string[] emit, pipe markers, format-Save bug-repro fixtures; bible retargets | `4a6b90cdb`/`caba76571`; bible `docs/test-bible/frontend/components.md`, `core/builder.md`, `core/candidate.md`, `utils/config.md` per manifest |
