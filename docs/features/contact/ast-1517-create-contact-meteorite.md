<!-- linear-archive: AST-1517 archived 2026-10-02 -->

## Linear archive (AST-1517)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1517/create-contact-meteorite-estelle-needs-to-be-able-to-use-our-endpoints  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** katherine  
**Priority / estimate:** None / 3  
**Parent:** AST-1414 — Estelle needs to be able to use our endpoints.  
**Blocked by / blocks / related:** parent: AST-1414

### Description

## What this implements

Implement the `create_contact_meteorite` handler registered in sibling #1. Link path uses #2 scrape helper; page-text path lands as given. Existing meteorite landing state; existing analysis dispatch.

## Citations

`pattern.state.entity-state-transitions`, `astral.state.job-prior-states-enforced`, `astral.standards.debug-contract-gated`, `astral.standards.dry-and-focused-functions`

## Scope

`src/core/meteorite.py` (modified — `create_contact_meteorite` wrapper). Technical: candidate-scoped entrypoint; link mode calls gazer scrape helper then `create_meteorite_job`; text mode calls `create_meteorite_job` directly; returns create result dict for contact dispatch.

## Acceptance criteria

- [X] 3. Given a job URL, Estelle can emit `create_contact_meteorite` for the Slack-resolved candidate. The job exists in the meteorite landing state with stored visible text and the link. Meteorite analysis is queued via existing dispatch.
- [X] 4. Given pasted page text and no usable link, `create_contact_meteorite` lands a meteorite from that text (no fetch) for the same candidate.
- [X] 5. Style D on create contact-task paths when debug=True.

## Boundaries

- [X] Does not own markup/dispatch (sibling #1) or scrape helper (sibling #2).

## Notes for planning

After sibling #2.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1414-estelle-endpoints`, child `sub/AST-1414/AST-NNN-create-contact-meteorite`. Created at dispatch-parent.

### Comments

#### radia — 2026-08-27T03:54:01.936Z
[code-rubric] PROCEED (Commit: b7456464) Contact meteorite create clean

#### betty — 2026-08-27T03:49:38.156Z
origin/sub/AST-1414/AST-1517-create-contact-meteorite @ `b7456464` · contact create tests ready

#### joan — 2026-08-27T01:35:11.082Z
[plan-rubric] PROCEED (Commit: 2e8da926) meteorite create ready

#### katherine — 2026-08-27T01:32:57.430Z
`origin/sub/AST-1414/AST-1517-create-contact-meteorite` @ `2e8da9268e503b9ffba5dda08f875f5098a50305` · create meteorite plan

---

# AST-1517 — create_contact_meteorite

**Linear:** [AST-1517](https://linear.app/astralcareermatch/issue/AST-1517/create-contact-meteorite-estelle-needs-to-be-able-to-use-our-endpoints)  
**Parent:** [AST-1414](https://linear.app/astralcareermatch/issue/AST-1414/estelle-needs-to-be-able-to-use-our-endpoints) — Estelle needs to be able to use our endpoints  
**Publish ref:** `sub/AST-1414/AST-1517-create-contact-meteorite`

Child #3 of AST-1414: implement the `create_contact_meteorite` handler already registered by sibling AST-1515 as `CONTACT_TASK_CONFIG["create_contact_meteorite"]["handler"]` → `src.core.meteorite.create_contact_meteorite`. Link mode calls AST-1516 `contact_task_gazer_scrape` then `create_meteorite_job`; text mode calls `create_meteorite_job` with the pasted body and no fetch. Lands in existing `METEORITE_CONFIG["job_create_state"]` (`METEORITE_NEW`); analysis continues via existing meteorite dispatch (no new states, no new dispatch rows). Does **not** own markup/dispatch (AST-1515) or the scrape helper body (AST-1516).

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/core/meteorite.py` (modified — `create_contact_meteorite` wrapper). Technical: candidate-scoped entrypoint; link mode calls gazer scrape helper then `create_meteorite_job`; text mode calls `create_meteorite_job` directly; returns create result dict for contact dispatch.

**Out of scope:** `src/utils/config.py` / `src/core/contact.py` / `data/admin/agent_task.json` (AST-1515); `src/core/gazer.py` (AST-1516 — call `contact_task_gazer_scrape` only; do not edit); `src/core/tracker.py` (AST-1518); `land_meteorite` / email / mailbox paths; new job states or dispatch_task seeds.

**Depends on:** AST-1515 handler contract + AST-1516 `contact_task_gazer_scrape` (both present on epic worktree after `sync-child.sh` merges `origin/ftr/AST-1414-estelle-endpoints`). Dispatch calls `handler(astral_candidate_id, param, debug=debug)` and supports async via `asyncio.run`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/meteorite.py` | New public async `create_contact_meteorite`; private URL-vs-text helper; module docstring In-scope; Style D when `debug=True` | core |

## Stage 1: `create_contact_meteorite` handler

**Done when:** `from src.core.meteorite import create_contact_meteorite` succeeds; calling it with a URL-shaped param scrapes via `contact_task_gazer_scrape` then inserts a job in `METEORITE_NEW` with visible text + `job_link`; calling it with pasted page text inserts from that text with `job_link=None` and never opens a browser; failure paths return `ok=False` dicts (no raise into Contact); Style D emits only when `debug=True`.

1. In `src/core/meteorite.py` module docstring, add `create_contact_meteorite` (AST-1517 contact-task create) to the described public surface (keep existing land/ensure/create summary intact — one short clause is enough).

2. Add private URL detector (module-level helper, immediately above the new public handler section):

```python
def _contact_param_looks_like_url(param: str) -> bool:
    """True when param is a single-line URL / bare host-path (link mode)."""
```

   Rules (exact):

   - `s = (param or "").strip()`; empty → `False`.
   - If `"\n"` or `"\r"` in `s` → `False` (pasted multi-line page text).
   - If any whitespace (`" "` / `"\t"`) in `s` → `False` (prose with an embedded URL stays text mode — AC4 “no usable link” as the param itself).
   - If `"://"` in `s` → `True`.
   - Else: `True` only when `"."` in `s` and `s` does not start with `"."` (bare `host.tld/...` same scheme-fix path gazer uses).

   ⚠️ **Decision — URL vs text:** AST-1515 `param_hint` is “URL or page text (rest of line)” with no mode flag. Single-token URL-shaped params → link mode (scrape-first). Anything with whitespace/newlines, or no domain dot / scheme → text mode (no fetch). Do **not** scrape when Estelle pastes a paragraph that happens to contain a URL.

3. Add a labeled section `# ---- Contact-task create (AST-1517) ----` immediately **after** `create_meteorite_job` (before `_land_fetch_link_text` / land helpers). Add public async handler:

```python
async def create_contact_meteorite(
    astral_candidate_id: str,
    param: str,
    *,
    debug: bool = False,
) -> Dict[str, Any]:
```

   Signature matches AST-1515 dispatch: positional `(astral_candidate_id, param)` plus keyword-only `debug`.

4. Implement body as follows:

   a. `log = get_logger(__name__)`; `log.set_debug_flag(debug)`.

   b. `cid = (astral_candidate_id or "").strip()`. If empty: return
      `{"ok": False, "error": "no_candidate", "task_key": "create_contact_meteorite"}`.

   c. `raw = (param or "").strip()`. If empty: return
      `{"ok": False, "error": "param_required", "task_key": "create_contact_meteorite"}`.

   d. **Link mode** when `_contact_param_looks_like_url(raw)`:

      - Late-import inside the function (avoid import cycle — `gazer` already imports `create_meteorite_job` at module top):
        `from src.core.gazer import contact_task_gazer_scrape`
      - `scrape = await contact_task_gazer_scrape(cid, raw, debug=debug)`
      - If not a `dict` or `not scrape.get("ok")`: return
        `{"ok": False, "error": (scrape.get("error") if isinstance(scrape, dict) else "scrape_failed") or "scrape_failed", "task_key": "create_contact_meteorite", "mode": "link", "scrape": scrape if isinstance(scrape, dict) else None}` — do **not** call `create_meteorite_job`.
      - `visible = (scrape.get("visible_text") or "").strip()`; if empty: return
        `{"ok": False, "error": "empty_visible_text", "task_key": "create_contact_meteorite", "mode": "link", "scrape": scrape}`.
      - `link = (scrape.get("final_url") or scrape.get("url") or raw).strip()`
      - Call create (step e) with `html_body=visible`, `job_link=link`, `mode="link"`, and attach scrape summary fields on success (`page_status`, `url`, `final_url` from scrape).

      ⚠️ **Decision — still create when `page_status` is blocked/closed/missing:** Parent AC3 requires a job with stored visible text + link after a URL create; it does not gate on `ok` page status. Classifier outcome stays on the scrape payload / follow-up turn. Only hard-fail scrape (`ok=False`) or empty visible text blocks create.

   e. **Text mode** otherwise:

      - Call create (step f) with `html_body=raw`, `job_link=None`, `mode="text"`.
      - Do **not** import or call gazer / Playwright / `_land_fetch_link_text`.

   f. Shared create + normalize (both modes):

      ```python
      try:
          created = create_meteorite_job(
              cid,
              html_body,
              job_link=job_link,
              debug=debug,
          )
      except Exception as exc:
          return {
              "ok": False,
              "error": str(exc),
              "task_key": "create_contact_meteorite",
              "mode": mode,
          }
      ```

      Success return dict (exact keys):

      ```python
      {
          "ok": True,
          "task_key": "create_contact_meteorite",
          "mode": mode,  # "link" | "text"
          "astral_candidate_id": cid,
          "result": created,  # create_meteorite_job return dict (astral_job_id, company, state, …)
          # link mode only — omit keys in text mode:
          "url": scrape.get("url"),
          "final_url": scrape.get("final_url"),
          "page_status": scrape.get("page_status"),
      }
      ```

      ⚠️ **Decision — call `create_meteorite_job`, not `land_meteorite` / `tracker.save_meteorite_job`:** Ticket Technical scope names `create_meteorite_job` explicitly. That path is the same METEORITE_NEW carve-out gazer email ingest already uses; `METEORITE_NEW` is the meteorite landing state; existing `qualify_meteorite` dispatch claims that state — no new dispatch wiring in this ticket.

   g. **Style D (`debug=True` only):** two index headers (found → recorded), matching parent AC8 / sibling AST-1518 write-path shape:

      - `func="meteorite.create_contact_meteorite"`
      - `index=1`, `total=2`, `identifier=` truncated param (80 chars) or `cid`, `outcome="found"`; `debug_detail` lines: `mode=`, `param=` (via `truncate_debug_content` when long).
      - `index=2`, `total=2`, same identifier, `outcome=` either `recorded astral_job_id=… state=…` or `failed error=…`; on success `debug_detail` for `company=`, `job_link=`, and link-mode `page_status=`.

      Import `truncate_debug_content` from `src.utils.logging` if not already imported. No Style D when `debug=False`. Emit Style D on both success and soft-fail returns (so Contact debug shows the create attempt).

5. Do **not** edit `CONTACT_TASK_CONFIG`, contact dispatch, gazer, or tracker. Do **not** add stub alternate handler names. Do **not** change `create_meteorite_job` / `land_meteorite` behavior.

## Execution contract

- Execute stages and steps in order; one commit per stage on epic worktree; push `git push origin HEAD:sub/AST-1414/AST-1517-create-contact-meteorite` after each stage.
- No files outside Files Changed.
- Ambiguity, missing `contact_task_gazer_scrape`, or `create_meteorite_job` signature drift → stop, comment on **AST-1517** with Stage blocked format, wait.
- Test tree / bible: Betty only — engineer does not edit `tests/` or `docs/test-bible/**`.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1517
**Overall:** APPROVED
**Publish ref:** `sub/AST-1414/AST-1517-create-contact-meteorite` @ `2e8da9268e503b9ffba5dda08f875f5098a50305`

## Traceability
AC3 (parent AC3)→S1 link mode; AC4 (parent AC4)→S1 text mode; AC5 (parent AC8)→S1 Style D; parent AC1–2,6–8→N/A (siblings); stage maps to child Purpose / create wrapper slice only.

## Findings

### acceptable — URL vs text split
`_contact_param_looks_like_url` rejects whitespace/newlines so pasted prose stays text mode (AC4); single-token URL shapes route through `contact_task_gazer_scrape` with late import (avoids `gazer`↔`meteorite` cycle at module load).

### acceptable — Create path and landing state
Calls `create_meteorite_job` (not `land_meteorite` / `save_meteorite_job`); lands `METEORITE_NEW` via existing carve-out; `qualify_meteorite` on `METEORITE_NEW` satisfies parent AC3 analysis queue; blocked/closed/missing `page_status` does not block create when scrape succeeds with visible text.

### acceptable — Boundaries, errors, debug
Single-file scope; scrape hard-fail / empty visible text return `ok=False` without raising into Contact; handler signature matches AST-1515 dispatch; Style D gated on `debug=True`; does not edit config/contact/gazer/tracker.

context_tokens≈58000

## Review (build stub)

| Field | Value |
|-------|-------|
| Status | Code Complete |
| Publish ref | `origin/sub/AST-1414/AST-1517-create-contact-meteorite` |
| Tip | `4ddaed5c` |
| Branch | `sub/AST-1414/AST-1517-create-contact-meteorite` |

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `4ddaed5c` | `create_contact_meteorite` — URL scrape→create / text→create; Style D |

**Betty note:** component tests for link vs text mode, scrape-fail soft returns, METEORITE_NEW landing + job_link, Style D on debug=True deferred to qa-child.

## Radia review

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1517
**Publish ref:** `sub/AST-1414/AST-1517-create-contact-meteorite` @ `b7456464e579619c287cd5972829542f6b3da187`
**Overall:** CLEAN

## Statutes checked

Full-set statute sweep — all scoped/universal statutes conform or not-applicable. Key conforms: `astral.standards.debug-contract-gated`, `astral.standards.dry-and-focused-functions`, `astral.layers.import-direction` (late-import breaks gazer↔meteorite cycle), `astral.state.core-decides-transitions` (METEORITE_NEW carve-out via existing `create_meteorite_job`).

## Plan adherence

Stage 1 implemented in `4ddaed5c`: URL detector, link mode (scrape→create), text mode (direct create), Style D on debug=True, soft-fail returns for scrape/empty visible text. Betty `TestAst1517CreateContactMeteorite` covers URL detector, text/link modes, scrape soft-fail, Style D.

## Findings

*(none — fix-now / discuss)*

## What's solid

- URL-vs-text split prevents scraping pasted prose that embeds a URL (whitespace/newline guard).
- Late-import of `contact_task_gazer_scrape` avoids module-load cycle.
- Scrape failures return structured payloads — Contact turn stays alive.
- Link mode uses `create_meteorite_job` → `METEORITE_NEW` via existing carve-out.
- Style D matches sibling AST-1518 dual-index write-path shape.

context_tokens≈44000

## Bug: AST-2061 — Estelle pinhole: meteorite-only writes, nh3 sanitize, private-channel gate

**Linear:** [AST-2061](https://linear.app/astralcareermatch/issue/AST-2061) (fix child of orphaned bug [AST-2055](https://linear.app/astralcareermatch/issue/AST-2055)) · **Publish ref:** `sub/AST-2055/AST-2061-estelle-pinhole` · **Parent ftr:** `ftr/AST-2055-estelle-pinhole`

Scope is AST-2061 `## Scope` (amended at `[scope-gate]` to add `src/external/slack.py`): `requirements.txt`, `src/utils/config.py`, `src/core/meteorite.py`, `src/external/slack.py`, `src/core/contact.py`. Nothing else is edited.

### As-is

Contact Estelle has write paths beyond `meteorite` (state on `origin/dev` `2fd5c63e7`):

1. **`job` write.** The `~~/create_contact_meteorite <url or text>~~` markup (`CONTACT_TASK_CONFIG["create_contact_meteorite"]`, listed in every turn prompt under "Available contact tasks") dispatches to `src.core.meteorite.create_contact_meteorite` (this doc's Stage 1). That function calls `create_meteorite_job`, which writes a `job` row immediately and skips the meteorite stage/land pipeline.
2. **`candidate` write.** `CONTACT_CONFIG["skills"]` (`save_candidate_profile`, `save_candidate_contact`) is listed in the turn prompt as "Available Contact skills (ACL)". `run_contact_estelle_turn` step **e** executes the model's `skill_calls` through `run_contact_skill`, which calls `save_candidate_data`.
3. **Raw text stored.** `insert_slack_meteorite` (the `/add-job` payload), the `contact_land_meteorite` blob (into `stage_meteorite`), and `apply_paste` (BOT_BLOCKED → READY) save Contact text with no library sanitizer. `apply_paste` gets raw Slack text: its `<https://…|label>` link markup is never unwrapped, so `_normalize_apply_paste_content`'s homegrown `re.sub(r"<[^>]+>", " ", …)` deletes those URLs.
4. **Public channels accepted.** `_handle_slack_event_body` limits `message` to DMs (`_is_dm_message`), but accepts `app_mention` in any channel, public included. That means a command, an Estelle turn, and saves.

### To-be

- Estelle writes only `meteorite`: insert (`/add-job` → `insert_slack_meteorite`, `land_calls` → `stage_meteorite`) plus the existing BOT_BLOCKED → READY `apply_paste` update. No Contact-reachable path calls `create_meteorite_job` or writes `job` / `candidate`.
- Every Contact-originated meteorite write goes through **one** `nh3`-backed helper in `src/core/meteorite.py` before saving.
- `app_mention` is honored only in DMs (`im`) and private channels (`group`), read from `CONTACT_CONFIG["allowed_channel_types"]`. A public-channel mention is rejected before any resolve, command, turn, or save.
- An import-time assert in `config.py` keeps the pinhole closed.
- Read tasks (`get_job_by_pattern`, `get_job_data`, `get_company_data`, `get_candidate_data`) and `gazer_scrape` are unchanged.

### Repro

Fixtures only (no DB seed needed; component tests patch handlers):

1. **Job leak.** Mock the Estelle turn reply to `"On it ~~/create_contact_meteorite https://jobs.example.com/123~~"` for bound candidate `cand-1`, then run `run_contact_estelle_turn(channel="D1", text="here's a job", astral_candidate_id="cand-1")`. Today `run_contact_task_dispatch` resolves `src.core.meteorite.create_contact_meteorite`, which calls `create_meteorite_job("cand-1", …)` and returns a `job` row.
2. **Candidate write.** Mock the parsed response to `{"reply": "ok", "skill_calls": [{"skill_key": "save_candidate_contact", "fields": {"contact.contact_email": "x@evil.test"}}]}`. Today `save_candidate_data("cand-1", {"contact": {"contact_email": "x@evil.test"}})` is called.
3. **Raw text.** Call `insert_slack_meteorite("cand-1", "<img src=x onerror=alert(1)>Senior Eng", source_id="C1:1.0")`. Today the stored row's `content` is the literal markup.
4. **Public channel.** Call `handle_slack_event({"event_id": "Ev1", "event": {"type": "app_mention", "user": "U1", "channel": "C1PUBLIC", "ts": "1.0", "text": "<@UBOT> /add-job https://x.io/1"}})` with `conversations.info` answering `{"ok": true, "channel": {"is_private": false}}`. Today this is accepted and `insert_slack_meteorite` runs.

### Root cause

- AST-1517 (this doc, Stage 1) wired a Contact task straight to `create_meteorite_job`, the legacy email-ingest job creator. It predates the AST-2032/AST-2034 raw-NEW meteorite path and was never retired.
- AST-1071 gave Contact a write ACL onto `candidate`, which the To-be rules out (candidate is read-only to Estelle).
- No sanitization library exists in the backend (`beautifulsoup4` is a parser). Each write path stores its input as-is, apart from a homegrown regex in `apply_paste`.
- `app_mention` payloads carry no `channel_type`, and the gate never checked channel kind for mentions. Modern private channels use `C…` ids, the same as public ones, so the id alone can't decide.

### Proposed change

Execute in this order. One commit for the whole fix on the epic worktree (`fix(AST-2061): …`), pushed to `origin/sub/AST-2055/AST-2061-estelle-pinhole`.

#### 1. `requirements.txt`

Under `# Web scraping & automation`, directly after `beautifulsoup4>=4.12.0`, add:

```text
nh3>=0.3.7,<0.4  # HTML sanitizer (Rust ammonia); Contact meteorite writes (AST-2061)
```

`0.3.7` is the current release (verified with `pip index versions nh3`). The `<0.4` ceiling matches the `anthropic` / `httpx` pinning style.

#### 2. `src/external/slack.py`: new `fetch_channel_type`

- Add `"fetch_channel_type"` to `__all__`, after `"fetch_user_profile"`. Add `channel type lookup (``fetch_channel_type``)` to the module docstring's Production list.
- Add directly after `fetch_user_profile`:

```python
def fetch_channel_type(channel: str) -> str:
    """GET conversations.info; return Slack channel_type: im | mpim | group | channel.

    Read-only. Raises on blank id, HTTP failure, or ok:false — callers fail closed.
    """
    require_controlled_external_io("slack.fetch_channel_type")
    ch = (channel or "").strip()
    if not ch:
        raise ValueError("channel is required")
    payload = _slack_bot_get("conversations.info", {"channel": ch})
    if not payload.get("ok"):
        raise RuntimeError(_slack_error("conversations.info", payload))
    info = payload.get("channel") if isinstance(payload.get("channel"), dict) else {}
    # mpim is also is_private, so check it before the private-channel branch.
    if info.get("is_im"):
        return "im"
    if info.get("is_mpim"):
        return "mpim"
    if info.get("is_private") or info.get("is_group"):
        return "group"
    return "channel"
```

The returned values are Slack's own `message.*` event `channel_type` vocabulary, so one allowlist serves both event shapes. No new OAuth scopes are needed: `channels:read` and `groups:read` are already granted (AST-1814).

#### 3. `src/utils/config.py`

a. **`CONTACT_CONFIG["skills"]`:** replace the two entries with an empty dict. Keep the key, because `contact_skills()`, `contact_skill_meta()`, `run_contact_skill()` and the admin `/api/admin/contact/skills` routes read it. Update the comment above it:

```python
    # AST-2061: Estelle has no write skills — candidate is read-only to Contact.
    # Map kept (empty) for contact_skills()/admin routes; keys must never appear in TASK_CONFIG.
    "skills": {},
```

b. **`CONTACT_CONFIG["allowed_channel_types"]`:** add directly after `"bot_event_types"`:

```python
    # AST-2061: Slack channel_type values where Estelle acts (DM + private channel).
    # app_mention carries no channel_type — Contact looks it up via conversations.info.
    "allowed_channel_types": ("im", "group"),
```

   Add an assert after the `bot_event_types` assert:

```python
assert isinstance(CONTACT_CONFIG["allowed_channel_types"], tuple) and CONTACT_CONFIG["allowed_channel_types"]
assert set(CONTACT_CONFIG["allowed_channel_types"]) <= {"im", "mpim", "group", "channel"}
assert "channel" not in CONTACT_CONFIG["allowed_channel_types"]  # public channels never (AST-2061)
```

c. **Skill asserts:** delete only the `save_candidate_profile` subset assert (`assert set(CONTACT_CONFIG["skills"]["save_candidate_profile"]["allowed_paths"]).issubset(…)`, 3 lines), because it would raise `KeyError` once the map is empty. Keep the `isinstance(…, dict)` assert, both `for _skill_key …` loops (they no-op when the map is empty), and the commands-vs-skills collision assert.

d. **`CONTACT_TASK_CONFIG`:** delete the `"create_contact_meteorite"` entry (8 lines).

e. **Pinhole assert:** add directly after the AST-2035 `for _cmd_id in CONTACT_CONFIG["commands"]: assert _cmd_id not in CONTACT_TASK_CONFIG` block (both configs exist by then):

```python
# AST-2061 pinhole: every Contact command/task handler must be listed here, keyed by dotted path.
# Writes are meteorite-only (never create_meteorite_job / job / candidate); everything else reads.
_CONTACT_PINHOLE_HANDLERS = {
    "src.core.meteorite.insert_slack_meteorite": "write meteorite (NEW)",
    "src.core.gazer.contact_task_gazer_scrape": "read (external fetch, no platform write)",
    "src.core.tracker.contact_task_get_job_by_pattern": "read job",
    "src.core.tracker.contact_task_get_job_data": "read job",
    "src.core.tracker.contact_task_get_company_data": "read company",
    "src.core.tracker.contact_task_get_candidate_data": "read candidate",
}
assert all(
    _h.startswith("src.core.meteorite.") for _h, _kind in _CONTACT_PINHOLE_HANDLERS.items()
    if _kind.startswith("write")
)
for _h in [m["handler"] for m in CONTACT_TASK_CONFIG.values()] + [
    m["handler"] for m in CONTACT_CONFIG["commands"].values()
]:
    assert _h in _CONTACT_PINHOLE_HANDLERS, f"Contact handler outside pinhole: {_h}"
```

   ⚠️ **Decision: an allowlist, not a denylist.** The AC asks the assert to fail when a handler "points at a non-read path outside `src.core.meteorite` (for example `create_meteorite_job`)". `create_meteorite_job` is itself in `src.core.meteorite`, so a module-prefix rule can't express it. An explicit path → kind allowlist fails on `create_meteorite_job`, `land_meteorite`, `create_contact_meteorite`, and any new unreviewed handler. Adding a handler means consciously classifying it here. The second assert guarantees every allowlisted write lives in `src.core.meteorite`.

#### 4. `src/core/meteorite.py`

a. **Delete** `_contact_param_looks_like_url` and the whole `# ---- Contact-task create (AST-1517) ----` section, i.e. `create_contact_meteorite` (current lines ~416–551). Delete the module docstring line `create_contact_meteorite (AST-1517 contact-task create) wraps scrape-or-text → create.` and add `sanitize_contact_text (AST-2061): nh3 plain-text sanitize for every Contact-originated meteorite write.` `create_meteorite_job` is unchanged, because gazer email ingress still uses it.

b. **Imports:** add `import html as html_module` to the stdlib block (alias matches `src/utils/formatting.py` and avoids shadowing `html_body` locals), and `import nh3` as a third-party import between the stdlib and `src.*` blocks.

c. **New helper:** place it directly above `insert_slack_meteorite`:

```python
def sanitize_contact_text(text: str) -> str:
    """Plain text for Contact-originated meteorite writes (AST-2061) — nh3, no allowed tags.

    Callers unwrap Slack <url|label> link markup first (nh3 would read it as a tag).
    unescape → nh3.clean(tags=set()) → unescape: Slack's entity encoding is undone so
    encoded markup (&lt;script&gt;) is stripped, not stored; URLs keep a literal &.
    """
    raw = text if isinstance(text, str) else ""
    # nh3 drops every tag (keeps inner text), drops <script>/<style> content and comments.
    cleaned = nh3.clean(html_module.unescape(raw), tags=set())
    return html_module.unescape(cleaned).strip()
```

   ⚠️ **Decision: entity handling (verified against `nh3==0.3.7` in a scratch venv).** `nh3.clean` returns HTML-escaped text, so storing it raw would turn `https://x.io/job?id=1&src=slack` into `…&amp;src=…` and break the stage/scrape link path. Slack also delivers user-typed `<script>` as `&lt;script&gt;`, which `nh3` alone would keep. Hence: unescape → clean → unescape once. Probe results:

   | Input | Stored |
   |-------|--------|
   | `https://x.io/job?id=1&amp;src=slack` | `https://x.io/job?id=1&src=slack` |
   | `&lt;script&gt;alert(1)&lt;/script&gt;Senior Eng` | `Senior Eng` |
   | `<b>Senior</b> Eng <img src=x onerror=alert(1)> AT&amp;T` | `Senior Eng  AT&T` |
   | `<@U123> salary 1 < 2` | `<@U123> salary 1 < 2` |
   | `line1\n\nline2  <!-- c -->` | `line1\n\nline2` |
   | `&amp;lt;script&amp;gt;x` (double-encoded) | `<script>x` |

   **Accepted residual:** double-encoded input comes out as inert *plain text* that looks like a tag (last row). Stored content is plain text for Ruth/scrape, never rendered as raw HTML. Closing the residual would need repeated passes (an unbounded loop or a pass limit), which is a heuristic needing Susan's approval, so it's not added. **No length cap** (AST-2055 Boundaries).

d. **`insert_slack_meteorite`:** change `body = payload.strip() if isinstance(payload, str) else ""` to `body = sanitize_contact_text(payload)`. The `payload is required` miss therefore also fires when sanitizing leaves nothing (for example a payload that was only `<script>…</script>`). Update the comment `# Link vs text is Ruth's call at the stage hop — store the payload raw.` to `# Link vs text is Ruth's call at the stage hop — store the sanitized payload (AST-2061).` The payload is already Slack-unwrapped by `parse_contact_command` (`_SLACK_LINK_RE`).

e. **`_normalize_apply_paste_content` (folded onto the helper; `apply_paste` is its only caller):**

```python
def _normalize_apply_paste_content(raw: str) -> str:
    text = (raw or "").strip()
    if not text:
        return ""
    if "<" in text and ">" in text:
        # Gmail/board paste HTML → nested auto-links unwrapped before nh3 strips markup.
        text = normalize_pasted_list_email_html(text)
        text = re.sub(r"[ \t]+", " ", sanitize_contact_text(text))
        return text.strip()
    text = sanitize_contact_text(text)
    return "\n\n".join(line.strip() for line in text.splitlines() if line.strip())
```

   The homegrown `re.sub(r"<[^>]+>", " ", text)` tag strip is gone; `nh3` is the only markup remover. `normalize_pasted_list_email_html` (entity-unescape + Gmail nested auto-link unwrap, AST-1131) and the whitespace / blank-line shaping stay, since they are formatting, not sanitizing. `apply_paste` itself is unchanged: its `content = _normalize_apply_paste_content(pasted_text)` now sanitizes, and the existing `empty_paste` miss covers sanitized-to-empty.

#### 5. `src/core/contact.py`

a. **Import** `fetch_channel_type` in the `from src.external.slack import (…)` block, alphabetically after `fetch_full_conversation_history`.

b. **Slack link unwrap before `apply_paste`.** Add a one-line helper next to `_SLACK_LINK_RE`, and use it in `parse_contact_command` too (`payload = _unwrap_slack_links(m.group(2) or "").strip()`):

```python
def _unwrap_slack_links(text: str) -> str:
    """Slack <http(s)://…|label> / <http(s)://…> → bare URL (before nh3 sanitize, AST-2061)."""
    return _SLACK_LINK_RE.sub(r"\1", text if isinstance(text, str) else "")
```

   - `try_meteorite_apply_paste_from_slack`: `apply_paste(int(row["id"]), _unwrap_slack_links(text), debug=debug)`.
   - `run_contact_estelle_turn` land loop: `apply_paste(int(paste_row["id"]), _unwrap_slack_links(text), debug=debug)`.

c. **`contact_land_meteorite`:** after the blob is assembled (after the `Employer:` append) and before the `if not blob.strip():` check, insert:

```python
    # AST-2061: one nh3 sanitize point for every Contact meteorite write.
    from src.core.meteorite import sanitize_contact_text

    blob = sanitize_contact_text(_unwrap_slack_links(blob))
```

   Then fold the existing late `from src.core.meteorite import stage_meteorite` into this import (`import sanitize_contact_text, stage_meteorite`). The import stays late because `meteorite.py` late-imports `contact`. The existing `blob is required` error covers sanitized-to-empty.

d. **`run_contact_estelle_turn`:**
   - In step **b**, delete the `"## Available Contact skills (ACL)"` header, its two instruction lines, and the `for skill_key, meta in contact_skills().items():` loop with its trailing `lines.append("")`. Change `"Embed instructions in agent_payload.reply only — not skill_calls."` to `"Embed instructions in agent_payload.reply only."`.
   - Delete step **e** entirely (`# e. Optional skill_calls …` through the end of the `for item in calls:` loop).
   - Keep `"skill_results": []` in both the `empty` dict and the final return dict. Delete the `skill_results` local and return the literal `[]`. `_emit_listen_info` and callers read this key, so keeping the dict shape avoids widening the blast radius.

   ⚠️ **Decision: keep `run_contact_skill`, `contact_skills`, `contact_skill_keys`, `contact_skill_meta`, `_nest_dotted_path`, and `_deep_merge`.** They aren't dead: `src/ui/api/api_contact.py` (out of scope) imports `run_contact_skill` and `contact_skills` for the admin `/api/admin/contact/skills` routes. With `skills` empty, the GET returns `{}` and the POST returns 400 `unknown contact skill`. Estelle can't reach either.

e. **`_handle_slack_event_body`: private-channel gate.** Replace the comment line `# app_mention: accept as channel @Estelle` with:

```python
    # AST-2061: Estelle acts only in DMs / private channels. app_mention carries no
    # channel_type (and private channels use C… ids), so ask Slack; fail closed.
    if etype == "app_mention":
        mention_channel = event.get("channel") or ""
        ctype = event.get("channel_type")
        if not ctype:
            try:
                ctype = fetch_channel_type(mention_channel)
            except Exception as exc:
                logger.exception(
                    "%s | contact channel type lookup\n  %s: %s\n  This @Estelle mention is being ignored",
                    mention_channel or "-", type(exc).__name__, exc,
                )
                ctype = None
        if ctype not in CONTACT_CONFIG["allowed_channel_types"]:
            logger.debug(
                "Response from handle_slack_event: accepted=False reason=channel_not_private channel_type=%r",
                ctype,
            )
            return {"accepted": False, "reason": "channel_not_private"}
```

   ⚠️ **Decision: placement.** The gate sits right after the `message` subtype/DM checks, i.e. after event-id dedupe and before `resolve_slack_user`, activity recording, the conversation-cache append, the recognition post, the command intercept, paste recovery, and the turn. A public mention therefore gets no command, turn, or save (AC), and also no public "I know who that is" reply and no `slack_username` stamp. This is still "ahead of the command intercept and the turn", as scope requires. `message` events are already DM-only (`im` ⊂ allowed), so they are not re-gated. An event-supplied `channel_type` is authoritative and used when present, so the lookup only runs when Slack omits it. There is no prefix shortcut and no cache.

### Blast radius

- **Tests (Betty, `qa-fix`):** about 19 `create_contact_meteorite` references (`test_meteorite.py` 11, `test_contact.py` 5, `test_config.py` 1) plus 2 `_contact_param_looks_like_url` refs in `TestAst1517CreateContactMeteorite` go away with the function. Skills: `save_candidate_profile` / `save_candidate_contact` in `test_config.py`, `test_contact.py`, and `test_api_contact.py` (9 refs: the admin route now 400s on those keys). `skill_calls` / `skill_results` in `test_contact.py`, `test_config.py`, `test_repo_admin_json.py`. About 20 `app_mention` cases in `test_contact.py` use `C…` channels with no `channel_type`; each now calls `fetch_channel_type` and needs it patched to `"group"` (or the event given `"channel_type": "group"`) to keep today's acceptance. `apply_paste` / `insert_slack_meteorite` content assertions change wherever input contained markup or entities.
- **Shared code:** `insert_slack_meteorite` (AST-2034 / AST-2035 `/add-job`), `apply_paste` (AST-1561), `stage_meteorite` callers via `contact_land_meteorite` (AST-1531). Gazer email ingress (`create_meteorite_job`, `stage_meteorite` from `check_inbox`) is **not** sanitized by this change, since it's out of scope.
- **Admin UI:** Manage Contact skills list goes empty and its POST 400s (above).
- **Out-of-scope stale text (follow-up for Chuckles, not blocking):** `data/admin/agent_task.json` `contact_estelle_turn.system_prompt` still describes `skill_calls`, and `TASK_CONFIG["contact_estelle_turn"]["response_schema"]["skill_calls"]` remains (optional). If Estelle still emits `skill_calls`, Contact ignores them; no write happens.
- **Known edge losses from `nh3` (accepted):** a bare `a<b` with no space reads as a tag start and drops `<b`. Slack `<mailto:…|…>` markup, which `_SLACK_LINK_RE` doesn't unwrap (http(s) only), is stripped.
- **Slack:** one `conversations.info` call per `app_mention` without `channel_type`. In integration mode `require_controlled_external_io` blocks it, so the gate fails closed (mention ignored).

### What must still hold

- `create_meteorite_job` exists and behaves the same (gazer email ingress).
- Read tasks `get_job_by_pattern`, `get_job_data`, `get_company_data`, `get_candidate_data` and `gazer_scrape` stay in `CONTACT_TASK_CONFIG` with the same handlers. Markup parse/strip/dispatch (AST-1515) is unchanged for them.
- `/add-job` still lands a raw NEW meteorite (AST-2034) with the `estelle_thread_ts` stamp and code-mode ack (AST-2035); only the content is sanitized.
- `land_calls` → `contact_land_meteorite` → `stage_meteorite` and BOT_BLOCKED → READY `apply_paste` still work with the same return shapes and soft-fail semantics (never raise into Contact).
- DM `message` and DM/private `app_mention` flows behave as today: recognition reply (AST-1668), activity record (AST-1094/AST-1105), command intercept, paste recovery, Estelle turn.
- `resolve_slack_user`'s `contact.slack_username` stamp (AST-1105) and agent_data audit rows are untouched.
- `run_contact_estelle_turn` return dict keeps its keys (`skill_results` is always `[]`).
- No new artifact / `rubric_vector` write path, and no payload length cap.
