# AST-358 — Replace per-vector grade_scores with universal grade values + per-vector importance multiplier

<!-- linear-archive: AST-358 archived 2026-06-03 -->

## Linear archive (AST-358)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-358/replace-per-vector-grade-scores-with-universal-grade-values-per-vector  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** susan  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Context

The current scored grading model bakes per-vector weighting into the grade values themselves. Each vector defines its own `grade_scores` dict — e.g. `TITLE_MATCH` has `{"A": 50, "B": 40, "C": 20, "D": 5}` while `EDUCATION_FIT` has `{"A": 10, "B": 8, "C": 5, "D": 2}`.

This conflates two independent ideas:

1. **How well the candidate matches a vector** (the grade)
2. **How much that vector matters to this rubric** (the importance)

It also introduces non-monotonic ratios that vary per vector (A:B:C:D spacing differs across vectors), which makes it hard to reason about the model and harder to tune. The grade-to-grade gap should be a property of the grade, not the vector.

## What we want instead

A clean three-knob model:

* **Universal grade values** — A, B, C, D have a single numeric value each, used for every vector in every rubric. F is a dealbreaker (halt). X excludes the vector from scoring entirely. The non-monotonic spacing is intentional and stays — e.g. `A=7, B=6, C=3, D=0` — but it's defined once at the config level.
* **Confidence as a multiplier on grade density** — confidence 1–5 maps to a 0–100% multiplier (5=100%, 4=80%, ..., 1=0%). `density = (grade_value / max_grade_value) × confidence_pct`.
* **Per-vector importance, set by the user, 1–10** — each vector on each rubric has an importance value selected by the user when authoring the rubric (or by us when configuring system rubrics). 1–10 maps linearly to a percentage multiplier between two configured endpoints (e.g. 30% to 200%). Importance is the only signal of how much a vector matters; positional ordering in the UI is purely cosmetic and does not affect scoring.

## Scoring formula

```
For each vector i in the rubric:
    base_i = rubric_total / V                          # equal share; V = vector count
    density_i = (grade_value_i / max_grade_value)      # 0.0 to 1.0
                × (confidence_i / 5)                   # 0.0 to 1.0
    importance_mult_i = linear_map(importance_i,       # importance 1..10
                                    in_range=[1,10],
                                    out_range=[floor%, ceiling%])
    contribution_i = base_i × density_i × importance_mult_i

rubric_score = sum(contribution_i)  for all i where grade != X
```

* **F at any vector** → halt; rubric returns the configured fail_state with `score=None`.
* **X at any vector** → that vector contributes nothing AND is not counted toward V or the denominator. (Preserve the existing semantic: X is excluded from both numerator and denominator.)
* **Scores can exceed** `rubric_total`. This is intentional. With the importance ceiling above 100%, a rubric stacked with high-importance As will score above the nominal total. We do not normalize this away because there is no cross-rubric or cross-candidate comparison happening at the score level; the score is a standalone signal for one (candidate, job, rubric) tuple.

## What becomes config

All of these need to be admin-configurable (config-driven, not UI-managed at runtime — at least in v1):

| Config | Example | Notes |
| -- | -- | -- |
| `GRADE_VALUES` | `{"A": 7, "B": 6, "C": 3, "D": 0}` | Universal across all rubrics. F and X are not in this map; they're handled as control flow. |
| `CONFIDENCE_PERCENTAGES` | `{1: 0.0, 2: 0.2, 3: 0.5, 4: 0.8, 5: 1.0}` | Or a formula. Whatever we pick should be explicit, not derived. |
| `IMPORTANCE_FLOOR_PCT` | `0.30` | Multiplier applied when importance=1. |
| `IMPORTANCE_CEILING_PCT` | `2.00` | Multiplier applied when importance=10. |
| `RUBRIC_TOTAL` | `3000` | Cosmetic display number. Per-rubric or global; either works. |

Per-rubric config still defines the vector list, but each vector entry now needs only `name` and `importance` — no more per-vector `grade_scores`.

## Behavioral guarantees

* F = dealbreaker, halt, fail_state, score=None.
* X = exclude from scoring, no contribution, not counted in V.
* The 0–10 final score scale should be preserved for threshold comparison consistency: the internal computation produces a number that may exceed `rubric_total`, and the returned score is normalized to 0–10 against `rubric_total` before being compared against `pass_threshold`.
* Existing state-machine wiring (pass_state, fail_state, pass_threshold per task) is unchanged.

## Why this is worth doing

The current model works but it's hard to tune. Adjusting how much `TITLE_MATCH` matters relative to `EDUCATION_FIT` requires editing two `grade_scores` dicts and reasoning about how the A-values affect the denominator. Under the new model it's one number per vector (importance: 1–10) and the math falls out. It also separates "what is this candidate like" from "what does this rubric care about," which are two different conversations and shouldn't share a config field.

### Comments

#### chuckles — 2026-05-18T00:05:47.475Z
## Landed on origin/dev — Chuckles

- Merged `origin/ftr/AST-358-replace-per-vector-grade-scores-with-universal-grade-values-per-vector-importance-multiplier` → local `dev` (already up to date from prep-uat) → pushed **`origin/dev`** (`e073aa44` → `d121c98a`)
- Deleted `origin/ftr/AST-358-replace-per-vector-grade-scores-with-universal-grade-values-per-vector-importance-multiplier`
- Children already **PR Ready** (assignee unchanged): **AST-428**, **AST-429**

**Push tip:** `d121c98a` — `merge(AST-358): prep-uat — integrate parent feature branch into local dev for UAT` (rollup of 428 + 429)

Ready for Susan to merge **`dev`** → **`main`**. Parent **Done** when you close the epic.

— Chuckles

#### chuckles — 2026-05-17T23:33:00.576Z
## UAT Ready — Chuckles

All **2** child branches merged into parent branch and child branches deleted.

**Parent branch:** `origin/ftr/AST-358-replace-per-vector-grade-scores-with-universal-grade-values-per-vector-importance-multiplier`

**Merged in order:**
1. **AST-428** — Universal grade values config (`sub/AST-358/AST-428-…-universal-grade-values-config` — deleted)
2. **AST-429** — Importance-based scoring engine (`sub/AST-358/AST-429-…-importance-based-scoring-engine` — deleted)

**Local `dev`** merged (`d121c98a` — `merge(AST-358): prep-uat — integrate parent feature branch into local dev for UAT`). Restart the app if it is running, then test.

If testing fails on `dev`:
```bash
git reset --hard origin/dev
```

Children **AST-428** / **AST-429** remain **User Testing** with Ada as assignee.

— Chuckles

#### chuckles — 2026-05-17T22:33:17.703Z
## Dispatch — Chuckles

Dispatched **2** child tickets from the approved definition. Prerequisites **AST-357** (confidence) and **AST-359** (importance UI + multiplier table) are **Done**.

| Ticket | Title | Assigned to | Branch | Blocked by |
|--------|-------|-------------|--------|------------|
| [AST-428](https://linear.app/astralcareermatch/issue/AST-428) | Universal grade values config | Ada | `sub/AST-358/AST-428-replace-per-vector-grade-scores-with-universal-grade-values-per-vector-importance-multiplier-universal-grade-values-config` | — |
| [AST-429](https://linear.app/astralcareermatch/issue/AST-429) | Importance-based scoring engine | Ada | `sub/AST-358/AST-429-replace-per-vector-grade-scores-with-universal-grade-values-per-vector-importance-multiplier-importance-based-scoring-engine` | AST-428 |

**Assignment rationale:**
- **Ada:** Config + `consult.py` scoring — agent runtime / config plumbing domain; both children are one coherent core layer change.
- **Hedy / Katherine:** Not assigned — no tracker, Flask, or React work in this epic beyond what AST-359 already shipped.

Susan can override any assignment by reassigning the child ticket directly.

Parent moves to **In Progress**. **prep-uat** will merge child branches and hand the parent branch to Susan when all children reach **Review Posted**.

**Git (authoritative — ignore Linear `gitBranchName`):**
- Parent: `origin/ftr/AST-358-replace-per-vector-grade-scores-with-universal-grade-values-per-vector-importance-multiplier`
- Children:
  - `origin/sub/AST-358/AST-428-replace-per-vector-grade-scores-with-universal-grade-values-per-vector-importance-multiplier-universal-grade-values-config`
  - `origin/sub/AST-358/AST-429-replace-per-vector-grade-scores-with-universal-grade-values-per-vector-importance-multiplier-importance-based-scoring-engine`

Plan attachments should use  
`https://github.com/susansomerset/astral/blob/<sub-ref-or-ftr-ref>/docs/features/consult/...`  
after **plan-astral** lands the plan doc.

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
