# AST-1531 — Caller cutover (mailbox, inbox, Contact)

**Linear:** [AST-1531](https://linear.app/astralcareermatch/issue/AST-1531/caller-cutover-mailbox-inbox-contact-generalize-meteorite-ingress)  
**Parent:** [AST-1527](https://linear.app/astralcareermatch/issue/AST-1527/generalize-meteorite-ingress-point) — Generalize Meteorite Ingress Point  
**Publish ref:** `sub/AST-1527/AST-1531-caller-cutover-mailbox-inbox-contact`

Wire mailbox `meteorite_email` `_handle_bound`, inbox `_land_bound_inbox_message` / `fetch_email` / admin Land, and `contact_land_meteorite` through the public `stage_meteorite` entry (AST-1530). Keep hygiene / archive / bind / strip ownership in the callers. Does **not** own catalog (AST-1529) or stage core (AST-1530).

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/core/meteorite_email.py` — **modified** — `_handle_bound` drops mechanical classify tree; bind → stage → archive/skip from stage outcomes; mailbox hygiene stays here.
- `src/core/inbox.py` — **modified** — `_land_bound_inbox_message` / `fetch_email` / admin Land paths call stage instead of raw HTML → `land_meteorite`.
- `src/core/contact.py` — **modified** — `contact_land_meteorite` (and paste/Slack scrap callers on this path) send blob + source handle through stage before land.
- `src/core/meteorite_email.py` — **major modified** `_handle_bound`: remove subject/href/inspector heuristic tree; call stage; drive archive-on-success / leave-in-inbox from stage+land outcomes; keep unbound trash / `last_email_check`.
- `src/core/inbox.py` — **modified** `_land_bound_inbox_message` and selected-ids / `run_fetch_email` land path: stage then land; preserve bind/strip ownership in inbox.
- `src/core/contact.py` — **modified** `contact_land_meteorite`: pass source handle + scrap body into stage; do not call `land_meteorite` with unclassified blobs.

All Files Changed / Stages stay inside that set.

**Out of scope (siblings / keep):**

- `STAGE_METEORITE_CONFIG` / `TASK_CONFIG["stage_meteorite"]` / `agent_task` row — **AST-1529** (do not re-edit).
- `stage_meteorite` / `invoke_stage_meteorite` / scrap map — **AST-1530** (consume only; do not rewrite).
- `create_meteorite_job_from_inbox_message` (legacy single Create API) — not listed in this ticket Scope; leave calling `land_meteorite` until a later ticket.
- `create_contact_meteorite` in `src/core/meteorite.py` (Contact-task markup land) — not in this ticket’s Files; do not retarget here.
- Rewrites of `land_meteorite` / `qualify_meteorite` / Gmail external / UI blueprints.

**Depends on:** AST-1529 + AST-1530 present after `sync-child.sh` with `--ftr AST-1527-generalize-meteorite-ingress-point` (full parent slug). Public contract already on tip:

```python
async def stage_meteorite(
    candidate_id: str,
    blob: str,
    *,
    source_kind: str,   # key of STAGE_METEORITE_CONFIG["source_ref_prefixes"]: email|slack|paste
    source_id: str,
    debug: bool = False,
) -> Dict[str, Any]:
```

Return keys (AST-1530): `outcome`, `stage_outcome`, `skipped`, `scraps`, `land`, `error`, `batch_id`, `company`, `company_inserted`, `outcomes`. Landable → `skipped=False` and `outcome`/`land` from `land_meteorite`. Skip outcomes (`not_job_content`, `not_original_posting`) → `skipped=True`, `land=None`, `outcome == stage_outcome`. Agent/map failure → `outcome == METEORITE_CONFIG["land_outcome_error"]`, `skipped=False`.

**AC partition (this ticket):** Parent AC6 only — mailbox / inbox Land/`fetch_email` / Contact land each invoke stage before land; mechanical subject/href/inspector classify is gone from `_handle_bound`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/meteorite_email.py` | Rewrite `_handle_bound` → `stage_meteorite`; map stage→archive tokens; delete mechanical classify + scrape/BOT_BLOCKED helpers now unused; update module docstring | core |
| `src/core/inbox.py` | `_land_bound_inbox_message` → stage; treat stage skip as passed in `run_fetch_email` / `land_inbox_message_ids`; update module docstring | core |
| `src/core/contact.py` | `contact_land_meteorite` → stage with required `source_kind`/`source_id`; Estelle `land_calls` site passes Slack handle; update header note | core |

## Stage 1: Mailbox — `_handle_bound` → `stage_meteorite`

**Done when:** `_handle_bound` no longer runs subject/href/inspector heuristic forks; every bound message with a candidate API key fetches HTML once, calls `stage_meteorite(..., source_kind="email", source_id=<gmail message id>)`, then archives or leaves inbox from stage+land outcomes via existing `_finalize_archive` rules; unbound trash / `last_email_check` paths unchanged; dead classify helpers removed; `python3 -m py_compile src/core/meteorite_email.py` succeeds.

1. Update the module docstring (top of `src/core/meteorite_email.py`) so it no longer describes “Susan decision tree → land_meteorite / BOT_BLOCKED”. Replace with: candidate-bound bind → `stage_meteorite` → archive on land success / all-skip (including stage skip outcomes) / leave inbox on error; unbound Trash + `last_email_check` unchanged (AST-1531). Keep AST-1140 / selected-ids notes.

2. Replace `_handle_bound` body (keep signature and return tuple `(processed, passed, failed, errors, outcome)`):

   a. Keep the existing candidate / API-key gate (missing → `failed`, leave inbox).  
   b. Keep `get_message_html(mid)` try/except (failure → `error`).  
   c. **Remove** all of: empty-body ignore forks; `_subject_is_url` / `_body_http_links` / `_body_looks_like_inspector_html` branches; `_land_jd` / `_scrape_land_or_bot_blocked` calls.  
   d. Assemble blob for stage (caller-owned visible content — no strip_extract here; inbox owns strip):

      ```python
      subject = (payload.get("subject") or "").strip()
      html = payload.get("html_body") or ""
      if subject and html:
          blob = f"{subject}\n\n{html}"
      else:
          blob = subject or html
      ```

   e. Late-import and call:

      ```python
      from src.core.meteorite import stage_meteorite

      stage = await stage_meteorite(
          cid,
          blob,
          source_kind="email",
          source_id=mid,
          debug=debug,
      )
      ```

      ⚠️ **Decision — `source_kind="email"` / `source_id=mid`:** Gmail message id is the stable source handle; prefix `email-` comes from `STAGE_METEORITE_CONFIG` inside stage. Do not invent UUIDs.

   f. Map stage result → one archive token string via a new helper `_stage_archive_token(stage: dict) -> str` placed next to `_land_outcome_token`:

      - If `stage.get("skipped")` is true → `"skipped"` (types 5/6 — archive under existing all-skip rule).  
      - Else if `stage.get("land")` is a dict → `_land_outcome_token(stage["land"])`.  
      - Else → `_land_outcome_token(stage)` (covers error shape where `outcome` is `land_outcome_error`).

   g. `outcomes = [_stage_archive_token(stage)]` then `return (1, *await _finalize_archive(mid, outcomes, …))` — same archive/leave-inbox contract as today (`_finalize_archive` unchanged).

   h. When `debug=True`, `_detail` one line: `stage_outcome={stage.get("stage_outcome")!r} skipped={stage.get("skipped")!r} archive_token={outcomes[0]}` (no new Style D index — stage already emits Style D; mailbox keeps existing `_dbg` / `_finalize_archive` indices).

3. **Delete** these helpers and any imports that become unused after step 2 (do not leave dead classify code):

   - `_subject_is_url`, `_body_http_links`, `_body_looks_like_inspector_html`
   - `_land_jd`, `_create_bot_blocked_job`, `_scrape_land_or_bot_blocked`
   - Imports used only by those: `urlparse`, `re` (if unused), `_meteorite_fetch_link_visible_text`, `save_meteorite_job`, `transition_job_state`, `job_link_exists_for_candidate`, `METEORITE_EMAIL_INGEST_CONFIG`, `TASK_CONFIG`
   - Keep `_body_text` / `_body_is_empty` **only if** still referenced after the rewrite; if not, delete them too.
   - Keep `_land_outcome_token`, `_finalize_archive`, hygiene helpers, `do_task` import (AST-1522 monkeypatch), Gmail archive/trash, candidate stamp imports.

4. Do **not** change `run_meteorite_email`, `process_meteorite_email_messages`, `run_meteorite_email_selected_ids` beyond what falls out of `_handle_bound` (they already call it). Do not stamp `last_email_check` differently. Do not Trash unbound mail from `_handle_bound`.

5. Compile: `python3 -m py_compile src/core/meteorite_email.py` (repo venv if needed: `~/astral/.venv/bin/python`).

## Stage 2: Inbox — `_land_bound_inbox_message` → stage

**Done when:** `_land_bound_inbox_message` still fetches + `strip_extract_email_html`, then calls `stage_meteorite` with `source_kind="email"` / `source_id=message_id` (never raw `land_meteorite` on the stripped blob); empty stripped HTML still returns the existing error dict without calling stage; `run_fetch_email` and `land_inbox_message_ids` count stage skip outcomes as **passed** (not failed); `python3 -m py_compile src/core/inbox.py` succeeds.

1. Update module docstring: fetch_email / Land → `stage_meteorite` then land-inside-stage (AST-1531); bind/strip stay in inbox.

2. In `_land_bound_inbox_message`, after successful strip (non-empty `html`):

   - Replace `from src.core.meteorite import land_meteorite` + `await land_meteorite(cid, text=html, …)` with:

     ```python
     from src.core.meteorite import stage_meteorite

     stage = await stage_meteorite(
         cid,
         html,
         source_kind="email",
         source_id=mid,
         debug=debug,
     )
     ```

   - Keep existing empty-strip early return unchanged (no stage call).  
   - Debug index/detail: use `stage.get("outcome")` for the index outcome; detail may include `stage_outcome=` and `skipped=` in addition to existing `html_len` / candidate lines.  
   - **Return `stage`** (full stage dict). Callers that read `outcome` / `error` / `company` / `outcomes` still work: landable paths copy those from land; skip paths set `outcome` to the skip literal.

3. In `run_fetch_email`, after `land = await _land_bound_inbox_message(...)`:

   - Treat as **passed** when any of:  
     `land.get("skipped")` is true, **or**  
     `outcome in STAGE_METEORITE_CONFIG["skip_outcomes"]`, **or**  
     `outcome in (created_k, skip_k, super_k)` (existing).  
   - Import `STAGE_METEORITE_CONFIG` from `src.utils.config` (add to existing config import block).  
   - Error / other outcomes stay failed/errors as today.

4. In `land_inbox_message_ids`, apply the **same** passed rule when scoring `land_outcome` from `_land_bound_inbox_message` (step 3). Do not change unbound / missing-id skip tokens.

5. Do **not** edit `create_meteorite_job_from_inbox_message` (out of Scope). Do not edit UI API modules.

6. Compile: `python3 -m py_compile src/core/inbox.py`.

## Stage 3: Contact — `contact_land_meteorite` → stage

**Done when:** `contact_land_meteorite` requires `source_kind` + `source_id`, builds a blob from `text` / `scraps` / optional `job_link`, calls `stage_meteorite` (never `land_meteorite` directly), and returns the stage dict; Estelle `land_calls` loop passes `source_kind="slack"` and a non-empty Slack source id; `python3 -m py_compile src/core/contact.py` succeeds.

1. Update the AST-1471 header note to: Contact scrap path → `contact_land_meteorite` → `stage_meteorite` (AST-1531).

2. Replace `contact_land_meteorite` signature and body:

   ```python
   def contact_land_meteorite(
       astral_candidate_id: str,
       *,
       source_kind: str,
       source_id: str,
       scraps: Optional[List[Dict[str, Any]]] = None,
       text: Optional[str] = None,
       job_link: Optional[str] = None,
       employer_name: Optional[str] = None,
       debug: bool = False,
   ) -> Dict[str, Any]:
       """Contact/Estelle sync entry to stage_meteorite (AST-1531)."""
   ```

   a. Validate: `kind = (source_kind or "").strip()` must be a key of `STAGE_METEORITE_CONFIG["source_ref_prefixes"]`; `sid = (source_id or "").strip()` must be non-empty; else return  
      `{"outcome": METEORITE_CONFIG["land_outcome_error"], "error": "source_kind/source_id required", "skipped": False, "scraps": [], "land": None, "outcomes": [], "company": None, "company_inserted": False}`  
      (sync return — no raise). Import `STAGE_METEORITE_CONFIG` + `METEORITE_CONFIG` if not already imported in this module’s land path.

   b. Assemble blob (unclassified scrap body for stage — do **not** pass `scraps=` into land):

      - If `isinstance(text, str) and text.strip()`: start with that text.  
      - Elif `isinstance(scraps, list) and scraps`: for each dict scrap, append non-empty `text` / `content` / `html_body` lines and any `job_link` line; join with `\n\n`.  
      - If `job_link` kwarg is a non-empty str and not already in the blob, append `\n\n{job_link}`.  
      - `employer_name` may be appended as a single `Employer: …` line when non-empty (optional context for Ruth); do not invent employer when missing.  
      - If final blob strip is empty → same error dict as (a) with `error="blob is required"`.

   c. Call:

      ```python
      from src.core.meteorite import stage_meteorite

      return asyncio.run(
          stage_meteorite(
              astral_candidate_id,
              blob,
              source_kind=kind,
              source_id=sid,
              debug=debug,
          )
      )
      ```

   ⚠️ **Decision — required source handle on Contact:** Stage needs stable source-refs; Estelle Slack events supply `message_ts` (fallback below). Paste callers (future / other) pass `source_kind="paste"` + their session id — this ticket only rewires the Estelle call site on this path.

3. In `run_contact_estelle_turn` `land_calls` loop (e2), every `contact_land_meteorite(...)` call must pass:

   - `source_kind="slack"`  
   - `source_id=(message_ts or thread_ts or channel)` — first non-empty after strip among those three (all already in scope of the turn). Prefer `message_ts`, then `thread_ts`, then `channel`.

   Keep the existing scraps-vs-text branch for **blob inputs** (`scraps=` vs `text=` / `job_link=` / `employer_name=`), but always include the source kwargs.

4. Do **not** change Estelle prompt prose beyond what is required for the call to compile (optional one-line note that land goes through stage is fine; do not invent a new land_calls schema). Do not edit `create_contact_meteorite` in `meteorite.py`.

5. Compile: `python3 -m py_compile src/core/contact.py` and a final  
   `python3 -m py_compile src/core/meteorite_email.py src/core/inbox.py src/core/contact.py`.

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish to `origin/sub/AST-1527/AST-1531-caller-cutover-mailbox-inbox-contact` after each stage (build-child).
- No files outside the Files Changed table.
- Ambiguity / drift → stop, comment on **parent** AST-1527 with the Stage blocked format from plan-child, wait.
- Do not re-implement scrap map / Ruth invoke inside callers — only call `stage_meteorite`.
- Do not revive `gaze_email` / gazer HTML ingest / mailbox mechanical classify.
- Sync before build: `sync-child.sh … --ftr AST-1527-generalize-meteorite-ingress-point` (full slug — short `AST-1527` alone misses `origin/ftr/...`).

## Estimate

Confirm Chuckles estimate: 3 — agree

Three known callers onto an already-shipped `stage_meteorite` contract; mechanical tree deletion is large in `meteorite_email.py` but bounded; inbox/contact are thin rewires plus skip-as-passed / source-handle wiring.

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1531
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1527/AST-1531-caller-cutover-mailbox-inbox-contact` @ `54754e3328e39f5a839e45cf3df12e6c9f3dae93`

## Traceability
AC6 → Stage 1 (`_handle_bound` → `stage_meteorite`, mechanical tree deleted); Stage 2 (`_land_bound_inbox_message`, `run_fetch_email`, `land_inbox_message_ids`); Stage 3 (`contact_land_meteorite` + Estelle `land_calls` with Slack source handle).

## Findings

### discuss — Bound empty-body mailbox messages
Plan removes empty-body ignore forks and always calls stage. When subject and HTML are both empty, blob is empty → invoke fails → archive token `error` → `(passed=0, errors=1)` vs old `(passed=1, ignored)`. Leave-inbox behavior similar; runner accounting shifts. If empty bound mail is rare, acceptable; otherwise add an explicit pre-stage empty-blob branch (documented) without restoring the full heuristic tree.

### acceptable — `create_meteorite_job_from_inbox_message` stays on raw `land_meteorite`
Explicitly out of Scope; not an admin Land / `fetch_email` path in this partition. Ticket AC6 covers the three wired ingress surfaces; legacy Create API is a follow-on if Susan wants full inbox parity.

### acceptable — BOT_BLOCKED / scrape helpers removed from mailbox
Epic intent: classify via stage → `land_meteorite` scrape path. Short-URL BOT_BLOCKED creation was mechanical-tree behavior; not revived here.

### acceptable — `contact_land_meteorite` signature break
`source_kind` / `source_id` required; only production caller is Estelle `land_calls` (plan updates it). Paste ingress can use `source_kind="paste"` when wired later.

context_tokens≈52000

## Review (build stub)

**Publish ref:** `origin/sub/AST-1527/AST-1531-caller-cutover-mailbox-inbox-contact`  
**Plan path:** `docs/features/meteorite/ast-1531-caller-cutover-mailbox-inbox-contact.md`

**Built tip:** `f948e6ada5ff751aec7de5a96293bab1f53cb0e1` (`f948e6ad`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `2a0f464a` | mailbox `_handle_bound` → `stage_meteorite`; mechanical tree deleted |
| 2 | `4457be23` | inbox `_land_bound_inbox_message` / fetch / Land → stage; skip = passed |
| 3 | `f948e6ad` | `contact_land_meteorite` → stage; Estelle Slack `source_kind`/`source_id` |

## Radia review

# Radia review — AST-1531

`[code-rubric] revision=2`  
**Rubric:** code-rubric.v2  
**Ticket:** AST-1531  
**Publish ref:** `origin/sub/AST-1527/AST-1531-caller-cutover-mailbox-inbox-contact` @ `3afaf3e853bc1efdb948b2c74c19753ac9cc8f00`  
**Overall:** CLEAN  

**Diff baseline:** `origin/dev...origin/sub/AST-1527/AST-1531-caller-cutover-mailbox-inbox-contact` (27 paths). AST-1531 product delta: `src/core/meteorite_email.py`, `src/core/inbox.py`, `src/core/contact.py`. Branch tip also carries AST-1529/1530 foundation + Betty merge-tests (expected epic lineage; 1531 engineer commits stayed inside Files Changed).

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no agent-vector changes |
| astral.agent.do-task-delegation | scoped | conforms | callers delegate classify/land to `stage_meteorite` (no ad-hoc Ruth) |
| astral.agent.grade-vector-validation | scoped | not-applicable | n/a |
| astral.batch.batch-id-first | scoped | not-applicable | no new batch claim paths in callers |
| astral.batch.batch-id-format | scoped | not-applicable | batch id minting stays in 1530 invoke |
| astral.batch.claim-process-release | scoped | conforms | no METEORITE_NEW claim added in callers |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | n/a |
| astral.config.config-source-of-truth | scoped | conforms | skip-as-passed reads `STAGE_METEORITE_CONFIG["skip_outcomes"]` |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | n/a |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | n/a |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | n/a |
| astral.dispatch.seed-auto-false | scoped | not-applicable | n/a |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | n/a |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single AST-1531 plan file |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty owns tests/bible |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer commits limited to three core files |
| astral.layers.core-vs-external-bright-line | scoped | conforms | mailbox mechanical scrape/BOT_BLOCKED removed; scrape stays in `land_meteorite` via stage |
| astral.layers.import-direction | scoped | conforms | late `stage_meteorite` imports in callers; no UI/data imports |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | n/a |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | no UI edits |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | n/a |
| astral.idioms.render-verdict-orchestrates-consult | scoped | conforms | callers orchestrate; stage/consult own Ruth path |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | n/a |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no 1531 catalog edits |
| astral.seed.archie-catalog-wins | scoped | not-applicable | n/a |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | n/a |
| astral.seed.define-approved | scoped | not-applicable | n/a |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | n/a |
| astral.seed.other-via-coverage-join | scoped | not-applicable | n/a |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no data-layer edits |
| astral.standards.database-header-inventory | scoped | not-applicable | n/a |
| astral.standards.debug-contract-gated | scoped | conforms | mailbox uses `_detail` only (plan); inbox debug gated; no new ungated emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | large deletion in mailbox; thin inbox/contact rewires |
| astral.standards.in-scope-only | scoped | conforms | `create_meteorite_job_from_inbox_message` left on `land_meteorite` per plan |
| astral.standards.logging-via-utils | scoped | conforms | `get_logger` / debug helpers only |
| astral.standards.names-not-ticket-ids | scoped | conforms | source kinds use config keys (`email`/`slack`/`paste`) |
| astral.standards.no-cross-contamination | scoped | conforms | no parallel classify vocabulary in callers |
| astral.standards.no-hardcoded-sets | scoped | conforms | skip-as-passed uses `STAGE_METEORITE_CONFIG` |
| astral.standards.public-then-helpers | scoped | conforms | `_stage_archive_token` helper colocated with archive helpers |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | n/a |
| astral.state.core-decides-transitions | scoped | conforms | BOT_BLOCKED mechanical path removed; transitions stay in land |
| astral.state.job-prior-states-enforced | scoped | not-applicable | n/a |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | n/a |
| astral.ui.frontend-file-placement | scoped | not-applicable | n/a |
| astral.ui.naming-conventions | scoped | not-applicable | n/a |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | n/a |
| orch.git.betty-merge-tests-one-sha | universal | conforms | `merge-tests(AST-1531)` on tip |
| orch.git.commit-vocabulary | universal | conforms | three `code(AST-1531)` stage commits + merge-tests |
| orch.git.flow-direction-inviolable | universal | conforms | sub topology |
| orch.git.ftr-sub-topology | universal | conforms | publish ref matches child pattern |
| orch.git.merge-on-checkout | universal | conforms | n/a |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | n/a |
| orch.git.no-dev-agent-branches | universal | conforms | n/a |
| orch.git.one-epic-worktree-per-parent | universal | conforms | review in `astral-AST-1527` |
| orch.git.three-permanent-branches | universal | conforms | diff vs `origin/dev` |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | empty-body shift flagged at plan (Joan discuss) |
| orch.pipeline.plan-is-bible | universal | conforms | all three stages match plan |
| orch.pipeline.project-scoped-queues | universal | conforms | n/a |
| orch.pipeline.status-gates-skill-entry | universal | conforms | reviewed at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | n/a |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns cutover tests + bible |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | n/a |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Katherine assignee preserved |
| orch.roles.pre-commit-path-bans | universal | conforms | n/a |

**Straggler (C4):** Joan plan-rubric APPROVED attached; no Excluded-statute list — no stragglers.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited in plan body | — | Cutover consumes `stage_meteorite` contract only |

## Plan adherence

**Stage 1 (mailbox):** `_handle_bound` rebuilt — `subject`+`html` blob → `stage_meteorite(email, mid)` → `_stage_archive_token` → `_finalize_archive`. Mechanical tree + BOT_BLOCKED/scrape helpers deleted; docstring updated; hygiene/unbound/`last_email_check` paths preserved.

**Stage 2 (inbox):** `_land_bound_inbox_message` strips then stages (not raw `land_meteorite`); empty strip early return unchanged; `run_fetch_email` + `land_inbox_message_ids` treat `skipped` or `skip_outcomes` as passed; `create_meteorite_job_from_inbox_message` untouched.

**Stage 3 (contact):** `contact_land_meteorite` requires `source_kind`/`source_id`, assembles blob, calls `stage_meteorite`; Estelle `land_calls` pass `source_kind="slack"` + `message_ts`→`thread_ts`→`channel` fallback.

**Estimate (3):** Matches — three caller rewires on shipped stage contract.

**C6 lenses:** No new layer violations; archive `except` pre-existing; debug gated per plan; no caller-side scrap map duplication.

## Findings

### fix-now

(none)

### discuss

1. **Bound empty-body mailbox messages (Joan plan discuss — now live):** Plan removed empty-body ignore forks. When subject and HTML are both empty, blob is empty → `invoke_stage_meteorite` fails → `_stage_archive_token` → `error` → runner counts `(passed=0, errors=1)` vs old `(passed=1, ignored)`. Inbox stays on error (similar to old ignore). Joan flagged at plan approval; implementation matches that decision. **Confirm Susan accepts the accounting shift** for rare empty bound mail — or add a documented pre-stage empty-blob branch without restoring the heuristic tree.

### advisory

1. **`run_fetch_email` skip-as-passed** — logic added in `run_fetch_email` / `land_inbox_message_ids`; component tests cover `_land_bound_inbox_message` and `land_inbox_message_ids` wiring but not a direct `run_fetch_email` stage-skip → `total_passed` assertion. Low risk given mirrored passed rule in both functions.

2. **Legacy Create API** — `create_meteorite_job_from_inbox_message` still calls `land_meteorite` directly (plan out of scope). Full inbox parity needs a follow-on ticket if desired.

3. **Caller blob shape** — mailbox passes `subject\n\n{raw html}`; inbox passes strip output only. Intentional per plan (strip ownership in inbox); Ruth sees different shapes per ingress surface.

4. **Estelle `slack_sid` empty** — if `message_ts`/`thread_ts`/`channel` all empty, `contact_land_meteorite` returns structured error without staging. Reasonable fail-closed; worth knowing for malformed Slack events.

5. **`asyncio.run` in sync `contact_land_meteorite`** — pre-existing pattern (was used with `land_meteorite`); not introduced by this ticket.

6. **Retired mailbox tests** — `TestAst1090SubjectIsUrl` skipped; mechanical-classify tests rewritten for stage path. Appropriate for cutover.

## What's solid

- Mechanical classify tree fully removed from `meteorite_email.py` (~300 lines); no dead scrape/BOT_BLOCKED imports remain.
- `_stage_archive_token` cleanly bridges stage skip vs land rollup vs error into existing archive contract.
- Inbox skip-as-passed uses both `land.get("skipped")` and `STAGE_METEORITE_CONFIG["skip_outcomes"]` (defensive).
- Contact signature break isolated to Estelle `land_calls` with Slack source handle wiring.
- Tests lock mailbox stage+archive-on-skip, inbox strip→stage, contact source gates, and selected-ids stage path.

## Frame diff

- `src/core/meteorite_email.py`: `_handle_bound` → `stage_meteorite`; add `_stage_archive_token`; delete mechanical classify/scrape/BOT_BLOCKED helpers.
- `src/core/inbox.py`: `_land_bound_inbox_message` / `run_fetch_email` / `land_inbox_message_ids` → stage; skip outcomes count as passed.
- `src/core/contact.py`: `contact_land_meteorite` → `stage_meteorite` with required source handle; Estelle `land_calls` Slack `source_id`.
- Betty merge-tests: `test_meteorite_email.py`, `test_inbox.py`, `test_contact.py` + bible entries.

context_tokens≈45000

---

```
[code-rubric] PROCEED (Commit: 3afaf3e8) caller cutover clean
```
