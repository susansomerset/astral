# Meteorites

**Test module:** `tests/component/data/database/test_meteorites.py`

_(Coverage map and manifest blocks appended by Betty `qa-child`.)_

### AST-1557 · AST-1555

**Parent:** [AST-1555 — Meteorite ingress: staging table + inbox/meteorite consolidation](https://linear.app/astralcareermatch/issue/AST-1555/meteorite-ingress-staging-table-inboxmeteorite-consolidation). **Publish:** `origin/sub/AST-1555/AST-1557-meteorite-table-claim-helpers`.

Flat `meteorite` staging table + data-layer claim/insert/update/retention helpers. Config registry `METEORITE_STATES` / `METEORITE_STATES_RETENTION`: **`docs/test-bible/utils/config.md`** § AST-1557. No inbox verbs, classify runner, Estelle, or retention **runner** (siblings AST-1558–AST-1562).

| Area | Source | Component tests |
| --- | --- | --- |
| Schema + indexes | `src/data/database.py` | **`TestAst1557MeteoriteSchema`** |
| Insert fan-out forces NEW; empty no-op | same | **`TestAst1557InsertMeteoriteRows`** |
| Claim → get → clear; states union | same | **`TestAst1557MeteoriteBatchClaim`** |
| get / list-by-state / update whitelist + state key gate | same | **`TestAst1557MeteoriteReadUpdate`** |
| Retention list + delete by ids | same | **`TestAst1557MeteoriteRetention`** |

**Broken / obsolete:** none — additive table/helpers.

**Integration:** none revised (no existing scenario exercises `meteorite` table).

## QA test manifest

1. Schema: `tests/component/data/database/test_meteorites.py::TestAst1557MeteoriteSchema`
2. Insert fan-out: `tests/component/data/database/test_meteorites.py::TestAst1557InsertMeteoriteRows`
3. Claim pool: `tests/component/data/database/test_meteorites.py::TestAst1557MeteoriteBatchClaim`
4. Read/update: `tests/component/data/database/test_meteorites.py::TestAst1557MeteoriteReadUpdate`
5. Retention helpers: `tests/component/data/database/test_meteorites.py::TestAst1557MeteoriteRetention`
6. Config registry: `tests/component/utils/test_config.py::TestAst1557MeteoriteStates`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_meteorites.py \
  tests/component/utils/test_config.py::TestAst1557MeteoriteStates \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.
