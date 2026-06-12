# Board config entry schema (normative)

**Owner:** production boards track (**AST-415+**). Spike drafts use **schema v3** on Linear (**AST-414**); this doc is the **promoted** shape for `BOARD_CONFIG` in `src/utils/config.py`.

## `BOARD_CONFIG` top-level

- Type: `dict[str, BoardEntry]`
- Keys: stable **`board_key`** (lowercase slug, e.g. `a16z`, `heavybit`) — same string as spike `board_key`.

## `BoardEntry` fields

| Field | Type | Required | Notes |
|-------|------|----------|--------|
| `label` | string | yes | Human label (UI / API) |
| `entry_url` | string | yes | Board landing URL |
| `adopted` | bool | yes | `true` = production-runnable; exposed by read API |
| `parse_instructions` | object | yes | Verbatim Phase-3-style JSON (listing card parse contract) |
| `search_criteria_schema` | object | yes | JSON Schema for **Astral-canonical** search params (API/query), not raw page labels |
| `criteria_param_map` | object | yes | Maps Astral param names → `{widget_id, …}` for gaze/automation |
| `craft_task_key` | string | yes | `TASK_CONFIG` key for board rubric craft (e.g. `craft_joblist_rubric`) — may be shared across boards until per-board craft lands |
| `scrape_mode` | string | yes | `"interactive"` \| `"deep_link"` |
| `widgets` | object | when adopted | Optional at first ship: nested `w-*` widget defs (from spike v3); may be omitted until ingest needs them |
| `search_keys` | object | optional | Page-label-keyed spike inventory; **not** returned by public list API unless needed |

## `adopted: false`

- Retained in `BOARD_CONFIG` for research/spike promotion.
- **Must not** appear in `GET /api/boards` list or detail for operators.

## Promotion from spike v3

1. Susan approves spike `board_profile_draft.json` on Linear (**AST-414** pattern).
2. Engineer transcribes into one `BOARD_CONFIG[board_key]` entry (no runtime read of `debug/spikes/`).
3. Build `search_criteria_schema` + `criteria_param_map` from spike `search_keys` (Astral names are **engineer-owned**, not copied from page labels).

## Example (minimal adopted entry — illustrative)

```json
{
  "a16z": {
    "label": "a16z Jobs",
    "entry_url": "https://jobs.a16z.com/jobs",
    "adopted": true,
    "parse_instructions": {},
    "search_criteria_schema": {"type": "object", "properties": {}},
    "criteria_param_map": {},
    "craft_task_key": "craft_joblist_rubric",
    "scrape_mode": "interactive"
  }
}
```
