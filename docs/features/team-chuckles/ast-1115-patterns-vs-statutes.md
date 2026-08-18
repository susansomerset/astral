# AST-1115 — Patterns vs Statutes

<!-- linear-archive: AST-1115 archived 2026-08-17 -->

## Linear archive (AST-1115)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1115/patterns-vs-statutes  
**Status at archive:** Archive  
**Project:** Team Chuckles  
**Assignee:** unassigned  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Where/how are patterns being evaluated?  Are they part of the work Joan is doing, or is she just establishing statutes?  I think we may be missing that, and they are just as important as statutes (for DRY)

From Claude Sonnet:
I pulled [AST-1115](https://linear.app/astralcareermatch/issue/AST-1115/patterns-vs-statutes) from Linear and cross-checked it against the actual `canon/` trees in `/Users/susan/chuckles/astral` (team-chuckles doesn't have a `canon/` dir — it lives in the product repo). Your instinct was right: there's a real gap, not just a documentation nit.

## What's actually there

Two genuinely separate "pattern" mechanisms exist in `astral/canon/`, and they've never been reconciled:

**1. The real Pattern Catalog** — `canon/patterns/{batch,config,dispatch,layers,state,ui}/`, 7 files, id scheme `pattern.{domain}.{slug}`, each with `canonical_refs`, `related_statutes`, Archie approval lineage. Example: `pattern.batch.entity-claim-process-release`. One (`pattern.dispatch.run-next-chain-authority`, from [AST-1109](https://linear.app/astralcareermatch/issue/AST-1109/hard-coded-daisy-chain-in-configpy)) is still `status: proposed`, not yet approved.

**2. A statute subfolder that borrowed the word "pattern"** — `canon/statutes/astral/patterns/`, only 3 files (`astral.patterns.coat-check-never-store-empty`, `astral.patterns.require-auth-on-protected-endpoints`, `astral.patterns.render-verdict-orchestrates-consult`). These are ordinary statutes — `tier: scoped`, `checkable: judgment`, Statement/Rationale/Examples — that happen to be namespaced `patterns` because they were harvested from named idioms in `ASTRAL_CODE_RULES.md`. They are not catalog entries and don't overlap in content with the 7 real ones.

## Where each gets evaluated (or doesn't)

* `define-parent` (epic definition) — requires citing real catalog ids (`pattern.{domain}.{slug}`) under "Architectural definition." Citation is mandatory.
* **Joan** (`joan-AGENTS.md`, plan-rubric.v1) — is scoped to `canon/statutes/**` only; her title is literally "Statute Validator." Her only "pattern" awareness is a **hardcoded checklist** in `validate-plan/SKILL.md` (§2.4 batch, §2.6 state machine, §2.8 coat-check) — three named idioms lifted straight from `ASTRAL_CODE_RULES.md`, not read from the catalog. It doesn't cover 4 of the 7 approved catalog patterns (config-block, layers/import-discipline, admin-endpoint, entity-agent-responses) and would silently miss any new one Archie approves.
* **Radia** (`review-child/SKILL.md` §5.1) — explicitly says *"Do not invent* `canon/patterns/`. Active `astral.patterns.*` statutes are already covered by §5.0." So at review time, the 7-entry real catalog is **never checked at all** — only the 3 statute-namespace "patterns" get swept, and only because they're statutes like any other.

So: citations are demanded going in (define-parent), nothing validates them at plan time beyond a stale 3-item hardcoded list, and review time explicitly disclaims the catalog. A cited `pattern.config.config-block` reference could be violated end to end and no agent would ever flag it. That's the DRY risk you flagged — the catalog exists and is Archie-approved, but it's a dead letter.

## Recommended next actions

1. **Close the loop at review time.** Rewrite `review-child/SKILL.md` §5.1 to actually resolve cited `pattern.*` ids against `canon/patterns/**` and score conformance from each file's Solution shape — not just defer to the statute sweep. The "do not invent canon/patterns/" line should go; it's protecting against a file that turns out to genuinely exist.
2. **Give Joan the catalog, not a hardcoded checklist.** Replace the fixed §2.4/§2.6/§2.8 list in plan-rubric.v1 with a scan of `canon/patterns/**` the same way statute relevance is matched — so new approved patterns (like the pending `pattern.dispatch.run-next-chain-authority`) are automatically in scope once approved.
3. **Rename the statute namespace to stop the collision.** `astral.patterns.*` inside `canon/statutes/` reads as if it's the catalog. Something like `astral.idioms.*` (or fold them under an existing statute domain) would remove the ambiguity that's presumably why this ticket exists.

Given this is currently a Discussion-status ticket assigned to Fable with no comments yet, want me to post this analysis as a comment on [AST-1115](https://linear.app/astralcareermatch/issue/AST-1115/patterns-vs-statutes), or would you rather I go straight to drafting the `review-child`/`validate-plan` SKILL.md edits for #1–2?

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
