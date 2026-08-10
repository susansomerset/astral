# AST-1163 — Issues while running anticipate_scan

<!-- linear-archive: AST-1163 archived 2026-08-07 -->

## Linear archive (AST-1163)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1163/issues-while-running-anticipate-scan  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1162; related: AST-1161

### Description

## Purpose

`anticipate_scan` is the entry hop of the resume artifact chain. A recent run showed empty candidate name tokens and empty / unusable ANALYSIS phase tokens because grade vectors could not be matched to the candidate's live rubric — so the hop went to the LLM without identity or consult recap. Until those prompt inputs resolve correctly, Generate Artifacts cannot produce a trustworthy ATS keyword scan. This epic restores correct candidate-name and ANALYSIS token context for that hop (and sibling artifact hops that share the same resolve path). Provider timeout / blank-error / zero-token hardening for the same hop is **AST-1164** (related), deferred until name + vector context is understood.

## Functional scope

* Artifact `do_task` hops (starting with `anticipate_scan`) resolve `{$FIRST_NAME}`, `{$LAST_NAME}`, and related candidate identity tokens from the same authoritative name fields the rest of the product uses after the contact/name-columns cutover — when the candidate has names set, those tokens are non-empty in the prompts that reference them.
* `{$ANALYSIS_JD}`, `{$ANALYSIS_DO}`, `{$ANALYSIS_GET}`, and `{$ANALYSIS_LIKE}` format every persisted consult grade vector using the **same** label-or-code resolution rules as consult scoring against the candidate's live rubric for that phase (CONSIDER / rubric blob / ANALYSIS RESULT). Prompt assembly for artifact hops matches other agent calls — vectors scoring accepts must not be silently skipped in the ANALYSIS token formatter, leaving the token empty while grades exist.
* With `debug=True` on the touched backend resolve/format path: log what was **found** and what was **recorded** per step (candidate id, name-token outcomes, per-phase grade count vs formatted vector count). Index headers use universal `index N/M` + primary identifier + outcome (Style D); working detail lines use the contract prefix (two spaces, pipe, two spaces); payloads >50 lines use first 15 / `<n lines omitted>` / last 15. Backend only.

## Architectural definition

* **Patterns to reuse** — `pattern.config.config-block` (token registry / JOB_TOKEN_CONFIG remain config authority; no parallel token maps); `pattern.batch.entity-claim-process-release` (artifact hop stays claim/process/release; no new dispatch lifecycle); `pattern.dispatch.run-next-chain-authority` (`run_next` / hop order unchanged — fix resolve inputs, not chain topology).
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.config.config-source-of-truth` (TOKEN_SOURCES / JOB_TOKEN_CONFIG); `astral.standards.debug-contract-gated` (debug contract above); `astral.standards.in-scope-only`; `astral.standards.no-cross-contamination`; `astral.standards.dry-and-focused-functions`; `astral.standards.logging-via-utils`; `astral.standards.data-raises-caller-logs`; `astral.layers.import-direction`; `astral.agent.do-task-delegation` (prompt assembly stays in `do_task`); `astral.agent.grade-vector-validation` (ANALYSIS formatter uses the same vector match rules as consult scoring); `astral.batch.claim-process-release`; `astral.dispatch.run-next-is-chain-authority`; `astral.patterns.coat-check-never-store-empty` (do not persist empty failed ANALYSIS / hollow prompt outputs as if successful).

## Boundaries

* Does **not** re-author `anticipate_scan` prompt prose in Manage Tasks (Susan's prompts stay).
* Does **not** harden provider timeouts, blank `error=`, or `stop=?` / zero-token response classification — that is **AST-1164** (related).
* Does **not** add hollow-context fail-fast / long-wait gates in this epic; Susan wants name + missing-vector causes understood first (provider wait may or may not be related).
* Does **not** change consult grading persistence keys, pass/fail thresholds, or job state machine topology.
* Does **not** regenerate or rewrite candidate rubrics; it aligns ANALYSIS formatting with the live rubric and match rules consult scoring already uses.
* Does **not** expand schedulability of `anticipate_scan` (still chain-hop, not a default Scheduled Action).
* Must not break other artifact hops that share the same token resolve / job_context builders (`contemplate_job` and later hops).
* Sibling UT work on signature spacing (**AST-1161** / **AST-1162**) is out of scope.

## Acceptance criteria

1. For a candidate with non-empty first/last name columns, running `anticipate_scan` (or Manage Tasks preview for that task with the same candidate) substitutes non-empty `{$FIRST_NAME}` and `{$LAST_NAME}` — no empty-token warnings for those names on that run.
2. For a job with persisted JD/DO/GET/LIKE grades whose vectors match the candidate's live rubric under the same label-or-code rules consult scoring uses, each corresponding `{$ANALYSIS_*}` token is non-empty and includes CONSIDER / rubric blob / ANALYSIS RESULT for those vectors — no per-vector "no rubric criterion" skip that empties the token while grades exist.
3. A debug-gated run of the fixed path shows per-index found/recorded lines for candidate identity and each ANALYSIS phase (counts of grades vs formatted vectors).
4. Susan can reproduce: after #1–#2 land, a Generate Artifacts / `anticipate_scan` run on a candidate with names and complete consult grades no longer logs empty `{$FIRST_NAME}` / `{$LAST_NAME}` or empty `{$ANALYSIS_*}` from unmatchable vectors (any remaining failure is outside this epic — e.g. **AST-1164** provider path).

## Dependencies and blockers

* Baseline: AST-513 (ANALYSIS job tokens), AST-1014 (name columns + token view), AST-595/AST-597 (BUILD_ARTIFACTS hop states / mid-chain), AST-1150/AST-1155 (rubric completeness / incomplete grades) — already shipped; this epic fixes runtime wiring/parity against that baseline.
* **Related (not blocking):** **AST-1164** — provider timeout / empty-error / zero-token hardening for the same hop; deferred until name + vector issues are understood.
* No open Linear blockers. Parallel Artifacts UT: **AST-1161** (signature spacing) — no functional dependency.

## Open questions

none.

## Proposed child tickets

#### 1: **Artifact hop candidate token view (names) - Ada**

Ensure artifact `do_task` / preview resolve paths feed the walkable candidate token view (name columns + library blobs) so `{$FIRST_NAME}` / `{$LAST_NAME}` (and siblings) resolve for `anticipate_scan` and shared hops; include debug found/recorded for name-token outcomes on the touched path. Does **not** own ANALYSIS formatter matching (#2).
**Citations:** `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.agent.do-task-delegation`; `astral.standards.debug-contract-gated`; `astral.standards.in-scope-only`.

#### 2: **ANALYSIS token vector↔rubric match parity - Hedy**

Make ANALYSIS_* job-token formatting resolve grade vectors against live rubric criteria with the **same** label-or-code matching rules consult scoring already uses (prompt assembly parity across agent calls), so persisted grades produce non-empty formatted ANALYSIS tokens; include debug found/recorded for per-phase grade vs formatted counts. Does **not** own candidate name view (#1).
**Citations:** `astral.agent.grade-vector-validation`; `astral.config.config-source-of-truth`; `astral.standards.dry-and-focused-functions`; `astral.standards.debug-contract-gated`; `astral.patterns.coat-check-never-store-empty`.

---

## Original brief

```
LLM deepseek task=anticipate_scan 1425.7s stop=? tokens in=0 out=0
do_task(anticipate_scan) provider call failed batch_id=anticipate_scan-bc0b3279-bde7-4c7e-a895-156ca2fa7b4a error=
_format_analysis_phase_text: no rubric criterion for vector 'Compensation' (phase=ANALYSIS_JD)
_format_analysis_phase_text: no rubric criterion for vector 'Domain & Role Type Exclusions' (phase=ANALYSIS_JD)
_format_analysis_phase_text: no rubric criterion for vector 'Program Scope' (phase=ANALYSIS_JD)
_format_analysis_phase_text: no rubric criterion for vector 'Remote/Location Policy' (phase=ANALYSIS_JD)
_format_analysis_phase_text: no rubric criterion for vector 'Technical Scope' (phase=ANALYSIS_JD)
_format_analysis_phase_text: no rubric criterion for vector 'AI/ML Product Integration' (phase=ANALYSIS_DO)
_format_analysis_phase_text: no rubric criterion for vector 'Autonomy & Creative Latitude' (phase=ANALYSIS_DO)
_format_analysis_phase_text: no rubric criterion for vector 'Cloud Platform & Architecture Depth' (phase=ANALYSIS_DO)
_format_analysis_phase_text: no rubric criterion for vector 'Cross-Functional Scope' (phase=ANALYSIS_DO)
_format_analysis_phase_text: no rubric criterion for vector 'Company Stage Fit' (phase=ANALYSIS_DO)
_format_analysis_phase_text: no rubric criterion for vector 'Delivery Framework Ownership' (phase=ANALYSIS_DO)
_format_analysis_phase_text: no rubric criterion for vector 'Healthcare Domain Expertise' (phase=ANALYSIS_DO)
_format_analysis_phase_text: no rubric criterion for vector 'Meaningful Work & Utilization' (phase=ANALYSIS_DO)
_format_analysis_phase_text: no rubric criterion for vector 'Remote-First Requirement' (phase=ANALYSIS_DO)
_format_analysis_phase_text: no rubric criterion for vector 'Structure-from-Chaos Need' (phase=ANALYSIS_DO)
_format_analysis_phase_text: no rubric criterion for vector 'Team Culture & Respect' (phase=ANALYSIS_DO)
_format_analysis_phase_text: no rubric criterion for vector 'Technical Hands-On Partnership' (phase=ANALYSIS_DO)
_format_analysis_phase_text: no rubric criterion for vector 'Keyword / ATS Match' (phase=ANALYSIS_GET)
_format_analysis_phase_text: no rubric criterion for vector 'Credential & Certification Alignment' (phase=ANALYSIS_GET)
_format_analysis_phase_text: no rubric criterion for vector 'Domain/Sector Credibility' (phase=ANALYSIS_GET)
_format_analysis_phase_text: no rubric criterion for vector 'Education Level Match' (phase=ANALYSIS_GET)
_format_analysis_phase_text: no rubric criterion for vector 'Role Type Fit (IC vs. Manager vs. Consultant)' (phase=ANALYSIS_GET)
_format_analysis_phase_text: no rubric criterion for vector 'Scope & Scale Signaling' (phase=ANALYSIS_GET)
_format_analysis_phase_text: no rubric criterion for vector 'Technical Depth vs. Management Breadth' (phase=ANALYSIS_GET)
_format_analysis_phase_text: no rubric criterion for vector 'Work Model & Geographic Compatibility' (phase=ANALYSIS_GET)
_format_analysis_phase_text: no rubric criterion for vector 'Chaos-to-Structure Mandate' (phase=ANALYSIS_LIKE)
_format_analysis_phase_text: no rubric criterion for vector 'Compensation & Practical Fit' (phase=ANALYSIS_LIKE)
_format_analysis_phase_text: no rubric criterion for vector 'Domain Fit: Healthcare, SaaS, Cloud' (phase=ANALYSIS_LIKE)
_format_analysis_phase_text: no rubric criterion for vector 'Gut Instinct: Would She Brag?' (phase=ANALYSIS_LIKE)
_format_analysis_phase_text: no rubric criterion for vector 'Growth & Learning Trajectory' (phase=ANALYSIS_LIKE)
_format_analysis_phase_text: no rubric criterion for vector 'Mission & Impact Alignment' (phase=ANALYSIS_LIKE)
_format_analysis_phase_text: no rubric criterion for vector 'Meaningful Work & Utilization' (phase=ANALYSIS_LIKE)
_format_analysis_phase_text: no rubric criterion for vector 'Remote-First Authenticity' (phase=ANALYSIS_LIKE)
_format_analysis_phase_text: no rubric criterion for vector 'Team Culture & Respect' (phase=ANALYSIS_LIKE)
_format_analysis_phase_text: no rubric criterion for vector 'Technical Hands-On Partnership' (phase=ANALYSIS_LIKE)
Token {$FIRST_NAME} resolved to empty (path=first, task=anticipate_scan)
Token {$LAST_NAME} resolved to empty (path=last, task=anticipate_scan)
Token {$FIRST_NAME} resolved to empty (path=first, task=anticipate_scan)
Token {$FIRST_NAME} resolved to empty (path=first, task=anticipate_scan)
Token {$FIRST_NAME} resolved to empty (path=first, task=anticipate_scan)
Token {$FIRST_NAME} resolved to empty (path=first, task=anticipate_scan)
Token {$FIRST_NAME} resolved to empty (path=first, task=anticipate_scan)
Token {$FIRST_NAME} resolved to empty (path=first, task=anticipate_scan)
Token {$ANALYSIS_DO} resolved to empty (job_context, task=anticipate_scan)
Token {$FIRST_NAME} resolved to empty (path=first, task=anticipate_scan)
Token {$FIRST_NAME} resolved to empty (path=first, task=anticipate_scan)
```

## Git (authoritative — ignore Linear `gitBranchName`)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Ticket | `origin/…` |
| -- | -- |
| AST-1163 (parent) | ftr/AST-1163-anticipate-scan-token-context |
| AST-1192 | sub/AST-1163/AST-1192-artifact-hop-candidate-token-view-names |
| AST-1193 | sub/AST-1163/AST-1193-analysis-token-vector-rubric-match-parity |

**Epic worktree:** `astral-AST-1163/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/dc470ea8ea95e57f1914a037a661763a/eda4a7a7-a9d8-48f1-8952-cd89499a3bf9/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/dc470ea8ea95e57f1914a037a661763a/504b01c9-4a94-4d32-9d02-3c94dc60317f/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/13f27d35-e96a-4037-b577-59edfc728041/store.db` |
| Radia | review | `/home/susan/.cursor/chats/dc470ea8ea95e57f1914a037a661763a/80d679a3-43bd-4f56-8cf1-998c6f876e85/store.db` |

### Comments

#### hedy — 2026-08-05T23:17:12.589Z
AST-1193 plan-discuss r1 note (no status change asked):

Parent-log ANALYSIS empties are **not** explained by code-vs-label match alone — vectors are full labels. Formatter loads live `rubric_criteria_for_task` only and ignores job-carried `*_rubric` snapshots (AST-1063). Plan Stage 3 on AST-1193: live first, then snapshot identity + live content-by-code, so AC4 can land without regenerating rubrics. Override on the child if that decision is wrong.

#### chuckles — 2026-08-03T22:38:04.557Z
@susan

1. Which candidate id + job id produced the pasted log (so UAT can replay the exact hollow-token case)?
2. Is the DeepSeek ~24m / `tokens in=0 out=0` provider failure **in scope** as its own hardening, or **out of scope** once hollow name/ANALYSIS context fails fast (treat long empty provider waits as a symptom)?
3. Confirm product rule: ANALYSIS token vector matching must use the **same** label-or-code resolution rules as consult scoring (vs requiring grades to store full live labels only).

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
