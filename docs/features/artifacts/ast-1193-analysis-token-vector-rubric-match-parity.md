<!-- linear-archive: AST-1193 archived 2026-08-07 -->

## Linear archive (AST-1193)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1193/analysis-token-vectorrubric-match-parity-issues-while-running  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1163 — Issues while running anticipate_scan  
**Blocked by / blocks / related:** parent: AST-1163

### Description

## What this implements

Make ANALYSIS_* job-token formatting resolve grade vectors against live rubric criteria with the **same** label-or-code matching rules consult scoring already uses (prompt assembly parity across agent calls), so persisted grades produce non-empty formatted ANALYSIS tokens; include debug found/recorded for per-phase grade vs formatted counts. Does **not** own candidate name view (sibling).

## Acceptance criteria

- [X] 2. For a job with persisted JD/DO/GET/LIKE grades whose vectors match the candidate's live rubric under the same label-or-code rules consult scoring uses, each corresponding `{$ANALYSIS_*}` token is non-empty and includes CONSIDER / rubric blob / ANALYSIS RESULT for those vectors — no per-vector "no rubric criterion" skip that empties the token while grades exist.
- [X] 3. A debug-gated run of the fixed path shows per-index found/recorded lines for each ANALYSIS phase (counts of grades vs formatted vectors).
- [X] 4. Susan can reproduce: after this child lands, a Generate Artifacts / `anticipate_scan` run with complete consult grades no longer logs empty `{$ANALYSIS_*}` from unmatchable vectors.

## Boundaries

Does **not** own candidate name token view (sibling AST-1192). Does **not** harden provider timeouts / blank errors (**AST-1164**). Does **not** regenerate candidate rubrics. Does **not** change `JOB_TOKEN_CONFIG` phase maps, grade persistence keys, `_grade_set_vector_diff` / IncompleteGradeSetError, or Manage Tasks prompt prose.

## In scope

- [X] `astral.agent.grade-vector-validation` — ANALYSIS formatter: live label-or-code parity with scoring helpers; on live miss, job-carried `*_rubric` snapshot identity (AST-1063) + live content-by-code so persisted grades are not silently skipped
- [X] `astral.config.config-source-of-truth` — keep reading `JOB_TOKEN_CONFIG` analysis phase maps; no parallel token/phase maps
- [X] `astral.standards.dry-and-focused-functions` — one shared `_find_rubric_criterion` for scoring helpers + ANALYSIS formatter
- [X] `astral.standards.debug-contract-gated` — Style D found/recorded per ANALYSIS phase only when `debug=True`
- [X] `astral.patterns.coat-check-never-store-empty` — do not persist empty failed ANALYSIS / hollow prompt outputs as if successful (this ticket formats only; no new empty persistence)
- [X] `astral.standards.logging-via-utils` — debug via `src/utils/logging.py` helpers on the touched path
- [X] `astral.standards.in-scope-only` — only ANALYSIS match parity + debug on `consult`/`agent` job_context path

## Considered but excluded

- [X] `astral.agent.do-task-delegation` — prompt assembly stays in `do_task`; this child only fixes job_context ANALYSIS formatting inputs (no new agent call shape)
- [X] `astral.batch.claim-process-release` — no new dispatch lifecycle
- [X] `astral.dispatch.run-next-is-chain-authority` — hop order unchanged
- [X] `astral.layers.import-direction` — no new cross-layer imports planned
- [X] Candidate name token view / `{$FIRST_NAME}` / `{$LAST_NAME}` — **AST-1192**
- [X] Provider timeout / blank error / zero-token hardening — **AST-1164**
- [X] Rubric regeneration / `rubric_vector` writes — out of epic
- [X] `_grade_set_vector_diff` / IncompleteGradeSetError / pass thresholds — out of scope
- [X] `tests/`, `docs/test-bible/**` — Betty

## Notes for planning

Joan r1: label-or-code alone is a no-op for the parent log (full labels). Plan Diagnosis + Stage 3: live label-or-code first, then job-carried `*_rubric` snapshot identity (AST-1063) with live content-by-code — closes AC4 without regenerating rubrics. Stage 1 remains shared `_find_rubric_criterion` DRY.

## Git branch (authoritative)

`origin/sub/AST-1163/AST-1193-analysis-token-vector-rubric-match-parity` — ignore Linear `gitBranchName`.

### Comments

#### chuckles — 2026-08-05T23:38:00.859Z
[merge-child] blocked: sub not stacked on ftr — `origin/ftr/AST-1163-anticipate-scan-token-context` has AST-1192 commits not in `origin/sub/AST-1163/AST-1193-analysis-token-vector-rubric-match-parity`. @Hedy Lamarr — merge `origin/ftr/AST-1163-anticipate-scan-token-context` into the publish ref and push, then Chuckles retries merge-child.

— Chuckles

#### radia — 2026-08-05T23:36:15.921Z
[code-rubric] revision=1

**Rubric:** code-rubric.v1
**Ticket:** AST-1193
**Publish ref:** `64ea1d86` → doc-only `b91302dd` (`origin/sub/AST-1163/AST-1193-analysis-token-vector-rubric-match-parity`)
**Overall:** CLEAN

## Plan adherence

- Implementation matches Stage 1–3 literally: `_find_rubric_criterion` placed immediately after `_strip_code`; both scoring helpers refactored onto it with behavior byte-for-byte preserved (first-match-then-decide, unchanged `ValueError` messages); `_format_analysis_phase_text` live-first / snapshot-identity-fallback / live-content-by-code / blob-less-but-nonempty exactly per Stage 3 step 3's four emit rules; `phase_tokens` sourced from `JOB_TOKEN_CONFIG["analysis_phases"]` (no second hardcoded tuple, no `total=4`); debug via a **local** `get_logger(__name__, debug_flag=debug)` handle only — grepped the diff for `set_debug_flag`, zero hits, shared module logger never clobbered.
- `src/` footprint is exactly the two planned files (`consult.py`, `agent.py`). Role boundaries clean per commit (`code()` → `src/` only, `test()` → `tests/`+`docs/test-bible/` only, `docs()` → `docs/features/` only).
- Joan's `plan-rubric.v1` r1 verdict (APPROVED) is attached with 2 open `discuss` items from her final pass — both are **closed by the shipped code**, not carried forward: the snapshot-key-derivation-coupling discuss is answered directly by `_analysis_phase_rubric_snapshot_key`'s docstring ("Couples to `grades_key == f\"{save_prefix}_grades}\"` — same stem both sides today") — exactly the comment she suggested; the residual-AC4-precondition discuss isn't a code gap, it's a UAT-time question already instrumented via the `snapshot_criteria=` debug count.

**Pattern conformance:** all cited ids (`astral.agent.grade-vector-validation`, `astral.config.config-source-of-truth`, `astral.standards.dry-and-focused-functions`, `astral.standards.debug-contract-gated`, `astral.patterns.coat-check-never-store-empty`, `astral.standards.logging-via-utils`, `astral.standards.in-scope-only`) score `conforms` via the full sweep. `grade-vector-validation`'s literal statement (do_task schema/grade-value validation) isn't touched by this diff — the citation covers the plan's extended reading (grade-vector *matching* for rendering), which Joan's traceability already accepted at Plan Approved; noting the stretch for the record, not as a finding.

**Cross-ticket note (not a finding):** this branch inherited `test(AST-1192)` / `test(AST-1189)` / `test(AST-1190)` commits via `merge-tests` (stacked-sibling test lineage in this epic worktree) but none of AST-1192's `src/` changes — `TestAst1192TokenViewForDoTask` would fail standalone on this branch's `agent.py`. Expected/by-design until `merge-child` lands both siblings on `ftr/AST-1163` in order; not something AST-1193's own diff introduced or can fix.

**What's solid:** Debug contract textbook — `index`/`total` from the config-authority phase map, counts-only detail lines (no blob spam), early-return paths still emit when `debug=True`. Snapshot-fallback emit shape is byte-identical to the existing block string with `rubric_blob == ""`, so the "blob-less but non-empty" path shares one code path rather than forking — exactly what Joan flagged as load-bearing for AC4.

## Frame diff

(none) — implementation matches the plan doc's Files Changed / Stage 1 / Stage 2 / Stage 3 as written; no adds or moves applied to this description.

Full active corpus (63 leaves — 18 universal + 45 scoped) swept in-session; zero violations, zero stragglers vs Joan's plan-rubric attachment. Doc-only verdict appended to the plan doc under `## Review` on `origin/<publish-ref>` (not pasted here per C1 note — full checked-list stays off-ticket).

context_tokens≈62000

— Radia

#### betty — 2026-08-05T23:29:32.569Z
## QA test manifest — AST-1193

**Publish:** `origin/sub/AST-1163/AST-1193-analysis-token-vector-rubric-match-parity` @ `64ea1d86`
**Betty SHA:** `origin/tests` `d15b790f` (`merge-tests(AST-1193): origin/tests d15b790f…`)

### Classification

1. **Existing coverage:** AST-513 `TestAst513JobTokenContext` + scoring label/code helpers (`TestRubricLookup` / `TestImportanceForLabelBranches`) — keep in manifest after revision.
2. **Broken / obsolete (revised this pass):** `TestAst513JobTokenContext` — formatter loads live criteria via `rubric_criteria_for_task` (not artifact blobs alone); patch live criteria + `_astral_candidate_id`.
3. **Gaps (this pass):** `_find_rubric_criterion`; snapshot fallback + live content-by-code; snapshot-without-live nonempty CONSIDER; Style D found/recorded; `debug=False` quiet; agent `debug=` thread into builder.

### Manifest (test-child)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_consult.py::TestAst1193AnalysisMatchParity \
  tests/component/core/test_consult.py::TestAst513JobTokenContext \
  tests/component/core/test_agent.py::TestAst1193DebugJobContext \
  -q
```

1. **`TestAst1193AnalysisMatchParity`** — finder label/code; live-miss + `*_rubric` snapshot → live content-by-code; snapshot-only CONSIDER nonempty; `debug=True` found/recorded; `debug=False` quiet.
2. **`TestAst513JobTokenContext`** — revised live-path regression for VISIBLE_JD / ANALYSIS formatting.
3. **`TestAst1193DebugJobContext`** — `_job_context_for_call(..., debug=True)` reaches `build_job_token_context`.

**Pass criterion:** pytest green on the three paths above — not zero-arg harness / branch-lock gate.

### Bible (publish-ref shasum)

- `docs/test-bible/core/consult.md` — `802e77e1bb1b6ea9225e4e3275f0bbb64d2e376f`

— Betty

#### joan — 2026-08-05T23:23:20.644Z
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1193
**Overall:** APPROVED
**Publish ref tip:** `origin/sub/AST-1163/AST-1193-analysis-token-vector-rubric-match-parity` @ `f133877f`

## Traceability

AC2→S1 (shared label-or-code predicate) + S3 (live-first path, live `content`); AC3→S2 (per-phase found/recorded); AC4→S3 (snapshot identity fallback) — **now delivered**, conditional on snapshot presence (finding 3). Stages→definition: S1→In-scope `dry-and-focused-functions`; S2→In-scope `debug-contract-gated`; S3→In-scope `grade-vector-validation` (the snapshot clause is now explicit in the child description). No orphan stages. Parent AC1 is N/A–boundary (sibling AST-1192).

**Considered:** full active corpus swept (65 leaves — 18 universal + 30 scoped considered, 17 scoped excluded on layer/path predicates). All `conforms`; both round-1 `needs-discussion` items (`debug-contract-gated`, `no-hardcoded-sets`) are now closed by the delta. Recorded in-session per R7.

## Findings

**1. `resolved` — round-1 fix-now is closed. I traced the snapshot mechanism end to end and it holds.**

The things that could have made Stage 3 a paper fix all check out:

- **Shape.** `_rubric_snapshot_for_job_data:207-212` emits a list of **dicts** with `code` / `label` / `importance` / `grade_descriptions`. So `_find_rubric_criterion(snapshot, vector_label)` can match it (the helper skips non-dicts, which would have silently killed the fallback had the snapshot been a list of strings), and `code` is present, so the live-content-by-code hop in step 3b has something to hop on. `content` is indeed dropped — Diagnosis point 4 is accurate.
- **Key derivation.** `grades_key[:-7] + "_rubric"` matches every real write site: `jd_rubric` at `consult.py:1962`, and `f"{prefix}_rubric"` at `consult.py:1053` where `save_prefix` is `do` / `get` / `like` (`config.py:645,671,697`). All four ANALYSIS phases resolve to a key that is actually persisted. Deriving from `grades_key` rather than `rubric_artifact` was the right call — `ANALYSIS_JD`'s artifact key is `jobdesc_rubric`, which is **not** the job-carried key. The frontend's `jobCarriedRubricKey("jd_grades") == "jd_rubric"` independently confirms the convention.
- **The fallback cannot miss when the snapshot exists.** This is the part that upgrades the plan from plausible to deterministic, and it is worth stating in the plan: the snapshot is written from the *same* criteria list used for reason hydrate and completeness in that call. `_hydrate_grade_reasons_from_rubric:186` raises when a vector has no criterion, and AST-1155's `_require_complete_grade_set` / `_grade_set_vector_diff:616-631` demands exact set equality on stripped labels. A successful grade save therefore *implies* every grade vector equals a label in the list that was snapshotted. So snapshot present ⟹ every vector matches ⟹ non-empty token. Not a heuristic.
- **Emit shape is unchanged, not invented.** Today's block is `f"CONSIDER: {title}\n{rubric_blob}\nANALYSIS RESULT: …"` (`consult.py:834-836`). Step 3c's blob-less variant is byte-identical to that string with `rubric_blob == ""`, so the engineer can implement one code path rather than two.
- **Stage 2 is executable as literally written.** `get_logger(name, debug_flag=…)` exists at `logging.py:284`, `debug_index` is keyword-only with exactly `func` / `index` / `total` / `identifier` / `outcome` (`logging.py:233-241`), `debug_detail(message)` at `:255`. And the round-1 concern was real — `set_debug_flag:202-213` does lower a DEBUG logger back to INFO. The local-handle rule is the correct fix.
- **Meteorite fork.** The `ANALYSIS_JD` override keeps `grades_key: "jd_grades"`, so it derives `jd_rubric` on that fork too; and if a meteorite job lacks the snapshot, step 3c's last branch degrades to today's warning rather than misbehaving.

I also confirmed the plan's own honesty check: `data/astral.db` here symlinks to the real DB and has 0 jobs / 0 candidates, so the "no live row dump" caveat is accurate rather than convenient.

**2. `discuss` — read and write derive the snapshot key by two different rules.**

The write side uses `f"{save_prefix}_rubric"`; the plan's read side uses `grades_key[:-7] + "_rubric"`. These agree for all four phases today only because `grades_key == f"{save_prefix}_grades"` in each case, which is a coincidence of naming rather than an enforced invariant — a future task whose `save_prefix` differs from its `grades_key` stem would write a snapshot the formatter silently never finds, and the symptom would be an empty ANALYSIS token with no error. One tiny shared helper (or a comment at the read site naming the coupling to `save_prefix`) makes the next person's life easier. Your call whether it earns a line in this ticket.

**3. `discuss` — the residual AC4 precondition, and what to do if UAT trips it.**

Self-assessment names this correctly: if a failing job predates the AST-1063 write path, it carries no `*_rubric` and the fallback cannot fire. That cannot be settled before build from this worktree (empty DB), so it is properly a UAT-time question, not a plan defect — and Stage 2's `snapshot_criteria=` count is exactly the instrument that answers it. Two requests so the answer doesn't turn into improvisation:

- If a debug run shows `snapshot_criteria=0` with `found_grades>0` on the reproduce job, that is the **escalate** the plan already names — post it on AST-1163 and stop. Do **not** reach for the tempting nearby fixes: widening `_rubric_snapshot_for_job_data` to store `content`, backfilling snapshots onto existing jobs, or relaxing the match to fuzzy/casefold are all explicitly out of bounds here.
- Worth knowing while you build: a blob-less `CONSIDER` block is **in** bounds. Parent AC2 is scoped to vectors that match the *live* rubric, and those always get live `content`; the blob-less branch only occurs outside AC2's scope, where AC4's non-empty requirement is the governing bar. So the weaker-context case is not an AC2 miss.

**4. `nit`** — Stage 1 step 4 takes three clauses and a "may" to arrive at its actual instruction. The final rule is unambiguous (Stage 1 commit = helper + scoring refactors; Stage 3 commit = formatter), so `plan-is-bible` is satisfied, but collapsing it to those two clauses would read better on the next pass.

## What the plan gets right

The Diagnosis section is the model of what a round-2 revision should look like — it names the mechanism, states plainly that Stage 1 is a no-op for the observed run, and keeps Stage 1 anyway because the DRY win is real. Ordering live-first and treating the snapshot strictly as *identity* (never as a content source) is the conservative choice: it cannot regress a currently-working match, and it cannot fabricate a rubric blob. Insisting the predicate stay byte-for-byte identical with no fuzzy matching remains the right guardrail, and I re-verified that `_lookup_rubric_reason_for_grade:154-161` and `_importance_for_label:597-604` are indeed identical predicates that both commit to the first match before deciding — so `_find_rubric_criterion` preserves behavior exactly in both call sites. Removing the `if not rubric_criteria: return ""` early exit is additive rather than risky, since the observed run had non-empty live criteria. `Conf: Medium` with the failure mode spelled out is the honest reading, and Boundaries against AST-1192, AST-1164, rubric regeneration, and the test tree hold throughout.

context_tokens≈146000

— Joan

#### hedy — 2026-08-05T23:17:11.459Z
[plan-discuss] round=1 reply

Agreed on finding 1: Stage 1 label-or-code alone is a no-op for the parent log (full labels, not 2-char codes). Diagnosis is now in the plan: formatter never reads job-carried `*_rubric` snapshots; 100% live miss fits post-grade rubric drift after AST-1155 accepted those labels.

**Delta @ `f133877f`:**
1. **fix-now / AC4:** New Stage 3 — live `_find_rubric_criterion` first; on miss, match grade vector to phase `*_rubric` snapshot (same helper); pull `content` from live by code; if live content gone, still emit CONSIDER + ANALYSIS RESULT (non-empty token). Stage 1 kept as DRY only (no longer claims it closes the bug).
2. **discuss / debug-contract:** Stage 2 uses local `get_logger(__name__, debug_flag=debug)` only — never `set_debug_flag(debug)` / never lower shared module DEBUG.
3. **discuss / hardcoded phases:** iterate + `total` from `JOB_TOKEN_CONFIG["analysis_phases"].keys()`.
4. **Conf:** `high` → `Medium` (fallback needs snapshots on the failing jobs).

Plan: https://github.com/susansomerset/astral/blob/sub/AST-1163/AST-1193-analysis-token-vector-rubric-match-parity/docs/features/artifacts/ast-1193-analysis-token-vector-rubric-match-parity.md

Status stays **Plan Discuss** for Joan.

#### joan — 2026-08-05T23:13:24.734Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1193
**Overall:** REVISE
**Publish ref tip:** `origin/sub/AST-1163/AST-1193-analysis-token-vector-rubric-match-parity` @ `4ec1524d`

## Traceability

AC2→S1 (parity predicate — mapped, but see finding 1: satisfiable *vacuously* on the observed data); AC3→S2 (per-phase found/recorded); AC4→**no stage demonstrably delivers it**. Stages→definition: S1→Functional scope bullet 2, S2→Functional scope bullet 3. No orphan stages. Parent AC1 is N/A–boundary ("Does **not** own candidate name token view (sibling AST-1192)").

**Considered:** full active corpus swept (65 leaves — 18 universal + 30 scoped considered, 17 scoped excluded on layer/path predicates). Two `needs-discussion` (findings 2 and 3); all others `conforms`. Recorded in-session per R7.

## Findings

**1. `fix-now` — label-or-code parity is a no-op for every vector in the pasted log, so AC4 (Susan's reproduction) is not delivered.**

The drift the plan describes is real and I verified it: `_format_analysis_phase_text` matches label-only at `src/core/consult.py:816-821`, while `_lookup_rubric_reason_for_grade:154-161` and `_importance_for_label:597-604` both accept stripped-label **or** uppercased code. Extracting one predicate is the right cleanup.

But it cannot be the cause of the reported failure. The plan's own Done-when scopes the behavior change precisely: "A grade whose `vector` is a **2-char code** that scoring would accept produces a CONSIDER … block instead of the skip." Every one of the ~35 unmatched vectors in the parent's log is a full human label, not a code — `'Compensation'`, `'Program Scope'`, `'Domain & Role Type Exclusions'`, `'Keyword / ATS Match'`, `'Gut Instinct: Would She Brag?'`. The new disjunct fires only when a criterion's `code` equals the upper-cased vector, and codes are two characters by construction (`_CODE_SUFFIX = r'\s*\([A-Z]{2}\)\s*$'` at line 124; `_vector_labels_map:146-147` maps code→label). `'COMPENSATION'` will never equal a 2-char code. After Stage 1 ships, that run logs the same 35 warnings and `{$ANALYSIS_DO}` is still empty.

Note how AC2 is worded — "grades **whose vectors match** the candidate's live rubric under the same label-or-code rules" — it is conditional, so the parity fix satisfies AC2 on paper while the observed bug survives untouched. AC4 is the one that bites: "a … run with complete consult grades **no longer logs empty** `{$ANALYSIS_*}` from unmatchable vectors."

There is also affirmative evidence the real cause is elsewhere. `_grade_set_vector_diff:616-631` compares live rubric labels against grade vectors on stripped labels, and AST-1155's `IncompleteGradeSetError` rejects a grade set that is not an exact match. If these grades persisted through that gate, their vectors *did* equal the live rubric labels at grading time — which points at the rubric having changed after the grades were written (or the phase's `rubric_owner_task_key` resolving a different rubric than the one graded against), not at a code-vs-label predicate. A 100% miss rate across all four phases fits "wrong or newer criteria list" far better than "code formatting."

**Recommendation:** before build, diagnose one concrete vector end to end — for that candidate and job, dump `rubric_criteria_for_task(cid, owner)` for each phase's `rubric_owner_task_key` alongside the persisted `*_grades` vectors — and write into the plan why `'Compensation'` misses today and what makes it hit after the change. Then either add the stage that fixes the actual mismatch class, or, if the cause is rubric drift between grading time and now, say so plainly and escalate on **AST-1163**: parent Boundaries forbid regenerating rubrics, so choosing between rendering a grade without its rubric blob, resolving against an analysis-time snapshot (`_rubric_snapshot_for_job_data:191` exists for AST-1063, though it deliberately omits `content`), or something else is an Archie/Susan call, not a build-time improvisation. Keep Stage 1 either way — it is good DRY work — but the plan should stop claiming it closes the bug.

**2. `discuss` (R3 `astral.standards.debug-contract-gated` → needs-discussion) — `set_debug_flag(debug)` with `debug=False` silences debug output that other callers turned on.**

Stage 2 steps 1–2 call `logger.set_debug_flag(debug)` at the top of `build_job_token_context` and `_format_analysis_phase_text`. That setter does not merely gate new lines — `src/utils/logging.py:202-213` *lowers* the named logger from DEBUG back to INFO when the flag is false. Since `logger` here is the shared `src.core.consult` module logger, any artifact hop that builds job token context with `debug=False` will switch off debug for the rest of that run for everything else in `consult.py` (a `render_verdict` debug run, a debug-enabled preview, or the sibling epics' debug work). The statute asks for no new contract lines when `debug=False`; suppressing existing ones is a side effect worth avoiding. Recommend raising only — set the flag when `debug` is true and never lower it — or take a local handle the way `emit_llm_call_debug` does, so a non-debug caller cannot clobber module state. Also please settle the step-2 "or rely on module logger flag" alternative into one instruction; `plan-is-bible` means the engineer executes what is written, and that step currently offers two shapes.

**3. `discuss` (R3 `astral.standards.no-hardcoded-sets` → needs-discussion) — second hardcoded phase list plus literal `total = 4`.**

Stage 2 step 3 derives `index` from a literal `("ANALYSIS_JD", "ANALYSIS_DO", "ANALYSIS_GET", "ANALYSIS_LIKE")` tuple and hardcodes `total = 4`, while `JOB_TOKEN_CONFIG["analysis_phases"]` is the config authority the plan otherwise commits to (and which the meteorite override mutates at `consult.py:788-790`). I am not calling this a violation — `build_job_token_context:853` already iterates that same literal tuple, so the plan matches adjacent style — but this adds a second copy plus a count that silently goes stale if a phase is ever added. Deriving both from the config map costs one line and matches `astral.config.config-source-of-truth`.

**4. `acceptable`** — I checked the two refactor targets for semantic drift, since replacing an inline loop with a first-match helper can change behavior. Both `_lookup_rubric_reason_for_grade` and `_importance_for_label` already commit to the first matching criterion and then decide (returning or raising inside the loop, raising after it), so `_find_rubric_criterion` returning the first match preserves behavior exactly. The plan's insistence that the predicate be byte-for-byte identical, with no fuzzy or casefold matching, is the right guardrail.

## What the plan gets right

The proposed helper's predicate is a faithful copy of `consult.py:157-161`, placement after `_strip_code` respects public-then-helpers, and collapsing three copies of the loop into one is a genuine §1.3 DRY win that prevents the next drift. Stage 1 step 4 correctly enumerates the behavior that must **not** change — meteorite override merge, `grades_key`, empty-criteria early return, warn-and-continue per vector rather than failing the whole token, and the CONSIDER / blob / ANALYSIS RESULT block shape — which is exactly the specificity that makes a plan reviewable. Stage 2 step 6's explicit "no new empty persistence" keeps `astral.patterns.coat-check-never-store-empty` clean, the counts-only debug detail avoids blob spam, and the `do_task` → `_job_context_for_call` → `build_job_token_context` thread is the minimal wiring for AC3. Boundaries against AST-1192, AST-1164, and the test tree are respected throughout.

Self-assessment is well-formed and `Risk: Medium` is honest about wrong-blob attachment. `Conf: high` is the claim to revisit — it rests entirely on the label-only/label-or-code drift being the cause, and the log's vector shapes say it is not.

context_tokens≈118000

— Joan

#### hedy — 2026-08-05T23:09:06.175Z
Plan published on `origin/sub/AST-1163/AST-1193-analysis-token-vector-rubric-match-parity` @ `4ec1524d`.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1163/AST-1193-analysis-token-vector-rubric-match-parity/docs/features/artifacts/ast-1193-analysis-token-vector-rubric-match-parity.md

**Self-assessment**
- **Scope:** Single-Component — `consult.py` ANALYSIS formatter + shared criterion finder; thin `debug` thread through `agent._job_context_for_call`.
- **Conf:** high — formatter still label-only while scoring helpers already use AST-707 label-or-code; fix is shared `_find_rubric_criterion` + Style D found/recorded counts.
- **Risk:** Medium — ANALYSIS tokens feed artifact LLM prompts; wrong match would attach the wrong rubric blob, but the predicate is already trusted by scoring/hydration.

---

# AST-1193 — ANALYSIS token vector↔rubric match parity

**Linear:** https://linear.app/astralcareermatch/issue/AST-1193/analysis-token-vectorrubric-match-parity-issues-while-running  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1163/issues-while-running-anticipate-scan  
**Publish ref:** `sub/AST-1163/AST-1193-analysis-token-vector-rubric-match-parity`

Make `{$ANALYSIS_JD}` / `{$ANALYSIS_DO}` / `{$ANALYSIS_GET}` / `{$ANALYSIS_LIKE}` format every persisted consult grade vector into a non-empty CONSIDER / rubric blob / ANALYSIS RESULT block for artifact hops (starting with `anticipate_scan`). Prefer the live rubric via the **same** label-or-code match scoring already uses; when live misses a full-label vector that still appears on the job-carried analysis-time `*_rubric` snapshot (AST-1063), resolve identity from that snapshot and pull `content` from live by code so grades that already passed scoring are not silently skipped. Add debug-gated found/recorded counts per ANALYSIS phase. Does **not** own candidate name token view (**AST-1192**), provider timeout hardening (**AST-1164**), or rubric regeneration.

## Diagnosis (why `'Compensation'` misses today)

Verified in code against the parent log (~35 full human labels across all four ANALYSIS phases — not 2-char codes):

1. **`_format_analysis_phase_text`** (`consult.py`) loads criteria only from live `rubric_criteria_for_task(cid, owner)`. It never reads the job-carried `jd_rubric` / `do_rubric` / `get_rubric` / `like_rubric` snapshots that `render_verdict` / evaluate batch already persist via `_rubric_snapshot_for_job_data` (AST-1063).
2. Match today is **label-only** (stripped). Scoring helpers `_lookup_rubric_reason_for_grade` / `_importance_for_label` already accept stripped label **or** uppercased code (AST-707). That drift is real and worth fixing for code-shaped vectors, but **every** unmatched vector in the parent log is a full label (`'Compensation'`, `'Program Scope'`, …). The code disjunct cannot fire for those strings (`_CODE_SUFFIX` / `_vector_labels_map` treat codes as two letters). **Stage 1 alone is a no-op for the observed run.**
3. Grades that persisted through AST-1155 `_require_complete_grade_set` had vectors equal to the **then-live** rubric labels. A 100% miss against **now-live** criteria (with non-empty criteria — otherwise the formatter returns `""` before per-vector warnings) fits **post-grade rubric label change** (or a different current criteria set for that owner), not code-vs-label formatting.
4. Snapshots intentionally **omit `content`** (list-header shape). So snapshot-only formatting cannot supply the rubric blob; content must still come from live (by code) when possible.

Local `data/astral.db` in this worktree has zero jobs/candidates — diagnosis is from code + parent log shapes, not a live row dump.

⚠️ **Decision (AC4 delivery):** Prefer live label-or-code first. On miss, match the grade vector to the job-carried phase `*_rubric` snapshot by the same label-or-code helper; use snapshot `label`/`code` for identity; resolve `content` from live by code (or label). If live has no content for that code, still emit `CONSIDER: {title}\n\nANALYSIS RESULT: …` so the token is non-empty. Do **not** regenerate rubrics. Do **not** invent fuzzy label matching. (Escalate path rejected for this plan: parent AC4 requires the reproduce case to stop logging empty ANALYSIS from these unmatchable vectors; snapshot identity + live content is the mismatch class that closes it without rewriting `rubric_vector`.)

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | Add shared `_find_rubric_criterion`; refactor scoring helpers; ANALYSIS formatter: live label-or-code + snapshot fallback + live content-by-code; phase iteration from `JOB_TOKEN_CONFIG["analysis_phases"]`; Style D found/recorded via local debug logger handle | core |
| `src/core/agent.py` | Pass `debug` from `do_task` into `_job_context_for_call` → `build_job_token_context(..., debug=debug)` | core |

**Out of files (siblings / boundaries):**

| File / area | Owner |
|-------------|-------|
| Candidate name / `build_candidate_token_view` / `{$FIRST_NAME}` / `{$LAST_NAME}` | AST-1192 |
| Provider timeout / blank `error=` / zero-token classification | AST-1164 |
| `JOB_TOKEN_CONFIG` phase key declarations / grades_key / owner task keys | unchanged (read-only) |
| Rubric regeneration / `rubric_vector` writes / widening `_rubric_snapshot_for_job_data` to store `content` | out of epic |
| `_grade_set_vector_diff` / IncompleteGradeSetError / pass thresholds | out of scope |
| Manage Tasks prompt prose | out of epic |
| `tests/`, `docs/test-bible/**` | Betty |

## Stage 1: Shared label-or-code criterion lookup (DRY — not the AC4 fix alone)

**Done when:** Scoring helpers and the ANALYSIS formatter share one `_find_rubric_criterion` with the AST-707 predicate. A grade whose `vector` is a 2-char code that scoring would accept matches via this helper. **This stage does not by itself close AC4 for the parent log** (full-label vectors); Stage 3 does.

1. In `src/core/consult.py`, immediately after `_strip_code`, add:

   ```python
   def _find_rubric_criterion(rubric_criteria: list, vector_label: str):
       """Return the criterion dict matching vector by stripped label or code (AST-707 / AST-1193)."""
       target = _strip_code((vector_label or "").strip())
       t_upper = target.upper()
       for item in rubric_criteria or []:
           if not isinstance(item, dict):
               continue
           lab = _strip_code(str(item.get("label") or "").strip())
           code = str(item.get("code") or "").strip().upper()
           if lab != target and code != t_upper:
               continue
           return item
       return None
   ```

   Match rules must be **byte-for-byte** the same predicate as today's loops in `_lookup_rubric_reason_for_grade` and `_importance_for_label`. Do **not** add fuzzy / casefold label matching or substring match.

2. In `_lookup_rubric_reason_for_grade`, replace the open match loop with `_find_rubric_criterion(rubric_criteria, vector_label)`. Keep grade-description resolution and `ValueError` messages unchanged.

3. In `_importance_for_label`, replace the open match loop with `_find_rubric_criterion(rubric_criteria, vector_label)`. Keep importance / default / `ValueError` behavior.

4. Do **not** yet change `_format_analysis_phase_text` beyond what Stage 3 specifies (Stage 3 owns the formatter body). Stage 1 may leave the formatter on the old loop until Stage 3 lands in the same build sequence — implement Stage 1 helpers first, then Stage 3 switches the formatter to the shared finder + snapshot path in one coherent edit if committing stages separately: **Stage 1 commit = helper + scoring refactors only; Stage 3 commit = formatter.**

## Stage 2: Debug found/recorded per ANALYSIS phase + wire from `do_task`

**Done when:** A `do_task` hop with `debug=True` that builds job token context emits Style D per-index headers for each ANALYSIS phase with found grade counts vs recorded vector counts. `debug=False` emits **no** new debug-contract lines and **does not** lower the shared `src.core.consult` module logger's debug state.

1. Change `build_job_token_context` signature to:

   ```python
   def build_job_token_context(
       job: Dict[str, Any], candidate_data: dict, *, candidate_id: str = "", debug: bool = False
   ) -> Dict[str, str]:
   ```

2. Debug handle rule (single instruction — no alternatives): obtain a **local** logger for contract lines with `log = get_logger(__name__, debug_flag=debug)` (same pattern as other gated helpers). Emit `log.debug_index` / `log.debug_detail` only through that handle. **Do not** call `logger.set_debug_flag(debug)` (or `False`) inside `build_job_token_context` or `_format_analysis_phase_text` — that setter lowers the shared module logger from DEBUG to INFO when `debug=False` and would clobber other consult debug runs in-process.

3. Change `_format_analysis_phase_text` to accept `*, debug: bool = False, job_id: str = ""`. Pass `debug=debug` and `job_id=str(job.get("astral_job_id") or "")` from the builder. Inside the formatter, use the same local-handle rule: `log = get_logger(__name__, debug_flag=debug)`.

4. Phase list authority: in `build_job_token_context`, replace the hardcoded `("ANALYSIS_JD", "ANALYSIS_DO", "ANALYSIS_GET", "ANALYSIS_LIKE")` iteration with:

   ```python
   phase_tokens = tuple((JOB_TOKEN_CONFIG.get("analysis_phases") or {}).keys())
   ```

   Use `phase_tokens` for both formatting and debug `index`/`total` (`total=len(phase_tokens)`). Meteorite override continues to mutate owner/artifact for `ANALYSIS_JD` only inside the formatter — it does not change the key set.

5. After computing the joined blocks string for a phase (including early-return empty cases), when `debug=True`, emit via the local handle:

   - `log.debug_index(func="_format_analysis_phase_text", index=<1-based among phase_tokens>, total=len(phase_tokens), identifier=f"{job_id}:{phase_token}", outcome="formatted" if text else "empty")`
   - `log.debug_detail(f"found_grades={found} recorded_vectors={recorded} live_criteria={n_live} snapshot_criteria={n_snap}")`

   Counts:
   - **found_grades:** grade dicts with non-empty stripped `vector`
   - **recorded_vectors:** CONSIDER blocks appended
   - **live_criteria** / **snapshot_criteria:** lengths of the lists used for that phase (0 when missing)
   - Early exits still emit index + detail when `debug=True`

   Counts only — no full blobs / token text.

6. In `src/core/agent.py`: add `debug: bool = False` to `_job_context_for_call`; pass `debug=debug` into the builder; at the `do_task` call site pass `debug=debug`.

7. Preview / adhoc callers may keep default `debug=False`. Do not invent UI debug toggles.

8. Coat-check: do **not** persist empty ANALYSIS strings into job_data / artifacts as success.

## Stage 3: ANALYSIS formatter — live first, snapshot identity fallback (AC4)

**Done when:** For a job with persisted `*_grades` and matching phase `*_rubric` snapshot labels (even when live criteria labels have drifted), each `{$ANALYSIS_*}` token is non-empty and includes CONSIDER / ANALYSIS RESULT for those vectors. Live label-or-code hits still use live `content`. Debug counts from Stage 2 show `recorded_vectors` tracking found grades on that path.

1. In `_format_analysis_phase_text`, keep meteorite phase-cfg merge and grades load. Derive snapshot key from `grades_key`: if `grades_key` ends with `"_grades"`, snapshot key is `grades_key[:-7] + "_rubric"` (e.g. `do_grades` → `do_rubric`, `jd_grades` → `jd_rubric`). Read `snapshot = job_data.get(snapshot_key)`; treat non-list as `[]`.

2. Load live `rubric_criteria` via `rubric_criteria_for_task(cid, owner)` when owner + cid present; else `[]`. **Remove** the early `if not rubric_criteria: return ""` — empty live must not abort formatting when grades + snapshot can still produce blocks. Keep early `return ""` only for missing phase cfg or empty/non-list grades.

3. For each grade dict with non-empty `vector_label`:

   a. `criterion = _find_rubric_criterion(live_criteria, vector_label)`  
   b. If `criterion is None` and snapshot is a non-empty list: `snap_row = _find_rubric_criterion(snapshot, vector_label)`  
      - If `snap_row` is not None: set `title = str(snap_row.get("label") or vector_label).strip()` and `code = str(snap_row.get("code") or "").strip()`; then `criterion = _find_rubric_criterion(live_criteria, code) if code else None` to obtain live `content` (and prefer live label for title when that live hit exists). If live content lookup misses, keep `criterion = None` but still treat as a **snapshot identity hit** (see c).  
   c. Emit rules:
      - **Live hit (a):** `title = str(criterion.get("label") or vector_label).strip()`; `rubric_blob = str(criterion.get("content") or "").strip()`; append CONSIDER / blob / ANALYSIS RESULT as today.
      - **Snapshot identity hit with live content (b with live criterion):** same block shape using live content; title from live label if present else snapshot label.
      - **Snapshot identity hit without live content:** append  
        `CONSIDER: {title}\n\nANALYSIS RESULT: {letter} ({conf_s} confidence)`  
        (blank line where blob would be — token still non-empty; title from snapshot).
      - **Neither live nor snapshot:** keep existing warning  
        `"_format_analysis_phase_text: no rubric criterion for vector %r (phase=%s)"`  
        and `continue`.

4. Letter / confidence formatting and `\n\n` join unchanged.

5. Pass `job_data` snapshot path only — do **not** widen `_rubric_snapshot_for_job_data` to persist `content` in this ticket.

6. `build_job_token_context` iterates `phase_tokens` from Stage 2 and passes `debug` / `job_id` into the formatter.

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the plan.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.**
- Completes each stage on the epic worktree, commits, publishes to `origin/sub/AST-1163/AST-1193-analysis-token-vector-rubric-match-parity`, then continues.

## Self-Assessment

**Scope:** `Single-Component` — `consult.py` ANALYSIS formatting + shared criterion finder + snapshot fallback; thin `debug` thread through `agent._job_context_for_call`.

**Conf:** `Medium` — Stage 1 DRY is certain; AC4 delivery rests on job-carried `*_rubric` snapshots existing for the failing jobs (AST-1063 write path) and on snapshot labels still matching persisted grade vectors after live drift. If a job lacks `*_rubric`, fallback cannot help and that case needs a separate escalate.

**Risk:** `Medium` — snapshot fallback can attach a live content blob by code after label drift (intended); wrong-code collisions would mis-attach content, same class of risk as scoring's code match. Emitting CONSIDER without blob when live content is gone is weaker context but still non-empty (AC4).

## Code rules check

- §1.3 DRY: one `_find_rubric_criterion` for scoring, live ANALYSIS, and snapshot lists.
- §1.5.1 debug-contract-gated: local `get_logger(..., debug_flag=debug)` only; never lower shared module debug via `set_debug_flag(False)`.
- §1.4 / §2.1: phase iteration from `JOB_TOKEN_CONFIG["analysis_phases"]` keys; no second hardcoded phase tuple / magic `total=4`.
- §2.3.1: formatter consumes persisted grades; no decode/validation change.
- Coat-check: no new empty ANALYSIS persistence.
- Boundaries: no name-token work, no AST-1164, no rubric regeneration, no test-tree edits.

## Revisions

Revision 1 — 2026-08-05  
Driven by: Joan `[plan-discuss] round=1 concern` (fix-now: label-or-code alone is a no-op for full-label parent-log vectors / AC4; discuss: `set_debug_flag(False)` clobber; discuss: hardcoded phase tuple + `total=4`).  
Changes: Added Diagnosis + AC4 Decision (live first, job-carried `*_rubric` snapshot identity fallback, live content-by-code). Stage 1 scoped as DRY only. Stage 2 uses local debug logger handle (never lower shared flag) and phase keys from `JOB_TOKEN_CONFIG`. New Stage 3 implements snapshot fallback. Conf `high` → `Medium`.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1163/AST-1193-analysis-token-vector-rubric-match-parity`
**Tip:** `29c1af56`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `5a7b1f39` | Shared `_find_rubric_criterion`; scoring helpers refactored |
| 2–3 | `29c1af56` | ANALYSIS live-first + `*_rubric` snapshot fallback; Style D found/recorded; `do_task` debug thread |

### code-rubric.v1 verdict

[code-rubric] revision=1

**Rubric:** code-rubric.v1
**Ticket:** AST-1193
**Publish ref:** `64ea1d86` (`origin/sub/AST-1163/AST-1193-analysis-token-vector-rubric-match-parity`)
**Overall:** CLEAN

Full active corpus (63 leaves — 18 universal + 45 scoped) swept in-session against `git diff origin/dev...origin/sub/AST-1163/AST-1193-analysis-token-vector-rubric-match-parity` (diff layers `{core, docs}`; paths `src/core/agent.py`, `src/core/consult.py`, `docs/features/**`, `docs/test-bible/**`, `tests/**`; change_types `{add, modify}`). No violations, no stragglers. `src/` footprint is exactly the two planned files (`consult.py` +112/-49 net, `agent.py` +6/-2); role boundaries clean per commit (`code()` → `src/` only, `test()` → `tests/`+`docs/test-bible/` only, `docs()` → `docs/features/` only).

**Plan adherence:** Implementation matches Stage 1–3 literally — `_find_rubric_criterion` placed immediately after `_strip_code`, both scoring helpers refactored onto it with behavior byte-for-byte preserved (first-match-then-decide, unchanged `ValueError` messages), `_format_analysis_phase_text` live-first / snapshot-identity-fallback / live-content-by-code / blob-less-but-nonempty exactly per Stage 3 step 3's four emit rules, `phase_tokens` sourced from `JOB_TOKEN_CONFIG["analysis_phases"]` (no second hardcoded tuple, no `total=4`), debug via a **local** `get_logger(__name__, debug_flag=debug)` handle only (grepped the diff for `set_debug_flag` — zero hits; the shared module logger is never clobbered). Joan's `plan-rubric.v1` r1 verdict (APPROVED) is attached with 2 open `discuss` items from her final pass — both are closed by the shipped code, not carried forward:

- Her snapshot-key-derivation-coupling discuss is answered directly: `_analysis_phase_rubric_snapshot_key`'s docstring states "Couples to `grades_key == f\"{save_prefix}_grades\"` — same stem both sides today" — exactly the comment she suggested "so the next person's life [is] easier."
- Her residual-AC4-precondition discuss (snapshot absent on pre-AST-1063 jobs) isn't a code gap — it's a UAT-time question already instrumented via the `snapshot_criteria=` debug count Stage 2 emits, per her own escalate-path framing.

**Pattern conformance:** all cited ids (`astral.agent.grade-vector-validation`, `astral.config.config-source-of-truth`, `astral.standards.dry-and-focused-functions`, `astral.standards.debug-contract-gated`, `astral.patterns.coat-check-never-store-empty`, `astral.standards.logging-via-utils`, `astral.standards.in-scope-only`) score `conforms` via the full sweep. `grade-vector-validation`'s literal statement (do_task schema/grade-value validation) isn't touched by this diff — the citation covers the plan's extended reading (grade-vector *matching* for rendering), which Joan's traceability already accepted at Plan Approved; noting the stretch for the record, not as a finding.

**Cross-ticket note (not a finding):** this branch inherited `test(AST-1192)` / `test(AST-1189)` / `test(AST-1190)` commits via `merge-tests` (stacked-sibling test lineage in this epic worktree) but none of AST-1192's `src/` changes — `tests/component/core/test_agent.py::TestAst1192TokenViewForDoTask` would fail standalone on this branch's `agent.py` (no `_token_view_for_do_task` here). Expected/by-design until `merge-child` lands both siblings on `ftr/AST-1163` in order; not something AST-1193's own diff introduced or can fix.

**What's solid:** Debug contract textbook — `index`/`total` from the config-authority phase map, `found_grades`/`recorded_vectors`/`live_criteria`/`snapshot_criteria` counts only (no blob spam), early-return paths still emit when `debug=True`. Snapshot-fallback emit shape is byte-identical to the existing block string with `rubric_blob == ""`, so the "blob-less but non-empty" path shares one code path rather than forking — exactly what Joan flagged as load-bearing for AC4.

## Frame diff

(none) — implementation matches the plan doc's Files Changed / Stage 1 / Stage 2 / Stage 3 as written; no adds or moves applied to this description.

context_tokens≈62000

— Radia

## Resolution

**Date:** 2026-08-05  
**Radia:** `[code-rubric] revision=1` — **Overall: CLEAN** (no fix-now / discuss / advisory to land).  
**Action:** No product changes. Resolution commit records intake of Radia’s doc-only review tip and §9a clean before User Testing.  
**Publish tip after resolve:** see commit SHA on `origin/sub/AST-1163/AST-1193-analysis-token-vector-rubric-match-parity`.
