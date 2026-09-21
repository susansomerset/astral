# slack (external)

**Test module:** `tests/component/external/test_slack.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/external/slack.py` | `tests/component/external/test_slack.py` | no |

---

### AST-1069 · AST-1043

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1069-slack-events-api-webhook-ingress`.

Signature verify (HMAC v0 + skew), URL challenge parse, `chat.postMessage` behind `require_controlled_external_io`. Socket Mode helper is local-script only (not component-tested here). Contact HTTP: **`docs/test-bible/core/contact.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Verify / challenge / gated post_message | `src/external/slack.py` | **`TestAst1069ExternalSlack`** |

**Broken / obsolete:** none — new external module.

**Integration:** no existing scenario — no revision.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_slack.py::TestAst1069ExternalSlack \
  -q
```

---

### AST-1070 · AST-1043

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1070-slack-sourced-conversation-context`.

`fetch_conversation_history`: `conversations.history` vs `conversations.replies`, gated by `require_controlled_external_io`, raises on `ok:false`. Contact cache consumers: **`docs/test-bible/core/contact.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| History / replies / gate / ok:false | `src/external/slack.py` | **`TestAst1070FetchConversationHistory`** |

**Broken / obsolete:** none — additive Web API helper.

**Integration:** no existing scenario — no revision.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_slack.py::TestAst1070FetchConversationHistory \
  -q
```

### AST-1105 · AST-1043 (UAT)

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1105-uat-slack-username-display-activity-profile`.

`fetch_user_profile` returns Slack `user.name` as `username` (empty when omitted). Core/Profile/UI: **`docs/test-bible/core/contact.md`**, **`docs/test-bible/utils/config.md`**, **`docs/test-bible/frontend/pages.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| username on users.info parse | `src/external/slack.py` | revised **`TestAst1068FetchUserProfile`**; **`TestAst1105FetchUserProfileUsername`** |

**Broken / obsolete:** AST-1068 assert omitted `username` — revised.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_slack.py::TestAst1068FetchUserProfile \
  tests/component/external/test_slack.py::TestAst1105FetchUserProfileUsername \
  -q
```

---

### AST-1667 · AST-1636

**Parent:** [AST-1636 — Bind new Slack contacts to existing candidates by metadata before creating a prospect](https://linear.app/astralcareermatch/issue/AST-1636). **Publish:** `origin/sub/AST-1636/AST-1667-workspace-poster-pool-external`.

`list_workspace_posters`: workspace poster pool from `conversations.list` + history/replies message authors, enriched via `users.list` (bots/deleted dropped); gated by `require_controlled_external_io`; soft-skip per-channel history/replies errors; hard `ok:false` raises. Does **not** use `conversations.members` or treat `users.list` alone as "has posted". Sibling Contact/UI: later children under AST-1636.

| Area | Source | Component tests |
| --- | --- | --- |
| Poster pool / gate / soft-skip / bots+deleted / hard fail | `src/external/slack.py` | **`TestAst1667WorkspacePosterPool`** |

**Broken / obsolete this pass:** none — additive helper; existing AST-1069/1070/1105 suites unchanged.

**Integration:** no existing scenario exercises Slack poster pool — no revision; do not invent.

## QA test manifest

1. Workspace poster pool (new): `tests/component/external/test_slack.py::TestAst1667WorkspacePosterPool`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_slack.py::TestAst1667WorkspacePosterPool \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):**
- `docs/test-bible/external/slack.md` — *(filled after publish)*

