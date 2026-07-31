# contact_listen

**Test module:** `tests/component/data/test_contact_listen.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/data/contact_listen.py` | `tests/component/data/test_contact_listen.py` | no |

---

### AST-1067 · AST-1043

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1067-manage-slack-admin-listen-switch`.

Durable JSON listen flag under `ASTRAL_CONFIG["db_dir"]` / `CONTACT_CONFIG["listen_state_filename"]`. Silent data layer (no logging). Core hydrate/set: **`docs/test-bible/core/contact.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| load missing/invalid; save round-trip; TypeError | `src/data/contact_listen.py` | **`TestAst1067ContactListenData`** |

**Broken / obsolete:** none — new module.

**Integration:** no existing scenario — no revision.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/test_contact_listen.py::TestAst1067ContactListenData \
  -q
```
