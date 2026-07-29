# AST-1047 — Reusable get_candidate string lookup + From bind

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1047/reusable-get-candidate-string-lookup-from-bind-bind-email-to-candidate  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1044/bind-email-to-candidate  

**Publish ref (origin):** `sub/AST-1044/AST-1047-reusable-get-candidate-string-lookup-from-bind`  
**Parent integration ref:** `ftr/AST-1044-bind-email-to-candidate`

Ship a **reusable core string → astral candidate id lookup** (Susan’s conceptual `get_candidate` helper) that matches configured contact-email and name fields, returns the id only on an **unambiguous** hit, and wire Manage Email’s **From** address through that helper on the existing inbox list/get API payloads (including `debug=True` found/matched Style D lines). Sibling AST-1048 owns React chrome / Create enablement UI; AST-1049 owns strip/extract + meteorite create.

Boundaries (do **not** implement): Manage Email React rename/chrome/Create button (AST-1048), strip/extract + meteorite create wire (AST-1049), multi-candidate picker UX, Gmail client reimplementation, Profile/Admin contact editors, mailbox mutation.

**Hard dependency note:** Parent names **AST-1014** contact-blob homes as the long-term email source. This tip may still have transitional `profile.*` email/name paths. The lookup config lists **both** library and transitional paths so matches work before/after 1014 lands on `origin/dev`; missing paths simply contribute no values.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `CANDIDATE_LOOKUP_CONFIG` (email/name dotted paths + casefold flag) | utils |
| `src/core/candidate.py` | Add `get_candidate_id_for_query(...)` + path/value helpers; `debug=` Style D found/matched lines | core |
| `src/core/inbox.py` | Enrich list (+ optional get) with From → lookup match payload; pass `debug` | core |
| `src/ui/api/api_inbox.py` | Pass `debug` via `ui_llm_debug`; leave `@require_admin`; no React | ui |

---

## Stage 1: Config — lookup field vocabulary

**Done when:** `CANDIDATE_LOOKUP_CONFIG` is importable from `src.utils.config` with the email/name path tuples below; no core/UI changes yet.

1. In `src/utils/config.py`, after `CANDIDATE_CONFIG` (or immediately after `CANDIDATE_LIBRARY_CONFIG` if that block already exists on this tree), add:

```python
# AST-1047: reusable string → candidate-id match homes (Manage Email From bind first caller).
CANDIDATE_LOOKUP_CONFIG = {
    # Dotted paths resolved against a full candidate row (top-level columns + candidate_data).
    "email_paths": (
        "contact.contact_email",   # AST-1014 contact blob
        "contact.reply_email",
        "profile.contact_email",   # transitional pre-1014
        "profile.reply_email",
    ),
    "name_paths": (
        "first", "last", "full",           # AST-1014 name columns when present
        "profile.first", "profile.last",   # transitional
    ),
    "match_casefold": True,  # case-insensitive compare for emails and names
}
```

2. If the top-of-file config inventory lists named `*_CONFIG` blocks, add a one-line `CANDIDATE_LOOKUP_CONFIG` entry next to other candidate config bullets.

⚠️ **Decision:** Field keys live only in this config block (§2.1 / no hardcoded sets in core). Dual library + transitional paths are intentional until 1014 is universal on `dev`; empty/missing path values are skipped, not errors.

---

## Stage 2: Core reusable lookup (Susan’s get_candidate shape)

**Done when:** Calling `get_candidate_id_for_query` with a string that uniquely matches one candidate’s configured email or name returns that `astral_candidate_id`; zero hits or two+ distinct candidate ids return `None`; existing `get_candidate(candidate_id)` ID fetch is **unchanged**; with `debug=True`, Style D found/matched lines emit; with `debug=False`, no new debug-contract lines.

1. In `src/core/candidate.py` (public section near `get_candidate` / `list_candidates`), **keep** existing:

```python
def get_candidate(candidate_id: str) -> Optional[Dict[str, Any]]:
    ...
```

Do **not** overload or rename it.

2. Add public:

```python
def get_candidate_id_for_query(
    query: str,
    *,
    debug: bool = False,
) -> Optional[str]:
```

**Behavior (literal):**

- Import `CANDIDATE_LOOKUP_CONFIG` from `src.utils.config`. Use existing `get_logger` / `truncate_debug_content` (add imports if missing).
- `raw = (query or "").strip()`. If empty → return `None` (optional debug: `found|empty_query`).
- **Normalize for matching:** use `email.utils.parseaddr(raw)` (stdlib). Let `addr = (parsed_email or "").strip()`.  
  - If `addr` contains `@`, the **match needle** is `addr`.  
  - Else the **match needle** is `raw` (name-style query).  
  - Never invent an email from a display name alone.
- `needle_cmp = needle.casefold() if CANDIDATE_LOOKUP_CONFIG["match_casefold"] else needle`.
- Scan `list_candidates(include_deleted=False)` (exclude DELETED).
- For each candidate, collect string values from all `email_paths` + `name_paths` via a private helper `_lookup_path_value(candidate, dotted_path) -> str`:
  - Split path on `.`.
  - If first segment is `contact` or `profile` (or any blob under `candidate_data`), read from `candidate["candidate_data"]` nested dicts.
  - If first segment is a top-level column (`first` / `last` / `full` / `pronouns` / `astral_candidate_id`), read from the candidate row first; if missing/empty, also try `candidate_data.profile.<seg>` only when that path is listed in config (do not invent extra homes).
  - Coerce to stripped `str`; skip `None` / non-strings / empty.
- A candidate **hits** when any collected value, after the same casefold rule, equals `needle_cmp`.
- Build the set of distinct `astral_candidate_id` strings among hits (skip blank ids).
- If `len(ids) == 1` → return that id. If `0` or `>= 2` → return `None`.

3. **Debug contract** (`debug=True` only), one index per call (batch of 1):

- `logger.set_debug_flag(True)` then `logger.debug_index(func="get_candidate_id_for_query", index=1, total=1, identifier=<needle truncated>, outcome=...)` where outcome is `found|matched` (unique id), `found|none`, `found|ambiguous`, or `found|empty_query`.
- `logger.debug_detail` lines: `query=`, `needle=`, and on match `candidate_id=`; on ambiguous `candidate_ids=` (sorted id list). Use `truncate_debug_content` on long strings.

⚠️ **Decision — name vs existing `get_candidate`:** Catalog already uses `get_candidate(candidate_id)` for ID fetch across UI/core. Overloading it for string lookup would break every caller that passes an id that happens to look like email/name text. The reusable string→id helper is therefore **`get_candidate_id_for_query`** — same responsibility Susan named “get_candidate” in the epic, without colliding. Do not rename the ID fetcher in this ticket.

⚠️ **Decision — ambiguous:** Multiple candidates matching the same needle → `None` (no picker). Parent invariant: emails unique across candidates; name collisions are fail-closed.

---

## Stage 3: From bind on Manage Email inbox API (no React)

**Done when:** `GET /api/admin/inbox/messages` (and message get if it returns the list row shape) includes a `candidate_match` object derived solely from each message’s `from_address` via `get_candidate_id_for_query`; unmatched/ambiguous → `matched: false` and null id; `@require_admin` unchanged; no React/nav rename.

1. In `src/core/inbox.py`, add a thin enricher used by list (and get if the get payload is the same message dict family):

```python
def _candidate_match_for_from(from_address: str, *, debug: bool = False) -> dict:
    cid = get_candidate_id_for_query(from_address or "", debug=debug)
    return {
        "matched": cid is not None,
        "astral_candidate_id": cid,
    }
```

Import `get_candidate_id_for_query` from `src.core.candidate`.

2. Change `list_inbox_messages` to accept `debug: bool = False`. After `external_list_inbox_messages()`, return a **new list** of dicts: each original message fields plus `"candidate_match": _candidate_match_for_from(msg["from_address"], debug=debug)`.

⚠️ **Decision:** Enrich in **core inbox** (not only in the Flask layer) so any future core caller of list gets the same From-bind contract. UI stays thin.

3. When `debug=True` on list enrichment, emit Style D **per message** in the enricher loop:

- `debug_index(func="inbox_from_bind", index=i, total=n, identifier=<message id>, outcome=found|matched` or `found|none`)  
- detail: `from_address=`, `astral_candidate_id=` when matched.  
  (Ambiguous and none both surface as `matched: false` / null id; outcome label `found|none` is enough — lookup already logged ambiguous internally when its own `debug=True` is set. Pass the same `debug` flag into `get_candidate_id_for_query` so lookup lines appear too.)

4. In `src/ui/api/api_inbox.py`:

- Import `ui_llm_debug` from `src.utils.deploy_status` (same pattern as other LLM/debug admin routes).
- `inbox_list_messages`: `debug = ui_llm_debug(explicit_debug=request.args.get("debug", "").lower() in ("1", "true", "yes"))` then `list_inbox_messages(debug=debug)`.
- Keep `@require_admin`. Do **not** change response envelope key `messages`.
- Do **not** edit `AdminReadEmail.tsx`, `NAV_CONFIG` label, or routes (AST-1048).

5. If `get_message_html` returns a payload that AST-1048 will also use for bind display on the selected message, add the same `candidate_match` key there by re-reading From from list metadata **only if** the get payload already includes `from_address`. If get payload is HTML-only today (`html_body` without From), **skip** enriching get — list enrichment is sufficient for the bind wire in this ticket.

---

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order.
- Does not skip, reorder, combine, or expand steps.
- Does not add files outside the Files Changed table.
- On ambiguity or codebase drift — **stops, comments on parent AST-1044**, waits.
- Commits per stage on the epic worktree; publishes to `origin/sub/AST-1044/AST-1047-reusable-get-candidate-string-lookup-from-bind`.

Blocking comment format (parent AST-1044):

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

---

## Self-Assessment

**Scope:** Single-Component — config + candidate lookup helper + inbox From enrichment on existing admin inbox API; no React, no meteorite create, no schema migration.

**Conf:** high — reuses `list_candidates` / `get_candidate` row shape, stdlib `parseaddr`, existing `@require_admin` inbox blueprint, and AST-538 debug helpers; dual path config covers pre/post AST-1014.

**Risk:** Medium — a false unique match would enable Create in AST-1048/1049 for the wrong candidate; mitigated by exact string match on configured homes only, fail-closed ambiguity, and From-email extraction before compare. Wrong overload of `get_candidate(id)` avoided by Decision above.

---

## Code Rules self-review

| Rule / citation | Check |
|-----------------|--------|
| §2.1 / `astral.config.config-source-of-truth` / `no-hardcoded-sets` | Email/name homes only in `CANDIDATE_LOOKUP_CONFIG` |
| §1.5.1 / `debug-contract-gated` | Style D only when `debug=True`; truncate long From/query |
| §3.3 / import-direction / core-vs-external | UI → core only; Gmail stays in external via existing inbox |
| §1.3 DRY | One lookup helper; inbox From bind calls it — no second matcher in UI |
| Existing `get_candidate(id)` | Untouched ID fetch — no signature break |
| No picker / no Create UI | Ambiguous → `None`; React left to AST-1048 |

## Review (build stub)

**Publish ref:** `origin/sub/AST-1044/AST-1047-reusable-get-candidate-string-lookup-from-bind`
**Plan path:** `docs/features/meteorite/ast-1047-reusable-get-candidate-string-lookup-from-bind.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `05e8a2b4` | `CANDIDATE_LOOKUP_CONFIG` email/name paths + casefold |
| 2 | `3ad56efc` | `get_candidate_id_for_query` + `_lookup_path_value`; Style D |
| 3 | `a530d025` | Inbox list `candidate_match` From bind; `api_inbox` `ui_llm_debug` |

**Tip:** `a530d0255a69308d63896541b621b49b0faf39b4` on `origin/sub/AST-1044/AST-1047-reusable-get-candidate-string-lookup-from-bind`

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1047
**Publish ref tip (pre-docs):** `0cefd0c2133867fcf5f6d0c3ec23d086c354908a`
**Overall:** DISCUSS

### What’s solid
- `CANDIDATE_LOOKUP_CONFIG` owns email/name homes; `get_candidate_id_for_query` returns id only on unique hit; existing `get_candidate(id)` untouched.
- Inbox list From→`candidate_match` enrichment in core; `api_inbox` stays thin + `@require_admin` + `ui_llm_debug`.
- Style D gated on `debug=True` (lookup + per-message `inbox_from_bind`); no React/Create/strip (AST-1048/1049).

### Issues
- **discuss (straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` at plan time; three-dot diff includes `docs/features/**` + Betty `tests/**` / `docs/test-bible/**` so they score in-scope (all **conforms** on substance).

### Recommended actions
- Ada: acknowledge stragglers (no product change expected) → resolve-child → User Testing.

## Resolution

**Date:** 2026-07-29
**Review:** Radia @ `20e640f5` — **Overall:** DISCUSS; **fix-now:** none; **discuss:** statute straggler ×3 (all substance **conforms**); no advisory.

No product changes. Acknowledged discuss stragglers as plan-time Joan exclusions that became in-scope on the three-dot vs `origin/dev` (`docs/features/**` + Betty tests/bible) — no code delta. Advanced to **User Testing**.
