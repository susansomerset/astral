# Contact

**Test module:** `tests/component/core/test_contact.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/contact.py` | `tests/component/core/test_contact.py` | no |

---

### AST-1066 · AST-1043

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1066-contact-core-module-and-contact-config`.

Contact scaffold: `slack_listen_enabled`, `contact_skills` / `contact_skill_keys`, `slack_env_names`, `non_production_reply_prefix` — reads `CONTACT_CONFIG` only; no Slack HTTP / DB / skill runners. Config block: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Listen default / skills shallow copy / env names / prefix / no TASK_CONFIG collision | `src/core/contact.py` | **`TestAst1066ContactScaffold`** |

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
| Meta / allowlisted write / reject path·skill·missing / Style D on+off | `src/core/contact.py` | **`TestAst1071ContactSkillRunners`** |

**Broken / obsolete:** AST-1066 empty-skills asserts — revised in **`TestAst1066ContactScaffold`** / **`TestAst1066ContactConfig`**.

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

`resolve_slack_user`: lookup via `get_candidate_id_for_query`; create PROSPECT only when `estelle_in_play=True` via `initiate_prospect_candidate(..., first=, last=)` (names from `users.info`; display_name fills `first` when empty); `handle_slack_event` accept wires resolve. Candidate: **`docs/test-bible/core/candidate.md`**. External: **`docs/test-bible/external/slack.md`**. Config: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Resolve hit/miss/create; Events accept wire | `src/core/contact.py` | **`TestAst1068ResolveSlackUser`** |

**Broken / obsolete:** **`TestAst1069ContactSlackIngress`** accept-path — revised to stub `resolve_slack_user`. Create asserts that expected `candidate_data.profile` — revised for AST-1014 `first=`/`last=` kwargs.

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

`run_contact_estelle_turn`: listen re-check → Slack context live_content → `do_task(contact_estelle_turn)` → `conversational_turn_from_do_task_result` → optional ACL `skill_calls` → Slack reply (non-prod prefix) on success/concern only; concern `admin_aside` → warning log (never Slack); Style D when `debug=True`. Hooked from `handle_slack_event` after accept + resolve + inbound append. Config: **`docs/test-bible/utils/config.md`**. Envelope: **`docs/test-bible/core/agent.md`** (AST-1072). Catalog: **`docs/test-bible/core/repo_admin_json.md`**.

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

