# AST-1116 — UAT: Cover Letter preview fails field definitions for cover_letter

**Linear:** [AST-1116](https://linear.app/astralcareermatch/issue/AST-1116/uat-cover-letter-preview-fails-field-definitions-for-cover-letter)

**Parent:** [AST-1091](https://linear.app/astralcareermatch/issue/AST-1091/job-resume-artifact-cover-letter-and-suggested-responses-is-not-saved) (AC reference only)

**Publish ref:** `origin/sub/AST-1091/AST-1116-cover-letter-field-defs`

JAR Cover Letter tab passes `shapes_key: "cover_letter"` into `ArtifactEditor`, which loads `/api/shapes/candidates` and hard-fails when `detail.cover_letter` is missing or empty. Add the field-def list and normalize pin-resolved cover bodies onto the Subject/Letter spine so preview shows hop content.

## UAT fitness

- **AC restored:** After a successful `finalize_cover_letter` hop (chain may continue), `job_data.artifacts.cover_letter` equals that hop's RESPONSE `agent_data_id` and that id loads the hop body from `agent_data`. — and — A full successful daisy-chain that ran those three hops leaves all three pointer keys set; UAT surfaces that show Job Resume / Cover Letter / suggested answers resolve content via those ids without a manual PUT of the response body.
- **Correct outcome:** Cover Letter UAT preview shows the hop content (and editable field tabs) via the pin, not a field-definitions error.
- **Sibling check:** AST-1099 pin write and AST-1100 pin→body hydrate stay intact — this ticket only adds `DATA_SHAPES` field defs + cover normalize on display hydrate; does not change pin keys or GET hydrate entry points. Verified by not touching `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK`, `resolve_job_artifact_agent_data_body`, or job GET wiring beyond the existing hydrate call path.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Swallowing `shapeError` / blank editor; putting full cover JSON back on `job_data.artifacts` as the pin replacement strategy; inventing unrelated `DATA_SHAPES` keys without aligning `JOBS_RECOMMENDED_ARTIFACT_TABS.shapes_key`; setting `shapes_key` to `None` so raw dict tabs appear without defs (loses fixed Subject/Letter tabs and breaks edit/save contract).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `DATA_SHAPES["candidates"]["detail"]["cover_letter"]` field-def list (Subject / Letter / signature) | utils |
| `src/core/tracker.py` | In `hydrate_job_artifacts_for_display`, when resolved/left `cover_letter` value is a dict, replace with `normalize_cover_letter_artifact(...)` (display overlay only; no `save_job_data`) | core |

**Out of scope (do not touch):**

| Item | Owner |
|------|--------|
| Pin write / `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK` | AST-1099 |
| Print HTML / Materials print routes | AST-1117 |
| TASK_CONFIG `persist_in` | parent forbids |
| Unrelated JAR tabs / Job Resume `use_resume_structure` | excluded |
| `tests/` / `docs/test-bible/**` | Betty |

## Stage 1: Config — DATA_SHAPES cover_letter field defs

**Done when:** `GET /api/shapes/candidates` JSON includes non-empty `detail.cover_letter` with three fields keyed `Subject`, `Letter`, `signature`; `JOBS_RECOMMENDED_ARTIFACT_TABS` cover row still has `shapes_key: "cover_letter"`; `python3 -m py_compile src/utils/config.py` passes.

1. In `src/utils/config.py`, inside `DATA_SHAPES["candidates"]["detail"]`, immediately after the `"base_resume_structure"` list (before the closing of the `detail` dict), add:

```python
            # AST-1116: ArtifactEditor fixed tabs for JAR Cover Letter (shapes_key=cover_letter).
            # Keys match BUILD_CONFIG["artifact_shapes"]["cover_letter"] + normalize_cover_letter_artifact.
            "cover_letter": [
                {"key": "Subject", "label": "Subject", "type": "str"},
                {"key": "Letter", "label": "Letter", "type": "str"},
                {"key": "signature", "label": "Signature", "type": "str"},
            ],
```

2. Do **not** change `JOBS_RECOMMENDED_ARTIFACT_TABS` (keep `artifact_key` / `shapes_key` as `"cover_letter"`).
3. Do **not** add other `DATA_SHAPES` keys or invent a parallel shapes API.

⚠️ **Decision:** Field keys are `Subject` / `Letter` / `signature` (canonical job cover spine), not hop RESPONSE `re_line` / `body`. Hop aliases are mapped in Stage 2 via existing `normalize_cover_letter_artifact` so fixed tabs fill after pin hydrate and after human PUT (which already normalizes on save).

## Stage 2: Tracker — normalize cover body on display hydrate

**Done when:** After `hydrate_job_artifacts_for_display`, a pin string on `cover_letter` that resolves to `{re_line, body, signature}` (or Subject/Letter) becomes `{Subject, Letter, signature}` in the returned overlay dict; stored pins on disk are unchanged; `python3 -m py_compile src/core/tracker.py` passes.

1. In `src/core/tracker.py` `hydrate_job_artifacts_for_display`, after the existing pin-resolve loop (or inside it when applying a resolved body for `cover_letter`), ensure the display value for key `"cover_letter"` is normalized when it is a `dict`:

```python
    # After pin resolve loop (and also if cover_letter was already a body dict):
    cover = out.get("cover_letter")
    if isinstance(cover, dict):
        out["cover_letter"] = normalize_cover_letter_artifact(cover)
```

2. Place the normalize step **after** the pin-key loop so both (a) freshly resolved pin bodies and (b) legacy body dicts already under `cover_letter` get Subject/Letter keys for ArtifactEditor.
3. Do **not** call `save_job_data` / `save_job_artifact_cover_letter` from hydrate.
4. Do **not** change `resolve_job_artifact_agent_data_body` itself.

## Self-Assessment

**Scope — Single-Component:** `DATA_SHAPES` cover field defs in config + one normalize line in tracker display hydrate for the Cover Letter UAT tab.

**Conf — high:** Failure mode is proven (`shapes.detail.cover_letter` empty → `shapeError`); fix reuses `normalize_cover_letter_artifact` and the existing `shapes_key` / `/api/shapes/candidates` contract.

**Risk — Medium:** Wrong field keys leave tabs blank after the error clears; hydrate normalize bugs could mask raw RESPONSE shape for other consumers of the GET overlay (JAR is the intended consumer).

## Code rules check

| Rule | Notes |
|------|-------|
| §2.1 / `astral.config.config-source-of-truth` | Field defs live only in `DATA_SHAPES` |
| §3.3 / `astral.layers.import-direction` | No UI→data; FE still reads shapes API; normalize stays in core |
| `astral.patterns.coat-check-never-store-empty` | Hydrate still does not write; normalize is overlay-only |
| `astral.standards.in-scope-only` | Cover Letter field defs + hydrate normalize only |
| `astral.batch.entity-agent-responses-latest-only` | Pin remains id; body still from `agent_data` |
| `astral.layers.ui-config-driven-business-logic` | Tab still driven by config `shapes_key` |

## Review (build)

**Branch:** `origin/sub/AST-1091/AST-1116-cover-letter-field-defs`  
**Tip:** `e550a2c8`  
**Built:** Stages 1–2 — `DATA_SHAPES.candidates.detail.cover_letter` field defs; display-hydrate normalize via `normalize_cover_letter_artifact`. Tests/bible deferred to Betty.
