# AST-1326 — Make "Highlights" a REQUIRED resume section
**Component:** artifacts  
**Children:** AST-1332, AST-1333  
**Linear archived:** AST-1326 2026-08-19; AST-1332 2026-08-19; AST-1333 2026-08-19

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-12 06:30 | AST-1332 | docs | `17530d63a` | docs(AST-1332): plan — required Highlights catalog and default order |
| 2026-08-12 06:33 | AST-1332 | docs | `ed45e1152` | docs(AST-1332): Joan validate — plan APPROVED |
| 2026-08-12 06:34 | AST-1332 | code | `111161d73` | code(AST-1332): required Highlights in catalog and default order |
| 2026-08-12 06:35 | AST-1332 | code | `1bf6c7c9f` | code(AST-1332): coerce Highlights order above Experience |
| 2026-08-12 06:35 | AST-1332 | code | `31c06b674` | code(AST-1332): append review stub |
| 2026-08-12 06:36 | AST-1332 | code | `baa485fa6` | code(AST-1332): review stub tip SHA |
| 2026-08-12 06:39 | AST-1326/1332 | sync | `d63d0338f` | sync(publish-ref): origin/sub/AST-1326/AST-1332-required-highlights-catalog-and-default-order |
| 2026-08-12 06:40 | AST-1332 | test | `1883ec76b` / `64c65a027` | test(AST-1332): required Highlights catalog + order coerce coverage |
| 2026-08-12 06:41 | AST-1332 | merge-tests | `5a74865a2` | merge-tests(AST-1332): origin/tests 1883ec76b88cba70f76d7522dfc8598d6b3b5772 |
| 2026-08-12 06:42 | AST-1326/1332 | sync | `b3f672316` | sync(publish-ref): origin/sub/AST-1326/AST-1332-required-highlights-catalog-and-default-order |
| 2026-08-12 06:46 | AST-1332 | docs | `ddfe24b32` | docs(AST-1332): Radia review — FIX-NOW AST-1334 regression |
| 2026-08-12 06:47 | AST-1332 | resolve | `da55f5e98` | resolve(AST-1332): — restore AST-1334 UI from origin/dev |
| 2026-08-12 06:50 | AST-1332 | test | `6649ab66f` / `b23af46b5` | test(AST-1332): restore AST-1334 Modal/JAR test-tree from origin/dev |
| 2026-08-12 06:50 | AST-1332 | test | `0297c0d3d` | test(AST-1332): note [qa-handoff] AST-1334 test-tree restore |
| 2026-08-12 06:52 | AST-1332 | resolve | `653a0b9ab` | resolve(AST-1332): — clean |
| 2026-08-12 06:57 | AST-1333 | docs | `d11875f79` | docs(AST-1333): plan — craft/parse schema and agent_task prompts |
| 2026-08-12 06:59 | AST-1333 | docs | `8477360a4` | docs(AST-1333): Joan validate — checklist empty highlights clash |
| 2026-08-12 07:00 | AST-1333 | docs | `df4946127` | docs(AST-1333): plan — reconcile QUALITY CHECKLIST with empty highlights |
| 2026-08-12 07:01 | AST-1333 | docs | `66f0508e3` | docs(AST-1333): Joan validate — APPROVED |
| 2026-08-12 07:03 | AST-1333 | code | `26806660a` | code(AST-1333): require Highlights in craft/parse agent_task prompts |
| 2026-08-12 07:03 | AST-1333 | code | `5ae3463ff` | code(AST-1333): require highlights in craft/parse response schema |
| 2026-08-12 07:04 | AST-1326/1333 | sync | `3b73fc89f` | sync(publish-ref): origin/sub/AST-1326/AST-1333-craft-parse-schema-and-agent-task-prompts |
| 2026-08-12 07:04 | AST-1326 | sync | `e1ae361df` | sync(ftr): origin/ftr/AST-1326-make-highlights-a-required-resume-section |
| 2026-08-12 07:04 | AST-1333 | docs | `e2a29d8e2` | docs(AST-1333): review stub after craft/parse highlights build |
| 2026-08-12 07:07 | AST-1333 | test | `6d2d68748` / `b9e14e293` / `c19fc42dc` | test(AST-1333): craft/parse required Highlights schema + prompts |
| 2026-08-12 07:07 | AST-1333 | merge-tests | (see test row) | merge-tests(AST-1333): origin/tests b9e14e29350f731b81a41063ff8df909b939e152 |
| 2026-08-12 07:12 | AST-1333 | docs | `486162320` | docs(AST-1333): Radia review — craft parse highlights schema |
| 2026-08-12 07:13 | AST-1333 | resolve | `7ecad23c1` | resolve(AST-1333): — clean |
| 2026-08-12 12:12 | AST-1326 | docs | `4960cdb24` | docs(AST-1326): mirror epic registry Threads |
| 2026-08-19 12:52 | AST-1332 | docs | `d45fb7532` | docs(AST-1332): archive Linear issue content |
| 2026-08-19 12:52 | AST-1333 | docs | `835ec1cbe` | docs(AST-1333): archive Linear issue content |
| 2026-08-19 12:54 | AST-1326 | docs | `611cb0969` | docs(AST-1326): archive Linear issue content |

_AST-1332 had a genuine cross-sibling merge regression, documented in full under its own Review/Resolution below: a `sync(publish-ref)` merge took the wrong side of a conflict and silently reverted AST-1334 (a shipped, unrelated `origin/dev` ticket's Modal footer work) — caught by Radia's build review, not self-detected. AST-1333 went through one real Joan plan-discuss round (a genuine prompt/schema contradiction — QUALITY CHECKLIST said "every key non-empty" while the new Highlights field is allowed to be empty), also detailed below. A `[thread-missing]` Cursor-chat recovery note on the parent (2026-08-12T02:49) is process narration, omitted from this archive._

## Epic — AST-1326
_Archived: 2026-08-19 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1326/make-highlights-a-required-resume-section · Status at archive: Archive · Project: Astral Artifacts · Assignee: chuckles · Priority / estimate: Urgent / 5 · Blocked by / blocks / related: —_

### Purpose

Abrams-style resumes treat Highlights as a first-class body section that must always exist and must sit above Experience—not as an optional extra operators may forget. After AST-1299, Highlights can be authored and emitted, but it is still optional in the required catalog, hop schema, and agent prompts, so craft/parse and base_resume_content can omit or bury it. This epic makes Highlights a required section with stable product order and aligns the craft/parse contracts so models and operators share that rule.

### Functional scope

* **Highlights is required.** Every valid resume structure includes the section id `highlights` (display title Highlights). It cannot be omitted or disabled. Candidates that lack it get it minted the same way other required sections appear in the default catalog.
* **Order above Experience.** On `/artifacts/base_resume_content` (and any structure UI that follows section order), Highlights sits immediately above Experience. The default catalog order encodes that placement; stored structures that already have Highlights are coerced so Highlights remains immediately above Experience.
* **Default format stays the Abrams treatment.** Required Highlights defaults to `bullet_list` (no new visual format). Operators may still change format within the closed format list where structure editing allows it for body sections.
* **Craft/parse response schema requires Highlights.** The shared craft-base / simple-resume-parse response schema includes `highlights` as a required string field (empty string allowed when the source has no highlight material).
* **Agent task prompts require Highlights above Experience.** `craft_resume_base` and `simple_resume_parse` agent_task prompt content instruct that Highlights is required and ordered immediately above Experience, and stay consistent with the schema (including segment count / field inventory language).

### Architectural definition

* **Patterns to reuse** — `pattern.config.config-block` (required ids, default order/format for Highlights, and schema field membership live in config); `pattern.layers.import-discipline` (catalog/normalize in utils+core; prompts/schema in config + agent_task seed; UI remains a thin consumer); `pattern.ui.admin-endpoint` (structure and catalog resolve from API/config; React does not invent required-id or format lists).
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.standards.in-scope-only`; `astral.layers.import-direction`; `astral.layers.ui-config-driven-business-logic`; `astral.agent.do-task-delegation`; `astral.seed.agent-tables-in-repo-json` / `astral.seed.archie-catalog-wins`.

### Boundaries

* Does **not** invent a new body format or typography treatment for Highlights — reuses `bullet_list` (and the closed format list).
* Does **not** reopen AST-1299's open-extra model for arbitrary titles; only elevates `highlights` into the required set.
* Does **not** own AST-1201 (base-resume daisy chain) or AST-1205 (approve artifacts).
* Does **not** change draft_job_resume nested envelope / deviations work (AST-1268 family); job drafts still follow the candidate's enabled base keys once Highlights is on the base.
* Does **not** strip historical optional sections (`prior_experience`, `education_certifications`, `technical_skills`) from candidates who have them.

### Acceptance criteria

1. A structure missing `highlights` fails normalize the same way a missing required section does today; `enabled=false` on Highlights is rejected.
2. Default / newly minted structures place Highlights immediately above Experience by `order` on base_resume_content.
3. A candidate who already had Highlights below Experience shows Highlights immediately above Experience after resolve/normalize (without the operator manually reordering).
4. Craft-base and simple-resume-parse response schemas require a `highlights` string; responses omitting the key fail schema validation.
5. `craft_resume_base` and `simple_resume_parse` agent_task prompts state that Highlights is required and sits above Experience, consistent with the schema field inventory / segment instructions.
6. HTML emit for Highlights continues via the existing `bullet_list` (or chosen closed format) path — no new visual language.

### Dependencies and blockers

none (AST-1299 alternative-sections catalog is Done).

### Open questions

none

### Proposed child tickets

**1!: Required Highlights catalog and default order — Ada** — Elevate `highlights` into the required resume-structure catalog and default structure: present + enabled, default format `bullet_list`, order immediately above Experience; normalize/resolve mint and coerce order accordingly. Drives base_resume_content ordering. Does **not** own hop schema or agent_task prompt text (sibling #2).
**Citations:** `pattern.config.config-block`, `pattern.layers.import-discipline`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`
**Estimate:** 3

**2: Craft/parse schema and agent_task prompts — Katherine** — Add required `highlights` to the shared craft-base / simple-resume-parse response schema; update those agent_task prompts so Highlights is required and ordered above Experience (segment inventory / instructions stay consistent with the schema). Does **not** own structure-catalog membership or UI order (sibling #1).
**Citations:** `pattern.config.config-block`, `astral.agent.do-task-delegation`, `astral.seed.agent-tables-in-repo-json`, `astral.seed.archie-catalog-wins`
**Estimate:** 3

### Original brief

Please move Highlights above Experience in the base_resume_content screen.

Also confirm that Highlights are included in the response schema and agent_task prompt content to reflect this requirement.

#### Comments

##### chuckles — 2026-08-12T13:46:40.129Z
AST-1332 REVIEW — Radia: AST-1334 Modal/JAR regression on publish ref; Ada resolving merge with origin/dev.

##### chuckles — 2026-08-12T13:59:08.331Z
AST-1333 REVIEW — Joan needs plan discuss on QUALITY CHECKLIST vs empty highlights.

### Files changed (plan vs actual)

_No direct product commit trail on the parent — the epic worktree only carries `sync(publish-ref)` / `sync(ftr)` housekeeping commits and the epic-registry Threads mirror / `docs(AST-1326)` archive commits. Implementation landed entirely via the two sub-issues below._

## Sub-issues

### AST-1332 — Required Highlights catalog and default order
_Archived: 2026-08-19 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1332/required-highlights-catalog-and-default-order-make-highlights-a · Status at archive: Archive · Project: Astral Artifacts · Assignee: ada · Priority / estimate: None / 3 · Blocked by / blocks / related: parent: AST-1326; blocks: AST-1333_

#### What this implements

Elevate `highlights` into the required resume-structure catalog and default structure: present + enabled, default format `bullet_list`, order immediately above Experience; normalize/resolve mint and coerce order accordingly. Does **not** own hop schema or agent_task prompt text (sibling #2).

#### Acceptance criteria

1. [x] A structure missing `highlights` fails normalize the same way a missing required section does today; `enabled=false` on Highlights is rejected.
2. [x] Default / newly minted structures place Highlights immediately above Experience by `order` on base_resume_content.
3. [x] A candidate who already had Highlights below Experience shows Highlights immediately above Experience after resolve/normalize (without the operator manually reordering).
4. [x] HTML emit for Highlights continues via the existing `bullet_list` (or chosen closed format) path — no new visual language.

#### Boundaries

Does not own hop schema or agent_task prompt text (sibling Craft/parse schema). Does not invent a new body format. Does not strip historical optional sections.

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `highlights` to `RESUME_STRUCTURE_REQUIRED_SECTION_IDS` (before `experience`); add `"highlights": "bullet_list"` to `RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID`; insert `highlights` into `RESUME_STRUCTURE_DEFAULT["sections"]` with title Highlights, enabled True, format from the map, order immediately above Experience; renumber Experience and following default orders | utils |
| `src/core/candidate.py` | After per-section validation in `normalize_resume_structure`, coerce section `order` values so when both `highlights` and `experience` are present, `highlights` sits immediately above `experience` in order-sorted section lists | core |

#### Stage 1 & 2 — Config catalog + order coercion

Exact new default orders: `candidate_name` 0, `candidate_title` 1, `candidate_tagline` 2, `candidate_contact_detail` 3, `professional_summary` 4, `core_competencies` 5, `highlights` 6, `experience` 7, `prior_experience` 8, `education_certifications` 9, `technical_skills` 10. Normalize coercion algorithm (literal): sort current sections by `(order, id)`, remove `highlights` from that sorted id list, reinsert it at the index of `experience`, then rewrite contiguous `order` ints `0..n-1` over the new sequence — applied on every successful normalize (save and resolve-when-valid), so AC3 holds without an operator reorder.

⚠️ **Decision:** `highlights` joins **required**, not historical-optional — same path as `experience` for required + disable rules. KNOWN grows from ten to eleven ids; hop/schema field inventory remains AST-1333. ⚠️ **Decision:** Default format is `bullet_list` only; operators may still pick another closed body format on save where the structure editor allows it — this ticket does not lock format the way `experience` locks `experience_detail`. ⚠️ **Decision:** Do not patch the legacy `DATA_SHAPES` `base_resume_structure` tab list — persistence authority is `artifacts.resume_structure`. ⚠️ **Decision:** Reassign all section orders to `0..n-1` after moving Highlights — tie-breaking and gaps from operator edits are normalized away; adjacency is the product rule, not preserving sparse order ints.

#### Plan review — Joan (plan-rubric.v1, APPROVED)

**acceptable** — no explicit Self-assessment scope/conf/risk line in the plan (only an Estimate confirm); optional hygiene, not blocking given explicit Decision blocks and a two-file footprint. In-session sweep: 56 statutes considered (18 universal + 38 scoped), 8 excluded on path; all cited statutes/patterns conform; zero plan-discuss rounds.

#### QA test manifest — Betty

Existing (revised): `TestAst1303ResumeStructureCatalog` — required eight + `highlights: bullet_list`; extras use `publications` instead. Broken/revised: `TestAst1306ResumeStructureSavePrep` pending-slug → Publications; `TestAst1324HydrateResumeStructureFromBaseResumeGet` hydrates `publications` (not required `highlights`). Gaps (new): `TestAst1332RequiredHighlightsCatalog`, `TestAst1332RequiredHighlightsNormalize` (omit/disable + order coerce).

#### Radia review — code-rubric.v1, FIX-NOW → resolved

**fix-now — AST-1334 regression smuggled into publish ref.** The three-dot diff vs `origin/dev` reverted AST-1334 (already shipped on dev, a different parent — AST-1329's Recommended Job Report modal-footer work), even though the AST-1332 plan explicitly scoped only `config.py` + `candidate.py`. Six paths were affected: `Modal.tsx` (dropped `showFooter` prop + conditional footer), `JobAnalysisReportModal.tsx` (dropped `showFooter={false}`), the AST-1334 feature doc (**deleted**), its test-bible section, and its two component test files. **Root cause:** the `d63d0338 sync(publish-ref)` merge combined a `sync(dev)` pull with the sub's pre-AST-1334 tip; conflict resolution kept the older `Modal.tsx` (no `showFooter`) instead of the correct dev tree. **Recommendation:** re-merge `origin/dev`, keep dev's AST-1334 files on every conflicted ui/docs/test path while retaining AST-1332's own `config.py`/`candidate.py`/tests, re-run the manifest green, and explicitly verify `showFooter` survives.

**discuss** — process question (not product): should `sync(publish-ref)` after `sync(dev)` be gated on a quick diff smoke-check when dev has landed sibling tickets since the sub forked? Left open for orchestration, not answered in code.

Full statute sweep otherwise scored conforms/not-applicable throughout on the *intended* AST-1332 product paths — the violations flagged (`astral.docs.features-single-file-per-ticket`, `astral.standards.in-scope-only`, `astral.standards.no-cross-contamination`, `orch.pipeline.plan-is-bible`, `orch.git.merge-on-checkout` needs-discussion) were all specifically the AST-1334 regression, not new AST-1332 defects. **What's solid:** the config catalog and coercion algorithm matched the Joan-approved plan exactly; engineer product commits were test-tree-clean; fixture migrations from `highlights`-as-extra → `publications` were correct.

#### Resolution (2026-08-12)

Restored from `origin/dev` (product + feature doc only): `Modal.tsx` (`showFooter` prop + conditional footer), `JobAnalysisReportModal.tsx` (`showFooter={false}`), the AST-1334 feature doc. AST-1332's own product (`config.py` + `candidate.py`) retained unchanged. Betty then restored the AST-1334 test-tree from `origin/dev` (bible section + both component test files) — the three-dot diff vs `origin/dev` no longer touched any AST-1334 path, and the AST-1332 manifest re-ran 21 passed. The `sync`-gate process question was left open, not answered in code.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/utils/config.py` | Required-id tuple + default format map + DEFAULT section entry/renumbering | `111161d73` — +14/-4 |
| ✓ | `src/core/candidate.py` | Order-coercion block in `normalize_resume_structure` | `1bf6c7c9f` — +17 |
| | _tests_ | required Highlights catalog + order coerce coverage | `1883ec76b`; bible `docs/test-bible/core/candidate.md` @ `02927f20202c8dea91754697f85a6c191a29fa1c` |
| | _cross-ticket cleanup_ | (unplanned) restore AST-1334 UI + test-tree reverted by a bad `sync` merge | `da55f5e98`, `6649ab66f` |

### AST-1333 — Craft/parse schema and agent_task prompts
_Archived: 2026-08-19 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1333/craftparse-schema-and-agent-task-prompts-make-highlights-a-required · Status at archive: Archive · Project: Astral Artifacts · Assignee: katherine · Priority / estimate: None / 3 · Blocked by / blocks / related: parent: AST-1326_

#### What this implements

Add required `highlights` to the shared craft-base / simple-resume-parse response schema; update those agent_task prompts so Highlights is required and ordered above Experience (segment inventory / instructions stay consistent with the schema). Does **not** own structure-catalog membership or UI order (sibling #1).

#### Acceptance criteria

- [X] 4. Craft-base and simple-resume-parse response schemas require a `highlights` string; responses omitting the key fail schema validation.
- [X] 5. `craft_resume_base` and `simple_resume_parse` agent_task prompts state that Highlights is required and sits above Experience, consistent with the schema field inventory / segment instructions.

#### Boundaries

Does not own required catalog membership, default order, or normalize mint/coerce (sibling Required Highlights catalog). Does not change draft_job_resume nested envelope work.

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Insert `"highlights": {"type": "str", "required": True}` into `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA` immediately before `experience` (shared by `craft_resume_base` and `simple_resume_parse` via object identity) | utils |
| `data/admin/agent_task.json` | Update current `craft_resume_base` and `simple_resume_parse` `cache_prompt` text: segment count / field inventory / segment instructions require Highlights above Experience | data/admin |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Keep byte-identical with `data/admin/agent_task.json` after the prompt edits (`cp` after catalog edit) | docs |

#### Stage 1 — Shared response schema

`_CRAFT_RESUME_BASE_RESPONSE_SCHEMA` gains `"highlights": {"type": "str", "required": True}` immediately before `experience`; final key order: `resume_structure`, `candidate_name`, `candidate_title`, `candidate_contact_detail`, `candidate_tagline`, `professional_summary`, `core_competencies`, `highlights`, `experience`, `prior_experience`, `education_certifications`, `technical_skills`. Both `TASK_CONFIG["craft_resume_base"]["response_schema"]` and `TASK_CONFIG["simple_resume_parse"]["response_schema"]` stay the same object (`is` identity) — omitting `highlights` fails validation with `Missing required field 'highlights'`; empty string still passes.

⚠️ **Decision:** One shared schema object stays the single hop contract for both task keys (AST-1037). `required: True` means the key must be present, not non-empty — same as other required str fields. ⚠️ **Decision:** Do not mirror `highlights` into `BUILD_CONFIG["artifact_shapes"]["resume_content"]` on this ticket — parent AC names craft-base / simple-resume-parse response schemas only.

#### Stage 2 — agent_task seed prompts

`craft_resume_base` `cache_prompt`: segment count "exactly 9" → "exactly 10"; new `### highlights` segment block inserted immediately before `### experience`, instructing Highlights placement immediately above Experience, one-highlight-per-line plain text, resume as source of truth, no invented highlights, empty string allowed when source has none (key still required). `simple_resume_parse` `cache_prompt`: field-inventory block updated to list `highlights` among the required fields; the `resume_structure` known-id parenthetical gets `highlights` inserted before `experience`; a matching new `### highlights` block added before `### experience`. `docs/uat-fixtures/AST-756/expected-agent_task.json` re-synced byte-identical via whole-file `cp` (AST-786/AST-834 pattern) so catalog and fixture cannot drift.

⚠️ **Decision:** Prompt text is the durable Archie catalog — commit the JSON, not just a live Manage Tasks DB edit. ⚠️ **Decision:** Fixture sync via whole-file `cp`, not a surgical dual-edit, since the twin must match the full catalog.

#### Plan-discuss round=1 — Joan REVISE, then round 2 APPROVED

**fix-now — `craft_resume_base` QUALITY CHECKLIST contradicted the new empty-Highlights allowance.** The live prompt's checklist ended with "Every key present with a **non-empty string value**," while Stage 1's Decision and the new `### highlights` body both explicitly allow `""` when source material is absent. Shipping the `### highlights` block without reconciling the checklist would tell the model to violate AC5/schema for a valid empty-highlights response. **Recommendation:** amend the checklist to "every **required** key present," explicitly allowing empty strings for fields like `highlights` where source material is absent.

**discuss** — assignee was Katherine, not Joan, at fetch time (procedural gap, not blocking). **acceptable** — same Self-assessment-line hygiene gap as sibling AST-1332; footprint small, Decisions specific.

**Katherine's round=1 reply (Revision 1):** Stage 2 step 1 gained explicit step **1d**, replacing the blanket non-empty checklist bullet with: "Every required key present (string values may be empty when source material is absent — especially `highlights`)." Round 2: Joan confirmed the fix-now closed and approved.

#### QA test manifest — Betty

Existing: `TestAst1037SimpleResumeParseConfig` (shared schema identity). Broken/revised: AST-517 inject + AST-1005 `_OTHER_REQUIRED` gain `highlights: ""`; AST-996 / AST-1027–1030 prompt contracts retargeted to `simple_resume_parse` `current=1` (parse-specific marker/title/competencies contracts live on Ruth, not Judith synthesis — correct retarget). Gaps: `TestAst1333CraftParseHighlightsSchema`; `TestAst1333CraftParseHighlightsPrompts`.

#### Radia review — code-rubric.v1, CLEAN

Full statute sweep (scoped ticket delta: `config.py` schema line, `agent_task.json` + fixture twin, Betty tests/bible): all conforms/not-applicable — **no AST-1334-style regression in this diff** (explicitly checked and contrasted against the AST-1332 review finding). Schema key order matches plan; object-identity test proves both task keys share the schema; omit → `Missing required field 'highlights'`, `""` passes for both.

**discuss** — sibling issue-doc edit in the three-dot diff: this publish ref also carries a 2-line status update to AST-1332's own doc (a qa-handoff status note), not listed in AST-1333's Files Changed — docs-only, no product impact, non-blocking. **advisory** — the large `expected-agent_task.json` three-dot stat (~1359 lines) reflects a pre-existing dev↔fixture drift the plan-authorized whole-file `cp` corrects; the real two-dot diff (catalog → branch fixture) is 4 lines, the two prompt edits only — reviewers should not read the large stat as unrelated churn.

**What's solid:** shared schema object identity preserved so craft/parse contracts cannot drift; Joan's round-1 checklist clash fully resolved in the prompts; no AST-1334 regression (contrast with sibling); validation test proves both the omit-fails and empty-passes paths for both task keys.

#### Resolution (2026-08-12)

CLEAN. No fix-now/discuss product work. Product tip unchanged; advanced to User Testing after §9a dry-run.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/utils/config.py` | `highlights` required field in `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA` | `5ae3463ff` — +1 |
| ✓ | `data/admin/agent_task.json` | `craft_resume_base` + `simple_resume_parse` `cache_prompt` updates (Highlights segment, checklist fix, field inventory) | `26806660a` (with fixture twin) — 2-line real diff on the catalog itself |
| ✓ | `docs/uat-fixtures/AST-756/expected-agent_task.json` | Byte-identical resync via whole-file `cp` | `26806660a` — +653/-710 (large stat is pre-existing drift correction, not new churn — see Radia advisory) |
| | _tests_ | craft/parse required Highlights schema + prompts coverage | `6d2d68748`/`b9e14e293`; bible `docs/test-bible/utils/config.md` @ `d49cbf8fe38a1f01735f6caf48a35667d8903f34` |
