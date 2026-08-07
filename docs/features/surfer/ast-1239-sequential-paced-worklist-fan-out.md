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

## Pre-build dependency gate (before Stage 1 code)

**Done when:** Builder can name the live AST-1231 symbols that satisfy the **Consumer contract** below (or confirm provisional paths still match a published AST-1231 plan on `origin/sub/AST-1169/AST-1231-batch-scoped-intake`).

1. Confirm AST-1236 helpers exist at:
   - `src/ui/extension/src/lib/dwell.ts` → `dwell`
   - `src/ui/extension/src/lib/pacingConfig.ts` → `fetchPacingConfig`, `createTabBudget`, `getPacingConfig`
2. Confirm sibling HTTP ownership:
   - **AST-1231** owns batch-scoped post + remaining-work query (+ per-URL `debug=` Style D on that path).
   - **AST-1170** owns authenticated `getJson` / `postJson`, tab open/close/load-wait, and visible-text capture via content-script messaging.
3. If AST-1231 has published a plan or code whose remaining/post/fail shapes **differ** from the Consumer contract below → **STOP**, comment on **AST-1239** (not parent) with the delta, and wait — do not invent a second client vocabulary and do not implement AST-1231 routes here.
4. If AST-1231 has **no** published plan/code yet at build time → still implement `fanOut.ts` against the Consumer contract ports (shell can stub); do **not** add server routes. Full end-to-end AC verification waits on AST-1231 + AST-1170 landing (UAT / integration), which is expected for this epic ordering.

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

**Done when:** `src/ui/extension/src/lib/fanOut.ts` exists with the exports and control flow below; it imports `dwell`, `fetchPacingConfig`, and `createTabBudget` from the AST-1236 modules; it contains **no** `chrome.alarms` / `browser.alarms`, **no** inline `setTimeout`/`setInterval` for pacing (only `dwell()`), **no** hardcoded dwell seconds / max_tabs literals, **no** Flask/Python files, and **no** WXT entrypoints; a fresh open→close happens per URL; `createTabBudget` wraps each in-flight page; worker-memory URL lists are never used as the source of truth.

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
  stoppedReason: "exhausted" | "empty_batch";
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
```

Do **not** snapshot a URL list into a local array that outlives one iteration.

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
      failed += 1;
    } else {
      await ports.postPage({
        batchId: id,
        pageUrl: nextUrl,
        pageText,
        debug: opts?.debug,
      });
      // Delivery only — do NOT treat ack as URL success / batch complete.
      visited += 1;
    }
  } catch (err) {
    const reason =
      err instanceof Error ? err.message.slice(0, 200) : "page_error";
    await ports.reportUrlFailure({
      batchId: id,
      pageUrl: nextUrl,
      reason,
      debug: opts?.debug,
    });
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
rg -n 'from \"\./dwell\"|from \"\./pacingConfig\"|runPacedFanOut|createTabBudget|fetchRemaining|reportUrlFailure' src/ui/extension/src/lib/fanOut.ts
# expect imports + exports present
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

**Risk:** Medium — wrong remaining semantics (re-visiting `delivered`) or treating delivery as success would corrupt worklist completion and stealth; budget misuse could open parallel tabs. Mitigated by pending-only contract, explicit delivery≠success rule, and mandatory `createTabBudget` finally-release.

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
