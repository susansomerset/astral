# AST-953 — Topic Menu Generation

<!-- linear-archive: AST-953 archived 2026-08-07 -->

## Linear archive (AST-953)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Give intake a durable **Topic Menu** after the preamble library is populated ([AST-952](https://linear.app/astralcareermatch/issue/AST-952/candidate-profile-preamble-to-intake)): Estelle confirms the preamble with the candidate (“Anything here you would change?”), then invents a directed set of interview topics—each short, answerable in a few minutes, marked required when Estelle’s prompt says so, and explicitly tied to a closed `informs` catalog. This epic stops at a confirmed, persisted menu ready for a later intake conversation; piecewise satisfaction turns and REQUIRED/ALL_TOPICS_READY state hops are a follow-on.

## Functional scope

* **Preamble confirm (Topic Menu step 1).** Estelle presents a confirmable summary of the preamble packet and asks whether the candidate would change anything; accepted preamble is the input to menu generation. (Owned here — not [AST-952](https://linear.app/astralcareermatch/issue/AST-952/candidate-profile-preamble-to-intake).)
* **Topic Menu generation.** From the confirmed preamble, Estelle invents the Topic Menu (pure Estelle — no config template library of seed topics).
* **Topic shape.** Each topic carries at least: display name; directed ask; required flag (for Estelle’s prompt judgment only in this epic); `informs` list; and status (`open` / `ready` / `retired`).
* **Closed** `informs` **vocabulary.** `informs` may only target: rubrics, base resume, strengths, priorities, deal breakers, and/or backstory. One topic may inform multiple of those. Estelle confirms coverage of the informs set; she does not invent new target kinds.
* **Directed, bite-sized topics.** Topics are scoped so a candidate can answer in fewer than a few minutes; each topic must directly inform at least one allowed `informs` target—no orphan small-talk topics.
* **Topic lifecycle without wipe.** Regenerating or revising keeps prior topic content; topics move among `open`, `ready`, and `retired` rather than deleting history wholesale.
* **Debug traceability (backend).** On any new or touched backend `debug=True` paths for confirm or menu generation: log what was found and what was recorded per step (index headers with universal `index N/M`, primary id, outcome; working detail under `|`; long blobs truncated per Code Rules / AST-538). UI has no debug-logging requirement.

## Architectural definition

* **Patterns to reuse**
  * `pattern.config.config-block` — closed `informs` catalog / Topic Menu config live as an explicit product config block.
* **New patterns proposed**
  * **Topic Menu + closed** `informs` **targets** — durable menu of directed topics each declaring rubrics / base resume / strengths / priorities / deal breakers / backstory coverage; introduced by children #1–#2; later satisfaction work reuses the same model.
  * **Topic status triad (**`open` **/** `ready` **/** `retired`**)** — revise without wiping prior content; introduced by #1; later intake satisfaction updates status rather than regenerating from scratch.
  * **Estelle preamble confirm before menu generation** — confirmable summary pass as step 1 of Topic Menu; introduced by #2; pairs with [AST-952](https://linear.app/astralcareermatch/issue/AST-952/candidate-profile-preamble-to-intake) library output.
* **Applicable statutes**
  * `astral.config.config-source-of-truth` — informs catalog / topic config are config, not hardcodes.
  * `astral.standards.no-hardcoded-sets` — allowed informs / topic status enums live in config.
  * `astral.agent.do-task-delegation` — Estelle confirm/generation are agent tasks, not a new persona stack.
  * `astral.layers.import-direction` / `astral.layers.core-vs-external-bright-line` / `astral.layers.ui-config-driven-business-logic` — persistence, agent orchestration, and UI stay in correct layers.
  * `astral.standards.debug-contract-gated` — backend `debug=True` found/recorded contract on touched paths.
  * `astral.docs.features-single-file-per-ticket` — one plan doc per child when planning.

## Boundaries

* Does **not** own the mechanical preamble front door, PREAMBLE_CONFIG, Ruth Valid/Try Again/Escalate checks, or the contact/context/artifacts library — [AST-952](https://linear.app/astralcareermatch/issue/AST-952/candidate-profile-preamble-to-intake); this epic consumes the populated preamble and owns the Estelle confirm pass.
* Does **not** own the later Estelle intake conversation that gradually satisfies required topics, progress UI for satisfaction, or REQUIRED_TOPICS_READY / ALL_TOPICS_READY automation — follow-on after this menu exists.
* Does **not** decide optional-topic skip vs artifact-request product rules beyond Estelle’s ability to mark a menu item `required` at generation time.
* Does **not** invent or rewrite the candidate state vocabulary.
* Does **not** craft base resume, rubrics, or other artifacts; `informs` declares intent only.
* Does **not** run company/job search or change ACTIVE_SEARCH dispatch gating.
* Must not regress intake chat session surfaces (AST-539 family) except where confirm/generation intentionally replaces the old “ready to build” generation gate for menu creation.
* Code Rules / statutes: closed `informs` vocabulary and topic status enums stay config-driven; backend debug contract when `debug=` surfaces are touched.

## Acceptance criteria

1. After a Valid preamble packet exists, Estelle runs a confirmable “Anything here you would change?” pass; the candidate can accept or correct before Topic Menu generation proceeds.
2. Given a confirmed preamble, Estelle produces a persisted Topic Menu (pure Estelle authorship) whose topics each have name, ask, required flag, status (`open` / `ready` / `retired`), and non-empty `informs` drawn only from rubrics, base resume, strengths, priorities, deal breakers, and/or backstory.
3. Estelle’s generation confirms informs coverage (one topic may cover multiple informs); topics without an allowed `informs` target are not accepted into the menu.
4. Every generated topic is directed and short enough to answer in a few minutes.
5. Revising the menu keeps prior topic content and uses `open` / `ready` / `retired` rather than wiping the menu wholesale.
6. This epic does **not** require automated hops to `REQUIRED_TOPICS_READY` / `ALL_TOPICS_READY` or a full satisfaction-turn loop to be considered done.
7. Touched backend `debug=True` confirm/generation paths emit per-step found/recorded debug lines per the contract above.

## Dependencies and blockers

* **Blocked by:** [AST-952](https://linear.app/astralcareermatch/issue/AST-952/candidate-profile-preamble-to-intake) — Candidate Profile Preamble to Intake; delivers the contact/context library this epic confirms and consumes. Do not dispatch Topic Menu children that need the packet until that handoff is available.
* Related (Done vocabulary): candidate state registry / [AST-871](https://linear.app/astralcareermatch/issue/AST-871/candidate-state-machine) family — topic-ready states exist for a **later** satisfaction/state-hops epic; not automated here.
* Soft adjacency: intake chat session (AST-539 family) — confirm/generation land in that experience without orphaning session resume/archive behavior.

## Open questions

none.

## Proposed child tickets

#### 1!: **Topic Menu model and persistence - Ada**

Durable Topic Menu storage: topic name, ask, required flag, closed `informs` catalog (rubrics, base resume, strengths, priorities, deal breakers, backstory), and status triad `open` / `ready` / `retired` (revise without wipe). Does **not** own Estelle confirm/generation (#2) or later satisfaction/state-hops work.
**Citations:** new Topic Menu + closed informs pattern (proposed); new topic status triad pattern (proposed); `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.standards.debug-contract-gated`.

#### 2: **Estelle preamble confirm and Topic Menu generation - Hedy**

Topic Menu step 1: Estelle confirmable preamble summary (“Anything here you would change?”), then pure-Estelle generation of a valid Topic Menu with informs-coverage confirmation (one ask may inform many). After #1; needs [AST-952](https://linear.app/astralcareermatch/issue/AST-952/candidate-profile-preamble-to-intake) handoff. Does **not** own the later satisfaction conversation or state hops.
**Citations:** new Estelle preamble-confirm-before-menu pattern (proposed); new Topic Menu + closed informs pattern (proposed); `astral.agent.do-task-delegation`; `astral.standards.debug-contract-gated`.

**Monolith check:** Functional scope has 7 capabilities; 2 proposed children (generation-only epic per Susan — satisfaction/state hops deferred).

**New patterns:** (1) Topic Menu + closed informs — #1–#2. (2) Topic status triad open/ready/retired — #1. (3) Estelle preamble confirm before menu — #2.

## Git (authoritative — ignore Linear gitBranchName)

| Ticket | origin |
| -- | -- |
| [AST-953](https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation) (parent) | ftr/AST-953-topic-menu-generation |
| [AST-1074](https://linear.app/astralcareermatch/issue/AST-1074/topic-menu-model-and-persistence-topic-menu-generation) | sub/AST-953/AST-1074-topic-menu-model-and-persistence |
| [AST-1075](https://linear.app/astralcareermatch/issue/AST-1075/estelle-preamble-confirm-and-topic-menu-generation-topic-menu) | sub/AST-953/AST-1075-estelle-preamble-confirm-and-topic-menu-generation |

**Epic worktree:** astral-AST-953/ — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **Thread** column is the fully-qualified `store.db` path (UUID is the directory name — extract for `agent --resume`). **datt resume:** read this table — not chat memory. One UUID per agent; never the parent Chuckles Thread UUID.

| Agent | Role | Thread |
| -- | -- | -- |
| Hedy | engineer | `/home/susan/.cursor/chats/b7bfc3a6a8fa35b32f7bf5f2ab3c017f/643a4613-9f42-428e-bd24-61eebbf8c9a5/store.db` |
| Ada | engineer | `/home/susan/.cursor/chats/b7bfc3a6a8fa35b32f7bf5f2ab3c017f/76c6db7e-d67f-401a-a1a0-6f5096f9b9b9/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/da578054-80a0-4b6b-929b-633275070195/store.db` |
| Radia | review | `/home/susan/.cursor/chats/b7bfc3a6a8fa35b32f7bf5f2ab3c017f/dfb49f98-08ec-4552-a640-3c0c319edde8/store.db` |

---

## Original brief

At candidate intake, the software will ask for some basic details from the candidate, and then send all that up to Estelle to capture metadata and create a "Topic Menu" for the AI interactions.  This supersedes our previous flags for candidate intake, allowing the topics to be resolved so that decisions like "Do we have all the high priority topics addressed?  Does the candidate want to move on to artifact generation, or keep talking?"

Examples of topics [{name:"Overall Experience at Acme", ask:"What was great, what was tolerable, and why did you leave?", required:True, informs:["backstory", "priorities", "dealbreakers", "strengths", "base_resume", "like_rubric", "do_rubric"]}, {name:"Detailed experience at Acme", ask:"Your resume says 'manufactured anvils and metal birdseed', but your linkedin profile just says 'abetted crimes for a coyote'— what's the real story there?", required:False, informs:["candidate_bio", "backstory", "do_rubric", "get_rubric"]}]

…and so on, so that topic satisfaction can be done in pieces rather than one big green flag for the candidate that can lead into rabbit holes.  Topics should be directed, take fewer than a few minutes to answer by the candidate, and must directly "inform" candidate profile content (profile conte[n/x]t or artifacts).

### Comments

#### chuckles — 2026-07-30T17:59:50.220Z
Yes — spawning Betty now on the bible/test-tree merge conflicts blocking AST-1074 publish-ref refresh (and the same hunks will hit when we refresh ftr onto origin/dev before prep-uat). Then Hedy sub-chuck for AST-1075 Plan Approved → UT.

— Chuckles

#### susan — 2026-07-30T17:52:16.833Z
@chuckles Are you going to call betty to resolve these issues?

#### chuckles — 2026-07-30T17:48:32.513Z
[do-all-the-things] blocked: merge conflict refreshing AST-1074 publish ref onto origin/dev — docs/test-bible/core/repo_admin_json.md (@Betty White); docs/test-bible/external/slack.md (@Betty White); docs/test-bible/ui/api/api_contact.md (@Betty White); tests/component/core/test_repo_admin_json.py (@Betty White); tests/component/external/test_slack.py (@Betty White); tests/component/ui/api/test_api_contact.py (@Betty White). AST-1075 stuck Plan Approved until AST-1074 sub is refreshable.

— Chuckles

#### chuckles — 2026-07-30T16:50:32.874Z
[publish-ref-stale] AST-1074 STALE(dev+106) on origin/sub/AST-953/AST-1074-topic-menu-model-and-persistence — refresh before AST-1075 build-child.

@Ada Lovelace: merge origin/dev + origin/ftr/AST-953-topic-menu-generation into your sub/*, push republish. No product change required.

— Chuckles

#### chuckles — 2026-07-30T03:01:25.644Z
[check-linear] Discussion — answers folded into definition; open questions none — waiting on your Todo approval (@susan)

#### susan — 2026-07-30T02:57:19.531Z
@Chuckles I answered your questions.

#### chuckles — 2026-07-30T02:38:50.761Z
@susan Open questions still open on AST-953 (format revised per your note — Architectural definition + bang-style children; preamble confirm is Topic Menu step 1 per AST-952):

1. **Epic breadth — generation only vs full satisfaction loop?** Confirm full loop in this parent, or generation-only first?

2. **Allowed `informs` vocabulary.** Closed config catalog, or Estelle may invent new targets?

3. **Who authors the menu?** Pure Estelle; config templates; or hybrid seeds + Estelle?

4. **Optional topics after REQUIRED_TOPICS_READY.** Finish optionals, skip toward artifacts from REQUIRED, or ALL mandatory before artifacts?

5. **Regeneration.** Regenerate whole menu, merge/add, or freeze after first generation?

— Chuckles

#### susan — 2026-07-30T02:36:54.871Z
@chuckles I think this description needs a revision for our latest formatting needs

#### chuckles — 2026-07-28T04:15:06.692Z
@susan Open questions on AST-953 Topic Menu Generation:

1. **Epic breadth — generation only vs full satisfaction loop?** Working assumption: this parent owns menu generation, piecewise satisfaction during intake, progress visibility, and REQUIRED/ALL_TOPICS_READY automation. Confirm, or should satisfaction + state hops be a follow-on after generation-only?

2. **Allowed `informs` vocabulary.** Closed config catalog of existing profile/context/artifact keys, or may Estelle name new targets later stages must learn?

3. **Who authors the menu?** Pure Estelle from preamble; config template library Estelle selects/adapts; or hybrid (required seeds + Estelle fills gaps)?

4. **Optional topics after REQUIRED_TOPICS_READY.** Stay to finish optionals, skip optionals toward artifacts from REQUIRED, or is ALL_TOPICS_READY mandatory before artifact request?

5. **Regeneration.** If preamble changes mid-intake: regenerate whole menu, merge/add topics, or freeze after first generation?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
