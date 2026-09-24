<!-- linear-archive: AST-1679 archived 2026-09-24 -->

## Linear archive (AST-1679)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1679/operative-save-hydrate-blob-retirement-craftparse-land-move-candidate  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** hedy  
**Priority / estimate:** None / 5  
**Parent:** AST-1677 — Move candidate_data.artifacts.resume_structure to artifact table  
**Blocked by / blocks / related:** parent: AST-1677; blocks: AST-1680

### Description

## What this implements

Wire structure through candidate operative validation + `get_candidate_current` hydrate on GET; intercept API PUT for operative save; stop durable library SoT writes for `artifacts.resume_structure`; retarget craft/parse and agent craft-persist structure land to the operative key. No backfill helper. Does not own job drafting token/filter consumers (#3) or React chrome. After #1. Mirror AST-1576’s split (structure half now operative) and AST-1633-style blob retirement.

## Citations

`patt.artifact.write-operative`; `patt.artifact.read-current`; `patt.artifact.manage-catalog`; `astral.standards.in-scope-only`; `stat.logging.info.entity`; `stat.logging.info.api`; `stat.logging.error`

## Scope

`src/core/candidate.py` — operative validate/save for the structure shape; hydrate overlay from `get_candidate_current`; gate durable library writes for `artifacts.resume_structure`; retarget craft/parse structure land; keep `resolve_resume_structure` honest against hydrated/current SoT. `src/core/agent.py` — craft-persist path that today library-saves structure lands structure via operative key (body path unchanged). `src/ui/api/api_candidate.py` — PUT intercept: pop library `artifacts.resume_structure`, operative save; GET hydrate overlays current structure for detail and `/resume_structure`.

## Acceptance criteria

3. **Operative round-trip** — After save via operative API/helper, `database.get_current_artifact('candidate', <id>, 'resume_structure')` returns a row whose `artifact_data` matches the saved structure dict; a second distinct save creates a new uuid and retires prior `current=1`. Fail: no row, blob-only write, or in-place UPDATE of the same uuid’s body.
4. **Hydrate on GET** — GET candidate detail (and GET `/api/candidates/<id>/resume_structure`) shows current structure after operative save. Fail: response still serves only pre-save blob and ignores current row.
5. **No durable blob SoT on save** — Successful structure save calls operative `save_artifact`; a post-save library read of raw candidate_data without hydrate is not relied on as SoT. Fail: structure persists only via library merge.
6. **Craft/parse land structure operatively** — Successful `craft_resume_base` / `parse_candidate_resume` persist structure through `candidate.artifacts.resume_structure` operative key; body still through `candidate.artifacts.base_resume`. Fail: structure written only to library blob on those paths.
7. **No backfill** — Candidates with only legacy blob structure and no artifact row still load that blob (or default) until re-save; no bulk migration script ships. Fail: deploy runs a backfill job or clears legacy blob on hydrate miss.

## Boundaries

After sibling #1. Does not own catalog registration (#1) or job drafting consult/tracker rewires (#3). No React chrome.

## Notes for planning

`candidate.artifacts.resume_structure` must already be in `ARTIFACT_CONFIG` before Stage 1 verify. Prefer sync from parent ftr.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1677-move-resume-structure-artifact-table`, child `sub/AST-1677/AST-1679-operative-save-hydrate-blob-retirement`. Created at dispatch-parent.

### Comments

#### radia — 2026-09-16T17:37:16.317Z
[code-rubric] PROCEED (Commit: 6b0ff391) operative hydrate clean

#### betty — 2026-09-16T17:32:55.256Z
`origin/sub/AST-1677/AST-1679-operative-save-hydrate-blob-retirement` @ `6b0ff391` · manifest green

#### betty — 2026-09-16T17:28:32.420Z
Product bug — holding Code Complete (not Tests Ready).

Leaf-only PUT `{artifacts: {base_resume: …}}` ingest always writes `arts["resume_structure"]`, then AST-1679 pops both `base_resume` and `resume_structure`. `body` empties, so the pilot save nested under `if body:` never runs — only structure operative-saves. AC6 body land via `candidate.artifacts.base_resume` is broken for leaf-only base_resume PUTs (and label-ingest PUTs with no other library fields).

Fix (api_candidate.py): move the pilot `save_candidate_data(..., artifact_key, pilot_body)` outside `if body:` — same placement as the new resume_structure / context-leaf operative saves.

Red gates on tip (green once fixed):
- `TestAst1679ResumeStructureOperativeApi::test_leaf_only_base_resume_put_still_saves_pilot_and_structure`
- `TestAst519ResumeStructureApi::test_put_base_resume_strips_orphan_keys`
- `TestAst1305LegacyLabelIngestApi::test_put_label_list_keeps_highlights_and_drops_prose_experience`
- `TestAst1305LegacyLabelIngestApi::test_put_title_keyed_dict_keeps_highlights_and_publications`

Green already: `TestAst1679ResumeStructureOperativeSaveHydrate`, rest of `TestAst1679ResumeStructureOperativeApi`, `TestAst1576CraftPersistOperative`, `TestAst1679CraftPersistResumeStructureOperative`.

`origin/sub/AST-1677/AST-1679-operative-save-hydrate-blob-retirement` @ `3ef8104f` · test SHA `4bec7f0d` · stay Code Complete · Hedy

#### joan — 2026-09-16T17:11:54.974Z
[plan-rubric] PROCEED (Commit: 2126fc8) operative hydrate blob retire

#### hedy — 2026-09-16T17:09:29.858Z
`origin/sub/AST-1677/AST-1679-operative-save-hydrate-blob-retirement` @ `2126fc8ddaca32ab9ad2054d9bb92820014da98b` · plan ready

---

# Operative save, hydrate, blob retirement + craft/parse land

**Linear:** [AST-1679](https://linear.app/astralcareermatch/issue/AST-1679)
**Parent:** [AST-1677](https://linear.app/astralcareermatch/issue/AST-1677) — Move candidate_data.artifacts.resume_structure to artifact table
**Publish ref:** `sub/AST-1677/AST-1679-operative-save-hydrate-blob-retirement`

Wire `artifacts.resume_structure` through candidate operative validation + `get_candidate_current` hydrate on GET; intercept API PUT for operative save; stop durable library SoT writes for that leaf; retarget craft/parse and agent craft-persist structure land to `candidate.artifacts.resume_structure`. Body still lands on `candidate.artifacts.base_resume`. No backfill helper. No React chrome. Does not own catalog (#1 AST-1678 — already on tip) or job drafting token/filter consumers (#3 AST-1680). Mirror AST-1576’s structure half (body already operative) and AST-1633-style blob retirement for an `artifacts.*` leaf with shape `resume_structure` / sentinel `structure_dict`.

## UAT fitness

- **AC restored:** Parent/child AC3 — "Operative round-trip — After save via operative API/helper, `database.get_current_artifact('candidate', <id>, 'resume_structure')` returns a row whose `artifact_data` matches the saved structure dict; a second distinct save creates a new uuid and retires prior `current=1`." Parent/child AC4 — "Hydrate on GET — GET candidate detail (and GET `/api/candidates/<id>/resume_structure`) shows current structure after operative save." Parent/child AC5 — "No durable blob SoT on save — Successful structure save calls operative `save_artifact`; a post-save library read of raw candidate_data without hydrate is not relied on as SoT." Parent/child AC6 — "Craft/parse land structure operatively — Successful `craft_resume_base` / `parse_candidate_resume` persist structure through `candidate.artifacts.resume_structure` operative key; body still through `candidate.artifacts.base_resume`." Parent/child AC7 — "No backfill — Candidates with only legacy blob structure and no artifact row still load that blob (or default) until re-save; no bulk migration script ships."
- **Correct outcome:** After PUT `{artifacts: {resume_structure: …}}` (or craft/parse land), a current `resume_structure` artifact row holds the normalized structure dict; GET detail and GET `/resume_structure` overlay that current onto `candidate_data.artifacts.resume_structure` for the existing editor contract; a second distinct save rotates current; identical re-save no-ops (AST-1635 shared); legacy blob-only candidates still resolve structure from the blob (or default) until first operative save.
- **Sibling check:** AST-1678 catalog + `BUILD_CONFIG["artifact_shapes"]["resume_structure"] == "structure_dict"` already on this tip (`candidate.artifacts.resume_structure` in `ARTIFACT_CONFIG`) — hand-verify before Stage 1. AST-1680 owns consult/tracker job-drafting rewires only — this ticket keeps `resolve_resume_structure` honest against hydrated/current SoT so #3 can consume without blob-only bypass. `base_resume` operative path and context-leaf operative paths stay intact except structure is added as a catalog-owned artifacts leaf.
- **Not sufficient:** Removing a stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Library-merge-only write of `artifacts.resume_structure` (or clearing the leaf without an artifact row) fails AC3/AC5. Reusing `resume_content` / `plain_text` validation instead of `normalize_resume_structure` invents the wrong shape. Touching `config.py` / React / `consult.py` / `tracker.py` / `database.py` invents sibling or out-of-scope work. Coat-check or bulk backfill violates AC7 / parent non-goals.

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/core/candidate.py` — operative validate/save for the structure shape; hydrate overlay from `get_candidate_current`; gate durable library writes for `artifacts.resume_structure`; retarget craft/parse structure land; keep `resolve_resume_structure` honest against hydrated/current SoT.
- `src/core/agent.py` — craft-persist path that today library-saves structure lands structure via operative key (body path unchanged).
- `src/ui/api/api_candidate.py` — PUT intercept: pop library `artifacts.resume_structure`, operative save; GET hydrate overlays current structure for detail and `/resume_structure`.

Every Files Changed row and every Stage step stays inside those three files. No `config.py`, no React, no `database.py`, no `consult.py`, no `tracker.py`, no other catalog keys, no pin/read-operative structure surface, no bulk migrate.

**Already on tip (do not re-invent):**

- `ARTIFACT_CONFIG["candidate.artifacts.resume_structure"]` with `body_shape: "resume_structure"` and `BUILD_CONFIG["artifact_shapes"]["resume_structure"] == "structure_dict"` (AST-1678).
- Shared str-path identical-to-current no-op before `save_artifact` (AST-1635) — applies once structure uses the str-path.
- `normalize_resume_structure` / `default_resume_structure` / `resolve_resume_structure` / PUT merge+normalize helpers — reuse; do not rewrite section contracts.
- Pilot `base_resume` operative pop + hydrate pattern in API / `get_candidate` (AST-1576) — structure hydrate is the Strengths-style miss→legacy twin under `artifacts`, not the base_resume miss→strip twin.

**Catalog prerequisite:** Before Stage 1 hand-verify:

```bash
python3 -c "from src.utils.config import ARTIFACT_CONFIG, BUILD_CONFIG; assert 'candidate.artifacts.resume_structure' in ARTIFACT_CONFIG; e=ARTIFACT_CONFIG['candidate.artifacts.resume_structure']; assert e['body_shape']=='resume_structure'; assert BUILD_CONFIG['artifact_shapes']['resume_structure']=='structure_dict'"
```

must exit 0 (true on this tip — AST-1678 is an ancestor). If missing at **build-child** start — stop, comment on parent AST-1677 with Stage blocked (catalog sibling not on tip); do **not** register the key in this ticket.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Module docstring + `_RESUME_STRUCTURE_ARTIFACT_KEY`; str-path `resume_structure` validate via `normalize_resume_structure`; entity info on structure operative save; dict-path strip `artifacts.resume_structure`; `hydrate_operative_resume_structure_for_response` + call from `get_candidate`; retarget `parse_candidate_resume` + `run_candidate_artifact_generation` craft land to operative key | core |
| `src/core/agent.py` | `persist_candidate_craft_hops` structure land → operative key (body path unchanged) | core |
| `src/ui/api/api_candidate.py` | Import hydrate; PUT `/data`: pop `artifacts.resume_structure` after normalize/ingest, library-merge remainder, then operative save; GET detail + rely on `get_candidate` hydrate for `/resume_structure`; api info when structure PUT completes | ui |

**Out of this ticket (do not touch):** `src/utils/config.py` (sibling Ada AST-1678 — already on tip); `consult.py` / `tracker.py` (sibling Katherine AST-1680); React Base Resume / JAR / ArtifactEditor; `database.py`; other artifact/context leaves; `tests/` / `docs/test-bible/**`; existing `base_resume` operative wiring (leave as-is except structure pop may run in the same PUT).

## Stage 1: Core — validate, hydrate, library gate, craft/parse land

**Done when:** `save_candidate_data(cid, "candidate.artifacts.resume_structure", <normalized dict>)` inserts a current artifact row whose `artifact_data` matches that dict; a second save with a distinct dict returns a new uuid and prior row is not current; identical re-save returns the same uuid without retire; invalid structure raises `ValueError` from `normalize_resume_structure` (no `save_artifact`); `get_candidate` overlays current structure onto `candidate_data.artifacts.resume_structure` when a row exists and leaves the legacy blob alone on miss; dict-path `save_candidate_data(cid, {"artifacts": {"resume_structure": …, "other": …}})` does not persist `resume_structure` into the library blob; `parse_candidate_resume` and UI craft land (`run_candidate_artifact_generation` craft_resume_base branch) persist structure via the operative key and body via `candidate.artifacts.base_resume`.

1. In `src/core/candidate.py` module docstring **In-scope** / operative bullets, after the Writing Preferences line, add one line that resume structure uses the same operative save + `get_candidate_current` hydrate path with catalog key `candidate.artifacts.resume_structure` (cite AST-1679). Do not rewrite base_resume or context-leaf bullets.

2. Near the other artifact-key constants (immediately below `_WRITING_PREFERENCES_ARTIFACT_KEY` is fine), add:

```python
_RESUME_STRUCTURE_ARTIFACT_KEY = "candidate.artifacts.resume_structure"
# Catalog-owned artifacts leaf — never durable library-merge SoT (AST-1679).
_ARTIFACTS_OPERATIVE_LEAVES = frozenset({"resume_structure"})
```

⚠️ **Decision:** Closed frozenset for artifacts leaves mirrors `_CONTEXT_OPERATIVE_LEAVES`. Do **not** add `base_resume` here (already gated by API pop + craft operative key; expanding that gate is out of scope). Do not hardcode the leaf string at every strip site beyond this frozenset + the module constant for logs/hydrate.

3. In `save_candidate_data` **str-path**, after the existing `plain_text` branch and **before** `artifact_type = artifact_key.rsplit(...)`, add:

```python
        elif entry["body_shape"] == "resume_structure":
            # AST-1679: structure dict — BUILD_CONFIG sentinel "structure_dict"; validate via normalize.
            if not isinstance(blob, dict) or not blob:
                raise ValueError("resume_structure body must be a non-empty dict")
            blob = normalize_resume_structure(blob)
```

Do **not** iterate `shape.items()` — sentinel is `"structure_dict"`, not a field map (AST-1678 comment). Leave `resume_content` / `plain_text` branches unchanged. `normalize_resume_structure` already raises `ValueError` on invalid sections/accent — let it propagate.

⚠️ **Decision:** Assign the normalized dict back to `blob` so identical-to-current compare and `save_artifact` persist the canonical structure (same object the GET contract expects), not a raw partial.

4. Still in the str-path, after a successful `database.save_artifact(...)` (existing assign-then-return), extend the entity info chain so structure also logs (`stat.logging.info.entity`), after the Writing Preferences branch:

```python
        elif artifact_key == _RESUME_STRUCTURE_ARTIFACT_KEY:
            logger.info(
                "%s | candidate %s: %s (batch: %s)",
                candidate_id,
                "resume_structure artifact saved",
                new_uuid,
                "-",
            )
```

Do **not** emit entity info on the AST-1635 identical-body no-op return path. Do **not** add entity info for `base_resume` or other keys on this ticket.

5. In the **dict-path** of `save_candidate_data`, after the existing `_CONTEXT_OPERATIVE_LEAVES` strip and before `steps = []`, gate durable library SoT for structure:

```python
    # AST-1679: catalog owns artifacts.resume_structure — never library-merge that leaf.
    arts = blob_merge.get("artifacts")
    if isinstance(arts, dict):
        cleaned_arts = {
            k: v for k, v in arts.items() if k not in _ARTIFACTS_OPERATIVE_LEAVES
        }
        if cleaned_arts:
            blob_merge["artifacts"] = cleaned_arts
        else:
            blob_merge.pop("artifacts", None)
```

Do **not** raise when `resume_structure` is present — strip silently (same spirit as context leaves / API pop). Other artifact keys pass through.

6. Add `hydrate_operative_resume_structure_for_response(candidate_id: str, cd: dict) -> None` immediately after `hydrate_operative_base_resume_for_response`:

```python
def hydrate_operative_resume_structure_for_response(candidate_id: str, cd: dict) -> None:
    """Overlay operative current resume_structure into candidate_data.artifacts (display only).

    Miss → leave legacy artifacts.resume_structure blob untouched (parent AC7 migration window).
    Hit → write current dict onto artifacts.resume_structure for the editor / resolve contract.
    """
    if not isinstance(cd, dict):
        return
    body = get_candidate_current(candidate_id, _RESUME_STRUCTURE_ARTIFACT_KEY)
    if body is None:
        return
    if not isinstance(body, dict):
        return
    arts = cd.get("artifacts")
    if not isinstance(arts, dict):
        arts = {}
        cd["artifacts"] = arts
    arts["resume_structure"] = body
```

⚠️ **Decision:** On miss, **do not** pop/clear `artifacts.resume_structure` (unlike `hydrate_operative_base_resume_for_response`, which strips blob on miss). Parent AC7: legacy blob until re-save; no coat-check fetch. After hydrate hit, `resolve_resume_structure(cd)` reads the overlaid current without a separate table path inside resolve.

7. In `get_candidate`, immediately after `hydrate_operative_base_resume_for_response(candidate_id, cd)`, add:

```python
    hydrate_operative_resume_structure_for_response(candidate_id, cd)
```

(Place before context-leaf hydrates is fine — order vs strengths does not matter for independent leaves.)

8. Retarget craft/parse structure land to the operative key (body path unchanged):

In `parse_candidate_resume`, replace:

```python
    save_candidate_data(candidate_id, {"artifacts": {"resume_structure": structure}})
```

with:

```python
    save_candidate_data(candidate_id, _RESUME_STRUCTURE_ARTIFACT_KEY, structure)
```

In `run_candidate_artifact_generation` (the `task_key == "craft_resume_base"` persist branch), replace the dict-path structure save the same way — keep the existing `TASK_CONFIG["craft_resume_base"]["artifact_key"]` body save.

Do **not** change `run_session_resume_parse` synthetic in-memory `artifacts.resume_structure` (no candidate bind / no durable write).

**Verify (hand):** with a candidate that has no resume_structure artifact, hydrate leaves legacy blob alone. After Stage 2, full PUT round-trip. After this stage, `parse_candidate_resume` / craft land should already create a current row.

## Stage 2: Agent craft-persist + API PUT intercept + GET hydrate + logging

**Done when:** Agent `persist_candidate_craft_hops` for `craft_resume_base` persists structure via `candidate.artifacts.resume_structure` and body via the existing artifact_key; `PUT /api/candidates/<id>/data` with body `{"artifacts": {"resume_structure": <partial or full>}}` creates/rotates a current `resume_structure` artifact row after the existing merge+normalize; library `candidate_data.artifacts.resume_structure` is not the SoT for that write; when the same PUT also lands `base_resume` and ingest updates structure, that ingested structure is operatively saved too; `GET /api/candidates/<id>` and `GET /api/candidates/<id>/resume_structure` show current structure when a row exists; no React files changed.

1. In `src/core/agent.py`, inside the `persist_candidate_craft_hops` success block that today does:

```python
                save_candidate_data(
                    str(index), {"artifacts": {"resume_structure": structure}}
                )
                save_candidate_data(str(index), artifact_key, content)
```

replace the structure call with:

```python
                save_candidate_data(
                    str(index),
                    "candidate.artifacts.resume_structure",
                    structure,
                )
```

Keep the body `save_candidate_data(str(index), artifact_key, content)` unchanged. Lazy import block already imports `save_candidate_data` / `split_craft_resume_base_payload` — do not import the private `_RESUME_STRUCTURE_ARTIFACT_KEY` from candidate; use the catalog string literal at the agent call site (same style as API context-leaf keys).

⚠️ **Decision:** Literal catalog key at agent/API call sites; private module constant stays inside `candidate.py` for hydrate/logs/str-path identity checks.

2. In `src/ui/api/api_candidate.py`, in the `from src.core.candidate import (` block, add `hydrate_operative_resume_structure_for_response` next to `hydrate_operative_base_resume_for_response`. Logger / `get_logger` already present — do not re-add.

3. In `get_candidate_detail`, immediately after `hydrate_operative_base_resume_for_response(candidate_id, cd)`, add:

```python
    hydrate_operative_resume_structure_for_response(candidate_id, cd)
```

(Idempotent with `get_candidate`'s hydrate — same double-call pattern as base_resume / context leaves.)

4. Do **not** rewrite `get_candidate_resume_structure` beyond relying on hydrate: it already calls `get_candidate(candidate_id)` then `resolve_resume_structure(cd)`. After Stage 1’s `get_candidate` hydrate, that path reads current. Confirm no second blob-only read is introduced.

5. In `update_candidate_data`, initialize `resume_structure_saved = False` next to the other `*_saved` flags. Inside the `if isinstance(arts, dict):` block, **keep** the existing resume_structure merge+normalize and base_resume ingest logic that may write `arts["resume_structure"]`. After those blocks (and after the `base_resume` pop into `pilot_body`), pop structure for operative save:

```python
                resume_structure_body = None
                if "resume_structure" in arts and isinstance(arts["resume_structure"], dict):
                    resume_structure_body = arts.pop("resume_structure")
                if not arts:
                    body.pop("artifacts", None)
```

If today’s code already has `if not arts: body.pop(...)` after the base_resume pop, fold the structure pop **immediately before** that emptiness check so a structure-only PUT clears `artifacts` the same way base_resume-only does.

⚠️ **Decision:** Pop **after** normalize + optional base_resume ingest so accent/partial section PUTs and ingest-updated structure both land as one normalized operative body. Do not library-merge the popped dict.

6. After the existing base_resume operative-save block (`if base_resume_in_save and pilot_body is not None: ...`), add:

```python
                if resume_structure_body is not None:
                    save_candidate_data(
                        candidate_id,
                        "candidate.artifacts.resume_structure",
                        resume_structure_body,
                    )
                    resume_structure_saved = True
```

Ensure a structure-only PUT (body emptied after pop) still reaches this save — same leaf-only pattern as context leaves (structure pop happens inside `if body:` / arts handling; if the only remaining work is the operative saves after library merge, keep the save outside a `if body:` that skipped when empty, or mirror base_resume’s placement which already runs after `if body: save_candidate_data(... library ...)`). Concrete placement on tip today: library `save_candidate_data` + base_resume operative save sit inside `if body:` after arts mutation; structure-only PUT currently leaves `arts` non-empty until pop — after pop, `body` may be `{}`. **Required behavior:** structure operative save must still run when `resume_structure_body is not None` even if library `body` is empty. Prefer: compute/pop structure inside the arts block (assign to an outer `resume_structure_body = None` initialized before `if body:`), then after the `if body:` library/base_resume block (sibling to context-leaf operative saves), call structure operative save when `resume_structure_body is not None`.

7. On the success path of `update_candidate_data` (after the try succeeds, immediately after the existing `if writing_preferences_saved:` api info block), if `resume_structure_saved`, emit one api info line (`stat.logging.info.api`):

```python
    if resume_structure_saved:
        logger.info(
            "%s | api %s completed: PUT %s",
            candidate_id,
            f"/api/candidates/{candidate_id}/data",
            200,
        )
```

Do **not** emit this info for GETs or for PUTs that did not touch structure. Existing context-leaf info lines stay as-is.

8. Do **not** change the existing `except Exception as e:` `logger.exception` format — it already includes `type(e).__name__` and `e`. Confirm it remains; no edit required unless somehow missing (`stat.logging.error`).

9. Do **not** edit React. Existing PUT `{ artifacts: { resume_structure: … } }` and GET `/resume_structure` keep working via intercept + hydrate.

**Verify (hand):**

```bash
# After save via PUT (use a real candidate_id and a normalized structure dict):
python3 -c "
from src.data import database
row = database.get_current_artifact('candidate', '<id>', 'resume_structure')
assert row and isinstance(row['artifact_data'], dict) and row['artifact_data'].get('sections')
"
# Second save with different sections/accent → new artifact_uuid; prior current=0
# Identical body → same uuid (AST-1635 shared no-op)
# GET /api/candidates/<id>/resume_structure reflects current after save
```

## Execution contract

- Execute steps in order within a stage; stages in order; one stage → one `code()` commit on the epic worktree, then push `origin/<publish-ref>`.
- Do not add files, touch Ada/Katherine scopes, register other catalog keys, or add a backfill/migrate script.
- On ambiguity or drift — stop, comment on parent AST-1677 with the Stage blocked template, wait.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Canon Scope (this ticket)

| Id | Role |
|----|------|
| `patt.artifact.write-operative` | pattern — read in full; structure via `save_candidate_data` str-path → `save_artifact` (identical no-op already shared) |
| `patt.artifact.read-current` | pattern — read in full; hydrate via `get_candidate_current` |
| `patt.artifact.manage-catalog` | pattern — read in full; retire blob authority for registered `candidate.artifacts.resume_structure` only (catalog entry from AST-1678) |
| `astral.standards.in-scope-only` | statute — resume_structure only; three named files |
| `stat.logging.info.entity` | statute — entity info on structure operative save |
| `stat.logging.info.api` | statute — api info when structure PUT completes |
| `stat.logging.error` | statute — exception once at PUT handler (already present; confirm) |

## Traceability

- Parent/child AC3 (operative round-trip) → Stage 1 §§3–4 + Stage 2 §§5–6 + verify (shared AST-1635 no-op)
- Parent/child AC4 (hydrate on GET) → Stage 1 §§6–7 + Stage 2 §§3–4
- Parent/child AC5 (blob not SoT on write) → Stage 1 §§2+5 + Stage 2 §§5–6
- Parent/child AC6 (craft/parse land operatively) → Stage 1 §8 + Stage 2 §1
- Parent/child AC7 (no backfill; legacy until re-save) → Stage 1 §6 miss path
- Sibling freeze / catalog ownership → Ada AST-1678 on tip; this ticket does not touch `ARTIFACT_CONFIG`
- Job drafting interfaces → Katherine AST-1680 (out of scope; hydrate/resolve honesty is the handoff)

## Joan validate

[plan-rubric]
**Ticket:** AST-1679
**Overall:** APPROVED
**Corpus:** fc0c368e59 · ticket ids partially outside clerk roster (draft patterns + statute paths resolved from worktree)
**Publish ref:** sub/AST-1677/AST-1679-operative-save-hydrate-blob-retirement @ 2126fc8ddaca32ab9ad2054d9bb92820014da98b

## Canon scores

patt.artifact.write-operative | A | | Stage 1 §3 str-path validate+normalize; AST-1635 identical no-op; save_artifact retire+insert
patt.artifact.read-current | A | | Stage 1 §6 hydrate via get_candidate_current; miss→legacy blob per AC7 (documented deviation from strip-on-miss)
patt.artifact.manage-catalog | A | | Stage 1 §2+5 dict-path strip + Stage 2 §5-6 API pop; blob retirement for resume_structure only; catalog from AST-1678
astral.standards.in-scope-only | A | | Three scoped files only; explicit out-of-scope fence for config/React/consult/tracker/database
stat.logging.info.entity | A | | Stage 1 §4 mirrors existing context-leaf entity info chain on successful save only
stat.logging.info.api | A | | Stage 2 §7 api info on structure PUT completion; matches writing_preferences pattern
stat.logging.error | A | | Stage 2 §8 confirm existing logger.exception on update_candidate_data (type+exc present on tip)

## Traceability

AC3→Stage 1 §§3-4 + Stage 2 §§5-6; AC4→Stage 1 §§6-7 + Stage 2 §§3-4; AC5→Stage 1 §§2+5 + Stage 2 §§5-6; AC6→Stage 1 §8 + Stage 2 §1; AC7→Stage 1 §6 miss path | Parent functional scope §§2-5 + AC3-8 via child slice; parent AC1-2 N/A (AST-1678); parent AC9 N/A (config); job drafting AC7 parent → AST-1680

## Findings

### acceptable — plan placement nuance
- **Location:** Stage 2 §5 snippet vs §6 placement note
- **Finding:** Step 5 snippet initializes `resume_structure_body` inside the `arts` block; step 6 requires outer init before `if body:` for structure-only PUT when library `body` empties after pop.
- **Recommendation:** No plan revision required — step 6 "Required behavior" is explicit; engineer follows §6 over the inline snippet scope.

### acceptable — canon infrastructure
- **Location:** canon_clerk roster
- **Finding:** `patt.artifact.*` and `astral.standards.in-scope-only` not in active clerk roster; logging statutes are. Bodies read from worktree paths.
- **Recommendation:** No plan change; scores based on resolved directive text.

context_tokens≈42000

## Review (build stub)

**Built:** `origin/sub/AST-1677/AST-1679-operative-save-hydrate-blob-retirement` @ `ce12e7ee5df425086d20caa9e8f65dbacf4c32d3`.

**Stages delivered:**
- Stage 1: resume_structure validate + hydrate + library gate + craft/parse land — `e846f7c3ca0f9858376f51b0c953d3d998e466e5`.
- Stage 2: agent craft-persist + API PUT intercept + GET hydrate + api info — `ce12e7ee5df425086d20caa9e8f65dbacf4c32d3`.

**Betty:** at **Code Complete** — cover operative `resume_structure` validate via `normalize_resume_structure`, `save_artifact` round-trip + retire prior current, identical-body no-op (AST-1635 shared), dict-path strips `artifacts.resume_structure` via `_ARTIFACTS_OPERATIVE_LEAVES`, hydrate overlays current / leaves legacy on miss (not base_resume strip-on-miss), PUT pop after normalize/ingest + operative path (incl. base_resume-ingest-updated structure), GET detail + `/resume_structure` via `get_candidate` hydrate, craft/parse + agent craft-persist structure operative / body base_resume; no backfill.

## Radia review

[code-rubric]
**Ticket:** AST-1679
**Publish ref:** 6b0ff39183311813af9e308e41ebea1d2b65b742
**Corpus:** fc0c368e59 · ticket pattern ids not in `canon_clerk` active roster (bodies resolved from `canon/directives/draft/` + `canon/directives/active/` for logging statutes)
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.write-operative | A | | |
| patt.artifact.read-current | A | | |
| patt.artifact.manage-catalog | A | | |
| astral.standards.in-scope-only | A | | |
| stat.logging.info.entity | A | | |
| stat.logging.info.api | A | | |
| stat.logging.error | A | | |

## Column diff vs plan stage

(aligned)

## Frame diff

(none)

## Findings

### advisory

- **Location:** `origin/dev...publish-ref` diff includes `src/utils/config.py`, `tests/component/utils/test_config.py`, `docs/features/foundation/ast-1678-*.md`
- **Finding:** Cumulative three-dot diff carries AST-1678 catalog ancestor commits on the epic branch union. AST-1679 code commits (`b800d2b7`–`88a73032`) touch only `candidate.py`, `agent.py`, `api_candidate.py` — no AST-1679 edits to config.
- **Recommendation:** Expected epic stacking; no AST-1679 action. Downstream reviewers should score 1679 product slice via those three files.

- **Location:** `canon/canon_clerk.py expand`
- **Finding:** `patt.artifact.*` and `astral.standards.in-scope-only` still fail clerk expand; logging statutes resolve from active roster.
- **Recommendation:** Infrastructure track only — out of AST-1679 scope.

- **Location:** `src/core/candidate.py` dict-path `_ARTIFACTS_OPERATIVE_LEAVES` strip
- **Finding:** `save_candidate_data(..., {"artifacts": {"resume_structure": …}})` strips the leaf without operative write (by design). All in-repo durable callers retargeted to str-path; grep shows no remaining dict-path structure saves in `src/`.
- **Recommendation:** AST-1680 / future callers must use str-path or API intercept — not a fix-now for this ticket.

## What's solid

- **Operative validate/save (AC3/AC5):** str-path `resume_structure` branch validates non-empty dict, runs `normalize_resume_structure`, shares AST-1635 identical-body no-op, then `save_artifact` retire+insert. `TestAst1679ResumeStructureOperativeSaveHydrate` covers round-trip, second-save rotation, identical uuid, library blob absence.
- **Hydrate (AC4/AC7):** `hydrate_operative_resume_structure_for_response` overlays current via `get_candidate_current`; miss leaves legacy blob (not base_resume strip-on-miss). Wired in `get_candidate` and `get_candidate_detail`. API tests confirm GET detail + `/resume_structure` overlay after operative save and legacy preservation on miss.
- **Blob retirement (AC5):** `_ARTIFACTS_OPERATIVE_LEAVES` dict-path strip + API pop after normalize/ingest; post-save raw library lacks `resume_structure`.
- **Craft/parse/agent land (AC6):** `parse_candidate_resume`, `run_candidate_artifact_generation` craft branch, and `agent.persist_candidate_craft_hops` use `candidate.artifacts.resume_structure` str-path; body stays on `base_resume` key. Agent integration test asserts both operative keys on craft persist.
- **API PUT leaf-only fix:** `base_resume` operative save moved outside nested `if body:` (commit `88a73032`) per plan §6 — regression-gated by `test_leaf_only_base_resume_put_still_saves_pilot_and_structure`.
- **Logging:** entity info on successful structure save only (mirrors context-leaf chain); api info on `resume_structure_saved` PUT; existing `logger.exception` with `type(e).__name__` + `e` on `update_candidate_data` failure unchanged.

## Recommended actions (for Chuckles — not Radia)

1. Post slim upshot and advance to **Review Posted** — catalog prerequisite (AST-1678) is on the branch ancestor; operative slice is complete.
2. No `resolve-child` product work indicated from canon pass; engineer may tick frame rows if any were added (none proposed here).
