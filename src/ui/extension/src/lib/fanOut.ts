/** Sequential paced Surfer worklist fan-out (AST-1239 / AST-1174). */

import { dwell } from "./dwell";
import { createTabBudget, fetchPacingConfig } from "./pacingConfig";

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
  const id = (batchId || "").trim();
  if (!id) throw new Error("runPacedFanOut: batchId is required");

  await fetchPacingConfig(ports.getJson);
  const budget = createTabBudget(); // uses getPacingConfig().max_tabs (ships at 1)
  let visited = 0;
  let failed = 0;
  /** Per-run liveness only — not a durable resume cursor (AC7 still re-asks the server). */
  const recordedThisRun = new Set<string>();
  const FAN_OUT_FAILURE_DETAIL_MAX = 200;

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
}
