# AST-441 — Investigate suspicious local run of evaluate_jd

<!-- linear-archive: AST-441 archived 2026-06-15 -->

## Linear archive (AST-441)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-441/investigate-suspicious-local-run-of-evaluate-jd  
**Status at archive:** Done  
**Project:** Astral Agent  
**Assignee:** susan  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

During a local `evaluate_jd` run (batch `evaluate_jd-34e38ddb-6801-4202-9634-808338f58fae`, 2026-05-18), the dispatcher claimed **38** jobs in `JD_READY_RETRY` and sent **37 empty JD slots** plus one populated listing to the agent in a single call. The model returned grades for **one** job; **37** were treated as agent omissions and routed to `ERROR_EVALUATE_JD`. The product bug is not ambiguous claim logic — **claim correctly keys off state only** — but that `evaluate_jd` **ran without verifying JD content was present before calling the agent**. JD text did not come through for most jobs; manual reset without re-scrape may have contributed but cannot be confirmed for individual IDs from this repro. Susan wants **investigation plus a fix plan** that goes through the normal Astral workflow (define → dispatch → plan → build). A **belt-and-suspenders readiness check** before any agent send prevents wasted tokens, misleading errors, and false "missing ID" outcomes.

**Repro evidence (in this ticket):** full `no_cache` block (38 index slots, only `[index=010]` has JD text), parsed response for the one graded job, and dispatcher/consult log excerpt for the batch.

## Functional scope

### Investigation (phase 1)

* **Root-cause determination:** For batch `evaluate_jd-34e38ddb-6801-4202-9634-808338f58fae`, determine why `job_description` was empty for most claimed jobs (never scraped, cleared after prior analysis, manual state reset without JD, or other) to the extent evidence allows; document uncertainty where per-job IDs cannot be recovered.
* **Pipeline trace:** Document the path from state-based claim through batch assembly to agent call for `evaluate_jd`, including what happens when claimed jobs mix empty and non-empty JD text.
* **Outcome assessment:** Conclude whether routing 37 omitted IDs to `ERROR_EVALUATE_JD` was misleading given empty inputs, and what operators should have seen instead.
* **Findings record:** Written answers Susan can act on, with a clear **fix required** statement tied to the readiness gap (not claim-layer changes).

### Fix (phase 2 — after investigation, via normal workflow)

* **Pre-agent readiness gate:** Before `evaluate_jd` sends live content to the agent, verify each job in the batch has usable JD text. Jobs that fail the check must **not** be included in the agent prompt and must **not** be treated as agent omissions or missing-response errors.
* **Appropriate handling for not-ready jobs:** Not-ready jobs receive an observable outcome distinct from rubric fail and from agent/parse error (e.g. hold for scrape, return to a scrape-eligible state, or operator-visible skip reason — exact states defined in the dev plan, not here).
* **Batch integrity:** When a batch is claimed, only jobs that pass the readiness check are sent together; empty slots must never be forwarded to the model as if they were valid JD listings.
* **Operator safety:** Re-running `evaluate_jd` after manual state changes cannot silently burn an API call on blank content or mass-assign `ERROR_EVALUATE_JD` for jobs that were never ready.
* **Fix plan artifact:** Investigation concludes with a concrete fix plan suitable for child tickets (investigation ticket may remain parent or findings roll into plan doc per team convention).

## Boundaries

* **Claim stays dumb:** Job claim continues to key off **state only** (e.g. `JD_READY`, `JD_READY_RETRY`); no business-logic or JD-presence checks at the claim/dispatcher claim layer.
* Readiness and empty-JD handling live **after claim, before agent call** (consult/evaluate path), not in tracker claim criteria.
* Does **not** cover `qualify_job_listings` (AST-440) except as a pattern reference for similar pre-agent checks if useful.
* Does **not** re-litigate rubric quality for the one graded job (Remote Status `F` on the Re:Build role stands for the JD that was present).
* Does **not** change consult pass/fail math or encoded-response contracts except as required to support the readiness gate.
* Investigation is anchored to the **documented local repro**; production-wide audit is optional follow-up.

## Acceptance criteria

### Investigation complete when:

1. Findings explain the 37 empty JD slots in plain language and state whether manual reset was likely vs JD never present, with explicit note where per-job proof is unavailable.
2. Claim/batch/agent path is documented: state-only claim → assembly → what went wrong when JD text was missing.
3. Written verdict: `ERROR_EVALUATE_JD` for agent "missing" IDs on empty inputs is **not acceptable**; desired behavior is stated observably.

### Fix complete when:

4. `evaluate_jd` **never** sends a job with empty or missing JD text to the agent.
5. Jobs failing the readiness check get a **non-error, non-rubric-fail** outcome (observable in logs and job state) and do not inflate "missing ID" or `ERROR_EVALUATE_JD` counts.
6. Re-running against the repro scenario (or equivalent test fixture): a batch with 37 empty + 1 populated JD does **not** produce 37 `ERROR_EVALUATE_JD` from agent omission; only the ready job is graded.
7. A **fix plan** exists (in plan doc or child tickets) and has entered the normal build workflow.

## Dependencies and blockers

* **AST-434** — production-readiness context; parallel.
* **AST-440** — sibling qualify reliability; parallel.
* Local DB or fixture access helps investigation but is not required to ship the readiness gate if repro is captured in tests.
* None otherwise.

## Open questions

None — Susan confirmed investigation + fix through workflow; claim remains state-only; readiness check before agent send.

### Comments

#### chuckles — 2026-05-25T01:08:03.165Z
## Landed on origin/dev — Chuckles

- **`origin/ftr/AST-441-investigate-suspicious-local-run-of-evaluate-jd`** was already merged into **`origin/dev`** (merge step: already up to date; no new push required).
- Deleted **`origin/ftr/AST-441-investigate-suspicious-local-run-of-evaluate-jd`**.
- Moved to **Done** (were PR Ready): **AST-441**, **AST-445**, **AST-446** (Ada kept assignee on children).

**`origin/dev` tip:** `917b08b7`

**Engineers — merge before your next skill** (`orientation-astral` § Merge integration line):

```bash
git fetch origin
git checkout dev-<agent>
git merge origin/dev
```

Do **not** rebase `origin/dev` onto `dev-<agent>` unless Susan directs.

— Chuckles

#### chuckles — 2026-05-23T03:25:47.849Z
## UAT Ready — Chuckles (prep-uat)

All **2** child branches merged into parent branch and child branches deleted.

**Parent branch:** `origin/ftr/AST-441-investigate-suspicious-local-run-of-evaluate-jd`

**Merged in order:**
1. **AST-445** — findings and fix plan (docs + spike script) — deleted
2. **AST-446** — pre-agent JD readiness gate in `evaluate_jd_batch` — deleted

Local `dev` merged (prep-uat §8). Restart the app / dispatcher if running, then test.

`ftr` tip: `88dbddd5` · local `dev` merge: `40247c22`

## Manual test steps

**Prerequisites:** Local `dev`; candidate with jobs in `JD_READY` or `JD_READY_RETRY`. Read findings first: `docs/features/consult/ast-445-evaluate-jd-investigation-findings.md`.

### AST-445 — Investigation (docs)

1. Read investigation findings and fix plan under `docs/features/consult/` — confirms 37 empty slots / misleading `ERROR_EVALUATE_JD` verdict.
2. Optional: `python3 scripts/spikes/ast445_evaluate_jd_batch_trace.py` (read-only trace helper).

### AST-446 — Readiness gate (runtime)

3. **Short/empty JD** — Put a job in `JD_READY` with empty or very short `job_description` (< `min_jd_chars`, default 80). Run **evaluate_jd** (Scheduled Actions or batch). Confirm: **no agent call** for that job; state moves to **`PASSED_JOBLIST`** (scrape re-entry); `job_data.jd_readiness_skip` records `empty_or_short_jd` in logs/DB — **not** `ERROR_EVALUATE_JD`.
4. **Ready JD** — Job with real JD text in `JD_READY`: evaluate_jd runs normally; graded job gets pass/fail outcome as before.
5. **Mixed batch** — One batch with mostly empty JD + one populated: only the ready job is sent to the agent; empty jobs skipped per step 3; **no mass ERROR_EVALUATE_JD** from “missing ID” on blanks.
6. **Claim unchanged** — Dispatcher still claims by **state only** (`JD_READY` / `JD_READY_RETRY`); readiness is **after** claim, before agent (no claim-layer JD check).
7. **Regression** — `qualify_job_listings` and other consult tasks unchanged.

### Parent acceptance

8. **AC 1–3** — Investigation docs satisfy investigation criteria.
9. **AC 4–6** — Runtime behavior matches readiness gate (steps 3–5).

If testing fails on `dev`:
  `git reset --hard origin/dev`

— Chuckles

#### chuckles — 2026-05-19T20:34:32.766Z
[check-linear]

**Plan review pass (Ada — AST-445, AST-446):** Re-read `origin/sub/AST-441/AST-445-*` and `AST-446-*` plan docs. Both still **Plan Ready** with existing **REVISE** reviews (2026-05-19); branch tips unchanged — fix plan still routes not-ready jobs → `PASSED_JOBLIST`, which is **not** in `JOB_STATES["PASSED_JOBLIST"].prior_states` for `JD_READY` / `JD_READY_RETRY`.

**Ada:** Update fix plan + AST-446 plan with a **legal** target state (e.g. extend `PASSED_JOBLIST` `prior_states` to include `JD_READY`/`JD_READY_RETRY` for scrape re-entry, or a new hold state Susan approves). Fix `DISPATCH_TASKS` → `dispatch_tasks` DB reference in AST-445 Stage 2. Re-request review when pushed.

**Chuckles queue:** No other Team Astral **Plan Ready** tickets. **Todo** Chuckles: AST-412 (boards spike — not plan-review).

— Chuckles

#### chuckles — 2026-05-19T16:27:48.216Z
## Dispatch — Chuckles

Dispatched **2** child tickets from the approved definition.

| Ticket | Title | Assigned to | Branch | Blocked by |
|--------|-------|-------------|--------|------------|
| AST-445 | Findings and fix plan | Ada | `sub/AST-441/AST-445-investigate-suspicious-local-run-of-evaluate-jd-findings-and-fix-plan` | — |
| AST-446 | Pre-agent JD readiness gate | Ada | `sub/AST-441/AST-446-investigate-suspicious-local-run-of-evaluate-jd-pre-agent-jd-readiness-gate` | AST-445 |

**Assignment rationale:**
- **Ada:** Both tickets are consult/`evaluate_jd_batch` domain (`evaluate_jd`, `_run_batch_consult`); investigation produces the plan doc, implementation ships the readiness gate.
- **Hedy / Katherine:** Not assigned this dispatch.

Susan can override any assignment by reassigning the child ticket directly.

Parent moves to **In Progress**. `prep-uat` will merge child branches and hand the parent branch to Susan when all children reach Review Posted.

**Git (authoritative — ignore Linear `gitBranchName`):**
- Parent: `origin/ftr/AST-441-investigate-suspicious-local-run-of-evaluate-jd`
- Children:
  - `origin/sub/AST-441/AST-445-investigate-suspicious-local-run-of-evaluate-jd-findings-and-fix-plan`
  - `origin/sub/AST-441/AST-446-investigate-suspicious-local-run-of-evaluate-jd-pre-agent-jd-readiness-gate`

Plan attachments should use  
`https://github.com/susansomerset/astral/blob/<sub-ref-or-ftr-ref>/docs/features/...`  
after **plan-astral** lands the plan doc.

— Chuckles

#### chuckles — 2026-05-19T16:24:05.510Z
## Dispatch blocked — @susan

Dispatch did not run (no child tickets, no branches).

**Show-stoppers:**
1. **Status** is **Backlog** — dispatch requires **Todo**.
2. **Assignee** is **Susan** — dispatch requires **Chuckles**.

Definition looks ready (open questions cleared in Description). When you want dispatch:
- Move **AST-441** to **Todo**
- Assign **Chuckles**
- Say **dispatch 441** again (or re-run `/dispatch-linear`)

— Chuckles

#### chuckles — 2026-05-19T16:17:59.808Z
Updated Definition per your answers:
- **Investigation + fix** through normal workflow (readiness gate + fix plan / child tickets)
- Core bug framed as **JD not ready but evaluate ran anyway**; manual reset noted as possible but unprovable per-ID
- **Claim stays state-only**; belt-and-suspenders check is **before agent send**, not at claim
- Open questions cleared

If this looks right, move to **Todo** and assign me for dispatch.

— Chuckles

#### chuckles — 2026-05-19T16:11:39.791Z
Definition draft ready for review. Key decisions made:
- Scoped as **investigation + findings** (root cause for 37 blank JD slots, claim/batch behavior, ERROR_EVALUATE_JD verdict); fixes deferred to follow-on tickets unless you expand scope
- Repro anchored to batch `evaluate_jd-34e38ddb-6801-4202-9634-808338f58fae`; your no_cache block and logs kept as evidence reference
- **3 open questions** (investigation-only vs fix epic, manual reset history, desired empty-JD handling)

Please review the Description and comment with changes or approval.

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
