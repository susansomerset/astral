# AST-1413 — Ad Hoc preview modal and agent_data panes

- **Linear:** [AST-1413](https://linear.app/astralcareermatch/issue/AST-1413)
- **Parent:** [AST-1403](https://linear.app/astralcareermatch/issue/AST-1403)
- **Publish ref:** `sub/AST-1403/AST-1413-ad-hoc-preview-modal-and-agent-data-panes`

After #2, Preview Prompt still paints an inline “Resolved Prompt Preview” block at the bottom of Agent Ad Hoc, and a successful Test still dumps `response_text` into a `<pre>` (plus a one-line timesheet). This ticket moves Preview into the shared scrollable `Modal` (same family as Manage Tasks preview) with tabs for System, Cache A–D, No Cache, User, and Live Content, and replaces the dumped Test response with the same agent_data tabbed panes Execution History already uses (`BatchAgentDataModal` body: `BLOCK_TYPE_ORDER` tabs + Tokens & Cost). Preview does not write or refresh those panes. Does **not** change how blocks are stored (sibling #1 / AST-1411) or which editors exist (sibling #2 / AST-1412).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx` | Preview → `Modal` with eight resolved tabs; after Test, inline `BatchAgentDataPanes` for `batch_id`; delete inline preview block and Response `<pre>` dump | ui |
| `src/ui/frontend/src/components/BatchAgentDataModal.tsx` | Export pane body as `BatchAgentDataPanes`; default export stays the Execution History wide `Modal` wrapper | ui |
| `src/ui/frontend/src/App.css` | Add `.batch-agent-data-wrapper--page` so the existing flex textarea has a height outside the wide modal | ui |

Do **not** edit: `src/ui/frontend/src/pages/AdminTaskPrompts.tsx`, `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx`, `src/ui/frontend/src/components/Modal.tsx`, `src/core/agent.py`, `src/ui/api/api_admin.py` (preview JSON already returns `cache_a`–`cache_d` + `live_content`; Test already returns `batch_id`), `src/utils/config.py`, `src/data/database.py`, seven-segment editors / `editorSegmentBody` / Save As (sibling #2), `tests/`, bible. Do **not** add a new component file. Do **not** extract preview labels into a shared module.

**Pre-flight (build-child):** After `sync-child.sh` with `--ftr AST-1403-update-adhoc-agent-to-mirror-new-task-structure`, `AdminAnthropicAdHoc.tsx` must already have seven editor `TABS` (`system` … `user`) and `editorSegmentBody()`. If `type TabKey` is still `"user" | "cache" | "nocache"`, stop and comment on **AST-1403** — do not re-implement #2.

## Stage 1: Preview Prompt is a scrollable modal

**Done when:** Clicking Preview Prompt (after a 200 from `POST /api/admin/adhoc/preview`) opens `Modal` from `src/ui/frontend/src/components/Modal.tsx`. The page body does **not** contain the “Resolved Prompt Preview” heading or an inline preview `<pre>`. The modal `TabBar` has exactly these tabs, in this order: System, Cache A, Cache B, Cache C, Cache D, No Cache, User, Live Content. Empty slots render `(empty)`. Cache A text is `cache_a` from the JSON, falling back to `cache`. Closing the modal (header `icon-control` × or footer Cancel) hides it and does **not** call `GET /api/agent_data/...`. Preview Prompt / ▶ Test / Save As button classes are unchanged. `cd src/ui/frontend && npx tsc -b --noEmit` passes.

1. In `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx`, add:

   ```ts
   import Modal from "../components/Modal"
   ```

   next to the existing `TabBar` / `TokenTextarea` imports.

2. Replace `type PreviewKey` and `PREVIEW_TABS` with:

   ```ts
   type PreviewKey = "system" | "cache_a" | "cache_b" | "cache_c" | "cache_d" | "nocache" | "user" | "live_content"

   const PREVIEW_TABS: { key: PreviewKey; label: string }[] = [
     { key: "system",       label: "System" },
     { key: "cache_a",      label: "Cache A" },
     { key: "cache_b",      label: "Cache B" },
     { key: "cache_c",      label: "Cache C" },
     { key: "cache_d",      label: "Cache D" },
     { key: "nocache",      label: "No Cache" },
     { key: "user",         label: "User" },
     { key: "live_content", label: "Live Content" },
   ]
   ```

   Delete `type PreviewData = Record<PreviewKey, string>`.

3. Add this file-local helper immediately after `taskHasExistingPrompts` (same shape as `previewField` in `AdminTaskPrompts.tsx`; do **not** import from that page):

   ```ts
   function previewField(tab: PreviewKey, data: Record<string, unknown> | null): string {
     if (!data) return ""
     const txt = (k: string): string => (typeof data[k] === "string" ? (data[k] as string) : "")
     switch (tab) {
       case "cache_a":
         return txt("cache_a") || txt("cache")
       default:
         return txt(tab)
     }
   }
   ```

4. Change preview state: `previewData` type becomes `Record<string, unknown> | null`. Add `const [previewOpen, setPreviewOpen] = useState(false)` next to `previewTab`. Keep `previewTab` default `"system"`.

5. In `handlePreview`, keep the POST body (`agent_id`, `task_key`, `entity_id` / `entity_ids`, `...editorSegmentBody()`, `candidate_id`) unchanged. Replace the success `.then(data => { setPreviewData(data as PreviewData); setPreviewTab("system") })` with:

   ```ts
         .then(data => {
           setPreviewData(data)
           setPreviewTab("system")
           setPreviewOpen(true)
         })
   ```

   Do **not** call `api("/api/agent_data/...")` here. Do **not** clear Test state (`response` / `timesheet` still exist in this stage).

6. Delete `byteSize` and `previewTabsWithSize` (modal tabs match Manage Tasks: labels only, no byte-size suffix).

7. Delete the entire JSX block `{previewData && ( … Resolved Prompt Preview … )}`. In its place, immediately before `<Toast … />`, add:

   ```tsx
         <Modal
           open={previewOpen}
           onClose={() => setPreviewOpen(false)}
           title={taskKey ? `Preview: ${taskKey}` : "Preview"}
         >
           <TabBar tabs={PREVIEW_TABS} active={previewTab} onChange={key => setPreviewTab(key)} />
           <pre style={{
             marginTop: 12, padding: 12, borderRadius: 4,
             background: "var(--bg-deep)", border: "1px solid var(--border)",
             color: "var(--text-primary)", fontFamily: "monospace", fontSize: 12,
             whiteSpace: "pre-wrap", wordBreak: "break-word",
             maxHeight: 500, overflow: "auto",
           }}>
             {previewField(previewTab, previewData) || "(empty)"}
           </pre>
         </Modal>
   ```

   Do **not** pass `size="wide"`. Do **not** pass `showFooter={false}` (Manage Tasks preview keeps the default Cancel footer). Close is the existing `Modal` `icon-control` × — do not add a second close button. Do **not** change Preview Prompt (`btn secondary`) / ▶ Test (`btn primary`) / Save As (`btn secondary`).

8. Leave the Response `<pre>` dump in this stage. Do **not** edit `TABS`, `editors`, `editorSegmentBody`, fetch/Save As, or entity picker.

⚠️ **Decision:** Same `Modal` family as Manage Tasks preview (default card width, header ×, Cancel footer, `TabBar` + scrollable `<pre maxHeight: 500>`), not `size="wide"`. Parent AC names the preview tabs System / Cache A–D / No Cache / User / Live Content — use those short labels, not Manage Tasks’ “System Prompt” / “Cache Block A” editor strings. Live Content is Ad Hoc–only (Manage Tasks preview has no live-content slot).

⚠️ **Decision:** Duplicate `previewField` here rather than sharing with `AdminTaskPrompts.tsx`. That page is out of scope; Cache A still needs the `cache_a` || `cache` alias sibling #1 kept on the Preview JSON.

## Stage 2: After Test, workbench shows Execution History agent_data panes

**Done when:** A successful `POST /api/admin/adhoc/test` (HTTP 200, `success: true`, non-empty string `batch_id`) renders `BatchAgentDataPanes` on the workbench for that `batch_id` (tabs in `BLOCK_TYPE_ORDER` for stored blocks, including SYSTEM / each stored CACHE_A–D / NO_CACHE / TASK / RESPONSE, plus the existing Tokens & Cost summary). There is no Response `<pre>` dump and no Ad Hoc timesheet header next to it. Preview Prompt does not set, clear, or refetch `testBatchId`. Execution History still opens `BatchAgentDataModal` (wide modal) with the same pane body. `cd src/ui/frontend && npx tsc -b --noEmit` passes.

1. In `src/ui/frontend/src/components/BatchAgentDataModal.tsx`, keep `BLOCK_TYPE_ORDER`, fetch URLs, timesheet math, FEEDBACK hydrate, and CSS class names. Split as follows.

   Add:

   ```ts
   interface PanesProps {
     batchId: string
     candidateId?: string
     className?: string
   }
   ```

   Move the current `BatchAgentDataModal` function body (all hooks + the inner `<div className="batch-agent-data-wrapper">…</div>`) into:

   ```ts
   export function BatchAgentDataPanes({ batchId, candidateId, className }: PanesProps) {
   ```

   Drop the `if (!batchId) return` early-out in the fetch effect (`batchId` is now a required string). Change the wrapper to:

   ```tsx
       <div className={className ? `batch-agent-data-wrapper ${className}` : "batch-agent-data-wrapper"}>
   ```

   The default export becomes only the Execution History chrome:

   ```tsx
   export default function BatchAgentDataModal({ batchId, candidateId, onClose }: Props) {
     return (
       <Modal open={!!batchId} onClose={onClose} title={batchId ?? ""} size="wide">
         {batchId ? <BatchAgentDataPanes batchId={batchId} candidateId={candidateId} /> : null}
       </Modal>
     )
   }
   ```

   Do **not** change `AdminPerformanceMonitor.tsx` or `AdminVectorFeedback.tsx` imports (they keep the default Modal). Do **not** change `size="wide"` on that wrapper. Do **not** add FEEDBACK-omit logic for Ad Hoc — reuse the pane as-is.

2. In `src/ui/frontend/src/App.css`, immediately after the `.batch-agent-data-wrapper { … }` block (before `.batch-agent-data-body`), add:

   ```css
   .batch-agent-data-wrapper--page {
     height: 560px;
     padding: 0;
     margin-top: 20px;
   }
   ```

   Do **not** change `.batch-agent-data-wrapper` itself (Execution History wide modal still fills `modal-body`). The page class is a sized parent so `flex: 1; min-height: 0` on `.batch-agent-data-textarea` is not a 0-height box; 560px matches the previous dump’s visible area (`maxHeight: 600` minus the Response header). Do **not** truncate `block_data`.

3. In `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx`, add:

   ```ts
   import { BatchAgentDataPanes } from "../components/BatchAgentDataModal"
   ```

4. Delete `response` and `timesheet` state. Add `const [testBatchId, setTestBatchId] = useState<string | null>(null)`. Delete `responseBodyToText` and `formatResponse`.

5. Replace `handleTest` success/error handling. Keep the POST body unchanged (still `...editorSegmentBody()`, no `debug`). At the start of `handleTest`, after the agent-id guard:

   ```ts
       setTesting(true)
       setTestBatchId(null)
   ```

   Replace the `.then(data => { if (data.success) { setResponse… } … })` / `.catch(e => setResponse…)` with:

   ```ts
         .then(data => {
           if (data.success) {
             const id = typeof data.batch_id === "string" ? data.batch_id.trim() : ""
             if (id) setTestBatchId(id)
             else setToast({ text: "Test succeeded without batch_id", variant: "error" })
           } else {
             setToast({ text: data.error || "Unknown error", variant: "error" })
           }
         })
         .catch(e => setToast({ text: e.message, variant: "error" }))
   ```

   HTTP 500 (including sibling #1 soft-fail that still returns `batch_id`) stays on the existing `if (!r.ok) throw` path — toast only; do **not** load panes. Do **not** display `response_text`.

6. `handlePreview` must not read or write `testBatchId`.

7. Delete the entire JSX `{response !== null && ( … Response … )}` block and the disabled hydrated-output comment. After the prompt editor tabs (and after the Stage 1 Preview `Modal`), render:

   ```tsx
         {testBatchId && (
           <BatchAgentDataPanes
             batchId={testBatchId}
             candidateId={selectedId || undefined}
             className="batch-agent-data-wrapper--page"
           />
         )}
   ```

   `BatchAgentDataPanes` already GETs `/api/agent_data/<batch_id>` and `/api/admin/timesheets?batch_id=…` — do not add a parallel fetch on the page.

⚠️ **Decision:** Panes are **inline on the workbench** (they replace the dump at the bottom). Preview is the modal. Opening Execution History’s `BatchAgentDataModal` after Test would hide inspection in a second popup and contradict “on the workbench.” Reuse is the extracted pane body, not a second copy of tab/order/cost logic.

⚠️ **Decision:** Named export from the existing modal file rather than a new `components/*.tsx`. Placement stays `src/components/` (flat); one extra file is not required.

⚠️ **Decision:** Only HTTP 200 + `success` + non-empty `batch_id` mounts panes (parent AC4: after a **successful** Test). Soft-fail 500 may still have stored blocks — operator inspects those from Execution History, not from this dump replacement.

## Execution contract

- Execute stages in order. One commit per stage on this epic worktree, then `git push origin HEAD:sub/AST-1403/AST-1413-ad-hoc-preview-modal-and-agent-data-panes`.
- Do not add files, routes, config blocks, or editor tabs not listed above.
- Do not fold Test into `do_task`. Do not persist on Preview.
- If `TABS` is still three-slot, or Preview JSON lacks `cache_a`–`cache_d`, or Test JSON lacks `batch_id`, stop and comment on **AST-1403** with the Stage N blocked template — do not improvise.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric.v1
**Ticket:** AST-1413
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1403/AST-1413-ad-hoc-preview-modal-and-agent-data-panes` @ `a65cf3e34b3f5c26085176267399924a9945d2b1`

## Traceability

AC3→Stage 1 (Preview `Modal`, eight resolved tabs incl. Live Content, no inline preview block, `cache_a`||`cache` alias); AC4→Stage 2 (`BatchAgentDataPanes` inline after HTTP 200 + `success` + `batch_id`; Response `<pre>` removed; Preview does not touch `testBatchId`).

## Findings

**acceptable** — Short preview tab labels (“Cache A”) vs Manage Tasks editor strings; matches parent AC3 wording and is documented.

**acceptable** — `BatchAgentDataPanes` named export refactor in existing `BatchAgentDataModal.tsx`; default wide `Modal` wrapper preserved for Execution History / Vector Feedback consumers.

**acceptable** — HTTP 500 / soft-fail with `batch_id` does not mount workbench panes; operator uses Execution History — consistent with AC4 “after a successful Test.”

context_tokens≈62000

[plan-rubric] PROCEED (Commit: a65cf3e3) preview modal plus panes

## Review stub (Katherine / build)

**Publish ref:** `origin/sub/AST-1403/AST-1413-ad-hoc-preview-modal-and-agent-data-panes`  
**Product commits:** `31889c26` (Stage 1 — Preview Prompt `Modal` with eight resolved tabs), `56bac797` (Stage 2 — `BatchAgentDataPanes` inline after Test; Response dump removed)
