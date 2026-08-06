# Repo Admin JSON

**Test module:** `tests/component/core/test_repo_admin_json.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/repo_admin_json.py` | `tests/component/core/test_repo_admin_json.py` | no |

---

### AST-782 · AST-756

Repo-owned **`data/admin/agent.json`** and **`data/admin/agent_task.json`**: bare Copy Output arrays loaded at startup; export writes current DB rows back to disk. Not invoked from admin save paths.

| Area | Source | Component tests |
| --- | --- | --- |
| Missing / malformed file handling | `src/core/repo_admin_json.py` | `TestLoadRepoAdminJsonFile` |
| Transactional apply order (agent → agent_task) | `src/core/repo_admin_json.py` | `TestApplyRepoAdminJsonAtStartup::test_applies_agent_then_agent_task_on_one_connection` |
| Export UTF-8 round-trip files | `src/core/repo_admin_json.py` | `TestExportRepoAdminJsonToFiles` |

Data-layer SQL: **`docs/test-bible/data/database/agents.md`** and **`agent_tasks.md`**. Bootstrap wire: **`docs/test-bible/core/bootstrap.md`**.

---

### AST-783 · AST-756

**Divergence compare + revert:** normalized export-shape compare of live DB vs checked-in repo JSON; **`revert_repo_admin_json_table`** reuses AST-782 startup apply. Admin **`GET /api/admin/repo_json/status`**, **`POST /api/admin/repo_json/revert/<table_key>`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Scalar normalization + compare/revert | `src/core/repo_admin_json.py` | `tests/component/core/test_repo_admin_json.py::TestAst783RepoAdminJsonDivergence` |
| Admin HTTP routes | `src/ui/api/api_admin.py` | `tests/component/ui/api/test_api_admin.py::TestAst783RepoJsonApi` |
| Shared banner + themed confirm | `src/ui/frontend/src/components/RepoJsonDivergenceBanner.tsx` | `tests/component/frontend/components/test_RepoJsonDivergenceBanner.test.tsx` |

Routed pages: **`docs/test-bible/frontend/pages.md`** (**AST-783**).

**UAT seed (AST-786 / AST-878 / AST-1037 / AST-1055 / AST-1060 / AST-1072):** populated **46**-row catalog on the AST-1073 tip (includes **`contact_estelle_turn`**, **`preamble_validate_response`**, **`topic_menu_preamble_confirm`**, **`topic_menu_generate`**). Parallel **AST-1015** **`preamble_validate_response`** stays in **`TestAst1015PreambleValidateCatalogRow`** — not folded into AST-786 on this tip. See **`docs/test-bible/data/database/agent_tasks.md`**.

**UAT seed (AST-787):** six agent personas — see **`docs/test-bible/data/database/agents.md`** (**AST-787**).

**Grouping on revert/startup (AST-790):** import forwards four grouping columns — see **`docs/test-bible/data/database/agent_tasks.md`** (**AST-790**).

---

### AST-793 · AST-756 (UAT bug)

**Product fix:** `apply_agent_task_repo_json_startup` writes repo JSON rows verbatim (including **`task_key_uuid`** and **`updated_at`**) via **`_apply_agent_task_repo_json_rows_exact`** so post-revert **`get_repo_admin_json_divergence_status`** clears **`agent_task.diverged`**. **`src/data/database.py` only** — compare/UI unchanged.

| Area | Source | Component tests |
| --- | --- | --- |
| Revert clears divergence | `src/core/repo_admin_json.py`, `src/data/database.py` | `tests/component/core/test_repo_admin_json.py::TestAst793AgentTaskRevertDivergence::test_revert_clears_agent_task_divergence_after_db_edit` |
| Preserves file UUID | `src/data/database.py` | `TestAst793AgentTaskRevertDivergence::test_revert_preserves_repo_task_key_uuid` |
| Idempotent double revert | same | `TestAst793AgentTaskRevertDivergence::test_double_revert_agent_task_stays_not_diverged` |

**AST-793** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_repo_admin_json.py::TestAst793AgentTaskRevertDivergence \
  -q
```

**test-child scope gate (required):** `git show 05b4374 --name-only` — expect **only** `src/data/database.py` and `docs/features/foundation/ast-793-uat-divergence-banner-persists-after-revert-to-file.md` (no `data/admin/**`).

---

### AST-878 · AST-872 (UAT bug)

Repo **`agent_task.json`** catalog gains **`fetch_culture_pages`** — primary manifest in **`docs/test-bible/data/database/agent_tasks.md`** (**AST-878**).

---

### AST-880 · AST-879

**`vet_inflow_discovery`** repo JSON + UAT fixture carry AST-880 encoded A–F rubric marker — byte identity with **`docs/uat-fixtures/AST-756/expected-agent_task.json`** unchanged (**AST-786**). DB migration: **`docs/test-bible/data/database/agent_tasks.md`** / **`TestAst880VetInflowEncodedPromptMigration`**.

---

### AST-1055 · AST-1052

Repo **`agent_task.json`** gains **`meteorite_like`** + **`meteorite_upshot`** (Grace / Estelle prompt twins). Catalog frozenset **39 → 41**; UAT fixture **`docs/uat-fixtures/AST-756/expected-agent_task.json`** byte-locked. Primary TASK_CONFIG / consult: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Catalog + prompts | `data/admin/agent_task.json` | **`TestAst1055MeteoriteCatalogRows`**, revised **`TestAst786AgentTaskRepoJsonSeed`** |

**Broken / obsolete:** AST-786 **39**-row asserts → **41** (superseded to **42** by **AST-1060**).

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1055MeteoriteCatalogRows \
  -q
```

### AST-1060 · AST-1058

Repo **`agent_task.json`** gains **`qualify_meteorite`** (Ruth enrichment shell). Catalog frozenset **41 → 42**; UAT fixture byte-locked. Primary config: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Catalog + Ruth prompts | `data/admin/agent_task.json` | **`TestAst1060QualifyMeteoriteCatalogRow`**, revised **`TestAst786AgentTaskRepoJsonSeed`** |

**Broken / obsolete:** AST-786 **41**-row asserts → **42** (qualify only; do **not** fold AST-1015 preamble into this tip’s lock).

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1060QualifyMeteoriteCatalogRow \
  -q
```


### AST-1072 · AST-1046

Repo **`agent_task.json`** gains **`contact_estelle_turn`** (Estelle CHAT seed — ternary envelope prompts). Catalog frozenset **42 → 43**; UAT fixture **`docs/uat-fixtures/AST-756/expected-agent_task.json`** byte-locked. Primary config / agent: **`docs/test-bible/utils/config.md`** / **`docs/test-bible/core/agent.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Catalog + Estelle envelope prompts | `data/admin/agent_task.json` | **`TestAst1072ContactEstelleTurnCatalogRow`**, revised **`TestAst786AgentTaskRepoJsonSeed`** |

**Broken / obsolete:** AST-786 **42**-row asserts → **43** (`contact_estelle_turn` only; do **not** fold AST-1015 preamble into this tip’s lock).

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1072ContactEstelleTurnCatalogRow \
  -q
```


---

### AST-1075 · AST-953

**Parent:** [AST-953 — Topic Menu Generation](https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation). **Publish:** `origin/sub/AST-953/AST-1075-estelle-preamble-confirm-and-topic-menu-generation`.

Repo `agent_task.json` gains Estelle rows `topic_menu_preamble_confirm` + `topic_menu_generate` (Topic Menu group; confirm ask + closed informs generate prompts). Full AST-786 frozenset/UAT fixture lock stays tip-owned (parallel epics); this ticket asserts the two new rows only. Config: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Catalog Estelle Topic Menu rows | `data/admin/agent_task.json` | **`TestAst1075TopicMenuCatalogRows`** |

**Broken / obsolete:** do **not** fold these keys into AST-786 tip lock from other epics in this pass — row-level assert only.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_repo_admin_json.py::TestAst1075TopicMenuCatalogRows \
  -q
```

### AST-1073 · AST-1046

Repo **`agent_task.json`** enriches **`contact_estelle_turn`** prompts (ACL `skill_calls` + Slack/live_content). Catalog frozenset **43 → 46** on this tip (also carries preamble + topic_menu rows from rolled base); UAT fixture byte-locked. Primary: **`docs/test-bible/core/contact.md`** / **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Prompt enrich + catalog lock | `data/admin/agent_task.json` | revised **`TestAst1072ContactEstelleTurnCatalogRow`**, revised **`TestAst786AgentTaskRepoJsonSeed`** |

**Broken / obsolete:** AST-786 **43**-row asserts → **46**.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1072ContactEstelleTurnCatalogRow \
  -q
```

### AST-1089 · AST-1087

Repo **`agent_task.json`** gains **`parse_meteorite_email`** (Ruth email-HTML parse shell; both `html_links` / `subject_body` modes in prompts). Catalog frozenset **46 → 47**; UAT fixture byte-locked. Primary config: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Catalog + Ruth parse prompts | `data/admin/agent_task.json` | **`TestAst1089ParseMeteoriteEmailCatalogRow`**, revised **`TestAst786AgentTaskRepoJsonSeed`** |

**Broken / obsolete:** AST-786 **46**-row asserts → **47**.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1089ParseMeteoriteEmailCatalogRow \
  -q
```

### AST-1106 · AST-1087

**Parent:** [AST-1087](https://linear.app/astralcareermatch/issue/AST-1087/add-gaze-email-as-a-dispatch-task). **Publish:** `origin/sub/AST-1087/AST-1106-uat-gaze-email-missing-from-scheduled-actions-default-view`.

Repo **`agent_task.json`** gains empty-prompt **`gaze_email`** Job Review shell (`task_seq` 2.3); AST-756 fixture byte-locked. Catalog frozenset **47 → 48**.

| Area | Source | Component tests |
| --- | --- | --- |
| Catalog row + fixture lock | `data/admin/agent_task.json`, `docs/uat-fixtures/AST-756/expected-agent_task.json` | **`TestAst1106GazeEmailCatalogRow`**; revised **`TestAst786AgentTaskRepoJsonSeed`** (48) |

**Broken / obsolete:** AST-786 **47**-row asserts → **48**.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_repo_admin_json.py::TestAst1106GazeEmailCatalogRow \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  -q
```

### AST-1107 · AST-1087

**Parent:** [AST-1087 — Add gaze_email as a dispatch task](https://linear.app/astralcareermatch/issue/AST-1087/add-gaze-email-as-a-dispatch-task). **Publish:** `origin/sub/AST-1087/AST-1107-uat-admin-task-name-should-equal-task-key-for-now`.

Temporary UAT clarity: every current `agent_task.task_name` equals that row’s `task_key` (repo JSON + AST-756 fixture). Grouping / prompts / `task_key` identifiers unchanged. UI already renders `task_name || task_key`.

| Area | Source | Component tests |
| --- | --- | --- |
| Catalog label rewrite + fixture lock | `data/admin/agent_task.json`, `docs/uat-fixtures/AST-756/expected-agent_task.json` | **`TestAst1107TaskNameEqualsTaskKey`**; revised catalog row asserts that pinned friendly labels |

**Broken / obsolete:** Friendly `task_name` asserts (Qualify Meteorite, Parse Meteorite Email, Topic Menu…, etc.) → `task_name == task_key`.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_repo_admin_json.py::TestAst1107TaskNameEqualsTaskKey \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1089ParseMeteoriteEmailCatalogRow \
  tests/component/core/test_repo_admin_json.py::TestAst1106GazeEmailCatalogRow \
  -q
```


### AST-1144 · AST-1128

**Parent:** [AST-1128 — gaze_email — candidate-bound dispatch (redesign)](https://linear.app/astralcareermatch/issue/AST-1128/gaze-email-candidate-bound-dispatch-redesign). **Publish:** `origin/sub/AST-1128/AST-1144-uat-parse-meteorite-email-metadata-dict-str`.

`parse_meteorite_email` cache_prompt documents optional `metadata` object (`company` / `location`); AST-756 fixture remains byte-identical to repo `agent_task.json`.

| Area | Source | Component tests |
| --- | --- | --- |
| Prompt + fixture lock | `data/admin/agent_task.json` | **`TestAst1144ParseMeteoriteEmailMetadataPrompt`** |

**Broken / obsolete:** none — additive prompt wording.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_repo_admin_json.py::TestAst1144ParseMeteoriteEmailMetadataPrompt \
  -q
```

### AST-1196 · AST-1188

**Parent:** [AST-1188 — Errors for qualify_meteorite dispatch task](https://linear.app/astralcareermatch/issue/AST-1188/errors-for-qualify-meteorite-dispatch-task). **Publish:** `origin/sub/AST-1188/AST-1196-agent-task-synthesize-email-link-subject`.

`qualify_meteorite` `cache_prompt` / `user_prompt`: synthesize `email-<originalsender>-<timestamp>` when no ATS link; subject as title; empty-string fails (never JSON null); positional `astral_job_id` (`000`/`001`/…); never drop a row. Surgical AST-756 fixture lockstep on that row’s three fields only. Catalog tip lock **53** current keys (includes `evaluate_meteorite` / `craft_evaluate_meteorite_rubric` / candidate-requested / `find_company_website`). Full catalog↔fixture byte-identity deferred to parent re-baseline (fixture still 51 rows).

| Area | Source | Component tests |
| --- | --- | --- |
| Prompt contract + surgical fixture | `data/admin/agent_task.json`, `docs/uat-fixtures/AST-756/expected-agent_task.json` | **`TestAst1196QualifyMeteoritePromptContract`** |
| Catalog frozenset / startup apply | same | revised **`TestAst786AgentTaskRepoJsonSeed`** (53; byte-for-byte retired) |
| Ruth shell fields still present | same | **`TestAst1060QualifyMeteoriteCatalogRow`** (unchanged asserts still green) |

**Broken / obsolete:** AST-786 **48**-row + whole-file byte-identity asserts — tip catalog is **53**; inherited fixture drift (missing two meteorite rows) is out of scope for this child. Also revised **`TestAst1107TaskNameEqualsTaskKey::test_fixture_byte_locked_after_rename`**, **`TestAst1144…`** fixture byte tail, **`TestAst1154…::test_fixture_byte_locked_with_completeness_prompts`** → per-key / surgical checks.

**Integration:** none revised.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_repo_admin_json.py::TestAst1196QualifyMeteoritePromptContract \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1060QualifyMeteoriteCatalogRow \
  tests/component/core/test_repo_admin_json.py::TestAst1107TaskNameEqualsTaskKey \
  tests/component/core/test_repo_admin_json.py::TestAst1144ParseMeteoriteEmailMetadataPrompt \
  tests/component/core/test_repo_admin_json.py::TestAst1154GradedTaskCompletenessPrompts \
  -q
```


### AST-1212 · AST-1182

**Parent:** [AST-1182 — Rename task to meteorite_email + AI payload as visible text/links](https://linear.app/astralcareermatch/issue/AST-1182/rename-task-to-meteorite-email-ai-payload-as-visible-textlinks). **Publish:** `origin/sub/AST-1182/AST-1212-rename-parse-meteorite-email-to-meteorite-email`.

Ruth `agent_task` row identity `parse_meteorite_email` → **`meteorite_email`** (`task_name` lockstep; `task_key_uuid` frozen). AST-756 fixture surgical sync on that row. Catalog frozenset still **53** (rename, not add). Config half: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Catalog + fixture row + frozenset | `data/admin/agent_task.json`, `docs/uat-fixtures/AST-756/expected-agent_task.json` | revised **`TestAst786AgentTaskRepoJsonSeed`**, **`TestAst1089ParseMeteoriteEmailCatalogRow`**, **`TestAst1106GazeEmailCatalogRow`**, **`TestAst1144ParseMeteoriteEmailMetadataPrompt`** |

**Broken / obsolete:** catalog/fixture lookups and AST-786 frozenset entry still named `parse_meteorite_email`.

**Integration:** none revised.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1089ParseMeteoriteEmailCatalogRow \
  tests/component/core/test_repo_admin_json.py::TestAst1106GazeEmailCatalogRow \
  tests/component/core/test_repo_admin_json.py::TestAst1144ParseMeteoriteEmailMetadataPrompt \
  -q
```
