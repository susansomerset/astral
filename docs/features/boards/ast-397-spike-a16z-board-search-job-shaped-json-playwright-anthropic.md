# AST-397 — Spike: a16z board search → job-shaped JSON (Playwright + Anthropic)

<!-- linear-archive: AST-397 archived 2026-06-15 -->

## Linear archive (AST-397)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-397/spike-a16z-board-search-job-shaped-json-playwright-anthropic  
**Status at archive:** Done  
**Project:** Astral Boards  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Summary

**Astral Boards** direction: we will support **only boards we explicitly adopt**, each with a maintainable Playwright profile (navigation, cookies, inputs, result parsing). **a16z** is a **candidate** board, not yet adopted.

This issue is a **spike**, not a shippable feature. Work is **gated in phases**: each phase produces a **small, reviewable artifact**; **Susan (or delegate) approves the artifact before the next phase starts.**

**Prior child issues** [AST-398](https://linear.app/astralcareermatch/issue/AST-398) / [AST-399](https://linear.app/astralcareermatch/issue/AST-399) **are canceled**.

**Phase children:** AST-400 (Phase 1), AST-401 (Phase 2), AST-402 (Phase 3), [AST-414](https://linear.app/astralcareermatch/issue/AST-414) (Phase 4).

---

## Longer-term north star (not gated in Phases 1–3)

Eventually: parameterized saved-search → structured rows mappable to `job` / hiring `company`. **Do not start LLM/json shaping until Phases 1–3 are green** and we agree the board is worth a profile.

---

## Example parameters (literals for Phase 3 automation)

| Parameter | Example value |
| -- | -- |
| Board entry URL | `https://jobs.a16z.com/jobs` |
| `title_query` | `Python Engineer in Healthcare` |
| `work_mode` | `Remote` |
| `max_listing_age` | `14d` |

---

## Phase 1 — Reach the board, survive the real world

**Goal:** Playwright opens the **correct** jobs URL, dismisses cookie/consent if present, lands on a human-sane screen.

**Deliverable:** visible-text capture + notes. **Local:** `debug/spikes/AST-400/` (§3.6).

**Gate:** Susan. **Child:** AST-400.

---

## Phase 2 — Know the machine before we drive it

**Goal:** Inventory **all input widgets** and **capture real option lists** (filter trays + inline menus).

**Deliverable:** `widgets.json` with `controls[]`, `block_tray_option_lists`, `inline_tray_option_lists` — not example parameter names only.

**Gate:** Susan maps list to UI. **Child:** AST-401.

---

## Phase 3 — One honest search, visible results + parse instructions

**Goal:** One parameterized search using Phase 2 mapping.

**Deliverables:** results visible text + `board_results_parse_instructions.json`. **Local:** `debug/spikes/AST-402/`.

**Gate:** Susan. **Child:** AST-402.

---

## Phase 4 — `board_profile_draft.json` (canonical for all board spikes)

**Goal:** Assemble a **local draft profile** from Phases 1–3 — **real** `page_controls` **and tray option lists**, plus `parse_instructions` and automation bridge (`criteria_param_map`).

**Deliverable:** `debug/spikes/AST-414/board_profile_draft.json` — attach on [AST-414](https://linear.app/astralcareermatch/issue/AST-414). **No** `BOARD_CONFIG` / `config.py` in spike. Promotion → **AST-415** after adoption.

**Canonical schema:** AST-414 description + Linear attachments (also the template for [AST-410](https://linear.app/astralcareermatch/issue/AST-410)–[413](<https://linear.app/astralcareermatch/issue/AST-413>)).

**Gate:** Susan reviews attachment.

---

## Non-goals (this spike parent)

* No SQLite, dispatch, Anthropic ingest, or production **BOARD_CONFIG** commits in spike work.

---

## Resolved

* Entry URL is always the known jobs index (`https://jobs.a16z.com/jobs`).
* Headless default; `--headed` for local repro.

### Comments

#### chuckles — 2026-05-18T19:47:35.223Z
## finish-up — Chuckles (spike cleanup)

Susan requested **finish-up** for **AST-397**.

### Git
- `origin/ftr/AST-397-spike-a16z-board-search-job-shaped` was **already contained in** `origin/dev` (merge → *Already up to date*). **No push** to `origin/dev`.
- Deleted on **origin**:
  - `ftr/AST-397-spike-a16z-board-search-job-shaped`
  - `sub/AST-397/AST-400-spike-a16z-board-search-job-shaped`
  - `sub/AST-397/AST-401-spike-a16z-board-search-job-shaped`
  - `sub/AST-397/AST-402-spike-a16z-board-search-job-shaped`
  - `sub/AST-397/AST-414-spike-a16z-board-profile-phase-4`

### Not landed on dev (by design)
Child branches still had **docs-only** resolution commits (400–402) and **debug/spikes** work on **414** — spike non-goals say no product / BOARD_CONFIG commits. Artifacts remain on engineer branches until needed; say if you want any of that cherry-picked to `dev`.

### Linear
Parent + phase children were already **Done** — left statuses unchanged (did not move to PR Ready).

`origin/dev` tip: `65862be6`

— Chuckles

#### chuckles — 2026-05-17T14:51:42.387Z
**Phase 4 added to spike pattern** (2026-05-17, per Susan)

After Phase 3 gate: promote artifacts → committed **`BOARD_CONFIG["a16z"]`** + **`TASK_CONFIG["craft_board_search_a16z"]`** in `config.py` (no SQLite, no `board` table).

* Child: [AST-414](https://linear.app/astralcareermatch/issue/AST-414)
* Docs: `docs/features/boards/board-spike-phases.md`, `board-config-entry.schema.md`

Phases 1–3 (AST-400–402) are Done; Phase 4 is the config promotion step before production `board_search` / gazer work (AST-403+).

— Chuckles

#### chuckles — 2026-05-15T21:01:35.155Z
## Dispatch — Chuckles

Dispatched **3** child tickets from the phased **AST-397** definition (one engineer, sequential **blockedBy** chain per skill: next phase waits until prior reaches **Review Posted**).

| Ticket | Title | Assigned to | Blocked by |
|--------|-------|-------------|------------|
| [AST-400](https://linear.app/astralcareermatch/issue/AST-400/spike-a16z-board-search-job-shaped-json-playwright-anthropic-phase-1) | Phase 1 — reach board, first-screen visible text | Hedy | — |
| [AST-401](https://linear.app/astralcareermatch/issue/AST-401/spike-a16z-board-search-job-shaped-json-playwright-anthropic-phase-2) | Phase 2 — input widget inventory | Hedy | AST-400 |
| [AST-402](https://linear.app/astralcareermatch/issue/AST-402/spike-a16z-board-search-job-shaped-json-playwright-anthropic-phase-3) | Phase 3 — parameterized search, visible results text | Hedy | AST-401 |

**Assignment rationale:**
- **Hedy:** All three phases are Playwright / board reconnaissance and **`scripts/spikes/`**-style work — same domain as gazer/roster/playwright.
- **Ada / Katherine:** Not assigned — no agent runtime or React scope in Phases 1–3.

Canceled siblings **AST-398** / **AST-399** stay under the parent for history; active work is **400 → 401 → 402**.

Susan can override any assignment by reassigning the child ticket directly. Parent **In Progress**; assignee **Susan** (Chuckles is never assignee on tickets). I'll roll up to **Testing** when all **active** children reach **Review Posted**.

— Chuckles

#### chuckles — 2026-05-15T20:52:35.503Z
## Spike reset — Chuckles

- **Canceled:** [AST-398](https://linear.app/astralcareermatch/issue/AST-398/spike-a16z-board-search-job-shaped-json-playwright-anthropic), [AST-399](https://linear.app/astralcareermatch/issue/AST-399/spike-a16z-board-search-job-shaped-json-playwright-anthropic-anthropic) (superseded by phased approach on this parent).
- **Updated:** this issue’s **Description** — **Phase 1** visible-text only on first screen (`https://jobs.a16z.com/jobs`), **Phase 2** input-widget inventory for human mapping, **Phase 3** parameterized search + visible results text; **gates** between phases.
- **State:** **Backlog**, assignee **@susan** for description pass — when you’re happy, move to **Todo** and we can **dispatch** fresh small tickets if you still want that pattern.

— Chuckles

#### chuckles — 2026-05-15T18:17:07.270Z
## Dispatch — Chuckles

Dispatched **2** child tickets from the approved definition.

| Ticket | Title | Assigned to | Blocked by |
|--------|-------|-------------|------------|
| [AST-398](https://linear.app/astralcareermatch/issue/AST-398/spike-a16z-board-search-job-shaped-json-playwright-anthropic) | Playwright capture to raw findings | Hedy | — |
| [AST-399](https://linear.app/astralcareermatch/issue/AST-399/spike-a16z-board-search-job-shaped-json-playwright-anthropic-anthropic) | Anthropic normalization to job/company JSON | Ada | AST-398 |

**Assignment rationale:**
- **Hedy:** Board scrape + pagination + job-list-adjacent Playwright work aligns with tracker/gazer/roster flows and `src/external/playwright.py` usage from core.
- **Ada:** Anthropic normalization, JSON contract, and prompt/model documentation sit squarely in agent-runtime / external API ownership.
- **Katherine:** Not assigned on this dispatch (no React/API UI scope).

Susan can override any assignment by reassigning the child ticket directly. Parent moves to **In Progress**. I'll roll up to **Testing** when all children reach **Review Posted**.

— Chuckles

#### susan — 2026-05-15T17:19:08.402Z
NONE of the output of this spike should live in the src directory.  For discovery, let's put the work under scripts/spikes/.  These scripts can import from anywhere, no limit on that point.  The results should be a json text file attached to this ticket of the output, once we are confident that the json is valid.

---

_Implementation detail may live in git history on `origin/dev`._
