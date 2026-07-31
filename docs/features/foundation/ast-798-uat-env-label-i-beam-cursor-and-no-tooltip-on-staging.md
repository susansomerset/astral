<!-- linear-archive: AST-798 archived 2026-07-22 -->

## Linear archive (AST-798)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-798/uat-env-label-i-beam-cursor-and-no-tooltip-on-staging  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-791 — List of UAT issues in environment tooltip is not updating  
**Blocked by / blocks / related:** parent: AST-791

### Description

## What failed

On staging after the AST-792 merge, hovering the admin deploy footer **environment label** shows an **I-beam (text) cursor** over the environment text and **no tooltip** appears. Susan reports this worked on **localhost** before the latest merge.

## Expected

With `ASTRAL_DEPLOY_ENV` set and admin session, hovering the environment label shows **pointer** cursor and, after **0.5 seconds**, a tooltip with up to **20** ticket lines (`AST-NNN` + timestamp) for parents currently in **User Testing** — same AST-691 UX as before this epic.

When no parents qualify, the env label is **non-interactive** (no pointer, no tooltip).

## Repro

1. Log in as admin on **staging** (fresh deploy from current `origin/dev` after AST-791 prep-uat).
2. Open left nav deploy footer; locate the environment label (e.g. `staging`).
3. Hover the environment text for ≥0.5s.
4. **Observed:** I-beam cursor; no tooltip.
5. **Expected:** pointer cursor; tooltip lines when any User Testing parents are on the deploy.

## Parent AC (quoted inline)

> 3. A parent prep-uat'd to staging while in **User Testing** appears in the tooltip with an updated timestamp; re-prep-uat of the same parent updates timestamp only (no duplicate lines).

> 6. When no logged parents are in **User Testing**, the env label is non-interactive (same as AST-691 empty-list behavior).

## Boundaries

* Does **not** change User Testing filter semantics or Linear client behavior unless required to restore tooltip UX.
* Does **not** re-scope AST-792 backend filter — fix the staging/admin hover regression only.

### Comments

#### radia — 2026-06-25T01:35:35.108Z
### Radia review — AST-798

**Diff:** `origin/dev...origin/sub/AST-791/ast-798-uat-env-label-i-beam-cursor-and-no-tooltip-on-staging` @ `2306d71`
**Doc:** `docs/features/foundation/ast-798-uat-env-label-i-beam-cursor-and-no-tooltip-on-staging.md` (§ Radia review)

**What's solid**
- `_resolve_linear_api_key()` with rollcall env precedence (`LINEAR_API_KEY` → `LINEAR_KEY_CHUCKLES` → `LINEAR_KEY_CURSOR`); missing all → `LinearApiError("Linear API key not configured")` — core fail-closed unchanged.
- CSS: `.nav-deploy-env { cursor: default; user-select: none; }`; interactive class still `pointer`.
- `src/` scope clean: `linear.py`, `App.css`, `env.example` only.
- Betty manifest: key resolution tests + AdminDeployFooter static-env coverage.

**advisory:** Frontend test asserts App.css source contract instead of `getComputedStyle` cursor — adequate, slightly below plan wording.

**fix-now:** none
**discuss:** none

**Susan manual:** confirm Railway staging has at least one Linear env var before UAT (plan § Manual verify).

#### betty — 2026-06-25T01:34:06.632Z
## QA test manifest (AST-798)

**Publish:** `origin/sub/AST-791/ast-798-uat-env-label-i-beam-cursor-and-no-tooltip-on-staging` @ `ce78bfa` (`merge-tests(AST-798): origin/tests ca81fd0`)

**Scope:** Linear API key env precedence (`_resolve_linear_api_key`) + static env label CSS (`cursor: default; user-select: none`). No AST-792 filter or AdminDeployFooter logic changes.

### Manifest (test-child)

1. **Linear key resolution** — `tests/component/external/test_linear.py::TestResolveLinearApiKey` (3 tests): prefers `LINEAR_API_KEY`, falls back to `LINEAR_KEY_CHUCKLES`, raises `LinearApiError` when all unset.

2. **Static env cursor (CSS contract)** — `tests/component/frontend/components/test_AdminDeployFooter.test.tsx` — extend **`test_renders_static_environment_span_when_merge_tickets_empty_or_missing`**: `nav-deploy-env` class, no `nav-deploy-env-interactive`, App.css source regex for `cursor: default` + `user-select: none` on `.nav-deploy-env`.

```bash
.venv/bin/python -m pytest tests/component/external/test_linear.py -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_AdminDeployFooter.test.tsx
```

**Pass criterion:** pytest + Vitest green on manifest — not zero-arg harness / branch-lock gate.

**Manual UAT (Susan):** set `LINEAR_API_KEY` / `LINEAR_KEY_CHUCKLES` / `LINEAR_KEY_CURSOR` on Railway staging; hover env label ≥0.5s → pointer + `AST-791` tooltip line.

**Bible shasums (`origin/sub/...` @ `ce78bfa`):**
- `docs/test-bible/external/linear.md`: `c434106945877c5c24c34db7496b1aa50b006e0eb852c4d52e8e39f1e82bb148`
- `docs/test-bible/frontend/components.md`: `776c57ef4cae76ed3b22b523ed484af7ba28463e688a3749568874c64051cfd3`

— Betty

#### ada — 2026-06-25T01:28:13.617Z
Plan doc: [ast-798-uat-env-label-i-beam-cursor-and-no-tooltip-on-staging.md](https://github.com/susansomerset/astral/blob/sub/AST-791/ast-798-uat-env-label-i-beam-cursor-and-no-tooltip-on-staging/docs/features/foundation/ast-798-uat-env-label-i-beam-cursor-and-no-tooltip-on-staging.md)

**Scope:** `scope-minor` — Linear API key env precedence in `external/linear.py` plus default-cursor CSS on static env label; no AST-792 filter or AdminDeployFooter logic changes.

**Conf:** `high` — Staging empty `merge_tickets` from missing `LINEAR_API_KEY` matches AST-693/692 pattern; rollcall env names are established; AST-691 defines default vs I-beam cursor.

**Risk:** `risk-low` — Tooltip still empty if Railway env unset after deploy; CSS fix is cosmetic for empty state only.

Two product stages + Betty manifest; Susan must set Linear key on Railway staging for tooltip content.

---

# UAT: env label I-beam cursor and no tooltip on staging

**Linear:** [AST-798 — UAT: env label I-beam cursor and no tooltip on staging](https://linear.app/astralcareermatch/issue/AST-798/uat-env-label-i-beam-cursor-and-no-tooltip-on-staging)

**Parent:** [AST-791 — List of UAT issues in environment tooltip is not updating](https://linear.app/astralcareermatch/issue/AST-791/list-of-uat-issues-in-environment-tooltip-is-not-updating) (AC reference only)

**Publish ref:** `origin/sub/AST-791/ast-798-uat-env-label-i-beam-cursor-and-no-tooltip-on-staging` (origin only)

## Summary

After AST-792 landed on staging, Susan sees an **I-beam (text) cursor** on the admin deploy footer environment label and **no hover tooltip**. Localhost worked because `.env` had a Linear API key; staging does not set `LINEAR_API_KEY`, so AST-792’s fail-closed path returns `merge_tickets: []` even though `data/merge_ticket_log.json` on `origin/dev` contains **AST-791** (parent in **User Testing**). The frontend correctly omits `nav-deploy-env-interactive` when the array is empty, but monospace footer text still renders the I-beam cursor (AST-691 regression class of bug).

This bug restores staging tooltip UX: resolve Linear API credentials on the deploy runtime (team-standard env names) so the AST-792 filter can return **AST-791**, and set explicit **default** (non–I-beam) cursor on the static env label.

⚠️ **Decision:** Add `_resolve_linear_api_key()` in `src/external/linear.py` — try `LINEAR_API_KEY`, then `LINEAR_KEY_CHUCKLES`, then `LINEAR_KEY_CURSOR` (first non-empty), same precedence as `scripts/git/create-dev-pr.py` / rollcall. Missing all three → raise `LinearApiError("Linear API key not configured")` (core still fail-closed to `merge_tickets: []`). Does **not** weaken User Testing filter semantics or return unfiltered log rows.

⚠️ **Decision:** CSS-only cursor fix on `.nav-deploy-env` — `cursor: default; user-select: none;` so empty/non-interactive state matches AST-691 “default cursor, not I-beam”. Interactive state keeps `nav-deploy-env-interactive { cursor: pointer; }`.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/external/linear.py` | Add `_resolve_linear_api_key()`; use in `_graphql`; raise `LinearApiError` when unset | external |
| `src/ui/frontend/src/App.css` | `.nav-deploy-env`: `cursor: default; user-select: none;` | ui |
| `env.example` | Note alternate env names (`LINEAR_KEY_CHUCKLES`, `LINEAR_KEY_CURSOR`) for Railway | docs |
| `tests/component/external/test_linear.py` | Tests for key resolution order + missing-key `LinearApiError` (Betty manifest) | test |
| `tests/component/frontend/components/test_AdminDeployFooter.test.tsx` | Assert non-interactive env uses default cursor class/styles (Betty manifest) | test |

**Verify only (no change expected):**

| File | Role |
|------|------|
| `src/core/deploy_status.py` | Fail-closed filter unchanged; benefits once Linear key resolves |
| `src/ui/frontend/src/components/AdminDeployFooter.tsx` | Hover/tooltip logic unchanged |
| `data/merge_ticket_log.json` on `origin/dev` | Already contains **AST-791** after prep-uat |

**Out of scope:** AST-792 filter logic changes; Chuckles skill updates; Railway dashboard provisioning (Susan sets env on staging service — verify in manual step below).

---

## Stage 1: Linear API key resolution (external)

**Done when:** `_graphql` uses first available key from team env list; `fetch_parent_issue_states(["AST-791"])` succeeds when any listed env var is set; missing all keys raises `LinearApiError` with message containing `not configured`; `python3 -m py_compile src/external/linear.py` passes.

1. In `src/external/linear.py`, add module constant and helper after imports:

   ```python
   _LINEAR_KEY_ENVS = ("LINEAR_API_KEY", "LINEAR_KEY_CHUCKLES", "LINEAR_KEY_CURSOR")

   def _resolve_linear_api_key() -> str:
       for name in _LINEAR_KEY_ENVS:
           value = os.environ.get(name, "").strip()
           if value:
               return value
       raise LinearApiError("Linear API key not configured")
   ```

2. In `_graphql`, replace `os.environ["LINEAR_API_KEY"]` with `_resolve_linear_api_key()` in the `Authorization` header.

3. Do **not** change `fetch_parent_issue_states` GraphQL query, filter logic in core, or fail-closed behavior in `src/core/deploy_status.py`.

4. `python3 -m py_compile src/external/linear.py`

**Ritual:** `code(AST-798): resolve Linear API key env precedence for deploy status`

---

## Stage 2: Non-interactive env label cursor (CSS)

**Done when:** `.nav-deploy-env` has `cursor: default` and `user-select: none`; `.nav-deploy-env-interactive` still sets `cursor: pointer`; `cd src/ui/frontend && npx tsc -b --noEmit` passes.

1. In `src/ui/frontend/src/App.css`, update `.nav-deploy-env` block (keep existing color/transform rules):

   ```css
   .nav-deploy-env {
     color: var(--text-secondary);
     text-transform: lowercase;
     cursor: default;
     user-select: none;
   }
   ```

2. Confirm `.nav-deploy-env-interactive { cursor: pointer; }` remains unchanged (wins when interactive).

3. In `env.example`, extend the Linear block comment:

   ```bash
   # First non-empty wins: LINEAR_API_KEY, LINEAR_KEY_CHUCKLES, LINEAR_KEY_CURSOR
   # Required on Railway staging for admin deploy footer UAT tooltip (AST-792/798)
   LINEAR_API_KEY=your_linear_api_key_here
   ```

4. `cd src/ui/frontend && npx tsc -b --noEmit`

**Ritual:** `code(AST-798): default cursor on static deploy env label`

---

## Stage 3: Component tests (Betty manifest — engineer runs in test-child)

**Done when:** Betty manifest passes; key resolution and cursor behavior covered.

1. **`tests/component/external/test_linear.py`** — add:
   - `test_resolve_linear_api_key_prefers_linear_api_key` — set only `LINEAR_API_KEY`
   - `test_resolve_linear_api_key_falls_back_to_chuckles_key` — unset `LINEAR_API_KEY`, set `LINEAR_KEY_CHUCKLES`
   - `test_fetch_raises_linear_api_error_when_no_key` — clear all three env vars; expect `LinearApiError` with `not configured`

2. **`tests/component/frontend/components/test_AdminDeployFooter.test.tsx`** — extend `test_renders_static_environment_span_when_merge_tickets_empty_or_missing`:
   - Assert env span has **no** `nav-deploy-env-interactive` class (existing)
   - Assert computed style `cursor` is `default` (not `text`) on the env span when merge_tickets empty

3. Pytest gate:

   ```bash
   .venv/bin/python -m pytest tests/component/external/test_linear.py -q

   cd src/ui/frontend && npm run test:component -- \
     ../../../tests/component/frontend/components/test_AdminDeployFooter.test.tsx
   ```

**Ritual:** `test(AST-798): Linear key resolution and static env cursor coverage`

---

## Manual verify (Susan — staging UAT)

After **prep-uat** redeploy from `origin/dev` with this fix:

1. Confirm Railway **staging** service has at least one of: `LINEAR_API_KEY`, `LINEAR_KEY_CHUCKLES`, or `LINEAR_KEY_CURSOR` (same key used by Chuckles rollcall).
2. Admin login on staging → hover env label ≥0.5s.
3. **Expected:** pointer cursor; tooltip line `AST-791 {timestamp}` (parent in **User Testing**, logged on deploy).

If tooltip still empty after deploy, check `GET /api/deploy_status` JSON for `merge_tickets` — empty with log on disk means Linear key still missing on Railway.

---

## Execution contract (for the developer agent)

Execute stages in order. Do not change AST-792 filter rules, AdminDeployFooter hover timing, or tooltip line format.

Blocking questions use parent **AST-791** with:

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

---

## Self-Assessment

**Scope:** `scope-minor` — One external helper + env.example note + two CSS properties; no core/UI component logic changes.

**Conf:** `high` — Root cause matches AST-693/692 staging pattern; rollcall env precedence is established; AST-691 documents default vs I-beam cursor expectation.

**Risk:** `risk-low` — Worst case is unchanged empty tooltip if Railway env still unset; CSS cursor fix is cosmetic-only for empty state.

---

## Self-review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses team Linear key env list pattern from rollcall / create-dev-pr |
| §2.1 config | Keys remain env secrets; no new config.py block |
| §3.3 imports | external → stdlib only; ui CSS only |
| §3.5 naming | `_resolve_linear_api_key`, existing class names unchanged |

No conflicts requiring `conf-!!-NONE`.

---

## Revisions

*(none — initial FIX-UAT plan)*

---

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-791/ast-798-uat-env-label-i-beam-cursor-and-no-tooltip-on-staging`

**Product commits:** `b4cb30e` (Linear API key env precedence), `1ed038b` (default cursor CSS + env.example)

**Note for Betty (Stage 3):** Component tests per plan Stage 3 — manifest at Code Complete.

---

## Radia review (2026-06-25)

**Diff:** `origin/dev...origin/sub/AST-791/ast-798-uat-env-label-i-beam-cursor-and-no-tooltip-on-staging` @ `ce78bfa`  
**Product commits:** `b4cb30e`, `1ed038b`, `ca81fd0` (tests)

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity (Stages 1–2) | `_resolve_linear_api_key()` with rollcall env precedence; `_graphql` uses helper; missing all keys → `LinearApiError("Linear API key not configured")` (core fail-closed path unchanged). CSS `cursor: default; user-select: none` on `.nav-deploy-env`; interactive class untouched. |
| Root-cause fix | Replaces hard `os.environ["LINEAR_API_KEY"]` (KeyError) with team-standard env names so staging can use `LINEAR_KEY_CHUCKLES` / `LINEAR_KEY_CURSOR` without weakening AST-792 UAT filter. |
| Layer compliance (§3.3) | external stdlib-only; CSS-only ui change; no core/component logic edits. |
| Scope boundaries | `src/` diff is `linear.py` + `App.css` + `env.example` only. AST-796 test/bible rows arrived via `merge-tests` (no sibling product on this ref). |
| Self-Assessment | Stated `scope-minor` / `high` conf matches footprint. |
| Tests | `TestResolveLinearApiKey` (3 cases) + AdminDeployFooter static-env assertions per Betty manifest. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **advisory** | `test_AdminDeployFooter.test.tsx` | Plan Stage 3 asked for computed `cursor` style on the env span; test asserts **App.css source** contains `cursor: default` / `user-select: none` instead of `getComputedStyle`. Contract coverage is adequate; slightly weaker than plan wording. |

### Recommended actions

| Action | Owner |
|--------|-------|
| None required for resolve | — |
| Optional: swap CSS file assertion for `getComputedStyle(envLabel).cursor === 'default'` | Engineer |
| Manual: confirm Railway staging has one of the three Linear env vars (plan § Manual verify) | Susan |

---

## Resolution (2026-06-25)

**Publish ref:** `origin/sub/AST-791/ast-798-uat-env-label-i-beam-cursor-and-no-tooltip-on-staging` @ `2306d71` (Radia `docs(AST-798): Radia review — clean`)

Radia review clean — no fix-now or discuss items. No product code changes. Advisory CSS source-contract test left as Betty shipped. §9a dry-run clean vs `origin/dev` and `origin/ftr/ast-791-list-of-uat-issues-in-environment-tooltip-is-not-updating`.

**Outcome:** Linear key env precedence + static env default cursor ready for Susan staging UAT (Railway must expose at least one rollcall Linear env var for tooltip content).
