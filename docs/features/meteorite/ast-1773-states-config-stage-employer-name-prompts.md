# AST-1773 — States, config, stage employer_name prompts

**Linear:** [AST-1773](https://linear.app/astralcareermatch/issue/AST-1773/states-config-stage-employer-name-prompts-meteorite-state-check-unique)  
**Parent:** [AST-1762](https://linear.app/astralcareermatch/issue/AST-1762/meteorite-state-check-unique-before-landed) — Meteorite state CHECK_UNIQUE before LANDED  
**Publish ref:** `sub/AST-1762/AST-1773-states-config-stage-employer-name-prompts`

Owns the uniqueness-gate **registry and catalogs** for AST-1762: add `CHECK_UNIQUE` / `DUPLICATE` to `METEORITE_STATES`, retarget stage/scrape success destinations in `METEORITE_INGRESS_DISPATCH_CONFIG` to `CHECK_UNIQUE` (land stays `READY`), confirm optional `employer_name` on `stage_meteorite` (no `company_name`), teach stage prompts never to invent employer names, add Ruth duplicate-review `TASK_CONFIG` + companion config + `agent_task` row, and seed `check_unique_meteorite` dispatch. Does **not** implement SQL matching, Ruth invoke, or stage/scrape/land runner rewrites (siblings **AST-1774** / **AST-1775**).

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/utils/config.py` — **modified** — add `CHECK_UNIQUE` and `DUPLICATE` to `METEORITE_STATES`; retarget stage/scrape success destinations and ingress dispatch config; add `TASK_CONFIG` + config block for Ruth duplicate-review; seed/assert `check_unique_meteorite`.
- `src/utils/config.py` — **modified** `METEORITE_STATES` — new `CHECK_UNIQUE` (priors from stage/scrape landable-success writers: `NEW`, `SCRAPE_LINK` as applicable) and terminal `DUPLICATE`; update assert closed set.
- `src/utils/config.py` — **modified** `METEORITE_INGRESS_DISPATCH_CONFIG` / scrape success map — success targets become `CHECK_UNIQUE`; add check-unique task key + trigger `CHECK_UNIQUE`; land trigger remains `READY`.
- `src/utils/config.py` — **modified** `TASK_CONFIG["stage_meteorite"]` — confirm optional `employer_name` (`required: False`); no `company_name`.
- `src/utils/config.py` — **new** Ruth duplicate-review `TASK_CONFIG` + config block.
- `src/utils/config.py` — **modified** `SEED_CONFIG` + monitoring format strings.
- `data/admin/agent_task.json` — **modified** `stage_meteorite` prompts for optional `employer_name`; **new** Ruth duplicate-review row.
- `data/admin/dispatch_task.json` — **new** `check_unique_meteorite` row.

All Files Changed / Stages stay inside that set.

**Out of scope (siblings):**

- `src/core/meteorite.py` stage/scrape → `CHECK_UNIQUE` writers, `run_check_unique_meteorite` SQL + transitions — **AST-1774** (child #2)
- `src/core/meteorite.py` Ruth duplicate-review invoke + `DUPLICATE`/`READY` outcome map — **AST-1775** (child #3)
- `src/core/dispatcher.py` routing for `check_unique_meteorite` — **AST-1774**
- `apply_paste` / other direct `READY` writers outside stage/scrape landable success
- Changing `STAGE_METEORITE_CONFIG["outcomes"]` (must remain exactly six literals)
- Editing `docs/uat-fixtures/**` twins — Betty owns at qa-child if needed

**Depends on:** **AST-1753** Done (stage_meteorite row is the live classify catalog). No open parent blocker.

**AC partition (this ticket):** Parent AC1, AC2, AC4 (row-state-only / six outcomes), AC9 (land gate config), AC10 (registry closed set). AC3 / AC5–AC8 → siblings.

**Canon Scope (read at plan):**

- `astral.dispatch.entity-state-bound` — full (new dispatch key’s `trigger_state` must be a real `METEORITE_STATES` member; helpers that resolve trigger/entity for ingress keys must include the new hop).
- `astral.entity.required-metadata` — id-only (no new entity table / metadata columns in this ticket).
- `stat.logging.debug` — id-only (no product logging code in this ticket’s files; noisy match/peer detail stays a sibling concern).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `CHECK_UNIQUE` / `DUPLICATE` to `METEORITE_STATES` + closed-set assert; retarget ingress success → `CHECK_UNIQUE`; add check-unique task/trigger keys; confirm `employer_name` optional + no `company_name`; add `REVIEW_DUPLICATE_METEORITE_CONFIG` + `TASK_CONFIG["review_duplicate_meteorite"]`; extend `SEED_CONFIG` ingress paste + retire-null-pool list; wire dispatch trigger/entity helpers for the new key | utils |
| `data/admin/agent_task.json` | Append `## EMPLOYER NAME (optional)` to `stage_meteorite` prompts (never invent); add live `review_duplicate_meteorite` Ruth row lockstep with `TASK_CONFIG` | catalog |
| `data/admin/dispatch_task.json` | Add `check_unique_meteorite` row matching sibling ingress shape (`trigger_state=CHECK_UNIQUE`) | catalog |

## Stage 1: `METEORITE_STATES` + ingress dispatch retarget + helpers

**Done when:** `set(METEORITE_STATES)` includes `CHECK_UNIQUE` and `DUPLICATE`; `import src.utils.config` passes asserts; scrape `"ok"` maps to `CHECK_UNIQUE`; land trigger remains `READY`; `get_dispatch_trigger_state("check_unique_meteorite")` (or whatever the existing helper is named — `_dispatch_trigger_state_for_task_key`) returns `CHECK_UNIQUE` and entity type `meteorite`; `STAGE_METEORITE_CONFIG["outcomes"]` still has length 6; `python3 -m py_compile src/utils/config.py` succeeds.

1. In `src/utils/config.py`, update `METEORITE_STATES`:

   - Add `"CHECK_UNIQUE": {"prior_states": ["NEW", "SCRAPE_LINK"]}` (stage/scrape landable-success writers — sibling #2 will write these).
   - Add `"DUPLICATE": {"prior_states": ["CHECK_UNIQUE"]}` — terminal hold reached only from the uniqueness hop (not `None`; unlike insert-legal `NOT_A_JOB` / `NEW_EMAIL_ERROR`, rows arrive via transition from `CHECK_UNIQUE`).
   - Change `"READY"` `prior_states` from `["NEW", "SCRAPE_LINK", "BOT_BLOCKED"]` to `["CHECK_UNIQUE", "BOT_BLOCKED"]` — uniqueness hop promotes to landable; Estelle paste recovery from `BOT_BLOCKED` stays.
   - Update the closed-set assert to include `"CHECK_UNIQUE"` and `"DUPLICATE"`.

2. In `METEORITE_INGRESS_DISPATCH_CONFIG`:

   - Keep `stage_task_key` / `scrape_task_key` / `land_task_key` and their existing trigger states (`NEW` / `SCRAPE_LINK` / `READY`).
   - Add `"check_unique_task_key": "check_unique_meteorite"`.
   - Add `"check_unique_trigger_state": "CHECK_UNIQUE"`.
   - Change `scrape_page_status_states["ok"]` from `"READY"` to `"CHECK_UNIQUE"`.
   - Update the distinct-keys assert to require **four** unique task-key strings (stage/scrape/land/check_unique).
   - Extend the trigger-state loop / asserts so `check_unique_trigger_state` is in `METEORITE_STATES`.
   - Update the scrape map values assert so allowed destinations include `CHECK_UNIQUE` (still allow `BOT_BLOCKED` / `SCRAPE_ERROR` / `LINK_EXPIRED` as today).

3. In `_dispatch_trigger_state_for_task_key` and `_dispatch_entity_type_for_task_key`, add branches for `METEORITE_INGRESS_DISPATCH_CONFIG["check_unique_task_key"]` parallel to stage/scrape/land (trigger → `check_unique_trigger_state`; entity → `"meteorite"`).

4. Confirm (assert, do not change outcomes): `len(STAGE_METEORITE_CONFIG["outcomes"]) == 6` remains; do **not** add `CHECK_UNIQUE` or `DUPLICATE` to Ruth classify outcomes.

5. Confirm `TASK_CONFIG["stage_meteorite"]["response_schema"]["jobs"]["items_schema"]`:

   - `"employer_name": {"type": "str", "required": False}` already present — keep as-is.
   - Assert `"company_name" not in` that `items_schema`.
   - Add a pin assert: `TASK_CONFIG["stage_meteorite"]["response_schema"]["jobs"]["items_schema"]["employer_name"]["required"] is False`.

⚠️ **Decision — READY priors:** Drop `NEW` / `SCRAPE_LINK` from `READY.prior_states` in this ticket (registry end-state). Sibling #2 retargets the live writers; priors are not runtime-enforced on `update_meteorite` today. Keeping stale priors would document a graph the epic is removing.

⚠️ **Decision — DUPLICATE priors:** Use `["CHECK_UNIQUE"]` (transition graph), not `None`. Parent allows either; `None` is reserved here for insert-legal terminals that are not dispatch destinations (`NOT_A_JOB`, `NEW_EMAIL_ERROR`).

**AC check after this stage:** Parent AC4 (six outcomes untouched), AC9 (`land_trigger_state` still `READY`), AC10 (closed set).

## Stage 2: Ruth duplicate-review config + SEED_CONFIG

**Done when:** `REVIEW_DUPLICATE_METEORITE_CONFIG` and `TASK_CONFIG["review_duplicate_meteorite"]` exist with locked closed outcomes; `SEED_CONFIG["dispatch_task-meteorite-ingress"]` includes a per-candidate `check_unique_meteorite` / `CHECK_UNIQUE` INSERT matching land sibling shape; retire-null-pool DELETE list includes `check_unique_meteorite`; `import src.utils.config` still passes; `python3 -m py_compile src/utils/config.py` succeeds.

1. Immediately after `STAGE_METEORITE_CONFIG` asserts (or beside other meteorite companion blocks), insert:

```python
# AST-1773: Ruth duplicate-review after SQL/null-peer detection (invoke owned by AST-1775).
REVIEW_DUPLICATE_METEORITE_CONFIG = {
    "task_key": "review_duplicate_meteorite",
    "outcomes": ("duplicate", "not_duplicate"),
    "peer_id_response_key": "peer_meteorite_id",
}
```

   Assert: `task_key` non-empty; `len(outcomes) == 2`; outcomes unique; `peer_id_response_key == "peer_meteorite_id"`.

2. Add `TASK_CONFIG["review_duplicate_meteorite"]` near `TASK_CONFIG["stage_meteorite"]` (Ruth family):

```python
"review_duplicate_meteorite": {
    "response_format": "json",
    "output_type": "fields",
    "scored": False,
    "response_schema": {
        "outcome": {"type": "str", "required": True},
        "peer_meteorite_id": {"type": "str", "required": False},
    },
    "context_format": "review_duplicate_meteorite_{index}",
    "entity_type": None,
    "requires_candidate_key": True,
    "trigger_state": None,
    "agent_task": "review_duplicate_meteorite",
},
```

   After `REVIEW_DUPLICATE_METEORITE_CONFIG` is defined, lockstep:

```python
TASK_CONFIG["review_duplicate_meteorite"]["response_schema"]["outcome"]["enum"] = list(
    REVIEW_DUPLICATE_METEORITE_CONFIG["outcomes"]
)
assert TASK_CONFIG["review_duplicate_meteorite"]["agent_task"] == REVIEW_DUPLICATE_METEORITE_CONFIG["task_key"]
assert (
    REVIEW_DUPLICATE_METEORITE_CONFIG["peer_id_response_key"]
    in TASK_CONFIG["review_duplicate_meteorite"]["response_schema"]
)
```

3. Extend `SEED_CONFIG["dispatch_task-meteorite-ingress"]` with a fifth INSERT twin of `land_meteorite`, substituting:

   - `task_key` = `check_unique_meteorite` (from `METEORITE_INGRESS_DISPATCH_CONFIG["check_unique_task_key"]` literal in the SQL string, same style as existing siblings)
   - `entity_type` = `'meteorite'`
   - `trigger_state` = `'CHECK_UNIQUE'`
   - same `sort_by` / `batch_call_mode` / `freq_hrs` / `min_count` / `batch_size` / `auto_mode` / `score_floor` as `land_meteorite`

4. Extend `SEED_CONFIG["dispatch_task-meteorite-ingress-retire-null-pool"]` task_key `IN (...)` list to include `'check_unique_meteorite'`.

5. **Monitoring format strings (ticket phrase):** `METEORITE_MONITORING_CONFIG` today only carries `outcome_already_ingested` (AST-1560 row-transition format keys were retired; live transitions use `_meteorite_state_info`). Do **not** reintroduce format-string keys here. SEED + closed-set / ingress asserts are the monitoring-adjacent deliverable for this ticket; sibling runners keep using `_meteorite_state_info` / `logger.debug` per their citations.

⚠️ **Decision — task_key name:** `review_duplicate_meteorite` (Ruth agent_task + `TASK_CONFIG`) vs dispatch runner `check_unique_meteorite`. Keeps classify/review catalog keys distinct from the SQL hop key, matching `stage_meteorite` (Ruth) vs transition runners pattern on the ingress spine.

⚠️ **Decision — outcomes vocabulary:** snake_case `duplicate` / `not_duplicate` (not Title Case) to match `stage_meteorite` outcome style. Peer id is optional in schema; prompts (Stage 3) require it when outcome is `duplicate`.

## Stage 3: `agent_task.json` + `dispatch_task.json`

**Done when:** `stage_meteorite` prompts teach optional `employer_name` and forbid guessing; no `$RESPONSE_SCHEMA` dump; no `company_name` instruction; new `review_duplicate_meteorite` catalog row exists lockstep with Stage 2; `dispatch_task.json` has `check_unique_meteorite` with `trigger_state=CHECK_UNIQUE`; both JSON files parse; config import still green.

1. In `data/admin/agent_task.json`, locate `"task_key": "stage_meteorite"`. **Append** to `cache_prompt` after the existing `## JOB TITLE (optional)` block (do not rewrite OUTCOMES / HEADER / ELECTRONIC CONTACT / JOB TITLE):

```
## EMPLOYER NAME (optional)

For every jobs item you return on landable outcomes (single_jd_no_link, single_jd_with_more, multi_jd_inline, link_list), include optional employer_name when you can tell which employer the candidate would work for.

Use an employer name that is explicit in the CONTENT (JD body, recruiter letterhead, signature block, or clear subject). If the employer is unknown or only implied, omit employer_name or return an empty string.

Never invent employer names. Never guess from vague branding or the recruiter's agency name when the hiring employer is unclear. Do not emit a company_name field.
```

2. Update the same row’s **`user_prompt`** to (replace the whole string):

```
Read CONTENT. Return JSON with outcome (exactly one closed outcome literal) and jobs (scrap fields per outcome; empty list for not_job_content and not_original_posting). For single_jd_no_link and multi_jd_inline, each jobs item must include from_email, to_email, and sent_at (bare emails; peel inner headers on forwards). Include optional electronic_contact per item (prefer metadata; never invent addresses). Include optional job_title per landable jobs item when the role name is known (prefer subject when it names the role; omit when unknown; never invent). Include optional employer_name per landable jobs item when the hiring employer is explicit in CONTENT (omit when unknown; never invent; never emit company_name). Do not emit grade vectors.
```

3. Leave `nocache_prompt`, `system_prompt`, and `cache_prompt_b`/`_c`/`_d` unchanged. Do **not** insert `$RESPONSE_SCHEMA` into any `stage_meteorite` prompt field.

4. Append a **new** agent_task object for Ruth duplicate-review:

   | Field | Value |
   |-------|--------|
   | `task_key` | `review_duplicate_meteorite` |
   | `task_name` | `review_duplicate_meteorite` |
   | `agent_id` | `college_intern_ruth` |
   | `task_group_name` | `Land Meteorite` |
   | `task_group_order` | `4200` |
   | `task_seq` | `5` (after `land_meteorite` seq 4) |
   | `current` | `1` |
   | `task_key_uuid` | new random UUID4 string |
   | `run_next` | empty / same as sibling Ruth rows |
   | `updated_at` | omit or match peer row style in file |

   **`cache_prompt`** (literal):

```
## INSTRUCTIONS

You compare one CHECK_UNIQUE meteorite against one or more LANDED peer meteorites for the same candidate.

Return JSON with:
- outcome: exactly one of duplicate, not_duplicate
- peer_meteorite_id: when outcome is duplicate, the LANDED meteorite id this row duplicates; omit or empty when not_duplicate

Treat two postings as duplicate when they describe the same underlying job for the candidate (same role at the same employer), even if recruiters or wrappers differ. Prefer not_duplicate when content is insufficient to decide.

Never invent peer ids. Never invent outcome strings outside the closed set.
```

   **`user_prompt`** (literal):

```
Read CONTENT (CHECK_UNIQUE row plus LANDED peers). Return JSON with outcome (duplicate or not_duplicate) and peer_meteorite_id when duplicate. Do not emit grade vectors.
```

   Leave other prompt fields empty like `stage_meteorite`.

5. In `data/admin/dispatch_task.json`, append a row matching the `land_meteorite` sibling shape, with:

   - `task_key`: `check_unique_meteorite`
   - `trigger_state`: `CHECK_UNIQUE`
   - `candidate_id`: `null` (same as current sibling rows in this file)
   - `entity_type`: `null` (same as current sibling rows in this file — live per-candidate seeds live in `SEED_CONFIG`)
   - `sort_by`: `updated_at`
   - `batch_call_mode`: `0`
   - `freq_hrs`: `0.1`
   - `min_count`: `1`
   - `batch_size`: `10`
   - `auto_mode`: `0`
   - `score_floor`: `null`

6. Verify from the epic worktree:

```bash
python3 - <<'PY'
import json
from pathlib import Path
from src.utils.config import (
    METEORITE_STATES,
    METEORITE_INGRESS_DISPATCH_CONFIG,
    STAGE_METEORITE_CONFIG,
    TASK_CONFIG,
    REVIEW_DUPLICATE_METEORITE_CONFIG,
    SEED_CONFIG,
    _dispatch_trigger_state_for_task_key,
    _dispatch_entity_type_for_task_key,
)
assert "CHECK_UNIQUE" in METEORITE_STATES and "DUPLICATE" in METEORITE_STATES
assert METEORITE_INGRESS_DISPATCH_CONFIG["land_trigger_state"] == "READY"
assert METEORITE_INGRESS_DISPATCH_CONFIG["scrape_page_status_states"]["ok"] == "CHECK_UNIQUE"
assert METEORITE_INGRESS_DISPATCH_CONFIG["check_unique_trigger_state"] == "CHECK_UNIQUE"
assert len(STAGE_METEORITE_CONFIG["outcomes"]) == 6
assert TASK_CONFIG["stage_meteorite"]["response_schema"]["jobs"]["items_schema"]["employer_name"]["required"] is False
assert "company_name" not in TASK_CONFIG["stage_meteorite"]["response_schema"]["jobs"]["items_schema"]
assert set(REVIEW_DUPLICATE_METEORITE_CONFIG["outcomes"]) == {"duplicate", "not_duplicate"}
assert _dispatch_trigger_state_for_task_key("check_unique_meteorite") == "CHECK_UNIQUE"
assert _dispatch_entity_type_for_task_key("check_unique_meteorite") == "meteorite"
seed = "\n".join(SEED_CONFIG["dispatch_task-meteorite-ingress"])
assert "check_unique_meteorite" in seed and "CHECK_UNIQUE" in seed
agents = json.loads(Path("data/admin/agent_task.json").read_text())
stage = next(r for r in agents if r.get("task_key") == "stage_meteorite")
for k in ("cache_prompt", "user_prompt"):
    t = stage.get(k) or ""
    assert "employer_name" in t and "never invent" in t.lower()
    assert "$RESPONSE_SCHEMA" not in t
    assert "company_name" in t  # forbid instruction mentions the wrong key
assert any(r.get("task_key") == "review_duplicate_meteorite" for r in agents)
disp = json.loads(Path("data/admin/dispatch_task.json").read_text())
row = next(r for r in disp if r.get("task_key") == "check_unique_meteorite")
assert row.get("trigger_state") == "CHECK_UNIQUE"
print("AST-1773 config+catalog OK")
PY
python3 -m py_compile src/utils/config.py
```

⚠️ **Decision — prompt pattern:** Mirror AST-1755’s `## JOB TITLE (optional)` append style for employer_name so outcome / breadcrumb / electronic-contact sections stay untouched.

⚠️ **Decision — dispatch_task.json pool:** Match current sibling rows (`candidate_id` null in the JSON file). Per-candidate claim rows are the `SEED_CONFIG` paste path (post-remediation). Do not invent a divergent global-pool SEED; parent “global pool like siblings” means “same shape as stage/scrape/land siblings as they exist on HEAD.”

## Estimate

Confirm Chuckles estimate: 3 — agree
