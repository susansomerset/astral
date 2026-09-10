# Review rubrics

Versioned rubrics score plans, code, and (later) tests. Rubrics **consume** statutes and patterns; they do **not** define them. Statute corpus: [`../statutes/`](../statutes/).

## Citation

Review artifacts (Linear comments / attachments / review docs) must name the rubric revision they were scored against — e.g. `plan-rubric.v1` or `code-rubric.v1` (filename + frontmatter `revision`).

## Index

| id | path | executor | status |
|----|------|----------|--------|
| `plan-rubric.v1` | [`plan/plan-rubric.v1.md`](plan/plan-rubric.v1.md) | Joan / `validate-plan` | active |
| `code-rubric.v1` | [`code/code-rubric.v1.md`](code/code-rubric.v1.md) | Radia / `review-child` | superseded (by `code-rubric.v2`) |
| `code-rubric.v2` | [`code/code-rubric.v2.md`](code/code-rubric.v2.md) | Radia / `review-child` | active |

`code-rubric.v2` (AST-1115) rewrites C5 — Radia now resolves cited pattern ids against the real `canon/patterns/**` catalog and scores conformance, instead of deferring to the statute sweep. `code-rubric.v1` remains resolvable for historical `[code-rubric] revision=1` citations; new reviews cite `revision=2`.

Test rubric: deferred second wave (Betty).
