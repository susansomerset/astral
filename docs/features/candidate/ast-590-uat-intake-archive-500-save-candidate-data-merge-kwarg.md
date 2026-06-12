# AST-590 — UAT: intake archive 500 — save_candidate_data merge kwarg

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-590/uat-intake-archive-500-save-candidate-data-merge-kwarg  
**Parent:** https://linear.app/astralcareermatch/issue/AST-539/candidate-intake-chat-session  
**Publish ref:** `sub/AST-539/AST-590-intake-archive-save-candidate-data-kwarg` (origin only)

Susan UAT on **AST-539**: **Start Over** → `POST …/intake/sessions/active/archive` returns **500** with `TypeError: save_candidate_data() got an unexpected keyword argument 'merge'`. Stack: `archive_active_intake_session` → `_append_intakes_old` → `save_candidate_data(..., merge=True)`. The public API is `save_candidate_data(candidate_id, data, replace=False)` in `src/core/candidate.py` — merge is the default when `replace=False`; there is no `merge` kwarg. Same typo exists on source-material persist and build payload paths introduced with **AST-582** / **AST-558** intake core.

**Expected:** Archive succeeds; `candidate_data.intakes_old` appended; **AST-584** Start Over fresh initiate can proceed.

**Out of scope:** React (`CandidateIntake.tsx`, `IntakeChatModal.tsx`), API route shape, **AST-583**/**AST-584**/**AST-585** UI flows beyond unblocking archive.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/intake.py` | Remove invalid `merge=True` kwargs on three `save_candidate_data` calls | core |
| `tests/component/core/test_intake.py` | Add `TestIntakeArchive` — real archive path (no `save_candidate_data` mock) | tests |

**Out of scope:** `src/core/candidate.py` signature change, `src/ui/api/api_intake.py`, frontend.

---

## Stage 1: Fix save_candidate_data call sites

**Done when:** All three call sites use the documented `save_candidate_data` signature; default merge behavior preserved; no `merge=` kwarg anywhere in `intake.py`.

1. In `src/core/intake.py`, in `_persist_source_materials` (~L41–51), change:

   ```python
   save_candidate_data(
       candidate_id,
       {
           "context": {
               "starting_resume_text": starting_resume_text.strip(),
               "sample_cover_text": (sample_cover_text or "").strip(),
               "linkedin_profile_text": (linkedin_profile_text or "").strip(),
           }
       },
       merge=True,
   )
   ```

   to (remove the invalid kwarg — default `replace=False` deep-merges):

   ```python
   save_candidate_data(
       candidate_id,
       {
           "context": {
               "starting_resume_text": starting_resume_text.strip(),
               "sample_cover_text": (sample_cover_text or "").strip(),
               "linkedin_profile_text": (linkedin_profile_text or "").strip(),
           }
       },
   )
   ```

2. In `_apply_build_payload` (~L233–234), change:

   ```python
   save_candidate_data(candidate_id, merge_data, merge=True)
   ```

   to:

   ```python
   save_candidate_data(candidate_id, merge_data)
   ```

3. In `_append_intakes_old` (~L248), change:

   ```python
   save_candidate_data(candidate_id, {"intakes_old": items}, merge=True)
   ```

   to:

   ```python
   save_candidate_data(candidate_id, {"intakes_old": items})
   ```

4. Run `grep -n 'merge=True' src/core/intake.py` — must return no matches.

⚠️ **Decision:** Do **not** add a `merge` alias to `save_candidate_data` — **AST-582** plan mistakenly used `merge=True`; the established candidate API uses `replace=False` (merge) vs `replace=True` (full replace). One-line call-site fix only.

---

## Stage 2: Core archive regression tests

**Done when:** `pytest tests/component/core/test_intake.py -k archive -q` passes; existing intake tests in that file still pass.

**Context:** `tests/component/ui/api/test_api_intake.py -k archive` mocks `archive_active_intake_session` and would **not** catch this TypeError. Add **`TestIntakeArchive`** per approved **AST-582** Stage 3 so archive exercises real `save_candidate_data`.

1. In `tests/component/core/test_intake.py`, after `TestIntakeSessionFlow`, add:

   ```python
   class TestIntakeArchive:
       @pytest.mark.asyncio
       async def test_archive_active_session_appends_intakes_old_and_clears_active(
           self, seeded_db, mock_do_task, monkeypatch: pytest.MonkeyPatch
       ) -> None:
           created = await intake_mod.create_intake_session_and_start("cand-1", "Resume text")
           await _wait_for_transcript_assistant(created["session_id"])
           result = intake_mod.archive_active_intake_session("cand-1")
           assert set(result.keys()) == {
               "archived_session_id",
               "archived_at",
               "intakes_old_count",
           }
           assert result["archived_session_id"] == created["session_id"]
           assert result["intakes_old_count"] == 1
           assert intake_mod.fetch_active_intake_session("cand-1") is None
           row = intake_mod.database.get_intake_session(created["session_id"])
           assert row is not None
           assert row["status"] == INTAKE_CONFIG["session_status_archived"]
           cand = intake_mod.get_candidate("cand-1")
           assert cand is not None
           old = (cand.get("candidate_data") or {}).get("intakes_old") or []
           assert len(old) == 1
           assert old[0]["intake_session_id"] == created["session_id"]
           assert len(old[0].get("transcript") or []) >= 2

       def test_archive_raises_when_no_active_session(self, seeded_db) -> None:
           with pytest.raises(LookupError, match="no active"):
               intake_mod.archive_active_intake_session("cand-1")

       @pytest.mark.asyncio
       async def test_second_archive_appends_second_entry(
           self, seeded_db, mock_do_task, monkeypatch: pytest.MonkeyPatch
       ) -> None:
           first = await intake_mod.create_intake_session_and_start("cand-1", "Resume one")
           await _wait_for_transcript_assistant(first["session_id"])
           intake_mod.archive_active_intake_session("cand-1")
           second = await intake_mod.create_intake_session_and_start("cand-1", "Resume two")
           await _wait_for_transcript_assistant(second["session_id"])
           result = intake_mod.archive_active_intake_session("cand-1")
           assert result["intakes_old_count"] == 2
           cand = intake_mod.get_candidate("cand-1")
           ids = [
               e["intake_session_id"]
               for e in (cand.get("candidate_data") or {}).get("intakes_old") or []
           ]
           assert ids == [first["session_id"], second["session_id"]]
   ```

2. Do **not** monkeypatch `save_candidate_data` in `TestIntakeArchive` — the regression must call the real wrapper.

3. Run:

   ```bash
   pytest tests/component/core/test_intake.py -k archive -q
   pytest tests/component/ui/api/test_api_intake.py -k archive -q
   pytest tests/component/core/test_intake.py -q
   ```

---

## Self-Assessment

**Scope:** `minor` — Three one-line kwarg removals in `src/core/intake.py` plus focused archive tests; no API or UI changes.

**Conf:** `high` — Root cause and fix are explicit in the ticket and `save_candidate_data` signature; mirrors **AST-582** archive behavior with correct API usage.

**Risk:** `Medium` — Archive is on the **Start Over** critical path; wrong persistence could drop `intakes_old` entries, but fix aligns with existing merge semantics and **AST-582** read-append-write for lists.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | No new helpers; reuse `save_candidate_data` as documented. |
| §2.1 config | No config changes. |
| §3.3 imports | No import changes. |
| §3.5 naming | No renames. |

No conflicts — plan is a call-site correction plus missing **AST-582** core tests.

---

## Review

**Built:** `origin/sub/AST-539/AST-590-intake-archive-save-candidate-data-kwarg` @ _(pending commit)_
**Scope:** Stage 1 only — removed invalid `merge=True` on three `save_candidate_data` call sites in `src/core/intake.py`. Stage 2 archive tests deferred to Betty (`qa-astral`).
