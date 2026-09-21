# Directive audits

One TSV per directive per audited commit.

```
audit-<directive-id>-<sha>.tsv
```

`<sha>` is the short hash of the **code** audited (`git rev-parse --short HEAD`).
Produced by `../docs/directive-audit-prompt.md`.

Not loaded at runtime. The clerk never reads this directory, and nothing here
appears in an index or a payload.

---

## Shape

Tab-separated. One header row. One row per file in the directive's territory.

```
file	grade	loe
src/utils/config.py	D	2
src/data/database.py	D	3
src/ui/api/api_admin.py	D	5
src/core/roster.py	A
src/core/tracker.py	A
src/utils/formatting.py	X
```

| Column | |
|---|---|
| `file` | repo-relative path. Every file in territory gets a row, pass or fail. Files outside the territory are absent, not `X` |
| `grade` | `A` `B` `C` `D` `F` `X` — defined once in `../instruction_preamble.md` |
| `loe` | `1`–`5`, the cost of correcting *this file*. Empty for `A` and `X` |

**One grade per file, worst case.** Nine clean functions and one that ignores the
directive is a `D`. Averaging hides exactly what the sweep is for.

**Grade and loe are independent.** An `F` can be loe 1 (delete one banned import);
a `C` can be loe 5 (nearly the right shape, but fixing it moves four modules).

---

## Why TSV and not a report

The interesting questions are sorts and sums — which directive has the most
`D` and `F` rows, which file appears across the most audits, what the total loe
is for one directive. A spreadsheet answers those; a prose summary answers one
of them, badly, and goes stale the moment the next sweep runs.

**Overwrite when the directive changes; new file when the code does.** The
filename keys on the code SHA, so:

- Reworded a directive and re-ran it against the same commit → **overwrite** the
  existing TSV. It always reflects the current directive against that code.
- Committed code and re-ran → **new file**, new SHA. Two commits are directly
  diffable.

That trade is deliberate. You keep the history of how the code graded over time,
which is the question worth asking, and you lose the history of how a directive
graded before it was reworded — which `../docs/CHANGELOG.md` records anyway.
