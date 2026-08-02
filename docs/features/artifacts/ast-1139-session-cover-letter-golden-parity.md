# AST-1139 — Session cover letter golden parity

**Linear:** https://linear.app/astralcareermatch/issue/AST-1139/session-cover-letter-golden-parity-cover-letter-header-is-incorrect  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1124/cover-letter-header-is-incorrect  
**Publish ref:** `sub/AST-1124/AST-1139-session-cover-letter-golden-parity`

After AST-1137: Admin Session Cover Letter HTML keeps SomersetCover `fromBlock` + the golden stylesheet contract; empty form `from_block` defaults via `resolve_cover_from_block` (candidate-owned text / contact defaults); UI allows Open HTML with empty from-block when a candidate is selected; Style D debug records fromBlock source + document path. Does **not** own job Print Cover Letter emit (AST-1138), candidate from-block storage/UI (AST-1137), or AST-1123 signature-image token semantics.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | On `BUILD_CONFIG["session_cover_letter"]["fields"]["from_block"]`, add `"empty_uses_candidate_resolve": True` (keep `"required": True`). Add `"from_block_sources": ("session", "candidate", "default")` on the `session_cover_letter` block for builder debug source labels. | utils |
| `src/core/builder.py` | In `build_session_cover_letter`: load candidate before from-block required check; when form `from_block` is empty and candidate is present, fill from `resolve_cover_from_block`; track fromBlock source for Style D; call shared SomersetCover emit helper (name after ftr merge — see Stage 2); CSS drift fix only if listed golden declarations differ. Reuse `_candidate_for_cover_from_block` if present after ftr merge; otherwise add it (identical to AST-1138 contract). | core |
| `src/ui/frontend/src/pages/AdminSessionCoverLetter.tsx` | Treat `from_block` as not blocking Open HTML when a candidate is selected; update help copy for empty-from-block defaults. | ui |

**Out of files (siblings / boundaries):** `resolve_cover_from_block` / `COVER_FROM_BLOCK_CONFIG` / Candidate Profile from-block field (AST-1137 — consume only); `build_cover_letter_from_job` / job Print Cover Letter path (AST-1138); AST-1123 token policy; resume HTML / `_emit_html_document` resume header; `tests/`, bible; no new admin HTML route.

## Stage 1: Config — session from-block defaulting contract

**Done when:** `session_cover_letter` declares that empty form `from_block` may resolve from the candidate, and names the allowed builder-level fromBlock source strings. No builder/UI behavior change yet.

1. In `src/utils/config.py`, inside `BUILD_CONFIG["session_cover_letter"]`, change the `from_block` field entry to:
   ```python
   "from_block": {"required": True, "empty_uses_candidate_resolve": True},
   ```
   Keep all other `fields` entries unchanged.
2. On the same `session_cover_letter` block (sibling of `"fields"` / `"document_title"`), add:
   ```python
   "from_block_sources": ("session", "candidate", "default"),
   ```
   - `"session"` = non-empty form `from_block` used as-is  
   - `"candidate"` / `"default"` = values returned by `resolve_cover_from_block` (must match `COVER_FROM_BLOCK_CONFIG["sources"]`)
3. Do **not** change `required` on other session fields. Do **not** add job `job_cover_somerset` here (AST-1138). Do **not** invent a new API route.

⚠️ **Decision:** Keep `required: True` so emitted HTML still expects a from-block after defaulting; `empty_uses_candidate_resolve` is the explicit gate for empty form + candidate (config source of truth — no bare `if key == "from_block"` policy without this flag).

## Stage 2: Builder — empty from-block → resolve + debug + CSS parity

**Done when:** Empty session `from_block` with a valid `candidate_id` emits SomersetCover HTML using `resolve_cover_from_block` text; non-empty form text wins; no candidate + empty from-block still 400s; Style D logs fromBlock source + `document_path=somerset_cover`; listed CSS selectors match the parent golden declarations.

### 2a. Shared emit helper name (ftr-aware)

At build start, after mandatory `git merge origin/ftr/AST-1124-cover-letter-header-is-incorrect`:

1. If `_emit_somerset_cover_html_document` exists (AST-1138 landed on ftr), call that from `build_session_cover_letter` (session path already should). Do **not** reintroduce a second CSS copy.
2. If only `_emit_session_cover_html_document` exists, keep calling that name for this ticket — do **not** rename in AST-1139 (rename is AST-1138). CSS drift edits (2c) apply to whichever helper session currently calls.

### 2b. Empty from-block defaulting in `build_session_cover_letter`

Rewrite the normalize / candidate-load order in `build_session_cover_letter` as follows (literal behavior):

1. Validate `fields` is a dict (existing).
2. Read `cfg = BUILD_CONFIG["session_cover_letter"]`, `field_defs = cfg["fields"]`.
3. Resolve `cid` / load candidate **before** required checks when `candidate_id` is a non-empty stripped string (same `get_candidate` / not-found `ValueError` as today). Build `candidate_root = _coerce_candidate_blob(row)` when loaded; else `{}`.
4. Initialize `from_block_source = None` (str | None).
5. Build `normalized: Dict[str, str]` by iterating `field_defs`:
   - Coerce each value to string (same type error as today for non-str).
   - **Special case `from_block`:**  
     - If `raw.strip()` non-empty → `normalized["from_block"] = raw` (preserve internal newlines; do not strip — match current assignment of `raw` as today for other fields; for from_block use `raw` unchanged like today). Set `from_block_source = cfg["from_block_sources"][0]` (`"session"`).  
     - Else if `field_defs["from_block"].get("empty_uses_candidate_resolve")` and `candidate_root` is non-empty (candidate was loaded):  
       - Shape for resolve: if `_candidate_for_cover_from_block` exists in this module, call it; else add helper (public-helpers section near cover emit):
         ```python
         def _candidate_for_cover_from_block(cd: dict) -> dict:
             """Shape coerced builder candidate blob for ``resolve_cover_from_block``."""
             out: Dict[str, Any] = {
                 "full": cd.get("_full") or "",
                 "first": cd.get("_first") or "",
                 "last": cd.get("_last") or "",
                 "contact": cd.get("contact") or {},
             }
             if "astral_candidate_id" in cd:
                 out["astral_candidate_id"] = cd["astral_candidate_id"]
             if "_astral_candidate_id" in cd:
                 out["_astral_candidate_id"] = cd["_astral_candidate_id"]
             return out
         ```
       - `from_res = candidate_mod.resolve_cover_from_block(_candidate_for_cover_from_block(candidate_root), debug=debug)`
       - `normalized["from_block"] = from_res["text"]`
       - `from_block_source = from_res["source"]` (must be `"candidate"` or `"default"` — already constrained by AST-1137)
       - Do **not** raise required for empty resolve text (composition may be empty if contact/name blank).
     - Else (empty form, no candidate): apply existing required failure — `from_block is required`.
   - For every other key: existing `required` + `normalized[key] = raw` behavior unchanged.
6. Signature image token status / `_emit_*_cover_html_document` call unchanged aside from helper name per 2a.
7. Style D (`debug=True`) on success index `func="builder.build_session_cover_letter"`:
   - Keep existing field/candidate/signature detail lines.
   - Add `|` `from_block_source={from_block_source}` (must be one of `cfg["from_block_sources"]`).
   - Add `|` `from_block_chars={len(normalized["from_block"])}`.
   - Add `|` `document_path=somerset_cover`.
   - No new debug when `debug=False`.

⚠️ **Decision:** Form non-empty text is source `session` and does **not** write through to `contact.cover_letter_from_block` (Admin tool still does not persist). Empty form + candidate uses AST-1137 resolve only.

### 2c. Golden CSS parity (session emit helper)

Against the parent Original brief `<style>` (AST-1124 Description), verify the session SomersetCover helper’s embedded rules for: `body`, `.cover-letter`, `.fromBlock`, `.toBlock`, `.letterdate`, `.lettersubject`, `.lettercontent`, `.lettercontent p`, `.lettercontent p:last-child`, `.letterSignoff`, `.signature-img`, `@page` / `@page :first`, and `@media print` blocks.

1. For each listed selector, every golden declaration must be present with the same value (CSS variables allowed where golden uses `var(--…)`). Theme tokens may come from `BUILD_CONFIG["default_style"]` where the helper already interpolates into `:root` / `background: {page_bg}`.
2. **Known baseline (as of ftr + AST-1137):** listed SomersetCover rules already match the golden; `:root` / `*` extras may remain; body may keep extra `color` / `line-height` / `font-size` only if they do not contradict a golden declaration (golden does not set those — leave as-is unless a listed property drifts).
3. If any listed declaration differs from the golden, edit **only** that helper’s CSS string to restore parity. Do **not** touch resume `_emit_html_document` CSS.
4. Do **not** change DOM structure for AST-1123 token placement.

## Stage 3: Admin Session UI — empty from-block when candidate selected

**Done when:** With a candidate selected, Open HTML is enabled even if From block is blank; without a candidate, From block remains required in the UI; help text states empty from-block uses candidate defaults.

1. In `AdminSessionCoverLetter.tsx`, change `requiredComplete` so that for `from_block`, the field is treated as satisfied when `(fields.from_block ?? "").trim() !== ""` **or** `selectedId` is a non-empty trimmed string. All other `required` fields keep the existing nonempty check.
2. Update the intro `<p>` (help copy) to state clearly: when a candidate is selected, leaving From block empty uses that candidate’s cover from-block text or the contact default (`Name • City, ST` / `email • phone`); when no candidate is selected, From block is required. Keep “does not save to the database.”
3. Do **not** compose defaults in React (no client-side `Name • City` join). Do **not** add a new API. Do **not** change `SESSION_COVER_FIELDS` keys/labels beyond copy if needed — `required: true` on the field descriptor may stay; gating is only in `requiredComplete`.
4. No change to `api_admin.session_cover_letter_html` unless a type/error message must mention the new defaulting (prefer builder `ValueError` strings unchanged).

## Contract check (manual — builder notes only)

- Candidate selected + empty From block + filled date/letter/signoff/signature → Open HTML succeeds; HTML has `<div class="fromBlock">` with `<br>` between default lines when contact resolves to two lines.
- Candidate with custom `contact.cover_letter_from_block` → that text appears; debug `from_block_source=candidate`.
- Candidate without custom from-block → composed defaults; debug `from_block_source=default`.
- Non-empty form From block → that text wins; debug `from_block_source=session`.
- No candidate + empty From block → Open HTML stays disabled; API still 400 if called.
- Embedded `<style>` includes `.fromBlock`, `.toBlock`, `.letterdate`, `.lettersubject`, `.lettercontent`, `.letterSignoff`, `.signature-img` matching golden declarations.
- Job Print Cover Letter / resume HTML not modified by this ticket’s commits.

## Self-Assessment

**Scope:** `Single-Component` — session cover config flag + `build_session_cover_letter` defaulting/debug + Admin Session form gating; no job cover emit rewrite.

**Conf:** `high` — AST-1137 `resolve_cover_from_block` is on ftr; session SomersetCover emitter and Admin form already exist; this ticket wires empty-form defaults and documents CSS parity.

**Risk:** `Medium` — Admin Session Cover Letter is user-visible; wrong required gating could block Open HTML or emit empty headers. Mitigated by keeping no-candidate required path and reusing the shared resolve helper.

## Code Rules check

- §1.1 in-scope-only / no-cross-contamination: session Admin path only; no job cover rewrite; no resume golden reopen; no AST-1123 token work.
- §1.3 DRY: reuse `resolve_cover_from_block` and the single SomersetCover HTML helper (shared with AST-1138 when present on ftr); do not fork CSS.
- §1.4 / §2.1: `empty_uses_candidate_resolve` + `from_block_sources` live in `BUILD_CONFIG["session_cover_letter"]`.
- §1.5.1 debug-contract-gated: Style D only when `debug=True`.
- §3.2 / §3.3: UI does not compose from-block defaults; composition stays in core via AST-1137 helper.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1124/AST-1139-session-cover-letter-golden-parity`

| Stage | Summary |
|-------|---------|
| 1 | `empty_uses_candidate_resolve` + `from_block_sources` on `session_cover_letter` |
| 2 | `build_session_cover_letter` empty→`resolve_cover_from_block`; Style D source + `document_path=somerset_cover`; SomersetCover helper present for call sites |
| 3 | Admin Session: empty from-block allowed when candidate selected; help copy |

Tip: `84737c54`

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1139
**Publish ref:** `c2ffe7bad168cfcd69e3f939ad20b5c0e3aeaf8f` (`origin/sub/AST-1124/AST-1139-session-cover-letter-golden-parity`)
**Overall:** DISCUSS

### What's solid

- Stages 1–3 match the plan: `empty_uses_candidate_resolve` + `from_block_sources`; `build_session_cover_letter` loads candidate before from-block check, empty→`resolve_cover_from_block`, Style D `from_block_source` / `from_block_chars` / `document_path=somerset_cover` behind `set_debug_flag`; Admin Session gates Open HTML when candidate selected; help copy updated; no React-side composition.
- SomersetCover CSS selectors for golden list present (`.fromBlock`, `.toBlock`, `.letterdate`, `.lettersubject`, `.lettercontent`, `.letterSignoff`, `.signature-img`, `@page`, `@media print`).
- Debug contract gated correctly on the session builder path.
- One `merge-tests(AST-1139)` pins Betty tip; engineer commits stay off the test tree.

### Issues

**discuss (C4 straggler):** Joan excluded `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, and `astral.debug.spikes-under-debug-dir` at plan time; three-dot vs `origin/dev` puts them in-scope. Sweep scores all three **conforms**.

**discuss (cross-ticket boundary):** AST-1138 left call sites to `_emit_somerset_cover_html_document` / `_candidate_for_cover_from_block` / `_job_cover_somerset_fields` without defining the rename + job field mapper. AST-1139 `code` commit completed those helpers (plan allowed adding `_candidate_for_cover_from_block` if missing). Not a session-AC defect; resolve/merge hygiene only — confirm AST-1138 tip owns the job helper long-term.

**advisory:** Frontend `requiredComplete` hardcodes `from_block` + candidate-selected exception (plan Stage 3 literal) rather than reading `empty_uses_candidate_resolve` from a server payload — acceptable per plan.

### Recommended actions

1. Katherine: no product fix required for AST-1139 AC; acknowledge discuss items (or no-op) via resolve-child.
2. Optional: ensure AST-1138 publish tip already contains the helper defs so future children do not re-land job mappers.

### Pattern conformance

Ticket-cited: `astral.standards.dry-and-focused-functions` / `in-scope-only` / `debug-contract-gated` / `astral.config.config-source-of-truth` / `astral.layers.import-direction` / `astral.layers.ui-config-driven-business-logic` — conforms (see table). Invented pattern catalog: none.

### Plan adherence

Self-Assessment Single-Component matches session config + builder defaulting/debug + Admin gating. Job Print Cover Letter rewrite not introduced as new scope beyond repairing shared helpers already called from the ftr tip. CSS parity Stage 2c satisfied by existing SomersetCover helper rules.

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
| astral.config.config-source-of-truth | scoped | conforms | empty_uses_candidate_resolve + from_block_sources in BUILD_CONFIG |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | not touched by this ticket’s behavior |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | not touched by this ticket’s behavior |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths match none of ['artifacts/**', 'scripts/spikes/**'] |
| astral.debug.spikes-under-debug-dir | scoped | conforms | feature plans under docs/features/; not spike dumps |
| astral.dispatch.run-next-is-chain-authority | scoped | conforms | not touched by this ticket’s behavior |
| astral.dispatch.seed-auto-false | scoped | conforms | not touched by this ticket’s behavior |
| astral.docs.features-single-file-per-ticket | scoped | conforms | one docs/features/artifacts/ast-1139-….md (siblings also present on tip) |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits touch tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | test-tree on Betty test/merge-tests SHAs only |
| astral.layers.core-vs-external-bright-line | scoped | conforms | no external I/O |
| astral.layers.import-direction | scoped | conforms | builder→candidate resolve + utils; UI no compose |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers ['scripts'] ∩ diff ['core', 'docs', 'ui', 'utils'] empty |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | UI gates Open HTML only; composition in core |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | not touched by this ticket’s behavior |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | not touched by this ticket’s behavior |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | existing auth’d session HTML endpoint; no new routes |
| astral.seed.agent-tables-in-repo-json | scoped | conforms | not touched by this ticket’s behavior |
| astral.seed.archie-catalog-wins | scoped | conforms | not touched by this ticket’s behavior |
| astral.seed.boot-only-not-hot-path | scoped | conforms | not touched by this ticket’s behavior |
| astral.seed.define-approved | scoped | conforms | not touched by this ticket’s behavior |
| astral.seed.operator-rows-stay-deleted | scoped | conforms | not touched by this ticket’s behavior |
| astral.seed.other-via-coverage-join | scoped | conforms | not touched by this ticket’s behavior |
| astral.standards.data-raises-caller-logs | scoped | conforms | not touched by this ticket’s behavior |
| astral.standards.database-header-inventory | scoped | not-applicable | layers ['data'] ∩ diff ['core', 'docs', 'ui', 'utils'] empty |
| astral.standards.debug-contract-gated | scoped | conforms | set_debug_flag + Style D details only when debug=True |
| astral.standards.dry-and-focused-functions | scoped | conforms | reuses resolve_cover_from_block + single SomersetCover emit |
| astral.standards.in-scope-only | scoped | conforms | session Admin path primary; shared emit helpers completed for ftr tip |
| astral.standards.logging-via-utils | scoped | conforms | builder _log debug helpers |
| astral.standards.names-not-ticket-ids | scoped | conforms | API/config names domain language; ticket only in comments/docs |
| astral.standards.no-cross-contamination | scoped | conforms | no resume emit; job path only via shared SomersetCover helper |
| astral.standards.no-hardcoded-sets | scoped | conforms | from_block_sources + empty_uses flag from config |
| astral.standards.public-then-helpers | scoped | conforms | helpers near cover emit; session public entry unchanged |
| astral.standards.utils-data-late-import-only | scoped | conforms | config literals only; no utils→data |
| astral.state.core-decides-transitions | scoped | conforms | not touched by this ticket’s behavior |
| astral.state.job-prior-states-enforced | scoped | conforms | not touched by this ticket’s behavior |
| astral.state.no-daisy-chain-in-run | scoped | conforms | not touched by this ticket’s behavior |
| astral.ui.frontend-file-placement | scoped | conforms | page stays AdminSessionCoverLetter.tsx |
| astral.ui.naming-conventions | scoped | conforms | existing PascalCase page; field keys snake_case |
| astral.ui.single-gunicorn-worker | scoped | conforms | config touch unrelated to gunicorn |
| orch.git.betty-merge-tests-one-sha | universal | conforms | one merge-tests(AST-1139) @ c2ffe7ba pinning tests 7ea88470 |
| orch.git.commit-vocabulary | universal | conforms | docs/code/test/merge-tests vocabulary on sub |
| orch.git.flow-direction-inviolable | universal | conforms | publish on origin/sub/AST-1124/AST-1139-… |
| orch.git.ftr-sub-topology | universal | conforms | child sub under parent ftr/AST-1124-… |
| orch.git.merge-on-checkout | universal | conforms | no illegal merge recipe in commits |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no cherry-pick/rebase/force on tip |
| orch.git.no-dev-agent-branches | universal | conforms | sub publish-ref only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | astral-AST-1124 epic worktree |
| orch.git.three-permanent-branches | universal | conforms | no permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | no open product decisions in diff |
| orch.pipeline.plan-is-bible | universal | conforms | stages 1–3 match plan Files Changed |
| orch.pipeline.project-scoped-queues | universal | conforms | Artifacts child scope only |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no canon/statutes edits |
| orch.roles.betty-owns-test-tree | universal | conforms | test/bible via Betty test+merge-tests commits |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee remains Katherine |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Katherine stays assignee through Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | no banned-path product edits |

## Notes

Joan plan-rubric APPROVED attached. §5f applied; §5g N/A. Three-dot includes AST-1137/1138 lineage vs `origin/dev`.

context_tokens≈24000
