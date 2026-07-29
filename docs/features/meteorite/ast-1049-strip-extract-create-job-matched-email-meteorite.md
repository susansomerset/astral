# AST-1049 — Strip/extract + create job from matched email via meteorite

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1049/stripextract-create-job-from-matched-email-via-meteorite-bind-email-to  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1044/bind-email-to-candidate  

**Publish ref (origin):** `sub/AST-1044/AST-1049-strip-extract-create-job-matched-email-meteorite`  
**Parent integration ref:** `ftr/AST-1044-bind-email-to-candidate`

Wire Manage Email **Create** so a matched inbox message is strip/extracted (message **subject** included in the HTML), then passed to the existing AST-1042 / AST-1034 meteorite job-create path for that candidate. Operator sees success or a clear failure without leaving the pane. Backend `debug=True` emits Style D found/matched/recorded detail on the create orchestration path.

Boundaries (do **not** implement): reusable lookup / From enrichment (AST-1047 — already on `ftr`); Manage Email rename / match chrome / Create **enablement** stub (AST-1048 — already on `ftr`); Gmail client rewrite; mailbox mutation; Profile/Admin contact editors; inventing a second meteorite create API (call `create_meteorite_job` / existing `POST /api/candidates/<id>/meteorite/jobs` from core).

**Depends on:** AST-1047 + AST-1048 rolled on `origin/ftr/AST-1044-bind-email-to-candidate` (merge that tip before build — Create button stub + `candidate_match` payloads exist). Soft UAT gate: AST-1034 create capability available on the line Susan expects for staging.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `INBOX_CREATE_JOB_CONFIG` (strip tag/attr lists + subject HTML template) | utils |
| `src/external/gmail.py` | Extend `get_message_html` / `GmailMessageHtml` to include `subject` + `from_address` from full-message headers | external |
| `src/core/inbox.py` | Add `strip_extract_email_html` + `create_meteorite_job_from_inbox_message`; `debug=` Style D on create path | core |
| `src/ui/api/api_inbox.py` | `POST /api/admin/inbox/messages/<message_id>/create-job` (`@require_admin`, `ui_llm_debug`) | ui |
| `src/ui/frontend/src/pages/AdminManageEmail.tsx` | Replace Create stub with POST + toast success/failure; in-flight disable | ui |

No new meteorite HTTP blueprint. Do **not** edit `src/core/meteorite.py` create signature (call existing `create_meteorite_job`). Do **not** edit `tests/` / bible.

---

## Stage 1: Config — strip/extract + subject inclusion

**Done when:** `INBOX_CREATE_JOB_CONFIG` is importable from `src.utils.config` with the keys below; no core/UI changes yet.

1. In `src/utils/config.py`, immediately after `CANDIDATE_LOOKUP_CONFIG` (or after `METEORITE_CONFIG` if preferred for adjacency — **use after `CANDIDATE_LOOKUP_CONFIG`** so inbox create stays with the bind epic’s config cluster), add:

```python
# AST-1049: Manage Email Create — strip/extract email HTML + subject inclusion before meteorite job create.
INBOX_CREATE_JOB_CONFIG = {
    # Tags removed entirely (and their children) before job HTML is recorded.
    "strip_tags": (
        "script", "style", "noscript", "iframe", "object", "embed", "link", "meta",
    ),
    # Attribute names removed from every remaining tag (casefold compare).
    "strip_attr_names": (
        "style", "onclick", "onload", "onerror", "onmouseover", "srcset",
    ),
    # True → also drop any attribute whose name starts with "on".
    "strip_on_attrs": True,
    # Format with subject= (HTML-escaped) and body= (already-stripped HTML fragment).
    "subject_html_template": (
        '<header class="email-subject"><h1>{subject}</h1></header>\n'
        '<section class="email-body">{body}</section>'
    ),
}
```

2. If the top-of-file config inventory lists named `*_CONFIG` blocks, add a one-line `INBOX_CREATE_JOB_CONFIG` entry next to `CANDIDATE_LOOKUP_CONFIG` / meteorite bullets.

⚠️ **Decision — hygiene strip, not NLP:** Parent asks for strip/extract + subject-in-content for this epic, not a full routing/classify pipeline. Tag/attr cull + subject wrapper is the concrete extract; do not invent JD section parsers or LLM calls here.

⚠️ **Decision — config owns strip sets:** No inline tag lists in core (§2.1 / no-hardcoded-sets).

---

## Stage 2: Gmail get — subject + From on HTML payload

**Done when:** `get_message_html(message_id)` returns `id`, `html_body`, `subject`, and `from_address` (strings; empty when missing); list metadata unchanged; no core orchestration yet.

1. In `src/external/gmail.py`, extend `GmailMessageHtml`:

```python
class GmailMessageHtml(TypedDict):
    id: str
    html_body: str
    subject: str
    from_address: str
```

2. In `get_message_html`, after fetching `format="full"`, parse headers the same way `_message_metadata` does (`Subject`, `From`) and return them alongside `_extract_html_body(...)`. Keep `require_controlled_external_io("gmail.get_message_html")`.

⚠️ **Decision — extend get, not a second Gmail fetch helper:** Create needs subject + From for strip + rematch. One full get already loads the payload; adding headers avoids a second API round-trip and keeps subject authoritative from Gmail (not the React list row).

3. Do **not** change `list_inbox_messages` metadata shape.

---

## Stage 3: Core strip/extract + create orchestration

**Done when:** Given a Gmail `message_id` whose From uniquely matches a candidate, core returns a meteorite create payload (same fields as `create_meteorite_job` success dict); unmatched/ambiguous From raises `ValueError` with a clear message; empty body after strip raises `ValueError`; with `debug=True`, Style D index lines cover found → matched → extracted → recorded; with `debug=False`, no new debug-contract lines from this path.

1. In `src/core/inbox.py`, update the module docstring to note AST-1049 Create orchestration (still no persistence beyond calling meteorite create).

2. Add public helpers (public-first, above any new private helpers):

```python
def strip_extract_email_html(subject: str, html_body: str) -> str:
    """Cull configured tags/attrs; wrap subject + body per INBOX_CREATE_JOB_CONFIG."""
```

Concrete behavior:

- Lazy-import BeautifulSoup (B1 comment: heavy dep only on create/strip path).
- Parse `html_body` (empty → treat as `""`).
- Decompose/remove every tag whose name casefolds into `INBOX_CREATE_JOB_CONFIG["strip_tags"]`.
- For remaining tags: drop attrs in `strip_attr_names` (casefold); if `strip_on_attrs`, drop any attr starting with `on`.
- `body = soup.decode_contents()` if a body/root exists, else `str(soup)` — use the culled fragment’s inner HTML (prefer `soup.body.decode_contents()` when `<body>` present, else full culled markup string).
- HTML-escape `subject` for attribute/text safety (`html.escape(subject or "", quote=True)`).
- Return `INBOX_CREATE_JOB_CONFIG["subject_html_template"].format(subject=escaped_subject, body=body)`.
- If the returned string is empty/whitespace after strip → callers treat as invalid (raise in orchestrator).

3. Add public:

```python
def create_meteorite_job_from_inbox_message(
    message_id: str,
    *,
    debug: bool = False,
) -> dict:
```

Concrete steps:

1. `mid = (message_id or "").strip()`; empty → `ValueError("message_id is required")`.
2. `logger.set_debug_flag(debug)`.
3. `payload = get_message_html(mid)` (core wrapper → external).
4. Rematch: `cid = get_candidate_id_for_query(payload.get("from_address") or "", debug=False)` — do **not** trust a client-supplied candidate id.
   - If `cid is None` → `ValueError("message is not matched to a candidate")`.
5. `html = strip_extract_email_html(payload.get("subject") or "", payload.get("html_body") or "")`.
   - If not `html.strip()` → `ValueError("stripped email HTML is empty")`.
6. `from src.core.meteorite import create_meteorite_job` (module-level import is fine if no cycle; otherwise late import with cycle comment).
7. `result = create_meteorite_job(cid, html, debug=debug)`.
8. When `debug=True`, emit four Style D steps (or fewer if you combine found+matched — prefer **four** clear outcomes):

| index | outcome | detail |
|-------|---------|--------|
| 1/4 | `found` | `message_id`, subject (truncated), raw html length |
| 2/4 | `matched` | `astral_candidate_id=cid`, from_address (truncated) |
| 3/4 | `extracted` | stripped html via `truncate_debug_content` / `debug_detail` lines |
| 4/4 | `recorded` | `astral_job_id`, company, state |

Use `debug_index` / `debug_detail` / `truncate_debug_content` from `src.utils.logging`. No new lines when `debug=False`.

9. Return `result` (full core dict is fine for the API to project).

⚠️ **Decision — rematch on Create:** Parent forbids Create for unmatched/ambiguous senders. Re-running `get_candidate_id_for_query` on Gmail From at Create time prevents a stale list row or forged client `candidate_id` from creating orphan meteorite jobs.

⚠️ **Decision — orchestration in `inbox.py`:** Email fetch + bind live here; meteorite stays create-only. UI → core inbox → core meteorite; UI never imports Gmail or data.

⚠️ **Decision — do not call the HTTP meteorite route from core:** Call `create_meteorite_job` directly (import-discipline). The existing `POST /api/candidates/.../meteorite/jobs` remains for other authenticated callers; Manage Email uses the admin inbox create-job route below.

---

## Stage 4: Admin API — Create-job endpoint

**Done when:** Authenticated admin `POST /api/admin/inbox/messages/<message_id>/create-job` creates a meteorite job and returns 201 with job ids; unmatched → 400; missing id → 400; Gmail/upstream failures → 502; unauthenticated/non-admin → 401/403; `debug` gated via `ui_llm_debug`.

1. In `src/ui/api/api_inbox.py`, import `create_meteorite_job_from_inbox_message` from `src.core.inbox`.

2. Add:

```python
@inbox_bp.route("/messages/<message_id>/create-job", methods=["POST"])
@require_admin
def inbox_create_job_from_message(message_id: str):
    ...
```

Handler:

- `mid = (message_id or "").strip()`; empty → 400 `{"error": "message_id is required"}`.
- `debug = ui_llm_debug(explicit_debug=(request.get_json(silent=True) or {}).get("debug") is True)` — also accept query `?debug=1` the same way list does **or** JSON body `debug`; pick **one** and document it in the plan: **use JSON body `debug` OR query, with `ui_llm_debug(explicit_debug=...)` matching list’s query pattern.** Concrete: mirror list — `explicit_debug=request.args.get("debug", "").lower() in ("1", "true", "yes") or bool((request.get_json(silent=True) or {}).get("debug"))`.
- `try: result = create_meteorite_job_from_inbox_message(mid, debug=debug)`
- Map:
  - `ValueError` → 400 `{"error": str(e)}`
  - other `Exception` → `logger.warning(...)` → 502 `{"error": str(e)}`
- Success → **201**:

```json
{
  "astral_job_id": "...",
  "company": "meteorite-<candidate_id>",
  "state": "JD_READY",
  "latest_score": 10.0,
  "company_inserted": true,
  "astral_candidate_id": "<cid>"
}
```

Include `astral_candidate_id` from the rematch (add to return in core if needed — either extend the returned dict in Stage 3 with `"astral_candidate_id": cid` or read `company` / ensure path; **prefer** adding `"astral_candidate_id": cid` onto the dict returned by `create_meteorite_job_from_inbox_message`).

3. Do **not** remove `@require_admin` from existing inbox routes. Do **not** add a React-callable path under `/api/candidates/...` for this flow (admin pane stays on admin inbox).

---

## Stage 5: Manage Email — wire Create control

**Done when:** Clicking enabled **Create** on a matched message POSTs create-job, shows a success toast with `astral_job_id` (and candidate id if useful), or an error toast with the API error; button disables while the request is in flight; unmatched Create remains disabled; browse still works.

1. In `AdminManageEmail.tsx`, replace the stub:

```ts
function onCreateClick() {}
```

with an async handler that:

- No-ops if `!selectedMatched` or `!selectedId` or already `createBusy`.
- Sets `createBusy` true; clears prior toast.
- `POST /api/admin/inbox/messages/${encodeURIComponent(selectedId)}/create-job` with `Content-Type: application/json` and body `{}` (debug comes from deploy/`ui_llm_debug` on server; do not invent a React debug toggle).
- On `r.ok`: parse JSON; toast success e.g. `Created job {astral_job_id}` (`variant: "success"`).
- On failure: parse `error` string when present; toast `variant: "error"`.
- `finally`: `createBusy` false.

2. Bind `disabled={!selected?.candidate_match?.matched || createBusy}` (keep matched gate from AST-1048).

3. Do **not** strip HTML in the browser. Do **not** POST `html_body` to `/api/candidates/.../meteorite/jobs` from React — server owns strip + create.

⚠️ **Decision — admin inbox create-job only:** Keeps Gmail I/O and rematch on the server; React stays thin (pattern.ui.admin-endpoint / import-direction).

---

## Out of scope (do not implement here)

- Changing match rules, `CANDIDATE_LOOKUP_CONFIG`, or list enrichment (AST-1047).
- Renaming nav / match column chrome beyond Create wiring (AST-1048).
- Reimplementing `create_meteorite_job` / meteorite ensure (AST-1041 / AST-1042).
- Auto-create on inbox arrival; Gmail label/archive/delete.
- Multi-candidate picker; creating jobs when rematch returns `None`.
- Editing `tests/` or `docs/test-bible/**` (Betty after Code Complete).

---

## Self-Assessment

**Scope:** `Single-Component` — config + gmail get header fields + inbox strip/orchestrate + one admin POST + Create button wire; reuses existing `create_meteorite_job`.

**Conf:** `high` — AST-1048 stub and AST-1042 create API are on `ftr`; strip/extract is a bounded HTML cull + subject template; rematch reuses AST-1047 helper.

**Risk:** `Medium` — wrong strip could drop JD text or leave unsafe markup; rematch bugs would block Create or (if skipped) risk wrong candidate — rematch + empty-html guard mitigate; does not touch non-meteorite job flows.

---

## Code rules self-review

- **§2.1 / no-hardcoded-sets:** Strip tags/attrs + subject template only in `INBOX_CREATE_JOB_CONFIG`.
- **§1.5.1 / debug-contract-gated:** Create orchestration accepts `debug=`; Style D only when true; API uses `ui_llm_debug`.
- **§3.3 import-direction:** UI → core inbox → core meteorite / external gmail via existing inbox wrappers; UI does not import Gmail or data.
- **§3.2 bright line:** Strip/orchestration in core; Gmail stays external.
- **require_auth / require_admin:** New route stays `@require_admin` on `/api/admin/inbox/**`.
- **§1.3 DRY:** Call existing `create_meteorite_job`; do not duplicate ensure/insert SQL.
- **Out of scope enforced:** no lookup redesign, no mailbox mutation, no second create HTTP surface for React.

---

## Review

**Publish ref:** `sub/AST-1044/AST-1049-strip-extract-create-job-matched-email-meteorite`

**Product tip (pre-docs):** `ad5e0ce6` (`merge-tests(AST-1049)`; product `code(AST-1049)` @ `09152424`)

**Overall:** DISCUSS — no fix-now

**1049-only product delta (`09152424`):** `INBOX_CREATE_JOB_CONFIG`; `get_message_html` + `GmailMessageHtml` subject/From; `strip_extract_email_html` + `create_meteorite_job_from_inbox_message` (rematch + Style D + `create_meteorite_job`); `POST .../create-job` `@require_admin`; Manage Email Create POST + toast + `createBusy`.

### discuss
- **Three-dot vs 1049-only:** `origin/dev...origin/<publish-ref>` includes rolled-up AST-1047/1048. Statute substance for this review is judged on `09152424` + plan AC4–5; sibling commits are not re-litigated as 1049 fix-now.
- **Empty-html guard vs subject template:** After wrap, `subject_html_template` always yields non-whitespace markup even when body/subject are empty, so the post-strip `html.strip()` guard rarely trips. Plan-conforming; optional later tighten (check culled body before wrap) is out of scope unless UAT shows empty JD creates.

### acceptable
- Rematch ignores any client candidate id; Create blocked when From does not uniquely match — matches parent unmatched/ambiguous ban.
- Create path Style D uses found → matched → extracted → recorded (plan bible); child AC shorthand “found/matched/recorded” is covered; `extracted` is the planned middle step.
- Parallel email denylist vs page `html_cull` (Joan discuss) — dedicated inbox config kept; no playwright import from inbox.

### Statutes checked

| id | applies | verdict | note |
|---|---|---|---|
| astral.agent.confidence-bounds | yes | conforms | No agent/do_task |
| astral.agent.do-task-delegation | yes | conforms | Untouched |
| astral.agent.grade-vector-validation | yes | conforms | Untouched |
| astral.batch.batch-id-first | yes | conforms | No batch |
| astral.batch.batch-id-format | yes | conforms | No batch |
| astral.batch.claim-process-release | yes | conforms | Untouched |
| astral.batch.entity-agent-responses-latest-only | yes | conforms | Untouched |
| astral.config.config-source-of-truth | yes | conforms | `INBOX_CREATE_JOB_CONFIG` owns strip + template |
| astral.config.pass-threshold-vs-score-floor | yes | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | yes | conforms | No new secrets |
| astral.debug.no-repo-root-artifacts-dir | no | n/a | paths miss |
| astral.debug.spikes-under-debug-dir | yes | conforms | Feature plan only; no spikes |
| astral.docs.features-single-file-per-ticket | yes | conforms | One plan file for AST-1049 |
| astral.git.betty-no-src-or-features | yes | conforms | Betty tests/bible only on tip |
| astral.git.engineer-test-tree-ban | yes | conforms | Engineer `09152424` has no tests/bible |
| astral.layers.core-vs-external-bright-line | yes | conforms | Strip/orchestrate core; Gmail external |
| astral.layers.import-direction | yes | conforms | UI → core inbox → meteorite/gmail |
| astral.layers.scripts-exempt-from-layer-rules | no | n/a | layers miss |
| astral.layers.ui-config-driven-business-logic | yes | conforms | Rematch/strip server-side; React POST/toast |
| astral.patterns.coat-check-never-store-empty | yes | conforms | Untouched |
| astral.patterns.render-verdict-orchestrates-consult | yes | conforms | Untouched |
| astral.patterns.require-auth-on-protected-endpoints | yes | conforms | `@require_admin` on create-job |
| astral.standards.data-raises-caller-logs | yes | conforms | ValueError → 400; other → 502 + log |
| astral.standards.database-header-inventory | no | n/a | layers miss |
| astral.standards.debug-contract-gated | yes | conforms | Style D only when debug; `ui_llm_debug` |
| astral.standards.dry-and-focused-functions | yes | conforms | Calls existing `create_meteorite_job` |
| astral.standards.in-scope-only | yes | conforms | Create wire only |
| astral.standards.logging-via-utils | yes | conforms | get_logger / debug helpers |
| astral.standards.no-cross-contamination | yes | conforms | Layers respected |
| astral.standards.no-hardcoded-sets | yes | conforms | Tag/attr lists in config |
| astral.standards.public-then-helpers | yes | conforms | Public strip + orchestrate |
| astral.standards.utils-data-late-import-only | yes | conforms | No new utils→data |
| astral.state.core-decides-transitions | yes | conforms | Reuses meteorite create carve-out |
| astral.state.job-prior-states-enforced | yes | conforms | No prior expansion |
| astral.state.no-daisy-chain-in-run | yes | conforms | Untouched |
| astral.ui.frontend-file-placement | yes | conforms | Wire existing AdminManageEmail only |
| astral.ui.naming-conventions | yes | conforms | snake_case create-job; PascalCase page |
| astral.ui.single-gunicorn-worker | yes | conforms | Untouched |
| orch.git.betty-merge-tests-one-sha | yes | conforms | One merge-tests tip |
| orch.git.commit-vocabulary | yes | conforms | code/test/docs/merge-tests |
| orch.git.flow-direction-inviolable | yes | conforms | sub under ftr |
| orch.git.ftr-sub-topology | yes | conforms | `sub/AST-1044/AST-1049-…` |
| orch.git.merge-on-checkout | yes | conforms | Review merged ftr + publish tip |
| orch.git.no-cherry-pick-rebase-force | yes | conforms | No forbidden ops |
| orch.git.no-dev-agent-branches | yes | conforms | On sub/* |
| orch.git.one-epic-worktree-per-parent | yes | conforms | astral-AST-1044 |
| orch.git.three-permanent-branches | yes | conforms | Untouched |
| orch.pipeline.call-susan-for-product-decisions | yes | conforms | No product ambiguity in delta |
| orch.pipeline.plan-is-bible | yes | conforms | Stages match `09152424` |
| orch.pipeline.project-scoped-queues | yes | conforms | Meteorite |
| orch.pipeline.status-gates-skill-entry | yes | conforms | Tests Passed → review |
| orch.roles.archie-approves-statutes | yes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | yes | conforms | Betty owned test commit |
| orch.roles.chuckles-never-ticket-assignee | yes | conforms | Engineer implementer path |
| orch.roles.engineer-assignee-through-resolve | yes | conforms | Review does not steal implementer role |
| orch.roles.pre-commit-path-bans | yes | conforms | No banned paths in product commit |

**Active statutes:** 56 · **Applicable (yes):** 53 · **n/a:** 3 · **fix-now:** 0 · **discuss:** 2

— Radia
