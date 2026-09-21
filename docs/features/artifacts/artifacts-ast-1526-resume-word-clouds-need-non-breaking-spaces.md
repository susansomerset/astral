# AST-1526 — Resume word clouds need non-breaking spaces
**Component:** artifacts  
**Children:** AST-1528, AST-1536  
**Linear archived:** AST-1526 2026-09-09; AST-1528 2026-09-09; AST-1536 2026-09-09

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-29 10:16 | AST-1528 | docs | `caf38f385` | plan — word-cloud NBSP bullet glue |
| 2026-08-29 10:18 | AST-1528 | docs | `c367d956a` | Joan validate — NBSP glue path clear |
| 2026-08-29 10:19 | AST-1528 | code | `0301a6e40` | NBSP-bullet-NBSP on resume site markers |
| 2026-08-29 10:20 | AST-1528 | docs | `9dcc097ab` | build review stub |
| 2026-08-29 10:26 | AST-1528 | test | `9506781ad` | NBSP-bullet-NBSP glue lock on resume markers |
| 2026-08-29 10:26 | AST-1528 | merge-tests | `93939313c` | origin/tests 9506781a |
| 2026-08-29 10:30 | AST-1528 | docs | `7f40d36e0` | Radia review — NBSP bullet glue clean |
| 2026-08-29 17:48 | AST-1536 | docs | `5002e79e6` | plan-fix — NBSP glue at word_cloud render only |
| 2026-08-29 17:51 | AST-1536 | test | `fc2d8721b` | bug-repro — format-switch cloud glue at render |
| 2026-08-29 17:51 | AST-1536 | merge-tests | `15b28b28e` | origin/tests fc2d8721 |
| 2026-08-29 17:52 | AST-1536 | code | `58aaece63` | word_cloud NBSP glue at render only |
| 2026-08-29 17:55 | AST-1536 | docs | `aa5b552c3` | Radia review — render-only cloud glue clean |
| 2026-08-31 12:13 | AST-1526 | docs | `5fa373a9b` | mirror epic registry Threads |
| 2026-09-09 18:01 | AST-1528 | docs | `990b7d2df` | archive Linear issue content |
| 2026-09-09 18:01 | AST-1536 | docs | `82377d569` | archive Linear issue content |
| 2026-09-09 18:07 | AST-1526 | docs | `8d3e4b9f3` | archive Linear issue content |

_Straightforward build-then-bugfix arc, no cross-family entanglement: AST-1528 glued word-cloud bullet separators on the shared resume site-marker expand path (`_resume_site_markers`), which ran upstream of format dispatch — Susan then reported the glue was applied at the wrong time (generation, not render), because switching a section's format from `word_cloud` to free prose carried the encoding with it. AST-1536 moved the glue to a dedicated render-only helper called only from the `word_cloud` HTML-emit arm. AST-1536 has its own standalone ticket doc, but the richer build narrative (root cause, full proposed-change code, blast radius) lives embedded in `ast-1528-word-cloud-nbsp-bullet-glue.md` under a `## Bug: AST-1536` heading — reproduced below from that source since AST-1526 is genuinely its family (not foreign content)._

## Epic — AST-1526
_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1526/resume-word-clouds-need-non-breaking-spaces · Status at archive: Archive · Project: Astral Artifacts · Assignee: chuckles · Priority / estimate: None / 2 · Blocked by / blocks / related: —_

### Purpose

Resume **word cloud** sections (Core Competencies, Prior Experience when formatted as `word_cloud`, and any other body section on that format) must glue bullet separators with non-breaking spaces the same way the old `__` digraphs did — so print/HTML wrap never drops a bare `•` onto the start of a line, and the spaces between cloud items stay non-breaking. Pipe-authored content (`|` → emit bullet) currently lands as ordinary `" • "` and only tightens the left side, which is weaker than the historical `__•__` → NBSP-bullet-NBSP contract operators still expect.

### Functional scope

* **Word-cloud bullet glue.** On Open HTML / Print for base, session, and job resumes, every `word_cloud` body shows a non-breaking space immediately before each `•`, and non-breaking spaces as the separators between cloud items (the old `__` equivalent) — not ordinary spaces that let the line wrap onto a leading bullet.
* **Shared marker path, word-cloud outcome.** Restore that glue through the existing resume site-marker expand used before HTML emit (so pipe-authored and already-bulleted cloud strings both get the full NBSP treatment). Do not invent a second visual language, new digraphs, or a CSS-only wrap workaround.
* **Out of scope.** Cover-letter from-block layout; inventing new authoring digraphs; changing `word_cloud` typography (uppercase / letter-spacing) beyond separator whitespace; reopening AST-1381 experience-array work; UI authoring chrome.

### Component scope

* `src/core/builder.py` — **modified** — resume site-marker expand and/or `word_cloud` emit so cloud bullet joins use NBSP before `•` and NBSP between items (old `__` equivalence). No other files unless plan-child proves a config token already owns the emit separator and must move with DRY.

### Technical scope

* `src/core/builder.py` — modified `_resume_site_markers` (and only if needed the `word_cloud` arm of body-section emit): after `|`→bullet join (or when text already contains space-bullet-space), produce the same NBSP-bullet-NBSP shape `__•__` historically expanded to, so cloud HTML text nodes no longer keep a regular space after `•`. Do not fork a parallel marker helper for clouds alone unless plan forces it; prefer one expand path (DRY). No new tables, schema fields, or agent_task prompt changes expected.

### Architectural definition

* **Patterns to reuse** — `pattern.config.config-block` (authoring/emit separators already live on `COVER_FROM_BLOCK_CONFIG`; do not invent a second inline separator set in the builder); `pattern.layers.import-discipline` (emit stays in core builder; UI does not own spacer logic).
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.standards.in-scope-only`; `astral.standards.dry-and-focused-functions`; `astral.standards.no-hardcoded-sets` / `astral.config.config-source-of-truth`; `astral.layers.import-direction`; `astral.git.engineer-test-tree-ban`. Adjacent history: AST-1027 (preserve `__`/`~~` so markers expand 1:1) and AST-1381 (`|`→`•`); this epic closes the remaining space-side gap for word clouds.

### Acceptance criteria

1. A `word_cloud` section authored with `|` between items (e.g. Core Competencies) prints/Open-HTMLs with `\u00a0` immediately before each `•` and `\u00a0` between items — not a regular space after the bullet that allows wrap to start with `•`.
2. The same section authored with the old `__•__` digraphs still expands to the same NBSP-bullet-NBSP shape (no regression vs AST-1027).
3. Base resume Print, session Open HTML, and job resume Print that emit `word_cloud` all show the glued separators (shared builder path).
4. Non-`word_cloud` formats are unchanged in intent (no new digraphs, no cloud typography redesign); cover-letter from-block is untouched unless it already shared this exact helper call and the glue change is inseparable (prefer leave cover alone).

### Open questions

none

### Proposed child tickets

**Monolith check:** Functional scope has 2 capabilities on one inseparable emit path — single child intentional.

**1: Word-cloud NBSP bullet glue — Katherine** — Restore non-breaking spaces before each cloud `•` and between cloud items (old `__` equivalence) on the shared resume marker / `word_cloud` emit path so Print and Open HTML never wrap onto a leading bullet. Does **not** own cover from-block, new digraphs, or experience-array work.
**Citations:** `pattern.config.config-block`, `pattern.layers.import-discipline`, `astral.standards.in-scope-only`, `astral.standards.dry-and-focused-functions`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`, `astral.git.engineer-test-tree-ban`.
**Scope:** `src/core/builder.py` — modified `_resume_site_markers` and/or `word_cloud` body emit so space-bullet-space becomes NBSP-bullet-NBSP for cloud (and any text already on that expand path); no new files.
**Estimate: 2**

### Original brief

For word clouds, the string between the bullets should be non-breaking spaces, and one nonbreaking space before the bullet character (so that the new line never starts with a bullet). The equivalent of the `__` characters in the old formatting method.

#### Comments

##### susan — 2026-08-29T20:07:10.993Z
[bug]

The word-cloud nonbreaking spaces should be applied at the time of RENDER, not the time of GENERATION. Resume content can be switched from word cloud to free prose, and the additional encoding would mess it up.

##### chuckles — 2026-08-30T05:00:56.021Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-1536** | Word-cloud NBSP glue must apply at render, not generation |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-1536** — _Word-cloud NBSP glue must apply at render, not generation_
- **Quick check:** re-run the failure you reported for **AST-1536**.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

### Files changed (plan vs actual)

_No direct product commit trail on the parent beyond the epic-registry Threads mirror and archive-docs commits. Implementation landed via the two sub-issues below._

## Sub-issues

### AST-1528 — Word-cloud NBSP bullet glue
_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1528/word-cloud-nbsp-bullet-glue-resume-word-clouds-need-non-breaking · Status at archive: Archive · Project: Astral Artifacts · Assignee: katherine · Priority / estimate: None / 2 · Blocked by / blocks / related: parent: AST-1526_

#### What this implements

Restore non-breaking spaces before each cloud `•` and between cloud items (old `__` equivalence) on the shared resume marker / `word_cloud` emit path so Print and Open HTML never wrap onto a leading bullet. Resume `word_cloud` sections currently emit pipe-authored and space-bullet-space text as `\u00a0• ` — NBSP only on the left of `•`. Print/Open HTML can still wrap onto a leading bullet because the space after `•` is ordinary. Restores the historical `__•__` equivalence: NBSP-bullet-NBSP on the shared resume site-marker expand path. Cover-letter from-block stays on `candidate.expand_cover_from_block_text` and is not retargeted.

#### Stage 1 (as built)

In `_resume_site_markers`, the final tighten (previously `t.replace(" • ", "\u00a0• ")` after the `|` → `emit_separator` join) changes so every occurrence of the shared emit separator (`COVER_FROM_BLOCK_CONFIG["emit_separator"]`, currently `" • "`) becomes the glued form `"\u00a0•\u00a0"` — via the already-loaded `emit_sep` variable, not a second hard-coded literal. Order of operations unchanged: `__` → `\u00a0`, `~~` → `‑`, then `|` join with `emit_sep`, then the glue replace. `_emit_education_list_html`'s local `bullet` partition/join string updated to match the new shape (`"\u00a0•\u00a0"`, was `"\u00a0• "`) since education body text runs through the same marker expand before emit. Header `h1_inner` (`name\u00a0• title`) and contact `"\u00a0• ".join(parts)` explicitly left asymmetric — outside the glue replace, outside cloud separator intent. `COVER_FROM_BLOCK_CONFIG` in `src/utils/config.py` untouched — cover `expand_cover_from_block_text` shares `emit_separator` and stays `" • "`.

⚠️ **Decision:** prefer one expand path in `_resume_site_markers` (DRY) over a `word_cloud`-arm-only post-pass — the education partition update is inseparable blast inside `builder.py` from that shared tighten, not a new digraph or format.

#### Plan review — Joan (APPROVED)

**acceptable** — ticket was Plan Ready but assignee was Katherine, not Joan, at validate time — normal handoff, no plan change. **acceptable** — the global `emit_sep` → `\u00a0•\u00a0` replace also glues compact-title `title • company` strings, not only `word_cloud` — documented blast radius, parent AC4 allows inseparable shared-path blast, Betty's qa-child section names the compact-title asserts to flip. **acceptable** — `tests/component/core/test_builder.py` listed in Files Changed despite being outside ticket Scope — correct per `astral.git.engineer-test-tree-ban` (Betty at qa-child); explicit scope gate + engineer commit-only rule are both correct.

#### Radia review — code-rubric.v1, CLEAN

Full 65-statute sweep conforms/not-applicable throughout (18 universal, 47 scoped). Plan adherence confirmed exactly: `_resume_site_markers` final tighten uses `emit_sep` (not a second hard-coded literal), replaces with `\u00a0•\u00a0`, `__`/`~~`/`|`-join order unchanged; `_emit_education_list_html` partition string updated to match; `COVER_FROM_BLOCK_CONFIG` / cover from-block path untouched; header/contact joins correctly left asymmetric; documented blast radius (compact-title, education, meta tagline, competencies) applied consistently; Betty flipped legacy left-only asserts and added `TestAst1528WordCloudNbspBulletGlue`; bible manifest matches; estimate 2 fits footprint.

**advisory** — branch history carried an `e180a0d8 test(AST-1524)` ancestor commit in the log, but the three-dot diff vs `origin/dev` had zero deltas on those files (already aligned with dev) — no scope smuggling, optional squash/rebase only if Susan wants a linear AST-1528-only history. **advisory (UAT note for parent)** — header name/title and contact-line bullets remain left-NBSP-only by design; word_cloud/marker-path separators are fully glued both sides; UAT should not expect global `\u00a0•\u00a0` everywhere in resume HTML.

#### What's solid

Correct DRY fix — one shared expand path instead of a `word_cloud`-only fork; `emit_sep`-driven replace ties search string to config without mutating cover emit config; education partition companion prevents credential/rest split regression; `TestAst1528WordCloudNbspBulletGlue` scopes its negative `\u00a0• ` check to the `competencies-list` paragraph (avoids false fail on the asymmetric header); AST-1027 digraph fidelity preserved; AST-1382 pipe→bullet repro tightened (no more `or` fallback accepting left-only glue).

**Note — this shipped fix was itself later found to be at the wrong layer** (generation-time, not render-time) and was replaced by AST-1536, below, per Susan's direct bug report.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ (later revised by AST-1536) | `src/core/builder.py` | Tighten `_resume_site_markers` space-bullet-space → NBSP-bullet-NBSP; keep `_emit_education_list_html` partition on the same glued shape | `0301a6e40` — +3/-2 |
| | _tests_ | Flip asymmetric `\u00a0• ` expectations (markers, compact titles, education, competencies HTML) to `\u00a0•\u00a0` | `9506781ad`; bible per Betty manifest |

### AST-1536 — Word-cloud NBSP glue must apply at render, not generation
_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1536/word-cloud-nbsp-glue-must-apply-at-render-not-generation · Status at archive: Archive · Project: Astral Artifacts · Assignee: katherine · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1526_

#### Susan's report (verbatim)

[bug]

The word-cloud nonbreaking spaces should be applied at the time of RENDER, not the time of GENERATION. Resume content can be switched from word cloud to free prose, and the additional encoding would mess it up.

#### As-is / To-be / Root cause / Proposed change _(embedded build narrative, sourced from `ast-1528-word-cloud-nbsp-bullet-glue.md` § "Bug: AST-1536")_

**As-is:** AST-1528 added `emit_sep` → `\u00a0•\u00a0` inside `_resume_site_markers`, which runs on **every** resume string leaf via `_apply_resume_text_markers` **before** `_emit_body_sections_html` chooses a section format. Pipe-authored cloud text and space-bullet text therefore carry full NBSP-bullet-NBSP glue in the shared markers dict used by base Print, session Open HTML, and job Print. When that section's structure `format` is switched from `word_cloud` to `free_prose` (or any non-cloud format), emit still reads the already-glued string — free prose shows cloud encoding instead of ordinary `" • "` separators. Education partition was also tied to the global glued shape.

**To-be:** NBSP-before-bullet and NBSP-between-items glue (`\u00a0•\u00a0`) applies **only** when `_emit_body_sections_html` emits a section whose resolved `format` is `word_cloud` — immediately before `_emit_inline_emphasis_html` on that section's text. Stored / marker-expanded content keeps ordinary separators (pipe join → `" • "` / left-only `\u00a0• ` at most on the shared marker path); format switches do not inherit cloud glue. Parent AC1–3 still hold on Print/Open HTML for sections still on `word_cloud`. Cover from-block untouched.

**Repro:**
1. Candidate (or session paste) with structure section `core_competencies` (or any body section) at `format: word_cloud` and content `"Delivery | Alignment | Cloud"`.
2. Base Resume Print or session Open HTML — competencies paragraph shows `\u00a0•\u00a0` glue (expected while on word_cloud).
3. Structure editor: change that section's `format` to `free_prose`; save structure (content string unchanged).
4. Print / Open HTML again — **broken (pre-fix):** body emits with `\u00a0•\u00a0` in free-prose paragraphs because glue ran in `_resume_site_markers` before format dispatch. **Fixed:** free prose shows ordinary `" • "` (or left-only `\u00a0• ` from legacy marker tighten), not full cloud glue; switching back to `word_cloud` restores glued HTML.

**Root cause:** AST-1528 placed the `\u00a0•\u00a0` tighten on `_resume_site_markers` (shared pre-emit marker expand) instead of on the `word_cloud` HTML emit arm. `_apply_resume_text_markers` runs once upstream of format-specific emit, so glue is format-agnostic — violating Susan's render-time-only requirement and parent AC4 intent for non-`word_cloud` formats.

**Proposed change (as built, all in `src/core/builder.py`):**
1. **`_resume_site_markers` — remove global full glue.** Delete the AST-1528 final glue-replace block; restore the pre-AST-1528 left-only tighten (`t.replace(emit_sep, "\u00a0• ")`) so compact-title / education / contact strings keep historical asymmetric NBSP-before-bullet without both-sides cloud glue. `__`→`\u00a0`, `~~`→`‑`, authoring `|`→`emit_sep.join` (AST-1381/AST-1027 digraph path) unchanged — `A__•__B` still becomes `\u00a0•\u00a0` via the `__` replacement alone.
2. **Add a render-only glue helper**, private, same helpers region as `_resume_site_markers`:
   ```python
   def _glue_word_cloud_bullet_separators(text: str) -> str:
       """NBSP both sides of • for word_cloud HTML emit only (AST-1536)."""
       if not text:
           return text
       emit_sep = COVER_FROM_BLOCK_CONFIG["emit_separator"]
       glued = "\u00a0•\u00a0"
       t = text.replace(emit_sep, glued).replace("\u00a0• ", glued)
       return t
   ```
   Uses `emit_sep` from config, not a second hard-coded set; the `.replace("\u00a0• ", glued)` pass upgrades left-only marker output to full glue idempotently for cloud emit.
3. **`_emit_body_sections_html` — word_cloud arm only.** The arm now calls `cloud_text = _glue_word_cloud_bullet_separators(str(text))` and emits `<p class="competencies-list">{_emit_inline_emphasis_html(cloud_text)}</p>` — glue applied at render, not generation. Not called from `_apply_resume_text_markers`, `_mark_resume_value`, or non-`word_cloud` format arms.
4. **`_emit_education_list_html` — revert partition bullet** back to `bullet = "\u00a0• "` (education is `indented_bold_single`, not word_cloud).
5. **Do not touch:** `COVER_FROM_BLOCK_CONFIG`, `candidate.expand_cover_from_block_text`, header `h1_inner`, contact join, experience compact-title paths beyond restored left-only marker behavior.

⚠️ **Decision:** render-time glue in a dedicated helper called only from the `word_cloud` arm — not a second fork of `_resume_site_markers`. Shared marker expand keeps the pipe/`__`/`~~` contract; cloud-specific NBSP-between-items is emit-only.

#### Board — Joan CANON: OK / Betty TESTS: REVISE

Joan: "Proposed change reverts AST-1528 global glue in `_resume_site_markers` and applies `\u00a0•\u00a0` only in the `word_cloud` emit arm via `_glue_word_cloud_bullet_separators` — still reads `emit_sep` from `COVER_FROM_BLOCK_CONFIG`; no config mutation; core-only; cover from-block untouched. Aligns with `astral.standards.in-scope-only`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`, `astral.layers.import-direction`, and cited patterns... Parent epic prose favoring one shared expand path is a plan/definition tension resolved by Susan's render-time bug — not a canon gap requiring statute or pattern edits." Betty: `docs/test-bible/core/builder.md` § AST-1528 had no format-switch repro; `TestAst1528WordCloudNbspBulletGlue` locked the generation-path glue this change removes — flagged for revision alongside the fix.

#### Blast radius / what must still hold

AST-1528's `TestAst1528WordCloudNbspBulletGlue` and bible § AST-1528 needed their `_resume_site_markers("A | B | C")` expectation moved to left-only/ordinary join (not full glue); session word_cloud HTML test stays green via the new render arm — Betty owned this test-tree update (`astral.git.engineer-test-tree-ban`). Compact-title/meta/competencies tests flipped for AST-1528's global glue reverted toward left-only expectations. Product fix landed on its own bug publish ref, rolled up to the parent `ftr` after the fix lane completed. No JSON migration — fix is emit-path only. Parent AST-1526 AC1–3 (word_cloud Print/Open HTML glue for base/session/job), AST-1027 digraph fidelity, AST-1381 pipe→bullet join, and header/contact asymmetric joins all confirmed to still hold; parent AC4 / bug boundary (cover from-block unchanged, no new digraphs, non-word_cloud formats don't inherit cloud glue after format switch) is the bug's own fix target.

#### Review

Radia review — clean: render-only `_glue_word_cloud_bullet_separators` on the `word_cloud` arm; generation-path global glue reverted. [bug-repro] format-switch OK. §3h shortcut — no resolve().

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/core/builder.py` | Remove global glue from `_resume_site_markers`; add `_glue_word_cloud_bullet_separators`; call it only from the `word_cloud` emit arm; revert education partition bullet | `58aaece63` — +13/-4 |
| | _tests_ | `[bug-repro]` free_prose no cloud glue; word_cloud control still glued after format switch; markers left-only + render cloud; digraph + compact-title/meta/edu regression suite | `fc2d8721b`; bible per Betty manifest |
