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
