# contact_debug

**Test module:** `tests/component/data/test_contact_debug.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/data/contact_debug.py` | `tests/component/data/test_contact_debug.py` | no |

---

### AST-1206 · AST-1203

**Parent:** [AST-1203 — Need to be able to set the "Debug" flag for Slack messages](https://linear.app/astralcareermatch/issue/AST-1203/need-to-be-able-to-set-the-debug-flag-for-slack-messages). **Publish:** `origin/sub/AST-1203/AST-1206-contact-debug-flag-foundation`.

Durable Contact Slack debug JSON under `ASTRAL_CONFIG["db_dir"]` / `CONTACT_CONFIG["debug_state_filename"]`. Silent data layer (values only). Core get/set: **`docs/test-bible/core/contact.md`**. Config: **`docs/test-bible/utils/config.md`**. Admin API: **`docs/test-bible/ui/api/api_contact.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| load missing/invalid; save round-trip; TypeError; listen file untouched | `src/data/contact_debug.py` | **`TestAst1206ContactDebugData`** |

**Broken / obsolete:** none — new module; separate from listen JSON.

**Integration:** no existing scenario asserts Contact debug durable file — no revision; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/test_contact_debug.py::TestAst1206ContactDebugData \
  -q
```
