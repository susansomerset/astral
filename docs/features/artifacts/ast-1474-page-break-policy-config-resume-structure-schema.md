# AST-1474 — Page-break policy config and resume_structure schema

**Linear:** [AST-1474](https://linear.app/astralcareermatch/issue/AST-1474)
**Parent:** [AST-1462](https://linear.app/astralcareermatch/issue/AST-1462) — Create and position page break
**Publish ref:** `sub/AST-1462/AST-1474-page-break-policy-config-resume-structure-schema`

Adds config-owned page-break policy tokens with keep-block-together as the default for every known (and extra) structure section; extends `normalize_resume_structure` / `RESUME_STRUCTURE_DEFAULT` / GET `/resume_structure` catalog so sections persist and expose `page_break_policy`. Does **not** emit print CSS (AST-1475) or build React controls (AST-1476).

## Scope gate

Ticket **## Scope** covers only:

- `src/utils/config.py` — allowed tokens, keep-together default map, catalog literals
- `src/core/candidate.py` — validate / normalize / default the new field
- `src/ui/api/api_candidate.py` — catalog payload for policies

Every file and change kind below matches that Scope. Out of scope: `builder.py`, React, `BUILD_CONFIG["supported_sections"][*]["page_break_policy"]` rewrites, tests/bible.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `RESUME_STRUCTURE_PAGE_BREAK_*` tokens, labels, default, per-known-id default map; set `page_break_policy` on every `RESUME_STRUCTURE_DEFAULT` section | utils |
| `src/core/candidate.py` | Import new config names; coerce/validate `page_break_policy` in `normalize_resume_structure`; default on hydrate/ingest append helpers | core |
| `src/ui/api/api_candidate.py` | Import new config names; add policy fields to GET catalog; include `page_break_policy` on each `all_sections` row | ui |

## Decisions (binding)

⚠️ **Decision:** Field name is `page_break_policy` (same key already used under `BUILD_CONFIG["supported_sections"]`) so structure rows, catalog, and later builder emit share one name.

⚠️ **Decision:** Operator-allowed token set is exactly three strings (parent Functional scope: flow / new page before / keep together):

| Token | Meaning |
|-------|---------|
| `normal` | Flow uninterrupted across pages |
| `page_break_before` | Force a new printed page before this section |
| `avoid_split` | Keep this section block together |

Default for **every** section (known + extra) when absent or when writing `RESUME_STRUCTURE_DEFAULT` is **`avoid_split`**. Do **not** copy the mixed `BUILD_CONFIG["supported_sections"]` policies into structure defaults (those still include `keep_with_next` / `normal` and are not this epic’s operator contract).

⚠️ **Decision:** Do **not** add `keep_with_next` to the structure allowed set. It remains a `BUILD_CONFIG` literal only. Structure persistence / catalog / normalize accept only the three tokens above. AST-1475 maps those three to print CSS; it does not need `keep_with_next` on structure rows.

⚠️ **Decision:** Do **not** edit `BUILD_CONFIG["supported_sections"][*]["page_break_policy"]` in this ticket. Legacy builder hard-code `#prior-experience { page-break-before: always }` and BUILD_CONFIG emit hints are AST-1475.

⚠️ **Decision:** Catalog exposes both a flat token list and human labels (config-owned) so AST-1476 does not hardcode enum strings or display copy (`astral.standards.no-hardcoded-sets` / `astral.layers.ui-config-driven-business-logic`).

## Stage 1: Config catalog literals

**Done when:** `RESUME_STRUCTURE_*` page-break constants exist next to the existing structure catalog in `config.py`; every section in `RESUME_STRUCTURE_DEFAULT["sections"]` carries `"page_break_policy": "avoid_split"`; no product callers required yet.

1. In `src/utils/config.py`, immediately after `RESUME_STRUCTURE_BODY_FORMATS` (before `RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID` is fine; keep the page-break block contiguous with other `RESUME_STRUCTURE_*` names), add:

```python
RESUME_STRUCTURE_PAGE_BREAK_POLICIES = (
    "normal",
    "page_break_before",
    "avoid_split",
)
RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT = "avoid_split"
RESUME_STRUCTURE_PAGE_BREAK_POLICY_LABELS = {
    "normal": "Flow uninterrupted",
    "page_break_before": "New page before",
    "avoid_split": "Keep block together",
}
```

2. After `RESUME_STRUCTURE_KNOWN_SECTION_IDS` is defined, add the keep-together default map (every known id → default):

```python
RESUME_STRUCTURE_PAGE_BREAK_DEFAULT_BY_ID = {
    sid: RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT
    for sid in RESUME_STRUCTURE_KNOWN_SECTION_IDS
}
```

3. In `RESUME_STRUCTURE_DEFAULT["sections"]`, add `"page_break_policy": RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT` to **every** section dict (contact + body + historical optional — all eleven rows).

4. Do **not** change `BUILD_CONFIG`, `DATA_SHAPES`, craft schemas, or any other config family.

## Stage 2: Normalize / default in candidate.py

**Done when:** `normalize_resume_structure` always writes a validated `page_break_policy` on each section row; missing/blank → default; unknown token → `ValueError`; hydrate and legacy-ingest append helpers stamp the default so GET never returns a section without the field.

1. In `src/core/candidate.py` imports from `src.utils.config`, add:
   - `RESUME_STRUCTURE_PAGE_BREAK_POLICIES`
   - `RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT`
   - (import `RESUME_STRUCTURE_PAGE_BREAK_DEFAULT_BY_ID` only if a step below uses it; prefer the single default constant for coerce)

2. In `normalize_resume_structure`, after `format` handling and before `out["sections"][sid] = row`, resolve policy:

   - Read `raw_policy = spec.get("page_break_policy")`.
   - If `raw_policy` is `None` or a blank string (after strip when `str`): set `policy = RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT`.
   - Else require `isinstance(raw_policy, str)` and `raw_policy in RESUME_STRUCTURE_PAGE_BREAK_POLICIES`; otherwise raise `ValueError` with a message naming the section id and listing `list(RESUME_STRUCTURE_PAGE_BREAK_POLICIES)` (same style as the format error).
   - Set `row["page_break_policy"] = policy`.
   - Apply for **all** section ids including contact and extras (no contact skip).

3. In `ingest_legacy_label_content_base_resume` → `_append_missing_section`, when building the new section dict, include `"page_break_policy": RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT` alongside `format`.

4. In `hydrate_resume_structure_from_base_resume` → `_append_missing`, when building `row`, include `"page_break_policy": RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT`.

5. Optional harden (same stage, same file): in hydrate, after `_fix_body_format` (or inside `_ensure_sid` when the section already exists), if `spec.get("page_break_policy")` is missing/blank/not in the allowed tuple, set `spec["page_break_policy"] = RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT` so read-only hydrate of pre-epic blobs shows keep-together without requiring Save. Do **not** call `normalize_resume_structure` from hydrate (hydrate stays non-raising for display).

6. Do **not** change `prepare_resume_structure_sections_for_save` beyond what already `dict(spec)`-copies — Save continues to pass the field through; normalize on the PUT path remains the validator.

7. Do **not** edit `builder.py`, tracker emit, or React.

## Stage 3: GET catalog + all_sections payload

**Done when:** `GET /api/candidates/<id>/resume_structure` returns catalog page-break fields and each `all_sections[]` row includes the section’s resolved `page_break_policy` string.

1. In `src/ui/api/api_candidate.py`, import:
   - `RESUME_STRUCTURE_PAGE_BREAK_POLICIES`
   - `RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT`
   - `RESUME_STRUCTURE_PAGE_BREAK_POLICY_LABELS`
   - `RESUME_STRUCTURE_PAGE_BREAK_DEFAULT_BY_ID`

2. In `get_candidate_resume_structure`, extend the `catalog` dict with exactly:

```python
"page_break_policies": list(RESUME_STRUCTURE_PAGE_BREAK_POLICIES),
"page_break_policy_labels": dict(RESUME_STRUCTURE_PAGE_BREAK_POLICY_LABELS),
"page_break_policy_default": RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT,
"page_break_policy_defaults": dict(RESUME_STRUCTURE_PAGE_BREAK_DEFAULT_BY_ID),
```

3. In the `all_sections.append({...})` loop, add:

```python
"page_break_policy": (
    spec["page_break_policy"]
    if isinstance(spec.get("page_break_policy"), str)
    and spec["page_break_policy"] in RESUME_STRUCTURE_PAGE_BREAK_POLICIES
    else RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT
),
```

4. Do **not** add new routes. Do **not** change PUT merge logic beyond what already runs `normalize_resume_structure` on `arts["resume_structure"]` (that path already persists whatever normalize writes, including the new field).

## Out of scope (siblings)

| Sibling | Owns |
|---------|------|
| AST-1475 (Hedy) | `builder.py` print `@media` from structure policies; `.role` keep-together; gate `#prior-experience` always-break |
| AST-1476 (Katherine) | ArtifactEditor / ResumeStructureEditor / JAR dropdown + Save UX |

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1474
**Overall:** APPROVED
**Publish ref:** `sub/AST-1462/AST-1474-page-break-policy-config-resume-structure-schema` @ `56eecd88`

## Traceability
AC1→Stages 1–2 (config `avoid_split` on all `RESUME_STRUCTURE_DEFAULT` rows + normalize coerce); AC2→Stages 2–3 (persist via normalize on PUT + GET `catalog`/`all_sections`); parent AC2/3/5/6 and end-to-end print CSS→siblings N/A for this child's Scope.

## Findings

### discuss — Missing `## Self-assessment`
- **Location:** plan doc (after `## Estimate`)
- **Finding:** No self-assessment / confidence block; other artifact plans carry one.
- **Recommendation:** Optional add before build — low risk here because stages, scope gate, and binding Decisions are already explicit.

### discuss — Child AC1 names print CSS
- **Location:** ticket AC1 vs plan Out of scope
- **Finding:** AC1 text says “in print CSS”; this slice delivers schema/defaults only; print emit is AST-1475.
- **Recommendation:** Ada should treat AC1 as satisfied at this layer when defaults persist `avoid_split` everywhere including `prior_experience`; full AC1 UAT waits on Hedy.

### acceptable — Hydrate soft-default vs normalize strict-validate
- **Location:** Stage 2 step 5
- **Finding:** Hydrate may silently stamp default policy for legacy blobs; PUT/Save still validates via `normalize_resume_structure`.
- **Recommendation:** Matches stated intent for read-only display of pre-epic data.

context_tokens≈18500

## Review

- **Publish ref:** `sub/AST-1462/AST-1474-page-break-policy-config-resume-structure-schema`
- **Tip:** `7c53225a`
- **Files:** `src/utils/config.py`, `src/core/candidate.py`, `src/ui/api/api_candidate.py`
