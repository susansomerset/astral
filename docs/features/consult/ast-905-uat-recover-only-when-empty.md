# UAT: recover rubric only when criteria empty — do not overwrite edits

**Parent:** [AST-900 — craft get rubric did not populate the rubric content for candidate](https://linear.app/astralcareermatch/issue/AST-900/craft-get-rubric-did-not-populate-the-rubric-content-for-candidate)

**Linear:** [AST-905](https://linear.app/astralcareermatch/issue/AST-905/uat-recover-rubric-only-when-criteria-empty-do-not-overwrite-edits)

**Publish ref:** `origin/sub/AST-900/AST-905-uat-recover-only-when-empty`

**Summary (FIX-UAT):** Pending / ledger recovery on craft-rubric ArtifactEditor pages currently applies whenever `GET …/pending` returns criteria — including when the candidate **already has** stored (or loaded) rubric criteria. That overwrites user edits and existing criteria on return. Susan: restore **only if there are NONE** already. Empty rubrics still recover; non-empty must not be overwritten. Sibling Save / max_tokens tickets stay out of scope.

---

## Root cause (UAT)

| Observation | Implication |
|-------------|-------------|
| AST-902 recovery `useEffect` runs after `loaded` and always applies non-empty pending | Load hydrates existing criteria into tabs, then recovery replaces them with agent generation |
| `get_pending_craft_generation` returns stash/ledger even when `rubric_vector` already has criteria for that owner | Server offers recovery when the product should treat the artifact as already populated |
| Empty still must recover | Gate is “has any stored/loaded criteria content,” not “disable recovery entirely” |

**Conclusion:** Add an empty-only gate on both the recovery API (authoritative) and the ArtifactEditor apply path (belt). Do not change Generate, Save, or pending clear-on-Save.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | `get_pending_craft_generation`: 404 when stored rubric criteria already exist for that craft task | core |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Skip applying pending recovery when loaded tabs already have criterion content | ui (React) |

**Not in scope:** prompts, AST-903/906 Save/truncation, page wrappers, clearing pending when skipping (optional later — skip alone fixes overwrite).

---

## Stage 1: Backend — pending recovery only when stored rubric is empty

**Done when:** `get_pending_craft_generation(candidate_id, craft_*_rubric)` returns 404 `No recoverable generation` when that candidate already has one or more stored rubric criteria for the matching owner task; empty stored list still returns stash/ledger as today.

1. In `src/core/candidate.py` `get_pending_craft_generation`, after confirming craft rubric task and candidate exists, **before** reading pending stash:
   - `owner = rubric_owner_task_key(task_key)` (import from `src.utils.config` if not already imported — function already exists next to `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY`).
   - If `owner`: `existing = rubric_criteria_for_task(candidate_id, owner)` (already defined in this module).
   - If `isinstance(existing, list)` and `len(existing) > 0`: return `({"error": "No recoverable generation"}, 404)`.
2. Leave stash + ledger fallback paths unchanged when `existing` is empty / missing.
3. Do not clear pending in this function.

⚠️ **Decision:** “Already has criteria” = non-empty `rubric_criteria_for_task` (table-backed hydrate source). Matches what the editor loads via GET candidate hydration — not the raw `artifacts` blob.

⚠️ **Decision:** Return the same 404 body as other no-recovery cases so ArtifactEditor’s existing 404 no-op stays correct.

---

## Stage 2: Frontend — do not apply recovery over loaded content

**Done when:** After artifact load, if any tab has non-empty `content` (trim), the recovery effect does not call `setTabs` / enter review from pending — even if the API incorrectly returned 200.

1. In `ArtifactEditor.tsx` recovery `useEffect` (page-return recovery), immediately inside the async body **before** `api(…/pending)` (or immediately after a successful parse, before `setTabs`):
   - If `tabsRef.current.some(t => (t.content || "").trim() !== "")`, return without applying recovery (no toast).
2. Prefer the check **before** the fetch when `tabsRef` already reflects the completed load (`loaded === true` is already a gate) — avoids a useless pending request when criteria exist.
3. Empty placeholder-only load (`New Criterion` with empty content) still fetches and recovers as today.
4. No changes to live `doGenerate`, Save, or unmount autosave.

⚠️ **Decision:** Reuse the same emptiness notion as existing `hasData` (`content.trim() !== ""`) — not tab count (placeholder always creates one tab).

---

## Execution contract (for build-child)

- Stages in order; one `code(AST-905):` commit per stage; publish to `origin/sub/AST-900/AST-905-uat-recover-only-when-empty`.
- Merge `origin/ftr/AST-900-craft-get-rubric-populate` before coding (AST-904/906 tips may already be on ftr).
- Do not edit `tests/` / `docs/test-bible/**`.
- If `rubric_criteria_for_task` is empty while the UI still shows hydrated criteria (hydrate path drift) — stop and comment on parent AST-900.

---

## Self-Assessment

**Scope:** `Single-Component` — pending recovery gate in `candidate.py` + one guard in `ArtifactEditor`; all six craft-rubric pages inherit.

**Conf:** `high` — UAT overwrite is the unconditional recovery apply; empty-only gate is explicit from Susan.

**Risk:** `Medium` — too-strict empty check could block legitimate recovery after a failed Save with empty table; mitigated by keeping recovery when stored list length is 0 (AST-904 re-stash still helps empty-table failures).

---

## Rules review (ASTRAL_CODE_RULES)

| Rule | Compliance |
|------|------------|
| §1.3 DRY | Reuses `rubric_owner_task_key`, `rubric_criteria_for_task`, existing 404 contract. |
| §3.2 / §3.3 | API unchanged shape; core owns empty check; UI only skips apply. |
| Boundaries | Empty still recovers; no prompt/Save/AST-903 work. |
