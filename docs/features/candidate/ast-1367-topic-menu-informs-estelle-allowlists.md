# AST-1367 — Topic Menu informs + Estelle allowlists

**Linear:** [AST-1367](https://linear.app/astralcareermatch/issue/AST-1367/topic-menu-informs-estelle-allowlists-add-ideal-day-to-the-set-of)
**Parent:** [AST-1360](https://linear.app/astralcareermatch/issue/AST-1360/add-ideal-day-to-the-set-of-candidate-context-strengths-priorities-etc) — Add `ideal_day` to the set of candidate context (strengths, priorities, etc.)
**Publish ref:** `sub/AST-1360/AST-1367-topic-menu-informs-estelle-allowlists`
**Depends on:** [AST-1365](https://linear.app/astralcareermatch/issue/AST-1365/ideal-day-library-token-add-ideal-day-to-the-set-of-candidate-context) — `ideal_day` in `CANDIDATE_LIBRARY_CONFIG["context_keys"]` (must be on HEAD after `sync-child.sh` before build)

Extend the Topic Menu closed informs / deliverables catalog with `ideal_day`, and align Estelle preamble confirm / generate packet + patch allowlists (config + matching seed prompt wording) so Ideal Day can be summarized, revised, and targeted by topics — peer of strengths / priorities / deal_breakers / backstory. Core packet builders and `validate_topic` already read those config tuples; no new API. This ticket does **not** own Candidate Ideal Day UI (AST-1366) or JD / DO / LIKE craft rubric prompt text (AST-1368).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `ideal_day` to `TOPIC_MENU_CONFIG["informs"]` + equality/home asserts; add to `TOPIC_MENU_GEN_CONFIG["packet_context_keys"]` and `patchable_context_keys` | utils |
| `data/admin/agent_task.json` | Update `topic_menu_preamble_confirm` and `topic_menu_generate` `cache_prompt` strings so patch/informs vocabulary includes `ideal_day` | data (seed) |

**Out of scope (do not touch):**

| File / area | Owner |
|-------------|--------|
| `CANDIDATE_LIBRARY_CONFIG` / `TOKEN_SOURCES["IDEAL_DAY"]` / completeness gate | AST-1365 (already on tip) |
| `NAV_CONFIG`, `CandidateIdealDay.tsx`, routes | AST-1366 |
| `craft_do_rubric` / LIKE / Job Description craft rows | AST-1368 |
| `src/core/intake.py` / `src/core/candidate.py` | No code change — already iterate config |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Already documents `context.ideal_day`; topic_menu `informs` already ⊆ `TOPIC_MENU_CONFIG["informs"]` |
| `tests/` / `docs/test-bible/**` | Betty — note AST-1365 left `test_topic_menu_informs_exclude_ideal_day_until_sibling` asserting exclusion until this sibling |

## Stages

### Stage 0: Prerequisite gate (build-time, no commit)

**Done when:** After `sync-child.sh` for this publish ref, `ideal_day` is in `CANDIDATE_LIBRARY_CONFIG["context_keys"]` and still **absent** from `TOPIC_MENU_CONFIG["informs"]` (this ticket’s work).

1. Run sync-child as usual for this ticket.
2. Confirm library home from AST-1365 and that informs catalog is still pre-change:

```bash
python3 -c "
from src.utils.config import CANDIDATE_LIBRARY_CONFIG, TOPIC_MENU_CONFIG
assert 'ideal_day' in CANDIDATE_LIBRARY_CONFIG['context_keys']
assert 'ideal_day' not in TOPIC_MENU_CONFIG['informs']
"
```

3. If the library assert fails (AST-1365 not yet on `origin/dev` / `origin/ftr/AST-1360` ancestry): **stop**. Comment on **parent AST-1360** with the Stage-blocked format naming this ticket and the missing library key — do **not** add `ideal_day` to `CANDIDATE_LIBRARY_CONFIG` here, and do **not** merge sibling `sub/AST-1360/AST-1365-*` by hand.
4. If `ideal_day` is **already** in `TOPIC_MENU_CONFIG["informs"]` before Stage 1: **stop** and comment on this ticket — do not double-apply.

### Stage 1: Topic Menu informs + Estelle packet/patch allowlists (config)

**Done when:** `TOPIC_MENU_CONFIG["informs"]` includes `ideal_day` after `backstory`; load-time equality assert matches; context-informs home loop includes `ideal_day`; `TOPIC_MENU_GEN_CONFIG` packet and patch tuples include `ideal_day` after `deal_breakers`; `import src.utils.config` succeeds; `validate_topic` accepts a topic with `informs: ["ideal_day"]`; preamble packet snapshot / patch whitelist include the key without editing `intake.py`.

1. In `src/utils/config.py`, inside `TOPIC_MENU_CONFIG`, extend `"informs"` — append **`"ideal_day"` immediately after `"backstory"`**:

```python
"informs": (
    "rubrics",
    "base_resume",
    "strengths",
    "priorities",
    "deal_breakers",
    "backstory",
    "ideal_day",
),
```

2. Update the equality assert that locks the catalog to the same seven-string tuple (including `"ideal_day"` after `"backstory"`).

3. Update the library-home loop immediately below so it also asserts `ideal_day` ⊆ `CANDIDATE_LIBRARY_CONFIG["context_keys"]`:

```python
for _ctx in ("strengths", "priorities", "deal_breakers", "backstory", "ideal_day"):
    assert _ctx in CANDIDATE_LIBRARY_CONFIG["context_keys"], _ctx
```

   Keep the existing `assert "base_resume" in TOPIC_MENU_CONFIG["informs"]` line unchanged.

4. In `TOPIC_MENU_GEN_CONFIG["packet_context_keys"]`, insert **`"ideal_day"` immediately after `"deal_breakers"`** (before `"hopes"`):

```python
"packet_context_keys": (
    "raw_resume",
    "raw_profile",
    "raw_sample",
    "bio_summary",
    "backstory",
    "strengths",
    "priorities",
    "deal_breakers",
    "ideal_day",
    "hopes",
    "interests",
    "concerns",
),
```

5. In `TOPIC_MENU_GEN_CONFIG["patchable_context_keys"]`, insert **`"ideal_day"` in the same place** (immediately after `"deal_breakers"`, before `"hopes"`) so confirm revise and packet visibility stay aligned.

   ⚠️ **Decision:** Placement after `deal_breakers` mirrors AST-1365’s library insertion among gated prose peers and keeps packet/patch tuples identical in relative order. Do not add Ideal Day to `packet_contact_keys` or `packet_name_columns`. Do not invent a separate Ideal Day informs key (`ideal_day_rubric`, etc.) — parent closed catalog uses the library key string.

6. Do **not** edit `src/core/intake.py` or `src/core/candidate.py` — `build_preamble_packet_snapshot`, `_apply_library_patches`, generate’s `INFORMS_CATALOG`, and `validate_topic` already read these config tuples.

7. Do **not** change `TASK_CONFIG` response schemas for `topic_menu_preamble_confirm` / `topic_menu_generate`.

### Stage 2: Estelle seed prompt vocabulary (agent_task)

**Done when:** `topic_menu_preamble_confirm.cache_prompt` lists `ideal_day` among allowed `library_patches` context keys; `topic_menu_generate.cache_prompt` lists `ideal_day` among allowed informs targets; no other `agent_task.json` rows change; JSON still loads.

1. In `data/admin/agent_task.json`, find the object with `"task_key": "topic_menu_preamble_confirm"`.
2. In that row’s `cache_prompt`, extend the ONLY-these-keys clause so `ideal_day` sits with the other gated context keys — insert **`ideal_day` immediately after `deal_breakers`** in the comma-separated list:

   Current fragment ends: `… strengths, priorities, deal_breakers, hopes, interests, concerns.`  
   Replace with: `… strengths, priorities, deal_breakers, ideal_day, hopes, interests, concerns.`

3. Find the object with `"task_key": "topic_menu_generate"`.
4. In that row’s `cache_prompt`, extend the informs line:

   Current: `informs — non-empty list drawn ONLY from: rubrics, base_resume, strengths, priorities, deal_breakers, backstory`  
   Replace with: `informs — non-empty list drawn ONLY from: rubrics, base_resume, strengths, priorities, deal_breakers, backstory, ideal_day`

   ⚠️ **Decision:** Keep the explicit list in the generate prompt (AST-1075 pattern) and add `ideal_day` rather than rewriting the prompt to “ONLY from INFORMS_CATALOG” in this ticket. Runtime still injects `INFORMS_CATALOG` from config; the seed line must not contradict the catalog. Do **not** edit `craft_*` rows (AST-1368).

5. Bump only the edited rows’ `updated_at` to current UTC `YYYY-MM-DD HH:MM:SS` if the file’s existing convention updates that field on prompt edits; do not rotate `task_key_uuid`. Prefer a surgical edit so other rows stay byte-identical aside from unavoidable JSON serializer normalization of the touched objects.

6. Do **not** change `system_prompt` / `user_prompt` / unused cache slots on these rows.

## Estimate

Confirm Chuckles estimate: 2 — agree
