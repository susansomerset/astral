# UAT: possible_job_links dropped from letter-pipe bracket tails

**Linear:** [AST-699](https://linear.app/astralcareermatch/issue/AST-699/uat-possible-job-links-dropped-from-letter-pipe-bracket-tails)  
**Parent:** [AST-696](https://linear.app/astralcareermatch/issue/AST-696/prefilter-output-with-links) (AC #2, #5 reference only)  
**Publish ref:** `origin/sub/AST-696/AST-699-uat-possible-job-links-dropped-letter-pipe-brackets`  
**Summary:** Susan UAT on prefilter runs shows `culture_links_to_explore` populated but `possible_job_links` always `[]` when the model returns **letter-grade pipe lines with bracket link_set tails** and a leading **batch position prefix** (e.g. `0|A|B|A|[35]|[22,34,39,52,53]`). The normalizer misroutes those lines to `_decode_payload` because `_ENCODED_LINE_RE` only checks for a leading `digits|`, treats single-letter grades as meta, and `_apply_prefilter_encoded_link_meta` parses the first meta token `A` as a job link (empty) while bracket tails land in culture — including the job index. Fix: route position-prefixed **letter-pipe** lines to `_job_from_letter_pipe` (which already strips the position field and parses bracket tails correctly). True encoded lines (`000|RCA3|MPB3|USA3|[59,60]|…`) stay on the decode path.

**Root cause (reproduced on epic worktree):**

| Payload | Path | `possible_job_links` | `culture_links_to_explore` |
|---------|------|----------------------|----------------------------|
| `A\|B\|A\|[35]\|[22,34,39,52,53]` | `_job_from_letter_pipe` | `[35]` ✓ | `[22, 34, 39, 52, 53]` ✓ |
| `0\|A\|B\|A\|[35]\|[22,34,39,52,53]` | `_decode_payload` (wrong) | missing / `[]` | `[35, 22, 34, 39, 52, 53]` ✗ |
| `000\|RCA3\|MPB3\|USA3\|[59,60]\|[51,46,53]` | `_decode_payload` | `[59, 60]` ✓ | `[51, 46, 53]` ✓ |

In `_normalize_rubric_task_response` (~420–427), any line matching `_ENCODED_LINE_RE` (`^\d{1,3}\|`) is sent to `_decode_payload`. Single-company prefilter batches often emit `0|` + letter grades + bracket tails; that is **letter-pipe**, not AST-357 encoded segments (`RCA3`).

**Out of scope:** Rubric vectors, debug logging (**AST-698**), prompt schema example (**AST-697**), roster persist rules, UI, changes to `_apply_prefilter_encoded_link_meta` unless routing fix is insufficient (it should not be needed).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | Add `_should_decode_as_encoded_line`; gate `_decode_payload` routing in `_normalize_rubric_task_response` | core |

Betty adds manifest rows in **astral-tests** for position-prefixed letter-pipe bracket tails — engineer does **not** edit `tests/` or the bible.

---

## Stage 1: Route position-prefixed letter-pipe lines correctly

**Done when:** `0|A|B|A|[35]|[22,34,39,52,53]` normalizes to `possible_job_links == [35]` and `culture_links_to_explore == [22, 34, 39, 52, 53]`; existing encoded bracket line `000|RCA3|MPB3|USA3|[59,60]|[51,46,53]` unchanged; bare letter-pipe `A|B|A|15|13,16,14` and `A|B|A|[35]|…` unchanged.

1. In `src/core/consult.py`, immediately after `_ENCODED_LINE_RE = re.compile(r"^\d{1,3}\|")` (~171), add helper **`_should_decode_as_encoded_line(text: str) -> bool`**:

   ```python
   def _should_decode_as_encoded_line(text: str) -> bool:
       """True when a pipe line has AST-357 encoded grade segments (e.g. RCA3), not letter-pipe grades."""
       from src.core.agent import _GRADE_SEG

       line = next((ln.strip() for ln in text.splitlines() if ln.strip()), text.strip())
       fields = [f.strip() for f in line.split("|")]
       if fields and re.match(r"^\d{1,3}$", fields[0]):
           fields = fields[1:]
       for f in fields:
           norm = "".join(ch for ch in f if ch not in " -:")
           if _GRADE_SEG.match(norm):
               return True
       return False
   ```

   ⚠️ **Decision:** Reuse **`_GRADE_SEG`** from `agent.py` (lazy import inside helper) — same norm/strip rules as `_decode_payload` (~189–191). Do **not** duplicate the regex in `consult.py`.

2. In **`_normalize_rubric_task_response`**, replace the encoded-line branch (~420–427):

   **Before:**
   ```python
   if _ENCODED_LINE_RE.match(first_line):
       from src.core.agent import _decode_payload
       ...
   ```

   **After:**
   ```python
   if _ENCODED_LINE_RE.match(first_line) and _should_decode_as_encoded_line(text):
       from src.core.agent import _decode_payload
       output_type = task_config.get("output_type", "")
       decoded = _decode_payload(task_key, output_type, text, ctx or {})
       _ensure_jobs_astral_ids(decoded.get("jobs") or [], batch_entities)
       return decoded
   ```

   When the line starts with `digits|` but has **no** encoded grade segments, execution **falls through** to the existing `_job_from_letter_pipe(text, task_config, ctx)` call (~428), which already strips a leading numeric position field (~364–365) and maps bracket tails via `_parse_link_index_field`.

3. Manual verification (no test edits in this stage): in a Python shell on the epic worktree:

   ```python
   from src.core import consult as c
   from tests.component.core.test_agent import _ast603_prefilter_task_config, _ast603_prefilter_ctx

   ctx = _ast603_prefilter_ctx()
   tc = _ast603_prefilter_task_config()

   j = c._normalize_rubric_task_response(
       "prefilter_company", tc, "0|A|B|A|[35]|[22,34,39,52,53]", ctx
   )["jobs"][0]
   assert j["possible_job_links"] == [35]
   assert j["culture_links_to_explore"] == [22, 34, 39, 52, 53]

   j2 = c._normalize_rubric_task_response(
       "prefilter_company", tc, "000|RCA3|MPB3|USA3|[59,60]|[51,46,53]", ctx
   )["jobs"][0]
   assert j2["possible_job_links"] == [59, 60]
   assert j2["culture_links_to_explore"] == [51, 46, 53]

   j3 = c._normalize_rubric_task_response(
       "prefilter_company", tc, "A|B|A|15|13,16,14", ctx
   )["jobs"][0]
   assert j3["possible_job_links"] == [15]
   assert j3["culture_links_to_explore"] == [13, 16, 14]
   ```

---

## Execution contract

- Execute **Stage 1** in order; **one commit** on **`astral-AST-696`**, then publish to **`origin/sub/AST-696/AST-699-uat-possible-job-links-dropped-letter-pipe-brackets`** via `git push origin HEAD:sub/AST-696/AST-699-uat-possible-job-links-dropped-letter-pipe-brackets` with **`--session astral-AST-696`** per build-child publish ritual.
- Do **not** edit `tests/`, `docs/ASTRAL_TEST_BIBLE.md`, or `docs/test-bible/**`.
- Blocking ambiguity → 🛑 comment on **AST-696** per plan-child execution contract.

---

## Self-Assessment

**Scope:** `minor` — One helper + one conditional in `src/core/consult.py`; no config, agent decode, or roster changes.

**Conf:** `high` — Root cause reproduced locally; `_job_from_letter_pipe` already handles bracket tails and position strip; fix is routing only.

**Risk:** `low` — Mis-routing encoded lines that lack `_GRADE_SEG` segments but are not letter-pipe is unlikely for production prefilter; encoded lines with `RCA3`-style segments still use `_decode_payload`. Regression surface covered by existing **AST-603** / **AST-697** tests plus Betty manifest for Susan's `0|A|B|A|[35]|…` shape.

---

## Code rules self-review

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses `_GRADE_SEG` from `agent.py`; reuses `_job_from_letter_pipe` instead of duplicating bracket parse in decode meta. |
| §3.3 imports | Lazy import of `_GRADE_SEG` / `_decode_payload` inside functions — matches existing consult ↔ agent pattern. |
| §2.1 config | No config changes. |
| §1.5.1 debug | Out of scope (**AST-698**). |

No conflicts requiring **Conf: !!-NONE**.

---

## Review

**Branch:** `origin/sub/AST-696/AST-699-uat-possible-job-links-dropped-letter-pipe-brackets`  
**Build tip:** `82b5e62`
