<!-- linear-archive: AST-859 archived 2026-07-29 -->

## Linear archive (AST-859)

**Archived:** 2026-07-29  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-859/uat-fix-vector-reviews-prompt-example-raocvk-racovk  
**Status at archive:** Archive  
**Project:** Astral Auditor  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-378 — Runtime Rubric Validation  
**Blocked by / blocks / related:** parent: AST-378

### Description

## What failed

Susan UAT 2026-07-10: compact `vector_reviews` strings still fail to hydrate because the **model follows a contradictory example** in `RUBRIC_FEEDBACK_CONFIG.prompt_suffix` in `config.py`.

Current prompt says format `CODE + R + rel + C + cla + V + ver` but example is `"Q1RAOCVK"` which decodes as Q1 + R + **A** + **O** + C + V + K — the clarity letter **O** appears **before** the `C` delimiter. Model output matches the bad example (`CLRAOCVK`, `BSRAOCVK`, … use `RAOCVK` tail instead of correct `RACOVK`).

## Expected

1. `prompt_suffix` example and wording match the parse regex (`CODE R rel C cla V ver`) — e.g. `"Q1RACOVK"` for relevance=A, clarity=O, verdict=K.
2. After deploy, model-emitted compact strings parse via `parse_vector_review_string` and hydrate in Admin / FEEDBACK / debug.
3. No change to lenient run-success semantics.

## Repro

1. Run rubric-backed task (e.g. `evaluate_jd`) on staging with current prompt.
2. Model returns `vector_reviews` like `CLRAOCVK` (RAOCVK tail).
3. Parse/hydrate fails or stores raw FEEDBACK only.
4. Inspect `RUBRIC_FEEDBACK_CONFIG.prompt_suffix` — example contradicts delimiter spec.

## Parent AC (quoted inline)

> 1. Every rubric-backed agent task returns per-vector feedback (Relevance, Clarity, Verdict) for every vector in the active rubric when the model complies, using only config-allowed value codes.

> 7. With debug enabled, rubric-backed runs log each vector feedback found and recorded, or log that raw FEEDBACK was stored due to parse failure.

## Boundaries

* Fix prompt/example in config only — do not change parse regex unless example fix is insufficient.
* Does not change agent_payload grading format.

### Comments

#### radia — 2026-07-10T21:47:50.251Z
### AST-859 review

**Diff:** `origin/dev...origin/sub/AST-378/AST-859-uat-fix-vector-reviews-prompt-example` (code `6a83783`, doc after push)
**Plan:** `docs/features/auditor/ast-859-uat-fix-vector-reviews-prompt-example.md` § Review (Radia)

**What looks good**
- Config-only fix: `RUBRIC_FEEDBACK_CONFIG.prompt_suffix` example `Q1RAOCVK` → `Q1RACOVK` with explicit literal R/C/V delimiter wording.
- Aligns model instruction with existing `parse_vector_review_string` regex — Susan staging `CLRAOCVK` tails correctly remain parse failures until re-dispatch.
- No regex/capture lenience added; tests guard suffix content + Q1/CLR parse matrix.

**advisory**
- Historical AST-724 plan doc still shows old example (explicitly out of scope).
- Stored FEEDBACK with bad-shaped strings stay unparseable until new runs — expected.

**Verdict:** Clean — approve for User Testing. No fix-now.

#### betty — 2026-07-10T21:46:48.882Z
## QA test manifest (AST-859)

**Publish ref:** `origin/sub/AST-378/AST-859-uat-fix-vector-reviews-prompt-example` @ `6a83783` (`merge-tests(AST-859): origin/tests e298b4d`)

**Pass criterion:** manifest lines green on publish ref — not zero-arg harness / branch-lock gate.

1. **Prompt suffix example (required):** `tests/component/utils/test_config.py::TestAst859VectorReviewsPromptExample` — `prompt_suffix` contains `Q1RACOVK`, not `Q1RAOCVK`; explicit delimiter wording.

2. **Parse regression (required):** `tests/component/utils/test_rubric_feedback.py::TestAst859CompactStringParseExamples` — `Q1RACOVK` and `CLRRACOVK` parse; `Q1RAOCVK` and Susan staging `CLRAOCVK` fail.

**Narrowed run:**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst859VectorReviewsPromptExample \
  tests/component/utils/test_rubric_feedback.py::TestAst859CompactStringParseExamples \
  -q
```

**Regression:** existing `G1RAOCVK` parse-failure fixtures in `test_rubric_feedback.py` unchanged (intentional bad-line cases).

**Bible shasums (publish ref):**
- `docs/test-bible/utils/config.md`: ffb9d59f232bb228dd06c01c4f85c86d7f550ffe6c61a2d0973bcbf1820959bf
- `docs/test-bible/utils/rubric_feedback.md`: ad583a63115939bcf628d9c4a2748218c2e201d983a5340e52494d0e12d4c4c4

— Betty

#### ada — 2026-07-10T21:44:30.044Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-378/AST-859-uat-fix-vector-reviews-prompt-example/docs/features/auditor/ast-859-uat-fix-vector-reviews-prompt-example.md

**Scope:** minor — single `RUBRIC_FEEDBACK_CONFIG["prompt_suffix"]` string in `config.py`; fix example `Q1RAOCVK` → `Q1RACOVK` and clarify literal `R`, `C`, `V` delimiters so models stop emitting unparseable `RAOCVK` tails.

**Conf:** high — Susan UAT root cause; regex and bad example verified; tests already use correct `RACOVK` shape (`G1RACOVK`, `CLRRACOVK`).

**Risk:** low — prompt-only; existing stored runs with wrong-shaped output still lenient-fail until next dispatch sees corrected suffix.

---

# AST-859 — UAT: Fix vector_reviews prompt example (RAOCVK → RACOVK)

- **Linear:** [AST-859](https://linear.app/astralcareermatch/issue/AST-859/uat-fix-vector-reviews-prompt-example-racovk)
- **Parent (context only):** [AST-378](https://linear.app/astralcareermatch/issue/AST-378/runtime-rubric-validation) — Runtime Rubric Validation
- **Publish ref:** `origin/sub/AST-378/AST-859-uat-fix-vector-reviews-prompt-example`
- **Shipped baseline:** [AST-816](https://linear.app/astralcareermatch/issue/AST-816/uat-compact-vector-reviews-still-not-hydrating-on-evaluate-jd) parse/hydrate; [AST-820](https://linear.app/astralcareermatch/issue/AST-820/uat-add-debug-logging-to-vector-feedback-hydration-debug-logging) pipeline debug trace

## Summary

Susan UAT 2026-07-10: compact **`vector_reviews`** still fail parse/hydrate on staging because **`RUBRIC_FEEDBACK_CONFIG.prompt_suffix`** teaches the wrong wire shape. The text says `CODE + R + rel + C + cla + V + ver`, but the example **`"Q1RAOCVK"`** omits the **`C`** delimiter before the clarity letter — models emit tails like **`RAOCVK`** (`CLRAOCVK`, `BSRAOCVK`, …) which **`parse_vector_review_string`** rejects. Fix the config example and wording only (e.g. **`"Q1RACOVK"`** = relevance **A**, clarity **O**, verdict **K**); no regex or capture logic change.

## Out of scope (explicit)

| Item | Owner |
|------|--------|
| `parse_vector_review_string` regex change | — (only if example fix insufficient; not expected) |
| Lenient run-success semantics | AST-724 |
| `agent_payload` grading format | — |
| Retroactive rewrite of stored FEEDBACK blocks | — |

## Root cause (plan-time)

Parse regex in **`src/utils/rubric_feedback.py`**:

```text
^([A-Za-z0-9]+)R([AOSRN])C([AOSRN])V([KED])$
```

Requires literal **`R`**, **`C`**, **`V`** delimiters between code and the three value letters.

| String | Parsed? | Why |
|--------|---------|-----|
| `Q1RAOCVK` (current example) | **No** | After `Q1` + `R` + `A`, next char is **`O`** — not delimiter **`C`** |
| `Q1RACOVK` (correct) | **Yes** | `Q1` + `R` + `A` + `C` + `O` + `V` + `K` |
| `CLRAOCVK` (Susan staging) | **No** | Model followed bad example — `CL` + `RAOCVK` tail without **`C`** before clarity **O** |
| `CLRRACOVK` (tests / AST-816) | **Yes** | `CLR` + `R` + `R` + `C` + `O` + `V` + `K` |

**`prompt_suffix`** is appended to rubric-backed **`do_task`** prompts in **`agent.py`** (~line 1822). Every rubric-backed consumer/craft task inherits the bad example from **`config.py`**.

⚠️ **Decision:** Config-only fix — correct example + explicit delimiter wording; do not add lenient parse for `RAOCVK` tails (would mask future prompt drift).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Fix `RUBRIC_FEEDBACK_CONFIG["prompt_suffix"]` example and delimiter wording | utils |

**Tests:** Betty owns **`tests/`** at Code Complete — engineer does **not** add test files in **build-child**. Existing **`test_rubric_feedback`** already uses **`G1RAOCVK`** as intentional parse-failure fixture.

---

## Stage 1: Fix prompt_suffix example and delimiter wording

**Done when:** `RUBRIC_FEEDBACK_CONFIG["prompt_suffix"]` contains example **`Q1RACOVK`**; `parse_vector_review_string("Q1RACOVK")` returns `(Q1, {relevance: A, clarity: O, verdict: K})`; `parse_vector_review_string("Q1RAOCVK")` still returns `None`; no other files changed.

1. In **`src/utils/config.py`**, locate **`RUBRIC_FEEDBACK_CONFIG["prompt_suffix"]`** (~line 2163).

2. Replace the example and tighten delimiter wording. Target string (single tuple element — preserve trailing sentence):

   ```python
   "prompt_suffix": (
       "Vector rubric review (agent_performance only — not agent_payload): include "
       "vector_reviews as a JSON list of strings. One string per rubric vector code "
       "you were given. Wire format: CODE then literal R, relevance letter, literal C, "
       "clarity letter, literal V, verdict letter — relevance/clarity "
       "{A|O|S|R|N}, verdict {K|E|D} "
       '(example: "Q1RACOVK" = code Q1, relevance A, clarity O, verdict K). '
       "agent_performance.status reflects only whether you "
       'could perform the task — never "failure" because grades or verdicts were harsh.'
   ),
   ```

   ⚠️ **Decision:** Use **`Q1RACOVK`** not **`Q1RACOVE`** — keep **O** clarity and **K** verdict to match the prior example's intended semantics (A/O/K), only fixing delimiter placement.

3. Do **not** change **`_VECTOR_REVIEW_RE`** in **`rubric_feedback.py`**.

4. Do **not** edit **`docs/features/auditor/ast-724-runtime-vector-feedback-capture.md`** — historical plan; AST-859 is the UAT delta.

5. Manual verify on epic worktree (no commit script):

   ```python
   from src.utils.rubric_feedback import parse_vector_review_string
   assert parse_vector_review_string("Q1RACOVK") is not None
   assert parse_vector_review_string("Q1RAOCVK") is None
   assert parse_vector_review_string("CLRAOCVK") is None
   assert parse_vector_review_string("CLRRACOVK") is not None
   ```

### Self-review (Stage 1)

| Rule | OK? |
|------|-----|
| §2.1 config | Single source of truth in `RUBRIC_FEEDBACK_CONFIG` |
| §1.4 no magic | Example documents allowed value letters inline |
| Scope | Config string only |

---

## Execution contract (build-child)

- **One stage**, one commit on epic worktree; publish to **`origin/sub/AST-378/AST-859-uat-fix-vector-reviews-prompt-example`**.
- Do **not** edit **`tests/`** or **`docs/test-bible/**`**.
- On ambiguity — **`🛑 Stage 1 blocked`** on **AST-378** parent; stop.

---

## Self-Assessment

**Scope:** `minor` — One string in `RUBRIC_FEEDBACK_CONFIG` in `config.py`.

**Conf:** `high` — Susan identified root cause; regex and bad example verified in codebase; tests already use correct `RACOVK` shape.

**Risk:** `low` — Prompt-only change; existing runs with wrong-shaped model output still lenient-fail until model sees corrected prompt on next dispatch.

---

## Self-review vs ASTRAL_CODE_RULES

| Section | Result |
|---------|--------|
| §2.1 config | Fix in `RUBRIC_FEEDBACK_CONFIG` only |
| §1.3 DRY | No duplicate prompt text elsewhere |
| §3.3 imports | No layer changes |

No unresolved rule conflicts.

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-378/AST-859-uat-fix-vector-reviews-prompt-example` (code tip `6a83783`)  
**Reviewed:** 2026-07-10

Minimal UAT fix diff (6 files) — config string + regression tests only; this review is AST-859 only.

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity | Single-stage config fix: `Q1RAOCVK` → `Q1RACOVK`; explicit literal `R`/`C`/`V` delimiter wording; no regex or capture changes. |
| Root cause | Bad example taught `RAOCVK` tails; Susan staging strings (`CLRAOCVK`, …) fail `parse_vector_review_string` — fix aligns prompt with existing regex. |
| §2.1 config | Single source in `RUBRIC_FEEDBACK_CONFIG["prompt_suffix"]`; consumed by `agent.py` rubric-backed prompt append — no duplicate prompt text. |
| Tests | `TestAst859VectorReviewsPromptExample` guards suffix content; `TestAst859CompactStringParseExamples` locks Q1/CLR parse matrix from plan manual verify. |
| Scope | No lenient parse for malformed tails — correct per plan (avoids masking future drift). |

### Issues

| Sev | Location | Finding |
|-----|----------|---------|
| advisory | Historical plans | `ast-724-runtime-vector-feedback-capture.md` still cites `Q1RAOCVK` — plan explicitly deferred; optional doc hygiene later, not blocking. |
| advisory | Staging data | Existing FEEDBACK blocks with `RAOCVK`-shape strings remain unparseable until re-dispatch with corrected prompt — expected per Self-Assessment. |

### Recommended actions

| Priority | Action |
|----------|--------|
| **resolve** | None required — approve for User Testing. |
| UAT | Re-run `evaluate_jd` (or rubric-backed task) with debug: model emits `RACOVK`-shape strings; capture/hydrate succeeds when rubric count matches. |

**Verdict:** Clean — approve for User Testing.

---

## Resolution

**Resolved:** 2026-07-10  
**Review:** Radia clean — no fix-now items.

| Item | Outcome |
|------|---------|
| Product | No additional changes — `ba84651` config fix stood as reviewed. |
| Tests | Betty manifest green at `6a83783` (5/5 on first pass). |
| Docs | Radia review section landed at `ea7b732`. |

**Publish ref:** `origin/sub/AST-378/AST-859-uat-fix-vector-reviews-prompt-example` @ `ea7b732`  
**§9a:** Clean merge into `origin/dev` and `origin/ftr/AST-378-runtime-rubric-validation`.
