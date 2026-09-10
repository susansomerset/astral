# AST-706 — "Reality Check" should reference the letter code of "RC" for re-hydration.

<!-- linear-archive: AST-706 archived 2026-06-23 -->

## Linear archive (AST-706)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-706/reality-check-should-reference-the-letter-code-of-rc-for-re-hydration  
**Status at archive:** Duplicate  
**Project:** Astral Agent  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** duplicate: AST-707

### Description

## Purpose

Company **prefilter_company** always grades a built-in **Reality Check** vector in the task prompt, even when that vector is absent from the candidate's `company_prefilter` rubric artifact. Models return compact encoded segments with code **RC**; decode and post-decode hydration today build `vector_labels` and rubric lookups only from the candidate artifact, so **RC** cannot be re-hydrated to **Reality Check** grade reasons and scoring fails or drops the vector. Production prefilter runs therefore error or produce incomplete notes/scores when the model correctly grades Reality Check. This epic wires the built-in vector into decode, hydration, and scoring with **importance 1**, while keeping **F** with confidence **2–5** a dealbreaker.

## Functional scope

* **Built-in Reality Check criterion:** Define a canonical **Reality Check** rubric criterion for prefilter with letter code **RC**, label **Reality Check**, and the grade descriptions already used in the live **prefilter_company** prompt (A/B/C/D/F semantics for "is this a real company website"). Store in config as the single source of truth for this built-in vector (not in the candidate artifact editor).
* **Effective prefilter rubric:** For **prefilter_company** only, build an **effective rubric list** = built-in **Reality Check** (always first) plus the candidate's `company_prefilter` criteria. If the candidate artifact already contains a criterion with code **RC** or label **Reality Check**, do not duplicate — the built-in entry supplies code **RC**, label, grade descriptions, and **importance 1** for scoring/hydration.
* **Decode (**`vector_labels`**):** When assembling `vector_labels` for **prefilter_company** (single-company and batch paths), always include `RC` **→** `Reality Check` even when **RC** is missing from the candidate artifact. Encoded segments like **RCA3** decode to vector **Reality Check**, not raw **RC**.
* **Re-hydration:** `_hydrate_grade_reasons_from_rubric` (and batch hydration) for prefilter must use the **effective rubric list**, so **Reality Check** grades receive `reason` text from the built-in criterion when the candidate artifact omits that vector.
* **Scoring:** `prefilter_score` computation uses the **effective rubric list** with **Reality Check** at **importance 1** (lowest weight). Other vectors use importance from the candidate artifact as today.
* **Pass/fail (dealbreaker):** **Reality Check** participates in existing dealbreaker rules — **F** with confidence **2–5** on **Reality Check** fails prefilter regardless of other vectors. No change to **AST-507** pass/fail semantics beyond including the built-in vector in the graded set.
* **Batch and monolithic paths:** Single-company `prefilter_company`, `_run_batch_company_prefilter`, coat-check / notes replay, and `_apply_prefilter_decoded_company_outcome` share the same effective-rubric and **vector_labels** behavior.

## Boundaries

* **prefilter_company only** — consult batch tasks (qualify, evaluate, DO/GET/LIKE) do not gain a built-in Reality Check vector.
* **No prompt copy redesign** — Susan may edit Manage Tasks prose manually; this epic lands config + runtime merge only. Do not auto-migrate `agent_task` rows.
* **No rubric craft UI changes** — candidates may still omit Reality Check from `company_prefilter`; the built-in vector is runtime-only.
* **No new company states or dispatch rows.**
* **Must not break** **AST-603** normalization, **AST-697** link_set decode, or **AST-702** batch prefilter orchestration.
* Config-driven built-in criterion per **ASTRAL_CODE_RULES** §2.1 — no inline magic strings scattered in core.

## Acceptance criteria

1. With a candidate `company_prefilter` artifact that **does not** include Reality Check, a model response `000|RCA3|MPB3|USA3` decodes to grades with vector **Reality Check** (not **RC**) for the first segment.
2. Same candidate context: after decode, hydration fills `reason` on the **Reality Check** grade from the built-in criterion (non-empty, matches built-in grade table).
3. `prefilter_score` on pass uses **importance 1** for **Reality Check** — verified when **Reality Check** is absent from the candidate artifact but present in grades (score differs from treating RC at default importance).
4. **Reality Check** grade **F** with confidence **3** fails prefilter (dealbreaker); **F** with confidence **1** does not fail solely on that row (existing confidence rules).
5. Candidate artifact that **already includes** Reality Check with code **RC** still hydrates and scores without duplicate-vector errors.
6. Batch prefilter (**HOMEPAGE_READY** path) and single-company prefilter behave the same for **RC** decode, hydration, and scoring.

## Dependencies and blockers

* **AST-603** (Done) — rubric normalization and hydration path.
* **AST-507** (Done) — encoded prefilter and dealbreaker **F** semantics.
* **AST-697** (Done) — link_set bracket decode (must not regress).
* **AST-702** (User Testing) — batch prefilter evaluate path.
* **AST-707** (User Testing, parent AST-700) — embedded RC merge and hydration landed; config still has **importance 8** — this epic sets **1** and verifies remaining AC.

None blocking start.

## Open questions

none.

---

## Original brief

When prefilter responds, it automatically includes the Reality Check vector that is not baked in to the candidate's rubric, so the agent returns "RC" but there's no match found in the rubrics.  It should have an importance of 1, but an F is a dealbreaker.

### Comments

#### chuckles — 2026-06-16T19:24:01.027Z
[check-linear]

Yes — **AST-707** (UAT bug under **AST-700**) is the implementation of this fix: `EMBEDDED_COMPANY_PREFILTER_CRITERIA` in config, merge in `_rubric_criteria_from_cd`, code-aware hydration so **RC** resolves when the candidate artifact omits Reality Check. Batch prefilter is at **User Testing** on Hedy's branch.

**One nuance:** **AST-707** shipped embedded **RC** at **importance 8**; your brief here asked for **importance 1**. If UAT passes on hydration, flip **8 → 1** in config during **AST-700** re-test (or a tiny follow-up) — not a separate epic.

**Recommendation:** mark **AST-706** duplicate of **AST-707**; track importance **1** on **AST-700** UAT if you still want that weight.

— Chuckles

#### susan — 2026-06-16T19:21:07.143Z
@chuckles I think I got confused on this one and we actually implemented this in a child of [AST-700](https://linear.app/astralcareermatch/issue/AST-700/prefilter-as-batch-process).  Do you agree?  Should we mark this as a duplicate, or is there more nuance we are missing?

---

_Implementation detail may live in git history on `origin/dev`._
