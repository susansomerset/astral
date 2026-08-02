# AST-1137 — Candidate from-block text + contact defaults

**Linear:** https://linear.app/astralcareermatch/issue/AST-1137/candidate-from-block-text-contact-defaults-cover-letter-header-is  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1124/cover-letter-header-is-incorrect  
**Publish ref:** `sub/AST-1124/AST-1137-candidate-from-block-text-contact-defaults`

Owns the candidate-controlled cover from-block: config field contract, persist + edit on Candidate Profile beside cover signature fields, and a shared resolve helper that returns custom text or the default `Name • City, ST` / `email • phone` composition when unset. Does **not** change job Print Cover Letter HTML emit or session Admin Cover Letter golden CSS (siblings AST-1138 / AST-1139 consume this contract).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `cover_letter_from_block` to `CANDIDATE_LIBRARY_CONFIG["contact_keys"]`; add `COVER_FROM_BLOCK_CONFIG` (field path, separators, contact segment paths, name source); add Candidate Profile textarea beside Cover Letter Signature; optional `TOKEN_SOURCES` entry only if an existing cover token map already documents sibling keys — **do not** invent a new resolve_tokens surface unless a current consumer requires it (none in this ticket). | utils |
| `src/core/candidate.py` | Add `resolve_cover_from_block(candidate: dict, *, debug: bool = False) -> dict` returning `{"text": str, "source": "candidate"\|"default"}` using `COVER_FROM_BLOCK_CONFIG` + name columns + `contact`. Optional Style D index/detail when `debug=True` (found custom vs recorded default). No builder / HTML emit. | core |
| `src/ui/frontend/src/pages/CandidateProfile.tsx` | No custom panel required — config-driven textarea via existing profile field renderer (same path as `contact.cover_letter_signature`). Touch only if the page hardcodes a field allowlist that would hide the new key; otherwise leave unchanged. | ui |

**Out of files (siblings):** `src/core/builder.py` job/session cover HTML, `AdminSessionCoverLetter.tsx`, job cover CSS golden — AST-1138 / AST-1139.

## Stage 1: Config contract

**Done when:** `COVER_FROM_BLOCK_CONFIG` and library/`UI_CONFIG` profile field declare the from-block key and composition rules; no business logic yet.

1. In `src/utils/config.py`, add `cover_letter_from_block` to `CANDIDATE_LIBRARY_CONFIG["contact_keys"]` (after `cover_letter_signature_image`, before `title_patterns`).
2. In `src/utils/config.py`, add module-level `COVER_FROM_BLOCK_CONFIG` (near `CANDIDATE_LIBRARY_CONFIG` / cover signature config) with exactly these keys:
   - `"contact_key": "cover_letter_from_block"`
   - `"segment_separator": " • "` (bullet with surrounding spaces, matching parent brief)
   - `"line_separator": "\n"`
   - `"name_column": "full"` — primary display name; when empty after strip, builder of the default line uses `recompute_full_name(first, last)` from name columns (same join as library)
   - `"line_1_contact_paths": ("location",)` — after name, join non-empty stripped segments with `segment_separator`
   - `"line_2_contact_paths": ("contact_email", "phone")` — join non-empty stripped segments with `segment_separator`
   - `"sources": ("candidate", "default")` — allowed `source` values returned by resolve (no hardcoded sets in core)
3. In `UI_CONFIG["detail"]["profile"]`, in the existing **"Cover Letter Signature"** group (immediately before or after the `contact.cover_letter_signature` textarea field), add:
   ```python
   {
       "key": "contact.cover_letter_from_block",
       "label": "Cover letter from-block",
       "type": "textarea",
   }
   ```
   Do **not** mark required. Empty / whitespace = unset (defaults apply at resolve time).
4. Do **not** add `cover_letter_from_block` to `TOPIC_MENU_GEN_CONFIG["packet_contact_keys"]` unless that tuple already lists signature keys (it does not today) — keep Estelle packet scope unchanged.
5. Do **not** change `BUILD_CONFIG["session_cover_letter"]` required `from_block` (session form field stays AST-1139).

⚠️ **Decision:** Field key is `contact.cover_letter_from_block` (not bare `from_block`) so it sits beside `cover_letter_signature*` and cannot be confused with session Admin `from_block` payload keys.

## Stage 2: Resolve helper (core)

**Done when:** `resolve_cover_from_block` returns custom text or default two-line composition; empty segments/lines omitted; `source` is always one of `COVER_FROM_BLOCK_CONFIG["sources"]`.

1. In `src/core/candidate.py`, after `recompute_full_name` (public section), add:

   ```python
   def resolve_cover_from_block(candidate: dict, *, debug: bool = False) -> dict:
       """Return cover from-block text + source for emit consumers (AST-1137).

       Returns ``{"text": str, "source": "candidate"|"default"}``.
       Custom wins when ``contact.cover_letter_from_block`` strips non-empty;
       otherwise compose defaults from name + contact per COVER_FROM_BLOCK_CONFIG.
       """
   ```

2. Implementation rules (literal):
   - Import `COVER_FROM_BLOCK_CONFIG` from `src.utils.config` (add to existing config import block).
   - Read `contact = (candidate.get("candidate_data") or {}).get("contact")` — if not a dict, treat as `{}`. Also accept a pre-built token view: if `candidate` already has top-level `"contact"` dict and no `"candidate_data"`, use that contact + top-level `first`/`last`/`full` (same shape as `build_candidate_token_view` output) so AST-1138 can pass either a DB row or a token view without a second adapter.
   - Custom path: `raw = contact.get(COVER_FROM_BLOCK_CONFIG["contact_key"])`; if `isinstance(raw, str)` and `raw.strip()` → return `{"text": raw.strip(), "source": "candidate"}` (strip outer whitespace only; preserve internal newlines).
   - Default path:
     - Name: `full = str(candidate.get("full") or "").strip()`; if empty, `full = recompute_full_name(str(candidate.get("first") or ""), str(candidate.get("last") or ""))`.
     - Build line 1: start with `[full]` if non-empty, then for each path in `line_1_contact_paths` append `str(contact.get(path) or "").strip()` when non-empty; join with `segment_separator`.
     - Build line 2: for each path in `line_2_contact_paths` append stripped non-empty values; join with `segment_separator`.
     - Join non-empty lines with `line_separator`.
     - Return `{"text": composed, "source": "default"}` (composed may be `""` if all contact/name empty).
   - `source` must be taken from / validated against `COVER_FROM_BLOCK_CONFIG["sources"]` (e.g. assign literals that appear in that tuple — do not invent a third source string).
3. When `debug=True`, emit one Style D index header (`func="candidate.resolve_cover_from_block"`, `identifier` = `candidate.get("astral_candidate_id")` or `candidate.get("_astral_candidate_id")` or `""`) with outcome `success — from_block {source}`, then `|` detail lines: `source=…`, `text_chars=N`, and for default path which line segments were non-empty (`line1_segments=…`, `line2_segments=…`). Use existing `logger` / `debug_index` / `debug_detail` patterns already in this module.
4. Do **not** call builder, do **not** write HTML, do **not** mutate `contact`.

⚠️ **Decision:** Resolve lives in `candidate.py` (not `builder.py`) so job/session emit siblings import one contract without pulling cover HTML into the candidate library layer.

## Stage 3: Profile edit path (UI)

**Done when:** Candidate Profile shows the from-block textarea and `PUT /api/candidates/<id>/data` persists `contact.cover_letter_from_block` via existing merge save (no new endpoint).

1. Confirm `CandidateProfile.tsx` renders `UI_CONFIG` profile fields generically (including textareas under `contact.*`). If it does, **no frontend code change** — Stage 1 config is sufficient.
2. If the page has a hardcoded skip-list / custom panel map that would omit unknown keys, extend it only as needed so `contact.cover_letter_from_block` renders as a normal textarea (no custom panel like signature image).
3. API: no new validation in `api_candidate.py` for this field (plain optional string). Do **not** add JPEG-style validation. Existing `save_candidate_data` merge already persists arbitrary contact keys.
4. Manual check (builder notes in Linear comment is enough; no product test tree edits): save a non-empty from-block → GET candidate shows it under `candidate_data.contact.cover_letter_from_block`; clear to empty → resolve returns `source=default` with composed lines from name/email/phone/location.

## Contract for siblings (non-goals for this ticket)

AST-1138 / AST-1139 **must** call `resolve_cover_from_block` (or equivalent import) when filling SomersetCover `fromBlock` / empty session from-block defaults. This ticket only guarantees the field + helper. Print Cover Letter AC 2–3 on the parent are satisfied when those siblings consume `text` / `source`.

## Self-Assessment

**Scope:** `Single-Component` — utils config + one core resolve helper + config-driven profile field; no builder/HTML emit.

**Conf:** `high` — mirrors `cover_letter_signature` profile + library key pattern; composition rules are fully specified in config.

**Risk:** `low` — additive optional contact field; empty default is backward-compatible; job/session render unchanged until siblings wire the helper.

## Code Rules check

- §1.1 in-scope-only: no job/session HTML, no AST-1123 token work.
- §1.4 / `no-hardcoded-sets`: separators and contact paths live in `COVER_FROM_BLOCK_CONFIG`.
- §2.1 config source of truth: field key + UI label in config.
- §3.2 / §3.3: UI stays config-driven; core imports utils only; ui does not grow business composition logic.
- §3.2 ui-config-driven: profile textarea from `UI_CONFIG`, not a React-only field.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1124/AST-1137-candidate-from-block-text-contact-defaults`

| Stage | Summary |
|-------|---------|
| 1 | `COVER_FROM_BLOCK_CONFIG` + `contact.cover_letter_from_block` library/UI field |
| 2 | `resolve_cover_from_block` — custom text or `Name • City, ST` / `email • phone` defaults |
| 3 | Profile: config-driven textarea (no `CandidateProfile.tsx` change) |

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1137
**Publish ref:** `4917e54b1d2de7ac8bd291c66d2229b38c40afd1` (`origin/sub/AST-1124/AST-1137-candidate-from-block-text-contact-defaults`)
**Overall:** FIX-NOW

### What's solid

- Stages 1–3 match the plan: `COVER_FROM_BLOCK_CONFIG`, library contact key, DATA_SHAPES profile textarea beside signature, `resolve_cover_from_block` with custom-vs-default + omit-empty segments/lines.
- Boundaries held: no builder/HTML emit, no session golden CSS, no frontend panel invent.
- Config drives separators, contact paths, and source labels; core imports utils only.
- One `merge-tests(AST-1137)` pins Betty's tip; engineer commits stay off the test tree.

### Issues

**fix-now:** `astral.standards.debug-contract-gated` — `resolve_cover_from_block` calls `logger.debug_index` / `debug_detail` under `if debug:` but never `logger.set_debug_flag(debug)`. Module logger defaults `_debug_flag=False`, so Style D helpers early-return even when the caller passes `debug=True`. Sibling emit paths (AST-1138/1139) will get silent debug. Fix: `logger.set_debug_flag(debug)` at function entry (same pattern as `save_candidate_data` / `get_candidate_id_for_query` in this module). Location: `src/core/candidate.py` `resolve_cover_from_block`.

**discuss (C4 straggler):** Joan excluded `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, and `astral.debug.spikes-under-debug-dir` at plan time; three-dot diff puts them in-scope. Sweep scores all three **conforms** (single feature file; Betty-owned test/bible; plan doc not a spike dump).

**advisory:** `COVER_FROM_BLOCK_CONFIG["name_column"]` is declared but resolve hardcodes `candidate.get("full")` per plan Stage 2 literal. Behavior matches AC; consider reading `name_column` later for true config-source symmetry.

### Recommended actions

1. Ada: add `logger.set_debug_flag(debug)` at the top of `resolve_cover_from_block` (resolve-child).
2. Optional: use `COVER_FROM_BLOCK_CONFIG["name_column"]` instead of literal `"full"`.

### Pattern conformance

Cited from ticket/plan: `pattern.config.config-block` — conforms; `pattern.ui.admin-endpoint` — conforms (existing PUT …/data; no new route); `astral.config.config-source-of-truth` / `astral.layers.ui-config-driven-business-logic` / `astral.standards.no-hardcoded-sets` / `astral.standards.in-scope-only` / `astral.layers.import-direction` — covered in statutes table.

### Plan adherence

Diff footprint matches Self-Assessment Single-Component (utils config + one core helper + config-driven profile field). No builder/HTML smuggle from AST-1138/1139. Plan Stage 2 debug steps followed except missing `set_debug_flag` (above).

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | conforms | no graded agent_task / confidence path |
| astral.agent.do-task-delegation | scoped | conforms | no do_task changes |
| astral.agent.grade-vector-validation | scoped | conforms | no graded tasks |
| astral.batch.batch-id-first | scoped | conforms | no batch claim APIs |
| astral.batch.batch-id-format | scoped | conforms | no batch_id generation |
| astral.batch.claim-process-release | scoped | conforms | no batch processing |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | no agent_data RESPONSE writes |
| astral.config.config-source-of-truth | scoped | conforms | COVER_FROM_BLOCK_CONFIG + library/UI field; composition from config |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | no scoring floors |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no secrets/env values |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths match none of ['artifacts/**', 'scripts/spikes/**'] |
| astral.debug.spikes-under-debug-dir | scoped | conforms | feature plan under docs/features/; not a spike dump |
| astral.dispatch.run-next-is-chain-authority | scoped | conforms | no run_next edits |
| astral.dispatch.seed-auto-false | scoped | conforms | no dispatch_task seed rows |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single docs/features/artifacts/ast-1137-….md |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits touch tests/bible only; engineer owns src/features |
| astral.git.engineer-test-tree-ban | scoped | conforms | test-tree changes on Betty test/merge-tests SHAs only |
| astral.layers.core-vs-external-bright-line | scoped | conforms | no external I/O; resolve in core |
| astral.layers.import-direction | scoped | conforms | core→utils only; no layer inversion |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers ['scripts'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | profile textarea via DATA_SHAPES; composition in core |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | no coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | no consult/render_verdict |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers ['ui'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.seed.agent-tables-in-repo-json | scoped | conforms | no seed JSON changes |
| astral.seed.archie-catalog-wins | scoped | conforms | no catalog seed |
| astral.seed.boot-only-not-hot-path | scoped | conforms | no seed boot path |
| astral.seed.define-approved | scoped | conforms | no seed define |
| astral.seed.operator-rows-stay-deleted | scoped | conforms | no operator seed rows |
| astral.seed.other-via-coverage-join | scoped | conforms | no seed coverage join |
| astral.standards.data-raises-caller-logs | scoped | conforms | no data-layer product changes |
| astral.standards.database-header-inventory | scoped | not-applicable | layers ['data'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.standards.debug-contract-gated | scoped | violates | resolve_cover_from_block gates with if debug but never set_debug_flag — Style D no-ops |
| astral.standards.dry-and-focused-functions | scoped | conforms | one focused resolve helper |
| astral.standards.in-scope-only | scoped | conforms | no builder/HTML/session emit; siblings own Print |
| astral.standards.logging-via-utils | scoped | conforms | uses module get_logger / debug helpers |
| astral.standards.names-not-ticket-ids | scoped | conforms | API name resolve_cover_from_block; ticket only in docstring |
| astral.standards.no-cross-contamination | scoped | conforms | candidate field+resolve only; no resume header mix-in |
| astral.standards.no-hardcoded-sets | scoped | conforms | separators/paths/sources from COVER_FROM_BLOCK_CONFIG |
| astral.standards.public-then-helpers | scoped | conforms | public resolve after recompute_full_name |
| astral.standards.utils-data-late-import-only | scoped | conforms | config.py add is literals only; no utils→data |
| astral.state.core-decides-transitions | scoped | conforms | no candidate state transitions |
| astral.state.job-prior-states-enforced | scoped | conforms | no job state work |
| astral.state.no-daisy-chain-in-run | scoped | conforms | no dispatch run chaining |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers ['ui'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.ui.naming-conventions | scoped | not-applicable | layers ['ui'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.ui.single-gunicorn-worker | scoped | conforms | config touch unrelated to gunicorn workers |
| orch.git.betty-merge-tests-one-sha | universal | conforms | one merge-tests(AST-1137) @ 4917e54b pinning tests 494d78b2 |
| orch.git.commit-vocabulary | universal | conforms | docs/code/test/merge-tests vocabulary on sub |
| orch.git.flow-direction-inviolable | universal | conforms | publish on origin/sub/AST-1124/AST-1137-… |
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
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee remains Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada stays assignee through Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | no banned-path product edits |

## Notes

- no plan-rubric verdict attachment missing — Joan APPROVED attached; stragglers noted above.
- §5f applied (debug= surface); §5g N/A (no LLM external).
- Three-dot vs `origin/dev` also includes unrelated Betty corpus from `merge-tests` (dispatcher/gazer/inbox/etc.); product surface for this ticket is `candidate.py` + `config.py` + plan/tests named above.

context_tokens≈22000
