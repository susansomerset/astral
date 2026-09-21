# AST-1756 — Stage jd_text fallback to ingress blob

**Linear:** [AST-1756](https://linear.app/astralcareermatch/issue/AST-1756/stage-jd-text-fallback-to-ingress-blob-stage-email-meteorite-enhancements)  
**Parent:** [AST-1753](https://linear.app/astralcareermatch/issue/AST-1753/stage-email-meteorite-enhancements) — stage_email_meteorite enhancements  
**Publish ref:** `sub/AST-1753/AST-1756-stage-jd-text-fallback-to-ingress-blob`

On text landable stage outcomes, when Ruth omits or blanks `jd_text`, set meteorite row `content` from the classify ingress blob (the subject+body text passed into `stage_meteorite`) instead of failing the map with `text scrap missing jd_text`. Prefer explicit non-empty `jd_text` when present. Does **not** edit agent_task prompts (**AST-1755**) or land → job title wiring (**AST-1757**).

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/core/meteorite.py` — **modified** — text-outcome stage map falls back to the classify ingress blob when `jd_text` is blank. Technical: thread the classify ingress blob into the jobs→row mapper; on text landable outcomes, when a jobs item's `jd_text` is blank/missing, set row `content` from that blob instead of failing with missing-`jd_text`; when `jd_text` is present, keep today's prefer-Ruth behavior.

All Files Changed / Stages stay inside that set.

**Out of scope (siblings / other epics):**

- `data/admin/agent_task.json` `stage_meteorite` prompts / `$RESPONSE_SCHEMA` — **AST-1755**
- Dispatch / public land paths passing `job_title=` into `tracker.save_meteorite_job` — **AST-1757** (do not edit `run_land_meteorite`, `land_meteorite`, or any Tracker save call site)
- URL scrape outcomes (`single_jd_with_more`, `link_list`) — already allow empty `jd_text` (`content: text or None`); do not change that branch
- Skip outcomes / `NOT_A_JOB` / error-row paths
- Adding new `logger.info` / title-or-fallback-specific chatter (`stat.logging.debug` stays on existing call/response style — no new debug lines for this fallback)

**Depends on:** none (Bang `!` with sibling #1). Disjoint edit sites in `meteorite.py` from **AST-1757**.

**AC partition (this ticket):** Parent AC5–AC6 only (AC1–4 → AST-1755; AC7–9 → AST-1757).

**Canon Scope (read at plan):** `patt.task.daisy-chain` (full — content must stay on the meteorite row from the same stage pass via the ingress blob / Ruth `jd_text` path; do not invent a parallel extract). `stat.logging.debug` — **id-only** for new lines (do not add fallback-specific debug chatter; keep existing call/response debug on `_classify_stage_blob` / `stage_meteorite` as already written).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/meteorite.py` | Thread ingress blob into `_map_classify_jobs_to_meteorite_rows`; text-outcome blank `jd_text` → `content` from blob; `stage_meteorite` passes `blob` at the sole call site | core |

## Stage 1: Ingress-blob fallback on text map

**Done when:** A text landable map (`single_jd_no_link` or `multi_jd_inline`) whose jobs item omits `jd_text` or returns blank/`None`/non-str produces a row dict with `content` equal to the stripped ingress blob and does **not** return `"text scrap missing jd_text"`. The same map with non-empty `jd_text` still sets `content` to that stripped `jd_text` (not the blob). URL / skip branches are unchanged. `python3 -m py_compile src/core/meteorite.py` succeeds. No edits outside `src/core/meteorite.py`.

1. In `src/core/meteorite.py`, change `_map_classify_jobs_to_meteorite_rows` signature to accept keyword-only `ingress_blob: str = ""` after the existing `*` fork (alongside `candidate_id`, `source_kind`, `source_id`, `timezone_key`):

```python
def _map_classify_jobs_to_meteorite_rows(
    outcome: str,
    jobs: List[Dict[str, Any]],
    *,
    candidate_id: str,
    source_kind: str,
    source_id: str,
    timezone_key: str = "",
    ingress_blob: str = "",
) -> Tuple[List[Dict[str, Any]], Optional[str]]:
```

2. In the **`text_source_ref_outcomes`** loop only (today’s block that returns `[], "text scrap missing jd_text"` when `text` is empty), replace the hard fail with:

   - Keep today’s `jd_text` read:  
     `text = (job.get("jd_text") or "").strip() if isinstance(job.get("jd_text"), str) else ""`
   - If `text` is non-empty: use it as `content` (unchanged prefer-Ruth behavior — AC6).
   - If `text` is empty: set  
     `fallback = ingress_blob.strip() if isinstance(ingress_blob, str) else ""`  
     If `fallback` is non-empty, use `fallback` as `content` (AC5).  
     If `fallback` is also empty, keep returning `[], "text scrap missing jd_text"` (degenerate: stage already rejects empty blob before classify; do not invent content).
   - Leave breadcrumb / `link` / electronic-contact mapping exactly as today. Do not touch the URL-outcome branch.

3. In `stage_meteorite`, at the sole call site of `_map_classify_jobs_to_meteorite_rows` (landable text/url success path), pass `ingress_blob=blob` (the same `blob` argument already passed into `_classify_stage_blob` — subject+body / assembled ingress text, **not** the `SOURCE_KIND`/`SOURCE_ID`/`CONTENT:` wrapper built inside `_classify_stage_blob`).

4. Do **not** edit `run_land_meteorite`, `land_meteorite`, `ingest_candidate_email_message` (beyond what already calls `stage_meteorite`), `_classify_stage_blob`, agent_task prompts, or Tracker save sites.

5. Verify from the epic worktree:

```bash
python3 -m py_compile src/core/meteorite.py

python3 - <<'PY'
from src.core.meteorite import _map_classify_jobs_to_meteorite_rows
from src.utils.config import STAGE_METEORITE_CONFIG

text_outcome = STAGE_METEORITE_CONFIG["text_source_ref_outcomes"][0]
blob = "Subject: Widget role\n\nFull JD body here."

# AC5 — blank jd_text → content is ingress blob; no map error string
rows, err = _map_classify_jobs_to_meteorite_rows(
    text_outcome,
    [{"jd_text": ""}],
    candidate_id="c1",
    source_kind="paste",
    source_id="s1",
    ingress_blob=blob,
)
assert err is None, err
assert rows and rows[0]["content"] == blob.strip()

# AC5 — missing jd_text key
rows, err = _map_classify_jobs_to_meteorite_rows(
    text_outcome,
    [{}],
    candidate_id="c1",
    source_kind="paste",
    source_id="s1",
    ingress_blob=blob,
)
assert err is None, err
assert rows[0]["content"] == blob.strip()

# AC6 — present jd_text wins over blob
rows, err = _map_classify_jobs_to_meteorite_rows(
    text_outcome,
    [{"jd_text": "  Ruth JD only  "}],
    candidate_id="c1",
    source_kind="paste",
    source_id="s1",
    ingress_blob=blob,
)
assert err is None, err
assert rows[0]["content"] == "Ruth JD only"

# Degenerate — blank jd_text and blank blob still errors the old string
rows, err = _map_classify_jobs_to_meteorite_rows(
    text_outcome,
    [{"jd_text": ""}],
    candidate_id="c1",
    source_kind="paste",
    source_id="s1",
    ingress_blob="   ",
)
assert rows == [] and err == "text scrap missing jd_text"

# URL branch unchanged — empty jd_text still allowed
url_outcome = STAGE_METEORITE_CONFIG["url_scrape_outcomes"][0]
rows, err = _map_classify_jobs_to_meteorite_rows(
    url_outcome,
    [{"job_link": "https://example.com/j", "jd_text": ""}],
    candidate_id="c1",
    source_kind="paste",
    source_id="s1",
    ingress_blob=blob,
)
assert err is None, err
assert rows[0]["content"] is None
print("AST-1756 map checks OK")
PY
```

⚠️ **Decision:** Pass the raw `stage_meteorite(..., blob=…)` argument as `ingress_blob`, not `_classify_stage_blob`’s `live_content` wrapper. Parent AC5 / Original brief say subject+body text Ruth classified as CONTENT — that is the caller blob before `SOURCE_KIND` / `SOURCE_ID` framing.

⚠️ **Decision:** On `multi_jd_inline`, every jobs item that blanks `jd_text` gets the **same** full ingress blob as `content`. Do not invent per-item JD slices — parent says do not invent JD text; the blob is the honest fallback for each blank item.

⚠️ **Decision:** No new `logger.debug` / `logger.info` lines for this fallback. Existing classify call/response debug already covers the stage pass (`stat.logging.debug` id-only for additions).

## Estimate

Confirm Chuckles estimate: 2 — agree
