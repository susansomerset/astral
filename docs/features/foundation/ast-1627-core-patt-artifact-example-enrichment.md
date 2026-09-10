# Core patt.artifact.* example enrichment

**Linear:** [AST-1627](https://linear.app/astralcareermatch/issue/AST-1627/core-pattartifact-example-enrichment-update-pattartifacts-directives)
**Parent:** [AST-1626](https://linear.app/astralcareermatch/issue/AST-1626/update-pattartifacts-directives-with-code-examples) — update patt.artifacts.* directives with code examples
**Publish ref:** `sub/AST-1626/AST-1627-core-patt-artifact-example-enrichment`

Add harvested fenced code examples to the five singular draft patterns (`manage-catalog`, `write-operative`, `read-current`, `read-operative`, `no-coat-check`) so agents citing those drafts copy live invoke shapes from `origin/dev` instead of inventing helpers. Docs-only; does **not** rename or enrich `patt.artifacts.ui-consistency` / `patt.artifacts.traceability` (sibling child); does **not** promote drafts to `active/`; does **not** change `src/` or `tests/`.

## UAT fitness

- **AC restored:** Parent AST-1626 AC1–AC5 for the five core drafts this child owns: (1) every kept in-scope draft has ≥1 fenced code block under Examples / Implementation examples; (2) every example call names a symbol that exists on `origin/dev` under `src/`; (3) `git diff origin/dev -- src/ tests/` empty on this publish ref; (4) Abstract / Arc / Applications / Exceptions headings remain; (5) each write/read draft’s examples include a one-line “do not” adjacent to the positive snippet. (Parent AC6 singular-rename of ui-consistency / traceability is **sibling** scope — not this ticket.)
- **Correct outcome:** An engineer citing any of the five `patt.artifact.*` drafts can copy a correct invoke pattern (catalog lookup, retire+insert write, current read, pin→body operative read, pre-load vs coat-check ban) without inventing helpers or reopening blob/coat-check paths.
- **Sibling check:** Sibling #2 (rename plural `patt.artifacts.ui-consistency` / `patt.artifacts.traceability` + their examples + cite sweep) stays untouched — verify by leaving those two plural draft paths unmodified and by not editing any in-repo plural cites. Parent purpose “teach the how” for the five already-singular drafts still holds after this child alone.
- **Not sufficient:** Removing confusion in prose alone, or adding empty / commentary-only fences with no callable `src/` symbols, is **not** done.
- **Wrong fix rejected:** Inventing new public helpers or alternate names in the drafts, promoting drafts to `active/`, or touching product/runtime code to “make examples match” — examples must harvest existing live paths; law sections stay authoritative.

## Explicit scope gate

Ticket **## Scope** names exactly these five draft files (Component + Technical):

- `canon/directives/draft/patt.artifact.manage-catalog.md` — **modified** — Examples for catalog register/lookup via live config accessors; rejection of unknown keys; no key inventory dump beyond the snippet.
- `canon/directives/draft/patt.artifact.write-operative.md` — **modified** — Examples for `save_artifact` retire+insert + entity-owned operative save; return uuid/pin called out in snippet comments; one-line “do not” (no in-place UPDATE).
- `canon/directives/draft/patt.artifact.read-current.md` — **modified** — Examples for `get_current_artifact` + entity-owned current-read wrapper used by GET hydrate / editor load; one-line “do not” (no `*_data` blob read for catalog keys).
- `canon/directives/draft/patt.artifact.read-operative.md` — **modified** — Examples for by-uuid `get_artifact` + pilot pin→body helper; one-line “do not” (no blob dotted-path / coat-check).
- `canon/directives/draft/patt.artifact.no-coat-check.md` — **modified** — Forbidden mid-turn blob/coat-check vs required pre-load + read-current/read-operative sequence; no new ban surfaces.

Every row in **Files Changed** is one of those paths (plus this plan doc). Every Stage step is “add Examples / worked snippets” of the kind Scope describes — not law rewrites, not product code, not sibling rename files.

**Out of this ticket (do not touch):** `canon/directives/draft/patt.artifacts.ui-consistency.md`; `canon/directives/draft/patt.artifacts.traceability.md`; any singular rename or cite sweep for those two; `src/**`; `tests/**`; `docs/test-bible/**`; draft→`active/` moves; new `ARTIFACT_CONFIG` keys; inventing helpers not present on `origin/dev`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `canon/directives/draft/patt.artifact.manage-catalog.md` | Add `# Examples` with live `ARTIFACT_CONFIG` lookup + unknown-key rejection | canon/draft |
| `canon/directives/draft/patt.artifact.write-operative.md` | Add `# Examples` with `database.save_artifact` + `save_candidate_data` str-path; do-not UPDATE | canon/draft |
| `canon/directives/draft/patt.artifact.read-current.md` | Add `# Examples` with `database.get_current_artifact` + `get_candidate_current` (+ hydrate pointer); do-not blob | canon/draft |
| `canon/directives/draft/patt.artifact.read-operative.md` | Add `# Examples` with `database.get_artifact` + `get_operative_base_resume`; do-not blob/coat-check | canon/draft |
| `canon/directives/draft/patt.artifact.no-coat-check.md` | Add `# Examples` contrasting forbidden coat-check call vs required artifact read | canon/draft |

## Stage 1: `manage-catalog` examples

**Done when:** `patt.artifact.manage-catalog.md` has a new `# Examples` section (after `# Implementation`, before `# OPEN QUESTIONS / DECISIONS`) with ≥1 fenced Python block that resolves a registered `ARTIFACT_CONFIG` key and shows unknown-key rejection via `.get` / `ValueError`. Abstract / Arc / Applications / Exceptions / Implementation headings and bullets are unchanged. No product files touched.

1. Open `canon/directives/draft/patt.artifact.manage-catalog.md`. Confirm `# Implementation` and `# OPEN QUESTIONS / DECISIONS` still exist; do not edit their bodies.
2. Insert a new top-level section `# Examples` between `# Implementation` and `# OPEN QUESTIONS / DECISIONS`.
3. Under `# Examples`, add a short prose lead (1–2 sentences): catalog SoT is `ARTIFACT_CONFIG` in `src/utils/config.py`; callers import that dict — do not invent a wrapper module or hardcode key tuples in consumer prose.
4. Add a fenced `python` block that shows **registered lookup** using the live pilot key `candidate.artifacts.base_resume` and reading fields that exist on that entry today (`entity_type`, `candidate_scoped`, `body_shape`, `ingestion_owner`). Snippet shape (symbols must match tree):

```python
from src.utils.config import ARTIFACT_CONFIG

key = "candidate.artifacts.base_resume"
entry = ARTIFACT_CONFIG[key]  # KeyError if somehow absent from the closed set
# entry["entity_type"], entry["candidate_scoped"], entry["body_shape"], entry["ingestion_owner"]
```

5. In the same section, add a second fenced block (or the same block with a clearly separated second half) showing **unknown-key rejection** the way entity wrappers do it live (`ARTIFACT_CONFIG.get` → `ValueError`), e.g. the pattern in `save_candidate_data` / `get_candidate_current`:

```python
entry = ARTIFACT_CONFIG.get(artifact_key)
if entry is None:
    raise ValueError(f"unknown catalog key: {artifact_key!r}")
```

6. Adjacent one-line **do not** (prose or comment in the fence): do not invent catalog keys in consumer code or dump the full key inventory in examples beyond what the snippet needs.
7. Do **not** list every current `ARTIFACT_CONFIG` key in prose. Do **not** change frontmatter `id` / `scope` / `point`.

## Stage 2: `write-operative` examples

**Done when:** `patt.artifact.write-operative.md` has `# Examples` with ≥1 fenced block covering data-layer `database.save_artifact` (retire+insert, returns uuid) and entity-owned `save_candidate_data(candidate_id, artifact_key, blob)` for the pilot key; a greppable one-line “do not” rules out in-place artifact body UPDATE. Law headings intact.

1. Open `canon/directives/draft/patt.artifact.write-operative.md`. Leave Abstract / Arc / Applications / Exceptions / Implementation bodies intact.
2. Insert `# Examples` between `# Implementation` and `# OPEN QUESTIONS / DECISIONS`.
3. Add a fenced block for the **data-layer** call. Harvest signature from `src/data/database.py` `save_artifact(entity_type, entity_id, artifact_type, artifact_data, source_artifact_ids=None, *, candidate_id=None) -> str`. Snippet must comment that prior `current=1` rows for the natural key are set to `current=0`, then a new UUID row is inserted `current=1`, and the **returned str is the new `artifact_uuid` / pin**.

```python
# data layer — blind retire-by-key + insert; returns new artifact_uuid
new_uuid = database.save_artifact(
    entity_type,   # e.g. "candidate"
    entity_id,     # candidate_id when entity is candidate
    artifact_type, # leaf, e.g. "base_resume"
    body,          # validated artifact_data
)
# pin new_uuid on grades / analysis when explainability applies
```

4. Add a fenced block for the **entity-owned** operative path in `src/core/candidate.py`: `save_candidate_data(candidate_id, "candidate.artifacts.base_resume", body) -> Optional[str]` — validates via `ARTIFACT_CONFIG` + `BUILD_CONFIG["artifact_shapes"]`, then delegates to `database.save_artifact`. Comment the return as the pin uuid.
5. Optional one-liner pointer (prose, not a new API): job-scoped operative writes use `tracker.save_job_artifact(astral_job_id, artifact_key, blob, …)` the same way — still live on `origin/dev`; do not expand into job/traceability examples (sibling).
6. Adjacent **do not:** never `UPDATE artifact SET artifact_data = …` (or any in-place body UPDATE) for operative writes; always retire+insert via `save_artifact`.
7. Do **not** invent alternate save helpers. Do **not** change Implementation bullets that already name `save_artifact`.

## Stage 3: `read-current` examples

**Done when:** `patt.artifact.read-current.md` has `# Examples` showing `database.get_current_artifact` and `get_candidate_current`, plus a call-site pointer to GET hydrate (`hydrate_operative_base_resume_for_response`); greppable “do not” against reading catalog content from `*_data` blobs. Law headings intact.

1. Open `canon/directives/draft/patt.artifact.read-current.md`. Leave law sections intact.
2. Insert `# Examples` between `# Implementation` and `# OPEN QUESTIONS / DECISIONS`.
3. Fenced block — **data layer** (`src/data/database.py`):

```python
row = database.get_current_artifact(entity_type, entity_id, artifact_type)
# row is None on miss; else row["artifact_data"] is the deserialized body
```

4. Fenced block — **entity wrapper** (`src/core/candidate.py` `get_candidate_current`): resolves `ARTIFACT_CONFIG`, requires `candidate_scoped`, leaf `artifact_type` from the key, delegates to `get_current_artifact`, returns `artifact_data` or `None`. Use pilot key `candidate.artifacts.base_resume` in the snippet.
5. Prose pointer (1 sentence): API GET hydrate for the pilot overlays via `hydrate_operative_base_resume_for_response(candidate_id, cd)` in `src/ui/api/api_candidate.py` / `src/core/candidate.py` — editors open on that current body, not a stale blob copy.
6. Optional prose pointer: job current-read twin is `tracker.get_job_current(astral_job_id, artifact_key)` — mention only; no job-editor examples.
7. Adjacent **do not:** do not hydrate catalog keys from `candidate_data` / `job_data` blob dotted paths for edit or live display.
8. Do **not** invent a new wrapper name. Do **not** remove the existing Implementation bullet that already names `get_candidate_current`.

## Stage 4: `read-operative` examples

**Done when:** `patt.artifact.read-operative.md` has `# Examples` showing `database.get_artifact(artifact_uuid)` and `get_operative_base_resume(artifact_uuid)`; greppable “do not” against blob dotted-path / coat-check fallback. Law headings intact.

1. Open `canon/directives/draft/patt.artifact.read-operative.md`. Leave law sections intact.
2. Insert `# Examples` between `# Implementation` and `# OPEN QUESTIONS / DECISIONS`.
3. Fenced block — **by pin** data layer:

```python
row = database.get_artifact(artifact_uuid)
# None on miss; else deserialize via row["artifact_data"] — no coat-check, no blob fallback
```

4. Fenced block — **pilot helper** `get_operative_base_resume(artifact_uuid)` in `src/core/candidate.py`: loads `database.get_artifact`, checks entity_type / artifact_type against `ARTIFACT_CONFIG["candidate.artifacts.base_resume"]`, returns body or `None`. Comment that Contact / explainability callers pass a stored pin, not “latest current.”
5. Adjacent **do not:** do not resolve explainability pins by reading `*_data` JSON blobs or by mid-turn coat-check; on miss return empty / surface ingestion gap.
6. Do **not** invent timestamp-based operative reads. Do **not** add scoped-without-pin examples beyond a one-line note that new code should store pins at write time (already in Implementation).

## Stage 5: `no-coat-check` examples + publish-ref verify

**Done when:** `patt.artifact.no-coat-check.md` has `# Examples` contrasting a forbidden mid-turn coat-check-style call with the required pre-load + `get_candidate_current` / `get_operative_base_resume` sequence; all five in-scope drafts each have ≥1 fenced ```` ``` ```` block under `# Examples`; `git diff origin/dev -- src/ tests/` is empty on this worktree after the docs commits; Abstract/Arc/Applications/Exceptions remain in all five files.

1. Open `canon/directives/draft/patt.artifact.no-coat-check.md`. Leave law sections intact.
2. Insert `# Examples` between `# Implementation` and `# OPEN QUESTIONS / DECISIONS`.
3. Fenced **forbidden** block — live coat-check surface as negative example only (do not register new keys). Use the existing async coat-check entry points named in the draft’s Applications (`get_job_data` / `get_company_data` in `src/core/tracker.py` / `src/core/roster.py`):

```python
# FORBIDDEN mid-turn — fetch-if-missing coat-check (legacy surfaces; do not extend)
# await get_job_data(job, "job_description")   # self-heal scrape path
# await get_company_data(company, "nav_links")  # registered company_data_keys handler
```

4. Fenced **required** block — pre-ingest / pre-load then artifact read:

```python
# REQUIRED — component/state already ingested; turn uses artifact APIs only
body = get_candidate_current(candidate_id, "candidate.artifacts.base_resume")
# or pin→body for explainability:
body = get_operative_base_resume(pinned_artifact_uuid)
```

5. Adjacent prose: missing content → fail visibly / ingestion state — never hide I/O inside an agent tool loop. Do **not** invent new ban APIs or expand `*_data_keys` maps in examples as if they were approved.
6. **Verify (builder checklist, docs-only — no `test()` product invent):**
   - `rg -n '```' canon/directives/draft/patt.artifact.manage-catalog.md canon/directives/draft/patt.artifact.write-operative.md canon/directives/draft/patt.artifact.read-current.md canon/directives/draft/patt.artifact.read-operative.md canon/directives/draft/patt.artifact.no-coat-check.md` — each file shows ≥1 fence.
   - For every callable named in new fences (`ARTIFACT_CONFIG`, `database.save_artifact`, `database.get_current_artifact`, `database.get_artifact`, `save_candidate_data`, `get_candidate_current`, `get_operative_base_resume`, `hydrate_operative_base_resume_for_response`, `get_job_data`, `get_company_data`, `save_job_artifact`, `get_job_current` if mentioned): confirm definition exists under `src/` on this tree (aligned with `origin/dev` after sync-child).
   - `rg -n '^# Abstract|^# Arc|^# Applications|^# Exceptions' canon/directives/draft/patt.artifact.{manage-catalog,write-operative,read-current,read-operative,no-coat-check}.md` — all present.
   - `rg -n 'do not|FORBID|never UPDATE|never.*blob|FORBIDDEN' canon/directives/draft/patt.artifact.{write-operative,read-current,read-operative,no-coat-check}.md` — greppable negative guidance on write/read drafts + no-coat-check.
   - `git diff origin/dev -- src/ tests/` — empty.
   - Plural drafts `patt.artifacts.ui-consistency.md` / `patt.artifacts.traceability.md` — unmodified (`git diff` clean for those paths).

⚠️ **Decision:** Place worked snippets in a new top-level `# Examples` section after `# Implementation` rather than appending fences inside Implementation bullets. Keeps normative Implementation lists authoritative (parent AC4 / law-unchanged) while giving agents a single greppable home for copy-paste shapes (ticket Technical scope: “Examples (or Implementation subsection)”).

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1627
**Overall:** APPROVED
**Corpus:** 7a40a9e0de4324d0d1c4d56abc52b13d3c297715 (canon tree on `origin/dev`; `canon_clerk.py` absent — clerk sha unavailable)
**Publish ref:** `sub/AST-1626/AST-1627-core-patt-artifact-example-enrichment` @ `ee95b46dcc55e7345a8e68a0e8d4b891c41dfbe7`

## Canon scores

patt.artifact.manage-catalog | A | |
patt.artifact.write-operative | A | |
patt.artifact.read-current | A | |
patt.artifact.read-operative | A | |
patt.artifact.no-coat-check | A | |
astral.standards.in-scope-only | A | |
astral.config.config-source-of-truth | A | |

## Traceability

AC1→Stages 1–5 (+S5 `rg` fence check); AC2→Stages 1–4 symbol harvest + S5 live-symbol `rg`; AC3→Explicit scope gate + S5 `git diff origin/dev -- src/ tests/`; AC4→per-stage “law headings intact” + S5 heading `rg`; AC5→Stages 2–4 + no-coat-check forbidden/required + S5 negative-guidance `rg`; parent AC6 (singular rename)→N/A — sibling #2, called out in UAT fitness / Boundaries.

## Findings

### discuss

- **Location:** Parent AST-1626 Applicable statutes vs child Citations
- **Finding:** Parent lists `astral.standards.names-not-ticket-ids`; child #1 Citations omit it. Plan’s example snippets already name live symbols (not ticket ids), but the frozen child list does not carry the statute Radia will not score later.
- **Recommendation:** Archie may amend Canon Scope at Discussion if ticket-id hygiene in new fences should be an explicit graded directive for this child; do not widen the list in-flight.

### acceptable

- **Location:** Stage 2 optional `save_job_artifact` / Stage 3 optional `get_job_current` pointers
- **Finding:** Brief cross-entity mentions beyond the candidate pilot.
- **Recommendation:** Keep as one-line pointers only (plan already bounds them); no expansion into job-editor examples on this child.

context_tokens≈28000

## Review (build)

**Built @ `caec5f7e965a675b7455c007e87dedb28b9bec96`** — `origin/sub/AST-1626/AST-1627-core-patt-artifact-example-enrichment`

Stages 1–5 landed: `# Examples` on the five singular drafts (`manage-catalog`, `write-operative`, `read-current`, `read-operative`, `no-coat-check`) with live `src/` symbols; no `src/`/`tests/` diff; plural ui-consistency / traceability drafts untouched.
