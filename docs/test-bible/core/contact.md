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
| Listen default / empty skills copy / env names / prefix / no TASK_CONFIG collision | `src/core/contact.py` | **`TestAst1066ContactScaffold`** |

**Broken / obsolete:** none — new module.

**Integration:** no existing scenario asserts Contact / CONTACT_CONFIG — no revision; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1066ContactConfig \
  tests/component/core/test_contact.py::TestAst1066ContactScaffold \
  -q
```
