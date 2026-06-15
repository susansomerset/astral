# AST-573 — Pronoun selection

<!-- linear-archive: AST-573 archived 2026-06-15 -->

## Linear archive (AST-573)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-573/pronoun-selection  
**Status at archive:** Done  
**Project:** Astral Candidate  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-539

### Description

## Purpose

Generated cover letters, consult narratives, and other agent prompts refer to the candidate in third person. Today those prompts can use name tokens (`{$FIRST_NAME}`) but not pronouns, so authors either guess or write awkward neutral copy. This feature lets each candidate choose a pronoun preference on their profile and exposes resolved pronoun forms as simple prompt tokens so Susan-authored prompt templates can read naturally for every candidate without per-person prompt forks.

## Functional scope

* **Profile preference.** The candidate profile includes a **pronoun preference** control with exactly these options, in this order: **they/them**, **she/her**, **he/him**, **ze/zir**, **e/eir**. The selected value is stored on the candidate record and round-trips through save/load like other profile contact fields.
* **Admin parity.** Admin Manage Candidates create/edit flows expose the same pronoun preference control so admins can set or change it for any candidate.
* **Default and backfill.** When pronoun preference is **unset**, tokens resolve as **they/them**. Existing candidates without a stored preference are **backfilled** to **they/them** so prompts never see an ambiguous empty pronoun set.
* **Prompt tokens.** Prompt authors use five flat tokens — no grammar jargon in token names:
  * `{$THEY}` — subject
  * `{$THEIR}` — possessive before a noun (e.g. **Their** experience)
  * `{$THEIRS}` — standalone possessive (e.g. the house is **theirs**)
  * `{$THEM}` — object
  * `{$THEMSELF}` — reflexive
    At resolution time each expands per the candidate's stored preference (or **they/them** default):
  * **they/them** → they / their / theirs / them / themselves
  * **she/her** → she / her / hers / her / herself
  * **he/him** → he / his / his / him / himself
  * **ze/zir** → ze / zir / zirs / zir / zirself
  * **e/eir** → e / eir / eirs / em / emself
* **Token discoverability.** All five pronoun tokens appear in the same token registry / Manage Tasks autocomplete surface as existing candidate tokens.
* **Example usage.** `This is {$FIRST_NAME}'s resume. {$THEIR} experience suggests {$THEY} might like a career in axe juggling.`

## Boundaries

* **Fixed list only.** No free-text custom pronouns, no prefer-not-to-say option, and no admin-editable catalog beyond the five Susan specified.
* **Five tokens in v1.** `{$THEY}`, `{$THEIR}`, `{$THEIRS}`, `{$THEM}`, `{$THEMSELF}` only — no legacy `{$SUBJECT_PRONOUN}` names.
* **Prompt resolution only.** Tokens apply where `{$TOKEN}` substitution runs for agent prompts. Does not automatically rewrite artifact HTML or stored cover letter bodies.
* **No intake interview step.** Candidate Intake (AST-539) does not collect pronouns in v1; preference is set on Profile or Admin only.
* **No prompt backfill mandate.** Shipping tokens does not require updating every existing prompt.
* **Must not break** existing candidate token resolution, Profile save paths, Admin candidate CRUD, or unrelated `resolve_tokens` behavior.

## Acceptance criteria

1. Candidate Profile shows a pronoun preference control with the five options in the specified order; saving persists and reload shows the same selection.
2. Admin Manage Candidates can view, set, change, and clear pronoun preference through existing admin save paths.
3. Candidates with no explicit preference (including pre-existing records after backfill) resolve all five tokens as **they** / **their** / **theirs** / **them** / **themselves**.
4. With preference **she/her**, a test prompt containing all five tokens resolves to **she**, **her**, **hers**, **her**, **herself** in Manage Tasks preview and in a production `do_task` call.
5. Each of the five preferences resolves to the correct five-form mapping above.
6. All five pronoun tokens appear in the token list available to prompt authors.
7. Prompts that use only name tokens behave unchanged regardless of pronoun setting.

## Dependencies and blockers

* Existing candidate profile storage, `TOKEN_SOURCES` / `resolve_tokens`, Profile UI, Admin candidate API (AST-216 and successors).
* None blocking dispatch.

## Decisions

* **Unset default:** resolve as **they/them**; backfill existing candidates to **they/them** (Susan 2026-06-03).
* **Token names:** `{$THEY}`, `{$THEIR}`, `{$THEIRS}`, `{$THEM}`, `{$THEMSELF}` — flat names, no grammar labels (Susan 2026-06-03).

## Open questions

none.

---

## Original brief

I want the candidate profile to select from a list of pronoun preferences, and for us to create tokenized pronoun uses for the prompt content.  E.g. "This is {$FIRST_NAME}'s resume. {$POSSESSIVE_PRONOUN} experience suggests {$SUBJECT_PRONOUN} might like a career in axe juggling."

Pronoun options, in this order:
they/them
she/her
he/him
ze/zir
e/eir

### Comments

#### susan — 2026-06-05T04:20:34.056Z
@chuckles you need to call them with these instructions headlessly because they don't check linear directly.  Let me know when that is done.

#### chuckles — 2026-06-05T04:19:09.125Z
origin/dev @ `7ce8f063` — finish-up landed AST-573.

Team sync (mandatory before next pipeline work):
  git fetch origin && git checkout dev-<agent> && git merge origin/dev
  git push origin dev-<agent>:refs/heads/dev-<agent>

Joan sync-agents merged+pushed ada, hedy, kath. **dev-betty** push rejected (non-fast-forward) — @Betty White run fetch/merge/push on `dev-betty` before next qa work.

@Ada Lovelace @Hedy Lamarr @Katherine Johnson @Betty White @Radia Perlman
— Chuckles

#### chuckles — 2026-06-04T01:19:32.760Z
## Manual test steps

**Prerequisites:** App running on local `dev` (merged). Restart if already up.

### Profile (AST-576)
1. Open **Candidate Profile** → Contact section → confirm **Pronoun preference** select with options in order: *(not set)*, they/them, she/her, he/him, ze/zir, e/eir.
2. Set **she/her**, save, reload — selection persists.
3. Clear to *(not set)*, save, reload — empty/unset displays correctly.

### Admin (AST-576)
4. **Admin → Manage Candidates** → add candidate with **ze/zir**; edit to **he/him**; clear pronoun on edit — each save round-trips.

### Tokens (AST-575)
5. **Manage Tasks** token autocomplete — confirm `{$THEY}`, `{$THEIR}`, `{$THEIRS}`, `{$THEM}`, `{$THEMSELF}` appear.
6. With candidate **she/her**, preview prompt: `{$THEY} … {$THEIR} … {$THEIRS} … {$THEM} … {$THEMSELF}` → she / her / hers / her / herself.
7. Repeat spot-check one other preference (e.g. **e/eir** → e / eir / eirs / em / emself).
8. Candidate with unset preference (or after backfill): all five tokens resolve as they / their / theirs / them / themselves.
9. Prompt using only `{$FIRST_NAME}` — unchanged regardless of pronoun setting.

`origin/ftr/ast-573-pronoun-selection` @ `6c47d3c2` · local `dev` @ `ed4f5a00` (land-ftr). Stashed unrelated local WIP as `chuckles prep-uat AST-573 retry` — `git stash list` to restore.

— Chuckles

#### susan — 2026-06-04T01:10:40.040Z
@chuckles Try again, please?

#### chuckles — 2026-06-03T23:22:29.381Z
@susan — prep-uat blocked: local `dev` has an in-progress merge with conflicts (`docs/ASTRAL_TEST_BIBLE.md`, `ast-554`, `ast-555`); `land-ftr AST-573` cannot run. `origin/ftr/ast-573-pronoun-selection` @ `6c47d3c2` is ready; child `sub/*` deleted. Resolve or abort merge on `dev`, then re-run prep-uat.

— Chuckles

#### chuckles — 2026-06-03T22:59:11.903Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-573 (parent) | ftr/ast-573-pronoun-selection |
| AST-575 | sub/AST-573/AST-575-pronoun-profile-data-and-prompt-tokens |
| AST-576 | sub/AST-573/AST-576-pronoun-preference-profile-and-admin-ui |

## Epic sessions (headless — Chuckles injects in every spawn; agents do not read Linear)

| Agent | Session id | Ticket | Role |
|-------|------------|--------|------|
| Joan | `f24b1c61-f3c6-4ad7-95fa-d85c35f18d3c` | AST-573 (parent) | git |
| Ada | `235d9ec6-fd42-47cc-b663-3de6e6be5c26` | AST-575 | engineer |
| Betty | `6b84f3fb-d82c-4dd0-8618-92e7786eb923` | AST-575 | qa |
| Radia | `3590af43-f9ed-4dfe-8f5b-de648423ac55` | AST-575 | review |
| Katherine | `7d72a6c1-1c2f-4c37-bd14-03bd1e785789` | AST-576 | engineer |
| Betty | `120aac8e-cf53-46d4-a6fb-1f73c94c774b` | AST-576 | qa |
| Radia | `4fa6875f-12b5-488a-a11a-6f1fd391493e` | AST-576 | review |

**Parent:** AST-573

— Chuckles

#### susan — 2026-06-03T22:44:23.196Z
Update the plan for the tokens to be {$THEY}, {$THEIR}, {$THEIRS}, {$THEM}, {$THEMSELF}. We don't need an english degree to write prompts.  ;-)

#### susan — 2026-06-03T22:05:22.146Z
@chuckles Default and backfill with they/them.  You can do web search if you need guidance on the more nuanced use of pronouns, like "Her dog" vs "the dog is hers".

#### chuckles — 2026-06-03T22:03:05.845Z
@susan Open questions on **AST-573**:

1. When pronoun preference is **unset**, should **`{$SUBJECT_PRONOUN}`** and **`{$POSSESSIVE_PRONOUN}`** resolve to empty strings (today’s default for missing candidate tokens), or default to **they/them** forms (**they** / **their**)?

---

_Implementation detail may live in git history on `origin/dev`._
