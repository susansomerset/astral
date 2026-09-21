# AST-1145 — Allow contact info tokens and | chars in fromBlock
**Component:** artifacts  
**Children:** AST-1147, AST-1148, AST-1149  
**Linear archived:** AST-1145 2026-08-11; AST-1147 2026-08-11; AST-1148 2026-08-11; AST-1149 2026-08-11

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-02 17:07 | AST-1147 | docs | `57606d9cb` | docs(AST-1147): plan — from-block token template config contract |
| 2026-08-02 17:13 | AST-1147 | code | `1db16f414` | code(AST-1147): extend COVER_FROM_BLOCK_CONFIG token template contract |
| 2026-08-02 17:13 | AST-1147 | docs | `30674c9e0` | docs(AST-1147): review stub after token template config |
| 2026-08-02 17:15 | AST-1147 | test | `3ed04ccab` | test(AST-1147): COVER_FROM_BLOCK_CONFIG token template contract |
| 2026-08-02 17:15 | AST-1147 | merge-tests | `df27f7239` | merge-tests(AST-1147): origin/tests 3ed04ccab |
| 2026-08-02 17:18 | AST-1147 | docs | `3c0518fad` | docs(AST-1147): Radia review — findings |
| 2026-08-02 17:33 | AST-1147 | resolve | `b6adb1d7d` | resolve(AST-1147): — clean |
| 2026-08-02 17:57 | AST-1149 | docs | `8572b8242` | docs(AST-1149): plan — from-block authoring help profile/session |
| 2026-08-02 18:00 | AST-1148 | docs | `fb615105b` | docs(AST-1148): plan — resolve tokens in from-block emit debug |
| 2026-08-02 18:06 | AST-1149 | code | `e33e3bfec` | code(AST-1149): from-block authoring help config + ui_config slice |
| 2026-08-02 18:07 | AST-1149 | code | `0029c82e6` | code(AST-1149): profile from-block tab help and placeholder |
| 2026-08-02 18:07 | AST-1149 | docs | `856f94705` | docs(AST-1149): review stub after authoring help build |
| 2026-08-02 18:07 | AST-1149 | code | `9155ed429` | code(AST-1149): session cover from-block authoring help |
| 2026-08-02 18:12 | AST-1149 | test | `562fd8bfe` | test(AST-1149): from-block authoring help profile/session chrome |
| 2026-08-02 18:13 | AST-1148 | code | `2c22cba54` | code(AST-1148): expand from-block tokens and migrate resolve |
| 2026-08-02 18:13 | AST-1148 | docs | `a2a05144b` | docs(AST-1148): review stub after from-block token expand |
| 2026-08-02 18:13 | AST-1148 | code | `e677b2c2d` | code(AST-1148): expand session-typed From via shared helper |
| 2026-08-02 18:20 | AST-1148 | test | `54123bd1b` | test(AST-1148): from-block token expand + resolve/session emit |
| 2026-08-02 18:27 | AST-1149 | docs | `b8f412837` | docs(AST-1149): Radia review — findings |
| 2026-08-02 18:31 | AST-1148 | docs | `4f8dc914f` | docs(AST-1148): Radia review — findings |
| 2026-08-02 18:32 | AST-1148 | resolve | `154f0a378` | resolve(AST-1148): — clean |
| 2026-08-02 18:33 | AST-1149 | resolve | `84d86b276` | resolve(AST-1149): — clean |
| 2026-08-02 18:36 | AST-1149 | merge-tests | `15c65f731` | merge-tests(AST-1149): origin/tests f59289f77 |
| 2026-08-02 18:39 | AST-1148 | merge-tests | `98cea0a19` | merge-tests(AST-1148): origin/tests 6f0230f82 |
| 2026-08-02 18:40 | AST-1145 | merge | `8e4c10f29` | Merge remote-tracking branch 'origin/dev' into tmp-refresh-AST-1145-… |
| 2026-08-11 18:13 | AST-1147 | docs | `02f399e26` | docs(AST-1147): archive Linear issue content |
| 2026-08-11 18:13 | AST-1148 | docs | `bf9aa0dbe` | docs(AST-1148): archive Linear issue content |
| 2026-08-11 18:13 | AST-1149 | docs | `99741c945` | docs(AST-1149): archive Linear issue content |
| 2026-08-11 18:15 | AST-1145 | docs | `fcbb66865` | docs(AST-1145): archive Linear issue content |

_Duplicate `test(AST-1147)`/`test(AST-1149)`/`test(AST-1148)` SHAs at the same minute (`73ad0b8d7`, `f59289f77`x1 dup, `6f0230f82`x1 dup) are re-pushes during a force-with-lease branch cleanup noted in the AST-1148 comments (see below) — omitted from the table above._

## Epic — AST-1145
_Archived: 2026-08-11 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1145/allow-contact-info-tokens-and-chars-in-fromblock · Status at archive: Archive · Project: Astral Artifacts · Assignee: chuckles · Priority / estimate: Urgent / — · Blocked by / blocks / related: —_

### Purpose

Cover letters need a candidate-owned **From** block that can mix contact tokens with ordinary text (including authoring `|`), so each candidate can keep a reusable contact header across cover letters without hardcoding values that drift when phone, email, or location change. AST-1124 / AST-1137 already store a from-block and compose a bullet default; this epic upgrades that contract so the default (and saved custom text) are token-driven, with `|` converted to `•` at emit the same way resume authoring uses pipes as separators that print as bullets.

### Functional scope

* **Tokenized From block:** From-block text may include contact tokens using consistent `{$TOKEN}` form. Allowed tokens for this surface: `FULL_NAME`, `LOCATION`, `CONTACT_EMAIL`, `PHONE` (existing registry names — brief aliases `RESUME_LOCATION` / `RESUME_EMAIL` / `CANDIDATE_MOBLE` are **not** added). At cover emit, those tokens resolve to the candidate's current values. Unrecognized `{$…}` tokens are left as-is for forward-compat (same as other text token surfaces).
* **Authoring `|` → printed `•`:** Candidates may put `|` in From-block text as an authoring separator. At emit, `|` separators convert to `•` (matching the AST-1137 golden / resume separator convention). Free text other than `|` is preserved.
* **Empty token / segment drop:** When a token resolves empty, omit that segment **and** its adjacent separator so recruiters never see dangling `•`, bare pipes, or unresolved placeholders in the printed From block.
* **Default when unset:** If the candidate has no saved from-block, emit uses a config-owned default template equivalent to two lines — `{$FULL_NAME} | {$LOCATION}` / `{$CONTACT_EMAIL} | {$PHONE}` — resolved and `|`→`•`, with empty segments omitted.
* **Persist across cover letters:** Saving the From block writes it to the existing candidate profile contact from-block field so the same authoring text is reused on later job and session cover emits. Empty / whitespace means "unset → default template."
* **Session-typed From:** Non-empty Admin Session Cover Letter From text runs the **same** token resolve + `|`→`•` + empty-segment rules before emit (not only candidate-saved / default paths).
* **Emit consumers:** Job Print Cover Letter and Admin Session Cover Letter both show the resolved From-block text inside the existing SomersetCover `fromBlock` region.
* **Debug (backend):** When `debug=True` on the resolve/emit path that expands from-block tokens, log Style D index headers plus working-detail lines for template source (candidate vs default vs session), tokens found/resolved/empty, `|`→bullet rewrite applied, and resolved text length — not batch-only summaries.

### Architectural definition

* **Patterns to reuse:** `pattern.config.config-block` (extend `COVER_FROM_BLOCK_CONFIG` for default token template, allowlisted tokens, `|`→`•` rewrite, empty-segment policy; no inline sets in core/UI); `pattern.ui.admin-endpoint` (persist via existing candidate profile data PUT; no new route).
* **New patterns proposed:** none — contact text tokens reuse the existing text-token registry / resolve path (not a SIGNATURE_IMAGE-style binary render token). No new alias names for the brief's typos.
* **Applicable statutes:** `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.standards.in-scope-only` / `astral.standards.no-cross-contamination`; `astral.standards.dry-and-focused-functions` / `astral.standards.public-then-helpers` (one expand path for candidate custom, default template, and session-typed From); `astral.standards.debug-contract-gated`; `astral.layers.import-direction`.

### Boundaries

* Does **not** change SomersetCover CSS/DOM chrome (`.fromBlock` layout stays AST-1124 / AST-1138 / AST-1139).
* Does **not** change cover `{$SIGNATURE_IMAGE}` render-token contract (AST-1125 / AST-1126).
* Does **not** register brief aliases `RESUME_LOCATION`, `RESUME_EMAIL`, or `CANDIDATE_MOBLE` / `CANDIDATE_MOBILE`.
* Does **not** add from-block content to the LLM prompt packet / Manage Tasks token pickers (AST-1137 kept it out of packet contact keys).
* Does **not** invent a second profile storage key — `contact.cover_letter_from_block` already owns persistence.
* Does **not** alter resume HTML header/contact strip.
* Does **not** treat From-block `|` as consult/rubric pipe-grade encoding.

### Acceptance criteria

1. With no saved from-block, Print Cover Letter and Session Cover Letter (empty From + selected candidate) emit a two-line From block with `•` between non-empty name/location and email/phone segments (AST-1137 golden shape).
2. Saving a custom From block on the candidate profile persists the authoring text (tokens and `|`); a later cover emit resolves tokens and prints `•` instead of `|`.
3. A saved From block with allowed contact tokens and `|` emits with tokens replaced, `|` shown as `•`, and no dangling separators when a token is empty.
4. Clearing the saved From block (empty/whitespace) returns emit to the default template behavior.
5. A non-empty typed Session Cover Letter From runs the same token + `|`→`•` + empty-segment rules before emit.
6. With `debug=True` on the touched resolve/emit path, logs show Style D index plus working-detail lines for source and token outcomes as described in Functional scope.
7. Resume print/HTML and signature-image token behavior are unchanged; brief token aliases are not resolvable.

### Dependencies and blockers

* AST-1124 (and children AST-1137 / AST-1138 / AST-1139) — candidate from-block field, `resolve_cover_from_block`, and SomersetCover fromBlock emit must be on the integration line this epic builds on. Soft gate: do not dispatch until that stack is safely on `origin/dev` or Susan explicitly overrides.
* none otherwise.

### Open questions

none

### Proposed child tickets

**1[!]: From-block token template + config contract — Ada** — Owns config for the default from-block token template, allowlisted token ids, `|`→`•` rewrite flag/literals, and empty-segment policy. Extends the existing from-block config block; does not implement resolve/emit behavior.
**Citations:** `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`.

**2: Resolve tokens in from-block + emit debug — Hedy** — Owns expanding allowlisted tokens, `|`→`•`, and empty-segment drop inside the shared from-block path used by job emit, session empty→candidate resolve, **and** non-empty session-typed From; Style D debug on the touched path. Consumes child #1 config. After #1.
**Citations:** `astral.standards.dry-and-focused-functions`; `astral.standards.debug-contract-gated`; `astral.standards.in-scope-only`.

**3: From-block authoring help on profile / session — Katherine** — Owns user-visible help (and any config-driven placeholder/label copy) so Susan can see that From supports the four tokens, that `|` authors as `•` in print, and what the default template looks like when unset. Does not own resolve math or HTML CSS. Parallel with #2 once #1 field labels/help strings exist.
**Citations:** `pattern.ui.admin-endpoint`; `astral.layers.import-direction`.

### Original brief

Add a "From" section to the cover letter, and use our default set of tokens and | to indicate the content to be displayed, so that the candidate could add other content if they wish.

When the user saves the Fromblock, then save that to the candidate_data profile content for future reference so that the change is persisted across coverletters. If there's no fromblock saved for the candidate, just use our default from the golden layout:

```
Susan Somerset • Oakland, CA
hire@susansomerset.com • 415-745-5238
```

`{$FULL_NAME} | {RESUME_LOCATION}\n{$RESUME_EMAIL} | {$CANDIDATE_MOBLE}`

#### Comments

##### chuckles — 2026-08-02T23:52:30.981Z
@susan

1. Printed separator: keep ` • ` (AST-1137 golden), switch default print to ` | `, or is `|` in the template only an authoring delimiter that becomes ` • ` at emit?
2. Token names: map brief `RESUME_LOCATION` / `RESUME_EMAIL` / `CANDIDATE_MOBLE` → existing `LOCATION` / `CONTACT_EMAIL` / `PHONE` with consistent `{$…}`, or add aliases as written (including the missing `$` / MOBLE spelling)?
3. Empty token + `|`: omit adjacent separator (segment drop), leave dangling separator, or leave unresolved `{$TOKEN}` literal?
4. Session-typed From (non-empty Admin field): same token + `|` rules before emit, or only candidate-saved / default template paths?

_(Resolved into the definition above: `|` is authoring-only and becomes ` • ` at emit; brief aliases are **not** added — existing `LOCATION`/`CONTACT_EMAIL`/`PHONE` names stay canonical; empty token/segment → drop the segment and its adjacent separator; session-typed From runs the same rules.)_

### Files changed (plan vs actual)

_No product commit trail on the parent — the one `merge origin/dev` commit is a routine refresh. Implementation landed via the three sub-issues below._

_Implementation detail may live in git history on `origin/dev`._

## Sub-issues

### AST-1147 — From-block token template + config contract
_Archived: 2026-08-11 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1147/from-block-token-template-config-contract-allow-contact-info-tokens · Status at archive: Archive · Project: Astral Artifacts · Assignee: ada · Priority / estimate: — · Blocked by / blocks / related: parent: AST-1145_

#### What this implements

Owns the config contract for a tokenized cover from-block default: default authoring template, allowlisted token ids, `|`→`•` rewrite literals, and empty-segment drop policy. Extends existing `COVER_FROM_BLOCK_CONFIG`. Does **not** implement resolve/emit (sibling AST-1148). Does **not** own profile/session help chrome (sibling AST-1149). Does **not** register brief aliases.

#### Acceptance criteria

Config half of parent AC1 (default template + allowlist + rewrite/empty policy declared for AST-1148 emit); AC7 (aliases not registered; no `TOKEN_SOURCES`/resume/signature edits).

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend `COVER_FROM_BLOCK_CONFIG` with default token template, allowlisted token ids, authoring/emit separator rewrite, and empty-segment policy. Keep AST-1137 keys intact for current resolve until AST-1148 migrates. Do not add brief aliases to `TOKEN_SOURCES` or this block | utils |

**Out of scope (siblings):** `resolve_cover_from_block` / builder from-block emit + Style D (AST-1148); profile/session help copy, placeholders, labels (AST-1149); SomersetCover CSS/DOM, `{$SIGNATURE_IMAGE}` (out of epic); `tests/` / bible (Betty).

#### Stage 1: Extend `COVER_FROM_BLOCK_CONFIG`

**Done when:** `COVER_FROM_BLOCK_CONFIG` declares the default token template, allowlist, `|`→`•` rewrite, and empty-segment policy as readable keys; AST-1137 keys still present and unchanged in meaning; no resolve/emit code changes; brief aliases absent from config.

Keep every existing AST-1137 key (`contact_key`, `segment_separator`, `line_separator`, `name_column`, `line_1_contact_paths`, `line_2_contact_paths`, `sources`). Add:

| Key | Value | Meaning for AST-1148 consumers |
|-----|-------|--------------------------------|
| `"default_template"` | `"{$FULL_NAME} \| {$LOCATION}\n{$CONTACT_EMAIL} \| {$PHONE}"` | Authoring-form default when saved from-block is empty/whitespace. Two lines joined by `line_separator`. Authoring separator between segments is bare `\|`. |
| `"allowed_token_ids"` | `("FULL_NAME", "LOCATION", "CONTACT_EMAIL", "PHONE")` | Only these registry names are expanded on the from-block surface. |
| `"authoring_separator"` | `"\|"` | Character candidates type as a segment separator in from-block text. |
| `"emit_separator"` | `" • "` | What `|` becomes at emit (spaces match AST-1137 golden / existing `segment_separator`). |
| `"empty_segment_policy"` | `"drop_with_adjacent_separator"` | When a token resolves empty (or a free-text segment is empty after strip), omit that segment **and** its adjacent authoring/emit separator. |

Update the block's leading comment to credit both AST-1137 and AST-1147 (keep the AST-1137 attribution). Do **not** add `RESUME_LOCATION`, `RESUME_EMAIL`, `CANDIDATE_MOBLE`, or `CANDIDATE_MOBILE` to `allowed_token_ids`, `TOKEN_SOURCES`, or any alias map. Do **not** change `TOKEN_SOURCES` entries for the four real tokens, `TOPIC_MENU_GEN_CONFIG["packet_contact_keys"]`, `BUILD_CONFIG["session_cover_letter"]`, or any core/UI/TSX file. Do **not** implement resolve that reads these new keys — that is AST-1148; this stage is declarative config only.

⚠️ **Decision:** Keep AST-1137 `line_*_contact_paths` / `segment_separator` keys alongside the new token-template keys. Current `resolve_cover_from_block` stays green until AST-1148 switches the default path to `default_template` + allowlist + rewrite. Removing path keys here would break emit mid-epic.

⚠️ **Decision:** `emit_separator` is `" • "` (spaced bullet), not bare `"•"`, so rewrite matches the AST-1137 golden and existing `segment_separator`. Sibling resolve must substitute `|` → `emit_separator` (not invent a third literal).

⚠️ **Decision:** `empty_segment_policy` is a single string enum value (`"drop_with_adjacent_separator"`), not a nested dict — AST-1148 implements the only allowed policy; if a second policy is ever needed, extend the string set in config then.

⚠️ **Decision:** No profile `placeholder` / `help` field metadata in this ticket. Ticket boundaries hand help chrome to AST-1149; config keys above are enough for emit to satisfy parent AC1's config half.

**Contract for siblings (non-goals):** AST-1148 must consume `default_template`, `allowed_token_ids`, `authoring_separator`, `emit_separator`, and `empty_segment_policy` inside the shared from-block expand path; unrecognized `{$…}` tokens stay as-is (forward-compat); Style D debug lives there. AST-1149 owns making the default template / `|`→`•` story discoverable on profile/session. This ticket only guarantees the keys exist with the values above.

**Self-Assessment:** `minor` — one utils config block extension; no core/UI behavior change. Conf high — the parent's open questions already map tokens and rewrite; the AST-1137 block is the clear extension point; the allowlist matches existing `TOKEN_SOURCES` names. Risk low — additive keys; existing resolve ignores unknown keys; no alias registration; siblings own consumption.

##### Comments

###### ada — 2026-08-03T00:08:12.713Z
Plan @ `9cd57e1f` (reminted after a `[thread-missing]` chat store.db rebuild). Scope minor — extend `COVER_FROM_BLOCK_CONFIG` only; no resolve/emit/UI. Conf high; Risk low.

###### joan — 2026-08-03T00:10:19.515Z (plan-rubric.v1)
**Overall: APPROVED.** Stage 1 → Purpose "tokenized From" + Functional scope "default template"; child #1 Proposed ticket. All in-scope statutes **conforms**.

###### betty — 2026-08-03T00:15:29.670Z
QA manifest AST-1147: `COVER_FROM_BLOCK_CONFIG` token template contract coverage in `test_config.py`. Publish `@ df27f723` (`merge-tests(AST-1147): origin/tests 3ed04ccab`).

###### radia — 2026-08-03T00:18:51.579Z (code-rubric.v1)
**Overall: DISCUSS** (procedural stragglers only). Three-dot vs `origin/dev` matches Stage 1 exactly: `COVER_FROM_BLOCK_CONFIG` gains `default_template`, `allowed_token_ids`, `authoring_separator`, `emit_separator`, `empty_segment_policy`; AST-1137 keys retained; boundaries vs AST-1148/1149 held; no brief aliases registered; diff also carries the Betty test corpus from `origin/tests` merge history (expected, not scope smuggling). No `fix-now`.

#### Resolution (2026-08-02)

Radia code-rubric DISCUSS, fix-now: none.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/utils/config.py` | Extend `COVER_FROM_BLOCK_CONFIG` with `default_template` / `allowed_token_ids` / `authoring_separator` / `emit_separator` / `empty_segment_policy` | `1db16f414` |
| | _tests_ | token template contract coverage | `3ed04ccab` — `test_config.py` + test-bible (Betty) |

### AST-1148 — Resolve tokens in from-block + emit debug
_Archived: 2026-08-11 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1148/resolve-tokens-in-from-block-emit-debug-allow-contact-info-tokens-and · Status at archive: Archive · Project: Astral Artifacts · Assignee: hedy · Priority / estimate: — · Blocked by / blocks / related: parent: AST-1145_

#### What this implements

Owns expanding allowlisted contact tokens, `|`→`•`, and empty-segment drop inside the shared from-block path used by job Print Cover Letter emit, session empty→candidate resolve, **and** non-empty session-typed From. Consumes AST-1147's `COVER_FROM_BLOCK_CONFIG` keys. Style D debug on the touched `debug=` expand/resolve path. Does **not** change SomersetCover CSS/DOM, signature-image tokens, profile/session help chrome (AST-1149), or register brief aliases.

#### Acceptance criteria

Parent AC1 (default composition via the template), AC2 (custom saved text resolves at emit), AC3 (tokens replaced, `|`→`•`, no dangling separators), AC4 (cleared from-block returns to default), AC5 (session-typed From uses the same rules), AC6 (Style D debug), AC7 (resume/signature unchanged; aliases not resolvable).

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Add shared `expand_cover_from_block_text`; rewrite `resolve_cover_from_block` to select authoring text (saved custom or `default_template`) then expand via that helper; Style D token/source/rewrite details when `debug=True`. Stop using the AST-1137 `line_*_contact_paths` composition for the default path (keys remain in config; do not delete) | core |
| `src/core/builder.py` | In `build_session_cover_letter`, when form `from_block` is non-empty (`source=session`), run the same expand helper before emit (pass candidate blob when loaded, else empty contact shape). Job path already consumes `resolve_cover_from_block` text — no second expand. Keep existing Style D `from_block_source` / `from_block_chars` lines | core |

**Out of scope (siblings):** `COVER_FROM_BLOCK_CONFIG` key declarations (AST-1147, already on `ftr`); profile/session help copy, placeholders, labels (AST-1149); SomersetCover CSS/DOM, `{$SIGNATURE_IMAGE}` (out of epic); brief aliases (never); `tests/` / bible (Betty).

#### Stage 1: Shared expand helper + resolve migration

**Done when:** `expand_cover_from_block_text` expands allowlisted tokens, rewrites `|`→`emit_separator`, drops empty segments per config policy; `resolve_cover_from_block` returns expanded text for both custom and default paths using `default_template` (no more path-based default composition); Style D details fire only when `debug=True`.

1. Add a module-level token regex `_FROM_BLOCK_TOKEN_RE = re.compile(r"\{\$([A-Z_]+)\}")` (do **not** import config's private `_TOKEN_RE`).
2. Public `expand_cover_from_block_text(text, candidate, *, source, debug=False) -> str`: allowlisted `{$TOKEN}` → candidate values; `|` → emit separator; empty segments dropped per `COVER_FROM_BLOCK_CONFIG`; unrecognized `{$…}` left as-is; `source` is a debug label only (`candidate`/`default`/`session`).
3. Implementation: `logger.set_debug_flag(debug)` first. Read `auth_sep`/`emit_sep`/`line_sep`/`policy`/`allowed` from `COVER_FROM_BLOCK_CONFIG` (no hardcoded literals) — raise `ValueError` naming the policy if it's ever not `"drop_with_adjacent_separator"` (only policy implemented). Build a walkable token view from `candidate` with the same dual-shape acceptance as `resolve_cover_from_block` (DB-row `candidate_data` shape or top-level token-view shape); fall back to `recompute_full_name` for `full` when empty. Inner `_lookup_allowed(name)`: not in `allowed` → `None` (leave `{$name}` literal); `TOKEN_SOURCES.get(name)` missing or not `source == "candidate"` → `None`; else walk `spec["path"]` on the view with a tiny local dotted-path walker (do **not** call `resolve_tokens`) and return the stripped string value (or `""`). Inner `_expand_segment` replaces tokens via the regex, counting `resolved`/`empty`/`left_as_is`. Normalize `\r\n`→`\n`; split on `line_sep`, then each line on `auth_sep` into segments, expand + strip each, **keep** only non-empty stripped segments, join keepers with `emit_sep`; drop lines that become empty; join surviving lines with `line_sep`. Does not mutate `candidate`, persist, or touch HTML.
4. `debug=True`: one `debug_index` (`func="candidate.expand_cover_from_block_text"`, outcome `success — from_block {source}`), then `debug_detail` lines `source=`, `tokens_found=`, `tokens_resolved=`, `tokens_empty=`, `tokens_left_as_is=`, `separator_rewrite=yes|no`, `text_chars=`. No lines when `debug=False`.

⚠️ **Decision:** Expand lives in `candidate.py` (not `builder.py`) so job resolve, session empty→resolve, and session-typed From share one path without pulling HTML into the library layer — same placement as AST-1137 resolve.

⚠️ **Decision:** Do **not** call `resolve_tokens()` for from-block text. The parent allowlist is a surface subset of `TOKEN_SOURCES`; `resolve_tokens` would expand every registry token (e.g. `{$GITHUB}`) and warn on empties. Walk `TOKEN_SOURCES` paths only for ids in `allowed_token_ids`.

⚠️ **Decision:** Segment-first algorithm (split lines → split on `authoring_separator` → expand tokens per segment → drop empty → join with `emit_separator`) implements `drop_with_adjacent_separator` literally. Do not regex-scrub dangling bullets after a blind global replace.

5. Rewrite `resolve_cover_from_block`: keep signature and return shape; resolve contact + custom raw exactly as today; custom non-empty → `authoring = raw.strip()`, `source="candidate"`; else `authoring = default_template`, `source="default"`, **deleting** the AST-1137 path-based line-composition block; `text = expand_cover_from_block_text(authoring, candidate, source=source, debug=debug)`; return `{"text": text, "source": source}`. `debug=True` Style D on resolve: one index (`func="candidate.resolve_cover_from_block"`, outcome `success — from_block {source}`) plus `source=` / `text_chars=` details (expand emits token/rewrite detail under its own index).

⚠️ **Decision:** Leave AST-1137 `line_*_contact_paths` / `segment_separator` / `name_column` keys in `COVER_FROM_BLOCK_CONFIG` untouched (AST-1147 contract). Resolve stops reading them; do not delete keys in this ticket.

#### Stage 2: Session-typed From uses the same expand

**Done when:** Non-empty Admin Session Cover Letter `from_block` is expanded with the same token / `|`→`•` / empty-segment rules before SomersetCover emit; empty→`resolve_cover_from_block` path already expands via Stage 1; job Print Cover Letter unchanged beyond consuming expanded resolve text.

In `build_session_cover_letter`, when the non-empty `from_block` special case fires (`source=session`): shape the candidate via `_candidate_for_cover_from_block(candidate_root)` when loaded, else an empty shape (`{"full":"","first":"","last":"","contact":{}}` — tokens resolve empty and drop; free text / unrecognized placeholders still emit); `normalized["from_block"] = expand_cover_from_block_text(raw, shaped, source=from_block_source, debug=debug)` — do **not** strip `raw` first (preserve internal newlines; expand normalizes `\r\n` itself). Empty form + `empty_uses_candidate_resolve` + candidate: keep calling `resolve_cover_from_block` (already expands) — do **not** double-expand. Job `build_cover_letter_from_job`: unchanged single call to `resolve_cover_from_block`. Do not change `_emit_somerset_cover_html_document`, SomersetCover CSS, signature-image token handling, resume builders, or profile persistence APIs. Existing builder Style D success details (`from_block_source`, `from_block_chars`, `document_path=somerset_cover`) stay; expand's own Style D covers token outcomes.

⚠️ **Decision:** Session-typed From does not write through to `contact.cover_letter_from_block` (AST-1139 contract unchanged). Expand is emit-only.

**Self-Assessment:** Single-Component — core candidate expand/resolve + one builder session call-site; no config key invention, no UI/CSS. Conf high — AST-1147 keys are on `ftr`; dual-shape contact handling and Style D patterns already exist. Risk Medium — cover emit is user-visible; a wrong empty-segment or allowlist rule would print dangling `•` / unresolved tokens / expand non-allowlisted registry tokens; mitigated by config-driven policy and one shared helper for all three sources.

##### Comments

###### hedy — 2026-08-03T01:00:46.400Z / 01:05:18.250Z
🛑 Plan publish blocked: epic worktree race with AST-1149 — while committing the plan, the shared epic worktree was switched onto the AST-1149 sub-branch, so the first push to the AST-1148 publish ref landed a tip whose ancestry incorrectly included AST-1149 plan commits. Hedy prepared a clean local tip and asked Susan to approve a `git push --force-with-lease` on the **child publish ref only** (never `dev`/`main`) to replace it, and flagged that the AST-1149 branch still carried the same pollution locally (not pushed to `origin/1149` — Katherine to reset/sync). Plan republished cleanly afterward. Scope Single-Component; Conf high — AST-1147 config keys already on `ftr`, dual-shape contact handling and Style D patterns already exist, allowlist-gated `TOKEN_SOURCES` walk avoids `resolve_tokens` expanding non-surface registry tokens; Risk Medium.

###### joan — 2026-08-03T01:10:47.452Z (plan-rubric.v1)
**Overall: APPROVED.** Stage 1 shared expand + resolve migration → Functional scope "Tokenized From block" / "`|`→`•`" / "empty segment drop" / "default when unset" / "Debug"; child #2 Proposed ticket. Stage 2 session-typed From → Functional scope "Session-typed From" + parent AC5. All in-scope statutes **conforms**. No `fix-now`.

**discuss — Stage 1 §4g, free text mixed with an empty token.** The parent says "when a token resolves empty, omit that segment and its adjacent separator." The plan drops a segment only when the *whole expanded segment* is empty after strip, so an authored segment like `Phone: {$PHONE}` with no phone on file keeps the label and prints `Phone:` — arguably the dangling artifact the parent wanted to avoid. This changes no acceptance criterion (the default template contains bare tokens only, so AC1–AC5 behave identically either way), and the alternative — dropping any segment containing an empty token — would silently delete text the candidate authored. Recommendation: add a fourth Decision stating the segment-level rule explicitly so Betty can pin the golden and Susan sees the mixed-segment behavior before it ships.

**discuss — Stage 1 §2/§4d, duplicated private helpers.** The plan defines a local token regex and a local dotted-path walker rather than importing config's private `_TOKEN_RE` / `_walk_dot_path`. No public equivalents exist, so the alternatives were importing privates across modules or promoting them in `config.py` (not in this ticket's Files Changed) — the plan made the in-scope-correct call. Flagging only so a later ticket can promote one public helper instead of carrying two copies.

**acceptable — self-assessment.** Single-Component / high / Medium is honest, Medium being the right call for a user-visible emit path; every Conf claim verified against the publish tip (AST-1147 keys present; `resolve_cover_from_block`'s dual-shape contact handling and `_candidate_for_cover_from_block`'s exact output shape confirmed).

###### betty — 2026-08-03T01:21:11.953Z
QA manifest AST-1148: token expand + resolve/session emit coverage in `test_candidate.py` / `test_builder.py`. Publish `@ 98cea0a1` (`merge-tests(AST-1148): origin/tests 6f0230f8`).

###### radia — 2026-08-03T01:31:28.597Z (code-rubric.v1)
**Overall: CLEAN.** `expand_cover_from_block_text` matches Stage 1 exactly: separators/policy/allowlist/template read only from `COVER_FROM_BLOCK_CONFIG`, allowlist-gated `TOKEN_SOURCES` walk (not `resolve_tokens` — confirmed no non-allowlisted registry token can leak). Single-expand invariant traced across all three call sites (job: one `resolve_cover_from_block` call; session empty+candidate: `resolve_cover_from_block` expands once internally; session-typed non-empty: `expand_cover_from_block_text` directly, no double-expand) — grepped every call site in `src/` to confirm. `_candidate_for_cover_from_block` (reused unchanged) never sets `candidate_data`, so expand correctly takes the token-view branch. Style D: two distinct `debug_index` calls (resolve's own + expand's own), each a single-item `index=1/total=1` (not a batch loop). Raw session `from_block` text passed un-stripped into expand per plan. No fix-now, no discuss.

#### Resolution (2026-08-03)

Clean sign-off — no fix-now, no discuss, no Frame diff adds. No product or plan-doc code changes in resolve.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/core/candidate.py` | `expand_cover_from_block_text` + `resolve_cover_from_block` migrates to `default_template` expand | `2c22cba54` |
| ✓ | `src/core/builder.py` | Session-typed From calls the shared expand before SomersetCover emit | `e677b2c2d` |
| | _tests_ | token expand + resolve/session emit coverage | `54123bd1b` — `test_candidate.py` / `test_builder.py` + test-bible (Betty) |

### AST-1149 — From-block authoring help on profile / session
_Archived: 2026-08-11 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1149/from-block-authoring-help-on-profile-session-allow-contact-info-tokens · Status at archive: Archive · Project: Astral Artifacts · Assignee: katherine · Priority / estimate: — · Blocked by / blocks / related: parent: AST-1145_

#### What this implements

Owns user-visible authoring help (and config-driven placeholder/label copy) so Susan can see that Cover From supports the four allowed tokens, that `|` authors as `•` in print, and what the default template looks like when unset — on Candidate Profile and Admin Session Cover Letter. Consumes AST-1147's `COVER_FROM_BLOCK_CONFIG` keys. Does **not** implement resolve/emit math or SomersetCover CSS. Does **not** invent a new save route.

#### Acceptance criteria

Discoverability side of AC1 (default template visible as placeholder), AC2 (help documents that saved custom text resolves), AC5 (session help documents the same typed-From rules), AC7 (no allowlist/template/signature edits; no alias strings).

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `authoring_help` + `session_authoring_help` to `COVER_FROM_BLOCK_CONFIG`. Move `contact.cover_letter_from_block` into its own `DATA_SHAPES` profile section with `placeholder` (= `default_template`) and `help` (= `authoring_help`) | utils |
| `src/ui/api/api_system.py` | Expose a small `cover_from_block` slice on `GET /api/ui_config` from `COVER_FROM_BLOCK_CONFIG` (help + default template) for Session Cover Letter | ui |
| `src/ui/frontend/src/components/FormFields.tsx` | Extend `Field` with optional `placeholder?` / `help?` so shapes JSON is typed | ui |
| `src/ui/frontend/src/components/TabbedTextArea.tsx` | Extend `TextTab` with optional `help?`; render muted help text above the textarea when present; pass `placeholder` through | ui |
| `src/ui/frontend/src/pages/CandidateProfile.tsx` | When building `textTabs`, pass `placeholder` and `help` from the section's first field (shapes); no hardcoded token names in the page | ui |
| `src/ui/frontend/src/pages/AdminSessionCoverLetter.tsx` | Load `/api/ui_config`, replace the intro help `<p>` with `cover_from_block.session_authoring_help`, show `cover_from_block.authoring_help` under the From field; optional From textarea `placeholder` = `default_template` | ui |

**Out of scope (siblings):** `COVER_FROM_BLOCK_CONFIG` token template / allowlist / rewrite / empty-policy keys (AST-1147, already on `ftr` — consume only); `resolve_cover_from_block` / builder emit / Style D (AST-1148); SomersetCover CSS/DOM, `{$SIGNATURE_IMAGE}` (out of epic); new admin/candidate routes (existing `PUT /api/candidates/<id>/data` stays); `tests/` / bible (Betty).

#### Stage 1: Config authoring chrome + profile shape visibility

**Done when:** `COVER_FROM_BLOCK_CONFIG` carries profile + session help strings; `DATA_SHAPES` exposes from-block as its own profile tab section with `placeholder`/`help` bound to those strings; `/api/ui_config` returns a `cover_from_block` object Session can read.

Add `"authoring_help"` (`"Allowed tokens: {$FULL_NAME}, {$LOCATION}, {$CONTACT_EMAIL}, {$PHONE}. Type | between segments; cover print shows •. Leave empty to use the default template (see placeholder)."`) and `"session_authoring_help"` (longer paragraph covering the same tokens/`|`/empty-candidate rules plus the existing signature-image and no-database-save notes) to `COVER_FROM_BLOCK_CONFIG`. In `DATA_SHAPES["candidates"]["detail"]["profile"]`, **remove** `contact.cover_letter_from_block` from the "Cover Letter Signature" group and insert a new one-field "Cover Letter From" section immediately after it (before "Signature Image"), with `placeholder: COVER_FROM_BLOCK_CONFIG["default_template"]` and `help: COVER_FROM_BLOCK_CONFIG["authoring_help"]` — not required. In `api_system.py`'s `ui_config()`, add a `"cover_from_block"` object with `default_template` / `authoring_help` / `session_authoring_help`. Do **not** change any AST-1147 key value; do **not** touch `candidate.py` or `builder.py`.

⚠️ **Decision:** Own `DATA_SHAPES` section ("Cover Letter From") instead of sharing "Cover Letter Signature". `CandidateProfile` maps each tab section to `sec.fields[0]` only — today from-block is `fields[1]` and never renders. A dedicated one-field section makes the textarea visible without rewriting `TabbedTextArea` into multi-field panels.

⚠️ **Decision:** Help copy lives in `COVER_FROM_BLOCK_CONFIG` (not hardcoded in TSX) — token names appear in those strings so the UI only renders config text, no React assembly of allowlists. Slight string overlap with `allowed_token_ids` is intentional for a single user-facing sentence.

⚠️ **Decision:** Profile `placeholder` reuses `COVER_FROM_BLOCK_CONFIG["default_template"]` by reference so the unset default is not duplicated as a second literal.

#### Stage 2: Profile tab shows help + placeholder

**Done when:** Candidate Profile "Cover Letter From" tab shows the from-block textarea with placeholder = default template and muted help listing tokens + `|`→`•` + empty→default. Save path unchanged (existing PUT).

`TabbedTextArea` renders a muted paragraph (reusing the signature-image blurb style) above the textarea when `tab.help` is set, and keeps passing `placeholder`. `CandidateProfile.tsx`'s `textTabs` map sets `placeholder: f.placeholder ?? (isResume && hasBaseResume ? "Locked — base resume has been generated from this text" : undefined)` (shapes placeholder wins; resume-lock override preserved) and `help: f.help?.trim() || undefined`. No token/`|`/`•` literals added in the page beyond rendering `f.help`/`f.placeholder` from shapes.

#### Stage 3: Session Cover Letter help parity

**Done when:** Admin Session Cover Letter intro and From-field help document the same token + `|`→`•` + empty→default authoring rules from config (not hardcoded page copy).

On mount, fetch `/api/ui_config`, read `cover_from_block` into state (default empty strings if missing). Replace the static intro `<p>` with `session_authoring_help` when non-empty; keep the existing AST-1139 intro text as a **fetch-failure-only fallback**. Render muted `authoring_help` under the From field label; set the From textarea placeholder to `default_template` when non-empty. Do not change Open HTML gating (from_block optional when a candidate is selected, per AST-1139); do not compose defaults in React; do not call resolve helpers from the page.

**Self-Assessment:** Single-Component — utils config + shapes + thin `/api/ui_config` exposure + profile/session help wiring; no resolve/emit. Conf high — AST-1147 keys are on `ftr`; `TabbedTextArea` already supports placeholder; the visibility fix is a one-field section split matching Signature Image's own-section pattern. Risk low — additive help chrome; save/emit paths untouched; wrong help text confuses authoring but cannot break HTML emit.

##### Comments

###### katherine — 2026-08-03T00:58:13.200Z
Plan @ `765c24af`. Scope Single-Component — utils config + shapes + thin `/api/ui_config` exposure + profile/session help wiring; no resolve/emit. Conf high; Risk low.

###### joan — 2026-08-03T01:03:20.044Z (plan-rubric.v1)
**Overall: APPROVED.** Stage 1 config help + `DATA_SHAPES` section + `ui_config` slice → Functional scope "Persist across cover letters" / "Session-typed From"; child #3 Proposed ticket. Stage 2 profile tab help/placeholder → discoverability side of AC2. Stage 3 session help parity → AC5. `astral.layers.ui-config-driven-business-logic`: React renders config strings; Stage 2/3 forbid composing the allowlist or defaults in the page. `astral.standards.dry-and-focused-functions`: **needs-discussion** — Stage 3 keeps the AST-1139 static intro paragraph as a fallback while adding near-identical copy to `session_authoring_help` (two copies of the same user-facing text).

**discuss — Stage 3 §1, duplicated session intro copy.** The config value is a plain literal that can never be absent, so the TSX fallback paragraph only ever covers an API failure. Recommendation: either drop the static paragraph and render a short neutral string on fetch failure, or add a one-line comment saying the literal is a fetch-failure fallback so a later reader doesn't edit the wrong copy.

**discuss — Stage 1 §1, help prose restates the allowlist.** `authoring_help` spells out the four tokens, duplicating AST-1147's `allowed_token_ids`. Recorded as a deliberate Decision (one readable sentence beats assembling prose from a tuple) and both copies live in config, so no statute is violated. Recommendation: add a comment on `allowed_token_ids` pointing at `authoring_help` so a future allowlist change updates both.

**R6 checklist:** definition-fidelity, layer/import, config-as-SoT, and file-placement passes all clean; no batch/state-machine/`do_task` concerns. Adversarial checks against the publish tip: no `DATA_SHAPES` schema validator exists that the new `placeholder`/`help` keys would trip; `/api/shapes/<entity>` returns the dict wholesale; `CandidateProfile`'s only positional consumer (`sections[0]` contact, `slice(1)` tabs) means the new section adds a tab without shifting the contact grid; Stage 2's placeholder fallback preserves the resume-lock override correctly.

###### betty — 2026-08-03T01:13:23.494Z
QA manifest AST-1149: authoring help profile/session chrome coverage across config, `api_system`, and frontend page tests. Publish `@ 15c65f73` (`merge-tests(AST-1149): origin/tests f59289f7`).

###### radia — 2026-08-03T01:27:44.792Z (code-rubric.v1)
**Overall: DISCUSS** — no fix-now. Diff matches the plan almost line-for-line: help/placeholder stay in `COVER_FROM_BLOCK_CONFIG`; no token/`|`/`•` literals invented in TSX; no new routes; no resolve/emit touched. `COVER_FROM_BLOCK_CONFIG["authoring_help"]` / `["session_authoring_help"]` are the only source of the token/`|`→`•` prose — `CandidateProfile.tsx` / `TabbedTextArea.tsx` render `f.help`/`f.placeholder` without re-deriving it. `AdminSessionCoverLetter.tsx` keeps a `SESSION_INTRO_FALLBACK` as a fetch-failure-only fallback (matches Joan's discuss item — does not compose config in React). The new "Cover Letter From" `DATA_SHAPES` section fixes the real `sec.fields[0]`-only bug (from-block was `fields[1]`, invisible) exactly per the plan's Decision.

#### Resolution (2026-08-02)

Clean — Radia DISCUSS with no fix-now; Frame diff none.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/utils/config.py` | `authoring_help` + `session_authoring_help`; own `DATA_SHAPES` "Cover Letter From" section | `e33e3bfec` |
| ✓ | `src/ui/api/api_system.py` | `cover_from_block` slice on `GET /api/ui_config` | `e33e3bfec` |
| ✓ | `src/ui/frontend/src/components/FormFields.tsx` | `Field` gains `placeholder?` / `help?` | `0029c82e6` |
| ✓ | `src/ui/frontend/src/components/TabbedTextArea.tsx` | `TextTab` gains `help?`; muted help render | `0029c82e6` |
| ✓ | `src/ui/frontend/src/pages/CandidateProfile.tsx` | `textTabs` pass `placeholder` / `help` from shapes | `0029c82e6` |
| ✓ | `src/ui/frontend/src/pages/AdminSessionCoverLetter.tsx` | Config-driven intro + From help/placeholder | `9155ed429` |
| | _tests_ | authoring help profile/session chrome coverage | `562fd8bfe` — config / `api_system` / frontend page tests + test-bible (Betty) |
