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
