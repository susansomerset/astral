# Agents

**Test module:** `tests/component/data/database/test_agents.py`

---

### AST-492 · AST-495 · AST-491

**`save_agent`** / **`get_agent`** / **`list_agents`** — **`brain_setting`** column required on insert; migration off legacy **`model_code`**. Full **AST-492** epic (tier helpers, **`do_task`**, admin CRUD, Manage Agents UI) lives in **`docs/test-bible/ui/api/api_admin.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Agent persistence + insert requires **`brain_setting`** | `src/data/database.py` | **`tests/component/data/database/test_agents.py`** |

Narrow manifest (**agents cluster**):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_agents.py
```
