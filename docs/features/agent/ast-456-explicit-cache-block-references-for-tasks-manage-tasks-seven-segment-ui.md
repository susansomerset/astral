# AST-456 — Explicit cache block references for tasks: Manage Tasks seven-segment UI

**Linear:** [AST-456](https://linear.app/astralcareermatch/issue/AST-456/explicit-cache-block-references-for-tasks-manage-tasks-seven-segment-ui)  
**Parent:** [AST-453 — Explicit cache block references for tasks](https://linear.app/astralcareermatch/issue/AST-453/explicit-cache-block-references-for-tasks)  
**Feature ref (origin only):** `sub/AST-453/AST-456-explicit-cache-block-references-for-tasks-manage-tasks-seven-segment-ui`

## Summary

Extend **Manage Tasks** (`src/ui/frontend/src/pages/AdminTaskPrompts.tsx`) so each task exposes **seven** ordered editors: **System Prompt** → **Cache Block A** → **Cache Block B** → **Cache Block C** → **Cache Block D** → **No Cache Block** → **User Prompt**. Reuse `TokenTextarea` / `TabbedTextArea` / `CollapsiblePanel` patterns already on the screen. Persist through admin REST PUT with fields from **AST-454** (`cache_prompt` as slot A plus `cache_prompt_b|c|d`). Token picker consumes **chain-safe** registry from **`/api/admin/tasks/meta/tokens`** (or dedicated endpoint emitted in **AST-455**) so operators never see phantom `{$NO_CACHE_BLOCK}` / `{$USER_PROMPT}` selectable entries—those literals stay impossible if absent server-side.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` | Extend `AgentTask` interface + edit state hooks for `cache_prompt_b|c|d`; refactor tab typing from four tabs to seven (`TabKey` union); reorder `PREVIEW_TABS`; load/save via API keys matching Flask JSON; preserve `run_next` + agent select UX untouched; collapse panels order per parent | ui |
| `src/ui/api/api_admin.py` | If AST-455 added `tasks/meta/chain_tokens`, consume it for token autocomplete source instead of whole `tokens`—**fallback** acceptable if sibling not merged: fetch `/tasks/meta/tokens` + client filter disallow list `{NO_CACHE_BLOCK, USER_PROMPT}` even if stray—document which path chosen in builder comment only if divergence | ui |

No Anthropic/page outside Manage Tasks scope.

---

## Stage 1: Types and modal edit state wiring

**Done when:** TypeScript builds (`npx tsc -b --noEmit`); modal tracks seven strings independently.

1. Extend `AgentTask` with optional `cache_prompt_b`, `cache_prompt_c`, `cache_prompt_d` strings (mirror server).
2. Add React state mirrors `editCacheB`, … initialized from `full_task` fetch (`GET task` returns complete row once modal opens—already pattern for system/user/cache).
3. Expand `TabKey` / preview unions to `'cache_b'|'cache_c'|'cache_d'` etc.
4. Map tab order exactly per parent enumerated list—**numbers in UI labels** acceptable (`Cache Block B`).

---

## Stage 2: Fetch + save payloads

**Done when:** Save issues single PUT including all seven fields plus existing keys; reloading modal shows persisted text.

1. Modify save handler assembling JSON body `{ system_prompt, user_prompt, cache_prompt, cache_prompt_b, cache_prompt_c, cache_prompt_d, nocache_prompt, … }`.
2. Guard: missing server fields ⇒ treat as empty string on read.
3. On successful save, toast + `loadAll()` like today.

---

## Stage 3: Preview tabs + token picker

**Done when:** Preview modal shows tabs for populated segments parity with server keys returned from preview endpoint (**AST-455** expands keys)—if backend returns fewer keys pre-merge, gates behind optional chaining stub is **disallowed**—coordinate merge order via Linear comment **if** sibling pending.

1. When opening preview after AST-455 ships, iterate ordered list of segment keys expecting new API shape documented in sibling plan.
2. `TokenTextarea`: load allowed tokens endpoint per **Decision** below.

⚠️ **Decision:** Prefer dedicated `chain_tokens` endpoint from AST-455; if unavailable during build window, temporarily filter forbidden names client-side and post `[qa-handoff]` to Betty if mismatch suspected.

---

## Stage 4: Layout + accessibility regressions spot-check

**Done when:** No React console errors opening modal; collapsed panels reopen on same task edit.

1. Respect `ADMIN_TASK_PROMPTS_DEFAULT_PANEL_LS` keyed by logical tab—but expand allowed stored values accordingly or migrate stale localStorage gracefully (silent fallback `'user'` if unknown key).
2. Keep `runNextGraphIsAcyclic` unaffected.

---

## Self-Assessment

**Scope:** `Single-Component` — One React module + minor API glue.

**Conf:** `high` — Mirrors existing Manage Tasks UX; sibling tickets define payloads.

**Risk:** `Medium` — Token list drift if API not coordinated with AST-455; mitigated by integration handoff ordering (AST-454 before UI save testing).

---

## Plan vs `ASTRAL_CODE_RULES.md`

| Section | Compliance |
|---------|-------------|
| §3.5 UI stack | Maintain config-driven REST; avoid duplicating resolver logic client-side beyond filtering. |

No conf-!!-NONE.

---

## Revisions / implementation notes

**Stage 3 (token picker):** `AdminTaskPrompts` loads `/api/admin/tasks/meta/tokens` and `/api/admin/tasks/meta/chain_tokens` (AST-455); merges uniquely and sorts A–Z for `TokenTextarea`. If `chain_tokens` responds non-OK, merge uses `meta/tokens` only.

**Preview tabs:** Ordered per parent segments; **`cache_a`** from preview API with legacy **`cache`** fallback for block A only.

---

## Review (implementation stub)

Built by Ada (`dev-ada`). Cherry-pick to **`origin/sub/AST-453/AST-456-explicit-cache-block-references-for-tasks-manage-tasks-seven-segment-ui`**; update hashes after publish.

**Branch:** `sub/AST-453/AST-456-explicit-cache-block-references-for-tasks-manage-tasks-seven-segment-ui`

**Commits:** `1532eaa6c72317efbd4ec5840b1e7466375154f9` (product `feat(AST-456)` on `dev-ada`); commit immediately after **may** carry `docs(AST-456)` plan stub — cherry-pick both when present onto this ref.

## Review

**Diff:** `git diff origin/dev...origin/ftr/AST-456` · **Code tip reviewed (pre-this-doc):** `55ca2cc6fcb8c6b0b973ee02815949b8e10f299a`

### What’s solid

- Seven collapsible editors follow parent ordering (system → cache A–D → no-cache → user); save payload emits all AST-454 fields alongside existing keys (`AdminTaskPrompts.tsx`).
- `mergedAdminTokenAutocomplete` pulls `/tasks/meta/tokens` + `/tasks/meta/chain_tokens`; non-OK chain endpoint gracefully falls back (**Revisions § Stage 3**).
- Preview tabs match backend keys with `previewField()` bridging `cache`→`cache_a` (**AST-455** compatibility).

### Issues

None **fix-now**; no **`src/ui`** `data`/`external` leakage or hardcoded forbidden chain token names (**G1** / registry stays server-side).

### Recommended actions

| Priority | Audience | Action |
|----------|-----------|--------|
| Advisory | UAT | Rotate default expanded panel dropdown across all seven tabs after shipping to confirm persisted `ADMIN_TASK_PROMPTS_DEFAULT_PANEL_LS` stays valid (unknown keys ignored; default panel falls back to **user**, matching `readDefaultEditPanel`). |

---

## Resolution

**Date:** 2026-05-23  

**Versus Radia (`review-astral`, Linear comment thread):**

- **Fix-now:** none (counts 0). No UI code changes needed for this **`resolve-astral`** pass.
- **Advisory:** UAT/default-panel **`readDefaultEditPanel`** persistence spot-check deferred to Susan’s **`prep-uat` / batched smoke** alongside other Manage Tasks regressions (`§ Review` Recommended actions unchanged in product).
- **Plan doc:** Radia’s **`docs(AST-456): Radia review …`** from `origin/ftr/AST-456` (**`64059250`**) merged to `dev-ada`; **`## Resolution`** advances ticket toward **User Testing**. **Publish ref:** **`origin/ftr/AST-456`**. Parent **AST-453**.

