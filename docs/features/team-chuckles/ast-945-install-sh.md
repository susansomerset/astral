# AST-945 — install.sh (Skill doc consistency pass)

- **Linear:** [AST-945](https://linear.app/astralcareermatch/issue/AST-945/installsh-skill-doc-consistency-pass-pipeline-shakedown)
- **Parent:** [AST-909](https://linear.app/astralcareermatch/issue/AST-909/skill-doc-consistency-pass-pipeline-shakedown)
- **Publish ref:** `origin/sub/AST-909/AST-945-install-sh`
- **Summary:** Change `~/team-chuckles/install.sh` so it no longer installs/copies the **merge-parent** skill into `~/.cursor/skills`; **finish-up** continues to install via the normal skills loop. Also remove a stale `~/.cursor/skills/merge-parent` link on install so hosts stop discovering the deprecated skill. Docs/install-script only; sequenced with AST-944 (#15 delete skill).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `~/team-chuckles/install.sh` | Skip `merge-parent` in the skills symlink loop; remove stale `~/.cursor/skills/merge-parent` if present | install script |
| `docs/features/team-chuckles/ast-945-install-sh.md` | This plan (on publish ref) | docs |

**Exempt:** deleting `skills/merge-parent/` (AST-944), other skills’ content, astral law docs, product `src/` / `tests/`.

**Commit home:** `install.sh` change in **`team-chuckles`**. Plan doc only on this astral **`sub/*`** ref.

## Stage 1: Binding install behavior

**Done when:** A fresh `./install.sh` leaves no `~/.cursor/skills/merge-parent` and still installs `finish-up`.

1. In `~/team-chuckles/install.sh`, inside the `for skill in "$REPO/skills"/*` loop (after `name="$(basename "$skill")"`), **skip** when `name` is `merge-parent`:

```bash
  # Deprecated: finish-up is the sole Chuckles parent-close skill (AST-909 / AST-945).
  if [[ "$name" == "merge-parent" ]]; then
    continue
  fi
```

2. **After** the skills loop (before or after AGENTS.md seeding), **remove stale destination** if it still exists from older installs:

```bash
# Drop deprecated merge-parent skill link left by prior installs.
if [[ -e "$CURSOR/skills/merge-parent" || -L "$CURSOR/skills/merge-parent" ]]; then
  rm -rf "$CURSOR/skills/merge-parent"
fi
```

3. Do **not** add a special-case install for `finish-up` — it already installs via the generic loop (`skills/finish-up` exists).
4. Do **not** delete `skills/merge-parent/` in this ticket (AST-944). Skipping + stale-link removal must work whether that directory still exists or not (sequencing “with #15”).

⚠️ **Decision:** Explicit skip + stale removal (not “rely on AST-944 delete alone”) so `install.sh` is correct on either order of landing with AST-944.

## Stage 2: Verify and commit

**Done when:** Grep/read of `install.sh` shows no path that creates `merge-parent` under `~/.cursor/skills`, and finish-up is still covered by the loop.

1. Apply Stage 1.
2. Confirm by inspection:
   - No `ln`/`cp` targets `merge-parent` except the skip/remove paths.
   - `finish-up` remains a normal skill directory install.
3. Optional local check (same host, non-destructive intent): run `./install.sh`, then `test ! -e ~/.cursor/skills/merge-parent` and `test -L ~/.cursor/skills/finish-up` (or equivalent). Do not push `origin/dev`.
4. Commit in **`team-chuckles`**: `code(AST-945): stop installing merge-parent skill`.
5. Code Complete note: hosts must re-run `./install.sh` for the skip/stale-remove to take effect.

## Execution contract

- This ticket only — do not delete the merge-parent skill tree (AST-944) or rewrite finish-up.
- No Astral product behavior change.
- If install.sh structure has drifted from the loop-at-lines-27–35 shape assumed here, stop and comment on **AST-909**.

## Self-Assessment

**Scope:** `minor` — one bash install script plus this plan doc.

**Conf:** `high` — current `install.sh` blindly symlinks every `skills/*` including `merge-parent`; to-be is skip + stale remove; finish-up already present.

**Risk:** `low` — install wiring only; worst case a host keeps an old symlink until re-install (Stage 1 step 2 addresses that).

## Self-review vs ASTRAL_CODE_RULES

- §1.1 in-scope only — satisfied.
- Plan under `docs/features/team-chuckles/` — satisfied.
- Aligns host skill install with finish-up as sole Chuckles parent-close skill.
