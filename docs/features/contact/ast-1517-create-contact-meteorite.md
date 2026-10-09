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

## Joan fix-board — AST-2061

[board-joan]  CANON: OK

AST-2061 board-joan done — CANON: OK.

---

**Triage notes (for Chuckles, not Linear):**

Read the `## Bug: AST-2061` plan-fix block on `origin/sub/AST-2055/AST-2061-estelle-pinhole` (As-is / To-be / Repro / Root cause / Proposed change / Blast radius / What must still hold). Skimmed in-force corpus via `canon/docs/DIRECTIVES-DIRECTORY.md` and overlapping **active** directives/patterns (`patt.contact.command-intercept`, `stat.logging.info.contact`, `stat.logging.info.api`, `astral.layers.import-direction`, `astral.layers.core-vs-external-bright-line`, `astral.config.config-source-of-truth` / registry-not-literals, `patt.config.block`, `stat.core.decides-transitions` / dispatch meteorite eligibility). No `docs/canon-index.md` on this ref.

**One question:** Does the proposed change conflict with or require updating any in-force directive?

**Answer:** No. Retiring `create_contact_meteorite` and Estelle `skill_calls` narrows Contact to meteorite writes and read tasks; it does not contradict `patt.contact.command-intercept` (commands unchanged; skills remain an optional registry shape, now empty). `stat.logging.info.contact` still allows `action:-` when no skills run. `fetch_channel_type` in `src/external/slack.py` fits the external I/O bright line; config-only allowlists (`allowed_channel_types`, `_CONTACT_PINHOLE_HANDLERS`) fit registry-not-literals. No active statute mandates Contact ACL save skills (AST-1071 was feature scope, not a standing “skills must be populated” rule). `nh3` sanitization in core is not an I/O-layer violation. Parent AST-2055 To-be mention of artifact/`rubric_vector` writes is deferred in this child’s Boundaries — product scope on the ticket, not a canon amendment this fix must land.

No F3 (`validate-plan` fix mode) canon work indicated from this triage pass.

## Radia review — AST-2061

[code-rubric]
**Ticket:** AST-2061
**Publish ref:** `origin/sub/AST-2055/AST-2061-estelle-pinhole` @ `31ccbee3be2997d5fc0a56febbb352e7055e84c3`
**Diff base:** `origin/ftr/AST-2055-estelle-pinhole...origin/sub/AST-2055/AST-2061-estelle-pinhole` (product: `requirements.txt`, `src/utils/config.py`, `src/core/meteorite.py`, `src/external/slack.py`, `src/core/contact.py`; plus plan-fix doc commits on sub)
**Corpus:** `4d5db7332d81afd9a496ed8ad234971d458c1700` (`canon/` tree at local worktree tip; no `docs/canon-index.md` on this ref — id resolution via `canon/statutes/**`, `canon/directives/active/**`, and `canon/instruction_preamble.md` grade scale)
**Overall:** CLEAN

## Fix-specific checks

- **[bug-repro]** not applicable — clean board opt-out; fix-board **TESTS: REVISE** routed to sibling **AST-2062** (blocked by this ticket). No `[bug-repro]` expected on this diff by design.
- **## What must still hold — OK** (each item traced against `origin/ftr...sub` product diff):
  - `create_meteorite_job` retained in `meteorite.py`; not reachable from Contact command/task registry (`create_contact_meteorite` removed from config and module).
  - Read tasks + `gazer_scrape` remain in `CONTACT_TASK_CONFIG` with same handler paths; pinhole `_CONTACT_PINHOLE_HANDLERS` assert covers every command/task handler.
  - `/add-job` → `insert_slack_meteorite` unchanged in registry; payload sanitized via `sanitize_contact_text` (Slack link unwrap still via `parse_contact_command` / `_unwrap_slack_links` on paste paths).
  - `land_calls` → `contact_land_meteorite` → `stage_meteorite` and `apply_paste` / `_normalize_apply_paste_content` keep soft-fail shapes; nh3 is the sole markup stripper on Contact writes.
  - Private-channel gate on `app_mention` before resolve/command/turn; DM `message` path unchanged (`_is_dm_message`).
  - `resolve_slack_user` / agent_data paths untouched in code; public mentions fail closed before those run (plan decision, consistent with AC).
  - `skill_results` always `[]`; no new artifact / `rubric_vector` path; no length cap.

## Canon scores

**Frozen list:** Linear AST-2061 Description has **no `## Citations` / frozen canon ids** (same fix-lane pattern as AST-1796 / AST-1784). Fix-board Joan **CANON: OK** at F2; engineering contract is the plan-fix block in `docs/features/contact/ast-1517-create-contact-meteorite.md` § Bug: AST-2061.

*(No directive ids on the frozen list — zero graded rows per `review-child` §5.1.)*

**Notes — Canon Scope / informal overlap (not scored as list rows):** Board triage named `patt.contact.command-intercept`, `stat.logging.info.contact`, `stat.logging.info.api`, `astral.layers.import-direction`, `astral.layers.core-vs-external-bright-line`, `astral.config.config-source-of-truth`, `patt.config.block`, `stat.core.decides-transitions`. Diff read against those: command intercept registry and ordering preserved; `fetch_channel_type` in `src/external/slack.py` with `require_controlled_external_io`; allowlists in `CONTACT_CONFIG`; core sanitize + late import pattern for meteorite↔contact cycle; no new Contact path to `job`/`candidate`. **No Canon Scope ESCALATE** — nothing in the diff plainly requires an off-list directive amendment.

## Column diff vs plan stage

`no plan-stage scores attached` (no F3 `validate-plan` fix-mode column; Joan fix-board only)

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

- **Location:** Linear AST-2061 Description  
  **Finding:** No frozen canon list on the bug ticket; Radia cannot emit per-id canon rows.  
  **Default:** Treat plan-fix § Bug: AST-2061 + fix-board **CANON: OK** as the lane bar for this review; optional Archie habit to add Citations on fix children (process only, not blocking this diff).

- **Location:** `CONTACT_CONFIG["allowed_channel_types"]` = `("im", "group")` vs `fetch_channel_type` → `"mpim"`  
  **Finding:** Multi-person DMs (`mpim`) are not in the allowlist; `app_mention` there fails closed. Plan/To-be explicitly chose DM + private channel only; `_is_dm_message` already accepts only `im` for `message` events.  
  **Default:** Ship as planned; if Susan wants Estelle in mpim, widen allowlist in a follow-up (not this pinhole ticket unless she says otherwise).  
  **@susan:** Should Estelle respond in Slack mpim (group DM) mentions, or is im + private `group` enough?

### advisory

- **Location:** `origin/ftr...sub` diff — `tests/**` absent  
  **Finding:** Sibling **AST-2062** owns test-bible updates per blast radius; `ftr` tip still references `create_contact_meteorite` in component tests until 2062 lands. Expected split; not cross-ticket product scope smuggling.  
  **Recommendation:** Chuckles: after **User Testing** on 2061, unblocks 2062; do not treat missing tests on this sub as a 2061 resolve-child item.

- **Location:** Plan blast radius — stale `agent_task.json` / `skill_calls` schema  
  **Finding:** Documented out-of-scope; model may still emit ignored `skill_calls`.  
  **Recommendation:** Optional follow-up doc/prompt hygiene (plan already flags for Chuckles).

## What's solid

- Pinhole matches plan: job/candidate write paths removed; single `sanitize_contact_text` + nh3; import-time handler allowlist; public `app_mention` gate with fail-closed `conversations.info`.
- Layering: Slack I/O in `external`, policy allowlist in config, sanitize in core meteorite.
- Scope contained to the six files named on the ticket (plus issue doc on sub).

## Chuckles — post-review branching

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** (clean, C7 complete) | Normal (AST-2055 ftr) | → **Review Posted** → `do-all-the-things` §3h clean shortcut → **User Testing**; **skip `resolve-child`** |

## Recommended actions (Chuckles downstream — not Radia)

1. Append this artifact to the issue doc; `docs(AST-2061): Radia review — clean`; push on `sub/AST-2055/AST-2061-estelle-pinhole`.
2. Post slim upshot `--as radia` below.
3. Advance to **Review Posted** → **User Testing** (no resolve-child).

context_tokens≈22000

[code-rubric] PROCEED (Commit: 31ccbee3) Estelle pinhole clean

## Test routing — AST-2061

Test-tree and bible coverage for this fix is owned by gap sibling [AST-2062](https://linear.app/astralcareermatch/issue/AST-2062) (fix-board `[board-betty] TESTS: REVISE`), which is blocked by AST-2061 and lands on `ftr/AST-2055-estelle-pinhole` after it. AST-2061 itself carries no `test()` / `merge-tests` commits: docs-acceptance.

## Bug: AST-2062 — Estelle pinhole tests + bible (test gap for AST-2061)

**Mini-parent:** [AST-2055](https://linear.app/astralcareermatch/issue/AST-2055) · **Publish ref:** `sub/AST-2055/AST-2062-estelle-pinhole-tests` · **Product fix:** AST-2061 (`31ccbee3`, on `ftr/AST-2055-estelle-pinhole` @ `54eb3f275`) · **Owner of edits:** Betty (test tree + bible). No `src/` change.

### As-is

On the AST-2061 tip, the touched suites (`test_contact`, `test_meteorite`, `test_config`, `test_slack`, `test_api_contact`, `test_repo_admin_json`) show 115 failures. The pre-fix commit `6b00d8c5f` shows 82, so **33 are new**, and all of them assert access the pinhole removed (AST-2061 test-fix, comment `c33245a5` + correction):

- **`test_meteorite.py` (7):** `TestAst1517CreateContactMeteorite`, every case (`create_contact_meteorite` / `_contact_param_looks_like_url` are deleted).
- **`test_contact.py` (23):**
  - 18 `app_mention` cases on `C…` channels with no `channel_type`. On the tip, `fetch_channel_type` isn't patched, so the gate fails closed (`accepted=False reason=channel_not_private`). With the lookup patched to `"group"` all 18 go green.
  - 3 AST-1515 markup tests that use `create_contact_meteorite` as the sample listed key.
  - `TestAst1071ContactSkillRunners::test_run_writes_allowlisted_contact_path` (`save_candidate_contact` is gone).
  - `TestAst1073ContactEstelleTurnLoop::test_skill_calls_run_for_resolved_candidate` (the `skill_calls` loop is gone).
- **`test_config.py` (3):** `TestAst1071ContactSkillsConfig::test_two_skills_not_in_task_config`, `TestAst1105ProfileSlackFields::test_slack_id_and_username_fields` (reads `skills["save_candidate_contact"]`), and `TestAst1515ContactTaskConfig::test_six_keys_handler_metadata_and_collision_guards`.

Other tests still **reference** the retired surfaces but stay green, because they mock them or were already red pre-fix:
- the rest of `TestAst1071ContactSkillRunners` / `TestAst1071ContactSkillsConfig` (stale `profile.*` paths, red on `6b00d8c5f`);
- `TestAst1515ContactTaskMarkup::test_dispatch_debug_style_d`;
- `TestAst1071ContactSkillsApi`, which uses the `save_candidate_profile` name in mocks and URLs.

**No test covers the new behavior:** no job-leak, candidate-write, sanitize, or public-channel repro, and nothing on `fetch_channel_type`, `sanitize_contact_text`, `allowed_channel_types`, or `_CONTACT_PINHOLE_HANDLERS`. The bible still lists the AST-1517 / AST-1071 surfaces as live.

### To-be

- The suites assert the pinhole, not the old access. The 33 new reds go green against the AST-2061 tip without touching `src/`.
- Four repro groups (job leak, candidate write, unsanitized write, public-channel `app_mention`) are each **red on `6b00d8c5f`** and **green on `54eb3f275`**.
- `fetch_channel_type`, `sanitize_contact_text`, `allowed_channel_types`, and the pinhole assert have direct cases.
- No test depends on `create_contact_meteorite` or the `save_candidate_*` skills.
- The four bible pages match.

### Repro

The test delta is itself the repro. Repro tests are marked **[bug-repro]** below. Run them against the pre-fix tree (`git checkout 6b00d8c5f` + the AST-2062 test files) and they fail **on their assertions**: the autouse fixture uses `raising=False` precisely so the pre-fix module still loads. Against `54eb3f275` they pass. Literal fixtures:

```python
# job leak — markup a pre-fix turn would dispatch to create_contact_meteorite (text mode, no fetch)
markup_spans = [("create_contact_meteorite", "Senior Engineer at Acme")]
# candidate write — Estelle output carrying skill_calls (fake skill key, no save_candidate_* name)
parsed_response = {"reply": "ok", "skill_calls": [{"skill_key": "save_profile_field", "fields": {"contact.contact_email": "x@evil.test"}}]}
# unsanitized write
payload = "<img src=x onerror=alert(1)>Senior Eng &lt;script&gt;alert(1)&lt;/script&gt;"   # stored: "Senior Eng"
# public channel — conversations.info says public
event = {"type": "app_mention", "user": "U1", "channel": "C1PUBLIC", "ts": "1.0", "text": "<@UBOT> /add-job https://x.io/1"}
fetch_channel_type = lambda _ch: "channel"
```

### Root cause

AST-2061 deliberately removed `create_contact_meteorite`, the `save_candidate_*` skills, and the `skill_calls` loop, and added a fail-closed channel lookup on `app_mention`. The existing tests were written for the old access and pass `app_mention` fixtures without a channel type. The fix-board routed the test work here (`[board-betty] TESTS: REVISE`) rather than to qa-fix on AST-2061, so nothing was revised or added alongside the product change.

### Proposed change

Betty lands all of this via qa-fix, in `tests/` and `docs/test-bible/` only. Every file is in AST-2062 `## Scope`. `test(AST-2062): …` commits on `astral-tests`, published to `origin/sub/AST-2055/AST-2062-estelle-pinhole-tests`.

#### 1. `tests/component/core/test_contact.py`

a. **Module autouse fixture**, directly after `_stub_estelle_turn`:

```python
@pytest.fixture(autouse=True)
def _ast2061_private_channel_default(monkeypatch: pytest.MonkeyPatch) -> None:
    # AST-2061: app_mention looks up channel type; default every case to a private channel.
    monkeypatch.setattr(contact_mod, "fetch_channel_type", lambda _ch: "group", raising=False)
```

   This makes all 18 `C…` `app_mention` cases green with no per-case edits. Tests that need a different channel type set it again inside the test (the later `setattr` wins).

b. **Retire `TestAst1071ContactSkillRunners`** (the whole class and its `# Branches:` comment) and replace it in place with:

   **`TestAst2061ContactSkillsRetired`**
   - `test_skills_registry_empty`: `contact_mod.contact_skills() == {}` and `contact_mod.contact_skill_keys() == ()`.
   - `test_run_contact_skill_refuses_any_key` (`sqlite_in_memory`): save candidate `c-2061-skill` with `candidate_data={}`. `pytest.raises(ValueError, match="unknown contact skill")` on `run_contact_skill("save_profile_field", astral_candidate_id="c-2061-skill", fields={"contact.contact_email": "x@evil.test"})`. Then `candidate_mod.get_candidate("c-2061-skill")["candidate_data"]` has no `contact` key.

c. **`TestAst1073ContactEstelleTurnLoop`:** replace `test_skill_calls_run_for_resolved_candidate` with **[bug-repro] `test_ast2061_skill_calls_never_write_candidate`**:
   - `deps = self._patch_turn_deps(...)` with `parsed_response` = the candidate-write fixture above. Also `save = MagicMock(); monkeypatch.setattr(contact_mod, "save_candidate_data", save)`.
   - Call `run_contact_estelle_turn(channel="C1", text="hi", astral_candidate_id="c1", debug=False)`.
   - Assert `deps["skill"].assert_not_called()`, `save.assert_not_called()`, `out["skill_results"] == []`.
   - Assert `"## Available Contact skills (ACL)" not in deps["do_task_calls"][0][1]["live_content"]`.
   - Pre-fix, `run_contact_skill` is called and the ACL header is present.

d. **AST-1515 sample key → `gazer_scrape`** (listed, `requires_candidate=True`; the handler is still stubbed `None`, so the expectations don't change):
   - `TestAst1515ContactTaskMarkup::test_dispatch_handler_unavailable_for_listed_key`: `markup_spans=[("gazer_scrape", "https://x.example/jd")]` and `results[0]["task_key"] == "gazer_scrape"`. Comment becomes `# All five handlers resolve — mock missing import path.`
   - `TestAst1515ContactTaskMarkup::test_dispatch_debug_style_d`: `markup_spans=[("gazer_scrape", "u")]`.
   - `TestAst1515ContactEstelleTurnMarkup::test_strips_markup_before_slack_post`: reply `"Sure! ~~/gazer_scrape https://jobs.example/1~~"`.
   - `TestAst1515ContactEstelleTurnMarkup::test_follow_up_turn_includes_task_results_in_live_content`: reply `"Checking ~~/gazer_scrape https://x.example~~"`.

e. **New `TestAst2061PrivateChannelGate`.** `setup_method` clears `contact_mod._seen_event_ids`. A shared `_patch(monkeypatch, ctype=..., side_effect=None)` helper:
   - sets `CONTACT_CONFIG["listen_enabled"]` to True;
   - sets `contact_mod.fetch_channel_type` to `MagicMock(return_value=ctype, side_effect=side_effect)`;
   - stubs `resolve_slack_user` → `{"astral_candidate_id": "c1", "state": "PROSPECT", "created": False}`;
   - stubs `_run_contact_command` → `{"ok": True}`, `try_meteorite_apply_paste_from_slack` → `{"applied": False}`, `contact_post_message` → `{"ok": True}`;
   - stubs `run_contact_estelle_turn` via `_stub_estelle_turn`;
   - stubs `record_estelle_activity` on `src.data.contact_estelle_activity`, so the tracked `data/contact_estelle_activity.json` is never written;
   - returns the mocks.

   Cases:
   - **[bug-repro] `test_public_mention_refused_no_command_turn_or_save`:** `ctype="channel"`, the public-channel event above. Assert `out == {"accepted": False, "reason": "channel_not_private"}` and that resolve, command, paste, turn, and post were all **not called**. Pre-fix, it's accepted and the command runs.
   - `test_mpim_mention_refused`: `ctype="mpim"`, same assertions.
   - `test_lookup_error_fails_closed`: `side_effect=RuntimeError("missing_scope")`. Refused as above, resolve not called.
   - `test_private_group_mention_passes`: `ctype="group"`, text `"hi"`. `out["accepted"] is True`, lookup called once with `"C1PUBLIC"`, turn called once.
   - `test_event_channel_type_skips_lookup`: event has `"channel_type": "im"`, mock `ctype="channel"`. Accepted, lookup **not called**.
   - `test_dm_message_not_gated`: `{"type": "message", "user": "U1", "channel": "D1", "channel_type": "im", "ts": "1.0", "text": "hi"}`. Accepted, lookup not called.

f. **New `TestAst2061ContactSanitizeEntry`:**
   - **[bug-repro] `test_land_blob_unwrapped_then_sanitized`:** stub `meteorite_mod.stage_meteorite` with an async capture, the same shape as `TestAst1531ContactLandStageCutover::test_stages_text_blob_with_source_handle`. Call `contact_land_meteorite("c1", source_kind="slack", source_id="C1:1", text="<https://x.io/job?id=1&amp;src=slack|Job> <img src=x onerror=alert(1)>Senior Eng", employer_name="Acme")`. Assert the captured blob `== "https://x.io/job?id=1&src=slack Senior Eng\n\nEmployer: Acme"`. Pre-fix, the blob is raw.
   - `test_land_markup_only_blob_is_required_error`: `text="<script>alert(1)</script>"`, no link or employer. Assert `out["error"] == "blob is required"` and the stage stub was not called.
   - **[bug-repro] `test_slack_paste_unwrapped_before_apply_paste`** (`sqlite_in_memory`): insert a `BOT_BLOCKED` row (the `_insert_meteorite_row` shape from `test_meteorite.py`, or a direct `db.insert_meteorite_rows`). Patch `meteorite_mod.find_meteorite_for_estelle_thread` → `{"id": row_id}`. Call `try_meteorite_apply_paste_from_slack(astral_candidate_id="c1", channel="D1", thread_ts="1.0", message_ts="1.0", text="Full JD <https://x.io/j?a=1&amp;b=2|link>")`. Assert the row's `content == "Full JD https://x.io/j?a=1&b=2"` and its state is `READY`. Pre-fix, the raw Slack markup goes through the old HTML branch and is stored mangled: `"Full JD \n https://x.io/j?a=1&amp;b=2|link"` (verified against `6b00d8c5f`'s `_normalize_apply_paste_content`).

g. **Leave unchanged:**
   - the `contact_skills` monkeypatches in the turn helpers (`_patch_turn_deps`, `TestAst1879…`, `TestAst1515ContactEstelleTurnMarkup._patch_turn`, `TestAst1561…`, `TestAst1585…`, `TestAst2035…`). The attribute still exists, so they're harmless;
   - `_stub_estelle_turn`'s `"skill_results": []`, which is still the turn's return shape;
   - `TestAst1066ContactScaffold`, which passes with an empty map.

#### 2. `tests/component/core/test_meteorite.py`

a. **Delete `TestAst1517CreateContactMeteorite`** with its `# Branches:` comment (currently lines 664–817).

b. **New `TestAst2061NoContactJobWrite`** (placed where the deleted class was):
   - `test_create_contact_meteorite_removed`: `not hasattr(meteorite_mod, "create_contact_meteorite")` and `not hasattr(meteorite_mod, "_contact_param_looks_like_url")`.
   - **[bug-repro] `test_contact_markup_never_reaches_create_meteorite_job`:** `create = MagicMock(); monkeypatch.setattr(meteorite_mod, "create_meteorite_job", create)`. Then `from src.core import contact as contact_mod` and `results = contact_mod.run_contact_task_dispatch(astral_candidate_id="c1", markup_spans=[("create_contact_meteorite", "Senior Engineer at Acme")])`. Assert `create.assert_not_called()` and `results == []` (unknown key ignored). Pre-fix, text mode calls `create_meteorite_job("c1", …)`.

c. **New `TestAst2061ContactSanitize`** (placed after `TestAst2034InsertSlackMeteorite`; `SID = "C1:1700000000.000200"`):
   - **[bug-repro] `test_insert_slack_meteorite_stores_sanitized_content`:** the unsanitized-write fixture → `out["ok"] is True`, and the row's `content == "Senior Eng"`, state `NEW`, `classify_outcome` None.
   - `test_insert_slack_meteorite_keeps_url_query`: payload `"https://x.io/job?id=1&amp;src=slack"` → `content == "https://x.io/job?id=1&src=slack"`.
   - `test_insert_markup_only_payload_is_required_miss`: payload `"<script>alert(1)</script>"` → `{"ok": False, "meteorite_id": None, "error": "payload is required"}`, and no row for `SID`.
   - **[bug-repro] `test_apply_paste_drops_script_content`:** a `BOT_BLOCKED` row; `apply_paste(row_id, "<p>Senior Eng</p><script>alert(1)</script>")` → ok, `content == "Senior Eng"`. Pre-fix, the regex leaves `"Senior Eng alert(1)"`.
   - `test_apply_paste_entity_encoded_plain_text`: `apply_paste(row_id, "&lt;script&gt;alert(1)&lt;/script&gt;Senior Eng")` → `content == "Senior Eng"`.
   - `test_apply_paste_plain_lines_unchanged`: `"line1\n\n  line2  "` → `content == "line1\n\nline2"`, which pins the existing line shaping.
   - `test_sanitize_contact_text_table`: parametrize `sanitize_contact_text` over the AST-2061 decision table: the `&amp;` URL, `&lt;script&gt;…`, `<b>…<img …> AT&amp;T` → `"Senior Eng  AT&T"`, `"<@U123> salary 1 < 2"` unchanged, `"line1\n\nline2  <!-- c -->"` → `"line1\n\nline2"`, and `None` → `""`. The double-encoded residual is **not** pinned (accepted plain-text residual; pinning it would freeze a known gap).

d. **Leave unchanged:** `TestAst1561ApplyPaste` and `TestAst2034InsertSlackMeteorite`. Their plain-text and URL fixtures already pass through the sanitizer unchanged (all green on the tip).

#### 3. `tests/component/utils/test_config.py`

a. **Replace `TestAst1071ContactSkillsConfig`** (both tests) with **`TestAst2061ContactSkillsEmpty::test_skills_registry_empty`**: `cfg.CONTACT_CONFIG["skills"] == {}`.

b. **`TestAst1105ProfileSlackFields::test_slack_id_and_username_fields`:** delete the trailing comment and 3 lines that read `skills["save_candidate_contact"]["allowed_paths"]`. The profile-field assertions stay.

c. **`TestAst1515ContactTaskConfig`:** remove `"create_contact_meteorite"` from `_EXPECTED_KEYS`. Rename the test to `test_five_keys_handler_metadata_and_collision_guards`, and change the `# Branches:` comment to `five keys`.

d. **New `TestAst2061ContactPinholeConfig`:**
   - `test_allowed_channel_types`: `cfg.CONTACT_CONFIG["allowed_channel_types"] == ("im", "group")`.
   - **[bug-repro] `test_create_contact_meteorite_retired`:** `"create_contact_meteorite" not in cfg.CONTACT_TASK_CONFIG`.
   - `test_every_contact_handler_in_pinhole`: every `CONTACT_TASK_CONFIG` and `CONTACT_CONFIG["commands"]` handler is a key of `cfg._CONTACT_PINHOLE_HANDLERS`. Every value starting `write` has a key starting `src.core.meteorite.`. `"src.core.meteorite.create_meteorite_job"` and `"src.core.meteorite.land_meteorite"` are not keys.
   - `test_pinhole_assert_rejects_job_writer`: read `src/utils/config.py` text and insert, immediately before the line starting `# AST-2061 pinhole:`:

     ```python
     CONTACT_TASK_CONFIG["leak"] = {"handler": "src.core.meteorite.create_meteorite_job", "description": "x", "param_hint": "x", "requires_candidate": True}
     ```

     `exec(compile(text, "config_spliced", "exec"), {"__name__": "config_spliced"})` inside `pytest.raises(AssertionError, match="Contact handler outside pinhole")`. Assert the anchor line exists first (`assert text.count("# AST-2061 pinhole:") == 1`), so a moved comment fails loudly instead of silently passing.

   ⚠️ **Decision: test the real import-time assert by splicing and re-executing the config source,** not by re-implementing its predicate in the test. A copied predicate would pass even if the assert were deleted. The anchor-count check keeps the splice from passing vacuously. If executing the full config module in-process proves heavy or has side effects, the fallback is a subprocess (`python -c` with the same splice); still no `src/` change.

e. **Leave unchanged:** `TestAst1073ContactEstelleTurnConfig::test_skill_calls_optional_on_chat_schema`. AST-2061 deliberately kept the optional `skill_calls` schema entry (the prompt follow-up is out of scope), so this assertion is still true.

#### 4. `tests/component/ui/api/test_api_contact.py`

a. In `TestAst1071ContactSkillsApi`, rename the sample key `save_candidate_profile` → `sample_skill` in every mock return, URL, and `assert_called_once_with` (9 refs). The routes are generic, so behavior and assertions are otherwise unchanged.

b. **New `TestAst2061ContactSkillsApiEmptyRegistry`** (real `contact_skills` / `run_contact_skill`, no mocks of either; `contact_client` + `auth_headers` fixtures, as in the class above):
   - `test_list_skills_empty`: `GET /api/admin/contact/skills` → 200, `{"skills": {}}`.
   - `test_run_any_skill_400`: patch `ui_llm_debug` → False; `POST /api/admin/contact/skills/sample_skill` with `{"astral_candidate_id": "c1", "fields": {"contact.contact_email": "x@evil.test"}}` → 400, `{"error": "unknown contact skill: 'sample_skill'"}`. This raises before any candidate lookup, so no DB fixture is needed.

#### 5. `tests/component/core/test_repo_admin_json.py`

**No change.** Its `skill_calls` assertions (`TestAst1072…::test_contact_estelle_turn_envelope_prompts`, `TestAst1515ContactEstelleTurnMarkupPrompt`) read `data/admin/agent_task.json`'s system prompt. That prompt still mentions `skill_calls` by design (out of scope per AST-2062 Boundaries), and the tests are green on the tip.

⚠️ **Decision:** the file is in scope as "modified per Betty's blast-radius list", but none of its assertions are false after AST-2061. Editing them now would make them disagree with the shipped prompt. They change when the prompt follow-up lands.

#### 6. `tests/component/external/test_slack.py`

**New `TestAst2061FetchChannelType`**, using the same env and mock pattern as `TestAst1068FetchUserProfile`: `ASTRAL_ALLOW_LIVE_EXTERNAL_IO=1`, `CONTACT_CONFIG["bot_token_env"]="xoxb-test"`, `slack_mod.requests.get` → a `MagicMock` response.
- `test_requires_gate`: `delenv("ASTRAL_ALLOW_LIVE_EXTERNAL_IO")` → `pytest.raises(Exception)` on `fetch_channel_type("C1")`.
- `test_maps_conversations_info_flags`: parametrize `channel` payloads:

  | Payload | Expected |
  |---------|----------|
  | `{"is_im": True}` | `"im"` |
  | `{"is_mpim": True, "is_private": True}` | `"mpim"` |
  | `{"is_private": True}` | `"group"` |
  | `{"is_group": True}` | `"group"` |
  | `{"is_private": False}` | `"channel"` |
  | `{}` | `"channel"` |

  Assert `get.call_args.args[0].endswith("/conversations.info")` and `get.call_args.kwargs["params"] == {"channel": "C1"}`.
- `test_ok_false_raises_with_scope_detail`: `{"ok": False, "error": "missing_scope", "needed": "im:read", "provided": "groups:read"}` → `RuntimeError`, message containing `conversations.info failed: missing_scope` and `im:read`.
- `test_blank_channel_raises`: `pytest.raises(ValueError, match="channel")` on `fetch_channel_type("  ")`.

#### 7. Bible

Each page gets a new `### AST-2062 · AST-2055 (Estelle pinhole — tests for AST-2061)` section after its last existing section, with Parent/Publish lines, a one-line summary, an Area / Source / Component tests table, **Broken / obsolete**, **Integration:** none (no scenario covers Contact Slack events or meteorite sanitize; do not invent), and a `## QA test manifest`. Retired sections are annotated, not deleted, so history stays readable.

- **`docs/test-bible/core/contact.md`**
  - New section table: skills retired → `TestAst2061ContactSkillsRetired`; candidate-write repro → `TestAst1073ContactEstelleTurnLoop::test_ast2061_skill_calls_never_write_candidate`; channel gate → `TestAst2061PrivateChannelGate` (6); land / paste sanitize entry → `TestAst2061ContactSanitizeEntry` (3); the `app_mention` default → module autouse `_ast2061_private_channel_default`.
  - **Broken / obsolete:** `TestAst1071ContactSkillRunners` (retired); `test_skill_calls_run_for_resolved_candidate` (replaced); the AST-1515 sample key moved to `gazer_scrape`; 18 `app_mention` cases fixed by the autouse default.
  - In the **AST-1071 · AST-1043** section, append `**Retired by AST-2061 / AST-2062:** skills ACL emptied; runner class replaced by TestAst2061ContactSkillsRetired.` and change its table row's test cell to `retired → TestAst2061ContactSkillsRetired`.
  - In the **AST-1515** section's Broken/obsolete line, append `**AST-2062:** handler_unavailable / turn fixtures retargeted from create_contact_meteorite to gazer_scrape.`
- **`docs/test-bible/core/meteorite.md`**
  - New section table: job-leak repro → `TestAst2061NoContactJobWrite` (2); sanitize → `TestAst2061ContactSanitize` (7).
  - In the **AST-1517 · AST-1414** section, append `**Retired by AST-2061 / AST-2062:** create_contact_meteorite deleted; class TestAst1517CreateContactMeteorite removed.` and remove its manifest line (`…::TestAst1517CreateContactMeteorite \`).
  - In the **AST-1561** and **AST-2034** sections, add one line each: `AST-2061: content now passes through sanitize_contact_text — see § AST-2062.`
- **`docs/test-bible/utils/config.md`**
  - New section table: skills empty → `TestAst2061ContactSkillsEmpty`; `allowed_channel_types` / retired task / handler pinhole / spliced import-assert → `TestAst2061ContactPinholeConfig` (4); revised `TestAst1515ContactTaskConfig::test_five_keys_…` and `TestAst1105ProfileSlackFields::test_slack_id_and_username_fields`.
  - In the **AST-1071 · AST-1043** section, append the same retired line (class replaced by `TestAst2061ContactSkillsEmpty`). In the `CONTACT_CONFIG` row near line 1464, append `skills emptied by **AST-2061**`.
- **`docs/test-bible/external/slack.md`**
  - New section table: `fetch_channel_type` gate / mapping / ok:false / blank → `TestAst2061FetchChannelType` (4).
  - Add `channel type lookup (fetch_channel_type)` to the page's surface line.

**QA test manifest — AST-2062** (on `core/contact.md`; the other three pages list their own lines):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_contact.py::TestAst2061ContactSkillsRetired \
  tests/component/core/test_contact.py::TestAst2061PrivateChannelGate \
  tests/component/core/test_contact.py::TestAst2061ContactSanitizeEntry \
  tests/component/core/test_contact.py::TestAst1073ContactEstelleTurnLoop::test_ast2061_skill_calls_never_write_candidate \
  tests/component/core/test_contact.py::TestAst1515ContactTaskMarkup \
  tests/component/core/test_contact.py::TestAst1515ContactEstelleTurnMarkup \
  tests/component/core/test_contact.py::TestAst2035ContactCommandIntercept \
  tests/component/core/test_contact.py::TestAst1668UnboundAndRecognition \
  tests/component/core/test_meteorite.py::TestAst2061NoContactJobWrite \
  tests/component/core/test_meteorite.py::TestAst2061ContactSanitize \
  tests/component/core/test_meteorite.py::TestAst2034InsertSlackMeteorite \
  tests/component/core/test_meteorite.py::TestAst1561ApplyPaste \
  tests/component/utils/test_config.py::TestAst2061ContactSkillsEmpty \
  tests/component/utils/test_config.py::TestAst2061ContactPinholeConfig \
  tests/component/utils/test_config.py::TestAst1515ContactTaskConfig \
  tests/component/utils/test_config.py::TestAst1105ProfileSlackFields \
  tests/component/ui/api/test_api_contact.py \
  tests/component/external/test_slack.py::TestAst2061FetchChannelType \
  -q
```

**Pass criterion:** green on the AST-2061 tip. The 33 AST-2061 reds are gone, and the remaining failures in the six files equal the 82 pre-existing on `6b00d8c5f` minus those retired with `TestAst1071ContactSkillRunners` / `TestAst1071ContactSkillsConfig`. Betty may `--deselect` pre-existing reds in listed classes (as the AST-2035 manifest does), naming each.

### Blast radius

- Test tree and bible only: the six test files and four bible pages above. No `src/`, no `data/`.
- The autouse fixture applies to every test in `test_contact.py`. It only replaces `contact_mod.fetch_channel_type`, which no other code path in that module uses, and `raising=False` keeps the pre-fix module importable for repro runs.
- `TestAst2061PrivateChannelGate` stubs `record_estelle_activity`. Existing accept-path tests already write the tracked `data/contact_estelle_activity.json` (seen dirtied on this worktree after local runs). That is pre-existing and not fixed here, but Betty should not commit that file.
- The spliced-exec config test re-executes `src/utils/config.py` source in a throwaway namespace. It doesn't touch the imported `src.utils.config` module object.

### What must still hold

- AST-2061 product behavior as shipped (its `## What must still hold`): read tasks and `gazer_scrape` unchanged; `/add-job` lands NEW with the thread stamp and ack; `land_calls` / `apply_paste` return shapes; DM and private flows unchanged; `skill_results` always `[]`.
- AST-2035 intercept tests (`TestAst2035ContactCommandIntercept`) and AST-2034 insert tests stay green. Their channels are covered by the autouse default and their fixtures pass through the sanitizer unchanged.
- No test pins the double-encoded sanitize residual, adds a length cap, or depends on `create_contact_meteorite` / `save_candidate_*` as live surfaces. Those names appear only as **absent / unknown** in the AST-2061 repro and retirement assertions.
- Engineer test-tree ban: Katherine does not edit `tests/` or `docs/test-bible/`. Betty lands this.

⚠️ **Decision: name references.** AC2 reads "no test still references `create_contact_meteorite` or the `save_candidate_*` skills". Read literally, that conflicts with AC1's job-leak repro, which must name the retired task key to prove it's dead. I read AC2 as "no test exercises them as live". Retirement and repro tests may name `create_contact_meteorite` only to assert absence. `save_candidate_*` is avoided entirely (fake `save_profile_field` / `sample_skill` keys are used instead).

## Joan fix-board — AST-2062

[board-joan]  CANON: OK

AST-2062 board-joan done — CANON: OK.

**Triage (stdout only; Chuckles posts the block above):** Read `## Bug: AST-2062` on `origin/sub/AST-2055/AST-2062-estelle-pinhole-tests` (full As-is → What must still hold). Scope is `tests/**` and `docs/test-bible/**` only — no `src/`, no `canon/`, no `data/`. Skimmed in-force corpus via `canon/docs/DIRECTIVES-DIRECTORY.md` and contact/logging/layers/registry orchestration roles (`patt.contact.command-intercept`, `stat.logging.info.contact`, layer/import/external rules, `orch.roles.betty-owns-test-tree` / `astral.git.engineer-test-tree-ban`).

**One question:** Does this plan-fix require changing or conflict with any in-force directive?

**Answer:** No. Tests and bible rows encode AST-2061 product behavior already judged canon-neutral on AST-2061; they do not introduce new product rules or contradict active patterns (commands/skills registry shape, listen logging, external I/O placement). Betty-owned test-tree work matches role statutes; Katherine is not asked to land test paths. The spliced `config.py` exec test validates the shipped import-time assert without redefining canon. No F3 canon landing indicated.

## Radia review — AST-2062

[code-rubric]
**Ticket:** AST-2062
**Publish ref:** `origin/sub/AST-2055/AST-2062-estelle-pinhole-tests` @ `20fc3341b` (tip under review; qa-fix / `[bug-repro]` land @ `c904c7725`, merge-tests @ `91220f994`)
**Diff base:** `origin/ftr/AST-2055-estelle-pinhole...origin/sub/AST-2055/AST-2062-estelle-pinhole-tests`
**Product:** no `src/` delta (0 bytes). Intended delta: `tests/**`, `docs/test-bible/**`, issue-doc patch on `docs/features/contact/ast-1517-create-contact-meteorite.md`.
**Corpus:** `4d5db7332d81afd9a496ed8ad234971d458c1700` (`canon/` at worktree tip; no `docs/canon-index.md` on ref)
**Overall:** FIX-NOW

## Fix-specific checks

- **[bug-repro] OK** — eight AST-2061 repros on the publish ref pin concrete To-be behavior (not tautologies); each should fail on pre-fix product (`6b00d8c5f` / pre-AST-2061) and pass against ftr with AST-2061 shipped:

  | Area | Test | What it pins |
  |------|------|----------------|
  | Job leak | `TestAst2061NoContactJobWrite::test_contact_markup_never_reaches_create_meteorite_job` | `create_meteorite_job` not called; dispatch returns `[]` for retired `create_contact_meteorite` markup |
  | Candidate write | `TestAst1073ContactEstelleTurnLoop::test_ast2061_skill_calls_never_write_candidate` | `run_contact_skill` / `save_candidate_data` not called; `skill_results == []`; ACL header absent from live prompt |
  | Sanitize (insert) | `TestAst2061ContactSanitize::test_insert_slack_meteorite_stores_sanitized_content` | stored `content == "Senior Eng"` from markup/entity payload |
  | Sanitize (paste) | `TestAst2061ContactSanitize::test_apply_paste_drops_script_content` | `content == "Senior Eng"` (not regex leftover `alert(1)`) |
  | Sanitize (land) | `TestAst2061ContactSanitizeEntry::test_land_blob_unwrapped_then_sanitized` | exact staged blob after unwrap + nh3 |
  | Sanitize (paste path) | `TestAst2061ContactSanitizeEntry::test_slack_paste_unwrapped_before_apply_paste` | `content == "Full JD https://x.io/j?a=1&b=2"`, state `READY` |
  | Public channel | `TestAst2061PrivateChannelGate::test_public_mention_refused_no_command_turn_or_save` | `accepted=False`, `channel_not_private`; resolve/command/paste/turn/post not called |
  | Registry | `TestAst2061ContactPinholeConfig::test_create_contact_meteorite_retired` | task key absent from `CONTACT_TASK_CONFIG` |

  Supporting (not all tagged `[bug-repro]`): autouse `_ast2061_private_channel_default`; `TestAst2061FetchChannelType`; pinhole spliced-exec assert; `test_mpim_mention_refused` encodes product decision that `mpim` ∉ allowlist.

- **## What must still hold — OK** (plan § AST-2062, conditional on AST-2061 on ftr):
  - Manifest retains `TestAst2035ContactCommandIntercept`, `TestAst2034InsertSlackMeteorite`, `TestAst1561ApplyPaste` — regression guard for intercept + NEW insert + paste shapes under sanitize.
  - No test pins double-encoded sanitize residual or payload length cap.
  - Retired names only appear as **absent/unknown** (`create_contact_meteorite` in dispatch repro; no live `save_candidate_*` exercise — fake `save_profile_field` / `sample_skill`).
  - `test_repo_admin_json.py` **unchanged** on diff (matches plan §5; Linear `## Component scope` still lists it — stale ticket text only).

## Canon scores

**Frozen list:** Linear AST-2062 Description has **no `## Citations` / frozen canon ids** (same fix-lane pattern as AST-2061).

*(No directive ids on the frozen list — zero graded rows.)*

**Notes:** Fix-board Joan **CANON: OK**; tests encode already-reviewed AST-2061 product. No Canon Scope ESCALATE from diff content.

## Column diff vs plan stage

`no plan-stage scores attached` (Joan fix-board only)

## Frame diff

(none)

## Findings

### fix-now

- **Location:** `data/admin/agent.json`, `data/admin/agent_task.json` on `origin/sub/.../AST-2062-estelle-pinhole-tests` (commits `33f5c0b1c`, `048d297b5`; not in `c904c7725` qa-fix)  
  **Finding:** Plan blast radius and ticket Boundaries require **tests + bible only; no `data/`**. Diff rewrites agent catalog (e.g. Grace `model_id` / `quantization`, prompt blocks) — unrelated to Estelle pinhole coverage and rides in via post–`merge-tests` sync/agent commits.  
  **Recommendation:** Before merge to `ftr`, **revert `data/admin/*` to `origin/ftr/AST-2055-estelle-pinhole`** (or drop those two commits from the publish ref). Do not land agent-catalog churn on this test-gap child.

### discuss

- **Location:** Linear AST-2062 `## Component scope` vs diff  
  **Finding:** Ticket lists `test_repo_admin_json.py` as modified; plan §5 says no change; diff agrees with plan.  
  **Default:** Leave file untouched; optional Linear scope tidy for Chuckles (process only).

- **Location:** Linear AST-2062 Description  
  **Finding:** No frozen canon list (same as AST-2061).  
  **Default:** Proceed on plan-fix + board bar once fix-now item cleared.

### advisory

- **Location:** Sub-branch history (`8aadab7a6 sync(dev)`, agent commits)  
  **Finding:** Extra non-test commits widen review surface; Betty’s `test(AST-2062)` + `merge-tests` commit is the intended product of qa-fix.  
  **Recommendation:** Chuckles: when appending Radia artifact, prefer citing `c904c7725` for test intent; tip `20fc3341` includes out-of-scope `data/` until reverted.

- **Location:** `docs/features/contact/ast-1517-create-contact-meteorite.md` on sub  
  **Finding:** Large doc append (plan + board + prior AST-2061 Radia) is normal fix-lane doc carry; not a test-tree violation.

## What's solid

- Repro-first design matches plan fixtures (public `app_mention`, sanitize payloads, skill_calls, retired task key).
- Channel gate tests fail-closed on lookup error; `event.channel_type` skips lookup; DM `message` not re-gated.
- Config pinhole test splices **real** `config.py` source — does not duplicate assert predicate.
- `TestAst2061FetchChannelType` maps `is_im` / `is_mpim` / `is_private` / `is_group` per plan table.
- No `src/` on three-dot diff; AST-2061 product assumed on ftr for green manifest.

## Chuckles — post-review branching

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **REVIEW** (fix-now: `data/`) | Normal (AST-2055 ftr) | → **Review Posted** → **`resolve-child`** (revert or excise `data/admin/*` on sub) → re-run manifest → **User Testing** after clean Radia pass |

**Do not** merge this sub to `ftr` with `data/admin` deltas from `33f5c0b1c` / `048d297b5`.

## Recommended actions (Chuckles downstream — not Radia)

1. Append artifact; `docs(AST-2062): Radia review — findings`; push on sub after engineer strips `data/`.
2. Post slim upshot `--as radia` (REVIEW until `data/` reverted).
3. Spawn **`resolve-child`** for Katherine/Betty: revert `data/admin/agent.json` and `data/admin/agent_task.json` to ftr tip; keep `c904c7725` test/bible commits.
4. Optional: trim misleading `test_repo_admin_json.py` line from Linear scope on next doc pass.

context_tokens≈24000

[code-rerubic] REVIEW (Commit: 20fc3341) drop data/admin churn

Fix typo in upshot - should be [code-rubric] not [code-rubtic]

[code-rubric] REVIEW (Commit: 20fc3341) drop data/admin churn

### Chuckles adjudication — fix-now `data/admin/*`

Not a defect. `33f5c0b1c` / `048d297b5` are Susan's own commits already on `origin/dev` (and `origin/main`), merged into this sub by `sync-child.sh`'s routine `sync(dev)` (`8aadab7a6`). The three-dot diff vs `ftr` shows them only because `ftr` has not absorbed `dev` since dispatch. `git diff origin/dev <sub> -- data/admin/` is empty, so landing `ftr` changes nothing there. Reverting them as recommended would undo Susan's `dev` work. No resolve-child; the remaining items are discuss/advisory only. Clean-review shortcut (do-all-the-things §3h) → User Testing after merge-tree dry-run.

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Katherine | engineer | `/home/susan/.cursor/chats/41478d0f1db935d4e257cb48678efa54/b154312d-6d49-4d35-b8f8-81940824bc05/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/1959c35a-7b7b-4840-9dbf-aeb7738e93d3/store.db` |
| Radia | review | `/home/susan/.cursor/chats/41478d0f1db935d4e257cb48678efa54/7f95a300-1863-41bc-b2d2-3b3b3cdd345a/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-2055 (parent) | ftr/AST-2055-estelle-pinhole |
| AST-2061 | sub/AST-2055/AST-2061-estelle-pinhole |
| AST-2062 | sub/AST-2055/AST-2062-estelle-pinhole-tests |

**Epic worktree:** `astral-AST-2055/` — one active sub checked out at a time.
