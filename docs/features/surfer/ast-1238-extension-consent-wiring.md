# AST-1238 — Extension / capture-route consent wiring

Mandatory handoff for **AST-1170** (extension shell) and **AST-1228** (page_intake HTTP), or whichever ticket owns those surfaces. Helpers live under `src/ui/extension/src/lib/` (same layout as pacing helpers).

## AST-1170 — background capture

- Before any page_intake / capture POST, call `assertMayCapture` from `src/ui/extension/src/lib/surferConsentGate.ts`.
- On throw, show the error message via the toast primitive and **do not** POST capture.
- Always re-check the server before capture — local storage is not authority.
- Do not duplicate consent API paths; import these helpers.

## AST-1170 — popup / action UI

- When consent `status === "opted_in"`, show the off-switch using DTO labels from the consent GET.
- On confirm, call `optOutSurfer` from `src/ui/extension/src/lib/surferOffSwitch.ts`.
- After success, subsequent captures must no-op via the gate.

## AST-1228 — page_intake HTTP route

- The route handler **must** call `require_current_surfer_consent(candidate_id)` before enqueueing classification / ingest.
- Map `ValueError` → 403 (or 400) JSON `{"error": str(e)}`.
- Leave a one-line code comment at the call site: `# AST-1238: consent gate — do not remove`.

## Self-check when capture route lands

Grep the route module for `require_current_surfer_consent`. If absent, that ticket is incomplete relative to parent AC2 — do not ship the route without the call.
