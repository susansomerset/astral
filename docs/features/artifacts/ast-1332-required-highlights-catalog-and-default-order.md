# AST-1332 — Required Highlights catalog and default order

**Linear:** https://linear.app/astralcareermatch/issue/AST-1332/required-highlights-catalog-and-default-order  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1326/make-highlights-a-required-resume-section  
**Publish ref:** `sub/AST-1326/AST-1332-required-highlights-catalog-and-default-order`

Elevate `highlights` into the required resume-structure catalog and default structure: present + enabled, default format `bullet_list`, order immediately above Experience; coerce that placement on normalize/resolve so base_resume_content follows it. Does **not** own hop schema or agent_task prompt text (sibling AST-1333). Does **not** invent a new body format or HTML emit path (existing `bullet_list` emit stays).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `highlights` to `RESUME_STRUCTURE_REQUIRED_SECTION_IDS` (before `experience`); add `"highlights": "bullet_list"` to `RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID`; insert `highlights` into `RESUME_STRUCTURE_DEFAULT["sections"]` with title Highlights, enabled True, format from the map, order immediately above Experience; renumber Experience and following default orders. | utils |
| `src/core/candidate.py` | After per-section validation in `normalize_resume_structure`, coerce section `order` values so when both `highlights` and `experience` are present, `highlights` sits immediately above `experience` in order-sorted section lists. Missing `highlights` / `enabled=False` continue to raise via the existing required-id checks (no separate mint path in normalize). | core |

**Out of files (siblings / boundaries):**

| File / area | Owner |
|-------------|-------|
| Craft-base / simple-resume-parse `response_schema`, agent_task prompt seed JSON | AST-1333 |
| `src/core/builder.py` HTML emit by format | unchanged — `bullet_list` path already emits Highlights |
| `DATA_SHAPES` / `BUILD_CONFIG["…"]["base_resume_structure"]` legacy tab template | out of scope — live UI reads `artifacts.resume_structure` order via `/resume_structure` |
| `tests/`, `docs/test-bible/**` | Betty |

## Traceability (this child's AC only)

Parent ACs 4–5 (schema + agent_task prompts) are AST-1333. Do not implement them here.

| Child AC | Stage |
|----------|--------|
| 1 — structure missing `highlights` fails normalize like other required ids; `enabled=false` rejected | 1 (required membership) + existing normalize checks (no code change beyond tuple) |
| 2 — default / newly minted structures place Highlights immediately above Experience by `order` | 1 |
| 3 — existing structure with Highlights below Experience shows Highlights immediately above Experience after resolve/normalize | 2 |
| 4 — HTML emit stays `bullet_list` / closed formats — no new visual language | 1 (default format only; no builder edits) |

## Stage 1: Config — required catalog + default order + format

**Done when:** `RESUME_STRUCTURE_REQUIRED_SECTION_IDS` includes `highlights` immediately before `experience`. `RESUME_STRUCTURE_KNOWN_SECTION_IDS` (composed from required + historical optional) is eleven ids with `highlights` in that same place. `RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID["highlights"]` is `"bullet_list"`. `RESUME_STRUCTURE_DEFAULT["sections"]["highlights"]` exists with title `"Highlights"`, `enabled` True, `job_agent_editable` True, `format` from the map, and `order` strictly less than `experience`'s `order` with no other default section between them when sorted by `order`. Historical optional ids remain in DEFAULT and in `RESUME_STRUCTURE_HISTORICAL_OPTIONAL_SECTION_IDS` (not stripped). No `candidate.py` behavior change in this stage.

1. In `src/utils/config.py`, in the `# Per-candidate resume section catalog (AST-517 / AST-1303)` block, change `RESUME_STRUCTURE_REQUIRED_SECTION_IDS` to this **exact** tuple (insert `highlights` before `experience`; do not reorder anything else):

   ```python
   RESUME_STRUCTURE_REQUIRED_SECTION_IDS = (
       "candidate_name",
       "candidate_title",
       "candidate_tagline",
       "candidate_contact_detail",
       "professional_summary",
       "core_competencies",
       "highlights",
       "experience",
   )
   ```

   Leave `RESUME_STRUCTURE_HISTORICAL_OPTIONAL_SECTION_IDS` and the `RESUME_STRUCTURE_KNOWN_SECTION_IDS` composition unchanged (still `*REQUIRED + *HISTORICAL`). Do **not** put `highlights` in the historical-optional tuple.

2. In `RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID`, add this entry (keep all existing keys):

   ```python
   "highlights": "bullet_list",
   ```

3. In `RESUME_STRUCTURE_DEFAULT["sections"]`, insert a `highlights` entry **immediately before** the `experience` entry, and renumber `order` ints so the body sequence is contiguous and Highlights sits immediately above Experience. Use these **exact** orders for the affected body/contact rows (contact 0–3 unchanged):

   | id | order |
   |----|-------|
   | `candidate_name` | 0 |
   | `candidate_title` | 1 |
   | `candidate_tagline` | 2 |
   | `candidate_contact_detail` | 3 |
   | `professional_summary` | 4 |
   | `core_competencies` | 5 |
   | `highlights` | 6 |
   | `experience` | 7 |
   | `prior_experience` | 8 |
   | `education_certifications` | 9 |
   | `technical_skills` | 10 |

   The new `highlights` section dict must be:

   ```python
   "highlights": {
       "id": "highlights",
       "title": "Highlights",
       "enabled": True,
       "order": 6,
       "job_agent_editable": True,
       "format": RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID["highlights"],
   },
   ```

   Update the existing `experience` / `prior_experience` / `education_certifications` / `technical_skills` entries' `"order"` values to 7 / 8 / 9 / 10 respectively (titles, enabled, formats, job_agent_editable unchanged).

4. Do **not** edit `RESUME_STRUCTURE_BODY_FORMATS`, `RESUME_STRUCTURE_CONTACT_SECTION_IDS`, `RESUME_STRUCTURE_EXTRA_*`, `BUILD_CONFIG`, `DATA_SHAPES`, `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA`, `TASK_CONFIG`, agent_task seed JSON, or `src/core/builder.py`.

5. Do **not** change `src/core/candidate.py` in this stage (Stage 2 adds order coercion). Leaving normalize without coerce for one commit is intentional — required membership alone already satisfies AC1 for omit / disable once Stage 1 lands (existing checks iterate `RESUME_STRUCTURE_REQUIRED_SECTION_IDS`).

⚠️ **Decision:** `highlights` joins **required**, not historical-optional. Open extras may still use other slugs; `highlights` is now a known required id (same path as `experience` for required + disable rules). KNOWN grows from ten to eleven ids; hop/schema field inventory remains AST-1333.

⚠️ **Decision:** Default format is `bullet_list` only — Abrams treatment. Operators may still pick another closed body format on save where the structure editor allows it; this ticket does not lock format the way `experience` locks `experience_detail`.

⚠️ **Decision:** Do not patch the legacy `DATA_SHAPES` `base_resume_structure` tab list. Persistence authority is `artifacts.resume_structure`; `/artifacts/base_resume_content` already orders from resolve/hydrate.

## Stage 2: Normalize — coerce Highlights immediately above Experience

**Done when:** Calling `normalize_resume_structure` on a structure that includes all required ids (including `highlights`) where `highlights.order` is greater than `experience.order` (or any other section sits between them when sorted by `(order, id)`) returns a structure where, in the order-sorted section list, `highlights` is immediately before `experience`. Omitting `highlights` still raises `ValueError` whose message contains `missing required`. `enabled=False` on `highlights` still raises `ValueError` whose message contains `cannot be disabled`. A default deep-copy from `default_resume_structure()` still normalizes with Highlights immediately above Experience. Relative order among sections other than the Highlights↔Experience adjacency is preserved (only `highlights` is moved; then orders are reassigned 0..n-1 in the new sequence).

1. In `src/core/candidate.py`, inside `normalize_resume_structure`, **after** the per-section loop that builds `out["sections"]` and **before** the final `if not out["sections"]` empty check / `return out`, add order coercion:

   ```python
   secs = out["sections"]
   if "highlights" in secs and "experience" in secs:
       ordered_ids = [
           sid
           for sid, _spec in sorted(
               secs.items(),
               key=lambda kv: (
                   kv[1]["order"] if isinstance(kv[1].get("order"), int) else 0,
                   kv[0],
               ),
           )
       ]
       ordered_ids = [sid for sid in ordered_ids if sid != "highlights"]
       exp_i = ordered_ids.index("experience")
       ordered_ids.insert(exp_i, "highlights")
       for i, sid in enumerate(ordered_ids):
           secs[sid]["order"] = i
   ```

   Use this algorithm literally (remove `highlights` from the sorted id list, insert it at the index of `experience`, then rewrite contiguous `order` ints). Do not invent a different adjacency rule (e.g. `experience.order - 1` without reshuffling).

2. Do **not** mint a missing `highlights` row inside `normalize_resume_structure`. Missing required ids continue to raise at the existing `missing = [...]` check (AC1). Minting for candidates with no / invalid structure remains `resolve_resume_structure` → `default_resume_structure()` (unchanged call sites).

3. Do **not** change `resolve_resume_structure`, `default_resume_structure`, `hydrate_resume_structure_from_base_resume`, `prepare_resume_structure_sections_for_save`, or UI/API modules. GET `/resume_structure` already sorts by `order` and exposes `required_ids` from config — after Stage 1 those lists include `highlights` automatically.

4. Do **not** edit builder emit, hop schemas, or agent_task prompts.

⚠️ **Decision:** Coerce on every successful normalize (including save and resolve-when-valid), not only on GET. That is what makes AC3 true without an operator reorder and without a separate UI rule.

⚠️ **Decision:** Reassign all section orders to `0..n-1` after moving Highlights. Tie-breaking and gaps from operator edits are normalized away; adjacency is the product rule, not preserving sparse order ints.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric.v1
**Ticket:** AST-1332
**Overall:** APPROVED
**Publish ref:** `sub/AST-1326/AST-1332-required-highlights-catalog-and-default-order` @ `17530d63a5a31f94f6a615bbdaeb2c7807437bc4`

## Traceability
AC1→S1+existing normalize checks; AC2→S1; AC3→S2 (`normalize_resume_structure` coerce on resolve/save); AC4→S1 default `bullet_list` + explicit builder out-of-scope (parent AC4–5 → AST-1333).

## Findings

### acceptable — No explicit Self-assessment line
- **Location:** `## Estimate` (end of plan)
- **Finding:** Peer artifacts plans usually include `**Self-assessment:**` scope/conf/risk; this plan only has Estimate confirm.
- **Recommendation:** Optional hygiene — add `Single-Component / high conf / low risk` before build; not blocking given explicit ⚠️ Decision blocks and two-file footprint.

**In-session (R1–R4, not printed):** 56 statutes considered (18 universal + 38 scoped via `src/**`); 8 excluded (docs/ui/data/scripts paths). Cited statutes/patterns conform: `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`, `astral.layers.import-direction`, `astral.standards.in-scope-only`, `pattern.config.config-block`, `pattern.layers.import-discipline`. Orchestration universals conform. No `fix-now` / `discuss` statute violations. Plan Discuss round count: 0.

context_tokens≈42000

[plan-rubric] PROCEED (Commit: 17530d63a5a31f94f6a615bbdaeb2c7807437bc4) config coerce highlights order

## Review

- **Publish ref:** `sub/AST-1326/AST-1332-required-highlights-catalog-and-default-order`
- **Tip:** `1bf6c7c9f34bd8c89389573c0b154cf35e7bb189`
- **Stages:** Stage 1 config catalog + default order; Stage 2 normalize Highlights↔Experience coerce
