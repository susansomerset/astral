# AST-1017 — Mechanical intake front door UI

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1017/mechanical-intake-front-door-ui-candidate-profile-preamble-to-intake  
**Parent:** https://linear.app/astralcareermatch/issue/AST-952/candidate-profile-preamble-to-intake  

**Publish ref (origin):** `sub/AST-952/AST-1017-mechanical-intake-ui`  
**Parent integration ref:** `ftr/AST-952-candidate-profile-preamble-to-intake`

Ship the **mechanical preamble front door** on Candidate Intake: read `PREAMBLE_CONFIG` from `GET /api/ui_config`, show **Intro** in Estelle-consistent presentation, walk ordered steps (resume → LinkedIn → sample cover letter), call Ruth validation (`POST …/preamble/validate`), persist **only** on `outcome === "Valid"` into the AST-1014 context library fields, then hand off into the existing Estelle `IntakeChatModal` session flow. Familiar seamless feel — same wide modal chrome and `.intake-msg--assistant` styling as Estelle chat.

Boundaries (do **not** implement): contact/context/artifacts library schema or remaps (AST-1014), Ruth agent_task / `validate_preamble_answer` core (AST-1015), `PREAMBLE_CONFIG` ownership or copy edits (AST-1016), Topic Menu / Estelle “Anything here you would change?” confirm (AST-953), hopes/interests/concerns editors, candidate state-machine changes, new agent personas, inlined validation logic in React.

**Prerequisite at build:** AST-1014 + AST-1016 are on `origin/ftr/AST-952-candidate-profile-preamble-to-intake`. AST-1015 is User Testing on `origin/sub/AST-952/AST-1015-preamble-validation-ruth` — **Chuckles `merge-child` must land it on ftr before Stage 1 can call validate live**. If `POST /api/candidates/<id>/preamble/validate` is missing after merging ftr, **stop** and comment on parent AST-952 (do not stub validation in the UI).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/IntakePreamblePanel.tsx` | New: Intro + ordered mechanical steps; Ruth validate; PUT library on Valid only | ui |
| `src/ui/frontend/src/pages/CandidateIntake.tsx` | New-intake → preamble phase → Estelle modal; remove Profile-only resume hard-gate when preamble can collect | ui |
| `src/ui/frontend/src/App.css` | Preamble panel styles reusing intake assistant/user message look; step composer | ui |

No Python/config/agent_task changes. No `IntakeChatModal.tsx` behavior change beyond receiving materials after preamble (same props). No `tests/` edits (Betty owns tests after Code Complete).

---

## Sibling contracts (read-only — do not re-implement)

### AST-1016 — `PREAMBLE_CONFIG` via ui_config

`GET /api/ui_config` (system blueprint, `@require_auth`) returns:

```json
{
  "preamble": {
    "intro": "<string>",
    "validation_task_key": "preamble_validate_response",
    "steps": [
      {
        "id": "raw_resume",
        "order": 1,
        "prompt_1st_try": "<string>",
        "prompt_2nd_try": "<string>",
        "target": { "blob": "context", "field": "raw_resume" },
        "validation_question": "<string>"
      }
    ]
  }
}
```

Three steps in order: `raw_resume` → `raw_profile` → `raw_sample`. UI must **not** hardcode step ids, prompts, or field names — iterate `preamble.steps` sorted by `order`.

### AST-1015 — Ruth validate API

```
POST /api/candidates/<candidate_id>/preamble/validate
Body: { "question": "<step.validation_question>", "answer": "<paste>", "step_index": <step.order>, "step_total": <steps.length> }
Response 200: { "success": bool, "outcome": "Valid"|"Try Again"|"Escalate"|null, "error": ..., "batch_id": ... }
```

- Advance / persist **only** when `success === true` and `outcome === "Valid"`.
- `Try Again` / `Escalate` / `success === false` → do **not** write library fields; do **not** advance.
- Do **not** call `do_task` or invent a client-side checker.

### AST-1014 — persist home

```
PUT /api/candidates/<candidate_id>/data
Body: { "context": { "<field>": "<answer>" } }
```

Deep-merge; one field per Valid step. After all steps done (or skipped), materials for Estelle session POST keep AST-558 call-boundary names:

| Session POST body key | Library field |
|-----------------------|---------------|
| `starting_resume_text` | `context.raw_resume` |
| `linkedin_profile_text` | `context.raw_profile` |
| `sample_cover_text` | `context.raw_sample` |

---

## Stage 1: `IntakePreamblePanel` — config-driven mechanical steps

**Done when:** A new component renders Intro + one step at a time from `preamble` config, calls Ruth validate, PUTs the target field only on Valid, handles Try Again / Escalate / transport errors without advancing, and invokes `onComplete(materials)` with the three session-body keys populated from the latest library values. `tsc` passes. Not yet wired as the Intake page gate.

1. Create `src/ui/frontend/src/components/IntakePreamblePanel.tsx` with props:

```ts
export type PreambleMaterials = {
  starting_resume_text: string
  sample_cover_text: string
  linkedin_profile_text: string
}

export type IntakePreamblePanelProps = {
  candidateId: string
  /** Current context raw_* (and legacy aliases already resolved by parent). */
  initialMaterials: PreambleMaterials
  onComplete: (materials: PreambleMaterials) => void
  onCancel: () => void
}
```

2. On mount, `GET /api/ui_config` and read `preamble`. If missing/malformed (`!intro` or `!Array.isArray(steps)` or empty steps), toast error and call `onCancel` — do not invent a local fallback script.

3. Build `pendingSteps`: sort `preamble.steps` by `order` ascending; **include** a step when the corresponding material string is empty after trim:

| `target.field` | material key |
|----------------|--------------|
| `raw_resume` | `starting_resume_text` |
| `raw_profile` | `linkedin_profile_text` |
| `raw_sample` | `sample_cover_text` |

⚠️ **Decision — skip non-empty targets:** If Profile (or a prior Valid preamble) already stored a non-empty value for that field, **skip** the step. Do not re-validate Profile-entered text in this ticket. Mechanical UI fills **gaps** and is the front door when fields are empty.

⚠️ **Decision — Intro always on this panel:** When the panel mounts for a new-intake / Start-Over path, always show `preamble.intro` as an assistant-styled bubble (`.intake-msg.intake-msg--assistant`) before the first pending prompt — even if `pendingSteps` is empty. If `pendingSteps` is empty after Intro, show a single **Continue** button that calls `onComplete(initialMaterials)`.

4. Layout inside the existing wide Modal body pattern (parent supplies Modal or this panel is placed where materials used to live — Stage 2 decides host; this component owns inner chrome only):

   - Thread region: Intro bubble; current step prompt as assistant bubble (`prompt_1st_try` on first attempt for that step, `prompt_2nd_try` after any Try Again on that step).
   - Composer: one `<textarea className="intake-preamble-input">` + **Submit** button (disabled when empty/busy).
   - Footer: **Cancel** → `onCancel`.

5. On Submit for step at index `i` in `pendingSteps` (1-based display index for humans is fine; Ruth `step_index` / `step_total` **must** be `step.order` and `preamble.steps.length` — full script length, not pending-only):

   a. `POST /api/candidates/${candidateId}/preamble/validate` with  
      `{ question: step.validation_question, answer: draft, step_index: step.order, step_total: preamble.steps.length }`.
   b. If HTTP not OK → toast error from body; stay on step.
   c. Parse JSON. If `!success` or `outcome` not in the closed set → toast `error` or “Validation failed”; stay.
   d. `outcome === "Try Again"` → set that step’s attempt to 2nd-try; replace visible prompt with `prompt_2nd_try`; clear draft; stay. Do **not** PUT.
   e. `outcome === "Escalate"` → toast: `This answer needs human review. Try a clearer paste, or edit this field on Profile and return to Intake.`; stay. Do **not** PUT. Do **not** treat Escalate as Valid.
   f. `outcome === "Valid"` → `PUT /api/candidates/${candidateId}/data` with  
      `{ context: { [step.target.field]: draft.trim() } }`  
      (`Content-Type: application/json`). On PUT failure → toast; stay (do not advance — Valid was judged but not recorded). On PUT OK → update local materials map for that field; advance to next pending step or `onComplete` with full materials.

6. Do **not** read or display `validation_task_key` in the UI beyond trusting the validate endpoint. Do **not** hardcode Valid/Try Again/Escalate string sets in multiple places — compare against the three literal strings in one local const `PREAMBLE_OUTCOMES` at the top of the file (UI mirror of the closed set; source of truth for outcomes remains AST-1015 config).

7. Reuse `api` from `../lib/api`, `Toast` patterns from `IntakeChatModal`. No new npm deps.

---

## Stage 2: Wire `CandidateIntake` — preamble before Estelle

**Done when:** New intake / Start Over opens the wide intake Modal in **preamble** phase first (Intro + mechanical steps); after `onComplete`, the same Modal (or immediate handoff) runs existing `IntakeChatModal` auto-start with persisted materials. Continue-on-active-session skips preamble. The old hard redirect “Add Original Resume Text on Profile before starting Intake” is removed when the preamble path can collect `raw_resume`. Profile remains available for edits; hopes/interests/concerns editors are **not** added.

1. In `CandidateIntake.tsx`, introduce phase state:

```ts
type IntakePhase = "idle" | "preamble" | "chat"
```

2. **Remove** the early return that toasts and `goProfile()` when `!loaded.starting_resume_text.trim()`. Instead keep loading materials (including empty strings) and proceed to confirm / resume dialog as today.

3. After user confirms **Start Intake** (no active session) **or** completes **Start Over** archive path:
   - Set `materials` from loaded/empty values.
   - Set phase `"preamble"` and open the wide Modal host (see step 5).
   - Do **not** open `IntakeChatModal` yet.

4. **Continue** on active session: set phase `"chat"`, open `IntakeChatModal` with current materials — **skip preamble** (session already past the front door).

5. Host chrome — pick **one** structure and implement exactly:

⚠️ **Decision — single wide Modal, two phases:** Reuse one `Modal open title="Candidate Intake" size="wide"`. When `phase === "preamble"`, render `IntakePreamblePanel` inside it. When `phase === "chat"`, render the **body** of today’s Estelle chat by either (a) extracting chat body from `IntakeChatModal` — **forbidden** (too much churn), or (b) closing preamble and mounting existing `IntakeChatModal` with `open autoStart` (and `freshStart` when Start Over). **Choose (b):** on preamble `onComplete`, set materials from callback, set `phase` to `"chat"`, mount `<IntakeChatModal … materials={materials} autoStart freshStart={…} />` as today. On preamble `onCancel`, `goProfile()`.

6. `IntakePreamblePanel` may render inside a lightweight wrapper Modal in the page when `phase === "preamble"`:

```tsx
{phase === "preamble" && (
  <Modal open onClose={goProfile} title="Candidate Intake" size="wide">
    <IntakePreamblePanel
      candidateId={selectedId}
      initialMaterials={materials}
      onComplete={handlePreambleComplete}
      onCancel={goProfile}
    />
  </Modal>
)}
{phase === "chat" && (
  <IntakeChatModal … />
)}
```

7. `handlePreambleComplete(m)`: `setMaterials(m)`; `setPhase("chat")`. Ensure `starting_resume_text` is non-empty before chat — if still empty after preamble (user cancelled mid-flight should not reach here; if Valid path somehow skipped resume), toast and `goProfile()` rather than POST session without resume.

8. Do **not** edit `NAV_CONFIG`, routes, or Estelle session/turn/build endpoints. Do **not** add hopes/interests/concerns fields to this UI (AC5: fields exist via AST-1014; confirm UI is AST-953).

---

## Stage 3: CSS — Estelle-consistent preamble presentation

**Done when:** Intro and step prompts visually match assistant bubbles in the intake thread; preamble composer aligns with existing intake composer spacing; no new global theme.

1. In `src/ui/frontend/src/App.css` under the existing `/* ---- Intake chat modal ---- */` section, add:

   - `.intake-preamble-panel` — column flex, gap matching `.intake-modal-body`
   - `.intake-preamble-thread` — reuse `.intake-thread` rules (or compose both classes in JSX: `className="intake-thread intake-preamble-thread"`)
   - `.intake-preamble-input` — same box model as `.intake-composer-input` / former `.intake-materials-field` min-height ~4rem
   - `.intake-preamble-actions` — footer row for Submit / Cancel matching `.intake-actions`

2. Prefer **reusing** `.intake-msg`, `.intake-msg--assistant`, `.intake-msg--user` over new bubble colors. Do not introduce a second visual language for Intro.

3. Run `cd src/ui/frontend && npx tsc -b --noEmit` after Stages 1–3. Fix only type errors in files listed in Files Changed.

---

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the Files Changed table.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on the Linear parent issue (AST-952), and waits.**
- Completes a stage on the epic worktree, commits, publishes to `origin/sub/AST-952/AST-1017-mechanical-intake-ui`, then proceeds.

Blocking comment format (parent AST-952):

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

---

## Self-Assessment

**Scope:** Single-Component — React intake UI only (`IntakePreamblePanel` + `CandidateIntake` wiring + CSS). Consumes AST-1014/1015/1016 APIs; no core/data/config authorship.

**Conf:** high — sibling contracts are shipped (1014/1016 on ftr; 1015 on sub UT); existing intake modal, `api` client, and ui_config preamble expose are known; outcome handling rules are explicit in AST-1015.

**Risk:** Medium — wrong Valid gate would persist bad raw_* into the library that Topic Menu (AST-953) reads; mitigated by requiring `success && outcome === "Valid"` before PUT and never treating Escalate as Valid. Build blocked if AST-1015 is not yet on ftr.

---

## Code Rules self-review

| Rule | Check |
|------|--------|
| §1.3 DRY | One panel for all steps; reuse Modal/`api`/Toast/intake message classes; no duplicated step hardcodes |
| §1.4 / §2.1 / `astral.config.config-source-of-truth` | Step order, prompts, targets, Intro from `PREAMBLE_CONFIG` via ui_config only |
| §3.2 / `astral.layers.ui-config-driven-business-logic` | UI executes config; does not own script or validation |
| §3.3 import-direction | Frontend → API only; no core/data imports from React |
| §1.5.1 | UI has no debug-logging requirement (backend only) |
| §3.5 naming / file placement | PascalCase component in `components/`; page stays `CandidateIntake.tsx`; CSS in `App.css` |
| §2.6 state machine | No candidate state transitions |
| New agents | Forbidden — Ruth via AST-1015 API only |

---

## Review

**Publish ref:** `sub/AST-952/AST-1017-mechanical-intake-ui`  
**Build tip:** `54ed55439c794c55c9b26796f6a87102598adfe3`

### Stages delivered

1. `IntakePreamblePanel` — loads `preamble` from `GET /api/ui_config`; Intro + ordered gap-fill steps; Ruth `POST …/preamble/validate`; PUT `context.<field>` only on Valid; Try Again / Escalate do not advance.
2. `CandidateIntake` — new-intake / Start Over → preamble Modal → Estelle `IntakeChatModal`; Continue-on-active skips preamble; Profile resume hard-gate removed.
3. `App.css` — Estelle-consistent preamble panel / input / actions.

### Radia — code-rubric.v1 (`[code-rubric] revision=1`)

**Tip reviewed:** `417778929d12a8c8bf4ba8fbe4dc3ec1f14f6d16` (`origin/sub/AST-952/AST-1017-mechanical-intake-ui` vs `origin/dev`)
**Overall:** DISCUSS

#### What’s solid
- Stages 1–3 match plan: config-driven steps from `/api/ui_config`; Ruth validate before PUT; Valid-only persist; Escalate ≠ Valid; Continue-on-active skips preamble; Profile resume hard-gate removed.
- File placement / naming / import-direction clean (React → API only). AST-1017 `code` commit is exactly the three planned UI files.

#### Issues
1. **discuss** — C4 stragglers: Joan excluded statutes that the three-dot tip scores in-scope because tip↔`origin/dev` have diverged (425-path XOR incl. siblings/other epics). Listed in Linear comment; all **conform** on tip; no AST-1017 product fix.

#### Notes
Joan plan-rubric APPROVED. Tip and `origin/dev` report multiple merge bases — product judgment focused on AST-1017 delta; full-set sweep still vs three-dot.
