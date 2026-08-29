# AST-1537 — Email header+body HTML for land/qualify

**Linear:** [AST-1537](https://linear.app/astralcareermatch/issue/AST-1537/email-headerbody-html-for-landqualify-manage-email-gives-html-for-the)  
**Parent:** [AST-1533](https://linear.app/astralcareermatch/issue/AST-1533/manage-email-gives-html-for-the-body-of-the-message-not-for-the-header) — Manage Email gives HTML for the body of the message, not for the header, and it must include both.  
**Publish ref:** `sub/AST-1533/AST-1537-email-header-body-html-land-qualify`

Owns the shared header+body HTML assembly and wires every email land path that feeds `stage_meteorite` / qualify so Ruth sees From/To/Subject/(Date) with the body. Does not own Manage Email React chrome or the copy button (sibling AST-1538).

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/utils/config.py` (extend inbox email HTML wrapper literals for From/To/Subject/(Date)+body)
- `src/core/inbox.py` (shared assemble/strip path for land + message get)
- `src/core/meteorite_email.py` (bound blob uses shared assembly)
- `src/external/gmail.py` (Date on full-message HTML payload when available)
- `src/ui/api/api_inbox.py` (expose assembled header+body HTML on message get)

All Files Changed / Stages stay inside that set.

**Out of scope (siblings / keep):**

- `AdminManageEmail.tsx` / `App.css` — **AST-1538** (render/copy/dark purple).
- Non-email meteorite ingress (paste / scrap / Contact / Slack) — unchanged.
- `consult.py` `_qualify_meteorite_email_subject` — do **not** edit; keep template markup that scraper already matches (see Stage 1 decision).
- New strip tag/attr sets beyond the existing AST-1049 cull lists.

**Depends on:** none (bang! for AST-1538). Parent ftr may be unpublished; `sync-child.sh` already skips missing `origin/ftr/AST-1533`.

**AC partition (this ticket):** Parent AC4 + AC5 only — email land → qualify input includes headers+body; non-email ingress unchanged. Parent AC1–3 / AC6 are AST-1538 (or shared UI).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend `INBOX_CREATE_JOB_CONFIG` wrapper to From/To/Subject/(Date)+body; refresh header comment | utils |
| `src/external/gmail.py` | Add `date` on `GmailMessageHtml`; copy Date header on `get_message_html` | external |
| `src/core/inbox.py` | Expand `strip_extract_email_html` headers; land/create call sites; `get_message_with_assembled_html` for admin get | core |
| `src/core/meteorite_email.py` | `_handle_bound` uses shared strip/assemble instead of plain subject prepend | core |
| `src/ui/api/api_inbox.py` | Message GET returns core assembled payload (thin) | ui |

## Stage 1: Config — header+body wrapper literal

**Done when:** `INBOX_CREATE_JOB_CONFIG` owns a single format template with placeholders `{from_address}`, `{to_address}`, `{subject}`, `{date}`, `{body}`; file header comment for that block mentions AST-1537 header fields; `python3 -m py_compile src/utils/config.py` succeeds.

1. In `src/utils/config.py`, update the inventory line for `INBOX_CREATE_JOB_CONFIG` (near the other config block comments) from “subject wrapper (AST-1049)” to note strip/extract + **header+body** wrapper (AST-1049 / AST-1537).

2. In `INBOX_CREATE_JOB_CONFIG`, **replace** the `subject_html_template` value (keep the **key name** `subject_html_template` — Betty’s config tests and bible already key on it; renaming is out of scope / would invent a second key). New value exactly:

```python
    "subject_html_template": (
        '<header class="email-headers">'
        '<p class="email-from"><span class="email-label">From:</span> {from_address}</p>'
        '<p class="email-to"><span class="email-label">To:</span> {to_address}</p>'
        '<div class="email-subject"><h1>{subject}</h1></div>'
        '<p class="email-date"><span class="email-label">Date:</span> {date}</p>'
        '</header>\n'
        '<section class="email-body">{body}</section>'
    ),
```

Update the inline comment above that key from “Format with subject= … and body=” to: Format with HTML-escaped `from_address` / `to_address` / `subject` / `date` and already-stripped `body`.

⚠️ **Decision — keep key name `subject_html_template`:** Parent asked to *extend* the existing wrapper literal, not invent a parallel config key. Renaming would force Betty-side bible/test key churn without product value.

⚠️ **Decision — preserve `class="email-subject"` + inner `<h1>`:** `consult._qualify_meteorite_email_subject` scrapes `class="email-subject"…<h1>…</h1>` (AST-1197). Consult is out of this ticket’s Scope; changing that selector would break title-source Style D. From/To/Date live as sibling elements under `email-headers`.

⚠️ **Decision — always emit the Date row:** Template always includes `{date}`. When Gmail omits Date, core passes `""` and the label still appears with an empty value. Avoids a second template or conditional markup in config.

## Stage 2: Gmail — Date on full-message HTML payload

**Done when:** `GmailMessageHtml` includes `date: str`; `get_message_html` sets it from the raw `Date` header via existing `_header_map` (empty string when missing); list metadata path unchanged; `python3 -m py_compile src/external/gmail.py` succeeds.

1. In `src/external/gmail.py`, extend `GmailMessageHtml` — insert `date: str` immediately after `to_address`:

```python
class GmailMessageHtml(TypedDict):
    id: str
    html_body: str
    subject: str
    from_address: str
    to_address: str
    date: str
```

2. In `get_message_html`, after reading headers with `_header_map`, add `"date": headers.get("date", "")` to the returned dict (same empty-string convention as list `_message_metadata`). Do **not** change `format=` / part extraction / other keys.

3. Update the `get_message_html` docstring to mention Subject/From/To/**Date**.

⚠️ **Decision — external-only Date read:** Full-message `format="full"` already returns all headers; `_header_map` already lowercases names. No new Gmail API knobs. List path already exposes `date` — do not touch list.

## Stage 3: Inbox — shared strip/assemble + land/create callers + get helper

**Done when:** `strip_extract_email_html` escapes and embeds From/To/Subject/Date into the config template; `_land_bound_inbox_message` and `create_meteorite_job_from_inbox_message` pass those fields from the Gmail payload; a public core helper returns the get payload plus `assembled_html` for the admin API; empty-strip guards unchanged; `python3 -m py_compile src/core/inbox.py` succeeds.

1. Change `strip_extract_email_html` signature to:

```python
def strip_extract_email_html(
    subject: str,
    html_body: str,
    *,
    from_address: str = "",
    to_address: str = "",
    date: str = "",
) -> str:
```

Keep the existing BeautifulSoup strip/cull + `normalize_pasted_list_email_html(body)` path unchanged.

2. After cull/normalize, HTML-escape **all four** header fields with `html_module.escape(..., quote=True)` (same as today’s subject). Return:

```python
return INBOX_CREATE_JOB_CONFIG["subject_html_template"].format(
    from_address=escaped_from,
    to_address=escaped_to,
    subject=escaped_subject,
    date=escaped_date,
    body=body,
)
```

Update the function docstring to say header+body wrap per `INBOX_CREATE_JOB_CONFIG`, not subject-only.

3. In `_land_bound_inbox_message`, after `payload = get_message_html(mid)`, replace the subject-only strip call with:

```python
html = strip_extract_email_html(
    payload.get("subject") or "",
    payload.get("html_body") or "",
    from_address=payload.get("from_address") or "",
    to_address=payload.get("to_address") or "",
    date=payload.get("date") or "",
)
```

Leave empty-html error return and `stage_meteorite(..., source_kind="email", ...)` unchanged.

4. In `create_meteorite_job_from_inbox_message`, same header kwargs on the `strip_extract_email_html` call (still rematch From-then-To before strip; still `land_meteorite` after — do not retarget that legacy path to stage).

5. Add a public helper **immediately after** `get_message_html` (public-then-helpers: this is public API for the admin get):

```python
def get_message_with_assembled_html(message_id: str) -> dict:
    """Gmail HTML payload plus assembled_html (header+body strip/wrap)."""
    payload = dict(get_message_html(message_id))
    payload["assembled_html"] = strip_extract_email_html(
        payload.get("subject") or "",
        payload.get("html_body") or "",
        from_address=payload.get("from_address") or "",
        to_address=payload.get("to_address") or "",
        date=payload.get("date") or "",
    )
    return payload
```

`html_body` remains the **raw** Gmail HTML fragment. `assembled_html` is the only field operators/sibling AST-1538 should render/copy.

6. Update the module docstring note for AST-1049 / strip ownership to mention AST-1537 header+body assembly shared by land and message get.

⚠️ **Decision — new `assembled_html` key, keep raw `html_body`:** Replacing `html_body` with assembled markup would double-wrap if any caller stripped again, and would hide the raw fragment. Sibling AST-1538 is told (by parent Scope) to render assembled HTML from the get API — that field is `assembled_html`.

## Stage 4: meteorite_email — bound blob uses shared assembly

**Done when:** `_handle_bound` no longer builds `f"{subject}\n\n{html}"`; it calls `strip_extract_email_html` with the same header kwargs as inbox land; archive / stage / debug behavior otherwise unchanged; `python3 -m py_compile src/core/meteorite_email.py` succeeds.

1. In `src/core/meteorite_email.py`, extend the existing `from src.core.inbox import …` to also import `strip_extract_email_html` (already imports `get_message_html`).

2. Inside `_handle_bound`, after a successful `payload = get_message_html(mid)`, **replace** the “Caller-owned blob (no strip_extract …)” block with:

```python
blob = strip_extract_email_html(
    payload.get("subject") or "",
    payload.get("html_body") or "",
    from_address=payload.get("from_address") or "",
    to_address=payload.get("to_address") or "",
    date=payload.get("date") or "",
)
```

Then `stage_meteorite(cid, blob, source_kind="email", source_id=mid, debug=debug)` as today.

3. If `blob` is empty/whitespace after assemble, keep current stage call behavior (do **not** add a new empty-html early-return unless one already exists — today empty still stages). Do not invent archive-policy changes.

4. Refresh the one-line comment that said inbox owns strip / no strip_extract here: mailbox bound land now uses the **same** inbox-owned strip helper (AST-1537).

⚠️ **Decision — mailbox lands through strip, not plain prepend:** Parent Technical scope requires `meteorite_email` bound blob to use shared header+body assembly. Plain `subject\n\nhtml` was the AST-1531 interim; this ticket retires it so qualify sees the same HTML shape as Manage Email Land / fetch_email.

## Stage 5: api_inbox — expose assembled HTML on message get

**Done when:** `GET /api/admin/inbox/messages/<message_id>` returns the dict from `get_message_with_assembled_html` (includes `assembled_html` + raw fields + `date`); `@require_admin` / 400 / 502 mapping unchanged; `python3 -m py_compile src/ui/api/api_inbox.py` succeeds.

1. In `src/ui/api/api_inbox.py`, change the import from `get_message_html` to `get_message_with_assembled_html` (keep other inbox imports).

2. In `inbox_get_message`, replace `payload = get_message_html(mid)` with `payload = get_message_with_assembled_html(mid)`; still `return jsonify(payload), 200` on success.

⚠️ **Decision — no React edit here:** Modal still reads `html_body` until AST-1538. Bang! means sibling waits on this API field; do not absorb modal/copy/chrome into this plan.

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1533/AST-1537-email-header-body-html-land-qualify`.
- Do not edit `tests/`, `docs/test-bible/**`, React, or consult.
- If `GmailMessageHtml` / strip call sites have drifted from this plan after `sync-child.sh`, stop and comment on **AST-1533** with the stage-blocked template — do not improvise.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1537
**Overall:** APPROVED
**Publish ref:** `sub/AST-1533/AST-1537-email-header-body-html-land-qualify` @ `6a3a4260d9a4a70a015c68b4a7bb6ec026629ce9`

## Traceability
AC4 → Stages 1–5 (config header+body template, gmail `date`, inbox shared strip on land/create/get, `meteorite_email` bound blob, api `assembled_html`); AC5 → Scope gate + email-only paths (paste/scrap/consult/React explicitly untouched).

## Findings

### acceptable
- **Location:** Plan structure — no formal `## Self-assessment` block
- **Finding:** Confidence/unknowns are implicit in stage ⚠️ decisions and estimate confirm, not a labeled self-assessment section.
- **Recommendation:** Optional polish only; stages and decisions are specific enough to build.

### acceptable
- **Location:** Stage 1 — always emit Date row
- **Finding:** Template renders `Date:` even when Gmail omits the header (empty value).
- **Recommendation:** Documented tradeoff; fine for AC4 qualify input; sibling AST-1538 can handle display nuance for AC1.

context_tokens≈42000

## Review

**Build tip:** `origin/sub/AST-1533/AST-1537-email-header-body-html-land-qualify` @ `fbfa03f0`
**Stages:** config wrapper → Gmail `date` → inbox strip/land/create/`assembled_html` → meteorite_email shared assemble → api_inbox get

## Radia review

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1537
**Publish ref:** `sub/AST-1533/AST-1537-email-header-body-html-land-qualify` @ `1b2c939ddd5c076723474a4265f41732b78e6f3f`
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no `src/core/agent*` or agent prompt paths in diff |
| astral.agent.do-task-delegation | scoped | not-applicable | no `do_task` / delegation changes |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade-vector / validation paths |
| astral.batch.batch-id-first | scoped | not-applicable | no batch claim/dispatch paths |
| astral.batch.batch-id-format | scoped | not-applicable | no batch id formatting |
| astral.batch.claim-process-release | scoped | not-applicable | no entity claim/release helpers |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no entity-agent-response persistence |
| astral.config.config-source-of-truth | scoped | conforms | `INBOX_CREATE_JOB_CONFIG["subject_html_template"]` extended in config; callers read template |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no secrets/env wiring |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no repo-root artifact dirs |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no spike/debug scripts |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch seed paths |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no `run_next` / chain authority |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single plan doc `docs/features/meteorite/ast-1537-*.md` |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty tip commits touch only `tests/**` + `docs/test-bible/**` |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer `code()` commits exclude test-tree; Betty `test()` + `merge-tests()` own bible/tests |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Gmail I/O stays external; core owns strip/assemble; UI thin over core |
| astral.layers.import-direction | scoped | conforms | `inbox`→`external.gmail`; `api_inbox`→`core.inbox`; no UI→data/external |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no `scripts/**` changes |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | no hardcoded business state in frontend (React untouched) |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check / storage paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | conforms | `consult.py` untouched; `email-subject`+`<h1>` preserved for scraper |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | `inbox_get_message` still `@require_admin`; no new routes |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed JSON |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no catalog overrides |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no boot/hot-path seed |
| astral.seed.define-approved | scoped | not-applicable | no define/seed approval flow |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no operator seed rows |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no coverage-join seed |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no `src/data/**` changes |
| astral.standards.database-header-inventory | scoped | not-applicable | no DB/migration changes |
| astral.standards.debug-contract-gated | scoped | conforms | no new debug emission; existing `create_meteorite_job_from_inbox_message` debug indices unchanged |
| astral.standards.dry-and-focused-functions | scoped | conforms | single shared `strip_extract_email_html` wired land/create/get/mailbox |
| astral.standards.in-scope-only | scoped | conforms | diff limited to scope-gate files; React/consult/non-email ingress untouched |
| astral.standards.logging-via-utils | scoped | conforms | `get_logger` only; no `print()` / stdlib logging |
| astral.standards.names-not-ticket-ids | scoped | conforms | no ticket ids in identifiers |
| astral.standards.no-cross-contamination | scoped | conforms | email assembly isolated to inbox/config/gmail/api paths |
| astral.standards.no-hardcoded-sets | scoped | conforms | template/strip sets remain config-owned |
| astral.standards.public-then-helpers | scoped | conforms | `get_message_with_assembled_html` placed after `get_message_html` per plan |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no utils→data touches |
| astral.state.core-decides-transitions | scoped | not-applicable | no state transition map edits |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job prior-state enforcement |
| astral.state.no-daisy-chain-in-run | scoped | conforms | still `stage_meteorite` / `land_meteorite`; no new daisy-chain |
| astral.ui.frontend-file-placement | scoped | not-applicable | no `src/ui/frontend/**` |
| astral.ui.naming-conventions | scoped | conforms | `assembled_html`, `email-headers` naming consistent |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no worker/config server changes |
| orch.git.betty-merge-tests-one-sha | universal | conforms | tip `merge-tests(AST-1537): origin/tests bda5e714` |
| orch.git.commit-vocabulary | universal | conforms | `code`/`test`/`docs`/`merge-tests` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | `sub/AST-1533/AST-1537-*` publish ref |
| orch.git.ftr-sub-topology | universal | conforms | child on `sub/<parent>/…` |
| orch.git.merge-on-checkout | universal | conforms | no merge/rebase violations in reviewed commits |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no forbidden git ops in diff |
| orch.git.no-dev-agent-branches | universal | conforms | no agent-named branches |
| orch.git.one-epic-worktree-per-parent | universal | conforms | review in `astral-AST-1533` worktree |
| orch.git.three-permanent-branches | universal | conforms | feature branch topology respected |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | product tradeoffs documented in plan ⚠️ decisions |
| orch.pipeline.plan-is-bible | universal | conforms | five stages land as specified |
| orch.pipeline.project-scoped-queues | universal | conforms | scoped child under AST-1533 |
| orch.pipeline.status-gates-skill-entry | universal | conforms | reviewed at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | no new/changed statutes |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty manifest + revised component tests on tip |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Ada (engineer) |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada assignee at Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | no banned-path commits evident |

**Active-set count:** 64 rows from `canon/statutes/README.md` § Harvested corpus + universal (registry reports 65; no extra active id beyond this table on review tree).

## Pattern conformance

none cited

## Plan adherence

Stages 1–5 implemented on publish tip: config `subject_html_template` extended with From/To/Subject/Date+body placeholders (key name preserved); `GmailMessageHtml.date` + `get_message_html` Date header; `strip_extract_email_html` header kwargs on land/create; new `get_message_with_assembled_html`; `meteorite_email._handle_bound` retires plain `subject\n\nhtml` prepend; `api_inbox` GET returns assembled payload. Scope gate honored — no React, `consult.py`, or non-email ingress. Estimate **3** matches footprint (five `src/` modules + Betty test/bible pass). Cross-ticket boundary clean — AST-1538 UI deferred; `html_body` raw + `assembled_html` split documented.

**Joan plan-rubric:** APPROVED @ `6a3a4260`; no Excluded-statute attachment → no straggler callout (`no plan-rubric Excluded list attached`).

**C6 lenses (§5a–§5g):** Imports/layers clean (B1 lazy bs4 comment retained; UI→core only). No silent failure, no new `print()`, no debug-contract regressions on touched paths. Gmail external change is non-LLM — §5g N/A. Header fields HTML-escaped; body remains stripped fragment (pre-existing AST-1049 contract).

## Findings

(none — no fix-now / discuss / advisory blockers)

## What's solid

- Shared assembly path unifies Manage Email land, legacy create, mailbox bound stage, and admin GET — qualify/Ruth see one HTML shape.
- Preserved `class="email-subject"` + inner `<h1>` protects `consult._qualify_meteorite_email_subject` without editing consult (AST-1197).
- Betty manifest narrows eight component classes; revised asserts cover escaping, header classes, and mailbox non-prepend regression.
- `assembled_html` vs raw `html_body` split avoids double-wrap and gives AST-1538 a stable render/copy field.

## Frame diff

Prior issue-doc stub (`docs(AST-1537): review stub — build complete` @ `fbfa03f0`) covered product code only. Tip adds:

- `test(AST-1537): header+body email HTML land/qualify coverage` — revised/new tests in `tests/component/{core,external,ui/api,utils}/`
- `docs/test-bible/{core,inbox,meteorite_email,external/gmail,ui/api/api_inbox,utils/config}.md` — AST-1537 manifest blocks
- `merge-tests(AST-1537): origin/tests bda5e714` — Betty merge SHA on publish ref

Product `src/**` unchanged since `fbfa03f0`.

## Notes

- C7 complete — Chuckles may append, `docs()` push, post slim upshot, move to **Review Posted** → **resolve-child** (PROCEED) or UT if no findings.
- Downstream **AST-1538** must switch modal/copy to `assembled_html` (out of scope here; API field ready).

context_tokens≈38000
