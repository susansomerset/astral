# Canon audit — single file

Thin by design. The payload carries its own usage instructions, including the
universal grade scale, so this prompt only says what to do with them.

---

Audit **`<FILE>`** against the canon directives in the payload.

## 1. Get the directives

From the repo root:

```bash
python3 canon-v2/canon_clerk.py expand stat.layers.import-rules stat.variables.named-constants stat.functions.clear-names stat.functions.dont-repeat-yourself stat.component.public-then-helpers stat.errors.raise-once-log-once patt.entity.batch-processing patt.layers.import-discipline
```

Read the `usage` field first — it tells you how to read everything else, and it
carries the grade scale. The scale is universal: it measures compliance with
whatever the directive's `# Statement` or `# Arc` says. Directives do not carry
their own bands.

**The payload is the complete set.** Do not read `canon/` (the v1 corpus), do not
consult `docs/ASTRAL_CODE_RULES.md`, and do not apply rules you know from
elsewhere. A rule not in the payload does not apply to this audit.

## 2. Read the file

Read `<FILE>` in full before scoring anything. Do not sample or grep it.

## 3. Decide territory before scoring

For each directive, first say whether the file is in its territory:

- **Statute** — does this file contain the kind of code the rule governs?
- **Pattern** — does this file participate in the arc at all?

If it is not in territory, grade it **X** with one line of why. This is a real
answer, not an evasion: a file that never claims a batch is outside
`patt.entity.batch-processing`, not failing it.

## 4. Grade what is in territory

Use the universal scale from `usage`, applied to this directive's rule.

- **Finding (C, D, or F)** — one line: `path:line — what the code does`, plus an
  effort rating (below) for what correcting it would cost.
- **Pass (A or B)** — the bare grade, no commentary.
- If the directive has a `# Resolution` section and you graded C or below, name
  the Resolution step that would fix it.

### Effort rating

Every finding carries one, from the `## Effort` table in `usage`. It scores the
**correction**, not the violation, and is independent of the grade.

## 5. Report

```
# Audit: <FILE>
corpus_sha: <copy from the payload>

stat.layers.import-rules              D/2  src/utils/config.py:5868 — utils imports core.candidate
                                        Resolution step 1: this is a formatter, it belongs in utils
stat.variables.named-constants        A
stat.functions.clear-names            B
stat.component.public-then-helpers    C/4  src/core/x.py:210 — public fn below the helper block
patt.entity.batch-processing          X    file never claims or releases a batch

Overall: FIX NOW   (worst in-territory grade is D)

## Could not determine
- <anything you could not settle from the file alone>
```

Findings are written `GRADE/EFFORT`. Passes are the bare grade. X carries no
effort — there is nothing to correct.

**Worst grade wins. Never average.** One D among six A grades is FIX NOW.
`A/B PROCEED · C DISCUSS · D/F FIX NOW`. X is excluded from the roll-up.

## 6. Do not fix anything

This is an audit. Report findings; change no code.

---

## Suggested targets

| File | Why |
|---|---|
| `src/core/dispatcher.py` | 1,376 lines. Contains the batch `try/finally` in `_run_unified`, so `patt.entity.batch-processing` is genuinely in territory. Also has a known asymmetry — the early-exit release at ~line 563 covers job and candidate but not company |
| `src/core/tracker.py` | 864 lines. Smaller. `get_new_job_batch` / `clear_job_batch`, plus the artifact family |
| `src/utils/config.py` | Has the known `utils → core` violations at 5868 and 5912 — good for testing whether the audit finds a real one, but 5,790 lines is a lot to read |
