# AST-1789 — Manage Candidates channel column, select warning, S snapshot

**Linear:** [AST-1789](https://linear.app/astralcareermatch/issue/AST-1789/manage-candidates-channel-column-select-warning-s-snapshot-manage)  
**Parent:** [AST-1786](https://linear.app/astralcareermatch/issue/AST-1786/manage-candidates-snapshot-slack-channel-candidate-mapping) — Manage Candidates Snapshot Slack Channel + candidate mapping  
**Publish ref:** `sub/AST-1786/AST-1789-manage-candidates-channel-column-s-snapshot`

Child #3 of AST-1786: Manage Candidates UI for Slack username list column, Slack channel `<select>` with membership warning, and row **S** `icon-control` that copies the stored channel’s ascending message snapshot JSON to the clipboard via sibling admin APIs. Does **not** own external Slack helpers (AST-1787) or Contact/API/shapes bodies (AST-1788).

## Explicit scope gate

Ticket **## Scope** (verbatim partition):

- `src/ui/frontend/src/pages/AdminManageCandidates.tsx` — username column, channel select + warning, **S** clipboard
- `src/ui/frontend/src/pages/CandidateProfile.tsx` — only if shapes-driven render needs a page touch (prefer none)

**Out of scope (siblings):** `src/external/slack.py` (AST-1787); `src/core/contact.py` / `src/ui/api/api_contact.py` / `src/utils/config.py` (AST-1788).

**Depends on:** AST-1788 contracts already on `origin/ftr/AST-1786-manage-candidates-snapshot-slack-channel` (synced onto this tip):

| Route | Response |
|-------|----------|
| `GET /api/admin/contact/slack_channels` | `{"channels":[{"id": str, "name": str}, …]}` |
| `GET /api/admin/contact/slack_channel_membership?astral_candidate_id=&channel=` | `{"channel","slack_user_id","is_member","warn","warn_reason"}` with `warn_reason` ∈ `{null,"unbound","not_member"}` |
| `GET /api/admin/contact/slack_channel_snapshot?astral_candidate_id=` | `{"astral_candidate_id","channel_id","channel_name","messages":[…]}` ascending |
| Shapes | list key `slack_username`; profile `contact.slack_channel_id` + `contact.slack_channel_name` (already in `DATA_SHAPES`) |

**Canon Scope (read in full for plan):** `stat.logging.info.api`, `stat.logging.error`. Patterns: none (`no established pattern applies` on parent). React does not write `app_log` (`stat.logging.info.api` Notes). This ticket does **not** add or change API handlers — no new route progress info and no new handler `logger.exception` lines. API failures surface via existing toast pattern (same as unbound Slack load / create / PUT).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminManageCandidates.tsx` | Flatten `slack_username` for list column; channel options + select on add/edit; membership warning; stamp both channel fields on save; row **S** snapshot clipboard | ui |

⚠️ **Decision — no `CandidateProfile.tsx`:** Profile Contact Information already renders `shapes.detail.profile` via `FormFields`. AST-1788 landed `contact.slack_channel_id` + `contact.slack_channel_name` in those shapes. No page edit required (ticket prefers none).

No other files. Do **not** edit `api_contact.py`, `contact.py`, `config.py`, `slack.py`, or invent a frontend Slack Web API client (parent AC 8).

## Stage 1: Username column, channel select + warning, S snapshot

**Done when:** Manage Candidates list cells for `slack_username` match `candidate_data.contact.slack_username` (or a clear empty placeholder); add/edit offer a Slack channel `<select>` from `GET /api/admin/contact/slack_channels`, stamp both `contact.slack_channel_id` and `contact.slack_channel_name` on save when a channel is selected; selecting a channel shows an unmistakable membership warning when unbound or not a member (selection still allowed) and clears that warning when the API says member; row **S** `icon-control` fetches `GET /api/admin/contact/slack_channel_snapshot` and copies JSON to the clipboard; no Slack Web API URLs/tokens in this file.

1. In `src/ui/frontend/src/pages/AdminManageCandidates.tsx`, add types/state parallel to unbound Slack bind:
   - `type SlackChannelOption = { id: string; name: string }`
   - `slackChannels: SlackChannelOption[]` (default `[]`)
   - Extend `EMPTY_ADD_FORM`, `addForm`, and `editForm` with `slack_channel_id: string` (selected option value; `""` = none). Do **not** add a free-text channel name field the admin can type.
   - `channelMembershipWarn: string | null` (default `null`) — human-readable warning under the channel select; `null` = no warning.
   - Optional: `snapshottingId: string | null` to disable the **S** button while a snapshot request is in flight (mirror `settingCandidateId` for **T**).

2. **Flatten list username (parent AC1):** In `flattenCandidate`, set top-level `slack_username` from `contact.slack_username` (string, or `""` when missing). Shapes already expose list key `slack_username`. In `baseColumns` mapping, when `col.key === "slack_username"`, add a `render` that shows the trimmed string, or `"—"` (or equivalent clear empty placeholder) when empty — do **not** leave an ambiguous blank cell that looks like a missing column.

3. **Load channel options:** Add `loadSlackChannels` (same toast-on-error family as `loadUnboundSlackUsers`):
   - `GET /api/admin/contact/slack_channels`
   - Parse `data.channels` array; keep only rows with non-empty string `id` and `name`; `setSlackChannels(...)`.
   - Call it when opening Add and when opening Edit (alongside `loadUnboundSlackUsers`). Do **not** hardcode Slack API hosts/tokens.

4. **Helper — stamp channel from selection** (mirror `slackBindFromSelection`):
   ```ts
   function slackChannelFromSelection(
     selectedId: string,
     options: SlackChannelOption[],
   ): { slack_channel_id: string; slack_channel_name: string } | null
   ```
   - Empty/trimmed-empty `selectedId` → `null`.
   - Find option by `id`; missing → `null`.
   - Return `{ slack_channel_id: row.id, slack_channel_name: row.name }`.

5. **Membership warning helper** — implement `runChannelMembershipCheck` used by add/edit:
   - **Inputs:** `channelId: string`, plus context: either `{ mode: "edit"; astral_candidate_id: string; formSlackUserId: string }` or `{ mode: "add"; formSlackUserId: string }`.
   - If `channelId` is empty after trim: set `channelMembershipWarn` to `null` and return (no warning for “— none —”).
   - ⚠️ **Decision — add / unbound without membership GET:** Sibling membership route requires `astral_candidate_id` and reads **stored** `contact.slack_user_id`, not the form’s pending bind. On **add** (no candidate id yet), or on **edit** when `formSlackUserId` is empty: do **not** call the membership API; set warn text to exactly:  
     `Warning: no Slack user is bound for this candidate. Channel assignment may be wrong.`  
     (parent AC3 — selection still allowed).
   - On **edit** with non-empty `formSlackUserId` and non-empty `channelId`:  
     `GET /api/admin/contact/slack_channel_membership?astral_candidate_id=<id>&channel=<channelId>`  
     - If `!r.ok`: toast the error body (or a short fallback); leave prior warn state or clear — do **not** invent Slack membership locally.  
     - If ok: read `warn` / `warn_reason`. When `warn` is true:  
       - `unbound` → same unbound sentence as above.  
       - `not_member` → `Warning: the bound Slack user is not a member of this channel.`  
       - any other truthy warn → use `not_member` sentence.  
     - When `warn` is false: set `channelMembershipWarn` to `null` (parent AC5).  
   - ⚠️ **Decision — membership uses saved bind:** The API ignores the form’s pending Slack username change until save. If admin changes bind + channel in one edit, the check reflects the **pre-save** bind. Acceptable under sibling contract; do not invent a `slack_user_id` query param.

6. **Wire channel `<select>` on Add and Edit** (after the existing Slack username select):
   - Label: `Slack channel`.
   - `className="dep-input dep-select"`.
   - Options: `<option value="">— none —</option>` plus `slackChannels.map` → `value={c.id}` label `#{c.name}` or `c.name` (use channel **name** as visible label; value is **id**).
   - `onChange`: update form `slack_channel_id`; then call `runChannelMembershipCheck` with the new id (and add vs edit context above).
   - Directly under the select, when `channelMembershipWarn` is non-null, render an unmistakable warning block (not toast-only): e.g. a `<p>` / `<div>` with `role="alert"`, visible warning color (`var(--warning, #ff9800)` or existing warning token), and the warn string. Selection must remain enabled (parent AC3–4).

7. **`openEdit`:** Initialize `slack_channel_id` from `String(contact.slack_channel_id ?? "").trim()`. Clear `channelMembershipWarn` then, if that id is non-empty, call `runChannelMembershipCheck` once so reopening edit with a stored channel re-surfaces AC3/4 warnings. Reset warn to `null` when closing add/edit modals / resetting forms.

8. **Persist both channel fields on save (parent AC2):**
   - In `handleAddSave` / `handleEditSave`, after building `contact` (including existing Slack bind stamps):  
     `const ch = slackChannelFromSelection(form.slack_channel_id, slackChannels)`  
     if `ch`: set `contact.slack_channel_id` and `contact.slack_channel_name`.  
   - ⚠️ **Decision — empty channel omits keys:** Same as Slack bind — empty selection does **not** send channel keys, so deep-merge leaves any existing stored channel intact. Do not invent a clear-channel path in this ticket.
   - Keep using existing `POST /api/candidates` and `PUT /api/candidates/<id>/data` only — no new write route.

9. **Row **S** icon-control (parent AC6):** In the `_actions` span, after the **T** button (or beside other icon-controls — keep the same flex row), add:
   ```tsx
   <button
     type="button"
     className="icon-control"
     title="Snapshot Slack channel"
     aria-label={`Snapshot Slack channel for ${row.astral_candidate_id}`}
     disabled={snapshottingId === row.astral_candidate_id}
     onClick={e => { e.stopPropagation(); void handleSlackChannelSnapshot(row) }}
   >
     S
   </button>
   ```
   - Must use shared `icon-control` class (not a one-off `btn`).
   - `handleSlackChannelSnapshot(row)`:
     - Read `contact.slack_channel_id` from `row.candidate_data`; if empty after trim: toast error `No Slack channel stored for this candidate` and return (do not call snapshot).
     - Set `snapshottingId` to the candidate id; `GET /api/admin/contact/slack_channel_snapshot?astral_candidate_id=<id>`.
     - On `!r.ok`: toast error from body / fallback; clear `snapshottingId`; return.
     - On ok: `await navigator.clipboard.writeText(JSON.stringify(body, null, 2))` then toast success `Slack channel snapshot copied` (same family as `copyJobSnapshotToClipboard` / Admin clipboard copies).  
     - ⚠️ **Decision — clipboard = full API JSON:** Copy the entire snapshot response object (includes `messages` ascending from the API). Do not reverse or re-sort messages in React; do not truncate.
     - `finally`: clear `snapshottingId`.
     - Clipboard failure: toast error; do not throw uncaught.

10. **Compile / lint:** From `src/ui/frontend`, run the project’s existing typecheck/lint for this page (e.g. `npx tsc --noEmit` or the repo’s frontend lint script if that is what prior Contact UI tickets used). Fix any type errors introduced in this file before the stage commit. Do **not** edit `tests/` or bible paths.

## Execution contract

- Execute steps in order within the stage; one stage → one `code(AST-1789): …` commit on the epic worktree, then push `origin/sub/AST-1786/AST-1789-manage-candidates-channel-column-s-snapshot`.
- Do not add files beyond the Files Changed table, touch sibling scopes, or call Slack Web API from React.
- On ambiguity or drift (e.g. membership/snapshot JSON shape changed) — stop, comment on parent AST-1786 with the Stage blocked template, wait.

**Acceptance mapped (this child):**

| AC | Where |
|----|--------|
| 1 (username column) | Stage 1 steps 2 |
| 2 (channel select + stamp both fields) | Stage 1 steps 3–4, 6, 8 |
| 3–5 (membership warnings) | Stage 1 steps 5–7 |
| 6 (**S** icon-control + ascending JSON clipboard) | Stage 1 step 9 |
| 8 (no Slack Web API in TSX) | Entire stage — admin `api()` routes only |

Parent AC 7, 9, 10 → sibling tickets (auth / external / shapes).

## Estimate

Confirm Chuckles estimate: 2 — agree

## Canon Scope (this ticket)

| Id | Role |
|----|------|
| `stat.logging.info.api` | statute — read in full; React does not emit `app_log`; this ticket adds no API routes (no completing-route info to add) |
| `stat.logging.error` | statute — read in full; this ticket adds no Python handlers; UI surfaces failures via toast, not `logger.exception` |

No placement statutes named. No harvested pattern ids (`no established pattern applies` on parent).

## Joan validate

[plan-rubric]
**Ticket:** AST-1789
**Overall:** APPROVED
**Corpus:** 2ac86c3f693409c364f8630a97198c8dbfa9c6f3
**Publish ref:** `d48d96ff49746b28fd4277caaeb0e53904ad6cb0`

## Canon scores

stat.logging.info.api | X | | React-only plan — no `src/ui/api/**` changes; statute Notes: frontend does not write `app_log`
stat.logging.error | X | | React-only plan — no Python handlers; failures via toast, not `logger.exception`

## Traceability

AC1 (username column) → Stage 1 step 2 flatten + column render; AC2 (channel select + stamp id+name) → Stage 1 steps 3–4, 6, 8 + existing POST/PUT; AC3–5 (membership warnings) → Stage 1 steps 5–7 (inline `role="alert"` block + API/local unbound paths); AC6 (**S** icon-control + ascending JSON clipboard) → Stage 1 step 9 (`icon-control`, full API JSON, no re-sort); AC8 (no Slack Web API in TSX) → entire stage admin `api()` only; AC7, AC9, AC10 → N/A — sibling #2 auth/external/shapes

## Findings

### discuss

- **Location:** Stage 1 step 3 (`loadSlackChannels` parse filter)
- **Finding:** Plan requires both non-empty `id` and `name`; AST-1787/1788 allow rows with empty `name` when `id` is present.
- **Recommendation:** Filter on non-empty `id` only; label empty names in the `<select>` (e.g. show id or “(unnamed)”).

### acceptable

- **Scope fidelity:** Single file `AdminManageCandidates.tsx`; explicit no-touch on `CandidateProfile.tsx` (shapes-driven `FormFields` already renders channel fields from AST-1788).
- **Dependency:** Publish-ref tip includes sibling shapes (`slack_username`, channel profile fields) and admin routes (`slack_channels`, `slack_channel_membership`, `slack_channel_snapshot`).
- **Pattern reuse:** Mirrors unbound Slack bind (`slackBindFromSelection`, `loadUnboundSlackUsers`, toast-on-error) and **T** `icon-control` row action; clipboard pattern aligns with `copyJobSnapshotToClipboard` family.
- **AC honesty:** Documented pre-save bind limitation on membership GET matches sibling #2 contract; add-flow unbound warning without candidate id matches AC3.
- **Canon Scope (all X):** Statutes cited for lane consistency; plan correctly commits to no `app_log` and no handler logging — scope observation only, not a plan defect.
- **Self-assessment:** Estimate confirm 2 — agree; one stage, one file, established Contact UI patterns.

context_tokens≈58000

## Review (build stub)

**Commit:** `4f7e29d47a5a777281b14f7e356a2893ee1df208`  
**Branch:** `sub/AST-1786/AST-1789-manage-candidates-channel-column-s-snapshot`

**Built:** Manage Candidates flatten + `slack_username` column placeholder; channel `<select>` from admin list (id-only filter, `(unnamed)` labels per Joan discuss); membership `role="alert"` warning; stamp both channel fields on save; row **S** `icon-control` clipboard snapshot via admin API. No `CandidateProfile.tsx` touch.

## Radia review

[code-rubric]

**Ticket:** AST-1789  
**Publish ref:** `a5cbf620538ba1a52e469b49b10591b156e3af01` (`origin/sub/AST-1786/AST-1789-manage-candidates-channel-column-s-snapshot`)  
**Corpus:** `2ac86c3f693409c364f8630a97198c8dbfa9c6f3`  
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.info.api | X | | React-only diff — no `src/ui/api/**` changes; frontend does not write `app_log` |
| stat.logging.error | X | | React-only diff — no Python handlers; failures surface via toast |

**Canon Scope note:** Both frozen ids score **X** on this ticket by design (Joan plan + issue doc). Statutes are lane markers here, not scored product law — roll-up excludes **X**.

## Column diff vs plan stage

(aligned) — Joan scored both directives **X**; code review agrees (no applicable Python/API logging surface in AST-1789 product diff).

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Branch diff vs `origin/dev` bundles sibling prerequisites** (AST-1787 `slack.py` + tests/bible, AST-1788 `contact.py` / `api_contact.py` / `config.py` + tests/bible, sibling issue docs) from `sync(ftr): origin/ftr/AST-1786-manage-candidates-snapshot-slack-channel`. Expected per plan **Depends on** AST-1788; AST-1789 `code()` commit touched only `AdminManageCandidates.tsx`. No action unless merge-child wants ticket-pure diffs.
- **Joan plan discuss resolved in build:** `loadSlackChannels` filters on non-empty `id` only; `channelOptionLabel` shows `(unnamed)` for empty names — matches Joan’s recommendation, not the plan’s original id+name filter.
- **Membership warn staleness (documented limitation):** `runChannelMembershipCheck` runs on channel `<select>` change only, using `editForm.slack_user_id` at that moment. Changing Slack username bind without re-selecting channel can leave a stale warn until channel changes — sibling API still uses pre-save stored bind per plan; acceptable but worth knowing for UAT.
- **No clear-channel path on edit:** Selecting `— none —` omits channel keys on PUT (existing stored channel preserved per plan decision). Not a defect; admin cannot clear channel in this ticket.

## What's solid

- **Product scope:** Single-file delivery (`AdminManageCandidates.tsx`); no `CandidateProfile.tsx` touch (shapes-driven profile already has channel fields from AST-1788).
- **AC1:** `flattenCandidate` adds `slack_username`; column render shows trimmed value or `—`.
- **AC2:** Channel `<select>` from `GET /api/admin/contact/slack_channels`; save stamps both `contact.slack_channel_id` and `contact.slack_channel_name` via existing POST/PUT; no new writer.
- **AC3–5:** Inline `role="alert"` warnings; add/unbound skips membership GET; edit calls membership API; `not_member` / member-clear paths tested.
- **AC6 / AC8:** Row **S** uses shared `icon-control`; copies full snapshot API JSON (no re-sort, no truncate); no Slack Web API hosts/tokens in TSX (tests assert no `slack.com` URLs).
- **Tests:** Four `AST-1789` cases cover column placeholder, add stamp + unbound warn, edit membership warn cycle, S clipboard; `AST-1302` revised for **S** icon-control; existing Add/Edit suites stub `/slack_channels`.

## Recommended actions (downstream — not executed here)

- Chuckles: append this artifact to `docs/features/contact/ast-1789-manage-candidates-channel-column-s-snapshot.md`, commit `docs(AST-1789): Radia review — clean`, post slim upshot via `linear_proxy --as radia`, move to **Review Posted**.
- datt **§3h:** PROCEED → **User Testing** (no `resolve-child` work).
- Parent UAT (AST-1786): exercise end-to-end channel assign + **S** snapshot with real admin session when all three children are on ftr.

---
