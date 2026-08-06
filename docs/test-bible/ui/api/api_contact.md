# api_contact

**Test module:** `tests/component/ui/api/test_api_contact.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/ui/api/api_contact.py` | `tests/component/ui/api/test_api_contact.py` | no |

---

### AST-1071 · AST-1043

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1071-contact-config-acl-entity-save-skills`.

Admin Contact skills: `GET /api/admin/contact/skills` + `POST /api/admin/contact/skills/<skill_key>` (`@require_admin`). Thin wrappers over `contact_skills` / `run_contact_skill`. Core runners: **`docs/test-bible/core/contact.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| List/run + 400/502 + auth 401/403 | `src/ui/api/api_contact.py` | **`TestAst1071ContactSkillsApi`** |

**Broken / obsolete:** none — new blueprint.

**Integration:** no existing scenario asserts Contact admin skills API — no revision.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_contact.py::TestAst1071ContactSkillsApi \
  -q
```

### AST-1067 · AST-1043

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1067-manage-slack-admin-listen-switch`.

Admin Manage Slack listen: `GET`/`PUT /api/admin/contact/listen` (`@require_admin`). Thin wrappers over `slack_listen_enabled` / `set_slack_listen_enabled` + deploy label / production gate. Core: **`docs/test-bible/core/contact.md`**. Page §6c: **`docs/test-bible/frontend/pages.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| GET/PUT + 400/502 + auth 401/403 | `src/ui/api/api_contact.py` | **`TestAst1067ContactListenApi`** |

**Broken / obsolete:** none — additive routes on `contact_bp`.

**Integration:** no existing scenario asserts Contact listen API — no revision.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_contact.py::TestAst1067ContactListenApi \
  -q
```


### AST-1094 · AST-1043

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1094-uat-manage-slack-estelle-activity-list`.

Admin GET `/api/admin/contact/estelle_activity` (`@require_admin`) → `{users: [...]}`. Core: **`docs/test-bible/core/contact.md`**. Page §6c: **`docs/test-bible/frontend/pages.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| GET users + 502 + auth 401 | `src/ui/api/api_contact.py` | **`TestAst1094EstelleActivityApi`** |

**Broken / obsolete:** none — additive route on `contact_bp`.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_contact.py::TestAst1094EstelleActivityApi \
  -q
```

### AST-1206 · AST-1203

**Parent:** [AST-1203 — Need to be able to set the "Debug" flag for Slack messages](https://linear.app/astralcareermatch/issue/AST-1203/need-to-be-able-to-set-the-debug-flag-for-slack-messages). **Publish:** `origin/sub/AST-1203/AST-1206-contact-debug-flag-foundation`.

Admin Manage Slack debug foundation: `GET`/`PUT /api/admin/contact/debug` (`@require_admin`). Thin wrappers over `slack_debug_enabled` / `set_slack_debug_enabled` + deploy label / production gate. Payload mirrors `/listen` (`debug_enabled` + `environment` + `is_production`). Core: **`docs/test-bible/core/contact.md`**. React toggle is sibling **AST-1208** (no §6c page test here).

| Area | Source | Component tests |
| --- | --- | --- |
| GET/PUT + 400/502 + auth 401/403 | `src/ui/api/api_contact.py` | **`TestAst1206ContactDebugApi`** |

**Broken / obsolete:** none — additive routes on `contact_bp`; listen routes unchanged.

**Integration:** no existing scenario asserts Contact debug API — no revision; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_contact.py::TestAst1206ContactDebugApi \
  -q
```
