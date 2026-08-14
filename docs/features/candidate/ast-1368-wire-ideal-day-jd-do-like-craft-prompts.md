# AST-1368 — Wire Ideal Day into JD / DO / LIKE craft prompts

**Linear:** [AST-1368](https://linear.app/astralcareermatch/issue/AST-1368/wire-ideal-day-into-jd-do-like-craft-prompts-add-ideal-day-to-the-set)
**Parent:** [AST-1360](https://linear.app/astralcareermatch/issue/AST-1360/add-ideal-day-to-the-set-of-candidate-context-strengths-priorities-etc) — Add `ideal_day` to the set of candidate context (strengths, priorities, etc.)
**Publish ref:** `sub/AST-1360/AST-1368-wire-ideal-day-jd-do-like-craft-prompts`
**Depends on:** [AST-1365](https://linear.app/astralcareermatch/issue/AST-1365/ideal-day-library-token-add-ideal-day-to-the-set-of-candidate-context) — `TOKEN_SOURCES["IDEAL_DAY"]` → `context.ideal_day` (must be on HEAD after `sync-child.sh` before build)

Put Ideal Day into the same candidate-context prompt material that already carries Strengths / Priorities / Deal Breakers / Backstory for the Job Description, DO, and LIKE craft rubric hops. On tip, that material is the **`craft_do_rubric.cache_prompt`** block; LIKE and Job Description reuse it via `{$CALLER_CACHE_A}` through the live craft chain. Edit the seed catalog only — no Python, no UI, no GET / joblist / meteorite craft rows.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `data/admin/agent_task.json` | On the `craft_do_rubric` row only: extend `cache_prompt` with an Ideal Day section + `{$IDEAL_DAY}` (peer of Strengths/Priorities/Deal Breakers/Back Story) | data (seed) |

**Out of scope (do not touch):**

| File / area | Why |
|-------------|-----|
| `craft_joblist_rubric` (even though its `cache_prompt` currently equals DO’s) | Parent / ticket boundaries: no joblist craft prompts |
| `craft_get_rubric`, `craft_evaluate_meteorite_rubric` | Boundaries: no GET / meteorite craft prompts |
| `craft_like_rubric` / `craft_jobdesc_rubric` prompt fields | They already set `cache_prompt` to `{$CALLER_CACHE_A}` (plus boundary `cache_prompt_b`); Ideal Day rides the caller cache once DO’s CACHE_A includes it |
| `grade_*` / consult prompts, `craft_resume_base` | Not JD/DO/LIKE craft |
| `src/utils/config.py` `TOKEN_SOURCES` / library keys | AST-1365 |
| Candidate Ideal Day UI / Topic Menu informs | AST-1366 / AST-1367 |
| `tests/` / bible | Betty |

## As-is (candidate-context inclusion today)

Live chain (from `run_next` on tip):

`craft_get_rubric` → `craft_do_rubric` → `craft_like_rubric` → `craft_evaluate_meteorite_rubric` → `craft_jobdesc_rubric` → `craft_joblist_rubric` → …

| Task | How Strengths/Priorities enter the hop |
|------|----------------------------------------|
| `craft_do_rubric` | Own `cache_prompt` lists BIO SUMMARY, STRENGTHS, PRIORITIES, DEAL BREAKERS, BACK STORY, BASE RESUME, LINKEDIN PROFILE TEXT with `{$…}` tokens |
| `craft_like_rubric` | `cache_prompt` = `{$CALLER_CACHE_A}` (resolved DO CACHE_A text) |
| `craft_jobdesc_rubric` | `cache_prompt` = `{$CALLER_CACHE_A}` (same chain; meteorite hop also forwards `{$CALLER_CACHE_A}`) |

⚠️ **Decision:** One seed edit on `craft_do_rubric.cache_prompt` is the correct inclusion class for all three named craft tasks. Duplicating Ideal Day into LIKE/JD rows would fight the caller-cache pattern; touching `craft_joblist_rubric` would violate in-scope-only.

## Stages

### Stage 0: Prerequisite gate (build-time, no commit)

**Done when:** After `sync-child.sh` for this publish ref, `TOKEN_SOURCES` contains `"IDEAL_DAY"` with `path` `context.ideal_day`.

1. Run sync-child as usual for this ticket.
2. Confirm Ideal Day token from AST-1365:

```bash
python3 -c "from src.utils.config import TOKEN_SOURCES; assert TOKEN_SOURCES['IDEAL_DAY']['path']=='context.ideal_day'"
```

3. If the assert fails (AST-1365 not yet on `origin/dev` / `origin/ftr/AST-1360` ancestry): **stop**. Comment on **parent AST-1360** with the Stage-blocked format naming this ticket and the missing token — do **not** add `IDEAL_DAY` to config here, and do **not** merge sibling `sub/AST-1360/AST-1365-*` by hand.

### Stage 1: Seed Ideal Day into DO candidate-context cache

**Done when:** `craft_do_rubric.cache_prompt` includes an Ideal Day section with `{$IDEAL_DAY}` immediately after the Back Story section and before Base Resume; no other `agent_task.json` rows change; JSON still loads; `craft_like_rubric` / `craft_jobdesc_rubric` / `craft_joblist_rubric` / GET / meteorite rows are byte-identical to pre-change (except unavoidable serializer normalization of the single edited string’s row if the dump touches only that object — prefer surgical edit so other rows are untouched).

1. In `data/admin/agent_task.json`, find the object with `"task_key": "craft_do_rubric"`.

2. Replace that row’s `cache_prompt` so the gated prose cluster gains Ideal Day **after Back Story, before Base Resume**. Exact target text (newlines and blank-line spacing must match the existing `\n\n\n` rhythm between sections):

```
{$FIRST_NAME}'s BIO SUMMARY:
{$BIO_SUMMARY}


{$FIRST_NAME}'s STRENGTHS:
{$STRENGTHS}


{$FIRST_NAME}'s PRIORITIES:
{$PRIORITIES}


{$FIRST_NAME}'s DEAL BREAKERS:
{$DEAL_BREAKERS}


{$FIRST_NAME}'s BACK STORY:
{$BACKSTORY}


{$FIRST_NAME}'s IDEAL DAY:
{$IDEAL_DAY}


{$FIRST_NAME}'s BASE RESUME:
{$BASE_RESUME}


{$FIRST_NAME}'s LINKEDIN PROFILE TEXT:
{$LINKEDIN_PROFILE_TEXT}
```

   Label style matches existing peers (`BACK STORY`, `DEAL BREAKERS` → `IDEAL DAY`). Token is exactly `{$IDEAL_DAY}` (AST-1365 registry).

3. **Edit discipline** (`astral.seed.agent-tables-in-repo-json` / prior AST-1252 noise lesson):
   - Change **only** `craft_do_rubric` → `cache_prompt`.
   - Do **not** rewrite the whole file through `json.dump` with `ensure_ascii=True` (that re-escapes unrelated prompts). Prefer a surgical string replace of the current DO `cache_prompt` value, or load/dump with `ensure_ascii=False` and identical 2-space indent **only if** a dry-run diff shows **no** unrelated row churn — if dry-run shows mass `\u2014` / punctuation churn, abort that approach and use surgical replace instead.
   - Do **not** change `run_next`, agent ids, other prompt fields, or `updated_at` unless the existing file tooling already requires a touch on that row (default: leave `updated_at` alone).

4. Do **not** edit `craft_like_rubric` or `craft_jobdesc_rubric` user_prompt instructional prose that mentions “strengths” / “priorities” in English. AC is candidate-context **material** (token block / caller cache), same class as today’s Strengths/Priorities inclusion — not a catalog rewrite of stage coaching copy.

5. Do **not** edit `craft_joblist_rubric.cache_prompt` even though it currently duplicates DO’s block.

6. Verify after edit:

```bash
python3 - <<'PY'
import json
from pathlib import Path
rows = json.loads(Path("data/admin/agent_task.json").read_text())
by = {r["task_key"]: r for r in rows}
cp = by["craft_do_rubric"]["cache_prompt"]
assert "{$IDEAL_DAY}" in cp
assert "IDEAL DAY" in cp
# Still after back story, before base resume
assert cp.index("{$BACKSTORY}") < cp.index("{$IDEAL_DAY}") < cp.index("{$BASE_RESUME}")
# Out-of-scope rows must not gain Ideal Day from this ticket
for k in ("craft_joblist_rubric", "craft_get_rubric", "craft_evaluate_meteorite_rubric"):
    blob = " ".join(str(by[k].get(f) or "") for f in (
        "cache_prompt", "cache_prompt_b", "cache_prompt_c", "cache_prompt_d",
        "nocache_prompt", "user_prompt", "system_prompt",
    ))
    assert "{$IDEAL_DAY}" not in blob, k
# LIKE + JD still forward caller cache A
assert "{$CALLER_CACHE_A}" in (by["craft_like_rubric"]["cache_prompt"] or "")
assert "{$CALLER_CACHE_A}" in (by["craft_jobdesc_rubric"]["cache_prompt"] or "")
print("ok")
PY
```

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

**Rubric:** plan-rubric
**Ticket:** AST-1368
**Overall:** APPROVED
**Publish ref:** `sub/AST-1360/AST-1368-wire-ideal-day-jd-do-like-craft-prompts` @ `482e445504320fa4296ce1cf2cd7f1e3e7578a90`

### Traceability
AC4→Stage 1 (`craft_do_rubric.cache_prompt` gains `{$IDEAL_DAY}` peer section; LIKE + Job Description inherit via existing `{$CALLER_CACHE_A}` chain — verified in plan Stage 1 §6); Stage 0 gates `TOKEN_SOURCES["IDEAL_DAY"]` from AST-1365.

### Findings

**acceptable** — Prior contaminated publish tip (`bb728bef`, sibling product + wrong plan) is documented on-ticket; `origin/sub/…/AST-1368-…` tip is now plan-only `482e4455`. Chuckles should keep publish ref on that clean SHA before build.

**acceptable** — `craft_joblist_rubric.cache_prompt` will diverge from DO (still no `{$IDEAL_DAY}`) while DO gains it; parent in-scope-only excludes joblist — plan’s explicit non-touch is correct.

**acceptable** — Meteorite hop prompt rows unchanged; enriched candidate-context text may flow through `{$CALLER_CACHE_A}` as today for Strengths/Priorities — not a meteorite prompt edit.

**acceptable** — Linear assignee Joan Clarke (validator identity collision only); no plan impact.

context_tokens≈52000

## Review (build stub)

**Built:** `astral-AST-1360` @ `d261670c` on `origin/sub/AST-1360/AST-1368-wire-ideal-day-jd-do-like-craft-prompts`

| Stage | Commit | Summary |
|-------|--------|---------|
| plan | `482e4455` | Plan doc |
| sync | `7828ca89` | Merge `origin/ftr/AST-1360-ideal-day-candidate-context` (IDEAL_DAY token) |
| 1 | `d261670c` | `craft_do_rubric.cache_prompt` + Ideal Day / `{$IDEAL_DAY}` |

**Verify:** plan Stage 1 §6 asserts — pass; surgical one-line `agent_task.json` diff (no mass re-serialize).

**Note for Betty:** seed catalog only; LIKE/JD inherit Ideal Day via `{$CALLER_CACHE_A}`; joblist/GET/meteorite rows intentionally unchanged.

