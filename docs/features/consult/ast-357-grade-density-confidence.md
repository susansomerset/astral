<!-- linear-archive: AST-357 archived 2026-06-03 -->

## Linear archive (AST-357)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-357/grade-density-include-a-confidence-factor-in-the-grade-set  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** betty  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-358

### Description

# Confidence rating scale: define the 1–5 values, the multiplier mapping, and the conf-1 → X conversion

## Context

Every grade an agent assigns to a vector comes with a confidence rating — a 1–5 integer expressing how strongly the job description (or other source material) supports the grade. Confidence is a multiplier on grade density: a confident A counts more than an uncertain A, and at the bottom of the scale, an unconfident grade contributes nothing at all.

This ticket establishes the canonical scale, the descriptions tied to each level, and the mapping from confidence level to multiplier. It also handles a behavioral quirk: agents are reluctant to use X (the "not applicable / no signal" grade) because it reads as an admission of defeat. They'd rather guess at a grade with confidence 1 than declare X. We can use that tendency to our advantage.

## The scale

| Confidence | Description | Multiplier |
| -- | -- | -- |
| 5 | The source explicitly states it. | 1.00 |
| 4 | The source strongly suggests it. | 0.75 |
| 3 | The source hints about it. | 0.50 |
| 2 | The source makes a vague reference. | 0.25 |
| 1 | The source doesn't say it out loud, but it's possible. | 0.00 |

Linear from 1.00 to 0.00 in steps of 0.25. This is config-driven — `CONFIDENCE_MULTIPLIERS` keyed by integer 1–5, admin-tunable.

## The conf-1 → X conversion

Any grade returned with confidence 1 is converted to X before scoring. The agent's grade letter is preserved in the audit data (so we can see *what* they tried to grade), but the effective grade for scoring purposes becomes X.

The reasoning: confidence 1 means "I'm guessing." A guess multiplied by zero is zero either way, so there's no scoring difference between "C with confidence 1" and "X." But X is the more honest representation of what happened, and treating them as equivalent gives us cleaner data downstream — Auditor-style analysis can count X-rate per vector without having to also reason about "low-confidence non-X grades that effectively are Xs."

This also lets the agent off the hook diplomatically. The prompts can keep encouraging real grades over X (which we want for cases where the agent has a weak but real signal), without forcing the agent to choose between "lie a little" and "admit defeat." A confidence-1 grade is the agent saying "I'm reaching here" and we honor that by treating it as no signal at all.

## Behavioral guarantees

* Confidence is required on every grade. The agent's response schema must include it; missing confidence is a hard validation failure, not a default.
* Confidence 1 → X conversion happens at the scoring boundary, not in the agent's output. The agent still returns its original grade and confidence; scoring logic does the conversion.
* F grades retain their dealbreaker behavior regardless of confidence. A confidence-1 F is still an F. (We may want to revisit this — a "guessing F" is a high-stakes guess — but the safe v1 behavior is to honor F at any confidence level.)
* X grades, whether returned directly by the agent or converted from confidence-1, behave identically downstream: excluded from scoring, not counted in V, surfaced in Auditor data.

## What becomes config

| Config | Example | Notes |
| -- | -- | -- |
| `CONFIDENCE_MULTIPLIERS` | `{1: 0.0, 2: 0.25, 3: 0.5, 4: 0.75, 5: 1.0}` | Linear default. Admin-tunable. |
| `CONFIDENCE_DESCRIPTIONS` | `{5: "The source explicitly states it.", ...}` | Used in prompts and possibly in UI tooltips. Single source of truth so prompt language and admin language stay aligned. |

The conf-1 → X conversion is hardcoded behavior, not a config flag. We don't want to leave the door open for the agent's unsupported guesses to influence scoring; that's fabrication, not pattern matching, and it's never the right answer.

## Why this is worth doing

Confidence is currently underspecified in the system. The scale exists in the rubric design language but the mapping to scoring weight isn't formalized, and the conf-1 → X conversion isn't happening at all today, which means low-confidence guesses are polluting the scored data with grade letters that mean less than they look like. Pinning down the multipliers and the conversion gives the scoring redesign and Auditor both a clean foundation to build on.

Parsing the rating

The current decoder parses for the vector code and grade, and must also parse for the rating and pass it all back 

Scoring: Grade "density"

Consult.py calculates the score and references config to match the confidence rating to its impact percentage (or to convert 1's to X grades).  That composite of grade and confidence create a "density" to the possible score of the vector (currently determined by its position).

### Comments

#### susan — 2026-05-06T20:55:34.476Z
Review feedback resolved. Branch `chuckles/ast-357-grade-density-include-a-confidence-factor-in-the-grade-set` is ready for testing. Commit: `f8a32a20`

— Betty

#### susan — 2026-05-06T20:31:25.052Z
**Radia — addendum (spec cross-check)**

Ticket text says **“A confidence-1 F is still an F.”** In **`_render_score`**, **`_effective_no_signal_for_score`** returns true for **`confidence == 1`** before considering the letter, so an **F1** row is **skipped** like other conf-1 rows rather than forcing **`fail_state`** the way **F2+** does. Binary **`_render_pass_fail`** can still fail the job when **no** row has **confidence > 1**, but the scored path may behave differently than the literal “F is always a dealbreaker” reading.

Worth confirming with Susan whether **F1** should **`return (fail_state, None)`** in **`_render_score`** (and/or be excluded from the “no confidence > 1” soft-fail path) so consult scoring can’t “pass” with a lingering **F1** hidden from the numerator.

— Radia

#### susan — 2026-05-06T20:31:09.278Z
**Code review (Radia)** — local feature ref **`chuckles/ast-357-grade-density-include-a-confidence-factor-in-the-grade-set`** missing (`git rev-parse` failed). Reviewed **local `dev`** range **`cf19f590^..720c20ae`** (`feat(ast-357): confidence…` through `chore(ast-357): add code review findings`).

**Counts:** fix-now **0** · discuss **1** · advisory **0**

**What’s solid:** **`CONFIDENCE_MULTIPLIERS`** wired into **`_render_score`**; **`_render_pass_fail`** implements **F2+** dealbreaker, literal **X** fail, and **no row with confidence > 1** fails; **`_effective_no_signal_for_score`** treats **X**, **conf 1**, and **F1** as no-signal for scoring — aligns with ticket + **§2.3.2** intent. **`ValueError`** on non-int confidence in `_render_score` matches “missing confidence is hard failure” direction.

**Discuss:** UI/CSS + `AgentAnalysisHeader` changes should be checked in browser for regressions on **JobsRecommended** / story tabs (not exercised here).

Doc added: `docs/features/consult/ast-357-grade-density-confidence.md` per diff — not edited in-repo from this pass.

— Radia

#### susan — 2026-05-06T20:16:55.851Z
**Radia — review blocked (no branch to diff)**

Linear lists `gitBranchName` `chuckles/ast-357-grade-density-include-a-confidence-factor-in-the-grade-set`, but that ref is **not** on `origin` here, so no checkout / diff was possible.

**State:** left **Code Complete**.

— Radia

---

# AST-357 — Grade density: include a confidence factor in the grade set

**Linear:** AST-357  
**Title:** Grade Density: Include a confidence factor in the grade set  
**Project:** Astral Consult (`docs/features/consult/`)

---

## Issue (Linear, summarized)

- Define canonical confidence scale `1-5`, descriptions, and admin-tunable `CONFIDENCE_MULTIPLIERS`.
- Confidence multiplies grade density; confidence `1` multiplier is `0.00`.
- **Scoring boundary behavior:** any non-`F` grade with confidence `1` is treated as effective `X` for scoring (original grade preserved in stored grades).
- **`F1` behavior:** treat as effective `X` at scoring boundary; **`F2-F5`** remain dealbreakers.
- **`X` encoding:** allow `X` with confidence `0` in encoded payloads; non-`X` grades require confidence `1-5`.
- Confidence is **required** on every grade; missing confidence is a hard validation failure (no defaults).
- UI: compact **5-bullet** confidence row centered under each grade icon; active bullets use **enabled nav/menu text color**, inactive use **disabled menu text color**, via **explicit CSS variables** mapped to existing theme tokens (tunable without changing global palette). For `X` (typically `confidence=0`), show **all inactive bullets** to preserve vertical alignment.

---

## Locked product decisions (this ticket)

1. **Binary pass/fail (`_render_pass_fail`)** must fail when any of these hold:
   - any **real** failing grade: **`F` with confidence `2-5`**
   - **all vectors are no-signal** using *effective* semantics: all grades are literal `X`, **or** every vector is confidence-`1` (including `F1` and non-`F` `*1`), i.e. **no confidence ratings `> 1`**
   - (still) literal all-`X` remains a fail (redundant with the “no confidence `> 1`” rule in the common case, but keep the explicit branch if it simplifies code readability)

2. **No backwards compatibility:** older responses without confidence should fail validation and route through the normal retry/error paths. **Do not** recalculate historical scores.

3. **Encoded persistence rule:** compact encoded strings are **in-flight only**. The database should store **decoded JSON** on success; raw encoded text should only appear when parse/decode fails (debugging). **No encoded-data migration work** for AST-357.

4. **Copy/source-of-truth:** confidence canonical text will live in `src/utils/config.py` as `CONFIDENCE_DESCRIPTIONS` + multipliers, and also in `ASTRAL_CONFIG["output_types"]` prompt strings. Rubric artifacts do **not** own confidence instructions. Accept the small duplication between constants and `output_types` (low churn).

5. **Testing:** skip automated test expansion in this ticket; Susan will validate manually. Still run compile/lint on touched files before commit (repo rule).

6. **Observability:** add richer **debug** logging around decode/validate/score decisions (segment-level reasons, confidence bounds, pass/fail triggers), without spamming non-debug paths.

---

## Plan

### Step 0 — Documentation home (first)

- **Add** this file: [`/Users/susan/chuckles/astral/docs/features/consult/ast-357-grade-density-confidence.md`](/Users/susan/chuckles/astral/docs/features/consult/ast-357-grade-density-confidence.md)
- **Remove** any duplicate Cursor-local plan copy for AST-357 (if one existed) so this repo doc is the single plan source.

### Step 1 — Config: canonical confidence + prompts

- **Modify** [`/Users/susan/chuckles/astral/src/utils/config.py`](/Users/susan/chuckles/astral/src/utils/config.py)
  - Add `CONFIDENCE_MULTIPLIERS` and `CONFIDENCE_DESCRIPTIONS` (defaults per AST-357).
  - Align `ASTRAL_CONFIG["output_types"]` text with the canonical descriptions (accept duplication; no token-in-token templating).
  - Fix `grades_encoded_meta` format documentation so it matches the encoded grammar (includes `{conf}` consistently).

### Step 2 — Schemas: require confidence everywhere grades exist

- **Modify** [`/Users/susan/chuckles/astral/src/utils/config.py`](/Users/susan/chuckles/astral/src/utils/config.py)
  - Add required `confidence` (`type: int`) to `grades.items_schema` for graded JSON tasks (`prefilter_company`, `grade_do`, `grade_get`, `grade_like`, and any other graded task schemas in this file).
  - Add required `confidence` on decoded `grades` items for encoded-decoded tasks (`qualify_job_listings`, `evaluate_jd`).

### Step 3 — Decode + validate (agent layer)

- **Modify** [`/Users/susan/chuckles/astral/src/core/agent.py`](/Users/susan/chuckles/astral/src/core/agent.py)
  - Update `_decode_payload` grade segment parsing to `{code}{grade}{conf}` with strict validation:
    - non-`X`: `conf in 1..5`
    - `X`: `conf == 0`
  - Extend `_validate_grades` (or adjacent validation) to require confidence for graded tasks and enforce bounds (including `X0`).

### Step 4 — Scoring + binary consult rules

- **Modify** [`/Users/susan/chuckles/astral/src/core/consult.py`](/Users/susan/chuckles/astral/src/core/consult.py)
  - Update `_render_pass_fail` to implement the locked fail rules (F2+, all-X / no-confidence->1 semantics).
  - Update `_render_score` to apply confidence multipliers from config and apply effective-`X` rules at scoring boundary (`*1`, `F1`), while preserving stored grades.

### Step 5 — UI: bullets + typings

- **Modify** [`/Users/susan/chuckles/astral/src/ui/frontend/src/components/AgentAnalysisHeader.tsx`](/Users/susan/chuckles/astral/src/ui/frontend/src/components/AgentAnalysisHeader.tsx)
- **Modify** [`/Users/susan/chuckles/astral/src/ui/frontend/src/App.css`](/Users/susan/chuckles/astral/src/ui/frontend/src/App.css)
- **Modify** TS types where job grade arrays are declared, minimally:
  - [`/Users/susan/chuckles/astral/src/ui/frontend/src/components/AgentStoryTab.tsx`](/Users/susan/chuckles/astral/src/ui/frontend/src/components/AgentStoryTab.tsx) (`vector_grades` items)
  - [`/Users/susan/chuckles/astral/src/ui/frontend/src/pages/JobsRecommended.tsx`](/Users/susan/chuckles/astral/src/ui/frontend/src/pages/JobsRecommended.tsx) (`like_grades` items)

### Step 6 — Manual verification (Susan)

- Validate new agent outputs decode + validate, UI bullets render, and pass/fail + scored paths match the locked rules.

---

## API typing note (recommended touchpoints)

Jobs list/detail already flatten grade arrays from `job_data` to top-level keys via [`/Users/susan/chuckles/astral/src/ui/api/api_jobs.py`](/Users/susan/chuckles/astral/src/ui/api/api_jobs.py) (`GET /api/jobs`, `GET /api/jobs/<id>`). No schema change is strictly required server-side (JSON is untyped), but **TypeScript** should treat these arrays as including optional/required `confidence` depending on how strict you want the UI:

- `GET /api/jobs?view=in_review|skipped|recommended` (flattened `*_grades` keys)
- `GET /api/jobs/<astral_job_id>` (same flattening + `agent_story` entries containing `vector_grades`)

`agent_story` shaping happens in core (`get_entity_agent_story`) and is consumed by the UI through the job detail endpoint above.

---

## Files changed (expected)

| File | Action |
|------|--------|
| [`docs/features/consult/ast-357-grade-density-confidence.md`](/Users/susan/chuckles/astral/docs/features/consult/ast-357-grade-density-confidence.md) | **Add** (this doc) |
| [`src/utils/config.py`](/Users/susan/chuckles/astral/src/utils/config.py) | **Modify** |
| [`src/core/agent.py`](/Users/susan/chuckles/astral/src/core/agent.py) | **Modify** |
| [`src/core/consult.py`](/Users/susan/chuckles/astral/src/core/consult.py) | **Modify** |
| [`src/ui/frontend/src/components/AgentAnalysisHeader.tsx`](/Users/susan/chuckles/astral/src/ui/frontend/src/components/AgentAnalysisHeader.tsx) | **Modify** |
| [`src/ui/frontend/src/App.css`](/Users/susan/chuckles/astral/src/ui/frontend/src/App.css) | **Modify** |
| [`src/ui/frontend/src/components/AgentStoryTab.tsx`](/Users/susan/chuckles/astral/src/ui/frontend/src/components/AgentStoryTab.tsx) | **Modify** (types) |
| [`src/ui/frontend/src/pages/JobsRecommended.tsx`](/Users/susan/chuckles/astral/src/ui/frontend/src/pages/JobsRecommended.tsx) | **Modify** (types) |
| [`scripts/migrate_encoded_agent_data.py`](/Users/susan/chuckles/astral/scripts/migrate_encoded_agent_data.py) | **Modify** (4-char segment parser aligned with `agent._decode_payload`) |
| [`docs/ASTRAL_CODE_RULES.md`](/Users/susan/chuckles/astral/docs/ASTRAL_CODE_RULES.md) | **Modify** (§2.3 / §2.3.2 confidence semantics) |

---

## Self-review vs `docs/ASTRAL_CODE_RULES.md` (intent)

- **§2.1 Config as source of truth:** multipliers + descriptions live in `config.py`; core reads them, does not hardcode scales.
- **§3.3 Layering:** parsing/validation/scoring in core; UI renders; API remains thin.
- **§2.3 re-validation note:** ticket explicitly requires hard confidence validation despite the general “Anthropic validates schema” pattern — this is intentional defense-in-depth for graded payloads.

---

## Review

**Commit:** `cf19f590e5b7ce62dc3eec4495508efe47cebe0f`  
**Branch:** `dev`  
**Reviewed:** 2026-04-27

---

## What's Solid

- **Plan coverage:** `CONFIDENCE_MULTIPLIERS` / `CONFIDENCE_DESCRIPTIONS` in `config.py`, required `confidence` on graded `TASK_CONFIG` schemas (including encoded decode shapes for `qualify_job_listings` / `evaluate_jd`), `ASTRAL_CODE_RULES` §2.3.2, and the feature doc match the locked product rules.
- **Encode path:** `_GRADE_SEG` and `_decode_payload` enforce 4-char segments (`{code}{letter}{digit}`), including `X` + `0` and non-`X` + `1–5`, with DEBUG-only decode tracing.
- **Defense in depth in `do_task`:** Confidence is validated on the inner task payload after JSON schema pass and again after encoded decode, so missing or out-of-range confidence fails before storage/consult, consistent with “no backwards compatibility.”
- **Vector validation:** `_validate_grades` still enforces vector sets and allowed letters, then chains `_validate_grade_confidence_list` so encoded jobs cannot skip confidence checks.
- **Consult semantics:** `_render_pass_fail` implements F2+ dealbreaker, literal all-`X` fail, and “no confidence `> 1`” fail; `_render_score` applies multipliers, skips no-signal rows (`X`, `*1`, `F1`) for numerator/denominator, and fails fast on F2+.
- **UI:** `AgentAnalysisHeader` renders five bullets with explicit CSS variables in `App.css`; `confidence` is optional on `Grade` for legacy display (all dim bullets).
- **Tooling alignment:** `scripts/migrate_encoded_agent_data.py` segment regex and decode match the agent layer, reducing drift when reprocessing old encoded payloads.

---

## Issues

### Issue 1 — Strict `int` for `confidence` in Python validators ⚠️ Discuss

`_validate_grade_confidence_list` requires `isinstance(conf, int)`. JSON from the API is usually deserialized to `int` for whole numbers, but if any path yields `3.0` (`float`), validation fails even though the value is semantically valid.

**Recommendation:** If you see spurious failures in logs, accept `int` or whole-number `float` (e.g. `float` with `g == int(g)`) or normalize once at parse boundary.

---

### Issue 2 — Stdlib `logging` imported beside `get_logger` ℹ️ advisory

`agent.py` and `consult.py` use `import logging` primarily for `logger.isEnabledFor(logging.DEBUG)`. `ASTRAL_CODE_RULES` §1.5 points at `src/utils/logging.py` as the logging home.

**Recommendation:** Low priority: route DEBUG gating through the project logger helper/constants if you want zero stdlib `logging` imports in core, or document this as an intentional exception for level checks.

---

### Issue 3 — Bullet “active” color tokens vs ticket wording ℹ️ advisory

The ticket asked for active/inactive bullets to track **enabled / disabled nav or menu text** colors. The implementation uses `--confidence-bullet-active: var(--text-secondary)` and `--confidence-bullet-inactive: var(--text-muted)`, which is clean and theme-driven but may not be identical to nav/menu tokens depending on your palette.

**Recommendation:** Quick visual pass in light/dark (or map the variables to the same tokens nav uses if they differ today).

---

## Recommended Actions

| # | Severity | Action |
|---|----------|--------|
| 1 | Discuss | Only if production shows failures: relax or normalize `confidence` type at validation boundary. |
| 2 | Advisory | Optional style pass: reduce duplicate `logging` imports in core or document the pattern. |
| 3 | Advisory | Confirm bullet contrast matches nav/menu intent; retarget CSS variables if needed. |

---

## Resolution

**Date:** 2026-05-06 — Betty (`f-resolve-linear`)

- **Radia (2026-05-06):** fix-now **0**; discuss **1** (browser / **JobsRecommended** + story tabs for **AgentAnalysisHeader** + CSS); advisory **0**.
- **Addendum (`F1` vs “F at any confidence” in original ticket prose):** **No code change.** This doc’s **## Issue** and **## Locked product decisions** already specify **`F1` → no-signal** for scored math and **`F2–F5`** as binary dealbreakers in `_render_pass_fail`, with “no row has confidence `> 1`” as the soft-fail path — matches `src/core/consult.py` (**`_effective_no_signal_for_score`**, **`_render_score`**, **`_render_pass_fail`**).
- **Discuss (UI):** Manual pass under **Testing** (light/dark) per Radia; optional follow-up if nav/menu token parity is desired for bullet colors (advisory #3 above).
- **Build:** `python3 -m compileall -q src` before this doc commit (no Python edits in resolve pass).

— Betty
