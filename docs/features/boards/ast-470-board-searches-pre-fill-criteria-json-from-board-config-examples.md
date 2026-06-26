# AST-470 — Board Searches: pre-fill criteria JSON from BOARD_CONFIG examples

<!-- linear-archive: AST-470 archived 2026-06-23 -->

## Linear archive (AST-470)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-470/board-searches-pre-fill-criteria-json-from-board-config-examples  
**Status at archive:** Canceled  
**Project:** Astral Boards  
**Assignee:** unassigned  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

**AST-457** Board Searches criteria mode opens with an empty `{}` textarea. Now that spike profiles are promoted into `BOARD_CONFIG` (`a16z`, `heavybit`, `general-catalyst` on `ftr/AST-379` @ `ee372bd7`), the UI should **pre-fill criteria JSON the user can edit** — keyed by Astral-canonical param names we already map in `criteria_param_map`, with **example values that are valid on that board** (from spike `search_keys` option lists where applicable).

Goal: reduce blank-slate JSON editing; user tweaks a known-good starter object instead of inventing keys.

---

## Functional scope

### When to pre-fill

* **New search** modal, **criteria** mode only.
* When the user **selects or changes** `board_key` in the picker.
* **Do not** overwrite criteria when **editing** an existing saved search (keep stored row).
* **Do not** pre-fill on deeplink mode.

### Source of truth

Add an engineer-owned `criteria_example` object on each adopted `BOARD_CONFIG` entry (extend `docs/features/boards/board-config-entry.schema.md`).

* Keys = Astral params from `search_criteria_schema` / `criteria_param_map` (`title_query`, `work_mode`, `max_listing_age`, …).
* Values = human-readable strings valid for that board (prefer first sensible option from spike `search_keys` where enumerated; free-text fields get short placeholder queries).
* Expose via existing `GET /api/boards/<board_key>` detail response (read API already returns full entry).
* **No** runtime read of `debug/spikes/`.

### Initial `criteria_example` values (seed in [config.py](<http://config.py>) with spike promotion)

| `board_key` | Starter JSON |
| -- | -- |
| `a16z` | `{"title_query": "software engineer", "work_mode": "Remote", "max_listing_age": "Past 30 days"}` |
| `heavybit` | `{"title_query": "engineer"}` |
| `general-catalyst` | `{"title_query": "product manager", "work_mode": "San Francisco"}` |

(`work_mode` on General Catalyst maps to the Location text field per `criteria_param_map`.)

### UI behavior (**AST-457** follow-on)

1. On board picker change (new search only): fetch board detail if not cached; set criteria textarea to `JSON.stringify(criteria_example, null, 2)`.
2. If `criteria_example` missing/empty, fall back to `{}` (current behavior).
3. User edits remain local until Save; mode-switch confirm flow unchanged.
4. Optional hint under textarea: “Example criteria for this board — edit before saving.”

---

## Acceptance criteria

1. Each adopted board in `BOARD_CONFIG` has a documented `criteria_example` matching its `search_criteria_schema` keys.
2. `GET /api/boards/<board_key>` includes `criteria_example` in the detail payload.
3. **New** Board Search + criteria mode: changing board updates textarea to that board’s example (pretty-printed JSON).
4. **Edit** existing search: opening modal keeps saved criteria unchanged.
5. Deeplink mode unaffected.
6. Component test: board switch on new-search form updates textarea content.

---

## Boundaries

* Not craft-task generation (`POST …/generate/craft_board_search_criteria`) — static config examples only.
* Not interactive Playwright widget driving (**AST-418** follow-on).
* Not adding new Astral param names beyond what each board’s schema already defines.
* Not pre-filling deeplink URL field.

---

## Dependencies

* **AST-457** — Board Searches UI (User Testing).
* **AST-415** — board detail read API.
* **BOARD_CONFIG** spike promotion (local `dev` `6134597a`, `ftr/AST-379` `ee372bd7`).

---

## Open questions

1. Should `GET /api/boards` list include `criteria_example` (avoid extra detail fetch), or is detail-on-select enough?
2. On board change when textarea was user-edited, confirm before replacing (same pattern as mode switch)?

— Chuckles

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
