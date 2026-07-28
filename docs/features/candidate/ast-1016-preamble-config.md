# AST-1016 — PREAMBLE_CONFIG preamble script

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1016/preamble-config-preamble-script-candidate-profile-preamble-to-intake  
**Parent:** https://linear.app/astralcareermatch/issue/AST-952/candidate-profile-preamble-to-intake  

**Publish ref (origin):** `sub/AST-952/AST-1016-preamble-config`  
**Parent integration ref:** `ftr/AST-952-candidate-profile-preamble-to-intake`

Ship **`PREAMBLE_CONFIG`** as the product-config source of truth for the mechanical intake preamble: ordered steps, each step’s target library field (`context.raw_*`), Archie-owned **Intro** / **1st Try** / **2nd Try** copy (placeholders until she supplies finals), and the Ruth validation task_key string consumers must call. Sibling **AST-1017** renders Intro and drives the step UI; sibling **AST-1015** owns the Ruth agent_task implementation.

Boundaries (do **not** implement): library persistence / remaps (AST-1014 — already on ftr), Ruth Valid/Try Again/Escalate agent_task body (AST-1015), mechanical intake front-door UI / Estelle chat chrome (AST-1017), Estelle confirm (AST-953), candidate state-machine vocabulary changes.

⚠️ **Decision — Parent AC3 “Intro appears…”:** This child owns the **Intro string** (and step copy) in config and makes the block readable to the UI via `/api/system/ui_config`. **Rendering** Intro at new-intake start in Estelle-consistent presentation is **AST-1017**. Do not edit `CandidateIntake.tsx` here.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `PREAMBLE_CONFIG` after `CANDIDATE_LIBRARY_CONFIG` (intro, steps, validation_task_key); assert step targets ⊆ library vocabulary | utils |
| `src/ui/api/api_system.py` | Include a JSON-safe `preamble` object on `GET /api/system/ui_config` from `PREAMBLE_CONFIG` | ui |

No frontend page changes, no `TASK_CONFIG` / agent_task rows, no database migration, no `tests/` edits (Betty owns tests after Code Complete).

---

## Stage 1: `PREAMBLE_CONFIG` contract

**Done when:** `PREAMBLE_CONFIG` is importable from `src.utils.config` with Intro + three ordered mechanical steps targeting `context.raw_resume` / `context.raw_profile` / `context.raw_sample`, 1st/2nd Try strings (Archie placeholders), and a `validation_task_key` literal; module-level asserts fail loudly if a step target is outside `CANDIDATE_LIBRARY_CONFIG`.

1. In `src/utils/config.py`, immediately **after** `CANDIDATE_LIBRARY_CONFIG` (before `assert "PROSPECT" not in CANDIDATE_STATES`), add:

```python
# AST-1016: mechanical preamble script (Intro + steps). UI = AST-1017; Ruth task = AST-1015.
PREAMBLE_CONFIG = {
    "intro": (
        "[PLACEHOLDER — Archie] Before we start with Estelle, we'll collect three "
        "source materials: your latest resume, your LinkedIn profile, and a sample "
        "cover letter from a past application."
    ),
    # AST-1015 must register an agent_task with this exact task_key (Ruth / Little Brain).
    "validation_task_key": "preamble_validate_response",
    "steps": [
        {
            "id": "raw_resume",
            "order": 1,
            "prompt_1st_try": (
                "[PLACEHOLDER — Archie] Let's start with your existing/latest resume. "
                "Paste the full text (or upload content) so we can store it as your raw resume."
            ),
            "prompt_2nd_try": (
                "[PLACEHOLDER — Archie] That didn't look like resume text. Please paste "
                "your full resume again — include roles, dates, and education if you have them."
            ),
            "target": {"blob": "context", "field": "raw_resume"},
            "validation_question": (
                "Does this response look like a valid answer to: paste your resume text?"
            ),
        },
        {
            "id": "raw_profile",
            "order": 2,
            "prompt_1st_try": (
                "[PLACEHOLDER — Archie] Next, paste your LinkedIn profile content "
                "(About, Experience, Education — the text you'd want Estelle to read)."
            ),
            "prompt_2nd_try": (
                "[PLACEHOLDER — Archie] That didn't look like a LinkedIn profile. "
                "Paste the profile text again (not just the profile URL)."
            ),
            "target": {"blob": "context", "field": "raw_profile"},
            "validation_question": (
                "Does this response look like a valid answer to: paste your LinkedIn profile text?"
            ),
        },
        {
            "id": "raw_sample",
            "order": 3,
            "prompt_1st_try": (
                "[PLACEHOLDER — Archie] Finally, paste a sample cover letter from a past "
                "application so we can learn your writing style."
            ),
            "prompt_2nd_try": (
                "[PLACEHOLDER — Archie] That didn't look like a cover letter. "
                "Paste a full sample cover letter (greeting through sign-off) again."
            ),
            "target": {"blob": "context", "field": "raw_sample"},
            "validation_question": (
                "Does this response look like a valid answer to: paste a sample cover letter?"
            ),
        },
    ],
}
```

2. Still in `config.py`, add asserts immediately after the block (same style as neighboring candidate asserts):

   - `PREAMBLE_CONFIG["validation_task_key"]` is a non-empty `str`.
   - `PREAMBLE_CONFIG["intro"]` is a non-empty `str`.
   - `steps` is a non-empty `list`; each step has keys `id`, `order`, `prompt_1st_try`, `prompt_2nd_try`, `target`, `validation_question` (all required strings / dict as above).
   - Step `order` values are unique and equal to `1..len(steps)` when sorted.
   - For each step: `target["blob"] == "context"` and `target["field"]` is in `CANDIDATE_LIBRARY_CONFIG["context_keys"]`.
   - Step `id` equals `target["field"]` (stable id for UI progress keys).

⚠️ **Decision:** Minimum mechanical sequence is exactly the three parent-brief sources (resume → LinkedIn → sample). Do **not** add contact/name/pronoun steps here — those are Profile/Admin + library columns (AST-1014), not this preamble script. Do **not** add hopes/interests/concerns steps — Topic Menu / Estelle (AST-953).

⚠️ **Decision:** `validation_task_key` is `"preamble_validate_response"`. AST-1015 must create the Ruth agent_task under that exact key (or stop and comment on the parent if they need a different key — then update this constant in a follow-up on this ticket). Do not invent the agent_task row in this ticket.

⚠️ **Decision:** Archie copy is placeholder-tagged with `[PLACEHOLDER — Archie]` so final wording is a string swap only — no step/id/target changes when finals arrive.

3. If `config.py`’s top-of-file comment inventory lists named `*_CONFIG` blocks, add a one-line entry for `PREAMBLE_CONFIG` next to `CANDIDATE_LIBRARY_CONFIG` / `INTAKE_CONFIG`.

---

## Stage 2: Serve preamble to UI consumers

**Done when:** Authenticated `GET /api/system/ui_config` JSON includes a `preamble` key whose value mirrors `PREAMBLE_CONFIG` (intro, validation_task_key, steps); no other ui_config keys change; `CandidateIntake.tsx` and other frontend pages are untouched.

1. In `src/ui/api/api_system.py`, import `PREAMBLE_CONFIG` from `src.utils.config` (same import site as `UI_CONFIG` / `BUILD_CONFIG`).

2. In `ui_config()`, add `"preamble": PREAMBLE_CONFIG` to the jsonify dict alongside the existing `**UI_CONFIG` / `base_resume_accent_palette` keys.

⚠️ **Decision:** Serve under `/api/system/ui_config` rather than a new blueprint route — AST-1017 already (or will) load ui_config for shared UI literals; one fetch gives Intro + steps. Do not add a dedicated `/api/preamble` endpoint.

3. Do **not** change `INTAKE_CONFIG`, session create/archive flows, or Estelle agent wiring in this ticket.

---

## Out of scope (explicit)

- Rendering Intro / step prompts in the intake page (AST-1017).
- Calling Ruth / interpreting Valid|Try Again|Escalate (AST-1015 + AST-1017).
- Writing `context.raw_*` via PUT (already library/API from AST-1014; UI persist path is AST-1017).
- Replacing placeholder Archie strings with finals unless Archie comments them on this ticket during build — if she does, Stage 1 strings only (same keys).

---

## Self-Assessment

**Scope:** `Single-Component` — one config block in `config.py` plus a one-key expose on existing `ui_config`; no core library, validation, or intake UI work.

**Conf:** `high` — mirrors `CANDIDATE_LIBRARY_CONFIG` / `INTAKE_CONFIG` patterns; targets are already-shipped AST-1014 context keys; placeholders are explicit.

**Risk:** `Medium` — wrong `target` or `validation_task_key` would make AST-1017 write/validate against the wrong homes; asserts + sibling contracts mitigate; Intro presentation AC half depends on AST-1017 consuming this block.

## Review

**Publish ref:** `sub/AST-952/AST-1016-preamble-config`  
**Build tip:** `927658d1bf3dfec1e097308ddcd15b27342f6c05`

### Radia — code-rubric.v1 (`[code-rubric] revision=1`)

**Tip reviewed:** `2c0cb3f2cdc18f728b6db9767c709496474def2c` (`origin/sub/AST-952/AST-1016-preamble-config` vs `origin/dev`)
**Overall:** DISCUSS

#### What’s solid
- `PREAMBLE_CONFIG` matches plan Stage 1 (intro, three `context.raw_*` steps, `preamble_validate_response`, asserts vs `CANDIDATE_LIBRARY_CONFIG`).
- Stage 2: `GET /api/ui_config` exposes `preamble` with `@require_auth` retained; no intake UI / Ruth / library churn in the AST-1016 `code` commit.
- Ancestor AST-1014 fix-nows already resolved on this tip (`api_admin` token view, PUT `debug=ui_llm_debug()`, agent lazy-import comment).

#### Issues
1. **discuss** — C4 stragglers: Joan excluded 16 statutes at plan time that the three-dot tip scores in-scope because the tip also carries resolved AST-1014 (+ Betty tests). Not product defects on the AST-1016 delta; statutes themselves **conform**.

#### Advisory
- Plan prose says `/api/system/ui_config`; live route is `/api/ui_config` (system blueprint) — implementation correctly extends the existing surface.

#### Notes
Joan plan-rubric verdict attached (APPROVED). No fix-now on AST-1016 deliverable.
