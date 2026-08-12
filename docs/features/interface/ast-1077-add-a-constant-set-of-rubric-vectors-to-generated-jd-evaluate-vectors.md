# AST-1077 — Add a constant set of rubric vectors to generated JD evaluate vectors

<!-- linear-archive: AST-1077 archived 2026-08-11 -->

## Linear archive (AST-1077)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1077/add-a-constant-set-of-rubric-vectors-to-generated-jd-evaluate-vectors  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

JD evaluate today grades only the candidate-authored job-description rubric. Operators need two constant vectors on every candidate’s JD rubric: **Quality Check** (is this enough of a JD to analyze?) and **Gut Check** (is this even plausible for this candidate?). Both carry importance **1** so they barely move the score when not F; the product value is the agent’s F (and related) signals. Scope is config-managed constants wired into the JD-evaluate rubric path — same product idea as company-prefilter **Reality Check**, for `evaluate_jd` / `jobdesc_rubric`.

## Functional scope

* **Config-owned constant JD vectors.** Quality Check (**QC**) and Gut Check (**GC**) live as managed criteria in config (labels, importance 1, grade letter → description text exactly as in the Original brief). Not hardcoded in core/UI.
* **Always present on every candidate JD rubric used by evaluate.** At `evaluate_jd` rubric hydration, merge QC and GC from config into the criteria list (**append** after candidate-authored criteria). If the operator deletes them in the editor, restore them on the next hydrate / generate / save so they cannot be lost.
* **Hard-fail on F.** They participate in existing JD evaluate grading and scoring. Importance stays 1. An **F** on Quality Check or Gut Check hard-fails the job via the existing evaluate_jd F-dealbreaker (that is the point).
* **Editor visibility.** After generate/save of the JD rubric, the Artifacts / rubric editor shows these two vectors (codes, labels, importance, grade descriptions). No separate backfill ticket — existing candidates pick them up when the JD rubric is next hydrated or saved in the UI.

## Architectural definition

* **Patterns to reuse** — `pattern.config.config-block`: constant criteria live in an organized `config.py` block (same shape as `EMBEDDED_COMPANY_PREFILTER_CRITERIA` / Reality Check). Hydration merges embedded rows into the `evaluate_jd` owner rubric the way `rubric_criteria_for_task` already merges RC for `prefilter_company`, except **append** (not prepend) and restore-on-delete.
* **New patterns proposed** — none (reuse embedded-criteria merge; do not invent a second embedding mechanism).
* **Applicable statutes** — `astral.config.config-source-of-truth` (definitions only in config); `astral.standards.no-hardcoded-sets` (no inline vector sets in core/UI); `astral.agent.grade-vector-validation` (agent grades must be in `{A,B,C,D,F,X}` — Quality Check lists A/B/C/F only; Gut Check lists A–D/F/X); `astral.standards.in-scope-only`; `astral.standards.dry-and-focused-functions`; `astral.layers.import-direction`; universal product set as touched.

## Boundaries

* Does **not** change DO / GET / LIKE / joblist / company-prefilter rubrics or add constant vectors there.
* Does **not** redesign scoring math, importance multipliers, or pass/fail thresholds beyond wiring these vectors into the existing evaluate_jd path (F-dealbreaker already hard-fails).
* Does **not** change Jobs list / Recommended Job Modal display work owned by AST-1059 / AST-1063 / AST-1064 (those consume whatever rubric/grades already exist).
* Does **not** add Admin UI to edit the constant definitions (config only until a later ticket).
* Does **not** invent new grade letters; Quality Check omits D/X by product brief; Gut Check includes X as written.
* Does **not** run a one-time DB backfill of existing rubric_vector rows.

## Acceptance criteria

1. Config holds Quality Check (**QC**) and Gut Check (**GC**) with importance **1** and the grade descriptions from the Original brief (verbatim meaning).
2. Generating, saving, or hydrating a candidate’s job-description / `evaluate_jd` rubric results in both vectors present, **appended after** candidate-authored criteria (codes + labels + importance + grade descriptions).
3. If an operator removes QC or GC from the editor, the next hydrate / generate / save restores them from config.
4. Running evaluate_jd for a candidate that has a JD rubric includes grades for both constant vectors in the job’s JD grades output.
5. An evaluate_jd run that grades Quality Check or Gut Check as **F** (with the existing dealbreaker confidence rule) moves the job to the normal JD fail path.
6. Candidate-authored JD criteria still appear; constants do not wipe or replace them (dedupe by code if a duplicate code already exists).
7. No other rubric owners gain these constants.

## Dependencies and blockers

none. Adjacent related: AST-1063 / AST-1064 (User Testing) and AST-1059 (PR Ready) for Jobs list rubric display — display consumers, not blockers for this epic.

## Open questions

none.

## Proposed child tickets

#### 1!: **Config constant JD vectors (QC / GC) - Ada**

Add the config block for Quality Check (**QC**) and Gut Check (**GC**) (importance 1; grade descriptions from the Original brief). No runtime merge yet — definitions only, ready for child 2.
**Citations:** `pattern.config.config-block`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`.

#### 2: **Wire constants into evaluate_jd rubric path - Ada**

Always-merge QC/GC into `evaluate_jd` rubric hydration (**append** after candidate criteria); restore on generate/save if missing; dedupe by code; hard-fail via existing F-dealbreaker; do not touch other rubric owners. After #1.
**Citations:** `pattern.config.config-block` (consume block), `astral.agent.grade-vector-validation`, `astral.standards.dry-and-focused-functions`, `astral.standards.in-scope-only`.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-1077 (parent) | ftr/AST-1077-add-a-constant-set-of-rubric-vectors |
| AST-1084 | sub/AST-1077/AST-1084-config-constant-jd-vectors |
| AST-1085 | sub/AST-1077/AST-1085-wire-constants-evaluate-jd |

**Epic worktree:** `astral-AST-1077/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **Thread** column is the fully-qualified `store.db` path (UUID is the directory name — extract for `agent --resume`). **datt resume:** read this table — not chat memory. One UUID per agent; never the parent Chuckles Thread UUID.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/bedf3b53afdf9337192ad7da1912456d/50714732-8857-438e-a0b8-5331012e24fa/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/e7d725cb-da4c-4747-871f-7a4a849f7455/store.db` |
| Radia | review | `/home/susan/.cursor/chats/bedf3b53afdf9337192ad7da1912456d/d1418481-9c6f-4686-b678-d65301f8704b/store.db` |

---

## Original brief

Add "Quality Check" to give the agent the chance to say "This is not a JD, no further analysis."  and "Gut Check" to give the agent the chance to say "This could be a slam dunk for the candidate"

Both of these have an Importance factor of 1, because it's really only the F's we care about.  These should be configured and managed in [config.py](<http://config.py>) and added to every candidate rubric when the job description rubric is generated for a candidate.

```
Quality Check
A == This is a valid job description with full details of the role and requirements and information about the company the candidate would be working for.
B == This is a valid job description with full details of the role and requirements, but limited information about the company the candidate would be working for.
C == This content references a job with enough detail about the role and requirements to perform fit analysis for the candidate.
F == This is not enough information to perform job fit analysis, either because it is not a job description, or it is too vague to determine fit for the candidate.
```

```
Gut Check
A == Based on the candidate's bio provided, this job would be a slam dunk for them.
B == Based on the candidate's bio provided, this job could be a good fit for them.
C == Based on the candidate's bio, this job would be doable, with caveats, for them.
D == Based on the candidate's bio, this job would be a stretch-to-impossible for them.
F == There's really no way this candidate could ever do this job.
X == There's not enough information about the job to make this determination with certainty.
```

### Comments

#### chuckles — 2026-07-31T00:09:36.954Z
[thread-orphan] Joan session `da0027e7-276d-4fe2-a6e6-65c8eb77e24d` relocated into epic workspace hash for AST-1077 (`…/0f41bf986cfef9e06ea903e586d6d4d9/…` → `…/bedf3b53afdf9337192ad7da1912456d/…`). Same UUID; continuing with `--resume`.

— Chuckles

#### chuckles — 2026-07-31T00:09:36.045Z
[thread-missing] Cursor chat `63cead8a-0eae-42bf-b0e4-d01eddb31a25` has no local `store.db` on **chuckles** (expected `/home/susan/.cursor/chats/bedf3b53afdf9337192ad7da1912456d/63cead8a-0eae-42bf-b0e4-d01eddb31a25/store.db`; blob-search also empty).

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered).

— Chuckles

#### chuckles — 2026-07-31T00:09:35.399Z
[thread-missing] Cursor chat `e1ee3f25-a0b0-47ce-9f6f-c58b0f10f42c` has no local `store.db` on **chuckles** (expected Betty workspace hash; blob-search also empty).

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered).

— Chuckles

#### chuckles — 2026-07-31T00:09:34.677Z
[thread-missing] Cursor chat `9b1d203a-2e06-424e-abc2-29894a4bc015` has no local `store.db` on **chuckles** (expected `/home/susan/.cursor/chats/bedf3b53afdf9337192ad7da1912456d/9b1d203a-2e06-424e-abc2-29894a4bc015/store.db`; blob-search also empty).

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered).

— Chuckles

#### chuckles — 2026-07-30T16:34:43.421Z
@susan open questions:

1. Codes **QC** / **GC** OK?
2. Always-merge at evaluate_jd hydration (RC pattern) + persist on generate/save, or craft-generate-only?
3. Quality Check F and Gut Check F both hard-fail JD via existing F-dealbreaker, or advisory?
4. Backfill existing candidates, or only post-ship generate/save?
5. Prepend (like RC) or append?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
