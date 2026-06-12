# AST-483 — Normalize grades segment whitespace in agent decode

**Linear:** Parent [AST-472](https://linear.app/astralcareermatch/issue/AST-472) · This issue [AST-483](https://linear.app/astralcareermatch/issue/AST-483)

**Publish ref:** `origin/sub/AST-472/AST-483-normalize-grades-segment-whitespace-in-agent-decode`

## Summary

Models sometimes prettify encoded consult lines (`000|DT A5|GC B4|…`) by inserting ASCII spaces, hyphens, or colons *inside* a single grade token (`DT A5`). Today `_decode_payload` classifies pipe fields strictly with `_GRADE_SEG.match(f)`, so embellished tokens drift into **`meta`** and trigger **`unexpected trailing content in grades-only line`** (`evaluate_jd` / `do_task decode failed`). Normalize each pipe field **only when deciding grade vs meta**: strip space, hyphen, and colon characters for `_GRADE_SEG` classification and for the string stored in **`grade_segs`**. Leave **`meta`** list entries **unchanged** (original field text after pipe-split `strip`). No changes to prompts, dispatcher, or UI.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | Narrow normalization + classification change in `_decode_payload` (~five lines touching the `"|"` classification loop unless a tiny helper proves clearer next to `_GRADE_SEG`) | core |
| `tests/component/core/test_agent.py` | Extend `TestDecodePayload` with one test that asserts spaced-hyphen tokens decode; one assertion that **`grades_meta`** metadata fields preserve interior spaces/hyphens when not valid grade tokens | tests |

---

## Stage 1: Decode normalization + regression test

**Done when:** A line **`0|DT A5|GC-B4`** with `vector_labels` `DT`, `GC` decodes two grade rows identical to **`0|DTA5|GCB4`**. A **`grades_meta`** line where the first metadata fragment contains **`Senior Role`** (spaces) unchanged in **`job_title`** (or comparable meta slot). No other modules modified.

1. **`src/core/agent.py`** — in `_decode_payload`, keep `fields = [f.strip() for f in line.split("|")]` and the **`pos`** / **`batch_entities`** logic unchanged.

2. Replace the **`for f in fields[1:]:`** loop (~lines 132–134) body so that:

   - Compute **`norm = ''.join(ch for ch in f if ch not in ' -:')`** immediately for each **`f`** (ASCII space **` `**, hyphen **` -`**, colon **`:`** only — explicitly the three classes named in AST-483).
   - If **`_GRADE_SEG.match(norm)`**: append **`norm`** to **`grade_segs`** (downstream slicing **`seg[:2]`**, **`seg[2]`**, **`seg[3]`** unchanged).
   - Else: append the **original **`f`** (post-pipe-strip)** to **`meta`**.

⚠️ **Decision:** Normalize per pipe field independently (same sequencing as today), not “first contiguous run then rest.” Matches current behavior for interleaved stray tokens; satisfies acceptance for spaced tokens inside valid grade fragments. **`meta`** always receives originals so **`joined = "|".join(meta)`** for **`grades_encoded_notes`** and **`grades_meta`** `job_title`/`job_link`/`job_data` **`key:value`** parsing keep interior spaces/colons intact when the fragment is classified as **`meta`** (classification uses **`norm`** but storage uses **`f`**).

3. Do **not** add config keys or widen **`_GRADE_SEG`**.

4. **`tests/component/core/test_agent.py`** — in **`TestDecodePayload`**, add **`test_decodes_whitespace_inside_grade_tokens_preserves_meta`**:

   - **`grades`** only: **`ctx = {"batch_entities": _batch_entities("job-1"), "vector_labels": {"DT": "Duty", "GC": "Greatness"}}`**. Assert **`_decode_payload("evaluate_jd", "grades", "0|DT A5|GC-B4", ctx)`** yields **`jobs[0]["grades"]`** mirroring **`0|DTA5|GCB4`** (two vectors, **`A`** conf **`5`**, **`B`** conf **`4`**).
   - **`grades_meta`**: reuse the shape from **`test_decodes_grade_rows_and_meta_fields`** — payload **`0|CR A2|company-1|Sr Job Role|https://example.com/job|location:Remote`** with **`vector_labels` `CR`**. Assert **`grades`** row decodes **`CR A2`** as **`CRA2`**; assert **`job["job_title"] == "Sr Job Role`** (spaces preserved in metadata fragment).

5. **`build-astral` ritual:** Implement on **`dev-ada`**; cherry-picks land on **`origin/sub/AST-472/AST-483-normalize-grades-segment-whitespace-in-agent-decode`** via detached publish worktree (see **orientation-astral**); do **not** create local **`sub/*`** checkout in **`astral-ada`**.

## Self-Assessment

### Scope

**minor** — Touches **`_decode_payload`’s classification loop** and one **`TestDecodePayload` method** only; encoded-string contract stays the same modulo readability stripping.

### Conf

**high** — The bug is deterministic (`_GRADE_SEG` vs prettified tokens); fix is a bounded character delete before **`re.match`**.

### Risk

**Medium** — Incorrect classification could mishandle malformed model lines (`meta` routed as grade or graded bits as **`meta`**); mitigated by enforcing **`_GRADE_SEG`** on **`norm`** and keeping **`meta`** as original **`f`**.

---

## Self-review vs ASTRAL_CODE_RULES

- **§1.3 DRY** — Single **`norm`** expression inline or one local helper avoids duplicate replace chains elsewhere.
- **§2.x config** — No new literals needing **`config.py`**; normalization chars are ASCII-only deletes specified by the ticket, not enumerated business enums.
- **§2.7 consult** — **No **`render_verdict`** change.
- **§3.3 imports** — **`agent.py`** only; no utils import from core.
- **§3.5 naming** — Private helper **`_normalize_…`** if extracted; **`snake_case`**.

---

## Execution contract (for `build-astral`)

Bindings per **plan-astral** SKILL: stages in order, no extra files, stop on contradiction (comment parent **AST-472** with 🛑 header per skill).

---

## Review stub (build-astral §11)

Built by Ada Lovelace.

- **Publish ref:** `origin/sub/AST-472/AST-483-normalize-grades-segment-whitespace-in-agent-decode`
- **Publish tip:** current `origin/sub/AST-472/AST-483-normalize-grades-segment-whitespace-in-agent-decode` (canonical **feat:** `170e4ea7`; review-stub commits may extend the tip)
- **Integration branch:** **`dev-ada`** (`astral-ada`); feat cherry-picked as **`994cde99`** on integration.

**QA handoff (**`build-astral` §7**):** Betty — add **`TestDecodePayload.test_decodes_whitespace_inside_grade_tokens_preserves_meta`** per Stage 1 step 4 in this plan (**`grades`** line `0|DT A5|GC-B4` vs compact; **`grades_meta`** job_title **`Sr Job Role`** spaces preserved).

## Review

**Radia** · **`git diff`** `origin/dev...origin/sub/AST-472/AST-483-normalize-grades-segment-whitespace-in-agent-decode` (baseline `origin/dev` after fetch)

### What’s solid

- **_decode_payload`:** Matches plan and ticket: **`norm`** strips only ASCII space, hyphen, colon for **`_GRADE_SEG`** classification; **`grade_segs`** stores **`norm`** so **`seg[:2]` / `[2]` / `[3]`** align with compact wire tokens; **`meta`** retains the pipe-split **`strip()`** originals so **`grades_meta`** / **`grades_encoded_notes`** tails stay unmodified for classification beyond the grade-or-meta fork.
- **Tests:** **`test_decodes_whitespace_inside_grade_tokens_preserves_meta`** asserts embellished **`grades`** equals compact decode and asserts **`Sr Job Role`** survives on **`grades_meta`**.
- **Rubrics:** No **`except` suppression**, **`print()`**, **`src/ui`/`src.data`** cross-imports, or config creep in the core change.

### Issues

| Severity | Topic | Notes |
|----------|-------|--------|
| discuss | **`ASTRAL_TEST_BIBLE`** cross-ticket scope | Same publish tip adds **§7.13y–7.13za** for **AST-479 … AST-482** alongside **§7.13zb** for **AST-483**. Acceptable if parent-integration branch explicitly rolls documentation forward; otherwise consider splitting bible commits so **`AST-483`** stays normalization-only for audit/revert hygiene. |

### Recommended actions

- Confirm with Susan/Chuckles whether rolled-up bible sections on this **`sub/`** tip are intentional; if not, trim to **§7.13zb** (and mirrored narrow-run notes) before merge-up.

---

## Resolution

**2026-05-25** · **`resolve-astral`** (Hedy / `dev-hedy`; ticket assignee unchanged **Ada**) after Radia **`Review Posted`** ([AST-483 thread](https://linear.app/astralcareermatch/issue/AST-483)).

- **Product:** No further code change on this pass beyond merged **`feat(AST-483)`**; **`_decode_payload`** matches the approved plan (**`norm`** for **`_GRADE_SEG`** / **`grade_segs`**, originals in **`meta`**). Advisory items accepted as-is.
- **Discuss (Radia bible):** **`ASTRAL_TEST_BIBLE`** is workspace-wide coverage map — contiguous **§7.13** subsections (**AST-479**–**482**) beside **§7.13zb** by design and do **not** expand **`AST-483`** **`test-astral`** surface (**§7.13zb** + Betty’s narrow manifest + **`LOCKED_AT_100`** caveat is the revert pairing). **`origin/sub/AST-472/…AST-483…`** bible edits stay normalization-scoped (**§7.13zb**) per Radia hygiene; sibling **§7.13zc** (**AST-485**) and other rollup rows accumulate on integration branches (**`dev-*`**) rather than widening this **`sub/`** artifact.
- **§9a:** Dry-run **`merge-tree`** vs **`origin/dev`** (and **`origin/ftr/…`** when visible) completed before **`User Testing`** advance.
