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

`resolve_slack_user`: lookup via `get_candidate_id_for_query`; create PROSPECT only when `estelle_in_play=True`; `handle_slack_event` accept wires resolve. Candidate: **`docs/test-bible/core/candidate.md`**. External: **`docs/test-bible/external/slack.md`**. Config: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Resolve hit/miss/create; Events accept wire | `src/core/contact.py` | **`TestAst1068ResolveSlackUser`** |

**Broken / obsolete:** **`TestAst1069ContactSlackIngress`** accept-path — revised to stub `resolve_slack_user`.

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
