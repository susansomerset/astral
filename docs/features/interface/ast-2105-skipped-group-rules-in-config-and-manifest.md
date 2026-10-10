# AST-2105 — Skipped group rules in config and manifest

- **Ticket:** [AST-2105](https://linear.app/astralcareermatch/issue/AST-2105) (child of [AST-2102](https://linear.app/astralcareermatch/issue/AST-2102) — Group the Skipped jobs list by Fail, Bot block and Error)
- **Publish ref:** `sub/AST-2102/AST-2105-skipped-group-rules` (origin only)
- **Canon Scope:** none — the ticket's Citations are "none. No in-force directive governs config registries or the manifest dict."

Adds the config side of Skipped grouping: one ordered registry in `src/utils/config.py` that names the four Skipped groups (Error, Bot block, Fail, Other), each with a display label, state-name prefixes and explicit member states; a module-level guard over it; and a `groups` entry on `build_state_ui_manifest()["jobs"]["skipped"]` so the React page ([AST-2106](https://linear.app/astralcareermatch/issue/AST-2106), not this ticket) can bucket rows without a parallel TS vocabulary. No state is renamed and no React file is touched.

## Build base (AST-2073 not yet on `origin/dev`)

Blocker [AST-2073](https://linear.app/astralcareermatch/issue/AST-2073) (Revise terminal states) is at User Testing but **not** on `origin/dev`. Per the ticket's Notes for planning, this sub is built on a tree where AST-2073's rename is present:

- At plan time the epic worktree ran `sync-child.sh sub/AST-2102/AST-2105-skipped-group-rules --ftr AST-2102-group-skipped-jobs`, then merged `origin/ftr/AST-2073-revise-terminal-states` (tip `7bb5500f0`) into the sub with message `sync(ftr): origin/ftr/AST-2073-revise-terminal-states`. That merge is on `origin/<publish-ref>` with this plan.
- **Builder:** after your own `sync-child.sh`, confirm `git merge-base --is-ancestor origin/ftr/AST-2073-revise-terminal-states HEAD` exits 0. If AST-2073's ftr has moved since (`git log HEAD..origin/ftr/AST-2073-revise-terminal-states` non-empty) and it is still not on `origin/dev`, merge it again with the same `sync(ftr): origin/ftr/AST-2073-revise-terminal-states` message. If it has landed on `origin/dev`, `sync-child.sh` already covers it — no extra merge.
- Consequence for Chuckles at `merge-child` / `prep-uat`: this sub carries AST-2073's commits until AST-2073 lands on dev.

**Verified on the merged tree at plan time:** `SKIPPED_STATES` has 55 unique entries; `ERROR_STATE_PREFIX == "ERROR_"` and `BOT_BLOCKED_STATE_PREFIX == "BOT_BLOCKED_"` exist (AST-2086 grammar, `config.py` ~L244–245); a dry run of the AC 2 rules gives Error 31, Bot block 4, Fail 19, Other = `['INVALID_TITLE']`. Fail is 19 rather than the ticket note's 13 because AST-2096's six `*_ALL_X` fail states (`ALL_X_FAIL_STATES`) landed on dev after AST-2086's branch was measured; all six start with `FAILED_` / `METEORITE_FAILED_` and belong in Fail. AC 2 pins only Other, so this is expected. `JOBS_SKIPPED_BELOW_DISPATCH_KEY` (`"__BELOW_DISPATCH_FLOOR__"`) is **not** in `SKIPPED_STATES` — hence the guard's explicit "or the below-dispatch key" clause.

## Explicit scope gate

Ticket `## Scope`: `src/utils/config.py` only — group rule registry, guard, manifest `groups` entry. Every row below is that file and each change is one of those three kinds. `section_order`, `section_labels`, `below_dispatch_*` and `bulk_retry_to_state_by_from_state` are unchanged. No `tests/`, bible, or React edits (Betty owns tests; AST-2106 owns `StateUiContext.tsx` / `JobsSkipped.tsx`).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `JOBS_SKIPPED_GROUPS` registry + two module-level guard asserts after `JOBS_SKIPPED_SECTION_LABELS`; add `"groups"` to `build_state_ui_manifest()["jobs"]["skipped"]` | utils |
| `docs/features/interface/ast-2105-skipped-group-rules-in-config-and-manifest.md` | This plan (plan-child) + review stub (build-child §10) | docs |

## Stage 1: Group rule registry, guard, manifest `groups`

**Done when:** `python3 -c "import src.utils.config"` exits 0; `build_state_ui_manifest()["jobs"]["skipped"]["groups"]` lists Error / Bot block / Fail / Other with the AC 1 prefixes and members; the AC 2 script prints `['INVALID_TITLE']`; adding `"NOT_A_STATE"` to Fail's members makes the import raise `AssertionError`.

0. Before editing, run `ruff check src/utils/config.py 2>&1 | tail -1` and record the count (expected `Found 102 errors.`).

1. In `src/utils/config.py`, locate the closing `}` of `JOBS_SKIPPED_SECTION_LABELS` (the dict ending with `bot_blocked_state_for("qualify_meteorite"): "Bot Blocked",`, ~L4330) and the blank line after it, immediately before the comment `# Which \`job[...]\` grade blob to read for rubric columns (keys ⊆ JOB_STATES).`. Insert this block there (one blank line before, one blank line after), exactly:

   ```python
   # AST-2105: Skipped page groups, in display order, keyed by group id. A row's group is the
   # first whose members list its state, else the first whose prefixes match it, else the last
   # group — the catch-all, with neither prefixes nor members. Prefixes and members live here only;
   # the React page reads them from build_state_ui_manifest()["jobs"]["skipped"]["groups"].
   JOBS_SKIPPED_GROUPS = {
       "error": {"label": "Error", "prefixes": [ERROR_STATE_PREFIX], "members": []},
       "bot_block": {"label": "Bot block", "prefixes": [BOT_BLOCKED_STATE_PREFIX], "members": []},
       "fail": {
           "label": "Fail",
           "prefixes": ["FAILED_", "METEORITE_FAILED_", "JD_SCRAPE_FAIL_"],
           # Resurrect-only manual skip + the below-floor virtual section (not a JOB_STATES key).
           "members": ["CANDIDATE_SKIPPED", JOBS_SKIPPED_BELOW_DISPATCH_KEY],
       },
       "other": {"label": "Other", "prefixes": [], "members": []},
   }
   # Explicit members must be real Skipped states (or the below-floor key), so a rename can't orphan one.
   assert all(
       m in SKIPPED_STATES or m == JOBS_SKIPPED_BELOW_DISPATCH_KEY
       for g in JOBS_SKIPPED_GROUPS.values() for m in g["members"]
   ), "JOBS_SKIPPED_GROUPS: member is not a Skipped state"
   # Exactly one catch-all, and it is last — anything after it would be unreachable.
   assert [not (g["prefixes"] or g["members"]) for g in JOBS_SKIPPED_GROUPS.values()] == (
       [False] * (len(JOBS_SKIPPED_GROUPS) - 1) + [True]
   ), "JOBS_SKIPPED_GROUPS: only the last group may be the catch-all"
   ```

   ⚠️ **Decision:** Registry is a dict keyed by group id (`error` / `bot_block` / `fail` / `other`), not a list of `{"key": …}` rows — Susan's standing rule is that elements are indexed by their id. Python dict insertion order carries the display order. The manifest (step 2) still emits an ordered **list** because AC 1 reads `groups[*].label` and AC 2's script indexes `g[-1]`.

   ⚠️ **Decision:** Error and Bot block prefixes reference AST-2086's `ERROR_STATE_PREFIX` / `BOT_BLOCKED_STATE_PREFIX` constants instead of retyping `"ERROR_"` / `"BOT_BLOCKED_"` — same values (AC 1), and the prefix strings then exist once in `config.py`. Fail's three prefixes have no existing constant and are written literally here, once.

   ⚠️ **Decision:** Placement after `JOBS_SKIPPED_SECTION_LABELS` keeps the Skipped UI config together; `SKIPPED_STATES`, `JOBS_SKIPPED_BELOW_DISPATCH_KEY`, and both prefix constants are all defined above this point, so the asserts run at import with every name bound.

2. In `build_state_ui_manifest()`, in the `"skipped": { … }` dict under `"jobs"`, add one entry **after** `"bulk_retry_to_state_by_from_state": dict(JOBS_SKIPPED_BULK_RETRY_TO_STATE),`:

   ```python
                   # AST-2105: ordered group rules (key, label, prefixes, members) — catch-all last.
                   "groups": [
                       {"key": k, "label": g["label"], "prefixes": list(g["prefixes"]), "members": list(g["members"])}
                       for k, g in JOBS_SKIPPED_GROUPS.items()
                   ],
   ```

   Do not change any other key in that dict, and do not change `skipped_order` / `skipped_labels`. The `list(...)` copies follow the function's existing `dict(...)` / `list(...)` copy pattern so callers can't mutate the registry.

3. Compile and lint (Susan's rule — before commit):
   - `python3 -m py_compile src/utils/config.py` → exit 0.
   - `python3 -c "import src.utils.config"` → exit 0 (AC 4 "Builds clean"; also proves both guard asserts pass).
   - `ruff check src/utils/config.py 2>&1 | tail -1` → must equal the pre-edit count recorded in step 0 (plan-time baseline: `Found 102 errors.`, all pre-existing). A higher count means the new lines introduced a finding — fix it in the new lines only.

4. Verify AC 1 — run from the worktree root:

   ```bash
   python3 -c "
   from src.utils import config as c
   sk = c.build_state_ui_manifest()['jobs']['skipped']
   g = sk['groups']
   assert [x['label'] for x in g] == ['Error','Bot block','Fail','Other'], g
   assert [x['key'] for x in g] == ['error','bot_block','fail','other'], g
   assert g[0]['prefixes'] == ['ERROR_'] and g[1]['prefixes'] == ['BOT_BLOCKED_'], g
   assert g[2]['prefixes'] == ['FAILED_','METEORITE_FAILED_','JD_SCRAPE_FAIL_'], g
   assert g[2]['members'] == ['CANDIDATE_SKIPPED', sk['below_dispatch_key']], g
   assert g[3]['prefixes'] == [] and g[3]['members'] == [], g
   assert g[0]['members'] == [] and g[1]['members'] == [], g
   print('AC1 ok')"
   ```

   → prints `AC1 ok`.

5. Verify AC 2 — run the ticket's script verbatim:

   ```bash
   python3 -c "
   from src.utils import config as c
   g = c.build_state_ui_manifest()['jobs']['skipped']['groups']
   def grp(s):
       for x in g:
           if s in x['members']: return x['label']
       for x in g:
           if any(s.startswith(p) for p in x['prefixes']): return x['label']
       return g[-1]['label']
   print(sorted(s for s in c.SKIPPED_STATES if grp(s) == 'Other'))"
   ```

   → prints exactly `['INVALID_TITLE']`. Anything else: stop and comment on the parent (do not adjust prefixes on the fly).

6. Verify AC 3 (guard bites) — temporary edit, never committed:
   - In the `"fail"` entry, change `"members": ["CANDIDATE_SKIPPED", JOBS_SKIPPED_BELOW_DISPATCH_KEY],` to `"members": ["CANDIDATE_SKIPPED", JOBS_SKIPPED_BELOW_DISPATCH_KEY, "NOT_A_STATE"],`.
   - `python3 -c "import src.utils.config"` → must exit non-zero with `AssertionError: JOBS_SKIPPED_GROUPS: member is not a Skipped state`.
   - Revert that one line by hand to the step-1 text, then re-run `python3 -c "import src.utils.config"` → exit 0, and confirm `git diff src/utils/config.py` contains no `NOT_A_STATE`.

7. Commit on the epic worktree with only `src/utils/config.py` staged: `code(AST-2105): Skipped group rules registry, guard, manifest groups`. Publish per build-child (`git push origin HEAD:sub/AST-2102/AST-2105-skipped-group-rules`).

## Notes for QA (Betty — informational, not builder steps)

- No existing test pins the exact key set of `build_state_ui_manifest()["jobs"]["skipped"]` (checked `tests/component/utils/test_config.py`), so the additive `groups` key should not break existing nodes.
- `tests/component/frontend/fixtures/stateUiManifestFixture.ts` is a partial snapshot; whether it gains `groups` is AST-2106's / Betty's call, not this ticket's.

## Estimate

Confirm Chuckles estimate: 2 — agree


## Joan validate

[plan-rubric]
**Ticket:** AST-2105
**Overall:** APPROVED
**Corpus:** c04b07deda8f5a750afd473ec847d06ed2207065
**Publish ref:** `origin/sub/AST-2102/AST-2105-skipped-group-rules` @ `a1d2e90ea`

## Canon scores

(explicit Canon Scope **none**, locked at parent Discussion — no directive ids on the ticket list; R3 has zero rows; Radia’s canon column for this child is likewise empty by design)

## Traceability

AC **1, 2, 3, 11** → Stage 1 (registry + guards + manifest `groups`, import/AC scripts, ephemeral AC3 guard check); parent AC **4–10** → N/A (AST-2106 / out of child `## Scope`).

### acceptable — No `## Self-assessment` block

- **Location:** Plan doc structure
- **Finding:** No self-assessment section (common on small config-only plans).
- **Recommendation:** Optional for build parity; not blocking at this footprint.

### discuss — Optional future canon (not scored)

- **Location:** Parent Architectural definition / child Citations
- **Finding:** `astral.config.config-source-of-truth` and draft `stat.layers.ui-config-driven-business-logic` spirit plainly describe “rules in config, manifest to UI,” but parent locked **Canon Scope: none** with rationale.
- **Recommendation:** No plan change; if Archie later wants enforceable law for manifest registries, amend Canon Scope at Discussion — do not widen the frozen list in build.

**R6 (adversarial):** Identity OK (`Plan Ready`, assignee Joan). Child scope is `config.py` only; plan’s Explicit scope gate, Files Changed, and stages align. AST-2073 build-base merge is documented with `merge-base --is-ancestor` check (verified on epic worktree). Registry placement after `JOBS_SKIPPED_SECTION_LABELS` matches live file (~L4330); `build_state_ui_manifest()` skipped block lacks `groups` today — additive change matches AC 1. Grouping semantics (members before prefixes, catch-all last) match parent functional scope #1. No React/sibling creep. DRY: reuses `ERROR_STATE_PREFIX` / `BOT_BLOCKED_STATE_PREFIX`; Fail literals once. Plan-time AC 2 note (55 skipped states, Other = `INVALID_TITLE`, below-dispatch key excluded from `SKIPPED_STATES`) matches merged-tree facts.

context_tokens≈42000

Slim upshot: `[plan-rubric] PROCEED (Commit: a1d2e90ea) Config groups manifest ready`

## Review (build stub)

**Built:** `origin/sub/AST-2102/AST-2105-skipped-group-rules` @ `6913fcd98`.

**Stages delivered:**
- Stage 1: `JOBS_SKIPPED_GROUPS` registry + two import-time guard asserts after `JOBS_SKIPPED_SECTION_LABELS`; `"groups"` list on `build_state_ui_manifest()["jobs"]["skipped"]`. Code is verbatim from the plan — `6913fcd98`

**Notes:**
- Build base: AST-2073's ftr is still merged on this sub (no new commits on it since plan); `sync-child.sh` also brought in a newer `origin/dev` (`68782e475`).
- Compile + import clean. Ruff on `config.py`: 102 before, 102 after.
- AC 1 script prints `AC1 ok`; AC 2 prints `['INVALID_TITLE']`; AC 3 temporary `"NOT_A_STATE"` member raised `AssertionError: JOBS_SKIPPED_GROUPS: member is not a Skipped state`, reverted (no `NOT_A_STATE` in the diff).
