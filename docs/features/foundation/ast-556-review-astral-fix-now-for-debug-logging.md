<!-- linear-archive: AST-556 archived 2026-06-15 -->

## Linear archive (AST-556)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-556/review-astral-fix-now-for-debug-logging-improve-quality-of-debug  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** radia  
**Priority / estimate:** None / —  
**Parent:** AST-538 — Improve Quality of Debug Logging  
**Blocked by / blocks / related:** parent: AST-538

### Description

## What this implements

Update review-astral skill: insufficient debug on touched debug= surfaces is fix-now.

## Acceptance criteria

6 from parent.

## Boundaries

Doc/skill only.

## Git branch (authoritative)

Per orientation-astral: parent `ftr/ast-538-improve-quality-of-debug-logging`, child `sub/AST-538/<child-id>-<slug>`.

### Comments

#### radia — 2026-06-03T03:23:06.792Z
`origin/sub/AST-538/AST-556-review-astral-debug-fix-now` @ `7cc02fe1` · §9a clean · ftr dry-run clean (publish rebased on `origin/ftr/ast-538`).

#### radia — 2026-06-03T03:18:40.015Z
**Diff:** `origin/dev...origin/sub/AST-538/AST-556-review-astral-debug-fix-now` @ `3682194d` (feat `bf87eb93` + Betty bible rows + review doc).

**Plan fidelity (AST-538 AC 6):** Global `review-astral` **§5f** + **§5** / **§5a** cross-refs verified on disk; table rows align with **`ASTRAL_CODE_RULES.md` §1.5.1** on `origin/dev`. Implementation record + manifest greps pass. Parent inflow example (summary-only) → **fix-now** per §5f per-index / discovery rows.

**fix-now:** none.

**discuss:** `docs/ASTRAL_TEST_BIBLE.md` §7.13zs + AST-556 manifest block on publish ref — not in plan **Files Changed** (skill + plan only). Manifest-only, no log-string tests; OK if bible updates on child publish ref are standing **qa-astral** handoff — confirm or trim on resolve.

**advisory:** Appendix A Vitest-only-with-zero-args note — orthogonal, fine.

**Doc:** `docs/features/foundation/ast-556-review-astral-fix-now-for-debug-logging.md` (Review section) @ `3682194d`.

— Radia

#### betty — 2026-06-03T03:11:41.375Z
**Tests Ready** — doc/skill-only child (**AST-556**). No new component tests; parent forbids log-string assertions. **`docs/ASTRAL_TEST_BIBLE.md`** on publish ref: `96759c27c96e36a9d90396a6fb7cdf3b158cf8f5eeb8112e97b6dd74a9c17d33` @ `4d78ff3b`.

**Integration line (engineer `dev-radia` replay):**

1. `git fetch origin`
2. `git merge origin/dev`
3. `git merge origin/sub/AST-538/AST-554-debug-logging-contract-and-helper` (blocker)
4. `git merge origin/sub/AST-538/AST-556-review-astral-debug-fix-now`

**Manifest (`test-astral`):**

1. Plan doc on publish tip: `docs/features/foundation/ast-556-review-astral-fix-now-for-debug-logging.md` includes **Implementation record** and §5f walkthrough.
2. `test -f docs/features/foundation/ast-556-review-astral-fix-now-for-debug-logging.md`
3. `grep -q 'Implementation record' docs/features/foundation/ast-556-review-astral-fix-now-for-debug-logging.md`
4. `grep -F '#### 5f. Backend debug logging' ~/.cursor/skills/review-astral/SKILL.md` (global skill — not in repo)
5. Epic regression (blocker helper tests; confirms merge line): `.venv/bin/python -m pytest tests/component/utils/test_debug_logging.py tests/component/utils/test_logging_batch.py -q`

Wrong test or manifest → `[qa-handoff]` first line, stay **Tests Ready**, assign **Betty**.

— Betty

#### radia — 2026-06-03T00:39:58.824Z
Plan: `docs/features/foundation/ast-556-review-astral-fix-now-for-debug-logging.md`

https://github.com/susansomerset/astral/blob/sub/AST-538/AST-556-review-astral-debug-fix-now/docs/features/foundation/ast-556-review-astral-fix-now-for-debug-logging.md

**Self-Assessment**
- **Scope:** `scope-minor` — Global `review-astral` §5f plus this plan doc only; no `src/` or Test Bible changes.
- **Conf:** `conf-high` — Parent AC #6 and AST-554 §1.5.1 define the contract; this ticket only encodes the review rubric.
- **Risk:** `risk-low` — Rubric miswording could skew review severity but does not affect runtime or integration merges.

Publish tip: `507d4264` on `origin/sub/AST-538/AST-556-review-astral-debug-fix-now`.

---

# AST-556 — review-astral fix-now for debug logging (Improve Quality of Debug Logging)

- **Linear (this ticket):** [AST-556](https://linear.app/astralcareermatch/issue/AST-556/review-astral-fix-now-for-debug-logging-improve-quality-of-debug)
- **Parent:** [AST-538](https://linear.app/astralcareermatch/issue/AST-538/improve-quality-of-debug-logging)
- **Publish ref:** `origin/sub/AST-538/AST-556-review-astral-debug-fix-now` (child of AST-538; not Linear `gitBranchName`)

## Summary

Update the global **`review-astral`** skill so Radia treats **insufficient backend debug instrumentation** on touched **`debug=`** surfaces as **fix-now**, matching parent **AST-538** acceptance criterion **6** and the contract in **`docs/ASTRAL_CODE_RULES.md` §1.5.1** (delivered by **AST-554**). No product code, no Test Bible log-string tests, no changes to **`qa-astral`** / **`test-astral`**.

## Dependency note

**AST-554** (`blockedBy` in Linear) is **User Testing**; §1.5.1 may not yet be on **`origin/dev`**. During **`review-astral`** runs before merge, cite **`docs/ASTRAL_CODE_RULES.md` §1.5.1** from **`origin/dev`** when present; otherwise use the same subsection text on **`origin/sub/AST-538/AST-554-debug-logging-contract-and-helper`**. This ticket does **not** implement §1.5.1 or **`logging.py`** helpers.

## Out of scope (explicit)

| Item | Owner |
|------|--------|
| `docs/ASTRAL_CODE_RULES.md` §1.5.1 body | **AST-554** (done / UAT) |
| `src/utils/logging.py` helpers | **AST-554** |
| Dispatcher/roster/component backfill | **AST-557** and sibling children |
| Sidebar **Agent Ad Hoc** rename | **AST-555** |
| Betty manifest assertions on log prose | Forbidden per parent |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `~/.cursor/skills/review-astral/SKILL.md` | Add **§5f** debug-logging review rubric; wire **§5** intro | global skill (not in repo) |
| `docs/features/foundation/ast-556-review-astral-fix-now-for-debug-logging.md` | This plan (repo) | docs |

**No** `src/**`, `tests/**`, or `docs/ASTRAL_CODE_RULES.md` edits in **AST-556**.

## Stage 1: Add §5f — Backend debug logging (AST-538) to `review-astral`

**Done when:** `~/.cursor/skills/review-astral/SKILL.md` contains a new subsection **#### 5f. Backend debug logging (AST-538 / AST-554)** immediately after **#### 5e. Optional: `debug/code_review_notes.md`** and before **### 6. Combined doc**, and **§5**’s opening paragraph references §5f when the diff touches **`debug=`**.

1. In **`~/.cursor/skills/review-astral/SKILL.md`**, locate **### 5. Perform the review** (first paragraph lists three lenses). Append one sentence after the third-lens sentence:

   > When the diff adds or changes backend paths that accept or forward **`debug: bool`** (including batch loops, dispatch runners, roster/consult/agent entry points, or Agent Ad Hoc backend handlers), also apply **§5f** explicitly.

2. Insert **#### 5f. Backend debug logging (AST-538 / AST-554)** with this content (preserve markdown structure; adjust only if a prior edit already added §5f — then replace in full):

   **When to apply:** Any changed **`src/core/**`, `src/utils/logging.py`**, or backend **`src/ui/api/**`** handler that introduces, modifies, or calls through a **`debug`** parameter (including **`debug_flag`** on **`get_logger`**). **Do not** require debug logging on **`src/ui/frontend/**`** (backend only per §1.5.1).

   **Contract source:** **`docs/ASTRAL_CODE_RULES.md` §1.5.1** (and **`src/utils/logging.py`** helpers: `debug_index`, `debug_detail`, `debug_detail_block`, `truncate_debug_content`, `format_debug_index_header`).

   **Severity:** Map violations below to **fix-now** in the Linear comment unless a documented grandfather or coexistence exception applies.

   | Check | fix-now when |
   |-------|----------------|
   | **Trigger / gating** | New debug-contract emission without **`debug=True`** on that path; **`debug=False`** run would emit index/detail contract lines. |
   | **Per-index headers** | Batch loop over multiple items in a debuggable path but **no** `debug_index` (or equivalent §1.5.1 header) per item when **`debug=True`** — only a terminal **`summary={...}`** or pass/fail counts. |
   | **Discovery + recorded detail** | Debug run logs outcome only (pass/fail, warning) without **`debug_detail`** / **`debug_detail_block`** showing **what was found** (e.g. search hits) and **what was written** (e.g. slug ingest outcome) for that index. |
   | **Detail prefix** | Substantive working-log lines not prefixed with **` \| `** (`DEBUG_DETAIL_PREFIX`) under an index header. |
   | **Header shape** | Index headers not using universal **`index N/M`** (domain-specific counters like `term 3/95` in the format string). |
   | **Long content** | Logging blobs **>50 lines** without **`truncate_debug_content`** / **`debug_detail_block`** (first 15 / `<n lines omitted>` / last 15). |
   | **Anti-patterns (touched files)** | New **`logger.info("[DEBUG] …")`** in a file otherwise edited for AST-538; full prompts/responses logged without truncation. |
   | **Helpers** | Hand-rolled debug INFO instead of **`_PrefixedLogger`** contract methods where the file is touched for this epic. |
   | **Data layer** | New logging inside **`src/data/**`** (still no log per §1.5). |

   **Grandfather (advisory, not fix-now):** Pre-existing **`logger.info("[DEBUG] …")`** left unchanged in a file **not** otherwise edited for AST-538 — note in comment only if noisy; do not block.

   **Coexistence (do not flag):** `run_next hop: …` hop lines; **`log_llm_batch_summary`** when **`log_batch_id`** is set; normal INFO/WARNING/ERROR when **`debug=False`**.

   **Not fix-now:** Betty lacking log-string tests; missing debug on UI-only diffs; insufficient debug on files **outside** the diff that were not touched for AST-538.

3. In **§5a** table row **Logging (E1)**, append to the cell text (after existing §1.5 reference):

   > For **`debug=`** surfaces, also **§5f**.

4. Do **not** change **§7** (Linear status), assignee rules, or doc-only commit workflow in **§6**.

⚠️ **Decision:** Rubric lives in the **global** skill path (`~/.cursor/skills/review-astral/SKILL.md`), not a repo copy under **`astral/.cursor/`**, per **orientation-astral** § Cursor skills (global only).

## Stage 2: Verification and handoff

**Done when:** A reader can run **`review-astral`** on a child backfill ticket and know exactly when insufficient debug is **fix-now**; plan published to **`origin/sub/AST-538/AST-556-review-astral-debug-fix-now`**; Linear **Plan Ready** with labels and GitHub plan link.

1. Re-read **`review-astral/SKILL.md`** end-to-end: confirm **§5f** is referenced from **§5** intro and **§5a Logging (E1)**; confirm no contradictory text (e.g. “debug is advisory only”) remains elsewhere in the skill.

2. **Manual check (no pytest):** Using the parent **AST-538** example log in the parent issue description, confirm §5f would flag “summary only, no per-index discovery” as **fix-now** — mental walkthrough only; do not add tests.

3. On **`dev-radia`**, commit **only** `docs/features/foundation/ast-556-review-astral-fix-now-for-debug-logging.md` with message:

   `docs(AST-556): plan — review-astral debug fix-now rubric`

4. Publish via Joan (**`JOAN_SESSION=de2831b2-4e47-463f-88eb-f09f0c63a494`**):

   `~/.cursor/skills/git-astral/git.sh store-plan-commit AST-556 <plan-sha> radia --session de2831b2-4e47-463f-88eb-f09f0c63a494`

5. **build-astral** (this ticket): implement **Stage 1** on the global skill file, then one commit on **`dev-radia`** that records the skill change — if the skill file is outside git, the builder posts the skill diff summary in a Linear comment and commits only any repo doc touch-ups; **preferred:** copy the exact §5f block into a short **`## Implementation record`** subsection at the bottom of **this** plan file in the same build commit so UAT can diff the skill text without opening `~/.cursor/`.

⚠️ **Decision:** Skill file is not versioned in **`astral`** git; **Implementation record** in the plan doc is the auditable mirror for Susan/Chuckles during UAT of **AST-556** itself.

## Self-Assessment

**Scope:** `scope-minor` — Only the global **`review-astral`** skill (~one new subsection + two cross-refs) and this plan doc; no application modules.

**Conf:** `conf-high` — Parent AC #6 and **AST-554** §1.5.1 text are fixed; the work is editorial alignment of the review rubric with that contract.

**Risk:** `risk-low` — Wrong rubric wording could cause false **fix-now** or missed gaps in review, but does not change runtime behavior or merge integration.

## Self-review against ASTRAL_CODE_RULES

| Rule area | Plan alignment |
|-----------|----------------|
| §1.5 / §1.5.1 | Plan references contract only; does not duplicate or alter rules (AST-554). |
| §3.3 layers | No imports or layer changes. |
| §1.3 DRY | Single §5f table; §5a cross-ref avoids duplicating full contract. |
| §3.6 debug/ | No spike or `debug/` repo output. |

No conflicts requiring `conf-!!-NONE`.

## Implementation record

**Built 2026-06-03** on `dev-radia`. Global skill `~/.cursor/skills/review-astral/SKILL.md` updated (not in astral git): **§5** intro sentence for `debug=` paths; **§5a Logging (E1)** cross-ref; new **§5f. Backend debug logging (AST-538 / AST-554)** with fix-now table (trigger/gating, per-index headers, discovery+detail, detail prefix, header shape, long content, anti-patterns, helpers, data layer), grandfather/coexistence/not-fix-now notes. No contradictory “debug is advisory only” text in skill.

**Manual §5f walkthrough (parent AST-538 example):** A debug run that logs only a terminal `summary={...}` with no per-index `debug_index` / discovery `debug_detail` for each batch item → **fix-now** per **Per-index headers** and **Discovery + recorded detail** rows.

## Review

| Field | Value |
|-------|-------|
| **Branch** | `origin/sub/AST-538/AST-556-review-astral-debug-fix-now` |
| **Tip** | `4d78ff3b` (three-dot vs `origin/dev`) |
| **Build commit** | `bf87eb93` (feat + implementation record) |
| **Reviewer** | Radia (`review-astral` after Tests Passed) |

### What's solid

- Global `~/.cursor/skills/review-astral/SKILL.md`: **§5** intro, **§5a Logging (E1)** cross-ref, **§5f** table and grandfather/coexistence/not-fix-now rows match **`docs/ASTRAL_CODE_RULES.md` §1.5.1** on `origin/dev` (parent **AST-538** AC **6**).
- Plan **Implementation record** mirrors skill; Betty manifest greps (`#### 5f. Backend debug logging`, `Implementation record`) pass on workstation.
- **§5f** walkthrough: parent inflow example (terminal `summary={...}` only) → **fix-now** per per-index + discovery rows — aligned with parent brief.
- No `src/**` / `tests/**` / `ASTRAL_CODE_RULES.md` edits on publish ref.

### Issues

| Severity | Location | Note |
|----------|----------|------|
| **discuss** | `docs/ASTRAL_TEST_BIBLE.md` §7.13zs (publish ref) | Plan **Files Changed** listed only skill + plan doc; bible row + AST-556 manifest block added by **Betty** (`19332d98`…`4d78ff3b`). Acceptable as manifest-only (no log-string tests) if Susan treats bible updates as **qa-astral** handoff on the child publish ref; otherwise trim on resolve or document as standing exception for doc/skill children. |
| **advisory** | `ASTRAL_TEST_BIBLE.md` Appendix A tail | Vitest runs only when harness has zero trailing args — helpful, orthogonal to AST-556; no action required. |

### Recommended actions

| Action | Owner |
|--------|--------|
| None (fix-now) | — |
| Confirm bible §7.13zs on this child ref is intentional scope | Susan / Betty |
| After any **discuss** resolution: engineer may **`resolve-astral`** (likely no code) or close as-is | Radia assignee → engineer per skill |

## Resolution

**Resolved 2026-06-03** (`resolve-astral`, `dev-radia`, `JOAN_SESSION=de2831b2-4e47-463f-88eb-f09f0c63a494`).

| Radia finding | Outcome |
|---------------|---------|
| **fix-now** (none) | No product or skill edits required; global `review-astral` §5f already matched **§1.5.1** on `origin/dev`. |
| **discuss** — `docs/ASTRAL_TEST_BIBLE.md` §7.13zs on publish ref | Left as Betty **qa-astral** manifest artifact (doc/skill-only child; no log-string tests). Plan **Files Changed** unchanged; not trimmed. |
| **advisory** — Appendix A Vitest note | No action. |

**Git:** `git fetch` → `merge origin/dev` → `merge origin/ftr/ast-538-improve-quality-of-debug-logging` → `merge origin/sub/AST-538/AST-556-review-astral-debug-fix-now` on `dev-radia`. Reconciled **`docs/ASTRAL_TEST_BIBLE.md`** §7.13zs (**AST-556** row) + §7.13zt (**AST-555** from **`origin/ftr`**) so §9a dry-run into **`ftr/ast-538`** is clean.
