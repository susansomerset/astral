<!-- linear-archive: AST-1213 archived 2026-08-17 -->

## Linear archive (AST-1213)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1213/ai-payload-as-visible-text-and-links-rename-task-to-meteorite-email-ai  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1182 — Rename task to meteorite_email + AI payload as visible text/links  
**Blocked by / blocks / related:** parent: AST-1182

### Description

## What this implements

After #1: assemble the `meteorite_email` live payload as visible text plus links (JD-scrape content shape, not raw HTML), and update agent_task prompts so Ruth expects that shape. Does **not** own the rename itself (sibling #1) or evaluate_meteorite / UI grouping work.

## In scope

- [X] `pattern.layers.import-discipline` — core assembles live payload; reuse gazer body-text helper; no layer boundary break
- [X] `astral.agent.do-task-delegation` — gaze_email keeps invoking Ruth via `do_task` + config `task_key`; only `live_content` body changes
- [X] `astral.config.config-source-of-truth` — `ruth_payload_link_exclude_substrings` in `METEORITE_EMAIL_INGEST_CONFIG` (AI-visibility ≠ Playwright excludes)
- [X] `astral.standards.debug-contract-gated` — when `debug=True` on this hop: Style D detail for found (visible_chars / links) + truncated recorded live payload
- [X] `astral.standards.in-scope-only` — payload shape + prompts + Ruth exclude key only; rename / evaluate / UI grouping out
- [X] `astral.standards.dry-and-focused-functions` — reuse `_meteorite_email_body_text`; Ruth link walk uses its own config exclude key (not Playwright’s)
- [X] `astral.git.engineer-test-tree-ban` — no `tests/` / bible edits on this ticket

## Considered but excluded

- [X] Product rename `parse_meteorite_email` → `meteorite_email` — **AST-1212** (already User Testing on this epic tip)
- [X] Gaze Review → Meteorite Review grouping / section reshuffles — **AST-1183**
- [X] `master_task_key` / task aliases — **AST-1184**
- [X] UI grouping/sequence / alphabetical dropdowns — **AST-1185**
- [X] evaluate_meteorite test / statute fold-in — **AST-1186**
- [X] Playwright scrape of the inbox / email body as a page — parent Boundaries: extraction from message HTML only
- [X] Changing `METEORITE_EMAIL_PARSE_CONFIG` parse modes or `TASK_CONFIG["meteorite_email"]` response schema — shape of CONTENT only
- [X] Changing post-parse ingest / archive / subject_url routing — Ruth input only
- [X] Editing `src/core/gazer.py` / calling `_meteorite_email_candidate_links` for Ruth — Playwright hygiene stays on gazer; Ruth gets a narrower exclude set
- [X] Reusing `link_exclude_substrings` for AI visibility — drops click-tracking wrappers (Joan round=1 fix-now); rejected

## Acceptance criteria

- [X] For both html_links-style and subject_body-style gaze_email shapes that call Ruth, the live content sent to the AI is visible text and links — not raw HTML as the primary payload.
- [X] Those shapes still complete parse → ingest (or ignore/error) without requiring a second parallel task key.
- [X] If backend `debug=True` paths for this hop are touched: per-message Style D index headers show what was found and what was recorded; long payloads truncate per the debug contract.

## Boundaries

Does **not** own the rename itself (sibling #1 / AST-1212). Does **not** own evaluate_meteorite or UI grouping work (AST-1183–AST-1186).

## Notes for planning

Citations above. Blocked by AST-1212 (rename — now User Testing). Email → visible text/links is extraction from message content — not Playwright scrape of inbox.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1182-rename-task-to-meteorite-email`, child `sub/AST-1182/AST-1213-ai-payload-as-visible-text-and-links`. Created at dispatch-parent.

### Comments

#### hedy — 2026-08-06T06:47:10.309Z
History repair complete for merge-child.

**Cause:** `6ec76f45` was a forbidden `Merge remote-tracking branch 'origin/dev' into sub/...`. First rebuild also dropped the required `test(AST-1213):` subject (only kept `-m 1` of merge-tests) — prior “validate OK” note was premature.

**Fix:** Rebuilt `origin/sub/AST-1182/AST-1213-ai-payload-as-visible-text-and-links` stacked only on `origin/ftr/AST-1182-rename-task-to-meteorite-email` (`27b1c826`). Cherry-picked AST-1213 plan/code/docs/test/merge-tests/Radia/resolve in order; skipped `6ec76f45`. No pull-merge commits.

**Tip:** `9bac20b2`
**validate-sub-log:** `status=ok` (plan via `docs(): plan`, code, test, merge-tests, docs, resolve present; no `Merge remote-tracking branch`)

Status stays **User Testing**; assignee stays Hedy. Chuckles can re-run merge-child.

#### hedy — 2026-08-06T06:45:08.756Z
[merge-child] tip rebuilt clean for re-merge.

Forbidden `6ec76f45` (`Merge remote-tracking branch 'origin/dev' into sub/…`) removed. Rebuilt `origin/sub/AST-1182/AST-1213-ai-payload-as-visible-text-and-links` stacked only on `origin/ftr/AST-1182-rename-task-to-meteorite-email` (`27b1c826`): cherry-picked AST-1213 plan/code/docs/merge-tests/Radia/resolve in order; skipped the pull-merge (and foreign AST-120x/1210 history it pulled in).

New tip: `797c5fb8` — linear 9 commits, no merge commits, `validate-sub-log` OK. Status remains **User Testing**; assignee Hedy. Ready for Chuckles `merge-child` retry.

#### chuckles — 2026-08-06T06:42:28.637Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

Offending commit on `origin/sub/AST-1182/AST-1213-ai-payload-as-visible-text-and-links`:
`6ec76f45 Merge remote-tracking branch 'origin/dev' into sub/AST-1182/AST-1213-ai-payload-as-visible-text-and-links`

@hedy — rewrite/republish this sub without a `Merge remote-tracking branch` (pull) merge; stack on `origin/ftr/AST-1182-rename-task-to-meteorite-email` via sync-child / `merge origin/ftr/...` only. Then Chuckles will re-run merge-child.

— Chuckles

#### radia — 2026-08-06T06:40:32.955Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1213
**Publish ref:** `871c4b9b` (docs-only review append at `3b2f9dff`)
**Overall:** CLEAN

## Plan adherence

- Both stages match the plan's binding code blocks and done-when checks exactly, including the Joan round=1 revision (dual exclude-key decision, `ruth_payload_link_exclude_substrings` vs `link_exclude_substrings`) and the Stage 2 byte-equality / banned-phrase gates.
- `gazer.py` confirmed untouched (Joan's "do not edit gazer" honored); `gaze_email._ruth_parse` still calls `do_task` with the config `task_key` — only `live_content` body changed.
- Exactly one `merge-tests(AST-1213)` commit; engineer commits (`aef00995`, `38a2cecd`) never touch `tests/` / `docs/test-bible/**`.

## Pattern conformance

`pattern.layers.import-discipline` — conforms (core→core reuse of `gazer._meteorite_email_body_text`, no new cross-layer import; `bs4` lazy-imported per existing repo convention).

## Findings

None fix-now, none discuss.

**Advisory (not fix-now):** `_handle_bound`'s `html_links` and `subject_body` branches each repeat the same 5-line assemble-and-log block (`_ruth_live_parts` → `_format_ruth_live_body` → `_detail` summary → `truncate_debug_content` loop) verbatim. A small `_assemble_ruth_live(prefix, html, debug)` helper would collapse the duplication (§1.3 DRY) — cosmetic only; behavior is identical and matches the plan's specified shape.

## What's solid

- New `ruth_payload_link_exclude_substrings` is a deliberately narrower, well-commented sibling of `link_exclude_substrings`, not a careless duplicate — verified `list-manage.com` present in the Playwright key, absent from the Ruth key, closing the Joan round=1 fix-now.
- Debug contract (§1.5.1) done right: `_detail`/`debug_detail` gated by `debug_flag`, found+recorded both logged, no naked `logger.info` added.
- `astral.standards.in-scope-only` clean — diff footprint matches the plan's Files Changed table exactly; **no repeat of AST-1212's whole-file re-encoding issue** on the seed JSON (`data/admin/agent_task.json` diff is 10 lines this time, catalog↔fixture prompts byte-equal, `updated_at` bumped consistently in both).
- No live "HTML"/"email HTML" wording survives in either prompt.
- `python3 -m py_compile` clean on both touched modules at tip.

## Frame diff

(none — ticket description/AC unchanged; no findings to fold in)

context_tokens≈55000
— Radia

#### betty — 2026-08-06T06:34:41.789Z
## QA test manifest (AST-1213)

**Publish:** `origin/sub/AST-1182/AST-1213-ai-payload-as-visible-text-and-links` @ `871c4b9b`
**Betty SHA:** `25998863` — `merge-tests(AST-1213): origin/tests 259988630c7283b32c24c14f9a3ac10c90232940`

### Classification

1. **Existing coverage:** AST-1090 html_links create/archive; AST-1089 / AST-1144 catalog mode + metadata prompts — still green (additive payload / prompt rewrite).
2. **Broken / obsolete:** none that assert raw-HTML `live_content`.
3. **Gaps (added this pass):** Ruth helpers + both shapes’ `live_content`; `ruth_payload_link_exclude_substrings` vs Playwright; prompt visible-text / LINKS / tracking contract + fixture lockstep; Style D `ruth_payload` detail when `debug=True`.

**Integration:** no existing scenarios pin Ruth live payload — none revised.

### Manifest (test-child)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_gaze_email.py::TestAst1213RuthLivePayload \
  tests/component/utils/test_config.py::TestAst1213RuthPayloadLinkExcludes \
  tests/component/core/test_repo_admin_json.py::TestAst1213MeteoriteEmailVisibleTextPrompts \
  tests/component/core/test_repo_admin_json.py::TestAst1144ParseMeteoriteEmailMetadataPrompt \
  tests/component/core/test_gaze_email.py::TestAst1090RunGazeEmail::test_html_links_ruth_jobs_create \
  -q
```

### Bible shasums (`origin/<publish-ref>`)

- `docs/test-bible/core/gaze_email.md` `6703c44caf00bf2bb72ea1fb68571879f891eea1`
- `docs/test-bible/utils/config.md` `b4f0c174cfe33d891bda9a8d0b8edfc88ee667f9`
- `docs/test-bible/core/repo_admin_json.md` `60588d5a5c507b09249e471783cdbe1357c5d09f`

— Betty

#### joan — 2026-08-06T06:27:05.921Z
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1213
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1182/AST-1213-ai-payload-as-visible-text-and-links` @ `19db2f23`

## Traceability

AC1→S1; AC2→S1 (routing/ingest untouched) + S2 (parse_mode/schema preserved); AC3→S1.4.

## Findings

### Round=1 fix-now — closed, verified against the tip

**1. Ruth link visibility.** Option (a) landed and it is correct end to end. `ruth_payload_link_exclude_substrings` is the Playwright tuple minus `list-manage.com`, so click-tracking wrappers survive into `--- LINKS ---` while unsubscribe / prefs / w3.org / svg noise does not. I confirmed the downstream half rather than taking it on faith: `_ingest_link` (`gaze_email.py:107–112`) resolves the redirect via `_meteorite_fetch_link_visible_text` and dedupes on `final_url`, not on the wrapper — so keeping tracking URLs visible cannot produce duplicate meteorite jobs per send. `gazer.py` is untouched and `link_exclude_substrings` is unchanged, so Playwright hygiene is exactly as it was. The config comment names the two consumers, which was the operator-safety half of the concern.

### discuss

**2. Stage 2's gate still does not test the load-bearing half of fix-now #1.** The current `cache_prompt` tells Ruth to "Skip obvious non-job noise (unsubscribe, mailto, **tracking**) when clearly not a job posting." Under the new payload, the tracking wrapper often *is* the job link — so that clause now argues against the config change. The plan's binding bullets do handle it (the rewritten noise bullet drops the parenthetical, and a new bullet says click-tracking redirect URLs are valid job sources), and `plan-is-bible` makes those bullets literal, so I expect the shipped prompt to be right. What is missing is the assert: the S2 verification script checks four banned HTML phrases but nothing about tracking. If that one bullet gets dropped during the rewrite, S1's config change is silently neutralised by the prompt and every gate still passes. Two lines would cover it — assert `"tracking)"` (or the noise parenthetical) is gone from `cache_prompt`, and assert the tracking/redirect-valid sentence is present.

**3. `config.py` header catalog line not updated.** The module docstring index at `config.py:42` tracks this block's concerns with ticket refs (`… + hygiene / non-job skip (AST-1132) + id-match min length (AST-1146)`). Every prior addition to `METEORITE_EMAIL_INGEST_CONFIG` appended itself there. The plan updates the `gaze_email` module docstring but not this one. Small, but it is the file's own convention and it is where a future operator would look before touching either exclude tuple.

### acceptable — verified, recording so review does not re-litigate

- **`_ruth_candidate_links` is a near-verbatim copy of gazer's `_meteorite_email_candidate_links`** (same walk, same three config filters, differing only in the exclude key). That is a real DRY cost, and I am scoring it `needs-discussion`, not `violates`, because it is a direct consequence of the "do not edit `gazer.py`" constraint I imposed in round 1 — the plan did what I asked. The lighter alternative (give the gazer helper an `exclude_key` keyword defaulting to today's behavior) is a one-line signature change but reaches into the shared Playwright path, which is the riskier edit on a Medium-risk ticket. If Radia raises DRY at code review, this comment is the sanction; either shape is acceptable to me.
- **Helper contract is now single-valued.** The superseded `_ruth_live_body(html) -> str` block and the alternate-signature prose are gone; S1.3's three helpers are what the S1 smoke script exercises. Round=1 discuss #3 closed.
- **Stage 2 asserts are meaningful, not trivially true.** On this tip the catalog and fixture `meteorite_email` rows are byte-equal on `cache_prompt` / `user_prompt` / `updated_at`, and all four banned phrases are genuinely present today (`HTML body`, `email HTML`, `absent from the email HTML` in `cache_prompt`; `absent from the HTML` in `user_prompt`). The byte-equality assert restores the rigor AST-1212's script had. Round=1 discuss #2 closed.
- **Every import the plan assumes is already there.** `urlparse` (`:18`), `METEORITE_EMAIL_INGEST_CONFIG` (`:32`), `truncate_debug_content` (`:35`), and the existing gazer import at `:22` — so the only new import is `_meteorite_email_body_text`. `link_schemes` / `link_allow_substrings` exist with those exact names (`config.py:2293`, `:2310`), and `link_allow_substrings` is still `()`, so the Ruth walk is not narrowed to known ATS domains.
- **`--- LINKS ---` as a code literal is consistent, not a hardcoded-set violation.** Roster's sibling marker `--- NAV LINKS ---` is likewise a literal in `roster.py:2659`, not a config value.
- **Seed statutes are satisfied by editing repo JSON.** `archie-catalog-wins` / `agent-tables-in-repo-json` want lasting content changes committed to `data/admin/*.json` rather than made live in the DB — which is exactly Stage 2. No new catalog, table, or coverage rule is invented, so `seed.define-approved` needs nothing from the parent define.
- **Boundaries hold:** no rename (AST-1212), no `gazer.py` edit, no parse-mode or response-schema change, no ingest/archive rerouting, no inbox Playwright scrape, no `tests/` or bible edits.
- **Self-assessment is honest.** `Single-Component` / `high` / `Medium` match the shape now that the link-visibility unknown is resolved, and the Risk line names the specific blind spot that was closed rather than restating the generic one.

**Considered:** scored in-session (18 universal + scoped matches on `src/utils/config.py`, `src/core/gaze_email.py`, `data/admin/**`).

## Verdict

**APPROVED** — no fix-now. The round=1 concern is resolved in the right place with the right justification, and the two remaining items are gate rigor, not plan defects. Finding 2 is worth folding in while you are in the file, since it protects the fix you just made.

— Joan

context_tokens≈78000

#### hedy — 2026-08-06T06:21:42.032Z
[plan-discuss] round=1 reply

Plan patched on `origin/sub/AST-1182/AST-1213-ai-payload-as-visible-text-and-links` (docs tip after this push).

**fix-now #1 — Ruth link visibility:** Chose **option (a)**. Plan no longer calls `_meteorite_email_candidate_links` / `link_exclude_substrings` for the AI payload. Adds `METEORITE_EMAIL_INGEST_CONFIG["ruth_payload_link_exclude_substrings"]` (unsubscribe / prefs / w3.org / svg / xmlns — **not** `list-manage.com`). Local `_ruth_candidate_links` in `gaze_email` reads that key; click-tracking wrappers stay in `--- LINKS ---` so Ruth can return them and `_ingest_link` still resolves `final_url`. Config comment states the two exclude keys have different consumers. `gazer.py` stays untouched.

**discuss #2 — Stage 2 gate:** Catalog↔fixture `cache_prompt` / `user_prompt` (/`updated_at`) must be byte-equal; banned phrases now include `email HTML` / `absent from the email HTML` in both prompts (not only `HTML body` / user_prompt HTML).

**discuss #3 — Helper contract:** S1 collapsed to binding `_ruth_candidate_links` + `_ruth_live_parts` + `_format_ruth_live_body`; removed superseded `_ruth_live_body(html) -> str` and the exploratory alternate-signature prose.

Status left **Plan Discuss** for Joan re-validate.

#### joan — 2026-08-06T06:18:46.392Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1213
**Overall:** REVISE
**Publish ref:** `origin/sub/AST-1182/AST-1213-ai-payload-as-visible-text-and-links` @ `a7959c45`

## Traceability

AC1→S1; AC2→S1 (routing/ingest untouched); AC3→S1.4.

## Findings

### fix-now

**1. Reusing `_meteorite_email_candidate_links` strips click-tracking wrappers, so a job whose title Ruth can still read becomes unreachable.**

`_meteorite_email_candidate_links` applies `METEORITE_EMAIL_INGEST_CONFIG["link_exclude_substrings"]`, which includes `list-manage.com`. Mailchimp-style senders wrap **every** href in a `list-manage.com/track/click` redirect. Today Ruth reads raw HTML, so she sees that href and can return it as `job_link`; `_ingest_link` (`gaze_email.py:107–111`) Playwright-fetches it and records `final_url`, i.e. the redirect resolves to the real posting. Nothing in `gaze_email` filters Ruth's returned links against the hygiene list — I checked, the only consumer of that helper is `gazer.py:1219`.

After this plan, the wrapped href is removed from `--- LINKS ---` while the anchor **text** survives in the visible-text block. Ruth is shown a job title with no corresponding URL, and both the current and the proposed `user_prompt` forbid inventing links absent from CONTENT. So the posting is silently dropped.

Run against the helpers on this tip:

```
=== visible_text as Ruth would receive it ===
New jobs matching your alert
Senior Engineer at Acme
Staff Engineer at Globex      ← title present
Unsubscribe

=== links Ruth would receive ===
1. https://jobs.example.com/apply/123
                              ← Globex tracking URL dropped
```

This is the risk your own Self-Assessment names ("dropping real job URLs"), but no Decision block resolves it — and because `plan-is-bible` makes S1.2's implementation literal, it ships as written. It also cuts against the parent AC that both shapes "still produce the same class of outcomes (job links/metadata for ingest)."

Worth noting the config semantics too: `link_exclude_substrings` is documented in `config.py` as governing what "remain[s] a Playwright candidate." Reusing it as **AI-visibility** policy quietly widens that knob — an operator later narrowing it for scraping reasons would also blind Ruth, with nothing in config saying so.

Options, your call:

- **(a)** Give the Ruth payload its own exclusion set in `METEORITE_EMAIL_INGEST_CONFIG` (scheme + genuine noise: unsubscribe / preferences / w3.org / svg), keeping tracking wrappers visible since `_ingest_link` already resolves `final_url`. Keeps link hygiene in config, no forked filter in `gaze_email`.
- **(b)** Emit links paired with their anchor text so Ruth can correlate title→URL, and include wrapped hrefs.
- **(c)** Accept the drop, but then also keep those titles out of the visible text so Ruth is not shown phantom postings — and say in a Decision which sender classes are expected to stop producing creates.

Any of the three is fine by me; the plan just cannot stay silent on it. Please also keep "do not edit `gazer.py`" intact — (a) and (b) are both achievable in `gaze_email` + config.

### discuss

**2. Stage 2's gate is weaker than Stage 2's own "Done when."** Two gaps: (i) it never asserts the catalog and fixture prompt strings are **equal to each other**, which is the whole point of the surgical sync — AST-1212's script asserted exactly that equality one commit earlier, so this is a regression in rigor (they are byte-equal on this tip today, including `updated_at`, so the sync starts from a clean base; the gate just would not notice a divergent edit); (ii) it forbids `"HTML body"` in `cache_prompt` but the prompt also says "links absent from the **email HTML**", which your prose says to replace and the gate would pass with it still there. The `user_prompt` check (`"absent from the HTML"`) is correctly targeted — I confirmed both strings are present today, so those asserts are meaningful rather than trivially true.

**3. Superseded helper signature left in the doc.** S1.2 specifies `_ruth_live_body(html) -> str`, then S1.4 works through alternatives and lands on `_ruth_live_parts` + `_format_ruth_live_body(text, links)`, which is what the smoke test exercises. Two contradictory contracts for the same helper in a plan the builder follows literally — please delete the superseded block so S1.2 reads as the final shape.

### acceptable — verified against the tip

- **The AST-1212 dependency really is satisfied on this branch.** Tip contains the rename commits; `config.py` has `meteorite_email` at 531 / 550 / 554 / 2390 and the catalog row is `meteorite_email` / `meteorite_email`. So "no changes expected in `src/utils/config.py`" is correct, and S2's `assert old["task_key"] == new["task_key"] == "meteorite_email"` will hold.
- **Both live assemblies are quoted exactly right** — `gaze_email.py:234` and `:264` match the plan's "today" strings character for character, and `_handle_bound`'s `subject_url` / ignore branches are genuinely untouched by the described edit.
- **CSS and script text do not leak into the payload.** This was my main suspicion, since neither extractor decomposes `<style>` / `<script>` and job-alert email is almost always styled. I tested it: bs4 classifies those contents as `Stylesheet` / `Script` strings and `get_text()` skips them, so a `<style>` block with `@media` / `padding` / `!important` produced 98 chars of clean text and zero CSS tokens. No action needed — recording it so it is not re-litigated at review.
- **No allow-list narrowing today.** `link_allow_substrings` is `()` and documented as "empty = no filter," so the payload is not restricted to known ATS domains. Finding 1 is entirely about the exclude tuple.
- **Debug is properly gated.** `_detail` is `if debug: logger.debug_detail(...)` (`:93`), and `truncate_debug_content` is already imported (`:35`) and used on this path (`:350`, `:493`), so the S1.4 emission satisfies `debug-contract-gated` with found/recorded split and the 50-line contract. No new `logger.info("[DEBUG] …")`.
- **DRY reasoning on the text extractor holds.** The local `_body_text` and gazer's `_meteorite_email_body_text` differ only in separator (`" "` vs `"\n"`); keeping the local one for `_body_is_empty` and the subject_body `jd_suffix` while Ruth gets the newline form is a defensible split, not a second implementation.
- **Boundaries hold:** no rename, no `gazer.py` edit, no parse-mode / response-schema change, no ingest-archive rerouting, no inbox Playwright scrape, no `tests/` or bible edits. `docs/uat-fixtures/**` is outside the `engineer-test-tree-ban` path list, so the fixture sync is engineer work.

**Considered:** scored in-session.

## Verdict

**REVISE** — one fix-now (finding 1) plus two cleanups. The plan's structure, reuse reasoning, and debug design are sound; what is missing is a decision about which links Ruth is allowed to see. Round 2 of 2 available before the discuss cap.

— Joan

context_tokens≈148000

#### hedy — 2026-08-06T06:13:17.392Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1182/AST-1213-ai-payload-as-visible-text-and-links/docs/features/meteorite/ast-1213-ai-payload-as-visible-text-and-links.md

`origin/sub/AST-1182/AST-1213-ai-payload-as-visible-text-and-links` @ `a7959c45`

**Scope:** Single-Component — `gaze_email` Ruth live-content assembly + matching `meteorite_email` agent_task prompts/fixture; no rename, no ingest redesign.

**Conf:** high — two known string assemblies; payload mirrors roster PJL visible text + enumerated links; gazer already owns body-text and candidate-link extraction.

**Risk:** Medium — bad extraction could drop real job URLs or leave markup in live_content and degrade Ruth parse → create counts; archive/ingest control flow unchanged.

---

# AST-1213 — AI payload as visible text and links

**Linear:** [AST-1213](https://linear.app/astralcareermatch/issue/AST-1213/ai-payload-as-visible-text-and-links-rename-task-to-meteorite-email-ai)
**Parent:** [AST-1182](https://linear.app/astralcareermatch/issue/AST-1182/rename-task-to-meteorite-email-ai-payload-as-visible-textlinks) — Rename task to meteorite_email + AI payload as visible text/links
**Publish ref:** `origin/sub/AST-1182/AST-1213-ai-payload-as-visible-text-and-links`

After the AST-1212 rename, assemble the `meteorite_email` live payload as **visible text plus links** (same content shape as JD-scrape / `select_job_page` page sections — not raw HTML markup), and rewrite Ruth’s `agent_task` prompts so she expects that shape. Parse modes, response schema, task key, and post-parse ingest/archive behavior stay as they are today.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `METEORITE_EMAIL_INGEST_CONFIG["ruth_payload_link_exclude_substrings"]` — AI-visibility noise only (not Playwright’s full exclude list) | utils |
| `src/core/gaze_email.py` | Assemble Ruth `live_content` as visible text + enumerated links (gazer body-text helper + local link walk using the Ruth exclude key); Style D detail when `debug=True` | core |
| `data/admin/agent_task.json` | Rewrite `meteorite_email` `cache_prompt` / `user_prompt` so CONTENT is visible text + links, not raw HTML | data/admin |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Surgical sync of that same row’s prompt fields (+ `updated_at` if bumped) — **no** whole-file `cp` | docs |

**No changes expected:** `src/core/agent.py`, `src/core/gazer.py` (reuse `_meteorite_email_body_text` + `_meteorite_fetch_link_visible_text` only — **do not** edit gazer; **do not** call `_meteorite_email_candidate_links` for Ruth), dispatcher, Gmail external, frontend, evaluate_meteorite / UI grouping siblings, `tests/` / bible (Betty after Code Complete). Do **not** Playwright-scrape the inbox; extraction is from the message HTML already fetched via `get_message_html`.

## Stage 1: Config + `gaze_email` — Ruth live payload = visible text + links

**Done when:** `METEORITE_EMAIL_INGEST_CONFIG` exposes a Ruth-only exclude tuple that keeps click-tracking hosts (e.g. `list-manage.com`) visible to Ruth; for both `html_links` and `subject_body` branches in `_handle_bound`, `live_content` starts with the existing `PARSE_MODE:` (and `SUBJECT:` for subject_body) header lines, then visible text plus an optional `--- LINKS ---` enumerated URL list with **no raw HTML tags as the primary content**; a Mailchimp-style `list-manage.com/track/click` href appears in that list while unsubscribe / preferences / w3.org / svg noise does not; `subject_url` / ignore shapes are unchanged. `python3 -m py_compile` succeeds for touched modules (repo venv: `~/astral/.venv/bin/python`).

1. In `src/utils/config.py`, inside `METEORITE_EMAIL_INGEST_CONFIG` (after `link_exclude_substrings` / near the Playwright allow comment), add:

```python
    # AST-1213: href fragments excluded from Ruth's --- LINKS --- payload only.
    # Deliberately narrower than link_exclude_substrings — click-tracking wrappers
    # (e.g. list-manage.com) stay visible; _ingest_link Playwright resolves final_url.
    # Do not reuse this key for Playwright candidate filtering.
    "ruth_payload_link_exclude_substrings": (
        "unsubscribe",
        "mailto:",
        "/preferences",
        "/email-settings",
        "w3.org",
        "/2000/svg",
        "schemas.xmlsoap.org",
        "xmlns=",
    ),
```

Do **not** remove or alter `link_exclude_substrings` (Playwright ingest hygiene stays as today). Do **not** add `list-manage.com` to the Ruth tuple.

⚠️ **Decision — Ruth AI-visibility excludes ≠ Playwright candidate excludes (Joan round=1 option a):** Reusing `_meteorite_email_candidate_links` / `link_exclude_substrings` would strip Mailchimp-style click wrappers from `--- LINKS ---` while leaving the job title in visible text; Ruth’s “do not invent URLs absent from CONTENT” rule then silently drops those postings. Parent AC requires the same class of job-link outcomes. Tracking wrappers stay in Ruth’s list; `_ingest_link` already Playwright-fetches and records `final_url`. Genuine noise (unsubscribe / prefs / namespace/svg markers) stays excluded. Config comment must state the two keys have different consumers so operators do not “narrow Playwright” and accidentally blind Ruth.

2. In `src/core/gaze_email.py`, keep importing `_meteorite_fetch_link_visible_text` from gazer; **also** import `_meteorite_email_body_text`. Do **not** import or call `_meteorite_email_candidate_links`. Import `METEORITE_EMAIL_INGEST_CONFIG` (already imported) and `urlparse` (already imported).

3. Add these private helpers (place with the other module privates above `_ruth_parse`) — **this is the binding final shape** (no superseded `_ruth_live_body(html) -> str` contract):

```python
def _ruth_candidate_links(html: str) -> list[str]:
    """Ordered unique http(s) hrefs for Ruth --- LINKS --- (ruth_payload excludes)."""
    # B1 lazy import: bs4 only on Ruth payload assembly (same pattern as gazer).
    from bs4 import BeautifulSoup

    cfg = METEORITE_EMAIL_INGEST_CONFIG
    schemes = {s.casefold() for s in cfg["link_schemes"]}
    excludes = tuple(s.casefold() for s in cfg["ruth_payload_link_exclude_substrings"])
    allows = tuple(s.casefold() for s in cfg["link_allow_substrings"])
    soup = BeautifulSoup(html or "", "html.parser")
    seen: set[str] = set()
    out: list[str] = []
    for tag in soup.find_all("a", href=True):
        href = (tag.get("href") or "").strip()
        if not href or href in seen:
            continue
        parsed = urlparse(href)
        scheme = (parsed.scheme or "").casefold()
        if scheme not in schemes:
            continue
        low = href.casefold()
        if any(frag in low for frag in excludes):
            continue
        if allows and not any(frag in low for frag in allows):
            continue
        seen.add(href)
        out.append(href)
    return out


def _ruth_live_parts(html: str) -> tuple[str, list[str]]:
    """Return (visible_text, ruth_candidate_links) from email HTML."""
    return _meteorite_email_body_text(html), _ruth_candidate_links(html)


def _format_ruth_live_body(text: str, links: list[str]) -> str:
    """Visible text + optional --- LINKS --- enumeration (JD-scrape payload shape)."""
    parts = [text] if (text or "").strip() else ["(no visible text)"]
    if links:
        parts.append("--- LINKS ---")
        for i, lnk in enumerate(links, 1):
            parts.append(f"{i}. {lnk}")
    return "\n".join(parts)
```

⚠️ **Decision — local `_ruth_candidate_links`, not a gazer edit:** Joan required “do not edit `gazer.py`.” Playwright continue to use `_meteorite_email_candidate_links` + `link_exclude_substrings`. Ruth’s walk is the same algorithm with a different exclude key — intentional dual policy, documented in config.

⚠️ **Decision — section marker `--- LINKS ---` (not `--- NEW LINKS ---`):** Email has no “nav vs new” split; one link list is enough. Keep the triple-dash header style so the shape stays recognizable next to roster PJL live content.

⚠️ **Decision — keep local `_body_text` for emptiness + create-path JD suffix:** `_body_is_empty` and the subject_body `jd_suffix` / no-link create path continue to use existing `_body_text(html)`. This ticket only changes what Ruth sees in `live_content`, not the text appended to scraped JDs or the empty-body gate.

4. In `_handle_bound`, replace the two raw-HTML live assemblies:

- **html_links** (today: `live = f"PARSE_MODE: {html_mode}\n\n{html}"`):

```python
text, links = _ruth_live_parts(html)
body = _format_ruth_live_body(text, links)
live = f"PARSE_MODE: {html_mode}\n\n{body}"
_detail(debug, f"ruth_payload visible_chars={len(text)} links={len(links)}")
for line in truncate_debug_content(live):
    _detail(debug, line)
parsed = await _ruth_parse(...)
```

- **subject_body** (today: `live = f"PARSE_MODE: {subject_mode}\nSUBJECT: {subject}\n\n{html}"`):

```python
text, links = _ruth_live_parts(html)
body = _format_ruth_live_body(text, links)
live = f"PARSE_MODE: {subject_mode}\nSUBJECT: {subject}\n\n{body}"
_detail(debug, f"ruth_payload visible_chars={len(text)} links={len(links)}")
for line in truncate_debug_content(live):
    _detail(debug, line)
parsed = await _ruth_parse(...)
```

Do **not** change shape routing, `_ruth_parse` args other than `live`, ingest loop, archive finalize, or `subject_url`.

⚠️ **Decision — emit truncated live payload under Style D detail:** Parent AC requires found/recorded visibility when this hop’s `debug=True` paths are touched. Summary line = found; `truncate_debug_content(live)` lines = recorded payload (50-line contract). Do **not** add new `logger.info("[DEBUG] …")` lines. `_detail` already no-ops when `debug=False`.

5. Update the module docstring one line to note AST-1213: Ruth live payload is visible text + links (not raw HTML); link list uses `ruth_payload_link_exclude_substrings`.

**Done when (recheck):**

```bash
~/astral/.venv/bin/python - <<'PY'
from src.core import gaze_email as ge
from src.utils.config import METEORITE_EMAIL_INGEST_CONFIG as cfg

assert "list-manage.com" in cfg["link_exclude_substrings"]
assert "list-manage.com" not in cfg["ruth_payload_link_exclude_substrings"]
assert "unsubscribe" in cfg["ruth_payload_link_exclude_substrings"]

html = (
    '<p>New jobs</p>'
    '<a href="https://jobs.example.com/apply/123">Senior Engineer at Acme</a>'
    '<a href="https://example.list-manage.com/track/click?u=1">Staff Engineer at Globex</a>'
    '<a href="https://example.com/unsubscribe">Unsubscribe</a>'
    '<a href="mailto:x@y.z">x</a>'
)
text, links = ge._ruth_live_parts(html)
assert "Staff Engineer at Globex" in text
assert "https://jobs.example.com/apply/123" in links
assert any("list-manage.com" in u for u in links), links  # tracking wrapper kept for Ruth
assert not any("unsubscribe" in u.casefold() for u in links)
body = ge._format_ruth_live_body(text, links)
assert "--- LINKS ---" in body
assert "<a" not in body and "<p>" not in body
assert ge._format_ruth_live_body("", []).startswith("(no visible text)")
print("ok")
PY
~/astral/.venv/bin/python -m py_compile src/utils/config.py src/core/gaze_email.py
```

**Ritual:** `code(AST-1213): Ruth live payload visible text + links`

## Stage 2: Ruth prompts expect visible text + links

**Done when:** Current `meteorite_email` row in `data/admin/agent_task.json` describes CONTENT as visible text plus a `--- LINKS ---` list (not HTML / email HTML as the payload); `user_prompt` no longer says “absent from the HTML”; catalog and fixture `cache_prompt` / `user_prompt` (/`updated_at`) are **byte-equal to each other**; catalog vs fixture drift outside this row is untouched.

1. Snapshot before edit (local `/tmp` only — do not commit):

```bash
cp data/admin/agent_task.json /tmp/agent_task.pre-ast-1213.json
cp docs/uat-fixtures/AST-756/expected-agent_task.json /tmp/expected-agent_task.pre-ast-1213.json
```

2. In `data/admin/agent_task.json`, locate the single `current == 1` object with `task_key == "meteorite_email"`. Rewrite **`cache_prompt`** and **`user_prompt`** only (optionally bump `updated_at` to current UTC `YYYY-MM-DD HH:MM:SS`). Do **not** change `task_key`, `task_name`, `task_key_uuid`, grouping, `task_seq`, `agent_id`, empty prompt slots, or any other row.

**`cache_prompt` binding content** (keep `## INSTRUCTIONS` header style; exact wording may be tightened for clarity but must include every bullet below):

- Still: mechanical meteorite email parse; `PARSE_MODE: html_links` | `subject_body` on the first CONTENT line; echo into response `parse_mode`.
- **Replace** every phrase that treats the body as markup: “HTML body”, “email HTML”, “HTML/body”, “absent from the email HTML”, “links absent from the HTML”.
- State that after the header line(s), CONTENT is **visible text** extracted from the message, optionally followed by a `--- LINKS ---` section of numbered `http(s)` URLs (same shape as JD-scrape visible text + links — not markup). Click-tracking redirect URLs in LINKS are valid job sources (downstream resolves the final URL).
- **html_links:** Use visible text + `--- LINKS ---` to extract every distinct meteorite **job** link worth scraping; skip obvious non-job noise when clearly not a posting; return `{job_link, job_title?, metadata?}` in `jobs` with optional `metadata` object `company` / `location`; prefer empty `jd_link` / `content_text`.
- **subject_body:** CONTENT includes `SUBJECT:` then visible text (+ optional links). Return `content_text` = usable subject + body text; set `jd_link` when one likely JD URL is present; prefer `jobs: []`.
- Always valid JSON only; do **not** invent links absent from CONTENT (visible text or LINKS list); do **not** copy qualify_meteorite’s astral_job_id contract.

**`user_prompt` binding** (one string): ask Ruth to parse CONTENT per `PARSE_MODE` and return JSON with `parse_mode`, `jobs`, optional `jd_link` / `content_text`; do not scrape or invent URLs absent from the CONTENT; do not emit grade vectors. Must **not** say “absent from the HTML” or “email HTML”.

3. **Surgical fixture sync (no whole-file `cp`):** in `docs/uat-fixtures/AST-756/expected-agent_task.json`, find the `current == 1` / `task_key == "meteorite_email"` object and set `cache_prompt`, `user_prompt`, and `updated_at` to the **exact same strings** as the catalog row. Do **not** add missing fixture rows or rewrite other tasks.

⚠️ **Decision — prompts ship with payload, not as a drive-by later:** Parent AC requires Ruth to expect the new shape; leaving HTML-oriented prompts would fight Stage 1.

4. Verify only the target row’s prompt fields (and optional `updated_at`) moved, catalog↔fixture prompts match, and HTML-as-payload wording is gone:

```bash
~/astral/.venv/bin/python - <<'PY'
import json
from pathlib import Path

def load(p):
    return json.loads(Path(p).read_text())

def by_uuid(rows):
    return {r["task_key_uuid"]: r for r in rows}

def by_key(rows, key="meteorite_email"):
    for r in rows:
        if r.get("task_key") == key and r.get("current") == 1:
            return r
    raise AssertionError(key)

for label, pre, post in (
    ("catalog", "/tmp/agent_task.pre-ast-1213.json", "data/admin/agent_task.json"),
    ("fixture", "/tmp/expected-agent_task.pre-ast-1213.json", "docs/uat-fixtures/AST-756/expected-agent_task.json"),
):
    a, b = by_uuid(load(pre)), by_uuid(load(post))
    assert set(a) == set(b), label
    changed = [u for u in a if a[u] != b[u]]
    assert len(changed) == 1, (label, changed)
    old, new = a[changed[0]], b[changed[0]]
    assert old["task_key"] == new["task_key"] == "meteorite_email"
    cp, up = new.get("cache_prompt") or "", new.get("user_prompt") or ""
    for banned in ("HTML body", "email HTML", "absent from the HTML", "absent from the email HTML"):
        assert banned not in cp, (label, banned, "cache_prompt")
        assert banned not in up, (label, banned, "user_prompt")
    assert "--- LINKS ---" in cp or "visible text" in cp.lower()
    for k in ("task_key_uuid", "agent_id", "task_group_order", "task_group_name", "task_seq", "task_name"):
        assert old[k] == new[k], (label, k)

# Surgical sync: catalog and fixture prompts must be byte-equal
cat = by_key(load("data/admin/agent_task.json"))
fix = by_key(load("docs/uat-fixtures/AST-756/expected-agent_task.json"))
assert cat["cache_prompt"] == fix["cache_prompt"]
assert cat["user_prompt"] == fix["user_prompt"]
assert cat.get("updated_at") == fix.get("updated_at")
print("ok")
PY
```

**Ritual:** `code(AST-1213): meteorite_email prompts visible text + links`

## Self-Assessment

**Scope:** `Single-Component` — Ruth live-content assembly in `gaze_email` + one ingest-config exclude key + matching `meteorite_email` agent_task prompt/fixture row; no rename, no ingest/archive redesign, no sibling UI/evaluate work.

**Conf:** `high` — call sites are two known string assemblies; payload shape copies roster PJL enumeration; Joan round=1 locked the link-visibility decision (option a); helpers and gates are now single-contract.

**Risk:** `Medium` — wrong extraction still degrades Ruth parse → create counts, but the known Mailchimp click-wrapper blind spot is closed by keeping tracking hosts in Ruth’s list while Playwright hygiene stays separate; archive/ingest control flow itself is unchanged.

## Code-rules check

- **§1.3 DRY:** Reuse `_meteorite_email_body_text`; Ruth link walk shares algorithm shape with gazer but must **not** share `link_exclude_substrings` (different consumer — Decision above).
- **§2.1 config:** New Ruth exclude tuple lives in `METEORITE_EMAIL_INGEST_CONFIG`; Playwright key unchanged; parse modes stay in `METEORITE_EMAIL_PARSE_CONFIG`.
- **§2.2 / `astral.agent.do-task-delegation`:** Still `do_task` with config `task_key`; only `live_content` body changes.
- **§1.5.1 debug:** Style D detail + `truncate_debug_content` only when `debug=True`.
- **§3.3 imports:** core → core/utils; no gazer edit; no utils→data or layer violations.
- **§1.1 in-scope:** No rename, no evaluate_meteorite, no UI grouping, no Playwright inbox scrape.
- **Engineer test-tree ban:** No `tests/` / bible edits.

## Revisions

Revision 1 — 2026-08-06
Driven by: Joan `[plan-discuss] round=1 concern` (plan-rubric.v1 REVISE @ `a7959c45`)
Changes:
- **fix-now #1:** Stop reusing `_meteorite_email_candidate_links` / `link_exclude_substrings` for Ruth. Add `ruth_payload_link_exclude_substrings` (option a) so click-tracking wrappers stay in `--- LINKS ---`; implement `_ruth_candidate_links` in `gaze_email`; keep gazer untouched.
- **discuss #2:** Strengthen Stage 2 gate — catalog↔fixture prompt byte-equality; ban leftover “email HTML” / “absent from the email HTML” phrases in both prompts.
- **discuss #3:** Collapse S1 helper contract to final `_ruth_live_parts` + `_format_ruth_live_body` (+ `_ruth_candidate_links`); remove superseded `_ruth_live_body(html) -> str` / exploratory alternate signatures.
- Files Changed / Self-Assessment / code-rules updated for the config + local link-walk delta.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1182/AST-1213-ai-payload-as-visible-text-and-links`
**Plan path:** `docs/features/meteorite/ast-1213-ai-payload-as-visible-text-and-links.md`

**Built tip:** `ecf25eda9e6eb3f936a1dbb8ee47c464b21ac8b4` (`ecf25eda`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `aef00995` | Ruth live payload visible text + links |
| 2 | `38a2cecd` | meteorite_email prompts visible text + links (+ surgical AST-756 fixture) |

## Radia review — [code-rubric] revision=1

**Rubric:** code-rubric.v1 · **Publish ref tip:** `871c4b9b`

**Overall: CLEAN**

**What's solid:**

- `gaze_email.py`: `_ruth_candidate_links` / `_ruth_live_parts` / `_format_ruth_live_body` match the plan verbatim; `gazer.py` untouched (Joan round=1 "do not edit gazer" honored); `do_task` call path unchanged — only `live_content` body differs.
- New `ruth_payload_link_exclude_substrings` is a deliberately narrower, well-commented sibling of `link_exclude_substrings` (not a careless duplicate) — closes the Joan round=1 fix-now (Mailchimp-style click wrappers stay visible to Ruth; Playwright hygiene list untouched). Verified: `list-manage.com` present in the Playwright key, absent from the Ruth key.
- Debug contract (§1.5.1) done right: `_detail`/`debug_detail` gated by `debug_flag`, found+recorded both logged (`visible_chars=/links=` summary, then `truncate_debug_content(live)` body), no naked `logger.info` added.
- `astral.standards.in-scope-only` clean this time — diff footprint matches the plan's Files Changed table exactly (`config.py`, `gaze_email.py`, the one `agent_task.json` row + fixture twin, one new `docs/features` file); no repeat of AST-1212's whole-file re-encoding issue on the seed JSON (verified: `data/admin/agent_task.json` diff is 10 lines, catalog↔fixture prompts byte-equal, `updated_at` bumped consistently in both).
- No live \"HTML\"/\"email HTML\" wording survives in either prompt; catalog and fixture are byte-equal on the touched row.
- Exactly one `merge-tests(AST-1213)` commit; engineer commits (`aef00995`, `38a2cecd`) never touch `tests/`/`docs/test-bible/**`; `src/core/gazer.py` confirmed untouched.
- `python3 -m py_compile` clean on both touched modules at tip.

**Advisory (not fix-now):** The `html_links` and `subject_body` branches in `_handle_bound` each repeat the same 5-line assemble-and-log block (`_ruth_live_parts` → `_format_ruth_live_body` → `_detail` summary → `truncate_debug_content` loop) verbatim. A small `_assemble_ruth_live(prefix, html, debug)` helper would collapse the duplication (§1.3 DRY), but it's cosmetic — behavior is identical and the plan's binding code blocks specified this shape explicitly.

**Pattern conformance:** `pattern.layers.import-discipline` — conforms (core→core reuse of `gazer._meteorite_email_body_text`, no new cross-layer import; `bs4` lazy-imported per existing repo convention).

**Plan adherence:** Both stages match the plan's binding code blocks and done-when checks exactly, including the Joan round=1 revision (dual exclude-key decision) and the Stage 2 byte-equality / banned-phrase gates.

## Frame diff

(none — ticket description/AC unchanged; no findings to fold in)

context_tokens≈55000

— Radia

## Resolution

**2026-08-06** — Radia **CLEAN** (zero fix-now, zero discuss).

- No product or prompt changes this pass.
- Advisory DRY helper on the duplicated assemble-and-log block left as-is — plan binding blocks specified that shape; cosmetic only.
- Intake: Radia `docs(AST-1213): Radia review — clean` @ `3b2f9dff` already on the checked-out sub via `sync-child`.
