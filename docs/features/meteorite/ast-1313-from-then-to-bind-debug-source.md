# AST-1313 — From-then-To bind + debug source

**Linear:** [AST-1313](https://linear.app/astralcareermatch/issue/AST-1313/from-then-to-bind-debug-source-email-bind-where-email-is-in-the-to)
**Parent:** [AST-1308](https://linear.app/astralcareermatch/issue/AST-1308/email-bind-where-email-is-in-the-to-field-alone) — Email bind where email is in the To: field (alone)
**Publish ref:** `origin/sub/AST-1308/AST-1313-from-then-to-bind-debug-source`

After sibling **AST-1312** put raw `to_address` on mailbox list/get rows, this ticket owns the single bind rule: a unique **From** hit still wins; otherwise **To** binds only when exactly one address remains after ignoring the configured Astral inbox; that unique lookup hit is a first-class `candidate_match`. List enrichment, create rematch, and every consumer that already reads `candidate_match` (Avail, gaze_email, Land Meteorite, Manage Email) use that rule. Style D records which header bound. This ticket does **not** expose To on mailbox rows, does **not** add Manage Email chrome, and does **not** own ingest/scrape/create beyond who is bound.

**Depends on:** AST-1312 `to_address` on `GmailInboxMessage` / `GmailMessageHtml` (User Testing on `origin/sub/AST-1308/AST-1312-mailbox-to-on-list-and-get-payloads`, rolled on `origin/ftr/AST-1308-email-bind-where-email-is-in-the-to-field-alone`). Do not re-implement AST-1312.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `INBOX_BIND_CONFIG` (header order + inbox identity alias of `GAZE_EMAIL_CONFIG["account_address"]`); one module-docstring line | utils |
| `src/core/inbox.py` | Replace From-only `_candidate_match_for_from` with one From-then-To helper; list enrichment + create rematch both call it; Style D bind source | core |

**No changes expected:** `src/external/gmail.py` (AST-1312 already owns `to_address`), `src/core/candidate.py` (`get_candidate_id_for_query` reused as-is), `src/core/gaze_email.py` (already filters on `candidate_match` from `list_inbox_messages`), `src/ui/api/api_inbox.py` (already jsonifies list rows; `@require_admin` stays), `src/ui/frontend/src/pages/AdminManageEmail.tsx` (already renders `candidate_match`; no To rules, no new column), `tests/` / `docs/test-bible/**` (Betty after Code Complete).

**Do not add files.** If a step cannot be executed in the files above, stop and comment on **AST-1308** with the stage-blocked template.

## Stage 1: `INBOX_BIND_CONFIG`

**Done when:** `src/utils/config.py` defines `INBOX_BIND_CONFIG` with `header_order == ("from", "to")` and `inbox_address` equal to `GAZE_EMAIL_CONFIG["account_address"]`. No core/UI callers yet. `python3 -m py_compile src/utils/config.py` succeeds (repo venv: `~/astral/.venv/bin/python` if present, else `python3`).

1. In the `src/utils/config.py` module docstring **Config sections** list, add this line immediately after the existing `INBOX_CREATE_JOB_CONFIG` line:

```
  INBOX_BIND_CONFIG — From-then-To mailbox bind order + Astral inbox address to ignore on To (AST-1313; inbox_address aliases GAZE_EMAIL_CONFIG["account_address"])
```

2. Immediately **after** the `# AST-1098` `CANDIDATE_STAGE_DISPATCH` auto_mode assert block (the `assert all(not bool(e.get("auto_mode")) …)` that follows `assert GAZE_EMAIL_CONFIG["auto_mode"] is False`), and **before** the `# AST-1087 / AST-1089` / `METEORITE_EMAIL_PARSE_CONFIG` comment, insert:

```python
# AST-1313: one bind rule for Manage Email / Avail / gaze_email / Land Meteorite / create rematch.
# header_order is the only allowed sequence (From unique hit wins; To is fallback).
# inbox_address is the product mailbox identity — same object as GAZE_EMAIL_CONFIG["account_address"].
# Live OAuth user remains GMAIL_USER environ; do not read os.environ here.
INBOX_BIND_CONFIG = {
    "header_order": ("from", "to"),
    "inbox_address": GAZE_EMAIL_CONFIG["account_address"],
}
assert INBOX_BIND_CONFIG["header_order"] == ("from", "to")
assert INBOX_BIND_CONFIG["inbox_address"] == GAZE_EMAIL_CONFIG["account_address"]
assert isinstance(INBOX_BIND_CONFIG["inbox_address"], str)
assert "@" in INBOX_BIND_CONFIG["inbox_address"]
```

⚠️ **Decision — alias `GAZE_EMAIL_CONFIG["account_address"]`, do not copy a second literal and do not read `GMAIL_USER`:** Parent requires the Astral inbox address to be config-owned. That identity already exists as the gaze mailbox expectation. A second string would drift. `GMAIL_USER` is the live OAuth identity (environ / secret-adjacent); bind ignore must not take it from environ.

⚠️ **Decision — `header_order` is asserted to `("from", "to")`:** Callers must not inline that pair. The assert locks Archie's From-first rule so a config typo cannot silently To-first and break AC1.

3. Do **not** add CC/BCC/Reply-To keys. Do **not** add `from_field` / `to_field` keys — those payload names are the shipped AST-1047 / AST-1312 contract (`from_address`, `to_address`), not a new behavior set.

4. Compile: `python3 -m py_compile src/utils/config.py`.

## Stage 2: One bind helper; list + create rematch; Style D source

**Done when:** `list_inbox_messages` `candidate_match` follows From-then-To (From unique hit wins; else To binds only on exactly one remaining address after ignoring `INBOX_BIND_CONFIG["inbox_address"]`); `create_meteorite_job_from_inbox_message` rematches with the same helper (no leftover From-only `get_candidate_id_for_query`); `candidate_match` JSON shape is still only `{matched, astral_candidate_id}`; with `debug=True` each list message emits Style D `func="inbox_bind"` including `bind_header`, `bind_address`, and candidate id or empty; with `debug=False` those paths emit no new debug-contract lines. `python3 -m py_compile src/core/inbox.py` succeeds.

**Preflight (before any `inbox.py` edit):** After `sync-child.sh`, `GmailInboxMessage` and `GmailMessageHtml` in `src/external/gmail.py` must include `to_address: str` (AST-1312). If either TypedDict lacks it, **stop** — comment on **AST-1308** with the stage-blocked template. Do **not** add `to_address` in this ticket. Parent publish ref is `origin/ftr/AST-1308-email-bind-where-email-is-in-the-to-field-alone` (epic registry); `sync-child --ftr AST-1308` looks for unsuffixed `origin/ftr/AST-1308` and will skip when only the slugged ftr exists.

1. In `src/core/inbox.py`, update the module docstring AST-1047 line to:

```
AST-1047 / AST-1313: From-then-To → candidate_match enrichment on list payloads.
```

2. Add imports (keep existing imports; do not reorder unrelated ones):

```python
from email.utils import getaddresses, parseaddr

from src.utils.config import INBOX_BIND_CONFIG, INBOX_CREATE_JOB_CONFIG, METEORITE_CONFIG
```

(`INBOX_CREATE_JOB_CONFIG` / `METEORITE_CONFIG` are already imported from `src.utils.config` — extend that import; do not add a second config import.)

3. **Delete** `_candidate_match_for_from` entirely (no alias, no re-export). Replace it with these two private helpers, still above `list_inbox_messages`:

```python
def _inbox_addr_folded() -> str:
    raw = INBOX_BIND_CONFIG["inbox_address"] or ""
    _display, parsed = parseaddr(raw)
    token = (parsed or raw).strip()
    return token.casefold()


def _remaining_to_addresses(to_header: str) -> list[str]:
    # Unique remaining mailbox tokens after dropping the Astral inbox (casefold).
    inbox = _inbox_addr_folded()
    remaining: list[str] = []
    seen: set[str] = set()
    for _display, addr in getaddresses([to_header or ""]):
        token = (addr or "").strip()
        if not token or "@" not in token:
            continue
        folded = token.casefold()
        if inbox and folded == inbox:
            continue
        if folded in seen:
            continue
        seen.add(folded)
        remaining.append(token)
    return remaining


def _bind_inbox_message(
    from_address: str,
    to_address: str,
    *,
    debug: bool = False,
) -> tuple[dict, str, str]:
    """From unique hit wins; else To when exactly one remaining address uniquely matches.

    Returns (candidate_match, bind_header, bind_address).
    bind_header is "from", "to", or "" when no header was eligible / no unique hit.
    candidate_match shape is only {"matched", "astral_candidate_id"} — do not add bind_header.
    """
    bind_header = ""
    bind_address = ""
    cid = None
    for header in INBOX_BIND_CONFIG["header_order"]:
        if header == "from":
            raw = from_address or ""
            cid = get_candidate_id_for_query(raw, debug=debug)
            if cid is None:
                continue
            bind_header = "from"
            _display, parsed = parseaddr(raw)
            bind_address = (parsed or "").strip() or raw.strip()
            break
        if header == "to":
            remaining = _remaining_to_addresses(to_address or "")
            if len(remaining) != 1:
                continue
            raw = remaining[0]
            cid = get_candidate_id_for_query(raw, debug=debug)
            bind_header = "to"
            bind_address = raw
            break
        raise ValueError(f"unsupported inbox bind header: {header!r}")
    return (
        {"matched": cid is not None, "astral_candidate_id": cid},
        bind_header,
        bind_address,
    )
```

⚠️ **Decision — `getaddresses` + unique-by-casefold, not comma-split and not unique-among-many:** Archie chose single-remaining-address To-bind to avoid google-group noise. `email.utils.getaddresses` is the stdlib parser for `Name <a@b>, c@d`. Two tokens of the **same** address still count as one remaining address (one mailbox identity). Two **distinct** remaining addresses stay unbound — do not pick a unique-among-many winner.

⚠️ **Decision — To is not consulted after a From unique hit:** Even if To would uniquely match a different candidate, return the From bind and do not call `_remaining_to_addresses` / a second lookup.

⚠️ **Decision — `candidate_match` JSON stays two keys:** Bind source is Style D only. Adding `bind_header` to the list payload would invite React To rules and is not in the AC. Manage Email chrome is out of scope.

⚠️ **Decision — reuse `get_candidate_id_for_query` as-is:** Same contact / extra-email / name homes as today's From bind. Do not invent a second lookup and do not start reading `email_list_paths` here if the existing helper does not.

4. In `list_inbox_messages`:
   - Change the docstring to: `Return every INBOX message metadata row for GMAIL_USER, with From-then-To candidate bind.`
   - Replace the From-only enrichment loop body with:

```python
    enriched: list[dict] = []
    n = len(messages)
    for i, msg in enumerate(messages, start=1):
        match, bind_header, bind_address = _bind_inbox_message(
            msg.get("from_address") or "",
            msg.get("to_address") or "",
            debug=debug,
        )
        row = dict(msg)
        row["candidate_match"] = match
        enriched.append(row)
        if debug:
            mid = (msg.get("id") or "")[:80]
            outcome = "found|matched" if match["matched"] else "found|none"
            logger.debug_index(
                func="inbox_bind",
                index=i,
                total=n,
                identifier=mid,
                outcome=outcome,
            )
            logger.debug_detail(f"bind_header={bind_header}")
            for line in truncate_debug_content(bind_address):
                logger.debug_detail(f"bind_address={line}")
            if match["matched"]:
                logger.debug_detail(f"astral_candidate_id={match['astral_candidate_id']}")
            else:
                logger.debug_detail("astral_candidate_id=")
```

   - **Delete** the old `func="inbox_from_bind"` block (including the `from_address=` detail loop). Do not keep both funcs.
   - Do **not** attach `bind_header` / `bind_address` onto `row`.
   - Missing `to_address` key (should not happen after AST-1312) is treated as `""` via `.get` — To path then cannot bind; From path still can.

5. Update count helper docstrings only (behavior already follows `candidate_match`):
   - `count_inbox_bound_by_candidate`: `… for matched From-then-To binds.`
   - `count_inbox_messages_bound_to_candidate`: `Live count of current inbox messages whose From-then-To bind is candidate_id.`

6. In `create_meteorite_job_from_inbox_message`:
   - Change the docstring to: `Fetch message, rematch From-then-To→candidate, strip/extract, gazer ingest → meteorite jobs.`
   - After the existing `from_address = payload.get("from_address") or ""` line, add:

```python
    to_address = payload.get("to_address") or ""
```

   - **Replace** the leftover From-only rematch:

```python
    # DELETE:
    cid = get_candidate_id_for_query(from_address, debug=False)
    if cid is None:
        raise ValueError("message is not matched to a candidate")
```

     with:

```python
    match, bind_header, bind_address = _bind_inbox_message(
        from_address, to_address, debug=False
    )
    cid = match["astral_candidate_id"] if match["matched"] else None
    if cid is None:
        raise ValueError("message is not matched to a candidate")
```

   - Keep `debug=False` on the helper so create does not emit a second `get_candidate_id_for_query` / `inbox_bind` index stream (create already owns `func="inbox_create_job"`).
   - On the existing index-2 `inbox_create_job` matched block, **replace** the `from_address=` detail loop with bind-source details (keep `astral_candidate_id=`):

```python
        logger.debug_detail(f"astral_candidate_id={cid}")
        logger.debug_detail(f"bind_header={bind_header}")
        for line in truncate_debug_content(bind_address):
            logger.debug_detail(f"bind_address={line}")
```

   - Raise text stays exactly `message is not matched to a candidate`.

7. Do **not** change `get_message_html` (no `candidate_match` on get). Do **not** edit `gaze_email.py`, `api_inbox.py`, or React. Gaze / Avail / Land Meteorite already consume list `candidate_match`. Do **not** remove or weaken `@require_admin` on inbox routes (AC6).

8. Compile: `python3 -m py_compile src/core/inbox.py src/utils/config.py`.

### Betty will need (not this ticket’s commit)

`tests/component/core/test_inbox.py` From-only fixtures (`TestAst1047InboxFromBind`, list enrichment) will need From-then-To cases: From unique wins over a conflicting To; To single-remaining bind after inbox ignore; multi remaining / inbox-only / empty To stay unmatched; create rematch uses To when From misses; `debug=True` emits `inbox_bind` + `bind_header` / `bind_address` and `debug=False` does not. Engineer does **not** edit `tests/` or `docs/test-bible/**`.

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order across the plan.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the plan.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.**
- When the codebase has drifted from what the plan assumes — **stops and comments.** Does not adapt silently.
- Completes a stage on the epic worktree, commits, and publishes to `origin/sub/AST-1308/AST-1313-from-then-to-bind-debug-source`.

Blocking comment format (parent **AST-1308**):

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

## Self-Assessment

**Scope:** Single-Component — `src/utils/config.py` (`INBOX_BIND_CONFIG`) plus `src/core/inbox.py` (one helper, list enrichment, create rematch, Style D). No external/UI/data edits.

**Conf:** high — reuses `get_candidate_id_for_query`, AST-1312 `to_address`, existing `{matched, astral_candidate_id}` consumers, and Style D helpers already on the list/create paths.

**Risk:** Medium — a wrong From-then-To decision would Avail / gaze_email / Land Meteorite / create the wrong candidate (or leave autoforwards unbound). Consumers themselves are unchanged; only the shared bind result moves.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Verdict |
|------|---------|
| §1.3 DRY | One helper; list + create rematch call it; no second To parser in gaze/UI. |
| §2.1 config | Header order + inbox identity in `INBOX_BIND_CONFIG`; inbox address aliases existing `account_address`; no `GMAIL_USER` in bind. |
| §2.4 batch | N/A — no claim/process/release. |
| §2.6 state | N/A — no entity state. |
| §3.3 imports | core → candidate + external gmail + utils only; `getaddresses` is stdlib. |
| §1.5.1 debug | Style D only when `debug=True`; `func="inbox_bind"`; truncate `bind_address`; no new lines when `debug=False`. |
| §3.5 naming | `to_address` / `from_address` unchanged; helper names snake_case, not ticket ids. |

No conflicts. Conf remains **high**.

## Joan validate

[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1313
**Publish ref:** `sub/AST-1308/AST-1313-from-then-to-bind-debug-source` @ `a55cf1f`
**Overall:** APPROVED

## Traceability

| Child AC | Plan stage(s) | Definition anchor |
|----------|---------------|-------------------|
| 1 — From unique hit binds A even if To uniquely matches B or none | Stage 2 step 3 (`header == "from"` first in `header_order`) | Parent AC 1 |
| 2 — From miss + single remaining To unique hit binds A | Stage 2 step 3 (`header == "to"` after From miss; `len(remaining) == 1`) | Parent AC 2 |
| 3 — From miss + To missing / multi-remaining / non-unique lookup → unbound | Stage 2 step 3 (`len(remaining) != 1` or `cid is None`) | Parent AC 3 |
| 4 — Configured Astral inbox address on To never binds by itself | Stage 2 step 3 (`_remaining_to_addresses` drops inbox by casefold) | Parent AC 4 |
| 5 — `debug=True` on touched bind paths logs header + address + candidate id/none; `debug=False` no new contract lines | Stage 2 steps 4, 6 (`func="inbox_bind"`; create rematch bind details on `inbox_create_job`) | Parent AC 5 |
| 6 — Unauthenticated callers still blocked | Stage 2 step 7 (no route/auth changes) | Parent AC 6 |

| Plan stage | Child AC |
|------------|----------|
| Stage 1 (`INBOX_BIND_CONFIG`) | Enables AC 4 + header order for AC 1–3 |
| Stage 2 (helper, list, create rematch, Style D) | AC 1–6 |

No orphan stages. Parent mailbox-To exposure correctly deferred to AST-1312 (preflight only).

## Statute verdicts

| Statute / pattern | Verdict | Rationale |
|-------------------|---------|-----------|
| `pattern.config.config-block` | conforms | `INBOX_BIND_CONFIG` owns `header_order` + `inbox_address` alias |
| `astral.config.config-source-of-truth` | conforms | Order and inbox identity read from config; asserted `("from", "to")` |
| `astral.standards.no-hardcoded-sets` | conforms | Callers iterate `INBOX_BIND_CONFIG["header_order"]`; no inline header pair |
| `pattern.layers.import-discipline` | conforms | Bind in `src/core/inbox.py`; Gmail/external untouched |
| `astral.layers.import-direction` | conforms | core → candidate + external + utils; stdlib `email.utils` only |
| `astral.layers.core-vs-external-bright-line` | conforms | To I/O AST-1312; decision here in core |
| `astral.standards.debug-contract-gated` | conforms | Style D `inbox_bind` + bind source details; create helper stays `debug=False` to avoid duplicate streams |
| `astral.standards.dry-and-focused-functions` | conforms | One `_bind_inbox_message`; list + create rematch both call it |
| `astral.layers.ui-config-driven-business-logic` | conforms | `candidate_match` shape unchanged; no React To rules |
| `astral.standards.in-scope-only` | conforms | Bind rule + debug source only; no new mailbox product |

## Considered and excluded

**Considered:** child **In scope** statutes (above).

**Excluded (boundary / sibling):**
- Raw `to_address` on list/get — AST-1312 (preflight dependency)
- `pattern.ui.admin-endpoint` / `astral.patterns.require-auth-on-protected-endpoints` — no route changes
- CC/BCC/Reply-To / forwarding headers — parent boundary
- Multi-remaining unique-among-many To pick — Archie decision documented
- Manage Email chrome / new column — out of scope
- ingest/scrape/dedupe/archive beyond who is bound — consumers read enriched list only
- `get_candidate_id_for_query` homes / second lookup — reused as-is
- `GMAIL_USER` as ignore address — correctly rejected; uses `GAZE_EMAIL_CONFIG["account_address"]`
- `bind_header` on JSON payload — Style D only (explicit decision)
- `tests/`, `docs/test-bible/**` — Betty

## Findings

| Sev | Location | Finding | Recommendation |
|-----|----------|---------|----------------|
| **acceptable** | Stage 2 preflight | Publish tip plan-only; `src/external/gmail.py` on this branch lacks `to_address` until ftr/AST-1312 merge. Plan requires stop-if-missing preflight. | Execute preflight before Stage 2 edits (merge `origin/ftr/AST-1308-email-bind-where-email-is-in-the-to-field-alone`). |
| **acceptable** | Stage 2 step 3 | When To has exactly one remaining address but lookup returns no unique hit, helper sets `bind_header="to"` with empty `astral_candidate_id` — consistent with parent AC 5 “candidate id or none/ambiguous.” | None. |
| **acceptable** | Stage 2 step 6 | Create rematch logs bind source on `inbox_create_job` index 2 instead of a second `inbox_bind` index stream when `debug=True`. | None — avoids duplicate debug noise; still satisfies AC 5 for the rematch path. |

**Tip verification:** Current `inbox.py` still has `_candidate_match_for_from`, `inbox_from_bind` debug, and From-only create rematch — all named replacement sites. `GAZE_EMAIL_CONFIG["account_address"]` exists at config line 2548; plan insertion anchor (post–AST-1098 assert, pre–`METEORITE_EMAIL_PARSE_CONFIG`) matches live `config.py`. `gaze_email.py`, `count_inbox_bound_by_candidate`, and Land Meteorite paths consume `list_inbox_messages()` → `candidate_match` without further edits.

**Self-assessment:** Single-Component / high conf / medium risk — honest; shared helper is the sole decision point; consumer surface unchanged.

context_tokens≈55000
— Joan

## Review (build stub)

**Publish ref:** `origin/sub/AST-1308/AST-1313-from-then-to-bind-debug-source`
**Plan path:** `docs/features/meteorite/ast-1313-from-then-to-bind-debug-source.md`

**Built tip:** `b5ed286ca98fd4b9e665e92f8619ae4e7aa414db` (`b5ed286c`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `8ce2d70c` | `INBOX_BIND_CONFIG` header order + inbox address alias |
| 2 | `b5ed286c` | `_bind_inbox_message` list enrichment + create rematch + Style D |

## Radia review

[code-rubric] revision=2
**Rubric:** code-rubric.v2
**Ticket:** AST-1313
**Publish ref:** `origin/sub/AST-1308/AST-1313-from-then-to-bind-debug-source` @ `d197a847`

**Overall:** CLEAN

**Diff baseline:** `origin/dev...origin/sub/AST-1308/AST-1313-from-then-to-bind-debug-source` (10 paths, +1103/−23). Includes sibling **AST-1312** commits on branch lineage (`gmail.py` `to_address`, `test_gmail.py`); **AST-1313 product delta** is engineer commits `8ce2d70c` (`config.py`) + `b5ed286c` (`inbox.py`); Betty `94163472` + `merge-tests` landed tests/bible.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | not-applicable | no agent paths |
| `astral.agent.do-task-delegation` | scoped | not-applicable | no dispatch/delegation |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | no grade vectors |
| `astral.batch.batch-id-first` | scoped | not-applicable | no batch_id |
| `astral.batch.batch-id-format` | scoped | not-applicable | no batch_id strings |
| `astral.batch.claim-process-release` | scoped | not-applicable | no claim/process/release |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | no entity-agent-response paths |
| `astral.config.config-source-of-truth` | scoped | conforms | `INBOX_BIND_CONFIG` owns `header_order` + `inbox_address`; callers iterate config |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | inbox identity aliases `GAZE_EMAIL_CONFIG`; no `GMAIL_USER` in bind |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | no artifacts |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | no spikes |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | no dispatch seed |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | no run_next |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | issue doc present |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty commits tests + test-bible only |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | engineer commits: `config.py` + `inbox.py` only |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | bind decision in core; Gmail I/O unchanged by 1313 commits |
| `astral.layers.import-direction` | scoped | conforms | core → candidate + external + utils; stdlib `email.utils` |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | no scripts |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | `candidate_match` shape unchanged; no React To rules |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | no coat-check |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | no render/consult |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | not-applicable | no route/auth edits (Joan excluded) |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | no seed tables |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | no seed catalog |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | no boot hot path |
| `astral.seed.define-approved` | scoped | not-applicable | no define flow |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | no seed rows |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | no coverage join |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | no data layer |
| `astral.standards.database-header-inventory` | scoped | not-applicable | no DB/migrations |
| `astral.standards.debug-contract-gated` | scoped | conforms | `func="inbox_bind"` per-message index + `bind_header`/`bind_address`/`astral_candidate_id` details; create rematch bind source on `inbox_create_job` index 2; `debug=False` paths silent |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | single `_bind_inbox_message`; list + create share it |
| `astral.standards.in-scope-only` | scoped | conforms | bind rule + debug source only; chrome/ingest untouched |
| `astral.standards.logging-via-utils` | scoped | conforms | `get_logger` + contract helpers; no `print` |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | `to_address`/`bind_header` naming; no ticket ids in symbols |
| `astral.standards.no-cross-contamination` | scoped | conforms | no cross-layer smuggling |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | `header_order` read from `INBOX_BIND_CONFIG`; asserted `("from", "to")` |
| `astral.standards.public-then-helpers` | scoped | conforms | public list/create unchanged in surface; helpers private |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | config add only; no utils→data |
| `astral.state.core-decides-transitions` | scoped | not-applicable | no state transitions |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | no job state |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | no run chain |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | no frontend |
| `astral.ui.naming-conventions` | scoped | not-applicable | no UI |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | no worker config |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | `merge-tests(AST-1313)` on tip |
| `orch.git.commit-vocabulary` | universal | conforms | `code` / `test` / `docs` / `merge-tests` |
| `orch.git.flow-direction-inviolable` | universal | conforms | sub publish topology |
| `orch.git.ftr-sub-topology` | universal | conforms | `sub/AST-1308/AST-1313-…` |
| `orch.git.merge-on-checkout` | universal | conforms | ftr merge commit on branch history |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | linear stack |
| `orch.git.no-dev-agent-branches` | universal | conforms | no agent branches |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | AST-1308 worktree |
| `orch.git.three-permanent-branches` | universal | conforms | sub publish |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | Archie decisions (single-remaining To, raw header, no JSON bind_header) documented in plan |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages 1–2 executed per plan in engineer commits |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Meteorite child scoped |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed gate |
| `orch.roles.archie-approves-statutes` | universal | conforms | no statute edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | test/bible by Betty pipeline |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | Ada assignee through Tests Passed |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | engineer assignee retained |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no banned-path commits observed |

**Sweep count:** 64 active statutes scored (per `canon/statutes/README.md` harvested corpus).

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| *(none cited in plan body)* | — | no "Patterns to reuse" section; Joan validate references `pattern.config.config-block` / `pattern.layers.import-discipline` informally — implementation matches both approved catalog shapes |

## Plan adherence

**Stage 1 (`8ce2d70c`):** `INBOX_BIND_CONFIG` inserted at plan anchor with docstring line, `header_order == ("from", "to")`, `inbox_address` aliasing `GAZE_EMAIL_CONFIG["account_address"]`, and four asserts. No CC/BCC/`from_field` keys.

**Stage 2 (`b5ed286c`):**
- `_candidate_match_for_from` deleted; `_inbox_addr_folded`, `_remaining_to_addresses`, `_bind_inbox_message` match plan verbatim.
- From unique hit breaks before To; `getaddresses` + casefold dedupe; inbox dropped via config address.
- List enrichment calls helper with `to_address`; debug `func="inbox_bind"` replaces `inbox_from_bind`; `astral_candidate_id=` emitted on no-match.
- Create rematch uses same helper with `debug=False`; bind source on `inbox_create_job` index 2.
- `candidate_match` remains `{matched, astral_candidate_id}` only.
- No `gaze_email` / API / React edits.

**Preflight:** Branch includes AST-1312 `to_address` on TypedDicts (merge `9af4e20a`); Stage 2 precondition satisfied.

**Self-Assessment** (config + core, medium risk) matches footprint. Joan plan-rubric APPROVED attached — **no stragglers** (Joan-excluded items remain `not-applicable` on this diff).

**Betty manifest:** `TestAst1313FromThenToBind` covers AC 1–5 scenarios (From wins, To after inbox ignore, unbound cases, duplicate To dedupe, create To rematch, debug gating); `TestAst1313InboxBindConfig` locks config asserts.

## C6 judgment aids (§5a–§5g)

| Lens | Verdict |
|------|---------|
| Imports (B1) | conforms — stdlib `email.utils` at module top |
| Layer compliance (B2) | conforms — bind in core; external passthrough only |
| Silent failure (D2) | conforms — no new swallow paths |
| Fallbacks (D3) | conforms — `msg.get("to_address") or ""` per plan for missing key |
| Logging (E1) | conforms — contract helpers only |
| Config/state in UI (G1) | conforms — config-driven bind order + inbox identity |
| Batch/transitions (H*) | not-applicable |
| Debug contract (§5f) | conforms — per-message `inbox_bind` index N/M; `truncate_debug_content` on `bind_address`; `debug=False` silent on list; create avoids duplicate `inbox_bind` stream |
| External cleanliness (§5g) | not-applicable — no LLM external changes |

## Findings

*(none)*

### Advisory (downstream awareness, not blocking)

- **Ambiguous From → To fallback:** When `get_candidate_id_for_query` returns `None` for an ambiguous From (≥2 hits), bind falls through to To. This is consistent with treating ambiguous From as a "miss" and is covered by the plan's `if cid is None: continue` loop; worth Susan knowing if product intent is to hard-block To whenever From is ambiguous regardless of To shape.
- **To path with single remaining but no lookup hit:** `bind_header="to"` with `matched=False` is Joan-documented and satisfies AC 5 debug-source logging.

## What's solid

- Single decision point (`_bind_inbox_message`) shared by list, counts, and create — consumers (`gaze_email`, Avail, Land Meteorite, Manage Email) need no edits.
- `metadataHeaders` / `to_address` dependency correctly inherited from AST-1312 on branch; 1313 commits stay in lane.
- Tests assert the highest-risk cases: From-over-To precedence, inbox ignore, multi/empty To unbound, duplicate To dedupe, create To rematch, and debug gating.

## Frame diff

- **`INBOX_BIND_CONFIG`:** new config block (`header_order`, `inbox_address` alias).
- **`_candidate_match_for_from`:** removed.
- **`_bind_inbox_message` + helpers:** added; returns `(candidate_match, bind_header, bind_address)`.
- **List payloads:** `candidate_match` now From-then-To; debug `func` renamed `inbox_from_bind` → `inbox_bind` with `bind_header`/`bind_address` details.
- **Create path:** rematch uses helper; debug bind source on existing `inbox_create_job` index 2.
- **JSON contract:** `candidate_match` shape unchanged; no `bind_header` on API payloads.

## Notes

- Joan plan-rubric verdict attached (`revision=1`, APPROVED). No straggler callouts.
- Three-dot diff vs `origin/dev` includes AST-1312 sibling work; 1313 review scoped to config + inbox engineer commits above.

context_tokens≈48000
— Radia
