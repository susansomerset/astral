<!-- linear-archive: AST-309 archived 2026-06-03 -->

## Linear archive (AST-309)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-309/cover-letter-artifact-shape-json-object  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** susan  
**Priority / estimate:** High / 2  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Define cover_letter as a JSON object in BUILD_CONFIG.artifact_shapes (not flat text). Shape: { re_line: string, body: string, signature: string }. re_line: agent-generated subject line (e.g. 'Re: Senior PM — Acme Corp'). body: full cover letter prose. signature: pre-populated from {$COVER_LETTER_SIGNATURE} token at build time — agent does not write it. candidate can override per-job in the Job Analysis Report Cover Letter panel. craft_job_cover_letter response_schema updated to match. [builder.py](<http://builder.py>) renders all three fields; signature block includes both text (cover_letter.signature) and image (candidate_data.profile.cover_letter_signature_image) with graceful fallback if image absent.

### Comments

#### chuckles — 2026-05-18T20:48:12.481Z
## Landed on origin/dev — Chuckles

- No `ftr/AST-309` branch on origin; product already on `origin/dev` from earlier prep-uat (`1befbd0a`)
- **AST-309** PR Ready → **Done** (no additional push required for this ticket)

`origin/dev` tip after AST-312 push: `ceec63c7`

— Chuckles

#### chuckles — 2026-05-18T19:17:54.833Z
## Landed on origin/dev — Chuckles

- Merged `origin/ftr/AST-309-cover-letter-artifact-shape-json-object` (prep-uat + finish-up) → pushed `origin/dev`
- Deleted `origin/ftr/AST-309-cover-letter-artifact-shape-json-object`
- Standalone — no children

Push tip: `1befbd0a`

— Chuckles

#### chuckles — 2026-05-18T19:11:08.664Z
## UAT Ready — Chuckles

**AST-309** is a **standalone** ticket (no child branches). prep-uat = merge feature branch into local `dev` only.

**Feature branch:** `origin/ftr/AST-309-cover-letter-artifact-shape-json-object` (5 commits ahead of prior `origin/dev` tip for this feature)

**Merged into local `dev`:** prep-uat §8. No `sub/*` branches to delete.

Restart the app if it is running, then test cover_letter JSON shape (`re_line`, `body`, `signature`) in BUILD_CONFIG / tracker / job API paths.

If testing fails on `dev`:
```
git reset --hard origin/dev
```

— Chuckles

#### hedy — 2026-05-16T23:07:43.834Z
Review feedback resolved. Branch `ftr/AST-309` ready for **prep-uat**. Commit: `171c9414` — Hedy (parent **AST-301**)

#### hedy — 2026-05-16T22:49:56.043Z
Review feedback resolved. Branch `ftr/AST-309` ready for UAT merge. Commit: `171c9414` — Hedy

**discuss:** `artifact_shapes.cover_letter.signature` → `required: False` (matches task schema). **AST-369** owns `craft_job_cover_letter` → save wire.

#### radia — 2026-05-16T22:42:54.891Z
## review-astral (Radia)

**Diff:** `origin/dev...origin/ftr/AST-309`

**Summary:** Cover-letter schema + tracker normalizer look right. **0 fix-now** · **2 discuss**

- **discuss:** `artifact_shapes.cover_letter.signature` still `required: True` while task schema marks signature optional — align.
- **discuss:** No `craft_job_cover_letter` → job artifact save wire yet — confirm **AST-369** owns persistence.

**Doc commit:** `7d739f31` on `origin/ftr/AST-309`

— Radia

#### hedy — 2026-05-16T22:38:27.210Z
**test-astral** — Hedy

**Integration:** `dev-hedy` after merges through `origin/ftr/AST-309` (Betty ref **`origin/ftr/AST-309`** @ **`b6d8ccf5`**).

**Command:**
`python3 -m pytest tests/component/utils/test_config.py::TestAst309CoverLetterTaskConfig tests/component/core/test_tracker.py::TestAst309CoverLetterArtifact tests/component/core/test_builder.py -k "cover_letter or CoverLetter or _cover_letter_nonempty" -q` → **6 passed**

**Result:** **PASS** — no product fixes; no new commits.

— Hedy

#### betty — 2026-05-16T21:55:34.133Z
**[qa-astral] publish fix** — Betty tests on **`origin/ftr/AST-309`** @ **`b6d8ccf5`** (cherry-pick `50fdb1bb`).

— Betty

#### betty — 2026-05-16T21:54:52.358Z
**[qa-astral] branch correction** — published to **`origin/ftr/AST-309`** @ `f761a250`. Ignore `hedy/ast-309-…` in the earlier manifest.

**Manifest** (run on **`origin/ftr/AST-309`**):
1. `tests/component/utils/test_config.py::TestAst309CoverLetterTaskConfig`
2. `tests/component/core/test_tracker.py::TestAst309CoverLetterArtifact`
3. `tests/component/core/test_builder.py` — cover letter artifact / `_cover_letter_nonempty` tests

— Betty

#### betty — 2026-05-16T21:43:47.690Z
QA manifest by Betty.

**Integration:** `origin/hedy/ast-309-cover_letter-artifact-shape-json-object` @ `f761a250`.

**Manifest (run in order):**
1. `tests/component/utils/test_config.py::TestAst309CoverLetterTaskConfig`
2. `tests/component/core/test_tracker.py::TestAst309CoverLetterArtifact`
3. `tests/component/core/test_builder.py` — cover letter artifact / `_cover_letter_nonempty` tests (bible-backed)

**Test commit:** `50fdb1bb` on `dev-betty` (cherry-picked `f761a250`)

— Betty

#### hedy — 2026-05-16T21:36:29.853Z
Built by Hedy.

**Branch:** `hedy/ast-309-cover_letter-artifact-shape-json-object`
**Commit:** `cfa13d16` (`dev-hedy`, pushed to `origin/hedy/ast-309-cover_letter-artifact-shape-json-object`)
**Label review:** agree on all three

#### chuckles — 2026-05-16T21:29:53.930Z
## Plan Review — Chuckles

**Verdict: APPROVED**

Plan is faithful to the definition. No findings. ASTRAL_CODE_RULES compliance confirmed. Self-assessment is honest.

**Note:** Implementation already on `origin/dev` ([retroactive-pipeline] C2).

— Chuckles

#### susan — 2026-05-05T17:31:21.355Z
[check-linear]

Thread reviewed for Hedy queue pass.

- Latest activity is the new plan-ready handoff comment for this ticket.
- No additional request, question, or blocker requiring code/docs changes beyond the posted plan.

Action: no-op.

— Hedy (check-linear)

#### susan — 2026-05-04T21:35:06.016Z
**Plan ready (a-plan-linear / Hedy)**

- **Doc:** `docs/features/artifacts/ast-309-cover_letter-artifact-shape-json-object.md` on `chuckles/ast-309-cover_letter-artifact-shape-json-object`.
- **Commit:** `d4ddc326`
- **Self-assessment:** Scope **Single-Component**; Conf **Medium** (merge with AST-310/369); Risk **Medium**.
- **Link:** https://github.com/susansomerset/astral/blob/chuckles/ast-309-cover_letter-artifact-shape-json-object/docs/features/artifacts/ast-309-cover_letter-artifact-shape-json-object.md

— Hedy

---

# AST-309 — cover_letter Artifact Shape — JSON Object

**Linear:** [AST-309](https://linear.app/astralcareermatch/issue/AST-309/cover-letter-artifact-shape-json-object)  
**Feature branch:** `<agent>/ast-309-cover_letter-artifact-shape-json-object`

## Summary

Lock **`job_data.artifacts.cover_letter`** to the object **`{ re_line, body, signature }`** (all strings) as already declared under **`BUILD_CONFIG["artifact_shapes"]["cover_letter"]`** on `dev`. Extend **`TASK_CONFIG["craft_job_cover_letter"]`** with a **`response_schema`** that matches that object plus any existing metadata keys the pipeline persists today (e.g. `astral_job_id`, `company`, `title` if still required). Ensure **`craft_job_cover_letter`** prompts tell the model **not** to populate `signature` (injected at build via **`{$COVER_LETTER_SIGNATURE}`** per **AST-310**). Align **`builder._resolve_cover_letter`** / **`_emit_cover_sections_html`** with any schema tightening (no silent dropping of valid dicts). Add **DATA_SHAPES** (or job artifact editor config) entries for the Job Analysis Report Cover Letter panel if missing, so per-job overrides edit the three fields explicitly.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `TASK_CONFIG["craft_job_cover_letter"]` — full `response_schema` for `re_line`, `body`, `signature`; prompt text adjustments; verify `artifact_shapes["cover_letter"]` matches. | utils |
| `src/core/builder.py` | Only if contract drift: keep `_cover_letter_nonempty` / emit paths consistent with required vs optional fields per plan decision below. | core |
| `src/utils/config.py` `DATA_SHAPES` | Job-side cover letter panel field keys for `job_data.artifacts.cover_letter` (if the JAR UI is driven from DATA_SHAPES — locate the exact block on `dev` before editing). | utils |

## Stage 1: Schema audit and TASK_CONFIG

**Done when:** `craft_job_cover_letter` Anthropic JSON output validates to the three-string object; empty `signature` in model output is allowed if the merge step fills from token at artifact-save time (document which layer merges — if none exists yet, **stop** with Linear 🛑 and cite **AST-369**).

1. Read current `BUILD_CONFIG["artifact_shapes"]["cover_letter"]` and `TASK_CONFIG["craft_job_cover_letter"]` on the branch tip.
2. Replace stub `response_schema` with explicit keys `re_line`, `body`, `signature` (`type: str`, `required` flags per product: typically `re_line`/`body` required from model, `signature` optional if filled server-side).
3. Add prompt instruction block: model returns JSON only; **do not** invent closing sign-off text in `signature` — leave empty or omit if schema allows.

## Stage 2: Persistence / merge hook (if on `dev` today)

**Done when:** When `craft_job_cover_letter` response is saved into `job_data.artifacts`, the stored dict always has string values for the three keys (empty string allowed).

1. Locate the code path that writes LIKE / cover letter results into the job row (search for `craft_job_cover_letter` or `cover_letter` in `src/core` / `src/data`).
2. If no single merge function exists, add a small normalizer helper in the same module that already saves job artifacts (do **not** create a parallel save path).

## Stage 3: Builder + UI alignment

**Done when:** Builder still renders three sections when any field non-empty; JAR UI sends/receives object shape.

1. In `builder.py`, confirm `_resolve_cover_letter` treats `signature` as optional for “has content” if `re_line`/`body` carry the letter (adjust `_cover_letter_nonempty` only if Stage 1 made `signature` server-owned always-empty from model).
2. Update DATA_SHAPES / frontend-facing job artifact definitions per the panel Susan referenced in the issue — follow existing key naming for `job_data` in the codebase.

## Self-Assessment

**Scope — `Single-Component`**  
Config + one save path + tight builder touch + optional DATA_SHAPES.

**Conf — `Medium`**  
Merge point for model output vs token-injected signature may live in **AST-369**; escalate if unclear.

**Risk — `Medium`**  
Schema drift breaks print HTML and job editor.

## Self-review vs ASTRAL_CODE_RULES

§2.1 — all shapes in `config.py`. §1.3 — reuse existing job artifact save patterns.

---

## Review stub (build)

Built by Hedy.

- **Branch:** `hedy/ast-309-cover_letter-artifact-shape-json-object`
- **Integration:** `dev-hedy`

**Note:** Full artifact save path from `craft_job_cover_letter` remains **AST-369**; this pass adds `response_schema`, prompt guard, and `normalize_cover_letter_artifact` / `save_job_artifact_cover_letter` in `tracker.py`.

---

## Radia review (review-astral 2026-05-16)

**Diff:** `origin/dev...origin/ftr/AST-309`

### What's solid

- `TASK_CONFIG.craft_job_cover_letter` gains `re_line` / `body` / `signature` `response_schema` and `nocache_prompt` telling the model to leave `signature` empty (server injects `{$COVER_LETTER_SIGNATURE}`).
- `normalize_cover_letter_artifact` + `save_job_artifact_cover_letter` coerce the three-string object at the tracker merge boundary (§1.3 DRY with `save_job_data`).
- Includes AST-302 state-machine companions on this branch (expected stack with 302/311).

### Issues

| Severity | Item |
|----------|------|
| **discuss** | `BUILD_CONFIG.artifact_shapes.cover_letter.signature` remains `required: True` while `TASK_CONFIG` marks `signature` optional — align shape vs runtime contract (empty string vs missing key). |
| **discuss** | No `craft_job_cover_letter` → `save_job_artifact_cover_letter` wire in core dispatch yet — acceptable if **AST-369** owns persistence; confirm plan handoff. |

### Recommended actions

| Action | Owner |
|--------|-------|
| Align `artifact_shapes` vs `response_schema` required flags | Hedy |
| Confirm AST-369 owns agent-output → job artifact save | Susan / Hedy |

**Counts:** 0 fix-now · 2 discuss · 0 advisory

— Radia

---

## Resolution (resolve-astral)

2026-05-16 — Radia **review-astral** (`origin/dev...origin/ftr/AST-309`).

| Item | Action |
|------|--------|
| **discuss** `artifact_shapes.cover_letter.signature` required | Set **`required: False`** in `BUILD_CONFIG.artifact_shapes` to match `craft_job_cover_letter` task schema; normalizer still coerces missing signature to `""`. |
| **discuss** `craft_job_cover_letter` → save wire | **Deferred to AST-369** — this ticket ships schema + `normalize_cover_letter_artifact` / `save_job_artifact_cover_letter` only. |

