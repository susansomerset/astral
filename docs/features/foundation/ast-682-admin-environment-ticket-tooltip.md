# Admin environment ticket tooltip

**Linear:** [AST-682 — Admin environment ticket tooltip](https://linear.app/astralcareermatch/issue/AST-682/admin-environment-ticket-tooltip-create-a-ticket-log-in-utils)

**Parent:** [AST-675 — Create a ticket log in utils](https://linear.app/astralcareermatch/issue/AST-675/create-a-ticket-log-in-utils) (definition reference only)

**Publish ref:** `origin/sub/AST-675/ast-682-admin-environment-ticket-tooltip` (origin only)

## Summary

When an admin session loads the left nav deploy footer and `ASTRAL_DEPLOY_ENV` is set, hovering the **environment label** shows a native tooltip listing up to **20** most recently landed parent epics (`ticket_id` + formatted timestamp), one per line. Data comes from the existing `merge_tickets` array on `GET /api/deploy_status` (shipped by sibling AST-681). No backend, API, or finish-up changes. Non-admin gating, absent-environment layout, uptime display, and 30s poll interval stay as today (AST-646 / AST-679).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/AdminDeployFooter.tsx` | Extend `DeployStatus` type; format and attach `title` tooltip on environment span | ui |

**Verify only (no change expected):**

| File | Role |
|------|------|
| `src/ui/frontend/src/components/NavigationShell.tsx` | Already renders `<AdminDeployFooter />` only when `isAdmin` — non-admin unchanged (AC 6) |
| `src/utils/deploy_status.py` | Already exposes `merge_tickets` (most recent first) via AST-681 |
| `src/ui/api/api_system.py` | Already returns full payload from `get_deploy_status_payload()` |

**QA manifest (Betty — not engineer commits):** Betty updates `docs/test-bible/**` and frontend component test manifest at **Code Complete** (`qa-child`). Engineer does not commit under `tests/` or `docs/test-bible/**` (pre-commit hook).

**Out of scope:** merge ticket log storage / append tool (AST-681), finish-up wiring (AST-683), new API routes, commit hash fields (removed AST-679), CSS changes, NavigationShell changes.

---

## Stage 1: Environment label tooltip in AdminDeployFooter

**Done when:** With `environment` present in deploy status, the `.nav-deploy-env` span has a `title` attribute containing up to 20 lines of `AST-NNN <formatted timestamp>` separated by `\n`, most recent first; when `environment` is absent the footer renders uptime only with no ticket tooltip; when `merge_tickets` is missing or empty the env label renders without a `title`; uptime and error branches unchanged; `cd src/ui/frontend && npx tsc -b --noEmit` passes.

1. In `src/ui/frontend/src/components/AdminDeployFooter.tsx`, add import:

   ```typescript
   import { fmtTime } from "../lib/fmt"
   ```

2. Extend types at top of file (after existing imports):

   ```typescript
   type MergeTicket = {
     ticket_id: string
     recorded_at: string
   }

   type DeployStatus = {
     environment?: string
     uptime: string
     uptime_seconds: number
     merge_tickets?: MergeTicket[]
   }
   ```

   Remove/replace the existing inline `DeployStatus` type block with the definition above.

3. Add module-level constants and helper **above** the component export (same file, no new module):

   ```typescript
   const MERGE_TICKET_TOOLTIP_LIMIT = 20

   function formatMergeTicketTooltip(mergeTickets: MergeTicket[] | undefined): string | undefined {
     if (!mergeTickets?.length) return undefined
     return mergeTickets
       .slice(0, MERGE_TICKET_TOOLTIP_LIMIT)
       .map(({ ticket_id, recorded_at }) => `${ticket_id} ${fmtTime(recorded_at)}`)
       .join("\n")
   }
   ```

   ⚠️ **Decision:** Slice on the client to 20 even though the API may return full history — parent AC caps display at 20; payload order from AST-681 is already most-recent-first, so `.slice(0, 20)` preserves that order.

   ⚠️ **Decision:** Reuse `fmtTime` from `lib/fmt.ts` so ISO `recorded_at` values from the log render consistently with other admin timestamps (12h, timezone-aware).

   ⚠️ **Decision:** Native `title` attribute with `\n` join — matches the pre-AST-679 commit-message tooltip pattern and satisfies “line breaks between entries” without new CSS or popover components.

4. In the success render branch, on the environment `<span className="nav-deploy-env">` only (not uptime, not footer container), add:

   ```tsx
   title={formatMergeTicketTooltip(status!.merge_tickets)}
   ```

   Full fragment when environment is set:

   ```tsx
   {status!.environment != null && (
     <>
       <span
         className="nav-deploy-env"
         title={formatMergeTicketTooltip(status!.merge_tickets)}
       >
         {status!.environment}
       </span>
       <span className="nav-deploy-sep">·</span>
     </>
   )}
   ```

5. Do **not** change:
   - The 30_000 ms poll interval or `useEffect` fetch logic.
   - Error branch (`Deploy status unavailable`).
   - Early return when `authLoading` or loading state.
   - Uptime span markup or classes.
   - Any file under `src/utils/`, `src/ui/api/`, or `scripts/`.

6. Run compile check:

   ```bash
   cd src/ui/frontend && npx tsc -b --noEmit
   ```

**Ritual:** `code(AST-682): environment label merge-ticket tooltip`

---

## QA expectations (Betty manifest — test-child gate)

Betty should extend frontend component coverage (engineer runs manifest in **test-child**, does not author tests in **build-child**):

| Behavior | Suggested test location |
| --- | --- |
| Env label gets `title` with ticket lines when `merge_tickets` populated | `tests/component/frontend/components/test_AdminDeployFooter.test.tsx` |
| At most 20 lines when API returns >20 entries | same |
| No `title` when `merge_tickets` is `[]` or omitted | same |
| Env absent → no env span / no tooltip; uptime still shown | existing `omits environment label` test — add `merge_tickets` to mock JSON only |
| Non-admin → footer not mounted | `test_NavigationShell.test.tsx` (unchanged gating) |

Suggested manifest pytest gate after Betty lands tests:

```bash
cd src/ui/frontend && npm run test -- --run \
  tests/component/frontend/components/test_AdminDeployFooter.test.tsx \
  tests/component/frontend/components/test_NavigationShell.test.tsx
```

---

## Execution contract (for the developer agent)

The plan is binding. Execute **Stage 1** only. Do not add files beyond `AdminDeployFooter.tsx`. Do not modify backend or tests. When `merge_tickets` shape differs from `{ ticket_id, recorded_at }`, stop and comment on AST-675.

Blocking comment format (parent issue):

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

---

## Self-Assessment

**Scope:** `Single-Component` — One React component (`AdminDeployFooter.tsx`) consumes an existing API field; no utils, API, or shell changes.

**Conf:** `high` — Reuses AST-646 footer fetch, AST-681 `merge_tickets` payload, and established `title` + `fmtTime` patterns; no new libraries or routes.

**Risk:** `low` — Admin-only UI; wrong tooltip text does not affect dispatch, auth, or non-admin nav; worst case is misleading deploy history display.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses `fmtTime`; single helper in component file — no duplicate date logic |
| §2.1 Config | No new config keys; display limit is UI concern (20) per parent AC |
| §3.3 Imports | Frontend-only; `fmtTime` from `lib/fmt` — no layer violations |
| §3.5 Naming | `merge_tickets` matches API key from AST-681; `MERGE_TICKET_TOOLTIP_LIMIT` names the cap |
| §1.5 Logging | N/A — no backend changes |

No conflicts requiring `conf-!!-NONE`.

---

## Review stub (Katherine / build)

**Publish ref:** `origin/sub/AST-675/ast-682-admin-environment-ticket-tooltip`  
**Product commit:** `01dec4cf` (Stage 1 — `AdminDeployFooter.tsx` merge-ticket `title` tooltip via `fmtTime`, cap 20)

---

## Radia review (2026-06-15)

**Diff:** `origin/dev...origin/sub/AST-675/ast-682-admin-environment-ticket-tooltip` @ `989dd99b` (AST-682 product `01dec4cf`, tests `7556b3c1`; branch stacks resolved AST-681)  
**Verdict:** Clean — no fix-now items.

### What's solid

| Check | Result |
|-------|--------|
| Stage 1 plan fidelity | Single-file product change: `AdminDeployFooter.tsx` only — types, `formatMergeTicketTooltip`, `title` on `.nav-deploy-env` |
| AC 4 (20 lines, id + timestamp, line breaks) | `.slice(0, 20)` + `fmtTime(recorded_at)` + `\n` join on native `title` |
| AC 5 (env absent) | Env span not rendered when `environment` unset — no tooltip surface |
| AC 6 (non-admin) | `NavigationShell` gating unchanged; footer still admin-only |
| AC 7 (uptime / poll / error) | 30s poll, error branch, uptime span untouched |
| Empty / missing `merge_tickets` | Helper returns `undefined` → no `title` attribute |
| Tests (Betty manifest) | Tooltip present, empty omits title, 20-line cap, uptime without title |

**Rules:** Frontend-only; `fmtTime` from `lib/fmt` — no layer violations; display cap 20 is UI concern per plan §2.1; no backend/API/finish-up scope smuggled (sibling AST-681 already reviewed).

### Advisory

- Native `title` tooltips are browser-dependent for multiline rendering; acceptable per plan decision (matches pre-AST-679 pattern).

### Recommended actions

None — **resolve-child** may proceed (no product changes required).

---

## Resolution (2026-06-15)

**Publish ref:** `origin/sub/AST-675/ast-682-admin-environment-ticket-tooltip` @ `fbfe4238` (Radia `docs(AST-682): Radia review — clean`)

Radia review clean — no fix-now, discuss, or product changes. Merged `origin/dev`, `origin/ftr/ast-675-create-a-ticket-log-in-utils`, and publish ref on epic worktree `work682`; §9a dry-run clean against `origin/dev` and `origin/ftr/ast-675-create-a-ticket-log-in-utils`. `npx tsc -b --noEmit` passes.

**Outcome:** Admin deploy footer environment label shows up to 20 merge-ticket lines via native `title` tooltip; non-admin and absent-env behavior unchanged.
