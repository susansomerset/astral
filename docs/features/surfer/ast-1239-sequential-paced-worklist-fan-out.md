# AST-1239 — Sequential paced worklist fan-out

**Linear:** [AST-1239](https://linear.app/astralcareermatch/issue/AST-1239/sequential-paced-worklist-fan-out-human-paced-fan-out-over-the-batch)
**Parent:** [AST-1174](https://linear.app/astralcareermatch/issue/AST-1174/human-paced-fan-out-over-the-batch-worklist) — Human-paced fan-out over the batch worklist
**Publish ref:** `origin/sub/AST-1174/AST-1239-sequential-paced-fan-out`

In the extension background context, walk the server Surfer worklist **one URL at a time**: fresh-open a tab, wait for load settle, `dwell()` via AST-1236, capture visible text, post under the batch id (delivery only), close the tab, continue. Never exceed `createTabBudget` / `max_tabs`. On every loop iteration (including after worker death), ask the server what remains — never trust worker memory. A bad load / empty capture records a failure outcome and the run moves on. No catch-up after a slow page; pauses are ordinary timers (`dwell()`), not `chrome.alarms`. Does **not** own pacing config/`dwell()` (AST-1236), progress/cancel UI (AST-1176), resume prompt (AST-1177), remaining-work / batch-scoped HTTP (AST-1231), or the WXT shell (AST-1170).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/extension/src/lib/fanOut.ts` | New: `runPacedFanOut` sequential loop + port types; uses AST-1236 `dwell` / `fetchPacingConfig` / `createTabBudget` | ui |

**No changes expected:** `src/utils/config.py`, `src/ui/api/api_surfer.py` (pacing GET stays AST-1236; remaining-work + batch page routes stay **AST-1231**), `src/core/surfer.py` / `page_intake` (AST-1169 / AST-1168), WXT `package.json` / entrypoints / manifest (**AST-1170**), progress/cancel UI (**AST-1176**), resume prompt (**AST-1177**), `tests/` / bible (Betty after Code Complete).

⚠️ **Decision — land `src/lib/fanOut.ts` even if AST-1170 scaffold is not yet on this branch:** Same placement rule as AST-1236. Create only the planned lib file under settled `src/ui/extension/src/lib/`. Do **not** invent `package.json`, WXT config, `entrypoints/`, or background wiring. AST-1170 imports `runPacedFanOut` and supplies the ports. If at build time the path conflicts with an already-merged AST-1170 layout (different `src/` nesting), **stop and comment on the parent** — do not relocate silently.

⚠️ **Decision — extension-only product diff; no new Flask routes on this ticket:** Remaining-work answers and batch-scoped page posts are **AST-1231**. Two-phase intake envelope is **AST-1228**. This ticket is the first **consumer** of those contracts plus AST-1236 pacing. Inventing parallel server endpoints here would violate in-scope-only and steal Katherine's ticket.

⚠️ **Decision — injectable ports, not hardcoded Astral base URL / chrome globals inside the loop module:** Mirror AST-1236 `fetchPacingConfig(getJson)`. Auth, host, `browser.tabs` / messaging, and content-script capture live in the shell (**AST-1170**). `fanOut.ts` receives a `FanOutPorts` object so the loop stays testable and does not bake a second API client.

## AC verification ownership

Which child ACs this ticket's diff can exercise vs inherit:

| AC | Ownership | Verifiable on AST-1239 diff alone? |
|----|-----------|--------------------------------------|
| 1 visit once / post / close | Loop + ports | **Partial** — unit/stub: open→dwell→post→close order; full multi-URL needs AST-1231 remaining + AST-1170 tabs |
| 2 no double-fetch after SW kill | Loop re-asks remaining + liveness set | **Partial** — liveness/`no_progress` on this diff; real SW kill needs AST-1170 |
| 3 bad page records outcome, continues | `reportUrlFailure` + loop continues | **Partial** — failure branch on this diff; persistence needs AST-1231 |
| 4 batch reaches completed on outcomes | Server auto-complete (AST-1231 / surfer core) | **Deferred** — loop must **not** await `COMPLETED`; Betty/UAT after AST-1231 |
| 5 Style D on server post path | AST-1231 handlers; this ticket only forwards `debug` | **Deferred** — do not chase client-side logging |
| 6 SW survives configured dwell | Ordinary `dwell()` under MV3 idle; shell hosts the timer | **Deferred** — needs AST-1170 background + live dwell |
| 7 mid-pause kill loses only in-flight page | No worker cursor; remaining still lists pending | **Deferred** — needs AST-1170 re-entry; loop contract supports it |

Do **not** tick Linear AC4 from the loop's `exhausted` exit. Do **not** invent client Style D for AC5.

## Pre-build dependency gate (before Stage 1 code)

**Done when:** Builder can name the live AST-1231 symbols that satisfy the **Consumer contract** below (or confirm provisional paths still match a published AST-1231 plan on `origin/sub/AST-1169/AST-1231-batch-scoped-intake`).

1. Confirm AST-1236 helpers exist at:
   - `src/ui/extension/src/lib/dwell.ts` → `dwell`
   - `src/ui/extension/src/lib/pacingConfig.ts` → `fetchPacingConfig`, `createTabBudget`, `getPacingConfig`
2. Confirm sibling HTTP ownership:
   - **AST-1231** owns batch-scoped post + remaining-work query (+ per-URL `debug=` Style D on that path).
   - **AST-1170** owns authenticated `getJson` / `postJson`, tab open/close/load-wait, and visible-text capture via content-script messaging.
3. **Failure `reason` vocabulary (agree with AST-1231 before inventing more):** Client sends only:
   - `empty_capture` — whitespace-only / missing capture
   - `page_error` — non-Error throw, or catch fallback when message is empty
   - `page_error:<detail>` — when `err instanceof Error` and `message` is non-empty: prefix + first **`FAN_OUT_FAILURE_DETAIL_MAX = 200`** characters of `err.message` (named constant in `fanOut.ts`, not a bare `200`)
   If AST-1231 validates/stores/groups on `reason` with a different enum → **STOP** and align; do not mint additional client strings.
4. If AST-1231 has published a plan or code whose remaining/post/fail shapes **differ** from the Consumer contract below → **STOP**, comment on **AST-1239** (not parent) with the delta, and wait — do not invent a second client vocabulary and do not implement AST-1231 routes here.
5. If AST-1231 has **no** published plan/code yet at build time → still implement `fanOut.ts` against the Consumer contract ports (shell can stub); do **not** add server routes. Full end-to-end AC verification waits on AST-1231 + AST-1170 landing (UAT / integration), which is expected for this epic ordering. Stubs that resolve without recording progress must trip the per-run liveness guard (`no_progress`) rather than loop forever.

### Consumer contract (ports — provisional until AST-1231 freezes paths)

These are the **TypeScript port shapes** `runPacedFanOut` requires. HTTP path strings are the **preferred** names when AST-1231 lands routes on `surfer_bp` (`/api/surfer/...`); if AST-1231 chooses different paths, only the **shell adapter** changes — not the loop logic — unless field semantics change (then STOP per gate §3).

```typescript
/** Outstanding visits = URLs still `pending` (never visited). */
export type RemainingWork = {
  batch_id: string;
  status: string; // e.g. RUNNING — informational; loop does not transition batch status
  remaining_urls: string[]; // pending only — must NOT include delivered / success / failed
  done_count: number; // terminal URL outcomes (success + failed)
  total_count: number;
};

/** Successful post = delivery ack only — never treat as URL success / batch complete. */
export type PageDeliveryAck = {
  ok: true;
  // optional echo fields allowed; loop must ignore classification / terminal outcome
};

export type FanOutPorts = {
  /** Authenticated GET helper (AST-1170). Used for pacing_config + remaining. */
  getJson: <T>(path: string) => Promise<T>;
  /**
   * Preferred remaining-work path (AST-1231):
   *   GET /api/surfer/batches/<batch_id>/remaining
   * Must derive remaining_urls from server state alone (no client list).
   */
  fetchRemaining: (batchId: string) => Promise<RemainingWork>;
  /**
   * Preferred batch-scoped page post (AST-1231 / two-phase intake):
   *   POST body includes batch_id + page_url + captured text/html
   * Returns when delivery is recorded (`delivered`) — classification may still be open.
   */
  postPage: (args: {
    batchId: string;
    pageUrl: string;
    pageText: string;
    debug?: boolean;
  }) => Promise<PageDeliveryAck>;
  /**
   * Record a terminal `failed` outcome without a successful post
   * (load error / empty capture). Preferred:
   *   POST /api/surfer/batches/<batch_id>/urls/fail  { url, reason }
   * or equivalent AST-1231 surface that writes URL outcome `failed`.
   */
  reportUrlFailure: (args: {
    batchId: string;
    pageUrl: string;
    reason: string;
    debug?: boolean;
  }) => Promise<void>;
  /** Fresh tab per URL (Joan / parent OQ1). Returns tab id. */
  openTab: (url: string) => Promise<number>;
  /** Wait until the tab has finished loading (settle) before dwell. */
  waitForLoad: (tabId: number) => Promise<void>;
  /** Visible text (or culled markup later via AST-1172) from the tab. */
  captureVisibleText: (tabId: number) => Promise<string>;
  /** Close the tab opened for this URL. Idempotent if already closed. */
  closeTab: (tabId: number) => Promise<void>;
};
```

⚠️ **Decision — `remaining_urls` = pending only:** Re-fetching a `delivered` URL would violate AC2 (no URL fetched twice) and claim-process-release intent. Delivered-but-unclassified stays non-terminal for **batch** completion (server / AST-1231) but is **not** a visit target. If AST-1231's remaining endpoint returns all non-terminal URLs including `delivered`, the adapter in AST-1170 (or a one-line filter documented in a plan amend) must strip non-`pending` before the loop — prefer AST-1231 returning pending-only so the loop stays dumb.

⚠️ **Decision — fan-out exits when `remaining_urls` is empty; it does not await batch `COMPLETED`:** Parent AC7 / child AC4: completion tracks outcomes, which may resolve shortly after the last tab closes (two-phase intake). The loop's job is visits + delivery/failure recording. Polling for `COMPLETED` would daisy-chain classification into the run (`astral.state.no-daisy-chain-in-run`) and is out of scope.

## Stage 1: `runPacedFanOut` module

**Done when:** `src/ui/extension/src/lib/fanOut.ts` exists with the exports and control flow below; it imports `dwell`, `fetchPacingConfig`, and `createTabBudget` from the AST-1236 modules; it contains **no** `chrome.alarms` / `browser.alarms`, **no** inline `setTimeout`/`setInterval` for pacing (only `dwell()`), **no** hardcoded dwell seconds / max_tabs literals, **no** Flask/Python files, and **no** WXT entrypoints; a fresh open→close happens per URL; `createTabBudget` wraps each in-flight page; worker-memory URL lists are never used as the source of truth; per-run `recordedThisRun` stops with `no_progress` if the server re-offers a URL already recorded this invocation.

1. Create `src/ui/extension/src/lib/fanOut.ts` with the port types from the Consumer contract (can live in the same file — do not add a second types-only file unless the file exceeds ~250 lines and readability suffers; prefer one file).

2. Export:

```typescript
import { dwell } from "./dwell";
import { createTabBudget, fetchPacingConfig } from "./pacingConfig";

export type { RemainingWork, PageDeliveryAck, FanOutPorts }; // as defined above

export type RunPacedFanOutResult = {
  batchId: string;
  visited: number; // successful delivery posts
  failed: number; // reportUrlFailure calls
  /** exhausted = no pending left; empty_batch = total_count 0; no_progress = server re-offered a URL this run already recorded */
  stoppedReason: "exhausted" | "empty_batch" | "no_progress";
};

/**
 * Sequential paced fan-out over server remaining work (AST-1239 / AST-1174).
 * Caller (AST-1170 background) supplies ports. This function does not read
 * chrome.* itself and does not keep a durable URL cursor in worker memory.
 */
export async function runPacedFanOut(
  batchId: string,
  ports: FanOutPorts,
  opts?: { debug?: boolean },
): Promise<RunPacedFanOutResult> {
  // implementation per steps 3–8
}
```

3. **Start of run — load pacing, create budget (once):**

```typescript
const id = (batchId || "").trim();
if (!id) throw new Error("runPacedFanOut: batchId is required");

await fetchPacingConfig(ports.getJson);
const budget = createTabBudget(); // uses getPacingConfig().max_tabs (ships at 1)
let visited = 0;
let failed = 0;
/** Per-run liveness only — not a durable resume cursor (AC7 still re-asks the server). */
const recordedThisRun = new Set<string>();
const FAN_OUT_FAILURE_DETAIL_MAX = 200;
```

Do **not** snapshot a URL list into a local array that outlives one iteration. `recordedThisRun` is only a liveness assertion that this invocation already posted or failed a URL; it is discarded when the function returns.

4. **Loop — server truth every iteration:**

```typescript
while (true) {
  const remaining = await ports.fetchRemaining(id);
  const nextUrl = (remaining.remaining_urls || [])[0];
  if (!nextUrl) {
    return {
      batchId: id,
      visited,
      failed,
      stoppedReason: remaining.total_count === 0 ? "empty_batch" : "exhausted",
    };
  }
  // Liveness: if the server still offers a URL this run already delivered or failed,
  // stop — do not re-open it (bot-shaped infinite loop / AC2). Conforming AST-1231
  // never hits this; stubs that resolve without recording do.
  if (recordedThisRun.has(nextUrl)) {
    return { batchId: id, visited, failed, stoppedReason: "no_progress" };
  }

  await budget.acquire();
  let tabId: number | null = null;
  try {
    tabId = await ports.openTab(nextUrl);
    await ports.waitForLoad(tabId);
    await dwell(); // ordinary timer only — never alarms; no inter-page second pause
    const pageText = await ports.captureVisibleText(tabId);
    if (!pageText || !pageText.trim()) {
      await ports.reportUrlFailure({
        batchId: id,
        pageUrl: nextUrl,
        reason: "empty_capture",
        debug: opts?.debug,
      });
      recordedThisRun.add(nextUrl);
      failed += 1;
    } else {
      await ports.postPage({
        batchId: id,
        pageUrl: nextUrl,
        pageText,
        debug: opts?.debug,
      });
      // Delivery only — do NOT treat ack as URL success / batch complete.
      recordedThisRun.add(nextUrl);
      visited += 1;
    }
  } catch (err) {
    const detail =
      err instanceof Error ? err.message.trim().slice(0, FAN_OUT_FAILURE_DETAIL_MAX) : "";
    const reason = detail ? `page_error:${detail}` : "page_error";
    await ports.reportUrlFailure({
      batchId: id,
      pageUrl: nextUrl,
      reason,
      debug: opts?.debug,
    });
    recordedThisRun.add(nextUrl);
    failed += 1;
  } finally {
    if (tabId != null) {
      try {
        await ports.closeTab(tabId);
      } catch {
        // best-effort close — do not abort the batch on close failure
      }
    }
    budget.release();
  }
  // No catch-up: next iteration only after this page fully finishes (incl. dwell).
}
```

⚠️ **Decision — per-run `recordedThisRun` liveness guard (Joan fix-now):** Not a retry policy and not a durable cursor. After a successful `postPage` or `reportUrlFailure`, add the URL. If the next `fetchRemaining` still leads with that URL, return `stoppedReason: "no_progress"`. On a conforming AST-1231 this never fires; on a non-recording stub it converts an invisible infinite paced re-visit into one loud exit (protects AC2 + stealth).

⚠️ **Decision — order is open → settle (`waitForLoad`) → `dwell()` → capture → post/fail → close:** Matches parent Functional scope (Susan: dwell is the only pause; no separate inter-page delay). Do not dwell before load settle (that would burn the human pause on a spinner). Do not capture before dwell (stealth contract is "look at it").

⚠️ **Decision — fresh `openTab` + `closeTab` per URL:** Parent OQ1 answered by Joan — not one reused tab navigated in sequence.

⚠️ **Decision — failure path always goes through `reportUrlFailure`:** Load errors and empty capture must become a terminal URL outcome on the server so the URL is not retried forever after wake (AC3) and so auto-complete can eventually fire (AC4). Do **not** swallow errors and skip recording. Do **not** call `postPage` with empty text as a substitute unless AST-1231 explicitly documents empty-body → `failed` (prefer the dedicated fail port).

⚠️ **Decision — `createTabBudget.acquire` before open and `release` in `finally`:** Honors AST-1236 one-at-a-time contract even if a future config raises `max_tabs` (Susan sign-off). With shipped `max_tabs: 1`, two pages cannot be in flight. Do not open the next tab before `release`.

⚠️ **Decision — no worker-memory resume cursor:** After SW death mid-pause, the in-flight page is lost; on next wake the shell calls `runPacedFanOut` again and `fetchRemaining` still lists that URL as pending (AC7). Do not store "current index" in `chrome.storage` in this ticket (resume UX is AST-1177; in-flight continuation after explicit re-entry is "ask the server").

5. **Usable text rule:** Treat capture as unusable when the string is missing, empty, or whitespace-only (`!pageText.trim()`). Do not invent additional heuristics (boilerplate detectors, min length floors, language checks) in this ticket — those would be product judgment belonging elsewhere.

6. **Debug:** Pass `opts?.debug` through to `postPage` / `reportUrlFailure` only. Do **not** add Style D / `debug_index` logging in the extension (server path owns AC5 / child AC5 when `debug=True` on the post/fail handlers from AST-1231). Do not log full page bodies from the client.

7. **Forbidden in this file:**
   - `chrome.alarms` / `browser.alarms`
   - Inline pacing `setTimeout` / `setInterval` (only `dwell()` may sleep for pacing)
   - Hardcoded `10`, `5`, `15`, `1` for pacing / max tabs
   - Local durable queue copied from the first `fetchRemaining` and walked without re-fetch
   - Marking URL/`batch` success because `postPage` returned
   - Toasts / progress UI / cancel flags / resume prompts
   - Re-deriving URLs from a search page DOM
   - Importing React or frontend app modules

8. **Verify Stage 1 by eye / compile hygiene** (no Vitest project may exist until AST-1170 — same as AST-1236):

```bash
test -f src/ui/extension/src/lib/fanOut.ts
rg -n 'chrome\.alarms|browser\.alarms|setInterval' src/ui/extension/src/lib/fanOut.ts
# expect no matches for alarms/setInterval
rg -n 'from \"\./dwell\"|from \"\./pacingConfig\"|runPacedFanOut|createTabBudget|fetchRemaining|reportUrlFailure|recordedThisRun|no_progress|FAN_OUT_FAILURE_DETAIL_MAX' src/ui/extension/src/lib/fanOut.ts
# expect imports + exports + liveness + named reason max present
```

**Ritual:** `code(AST-1239): sequential paced fan-out loop`

## Stage 2: Shell wiring note (documentation-only in plan — no code in this ticket)

**Done when:** Plan documents how AST-1170 must call the loop; **no files changed in this stage**.

AST-1170 background, after a search-page intake returns a `batch_id` (AST-1230 / AST-1231 surface), starts:

```typescript
await runPacedFanOut(batchId, ports, { debug });
```

Re-entry after worker death (without AST-1177 prompt) for an already in-flight batch the shell chooses to continue: same call — `fetchRemaining` supplies the next pending URL. AST-1177 later owns asking the candidate; this ticket only requires that re-invoking the loop is safe and server-driven.

If build-child is tempted to add `entrypoints/background.ts` to "make it run" → **STOP** — that is AST-1170.

**Ritual:** none (no commit for this stage — informational only). Skip creating an empty commit.

## Self-Assessment

**Scope:** Single-Component — one new extension lib module that consumes AST-1236 pacing helpers and AST-1231/AST-1170 ports; no Python layers in the planned diff.

**Conf:** Medium — loop control flow and pacing wiring are fully specified against landed AST-1236 APIs, but remaining-work / fail / post HTTP paths are still owned by AST-1231 (Todo) and the shell ports by AST-1170 (Discussion); provisional Consumer contract + pre-build gate prevent guessing server code.

**Risk:** Medium — wrong remaining semantics (re-visiting `delivered`) or treating delivery as success would corrupt worklist completion and stealth; budget misuse could open parallel tabs; a non-recording stub without liveness would infinite-loop the same URL. Mitigated by pending-only contract, delivery≠success, `createTabBudget` finally-release, and per-run `recordedThisRun` → `no_progress`.

## Code rules check

- **§1.3 DRY:** Single loop; single sleep path (`dwell`); reuses AST-1236 budget helper — no second pacing implementation.
- **§2.1 config:** No new config block; pacing numbers remain in `SURFER_PACING_CONFIG` / GET cache.
- **§2.4 batch / claim-process-release:** Client-driven form — claim by taking the first server-reported pending URL, process one page, release via `postPage` (delivered) or `reportUrlFailure` (failed); no worker-memory plan. No dispatcher `claim_*_batch` (Surfer batch is not dispatch_ledger).
- **§2.6 / no-daisy-chain:** Loop does not await classification or chain into batch COMPLETED / meteorite qualify.
- **§3.2 ui-config-driven-business-logic:** Remaining work and outcomes decided on the server; extension renders process only.
- **§3.3 import-direction:** No Python. Extension module imports only sibling `./dwell` + `./pacingConfig`.
- **§3.5 / frontend-file-placement:** Files under settled `src/ui/extension/` (sibling to frontend).
- **debug-contract-gated:** Client forwards `debug` flag; Style D lines stay on AST-1231 server handlers.
- **engineer-test-tree-ban:** No `tests/` / bible edits on this ticket.

## Build-child sync note

Authoritative parent ref is `origin/ftr/AST-1174-human-paced-fan-out` (epic registry / parent Git table). `sync-child.sh … --ftr AST-1174` looks for exact `origin/ftr/AST-1174` and will skip; use:

```bash
~/.cursor/scripts/git/sync-child.sh sub/AST-1174/AST-1239-sequential-paced-fan-out \
  --ftr AST-1174-human-paced-fan-out \
  --worktree /home/susan/astral-AST-1174/
```

## Revisions

Revision 1 — 2026-08-07
Driven by: Joan `[plan-discuss] round=1 concern` (REVISE) — unbounded `while (true)` on non-advancing remaining; AC verifiability bookkeeping; client-minted failure `reason` vocabulary.
Changes: Stage 1 adds per-run `recordedThisRun` liveness → `stoppedReason: "no_progress"`; new **AC verification ownership** table (AC4–7 deferred; AC5 flag-forward only); gate §3 freezes `empty_capture` / `page_error` / `page_error:<detail>` with named `FAN_OUT_FAILURE_DETAIL_MAX = 200`; Risk updated for infinite re-visit.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1174/AST-1239-sequential-paced-fan-out`
**Plan path:** `docs/features/surfer/ast-1239-sequential-paced-worklist-fan-out.md`

**Built tip:** `139f338f1b4623fa0d5fa212856bd20c45b7e4d1` (`139f338f`)

| Stage | Commit | Summary |
|-------|--------|--------|
| 1 | `139f338f` | sequential paced fan-out loop (`fanOut.ts`) |
| 2 | — | doc-only (no commit) |

## Review (Radia)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1239
**Publish ref:** `origin/sub/AST-1174/AST-1239-sequential-paced-fan-out` @ `5693a1a7`
**Overall:** DISCUSS

**Scope of diff swept:** `git diff origin/dev...origin/sub/AST-1174/AST-1239-sequential-paced-fan-out` — 30 changed files. This ticket's own footprint is one file: `src/ui/extension/src/lib/fanOut.ts` (A, 161 lines, commit `139f338f`) + its test `tests/component/frontend/lib/test_surferFanOut.test.ts` (A, 230 lines) + plan/bible docs. `src/ui/extension/src/lib/{dwell,pacingConfig}.ts`, `src/ui/api/api_surfer.py`, `src/ui/server.py`, `src/utils/config.py` are byte-identical to the already `Review Posted` AST-1236 tip (`git diff 7fc377c3..<this-tip> -- <those 5 files>` is empty) — not re-swept in depth. The remaining ~23 files are cross-ticket test/bible content (see Findings).

**Full-set sweep:** 65 active statutes (18 universal + 47 scoped) scored in-session against `fanOut.ts` + its test. 17 of 18 universal `conforms`; `orch.git.betty-merge-tests-one-sha` / `orch.roles.betty-owns-test-tree` → `needs-discussion` (see Findings — now a multi-ticket, multi-epic pattern, not a one-off). Scoped statutes matched by `src/ui/**` / `src/utils/config.py` (same ~32 as the AST-1236 sweep) all `conforms`, verified directly: `astral.standards.in-scope-only` (no Flask route, no WXT scaffold, no React import — matches plan's explicit "Forbidden in this file" list line-for-line: no `chrome.alarms`, no inline pacing `setTimeout`, no hardcoded `10/5/15/1`, no durable local queue, no success-on-post-ack, no toasts/progress/resume, no search-page URL re-derivation); `astral.standards.dry-and-focused-functions` (single `runPacedFanOut`, reuses `dwell()` / `createTabBudget` — no second pacing implementation); `astral.layers.ui-config-driven-business-logic` (remaining-work / outcome judgment stays server-side; loop only consumes `fetchRemaining`); `astral.standards.debug-contract-gated` (forwards `opts?.debug` into `postPage` / `reportUrlFailure` only — no client Style D, matches plan §6); `astral.git.engineer-test-tree-ban` (the single `code(AST-1239)` commit touches only `fanOut.ts`). `astral.batch.batch-id-first` / `astral.batch.claim-process-release` / `astral.state.no-daisy-chain-in-run` are cited in the ticket's In-scope list but mechanically `not-applicable` here (their `applies_when.paths` are `src/core/**` / `src/data/**` only — this ticket's loop lives entirely in `src/ui/extension/`) — behaviorally the code still matches the cited intent (every `FanOutPorts` call carries `batchId`; `fetchRemaining` re-asked every iteration, no durable cursor; loop never awaits classification/COMPLETED) even though the statute's formal predicate doesn't reach the extension layer. Remaining split (not-applicable / applies counts) matches the AST-1236 sweep exactly since diff layers are identical (`ui`, `utils`, `docs` — no `core`/`data`/`external` touched by this ticket's own commit).

**Independently verified (not taken on trust):** Walked `fanOut.ts` line-by-line against the plan's "Forbidden in this file" list (§7) and Revision-1 changes — every item confirmed absent/present as required, including the `recordedThisRun` → `no_progress` liveness guard added in plan Revision 1. `test_surferFanOut.test.ts` exercises all 3 AC-relevant paths this ticket owns (AC1 visit-once, AC2 no-progress liveness, AC3 failure recording) plus `closeTab`-failure resilience and page-error truncation (`FAN_OUT_FAILURE_DETAIL_MAX`). Confirmed the AST-1236 files are unchanged (empty diff against the AST-1236 review tip) — no re-sweep needed there.

**Straggler (C4):** no plan-rubric (Joan) verdict attachment on this ticket, only the plan doc — not a block.

**Pattern conformance:** `pattern.batch.entity-claim-process-release`, `pattern.layers.import-discipline` — cited, both conform (client-driven claim-by-fetch, no data/core code in this diff to violate import discipline).

## Plan adherence

- Diff matches the plan's Self-Assessment (`Single-Component`) exactly — one extension lib file, no Python layers touched, as planned.
- Revision 1 (Joan plan-discuss round — unbounded `while(true)` on non-advancing remaining) is fully reflected: `recordedThisRun` set + `no_progress` stop reason, exactly as the plan's Revision 1 note describes.
- AC ownership table honored: this ticket does not tick AC4–7 (deferred to AST-1231 / AST-1170) and does not invent client-side Style D for AC5.

## Findings

**discuss** — Cross-ticket / cross-epic test-tree contamination, now recurring and larger (C6 §5d; `orch.git.betty-merge-tests-one-sha` / `orch.roles.betty-owns-test-tree`): the `merge-tests(AST-1239)` commit's `origin/tests` SHA carries orphaned test files for **at least 5 other tickets**, none of whose product code is an ancestor of this branch:
  - `tests/component/core/test_page_intake.py` (AST-1227, parent AST-1168) — `src/core/page_intake.py` missing (same finding as the AST-1236 review, still unresolved).
  - `tests/component/core/test_surfer.py` (AST-1229, parent AST-1174 — this same epic) — `src/core/surfer.py` missing.
  - `tests/component/data/database/test_surfer_batches.py` (AST-1229) — no `surfer_batches` / `SURFER_BATCH_CONFIG` anywhere in `src/data/database.py` or `src/utils/config.py` on this branch.
  - `tests/component/core/test_candidate.py`'s new `TestAst1235SurferConsent` class (AST-1235, **parent AST-1173 — a different epic**) calls `candidate_mod.empty_surfer_consent()` / `normalize_surfer_consent()`, which do not exist in `src/core/candidate.py` here (`code(AST-1235)`/`AST-1237`/`AST-1238` commits confirmed **not** ancestors of this branch via `git merge-base --is-ancestor`).
  - `tests/component/frontend/lib/{test_surferConsent,test_surferConsentGate}.test.ts` and `tests/component/frontend/pages/{test_CandidateSurfer,test_CandidateSurferConsent}.test.tsx` (AST-1235/1237/1238, parent AST-1173) — all import extension/frontend modules (`surferConsent.ts`, `surferDisclosureDom.ts`, `CandidateSurfer.tsx`, `CandidateSurferConsent.tsx`) confirmed missing from this branch's tree.

  Root cause is the same shared-`origin/tests`-branch mechanism flagged on AST-1236, but this time it has pulled in unlanded work from a **second, unrelated parent epic (AST-1173)**, not just a same-epic sibling. Running the full component suite against this exact publish ref will fail collection/attribute-lookup on at least 6 files. Not this engineer's fault, outside engineer fix-authority (`astral.git.engineer-test-tree-ban`), and this ticket's own commit (`139f338f`) touches only `fanOut.ts`. Not blocking Review Posted, but given this is now the second and visibly larger occurrence in the same epic, recommend Susan/Betty look at scoping `merge-tests` to the ticket's own test commit (or landing `origin/tests`-ahead-of-`dev` product code faster) before a third child inherits an even bigger backlog.

## Frame diff

(none) — this ticket's own diff footprint (`fanOut.ts` + test) matches the ticket Description's In-scope / Considered-but-excluded frame exactly.

context_tokens≈130000

— Radia

## Resolution

2026-08-07 — Hedy resolve-child after Radia `[code-rubric] revision=1` (Overall: DISCUSS).

**fix-now:** none.

**discuss — cross-ticket / cross-epic `origin/tests` contamination on `merge-tests(AST-1239)`:** Acknowledged; no product change on this tip. Outside engineer fix-authority (`astral.git.engineer-test-tree-ban`); Betty owns the test tree / `merge-tests` scoping. This ticket's `code(AST-1239)` commit remains `fanOut.ts` only. Betty's AST-1239 manifest (fanOut + pacingConfig) already passed green at Tests Passed — full-suite orphans are a shared-lane process issue for Susan/Betty, not a fan-out loop defect.

**Product / plan:** unchanged vs built tip `139f338f` + Radia docs intake `9cb92796`.
