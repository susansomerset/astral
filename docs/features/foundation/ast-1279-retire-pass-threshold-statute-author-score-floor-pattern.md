# AST-1279 — Retire pass-threshold statute; author score_floor pattern + Code Rules

**Linear:** [AST-1279](https://linear.app/astralcareermatch/issue/AST-1279/retire-pass-threshold-statute-author-score-floor-pattern-code-rules)
**Parent:** [AST-1275](https://linear.app/astralcareermatch/issue/AST-1275/remove-pass-threshold-from-task-config) — Remove "pass_threshold" from task_config
**Publish ref:** `sub/AST-1275/AST-1279-retire-pass-threshold-statute-author-score-floor-pattern`

Retire active statute `astral.config.pass-threshold-vs-score-floor`, author approved catalog pattern `pattern.dispatch.score-floor`, and rewrite Code Rules §2.1 (plus the one §2.2 prose mention) so law matches shipped AST-1277 / AST-1278 behavior: `dispatch_task.score_floor` is the sole numeric floor (claim + scored soft-fail), explicit `0` is valid, and no `pass_threshold` key / statute / pattern remains. Docs and canon only — no runtime product edits.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `canon/statutes/astral/config/astral.config.pass-threshold-vs-score-floor.md` | Soft-retire (`status: retired`); statement notes successor pattern | canon / statutes |
| `canon/statutes/README.md` | Remove this id from the active harvested-corpus table | canon / statutes |
| `canon/statutes/HARVEST.md` | Mark crosswalk row retired (AST-1279) | canon / statutes |
| `canon/patterns/dispatch/pattern.dispatch.score-floor.md` | New — `status: approved` pattern (SCHEMA order) | canon / patterns |
| `canon/patterns/README.md` | Index the new approved pattern; bump approved count | canon / patterns |
| `canon/patterns/HARVEST.md` | Add crosswalk + supporting-package cite row | canon / patterns |
| `docs/ASTRAL_CODE_RULES.md` | §2.1: drop `pass_threshold` from TASK_CONFIG bullet; replace subsection with score_floor pattern; §2.2 drop `pass_threshold` from the example list | docs |

**Out of files (do not touch):** `src/**` (runtime owned by AST-1277 / AST-1278); `tests/` / `docs/test-bible/**` (Betty); sibling plan docs; historical feature plans that merely *cite* the retired statute (leave as historical); Linear text on sibling tickets.

---

## Stages

### Stage 1: Retire statute + index cleanup

**Done when:** `astral.config.pass-threshold-vs-score-floor` frontmatter has `status: retired` and the file still exists at its current path. `canon/statutes/README.md` harvested-corpus table no longer lists that id as an active row. `rg -n 'status: active' canon/statutes/astral/config/astral.config.pass-threshold-vs-score-floor.md` returns no matches. A catalog sweep of `canon/patterns/**` and `canon/statutes/**` finds no *active* statute and no pattern (any status) whose subject is `pass_threshold` / `pass-threshold` besides the retired statute file itself.

1. In `canon/statutes/astral/config/astral.config.pass-threshold-vs-score-floor.md`, change frontmatter only as follows (keep `id`, `title`, `tier`, `checkable`, `applies_when`, `source_docs`, `supersedes`, `approved_by`, `approved_at` unchanged):
   - `status: retired`
   - `superseded_by: null` (successor is a **pattern**, not a statute id — do not put `pattern.dispatch.score-floor` in `superseded_by`)

2. In the same file, replace the `# Statement` body (and Examples) so the retired file cannot be read as current law. Exact replacement after frontmatter:

   ```markdown
   # Statement

   **Retired (AST-1279).** Former rule that split `TASK_CONFIG.pass_threshold` (post-run grading) from `dispatch_task.score_floor` (claim gating only) is withdrawn. Authority for the numeric floor is pattern `pattern.dispatch.score-floor` — sole floor on the candidate’s `dispatch_task` row for both eligibility and scored soft-fail. Do not resurrect `pass_threshold` on `TASK_CONFIG`.

   ## Rationale

   Kept for citation history only. Active consumers must not treat this file as binding.

   ## Examples

   ### Conforming

   - (retired — see `pattern.dispatch.score-floor`)

   ### Violating

   - (retired — see `pattern.dispatch.score-floor`)
   ```

3. In `canon/statutes/README.md`, delete the harvested-corpus table row whose first column is `` `astral.config.pass-threshold-vs-score-floor` `` (the full markdown table row). Do not add a “retired” section; discovery is file frontmatter `status: active` (AUTHORING / README universal/scoped rules).

4. In `canon/statutes/HARVEST.md`, update the crosswalk row for `` `astral.config.pass-threshold-vs-score-floor` `` so the Status column becomes `create (AST-921), retired (AST-1279)` (keep id/tier/checkable/source/path columns).

5. Verify with ripgrep from repo root (expect **only** the retired statute file + historical docs/features / test-bible prose — not a second active statute or any `canon/patterns/**` file teaching `pass_threshold`):

   ```bash
   rg -n 'pass.threshold|pass_threshold' canon/statutes canon/patterns
   ```

   Allowed hits under `canon/`: the retired statute file (retirement wording) and zero matches under `canon/patterns/`. If any other `status: active` statute still teaches pass_threshold, **stop** and comment on the Linear **parent** (AST-1275) with the path — do not invent a second retirement in this ticket.

⚠️ **Decision:** Soft-retire (file remains) per `canon/statutes/AUTHORING.md`. `superseded_by` stays `null` because SCHEMA typed that field as a statute successor id; the replacement authority is recorded in the Statement prose and in Code Rules as `pattern.dispatch.score-floor`.

### Stage 2: Author `pattern.dispatch.score-floor` + pattern indexes

**Done when:** `canon/patterns/dispatch/pattern.dispatch.score-floor.md` exists with `status: approved`, SCHEMA-required frontmatter, and body sections in SCHEMA order. `canon/patterns/README.md` lists it under Harvested corpus as approved. `canon/patterns/HARVEST.md` has a crosswalk row and a supporting-package cite. No `pass_threshold` string appears in the new pattern file.

1. Create `canon/patterns/dispatch/pattern.dispatch.score-floor.md` with **exactly** this content (domain folder `dispatch/` already exists beside `pattern.dispatch.run-next-chain-authority.md`):

   ```markdown
   ---
   id: pattern.dispatch.score-floor
   name: dispatch_task.score_floor as sole numeric floor
   status: approved
   proposed_in: AST-1275
   approved_by: Archie
   approved_at: "2026-08-08"
   canonical_refs:
     - path: src/utils/config.py
       symbol: effective_dispatch_score_floor
     - path: src/utils/config.py
       symbol: DISPATCH_SCORE_FLOOR_VALUES
     - path: src/core/consult.py
       symbol: _dispatch_score_floor_for_task
     - path: docs/ASTRAL_CODE_RULES.md
       symbol: "§2.1"
   related_statutes:
     - astral.config.config-source-of-truth
     - astral.standards.no-hardcoded-sets
     - astral.idioms.render-verdict-orchestrates-consult
   supersedes: null
   superseded_by: null
   ---

   # Problem

   Scored consult / prefilter hops need one numeric floor for eligibility and post-run pass vs soft-fail. A parallel `TASK_CONFIG` threshold (`pass_threshold`) drifts from the candidate’s `dispatch_task` row and reintroduces magic floors.

   # Solution shape

   Treat `dispatch_task.score_floor` on the candidate’s matching row as the **sole** numeric floor for a scored step:

   - **Claim / count eligibility** and **scored soft-fail after the run** both read that row value (via `effective_dispatch_score_floor` / `_dispatch_score_floor_for_task` — pointers in `canonical_refs`).
   - Explicit `0` / `0.0` is valid and means no numeric soft-fail / no claim exclusion by floor.
   - `NULL` / missing normalizes to `1.0` for those paths (existing claim rule; same helper for verdict).
   - Do **not** put a numeric floor on `TASK_CONFIG`. Do **not** invent a coding statute for this concept — pattern only.
   - Dealbreaker (F-with-confidence) and technical-error fail paths stay outside the numeric floor.
   - Admin Score Floor options come from config (`DISPATCH_SCORE_FLOOR_VALUES` / labels API), including `0`.

   Point at `canonical_refs` — do not paste large code into this catalog entry.

   ## When not to use

   - Non-scored hops that do not consult `latest_score` / soft-fail math.
   - Resurrecting `pass_threshold` (or any synonym) on `TASK_CONFIG` as a second floor.
   - Turning this package into a coding statute under `canon/statutes/**`.

   ## Notes

   Proposed in parent AST-1275 architectural definition; runtime landed by AST-1277 / admin `0` by AST-1278; catalog + Code Rules by AST-1279. Retires the teaching of `astral.config.pass-threshold-vs-score-floor`.
   ```

2. In `canon/patterns/README.md`:
   - Update the Harvested corpus intro sentence so the approved count includes this entry (today: “Six catalog entries below are `status: approved`; one is `status: proposed`.” → seven approved, one proposed).
   - Append a table row: `` `| `pattern.dispatch.score-floor` | approved | `dispatch/pattern.dispatch.score-floor.md` |` `` after the existing `pattern.dispatch.run-next-chain-authority` row (or immediately above it if you prefer approved-before-proposed — either order is fine as long as the row exists once).

3. In `canon/patterns/HARVEST.md`:
   - Under **Supporting harvest packages**, add a row: `` `| dispatch score_floor (sole numeric floor) | `pattern.dispatch.score-floor` |` ``
   - Under **Crosswalk**, add: `` `| create (AST-1279) | `pattern.dispatch.score-floor` | dispatch | `dispatch/pattern.dispatch.score-floor.md` | AST-1275 / CODE_RULES §2.1 | approved — sole numeric floor; retires pass-threshold statute teaching |` ``

⚠️ **Decision:** Land `status: approved` with `approved_by: Archie` / `approved_at: "2026-08-08"`. Parent AST-1275 architectural definition named `pattern.dispatch.score-floor`, open questions none, and children 1–2 already shipped against that shape; ticket AC requires the pattern to be the cited authority (approved set). If Joan / Archie rejects the approval stamp during validate-plan, flip only the frontmatter status fields to `proposed` / `approved_by: null` / `approved_at: null` in a Plan Discuss revision — do not invent a different id.

### Stage 3: Rewrite Code Rules §2.1 (+ §2.2 prose)

**Done when:** `docs/ASTRAL_CODE_RULES.md` §2.1 no longer teaches `pass_threshold`; the old `#### pass_threshold vs dispatch_task.score_floor` subsection is gone and replaced by a score_floor subsection that cites **`pattern.dispatch.score-floor`** (not the retired statute). `rg -n 'pass_threshold' docs/ASTRAL_CODE_RULES.md` returns no matches. TASK_CONFIG bullet no longer lists `pass_threshold`.

1. In `docs/ASTRAL_CODE_RULES.md` §2.1 **Config blocks** → **TASK_CONFIG** bullet, replace the orchestration key list so it no longer includes `pass_threshold`. Exact old fragment to edit (keep surrounding sentence structure):

   - Remove `` `pass_threshold`, `` from the list that currently reads: pass/fail/error states, `save_prefix`, `pass_threshold`, readiness keys…

   After edit the orchestration clause must still list pass/fail/error states, `save_prefix`, readiness keys (`min_job_title_length`, `min_jd_chars`, `not_ready_state`), `requires_company`, and `fallback_batch_size` — **without** any threshold key.

2. In the same §2.1, replace the entire subsection headed `#### pass_threshold vs dispatch_task.score_floor` (including its `**Statute:** …` line and all three bullets) with:

   ```markdown
   #### dispatch_task.score_floor (sole numeric floor)

   **Pattern:** `pattern.dispatch.score-floor`

   - **`score_floor`** (on the candidate’s matching **`dispatch_task`** row) is the **only** numeric floor for a scored step: dispatch eligibility (claim/count) and post-run scored soft-fail / pass both read that row value via `effective_dispatch_score_floor` (explicit `0` valid; `NULL` → `1.0`).
   - Do **not** put a parallel floor on **TASK_CONFIG**. Do **not** cite retired statute `astral.config.pass-threshold-vs-score-floor`.
   - Dealbreaker and technical-error fails are unchanged; admin Score Floor options include `0` (`DISPATCH_SCORE_FLOOR_VALUES`).
   ```

3. In §2.2, edit the sentence that currently says core reads config for “grading_mode, vectors, pass_threshold, state transitions” — drop `pass_threshold` from that parenthetical (e.g. “grading_mode, vectors, state transitions”). Do not otherwise rewrite §2.2.

4. Confirm:

   ```bash
   rg -n 'pass_threshold|pass-threshold-vs-score-floor' docs/ASTRAL_CODE_RULES.md
   ```

   Expect: at most a mention of the **retired** statute id inside the new subsection’s “Do not cite” bullet (the template above includes that once). No teaching that `pass_threshold` is a live TASK_CONFIG key.

⚠️ **Decision:** Keep the retired statute id once in Code Rules as an explicit “do not cite” pointer so agents hunting the old name land on the pattern. Do not re-add a statute citation block for the retired id.

---

## Self-Assessment

**Scope:** Single-Component — canon statute/pattern indexes plus `docs/ASTRAL_CODE_RULES.md` §2.1/§2.2 prose; no `src/**`.

**Conf:** high — AUTHORING/SCHEMA paths are clear; sibling AST-1277 already shipped the symbols this pattern points at; retirement is a soft-retire already used elsewhere in the corpus.

**Risk:** Medium — wrong approved stamp or incomplete index cleanup would leave Joan/Radia citing dead law or a still-active contradictory statute; no runtime regression surface in this ticket itself.

## Rules self-review (§8)

- **§1.3 DRY:** Pattern points at existing helpers; no duplicated code blocks in the catalog.
- **§2.1 config:** Rewrite removes the obsolete dual-floor teaching; pattern aligns with config-owned `DISPATCH_SCORE_FLOOR_VALUES` / `effective_dispatch_score_floor`.
- **§2.4 batch / §2.6 state:** Unchanged; pattern explicitly leaves pass/fail/error state names alone.
- **§3.3 imports / §3.5 naming:** N/A (docs/canon only).
- **Test-tree ban:** Plan does not touch `tests/` or `docs/test-bible/**`.
- **No conflict requiring `conf-!!-NONE`.**
