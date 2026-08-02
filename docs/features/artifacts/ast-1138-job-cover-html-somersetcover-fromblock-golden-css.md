# AST-1138 — Job cover HTML — SomersetCover fromBlock + golden CSS

**Linear:** https://linear.app/astralcareermatch/issue/AST-1138/job-cover-html-somersetcover-fromblock-golden-css-cover-letter-header  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1124/cover-letter-header-is-incorrect  
**Publish ref:** `sub/AST-1124/AST-1138-job-cover-html-somersetcover-fromblock-golden-css`

After AST-1137: Print Cover Letter (cover-only job HTML via `build_cover_letter` / `build_cover_letter_from_job`) stops using the resume document header/contact strip; emits SomersetCover `fromBlock` from `resolve_cover_from_block`; reuses the existing SomersetCover stylesheet/DOM (session emit) for all cover style blocks; maps job Subject / Letter / signature into letter subject/body/signoff without dropping letter text; Style D debug on the touched job cover emit path. Does **not** own candidate from-block storage/UI, session Admin page defaults/CSS parity (AST-1139), resume HTML, or AST-1123 token semantics.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `BUILD_CONFIG["job_cover_somerset"]` — document title reuse + which session field keys job artifacts map into (no new CSS literals in config). Optional empty-string defaults for fields job artifacts do not store (`letter_date`, `to_block`, `signoff_closing`). | utils |
| `src/core/builder.py` | Rename/generalize session SomersetCover HTML helper for shared job+session use; add job→Somerset field mapper; rewrite `build_cover_letter_from_job` to call `resolve_cover_from_block` + shared SomersetCover emit (no resume `_emit_html_document` for cover-only); Style D debug for fromBlock source + document path. | core |

**Out of files (siblings / boundaries):** `CandidateProfile.tsx` / `COVER_FROM_BLOCK_CONFIG` / `resolve_cover_from_block` implementation (AST-1137 — consume only); `AdminSessionCoverLetter.tsx` / session empty-form defaults (AST-1139); `build_resume` / `build_base_resume` / `_emit_html_document` resume header+contact path; AST-1123 token literal/policy changes; `tests/`, bible.

## Stage 1: Config — job Somerset field map

**Done when:** `BUILD_CONFIG["job_cover_somerset"]` declares document title and the mapping from normalized job cover keys (`re_line`/`body`/`signature`) to Somerset session field keys; no builder behavior change yet.

1. In `src/utils/config.py`, inside `BUILD_CONFIG` immediately after `"session_cover_letter"`, add:
   ```python
   "job_cover_somerset": {
       "document_title_key": "session_cover_letter",  # reuse BUILD_CONFIG[…]["document_title"]
       # Normalized job cover keys → session_cover_letter field keys
       "artifact_to_fields": {
           "re_line": "subject",
           "body": "letter",
           "signature": "signature",
       },
       # Session fields job artifacts do not store — always "" for job Print Cover Letter
       "unset_fields": ("from_block", "letter_date", "to_block", "signoff_closing"),
   },
   ```
   `from_block` is listed under `unset_fields` as the **artifact** default (filled at emit from `resolve_cover_from_block`, not from the job artifact).
2. Do **not** duplicate golden CSS declarations into config — CSS stays in the shared SomersetCover emit helper (already matches parent brief / session AST-1024).
3. Do **not** change `session_cover_letter` required flags or Admin API contracts.

⚠️ **Decision:** Job artifacts stay `Subject`/`Letter`/`signature` (normalize via existing `_cover_letter_fields_for_read`). Layout-only session keys (`letter_date`, `to_block`, `signoff_closing`) are empty on the job path — omit-empty optional blocks already handled by the SomersetCover emit helper for `to_block`/`subject`; empty `letter_date` still emits the `.letterdate` div (same as session with blank date) so the stylesheet selector remains exercised without inventing a date.

## Stage 2: Share SomersetCover emit (DRY)

**Done when:** Session and job cover-only HTML both call one SomersetCover document helper; session public API behavior unchanged; helper docstring no longer claims "session-only".

1. In `src/core/builder.py`, rename `_emit_session_cover_html_document` → `_emit_somerset_cover_html_document`.
2. Update the helper signature to accept optional `document_title: Optional[str] = None`. When `None`, read title from `BUILD_CONFIG["session_cover_letter"]["document_title"]` (current behavior). When provided (job path), use the override — job path resolves override via `BUILD_CONFIG["job_cover_somerset"]["document_title_key"]` → that block's `"document_title"` (same string today: `SomersetCover`).
3. Keep CSS/DOM exactly as today (parent golden: `body`, `.cover-letter`, `.fromBlock`, `.toBlock`, `.letterdate`, `.lettersubject`, `.lettercontent` (+ `p` / `p:last-child`), `.letterSignoff`, `.signature-img`, `@page` / `@page :first`, print media rules). Do **not** edit selector/declaration values in this ticket unless a literal drift from the parent brief is found while reading the helper — if drift is found, align to the parent Description golden only (same as session target for AST-1139).
4. Point `build_session_cover_letter` at the renamed helper (behavior-identical call).
5. Keep `_session_cover_letter_paragraphs` name (shared paragraph split) — no rename required.

⚠️ **Decision:** Rename + thin title override beats copying the ~200-line CSS/DOM into a second job-only emitter (`astral.standards.dry-and-focused-functions`). AST-1139 can still tune session defaults without forking job CSS.

## Stage 3: Job cover-only → SomersetCover + fromBlock

**Done when:** `build_cover_letter_from_job` returns SomersetCover HTML with `fromBlock` from AST-1137 resolve; Subject/Letter/signature mapped; no resume `h1`/`.contact` chrome; resume builders untouched.

1. Add helper (private, near cover emit helpers):

   ```python
   def _job_cover_somerset_fields(cover: dict, from_block_text: str) -> dict:
       """Map normalized job cover + resolved from-block into session field keys."""
   ```

   Implementation (literal):
   - Start from `BUILD_CONFIG["job_cover_somerset"]`.
   - Build `fields: Dict[str, str]` with every key in `BUILD_CONFIG["session_cover_letter"]["fields"]` initialized to `""`.
   - For each `unset_fields` name, leave `""` (then set `from_block` from argument).
   - For each `(artifact_key, field_key)` in `artifact_to_fields.items()`, set `fields[field_key] = str(cover.get(artifact_key) or "")`.
   - `fields["from_block"] = from_block_text` (may be `""` if resolve returned empty).
   - Return `fields`.

2. Add helper to shape the coerced builder candidate blob for `resolve_cover_from_block`:

   ```python
   def _candidate_for_cover_from_block(cd: dict) -> dict:
   ```

   Map `_full`/`_first`/`_last` → `full`/`first`/`last`, pass through `contact` dict, and copy `astral_candidate_id` / `_astral_candidate_id` if present on `cd`. Do **not** change `resolve_cover_from_block` itself.

3. Rewrite `build_cover_letter_from_job` success path (after `_resolve_cover_letter` succeeds):
   - **Remove** the `_apply_contact_to_render_dict` / `_apply_resume_text_markers` / `_merge_effective_style` / `_emit_html_document(..., include_cover=True, body_section_ids=[])` path for this function.
   - `from_res = candidate_mod.resolve_cover_from_block(_candidate_for_cover_from_block(cd), debug=debug)` — import already via `candidate_mod` if present; else `from src.core import candidate as candidate_mod` (module already imports candidate for loads).
   - Resolve signature image the same way session does: `_signature_image_token_status(cover.get("signature") or "", {"contact": cd.get("contact") or {}})` (or pass a root that satisfies `tok["path"]` = `contact.cover_letter_signature_image`).
   - `fields = _job_cover_somerset_fields(cover, from_res["text"])`.
   - `html_out = _emit_somerset_cover_html_document(fields, signature_image_src=sig_src, document_title=…)` where title is loaded via `job_cover_somerset["document_title_key"]`.
   - Preserve existing `ValueError` when no cover content.
   - Do **not** change `build_cover_letter` load/orchestration except that it still returns `build_cover_letter_from_job(...)`.

4. **Do not** change `build_resume` / `_emit_html_document` / `_emit_cover_sections_html` — materials resume+cover embed and Resume Print stay on the resume stylesheet. Cover-only Print Cover Letter is the sole consumer of this rewrite (`/candidate/cover/<job_id>` → `build_cover_letter`).

5. Signature image token replace stays inside `_emit_somerset_cover_html_document` (AST-1126 session path). Do not reintroduce auto-image-above-name (`cover-signoff` job path is unused for cover-only after this change).

⚠️ **Decision:** Cover-only leaves the legacy `_emit_cover_sections_html` path for `build_resume` materials embed so Resume Print AC stays green without expanding into AST-1139/resume work. Parent AC #1 targets Print Cover Letter only.

## Stage 4: Style D debug on job cover emit

**Done when:** `debug=True` on `build_cover_letter_from_job` emits one index header + `|` details for fromBlock source and cover document path; no new debug when `debug=False`.

1. Replace/extend the existing debug block in `build_cover_letter_from_job` (keep `func="builder.build_cover_letter_from_job"`):
   - Index outcome: `success — somerset cover html` (or equivalent short success string).
   - `|` `from_block_source={from_res["source"]}` — must be one of `COVER_FROM_BLOCK_CONFIG["sources"]` values (`candidate` / `default`).
   - `|` `from_block_chars={len(from_res["text"])}`
   - `|` `document_path=somerset_cover` (literal distinguishing from old resume-shell path).
   - `|` `cover_source={cover_src!r}` (existing `_cover_letter_source_label`).
   - `|` field presence for mapped subject/letter/signature (nonempty bools).
   - Keep existing signature image token/image status lines and `html_chars` / preview block.
2. `resolve_cover_from_block(..., debug=debug)` may also emit its own index when debug — that is acceptable (AST-1137). Job emit must still log the fromBlock source on the **builder** index so cover-path debugging is scannable without reading candidate logs alone.
3. No React/UI debug.

## Contract check (manual — builder notes only)

- Print Cover Letter HTML contains `<div class="fromBlock">` with `<br>` between identity lines when defaults resolve to two lines; no centered resume `h1` / `.contact` strip as the cover header.
- Embedded `<style>` includes `.fromBlock`, `.toBlock`, `.letterdate`, `.lettersubject`, `.lettercontent`, `.letterSignoff`, `.signature-img` matching the shared golden helper.
- `build_resume` / `build_base_resume` HTML still uses resume header/contact (spot-check unchanged).
- Custom `contact.cover_letter_from_block` → `from_block_source=candidate`; empty → `default`.

## Self-Assessment

**Scope:** `Single-Component` — config map + `builder.py` cover-only emit rewrite reusing session SomersetCover helper; no UI.

**Conf:** `high` — AST-1137 resolve + AST-1024 SomersetCover emit already exist; this ticket is wiring and field mapping.

**Risk:** `Medium` — Print Cover Letter is user-visible; wrong mapping could drop Letter body or keep resume chrome. Mitigated by reusing the battle-tested session emitter and leaving resume paths untouched.

## Code Rules check

- §1.1 in-scope-only / no-cross-contamination: job cover-only only; no resume golden reopen; no session Admin defaults (AST-1139).
- §1.3 DRY: one SomersetCover document helper for session + job.
- §1.5.1 debug-contract-gated: Style D only when `debug=True`.
- §2.1 / §1.4: field map + unset keys in `BUILD_CONFIG["job_cover_somerset"]`.
- §3.3 import direction: builder → candidate resolve + utils config; no UI import.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1124/AST-1138-job-cover-html-somersetcover-fromblock-golden-css`

| Stage | Summary |
|-------|---------|
| 1 | `BUILD_CONFIG["job_cover_somerset"]` artifact→Somerset field map |
| 2 | Shared `_emit_somerset_cover_html_document` (session call sites updated) |
| 3 | `build_cover_letter_from_job` → resolve fromBlock + SomersetCover (no resume shell) |
| 4 | Style D debug: fromBlock source + `document_path=somerset_cover` |

**Build:** `code(AST-1138)` on `sub/AST-1124/AST-1138-job-cover-html-somersetcover-fromblock-golden-css` — `c86c8be587a10c29e1476a18e85a53bd6523f227`.

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1138
**Publish ref:** `70b1f775a1f675c828d1fd6d493126bc6b7c6141` (`origin/sub/AST-1124/AST-1138-job-cover-html-somersetcover-fromblock-golden-css`)
**Overall:** DISCUSS

### What's solid

- Stages 1–4 match the plan: `job_cover_somerset` config map; `_emit_somerset_cover_html_document` rename + title override; `_candidate_for_cover_from_block` / `_job_cover_somerset_fields`; `build_cover_letter_from_job` uses `resolve_cover_from_block` + SomersetCover (no resume `_emit_html_document` shell); Style D with `set_debug_flag`, `from_block_source`, `document_path=somerset_cover`.
- Golden selectors present on shared helper; `build_resume` / `_emit_html_document` path retained for resume.
- Session call site updated to renamed helper; no second CSS fork.
- One `merge-tests(AST-1138)`; helpers landed in follow-up `code(AST-1138)` before tests.

### Issues

**discuss (C4 straggler):** Joan excluded `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, and `astral.debug.spikes-under-debug-dir` at plan time; three-dot vs `origin/dev` puts them in-scope. Sweep scores all three **conforms**.

**advisory:** Intermediate commit `a2eabbc7` briefly called helpers before they were defined; tip `c86c8be5`+ completes the rename/defs before `merge-tests` — no tip defect.

### Recommended actions

1. Hedy: no product fix required for AST-1138 AC; acknowledge discuss via resolve-child (or no-op).

### Pattern conformance

Ticket-cited: `pattern.layers.import-discipline` / `in-scope-only` / `no-cross-contamination` / `debug-contract-gated` / `import-direction` / `dry-and-focused-functions` / `config-source-of-truth` — conforms (table). Invented catalog: none.

### Plan adherence

Self-Assessment Single-Component matches config + builder cover-only rewrite. Resume/session Admin boundaries held. CSS stays in shared helper per Joan discuss.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | conforms | not touched by this ticket’s behavior |
| astral.agent.do-task-delegation | scoped | conforms | not touched by this ticket’s behavior |
| astral.agent.grade-vector-validation | scoped | conforms | not touched by this ticket’s behavior |
| astral.batch.batch-id-first | scoped | conforms | not touched by this ticket’s behavior |
| astral.batch.batch-id-format | scoped | conforms | not touched by this ticket’s behavior |
| astral.batch.claim-process-release | scoped | conforms | not touched by this ticket’s behavior |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | not touched by this ticket’s behavior |
| astral.config.config-source-of-truth | scoped | conforms | BUILD_CONFIG[job_cover_somerset] artifact→field map |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | not touched by this ticket’s behavior |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | not touched by this ticket’s behavior |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths match none of ['artifacts/**', 'scripts/spikes/**'] |
| astral.debug.spikes-under-debug-dir | scoped | conforms | feature plans under docs/features/; not spike dumps |
| astral.dispatch.run-next-is-chain-authority | scoped | conforms | not touched by this ticket’s behavior |
| astral.dispatch.seed-auto-false | scoped | conforms | not touched by this ticket’s behavior |
| astral.docs.features-single-file-per-ticket | scoped | conforms | ast-1138 plan file present (sibling plans also on tip lineage) |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits touch tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | test-tree on Betty test/merge-tests SHAs only |
| astral.layers.core-vs-external-bright-line | scoped | conforms | no external I/O |
| astral.layers.import-direction | scoped | conforms | builder→candidate resolve + utils |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers ['scripts'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | config map only; no UI files |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | not touched by this ticket’s behavior |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | not touched by this ticket’s behavior |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers ['ui'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.seed.agent-tables-in-repo-json | scoped | conforms | not touched by this ticket’s behavior |
| astral.seed.archie-catalog-wins | scoped | conforms | not touched by this ticket’s behavior |
| astral.seed.boot-only-not-hot-path | scoped | conforms | not touched by this ticket’s behavior |
| astral.seed.define-approved | scoped | conforms | not touched by this ticket’s behavior |
| astral.seed.operator-rows-stay-deleted | scoped | conforms | not touched by this ticket’s behavior |
| astral.seed.other-via-coverage-join | scoped | conforms | not touched by this ticket’s behavior |
| astral.standards.data-raises-caller-logs | scoped | conforms | not touched by this ticket’s behavior |
| astral.standards.database-header-inventory | scoped | not-applicable | layers ['data'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.standards.debug-contract-gated | scoped | conforms | set_debug_flag + Style D only when debug=True |
| astral.standards.dry-and-focused-functions | scoped | conforms | shared _emit_somerset_cover_html_document; no CSS fork |
| astral.standards.in-scope-only | scoped | conforms | cover-only job path; resume emit untouched |
| astral.standards.logging-via-utils | scoped | conforms | builder _log debug helpers |
| astral.standards.names-not-ticket-ids | scoped | conforms | domain helper/API names; ticket only in comments/docs |
| astral.standards.no-cross-contamination | scoped | conforms | no resume header/contact shell on cover-only |
| astral.standards.no-hardcoded-sets | scoped | conforms | artifact_to_fields / unset_fields in config |
| astral.standards.public-then-helpers | scoped | conforms | private mappers beside cover emit helpers |
| astral.standards.utils-data-late-import-only | scoped | conforms | config literals only; no utils→data |
| astral.state.core-decides-transitions | scoped | conforms | not touched by this ticket’s behavior |
| astral.state.job-prior-states-enforced | scoped | conforms | not touched by this ticket’s behavior |
| astral.state.no-daisy-chain-in-run | scoped | conforms | not touched by this ticket’s behavior |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers ['ui'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.ui.naming-conventions | scoped | not-applicable | layers ['ui'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.ui.single-gunicorn-worker | scoped | conforms | config touch unrelated to gunicorn |
| orch.git.betty-merge-tests-one-sha | universal | conforms | one merge-tests(AST-1138) @ 70b1f775 pinning tests 5427c279 |
| orch.git.commit-vocabulary | universal | conforms | docs/code/test/merge-tests vocabulary on sub |
| orch.git.flow-direction-inviolable | universal | conforms | publish on origin/sub/AST-1124/AST-1138-… |
| orch.git.ftr-sub-topology | universal | conforms | child sub under parent ftr/AST-1124-… |
| orch.git.merge-on-checkout | universal | conforms | no illegal merge recipe in commits |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no cherry-pick/rebase/force on tip |
| orch.git.no-dev-agent-branches | universal | conforms | sub publish-ref only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | astral-AST-1124 epic worktree |
| orch.git.three-permanent-branches | universal | conforms | no permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | no open product decisions in diff |
| orch.pipeline.plan-is-bible | universal | conforms | stages 1–4 match plan Files Changed |
| orch.pipeline.project-scoped-queues | universal | conforms | Artifacts child scope only |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no canon/statutes edits |
| orch.roles.betty-owns-test-tree | universal | conforms | test/bible via Betty test+merge-tests commits |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee remains Hedy |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Hedy stays assignee through Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | no banned-path product edits |

## Notes

Joan plan-rubric APPROVED attached. §5f applied; §5g N/A. Three-dot includes AST-1137 lineage + sibling plan docs vs `origin/dev`.

context_tokens≈22000

## Resolution

**Date:** 2026-08-02  
**Review:** Radia `[code-rubric] revision=1` — Overall **DISCUSS** (no fix-now). Publish tip at review: `ef7e0776`.

| Finding | Action |
|---------|--------|
| discuss — C4 stragglers (`features-single-file-per-ticket`, `engineer-test-tree-ban`, `spikes-under-debug-dir`) now in-scope vs `origin/dev`; sweep **conforms** | No product change — acknowledged; tip already conforms |
| advisory — intermediate helper-order SHA | No tip defect; no change |

Merged `origin/dev` + `origin/ftr/AST-1124-cover-letter-header-is-incorrect` + `origin/<publish-ref>` before User Testing. No product edits required for this resolve pass.
