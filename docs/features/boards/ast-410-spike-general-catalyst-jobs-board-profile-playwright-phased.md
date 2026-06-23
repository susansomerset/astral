# AST-410 — Spike: General Catalyst Jobs board profile (Playwright, phased)

<!-- linear-archive: AST-410 archived 2026-06-15 -->

## Linear archive (AST-410)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-410/spike-general-catalyst-jobs-board-profile-playwright-phased  
**Status at archive:** Done  
**Project:** Astral Boards  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-413; related: AST-397; related: AST-379

### Description

## Purpose

**General Catalyst Jobs** (`https://jobs.generalcatalyst.com/jobs`) is a candidate board channel under the [AST-379](https://linear.app/astralcareermatch/issue/AST-379) boards epic. Before Astral can adopt it for candidate saved searches, we need a **Playwright R&D spike** that proves we can reach the board, inventory its interactive controls with real on-page labels and option lists, run one honest parameterized search, and assemble a **board profile draft** Susan can review.

This parent ticket is **research only** — not production ingest, not `BOARD_CONFIG`, not gazer. It follows the same gated four-phase pattern used for [AST-397](https://linear.app/astralcareermatch/issue/AST-397) / [AST-414](https://linear.app/astralcareermatch/issue/AST-414) (a16z) and [AST-413](https://linear.app/astralcareermatch/issue/AST-413) (Heavybit). Susan approves each phase before the next begins.

**Board key:** `general-catalyst`

**Phase children (dispatched 2026-05-17):** [AST-430](https://linear.app/astralcareermatch/issue/AST-430) Phase 1 · [AST-431](https://linear.app/astralcareermatch/issue/AST-431) Phase 2 · [AST-432](https://linear.app/astralcareermatch/issue/AST-432) Phase 3 · [AST-433](https://linear.app/astralcareermatch/issue/AST-433) Phase 4.

**Spike paths** (§3.6): `debug/spikes/<phase-child-id>/`; **Linear attachments** for handoff.

---

## Functional scope

When this spike is complete, the team has:

1. **Reach evidence** — Playwright loads the canonical URL; consent/bot issues documented in Phase 1.
2. **Widget inventory** — Real on-page labels and tray/inline option lists.
3. **One search + parse spec** — Parameters **discerned from discovered widgets** (not a fixed filter template per board).
4. **Profile draft JSON** — schema v3 per [AST-414](https://linear.app/astralcareermatch/issue/AST-414) attachment.

---

## Boundaries

* No production adoption, `BOARD_CONFIG`, or gazer in this spike.
* **AST-415+** only after Susan adopts and **all** board spikes (410–412) complete.
* No committed spike deliverables in git under `docs/features/`.

---

## Acceptance criteria

1. Parent **Done** when AST-430–433 are **Done** and Phase 4 attaches schema v3 `board_profile_draft.json` for `general-catalyst` / `https://jobs.generalcatalyst.com/jobs`.
   2.–6. Per-phase gates per original definition (Susan confirms each phase).

---

## Dependencies

[AST-414](https://linear.app/astralcareermatch/issue/AST-414) **Done** (schema v3). [AST-379](https://linear.app/astralcareermatch/issue/AST-379) epic context.

---

## Resolved decisions (Susan)

1. **Phase 3 parameters:** Discern from page widgets (Heavybit pattern) — do not impose example filters on every board.
2. **Consent/bot:** Phase 1 documents; Susan decides if blocked.
3. **Adoption:** Hold **AST-415** until all board spikes complete.

### Comments

#### chuckles — 2026-05-18T19:49:12.914Z
## Landed on origin/dev — Chuckles

**Note:** `prep-uat` had not rolled child branches into `ftr/` (parent `ftr` was already at `dev`; phase work lived only on `sub/AST-410/*`). Cherry-picked phase commits onto `dev`, then merged `ftr` (already up to date).

- Cherry-picked **AST-430 → 433** spike scripts into `scripts/spikes/general_catalyst_board_phase*.py` → pushed `origin/dev`
- Deleted `origin/ftr/AST-410-spike-general-catalyst-jobs-board-profile-playwright`
- Deleted all four `sub/AST-410/*` branches
- Children moved to **PR Ready** (assignee unchanged: Hedy): AST-430, AST-431, AST-432, AST-433
- Parent **PR Ready**

Push commit: `f842e065`

— Chuckles

#### chuckles — 2026-05-17T22:49:11.806Z
## Dispatch — Chuckles

Dispatched **4** phase child tickets from the approved definition.

| Ticket | Title | Assigned to | Branch | Blocked by |
|--------|-------|-------------|--------|------------|
| AST-430 | Phase 1 — reach | Hedy | `sub/AST-410/AST-430-spike-general-catalyst-jobs-board-profile` | — |
| AST-431 | Phase 2 — widgets | Hedy | `sub/AST-410/AST-431-spike-general-catalyst-jobs-board-profile` | AST-430 |
| AST-432 | Phase 3 — search/parse | Hedy | `sub/AST-410/AST-432-spike-general-catalyst-jobs-board-profile` | AST-431 |
| AST-433 | Phase 4 — draft JSON | Hedy | `sub/AST-410/AST-433-spike-general-catalyst-jobs-board-profile` | AST-432 |

**Assignment rationale:**
- **Hedy:** all phases — Playwright board spikes (same as AST-413 Heavybit)

Parent **In Progress**, assignee **Chuckles**. Sequential `blockedBy`; only **AST-430** unblocked for **plan-astral** first.

**Git (ignore Linear `gitBranchName`):**
- Parent: `origin/ftr/AST-410-spike-general-catalyst-jobs-board-profile-playwright`
- Children: `origin/sub/AST-410/AST-430-…` through `AST-433-…` (see table)

Susan gates each phase before the next. Spike workflow: no full prep-uat; finish-up lands on `dev` when parent is **PR Ready**.

— Chuckles

#### chuckles — 2026-05-17T22:44:18.507Z
Reassigned to **@Susan Somerset** — three open questions in the Description need your answers before dispatch.

— Chuckles

#### chuckles — 2026-05-17T22:42:57.507Z
Definition draft ready for review. Key decisions made:
- Four gated phases (reach → widgets → search/parse → schema v3 draft); same pattern as AST-413 / AST-414
- Spike output: `debug/spikes/<phase-child-id>/` + Linear attachments only — no production or `BOARD_CONFIG`
- Phase 4 canonical shape: AST-414 attachment *board_profile_draft.json (schema v3)*

**3 open questions** in Description (search literals, bot protection, adoption timing vs 411/412).

Ticket is already **Todo** — if the definition looks good, say the word for **dispatch-linear** (four phase children + `ftr`/`sub` branches). Or comment with edits first.

— Chuckles

#### chuckles — 2026-05-17T18:41:44.410Z
**Spike Phase 4 template aligned with AST-414** (2026-05-17, per Susan)

Updated parent spike definitions so Phase 4 is **`board_profile_draft.json`** (real page widgets + tray option lists), not `BOARD_CONFIG` commits:

* [AST-410](https://linear.app/astralcareermatch/issue/AST-410) General Catalyst
* [AST-411](https://linear.app/astralcareermatch/issue/AST-411) GV
* [AST-412](https://linear.app/astralcareermatch/issue/AST-412) YC
* [AST-413](https://linear.app/astralcareermatch/issue/AST-413) Heavybit
* [AST-397](https://linear.app/astralcareermatch/issue/AST-397) a16z parent — Phase 4 section added
* [AST-414](https://linear.app/astralcareermatch/issue/AST-414) — canonical schema + attachments

Also: §3.6 paths (`debug/spikes/AST-NNN/`), Linear attachments, no `board-spike-phases.md` / `docs/` spike output.

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
