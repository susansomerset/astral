# AST-983: Docs, bible, and test sweep for agent_responses table retirement

**Linear:** [AST-983](https://linear.app/astralcareermatch/issue/AST-983/docs-bible-and-test-sweep-for-agent-responses-table-retirement)  
**Parent:** [AST-975](https://linear.app/astralcareermatch/issue/AST-975/decommission-table-agent-responses) — Decommission table AGENT_RESPONSES  
**Publish ref:** `origin/sub/AST-975/AST-983-docs-bible-test-sweep-agent-responses`

After AST-981 (stop writing the standalone table) and AST-982 (drop schema), mandate prose, config comments, Test Bible language, and component tests still conflate the retired standalone `agent_responses` **table** with the live entity-row `agent_responses` JSON **columns**. This ticket updates engineer-owned mandate/config comments so inventory language matches reality, and specifies Betty’s bible/test cleanup so nothing still assumes the standalone table exists — without touching entity-column contract language that AST-984 will retire later.

## UAT fitness

- **AC restored:** Parent AST-975 AC 4 — “Mandate docs and Test Bible text no longer list the standalone `agent_responses` table as live inventory; if entity columns remain, prose clearly distinguishes **table (retired)** vs **entity JSON column (live)**.” Child AST-983 AC matches that sentence (entity columns remain until AST-984).
- **Correct outcome:** A reader of Code Rules / config comments / Test Bible sees the standalone table as **retired**, and entity-row `agent_responses` JSON columns as **still live** (latest-only refs into `agent_data`) until the column-retirement sibling lands. Component tests no longer mock or require `add_agent_response_entry` after AST-981 removes that call site.
- **Sibling check:** AST-981 removes runtime/script writes to the standalone table (including `add_agent_response_entry` usage). AST-982 removes table create/ensure/inventory from the data layer. AST-984 (later) drops entity columns and revises §2.4.1 / statute — **out of this plan**. Verify after merging `origin/ftr/AST-975-decommission-table-agent-responses` that 981+982 tips are present before editing prose that claims the table is gone.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done. (N/A as runtime symptom — this ticket is docs/test inventory honesty.)
- **Wrong fix rejected:** Deleting or rewriting §2.4.1 / `astral.batch.entity-agent-responses-latest-only` / `pattern.batch.entity-agent-responses` to drop entity-column language — that is AST-984. Also rejected: engineer commits under `tests/` or `docs/test-bible/**` (Betty owns those; pre-commit bans engineer edits).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `docs/ASTRAL_CODE_RULES.md` | Split ENTITY_TYPES bullet and §2.4.1 / layer-rules mentions so standalone **table** is retired and entity JSON **column** stays live | docs |
| `src/utils/config.py` | ENTITY_TYPES comment: same table-vs-column split | utils |
| `docs/test-bible/data/database/agent_responses.md` | Betty at qa-child: title/body state entity-column upsert scope; note standalone table retired (AST-975) | bible (Betty) |
| `docs/test-bible/core/roster.md` | Betty at qa-child: only if prose still implies a live standalone table (entity-column refs stay) | bible (Betty) |
| `docs/test-bible/dev/backfill_latest_only_rubric_entity_data.md` | Betty at qa-child: same — entity-column backfill language only | bible (Betty) |
| `tests/component/core/test_agent.py` | Betty at qa-child: remove `add_agent_response_entry` monkeypatches / imports after AST-981 deletes the product call | tests (Betty) |
| `tests/component/data/database/test_agent_responses.py` | Betty at qa-child: keep entity-column `append_agent_response` coverage; drop any cases that exercise the standalone table / `add_agent_response_entry` / `_ensure_agent_responses_schema` | tests (Betty) |

**Explicitly not in this ticket:** `src/data/database.py` schema/API (AST-982), runtime call sites (AST-981), entity-column DDL or §2.4.1 statute retirement (AST-984), historical feature plan docs under `docs/features/**` (leave as archaeology), `canon/statutes/**` / `canon/patterns/**` entity-column entries (still correct until AST-984).

**Build gate:** Linear `blockedBy` AST-982. Before Stage 1, merge `origin/ftr/AST-975-decommission-table-agent-responses` (and confirm AST-981 + AST-982 commits are ancestors). If ftr still creates/writes the standalone table, **stop** and comment on AST-983 — do not claim retirement in mandate prose while siblings are unfinished.

## Stage 1: Mandate + config comment split

**Done when:** `docs/ASTRAL_CODE_RULES.md` and `src/utils/config.py` no longer list the standalone `agent_responses` table as live inventory, and every remaining `agent_responses` mention in those two files is explicitly the entity JSON column (or clearly labeled pending AST-984). Grep of those two files for `agent_responses` shows no “table inventory” framing.

1. In `docs/ASTRAL_CODE_RULES.md`, locate the **ENTITY_TYPES** bullet under the config inventory (currently: “Single source of truth used across `agent_data`, `dispatch_ledger`, `agent_responses`, and config”). Replace so it names **entity-row `agent_responses` JSON columns** (company / job / candidate), not a table, and add a short clause that the standalone `agent_responses` **table** is retired (AST-975).

2. In the same file, §2.4.1 **Entity Agent Responses**: keep the latest-only entity-column contract unchanged. Immediately under the section heading (before “Every entity table…”), add one sentence: the standalone `agent_responses` **table** is retired; this section describes only the entity-row JSON **column** (live until AST-984). Do **not** delete the JSON example, `prompt_blocks` / `agent_data` FK language, or the statute id line.

3. In the same file, §3.2 / External layer paragraph that lists “data-layer interactions (agent_data, agent_responses, prompt resolution)”: reword `agent_responses` to **entity-row `agent_responses` refs** (or equivalent) so it cannot be read as the retired table.

4. In `src/utils/config.py`, update the `ENTITY_TYPES` comment block (the three lines above `ENTITY_TYPES = [...]`) to the same table-retired / column-live split as step 1. Do not change the `ENTITY_TYPES` list values.

5. Repo grep (engineer verification only — do not edit Betty trees):  
   `rg -n 'agent_responses' docs/ASTRAL_CODE_RULES.md src/utils/config.py`  
   Confirm every hit is column-scoped or explicitly marks the table retired. If a hit still treats the standalone table as live inventory, fix it in this stage.

⚠️ **Decision:** Engineer edits stop at Code Rules + `config.py` comments. Bible and `tests/` cleanup are Betty’s at **qa-child** (see Stage 2 expectations). Historical plans and entity-column statutes stay until AST-984.

## Stage 2: Betty expectations (no engineer commits)

**Done when:** This stage’s checklist is written into the plan (already below) so Betty’s qa-child pass has a concrete inventory; engineer does **not** create commits under `tests/`, `docs/test-bible/**`, or `docs/ASTRAL_TEST_BIBLE.md`.

1. At **Code Complete**, Betty owns:
   - `docs/test-bible/data/database/agent_responses.md` — scope line must say **entity JSON column** / `append_agent_response` upsert; add one line that the standalone table is retired (AST-975). Keep AST-726 upsert nodeids that still apply.
   - Cross-links in `docs/test-bible/core/roster.md`, `docs/test-bible/core/consult.md`, `docs/test-bible/dev/backfill_latest_only_rubric_entity_data.md` — only amend wording that implies a live standalone table; leave entity-column / dedupe stories intact.
   - `tests/component/core/test_agent.py` — after AST-981 removes `add_agent_response_entry` from `src/core/agent.py`, delete every `monkeypatch.setattr(..., "add_agent_response_entry", ...)` and any import/assert that requires that symbol. Prefer deleting dead mocks over rewiring them to a no-op.
   - `tests/component/data/database/test_agent_responses.py` — retain entity-column upsert coverage; remove cases that call `add_agent_response_entry`, `_ensure_agent_responses_schema`, or otherwise assert the standalone table exists.

2. Engineer must not patch those files if tests fail after merge — post `[qa-handoff]` and assign Betty (stay Tests Ready).

## Self-Assessment

- **Scope:** `minor` — two engineer files (Code Rules + config comment); Betty trees listed as expectations only.
- **Conf:** `high` — AC is a prose split already decided by parent OQ1 (keep columns until AST-984); sibling ownership is clear.
- **Risk:** `low` — comment/mandate wording only on the engineer path; wrong column-mandate edit would be caught by Joan/Radia and by AST-984’s later mandate change.

## Code Rules self-review

| Rule | Check |
|------|-------|
| §1.3 DRY | No new helpers; reuse existing §2.4.1 column contract. |
| §2.1 config | Comment-only change to `ENTITY_TYPES` block; no new config keys. |
| §2.4 / §2.4.1 | Column contract preserved; table marked retired only. |
| §2.6 state machine | Untouched. |
| §3.3 imports | Untouched. |
| §3.5 naming | Untouched. |
| Engineer test-tree ban | Stages forbid engineer commits to `tests/` / bible. |
