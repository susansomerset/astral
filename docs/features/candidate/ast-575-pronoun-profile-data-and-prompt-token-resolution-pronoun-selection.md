# Pronoun profile data and prompt token resolution (Pronoun selection)

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-575/pronoun-profile-data-and-prompt-token-resolution-pronoun-selection  
**Parent:** https://linear.app/astralcareermatch/issue/AST-573/pronoun-selection  
**Blocks:** https://linear.app/astralcareermatch/issue/AST-576/pronoun-preference-on-profile-and-admin-pronoun-selection (Katherine — Profile/Admin UI; needs stored field + token registry)

**Publish ref (origin):** `sub/AST-573/AST-575-pronoun-profile-data-and-prompt-tokens`  
**Parent integration ref:** `ftr/ast-573-pronoun-selection`

Store `profile.pronoun_preference` on candidate records, register five prompt tokens (`{$THEY}`, `{$THEIR}`, `{$THEIRS}`, `{$THEM}`, `{$THEMSELF}`), resolve each to the correct grammatical forms per preference (default **they/them** when unset or invalid), and backfill existing candidates to **they/them**. No Profile or Admin UI (sibling **AST-576**). No intake collection (**AST-539**).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `PRONOUN_PREFERENCE_*` constants, `PRONOUN_FORMS` map, five `TOKEN_SOURCES` entries, `resolve_tokens` `pronoun` source branch | utils |
| `src/data/database.py` | Idempotent `_migrate_pronoun_preference_backfill`; call from `_ensure_candidate_schema` | data |
| `tests/component/utils/test_config.py` | `TestPronounTokens` — registry, resolution per preference, default/backfill behavior | utils |
| `tests/component/data/database/test_candidate_migrations.py` | New file: backfill migration sets missing/empty `profile.pronoun_preference` to `they/them` | data |

**Not in scope:** `src/ui/frontend/**`, `NAV_CONFIG` / shapes profile field defs (**AST-576**), `api_candidate.py` validation beyond existing merge save (UI enforces options later).

---

## Data model

**Field:** `candidate_data.profile.pronoun_preference` — string, one of the five canonical values below.

**Canonical values (order matters for UI sibling; storage uses these exact strings):**

| Value | `{$THEY}` | `{$THEIR}` | `{$THEIRS}` | `{$THEM}` | `{$THEMSELF}` |
|-------|-----------|------------|-------------|-----------|---------------|
| `they/them` | they | their | theirs | them | themselves |
| `she/her` | she | her | hers | her | herself |
| `he/him` | he | his | his | him | himself |
| `ze/zir` | ze | zir | zirs | zir | zirself |
| `e/eir` | e | eir | eirs | em | emself |

**Default for resolution:** `they/them` when `profile.pronoun_preference` is missing, empty, or not in the table above.

⚠️ **Decision:** Resolution default only — do not reject unknown strings on save in this ticket (deep merge from **AST-576** may write only valid values; invalid stored values still resolve as **they/them**).

---

## Stage 1: Config constants and token registry

**Done when:** `PRONOUN_PREFERENCE_OPTIONS`, `PRONOUN_FORMS`, and five `TOKEN_SOURCES` entries exist; `get_tokens()` includes all five names; `python3 -m py_compile src/utils/config.py` passes.

1. In `src/utils/config.py`, after the `TOKEN_SOURCES` header comment block (before the `TOKEN_SOURCES = {` dict), add:

   ```python
   # AST-575: pronoun preference + resolved forms (parent AST-573).
   PRONOUN_PREFERENCE_DEFAULT = "they/them"
   PRONOUN_PREFERENCE_OPTIONS: tuple[str, ...] = (
       "they/them",
       "she/her",
       "he/him",
       "ze/zir",
       "e/eir",
   )
   PRONOUN_FORMS: dict[str, dict[str, str]] = {
       "they/them": {"THEY": "they", "THEIR": "their", "THEIRS": "theirs", "THEM": "them", "THEMSELF": "themselves"},
       "she/her": {"THEY": "she", "THEIR": "her", "THEIRS": "hers", "THEM": "her", "THEMSELF": "herself"},
       "he/him": {"THEY": "he", "THEIR": "his", "THEIRS": "his", "THEM": "him", "THEMSELF": "himself"},
       "ze/zir": {"THEY": "ze", "THEIR": "zir", "THEIRS": "zirs", "THEM": "zir", "THEMSELF": "zirself"},
       "e/eir": {"THEY": "e", "THEIR": "eir", "THEIRS": "eirs", "THEM": "em", "THEMSELF": "emself"},
   }
   ```

2. In `TOKEN_SOURCES`, after the existing profile identity block (after `COVER_LETTER_SIGNATURE`), add five entries:

   ```python
   "THEY":     {"source": "pronoun"},
   "THEIR":    {"source": "pronoun"},
   "THEIRS":   {"source": "pronoun"},
   "THEM":     {"source": "pronoun"},
   "THEMSELF": {"source": "pronoun"},
   ```

3. Above `resolve_tokens`, add a module-level helper (private, used only by `resolve_tokens`):

   ```python
   def _pronoun_preference_key(candidate_data: dict) -> str:
       raw = _walk_dot_path(candidate_data, "profile.pronoun_preference")
       if not isinstance(raw, str):
           return PRONOUN_PREFERENCE_DEFAULT
       key = raw.strip()
       return key if key in PRONOUN_FORMS else PRONOUN_PREFERENCE_DEFAULT
   ```

4. Run `python3 -m py_compile src/utils/config.py`.

⚠️ **Decision:** New `source: "pronoun"` in `TOKEN_SOURCES` rather than five dot-paths — one preference drives five surface forms; matches parent **Decisions** and keeps registry discoverable via `get_tokens()` / `GET /api/admin/tasks/meta/tokens`.

---

## Stage 2: `resolve_tokens` pronoun branch

**Done when:** A prompt `{$THEY} … {$THEMSELF}` with `profile.pronoun_preference: "she/her"` resolves to the she/her row in Python; missing preference resolves as they/them; `{$FIRST_NAME}` behavior unchanged; `py_compile` passes.

1. In `resolve_tokens`, inside `_replace`, after the `spec["source"] == "job"` block and before `return match.group(0)`, add:

   ```python
   if spec["source"] == "pronoun":
       pref = _pronoun_preference_key(candidate_data)
       return PRONOUN_FORMS[pref][name]
   ```

   (`name` is already `match.group(1)` from the regex.)

2. Do **not** emit empty-token warnings for pronoun tokens when preference is default — resolved strings are always non-empty for valid registry names.

3. Run `python3 -m py_compile src/utils/config.py`.

**Integration note (not a separate build step):** `preview_task_prompt` (`src/core/candidate.py`) and `do_task` (`src/core/agent.py`) already call `resolve_tokens`; Manage Tasks preview (**AC 4** preview half) and production runs share this path once **AST-576** can persist preference.

---

## Stage 3: Database backfill migration

**Done when:** Opening a DB via `_ensure_candidate_schema` sets `profile.pronoun_preference` to `they/them` on rows where it was missing or empty; rows that already have a valid preference are unchanged; migration is idempotent (second run is a no-op).

1. In `src/data/database.py`, add `_migrate_pronoun_preference_backfill(conn: sqlite3.Connection) -> None`:

   - Docstring: one-time idempotent backfill per parent AST-573 (unset → `they/them`).
   - `SELECT astral_candidate_id, candidate_data FROM candidate`.
   - For each row: `json.loads` candidate_data; skip empty/invalid JSON.
   - Ensure `cd.setdefault("profile", {})`.
   - Read `pref = profile.get("pronoun_preference")`.
   - If `pref` is a non-empty string and `pref.strip()` is in `PRONOUN_PREFERENCE_OPTIONS` (import from `src.utils.config`), **continue** (no update).
   - Else set `profile["pronoun_preference"] = PRONOUN_PREFERENCE_DEFAULT` and `UPDATE candidate SET candidate_data = ?`.
   - `conn.commit()` once after the loop.

2. In `_ensure_candidate_schema`, after `_migrate_candidate_data_structure(conn)` (same pattern as `_migrate_bio_upshot_to_summary`), call `_migrate_pronoun_preference_backfill(conn)`.

3. Run `python3 -m py_compile src/data/database.py`.

⚠️ **Decision:** Backfill writes explicit `they/them` (not leave key absent) so **AST-576** and admin tooling always see a stored value after first schema ensure.

---

## Stage 4: Component tests

**Done when:** `pytest tests/component/utils/test_config.py -k Pronoun -q` and `pytest tests/component/data/database/test_candidate_migrations.py -q` pass; `config.py` branch coverage preserved per §6a (branch comment blocks on new classes).

### 4a — `tests/component/utils/test_config.py`

Add class `TestAst575PronounTokens` with branch comment header per bible §6a.

1. `test_get_tokens_includes_five_pronoun_names` — assert `THEY`, `THEIR`, `THEIRS`, `THEM`, `THEMSELF` in `cfg.get_tokens()` and `TOKEN_SOURCES[name]["source"] == "pronoun"`.

2. `test_resolve_all_five_tokens_she_her` — candidate `{"profile": {"pronoun_preference": "she/her"}}`, text with all five tokens, assert exact string `she`, `her`, `hers`, `her`, `herself` in output (single combined assertion string is fine).

3. `test_resolve_default_when_preference_missing` — `{}` and `{"profile": {}}` → they/them forms.

4. `test_resolve_default_when_preference_invalid` — `{"profile": {"pronoun_preference": "custom/xyz"}}` → they/them forms.

5. Parametrize or five separate tests `test_resolve_preference_<slug>` for `he/him`, `ze/zir`, `e/eir` — one token each (`{$THEY}`) against expected subject form from `PRONOUN_FORMS`.

6. `test_first_name_unchanged_with_pronoun_set` — `{$FIRST_NAME}` with `profile.first` still resolves when pronoun preference present.

### 4b — `tests/component/data/database/test_candidate_migrations.py` (new file)

Use `tests/component/data/conftest.py` fixtures (`sqlite_in_memory` or `seeded_db` per sibling migration tests).

1. `test_pronoun_backfill_sets_default_when_missing` — insert candidate with `candidate_data` JSON `{"profile": {"first": "A"}}`, call `_ensure_candidate_schema(conn)` or invoke `_migrate_pronoun_preference_backfill` directly with connection from fixture, reload row, assert `profile.pronoun_preference == "they/them"`.

2. `test_pronoun_backfill_skips_valid_preference` — insert with `"pronoun_preference": "she/her"`, run migration, assert still `she/her`.

3. `test_pronoun_backfill_idempotent` — run migration twice, assert single stable value.

Run:

```bash
.venv/bin/python -m pytest tests/component/utils/test_config.py::TestAst575PronounTokens -q
.venv/bin/python -m pytest tests/component/data/database/test_candidate_migrations.py -q
```

---

## Self-Assessment

**Scope:** `Single-Component` — Touches only `config.py` token registry/resolver and one idempotent `database.py` migration plus focused component tests; no UI or API surface changes.

**Conf:** `high` — Extends established `TOKEN_SOURCES` / `resolve_tokens` and migration patterns already used for profile restructuring and bio_summary moves.

**Risk:** `Medium` — `resolve_tokens` is on every agent prompt path; wrong mapping would corrupt generated copy, but changes are additive and name tokens are untouched.

---

## Self-review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Single `PRONOUN_FORMS` table drives all five tokens; one `_pronoun_preference_key` helper. |
| §2.1 Config SoT | Options and forms live in `config.py`; migration imports `PRONOUN_PREFERENCE_*` from config. |
| §2.4 Batch | N/A — no batch processing. |
| §2.6 State machine | N/A — no candidate state transitions. |
| §3.3 Imports | `database.py` may import config constants for validation list (data → utils allowed for config reads in migrations per existing `_migrate_*` style). |
| §3.5 Naming | Plan doc slug matches ticket; no new pages/components. |

No `conf-!!-NONE` conflicts.

---

## Execution contract (developer agent)

- **AST-576** is out of scope — do not add profile/admin UI or `NAV_CONFIG` field rows.
- Blocking questions → comment on parent **AST-573** with 🛑 format from plan-astral §6.
- After each stage: commit on `dev-ada`, Joan `store-code-commit` per **build-astral** (not during plan-astral).

---

## Review (build)

**Branch:** `origin/sub/AST-573/AST-575-pronoun-profile-data-and-prompt-tokens`  
**Tip:** `0b625af9` (dev-ada: `f3a5439e` config + `0b625af9` migration)

**Built:** Stages 1–3 (config constants/registry, `resolve_tokens` pronoun branch, `_migrate_pronoun_preference_backfill`). Stage 4 component tests deferred to Betty per build-astral test-tree ban — see plan § Stage 4.

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-573/AST-575-pronoun-profile-data-and-prompt-tokens` (6 files, +407)  
**Reviewed tip:** `713ba55b`  
**AGENT_SESSION:** `3590af43-f9ed-4dfe-8f5b-de648423ac55`

### What's solid

- **Plan fidelity:** Scope matches `Single-Component` self-assessment — `config.py` registry/resolver, one idempotent migration, component tests only; no UI/API surface (**AST-576** / **AST-539** boundaries respected).
- **§2.1 Config SoT:** `PRONOUN_PREFERENCE_OPTIONS`, `PRONOUN_FORMS`, and `PRONOUN_PREFERENCE_DEFAULT` live in `config.py`; migration imports options/default from config (same pattern as `_migrate_bio_upshot_to_summary`).
- **Token contract:** Five `TOKEN_SOURCES` entries with `source: "pronoun"`; `_pronoun_preference_key` centralizes unset/invalid → **they/them**; `resolve_tokens` branch returns `PRONOUN_FORMS[pref][name]` — satisfies AC 3–6 for registry + resolution path shared by `preview_task_prompt` / `do_task`.
- **Backfill:** `_migrate_pronoun_preference_backfill` skips valid stored preferences, sets default otherwise, idempotent second run covered in tests.
- **Regression:** `TestAst575PronounTokens.test_first_name_unchanged_with_pronoun_set` guards AC 7; bible §7.13zzb documents manifest + regression command.
- **Layers (§3):** No UI imports; data layer raises no logs; no new debug surfaces (§5f N/A).

### Issues

| Severity | Location | Finding |
| -------- | -------- | ------- |
| — | — | No **fix-now** or **discuss** items. |

### Recommended actions

| Priority | Action | Owner |
| -------- | ------ | ----- |
| Advisory | Full five-form mapping is asserted only for **she/her**; **he/him**, **ze/zir**, **e/eir** use subject-only smoke tests — acceptable per plan Stage 4; optional hardening in resolve-astral if desired. | Ada |
| Advisory | Backfill scans all candidate rows on first `_ensure_candidate_schema` per process (same as sibling JSON migrations); monitor only if candidate table grows very large. | — |
| Next | **AST-576** can wire Profile/Admin UI to `profile.pronoun_preference` using `PRONOUN_PREFERENCE_OPTIONS` from config. | Katherine |

---

## Resolution (review)

**Date:** 2026-06-03  
**Review tip:** `713ba55b` (product + Betty tests) · Radia doc `57e4192b`  
**AGENT_SESSION:** `235d9ec6-fd42-47cc-b663-3de6e6be5c26` · **JOAN_SESSION:** `f24b1c61-f3c6-4ad7-95fa-d85c35f18d3c`

### vs Radia (fix-now / discuss)

- **fix-now:** none — no product or plan edits required for review findings.
- **discuss:** none.
- **Advisory:** left as-is — subject-only smoke tests for `he/him`, `ze/zir`, `e/eir` match plan Stage 4; full-table backfill scan matches existing migration pattern (`_migrate_bio_upshot_to_summary`).

### Resolve pass

- Integrated `origin/dev`, `origin/ftr/ast-573-pronoun-selection`, and `origin/sub/AST-573/AST-575-pronoun-profile-data-and-prompt-tokens` on `dev-ada`.
- Radia **Review (Radia)** section already on publish ref; this section records resolve closure only.

### Merge verification (§9a)

- `origin/sub/AST-573/AST-575-pronoun-profile-data-and-prompt-tokens` → `origin/dev`: clean.
- Same publish ref → `origin/ftr/ast-573-pronoun-selection`: clean.
