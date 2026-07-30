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
