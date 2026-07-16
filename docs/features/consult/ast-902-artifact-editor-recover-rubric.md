# Artifact editor surfaces and recovers generated rubric criteria

**Parent:** [AST-900 — craft get rubric did not populate the rubric content for candidate](https://linear.app/astralcareermatch/issue/AST-900/craft-get-rubric-did-not-populate-the-rubric-content-for-candidate)

**Ticket:** [AST-902](https://linear.app/astralcareermatch/issue/AST-902/artifact-editor-surfaces-and-recovers-generated-rubric-criteria-craft)

**Publish ref:** `origin/sub/AST-900/AST-902-artifact-editor-recover-rubric`

**Summary:** Shared `ArtifactEditor` must leave generated rubric criteria on screen for review after Generate, and must recover a backend-completed generation when the HTTP wait was abandoned (navigate away, dropped connection). All six craft-rubric artifact pages share this editor — one fix covers company prefilter, job list, job description, get, do, and like. Backend stash + `GET …/generate/<task_key>/pending` are **AST-901** (Ada); this ticket consumes that contract only. Review-then-Save stays; no auto-Save of generated criteria into the stored artifact.

**Build dependency:** Do not start **build-child** until AST-901 product commits (pending stash + recovery endpoint) are on `origin/ftr/AST-900-craft-get-rubric-populate` (or merged into this sub via merge-on-checkout). Planning does not require that tip yet.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Apply live generate into review; recover pending on page load; harden empty/abort paths | ui (React) |

**Not in scope:** six page wrappers (already pass `artifactKey`/`taskKey` into `ArtifactEditor`); `ArtifactsCompanySearchTerms.tsx` (not a craft-rubric ArtifactEditor page); backend `candidate.py` / `api_candidate.py` (AST-901); prompts, schemas, grading; `craft_resume_base` auto-persist behavior.

---

## Stage 1: Shared criteria → tabs mapper + empty-criteria guard on live Generate

**Done when:** Live `doGenerate` for rubric mode applies non-empty `parsed.criteria` into tabs under review (`snapshot` held), and treats empty/missing criteria as a user-visible error that clears review mode. Fixed-field (`craft_resume_base`) path unchanged.

1. In `ArtifactEditor.tsx`, add a helper function (module scope or inside the component before `doGenerate`):
   ```ts
   function criteriaToTabs(criteria: { code?: string; label?: string; content?: string; importance?: number }[]): SideTab[] {
     return criteria.map((v, i) => ({
       id: `g_${i}`,
       code: v.code,
       label: v.label ?? `Criterion ${i + 1}`,
       content: v.content ?? "",
       importance: rubricItemImportance(v),
     }))
   }
   ```
2. In `doGenerate`, after `const parsed = data.parsed_response` and the existing `if (!parsed) throw …`:
   - **Fixed fields branch:** keep current mapping (`fixedFields.map…`); do not add empty-criteria throw for resume.
   - **Else (rubric):** `const criteria = Array.isArray(parsed.criteria) ? parsed.criteria : []`. If `criteria.length === 0`, `throw new Error("Generation returned no criteria")`. Else `setTabs(criteriaToTabs(criteria))`.
3. Keep existing success path: `setDirty(true)`, toast `"Generated — review and Save or Cancel"`, leave `snapshot` set (review mode). Keep existing catch: `setSnapshot(null)`, error toast, `finally` clears `generating`.

⚠️ **Decision:** Empty criteria is an error in the UI even if HTTP 200 — matches AST-901 Stage 2 empty-criteria guard; if Ada’s tip is not yet merged, this still prevents the silent “success toast / unchanged tabs / stuck snapshot” bug in today’s code.

---

## Stage 2: Page-return recovery via `GET …/generate/<task_key>/pending`

**Done when:** Opening a craft-rubric artifact page for a candidate with a pending completed generation loads criteria into **review mode** (Save/Cancel visible, dirty, snapshot of pre-recovery tabs) without writing the stored artifact until Save.

1. Add a `useEffect` in `ArtifactEditor` that runs only when:
   - `!jobPersistence`
   - `!fixedFields` (rubric mode — not base resume / shape-driven tabs)
   - `selectedId` and `taskKey` are set
   - `loaded === true` (candidate artifact load finished)
2. Effect body:
   - Let `cancelled = false` (or `AbortController`).
   - `api(\`/api/candidates/${selectedId}/generate/${taskKey}/pending\`)`.
   - If `cancelled`, return without `setState`.
   - If status is **404** or **400**: no-op (no pending / not a craft rubric task).
   - If other non-OK: toast error with message from JSON `error` or `HTTP ${status}`; do not change tabs.
   - If OK: `const data = await resp.json()`. Require `data.success` and `data.parsed_response` with non-empty `criteria` array; else no-op (or toast `"No recoverable generation"` only if `data.error` present).
   - Enter review mode without overwriting the stored artifact:
     - `setSnapshot(tabsRef.current.map(t => ({ ...t })))` — capture whatever is on screen (empty placeholder or prior saved criteria).
     - `setTabs(criteriaToTabs(data.parsed_response.criteria))`.
     - `setDirty(true)`.
     - Toast: `"Recovered completed generation — review and Save or Cancel"` (variant `success`).
3. Cleanup: set `cancelled = true` (and abort if using `AbortController`).
4. Do **not** call Save from this effect. Do **not** clear pending client-side — Save already clears via AST-901 `update_candidate_data` when the matching artifact key is written.
5. Dependency array: `[jobPersistence, selectedId, taskKey, loaded, fixedFields]` — do **not** depend on `tabs` (would re-fetch in a loop).

⚠️ **Decision:** Recovery uses the same review gate as live Generate (snapshot + Save/Cancel). Cancel restores pre-recovery tabs and clears snapshot; pending stash remains until a successful Save of that artifact (Ada clears on Save) — if the user Cancels, a later revisit may recover again. That is intentional: Cancel must not discard a backend COMPLETED the user has not Saved.

⚠️ **Decision:** Skip pending fetch for `jobPersistence` and fixed-field editors so base resume and job-scoped ArtifactEditor usages are untouched.

---

## Stage 3: Unmount-safe live Generate + abandoned-wait messaging

**Done when:** A Generate whose HTTP response arrives after the editor unmounted does not call `setState`; if the in-flight request fails with a network/abort-style error, the user sees a toast that recovery may be available on return — without inventing a second recovery API.

1. In `doGenerate`, before `fetch`/`api`, create `const ac = new AbortController()` and store it in a `useRef` (e.g. `generateAbortRef`). On component unmount (`useEffect` cleanup), call `generateAbortRef.current?.abort()`.
2. Pass `{ method: "POST", signal: ac.signal }` into `api(...)` (ensure `api.ts` forwards `signal` via `RequestInit` — it already spreads `options` into `fetch`; no `api.ts` change unless TypeScript complains).
3. In `doGenerate` catch:
   - If `ac.signal.aborted` or `(e as Error).name === "AbortError"`: do **not** toast a hard failure; leave catch silent for abort (component is gone or remounting). Still `setGenerating(false)` / `setSnapshot(null)` only if still mounted — use a `mountedRef` flipped false on unmount, and gate all `setState` in `doGenerate` on `mountedRef.current`.
4. For other failures (network TypeError, failed fetch, HTTP errors): keep error toast. When the message indicates a network failure (e.g. `TypeError` / `"Failed to fetch"`), use toast text: `"Generation request interrupted — if it finished on the server, return to this page to recover"` (variant `error`). HTTP 4xx/5xx keep the server `error` string.
5. Do **not** poll pending inside `doGenerate` after failure — Stage 2 handles page return. Do **not** change autosave-on-unmount behavior for dirty review drafts beyond existing code.

⚠️ **Decision:** Abort + mounted guard prevents React warnings and avoids applying a late response onto a different candidate page; durability remains AST-901 stash + Stage 2 recovery.

---

## Execution contract (for build-child)

- Execute stages in order; one commit per stage on the epic worktree checkout of this sub; publish each to `origin/sub/AST-900/AST-902-artifact-editor-recover-rubric`.
- Before Stage 1 product work: `git fetch origin && git merge origin/ftr/AST-900-craft-get-rubric-populate` so AST-901 recovery endpoint exists; if the merge lacks `GET …/pending`, **stop** and comment on parent AST-900.
- Do **not** edit backend files, test-tree, or the six thin page wrappers unless a page stops compiling because of a prop change (none planned).
- Do **not** auto-Save generated or recovered criteria into `candidate_data.artifacts`.
- If `GET …/pending` response shape differs from AST-901 plan (`success`, `parsed_response.criteria`, `batch_id`, `recovered`) — stop and comment on parent AST-900.

---

## Self-Assessment

**Scope:** `Single-Component` — only `ArtifactEditor.tsx`; all six craft-rubric pages inherit via the shared component.

**Conf:** `high` — AST-901 defines the recovery contract; current `doGenerate` / review (`snapshot`) / Save paths are the exact surfaces to wire; no prompt or grading changes.

**Risk:** `Medium` — shared editor also serves base resume (fixed fields) and job persistence; incorrect gating could fetch pending or enter review on those modes. Mitigated by explicit `!jobPersistence && !fixedFields` guards.

---

## Rules review (ASTRAL_CODE_RULES)

| Rule | Compliance |
|------|------------|
| §1.3 DRY | One recovery + criteria mapper in `ArtifactEditor`; pages stay one-liners. |
| §2.1 config | No new frontend hardcoded state lists; Generate visibility still from `artifact_generate_states` manifest. |
| §3.2 UI | Frontend renders API results; no business rules beyond review-then-Save already present. |
| §3.3 imports | No new layers; stays in `src/ui/frontend`. |
| §3.5 naming | Reuses existing `taskKey` / `artifactKey` props; pending URL matches Ada’s route. |
| §1.5.1 debug | No backend debug work (AST-901). |

No conflicts requiring escalation.
