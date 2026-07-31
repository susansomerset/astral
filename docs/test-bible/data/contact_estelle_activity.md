# contact_estelle_activity

**Test module:** `tests/component/data/test_contact_estelle_activity.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/data/contact_estelle_activity.py` | `tests/component/data/test_contact_estelle_activity.py` | no |

---

### AST-1094 · AST-1043

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1094-uat-manage-slack-estelle-activity-list`.

Durable JSON @Estelle per–Slack-user activity under `ASTRAL_CONFIG["db_dir"]` / `CONTACT_CONFIG["activity_state_filename"]`. Silent data layer. Core list/record: **`docs/test-bible/core/contact.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| load missing/invalid; record upsert; list rows | `src/data/contact_estelle_activity.py` | **`TestAst1094EstelleActivityData`** |

**Broken / obsolete:** none — new module.

**Integration:** no existing scenario — no revision.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/test_contact_estelle_activity.py::TestAst1094EstelleActivityData \
  -q
```

### AST-1105 · AST-1043 (UAT)

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1105-uat-slack-username-display-activity-profile`.

Optional `slack_username` / `slack_display_name` on activity rows; preserve prior when later record passes `None`.

| Area | Source | Component tests |
| --- | --- | --- |
| Identity persist + preserve | `src/data/contact_estelle_activity.py` | **`TestAst1105ActivityIdentity`** |

**Broken / obsolete:** none — additive optional fields.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/test_contact_estelle_activity.py::TestAst1105ActivityIdentity \
  -q
```

