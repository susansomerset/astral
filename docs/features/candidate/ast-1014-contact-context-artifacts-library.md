# AST-1014 — Contact / context / artifacts library + name columns

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1014/contact-context-artifacts-library-name-columns-candidate-profile  
**Parent:** https://linear.app/astralcareermatch/issue/AST-952/candidate-profile-preamble-to-intake  

**Publish ref (origin):** `sub/AST-952/AST-1014-contact-context-artifacts-library`  
**Parent integration ref:** `ftr/AST-952-candidate-profile-preamble-to-intake`

Give the candidate a durable **contact / context / artifacts** library (three JSON blobs under `candidate_data`) plus **first / last / full / pronouns** as individual `candidate` table text columns, so Profile/Admin and later preamble / Topic Menu (AST-953) read and write one home each — no shadow copies of identity or contact in context prose.

Boundaries (do **not** implement): Ruth Valid/Try Again/Escalate (AST-1015), `PREAMBLE_CONFIG` (AST-1016), mechanical intake UI (AST-1017), Estelle confirm (AST-953), candidate state-machine vocabulary changes (AST-871).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `CANDIDATE_LIBRARY_CONFIG` (blob keys, context remaps, URL bases, full-name join rule); rename DATA_SHAPES `profile.*` → columns + `contact.*`; update TOKEN_SOURCES paths; add `FULL_NAME`; point pronoun resolution at `pronouns` column via token view; update intake/bootstrap required field paths that still say `profile.` / old context raw keys | utils |
| `src/data/database.py` | Add columns `first`, `last`, `full`, `pronouns` (+ wire missing `state_history` persist/parse that core already calls); header inventory; `_migrate_candidate_library_ast1014`; extend `save_candidate` / `_parse_candidate_row` | data |
| `src/core/candidate.py` | Library-aware save/get helpers; `build_candidate_token_view`; `check_context_complete` + resume parse paths use remapped context keys; optional `debug=` library-write contract lines; Admin/create paths write columns + contact | core |
| `src/core/builder.py` | `_apply_profile_to_render_dict` reads contact blob + name columns (no `profile`) | core |
| `src/core/intake.py` | Persist/read remapped context raw keys (`raw_resume` / `raw_profile` / `raw_sample`) where it currently uses `starting_resume_text` / `linkedin_profile_text` / `sample_cover_text` | core |
| `src/ui/api/api_candidate.py` | PUT `/data` routes column fields vs `contact`/`context`/`artifacts`; signature-image validation under `contact`; GET returns columns + migrated `candidate_data`; create/admin no longer write `profile` | ui |
| `src/ui/frontend/src/pages/CandidateProfile.tsx` | Load/save columns + `contact`/`context` (shapes-driven); signature image path `contact.cover_letter_signature_image` | ui |
| `src/ui/frontend/src/pages/AdminManageCandidates.tsx` | Create/edit first/last/email/pronouns against columns + contact; drop `profile.*` | ui |
| `src/ui/frontend/src/contexts/CandidateContext.tsx` | Display name / timezone from columns + `contact` | ui |
| `src/ui/frontend/src/lib/candidateLabel.ts` | Prefer table `first`/`last` | ui |
| `src/ui/frontend/src/components/Time.tsx` | Timezone from `contact.timezone` | ui |
| `src/ui/frontend/src/components/ProfileTextPage.tsx` | Edit under `contact` (not `profile`) | ui |
| `src/ui/frontend/src/components/NavigationShell.tsx` | Any `candidate_data.profile` reads → columns/contact | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Profile/contact reads → new homes | ui |
| `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` | Timezone from `contact` | ui |
| `src/ui/frontend/src/pages/CandidateIntake.tsx` | Context raw key names if referenced | ui |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Rewrite table + blob sections for library + columns | docs |

---

## Stage 1: Config contract — library vocabulary + shapes + tokens

**Done when:** `CANDIDATE_LIBRARY_CONFIG` is the sole source for blob key lists and context remaps; DATA_SHAPES Profile detail uses column keys + `contact.*` / remapped `context.*`; TOKEN_SOURCES resolve names from columns and contact/context from the new paths; no remaining `profile.` keys in DATA_SHAPES or TOKEN_SOURCES.

1. In `src/utils/config.py`, add `CANDIDATE_LIBRARY_CONFIG` immediately after `CANDIDATE_CONFIG` with these literal keys (no `os.environ`):

```python
CANDIDATE_LIBRARY_CONFIG = {
    "contact_keys": (
        "contact_email", "reply_email", "phone", "location",
        "github", "linkedin_url", "websites", "timezone",
        "cover_letter_signature", "cover_letter_signature_image",
        "title_patterns", "reason_codes",
    ),
    "context_keys": (
        "bio_summary", "backstory", "strengths", "priorities", "deal_breakers",
        "writing_preferences", "hopes", "interests", "concerns",
        "raw_resume", "raw_profile", "raw_sample",
    ),
    "context_key_remap": {
        "starting_resume_text": "raw_resume",
        "linkedin_profile_text": "raw_profile",
        "sample_cover_text": "raw_sample",
    },
    "name_columns": ("first", "last", "full", "pronouns"),
    "linkedin_url_base": "https://www.linkedin.com/in/",
    "github_url_base": "https://github.com/",
    "full_name_join": " ",  # join non-empty first + last when recomputing `full`
}
```

⚠️ **Decision:** Keep the three library blobs **inside** `candidate_data` (`contact` / `context` / `artifacts`) rather than three new SQL JSON columns. Parent AC requires three blobs **and** name/pronoun **table columns**; nesting the blobs under the existing JSON column matches today’s persistence pattern and avoids dual homes. Meta keys (`lifecycle`, `pending_craft_generations`, `intakes_old`) stay as **siblings** of the three blobs under `candidate_data` — not inside contact/context/artifacts.

⚠️ **Decision:** Rename `profile` → `contact`. Identity/comms leave freeform context; high-frequency name/pronoun tokens leave the blob for columns. Non-comms fields that Profile already edits (`timezone`, signatures, `title_patterns`, `reason_codes`) stay on **contact** so Profile keeps one blob home (they are not context prose and not rubric artifacts).

⚠️ **Decision:** Add empty `hopes` / `interests` / `concerns` to the context vocabulary now (Topic Menu inputs per parent); do not populate them in this ticket.

2. Update `DATA_SHAPES["candidates"]["detail"]["profile"]` Contact Information fields:

| Old key | New key |
|---------|---------|
| `profile.first` | `first` (top-level on the edit values object) |
| `profile.last` | `last` |
| `profile.pronoun_preference` | `pronouns` |
| `profile.contact_email` | `contact.contact_email` |
| `profile.reply_email` | `contact.reply_email` |
| `profile.phone` | `contact.phone` |
| `profile.location` | `contact.location` |
| `profile.github` | `contact.github` |
| `profile.linkedin_url` | `contact.linkedin_url` |
| `profile.timezone` | `contact.timezone` |
| `profile.cover_letter_signature` | `contact.cover_letter_signature` |
| `profile.cover_letter_signature_image` | `contact.cover_letter_signature_image` |
| `profile.title_patterns` | `contact.title_patterns` |
| `context.sample_cover_text` | `context.raw_sample` |
| `context.linkedin_profile_text` | `context.raw_profile` |
| `context.starting_resume_text` | `context.raw_resume` |
| `context.bio_summary` | unchanged |

Pronoun select `options` must continue to mirror `PRONOUN_PREFERENCE_OPTIONS` (same five values + empty “(not set)”); do not invent a second option list.

3. Update `TOKEN_SOURCES`:

| Token | New path / behavior |
|-------|---------------------|
| `FIRST_NAME` | `first` (column; see Stage 3 token view) |
| `LAST_NAME` | `last` |
| `FULL_NAME` | **new** token → `full` |
| `CONTACT_EMAIL` … `LINKEDIN_URL`, `LOCATION`, `GITHUB` | `contact.<key>` |
| `TITLE_PATTERNS`, `REASON_CODES`, `COVER_LETTER_SIGNATURE` | `contact.<key>` |
| `STARTING_RESUME_TEXT` | `context.raw_resume` (token **name** unchanged for prompt authors) |
| `LINKEDIN_PROFILE_TEXT` | `context.raw_profile` |
| `SAMPLE_COVER_TEXT` | `context.raw_sample` |
| other context / artifact tokens | same keys under `context.` / `artifacts.` |

4. Change `_pronoun_preference_key` to read preference from the token-view key `pronouns` (string column value), still defaulting invalid/empty to `PRONOUN_PREFERENCE_DEFAULT` via `PRONOUN_FORMS`.

5. Update every config path that still references `profile.title_patterns` or old context raw keys for intake/bootstrap required-field lists (search `profile.` and `starting_resume_text` / `linkedin_profile_text` / `sample_cover_text` in `config.py`) to the new homes. Do not add `PREAMBLE_CONFIG`.

---

## Stage 2: Data layer — columns + idempotent library migration

**Done when:** Fresh and existing DBs expose `first`/`last`/`full`/`pronouns` on `get_candidate`; one-time migration remaps `profile`→`contact`, lifts names/pronouns to columns, remaps context raw keys, seeds empty hopes/interests/concerns, and leaves **no** `profile` key and **no** old context raw keys on migrated rows; `save_candidate` can set columns and deep-merge library blobs; header inventory lists the new columns.

1. In `_ensure_candidate_schema`, extend CREATE TABLE and the idempotent ALTER loop with:

| Column | Def |
|--------|-----|
| `first` | `TEXT` |
| `last` | `TEXT` |
| `full` | `TEXT` |
| `pronouns` | `TEXT` |
| `state_history` | `TEXT DEFAULT '[]'` |

⚠️ **Decision:** While touching `save_candidate` / `_parse_candidate_row` / schema ensure, **wire `state_history`** (column + JSON parse + optional kwarg, preserve-when-omitted on update) to match what `src/core/candidate.py` already passes (`initiate_candidate` / `transition_candidate_state`) and what `CANDIDATE_DATA_MODEL.md` / AST-971 already document. This is unblock for the same upsert path — not Progress UI and not a new product feature.

2. Update the module header inventory `candidate — …` bullet to list: `state`, `state_history`, `candidate_data` (contact/context/artifacts + meta), `first`, `last`, `full`, `pronouns`, `candidate_api_key`, timestamps.

3. In `_parse_candidate_row`: keep parsing `candidate_data`; parse `state_history` to list (invalid/missing → `[]`); leave `first`/`last`/`full`/`pronouns` as plain strings (NULL → `""` or `None` consistently — use `""` for missing so UI selects work).

4. Extend `save_candidate` keyword-only args: `first`, `last`, `full`, `pronouns`, `state_history` (optional). On INSERT/UPDATE, set only provided name/pronoun columns. `candidate_data` merge behavior unchanged (deep-merge when `merge=True`).

5. Add `_migrate_candidate_library_ast1014(conn)` called from `_ensure_candidate_schema` **after** existing `_migrate_candidate_data_structure` / pronoun / context-array migrations. Idempotent probe: skip a row when `candidate_data` has `contact` and lacks `profile`, and context lacks old remap source keys, and name columns are already populated when profile had names. For each row that still needs work:

   - Parse `candidate_data`.
   - If `profile` dict present: copy contact-eligible keys into `contact` (from `CANDIDATE_LIBRARY_CONFIG["contact_keys"]`); copy `first`/`last` into columns if column empty; set `pronouns` from `profile.pronoun_preference` if column empty; **delete** `profile`.
   - Ensure `contact` / `context` / `artifacts` dicts exist.
   - Apply `context_key_remap`: for each old→new, if old in context and new absent, move value; always `pop` old key.
   - For each of `hopes`, `interests`, `concerns`: if missing, set `""`.
   - Recompute `full` when empty: join non-empty `first` and `last` with `full_name_join`.
   - If `pronouns` empty/invalid, set `PRONOUN_PREFERENCE_DEFAULT`.
   - Write columns + `candidate_data` JSON; commit.

6. Do **not** keep dual keys (`profile` alongside `contact`, or `starting_resume_text` alongside `raw_resume`) after migration — that would be a shadow copy (parent AC).

---

## Stage 3: Core library helpers + readers/writers

**Done when:** All core paths that read/write identity, contact, or context raw sources use columns + `contact`/`context`/`artifacts`; `build_candidate_token_view` feeds `resolve_tokens`; LinkedIn/GitHub URL-or-username normalization runs on contact save; library writes honor `debug=True` contract lines; builder/intake use remapped keys.

1. In `src/core/candidate.py`, add:

```python
def build_candidate_token_view(candidate: dict) -> dict:
    """Walkable dict for resolve_tokens: name columns + library blobs (no meta)."""
```

   Shape:

```python
{
  "first": candidate.get("first") or "",
  "last": candidate.get("last") or "",
  "full": candidate.get("full") or "",
  "pronouns": candidate.get("pronouns") or "",
  "contact": (candidate.get("candidate_data") or {}).get("contact") or {},
  "context": (candidate.get("candidate_data") or {}).get("context") or {},
  "artifacts": (candidate.get("candidate_data") or {}).get("artifacts") or {},
  "_astral_candidate_id": candidate.get("astral_candidate_id") or "",
}
```

   Every `resolve_tokens(..., candidate_data=cd)` call site that today passes raw `candidate_data` for name/contact/context tokens must pass this view (or an equivalent merge). Prefer updating the call sites that load a full candidate row; do not invent a second resolver.

2. Add `normalize_contact_urls(contact: dict) -> None` (mutates in place): for `linkedin_url` and `github`, if value is non-empty and has no `://`, prepend `CANDIDATE_LIBRARY_CONFIG` URL bases (strip leading `@`). This is library coercion, **not** Ruth validation (AST-1015).

3. Add `recompute_full_name(first: str, last: str) -> str` using `full_name_join`.

4. Extend `save_candidate_data` (or add `save_candidate_library`) so PUT-shaped bodies may include top-level `first`/`last`/`full`/`pronouns` plus `contact`/`context`/`artifacts` (+ meta). Implementation:

   - Pop column keys → `database.save_candidate(..., first=..., last=..., full=..., pronouns=...)`.
   - When `first` or `last` provided and `full` omitted, set `full=recompute_full_name(...)`.
   - On `contact` dict: run `normalize_contact_urls`; deep-merge via existing save.
   - Reject body key `profile` with `ValueError("profile was renamed to contact; refuse shadow write")` so divergent copies cannot land.
   - Accept optional `debug: bool = False`. When `debug=True`, emit §1.5.1 lines via `get_logger(..., debug_flag=debug)`: one `debug_index` header per logical write step (e.g. columns, contact, context, artifacts) with primary id = `astral_candidate_id` and outcome found/recorded; long blobs through `truncate_debug_content`. No new debug lines when `debug=False`.

5. Update `check_context_complete` to read remapped context keys if it references old names (keep gate field set from config — do not invent new completeness rules beyond key renames).

6. Update `parse_candidate_resume` / any reader of `starting_resume_text` to `context.raw_resume`; write structured output only to `artifacts` as today.

7. Update `initiate_candidate` / `save_candidate_admin` / Manage-Candidates create path helpers: accept names + pronouns as columns; contact email into `contact`; never write `profile`.

8. In `src/core/builder.py`, change `_apply_profile_to_render_dict` callers to pass **contact** plus inject `first`/`last`/`full` from columns into the render dict (rename helper to `_apply_contact_to_render_dict` if that keeps the file clearer — one rename, update all call sites in this file).

9. In `src/core/intake.py`, replace persistence/read of `starting_resume_text` / `linkedin_profile_text` / `sample_cover_text` with `raw_resume` / `raw_profile` / `raw_sample`. Parameter names on Python functions may keep the old names only if that avoids a wide churn **and** the plan step documents the mapping at the call boundary; prefer renaming parameters to the new keys when the function is already being edited.

---

## Stage 4: API + Profile/Admin UI — one home, no divergent copies

**Done when:** GET `/api/candidates/<id>` returns columns at top level and `candidate_data` without `profile`; PUT `/data` saves columns + contact/context/artifacts; Candidate Profile and Admin Manage Candidates edit first/last/pronouns/contact against the new homes and round-trip; timezone/signature/title-pattern pages that used `profile` use `contact`.

1. In `src/ui/api/api_candidate.py` `update_candidate_data`:

   - Treat top-level `first`/`last`/`full`/`pronouns` as column updates (via Stage 3 saver).
   - Validate signature image under `contact.cover_letter_signature_image` (same rules as today’s `profile` path).
   - Artifact / rubric / company_search_terms handling stays on `artifacts` (unchanged logic, new blob name already `artifacts`).
   - Do not accept `profile` in the body (propagate Stage 3 `ValueError` as 400).

2. `get_candidate_detail` / list sanitization: after hydrate, ensure response includes `first`/`last`/`full`/`pronouns` from columns; `candidate_data` has `contact` not `profile`.

3. `create_candidate`: map POST body so Admin can send `candidate_data.contact` + top-level names, or nested create payload documented in this step — Admin UI (step 5) must match.

4. `CandidateProfile.tsx`: build edit `values` as `{ first, last, pronouns, contact, context, ... }` from GET (columns + `candidate_data` sections). Save PUTs that object. Update signature image path to `contact.cover_letter_signature_image`. Keep FormFields/shapes-driven — no hardcoded field lists beyond signature/base-resume special cases already present.

5. `AdminManageCandidates.tsx`: add/edit forms read/write `first`/`last`/`pronouns` columns and `contact.contact_email` (and any other contact fields already in the modal). Remove `profile` / `pronoun_preference` nested under `candidate_data` on create/save. Pronoun field still driven from shapes (find field by key `pronouns`).

6. Update the remaining frontend files in the Files Changed table that read `candidate_data.profile` so they use columns and/or `contact` (timezone → `contact.timezone`; display name → `first`/`last`/`full`).

7. Smoke-check by inspection: no `profile.` string left in `src/ui/frontend/src` for candidate data paths (grep). Allow comments/history only if unavoidable — prefer zero.

---

## Stage 5: Data model doc

**Done when:** `CANDIDATE_DATA_MODEL.md` matches the shipped library + columns; no stale `profile` section as the identity home.

1. Rewrite `docs/features/candidate/CANDIDATE_DATA_MODEL.md`:

   - Document table columns `first`, `last`, `full`, `pronouns`, `state_history`.
   - Document `candidate_data` top-level: `contact`, `context`, `artifacts`, plus meta (`lifecycle`, `pending_craft_generations`, `intakes_old`).
   - Contact / context / artifacts key tables per Stages 1–2 (including remaps and hopes/interests/concerns).
   - Token table: column-backed name/pronoun tokens; contact/context paths; `FULL_NAME`.
   - Explicit rule: do **not** store first/last/full/pronouns inside contact/context/artifacts; do **not** store contact handles as context prose.

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — data schema + migration, config contract, core readers/writers (candidate/builder/intake), API, and Profile/Admin frontend all move from `profile` + nested names to columns + `contact` library.

**Conf:** `high` — remap and column lift follow existing `_migrate_candidate_*` / DATA_SHAPES / TOKEN_SOURCES patterns; boundaries with AST-1015/1016/1017 are explicit.

**Risk:** `HIGH` — nearly every candidate identity/token path changes; a missed `profile` reader would show blank names or break resume render / Admin create. Migration must be idempotent and shadow-copy-free.

---

## Code rules self-review

- **§2.1:** Library vocabulary and remaps live in `CANDIDATE_LIBRARY_CONFIG`; no inline key sets in migration/UI.
- **§1.3:** One remap table, one URL normalizer, one full-name join helper — no duplicated remap dicts in data vs core.
- **§1.5.1:** Library write path accepts `debug=` and emits contract lines only when true; data layer still does not log.
- **§2.4 / §2.6:** No new batch primitives; no candidate state vocabulary changes.
- **§3.3:** UI → core/utils only; data migration imports config options already used by pronoun backfill.
- **§3.5:** Frontend keeps shapes-driven Profile fields; PascalCase components / snake_case API unchanged.
- **Out of scope enforced:** no Ruth agent_task, no `PREAMBLE_CONFIG`, no mechanical preamble UI.

---

## Review

**Publish ref:** `sub/AST-952/AST-1014-contact-context-artifacts-library`
**Build tip:** `c907a7c40d9c5eedc30abf985ec4f72b56bc5626`
