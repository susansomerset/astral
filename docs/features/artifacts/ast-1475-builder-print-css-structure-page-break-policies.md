# AST-1475 — Builder print CSS from structure page-break policies

**Linear:** [AST-1475](https://linear.app/astralcareermatch/issue/AST-1475)
**Parent:** [AST-1462](https://linear.app/astralcareermatch/issue/AST-1462) — Create and position page break
**Publish ref:** `sub/AST-1462/AST-1475-builder-print-css-structure-page-break-policies`

Maps each enabled body section’s resolved `page_break_policy` (from `artifacts.resume_structure`, tokens owned by AST-1474) into the shared resume embedded `@media print` block so base, session-base, and job resume HTML honor flow / new-page-before / keep-together. Always keeps experience `.role` chunks together. Removes the legacy hard-coded `#prior-experience { page-break-before: always }` so structure policy wins. Does **not** own React editor controls (AST-1476) or config/schema (AST-1474).

## Scope gate

Ticket **## Scope** covers only:

- `src/core/builder.py` — print CSS from structure + mandatory role keep-together
- `tests/component/core/test_builder.py` — Betty at qa-child (engineer test-tree ban)
- `docs/test-bible/core/builder.md` — Betty at qa-child

Every product file and change kind below matches that Scope. Out of scope: `config.py` token lists, `candidate.py` normalize, `api_candidate.py` catalog, React / ArtifactEditor, cover-letter CSS, `BUILD_CONFIG["supported_sections"][*]["page_break_policy"]` rewrites.

**Prerequisite (sibling #1):** AST-1474 must be on the epic stack before **build-child** (`RESUME_STRUCTURE_PAGE_BREAK_POLICIES`, `RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT`, per-section `page_break_policy` on normalized structure). At plan time `origin/ftr/AST-1462-…` is not published yet; after Chuckles `merge-child` of AST-1474, `sync-child.sh` brings the constants. If build starts and those names are missing from `config.py`, **stop** and comment on the parent — do not reinvent tokens.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/builder.py` | Import AST-1474 page-break constants; add helper that maps structure policies → print CSS; replace hard-coded `#prior-experience` always-break with policy-driven rules; keep mandatory `.role` keep-together on all resume emit paths (`_emit_html_document` shared by base / session-base / job) | core |

**Betty at qa-child (not engineer commits):** `tests/component/core/test_builder.py`, `docs/test-bible/core/builder.md` — revise golden-print assertion that requires `#prior-experience { page-break-before: always; }`; add coverage for default keep-together, explicit `page_break_before`, `normal` (no forced break), and always-present `.role` avoid.

**Do not touch:** `src/utils/config.py`, `src/core/candidate.py`, `src/ui/api/api_candidate.py`, any `src/ui/frontend/**`, cover-letter print CSS in `_emit_cover_*`, canon pattern markdown files (pattern is introduced by behavior + citation only).

## Decisions (binding)

⚠️ **Decision:** Consume **only** AST-1474 structure tokens — `normal`, `page_break_before`, `avoid_split` — via `RESUME_STRUCTURE_PAGE_BREAK_POLICIES` / `RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT`. Do **not** read `BUILD_CONFIG["supported_sections"][*]["page_break_policy"]` (still has legacy `keep_with_next` mixed values; not the operator contract).

⚠️ **Decision:** CSS mapping (resume stylesheet style — `page-break-*` properties only, matching existing golden print rules):

| Token | Emit for section DOM id `#…` |
|-------|------------------------------|
| `avoid_split` | `page-break-inside: avoid;` |
| `page_break_before` | `page-break-before: always;` |
| `normal` | **no** section page-break rule (flow uninterrupted) |

Missing / blank / unknown policy on a section row → treat as `RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT` (`avoid_split`). Do not raise from the CSS helper (emit must stay best-effort; normalize already validates on Save).

⚠️ **Decision:** Emit policy rules only for **enabled body** section ids (`_structure_ordered_body_ids(resume_structure)`), using `_html_section_dom_id(sid)` for selectors. Skip contact/header trio (no body `<section id>`). Extras use the same helper (underscore → hyphen).

⚠️ **Decision:** **Always** include `.role { page-break-inside: avoid; }` inside `@media print` (keep the existing non-print `.role` rule too). This is mandatory experience keep-together — not driven by the section dropdown.

⚠️ **Decision:** **Delete** the hard-coded `#prior-experience { page-break-before: always; }` line. Prior experience gets a break only when its structure policy is `page_break_before`. Default `avoid_split` yields keep-together, not a forced new page.

⚠️ **Decision:** Keep golden companions `h2 { page-break-after: avoid; }` and `#competencies { page-break-after: avoid; }` unchanged — parent only gates the prior-experience always-break; those are not operator policy and are not this ticket’s removal target.

⚠️ **Decision:** Introduce pattern **`pattern.artifacts.resume-section-print-policy`** by implementing the helper + mapping above (structure policy → embedded print CSS; roles always avoid split). Do **not** add a new file under `canon/patterns/` in this ticket (not in Scope). Cite the pattern id in the module/helper docstring.

⚠️ **Decision:** Single injection point — `_emit_html_document` — so `build_base_resume`, `build_session_base_resume`, and `build_resume_from_job` all pick up policies via the `resume_structure=` they already pass. No per-entry-point CSS forks.

## Stage 1: Policy → print CSS helper + wire into `_emit_html_document`

**Done when:** Resume HTML from base, session-base, and job builders embeds `@media print` rules derived from structure `page_break_policy`; default / absent policy yields keep-together per enabled body section and **no** forced `#prior-experience` break; `.role` still has `page-break-inside: avoid` in print; setting `page_break_before` on a section emits `#<dom-id> { page-break-before: always; }`; `normal` omits that section’s break/inside rules.

1. In `src/core/builder.py`, extend the `src.utils.config` import with:
   - `RESUME_STRUCTURE_PAGE_BREAK_POLICIES`
   - `RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT`

2. Add a private helper **above** `_emit_html_document` (public-then-helpers: keep it with other emit helpers), e.g. `_print_section_page_break_css(resume_structure: Optional[dict]) -> str`:

   - If `resume_structure` is not a dict, treat as empty sections.
   - For each `sid` in `_structure_ordered_body_ids(resume_structure)` (empty list when structure missing):
     - Read `spec = (resume_structure.get("sections") or {}).get(sid) or {}`.
     - Resolve `policy = spec.get("page_break_policy")`; if not a `str` in `RESUME_STRUCTURE_PAGE_BREAK_POLICIES`, use `RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT`.
     - `dom = _html_section_dom_id(sid)`.
     - If `policy == "page_break_before"`: append `  #{dom} {{ page-break-before: always; }}\n`
     - Elif `policy == "avoid_split"`: append `  #{dom} {{ page-break-inside: avoid; }}\n`
     - Elif `policy == "normal"`: append nothing.
   - Return the concatenated string (may be empty).

   Docstring one-liner cite: implements `pattern.artifacts.resume-section-print-policy`.

3. In `_emit_html_document`, replace the static print block:

```css
@media print {{
  body {{ background: #fff; padding: 0; }}
  h2 {{ page-break-after: avoid; }}
  #competencies {{ page-break-after: avoid; }}
  #prior-experience {{ page-break-before: always; }}
  .role {{ page-break-inside: avoid; }}
  p, li {{ orphans: 3; widows: 3; }}
}}
```

with a f-string that:

   - Keeps `body`, `h2`, `#competencies`, `.role`, and `p, li` lines as today.
   - **Omits** `#prior-experience {{ page-break-before: always; }}`.
   - Inserts `{_print_section_page_break_css(resume_structure)}` inside the `@media print` block (after the competencies rule, before `.role`, is fine).

4. Remove or rewrite the stale comment near emit that says print CSS always has the golden prior-experience break (around the `emit_prior_experience` note) so it no longer claims an unconditional prior break.

5. Do **not** change cover-letter `@media print` blocks. Do **not** change body HTML emit order or DOM ids. Do **not** edit React or config defaults.

6. Smoke locally (no test-tree edits): call `build_session_base_resume` (or `build_base_resume` with a monkeypatched candidate) three times with the same content and structure differing only by one body section’s `page_break_policy` (`avoid_split` / `page_break_before` / `normal`) and confirm the embedded `<style>` matches the mapping table; confirm `.role { page-break-inside: avoid; }` remains; confirm `#prior-experience { page-break-before: always; }` is absent unless that section’s policy is `page_break_before`.

## Expected Betty / test-child notes (not engineer work)

When qa-child runs, expect at least:

- Flip or remove `TestGoldenStylesheet` (or equivalent) assertion that requires `#prior-experience { page-break-before: always; }` unconditionally.
- Add assertions: default structure → enabled body sections get `page-break-inside: avoid`; `page_break_before` on e.g. `experience` → `#experience { page-break-before: always; }`; `normal` on `prior_experience` → no `#prior-experience { page-break-before: always; }`; print block still contains `.role { page-break-inside: avoid; }`.
- ArtifactEditor structure-mode tests named in parent AC4 are **AST-1476**, not this child.

## Out of scope (siblings)

| Sibling | Owns |
|---------|------|
| AST-1474 (Ada) | Config tokens, normalize/default, GET catalog |
| AST-1476 (Katherine) | Structure header dropdown + Save UX (base + JAR) |

## Estimate

Confirm Chuckles estimate: 3 — agree

## Self-assessment

- **Confidence:** High — single shared emit path already receives `resume_structure`; AST-1474 fixed the token contract; change is localized CSS generation.
- **Risk:** Medium only for test golden flip (Betty) and ensuring ftr carries AST-1474 before build; product mapping itself is mechanical.
- **Ambiguity left:** None for build — if ftr lacks 1474 constants at build start, escalate rather than invent tokens.

## Joan validate

## Joan validate-plan — AST-1475

Identity: **Plan Ready**, assignee **Hedy Lamarr** (Joan label on ticket; Chuckles spawn — proceeding). Parent **AST-1462**. Publish ref `sub/AST-1462/AST-1475-builder-print-css-structure-page-break-policies` @ `740acbe2`. No `[plan-discuss]` rounds.

---

```text
[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1475
**Overall:** APPROVED
**Publish ref:** `sub/AST-1462/AST-1475-builder-print-css-structure-page-break-policies` @ `740acbe2`

## Traceability
AC1→Stage 1 (policy helper + remove hard `#prior-experience` always-break; default `avoid_split` → inside avoid); AC2→Stage 1 (`page_break_before` → `#<dom-id> { page-break-before: always; }`; `normal` omits rule); AC3→Stage 1 (mandatory `.role { page-break-inside: avoid; }` + section `avoid_split`); AC4 builder tests→Expected Betty section (golden flip + new print assertions); AC4 ArtifactEditor portion + parent AC4/5/6 UI→AST-1476 N/A; persistence/catalog→AST-1474 N/A.

## Findings

### discuss — Assignee is Hedy, not Joan
- **Location:** Linear assignee
- **Finding:** `validate-plan` expects Joan assignee during validation; ticket still assigned to Hedy.
- **Recommendation:** Chuckles restores Hedy after posting upshot (normal handoff).

### discuss — Child ticket AC4 names ArtifactEditor tests
- **Location:** ticket Description AC4 vs plan Expected Betty notes
- **Finding:** Ticket AC4 still says “ArtifactEditor structure-mode tests”; plan correctly scopes builder tests to Betty here and defers ArtifactEditor to AST-1476.
- **Recommendation:** Optional ticket description trim — plan is already right.

### discuss — CSS for enabled-but-empty body sections
- **Location:** Stage 1 helper vs `_emit_body_sections` skip-empty behavior
- **Finding:** Helper emits rules for all enabled body ids in structure; empty sections may skip HTML emit but still get print rules.
- **Recommendation:** Acceptable — harmless extra selectors; tightening to `emitted_ids` is optional follow-up, not required for this slice.

### acceptable — AST-1474 prerequisite not on epic worktree yet
- **Location:** Prerequisite note; `config.py` lacks `RESUME_STRUCTURE_PAGE_BREAK_*` on current tree
- **Finding:** Constants come from AST-1474 merge before build-child.
- **Recommendation:** Plan’s stop-and-escalate rule is correct; not a plan defect.

### acceptable — Golden test flip deferred to Betty
- **Location:** `TestAst1020GoldenStylesheet` requires unconditional `#prior-experience { page-break-before: always; }`
- **Finding:** Product change will break golden until qa-child; engineer test-tree ban blocks Ada/Hedy touching `tests/`.
- **Recommendation:** Matches workflow — Betty revises at qa-child per plan.

context_tokens≈24000
```

```text
[plan-rubric] PROCEED (Commit: 740acbe2) builder print CSS
```

```text
AST-1475 plan approved.
```

---

**In-session:** Scoped statutes considered — `astral.standards.in-scope-only`, `astral.config.config-source-of-truth` (via AST-1474 imports only), `astral.git.engineer-test-tree-ban` (Betty owns test paths; plan conforms). `pattern.config.config-block` + proposed `pattern.artifacts.resume-section-print-policy` (docstring cite, no canon file) match parent architectural intent. Single `_emit_html_document` injection covers `build_base_resume`, `build_session_base_resume`, and `build_resume_from_job`. Layer compliance: core-only product diff; `_structure_ordered_body_ids` + `_html_section_dom_id` align selectors with existing DOM ids (`core_competencies` → `#competencies`, etc.).

## Review

- **Publish ref:** `sub/AST-1462/AST-1475-builder-print-css-structure-page-break-policies`
- **Tip:** `7fb201ea`
- **Files:** `src/core/builder.py`

## Radia review

# Radia review — AST-1475

`[code-rubric] revision=2`  
**Rubric:** code-rubric.v2  
**Ticket:** AST-1475  
**Publish ref:** `sub/AST-1462/AST-1475-builder-print-css-structure-page-break-policies` @ `b9307d4a`  
**Overall:** CLEAN

---

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | No agent prompt/confidence surfaces in diff |
| astral.agent.do-task-delegation | scoped | not-applicable | No do_task delegation changes |
| astral.agent.grade-vector-validation | scoped | not-applicable | No rubric-vector validation changes |
| astral.batch.batch-id-first | scoped | not-applicable | No batch claim paths touched |
| astral.batch.batch-id-format | scoped | not-applicable | No batch-id format changes |
| astral.batch.claim-process-release | scoped | not-applicable | No claim/release helpers edited |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | No entity-agent-responses changes |
| astral.config.config-source-of-truth | scoped | conforms | AST-1475 consumes `RESUME_STRUCTURE_PAGE_BREAK_*` from config; no new scattered literals |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | No env/secret lookups |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | No debug artifact paths |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | No spike files |
| astral.dispatch.seed-auto-false | scoped | not-applicable | No dispatch seeding |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | No run_next/dispatch runner edits |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Plan doc matches ticket slug |
| astral.git.betty-no-src-or-features | scoped | not-applicable | Radia read-only |
| astral.git.engineer-test-tree-ban | scoped | conforms | Product diff is `builder.py` only; Betty owns test/bible commits |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Core-only product change; utils config import only |
| astral.layers.import-direction | scoped | conforms | `builder.py` imports page-break constants from `src.utils.config` at module top |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | No `scripts/**` changes |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | No UI layer product changes (AST-1474 api catalog on branch is prerequisite) |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | No coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | No consult/render paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | No route/auth changes |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | No seed JSON edits |
| astral.seed.archie-catalog-wins | scoped | not-applicable | No seed catalog conflicts |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | No boot/seed hot-path edits |
| astral.seed.define-approved | scoped | not-applicable | No define/seed work |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | No seed row resurrection |
| astral.seed.other-via-coverage-join | scoped | not-applicable | No coverage-join seed logic |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | No data layer changes |
| astral.standards.database-header-inventory | scoped | not-applicable | No `database.py` changes |
| astral.standards.debug-contract-gated | scoped | not-applicable | No new `debug=` emission; existing `_emit_html_document(debug=)` unchanged |
| astral.standards.dry-and-focused-functions | scoped | conforms | `_print_section_page_break_css` is focused; single injection point |
| astral.standards.in-scope-only | scoped | conforms | Product commit `7fb201ea` touches only `builder.py`; branch also carries documented AST-1474 prerequisite (4 `src/` files total) |
| astral.standards.logging-via-utils | scoped | conforms | No new `print()` / raw logging |
| astral.standards.names-not-ticket-ids | scoped | conforms | Helper name is domain-descriptive |
| astral.standards.no-cross-contamination | scoped | conforms | Imports stay inside layered `src/` tree |
| astral.standards.no-hardcoded-sets | scoped | conforms | Policy tuple read from config; no inline token sets |
| astral.standards.public-then-helpers | scoped | conforms | Private helper placed above `_emit_html_document` per plan |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | No utils→data late imports |
| astral.state.core-decides-transitions | scoped | not-applicable | No state transition edits |
| astral.state.job-prior-states-enforced | scoped | not-applicable | Job state machine untouched |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | No dispatch runner changes |
| astral.ui.frontend-file-placement | scoped | not-applicable | No frontend files in diff |
| astral.ui.naming-conventions | scoped | conforms | CSS selectors use existing `_html_section_dom_id` conventions |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | No server worker config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | `merge-tests(AST-1475)` at tip |
| orch.git.commit-vocabulary | universal | conforms | `code` / `test` / `merge-tests` / `docs` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | No wrong-parent product sync on tip (unlike prior AST-1474 contamination) |
| orch.git.ftr-sub-topology | universal | conforms | Publish ref follows `sub/AST-1462/AST-1475-*` |
| orch.git.merge-on-checkout | universal | conforms | `sync(ftr)` / `sync(dev)` commits present; merge-base `8aa3197f` |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No evidence of cherry-pick/rebase/force |
| orch.git.no-dev-agent-branches | universal | conforms | Standard sub publish ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review from `astral-AST-1462` worktree |
| orch.git.three-permanent-branches | universal | conforms | Diff anchored to `origin/dev` |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | No unresolved product-policy fork |
| orch.pipeline.plan-is-bible | universal | conforms | Stage 1 mapping, injection point, and golden removal match plan |
| orch.pipeline.project-scoped-queues | universal | conforms | Single-ticket review |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Spawn at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | `test(AST-1475)` + bible via Betty path |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | N/A to code diff |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Hedy remains assignee at Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | Radia read-only |

**Notes:** Joan plan-rubric verdict attached (APPROVED @ `740acbe2`); no Excluded statute list in attachment — straggler check N/A.

---

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `pattern.artifacts.resume-section-print-policy` | conforms | Helper implements plan mapping (`avoid_split`→inside avoid, `page_break_before`→before always, `normal`→omit); docstring cites id; canon file deferred per binding Decision |
| `pattern.config.config-block` | not-applicable | Not cited in plan Patterns; AST-1475 consumes existing AST-1474 config block rather than adding one |

---

## Plan adherence

**Product commit `7fb201ea` (+26/−3, `builder.py` only)** implements Stage 1 completely:

- Imports `RESUME_STRUCTURE_PAGE_BREAK_POLICIES` / `RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT`
- `_print_section_page_break_css` iterates `_structure_ordered_body_ids`, resolves policy with soft-default, maps tokens per binding table, uses `_html_section_dom_id`
- `_emit_html_document` f-string injects dynamic rules; removes hard `#prior-experience { page-break-before: always; }`; retains `h2`, `#competencies`, `.role`, `p, li` golden companions
- Stale emit comment updated
- Does **not** read `BUILD_CONFIG["supported_sections"][*]["page_break_policy"]`
- Cover-letter `@media print` block (≈L891) untouched
- All three resume emit paths (`build_base_resume`, `build_session_base_resume`, `build_resume_from_job`) already pass `resume_structure=` into `_emit_html_document`

**Branch tip vs `origin/dev`:** 4 `src/**` files — AST-1475 `builder.py` plus AST-1474 prerequisite (`config.py`, `candidate.py`, `api_candidate.py`). Expected epic-stack carry; no AST-1464 sibling product contamination on this ref (contrast AST-1474 prior review).

**Tests (Betty):** `TestAst1475PageBreakPrintCss` covers default `avoid_split`, `page_break_before` + `normal`, missing-policy soft-default + job path; `TestAst1020GoldenStylesheet` revised to assert absence of unconditional prior always-break. Bible manifest in `docs/test-bible/core/builder.md` § AST-1475 aligns.

**Estimate 3:** Fits isolated product + Betty golden flip.

---

## Findings

### discuss — Pattern not yet in canon catalog

- **Location:** `src/core/builder.py` `_print_section_page_break_css` docstring; plan binding Decision
- **Finding:** `pattern.artifacts.resume-section-print-policy` is cited and implemented but has no `canon/patterns/**` entry yet. Plan explicitly defers catalog file to a follow-up; Joan APPROVED this intro-by-behavior approach.
- **Recommendation:** Archie/Chuckles add approved pattern markdown when epic closes — not a block for this child.

### advisory — Print rules for enabled-but-empty body sections

- **Location:** `_print_section_page_break_css` vs `_emit_body_sections` skip-empty behavior
- **Finding:** Joan flagged harmless extra selectors when structure enables a section but body content is empty. Implementation matches plan (structure-driven ids, not emitted_ids).
- **Recommendation:** Optional follow-up only; no action required for AST-1475 sign-off.

### advisory — Prior Joan discuss items unchanged

- **Location:** issue doc Joan validate findings (assignee, AC4 ArtifactEditor wording, AST-1474 prerequisite timing)
- **Finding:** All addressed or acceptable; prerequisite AST-1474 constants now on branch.
- **Recommendation:** None.

---

## What's solid

- Single injection point in `_emit_html_document` covers base, session-base, and job resume paths
- Soft-default in CSS helper mirrors plan (“best-effort emit; normalize validates on Save”)
- Golden prior-experience always-break removal is the key parent AC deliverable
- Mandatory `.role { page-break-inside: avoid; }` preserved
- Branch hygiene: no wrong-parent product sync; clean 4-file `src/` footprint vs `origin/dev`

## Recommended actions (Chuckles — not Radia)

1. Post upshot; advance to Review Posted → User Testing routing per datt.
2. (Optional, epic close) Mint `canon/patterns/artifacts/pattern.artifacts.resume-section-print-policy.md` from implemented helper shape.

---

## Frame diff

| Field | Prior (issue doc stub) | This review |
|-------|------------------------|-------------|
| Tip SHA | `7fb201ea` | `b9307d4a` |
| Product files | `builder.py` | unchanged |
| Tests | stub | `f32da268` + `merge-tests` @ `b9307d4a` |
| `src/**` vs `origin/dev` | — | 4 files (1475 + 1474 prereq) |
| Verdict | stub | CLEAN |

context_tokens≈28000

---

```
[code-rubric] PROCEED (Commit: b9307d4a) structure policy print CSS
```

## Bug: AST-1487 — Restore builder page-break print CSS from structure

### As-is

`origin/dev` tip embeds `@media print { #prior-experience { page-break-before: always; } }` unconditionally in `_emit_html_document` and has no `_print_section_page_break_css`. Operator page-break policies persist on `artifacts.resume_structure.sections[*].page_break_policy` (AST-1474/1476 on dev) but print HTML ignores them: all-`avoid_split` still forces a new page before Prior Experience; `page_break_before` on Education & Certifications (`education_certifications` → `#education`) emits no break.

### To-be

Same as AST-1475 Stage 1 (already shipped on `sub/AST-1462/AST-1475-…` @ `7fb201ea`): resume print CSS derives from structure `page_break_policy` on every enabled body section; hard-coded prior always-break removed; `.role { page-break-inside: avoid; }` stays mandatory.

### Repro

1. On dev tip, call `build_session_base_resume(candidate_mod.default_resume_structure(), blob)` where `blob` includes non-empty `prior_experience` and `education_certifications` strings (minimal fixture from `TestAst1475PageBreakPrintCss._blob()` plus `"education_certifications": "MBA — Example U"`).
2. Inspect embedded `<style>`: `#prior-experience { page-break-before: always; }` is present even though every section policy is default `avoid_split`.
3. Set `structure["sections"]["education_certifications"]["page_break_policy"] = "page_break_before"`, re-emit: `#education { page-break-before: always; }` is absent.

### Root cause

AST-1475 product commit `7fb201ea` landed and passed review on `sub/AST-1462/AST-1475-builder-print-css-structure-page-break-policies` but never merged into `origin/dev`'s first-parent line for `src/core/builder.py`. Dev absorbed AST-1474 config/catalog and AST-1476 UI persistence; the builder emit half regressed to AST-1020's golden hard-coded `#prior-experience` always-break. `TestAst1475PageBreakPrintCss` and the revised `TestAst1020GoldenStylesheet` assertion from `f32da268` are also absent on dev tip.

### Proposed change

**Product (`src/core/builder.py`) — Hedy at make-fix:**

1. Extend the existing `src.utils.config` import block with `RESUME_STRUCTURE_PAGE_BREAK_POLICIES` and `RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT` (constants already on dev @ `config.py` L5568–5573).

2. Re-add `_print_section_page_break_css(resume_structure: Optional[dict]) -> str` immediately above `_emit_html_document`, matching AST-1475 Stage 1 / commit `7fb201ea`:
   - Docstring cites `pattern.artifacts.resume-section-print-policy`.
   - Non-dict structure → empty string.
   - For each `sid` in `_structure_ordered_body_ids(resume_structure)`: read `sections[sid].page_break_policy`; soft-default invalid/missing to `RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT`; map via `_html_section_dom_id(sid)`:
     - `page_break_before` → `  #{dom} { page-break-before: always; }\n`
     - `avoid_split` → `  #{dom} { page-break-inside: avoid; }\n`
     - `normal` → emit nothing.

3. In `_emit_html_document`'s `@media print` f-string (~L1437–1444):
   - Delete `#prior-experience {{ page-break-before: always; }}`.
   - Insert `{_print_section_page_break_css(resume_structure)}` after `#competencies {{ page-break-after: avoid; }}` and before `.role {{ page-break-inside: avoid; }}`.
   - Keep `body`, `h2`, `#competencies`, `.role`, and `p, li` lines unchanged.

4. Update the stale comment at ~L1176 from "print CSS always has the golden prior-experience break" to note structure-driven print page-breaks (same wording as `7fb201ea`).

5. No changes to cover-letter print CSS, config, API, React, or caller threading — `build_base_resume`, `build_session_base_resume`, and `build_resume_from_job` already pass `resume_structure=` into `_emit_html_document`.

**Tests (Betty at qa-fix / make-fix boundary per scope):**

- Restore `TestAst1475PageBreakPrintCss` from `f32da268` (three tests: default avoid_split + no forced prior; explicit `page_break_before`/`normal`; missing-policy soft-default + job path).
- Revise `TestAst1020GoldenStylesheet._assert_golden_style`: replace unconditional `assert "#prior-experience { page-break-before: always; }" in style` with `assert "#prior-experience { page-break-before: always; }" not in style` (or drop the prior-break assertion entirely if covered by AST-1475 class).
- Update `docs/test-bible/core/builder.md` manifest rows for AST-1475 + revised AST-1020 golden print note (remove "always-on `#prior-experience` break" language).

### Blast radius

- **Shared emit path:** `_emit_html_document` feeds base, session-base, and job resume HTML — all three pick up the fix via existing `resume_structure=` threading.
- **Golden print contract:** AST-1020 embedded stylesheet tests currently require the hard-coded prior break; they must flip with this fix (Betty).
- **Sibling docs:** AST-1476 plan references AST-1475 print mapping as prerequisite — no React/config changes needed.
- **Out of scope:** `config.py` tokens, `candidate.py` normalize, `api_candidate.py` catalog, ArtifactEditor (already correct on dev).

### What must still hold

- AST-1475 binding Decisions unchanged: token mapping table (`avoid_split` / `page_break_before` / `normal`); soft-default to `RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT`; rules only for `_structure_ordered_body_ids`; mandatory `.role { page-break-inside: avoid; }`; keep `h2 { page-break-after: avoid; }` and `#competencies { page-break-after: avoid; }`; no `BUILD_CONFIG["supported_sections"][*]["page_break_policy"]` reads.
- AST-1474/1476 on dev: catalog tokens and structure Save persistence continue to work without modification.
- Cover-letter `@media print` block untouched.
- Body HTML emit order and DOM ids (`prior_experience` → `#prior-experience`, `education_certifications` → `#education`) unchanged.
