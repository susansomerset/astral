# Admin Score Floor dropdown allows 0 (Remove "pass_threshold" from task_config)

**Linear:** [AST-1278](https://linear.app/astralcareermatch/issue/AST-1278/admin-score-floor-dropdown-allows-0-remove-pass-threshold-from-task)  
**Parent:** [AST-1275](https://linear.app/astralcareermatch/issue/AST-1275/remove-pass-threshold-from-task-config)  
**Publish ref:** `sub/AST-1275/AST-1278-admin-score-floor-dropdown-allows-0`

Restore admin Edit Dispatch Task **Score Floor** so **0.00** is listed and persists on the `dispatch_task` row. On tip, `DISPATCH_SCORE_FLOOR_VALUES` already includes **0.0…10.0** step **0.5**, but Scheduled Actions still hardcodes a React option list starting at **1.00**, and `handleSave` uses `parseFloat(form.score_floor) || 1`, which coerces **0** → **1**. The AST-750 admin metadata route `GET /api/admin/dispatch_tasks/score_floor_options` is missing from `api_admin.py` even though frontend tests already mock it. This ticket rewires the UI to config via that endpoint and fixes zero-save — it does **not** own consult verdict math (AST-1277 / Ada) or canon/docs (AST-1279 / Hedy).

**Verified (plan time):**

- `src/utils/config.py`: `DISPATCH_SCORE_FLOOR_VALUES = tuple(i * 0.5 for i in range(21))` — first **0.0**, last **10.0**; `dispatch_score_floor_option_labels()` present.
- `AdminScheduledActions.tsx` ~320–323: `Array.from({ length: 19 }, (_, i) => (1 + i * 0.5).toFixed(2))` — mins at **1.00**.
- `handleSave` create + edit: `parseFloat(form.score_floor) || 1` — zero falsy coercion.
- `api_admin.py`: no `/dispatch_tasks/score_floor_options` route; `create_dtask` / `update_dtask` already persist numeric **0.0** when the client sends it (`test_update_dispatch_task_scored_zero_score_floor`).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_admin.py` | Import `dispatch_score_floor_option_labels`; add `GET /dispatch_tasks/score_floor_options` | ui |
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Load floor options from API; delete hardcoded `useMemo`; fix zero-save coercion | ui |

**Out of scope (do not touch):**

| File / area | Reason |
|-------------|--------|
| `src/utils/config.py` `DISPATCH_SCORE_FLOOR_VALUES` / labels helper | Already correct on tip (0.0–10.0); no edit unless a stage finds them missing |
| `pass_threshold` / `render_verdict` / consult scoring | Sibling AST-1277 (Ada) |
| Statute / pattern / Code Rules §2.1 retirement | Sibling AST-1279 (Hedy) |
| `dispatch_claim_uses_score_floor`, claim/count SQL, dispatcher floors | Not this AC; eligibility math unchanged |
| `tests/**`, `docs/test-bible/**` | Betty (`qa-child`) |

## Stage 1: Admin API — score_floor_options from config

**Done when:** Authenticated `GET /api/admin/dispatch_tasks/score_floor_options` returns JSON `{"values": ["0.00", "0.50", …, "10.00"]}` (21 strings) sourced from `dispatch_score_floor_option_labels()`; no numeric list hardcoded in `api_admin.py`.

1. Confirm on tip (read-only): `DISPATCH_SCORE_FLOOR_VALUES` and `dispatch_score_floor_option_labels()` exist in `src/utils/config.py` with first value **0.0** / label **`"0.00"`**. If either symbol is missing or the catalog no longer starts at **0.0**, **stop** and comment on the Linear parent — do not invent a parallel catalog in the API or React.

2. In `src/ui/api/api_admin.py`, add `dispatch_score_floor_option_labels` to the existing `src.utils.config` import block (alongside `dispatch_claim_uses_score_floor`).

3. Immediately after `dispatch_task_state_options` (route `/dispatch_tasks/state_options`), add:

   ```python
   @admin_bp.route("/dispatch_tasks/score_floor_options")
   @require_admin
   def dispatch_task_score_floor_options():
       return jsonify({"values": dispatch_score_floor_option_labels()})
   ```

4. Do **not** add create/update validation that rejects floors outside the catalog — existing float coercion on scored rows is enough; backend already accepts **0.0**.

## Stage 2: Scheduled Actions — API options + persist 0

**Done when:** `AdminScheduledActions.tsx` has no client-generated score-floor option array; Score Floor `<select>` (modal and any filter that maps `scoreFloorOptions`) renders API values with **0.00** first; saving **0.00** on a scored row sends JSON `score_floor: 0` (not **1**); reopening edit shows **0.00** selected; table Floor column shows **0.00**; unscored rows still hide Score Floor and send `score_floor: null`.

1. Replace the hardcoded `useMemo` (~lines 320–323):

   ```typescript
   const scoreFloorOptions = useMemo(
     () => Array.from({ length: 19 }, (_, i) => (1 + i * 0.5).toFixed(2)),
     [],
   )
   ```

   with state next to `stateOptions`:

   ```typescript
   const [scoreFloorOptions, setScoreFloorOptions] = useState<string[]>([])
   ```

2. In `loadData`, extend `Promise.all` to fetch floors in parallel:

   ```typescript
   const [tasksRes, keysRes, statesRes, floorsRes] = await Promise.all([
     api("/api/admin/dispatch_tasks"),
     api("/api/admin/dispatch_tasks/task_keys"),
     api("/api/admin/dispatch_tasks/state_options"),
     api("/api/admin/dispatch_tasks/score_floor_options"),
   ])
   ```

   After the existing `statesRes` handling, set:

   ```typescript
   if (floorsRes.ok) {
     const floors = await floorsRes.json()
     setScoreFloorOptions(Array.isArray(floors?.values) ? floors.values : [])
   }
   ```

3. In `handleSave`, replace **both** scored-row `score_floor` expressions (edit PUT and create POST) — today both are `parseFloat(form.score_floor) || 1` — with:

   ```typescript
   score_floor: form.is_scored
     ? (() => {
         const n = parseFloat(form.score_floor)
         return Number.isFinite(n) ? n : 1
       })()
     : null,
   ```

   ⚠️ **Decision:** Use `Number.isFinite` — **not** `|| 1` — so **0.00** persists as **0**. Default **1** only when the form value is missing or non-numeric.

4. Leave unchanged:
   - `{form.is_scored && ( … Score Floor select … )}` gating.
   - Form default / new-row `score_floor: "1.00"`.
   - `openEdit` / table Floor display: `(row.score_floor ?? 1).toFixed(2)` (null → display **1.00**; actual **0** still formats as **0.00**).
   - No client fallback that regenerates 1.00–10.00 if the API fails — empty options until reload (same as empty `stateOptions` on failure).

5. Do **not** edit `tests/**`. Betty owns mocks that already reference `/api/admin/dispatch_tasks/score_floor_options`.

## Stage 3: QA handoff expectations (Betty — not engineer)

**Done when:** Engineer has not committed under `tests/`; Betty’s qa-child can assert catalog / GET / zero-save.

| Area | Expected bible/manifest update |
|------|--------------------------------|
| `tests/component/utils/test_config.py` | Keep/assert `TestAst750DispatchScoreFloorCatalog` — 21 values, first **0.0**, label **`"0.00"`** |
| `tests/component/ui/api/test_api_admin.py` | Assert GET `/api/admin/dispatch_tasks/score_floor_options` returns **`"0.00"`** first, 21 entries; keep zero-persist update test |
| `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` | Mock score_floor_options; assert scored edit save sends `score_floor: 0` when **0.00** selected |

Engineer smoke only: Scheduled Actions → edit a scored row → **0.00** is first option → save **0.00** → reload → Floor column and modal show **0.00**.

## Self-Assessment

**Scope:** `Single-Component` — one admin GET route and one React page; config catalog already present; no core/dispatcher/data changes.

**Conf:** `high` — same shape as AST-750 / `state_options`; backend zero-persist already covered; tip regression is the hardcoded React list plus `|| 1`.

**Risk:** `low` — admin dropdown and save payload only; claim gating and verdict math untouched.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.4 / §2.1 Config as source of truth | Floor option set stays in `DISPATCH_SCORE_FLOOR_VALUES`; UI reads via API ✓ |
| `astral.layers.ui-config-driven-business-logic` | No resurrected hardcoded 1–10 array in React ✓ |
| §1.3 DRY | Single formatter `dispatch_score_floor_option_labels()` ✓ |
| §3.3 Imports | `api_admin` imports utils only; frontend stays UI ✓ |
| §2.6 State machine | No state transitions changed ✓ |
| Engineer test-tree ban | Stages do not touch `tests/` ✓ |

No conflicts requiring `conf-!!-NONE`.

## Review (build)

**Built:** `origin/sub/AST-1275/AST-1278-admin-score-floor-dropdown-allows-0` @ `0c5c5067`

**Product:** Stage 1 — `GET /api/admin/dispatch_tasks/score_floor_options` via `dispatch_score_floor_option_labels()` (`pattern.ui.admin-endpoint`). Stage 2 — Scheduled Actions loads options from that API; `Number.isFinite` save so **0.00** persists. Config catalog already had **0.0** (no `config.py` edit).

**Out of build scope (Betty / qa-child):** Stage 3 table — catalog / GET / zero-save assertions.

## Review (Radia)

[code-rubric] revision=2 — **Overall: CLEAN**

Diff `origin/dev...origin/sub/AST-1275/AST-1278-admin-score-floor-dropdown-allows-0` @ `f409edb3`. Full active-set (64 statutes) scored in-session per code-rubric.v2 §5.0 — no fix-now, no discuss.

**What's solid:**

- Stage 1 + Stage 2 match the plan exactly: route placed immediately after `dispatch_task_state_options`, `Number.isFinite` replaces the falsy `parseFloat(...) || 1` coercion, no resurrected hardcoded 1.00–10.00 array (`astral.standards.no-hardcoded-sets`, `astral.layers.ui-config-driven-business-logic` both conform).
- New route wraps `@require_admin` → `@require_auth` (`astral.idioms.require-auth-on-protected-endpoints` conforms); imports stay `ui → utils` only (`astral.layers.import-direction` conforms).
- Engineer's own commits never touch `tests/` or `docs/test-bible/**` — that content arrives via a single `merge-tests(AST-1278)` SHA from Betty's `origin/tests` line (`astral.git.engineer-test-tree-ban`, `orch.git.betty-merge-tests-one-sha` conform).
- Boundaries held: no `pass_threshold` / `render_verdict` / `config.py` touch (sibling AST-1277/AST-1279 territory).

**Pattern conformance:**

| id | verdict | one-line |
|----|---------|----------|
| `pattern.config.config-block` | conforms | Options sourced from `dispatch_score_floor_option_labels()`; no re-invented catalog. |
| `pattern.ui.admin-endpoint` | conforms | New route cites it in-code; `@require_admin` auth + thin JSON shape, business rule (catalog) resolved server-side. |
| `pattern.dispatch.score-floor` (proposed) | not-applicable | Cited on the parent's "New patterns proposed" list but not yet under `canon/patterns/**` / Archie-approved. Parent text gates on this explicitly ("Archie approval required before implementation depends on the catalog id") — diff does not build against it; code cites the already-approved `pattern.ui.admin-endpoint` instead. Advisory only, not a fix-now invalid citation. |

**Notes:** No Joan plan-rubric verdict attachment on this ticket — noted per C4, not a block.

`context_tokens≈` see Linear comment.

— Radia

## Resolution

**Date:** 2026-08-08  
**Review:** [code-rubric] revision=2 — **CLEAN** (no fix-now, no discuss).  
**Action:** No product changes. Appended this section; tip advanced with `resolve(AST-1278): — clean`.  
**Publish:** `origin/sub/AST-1275/AST-1278-admin-score-floor-dropdown-allows-0` (post-resolve tip).  
**§9a:** dry-run into `origin/dev` clean; dry-run into `origin/ftr/AST-1275-remove-pass-threshold-from-task-config` clean.
