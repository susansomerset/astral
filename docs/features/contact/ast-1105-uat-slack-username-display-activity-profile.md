# AST-1105 — UAT: Slack username/display on Manage Slack activity + Profile

**Linear:** [AST-1105](https://linear.app/astralcareermatch/issue/AST-1105/uat-slack-usernamedisplay-on-manage-slack-activity-profile)  
**Parent:** [AST-1043](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent) — Slack Bot Agent  
**Publish ref:** `origin/sub/AST-1043/AST-1105-uat-slack-username-display-activity-profile`

UAT gap after AST-1094: Manage Slack @Estelle activity rows show only opaque `U…` Slack user ids, and Candidate Profile does not surface Slack user id / Slack username for Slack-bound candidates. `fetch_user_profile` / `resolve_slack_user` already call Slack `users.info` for PROSPECT first/last seed but do not return or persist Slack **username** (`user.name`), do not store display name on activity rows, and Profile NAV fields omit `contact.slack_user_id` / `contact.slack_username`.

**Depends on:** AST-1094 (activity JSON + Manage Slack table), AST-1068 (`resolve_slack_user` + `contact.slack_user_id`), AST-1067 (Manage Slack page) — on tip / `origin/dev`.

---

## UAT fitness

- **AC restored:** Parent AC #4 — "Slack @Estelle resolves via `get_candidate_id_for_query` (AST-1047) using Slack user id; first unknown Slack user creates **PROSPECT** with Slack user id stored and Slack-seeded profile fields; no @ means no candidate row from Slack." Parent AC (quoted as #5 on this bug; same Manage Slack list AC as prior #9) — "Admin **Manage Slack** lists Slack users who have @'ed Estelle: bind success/fail to an Astral candidate, inbound message count from that Slack user, and timestamp + channel of the last message seen." — restored with human-readable Slack identity on those rows plus Profile Slack id/username.
- **Correct outcome:** Activity list shows username and/or display name **plus** Slack user id (bind/count/channel/ts held); Profile shows Slack user id and Slack username for Slack-bound candidates.
- **Sibling check:** AST-1094 activity persistence/API shape extended only with optional identity fields; AST-1068 resolve still keys on Slack user id via `get_candidate_id_for_query` (no second matcher); AST-1067 listen switch unchanged; AST-1101 hear path unchanged. Verified by not editing Events verify/ack, listen flip, turn envelope, or Socket Mode production ingress.
- **Not sufficient:** Removing a stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Fabricating display names without Slack `users.info`; scraping Slack HTML; inventing a second identity matcher beside `get_candidate_id_for_query`; Socket Mode as production ingress.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/external/slack.py` | `fetch_user_profile`: add `username` from Slack `user.name` | external |
| `src/core/contact.py` | Persist `contact.slack_username` on PROSPECT create; return username/display from resolve; backfill username on match when missing; pass identity into `record_estelle_activity` | core |
| `src/data/contact_estelle_activity.py` | Optional `slack_username` + `slack_display_name` on record/list rows | data |
| `src/utils/config.py` | Profile Contact Information fields: `contact.slack_user_id`, `contact.slack_username` | utils |
| `src/ui/frontend/src/pages/AdminManageSlack.tsx` | Activity table columns for username / display name | ui |

No Events signing/challenge changes. No listen flip changes. No turn-loop / envelope. No Socket Mode production path. Do **not** add a second candidate matcher. Do **not** invent names without `users.info`. Do **not** put Slack username into `CONTACT_CONFIG["skills"]["save_candidate_contact"]["allowed_paths"]` (same ownership rule as `slack_user_id` — Contact resolve owns it).

---

## Stage 1: External — `users.info` username

**Done when:** `fetch_user_profile` returns `username` (Slack login name) alongside existing `first` / `last` / `display_name` / `slack_user_id`.

1. In `src/external/slack.py`, inside `fetch_user_profile`, after reading `user` / `profile`, set:

```python
    username = str(user.get("name") or "").strip()
```

2. Add `"username": username` to the returned dict (empty string when Slack omits it — never fabricate).

⚠️ **Decision — username = Slack `user.name`:** That is the workspace username/handle. Display name stays `profile.display_name` / `real_name` (already returned). Do not invent a synthetic handle from first/last.

**Done when (recheck):** Return keys include `username`; still no logging in external.

---

## Stage 2: Data — activity row identity fields

**Done when:** `record_estelle_activity` accepts optional `slack_username` / `slack_display_name` and persists them on the row; list returns them; missing previous rows stay valid without those keys.

1. In `src/data/contact_estelle_activity.py`, extend `record_estelle_activity` signature with:

```python
    slack_username: Optional[str] = None,
    slack_display_name: Optional[str] = None,
```

2. When building `row`, after `slack_user_id`:

```python
        "slack_username": slack_username.strip()
        if isinstance(slack_username, str) and slack_username.strip()
        else (prev.get("slack_username") if isinstance(prev.get("slack_username"), str) else None),
        "slack_display_name": slack_display_name.strip()
        if isinstance(slack_display_name, str) and slack_display_name.strip()
        else (prev.get("slack_display_name") if isinstance(prev.get("slack_display_name"), str) else None),
```

Preserve prior identity when a later record call passes `None` (e.g. transient `users.info` failure) so counts still update without wiping names.

**Done when (recheck):** New record with names → list row includes them; second record with `None` names keeps prior names and increments count.

---

## Stage 3: Core — resolve persist + activity identity

**Done when:** New PROSPECTs store `contact.slack_user_id` **and** `contact.slack_username`; resolve return includes `slack_username` / `slack_display_name`; matched candidates missing username get a one-time backfill via `users.info` + `save_candidate_data`; activity record receives those fields.

1. In `resolve_slack_user` **create** path, change `candidate_data` to:

```python
    username = str(profile.get("username") or "").strip()
    candidate_data = {
        "contact": {
            "slack_user_id": sid,
            "slack_username": username,
        },
    }
```

Return dict gains:

```python
        "slack_username": username,
        "slack_display_name": display,
```

2. In **found** path (existing `cid`), after loading the row:

- Read `contact = (row.get("candidate_data") or {}).get("contact")` if dict.
- `username = contact.get("slack_username")` if str else `""`.
- `display` may be empty on found (activity still needs display): if `username` is empty **or** you need display for activity, call `fetch_user_profile(sid)` once.
- If username was empty and fetch returns a username, merge via `save_candidate_data(cid, {"contact": {"slack_user_id": sid, "slack_username": username}}, debug=debug)` (merge keeps other contact keys).
- Always return `slack_username` / `slack_display_name` on the resolve result (strings, possibly empty).

3. In `handle_slack_event`, after resolve succeeds or fails with a user id, when calling `record_estelle_activity`, pass:

```python
                slack_username=resolved.get("slack_username")  # only when resolve ran
                # Prefer: stash resolved dict; on resolve exception leave names None.
```

Concrete wiring:

- Keep a local `resolved_meta = {"slack_username": None, "slack_display_name": None}` before resolve.
- On successful resolve, set from return keys.
- On resolve exception with a user, optionally `try: fetch_user_profile(user_for_activity)` for activity names only (do not create candidate).
- Pass into `record_estelle_activity`.

⚠️ **Decision — backfill on match, not Profile→Slack scrape:** Existing Slack-bound PROSPECTs created before this ticket lack `contact.slack_username`. Next @Estelle accept fills Profile + activity. Do not call Slack from the Profile UI.

⚠️ **Decision — no second matcher:** Lookup remains `get_candidate_id_for_query(slack_user_id)` only.

**Done when (recheck):** Create path stores username; match path returns username (backfill if needed); activity row after accept has `slack_username` and/or `slack_display_name` when Slack provides them.

---

## Stage 4: Config — Profile Slack fields

**Done when:** Candidate Profile Contact Information section lists Slack user id and Slack username keys.

1. In `src/utils/config.py`, inside `NAV_CONFIG` (or the profile detail block that serves Candidate Profile — the `"label": "Contact Information"` fields list under `detail.profile`), immediately after the name fields / before email fields, insert:

```python
                        {"key": "contact.slack_user_id", "label": "Slack user id", "type": "text"},
                        {"key": "contact.slack_username", "label": "Slack username", "type": "text"},
```

Exact insertion: after `{"key": "full", ...}` and before `contact.contact_email` in that Contact Information `fields` list (same block ~line 4037 area).

2. Do **not** add these paths to `CONTACT_CONFIG["skills"]["save_candidate_contact"]["allowed_paths"]`.

⚠️ **Decision — ordinary text fields:** FormFields has no read-only type; showing empty for non-Slack candidates is fine. Resolve owns writes; UAT can see values after bind.

**Done when (recheck):** `/api/nav_config` (or profile field payload) includes both keys with those labels.

---

## Stage 5: Manage Slack UI — show names

**Done when:** Activity table shows Slack username and display name in addition to Slack user id; empty names render as `—`; bind/count/channel/ts unchanged.

1. In `AdminManageSlack.tsx`, extend `EstelleActivityRow`:

```ts
  slack_username: string | null
  slack_display_name: string | null
```

2. Map those fields from the activity API JSON (same null/string guards as other columns).

3. Table header: add **Username** and **Display** after **Slack user** (or replace the single Slack user cell with id + username/display — prefer **separate columns** for clarity):

| Slack user | Username | Display | Bind | Candidate | Messages | Last channel | Last ts |

4. Cells: `row.slack_username || "—"`, `row.slack_display_name || "—"`.

**Done when (recheck):** Empty store still shows empty-state row; mocked users with names render in the new columns.

---

## Self-assessment

**Scope:** `MAJOR-CHANGE` — external profile shape + resolve contact persist/backfill + activity row fields + Profile NAV fields + Manage Slack columns.

**Conf:** `high` — reuses existing `users.info` helper and AST-1094 activity/UI path; AC maps to concrete fields.

**Risk:** `Medium` — extra `users.info` on match-without-username; mitigated by one call per accept and preserving prior activity names when fetch fails; no fabricated identities.

---

## Out of scope (do not implement)

- Fabricating usernames without Slack
- Second matcher / Socket Mode production ingress
- Events verify/ack, listen switch, Estelle turn envelope
- Adding slack_username to Contact skill ACL write paths
- Backfilling all historical activity rows via Slack history APIs (next @Estelle fills names)

---

## Review (build stub)

| Field | Value |
|-------|-------|
| Status | Code Complete |
| Publish ref | `origin/sub/AST-1043/AST-1105-uat-slack-username-display-activity-profile` |
| Tip | `25d810bb` |
| Branch | `sub/AST-1043/AST-1105-uat-slack-username-display-activity-profile` |

Stages 1–5 landed: `fetch_user_profile.username`, activity identity fields, resolve persist/backfill + activity wiring, Profile Slack fields, Manage Slack Username/Display columns.


---

## Radia review — code-rubric.v1

**Overall:** FIX-NOW  
**Publish tip reviewed:** `a39f94db` (`origin/sub/AST-1043/AST-1105-uat-slack-username-display-activity-profile`)  
**Diff:** `origin/dev...a39f94db` — layers `{core, data, external, utils, ui, docs}`; change_types `{add, modify}`; 16 paths (AST-1105 product + Betty bible/tests, with sibling-epic test bleed).

### Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | conforms | no graded agent tasks |
| astral.agent.do-task-delegation | scoped | conforms | no do_task |
| astral.agent.grade-vector-validation | scoped | conforms | no grade vectors |
| astral.batch.batch-id-first | scoped | conforms | no batch claim |
| astral.batch.batch-id-format | scoped | conforms | no batch_id |
| astral.batch.claim-process-release | scoped | conforms | no batch processing |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | no agent_data |
| astral.config.config-source-of-truth | scoped | conforms | Profile Slack keys in DATA_SHAPES; username from Slack |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | no threshold/score-floor edits |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no new secret literals |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss artifacts/** / scripts/spikes/** |
| astral.dispatch.seed-auto-false | scoped | conforms | config Profile Slack fields only; no dispatch seed |
| astral.debug.spikes-under-debug-dir | scoped | conforms | plan under docs/features — not spike notes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | one plan file AST-1105 |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty test/merge-tests touch tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer code() commits touch src only |
| astral.layers.core-vs-external-bright-line | scoped | conforms | users.info username in external; Contact orchestrates |
| astral.layers.import-direction | scoped | conforms | ui→core→data/external; UI never imports slack |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts/** in tip |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | table renders API identity fields; Profile via config |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | no coat-check |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | no consult |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | no new unauth surface; existing admin/Profile auth |
| astral.standards.data-raises-caller-logs | scoped | conforms | data silent; core logs fetch/backfill failures |
| astral.standards.database-header-inventory | scoped | conforms | JSON activity fields only; no new SQLite table |
| astral.standards.debug-contract-gated | scoped | conforms | Style D details include slack_username when debug |
| astral.standards.dry-and-focused-functions | scoped | conforms | reuse fetch_user_profile; thin activity field extend |
| astral.standards.in-scope-only | scoped | conforms | product stages stay on identity/UI; no Events/listen/turn |
| astral.standards.logging-via-utils | scoped | conforms | Contact logger; external silent |
| astral.standards.no-cross-contamination | scoped | violates | tip adds AST-1099 pin tests/bible without pin product on tip |
| astral.standards.no-hardcoded-sets | scoped | conforms | identity from Slack payload / contact paths |
| astral.standards.public-then-helpers | scoped | conforms | public resolve/record surfaces; private identity helper |
| astral.standards.utils-data-late-import-only | scoped | conforms | config has no data import |
| astral.state.core-decides-transitions | scoped | conforms | no state transition ownership |
| astral.state.job-prior-states-enforced | scoped | conforms | no job prior-state edits |
| astral.state.no-daisy-chain-in-run | scoped | conforms | no dispatch chain |
| astral.ui.frontend-file-placement | scoped | conforms | extends AdminManageSlack.tsx; Profile via DATA_SHAPES |
| astral.ui.naming-conventions | scoped | conforms | contact.slack_* keys; activity snake_case |
| astral.ui.single-gunicorn-worker | scoped | conforms | no worker config change |
| orch.git.betty-merge-tests-one-sha | universal | conforms | merge-tests SHA a39f94db |
| orch.git.commit-vocabulary | universal | conforms | plan/code/test/merge-tests vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | publish on origin/sub/AST-1043/AST-1105-… |
| orch.git.ftr-sub-topology | universal | conforms | matches parent Git table |
| orch.git.merge-on-checkout | universal | needs-discussion | merge-tests ancestry left AST-1099/1100 bible/test bleed |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | none observed |
| orch.git.no-dev-agent-branches | universal | conforms | uses sub/AST-1043/AST-1105-… |
| orch.git.one-epic-worktree-per-parent | universal | conforms | astral-AST-1043 |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Decisions held (user.name; no skill ACL; no fabricate) |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–5 product land as planned |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Contact child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no statute authorship |
| orch.roles.betty-owns-test-tree | universal | needs-discussion | Betty must scrub orphan AST-1099 tests off this tip |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Katherine through Tests Passed |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | implementer Katherine remains assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | doc-only review commit paths |

### Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.external.slack-web-api | conforms | fetch_user_profile.username from user.name |
| pattern.core.contact-agent (proposed) | conforms | persist/backfill + activity identity |
| pattern.config.config-block | conforms | Profile DATA_SHAPES Slack fields |

### Plan adherence

Stages 1–5 product match: external username, activity optional identity with prior-keep, resolve create/match backfill, Profile fields (not skill ACL), Manage Slack Username/Display columns. Self-Assessment MAJOR-CHANGE / high / Medium matches.

### Findings

**fix-now** — `astral.standards.no-cross-contamination` / merge integrity  
**Location:** tip vs `origin/dev` — `tests/component/utils/test_config.py::TestAst1099JobArtifactAgentDataPinConfig` + `docs/test-bible/utils/config.md` AST-1099 / AST-1100 sections.  
**Why:** Asserts `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK` and pin slots on `JOB_BUILD_ARTIFACT_CLEAR_KEYS` that are **not** on this Contact tip (pin map absent; clear keys still legacy-only). Orphan sibling-epic (AST-1091) test/bible bleed via merge-tests ancestry — would AttributeError/fail if run.  
**Action:** Betty scrub those AST-1099/1100 fragments off this publish tip (keep AST-1105 `TestAst1105ProfileSlackFields` + matching bible). Do not invent AST-1099 product on Contact tip.

**discuss** — `orch.git.merge-on-checkout` / `orch.roles.betty-owns-test-tree` — same bleed; engineer product is fine; test-tree scrub is Betty.

### What’s solid

Username from Slack `user.name` only; match-path backfill; activity preserves prior names on None; Profile keys not in Contact skill ACL; no second matcher; UI columns additive.

### Notes

no plan-rubric verdict attached

---

## Resolution

**Date:** 2026-07-31  
**Review tip:** `253200ee` (`docs(AST-1105): Radia review — include seed-auto-false statute`)  
**Overall:** FIX-NOW — **test-tree only** (no product fix)

- Radia **fix-now** `astral.standards.no-cross-contamination`: orphan AST-1099/1100 pin tests + bible sections on this Contact tip without pin product. Action is Betty scrub of `tests/` + `docs/test-bible/**` — engineer must not invent AST-1099 product here.
- **discuss** `orch.git.merge-on-checkout` / `orch.roles.betty-owns-test-tree`: same bleed; product Stages 1–5 held.
- **`[qa-handoff]`** to Betty; status stays **Review Posted** until scrub lands and Betty reassigns.

