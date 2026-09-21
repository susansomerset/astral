# AST-1045 — Verify unique contact info

<!-- linear-archive: AST-1045 archived 2026-08-11 -->

## Linear archive (AST-1045)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1045/verify-unique-contact-info  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1065; related: AST-1046

### Description

## Purpose

Contact identity is now the durable home for emails and related handles ([AST-1014](https://linear.app/astralcareermatch/issue/AST-1014/contact-context-artifacts-library-name-columns-candidate-profile)). Binding and lookup already treat an email as belonging to **at most one** candidate when the hit is unambiguous ([AST-1047](https://linear.app/astralcareermatch/issue/AST-1047/reusable-get-candidate-string-lookup-from-bind-email-to-candidate)), but nothing stops a save from writing the same contact value onto two candidates — or leaving duplicate values inside one candidate’s contact blob. This epic closes that gap at the **candidate contact save** boundary so uniqueness is enforced before bad data sticks, and so downstream bind/lookup stays trustworthy.

## Functional scope

* **Within-candidate contact cleanup on save.** When contact data is saved for one candidate, duplicate contact values inside that candidate’s contact set are removed or refused per the product rule locked in Open questions (list duplicates and/or the same value stored in more than one contact field).
* **Cross-candidate uniqueness on save.** Saving contact data that would give a second candidate a contact value already owned by another candidate fails (or follows the soft rule locked in Open questions). The save does not silently overwrite the other candidate.
* **Config names the unique set.** Which contact fields participate in within-candidate dedupe and cross-candidate uniqueness lives in product config — not hardcoded field lists in core. Prefer aligning with the existing candidate email/name lookup vocabulary where emails are in scope.
* **Clear failure to callers.** When a save is refused for uniqueness, callers get a clear domain error they can surface (Profile / Admin / intake). This epic does **not** redesign the Profile contact UI ([AST-1065](https://linear.app/astralcareermatch/issue/AST-1065/update-candidate-ui-for-contact-info)).
* **Debug traceability (backend).** On touched `debug=True` save/validation paths: per-step found/recorded lines (universal `index N/M`, primary identifier, outcome; working detail under `|`; long payloads truncated per Code Rules / AST-538). No React debug-logging requirement.

## Architectural definition

* **Patterns to reuse**
  * `pattern.config.config-block` — uniqueness / dedupe field participation and normalization rules belong in config (extend or sibling to `CANDIDATE_LOOKUP_CONFIG`), not inline sets in core.
  * `pattern.layers.import-discipline` — validation stays in core; data layer raises / persists only; UI stays thin.
* **New patterns proposed**
  * Candidate **contact uniqueness gate on save** (within-blob dedupe + cross-candidate collision check) — introduced by child #2; other entity uniqueness gates do not automatically inherit it without Archie approval.
* **Applicable statutes**
  * `astral.config.config-source-of-truth` — which fields are unique / how compare (e.g. casefold) lives in config.
  * `astral.standards.no-hardcoded-sets` — no inline unique-field sets in core.
  * `astral.standards.data-raises-caller-logs` — data raises; core decides; callers log/surface.
  * `astral.standards.debug-contract-gated` — backend `debug=True` found/recorded contract on touched paths.
  * `astral.standards.in-scope-only` / `astral.standards.dry-and-focused-functions` — uniqueness only; no drive-by Profile rewrite.
  * `astral.layers.import-direction` / `astral.layers.core-vs-external-bright-line` — gate in core on the existing contact save path.
  * `astral.docs.features-single-file-per-ticket` — one plan doc per child at plan time.

## Boundaries

* Does **not** re-implement the contact/context/artifacts library or name columns — [AST-1014](https://linear.app/astralcareermatch/issue/AST-1014/contact-context-artifacts-library-name-columns-candidate-profile).
* Does **not** own Profile/Admin contact manage UI or websites UX — [AST-1065](https://linear.app/astralcareermatch/issue/AST-1065/update-candidate-ui-for-contact-info).
* Does **not** rework `get_candidate_id_for_query` match semantics beyond staying compatible with the uniqueness rule (lookup already returns none on ambiguous hits).
* Does **not** own Slack Contact / Estelle envelope uniqueness — [AST-1043](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent) / [AST-1046](https://linear.app/astralcareermatch/issue/AST-1046/contact-estelle-conversational-envelope).
* Does **not** change the candidate state machine.
* Does **not** invent a second contact blob or restore `profile.*` shadow writes.
* Does **not** silently merge two candidate records when a collision is detected.

## Acceptance criteria

1. Saving contact data for a candidate that would duplicate a uniqueness-scoped contact value already held by a **different** candidate is refused (or soft-handled exactly as Open question #3 locks); the other candidate’s data is unchanged.
2. Saving contact data that contains within-candidate duplicates among uniqueness-scoped values results in a single retained value or a refused save — matching Open question #2 — with no residual duplicate list entries / dual-field copies for those scoped fields.
3. Which fields participate and how they compare (e.g. case-insensitive emails) are driven by config; changing the set does not require hunting hardcoded lists in core.
4. A refused uniqueness save surfaces a clear error to the save caller suitable for UI/API display; success path still persists normalized contact as today.
5. Touched backend `debug=True` uniqueness/save paths emit per-step found/recorded Style D lines (index header + `|` detail; long content truncated).
6. Existing unambiguous email bind/lookup behavior remains usable: after enforcement, two live candidates cannot both hold the same uniqueness-scoped email (going forward, subject to Open question #4 on legacy rows).

## Dependencies and blockers

* Soft blocked by / lands against: [AST-1014](https://linear.app/astralcareermatch/issue/AST-1014/contact-context-artifacts-library-name-columns-candidate-profile) (User Testing) — contact blob + save path that refuses `profile` shadow writes.
* Soft related: [AST-1047](https://linear.app/astralcareermatch/issue/AST-1047/reusable-get-candidate-string-lookup-from-bind-email-to-candidate) (Done) — lookup email paths / casefold; uniqueness should not fight that vocabulary.
* Soft related: [AST-1065](https://linear.app/astralcareermatch/issue/AST-1065/update-candidate-ui-for-contact-info) (Todo, Interface) — may surface uniqueness errors; this epic does not own that UI.
* none hard-blocking start once Open questions are answered.

## Open questions

1. Which contact fields must be **unique across candidates**? Emails only (`contact_email` / `reply_email`), or also phone, LinkedIn, GitHub, and/or websites?
   1. All contact info
2. Within **one** candidate, what does “dedupe” mean: (a) collapse duplicate entries in list fields such as websites, (b) forbid the same value in two scalar fields (e.g. contact email identical to reply email), or **both**?
   1. Avoid adding the same contact info twice for the same candidate
3. On a cross-candidate collision, should save **hard-fail** (recommended default), or soft-allow with a warning only?
   1. Hard fail with a toast
4. For **existing** duplicate rows already in the database: clean up / migrate in this epic, or enforce uniqueness only on new/changed writes going forward?
   1. There won't be duplicates
5. Confirm uniqueness-scoped emails should stay aligned with `CANDIDATE_LOOKUP_CONFIG` email paths (including transitional `profile.*` until gone), so bind/lookup and save enforcement share one vocabulary?
   1. Yes that's smart!

## Proposed child tickets

#### 1!: **Unique-contact field contract in config - Ada**

Define config for which contact values participate in within-candidate dedupe and cross-candidate uniqueness, plus compare rules (e.g. casefold for emails). Prefer extending or siblinging the existing candidate lookup config rather than a parallel hardcoded list. Does **not** own save-path enforcement (#2). Does **not** own Profile UI (AST-1065).
**Citations:** `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`.

#### 2: **Enforce uniqueness on candidate contact save - Ada**

On the candidate contact save path: apply within-candidate dedupe and cross-candidate uniqueness per #1; refuse or soft-handle collisions per Open questions; emit Style D debug on touched `debug=True` paths; raise a clear domain error for callers. After #1. Does **not** own config vocabulary (#1), library schema (AST-1014), or Profile/Admin contact UI (AST-1065).
**Citations:** new contact uniqueness gate on save (proposed); `astral.standards.data-raises-caller-logs`; `astral.standards.debug-contract-gated`; `astral.layers.import-direction`; `astral.layers.core-vs-external-bright-line`.

**Monolith check:** Functional scope has 5 capabilities; 2 proposed children (config contract → save enforcement). Intentional: UI surfacing stays on AST-1065; no third child unless Open question #4 adds a legacy cleanup slice.

**New patterns:** contact uniqueness gate on save — child #2.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-1045 (parent) | ftr/AST-1045-verify-unique-contact-info |
| AST-1079 | sub/AST-1045/AST-1079-unique-contact-field-contract |
| AST-1080 | sub/AST-1045/AST-1080-enforce-uniqueness-on-candidate-contact-save |

* **AST-1095**: `sub/AST-1045/AST-1095-uat-email-unique-root-and-extra`

**Epic worktree:** `astral-AST-1045/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. Each entry is agent · role, then the fully-qualified `store.db` path (UUID is the directory name — extract for `agent --resume`). **datt resume:** read this list — not chat memory.

* **Ada** · engineer
  `/home/susan/.cursor/chats/e6a6ae7abe06cb3817928b42cbb73f1f/f88ed418-ae8c-4e5c-91b9-8ae31524568b/store.db`
* **Betty** · qa
  `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/76c6db7e-d67f-401a-a1a0-6f5096f9b9b9/store.db`
* **Radia** · review
  `/home/susan/.cursor/chats/e6a6ae7abe06cb3817928b42cbb73f1f/9606c6e6-a564-4cf6-97a3-60233e05e70d/store.db`

---

## Original brief

Let's do a data validation on [candidate.py](<http://candidate.py>) for save_contact_data to dedupe emails/contact info and contact info for one candidate and ensure no duplicates across candidates.

### Comments

#### cursorapp — 2026-07-31T04:33:13.575Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-1095** | new email must be unique vs all root and extra emails |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-1095** — _new email must be unique vs all root and extra emails_
- **Issue reported:** When a new email is added for a candidate, uniqueness is not reliably enforced against the whole candidate table for both root email addresses (`contact.contact_email` / `contact.reply_email`) and extra emails (`contact.extra_emails`). AST-1065 UI scope clarified that adding an e
- **Should now:** Adding any email (root field or an extra-email entry) hard-fails when that address (casefold) is already held by another candidate as a root email or as an extra email. The other candidate is unchanged. Caller gets a clear domain error suitable for toast/UI.
- **Quick check (this fix only):**
  1. Candidate A has root email `a@example.com` (and/or that address in `extra_emails`).
  2. On Candidate B, add `a@example.com` as a new root email or as a new extra email.
  3. Save contact.
  4. Observe: save should refuse; today it may allow depending on which field/path was written.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-07-31T03:58:43.953Z
I'm so sorry, but the [AST-1065](https://linear.app/astralcareermatch/issue/AST-1065/update-candidate-ui-for-contact-info) ticket confusion threw a wrench in the scope of this ticket.  When a new email is added, it needs to be validated as unique in the whole candidate table, both the root email addresses and extra emails.

#### chuckles — 2026-07-31T00:11:39.173Z
[publish-ref-stale] AST-1080 (and AST-1079) STALE(dev+165) vs origin/dev — pausing build until Ada refreshes `sub/*` (`merge origin/dev` + `merge origin/ftr/AST-1045-verify-unique-contact-info` + republish).

@Ada Lovelace — refresh AST-1080 publish ref first; AST-1079 already on_ftr but also stale if you touch it.

— Chuckles

#### chuckles — 2026-07-30T18:16:01.537Z
@susan AST-1045 datt blocked on infra (not product):

1. `linear-chuckles` MCP is not connected in this session (persona MCPs present — hard-ban refuses hop).
2. Sub-chuck drones for AST-1079 repeatedly die `exit=143` (SIGTERM) with no agent output after ~6–9 min; children still Todo (AST-1079/AST-1080 → Ada).
3. Chuckles Linear API budget is near empty (rate limit).

Please restart linear-chuckles MCP (or fully restart Cursor MCP on chuckles box), then re-assign Todo/datt. I will not hop to other Linear MCPs.

— Chuckles

#### chuckles — 2026-07-30T03:20:00.527Z
@susan Open questions on AST-1045:

1. Which contact fields must be unique across candidates — emails only (`contact_email` / `reply_email`), or also phone, LinkedIn, GitHub, and/or websites?
2. Within one candidate, does “dedupe” mean (a) collapse duplicate list entries (e.g. websites), (b) forbid the same value in two scalar fields (e.g. contact email == reply email), or both?
3. On cross-candidate collision: hard-fail the save (recommended default), or soft-allow with a warning only?
4. Existing duplicate rows already in the DB — clean up / migrate in this epic, or enforce only on new/changed writes going forward?
5. Confirm uniqueness-scoped emails stay aligned with `CANDIDATE_LOOKUP_CONFIG` email paths (including transitional `profile.*` until gone) so bind/lookup and save enforcement share one vocabulary?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
