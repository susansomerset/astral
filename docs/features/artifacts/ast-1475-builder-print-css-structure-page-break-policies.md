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
