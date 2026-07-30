# AST-1074 — Topic Menu model and persistence

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1074/topic-menu-model-and-persistence-topic-menu-generation  
**Parent:** https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation  

**Publish ref (origin):** `sub/AST-953/AST-1074-topic-menu-model-and-persistence`  
**Parent integration ref:** `ftr/AST-953-topic-menu-generation`

Ship the durable **Topic Menu** model: config-driven closed `informs` catalog + status triad, a `candidate_data.topic_menu` meta sibling, and core validate / get / save / revise helpers that keep prior topic content (retire instead of wipe). Sibling **AST-1075** owns Estelle preamble confirm and menu generation; this ticket stops at persistence contracts those callers will use.

Boundaries (do **not** implement): Estelle confirm/generation agent tasks or prompts (AST-1075); satisfaction conversation / progress UI; REQUIRED_TOPICS_READY / ALL_TOPICS_READY hops; artifact crafting; candidate state-machine vocabulary changes; mechanical preamble (AST-952 family already on `dev`).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `TOPIC_MENU_CONFIG` (informs catalog, statuses, topic field contract); module asserts | utils |
| `src/core/candidate.py` | Topic Menu get / validate / save / revise helpers + `debug=` found/recorded lines | core |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Document `topic_menu` meta sibling + topic shape | docs |

No UI pages, no `TASK_CONFIG` / agent_task rows, no database schema migration (meta key under existing `candidate_data` JSON), no `tests/` / bible edits (Betty after Code Complete).

---

## Stage 1: `TOPIC_MENU_CONFIG` contract

**Done when:** `TOPIC_MENU_CONFIG` is importable from `src.utils.config` with a closed `informs` tuple, a closed `statuses` tuple, and topic field/name literals; module-level asserts fail loudly if the catalog drifts from parent AC vocabulary.

1. In `src/utils/config.py`, immediately **after** `PREAMBLE_CONFIG` asserts (before the next unrelated candidate config block), add:

```python
# AST-1074: Topic Menu closed informs + status triad (generation = AST-1075).
TOPIC_MENU_CONFIG = {
    # Parent AC closed vocabulary — Estelle may not invent new target kinds.
    "informs": (
        "rubrics",
        "base_resume",
        "strengths",
        "priorities",
        "deal_breakers",
        "backstory",
    ),
    "statuses": ("open", "ready", "retired"),
    "default_status": "open",
    # Stable key under candidate_data (meta sibling of contact/context/artifacts).
    "candidate_data_key": "topic_menu",
    "topic_required_fields": ("id", "name", "ask", "required", "informs", "status"),
}
```

2. Immediately after the block, add asserts:

   - `informs` is a non-empty `tuple` of unique non-empty `str`; equals exactly the six parent targets above (order as written).
   - `statuses` is a `tuple` equal to `("open", "ready", "retired")`.
   - `default_status` is in `statuses`.
   - `candidate_data_key == "topic_menu"`.
   - `topic_required_fields` is a non-empty `tuple` of unique non-empty `str` and includes at least `id`, `name`, `ask`, `required`, `informs`, `status`.
   - Cross-check library homes (documentation contract, not path writes): `strengths` / `priorities` / `deal_breakers` / `backstory` are members of `CANDIDATE_LIBRARY_CONFIG["context_keys"]`; `base_resume` is an artifacts key name (string literal match only — do not invent a new library key).

⚠️ **Decision:** Use umbrella `rubrics` (parent AC wording) rather than per-rubric keys (`like_rubric`, `do_rubric`, …). Parent closed catalog is six targets; per-artifact rubric mapping is later satisfaction / craft work, not this model.

⚠️ **Decision:** Store the menu as meta sibling `candidate_data.topic_menu` (same class as `lifecycle` / `intakes_old` / `pending_craft_generations`), **not** inside `context` or `artifacts`. Topics are intake orchestration state; library blobs stay prose/artifact content only (AST-1014).

⚠️ **Decision:** Do **not** expose `TOPIC_MENU_CONFIG` on `GET /api/ui_config` in this ticket — no UI consumer yet; AST-1075 imports config in Python. If a later UI ticket needs the catalog, add ui_config there.

3. If `config.py`’s top-of-file comment inventory lists named `*_CONFIG` blocks, add a one-line entry for `TOPIC_MENU_CONFIG` next to `PREAMBLE_CONFIG`.

---

## Stage 2: Core Topic Menu helpers (validate / get / revise / save)

**Done when:** `src/core/candidate.py` exposes public helpers that load/store `candidate_data.topic_menu`, validate topics against `TOPIC_MENU_CONFIG`, and revise without wiping prior topics (missing ids → `retired`); `debug=True` emits Style D found/recorded lines on save/revise paths; no Estelle / agent_task calls.

1. Near other library helpers in `src/core/candidate.py`, import `TOPIC_MENU_CONFIG` from `src.utils.config`.

2. Add `_topic_menu_key() -> str` returning `str(TOPIC_MENU_CONFIG["candidate_data_key"])`.

3. Add `empty_topic_menu() -> dict` returning:

```python
{"topics": []}
```

No other top-level keys in this ticket (generation timestamps / preamble-confirm markers belong to AST-1075 if needed).

4. Add `normalize_topic_menu(raw: Any) -> dict`:

   - If `raw` is not a `dict`, return `empty_topic_menu()`.
   - Read `topics = raw.get("topics")`; if not a `list`, treat as `[]`.
   - Return `{"topics": list(topics)}` (shallow copy of the list only — callers validate members separately).

5. Add `get_topic_menu(candidate_id: str) -> dict`:

   - Load candidate via existing `get_candidate`; if missing, raise `ValueError(f"Candidate not found: {candidate_id}")` (same pattern as intake archive helpers).
   - Return `normalize_topic_menu((candidate.get("candidate_data") or {}).get(_topic_menu_key()))`.

6. Add `validate_topic(topic: Any) -> dict` — returns a **new** normalized topic dict or raises `ValueError` with a safe message:

   - `topic` must be a `dict`.
   - `id`: non-empty `str` after strip (stable identity for revise).
   - `name`: non-empty `str` after strip.
   - `ask`: non-empty `str` after strip.
   - `required`: must be `bool` (reject truthy strings / ints).
   - `informs`: non-empty `list` of unique non-empty `str`; every entry must be in `TOPIC_MENU_CONFIG["informs"]`; reject empty list (parent: every topic informs at least one allowed target).
   - `status`: must be in `TOPIC_MENU_CONFIG["statuses"]`; if missing, use `TOPIC_MENU_CONFIG["default_status"]`.
   - Ignore unknown extra keys for forward-compat (do not persist them in the returned dict — only the required fields).
   - Returned shape:

```python
{
    "id": id,
    "name": name,
    "ask": ask,
    "required": required,
    "informs": list(informs),  # preserved order, deduped first-seen
    "status": status,
}
```

7. Add `validate_topic_menu(menu: Any) -> dict`:

   - Normalize via `normalize_topic_menu`.
   - Validate each topic; collect ids; raise `ValueError` if duplicate `id` values.
   - Return `{"topics": [validated…]}`.

8. Add `revise_topic_menu(existing: Any, incoming: Any) -> dict` — **revise without wipe**:

   - `existing_n = validate_topic_menu(existing)` (empty ok).
   - `incoming_n = validate_topic_menu(incoming)` (may be empty → retire all existing).
   - Index existing topics by `id`.
   - Build `out: list` in **incoming order**:
     - For each incoming topic: if id known, keep that identity and take incoming field values (name/ask/required/informs/status as validated); else append as new.
   - Then append every existing topic whose `id` is **not** in incoming, with `status` forced to `"retired"` (preserve name/ask/required/informs).
   - Return `{"topics": out}`.

⚠️ **Decision:** Revision identity is topic `id` (string), not name. AST-1075 must mint stable ids on generation (UUID or equivalent). Renaming a topic keeps the same `id` and updates `name`/`ask`. Topics dropped from an incoming generation are **retired**, never deleted from the list.

⚠️ **Decision:** Do **not** provide a `wipe=True` / hard-delete API in this ticket. Parent AC3 forbids wholesale wipe; retired retention is the only remove path.

9. Add `save_topic_menu(candidate_id: str, menu: Any, *, revise: bool = True, debug: bool = False) -> dict`:

   - `logger.set_debug_flag(debug)` at entry (same pattern as `save_candidate_data`).
   - Load current via `get_topic_menu(candidate_id)`.
   - If `revise` is `True`: `to_store = revise_topic_menu(current, menu)`.
   - If `revise` is `False`: `to_store = validate_topic_menu(menu)` (full replace of the `topics` list content **after** validation — still no partial deep-merge of individual topics; used only when caller intentionally supplies the complete authoritative list including any retired rows they want kept). Default remains `revise=True`.
   - Persist with `save_candidate_data(candidate_id, {_topic_menu_key(): to_store}, debug=debug)` (lists overwrite under `_deep_merge` — do not manually merge topic arrays).
   - When `debug=True`, emit Style D lines before/after persist:
     - found: current topic count + ids (truncated if long via existing `truncate_debug_content` if already imported in this module; otherwise short `len` + first/last id only).
     - recorded: stored topic count, counts by status (`open`/`ready`/`retired`), and whether `revise` was used.
     - Use `logger.debug_index` / `logger.debug_detail` with `func="candidate.save_topic_menu"`, identifier=`candidate_id`, outcome `found` then `recorded` (index `1/2`, `2/2`).
   - Return `to_store`.

10. Do **not** add Flask routes in this ticket. AST-1075 / a later UI ticket will call these helpers.

---

## Stage 3: Document the data model

**Done when:** `CANDIDATE_DATA_MODEL.md` documents `topic_menu` as a meta sibling and the topic field/status/informs contract; no stale claim that meta is only lifecycle/intakes/pending_craft.

1. In `docs/features/candidate/CANDIDATE_DATA_MODEL.md`, under the `candidate_data (library + meta)` section:

   - Extend the meta-siblings sentence to include `topic_menu` (AST-1074).
   - Add a subsection **### topic_menu (AST-1074 / AST-953)** describing:

```text
candidate_data.topic_menu = {
  "topics": [
    {
      "id": "<stable str>",
      "name": "<display name>",
      "ask": "<directed question>",
      "required": true|false,
      "informs": ["backstory", ...],  # ⊆ TOPIC_MENU_CONFIG["informs"], non-empty
      "status": "open" | "ready" | "retired"
    },
    ...
  ]
}
```

   - Note: revise keeps prior topics; dropped ids become `retired` rather than deleted.
   - Note: generation/confirm lives in AST-1075; this epic does not craft artifacts — `informs` declares intent only.
   - Cross-link `TOPIC_MENU_CONFIG` in `src/utils/config.py`.

2. Do **not** add Topic Menu fields under `contact` / `context` / `artifacts` tables in that doc.

---

## Self-Assessment

**Scope:** `Single-Component` — config contract + core candidate persistence helpers + data-model doc; no UI, no agent tasks, no schema migration.

**Conf:** `high` — mirrors AST-1014 meta-sibling + `save_candidate_data` / `PREAMBLE_CONFIG` assert patterns already on `dev`; revise-by-id is a concrete algorithm with no open product questions (parent Open questions: none).

**Risk:** `Medium` — wrong revise semantics would lose topic history for AST-1075 regenerations; mitigated by default `revise=True` and retired retention. Informs catalog mistakes would block valid menus — asserts lock the six parent targets.

---

## Code Rules check

- **§2.1 / config-source-of-truth / no-hardcoded-sets:** informs + statuses only in `TOPIC_MENU_CONFIG`; helpers read the config block, not inline frozensets.
- **§3.3 import direction:** core → utils/config + data via existing `save_candidate_data`; no UI → data shortcuts; no external Slack/LLM in this ticket.
- **§1.3 DRY:** reuse `save_candidate_data` / `get_candidate`; do not reimplement JSON merge.
- **debug-contract-gated:** Style D only when `debug=True` on `save_topic_menu`.
- **Out of scope enforced:** no Estelle tasks, no state hops, no satisfaction UI, no `tests/` edits.

---

## Review

**Publish ref:** `sub/AST-953/AST-1074-topic-menu-model-and-persistence`

**Build tip:** filled in after Stage 3 commit on this ref.

