<!-- linear-archive: AST-304 archived 2026-06-03 -->

## Linear archive (AST-304)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-304/add-parsable-chain-tokens-to-resolve-tokens  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** High / 3  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-310; blocks: AST-300

### Description

Extend resolve_tokens() in src/utils/config.py to support: {$CALLER_RESPONSE} (prior task output), {$CACHE_BLOCK_A} through {$CACHE_BLOCK_D} (accumulated cache blocks from preceding call), {$WRITING_PREFERENCES} (from candidate_data.context), {$SELECTED_AGENT} (resolves to assigned agent system prompt content). Token values are passed into resolve_tokens() by do_task() at call time — no changes to callers needed.

### Comments

#### susan — 2026-05-04T21:00:25.275Z
[check-linear] **e-push-linear housekeeping:** Branch was already merged into `dev` (merge commit `3f7ef802` on `dev`). No open PR (GitHub: *no commits between dev and feature branch*). Linear updated **Done**, plan attachment repointed to **`blob/dev/.../ast-304-add-parsable-chain-tokens-to-resolve_tokens.md**.

#### susan — 2026-04-29T22:20:47.822Z
Review feedback resolved. Branch `chuckles/ast-304-add-parsable-chain-tokens-to-resolve_tokens` is ready for testing.

**Commit:** `d4a61627e0be99044b6e3f2474434108029d8c47`

- Discuss (tests): explicit deferral + **## Revisions** on the combined plan doc.
- Advisory (DRY): `chain_context_selected_agent()` in `config.py`; `agent` + `api_admin` use it.

— Ada

#### susan — 2026-04-29T22:18:59.834Z
**Review posted — Radia**

Summary: **0** fix-now, **1** discuss (plan step 6 unit tests not in branch — confirm defer vs follow-up), **1** advisory (minor `chain_context` dict DRY between `agent.py` and `api_admin.py`).

Owner back to **Ada** per build comment. Conf / Risk / Scope unchanged.

**Combined doc (feature branch, includes review section):**  
https://github.com/susansomerset/astral/blob/f0bcf5731c6547b7a7137469e1a2316d963985da/docs/features/artifacts/ast-304-add-parsable-chain-tokens-to-resolve_tokens.md

— Radia

#### susan — 2026-04-29T22:12:32.765Z
Built by **Ada**.

**Branch:** `chuckles/ast-304-add-parsable-chain-tokens-to-resolve_tokens`  
**Commit:** `33be7896c1c30fc1053190a88833c8eb9c457e93`

Summary: optional `chain_context` on `resolve_tokens`; `TOKEN_SOURCES` entries for `CALLER_RESPONSE`, `CACHE_BLOCK_A`–`D`, `SELECTED_AGENT` (chain), `WRITING_PREFERENCES` (`context.writing_preferences`); `_chain_context` + wiring in `do_task` / `preview_prompt` and admin task enrichment + adhoc preview; `CANDIDATE_DATA_MODEL` row for writing preferences; review stub on plan doc.

— Ada

#### susan — 2026-04-29T22:09:39.410Z
Label review (build agent):

Conf: agree — current conf-Medium matches plan (chain dict + single-pass SELECTED_AGENT semantics are understood, minor product edge cases).
Risk: agree — current risk-Medium matches plan (only prompts that reference new tokens are affected).
Scope: agree — current scope-Single-Component matches plan (config + agent threading + admin preview + doc).

— Ada

#### susan — 2026-04-29T21:40:54.571Z
**Plan doc (repo):** `docs/features/artifacts/ast-304-add-parsable-chain-tokens-to-resolve_tokens.md`  
**GitHub (feature branch):** same path on `chuckles/ast-304-add-parsable-chain-tokens-to-resolve_tokens`.

**Self-assessment (for labels)**

- **Scope — Single-Component:** Touches `resolve_tokens` / `TOKEN_SOURCES` in `config.py`, threads optional `chain_context` through `do_task` + `preview_prompt` in `agent.py` and admin preview in `api_admin.py`, plus a small `CANDIDATE_DATA_MODEL` note for `context.writing_preferences` — no dispatcher or DB migrations.

- **Conf — Medium:** Chain dict contract aligns with AST-303 wording; `{$SELECTED_AGENT}` is intentionally single-pass raw `agent.content`, and optional `writing_preferences` may need product OK if prompts nest tokens inside that body.

- **Risk — Medium:** Only prompts that reference the new tokens change behavior; mis-wiring `chain_context` would skew those prompts, while legacy prompts stay unchanged.

Worktree note: `dev` is checked out in another clone, so this branch was cut from `origin/dev` at push time (not a local `git checkout dev` + rebase in this worktree).

— Ada

---

# AST-304 — Add Parsable Chain Tokens to resolve_tokens()

**Linear:** [AST-304](https://linear.app/astralcareermatch/issue/AST-304/add-parsable-chain-tokens-to-resolve-tokens) — Add Parsable Chain Tokens to resolve_tokens()  
**Project:** Astral Artifacts  
**Priority / estimate:** High / 3 points  

**Blocks:** AST-303 (daisy-chain execution), AST-300/301/310 family, AST-365, AST-368/371, AST-370 (per Linear relations). This ticket delivers the **token surface**; **AST-303** consumes `{$CALLER_RESPONSE}` and `{$CACHE_BLOCK_A}`–`{$CACHE_BLOCK_D}` when chaining lands.

## Goal

Extend `resolve_tokens()` so prompts can reference:

| Token | Source |
|--------|--------|
| `{$CALLER_RESPONSE}` | Prior hop output (text or serialized JSON), supplied at call time by `do_task()` when chaining |
| `{$CACHE_BLOCK_A}` … `{$CACHE_BLOCK_D}` | Materialized cache-prompt strings from the preceding hop, supplied at call time |
| `{$WRITING_PREFERENCES}` | `candidate_data["context"]["writing_preferences"]` (same pattern as other `context.*` tokens) |
| `{$SELECTED_AGENT}` | System prompt body (`agent.content`) of the **agent assigned to the current `agent_task`** — injected at call time so `config.py` never imports the data layer |

**Non-goal for this ticket:** Implementing recursion / `run_next` (AST-303, AST-306). **AST-304** only adds resolution rules and threads call-time context from `do_task()` / `preview_prompt()` (and admin preview where applicable).

## Decisions (locked for build)

1. **Fourth parameter** — `resolve_tokens(text, candidate_data, task_key, chain_context=None)` where `chain_context` is `Optional[Dict[str, str]]`. Keys use the same spelling as `TOKEN_SOURCES` / regex capture names (`CALLER_RESPONSE`, not nested objects). Missing keys → empty string + existing-style empty warning where appropriate.

2. **`{$WRITING_PREFERENCES}`** — Implemented as a normal **candidate** `TOKEN_SOURCES` entry: `path: "context.writing_preferences"`. Document the key in `docs/features/candidate/CANDIDATE_DATA_MODEL.md` (optional text field; UI may land separately). Until populated, token resolves empty (same as other optional context fields).

3. **`{$SELECTED_AGENT}`** — **Runtime / chain dict only:** before any `resolve_tokens` call for a task, the caller passes `chain_context["SELECTED_AGENT"] = agent_row.get("content") or ""` (raw DB string, **not** pre-resolved for nested `{$...}` inside that agent body — single pass over the outer prompt). Avoids `resolve_tokens` → `get_agent` imports from utils into data.

4. **Registry** — Add `TOKEN_SOURCES` rows for all seven chain-style names; introduce a small `source` discriminator (e.g. `"chain"`) whose resolver reads `chain_context` by token name. `get_tokens()` returns sorted keys including the new names so Manage Tasks / tooling stay truthful.

5. **Call sites** — `src/core/agent.py`: `do_task` and `preview_prompt` build the same `chain_context` baseline (`SELECTED_AGENT` only today; AST-303 later adds caller/cache strings). `src/ui/api/api_admin.py`: wherever prompts are resolved against a candidate with a known agent dict, pass the same `SELECTED_AGENT` rule so admin preview matches production.

## Procedure (implementation order)

1. **`TOKEN_SOURCES` + regex** — Today `_TOKEN_RE = re.compile(r"\{\$([A-Z_]+)\}")` already allows `CACHE_BLOCK_A` style names. Add entries for `CALLER_RESPONSE`, `CACHE_BLOCK_A`–`CACHE_BLOCK_D`, `WRITING_PREFERENCES` (candidate path), `SELECTED_AGENT` (chain source).

2. **`resolve_tokens`** — Add optional `chain_context`; in `_replace`, handle `source == "chain"` (read `chain_context.get(name, "")`, warn on empty when token present in text — mirror candidate empty logging). Preserve “unknown token name leaves literal `{$FOO}`” only for names **absent** from `TOKEN_SOURCES`; registered chain tokens with no value resolve to `""`.

3. **`do_task` / `preview_prompt`** — After `_resolve_task_prompts`, build `chain_context = {"SELECTED_AGENT": agent_row.get("content") or ""}` and pass into all four `resolve_tokens` calls. Signature change is backward-compatible (`None` default).

4. **`api_admin.py`** — Thread `SELECTED_AGENT` into preview endpoints that already have `agent` + `cd` + `task_key` (same dict shape as core).

5. **Docs** — Update `CANDIDATE_DATA_MODEL.md` context table with `writing_preferences`. Cross-link AST-303 plan for who fills `CALLER_RESPONSE` / cache blocks.

6. **Tests** — Add focused unit tests for `resolve_tokens` (chain keys present/absent, `WRITING_PREFERENCES` path, `SELECTED_AGENT` override, unknown token unchanged). Prefer tests colocated with existing config/agent test layout.

## Files changed (expected)

| File | Change |
|------|--------|
| `src/utils/config.py` | `TOKEN_SOURCES`, `resolve_tokens(..., chain_context=None)`, `get_tokens()` |
| `src/core/agent.py` | Build `chain_context`, pass into `resolve_tokens` in `do_task` + `preview_prompt` |
| `src/ui/api/api_admin.py` | Pass `chain_context` with `SELECTED_AGENT` where agent + task preview resolve tokens |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Document `context.writing_preferences` |
| Tests (e.g. under `tests/` if present) | New cases for chain + candidate tokens |

## Self-Assessment

**Scope:** `Single-Component` — Touches `resolve_tokens` / `TOKEN_SOURCES` in `config.py`, call-site threading in `agent.py` and `api_admin.py`, plus a small doc add for the new context key; no dispatcher, DB schema, or state-machine changes.

**Conf:** `Medium` — The chain dict contract is straightforward and matches AST-303’s written expectations, but `{$SELECTED_AGENT}` single-pass semantics and optional `writing_preferences` UX need Susan’s OK if prompts embed nested tokens inside the agent row body.

**Risk:** `Medium` — Mis-wiring `chain_context` would wrong-foot prompts that adopt the new tokens; existing prompts that never mention them behave as today. Chain-dependent behavior stays gated until AST-303 passes values.

## Self-review vs `ASTRAL_CODE_RULES.md`

| Section | Check |
|---------|--------|
| §1.3 DRY | One `chain_context` builder helper in `agent.py` (small local function or shared helper) avoids duplicating the dict literal four times. |
| §2.1 config | New literals only in `TOKEN_SOURCES`; no magic token strings scattered outside registry + tests. |
| §2.4 batch | No change to `batch_id` / claim flow; `chain_context` is per-call. |
| §2.6 state machine | Tokens enable future chaining; they do not introduce entity state transitions. |
| §3.3 imports | `config.py` does **not** import `database` / `get_agent`; `SELECTED_AGENT` value is always injected by core/UI. |
| §3.5 naming | Snake_case dict keys in Python (`chain_context`); token names remain `UPPER_SNAKE` per existing convention. |

**Conflicts:** None identified; AST-303 remains blocked until this plan is approved and built, then chained with 306/303 as already documented on AST-303.

---

## Review

**Branch:** `<agent>/ast-304-add-parsable-chain-tokens-to-resolve_tokens`  
**Code reviewed at:** `33be7896c1c30fc1053190a88833c8eb9c457e93`  
**Reviewed:** 2026-04-29 — Radia (`e-review-linear`). Radia’s narrative below may land in a later doc-only commit on this branch.

### What's solid

- **Plan fidelity (steps 1–5):** `TOKEN_SOURCES` gains `WRITING_PREFERENCES` plus five `source: "chain"` rows; `resolve_tokens(..., chain_context=None)` is backward-compatible; chain branch mirrors candidate empty-token warning style; registered chain keys with missing/empty values resolve to `""` while unknown names stay literal — matches locked decisions 1–2 and 4.
- **`SELECTED_AGENT` injection (decision 3):** `agent._chain_context(agent_row)` threads into all four `resolve_tokens` calls in `do_task` and `preview_prompt`; `config.py` does not import data (§3.3 / plan).
- **Admin parity (decision 5):** `_enrich_tasks` and `_resolve_adhoc` pass `chain_context` for system/cache (and full adhoc block set) so previews align with production when prompts reference chain tokens.
- **§2.1 / tooling:** `get_tokens()` remains `sorted(TOKEN_SOURCES.keys())`, so Manage Tasks picks up the new names without extra wiring.
- **Docs:** `CANDIDATE_DATA_MODEL.md` documents `context.writing_preferences` as optional, consistent with the plan.

### Issues

| Severity | Topic | Notes |
|----------|--------|--------|
| — | — | No fix-now items. |
| Discuss | Plan procedure **step 6 (tests)** | The plan calls for focused unit tests (`resolve_tokens` chain keys, `WRITING_PREFERENCES`, `SELECTED_AGENT`, unknown token unchanged). None appear in the branch diff. Confirm intentional deferral vs oversight; if deferring, a short `## Revisions` note (or Linear comment) keeps plan and repo aligned. |
| Advisory | Small DRY drift | `api_admin.py` builds `{"SELECTED_AGENT": ...}` inline in two places while `agent.py` uses `_chain_context`. Low risk; consider a shared helper only if AST-303 expands the dict and duplication grows. |

### Recommended actions

| Priority | Action | Owner |
|----------|--------|-------|
| Discuss | Add the planned tests or record an explicit waiver in the combined doc / Linear. | Ada / Susan |
| Advisory | When AST-303 threads `CALLER_RESPONSE` / `CACHE_BLOCK_*`, reuse one builder for the full `chain_context` shape from core (or a tiny shared module) so admin and `do_task` stay in lockstep. | Ada |

## Revisions

**Revision 1 — 2026-04-29**  
**Driven by:** Radia review (Discuss: plan procedure step 6 — unit tests not in branch).  
**Changes:** Explicit deferral of focused `resolve_tokens` unit tests: the repo had no `tests/` + pytest layout at build time. Revisit when a standard harness lands or when **AST-303** adds integration coverage for chain context.

## Resolution

**2026-04-29 — f-resolve-linear (Ada)**

- **Discuss (tests):** Waiver recorded under **## Revisions** above; no new test package in this pass.
- **Advisory (DRY):** Implemented `chain_context_selected_agent()` in `src/utils/config.py`; `agent._chain_context` and `api_admin` call sites use it so `{$SELECTED_AGENT}` injection stays single-sourced before **AST-303** merges additional chain keys.

