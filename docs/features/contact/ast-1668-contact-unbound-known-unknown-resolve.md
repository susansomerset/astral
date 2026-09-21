# AST-1668 — Contact unbound list + known/unknown resolve

**Linear:** [AST-1668](https://linear.app/astralcareermatch/issue/AST-1668/contact-unbound-list-knownunknown-resolve-bind-new-slack-contacts-to)  
**Parent:** [AST-1636](https://linear.app/astralcareermatch/issue/AST-1636/bind-new-slack-contacts-to-existing-candidates-by-metadata-before) — Bind new Slack contacts to existing candidates by metadata before creating a prospect  
**Publish ref:** `sub/AST-1636/AST-1668-contact-unbound-known-unknown-resolve`

Child #2 of AST-1636: Contact orchestration for the unbound Slack poster pool (external posters minus already-bound ids), admin GET for that pool, retire create-on-miss PROSPECT in `resolve_slack_user`, and post known/unknown recognition replies from config templates on the Estelle accept path. Does **not** implement `list_workspace_posters` (AST-1667) or Manage Candidates dropdown (AST-1669).

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/core/contact.py` — unbound orchestration + `resolve_slack_user` lookup-only + recognition reply wiring
- `src/utils/config.py` — known/unknown reply text keys
- `src/ui/api/api_contact.py` — admin GET unbound users
- `src/core/candidate.py` unchanged unless existing save entry must accept bind fields → **unchanged** (bind lookup reuses `get_candidate_id_for_query` / `list_candidates` already imported or importable from candidate)

**Out of scope (siblings):** `src/external/slack.py` poster helper body (call only); `AdminManageCandidates.tsx`; candidate write-path bind payload (AST-1669).

**Depends on:** AST-1667 `list_workspace_posters()` already on `origin/ftr/AST-1636-bind-slack-contacts` (merged into this worktree). Return shape: `list[{"slack_user_id": str, "username": str}]`.

**Canon Scope (read in full for plan):** `stat.logging.info.contact`, `stat.logging.info.api`, `stat.logging.debug`, `stat.logging.error`. Patterns: none (`no established pattern applies` on parent).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add known/unknown recognition reply text keys + asserts on `CONTACT_CONFIG` | utils |
| `src/core/contact.py` | `list_unbound_slack_users`; `resolve_slack_user` lookup-only (no `initiate_prospect_candidate`); recognition posts on accept; import `list_workspace_posters` / `list_candidates` as needed | core |
| `src/ui/api/api_contact.py` | `@require_admin` GET unbound Slack users thin wrapper | ui |

No other files. Do **not** edit `src/external/slack.py`, `src/core/candidate.py`, or frontend.

## Stage 1: Recognition reply config

**Done when:** `CONTACT_CONFIG` exposes two non-empty string keys with Susan's default wording, asserted like `hear_ack_reply_text`. No Contact or API behavior changes yet.

1. In `src/utils/config.py`, inside `CONTACT_CONFIG` (near `hear_ack_reply_text`), add:
   - `"known_recognition_reply_text": "I know who that is"`
   - `"unknown_recognition_reply_text": "I don't recognize you"`
2. Add asserts immediately after the existing `hear_ack_reply_text` assert:
   - `isinstance(..., str) and ....strip()` for both new keys (same shape as `hear_ack_reply_text`).
3. Do **not** remove `prospect_candidate_id_template` or other CONTACT keys in this ticket.

## Stage 2: Contact unbound list + lookup-only resolve + recognition wiring

**Done when:** `rg -n "initiate_prospect_candidate" src/core/contact.py` shows no call from `resolve_slack_user` (and the import is gone if unused elsewhere in the file); known Slack ids still resolve with `created=False`; unknown Estelle-in-play returns no candidate / `created=False` without minting PROSPECT; accept path posts known vs unknown config replies; unbound helper returns posters whose ids are not matched by `get_candidate_id_for_query`.

1. In `src/core/contact.py` module docstring, replace the AST-1068 create-on-miss line with AST-1668: lookup-only resolve + unbound pool + recognition replies (keep other AST notes).

2. Imports:
   - Add `list_candidates` from `src.core.candidate` only if Stage 2 step 4 needs it; prefer bind checks via existing `get_candidate_id_for_query` (already imported).
   - Add `list_workspace_posters` to the `src.external.slack` import list.
   - Remove `initiate_prospect_candidate` from the candidate import **if** nothing else in this module calls it after step 3 (it must not remain as a dead import).

3. Rewrite the miss branch of `resolve_slack_user` (today: when `get_candidate_id_for_query` returns `None` and `estelle_in_play` is true, fetch profile + `initiate_prospect_candidate`):
   - Keep the **hit** path unchanged (including username backfill via `save_candidate_data` / `fetch_user_profile`).
   - Keep the **miss + `not estelle_in_play`** path unchanged (`created=False`, empty names).
   - **Miss + `estelle_in_play`:** do **not** call `initiate_prospect_candidate`. Still call `fetch_user_profile(sid)` so activity/display can use username/display_name. Return:
     ```python
     {
         "astral_candidate_id": None,
         "state": None,
         "created": False,
         "slack_username": username,       # from profile
         "slack_display_name": display,    # from profile
     }
     ```
   - Debug Style D on this path: outcome `found|none` (not `recorded|created`).
   - Update the function docstring: lookup only; never creates PROSPECT.

4. Add public **`list_unbound_slack_users(*, debug: bool = False) -> list[dict]`**:
   - ⚠️ **Decision — bind filter:** Call `list_workspace_posters()` once, then keep only posters whose `slack_user_id` is a non-empty `str` and `get_candidate_id_for_query(sid, debug=debug) is None`. That reuses the same non-deleted Slack-id homes as resolve (`CANDIDATE_LOOKUP_CONFIG["slack_user_id_paths"]` / `include_deleted=False` inside the helper). Do **not** add a new candidate-table scanner API; do **not** edit `candidate.py`.
   - Return shape: `[{"slack_user_id": str, "username": str}, ...]` — preserve poster order from `list_workspace_posters` (already sorted by sibling).
   - `logger.debug` (ungated call site — ContextVar decides print) at joints per `stat.logging.debug`:
     - `Calling list_workspace_posters: []` / `Response from list_workspace_posters: …` (full list, no truncate)
     - `Beginning unbound filter loop on N items` / `End unbound filter loop after X items`
   - Propagate Slack/IO exceptions to the caller (API handler logs). Do not catch-and-`logger.exception`-then-re-raise.
   - If `debug` is True, `logger.set_debug_flag(True)` at entry (same pattern as other Contact entrypoints).

5. In `handle_slack_event`, after resolve + activity/cache warm and **before** the paste / Estelle turn block (`if result.get("accepted") and isinstance(channel, str) and channel:`):
   - ⚠️ **Decision — when to recognize:** Only when `accepted`, channel is a non-empty str, inbound `user` is a non-empty str, and `resolve_error` is absent (resolve ran without throw). Then:
     - `known = isinstance(result.get("astral_candidate_id"), str) and bool(result.get("astral_candidate_id"))`
     - `text_key = "known_recognition_reply_text" if known else "unknown_recognition_reply_text"`
     - `outbound = format_contact_reply_text(str(CONTACT_CONFIG[text_key]))`
     - `reply_thread_ts = event.get("thread_ts") or (msg_ts if isinstance(msg_ts, str) else None)`
     - `result["recognition_post"] = contact_post_message(channel=channel, text=outbound, thread_ts=reply_thread_ts, debug=debug)`
     - On post failure: `logger.error(..., exc_info=True)` once at this handler (existing Contact style for post failures); set `result["recognition_post"] = {"ok": False, "error": str(exc)}` — do not raise into the ack path.
   - ⚠️ **Decision — Estelle continues only when known:** Inside the existing accepted+channel block:
     - If **known** (`astral_candidate_id` set): keep today's paste → Estelle turn → hear-ack flow unchanged (recognition already posted; Estelle may still reply).
     - If **unknown** (user present, no `resolve_error`, no `astral_candidate_id`): **skip** paste, `run_contact_estelle_turn`, and hear-ack. Recognition reply is the only outbound for that event. Set `result["estelle_turn"] = {"ok": True, "outcome": "unrecognized", "skipped": True}` (or equivalent explicit skip marker) so debug bookends stay honest.
     - If no user or `resolve_error`: keep today's Estelle/hear-ack behavior (do not invent recognition).
   - Do **not** invent a new Contact `logger.info` dialect for recognition (`stat.logging.info.contact` remains the listen+Estelle action line after a real turn). Recognition is a Slack post, not a new info pipe.

6. Compile/lint `src/core/contact.py` and `src/utils/config.py` before the stage commit.

## Stage 3: Admin GET unbound Slack users

**Done when:** `GET /api/admin/contact/unbound_slack_users` is `@require_admin`, returns JSON unbound list from core, and does not emit a progress `info` line for the idempotent GET.

1. In `src/ui/api/api_contact.py`:
   - Import `list_unbound_slack_users` from `src.core.contact`.
   - Add route:
     ```python
     @contact_bp.route("/unbound_slack_users", methods=["GET"])
     @require_admin
     def contact_get_unbound_slack_users():
         ...
     ```
   - Resolve `debug` via `ui_llm_debug` + `request.args.get("debug", …)` the same way as `contact_get_estelle_activity`.
   - Call `users = list_unbound_slack_users(debug=debug)`; return `jsonify({"users": users}), 200`.
   - On exception: log once with live facts + traceback (`logger.exception` / `exc_info=True` — `stat.logging.error`), return `jsonify({"error": str(e)}), 502`. Next-step wording e.g. that the unbound list was not returned.
   - ⚠️ **Decision — no api info on GET:** Per `stat.logging.info.api`, idempotent GETs that only return current state are **not** progress — do **not** emit `| api … completed: GET …` for this route. PUT/POST progress patterns elsewhere stay as they are.

2. Do **not** register a new blueprint; `contact_bp` is already registered in `src/ui/server.py`.

3. Compile/lint `src/ui/api/api_contact.py` before the stage commit.

## Execution contract

- Stages in order; steps in order; no extra files.
- Ambiguity / drift → comment on **parent** AST-1636 with the Stage blocked template; wait.
- Sibling AST-1669 consumes `GET /api/admin/contact/unbound_slack_users` → `{"users":[{"slack_user_id","username"},…]}`.
- Acceptance mapped:
  1. No `initiate_prospect_candidate` from `resolve_slack_user` — Stage 2 step 3.
  2. Known resolve + known reply — Stage 2 steps 3 + 5.
  3. Unknown resolve + unknown reply + no PROSPECT + no Estelle-as-bound — Stage 2 steps 3 + 5.
  4–5. Unbound list / omit after bind — Stage 2 step 4 + Stage 3 (bind itself is AST-1669; filter uses `get_candidate_id_for_query`).
  6. `@require_admin` — Stage 3.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1668
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref:** `sub/AST-1636/AST-1668-contact-unbound-known-unknown-resolve` @ `8d4d98de29c06d61005e9572f9c30c0674f549c1`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.info.contact | C | 2 | Stage 2 cites statute but stages no canonical `contact listen …` info line after a real Estelle turn on the known path |
| stat.logging.info.api | A | | Stage 3 explicitly omits progress info on idempotent GET; matches `estelle_activity` precedent |
| stat.logging.debug | B | | New helper uses statute `logger.debug` joints; rest of `contact.py` stays Style D — acceptable mix |
| stat.logging.error | A | | Unbound API uses handler `logger.exception`; core propagates; recognition post failure matches existing Contact `logger.error`+`exc_info` pattern |

## Traceability

1 → Stage 2 step 3 (retire `initiate_prospect_candidate` on miss) · 2 → Stage 2 steps 3 + 5 (known resolve + `known_recognition_reply_text`) · 3 → Stage 2 steps 3 + 5 (unknown resolve, no PROSPECT, skip Estelle/hear-ack) · 4 → Stage 2 step 4 + Stage 3 (poster pool minus `get_candidate_id_for_query` hits) · 5 → Stage 2 step 4 filter (bind write is AST-1669; list omits bound ids by lookup) · 6 → Stage 3 (`@require_admin` GET `/unbound_slack_users`)

## Findings

### discuss — stat.logging.info.contact staging gap
**Location:** Stage 2 step 5 (`handle_slack_event` recognition / Estelle branching)
**Finding:** Plan correctly forbids a parallel recognition info dialect and skips Estelle on unknown users, but never stages the affirmative `logger.info` pipe line after `run_contact_estelle_turn` returns on the **known** path (`<candidate_id> | contact listen <event_type> <outcome>: action:…`). Codebase has no existing `contact listen` info line to “remain.”
**Recommendation:** Add an explicit sub-step on the known branch (after a successful Estelle turn, before hear-ack): emit the canonical format from `stat.logging.info.contact` § Do. Do not log recognition posts at info. Not blocking if engineer adds during build — flag for Plan Discuss only if they treat “remains” as no-op.

### acceptable — Scope & sibling boundaries
**Location:** `## Scope gate`, `## Files Changed`
**Finding:** Three-file footprint matches ticket partition; external helper is call-only; no frontend/candidate-table scanner creep.
**Recommendation:** None.

### acceptable — Resolve + recognition contract
**Location:** Stage 2 steps 3 + 5
**Finding:** Lookup-only miss path, config-driven known/unknown replies, recognition inserted before paste/Estelle block, unknown path skips paste/Estelle/hear-ack — satisfies child AC 1–3 and parent intent for retire-create-on-miss.
**Recommendation:** None.

### acceptable — Dependency on AST-1667
**Location:** `## Scope gate` Depends on; Stage 2 step 4
**Finding:** `list_workspace_posters()` is present on the epic worktree (`src/external/slack.py`); plan return-shape contract matches sibling.
**Recommendation:** None.

## R6 checklist (summary)

- Definition fidelity: pass — implements child #2 slice; defers poster fetch and Manage Candidates UI to siblings.
- AC coverage: pass — all six child AC bullets mapped in Execution contract.
- DRY / scope creep: pass — reuses `get_candidate_id_for_query`, existing post/activity patterns.
- Self-assessment: pass — estimate 5 with three staged commits and explicit decisions is honest.

context_tokens≈48000

---

[plan-rubric] PROCEED (Commit: 8d4d98de29c06d61005e9572f9c30c0674f549c1) Contact orchestration plan sound

## Review (build stub)

| Field | Value |
|-------|-------|
| Status | Code Complete |
| Publish ref | `origin/sub/AST-1636/AST-1668-contact-unbound-known-unknown-resolve` |
| Tip | `bf386176` |
| Branch | `sub/AST-1636/AST-1668-contact-unbound-known-unknown-resolve` |

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `8f1fe6dc` | `CONTACT_CONFIG` known/unknown recognition reply text keys |
| 2 | `141ab871` | unbound list, lookup-only resolve, recognition + contact listen info |
| 3 | `bf386176` | admin GET `/unbound_slack_users` |

**Betty note:** coverage for lookup-only resolve (no prospect), known/unknown recognition posts, unbound filter vs bound ids, and `@require_admin` unbound GET deferred to qa-child.

**Joan discuss addressed in build:** after `run_contact_estelle_turn` returns on the known path, emit canonical `stat.logging.info.contact` listen info line (before hear-ack).

## Radia review

[code-rubric]
**Ticket:** AST-1668
**Publish ref:** `c465a815ef891035236b7edce0373c7dc2a90230` (`origin/sub/AST-1636/AST-1668-contact-unbound-known-unknown-resolve`)
**Corpus:** `fc0c368e5927a57f1561c057ce9a0ff4abe1fb13`
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.info.contact | A | | |
| stat.logging.info.api | A | | |
| stat.logging.debug | B | | |
| stat.logging.error | A | | |

## Column diff vs plan stage

- `stat.logging.info.contact`: Joan **C** → Radia **A** — build emits canonical `contact listen` info line after `run_contact_estelle_turn` on the known path (`handle_slack_event` ~1778–1790).
- `stat.logging.debug`: Joan **B** → Radia **B** — `list_unbound_slack_users` uses statute joints; rest of `contact.py` retains Style D `debug_index`/`debug_detail` (plan-acknowledged mix).
- `stat.logging.info.api`, `stat.logging.error`: aligned with Joan **A**.

## Frame diff

(none)

## Findings

### advisory — Three-dot diff vs `origin/dev` is epic-polluted
**Location:** `git diff origin/dev...origin/sub/AST-1636/AST-1668-contact-unbound-known-unknown-resolve`
**Finding:** Multiple merge bases + stacked epic history inflate the three-dot diff (canon migration, sibling tickets, AST-1667, etc.). **AST-1668 product commits are scoped:** `8f1fe6dc` (+5 config), `141ab871` (contact), `bf386176` (api) — three files only.
**Recommendation:** Score footprint from ticket commits, not raw three-dot stat. Note for downstream doc hygiene.

### advisory — Branch history includes sibling AST-1667
**Location:** Publish-branch ancestry (`eb152ca2` … `827f1fa5`)
**Finding:** Expected dependency — `list_unbound_slack_users` calls `list_workspace_posters()` from AST-1667. No AST-1668 product code in `src/external/slack.py`.
**Recommendation:** None — dependency is declared in plan.

## What's solid

- **AC 1:** `initiate_prospect_candidate` absent from `contact.py`; miss + `estelle_in_play` is lookup-only with profile fetch, `created=False`.
- **AC 2–3:** Known path posts `known_recognition_reply_text` then Estelle; unknown posts `unknown_recognition_reply_text`, sets `estelle_turn` skip marker, skips paste/Estelle/hear-ack — no PROSPECT mint.
- **AC 4–5:** `list_unbound_slack_users` filters via `get_candidate_id_for_query`; preserves poster order; tests cover bound-id omission.
- **AC 6:** `GET /api/admin/contact/unbound_slack_users` is `@require_admin`; 401/403/502 paths tested; no progress `info` on idempotent GET (`info.assert_not_called()`).
- **Config:** Recognition defaults + asserts match Stage 1 plan.
- **API errors:** `logger.exception` with live facts + next-step wording on upstream failure.
- **Tests:** Manifest suites (`TestAst1668UnboundAndRecognition`, revised `TestAst1068ResolveSlackUser`, revised `TestAst1101ChannelHearEvidence`, config + API) align with bible intent.
- **Estimate 5** fits three staged commits + focused test coverage.

## Recommended actions (Chuckles downstream — not Radia lane)

- Append artifact to `docs/features/contact/ast-1668-contact-unbound-known-unknown-resolve.md`, commit `docs(AST-1668): Radia review — clean`, push sub ref.
- Post slim upshot via `linear_proxy --as radia save-comment`; move **Review Posted** → **User Testing** (PROCEED, no fix-now items).

---

**Slim Linear upshot (Chuckles posts):**

```
[code-rubric] PROCEED (Commit: c465a815) unbound resolve clean
```

context_tokens≈58000

## Bug: AST-1738 — Manage Candidates Slack username dropdown shows no users

### As-is

On Manage Candidates add/edit, the Slack username dropdown opens with no selectable users (only the empty/none option), so admins cannot bind a known Slack identity onto a candidate.

### To-be

The unbound list that feeds the dropdown includes workspace members/guests who are not already bound on a non-deleted candidate, so the Slack username `<select>` shows those people for binding.

### Repro

1. Admin opens Manage Candidates → Add Candidate (or Edit).
2. Open the **Slack username** dropdown.
3. Observe: no workspace users listed (cannot assign a known Slack user to the candidate).
4. Optional API check: `GET /api/admin/contact/unbound_slack_users` returns `{"users": []}` (or omits the people visible in the Slack workspace directory) while human members/guests exist who are not on any candidate's `contact.slack_user_id`.

### Root cause

`list_unbound_slack_users` builds the bind pool exclusively from `list_workspace_posters()` (Slack message authors the bot can read across conversations). That set is empty or near-empty in UAT for the Astral workspace (bot visibility / no scannable history), so the admin GET returns `users: []`. Manage Candidates (`AdminManageCandidates.tsx`) correctly renders whatever the GET returns — the empty dropdown is not a missing `<option>` wiring bug. Parent AST-1636 originally required a poster-derived pool; UAT to-be revises the **bind** pool to workspace members/guests (not already on a candidate).

### Proposed change

⚠️ **Decision — UAT revises bind-pool source:** For Manage Candidates bind only, stop using message-author posters as the unbound source. Use paginated Slack `users.list` humans (members/guests), excluding bots and deleted users, then subtract ids already on non-deleted candidates via `get_candidate_id_for_query`. Leave `list_workspace_posters()` implemented and exported (AST-1667) but **do not** call it from `list_unbound_slack_users`. This supersedes parent AC 10 / Technical-scope “not users.list alone as has posted” **for the unbound bind list only**; resolve / recognition / poster helper body stay as shipped.

1. In `src/external/slack.py`:
   - Add public **`list_workspace_members() -> list[dict]`** returning `[{"slack_user_id": str, "username": str}, …]`.
   - Gate once with `require_controlled_external_io("slack.list_workspace_members")`.
   - Paginate bot-token `users.list` (`limit=200`, cursor until empty) via the existing private `_slack_bot_get` (or the same GET pattern poster helpers use).
   - For each user dict: skip if `is_bot` or `deleted`; else append `slack_user_id` = `id` (non-empty str), `username` = `str(user.get("name") or "").strip()`.
   - Sort by `(username.lower(), slack_user_id)` for stable dropdown order (same as posters).
   - On `ok:false` / HTTP failure: **raise** (same hard-fail style as `_enrich_posters` / `list_workspace_posters`) — do not log-and-re-raise; callers/API log per `stat.logging.error`.
   - `logger.debug` joints per `stat.logging.debug`: Calling / Response on the public entry; Beginning/End on the users.list pagination loop with counts; no truncate; no `if debug` gate at call sites.
   - Add `"list_workspace_members"` to `__all__`; mention it in the module docstring next to the poster helper.
   - Do **not** change `list_workspace_posters` behavior in this bug.

2. In `src/core/contact.py` **`list_unbound_slack_users`**:
   - Import and call `list_workspace_members` instead of `list_workspace_posters`.
   - Keep the same bind filter: drop rows whose `slack_user_id` matches `get_candidate_id_for_query(..., debug=debug)`.
   - Keep return shape `[{"slack_user_id", "username"}, …]` and preserve member-list order after filter.
   - Update docstring + debug callee names/strings to members (not posters).
   - Propagate exceptions to `api_contact` (no catch-and-re-raise).

3. Do **not** change `src/ui/api/api_contact.py` route path, auth, or JSON envelope (`{"users": …}`) unless a compile touch is forced by import rename (none expected).
4. Do **not** change `AdminManageCandidates.tsx` for this bug — it already loads the GET and labels by `username`. Optional comment-only cleanup (“posters” → “members”) is out of scope unless make-fix is already touching that file for another reason.

### Blast radius

- Sibling AST-1669 dropdown UI: unchanged contract shape; options will populate once GET returns members.
- Sibling AST-1667 `list_workspace_posters`: remains; unbound path stops calling it.
- Betty component tests that stub `list_workspace_posters` for unbound / assume empty-poster ⇒ empty unbound will need revise to stub `list_workspace_members` (fix-board / qa-fix).
- Parent AST-1636 AC 9–10 (poster pool / not users.list alone): bind-pool product meaning changes under this UAT bug; poster helper AC for AST-1667 stays.
- `resolve_slack_user` / recognition replies / hear-ack: untouched.

### What must still hold

- Unbound GET remains `@require_admin`; idempotent GET still emits no progress `info` (`stat.logging.info.api`).
- Bots and deleted Slack users never appear in the unbound list.
- Slack user ids already on a non-deleted candidate's `contact.slack_user_id` stay omitted (AST-1668 AC 4–5).
- After bind, that user disappears from a subsequent unbound GET (AST-1669 still stamps both contact fields).
- No Slack Web API URLs/tokens from React (parent AC 7).
- Lookup-only resolve + known/unknown recognition (AST-1668 AC 1–3) unchanged.
