# AST-923 — State-consumer inventory + safe-change mechanics

- **Linear:** [AST-923](https://linear.app/astralcareermatch/issue/AST-923/state-consumer-inventory-safe-change-mechanics)
- **Parent:** [AST-911](https://linear.app/astralcareermatch/issue/AST-911/linear-issue-types-and-states-safe-change-mechanics-plan-discuss)
- **Publish ref:** `origin/sub/AST-911/AST-923-state-consumer-inventory`
- **Summary:** Inventory every Team Chuckles surface that keys on Linear state **names** and watcher tags; document extant status transition rules; give watcher configs an explicit state-vocabulary version with load-time mismatch detection; ship a written migration checklist dry-runnable for **AST-924**. Does **not** add **Plan Discuss**.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `~/team-chuckles/skills/rollcall/state_vocabulary.json` | **New.** Canonical vocabulary: `version` (int), `states` (name list), `watcher_tags` (name list) | team-chuckles / rollcall |
| `~/team-chuckles/skills/rollcall/watch_rules/define.json` | Add required `state_vocabulary_version` matching vocabulary `version` | watcher config |
| `~/team-chuckles/skills/rollcall/watch_rules/datt.json` | Same | watcher config |
| `~/team-chuckles/skills/rollcall/watch_rules/fix.json` | Same | watcher config |
| `~/team-chuckles/skills/rollcall/watch_rules/check.json` | Add `state_vocabulary_version`; drop stale `"In Review"` from `linear.states` (not a live AST team state) | watcher config |
| `~/team-chuckles/skills/rollcall/watch_rules/wrap.json` | Add `state_vocabulary_version` | watcher config |
| `~/team-chuckles/skills/rollcall/watch_linear.py` | Require `state_vocabulary_version` on load; compare to `state_vocabulary.json`; validate referenced state names ⊆ vocabulary; fail loud on mismatch | watcher runtime |
| `~/team-chuckles/docs/linear-state-consumers.md` | **New.** Full consumer inventory + extant transition rules (required metadata columns) | team-chuckles docs |
| `~/team-chuckles/docs/linear-state-migration-checklist.md` | **New.** Ordered migration checklist dry-runnable for AST-924 | team-chuckles docs |
| `docs/features/team-chuckles/ast-923-state-consumer-inventory.md` | This plan (on astral publish ref) | astral docs |

**Commit homes:** all product/tooling deliverables in **`team-chuckles`**. Plan doc only on this astral **`sub/*`** ref (same pattern as AST-945 / AST-939).

**Exempt / out of scope:**

- Adding **Plan Discuss** or changing Linear workspace states (**AST-924**).
- Plan-rubric content (**AST-916** / **AST-928**).
- Astral product `JOB_STATES` / `COMPANY_STATES` / `CANDIDATE_STATES` / `src/**`.
- Rewriting skill prose except where Stage 3 inventory **requires** a one-line owner pointer (do not edit skill gate logic).
- `docs/ASTRAL_CODE_RULES.md` §4.3 (stale Linear list in astral law) — **note in inventory only**; do not edit in this ticket.
- `wake_filters.json` keys are watcher **tags**, not Linear states — inventory them; do not change filter regexes.

---

## Stage 1: State-vocabulary versioning (configs + load gate)

**Done when:** Every `watch_rules/*.json` declares `state_vocabulary_version`; `watch_linear.py` refuses to load a rule whose version ≠ `state_vocabulary.json` `version`, or whose referenced Linear state names are not in `state_vocabulary.states`. A deliberate version mismatch is detectable by running the loader (no operator memory).

1. Create `~/team-chuckles/skills/rollcall/state_vocabulary.json` with exactly this shape (integer `version` starts at **1**):

```json
{
  "version": 1,
  "states": [
    "Backlog",
    "Discussion",
    "Todo",
    "In Progress",
    "Plan Ready",
    "Plan Approved",
    "Code Complete",
    "Tests Ready",
    "Tests Passed",
    "Review Posted",
    "User Testing",
    "PR Ready",
    "Done",
    "Canceled",
    "Cancelled",
    "Archive",
    "Duplicate"
  ],
  "watcher_tags": ["define", "datt", "fix", "check", "wrap"]
}
```

⚠️ **Decision:** `version` is an integer (not semver string) so equality is trivial. `states` is the **canonical name list** for Team Chuckles tooling — includes cancel/archive/duplicate names already referenced by `watch_linear.py` exclude sets. **Plan Discuss is not in v1** (AST-924 bumps version and adds the name).

2. In each of the five files under `~/team-chuckles/skills/rollcall/watch_rules/`, add a top-level key `"state_vocabulary_version": 1` (sibling of `"name"`, before other keys is fine).

3. In `~/team-chuckles/skills/rollcall/watch_rules/check.json`, remove `"In Review"` from `linear.states` (workspace has no such state; it is a stale string). Leave the other listed names unchanged.

4. In `~/team-chuckles/skills/rollcall/watch_linear.py`, extend `_load_rule` (after the existing required-key checks) to:

   a. Resolve vocabulary path as `Path(__file__).resolve().parent / "state_vocabulary.json"`.
   b. Load it with `json.load`; require keys `version` (int) and `states` (list of strings).
   c. Require `rule["state_vocabulary_version"]` to exist and be an `int`.
   d. If `rule["state_vocabulary_version"] != vocabulary["version"]`, raise `ValueError` whose message includes both integers and the rule path/name — e.g. `state_vocabulary_version mismatch: rule=… has N, vocabulary has M`.
   e. Collect Linear state **names** referenced by the rule from: `linear.state` (string), `linear.states` (list), and `by_state` object keys. Every collected name must be in `set(vocabulary["states"])`; otherwise raise `ValueError` naming the unknown state(s).
   f. Do **not** read or compare Linear state **ids**. Matching stays name-only (existing `_state_name` / GraphQL `state.name` filters).

5. Smoke-check from `~/team-chuckles/skills/rollcall/`:

```bash
python3 -c "
from pathlib import Path
import watch_linear as w
for p in sorted(Path('watch_rules').glob('*.json')):
    w._load_rule(p.resolve())
    print('ok', p.name)
"
```

All five must print `ok`. Then confirm mismatch detection:

```bash
python3 -c "
from pathlib import Path
import json, tempfile, watch_linear as w
p = Path('watch_rules/define.json')
rule = json.loads(p.read_text())
rule['state_vocabulary_version'] = 999
t = Path(tempfile.mkstemp(suffix='.json')[1])
t.write_text(json.dumps(rule))
try:
    w._load_rule(t)
    raise SystemExit('expected ValueError')
except ValueError as e:
    assert 'mismatch' in str(e).lower() or '999' in str(e)
    print('mismatch-detectable')
finally:
    t.unlink(missing_ok=True)
"
```

6. Commit in **team-chuckles**: `code(AST-923): state vocabulary v1 + watcher version gate`.

---

## Stage 2: Name-only matching confirmation

**Done when:** Grep of team-chuckles shows no GraphQL / filter usage of Linear state **ids** as primary keys for watcher/skill gating; inventory (Stage 3) will record the name-only law. No product behavior change beyond Stage 1’s stale `"In Review"` drop.

1. From `~/team-chuckles`, run and keep the transcript for the inventory “verification” section:

```bash
rg -n 'stateId|state\.id|fromStateId|toStateId|states\s*:\s*\{[^}]*id' \
  skills agents hooks \
  --glob '!**/__pycache__/**'
```

**Required:** zero hits that key watcher/skill filters on state ids. (Comment text mentioning ids is fine; live filter code is not.)

2. Confirm existing name filters remain the only path — spot-check that `watch_linear.py` still builds filters with `state.name` (`eq` / `in` / `nin`) and `_state_name` reads `state.name`. Do **not** rewrite those helpers unless the grep in step 1 finds a real id-keyed path (if it does: stop and comment on **AST-911** with the path).

3. Commit only if Stage 1 left uncommitted follow-ups; otherwise fold any Stage 2 doc note into Stage 3. Prefer **no separate commit** when Stage 1 already landed and grep is clean.

---

## Stage 3: Consumer inventory + extant transition rules

**Done when:** `~/team-chuckles/docs/linear-state-consumers.md` exists with (a) one inventory row per consumer below, (b) required metadata columns filled, (c) an **Extant status transition rules** section covering every name in `state_vocabulary.json` `states` that the pipeline uses (happy-path + watcher exclusives + exclude sets).

1. Create `~/team-chuckles/docs/linear-state-consumers.md`. Header must state: vocabulary version **1**; owner epic **AST-911**; this inventory is the baseline **AST-924** extends; consumers key on state **names** only.

2. **Inventory table columns** (required on every row — ticket AC):

| Column | Meaning |
|--------|---------|
| `path` | Repo-relative path under `team-chuckles/` (or `~/.cursor/…` only if not in-repo; prefer in-repo paths) |
| `kind` | One of: `watcher-config`, `watcher-runtime`, `skill-gate`, `handoff-table`, `rollcall-action`, `wake-tag`, `docs` |
| `state_names` | Exact Linear status names matched/gated (comma-separated), or `—` if tag-only |
| `tags` | Watcher pane tags (`define`/`datt`/`fix`/`check`/`wrap`) if applicable, else `—` |
| `vocabulary_version` | `1` for versioned watcher configs; `n/a` for prose/skills that follow names but do not declare a version |
| `owner_pointer` | Skill or script that owns changes (e.g. `skills/rollcall/watch_linear.py`, `skills/seed-agents-md/SKILL.md`) |

3. **Mandatory consumer rows** (include all; fill metadata from files as they exist after Stage 1):

| path | kind | notes for the builder |
|------|------|------------------------|
| `skills/rollcall/state_vocabulary.json` | `docs` | Canonical vocabulary; version source of truth |
| `skills/rollcall/watch_rules/define.json` | `watcher-config` | `Discussion` |
| `skills/rollcall/watch_rules/datt.json` | `watcher-config` | `Todo`, `In Progress` |
| `skills/rollcall/watch_rules/fix.json` | `watcher-config` | `User Testing` |
| `skills/rollcall/watch_rules/check.json` | `watcher-config` | states list after Stage 1 (no `In Review`) |
| `skills/rollcall/watch_rules/wrap.json` | `watcher-config` | `PR Ready` |
| `skills/rollcall/watch_linear.py` | `watcher-runtime` | `_WATCHER_EXCLUSIVE`, `_CHECK_ASSIGNEE_STATES`, `_NEVER_WATCH_STATES`, `_MENTION_EXCLUDE`, GraphQL `state.name` filters |
| `skills/rollcall/wake_filters.json` | `wake-tag` | keys = watcher tags; not Linear states |
| `skills/rollcall/WAKE_CHEATSHEET.md` | `wake-tag` | documents `[define]`…`[wrap]` ↔ states |
| `skills/rollcall/rollcall_table.py` | `rollcall-action` | `STATUS_SORT`, `action()` skill_by_status |
| `skills/rollcall/SKILL.md` | `skill-gate` | exclude statuses + action column docs |
| `agents/handoff-table.md` | `handoff-table` | status → seed persona / hook |
| `skills/seed-agents-md/SKILL.md` | `skill-gate` | status → seed |
| `skills/plan-child/SKILL.md` | `skill-gate` | Todo → Plan Ready |
| `skills/validate-plan/SKILL.md` | `skill-gate` | Plan Ready → Plan Approved |
| `skills/build-child/SKILL.md` | `skill-gate` | Plan Approved → Code Complete |
| `skills/qa-child/SKILL.md` | `skill-gate` | Code Complete → Tests Ready |
| `skills/test-child/SKILL.md` | `skill-gate` | Tests Ready → Tests Passed |
| `skills/review-child/SKILL.md` | `skill-gate` | Tests Passed → Review Posted |
| `skills/resolve-child/SKILL.md` | `skill-gate` | Review Posted → User Testing |
| `skills/define-parent/SKILL.md` | `skill-gate` | Discussion |
| `skills/dispatch-parent/SKILL.md` | `skill-gate` | Todo / In Progress parent |
| `skills/do-all-the-things/SKILL.md` | `skill-gate` | Todo / In Progress |
| `skills/check-linear/SKILL.md` | `skill-gate` | inbox statuses; User Testing+[fix] carve-out |
| `skills/fix-uat/SKILL.md` | `skill-gate` | parent User Testing |
| `skills/prep-uat/SKILL.md` | `skill-gate` | children User Testing → parent User Testing |
| `skills/merge-child/SKILL.md` | `skill-gate` | User Testing rollup |
| `skills/finish-up/SKILL.md` | `skill-gate` | PR Ready → Done |
| `skills/audit-linear/SKILL.md` | `skill-gate` | User Testing / PR Ready / Done parents |
| `docs/linear-state-migration-checklist.md` | `docs` | checklist itself (Stage 4); version n/a |

4. After drafting rows, run a discovery grep and **add any additional** team-chuckles files that gate on pipeline status names but are missing from the table:

```bash
cd ~/team-chuckles
rg -l 'Plan Ready|Plan Approved|Code Complete|Tests Ready|Tests Passed|Review Posted|User Testing|PR Ready|Discussion' \
  skills agents hooks docs \
  --glob '!**/__pycache__/**' | sort
```

Do **not** absorb astral `docs/ASTRAL_*.md` into the editable inventory rows (those are astral law). Add a short **Adjacent (astral, not edited here)** note listing `docs/ASTRAL_TEAM_WORKFLOW.md` (happy-path status→skill) and `docs/ASTRAL_CODE_RULES.md` §4.3 (stale; do not fix in AST-923).

5. **Extant status transition rules** section — one subsection or table row per pipeline status in vocabulary that consumers use. For each status document:

   - **Enter:** who may move an issue into this status (Susan / Chuckles skill / engineer skill / Betty / Radia), citing the skill name.
   - **Exit:** typical next status(es) and who moves.
   - **Gating consumers:** inventory `path` values that match this name (watcher and/or skill).

   Use `docs/ASTRAL_TEAM_WORKFLOW.md` “Linear status → skill (happy path)” plus watcher exclusivity in `watch_linear.py` as the baseline. Parent/child differences (e.g. User Testing parent vs child) must be explicit.

⚠️ **Decision:** Transition rules for **extant** statuses live in this inventory deliverable (not only in astral workflow). AST-924 adds Plan Discuss **on top of** this baseline — it must not rediscover enter/exit rules for Todo/Plan Ready/etc.

6. Commit in **team-chuckles**: `code(AST-923): linear state consumer inventory + transition rules`.

---

## Stage 4: Migration checklist (dry-runnable for AST-924)

**Done when:** `~/team-chuckles/docs/linear-state-migration-checklist.md` exists with a fixed order of operations and a completed **dry-run worksheet** filled as if adding **Plan Discuss** (no live Linear state create, no watcher pause on production — paper/dry-run only).

1. Create `~/team-chuckles/docs/linear-state-migration-checklist.md` with these **ordered** steps (parent AC order — do not reorder):

   1. **Pause watchers** — stop tmux session `chuck` (`Ctrl-C` in pane or `tmux kill-session -t chuck`); confirm no `watch_linear.py` processes.
   2. **Update vocabulary** — bump `state_vocabulary.json` `version` by 1; add new state **name(s)** to `states`.
   3. **Update watcher configs** — set each `watch_rules/*.json` `state_vocabulary_version` to the new version; add/remove state names in `linear.state` / `linear.states` / `by_state` as required; update `_WATCHER_EXCLUSIVE` / `_CHECK_ASSIGNEE_STATES` / exclude frozensets in `watch_linear.py` if the new state is watched or excluded.
   4. **Update skills / rollcall / handoff** — every inventory row with `kind` in `skill-gate`, `rollcall-action`, `handoff-table` that must learn the new state (for Plan Discuss: at minimum `validate-plan`, `plan-child`/`build-child` boundaries, `rollcall_table.py` `STATUS_SORT` + `action()`, `agents/handoff-table.md` if a seed applies, `check.json` if inbox should see it).
   5. **Install / refresh host links** — `cd ~/team-chuckles && ./install.sh`.
   6. **Resume watchers** — `bash -l ~/team-chuckles/skills/wake-up-chuck-linux.sh` (or Mac equivalent only if chuckles server is not the watcher host).
   7. **Verify canary** — load-check all five rules (`_load_rule` smoke from Stage 1); confirm version mismatch still raises; move or observe a **canary child** through the new state path without stalled watchers (AST-924 executes this live; this ticket only dry-runs the worksheet).

2. Include a **Dry-run worksheet (AST-924 — Plan Discuss)** section with one checkbox line per step above, filled out as a table:

   | Step | Dry-run note for Plan Discuss |
   |------|-------------------------------|
   | Pause | Would kill `chuck` session on chuckles host |
   | Vocabulary | v1 → v2; add `"Plan Discuss"` to `states` |
   | Watcher configs | Bump all five `state_vocabulary_version` to 2; decide which watchers list Plan Discuss (likely `check`; **not** define/datt/fix/wrap unless AST-924 says otherwise) |
   | Skills / rollcall / handoff | List concrete files from inventory that AST-924 must touch (names only — no edits in AST-923) |
   | Install | `./install.sh` |
   | Resume | wake-up-chuck-linux |
   | Canary | Deferred to AST-924 live run |

3. Do **not** create the Linear state, do **not** pause real watchers for this dry-run, do **not** bump vocabulary to v2 in this ticket.

4. Commit in **team-chuckles**: `code(AST-923): linear state migration checklist + Plan Discuss dry-run`.

---

## Stage 5: Verify + astral plan tip note

**Done when:** Stage 1 smoke + mismatch detection still pass; inventory and checklist paths exist on `team-chuckles` `main` (or the working branch used for these commits); Code Complete stub on the astral plan lists team-chuckles SHAs.

1. Re-run Stage 1 smoke + mismatch scripts.
2. Confirm files exist:

```bash
test -f ~/team-chuckles/skills/rollcall/state_vocabulary.json
test -f ~/team-chuckles/docs/linear-state-consumers.md
test -f ~/team-chuckles/docs/linear-state-migration-checklist.md
```

3. On the astral plan doc (this file), append the usual **Review (build stub)** table with plan SHA + team-chuckles commit SHAs per stage (build-child does this at Code Complete — during build, after commits).
4. Push team-chuckles commits to **`origin/main`** (team-chuckles remote). Publish astral plan tip with `git push origin HEAD:sub/AST-911/AST-923-state-consumer-inventory` only for plan/stub commits on the epic worktree.
5. Host note at Code Complete: re-run `./install.sh` so `~/.cursor/skills/rollcall` picks up vocabulary + `watch_linear.py` gate before watchers restart.

---

## Execution contract

- Execute stages in order. Do not add Plan Discuss to Linear or to `state_vocabulary.json` v1.
- Do not edit astral `src/**`, `tests/**`, or bible paths.
- If `watch_rules` or `_load_rule` shape has drifted so Stage 1 steps cannot apply literally — stop and comment on **AST-911** with the `🛑 Stage N blocked` format from plan-child.
- Discovery grep in Stage 3 may add inventory rows; it must **not** expand into rewriting those skills in this ticket.

---

## Self-Assessment

**Scope:** `Single-Component` — Team Chuckles rollcall watcher configs/runtime plus two docs under `team-chuckles/docs/`; no Astral product layers.

**Conf:** `high` — consumers and name-only GraphQL filters are already visible; ticket AC maps cleanly onto vocabulary file + load gate + inventory + checklist (same commit-home split as AST-909 children).

**Risk:** `Medium` — a buggy version gate could refuse to start all watchers after install; mismatch messaging and smoke scripts in Stage 1 exist to catch that before resume. Stale `"In Review"` removal is low risk (state does not exist on the AST team).

## Self-review vs ASTRAL_CODE_RULES

- §1.1 in-scope only — satisfied (team-chuckles tooling; product state machines untouched).
- §1.4 / §2.1 config-as-truth — vocabulary file is the single version + name list for watchers; rules declare version explicitly.
- §2.6 product state machine — N/A (Linear pipeline vocabulary, not JOB_STATES).
- §3.3 imports — `watch_linear.py` keeps local JSON load; no new astral layer imports.
- §4.3 Linear Workflow States in astral law is stale relative to real AST statuses — inventoried as adjacent; **not** edited here (avoids scope creep into astral law docs owned by other tickets).

## Review (build stub)

**Publish ref:** `origin/sub/AST-911/AST-923-state-consumer-inventory`

| Stage | Commit | Summary |
|-------|--------|---------|
| plan | `cf810fa` | Plan doc on astral sub |
| 1 | `team-chuckles@c2f7b13` | `state_vocabulary.json` v1; watcher `state_vocabulary_version`; `_load_rule` mismatch gate; drop stale `In Review` from check.json |
| 2 | (no commit) | Name-only grep clean — no state-id keyed filters |
| 3 | `team-chuckles@b0e6716` | `docs/linear-state-consumers.md` inventory + extant transition rules |
| 4 | `team-chuckles@89b14aa` | `docs/linear-state-migration-checklist.md` + Plan Discuss dry-run worksheet |

**Tip:** astral plan + stub (this commit); tooling on `team-chuckles` `main` @ `89b14aa`.

**Host note:** re-run `~/team-chuckles/./install.sh` before restarting watchers so `~/.cursor/skills/rollcall` picks up vocabulary + load gate.

---

## Radia review (2026-07-22)

**Diff:** `origin/dev...origin/sub/AST-911/AST-923-state-consumer-inventory` (astral docs) + `team-chuckles` `main` @ `89b14aa` (tooling).

### What's solid

| Area | Notes |
| --- | --- |
| Plan fidelity | Stages 1–4 match: vocabulary v1 exact shape (no Plan Discuss); five `watch_rules` declare `state_vocabulary_version: 1`; `_load_rule` mismatch + unknown-name gates; `In Review` dropped from `check.json`; inventory + transition rules; migration checklist + Plan Discuss dry-run worksheet. |
| Smoke | All five `_load_rule` ok; deliberate version `999` raises mismatch; name-id grep empty under `skills`/`agents`/`hooks`. |
| Scope / bible | Astral three-dot: plan + `docs/test-bible/README.md` docs-only note; no `src/` / pytest. Self-Assessment `Single-Component` matches. |
| Boundaries | No Plan Discuss in vocab/rules; §4.3 astral law left adjacent-only; skill gate logic not rewritten. |
| Rules | §1.1 in-scope (team-chuckles tooling); config-as-truth via `state_vocabulary.json`; §5a–§5g N/A (no astral product layers). |

### Issues

None (**fix-now**).

### Recommended actions

| Severity | Item |
| --- | --- |
| **Advisory** | `watch_linear.py` `_CHECK_ASSIGNEE_STATES` still contains dead `"In Review"` — inventory Verification section already notes it; harmless (no AST team state). Optional cleanup on a later pass / with AST-924 frozenset edits. |

**Verdict:** Clean — `resolve-child` may proceed (no product/doc fixes required beyond this `docs()` commit).

## Resolution

**Date:** 2026-07-22  
**Review:** Radia `942a2e0` — no **fix-now**; one **advisory** (dead `"In Review"` in `_CHECK_ASSIGNEE_STATES`).

| Item | Action |
|------|--------|
| fix-now | None |
| Advisory — stale `"In Review"` in `_CHECK_ASSIGNEE_STATES` | Deferred to AST-924 frozenset edits (per Radia); already noted in inventory Verification |

No product or team-chuckles code changes in resolve. Tooling tip remains `team-chuckles@89b14aa`.
