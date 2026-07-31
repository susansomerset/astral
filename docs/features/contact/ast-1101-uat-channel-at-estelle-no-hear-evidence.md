# AST-1101 — UAT: Channel @Estelle — no Contact hear evidence (activity / reply)

**Linear:** [AST-1101](https://linear.app/astralcareermatch/issue/AST-1101/uat-channel-estelle-no-contact-hear-evidence-activity-reply)  
**Parent:** [AST-1043](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent) — Slack Bot Agent  
**Publish ref:** `origin/sub/AST-1043/AST-1101-uat-channel-at-estelle-no-hear-evidence`

Staging verifies Slack Request URL (challenge OK) and Manage Slack listen shows on, but channel `@Estelle` produces no UAT-visible Contact hear evidence: no Manage Slack activity row and no non-prod `[<environment>]` reply. This bug restores accept → durable activity record → hear-ack (or Estelle turn reply) for channel `app_mention` when listen is on. Full dialogue quality remains AST-1046 / AST-1073; this ticket is hear/accept + UAT evidence only.

---

## UAT fitness

- **AC restored:** Parent AC #2 — "signed events are verified and ack’d; Estelle-relevant DMs/@-mentions reach Contact when Manage Slack listen is on." Parent AC #3 — "when on for non-production, replies are prefixed with `[<environment>]`." Parent AC #9 — "Admin **Manage Slack** lists Slack users who have @'ed Estelle: bind success/fail … inbound message count … timestamp + channel of the last message seen."
- **Correct outcome:** With listen on and Estelle in the channel, `@Estelle` → Contact accepts; Manage Slack activity row updates for that Slack user; non-prod outbound (Estelle turn reply **or** hear-ack fallback) carries `[<environment>]`.
- **Sibling check:** AST-1069 verify/ack/challenge unchanged; AST-1067 listen file + prefix helpers remain SoT; AST-1068 resolve/PROSPECT still owns bind; AST-1094 activity JSON API/UI unchanged in shape; AST-1070 cache append on accept stays; AST-1073 turn still runs when able. Verified by not editing Socket Mode production transport, fabricating activity without accept, or rewriting Estelle envelope schema.
- **Not sufficient:** Removing a stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Fabricating Manage Slack rows without a real accept; switching production ingress to Socket Mode; swallowing async handler errors without logging; treating “no conversational envelope” as done while AC #2/#3/#9 still fail.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `hear_ack_reply_text` on `CONTACT_CONFIG` + import-time assert | utils |
| `src/core/contact.py` | Always re-read durable listen file in `slack_listen_enabled`; log-wrapping Events background thread; after accept, hear-ack Slack post when Estelle turn did not post | core |

No edits to `src/external/slack.py` (signing / `post_message` stay dumb), Events UI blueprint, Manage Slack React/API list shape, activity data module schema, resolve/PROSPECT internals, conversation-cache key rules, Socket Mode script, or Estelle envelope (`TASK_CONFIG` / AST-1072).

---

## Stage 1: Config — hear-ack reply text

**Done when:** `CONTACT_CONFIG` exposes a non-empty hear-ack string used only as fallback outbound text; import-time assert passes; no runtime behavior change yet.

1. In `src/utils/config.py`, inside `CONTACT_CONFIG`, immediately after `"non_production_reply_prefix_template": "[{environment}] ",`, add:

```python
    # AST-1101: fallback Slack text when Contact accepts @/DM but Estelle turn posts nothing.
    "hear_ack_reply_text": "Heard you — Estelle is listening.",
```

2. After the existing assert on `non_production_reply_prefix_template` (or adjacent CONTACT_CONFIG asserts), add:

```python
assert isinstance(CONTACT_CONFIG["hear_ack_reply_text"], str) and CONTACT_CONFIG["hear_ack_reply_text"].strip()
```

⚠️ **Decision — config string, not hardcoded in Contact:** Call sites must not invent reply copy; operators can change wording without code edits. Prefix still comes only from `format_contact_reply_text` (AST-1067).

**Done when (recheck):** `CONTACT_CONFIG["hear_ack_reply_text"]` is a non-empty `str`.

---

## Stage 2: Core — durable listen re-read + logged Events worker + hear-ack

**Done when:** (1) `slack_listen_enabled()` always reflects the durable JSON under `db_dir` when present; (2) Exceptions in the post-ack `handle_slack_event` thread are logged via `get_logger` (not silent daemon death); (3) After an **accepted** inbound with a channel, if Estelle turn did not produce a successful Slack post, Contact posts one hear-ack via `format_contact_reply_text` + `contact_post_message` (prefix + cache append); activity recording path from AST-1094 is unchanged and still runs on accept before the turn.

### 2.1 Listen — durable file is SoT every call

1. In `src/core/contact.py`, change `slack_listen_enabled` so it **always** calls `load_contact_listen_enabled()` and, when the return value is not `None`, assigns `CONTACT_CONFIG["listen_enabled"] = loaded` before returning `bool(CONTACT_CONFIG["listen_enabled"])`.
2. Remove the once-only short-circuit from `_hydrate_listen_state` **or** delete `_hydrate_listen_state` / `_listen_hydrated` if unused after this change. `set_slack_listen_enabled` must still write the file **and** set `CONTACT_CONFIG["listen_enabled"]` (keep existing persist behavior).
3. Do **not** invent a multi-worker sync story — `astral.ui.single-gunicorn-worker` still holds. Re-read fixes stale in-process `False` after Admin toggles listen on (and any hydrate-once race).

⚠️ **Decision — re-read every `slack_listen_enabled()` call:** AST-1067 chose once-hydrate for speed; UAT shows challenge OK + UI “on” with no accept evidence — classic sticky in-process default. A small JSON read per event/admin GET is acceptable; durable file remains SoT across restarts.

### 2.2 Events HTTP — never swallow handler failures

1. In `receive_slack_events_http`, replace the bare `threading.Thread(target=handle_slack_event, …)` with a small private wrapper (e.g. `_run_handle_slack_event_background(payload, debug)`) that:
   - Calls `handle_slack_event(payload, debug=debug)` inside `try/except Exception`.
   - On exception: `get_logger(__name__).error("contact handle_slack_event background failed: %s", exc, exc_info=True)`.
   - Does **not** re-raise into the request path (ack already returned).
2. Keep ack-before-work (200 empty body) and do **not** move verify/challenge.

### 2.3 Hear-ack after accept when turn posts nothing

1. In `handle_slack_event`, after the existing AST-1094 `record_estelle_activity` block and the existing `run_contact_estelle_turn` try/except (leave both in place), add:

   - Preconditions: `result["accepted"] is True`, `channel` is a non-empty `str`.
   - Inspect `result.get("estelle_turn")` (may be missing if turn not run): treat as “posted” only when it is a `dict` and `isinstance(estelle_turn.get("slack_post"), dict)` and `estelle_turn["slack_post"].get("ok") is True`.
   - If **not** posted:  
     `outbound = format_contact_reply_text(str(CONTACT_CONFIG["hear_ack_reply_text"]))`  
     then `contact_post_message(channel=channel, text=outbound, thread_ts=event.get("thread_ts") or (msg_ts if isinstance(msg_ts, str) else None), debug=debug)`.  
     Store the return value on `result["hear_ack_post"]`. Wrap in `try/except Exception` and `log.error` on failure (do not unset `accepted`).
   - If Estelle turn already posted successfully: do **not** post hear-ack (no double reply).
2. Thread ts rule: prefer Slack `thread_ts` when present; else use message `ts` so channel-root @ replies land in a thread under the mention (same pattern as AST-1073 turn outbound).
3. `debug=True`: Style D index + detail for hear-ack path (`func="contact.handle_slack_event"`, outcome `hear_ack_posted` or `hear_ack_failed`), including whether prefix applied is visible only via the already-formatted outbound preview (truncate with `_TEXT_DEBUG_MAX`).

⚠️ **Decision — hear-ack is fallback only, not a fake activity row:** Activity still records only on real accept (AST-1094). Hear-ack proves Contact heard when Estelle turn / live I/O / do_task cannot produce a reply — restores AC #3 UAT evidence without claiming full Estelle dialogue quality.

⚠️ **Decision — compose `format_contact_reply_text` + `contact_post_message`:** Same as AST-1073 — prefix + cache append; do not call `post_contact_reply` (no cache) and do not change `external.slack.post_message`.

**Done when (recheck):** With listen file `true`, an `app_mention` payload through `handle_slack_event` records activity and either an Estelle `slack_post` or a hear-ack post whose text starts with `[` + deploy label when non-prod; with listen file `false`, `accepted=False` / `listen_off` and no activity write / no hear-ack.

---

## Stage 3: Self-check

**Done when:** Import direction holds; no UI/external signature changes; no fabricated activity without accept.

1. Confirm `src/ui/api/api_slack.py` still only calls `receive_slack_events_http`.
2. Confirm Manage Slack activity GET still uses `list_estelle_activity` (no UI changes required if Stage 2 records on accept).
3. Confirm Socket Mode / production transport unchanged.

---

## Out of scope (explicit)

- Slack app install wizard / Event Subscriptions dashboard clicks (ops — Request URL already verifies).
- Socket Mode as production ingress.
- Fabricating activity rows without accept.
- Estelle conversational rubric / envelope schema (AST-1072 / AST-1046 quality).
- Changing AST-1094 JSON schema or Manage Slack table columns.
- Multi-worker listen sync.

---

## Self-Assessment

**Scope:** `Single-Component` — Contact core listen/Events worker/hear-ack + one CONTACT_CONFIG string; no new modules.

**Conf:** `high` — Durable listen file already exists (AST-1067); activity record already on accept (AST-1094); Estelle turn already composes prefix + `contact_post_message` (AST-1073); bug maps to sticky hydrate + silent thread failures + turn-post gaps.

**Risk:** `Medium` — Wrong hear-ack could double-reply if “posted” detection is wrong; mitigated by requiring `slack_post.ok is True` before skipping hear-ack. Listen re-read fail-closed when file missing keeps config default.

## Review (build stub)

- **Publish ref:** `origin/sub/AST-1043/AST-1101-uat-channel-at-estelle-no-hear-evidence`
- **Tip:** `c7ff9851` — listen re-read + hear-ack (stages 1–2)
- **Stage commits:** `84d97108` (config), `c7ff9851` (contact)


---

## Radia review — code-rubric.v1

**Overall:** CLEAN  
**Publish tip reviewed:** `2a3ea72c` (`origin/sub/AST-1043/AST-1101-uat-channel-at-estelle-no-hear-evidence`)  
**Diff:** `origin/dev...2a3ea72c` — layers `{core, utils, docs}`; change_types `{add, modify}`; 7 paths (focused UAT hear evidence).

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
| astral.config.config-source-of-truth | scoped | conforms | hear_ack_reply_text in CONTACT_CONFIG |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | no threshold/score-floor edits |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no new secret literals |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss artifacts/** / scripts/spikes/** |
| astral.debug.spikes-under-debug-dir | scoped | conforms | plan under docs/features — not spike notes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | one plan file AST-1101 |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty test/merge-tests touch tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer code() commits touch src only |
| astral.layers.core-vs-external-bright-line | scoped | conforms | no external edits; post via contact_post_message |
| astral.layers.import-direction | scoped | conforms | core+utils only; UI/external signatures unchanged |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts/** in diff |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | no ui layer in three-dot tip |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | no coat-check |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | no consult |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | no ui/** in tip |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no data layer in tip |
| astral.standards.database-header-inventory | scoped | not-applicable | no data/** in tip |
| astral.standards.debug-contract-gated | scoped | conforms | Style D on hear-ack when debug=True |
| astral.standards.dry-and-focused-functions | scoped | conforms | small background wrapper + hear-ack block |
| astral.standards.in-scope-only | scoped | conforms | no Socket Mode / envelope / activity schema ownership |
| astral.standards.logging-via-utils | scoped | conforms | background failures via get_logger |
| astral.standards.no-cross-contamination | scoped | conforms | three-dot tip is 7 focused paths |
| astral.standards.no-hardcoded-sets | scoped | conforms | hear-ack copy from CONTACT_CONFIG |
| astral.standards.public-then-helpers | scoped | conforms | private _run_handle_slack_event_background |
| astral.standards.utils-data-late-import-only | scoped | conforms | config has no data import |
| astral.state.core-decides-transitions | scoped | conforms | no state transition ownership |
| astral.state.job-prior-states-enforced | scoped | conforms | no job prior-state edits |
| astral.state.no-daisy-chain-in-run | scoped | conforms | no dispatch chain |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend in tip |
| astral.ui.naming-conventions | scoped | not-applicable | no ui/** in tip |
| astral.ui.single-gunicorn-worker | scoped | conforms | durable listen re-read; no multi-worker invent |
| orch.git.betty-merge-tests-one-sha | universal | conforms | merge-tests SHA 2a3ea72c |
| orch.git.commit-vocabulary | universal | conforms | plan/code/test/merge-tests vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | publish on origin/sub/AST-1043/AST-1101-… |
| orch.git.ftr-sub-topology | universal | conforms | matches parent Git table |
| orch.git.merge-on-checkout | universal | conforms | tip tree vs origin/dev focused; no lost AST-1017 paths |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | none observed |
| orch.git.no-dev-agent-branches | universal | conforms | uses sub/AST-1043/AST-1101-… |
| orch.git.one-epic-worktree-per-parent | universal | conforms | astral-AST-1043 |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Decisions held (re-read listen; hear-ack fallback) |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–2 land as planned |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Contact child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no statute authorship |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns test/bible + merge-tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Hedy through Tests Passed |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | implementer Hedy remains assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | doc-only review commit paths |

### Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.core.contact-agent (proposed) | conforms | listen re-read + Events log wrap + hear-ack |
| pattern.config.config-block | conforms | CONTACT_CONFIG hear_ack_reply_text |

### Plan adherence

Stages 1–2 match: `hear_ack_reply_text`, remove once-hydrate, background exception log, hear-ack only when accepted + channel and Estelle `slack_post.ok` is not True, via `format_contact_reply_text` + `contact_post_message`. Self-Assessment Single-Component / high / Medium matches footprint. Sibling boundaries held.

### Findings

None.

### What’s solid

Sticky listen hydrate removed; daemon thread failures logged; hear-ack is fallback not fabricated activity; prefix still only via AST-1067 helper; no verify/challenge/UI edits.

### Notes

no plan-rubric verdict attached

## Resolution

**Date:** 2026-07-31  
**Review tip:** `f695eea8` (`docs(AST-1101): Radia review — clean`)  
**Overall:** CLEAN — **no fix-now**

- Acknowledged Radia **CLEAN** (`[code-rubric] revision=1`): Findings none; Stages 1–2 match plan; sibling boundaries held.
- No product or plan ACL changes in resolve.

