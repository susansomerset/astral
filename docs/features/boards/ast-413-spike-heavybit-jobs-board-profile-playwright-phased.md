# AST-413 — Spike: Heavybit Jobs board profile (Playwright, phased)

<!-- linear-archive: AST-413 archived 2026-06-15 -->

## Linear archive (AST-413)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-413/spike-heavybit-jobs-board-profile-playwright-phased  
**Status at archive:** Done  
**Project:** Astral Boards  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-379; related: AST-397

### Description

## Summary

**Board candidate:** **Heavybit Jobs** — not yet adopted. Playwright profile spike for [AST-379](https://linear.app/astralcareermatch/issue/AST-379).

Phased, gated process (same as [AST-397](https://linear.app/astralcareermatch/issue/AST-397) / [AST-414](https://linear.app/astralcareermatch/issue/AST-414)). **Board key:** `heavybit`.

**Phase children (dispatched 2026-05-17):** [AST-422](https://linear.app/astralcareermatch/issue/AST-422) Phase 1 · [AST-423](https://linear.app/astralcareermatch/issue/AST-423) Phase 2 · [AST-424](https://linear.app/astralcareermatch/issue/AST-424) Phase 3 · [AST-425](https://linear.app/astralcareermatch/issue/AST-425) Phase 4.

**Spike paths** (§3.6): `debug/spikes/AST-NNN/` per phase ticket; **Linear attachments** for handoff.

## Canonical entry URL

`https://www.heavybit.com/jobs`

## Query-param example

`https://www.heavybit.com/jobs?query=US` — Phase 3 may use param-style deep link if supported.

## Phases

1. **Reach** — AST-422. Gate: Susan.
2. **Widgets** + tray option lists — AST-423. Canonical: AST-414. Gate: Susan.
3. **Search + parse spec** — AST-424. Gate: Susan.
4. **Profile draft JSON** — AST-425 → `board_profile_draft.json` matching **AST-414** schema. No `BOARD_CONFIG` in spike. Gate: Susan → **AST-415** if adopted.

## Non-goals

No SQLite or production gazer until Phase 4 reviewed and **AST-415+** scheduled.

### Comments

#### chuckles — 2026-05-17T22:27:29.582Z
## Landed on origin/dev — Chuckles

Prep-uat rollup (sub → parent) was not on `ftr/` yet; merged all four phase branches into `origin/ftr/AST-413-spike-heavybit-jobs-board-profile-playwright`, then **finish-up**.

- Merged `origin/ftr/AST-413-spike-heavybit-jobs-board-profile-playwright` → local `dev` → pushed **`origin/dev`**
- Deleted `origin/ftr/AST-413-spike-heavybit-jobs-board-profile-playwright`
- Deleted `sub/AST-413/*` (422–425)
- Children already **PR Ready** (assignee unchanged): AST-422, AST-423, AST-424, AST-425

Push commit: `33142224`

— Chuckles

#### chuckles — 2026-05-17T18:48:55.919Z
## Dispatch — Chuckles

Dispatched **4** phase children from approved **[AST-413](https://linear.app/astralcareermatch/issue/AST-413)** definition. Parent was incorrectly left on **Hedy** as sole assignee; spike work is now decomposed like **AST-397**.

| Ticket | Phase | Assigned | Branch | Blocked by |
|--------|-------|----------|--------|------------|
| AST-422 | 1 — Reach | Hedy | ftr/AST-422 | — |
| AST-423 | 2 — Widgets + option lists | Hedy | ftr/AST-423 | AST-422 |
| AST-424 | 3 — Search + parse spec | Hedy | ftr/AST-424 | AST-423 |
| AST-425 | 4 — `board_profile_draft.json` | Hedy | ftr/AST-425 | AST-424 |

**Assignment rationale:**
- **Hedy:** Playwright spike scripts + Phase 4 assembler (same as a16z AST-400–414). Sequential gates; start **AST-422** only.

**Phase 4 schema:** Match **[AST-414](https://linear.app/astralcareermatch/issue/AST-414)** (`page_controls`, tray option lists, `criteria_param_map` with real labels) — not `BOARD_CONFIG` commits.

**Paths:** `debug/spikes/AST-422/` … `AST-425/` per §3.6.

Parent → **In Progress**, assignee **Chuckles** (coordination). Engineers own child tickets.

**Git (authoritative — ignore Linear `gitBranchName`):**
- Parent: `origin/ftr/AST-413`
- Children: `origin/ftr/AST-422` … `origin/ftr/AST-425`

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
