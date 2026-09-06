# Token catalog source_type typing

**Linear:** [AST-1596](https://linear.app/astralcareermatch/issue/AST-1596/token-catalog-source-type-typing-split-token-config-add-source-type)
**Parent:** [AST-1578](https://linear.app/astralcareermatch/issue/AST-1578/split-token-config-add-source-type-field-data-field-artifact-special) — Split token config: add source-type field
**Publish ref:** `sub/AST-1578/AST-1596-token-catalog-source-type-typing`

Land required `source_type` (`data_field` / `artifact` / `special_case`) on every `TOKEN_SOURCES` row, `artifact_key` on the sole artifact token (`BASE_RESUME`), a config constant for allowed types, startup asserts that reject half-typed catalogs, and thin read-only by-type / artifact-key getters. Resolve behavior, prompt parsing, claim/pin, and `ARTIFACT_CONFIG` membership stay unchanged.

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/utils/config.py` — `source_type` / `artifact_key` on `TOKEN_SOURCES`; allowed-type constant; startup asserts; optional thin getters

Every row in **Files Changed** is that one path. Technical kinds covered: annotate registry values, add allowed-type constant, add import-time asserts, add thin filter/map helpers. No other files, no resolve-path edits, no new `ARTIFACT_CONFIG` keys.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `TOKEN_SOURCE_TYPES` constant; `source_type` (+ `artifact_key` on `BASE_RESUME`) on every `TOKEN_SOURCES` entry; section/docstring typing contract; startup asserts; `get_tokens_by_source_type` + `get_artifact_key_for_token` | utils |

**Out of this ticket (do not touch):** `resolve_tokens` / consumer rewires; prompt-parse / claim / pin siblings; `ARTIFACT_CONFIG` key set; React/UI; `src/core/**`; `src/data/**`; `tests/` / `docs/test-bible/**` (Betty owns tests).

## Stage 1: Typed catalog + asserts (atomic)

**Done when:** `import src.utils.config` succeeds; every `TOKEN_SOURCES` entry has a valid `source_type`; `BASE_RESUME` is the only `artifact` entry and carries `artifact_key == "candidate.artifacts.base_resume"` present in `ARTIFACT_CONFIG`; missing/invalid typing fails at import. Existing `source` / `path` / `serialize` / `resolver` / `owner_task_key` / `field` keys are unchanged. `get_tokens()` still returns the same sorted name list.

1. In `src/utils/config.py` module docstring **Config sections:** list, add this line immediately after the existing `ARTIFACT_CONFIG` line:

```
  TOKEN_SOURCES — prompt {$TOKEN} registry with required source_type (data_field / artifact / special_case); artifact rows carry artifact_key into ARTIFACT_CONFIG (AST-1596 / AST-1578)
```

2. Immediately **before** the existing `# TOKEN_SOURCES: authoritative registry…` section comment (currently ~line 6291), insert the allowed-type constant (same style as `TASK_TYPES`):

```python
# AST-1596: closed set of TOKEN_SOURCES["source_type"] values (not redefined in callers).
TOKEN_SOURCE_TYPES = frozenset({"data_field", "artifact", "special_case"})
```

3. Replace the section comment above `TOKEN_SOURCES = {` with:

```python
# ---------------------------------------------------------------------------
# TOKEN_SOURCES: authoritative registry of tokens available in prompt content.
# Prompt authors use {$TOKEN_NAME} syntax; resolve_tokens() replaces them at runtime.
# Adding a new token = adding one entry here, no code change needed.
# AST-1596 / AST-1578: every entry requires source_type in TOKEN_SOURCE_TYPES.
#   data_field  — live blob / overlay field (no versioning / pin)
#   artifact    — ARTIFACT_CONFIG key via artifact_key (pinnable later; resolve path unchanged here)
#   special_case — non-data (chain / pronoun / rubric / config / output_type / job)
# TOKEN_SOURCES and ARTIFACT_CONFIG stay separate registries; artifact tokens reference keys.
# ---------------------------------------------------------------------------
```

4. Add `"source_type": "<…>"` to **every** existing `TOKEN_SOURCES` value dict. Keep all other keys byte-identical. Classification (exact — do not improvise):

**`source_type: "data_field"`** — every `source: "candidate"` row **except** `BASE_RESUME`:

| Token | Keep existing fields |
|-------|----------------------|
| `FIRST_NAME` | `source`, `path` |
| `LAST_NAME` | `source`, `path` |
| `FULL_NAME` | `source`, `path` |
| `CONTACT_EMAIL` | `source`, `path` |
| `REPLY_EMAIL` | `source`, `path` |
| `PHONE` | `source`, `path` |
| `LOCATION` | `source`, `path` |
| `GITHUB` | `source`, `path` |
| `LINKEDIN_URL` | `source`, `path` |
| `STARTING_RESUME_TEXT` | `source`, `path` |
| `LINKEDIN_PROFILE_TEXT` | `source`, `path` |
| `SAMPLE_COVER_TEXT` | `source`, `path` |
| `STRENGTHS` | `source`, `path` |
| `PRIORITIES` | `source`, `path` |
| `DEAL_BREAKERS` | `source`, `path` |
| `BACKSTORY` | `source`, `path` |
| `IDEAL_DAY` | `source`, `path` |
| `WRITING_PREFERENCES` | `source`, `path` |
| `TITLE_PATTERNS` | `source`, `path` |
| `REASON_CODES` | `source`, `path` |
| `COVER_LETTER_SIGNATURE` | `source`, `path` |
| `BIO_SUMMARY` | `source`, `path` |
| `COMPANY_SEARCH_TERMS` | `source`, `path` |

⚠️ **Decision:** `COMPANY_SEARCH_TERMS` stays `data_field` even though its path string contains `artifacts.` — it is **not** in `ARTIFACT_CONFIG` and parent Technical scope classifies all non–`BASE_RESUME` candidate path tokens as `data_field`. Do not type it `artifact`.

**`source_type: "artifact"`** — only:

```python
"BASE_RESUME": {
    "source": "candidate",
    "path": "artifacts.base_resume",
    "serialize": "resume_sections_json",
    "source_type": "artifact",
    "artifact_key": "candidate.artifacts.base_resume",
},
```

**`source_type: "special_case"`** — all remaining rows:

| Token | Existing `source` (unchanged) |
|-------|-------------------------------|
| `THEY`, `THEIR`, `THEIRS`, `THEM`, `THEMSELF` | `pronoun` |
| `RUBRIC_VECTORS`, `GET_RUBRIC`, `DO_RUBRIC`, `LIKE_RUBRIC`, `JD_RUBRIC`, `PREFILTER_RUBRIC` | `rubric` (+ `owner_task_key` where already present) |
| `RESPONSE_SCHEMA` | `config` |
| `OUTPUT_INSTRUCTIONS` | `output_type` |
| `CALLER_RESPONSE`, `CALLER_SYSTEM`, `CALLER_CACHE_A`, `CALLER_CACHE_B`, `CALLER_CACHE_C`, `CALLER_CACHE_D`, `SELECTED_AGENT`, `JOB_LIST_VISIBLE` | `chain` |
| `VISIBLE_JD`, `ANALYSIS_JD`, `ANALYSIS_DO`, `ANALYSIS_GET`, `ANALYSIS_LIKE`, `RESUME_SECTION_CATALOG` | `job` |

Do **not** add new token names. Do **not** remove keys. Do **not** change `JOB_TOKEN_CONFIG`.

5. Immediately **after** the closing `}` of `TOKEN_SOURCES` (before `JOB_TOKEN_CONFIG`), add startup asserts:

```python
# AST-1596: reject half-typed / invalid TOKEN_SOURCES catalogs at import.
for _token_name, _spec in TOKEN_SOURCES.items():
    assert isinstance(_spec, dict), _token_name
    assert "source_type" in _spec, f"TOKEN_SOURCES[{_token_name!r}] missing source_type"
    assert _spec["source_type"] in TOKEN_SOURCE_TYPES, (
        f"TOKEN_SOURCES[{_token_name!r}] invalid source_type={_spec['source_type']!r}"
    )
    if _spec["source_type"] == "artifact":
        assert "artifact_key" in _spec, (
            f"TOKEN_SOURCES[{_token_name!r}] artifact missing artifact_key"
        )
        assert _spec["artifact_key"] in ARTIFACT_CONFIG, (
            f"TOKEN_SOURCES[{_token_name!r}] artifact_key "
            f"{_spec['artifact_key']!r} not in ARTIFACT_CONFIG"
        )
    else:
        assert "artifact_key" not in _spec, (
            f"TOKEN_SOURCES[{_token_name!r}] non-artifact must not carry artifact_key"
        )

assert TOKEN_SOURCES["BASE_RESUME"]["source_type"] == "artifact"
assert TOKEN_SOURCES["BASE_RESUME"]["artifact_key"] == "candidate.artifacts.base_resume"
_artifact_tokens = {
    name for name, spec in TOKEN_SOURCES.items() if spec["source_type"] == "artifact"
}
assert _artifact_tokens == {"BASE_RESUME"}
```

⚠️ **Decision:** Asserts live immediately after `TOKEN_SOURCES` (not deferred to a helper module) so import fails before any caller reads an untyped registry — matches sibling `ARTIFACT_CONFIG` assert placement and parent AC4.

6. Do **not** edit `resolve_tokens`, `_walk_dot_path`, `get_tokens`, `get_manage_tasks_chain_tokens`, or `get_manage_agents_tokens` in this stage.

## Stage 2: Thin by-type / artifact-key getters

**Done when:** Callers can list token names by `source_type` and map an artifact token name → `artifact_key` via public helpers in `config.py`; unknown / non-artifact names fail fast without I/O; existing `get_tokens` / chain / manage-agents helpers remain unchanged.

1. Immediately **after** `get_manage_agents_tokens` (before `CALLER_HOP_TOKEN_NAMES`), add:

```python
def get_tokens_by_source_type(source_type: str) -> list:
    """Sorted TOKEN_SOURCES names whose source_type matches ``source_type``.

    ``source_type`` must be a member of TOKEN_SOURCE_TYPES; raises ValueError otherwise.
    """
    if source_type not in TOKEN_SOURCE_TYPES:
        raise ValueError(f"invalid source_type: {source_type!r}")
    return sorted(
        name
        for name, spec in TOKEN_SOURCES.items()
        if spec.get("source_type") == source_type
    )


def get_artifact_key_for_token(token_name: str) -> str:
    """Return ARTIFACT_CONFIG key for an artifact-typed TOKEN_SOURCES name.

    Raises ValueError if the name is missing, not artifact-typed, or lacks artifact_key.
    """
    spec = TOKEN_SOURCES.get(token_name)
    if spec is None:
        raise ValueError(f"unknown token: {token_name!r}")
    if spec.get("source_type") != "artifact":
        raise ValueError(f"token is not artifact-typed: {token_name!r}")
    key = spec.get("artifact_key")
    if not isinstance(key, str) or not key:
        raise ValueError(f"artifact token missing artifact_key: {token_name!r}")
    return key
```

⚠️ **Decision:** Ship the optional thin getters in this ticket (parent Technical scope + child Notes). They are read-only, no prompt scanning, no DB/network — safe for siblings that need by-type filters without scraping `TOKEN_SOURCES` dict shape.

2. Do **not** wire these helpers into `resolve_tokens`, admin APIs, or core consumers in this ticket.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1596
**Overall:** APPROVED
**Publish ref:** `sub/AST-1578/AST-1596-token-catalog-source-type-typing` @ `bd45f1d631c86198621de8e117964d6ae1f72f3b`

## Traceability
AC1–AC5 → Stage 1 (typed catalog, `TOKEN_SOURCE_TYPES`, import-time asserts, `BASE_RESUME` artifact linkage); AC6–AC7 → Stage 1 constraints (no `resolve_tokens` / `get_tokens` edits; admin name lists unchanged via existing `get_tokens()`).

## Findings

### acceptable
- **Location:** Parent Architectural definition — `patt.artifact.manage-catalog`, `patt.artifact.read-current`
- **Finding:** Parent cites draft artifact patterns under `canon/directives/draft/`; plan mirrors parent citations without inventing new pattern shapes.
- **Recommendation:** No plan change; draft status is parent-level, not a child-scope defect.

### acceptable
- **Location:** Plan structure — no `## Self-Assessment`
- **Finding:** `## Estimate` confirm line is present; classification tables and explicit out-of-scope boundaries make complexity obvious without a separate self-assessment block.
- **Recommendation:** Optional polish only; not blocking.

## R6 checklist (summary)
- Definition fidelity: conforms — single-file `src/utils/config.py` slice matches child Scope and parent Technical scope; all 51 live `TOKEN_SOURCES` rows classified (23 `data_field`, 1 `artifact`, 27 `special_case`); `COMPANY_SEARCH_TERMS` decision documented.
- Layer / config / placement: conforms — utils-only; `TOKEN_SOURCE_TYPES` constant; no magic inline enums in callers; helpers placed after existing public getters per `public-then-helpers`.
- Pattern compliance: conforms — `pattern.config.config-block` shape (extend registry block + constant + asserts); artifact token references registered `ARTIFACT_CONFIG` key only (`candidate.artifacts.base_resume`).
- Scope / DRY: conforms — explicit exclusions for resolve, claim/pin siblings, `ARTIFACT_CONFIG` membership, tests; no sibling creep.

**Considered:** (statute verdicts in-session per slim R7 — universal set + scoped `astral.config.*` / `astral.standards.*` / `astral.layers.*` touching `utils` + `src/**`; all `conforms`; orchestration/UI/batch/agent statutes excluded by layer/path predicates)

context_tokens≈34000

## Review (build stub)

**Built:** `origin/sub/AST-1578/AST-1596-token-catalog-source-type-typing` @ `edceb490d8f4a1a8436259241b1d99fe9df668d6`.

**Stages delivered:**
- Stage 1: `TOKEN_SOURCE_TYPES` + typed `TOKEN_SOURCES` + import asserts — `c0ee4de6`.
- Stage 2: `get_tokens_by_source_type` + `get_artifact_key_for_token` — `edceb490`.

**Betty:** at **Code Complete** — cover import asserts (half-typed / bad artifact_key), `BASE_RESUME` sole artifact linkage, by-type filter + artifact-key getter fail-fast; confirm `get_tokens()` names unchanged and `resolve_tokens` untouched.
