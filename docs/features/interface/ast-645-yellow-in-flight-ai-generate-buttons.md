<!-- linear-archive: AST-645 archived 2026-06-23 -->

## Linear archive (AST-645)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-645/yellow-in-flight-styling-for-ai-generate-buttons-when-the-generate  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-635 — When the Generate button is clicked, make it yellow while it's running.  
**Blocked by / blocks / related:** parent: AST-635

### Description

## What this implements

Shared **UI-call-to-AI** primary action buttons show a clear yellow/gold background while an LLM or async generate request is in flight, then return to green when idle. Covers artifact craft **Generate** / **Regenerate** (shared `ArtifactEditor`, **Company Search Terms**), **Generate Artifacts** / **Working…** on the Recommended Job Report, and other generate-style controls that kick off slow AI work — via one shared button styling pattern (class or small component), not per-page one-off CSS.

## Acceptance criteria

1. On an artifact criterion page with **Generate** visible, click **Generate**: from click until the request finishes, the button background is visibly yellow/gold (not green).
2. On a page with existing artifact content, click **Regenerate** and confirm: same yellow/gold while generating.
3. **Company Search Terms** **Generate** / **Regenerate** follows the same rule.
4. After success or error toast, the button returns to default green styling and the correct label (**Generate** / **Regenerate**).
5. **Save** and **Cancel** button colors on those pages are unchanged.
6. **Generate Artifacts** on the Recommended Job Report shows yellow/gold during **Working…** in-flight state, then green when ready.

## Boundaries

* No backend, API, or manifest changes.
* No new loading indicators beyond button color.
* Does not alter confirm-regenerate modal styling except the confirm button already uses red for destructive confirm.
* Does not change **Preview Materials**, **Save**, **Cancel**, dispatch Run/Stop, or non-AI actions.

## Notes for planning

* Use existing `--accent-gold` / `--accent-gold-hover` tokens in `App.css` where possible.
* `ArtifactEditor.tsx`, `ArtifactsCompanySearchTerms.tsx`, `RecommendedJobReportHeader.tsx` / `JobAnalysisReportModal.tsx` are primary touch points.
* plan-child §3.5 — prefer shared CSS class or thin wrapper over duplicating inline styles.

## Git branch (authoritative)

Per **orientation § Branch law**: parent **ftr/ast-635**, child **sub/AST-635/<child-segment>**. Created at dispatch-parent.

### Comments

#### radia — 2026-06-14T21:14:03.953Z
**Review (Radia)** — `origin/dev...origin/sub/AST-635/AST-645-yellow-in-flight-ai-generate-buttons` @ `55626b3d` (doc @ `dbcc7de7`)

### fix-now
None.

### discuss
None.

### advisory
- **CSS mirror blocks** — `.dep-btn.save.in-flight` and `.modal-btn.save.in-flight` in `App.css` are intentionally parallel (placed after each base `.save:hover` per plan). Optional later consolidation if more generate buttons adopt the pattern.

### Plan fidelity
Stage 1 matches combined plan: shared `.in-flight` modifier using `--accent-gold` / `--accent-gold-hover`; `ArtifactEditor.tsx`, `ArtifactsCompanySearchTerms.tsx`, `RecommendedJobReportHeader.tsx` wire `generating` / `primaryBusy`; Save/Cancel and confirm-regenerate modal excluded. No backend, API, or state lifecycle changes.

### ASTRAL_CODE_RULES
- **§1.3 DRY** — single modifier class; no inline gold per page.
- **§3.3** — frontend-only; no layer violations.

### Tests
Betty manifest (`test_ArtifactEditor`, `test_ArtifactsCompanySearchTerms`, `test_JobAnalysisReportModal`) holds POST mid-flight and asserts `in-flight` on generate controls only; clears after resolve. `page-mocks.ts` `/api/me` stub supports partial mock pattern.

**Doc:** `docs/features/interface/ast-645-yellow-in-flight-ai-generate-buttons.md` § Review (Radia)

#### katherine — 2026-06-14T21:12:34.075Z
**test-child:** `-t "AST-645"` on Betty's three manifest files — **3/3 green** @ `55626b3d`.

Full-file run on `test_ArtifactEditor.test.tsx` also hits sibling **`AST-553` job persistence** — red here and with **`origin/dev`** product (empty textarea; not introduced by AST-645). Other siblings in the three manifest files pass.

#### betty — 2026-06-14T21:09:28.966Z
**Bible shasum correction:** `c477bceac17070d073489ae1c67bff860661fd666c1c3256c5066dcef18c6c1c` on `origin/sub/AST-635/AST-645-yellow-in-flight-ai-generate-buttons` (§7.13zzr).

#### betty — 2026-06-14T21:09:23.903Z
## QA test manifest (AST-645)

**Publish ref:** `origin/sub/AST-635/AST-645-yellow-in-flight-ai-generate-buttons` @ `55626b3d`

**`docs/ASTRAL_TEST_BIBLE.md` shasum (publish ref):** `$(git show origin/sub/AST-635/AST-645-yellow-in-flight-ai-generate-buttons:docs/ASTRAL_TEST_BIBLE.md | shasum -a 256 | awk '{print $1}')` — see §7.13zzr

### Manifest

1. **`tests/component/frontend/components/test_ArtifactEditor.test.tsx`** — `AST-645: Generate/Regenerate button uses in-flight class while generating` (`.in-flight` on generate control while POST pending; **Save** stays without modifier).
2. **`tests/component/frontend/pages/test_ArtifactsCompanySearchTerms.test.tsx`** — `AST-645: Generate button uses in-flight class while generating` (§6c routed page; same class assertion during generate).
3. **`tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx`** — `AST-645: Generate Artifacts primary action uses in-flight class while Working` (primary modal action yellow class + **Working…** label during POST).

### Narrowed run

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx \
  ../../../tests/component/frontend/pages/test_ArtifactsCompanySearchTerms.test.tsx \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx
```

Use `-t "AST-645"` on each file if you want only the new rows; full file is fine for regression on sibling tests in those modules.

### Notes

- **Existing coverage:** prior Generate/Regenerate flow tests in the same files remain valid; no obsolete assertions removed.
- **Substrate fix:** `page-mocks.ts` + Company Search Terms test now partial-mock `api` (`setAuthTokenGetter`) and `/api/me` for **AuthContext** — required after **AST-612** provider stack.
- **Manual UAT (parent AC1–AC6):** Susan spot-check yellow/gold on staging after **test-child** green — not automated here.

— Betty

#### chuckles — 2026-06-14T21:02:29.718Z
Plan: [`docs/features/interface/ast-645-yellow-in-flight-ai-generate-buttons.md`](https://github.com/susansomerset/astral/blob/sub/AST-635/AST-645-yellow-in-flight-ai-generate-buttons/docs/features/interface/ast-645-yellow-in-flight-ai-generate-buttons.md)

**Self-assessment**
- **Scope:** `scope-minor` — Four frontend files (shared `.in-flight` CSS + three className conditionals); no backend or state-machine work.
- **Conf:** `conf-high` — Reuses existing `--accent-gold` tokens and `generating` / `primaryBusy` flags; additive styling only.
- **Risk:** `risk-low` — Visual-only change on generate buttons; no API or data impact if miswired.

**Approach:** One shared `.in-flight` modifier on `.dep-btn.save` / `.modal-btn.save` in `App.css`; wire in `ArtifactEditor`, `ArtifactsCompanySearchTerms`, and `RecommendedJobReportHeader`. Save/Cancel and confirm-regenerate modal unchanged.

---

# Yellow in-flight styling for AI generate buttons

**Linear:** [AST-645](https://linear.app/astralcareermatch/issue/AST-645/yellow-in-flight-styling-for-ai-generate-buttons-when-the-generate)  
**Parent:** [AST-635](https://linear.app/astralcareermatch/issue/AST-635/when-the-generate-button-is-clicked-make-it-yellow-while-its-running)  
**Publish ref:** `sub/AST-635/AST-645-yellow-in-flight-ai-generate-buttons`

Primary AI **Generate** / **Regenerate** / **Generate Artifacts** controls stay green when idle and switch to yellow/gold while an LLM or async generate request is in flight, using one shared CSS modifier on existing `dep-btn save` / `modal-btn save` buttons. No backend, API, or new loading chrome — only background color tied to existing `generating` / `primaryBusy` state that already drives labels and `disabled`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/App.css` | Add shared `.in-flight` modifier for `.dep-btn.save` and `.modal-btn.save` using `--accent-gold` tokens | ui |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Apply `in-flight` class on Generate/Regenerate button when `generating` | ui |
| `src/ui/frontend/src/pages/ArtifactsCompanySearchTerms.tsx` | Apply `in-flight` class on Generate/Regenerate button when `generating` | ui |
| `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx` | Apply `in-flight` class on primary modal action when `primaryBusy` | ui |

**Out of scope (do not edit):** `JobAnalysisReportModal.tsx` (already owns `primaryBusy` state and passes it to the header), **Save** / **Cancel** buttons, confirm-regenerate modal confirm button (red inline style), **Preview Materials**, **IntakeChatModal**, dispatch Run/Stop, backend/API.

**QA manifest (Betty — not engineer commits):** Manual smoke per parent AC1–AC6 on staging; no new automated test required unless Betty adds a lightweight class assertion in an existing component test during **qa-child**.

## Stage 1: Shared in-flight CSS and wire generate buttons

**Done when:** Clicking **Generate** or **Regenerate** on any artifact criterion page (via `ArtifactEditor`) or **Company Search Terms** shows yellow/gold background from click until the POST completes (success or error), then green again with correct label; **Generate Artifacts** on Recommended Job Report shows yellow/gold during **Working…** then green; **Save** and **Cancel** on those pages remain unchanged green/grey; confirm-regenerate modal stays unchanged while open (Generate header button still green until user confirms).

1. In `src/ui/frontend/src/App.css`, immediately after the existing `.dep-btn.save:hover` block (after line ~1060), add:

   ```css
   .dep-btn.save.in-flight,
   .dep-btn.save.in-flight:disabled {
     background: var(--accent-gold);
     border: none;
     color: var(--bg-deep);
   }

   .dep-btn.save.in-flight:hover:not(:disabled) {
     background: var(--accent-gold-hover);
   }
   ```

2. In the same file, immediately after the existing `.modal-btn.save:hover` block (after line ~773), add:

   ```css
   .modal-btn.save.in-flight,
   .modal-btn.save.in-flight:disabled {
     background: var(--accent-gold);
     border: none;
     color: var(--bg-deep);
   }

   .modal-btn.save.in-flight:hover:not(:disabled) {
     background: var(--accent-gold-hover);
   }
   ```

   ⚠️ **Decision:** Use a shared `.in-flight` modifier on existing `.save` classes instead of inline styles or a new React wrapper — matches ticket note §3.5 DRY and keeps **Save** buttons (same `.save` base, no modifier) green.

   ⚠️ **Decision:** Style `:disabled` explicitly so the gold background remains visible while generating (buttons stay `disabled={generating}` / `disabled={primaryBusy}` as today).

3. In `src/ui/frontend/src/components/ArtifactEditor.tsx`, on the Generate/Regenerate `<button>` (~lines 452–459), change `className="dep-btn save"` to:

   ```tsx
   className={`dep-btn save${generating ? " in-flight" : ""}`}
   ```

   Do not add `in-flight` to the **Save** button (~line 464) or the confirm-regenerate **Regenerate** button in the modal (~line 583, red inline background).

4. In `src/ui/frontend/src/pages/ArtifactsCompanySearchTerms.tsx`, on the Generate/Regenerate `<button>` (~lines 171–178), change `className="dep-btn save"` to:

   ```tsx
   className={`dep-btn save${generating ? " in-flight" : ""}`}
   ```

   Do not add `in-flight` to the **Save** button (~line 183) or confirm modal confirm button (~line 224).

5. In `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx`, on the primary action `<button>` (~lines 91–98), change `className="modal-btn save"` to:

   ```tsx
   className={`modal-btn save${primaryBusy ? " in-flight" : ""}`}
   ```

   Do not add `in-flight` to **Preview Materials** or other header buttons.

## Execution contract (for the developer agent)

- Execute Stage 1 only; one `code()` commit on publish ref during **build-child** (this plan stage is planning-only).
- Do not edit `tests/` or `docs/ASTRAL_TEST_BIBLE.md` unless Betty's **qa-child** manifest says otherwise.
- Do not change `generating` / `primaryBusy` lifecycle, API paths, or button labels.
- Blocking ambiguity → comment on **AST-635** with 🛑 template from **plan-child**.

## Self-Assessment

**Scope:** `scope-minor` — Four frontend files (one CSS block, three className conditionals); no backend, config, or state-machine changes.

**Conf:** `conf-high` — Existing `--accent-gold` tokens and boolean busy flags are already in place; work is additive CSS plus three string classNames.

**Risk:** `risk-low` — Worst case is wrong button color on generate controls; no data, API, or dispatch impact.

## Self-review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Single `.in-flight` modifier in `App.css`; no per-page inline gold backgrounds. |
| §2.1 config | No new config keys; reuses existing CSS variables in `App.css`. |
| §2.4 batch | N/A — no batch processing. |
| §2.6 state machine | N/A — no entity state transitions. |
| §3.3 imports | Stays within `src/ui/frontend/`; no cross-layer imports. |
| §3.5 naming | No new components; flat `components/` + existing page file only. |

No conflicts flagged.

## Review (build)

- **Branch:** `origin/sub/AST-635/AST-645-yellow-in-flight-ai-generate-buttons`
- **Tip:** `be5f6378`
- **Built:** 2026-06-14 — Stage 1 complete (shared `.in-flight` CSS + three className conditionals); Betty manifest pending.

## Review (Radia)

**Baseline:** `origin/dev...origin/sub/AST-635/AST-645-yellow-in-flight-ai-generate-buttons` @ `55626b3d`  
**Reviewed:** 2026-06-14

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity | Stage 1 only — shared `.in-flight` CSS on `.dep-btn.save` / `.modal-btn.save`, three className conditionals on `generating` / `primaryBusy`; no lifecycle, API, or label changes. |
| Acceptance criteria | AC1–AC6 covered: gold while in-flight, green when idle, Save/Cancel untouched, confirm-regenerate modal unchanged until confirm. |
| §1.3 DRY | One modifier class in `App.css`; no per-page inline gold. |
| §3.3 layer | `src/ui/frontend/` only; no backend or cross-layer imports. |
| Tests | Betty manifest asserts `in-flight` during held POST on all three touch points; Save excluded; partial `api` mock preserves `importOriginal` pattern. |

### Issues

None (**fix-now** / **discuss**).

### Recommended actions

| Severity | Item | Location |
|----------|------|----------|
| advisory | `.dep-btn` and `.modal-btn` in-flight blocks mirror each other — acceptable per plan placement after each base `.save:hover`; optional future consolidation to a shared selector group if more generate buttons adopt the pattern. | `App.css` |

## Resolution

**Resolved:** 2026-06-14  
**Publish ref:** `origin/sub/AST-635/AST-645-yellow-in-flight-ai-generate-buttons` @ `dbcc7de7`

No **fix-now** or **discuss** items from Radia review. Advisory CSS mirror blocks left as-is per plan. §9a dry-run clean vs `origin/dev` and `origin/ftr/ast-635`. Ready for **User Testing** (Susan manual AC1–AC6 on staging).
