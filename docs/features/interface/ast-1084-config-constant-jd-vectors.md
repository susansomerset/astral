# Config constant JD vectors (QC / GC)

**Linear:** [AST-1084](https://linear.app/astralcareermatch/issue/AST-1084/config-constant-jd-vectors-qc-gc-add-a-constant-set-of-rubric-vectors)
**Parent:** [AST-1077](https://linear.app/astralcareermatch/issue/AST-1077/add-a-constant-set-of-rubric-vectors-to-generated-jd-evaluate-vectors)
**Publish ref:** `sub/AST-1077/AST-1084-config-constant-jd-vectors`

Add a config-owned constant criteria block for Quality Check (**QC**) and Gut Check (**GC**) — importance **1**, grade letter → description text from the parent Original brief — shaped like `EMBEDDED_COMPANY_PREFILTER_CRITERIA`. Definitions only: no runtime merge into `evaluate_jd` hydration, generate/save restore, or other rubric owners (sibling AST-1085).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `EMBEDDED_EVALUATE_JD_CRITERIA` tuple after `EMBEDDED_COMPANY_PREFILTER_CRITERIA` | utils |

No other files. Do not import or reference the new constant from core/UI/data in this ticket.

## Stage 1: Config constant QC / GC block

**Done when:** `src/utils/config.py` defines `EMBEDDED_EVALUATE_JD_CRITERIA` as a `tuple[dict, ...]` with exactly two rows (QC then GC), each matching the RC row shape (`code`, `label`, `importance`, `content`, `grade_descriptions`). Importance is `1` on both. Grade letters and description strings match the parent Original brief (verbatim meaning). Nothing else in the repo imports or merges this constant yet.

1. In `src/utils/config.py`, immediately after the closing `)` of `EMBEDDED_COMPANY_PREFILTER_CRITERIA` (currently ends near the AST-707 Reality Check block, before the AST-803 legacy BUILD_ARTIFACTS helpers), insert a new constant:

   ```python
   # AST-1084 / AST-1077: embedded evaluate_jd vectors — definitions only;
   # merge/append into jobdesc / evaluate_jd hydration is AST-1085.
   EMBEDDED_EVALUATE_JD_CRITERIA: tuple[dict, ...] = (
       {
           "code": "QC",
           "label": "Quality Check",
           "importance": 1,
           "content": (
               "Quality Check — is this enough of a JD to analyze?\n"
               "A = This is a valid job description with full details of the role and requirements and information about the company the candidate would be working for.\n"
               "B = This is a valid job description with full details of the role and requirements, but limited information about the company the candidate would be working for.\n"
               "C = This content references a job with enough detail about the role and requirements to perform fit analysis for the candidate.\n"
               "F = This is not enough information to perform job fit analysis, either because it is not a job description, or it is too vague to determine fit for the candidate."
           ),
           "grade_descriptions": [
               {
                   "grade": "A",
                   "description": "This is a valid job description with full details of the role and requirements and information about the company the candidate would be working for.",
               },
               {
                   "grade": "B",
                   "description": "This is a valid job description with full details of the role and requirements, but limited information about the company the candidate would be working for.",
               },
               {
                   "grade": "C",
                   "description": "This content references a job with enough detail about the role and requirements to perform fit analysis for the candidate.",
               },
               {
                   "grade": "F",
                   "description": "This is not enough information to perform job fit analysis, either because it is not a job description, or it is too vague to determine fit for the candidate.",
               },
           ],
       },
       {
           "code": "GC",
           "label": "Gut Check",
           "importance": 1,
           "content": (
               "Gut Check — is this even plausible for this candidate?\n"
               "A = Based on the candidate's bio provided, this job would be a slam dunk for them.\n"
               "B = Based on the candidate's bio provided, this job could be a good fit for them.\n"
               "C = Based on the candidate's bio, this job would be doable, with caveats, for them.\n"
               "D = Based on the candidate's bio, this job would be a stretch-to-impossible for them.\n"
               "F = There's really no way this candidate could ever do this job.\n"
               "X = There's not enough information about the job to make this determination with certainty."
           ),
           "grade_descriptions": [
               {
                   "grade": "A",
                   "description": "Based on the candidate's bio provided, this job would be a slam dunk for them.",
               },
               {
                   "grade": "B",
                   "description": "Based on the candidate's bio provided, this job could be a good fit for them.",
               },
               {
                   "grade": "C",
                   "description": "Based on the candidate's bio, this job would be doable, with caveats, for them.",
               },
               {
                   "grade": "D",
                   "description": "Based on the candidate's bio, this job would be a stretch-to-impossible for them.",
               },
               {
                   "grade": "F",
                   "description": "There's really no way this candidate could ever do this job.",
               },
               {
                   "grade": "X",
                   "description": "There's not enough information about the job to make this determination with certainty.",
               },
           ],
       },
   )
   ```

2. Do **not** add QC/GC into `EMBEDDED_COMPANY_PREFILTER_CRITERIA`. Do **not** change `rubric_criteria_for_task`, `candidate.py` merge helpers, dispatcher, or UI. Do **not** add D/X grades to Quality Check or invent letters beyond the brief.

⚠️ **Decision:** Name the constant `EMBEDDED_EVALUATE_JD_CRITERIA` (parallel to `EMBEDDED_COMPANY_PREFILTER_CRITERIA`, keyed to the `evaluate_jd` owner) rather than a `jobdesc_*` alias — parent Architectural definition targets the evaluate_jd / jobdesc_rubric path; the wire-up sibling will import this exact name.

⚠️ **Decision:** Quality Check `grade_descriptions` list only A/B/C/F (no D/X); Gut Check lists A/B/C/D/F/X — locked by parent Boundaries / Original brief. Do not “complete” the QC set to the full `{A,B,C,D,F,X}` alphabet.

⚠️ **Decision:** `content` lines use `A = …` (same style as Reality Check) with the Original brief sentence text after `==` preserved verbatim; `grade_descriptions[].description` is that same sentence without the letter prefix.

## Self-Assessment

**Scope:** `minor` — single utils config constant; no core/UI/data wiring.

**Conf:** `high` — copy the existing `EMBEDDED_COMPANY_PREFILTER_CRITERIA` row shape; grade text is fixed in the parent Original brief; codes/importance locked in the ticket.

**Risk:** `low` — unused until AST-1085 imports it; wrong text would only surface when the sibling wires merge, and can be corrected in config without changing runtime paths in this ticket.

## Rules check

- §2.1 / `astral.config.config-source-of-truth` — definitions live only in `config.py`.
- `astral.standards.no-hardcoded-sets` — no inline QC/GC sets outside this config block.
- `pattern.config.config-block` — organized tuple next to the existing embedded-criteria block.
- §1.3 DRY — no second embedding mechanism; sibling reuses this constant.
- §3.3 imports — this ticket adds no new cross-layer imports.
- In-scope only — no evaluate_jd hydration, restore-on-delete, or other rubric owners.
