<!-- linear-archive: AST-1260 archived 2026-08-17 -->

## Linear archive (AST-1260)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1260/tighten-claim-process-release-remove-conflicting-candidate-law  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1257 — candidate table does not have batch_id  
**Blocked by / blocks / related:** parent: AST-1257

### Description

## What this implements

Amend `astral.batch.claim-process-release` **in place** (explicit ENTITY_TYPES + pool claim + no silent carve-outs). Survey canon for statutes that conflict with candidate batch/pool parity and **remove or amend** them. Update `pattern.batch.entity-claim-process-release` (canonical_refs + solution language), CODE_RULES §2.4 wording, and `docs/features/candidate/CANDIDATE_DATA_MODEL.md` (remove “no batch primitives” / single-candidate carve-out). Archie approval on statute frontmatter. Can draft in parallel with product children; must land before parent UAT so law matches product.

## In scope

- [X] `astral.batch.claim-process-release` — amend Statement/Rationale/Examples for ENTITY_TYPES pool claim; refresh Archie `approved_at`
- [X] `pattern.batch.entity-claim-process-release` — candidate canonical_refs + pool-parity Solution; refresh `approved_at`
- [X] `docs/ASTRAL_CODE_RULES.md` §2.4 — ENTITY_TYPES / candidate pool wording
- [X] `docs/features/candidate/CANDIDATE_DATA_MODEL.md` — lock columns; remove “no batch primitives”
- [X] `orch.roles.archie-approves-statutes` — frontmatter `approved_by: Archie` + refreshed `approved_at` on statute/pattern amends
- [X] `astral.docs.features-single-file-per-ticket` — plan at `docs/features/dispatcher/ast-1260-…`
- [X] `astral.git.engineer-test-tree-ban` — no tests/bible edits

## Considered but excluded

- [X] `astral.batch.batch-id-first` / `astral.batch.batch-id-format` — product claim signatures already land in AST-1258/1259; this ticket does not reimplement helpers
- [X] `astral.standards.database-header-inventory` — AST-1258 owns inventory/schema columns
- [X] `astral.standards.debug-contract-gated` — AST-1259 owns dispatch debug path
- [X] `astral.layers.import-direction` — no `src/` edits
- [X] `astral.state.core-decides-transitions` — no state-transition changes
- [X] Product claim/dispatch code (`src/data/database.py`, `src/core/candidate.py`, `src/core/dispatcher.py`) — AST-1258 / AST-1259
- [X] New pattern or statute ids — strengthen existing batch claim pattern/statute only
- [X] Archived AST-972 plan prose under `docs/features/candidate/` — historical; do not rewrite
- [X] Non-ENTITY_TYPES pollers (`gaze_email`, meteorite mailbox shells) — stay non-claim-queue exceptions (statute Notes only)

## Acceptance criteria

- [X] 5. `astral.batch.claim-process-release` is tightened in place; conflicting candidate-processing statute text is removed or amended; pattern catalog + CODE_RULES §2.4 + `CANDIDATE_DATA_MODEL` no longer bless unlocked or non-pool candidate claim; a candidate-only unlocked path would fail statute/pattern review.

## Boundaries

Does not implement product claim/dispatch code (AST-1258 / AST-1259). Does not invent a new pattern id — strengthens existing batch claim pattern and statute.

## Notes for planning

Bang sequencing: after #2 (AST-1259). Statute amend requires Archie approval in frontmatter.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

**Publish ref:** `sub/AST-1257/AST-1260-tighten-claim-process-release-remove-conflicting-candidate-law`

### Comments

#### chuckles — 2026-08-07T19:43:29.957Z
[merge-child] blocked: missing code(AST-1260): test(AST-1260): on origin/sub/AST-1257/AST-1260-tighten-claim-process-release-remove-conflicting-candidate-law

Docs-only ticket: validate-sub-log docs-acceptance only relaxes merge-tests when a `code()`/`test()` subject contains docs-acceptance. Current tip has docs()/merge-tests()/resolve() but no `code(AST-1260):` or `test(AST-1260):` labels.

@Hedy Lamarr — add marker commits on the publish ref (e.g. `code(AST-1260): docs-acceptance — …` and `test(AST-1260): docs-acceptance — …`) and push; Chuckles will re-run merge-child.

— Chuckles

#### radia — 2026-08-07T19:41:10.577Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1260
**Publish ref:** `sub/AST-1257/AST-1260-tighten-claim-process-release-remove-conflicting-candidate-law` @ `d5b04be0`
**Overall:** CLEAN

Full active-set sweep run in-session (65 active statutes: 18 universal + 47 scoped — 5 scoped matched this docs/canon-only diff and scored, 42 scoped `not-applicable` with layer/path reasons, mapping `canon/statutes/**` / `canon/patterns/**` to the `docs` layer per the same convention Joan used at plan-rubric). Diff is `src/**`-free: `canon/statutes/astral/batch/astral.batch.claim-process-release.md`, `canon/patterns/batch/pattern.batch.entity-claim-process-release.md`, `docs/ASTRAL_CODE_RULES.md` §2.4, `docs/features/candidate/CANDIDATE_DATA_MODEL.md`, plus the plan file and Betty's docs-acceptance bible entry.

## Plan adherence

All three stages land the plan's pinned text verbatim — diffed each amended file against the exact strings Stage 1–3 specify and they match character-for-character (Statement/Rationale/Examples/Notes on the statute; `canonical_refs`/Solution shape/`When not to use` on the pattern; §2.4 sentences; `CANDIDATE_DATA_MODEL` column bullets + both inventories). Ran all 5 of the plan's own Manual checks against the publish tip and every one passes:

1. `rg "No batch primitives|not batch-processed"` on `CANDIDATE_DATA_MODEL.md` → no matches.
2. Statute Statement contains `ENTITY_TYPES` and `pool` — confirmed (`ENTITY_TYPES = ["candidate", "company", "job"]` is a real `src/utils/config.py` symbol, not invented).
3. Pattern `canonical_refs` lists `claim_candidate_batch` and `get_new_candidate_batch`.
4. Statute Statement contains the zero-row-claim-needs-no-release qualification.
5. `CANDIDATE_DATA_MODEL.md` — `batch_id`/`batch_created_at` present on both the column bullets and the `## Snake_case` → **DB columns** line.

Joan's round-2 discuss (pinned Snake_case replacement string drops the list's `- ` bullet marker) did **not** manifest — the landed line keeps `- **DB columns:** …` as the first item of the same three-bullet list; builder judgment correctly preserved the list structure the plan's literal pinned string would have broken. `orch.roles.archie-approves-statutes` — conforms: both the statute and pattern frontmatter carry `approved_by: Archie` with `approved_at: "2026-08-07"` refreshed to this ticket's landing date, no engineer name substituted. Commit separation clean: three `docs(AST-1260)` stage commits touch exactly the four planned files (one commit per stage, matching the plan's per-stage commit contract); Betty's `docs(AST-1260): test bible — docs-acceptance` / `merge-tests` commits touch only `docs/test-bible/README.md` — no `tests/`, no `src/`, no bible edits by the engineer (`astral.git.engineer-test-tree-ban`, `astral.git.betty-no-src-or-features` — both conform).

## Pattern conformance

`pattern.batch.entity-claim-process-release` — conforms (this ticket *is* the pattern amend; `canonical_refs` now list candidate's data + core helpers as peers of job, Solution shape states pool-claim parity across every `ENTITY_TYPES` claim queue).

## Findings

None.

## Frame diff

(none)

## What's solid

- The new statute Statement is scoped exactly to what AC5 requires — pool claim + `ENTITY_TYPES` + zero-row-release qualification — without picking up stray scope (no new pattern/statute id invented, no `src/**` touched, archived AST-972 docs left alone).
- Notes section explicitly carves out non-`ENTITY_TYPES` pollers (`gaze_email`) so the statute doesn't accidentally sweep in unrelated mailbox code, and separately records company's empty-batch early exit as known-conforming — both loose ends Joan's plan-rubric round flagged are closed in the landed text, not just promised in the plan.
- `CANDIDATE_DATA_MODEL.md`'s `state_history` bullet rewording ("may be null when the transition was not batch-anchored" replacing "until candidate batch claim exists") correctly stops implying batch claim doesn't exist yet, without overclaiming that every history entry carries a `batch_id`.

context_tokens≈92000

— Radia

#### betty — 2026-08-07T19:36:15.766Z
## QA test manifest (docs-acceptance)

`origin/sub/AST-1257/AST-1260-tighten-claim-process-release-remove-conflicting-candidate-law` @ `d5b04be0` (`merge-tests(AST-1260): origin/tests 1af3db4f`)

**No pytest.** Docs/canon only — verify on publish tip:

1. `canon/statutes/astral/batch/astral.batch.claim-process-release.md` — Statement has `ENTITY_TYPES` + pool + zero-row release qualification; `approved_by: Archie`; `approved_at` present.
2. `canon/patterns/batch/pattern.batch.entity-claim-process-release.md` — `canonical_refs` include `claim_candidate_batch` and `get_new_candidate_batch`; Solution states candidate pool peers; `approved_by: Archie`.
3. `docs/ASTRAL_CODE_RULES.md` §2.4 — names every `ENTITY_TYPES` claim queue including candidate (no unlocked single-ctx carve-out).
4. `docs/features/candidate/CANDIDATE_DATA_MODEL.md` — `batch_id` / `batch_created_at` on column bullets + Snake_case **DB columns**; `rg -n "No batch primitives|not batch-processed"` → no matches.

```bash
# from epic worktree at publish tip
rg -n "ENTITY_TYPES|pool|zero-row" canon/statutes/astral/batch/astral.batch.claim-process-release.md
rg -n "claim_candidate_batch|get_new_candidate_batch" canon/patterns/batch/pattern.batch.entity-claim-process-release.md
rg -n "ENTITY_TYPES|candidate" docs/ASTRAL_CODE_RULES.md
rg -n "No batch primitives|not batch-processed" docs/features/candidate/CANDIDATE_DATA_MODEL.md   # expect empty
rg -n "batch_id|batch_created_at" docs/features/candidate/CANDIDATE_DATA_MODEL.md
```

**Bible (on publish-ref):**
- `docs/test-bible/README.md` `631d8f5da4457a42b74a97518c91646f981bfbbcb04c9ac97253fcd7350890c1`

— Betty

#### joan — 2026-08-07T19:32:29.429Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1260
**Overall:** APPROVED
**Publish ref tip:** `sub/AST-1257/AST-1260-tighten-claim-process-release-remove-conflicting-candidate-law` @ `b06acd03` (Revision 1; round=1 concern was scored @ `b84bf175`, anchors against `origin/ftr/AST-1257-candidate-table-does-not-have-batch-id` @ `0e314a47`)

## Traceability

AC5→S1–S3 (S1 statute; S2 pattern + §2.4; S3 `CANDIDATE_DATA_MODEL`). S1–S3 → parent Functional scope 5 / Architectural definition ("amend in place"). No orphan stages; no unmapped AC. R5 pass.

**Considered:** 22 active statutes scored in-session (18 universal + 4 scoped considered, 43 scoped excluded), unchanged from round=1 — same four-file change set. **Notes:** `canon / statutes` and `canon / patterns` layer cells remain unrecognized by the rubric enum and are mapped to `docs`; `astral.batch.claim-process-release` is still *excluded* as a governing statute (it is the subject of the edit, not law over a docs-only change set), so the Statement-text findings are scored under R6.

## Round=1 items — both closed

**fix-now (Snake_case inventory) → resolved.** Stage 3 gains a step 2 that replaces the `## Snake_case` → **DB columns** line with a pinned string carrying `batch_id`, `batch_created_at`; the old steps 2–3 renumber cleanly to 3–4. Done-when now names *both* inventories explicitly, and new Manual check 5 asserts both column names on that line. The column ordering in the replacement (lock columns before the timestamps) matches where the column-bullet guidance puts them. `orch.pipeline.plan-is-bible` → conforms.

**discuss (company empty-batch) → resolved, and correctly.** The Statement parenthetical is now “clear the lock in `finally` (and on every early-exit path **on which rows were actually claimed** — a zero-row claim needs no release).” I checked this does the intended job in both directions: company's empty-batch early exit claims zero rows and is now conforming, while the candidate teeth are untouched — claimed rows must still clear, and unlocked single-ctx is still called out as violating in the Examples. I also looked for a gap the new wording could open and there isn't one: in `_run_unified` any non-empty claim enters the `try`/`finally`, and the only early exit is the empty-batch path, so “rows actually claimed” has no uncovered case. The Notes line recording company's empty path as known-conforming is a good belt-and-braces addition, and Manual check 4 pins the qualification so it cannot be quietly dropped at build.

## Findings

No `fix-now`.

### discuss — the pinned Snake_case replacement drops the list bullet

The live line is a bullet in a three-item list:

```
- **DB columns:** astral_candidate_id, state, …
- **candidate_data keys:** …
- **Config keys:** …
```

Stage 3 step 2 says to replace it “with exactly” a string that begins `**DB columns:**` with no leading `- `. A builder executing that literally under `plan-is-bible` turns the first list item into a paragraph and splits the remaining two into a separate list. It is one character and it does not touch the law or AC5, so it does not block — but the whole point of pinning exact text is that the pinned text is what lands.

**Recommendation:** prefix the pinned string with `- ` (or say “replace the text after the bullet”). Worth folding into the build rather than spending another discuss round on it.

### acceptable

- Carried forward from round=1 and re-checked as still true: the canon survey (no statute to retire), the Archie approval basis via the parent Architectural definition, the pattern `canonical_refs` staying job+candidate, the AST-517 archive row, and commit vocabulary / path bans.
- Self-assessment stays Scope Single-Component / Conf high / Risk Medium, and the Risk line was honestly rewritten to name the empty-batch wording as the mitigated hazard rather than leaving the old generic text.

Status → Plan Approved.

— Joan

context_tokens≈102000

#### hedy — 2026-08-07T19:29:46.206Z
[plan-discuss] round=1 reply

Plan tip: `origin/sub/AST-1257/AST-1260-tighten-claim-process-release-remove-conflicting-candidate-law` @ `b06acd03`

https://github.com/susansomerset/astral/blob/sub/AST-1257/AST-1260-tighten-claim-process-release-remove-conflicting-candidate-law/docs/features/dispatcher/ast-1260-tighten-claim-process-release-remove-conflicting-candidate-law.md

**fix-now — Snake_case DB columns:** Stage 3 step 2 now replaces the `## Snake_case` → **DB columns** line with an exact string that includes `batch_id`, `batch_created_at`. Done when covers both inventories. Manual check 5 asserts both names on that line.

**discuss — empty-batch / company clear:** Stage 1 Statement parenthetical now requires release on early-exit paths **where rows were actually claimed** — "a zero-row claim needs no release." Notes adds: company's empty-batch early exit without `clear_company_batch` is known-conforming. Candidate teeth (claimed rows must clear; unlocked single-ctx still violates) unchanged.

**Self-assessment (unchanged axes):** Scope Single-Component; Conf high; Risk Medium (empty-batch false-flag mitigated).

Status → Plan Ready.

#### joan — 2026-08-07T19:28:00.169Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1260
**Overall:** REVISE
**Publish ref tip:** `sub/AST-1257/AST-1260-tighten-claim-process-release-remove-conflicting-candidate-law` @ `b84bf175` (anchors verified against `origin/ftr/AST-1257-candidate-table-does-not-have-batch-id` @ `0e314a47`, the merged tip the plan says it surveyed)

## Traceability

AC5→S1–S3 (S1 statute; S2 pattern + §2.4; S3 `CANDIDATE_DATA_MODEL`). S1–S3 → parent Functional scope 5 / Architectural definition ("amend in place"). No orphan stages; no unmapped AC. R5 pass.

**Considered:** 22 active statutes scored in-session (18 universal + 4 scoped considered, 43 scoped excluded). **Notes (rubric § Matching algorithm step 1):** the Files Changed layer cells `canon / statutes` and `canon / patterns` are unrecognized, so I mapped both to `docs`. One consequence worth stating plainly — `astral.batch.claim-process-release` is *excluded* from the considered set (its `applies_when.paths` are `src/core/**` / `src/data/**` and this plan touches no `src/`). It is the **subject** of the change, not a governing statute for it; the governing one is `orch.roles.archie-approves-statutes` (universal, `canon/statutes/**`). Findings about the new Statement text below are therefore scored under R6, not as an R3 verdict.

## Survey — independently confirmed

I re-ran the canon survey rather than taking it on trust, and Hedy's central claim holds. Grepping `canon/**` on the merged tip for unlocked / single-ctx / no-batch / carve-out candidate language returns exactly one hit, `pattern.batch.entity-claim-process-release` “Non-entity work with no batch table”, which is a legitimate When-not-to-use bullet. **No separate statute file blesses unlocked or non-pool candidate claim**, so “do not retire any statute file” is the correct action and AC5's “conflicting statute text removed or amended” is satisfied by the in-place amend alone.

All pinned anchor strings exist verbatim on the merged tip, which matters because every stage is an exact-text edit: `CANDIDATE_DATA_MODEL.md` line 15 `No batch primitives on candidate — candidates are not batch-processed.`, its `## Candidate table (columns)` header (line 5) and `state_history` bullet with “`batch_id` may be null until candidate batch claim exists” (line 9); CODE_RULES line 157 “All batch jobs that process entities by state use batch locking.” and line 187 “Do not select by state and process without batch_id…”; the statute's `# Statement` / `## Rationale` / `## Examples` sections with **no** `## Notes` (so Stage 1 step 5's append branch is the live one); and the pattern's `## When not to use` with exactly the three bullets Stage 2 says to keep.

## Findings

### fix-now — Stage 3 leaves a second, now-false column inventory in the same file

`CANDIDATE_DATA_MODEL.md` lists the candidate columns **twice**. Stage 3 fixes the first (`## Candidate table (columns)`, lines 5–15) but never touches the second — line 188 under `## Snake_case`:

> **DB columns:** astral_candidate_id, state, state_history, first, last, full, pronouns, candidate_data, candidate_api_key, created_at, updated_at, state_changed_at.

AST-1258 landed `batch_id` and `batch_created_at`, so that line is factually wrong on the merged tip and stays wrong after Stage 3 as written. Stage 3's own **Done when** says “The candidate data-model doc lists `batch_id` / `batch_created_at`” — the steps do not deliver that, and Stage 3 step 2's “do not change … except where they contradict pool claim” does not clearly authorize the edit either, so a builder following `orch.pipeline.plan-is-bible` literally will leave the doc self-contradicting. The Manual check will not catch it: check 1 only greps for `No batch primitives|not batch-processed`.

**Recommendation:** add a Stage 3 step appending `batch_id`, `batch_created_at` to the `## Snake_case` → **DB columns** list, and a Manual check 5 asserting both names appear in that line. One line each.

### discuss — the new Statement makes the existing **company** empty-batch path a violation this epic is forbidden to fix

The proposed Statement requires “clear the lock in `finally` (**including empty-batch / early-exit paths**)” for every `ENTITY_TYPES` claim queue, naming `company` explicitly. But the empty-batch early exit in `_run_unified` returns **before** the `try`/`finally`, and only job clears there today (`if entity_type == "job" and bid: clear_job_batch(bid)`, line 537) — AST-1259 adds candidate beside it and its plan says in terms “Leave company empty-path behavior unchanged (still no clear on empty).” Parent Boundaries also keep job/company claim behavior out of scope. So on the day this lands, canon outlaws a company path no child in the epic will change, and the next `src/core/**` review has to either flag it or learn to ignore the clause — which is the failure mode this epic exists to close, pointed the other way.

A defensible reading exists (an empty claim locked zero rows, so there is no lock to release), and that is probably what Hedy means. I just want the law to say it rather than leave it to the reader.

**Recommendation:** qualify the parenthetical — e.g. release must cover every early-exit path **on which rows were actually claimed**, so a zero-row claim needs no release — or add one Notes line recording that company's empty-batch early exit is known-conforming under this Statement. Either is one sentence and keeps the candidate teeth intact.

### acceptable

- **Archie approval.** Basing the frontmatter refresh on the parent Architectural definition is sound: Archie authored it, it directs this exact in-place amend, and the proposed Statement is a faithful expansion of his own wording ("every `ENTITY_TYPES` member … must have row batch locking and pool claim parity — silent per-entity carve-outs are review defects"), including AC5's "unless Archie has an explicit approved exception statute." With `approved_by: Archie` plus a refreshed `approved_at`, `orch.roles.archie-approves-statutes` → conforms. Radia should still confirm the landed frontmatter, not just the plan's promise.
- **Pattern `canonical_refs`** gains the candidate data and core helpers but no company refs (`claim_company_batch` / `get_new_company_batch`), so the list stays job+candidate. The parent's "peers of job/company" language is about candidate's standing, and AC5 does not require company entries — fine as scoped.
- **`docs/features/candidate/ast-517-…md` line 201** still carries `| §2.4 Batch | N/A — candidate not batch-processed. |`. The plan's do-not-rewrite-archives policy covers it even though the survey table names only AST-972 archives, and it is a point-in-time rules-check row in a shipped plan. Leaving it is right.
- **Commit vocabulary and path bans:** `docs(AST-1260): …` is one of the ten named types, and "Engineer commit touching only `canon/statutes/`" is the literal conforming example in `orch.roles.pre-commit-path-bans`.

Status → Plan Discuss. One fix-now; the discuss item is a single clause.

— Joan

context_tokens≈86000

#### hedy — 2026-08-07T19:22:51.179Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1257/AST-1260-tighten-claim-process-release-remove-conflicting-candidate-law/docs/features/dispatcher/ast-1260-tighten-claim-process-release-remove-conflicting-candidate-law.md

`origin/sub/AST-1257/AST-1260-tighten-claim-process-release-remove-conflicting-candidate-law` @ `b84bf175`

**Scope:** Single-Component — canon statute + pattern + CODE_RULES §2.4 + `CANDIDATE_DATA_MODEL`; no `src/`.

**Conf:** high — survey found no separate conflicting statute to retire; Statement/Solution/column bullets pinned; AST-1258/1259 already expose cited symbols on ftr.

**Risk:** Medium — under-broad law lets unlocked candidate claim pass review again; over-broad language mitigated by Notes for non-ENTITY_TYPES pollers.

Survey baked into plan: amend `astral.batch.claim-process-release` + pattern + §2.4 + data-model; do not invent new ids; do not rewrite AST-972 archives. Archie frontmatter refresh uses parent Architectural definition as the amend approval + `approved_at` on each amend commit.

---

# AST-1260 — Tighten claim-process-release; remove conflicting candidate law

**Linear:** [AST-1260](https://linear.app/astralcareermatch/issue/AST-1260/tighten-claim-process-release-remove-conflicting-candidate-law)
**Parent:** [AST-1257](https://linear.app/astralcareermatch/issue/AST-1257/candidate-table-does-not-have-batch-id) — candidate table does not have batch_id
**Publish ref:** `origin/sub/AST-1257/AST-1260-tighten-claim-process-release-remove-conflicting-candidate-law`

Amend `astral.batch.claim-process-release` **in place** so every `ENTITY_TYPES` dispatch claim queue requires pool claim → process → release (no silent carve-outs). Align `pattern.batch.entity-claim-process-release` (candidate helpers as peers of job/company), CODE_RULES §2.4 wording, and `CANDIDATE_DATA_MODEL.md` (remove “no batch primitives” / single-candidate carve-out). Docs/canon only — product claim/dispatch is AST-1258 / AST-1259.

## UAT fitness

- **AC restored:** Parent AC 5 — “`astral.batch.claim-process-release` is tightened in place; conflicting candidate-processing statute text is removed or amended; pattern catalog + CODE_RULES §2.4 + `CANDIDATE_DATA_MODEL` no longer bless unlocked or non-pool candidate claim; a candidate-only unlocked path would fail statute/pattern review.”
- **Correct outcome:** Review and plan validation treat unlocked / single-ctx candidate claim as a statute/pattern defect; law and data-model docs describe candidate pool claim the same way as job/company.
- **Sibling check:** AST-1258 (schema + `claim_candidate_batch` / get / clear + pool Avail) and AST-1259 (`get_new_candidate_batch` / dispatcher finally-clear) already landed on `origin/ftr/AST-1257-candidate-table-does-not-have-batch-id`. This ticket does not re-implement them — only makes law/docs match that product. Verified by reading those plans + tip symbols before Plan Ready.
- **Not sufficient:** Deleting the “No batch primitives” sentence alone, or refreshing `approved_at` without tightening the Statement / pattern solution language, is **not** done.
- **Wrong fix rejected:** Inventing a new pattern/statute id, or a candidate-only exception statute that re-blesses unlocked claim — parent and child Boundaries forbid that. Softening only Examples while leaving a vague Statement would still let unlocked candidate paths pass review.

## Survey findings (baked into this plan — builder does not re-decide)

Search on tip after merge of `origin/ftr/AST-1257-candidate-table-does-not-have-batch-id` (`rg` over `canon/statutes/**`, `canon/patterns/**` for unlocked / no-batch / single-candidate / carve-out candidate claim language):

| Location | Finding | Action this ticket |
|----------|---------|-------------------|
| `canon/statutes/astral/batch/astral.batch.claim-process-release.md` | Statement too weak — does not name `ENTITY_TYPES`, pool claim, or ban silent carve-outs | **Amend in place** (Stage 1) |
| Other active statutes under `canon/statutes/**` | No separate statute file blesses unlocked / non-pool candidate claim | **Do not retire** any statute file |
| `canon/patterns/batch/pattern.batch.entity-claim-process-release.md` | `canonical_refs` are job-only; Solution shape omits candidate pool peers | **Amend in place** (Stage 2) |
| `docs/ASTRAL_CODE_RULES.md` §2.4 | Says “all entity types” but does not call out candidate / `ENTITY_TYPES` claim-queue duty; company-only narrative | **Amend wording** (Stage 2) |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Line “No batch primitives on candidate — candidates are not batch-processed.” + missing lock columns | **Amend** (Stage 3) |
| Archived AST-972 feature docs under `docs/features/candidate/` | Historical decisions (single-ctx / no claim helpers) — overturned by AST-1257 | **Do not rewrite** archives |

⚠️ **Decision — Archie approval:** Parent AST-1257 Architectural definition already names this in-place amend and cites `orch.roles.archie-approves-statutes`. On each statute/pattern amend commit, set `approved_by: Archie` and refresh `approved_at` to that commit’s UTC date (`YYYY-MM-DD`). Do **not** set `approved_by` to an engineer name. If Archie rejects the exact Statement/Solution text at Plan Discuss / Plan Ready, stop and revise — do not invent alternate law.

⚠️ **Decision — no new ids:** Strengthen existing statute id `astral.batch.claim-process-release` and pattern id `pattern.batch.entity-claim-process-release`. Do not create a candidate-only pattern or exception statute.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `canon/statutes/astral/batch/astral.batch.claim-process-release.md` | Tighten Statement / Rationale / Examples; refresh `approved_at` | canon / statutes |
| `canon/patterns/batch/pattern.batch.entity-claim-process-release.md` | Add candidate `canonical_refs`; pool-parity Solution language; refresh `approved_at` | canon / patterns |
| `docs/ASTRAL_CODE_RULES.md` | §2.4 wording: explicit `ENTITY_TYPES` claim-queue + candidate pool parity | docs |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Remove “no batch primitives”; document `batch_id` / `batch_created_at` | docs |

No `src/**`, no `tests/**`, no bible, no new statute/pattern files, no `HARVEST.md` / SCHEMA / AUTHORING rewrites.

## Stage 1: Amend `astral.batch.claim-process-release`

**Done when:** The statute Statement requires pool claim → process → release for every `ENTITY_TYPES` dispatch claim queue (candidate included), bans silent carve-outs, and Examples flag unlocked single-ctx candidate claim as violating. Frontmatter keeps `id` / path / `status: active` / `approved_by: Archie` with refreshed `approved_at`.

1. Edit **only** `canon/statutes/astral/batch/astral.batch.claim-process-release.md`. Keep all SCHEMA frontmatter keys; do not change `id`, `tier`, `checkable`, `applies_when`, `source_docs`, or supersession fields. Set `approved_by: Archie` and `approved_at: "<UTC date of this commit YYYY-MM-DD>"`.
2. Replace `# Statement` body with exactly:

   > Every `ENTITY_TYPES` member used as a dispatch claim queue (`candidate`, `company`, `job`) must use claim → process → release with a row `batch_id` lock and **pool** claim parity: claim up to `limit` unclaimed rows in the claimable state set under one `batch_id`, process only those rows, and clear the lock in `finally` (and on every early-exit path **on which rows were actually claimed** — a zero-row claim needs no release). Do not select by state or single-ctx and process without batch locking. Silent per-entity carve-outs that skip pool claim for any `ENTITY_TYPES` claim queue are review defects unless Archie has an explicit approved exception statute.

3. Replace `## Rationale` body with exactly:

   > Batch locking is the concurrency and audit spine for dispatch. Candidate is an `ENTITY_TYPES` claim queue peer of job and company — not a single-row unlocked special case.

4. Replace `## Examples` with exactly:

   ```markdown
   ## Examples

   ### Conforming

   - Dispatcher claims candidates via `get_new_candidate_batch` / `claim_candidate_batch`, processes claimed rows, then `clear_candidate_batch` in `finally` (same shape as job/company).
   - Job or company claim → process → `clear_*_batch` in `finally`.

   ### Violating

   - A candidate dispatch branch sets `entities = [ctx]` when the ctx state is claimable and never locks `candidate.batch_id`.
   - A runner `SELECT`s jobs (or candidates) by state and updates them with no claim/clear.
   - Docs or statutes bless a candidate-only unlocked / non-pool claim path.
   ```

5. Optional `## Notes` — if present, replace with exactly this; if absent, append after Examples:

   > Non-`ENTITY_TYPES` pollers (e.g. `gaze_email`, meteorite mailbox shells) are not dispatch claim queues and stay outside this statute’s claim-lock duty. Do not use that exception to skip candidate pool claim.
   >
   > A zero-row claim locks no rows; company's empty-batch early exit without `clear_company_batch` is known-conforming under this Statement.

6. Do **not** create, retire, or rename any other statute file in this stage.

**Commit message:** `docs(AST-1260): tighten astral.batch.claim-process-release for ENTITY_TYPES pool claim`

## Stage 2: Pattern catalog + CODE_RULES §2.4

**Done when:** Pattern `canonical_refs` include candidate claim/get/clear (data) and core wrappers; Solution shape states candidate is a pool-claim peer of job/company; §2.4 prose explicitly requires the same for every `ENTITY_TYPES` claim queue and no longer reads as company-only law.

1. Edit `canon/patterns/batch/pattern.batch.entity-claim-process-release.md`:
   - Keep `id`, `status: approved`, `proposed_in`, `related_statutes`, supersession fields.
   - Set `approved_by: Archie` and refresh `approved_at` to this commit’s UTC date.
   - Replace `canonical_refs` with exactly this list (YAML):

     ```yaml
     canonical_refs:
       - path: src/data/database.py
         symbol: claim_job_batch
       - path: src/data/database.py
         symbol: clear_job_batch
       - path: src/data/database.py
         symbol: claim_candidate_batch
       - path: src/data/database.py
         symbol: get_candidate_batch
       - path: src/data/database.py
         symbol: clear_candidate_batch
       - path: src/core/candidate.py
         symbol: get_new_candidate_batch
       - path: src/core/candidate.py
         symbol: clear_candidate_batch
       - path: docs/ASTRAL_CODE_RULES.md
         symbol: "§2.4"
     ```

   - Replace `# Solution shape` body with exactly:

     > Claim a batch with a `batch_id` (first parameter on claim/get/clear helpers), process only claimed rows, and clear the batch in `finally` (or equivalent release). Pool claim applies to every `ENTITY_TYPES` dispatch claim queue — candidate helpers (`claim_candidate_batch` / `get_new_candidate_batch` / `clear_candidate_batch`) are first-class peers of job/company, not a single-ctx unlocked shape. Core decides transitions; data owns claim/clear. Point at `canonical_refs` — do not paste large code into this catalog entry.

   - Keep `# Problem` unchanged unless it still implies job-only scope; if so, replace Problem with:

     > Dispatch and entity runners need a concurrency-safe way to select work across an unclaimed pool, process it, and release the claim without racing other workers or losing auditability.

   - Under `## When not to use`, keep the three existing bullets and ensure this bullet is present (add if missing; do not duplicate):

     > Non-`ENTITY_TYPES` mailbox / null-entity pollers (e.g. `gaze_email`) that are not dispatch claim queues.

2. In `docs/ASTRAL_CODE_RULES.md` §2.4 (`### 2.4 Batch Processing Pattern`):
   - After the sentence “All batch jobs that process entities by state use batch locking.” insert (if not already present) exactly:

     > Every `ENTITY_TYPES` member used as a dispatch claim queue (`candidate`, `company`, `job`) uses the same pool claim → process → release shape. Candidate is not exempt: no unlocked single-ctx claim path, no empty release stub.

   - Keep the existing `batch_id` format paragraph, claim → process → release numbered list, Data layer / Core signature lines, and dispatcher narrative/pseudocode (company example may remain as illustration).
   - Replace the closing sentence “Do not select by state and process without batch_id. Use claim / get / clear and batch_id-first order consistently for all entity types.” with exactly:

     > Do not select by state (or single-ctx) and process without batch_id. Use claim / get / clear and batch_id-first order consistently for every `ENTITY_TYPES` claim queue, including candidate.

3. Do **not** edit other CODE_RULES sections, `HARVEST.md`, or pattern SCHEMA/AUTHORING/README.

**Commit message:** `docs(AST-1260): candidate pool peers in claim pattern and §2.4`

## Stage 3: `CANDIDATE_DATA_MODEL` honesty

**Done when:** Both column inventories in the candidate data-model doc list `batch_id` / `batch_created_at` (`## Candidate table (columns)` and `## Snake_case` → **DB columns**); the doc no longer says candidates lack batch primitives or are not batch-processed; `state_history[].batch_id` does not contradict row locks.

1. In `docs/features/candidate/CANDIDATE_DATA_MODEL.md`, under `## Candidate table (columns)`:
   - **Delete** the standalone line: `No batch primitives on candidate — candidates are not batch-processed.`
   - After the identity / `candidate_data` / `candidate_api_key` bullets (and with the timestamp bullets), ensure these two column bullets exist (add if missing; do not duplicate):

     - **batch_id** — Golden-ticket lock for dispatch claim → process → release (AST-1258). Null or empty means unclaimed. Same pool-claim role as job/company `batch_id`.
     - **batch_created_at** — Timestamp set when the row is claimed; cleared with `batch_id` on release.

   - Update the **state_history** bullet so it does **not** say batch claim “does not exist.” Keep the field shape `{from_state, to_state, timestamp, batch_id}`. Replace any “until candidate batch claim exists” wording with: `batch_id` on a history entry may be null when the transition was not batch-anchored; row lock columns are separate (claim/clear).

2. Under `## Snake_case`, replace the **DB columns:** line with exactly:

   `**DB columns:** astral_candidate_id, state, state_history, first, last, full, pronouns, candidate_data, candidate_api_key, batch_id, batch_created_at, created_at, updated_at, state_changed_at.`

3. Do **not** change token tables, library section layouts, or company FK notes except where they contradict pool claim (leave `company.candidate_id` batch-filter note as-is — that is company scoping, not candidate row locks).

4. Do **not** edit archived AST-972 plan markdown under `docs/features/candidate/`.

**Commit message:** `docs(AST-1260): candidate data model batch lock columns`

## Manual check (no product commit)

After Stage 3, from the epic worktree tip:

1. Confirm `rg -n "No batch primitives|not batch-processed" docs/features/candidate/CANDIDATE_DATA_MODEL.md` returns no matches.
2. Confirm statute Statement contains `ENTITY_TYPES` and `pool`.
3. Confirm pattern `canonical_refs` lists `claim_candidate_batch` and `get_new_candidate_batch`.
4. Confirm statute Statement contains `zero-row claim needs no release` (or equivalent empty-claim release qualification).
5. Confirm `rg -n "batch_id|batch_created_at" docs/features/candidate/CANDIDATE_DATA_MODEL.md` matches both names on the `## Snake_case` → **DB columns** line (and on the column bullets).
6. Do **not** run or edit pytest / bible.

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1257/AST-1260-tighten-claim-process-release-remove-conflicting-candidate-law`.
- Do not add files outside **Files Changed**.
- Do not implement or revise product claim/dispatch code (AST-1258 / AST-1259).
- On ambiguity or drift: stop and comment on **parent** AST-1257 with the 🛑 Stage N blocked template.

## Self-Assessment

**Scope:** Single-Component — canon statute + pattern + two docs files; no `src/` product change.

**Conf:** high — survey found no separate statute to retire; exact Statement / Solution / column bullets are pinned; siblings already expose the symbols this law cites.

**Risk:** Medium — under-broad language would let unlocked candidate paths pass review again; over-broad empty-batch wording mitigated by zero-row release qualification + Notes (company empty-path known-conforming).

## Revisions

**Revision 1 — 2026-08-07**  
Driven by: Joan `[plan-discuss] round=1 concern` (REVISE @ `b84bf175`)  
Changes: (fix-now) Stage 3 updates `## Snake_case` → **DB columns** to include `batch_id`, `batch_created_at`; Manual check 5 asserts both names on that line. (discuss) Stage 1 Statement qualifies release to early-exit paths where rows were actually claimed (zero-row needs no release); Notes records company's empty-batch early exit as known-conforming.

## Rules check (plan vs ASTRAL_CODE_RULES)

| Rule | Plan stance |
|------|-------------|
| §2.4 claim-process-release / batch-id-first / batch-id-format | This ticket amends the statute + §2.4 prose; does not reimplement claim SQL |
| `orch.roles.archie-approves-statutes` | Amend keeps `approved_by: Archie`; refresh `approved_at` per stage commit |
| `astral.docs.features-single-file-per-ticket` | Plan lives at this path only |
| `astral.git.engineer-test-tree-ban` / Betty owns tests | No `tests/` or bible edits |
| §3.3 import direction | N/A — docs/canon only |
| Out of scope | `src/data/database.py`, `src/core/dispatcher.py`, `src/core/candidate.py` product logic — siblings |

## Review (build stub)

**Publish ref:** `origin/sub/AST-1257/AST-1260-tighten-claim-process-release-remove-conflicting-candidate-law`
**Tip:** `6ae865c8`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `2ab2c564` | Tighten `astral.batch.claim-process-release` (ENTITY_TYPES pool; zero-row release note) |
| 2 | `33d376ff` | Candidate peers in claim pattern `canonical_refs` + CODE_RULES §2.4 |
| 3 | `6ae865c8` | `CANDIDATE_DATA_MODEL` lock columns + Snake_case inventory |

## Radia review — [code-rubric] revision=1

**Publish ref:** `sub/AST-1257/AST-1260-tighten-claim-process-release-remove-conflicting-candidate-law` @ `d5b04be0`
**Overall:** CLEAN

Full active-set sweep run in-session (65 active statutes: 18 universal + 47 scoped — 5 scoped matched this docs/canon-only diff, 42 `not-applicable`, mapping `canon/statutes/**` / `canon/patterns/**` to the `docs` layer per Joan's plan-rubric convention).

**Plan adherence:** All three stages land the plan's pinned text verbatim — diffed every amended file against the exact strings Stage 1–3 specify and they match character-for-character. All 5 of the plan's own Manual checks pass against the publish tip. Joan's round-2 discuss (pinned Snake_case string drops the list's `- ` bullet marker) did not manifest — the landed line keeps the bullet, list structure intact. `orch.roles.archie-approves-statutes` conforms: both statute and pattern frontmatter carry `approved_by: Archie` with `approved_at: "2026-08-07"`. Commit separation clean — three per-stage `docs(AST-1260)` commits touch exactly the four planned files; Betty's docs-acceptance/`merge-tests` commits touch only `docs/test-bible/README.md`.

**Pattern conformance:** `pattern.batch.entity-claim-process-release` — conforms.

**Findings:** None.

**What's solid:** Notes section carves out non-`ENTITY_TYPES` pollers and records company's empty-batch early exit as known-conforming — both loose ends from Joan's plan-rubric round are closed in the landed text. `CANDIDATE_DATA_MODEL.md`'s `state_history` rewording stops implying batch claim doesn't exist without overclaiming every history entry carries a `batch_id`.

context_tokens≈92000

— Radia

## Resolution

**Date:** 2026-08-07  
**Tip before resolve:** `d53331ca` (Radia `docs(AST-1260): Radia review — clean`)

| Finding | Action |
|---------|--------|
| None (Overall CLEAN) | No product or plan change required. |

**fix-now:** none.

