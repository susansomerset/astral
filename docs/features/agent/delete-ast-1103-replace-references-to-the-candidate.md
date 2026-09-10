# AST-1103 — Replace references to "the candidate"

<!-- linear-archive: AST-1103 archived 2026-08-14 -->

## Linear archive (AST-1103)

**Archived:** 2026-08-14  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1103/replace-references-to-the-candidate  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Agent personas and task prompts still talk about "the candidate" like an external case file. Astral's agents are meant to feel like members of that person's personal team — addressing and referring to them with `{$FIRST_NAME}` and pronoun tokens (`{$THEY}` / `{$THEIR}` / `{$THEIRS}` / `{$THEM}` / `{$THEMSELF}`) in warmer, informal teammate language. This epic updates the seeded `agent` / `agent_task` prompt corpus and default rubric vector copy in config so runtime and craft prompts match that voice.

## Functional scope

1. **Agent-task seed voice.** Rewrite prompt segments in the repo `agent_task` seed so clinical "the candidate" / "the candidate's …" references become `{$FIRST_NAME}` and pronoun-token language in informal teammate voice. Cover every current seed row that still uses that phrasing (consult, craft, intake, resume chain, meteorite twins, preamble/topic-menu, etc.). Preserve task contracts: schemas, payload rules, grade alphabets, cache-segment roles, and `run_next` wiring stay unchanged.
2. **Agent persona seed voice.** Rewrite persona `content` in the repo `agent` seed the same way (Estelle, Grace, Judith, Atlas, and any other personas that still say "the candidate"), so system/persona blocks resolve with the same personal-team voice.
3. **Default rubric vector copy in config.** Update embedded/default rubric vector text in `config` that still says "the candidate" / "this candidate" (notably evaluate_jd Quality Check / Gut Check) so grade definitions use the same personal-team language Susan wants for defaults.
4. **Seed/fixture parity.** After seed edits, keep the AST-756 expected admin JSON fixtures byte-identical to the repo seeds so startup apply and seed gates stay honest.
5. **Runtime token honesty for rubric bodies (if needed).** If default (or future crafted) rubric vector bodies contain `{$FIRST_NAME}` / pronoun tokens, those tokens must actually resolve when rubric text is injected into prompts — not appear as raw `{$…}` to the model. If Susan chooses informal non-token rewrites for embedded defaults only, this capability may collapse into a short "not required" note at plan time.

## Architectural definition

* **Patterns to reuse** — `pattern.config.config-block`: default/embedded rubric vector copy and any token-resolution behavior stay config/utils-owned, not reinvented in core call sites. Existing `TOKEN_SOURCES` / `resolve_tokens` / persona-content resolve path for `agent` + `agent_task` segments (already used for `{$FIRST_NAME}` and pronoun tokens) is the assembly contract — no second prompt system.
* **New patterns proposed** — none. If rubric-body token resolution is required, it is an extension of the existing resolve path for `{$RUBRIC_VECTORS}` content, not a new catalog pattern.
* **Applicable statutes** — `astral.config.config-source-of-truth` (embedded defaults and token behavior live in config/utils); `astral.standards.in-scope-only` (prompt/seed/copy only — no pipeline redesign); `astral.standards.no-cross-contamination` (seeds + config; no drive-by consult/scoring changes); `astral.standards.dry-and-focused-functions` (one resolve path, no parallel substitution); `astral.agent.do-task-delegation` (prompt text still flows through existing `do_task` assembly).

## Boundaries

* Does **not** change scoring, decode, dispatch, state machines, Manage Tasks UI chrome, or response schemas.
* Does **not** invent new tokens — uses existing first-name and pronoun tokens only.
* Does **not** bulk-rewrite already-stored candidate-owned `rubric_vector` rows. Craft prompts in seeds are updated so **future** crafts emit the new voice; existing crafted vectors refresh only if Susan re-runs craft (or a later ticket migrates them).
* Does **not** rewrite code comments, NAV copy, UI labels, test-bible prose, or unrelated "candidate" domain nouns (table names, entity types, API paths).
* Does **not** hand-edit live DB rows outside the normal repo-admin-JSON apply path.
* Tempting but excluded: full persona personality redesign beyond replacing clinical third-person with name/pronoun teammate voice; rewriting every occurrence of the word "candidate" in product docs.

## Acceptance criteria

1. After seed apply, current `agent_task` rows from the repo seed no longer use clinical "the candidate" / "the candidate's …" phrasing in prompt segments where a person reference is meant; they use `{$FIRST_NAME}` and/or pronoun tokens (or clearly informal teammate wording Susan approved) instead.
2. After seed apply, current `agent` persona rows likewise use that personal-team voice for person references.
3. Embedded/default evaluate_jd rubric vector copy in config no longer uses clinical "the candidate" / "this candidate" phrasing in grade definitions; wording matches the approved personal-team approach from Open questions.
4. `docs/uat-fixtures/AST-756/expected-agent.json` and `expected-agent_task.json` match the repo `data/admin/` seeds after the rewrite.
5. Spot-check with a real candidate: preview or run at least one consult-style task and one craft-style task — resolved prompts show the candidate's first name / pronouns, not raw tokens and not clinical "the candidate," for the rewritten segments.
6. If rubric-body token resolution was in scope: injecting `{$RUBRIC_VECTORS}` shows resolved names/pronouns inside vector text; if it was explicitly out of scope, embedded defaults contain no unresolved `{$…}` tokens.

## Dependencies and blockers

none.

## Open questions

1. **Embedded default vectors — tokens vs plain informal prose?** Putting `{$FIRST_NAME}` / pronoun tokens inside embedded rubric bodies only works if rubric text is resolved when `{$RUBRIC_VECTORS}` is built (today that injection is not a second full `resolve_tokens` pass over vector content). Prefer (A) tokens + resolve-on-rubric-body, or (B) informal rewrite without name tokens for embedded QC/GC only?
2. **Meta / UI-facing phrases in prompts** — e.g. "the candidate pressed Generate Profile", "Your message to the candidate", "allow the candidate to read them" — rewrite those too into name/pronoun teammate voice, or leave meta labels that mean "the human in the product" alone?
3. **Confirm agent personas in scope** — brief says seed `agent` and `agent_task`; definition includes both. Say if personas should stay third-person clinical while only task prompts change.

## Proposed child tickets

#### 1!: **Repo agent + agent_task seed voice rewrite - Ada**

Owns rewriting `data/admin/agent.json` and `data/admin/agent_task.json` to personal-team voice with `{$FIRST_NAME}` / pronoun tokens, plus AST-756 expected-fixture byte parity. Does **not** own config embedded rubric defaults or rubric-body resolve behavior (child 2).
**Citations:** `pattern.config.config-block` (seeds remain the admin-JSON source applied at startup); `astral.standards.in-scope-only`; `astral.standards.no-cross-contamination`.

#### 2: **Config default rubric voice (+ resolve if required) - Hedy**

Owns embedded/default rubric vector copy in config (evaluate_jd QC/GC and any sibling default vector text still using clinical phrasing). If Open question 1 is (A), also owns resolving tokens inside rubric body text when assembling `{$RUBRIC_VECTORS}`. Does **not** own broad `agent_task` seed edits (child 1). After #1 for fixture/seed coordination only if shared UAT needs both.
**Citations:** `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.standards.dry-and-focused-functions`.

Monolith check: four functional capabilities → two children (seeds+fixtures vs config defaults/+resolve). Intentional: one apply-path corpus edit, one config/resolve slice.

---

## Original brief

Our agent_task and even default rubric vectors use the phrase "the candidate", but we can use the token for the candidate's first name and the {$THEY|THEIR|THEIRS…} tokens.

The intention is for the AI agent persona to be a part of the candidate's personal team.  Please replace text in agent_task to use the candidate's first name token and pronouns in more informal language.

I believe we are "seeding" the agent and agent_task tables, so this should update those seeds and update prompt content in [config.py](<http://config.py>).

### Comments

#### chuckles — 2026-07-31T04:58:22.062Z
@susan

1. Embedded QC/GC defaults: (A) `{$FIRST_NAME}` / pronoun tokens + resolve tokens inside rubric body text when building `{$RUBRIC_VECTORS}`, or (B) informal rewrite without name tokens for those embedded vectors only?
2. Meta prompt phrases like "the candidate pressed Generate Profile" / "Your message to the candidate" — rewrite into name/pronoun voice, or leave those meta labels alone?
3. Confirm `agent` persona seeds are in scope with `agent_task` (definition assumes yes).

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
