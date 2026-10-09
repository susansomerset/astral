# Contact

**Test module:** `tests/component/core/test_contact.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/contact.py` | `tests/component/core/test_contact.py` | no |

---

### AST-1066 · AST-1043

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1066-contact-core-module-and-contact-config`.

Contact scaffold: `slack_listen_enabled`, `contact_skills` / `contact_skill_keys`, `slack_env_names` (`non_production_reply_prefix` removed **AST-2085** — `format_contact_reply_text` is a passthrough; `handle_slack_event` hear-ack test asserts no `[staging] ` prefix) — reads `CONTACT_CONFIG` only; no Slack HTTP / DB / skill runners. Config block: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Listen default / skills shallow copy / env names / no TASK_CONFIG collision | `src/core/contact.py` | **`TestAst1066ContactScaffold`** |

**Broken / obsolete:** empty-`skills` asserts superseded by **AST-1071** (scaffold still requires shallow-copy + collision checks).

**Integration:** no existing scenario asserts Contact / CONTACT_CONFIG — no revision; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1066ContactConfig \
  tests/component/core/test_contact.py::TestAst1066ContactScaffold \
  -q
```

---

### AST-1071 · AST-1043

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1071-contact-config-acl-entity-save-skills`.

ACL-gated `contact_skill_meta` / `run_contact_skill`: allowlisted `candidate_data` paths only via `save_candidate_data`; Style D when `debug=True`. Config inventory: **`docs/test-bible/utils/config.md`**. Admin HTTP: **`docs/test-bible/ui/api/api_contact.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Meta / allowlisted write / reject path·skill·missing / Style D on+off | `src/core/contact.py` | retired → **`TestAst2061ContactSkillsRetired`** |

**Broken / obsolete:** AST-1066 empty-skills asserts — revised in **`TestAst1066ContactScaffold`** / **`TestAst1066ContactConfig`**.

**Retired by AST-2061 / AST-2062:** skills ACL emptied; runner class replaced by TestAst2061ContactSkillsRetired.

**Integration:** no existing scenario asserts Contact skill runners — no revision.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1071ContactSkillsConfig \
  tests/component/core/test_contact.py::TestAst1071ContactSkillRunners \
  tests/component/ui/api/test_api_contact.py::TestAst1071ContactSkillsApi \
  -q
```

### AST-1069 · AST-1043

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1069-slack-events-api-webhook-ingress`.

`receive_slack_events_http` (verify / challenge / ack+schedule) + `handle_slack_event` (listen gate, `event_id` dedupe, `app_mention` + DM `message`). External HMAC/post: **`docs/test-bible/external/slack.md`**. Blueprint: **`docs/test-bible/ui/api/api_slack.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Listen/dedupe/type/DM filters; HTTP 401/challenge/ack | `src/core/contact.py` | **`TestAst1069ContactSlackIngress`** |

**Broken / obsolete:** none — additive Contact ingress.

**Integration:** no existing scenario asserts Slack Events — no revision.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_contact.py::TestAst1069ContactSlackIngress \
  tests/component/external/test_slack.py::TestAst1069ExternalSlack \
  tests/component/ui/api/test_api_slack.py::TestAst1069SlackEventsApi \
  -q
```

---

### AST-1068 · AST-1043

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1068-slack-resolve-via-get-candidate-id`.

`resolve_slack_user`: lookup via `get_candidate_id_for_query`; **AST-1668** retired create-on-miss (`initiate_prospect_candidate` removed from Contact) — miss + `estelle_in_play` fetches profile only (`created=False`, no PROSPECT); `handle_slack_event` accept wires resolve. Candidate: **`docs/test-bible/core/candidate.md`**. External: **`docs/test-bible/external/slack.md`**. Config: **`docs/test-bible/utils/config.md`**. Sibling unbound/recognition: **§ AST-1668** below.

| Area | Source | Component tests |
| --- | --- | --- |
| Resolve hit/miss lookup-only; Events accept wire | `src/core/contact.py` | **`TestAst1068ResolveSlackUser`** (revised **AST-1668**) |

**Broken / obsolete:** **`TestAst1069ContactSlackIngress`** accept-path — revised to stub `resolve_slack_user`. Create-on-miss asserts — **revised AST-1668** to lookup-only. Profile kwargs — revised for AST-1014 `first=`/`last=` kwargs.

**Integration:** no existing scenario asserts Slack resolve / PROSPECT create — no revision.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1068ProspectConfig \
  tests/component/core/test_candidate.py::TestAst1068CandidateSlackLookup \
  tests/component/external/test_slack.py::TestAst1068FetchUserProfile \
  tests/component/core/test_contact.py::TestAst1068ResolveSlackUser \
  tests/component/core/test_contact.py::TestAst1069ContactSlackIngress \
  -q
```


---

### AST-1070 · AST-1043

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1070-slack-sourced-conversation-context`.

Process-local conversation cache: `load_slack_conversation_context` returns Stage 3 envelope
`{"channel", "thread_ts", "messages", "source": "cache"|"slack"}` (cache hit / miss / TTL / `refresh=True`); empty/blank channel → `ValueError`; channel is stripped. `append_slack_conversation_message` warms+trims; `contact_post_message` appends outbound; inbound `handle_slack_event` keys DMs as `(channel, "")` never message `ts`. External fetch: **`docs/test-bible/external/slack.md`**. Config: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Envelope hit/miss/TTL/refresh; empty channel; append; DM key; post append | `src/core/contact.py` | **`TestAst1070ContactConversationContext`** |

**Broken / obsolete:** list-return asserts from first Tests Ready pass — revised to Stage 3 dict envelope + `source` + empty-channel raise (Radia FIX-NOW / Hedy `[qa-handoff]`).

**Integration:** no existing scenario asserts Slack conversation cache — no revision.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1070ContactContextConfig \
  tests/component/external/test_slack.py::TestAst1070FetchConversationHistory \
  tests/component/core/test_contact.py::TestAst1070ContactConversationContext \
  -q
```

### AST-1073 · AST-1046

**Parent:** [AST-1046 — Contact Estelle conversational envelope](https://linear.app/astralcareermatch/issue/AST-1046/contact-estelle-conversational-envelope). **Publish:** `origin/sub/AST-1046/AST-1073-contact-estelle-turn-loop`.

`run_contact_estelle_turn`: listen re-check → Slack context live_content → `do_task(contact_estelle_turn)` → `conversational_turn_from_do_task_result` → optional ACL `skill_calls` → Slack reply (no env prefix since AST-2085) on success/concern only; concern `admin_aside` → warning log (never Slack); Style D when `debug=True`. Hooked from `handle_slack_event` after accept + resolve + inbound append. Config: **`docs/test-bible/utils/config.md`**. Envelope: **`docs/test-bible/core/agent.md`** (AST-1072). Catalog: **`docs/test-bible/core/repo_admin_json.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Turn loop + handle_slack_event attach | `src/core/contact.py` | **`TestAst1073ContactEstelleTurnLoop`** |

**Broken / obsolete:** accept-path Contact tests stub `run_contact_estelle_turn` so ingress/resolve/context stay transport-focused (no live `do_task`). AST-786 catalog **43 → 46** on this tip.

**Integration:** no existing scenario asserts Estelle turn loop — no revision; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1073ContactEstelleTurnConfig \
  tests/component/core/test_contact.py::TestAst1073ContactEstelleTurnLoop \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1072ContactEstelleTurnCatalogRow \
  -q
```


### AST-1094 · AST-1043

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1094-uat-manage-slack-estelle-activity-list`.

Durable @Estelle per–Slack-user activity summary (JSON under `db_dir`): `list_estelle_activity`; record on accepted `handle_slack_event` after resolve (not on listen_off). Data module: **`docs/test-bible/data/contact_estelle_activity.md`**. Config: **`docs/test-bible/utils/config.md`**. API/UI: **`docs/test-bible/ui/api/api_contact.md`**, **`docs/test-bible/frontend/pages.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Data load/record/list | `src/data/contact_estelle_activity.py` | **`TestAst1094EstelleActivityData`** |
| Core list + record on accept | `src/core/contact.py` | **`TestAst1094EstelleActivity`** |

**Broken / obsolete:** none — additive; existing ingress tests stub Estelle turn and still accept.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/test_contact_estelle_activity.py::TestAst1094EstelleActivityData \
  tests/component/core/test_contact.py::TestAst1094EstelleActivity \
  -q
```

### AST-1101 · AST-1043 (UAT)

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1101-uat-channel-at-estelle-no-hear-evidence`.

Durable listen re-read every `slack_listen_enabled()`; Events background `_run_handle_slack_event_background` logs failures; after accept, hear-ack via `format_contact_reply_text` + `contact_post_message` when Estelle turn did not `slack_post.ok`; activity still AST-1094 on accept. Config: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Listen re-read + hear-ack + background log | `src/core/contact.py` | **`TestAst1101ChannelHearEvidence`** |

**Broken / obsolete:** none — additive; ingress stubs with successful Estelle `slack_post` still skip hear-ack.

**Integration:** none — do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_contact.py::TestAst1101ChannelHearEvidence \
  tests/component/core/test_contact.py::TestAst1094EstelleActivity \
  tests/component/core/test_contact.py::TestAst1069ContactSlackIngress \
  -q
```

### AST-1105 · AST-1043 (UAT)

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1105-uat-slack-username-display-activity-profile`.

Resolve persists/returns `slack_username` + `slack_display_name`; match-path backfill via `users.info` + `save_candidate_data`; activity record gets identity.

| Area | Source | Component tests |
| --- | --- | --- |
| Resolve persist/backfill + activity identity | `src/core/contact.py` | revised **`TestAst1068ResolveSlackUser`**; **`TestAst1105SlackUsernameDisplay`** |

**Broken / obsolete:** AST-1068 create contact payload / return shape — revised for username fields; found path stubs `fetch_user_profile`.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_contact.py::TestAst1068ResolveSlackUser \
  tests/component/core/test_contact.py::TestAst1105SlackUsernameDisplay \
  -q
```

### AST-1206 · AST-1203

**Parent:** [AST-1203 — Need to be able to set the "Debug" flag for Slack messages](https://linear.app/astralcareermatch/issue/AST-1203/need-to-be-able-to-set-the-debug-flag-for-slack-messages). **Publish:** `origin/sub/AST-1203/AST-1206-contact-debug-flag-foundation`.

Durable Contact Slack debug get/set: `slack_debug_enabled` / `set_slack_debug_enabled` (re-read every call, separate `contact_slack_debug.json`). Does **not** wire Events/hear (AST-1207) or Manage Slack React (AST-1208). Data: **`docs/test-bible/data/contact_debug.md`**. Config: **`docs/test-bible/utils/config.md`**. Admin API: **`docs/test-bible/ui/api/api_contact.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Default off; durable re-read; set persist; listen file untouched; TypeError | `src/core/contact.py` | **`TestAst1206ContactDebugFlag`** |

**Broken / obsolete:** none — additive twin of listen get/set; listen/Events paths untouched.

**Integration:** no existing scenario asserts Contact debug SoT — no revision; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/test_contact_debug.py::TestAst1206ContactDebugData \
  tests/component/utils/test_config.py::TestAst1206ContactDebugConfig \
  tests/component/core/test_contact.py::TestAst1206ContactDebugFlag \
  tests/component/ui/api/test_api_contact.py::TestAst1206ContactDebugApi \
  -q
```

### AST-1207 · AST-1203

**Parent:** [AST-1203 — Need to be able to set the "Debug" flag for Slack messages](https://linear.app/astralcareermatch/issue/AST-1203/need-to-be-able-to-set-the-debug-flag-for-slack-messages). **Publish:** `origin/sub/AST-1203/AST-1207-slack-events-contact-inbound-durable-debug`.

Events/Socket ingress hydrates `debug` from `slack_debug_enabled()` (caller kwarg ignored); Style D found→recorded depth on Contact Slack path helpers (`load_slack_conversation_context`, `append_slack_conversation_message`, `contact_post_message`, `run_contact_estelle_turn` bookend, `handle_slack_event` accept bookend). Blueprint: **`docs/test-bible/ui/api/api_slack.md`**. Foundation SoT: **`docs/test-bible/core/contact.md`** (AST-1206).

| Area | Source | Component tests |
| --- | --- | --- |
| Durable SoT on handle/receive; debug pass-through to turn | `src/core/contact.py` | **`TestAst1207DurableDebugSot`** |
| Events blueprint SoT wire | `src/ui/api/api_slack.py` | **`TestAst1207SlackEventsDebugSot`** |
| Estelle turn Style D bookend shape | `src/core/contact.py` | revised **`TestAst1073ContactEstelleTurnLoop::test_debug_style_d_index_and_detail`** |

**Broken / obsolete:** AST-1073 turn Style D asserted single `outcome="success"` — revised to found→recorded (`["found","recorded"]`) for AST-1207 bookend. No Style D golden-string expansion (ticket / Radia).

**Integration:** no existing scenario asserts Events durable debug SoT — no revision; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_contact.py::TestAst1207DurableDebugSot \
  tests/component/core/test_contact.py::TestAst1073ContactEstelleTurnLoop::test_debug_style_d_index_and_detail \
  tests/component/ui/api/test_api_slack.py::TestAst1207SlackEventsDebugSot \
  -q
```

### AST-1515 · AST-1414

**Parent:** [AST-1414 — Estelle needs to be able to use our endpoints](https://linear.app/astralcareermatch/issue/AST-1414/estelle-needs-to-be-able-to-use-our-endpoints). **Publish:** `origin/sub/AST-1414/AST-1515-contact-task-config-markup-parse-dispatch`.

Child #1: `CONTACT_TASK_CONFIG` block (six keys pre-registered), markup parse/strip, dynamic dispatch router (`handler_unavailable` until sibling handlers land), same-event follow-up Estelle turn when listed markup present, markup stripped before Slack post. Config: **`docs/test-bible/utils/config.md`**. Prompt contract: **`docs/test-bible/core/repo_admin_json.md`**. Does **not** implement gazer/meteorite/tracker handlers or extend skills ACL.

| Area | Source | Component tests |
| --- | --- | --- |
| Parse/strip/dispatch + turn strip/follow-up/live_content catalog | `src/core/contact.py` | **`TestAst1515ContactTaskMarkup`**, **`TestAst1515ContactEstelleTurnMarkup`** |

**Broken / obsolete:** none at AST-1515 land. **AST-1516/AST-1518 revise:** `handler_unavailable` / turn fixtures retargeted to `create_contact_meteorite` (gazer + reads now resolve; meteorite create still AST-1517). **AST-1517 revise:** all six handlers resolve — `handler_unavailable` / turn fixtures mock `_resolve_contact_task_handler` → `None`. Gazer: **`docs/test-bible/core/gazer.md`** § AST-1516. Reads: **`docs/test-bible/core/tracker.md`** § AST-1518. Create: **`docs/test-bible/core/meteorite.md`** § AST-1517. **AST-2062:** handler_unavailable / turn fixtures retargeted from create_contact_meteorite to gazer_scrape.

**Integration:** no existing scenario asserts contact-task markup dispatch — no revision; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_contact.py::TestAst1515ContactTaskMarkup \
  tests/component/core/test_contact.py::TestAst1515ContactEstelleTurnMarkup \
  -q
```


### AST-1531 · AST-1527

**Parent:** [AST-1527 — Generalize Meteorite Ingress Point](https://linear.app/astralcareermatch/issue/AST-1527/generalize-meteorite-ingress-point). **Publish:** `origin/sub/AST-1527/AST-1531-caller-cutover-mailbox-inbox-contact`.

`contact_land_meteorite` requires `source_kind` ∈ `STAGE_METEORITE_CONFIG["source_ref_prefixes"]` + non-empty `source_id`, builds blob from text/scraps/job_link/employer, then `asyncio.run(stage_meteorite(...))` — no unclassified `land_meteorite`. Mailbox/inbox: **`docs/test-bible/core/meteorite_email.md`**, **`docs/test-bible/core/inbox.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Source gates + stage blob + empty blob | `src/core/contact.py` | **`TestAst1531ContactLandStageCutover`** |

**Broken / obsolete:** none for this cutover. Pre-existing **`TestAst1071ContactSkillRunners`** profile→contact rename failures are outside AST-1531 (already red on AST-1530 tip).

**Integration:** none — do not invent.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_contact.py::TestAst1531ContactLandStageCutover \
  -q
```

---

### AST-1561 · AST-1555

**Parent:** [AST-1555](https://linear.app/astralcareermatch/issue/AST-1555/meteorite-ingress-staging-table-inboxmeteorite-consolidation). **Publish:** `origin/sub/AST-1555/AST-1561-bot-blocked-estelle-recovery-apply-paste`.

`try_meteorite_apply_paste_from_slack` (thread-first, then unprompted `paste` source_kind); `handle_slack_event` short-circuits Estelle turn on successful paste; `run_contact_estelle_turn` `land_calls` uses `apply_paste` when paste-source row exists. Meteorite helpers: **`docs/test-bible/core/meteorite.md`** § AST-1561.

| Area | Source | Component tests |
| --- | --- | --- |
| Slack paste routing | `src/core/contact.py` | **`TestAst1561ContactPasteRouting`** |

**Broken / obsolete:** none — additive; existing Estelle turn stubs unchanged for non-paste paths.

**Integration:** none revised.

Primary numbered manifest: **`docs/test-bible/core/meteorite.md`** § AST-1561.

---

### AST-1585 · AST-1571

**Parent:** [AST-1571 — Implement patt.artifact.read-operative](https://linear.app/astralcareermatch/issue/AST-1571/implement-pattartifactread-operative). **Publish:** `origin/sub/AST-1571/AST-1585-ui-contact-pilot-base-resume-operative-resolve`.

Contact `resolve_pinned_base_resume` (ownership + `get_operative_base_resume`); `run_contact_task_dispatch` UUID short-circuit / `pin_required` for `artifacts.base_resume`; Estelle raft strips blob `base_resume` and injects pin body when `base_resume_artifact_id` supplied. API + JAR: **`docs/test-bible/ui/api/api_candidate.md`**, **`docs/test-bible/frontend/lib.md`**, **`docs/test-bible/frontend/components.md`** § AST-1585. Helper SoT: **`docs/test-bible/core/candidate.md`** § AST-1584.

| Area | Source | Component tests |
| --- | --- | --- |
| Resolve / dispatch / Estelle raft | `src/core/contact.py` | **`TestAst1585ContactPinnedBaseResume`** |

**Broken / obsolete this pass:** none — additive short-circuits; other `get_candidate_data` params still hit tracker.

**Integration:** none revised.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_contact.py::TestAst1585ContactPinnedBaseResume \
  tests/component/ui/api/test_api_candidate.py::TestAst1585OperativeBaseResumeApi \
  -q
```


---

### AST-1668 · AST-1636

**Parent:** [AST-1636 — Bind new Slack contacts to existing candidates by metadata before creating a prospect](https://linear.app/astralcareermatch/issue/AST-1636). **Publish:** `origin/sub/AST-1636/AST-1668-contact-unbound-known-unknown-resolve`.

`list_unbound_slack_users` (posters minus `get_candidate_id_for_query` hits); `resolve_slack_user` lookup-only (no PROSPECT mint); `handle_slack_event` known/unknown recognition posts + unknown skips Estelle/paste/hear-ack. Config keys: **`docs/test-bible/utils/config.md`** § AST-1668. Admin GET: **`docs/test-bible/ui/api/api_contact.md`** § AST-1668. External posters: **`docs/test-bible/external/slack.md`** § AST-1667.

| Area | Source | Component tests |
| --- | --- | --- |
| Unbound filter + recognition / unknown skip | `src/core/contact.py` | **`TestAst1668UnboundAndRecognition`** |
| Revised resolve lookup-only | `src/core/contact.py` | **`TestAst1068ResolveSlackUser`** |
| Revised hear-ack vs recognition | `src/core/contact.py` | **`TestAst1101ChannelHearEvidence`** |

**Broken / obsolete this pass:** AST-1068 create-on-miss tests; AST-1101 hear-ack `post.assert_called_once` / `assert_not_called` (recognition now posts first).

**Integration:** no existing scenario exercises Contact unbound / recognition — no revision; do not invent.

## QA test manifest

1. Core unbound + recognition: `tests/component/core/test_contact.py::TestAst1668UnboundAndRecognition`
2. Revised resolve: `tests/component/core/test_contact.py::TestAst1068ResolveSlackUser`
3. Revised hear-ack: `tests/component/core/test_contact.py::TestAst1101ChannelHearEvidence`
4. Config recognition keys: `tests/component/utils/test_config.py::TestAst1668RecognitionReplyConfig`
5. Admin GET unbound: `tests/component/ui/api/test_api_contact.py::TestAst1668UnboundSlackUsersApi`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_contact.py::TestAst1668UnboundAndRecognition \
  tests/component/core/test_contact.py::TestAst1068ResolveSlackUser \
  tests/component/core/test_contact.py::TestAst1101ChannelHearEvidence \
  tests/component/utils/test_config.py::TestAst1668RecognitionReplyConfig \
  tests/component/ui/api/test_api_contact.py::TestAst1668UnboundSlackUsersApi \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):**
- `docs/test-bible/core/contact.md` — *(filled after publish)*
- `docs/test-bible/utils/config.md` — *(filled after publish)*
- `docs/test-bible/ui/api/api_contact.md` — *(filled after publish)*

---

### AST-1738 · AST-1636 (bug)

**Parent:** [AST-1636](https://linear.app/astralcareermatch/issue/AST-1636). **Publish:** `origin/sub/AST-1636/AST-1738-manage-candidates-slack-dropdown-empty`.

UAT: Manage Candidates Slack dropdown empty because `list_unbound_slack_users` used poster pool. Fix: members via `list_workspace_members`, not `list_workspace_posters`. Board REVISE: revise AST-1668 unbound stub; land empty-poster≠empty-unbound repro.

| Area | Source | Component tests |
| --- | --- | --- |
| [bug-repro] unbound from members when posters empty | `src/core/contact.py` | **`TestAst1738UnboundMembersNotPosters`** |
| Revised unbound pool stub (members + posters fallback) | same | **`TestAst1668UnboundAndRecognition::test_list_unbound_omits_bound_ids`** |

**Broken / obsolete this pass:** AST-1668 unbound stub assumed `list_workspace_posters` — revised.

## QA test manifest

1. **[bug-repro]** `tests/component/core/test_contact.py::TestAst1738UnboundMembersNotPosters`
2. Revised filter: `tests/component/core/test_contact.py::TestAst1668UnboundAndRecognition::test_list_unbound_omits_bound_ids`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_contact.py::TestAst1738UnboundMembersNotPosters \
  tests/component/core/test_contact.py::TestAst1668UnboundAndRecognition::test_list_unbound_omits_bound_ids \
  -q
```

**Pass criterion (test-fix):** repro flips red→green after make-fix; revised filter stays green.

**Bible shasum (publish tip):**
- `docs/test-bible/core/contact.md` — *(filled after publish)*

---

### AST-1788 · AST-1786

**Parent:** [AST-1786 — Manage Candidates Snapshot Slack Channel + candidate mapping](https://linear.app/astralcareermatch/issue/AST-1786/manage-candidates-snapshot-slack-channel-candidate-mapping). **Publish:** `origin/sub/AST-1786/AST-1788-contact-admin-channel-apis-shapes`.

Contact orchestration for admin channel picker / membership warn / snapshot: `list_admin_slack_channels`, `check_admin_slack_channel_membership` (unbound short-circuit), `get_admin_slack_channel_snapshot`. Calls AST-1787 external helpers only. API: **`docs/test-bible/ui/api/api_contact.md`**. Shapes: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Channel list / membership / snapshot orchestration | `src/core/contact.py` | **`TestAst1788AdminSlackChannelOrchestration`** |

**Broken / obsolete this pass:** none — additive helpers.

**Integration:** no existing scenario exercises these Contact admin helpers — no revision; do not invent.

## QA test manifest

1. Orchestration: `tests/component/core/test_contact.py::TestAst1788AdminSlackChannelOrchestration`
2. Admin APIs: `tests/component/ui/api/test_api_contact.py::TestAst1788AdminSlackChannelApis`
3. Shapes: `tests/component/utils/test_config.py::TestAst1788ManageListAndProfileSlackChannelShapes`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_contact.py::TestAst1788AdminSlackChannelOrchestration \
  tests/component/ui/api/test_api_contact.py::TestAst1788AdminSlackChannelApis \
  tests/component/utils/test_config.py::TestAst1788ManageListAndProfileSlackChannelShapes \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):**
- `docs/test-bible/core/contact.md` — *(filled after publish)*
- `docs/test-bible/ui/api/api_contact.md` — *(filled after publish)*
- `docs/test-bible/utils/config.md` — *(filled after publish)*

### AST-1879 · AST-1851 (Estelle turn passes the resolved candidate ctx)

**Primary manifest:** [`agent.md`](agent.md) § QA test manifest (AST-1879). `run_contact_estelle_turn`: when the candidate id is missing, blank or unresolved, it returns `error="no_candidate"` before loading the Slack context or calling `do_task`, with a warning ("Estelle is not replying"). A resolved candidate goes to `do_task` as `ctx={astral_candidate_id, candidate_data, candidate_api_keys}` (a copied map; empty when the row has none) instead of `candidate_data=`.

| Area | Source | Component tests |
| --- | --- | --- |
| AC 10 — None / "" / blank id and unresolved id → `no_candidate`, zero `do_task`, no post | `src/core/contact.py` | `TestAst1879EstelleTurnCandidateCtx::test_no_candidate_id_fails_before_do_task` (3 params), `…::test_unresolved_candidate_id_fails_before_do_task` |
| Resolved candidate → `ctx` with id + key map, no `candidate_data=` kwarg | same | `…::test_resolved_candidate_passes_ctx_with_key_map`, `…::test_resolved_candidate_without_keys_sends_empty_map` |
| Revised — turn stubs resolve a candidate row (`_turn_candidate_row`) | `test_contact.py` | `TestAst1073…` (`_patch_turn_deps`; success/failure turns carry `astral_candidate_id`; `test_skill_calls_acl_and_no_candidate` → `test_skill_calls_run_for_resolved_candidate`, and the no-candidate half now lives in `TestAst1879…`), `TestAst1515ContactEstelleTurnMarkup`, `TestAst1561ContactPasteRouting`, `TestAst1585…::test_estelle_turn_strips_blob_and_injects_pin` (reads `ctx["candidate_data"]`) |

The turn's model/key route (contact agent row, kimi key) is covered in [`agent.md`](agent.md) `TestAst1879EstelleTurnRoute`.

**Integration:** none.

### AST-2035 · AST-2032

**Parent:** [AST-2032 — Let Estelle post a meteorite from Slack](https://linear.app/astralcareermatch/issue/AST-2032). **Publish:** `origin/sub/AST-2032/AST-2035-contact-add-job-intercept`.

`parse_contact_command` matches a registered `/<id>` only as the first token after leading `<@U…>` mentions and unwraps Slack `<url|label>` / `<url>`. In `_handle_slack_event_body`, a bound sender's command skips paste recovery and the normal turn and runs `_run_contact_command`: empty payload → usage post; `code` → handler (`insert_slack_meteorite`, sibling **AST-2034** — `core/meteorite.md`) then a fixed ack naming the id only on success (a soft-fail posts nothing, so the AST-1101 hear-ack fires); `agent` → one `run_contact_estelle_turn` with the result JSON as `extra_context` (rendered under `## Command result (this inbound event)` in live content). `_emit_listen_info` prefixes `action:` with `<id>:<mode>,meteorite:<id>`. Registry + import-time asserts: [`../utils/config.md`](../utils/config.md) § AST-2035.

Known senders always get the AST-1668 recognition post first, so AC3's "one ack" is asserted as exactly one post containing the meteorite id plus no hear-ack. *(AST-2072 removed that recognition post; AC3 now also asserts exactly one post — see § AST-2072.)*

| Area | Source | Component tests |
| --- | --- | --- |
| Parse hits / misses (bare, label link, bare `<url>`, `\|label` mention, no mention, multi-line, mid-sentence, unregistered, non-str) | `src/core/contact.py` | **`TestAst2035ContactCommandIntercept::test_parse_contact_command`** (9 params) |
| Shipped registry: `add-job` is `code`, handler resolves to `insert_slack_meteorite` | `src/utils/config.py` | **`…::test_registry_ships_add_job_code_mode`** |
| AC1 link markup / AC2 multi-line DM — real insert against sqlite | `src/core/contact.py` + `src/core/meteorite.py` | **`…::test_ac1_link_markup_lands_raw_at_new`**, **`…::test_ac2_multiline_text_in_dm_lands_one_row`** |
| AC3 code mode: zero `do_task`, one id post, no hear-ack | same | **`…::test_ac3_code_mode_no_llm_one_ack_no_hear_ack`** |
| AC4 agent mode: one turn, id in `extra_context`; reply is the turn's; `extra_context` reaches live content | same | **`…::test_ac4_agent_mode_one_turn_with_id`**, **`…::test_ac4_extra_context_reaches_turn_live_content`** |
| AC5 BOT_BLOCKED row untouched, paste recovery not called | same | **`…::test_ac5_bot_blocked_row_untouched_paste_skipped`** |
| AC6 unbound sender / bare command → no row | same | **`…::test_ac6_unbound_sender_no_insert`**, **`…::test_ac6_bare_command_posts_usage_no_insert`** |
| AC7 mid-sentence → normal turn, no insert | same | **`…::test_ac7_mid_sentence_takes_normal_turn`** |
| Code-mode handler soft-fail → no ack, hear-ack fires | same | **`…::test_code_mode_handler_miss_no_ack_hear_ack_fires`** |
| AC8 no quoted command literal in `src/core/` | `src/core/**` | **`…::test_ac8_no_command_literals_in_core`** |
| AC9 INFO (debug off): listen line with id:mode + meteorite id; meteorite `NEW` entity line | same | **`…::test_ac9_info_lines_with_debug_off`** |

**Broken / obsolete this pass:** none. `test_contact.py` + `test_config.py` show the identical 37 failures (12 in `test_contact.py`) with the pre-build (`ftr`) `contact.py`/`config.py` and with this build — all pre-existing. Three of them sit in manifest regression classes and are `--deselect`ed below (not this ticket's to fix).

**Integration:** none — no existing scenario covers Contact Slack events; do not invent.

## QA test manifest

1. Command intercept (AC1–AC9 + parse + soft-fail): `tests/component/core/test_contact.py::TestAst2035ContactCommandIntercept`
2. Intercept-adjacent regression (paste recovery, recognition, hear-ack, turn): `tests/component/core/test_contact.py::TestAst1561ContactPasteRouting`, `TestAst1668UnboundAndRecognition`, `TestAst1101ChannelHearEvidence`, `TestAst1073ContactEstelleTurnLoop`, `TestAst1879EstelleTurnCandidateCtx`
3. Sibling insert entry (handler target): `tests/component/core/test_meteorite.py::TestAst2034InsertSlackMeteorite`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_contact.py::TestAst2035ContactCommandIntercept \
  tests/component/core/test_contact.py::TestAst1561ContactPasteRouting \
  tests/component/core/test_contact.py::TestAst1668UnboundAndRecognition \
  tests/component/core/test_contact.py::TestAst1101ChannelHearEvidence \
  tests/component/core/test_contact.py::TestAst1073ContactEstelleTurnLoop \
  tests/component/core/test_contact.py::TestAst1879EstelleTurnCandidateCtx \
  tests/component/core/test_meteorite.py::TestAst2034InsertSlackMeteorite \
  --deselect tests/component/core/test_contact.py::TestAst1101ChannelHearEvidence::test_background_wrapper_logs_exception \
  --deselect tests/component/core/test_contact.py::TestAst1073ContactEstelleTurnLoop::test_concern_posts_and_logs_aside \
  --deselect tests/component/core/test_contact.py::TestAst1073ContactEstelleTurnLoop::test_debug_style_d_index_and_detail \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible path shasums (record after publish):**
- `docs/test-bible/core/contact.md`
- `docs/test-bible/utils/config.md`

### AST-2062 · AST-2055 (Estelle pinhole — tests for AST-2061)

**Parent:** [AST-2055](https://linear.app/astralcareermatch/issue/AST-2055) (fix child [AST-2061](https://linear.app/astralcareermatch/issue/AST-2061)). **Publish:** `origin/sub/AST-2055/AST-2062-estelle-pinhole-tests`.

AST-2061 closed Estelle's write pinhole: no `skill_calls` / `save_candidate_*` path, Contact meteorite writes go through `sanitize_contact_text` (`nh3`), Slack `<url|label>` is unwrapped before sanitize (`_unwrap_slack_links`), and `app_mention` is honored only when the channel type (event `channel_type`, else `fetch_channel_type`) is in `CONTACT_CONFIG["allowed_channel_types"]` (`im`, `group`); anything else — including a lookup error — returns `channel_not_private` before resolve. Sanitize helper + no-job-write: [`meteorite.md`](meteorite.md) § AST-2062. Config/pinhole assert: [`../utils/config.md`](../utils/config.md) § AST-2062. Lookup: [`../external/slack.md`](../external/slack.md) § AST-2062.

| Area | Source | Component tests |
| --- | --- | --- |
| Skills registry empty; any key → unknown, no candidate write | `src/core/contact.py` | **`TestAst2061ContactSkillsRetired`** (2) |
| **[bug-repro]** candidate write: `skill_calls` never reach `run_contact_skill` / `save_candidate_data`; no ACL header in live content | same | **`TestAst1073ContactEstelleTurnLoop::test_ast2061_skill_calls_never_write_candidate`** |
| Channel gate: **[bug-repro]** public refused (no resolve/command/paste/turn/post); mpim refused; lookup error fails closed; group passes; event `channel_type` skips lookup; DM `message` not gated | same | **`TestAst2061PrivateChannelGate`** (6) |
| Sanitize entry: **[bug-repro]** land blob unwrap+sanitize; markup-only blob → `blob is required`; **[bug-repro]** Slack paste unwrapped before `apply_paste` | same | **`TestAst2061ContactSanitizeEntry`** (3) |
| `app_mention` default channel type | `tests/component/core/test_contact.py` | module autouse **`_ast2061_private_channel_default`** (`fetch_channel_type` → `"group"`, `raising=False` for pre-fix repro runs) |

**Broken / obsolete:** `TestAst1071ContactSkillRunners` (retired); `TestAst1073ContactEstelleTurnLoop::test_skill_calls_run_for_resolved_candidate` (replaced by the repro above); AST-1515 sample key moved to `gazer_scrape` (`test_dispatch_handler_unavailable_for_listed_key`, `test_dispatch_debug_style_d`, `test_strips_markup_before_slack_post`, `test_follow_up_turn_includes_task_results_in_live_content`); 18 `C…` `app_mention` cases fixed by the autouse default. Gate tests stub `record_estelle_activity` — do not commit `data/contact_estelle_activity.json` (older accept-path tests still dirty it).

**Repro gate:** every **[bug-repro]** node fails on its assertion against pre-fix `6b00d8c5f` (`src/` = `origin/dev` `2fd5c63e7`) and passes on the AST-2061 tip `54eb3f275`.

**Integration:** none — no scenario covers Contact Slack events or meteorite sanitize; do not invent.

## QA test manifest

1. Pinhole repros + retirement (contact): `TestAst2061ContactSkillsRetired`, `TestAst2061PrivateChannelGate`, `TestAst2061ContactSanitizeEntry`, `TestAst1073ContactEstelleTurnLoop::test_ast2061_skill_calls_never_write_candidate`
2. Revised regression (contact): `TestAst1515ContactTaskMarkup`, `TestAst1515ContactEstelleTurnMarkup`, `TestAst2035ContactCommandIntercept`, `TestAst1668UnboundAndRecognition`
3. Meteorite / config / API / Slack lines: [`meteorite.md`](meteorite.md), [`../utils/config.md`](../utils/config.md), [`../ui/api/api_contact.md`](../ui/api/api_contact.md) (whole `test_api_contact.py`), [`../external/slack.md`](../external/slack.md) — all in the command below.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_contact.py::TestAst2061ContactSkillsRetired \
  tests/component/core/test_contact.py::TestAst2061PrivateChannelGate \
  tests/component/core/test_contact.py::TestAst2061ContactSanitizeEntry \
  tests/component/core/test_contact.py::TestAst1073ContactEstelleTurnLoop::test_ast2061_skill_calls_never_write_candidate \
  tests/component/core/test_contact.py::TestAst1515ContactTaskMarkup \
  tests/component/core/test_contact.py::TestAst1515ContactEstelleTurnMarkup \
  tests/component/core/test_contact.py::TestAst2035ContactCommandIntercept \
  tests/component/core/test_contact.py::TestAst1668UnboundAndRecognition \
  tests/component/core/test_meteorite.py::TestAst2061NoContactJobWrite \
  tests/component/core/test_meteorite.py::TestAst2061ContactSanitize \
  tests/component/core/test_meteorite.py::TestAst2034InsertSlackMeteorite \
  tests/component/core/test_meteorite.py::TestAst1561ApplyPaste \
  tests/component/utils/test_config.py::TestAst2061ContactSkillsEmpty \
  tests/component/utils/test_config.py::TestAst2061ContactPinholeConfig \
  tests/component/utils/test_config.py::TestAst1515ContactTaskConfig \
  tests/component/utils/test_config.py::TestAst1105ProfileSlackFields \
  tests/component/ui/api/test_api_contact.py \
  tests/component/external/test_slack.py::TestAst2061FetchChannelType \
  --deselect tests/component/core/test_contact.py::TestAst1515ContactTaskMarkup::test_dispatch_debug_style_d \
  --deselect tests/component/ui/api/test_api_contact.py::TestAst1071ContactSkillsApi::test_run_upstream_502 \
  --deselect tests/component/ui/api/test_api_contact.py::TestAst1067ContactListenApi::test_put_upstream_502 \
  --deselect tests/component/ui/api/test_api_contact.py::TestAst1094EstelleActivityApi::test_get_activity_upstream_502 \
  --deselect tests/component/ui/api/test_api_contact.py::TestAst1206ContactDebugApi::test_put_upstream_502 \
  -q
```

The five `--deselect`s fail identically on pre-fix `6b00d8c5f` (pre-existing; not this ticket's to fix).

**Pass criterion:** pytest green on the AST-2061 tip. Across the six touched files, the 33 AST-2061 reds are gone; remaining failures equal the 82 pre-existing on `6b00d8c5f` minus the 7 retired with `TestAst1071ContactSkillRunners` / `TestAst1071ContactSkillsConfig` / `TestAst1517CreateContactMeteorite` (75). Not zero-arg harness / branch-lock gate.

### AST-2072 · AST-2050 (natural Estelle replies + thread_response placement)

**Parent:** [AST-2050](https://linear.app/astralcareermatch/issue/AST-2050) — Contact Estelle behavior. **Publish:** `origin/sub/AST-2050/AST-2072-estelle-thread-response`.

A bound sender no longer gets the canned AST-1668 "I know who that is" post — Estelle's own reply (turn, `/add-job` usage/ack, paste ack, hear-ack) is the only post. `_contact_reply_placement(thread_ts, message_ts)` resolves every reply's `(thread_ts, reply_broadcast)` from `CONTACT_CONFIG["thread_response"]`: `threads_only` (default) threads only an in-thread inbound, `always_no_share` threads under the user's thread or message, `always_with_share` adds `reply_broadcast`. `contact_post_message` passes `reply_broadcast` through and caches on the thread actually posted to (top-level → `(channel, "")`). The `/add-job` handler anchor stays `thread_ts or message_ts` regardless of placement. Config: [`../utils/config.md`](../utils/config.md) § AST-2072. Slack body: [`../external/slack.md`](../external/slack.md) § AST-2072.

| Area | Source | Component tests |
| --- | --- | --- |
| Helper: 3 modes × top-level / in-thread (AC 4–7) | `src/core/contact.py` | **`TestAst2072ThreadResponsePlacement::test_placement_helper`** (6) |
| `contact_post_message` broadcast pass-through + top-level cache key | same | **`…::test_contact_post_message_broadcast_and_top_level_cache_key`** |
| AC 3 bound turn = one post, no recognition | same | **`…::test_ac3_bound_turn_is_the_only_post`** |
| AC 4–7 end to end: real turn reply placement through `handle_slack_event` | same | **`…::test_ac4_to_7_turn_reply_placement`** (6) |
| AC 8 every reply site (turn, usage, code ack, paste ack, hear-ack, unknown) × `threads_only` / `always_with_share`, with an outcome guard so each case really hits its site | same | **`…::test_ac8_every_reply_site_obeys_setting`** (12) |
| AC 10 handler anchor = message ts while the ack posts top-level | same | **`…::test_ac10_handler_anchor_is_message_ts_under_threads_only`** |
| AC 12 one `contact listen` INFO line, debug off | same | **`…::test_ac12_one_listen_info_line_debug_off`** |
| AC 13 / AC 14 exact unknown and fallback text | same | **`…::test_ac13_unbound_sender_exact_text_no_turn`**, **`…::test_ac14_failed_turn_posts_exact_fallback`** |
| AC 1 / AC 14 retired strings absent from `src/` (whole-word `known_recognition_reply_text`, so `unknown_…` does not match) | `src/**` | **`…::test_ac1_ac14_retired_strings_absent_from_src`** |
| AC 9 placement-logic grep: hits only in the helper, the `_run_contact_command` anchor, and the paste-recovery lookup anchor (plan Stage 2 step 7) | `src/core/contact.py` | **`…::test_ac9_placement_logic_only_in_helper_and_anchors`** |

**Broken / obsolete this pass (revised):**
- `TestAst1073ContactEstelleTurnLoop::test_success_posts_prefixed_reply` — top-level reply now `thread_ts=None`, `reply_broadcast=False`.
- `TestAst1101ChannelHearEvidence::test_hear_ack_when_turn_does_not_post` — one post (hear-ack), top-level; no `recognition_post`.
- `TestAst1101ChannelHearEvidence::test_no_hear_ack_when_turn_posted` — no post at all (turn stubbed); no `recognition_post`.
- `TestAst1668UnboundAndRecognition::test_known_recognition_then_estelle` → renamed **`test_bound_sender_no_recognition_then_estelle`**.
- `TestAst2035ContactCommandIntercept::test_ac3_code_mode_no_llm_one_ack_no_hear_ack` — tightened to exactly one post (the § AST-2035 "recognition post first" note no longer holds).

**Integration:** none — no scenario covers Contact Slack events; do not invent.

## QA test manifest

1. New: `tests/component/core/test_contact.py::TestAst2072ThreadResponsePlacement`, `tests/component/utils/test_config.py::TestAst2072ThreadResponseConfig`, `tests/component/external/test_slack.py::TestAst2072PostMessageReplyBroadcast`
2. Revised regression (contact): `TestAst1073ContactEstelleTurnLoop`, `TestAst1101ChannelHearEvidence`, `TestAst1668UnboundAndRecognition`, `TestAst2035ContactCommandIntercept`
3. Revised regression (config / slack): `TestAst1668RecognitionReplyConfig`, `TestAst1101HearAckConfig`, `TestAst1069ExternalSlack`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_contact.py::TestAst2072ThreadResponsePlacement \
  tests/component/core/test_contact.py::TestAst1073ContactEstelleTurnLoop \
  tests/component/core/test_contact.py::TestAst1101ChannelHearEvidence \
  tests/component/core/test_contact.py::TestAst1668UnboundAndRecognition \
  tests/component/core/test_contact.py::TestAst2035ContactCommandIntercept \
  tests/component/utils/test_config.py::TestAst2072ThreadResponseConfig \
  tests/component/utils/test_config.py::TestAst1668RecognitionReplyConfig \
  tests/component/utils/test_config.py::TestAst1101HearAckConfig \
  tests/component/external/test_slack.py::TestAst2072PostMessageReplyBroadcast \
  tests/component/external/test_slack.py::TestAst1069ExternalSlack \
  --deselect tests/component/core/test_contact.py::TestAst1073ContactEstelleTurnLoop::test_concern_posts_and_logs_aside \
  --deselect tests/component/core/test_contact.py::TestAst1073ContactEstelleTurnLoop::test_debug_style_d_index_and_detail \
  --deselect tests/component/core/test_contact.py::TestAst1101ChannelHearEvidence::test_background_wrapper_logs_exception \
  -q
```

The three `--deselect`s fail identically on `origin/tests` with pre-AST-2072 product (same as the § AST-2035 deselects). Not this ticket's to fix. Needs `nh3` in the venv (AST-2061 product on dev) — `pip install -r requirements.txt`.

**Pass criterion:** pytest green on the manifest (78 passed) — not zero-arg harness / branch-lock gate. Across `test_contact.py` + `test_config.py` + `test_slack.py`, the remaining 33 failures equal the pre-existing set on `origin/tests` @ `39a11978c` (dev incl. AST-2055); AST-2072 adds none.
