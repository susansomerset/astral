# Directive audit — subagent prompt

One stateless agent per directive. Triage first (§1), then run agents only for
the directives a sweep can actually answer (§2). Each run writes one TSV.

---

## 1. Triage before spawning anything

Directives split four ways, and three of the four still resolve to a bounded
or no-agent run.

| Class | Test | Handling |
|---|---|---|
| **Forward-only** | applies to all 47k lines with no bounded search — `functions.dont-repeat-yourself`, `functions.helper-functions`, `component.comment-hygiene`, `variables.local-if-one-off`, `functions.clear-names` | **No agent.** Enforce on new and changed code only. A sweep produces an unbounded, unreliable list and burns context proving it |
| **Bounded** | a mechanical search answers it — `stat.config.single-home`, `stat.data.partial-update-allowlist`, `stat.ui.require-auth`, `stat.layers.import-rules` | **One agent each.** This is what the prompt below is for |
| **Pattern-shaped** | `kind: pattern`, and the point describes an interaction across files — a lock, a shared queue, a handshake — rather than a local shape. `patt.entity.batch-processing` is the reference case | **One agent, whole codebase, no {{SEARCH_SCOPE}}.** The failure mode is silence: code that should use the mechanism and doesn't will not share any of its vocabulary, so a scoped search only ever finds the positive instances and misses the case the sweep exists for. See §2's pattern override |
| **Already measured** | this session already counted it — `patt.config.task-config` (47/52/44), `stat.config.derive-dont-restate` (2 literal state sets), `stat.data.no-mirror-columns` (`agent_responses_legacy`) | **No agent.** Carry the number forward |

**A prior audit already did some of this triage.** If
`../audit/audit-<directive-id>-*.tsv` exists, the directive is **bounded** — the
search is known to terminate, and the old TSV tells you roughly where. A
directive with no TSV and no bounded search is **forward-only**.

Sorting the corpus this way is a ten-minute judgement, not thirty agent runs.
Roughly a third of the construct statutes are forward-only, and forcing an agent
to "find all DRY violations" is how you get a 200-item list nobody trusts.

**Why not a directive × folder matrix:** 30 directives × 7 folders is 210 cells,
and `applies_when` already says most are empty — `stat.ui.naming-conventions` against
`src/data/` is not a question. The scoping metadata makes the matrix redundant;
put the folder scope *inside* each agent's prompt instead.

---

## 2. The prompt

Substitute `{{DIRECTIVE_ID}}` and `{{SEARCH_SCOPE}}`. One agent per directive,
run in parallel, no shared state.

---

You are auditing this codebase against **one** canon directive, and writing one
row per relevant file.

**You are not fixing anything.** Do not edit files, propose refactors, or suggest
better designs. Grade what exists and estimate what correcting it would cost.

### The directive

```bash
python3 canon/canon_clerk.py expand {{DIRECTIVE_ID}}
```

Read the statement, rationale, and examples. If the directive names specific
functions, paths, or constants, those are your search anchors.

### Where to look

The audit's universe, for every directive and every run, is **git-tracked
files under `src/`** — nothing outside `src/` is ever in scope. `scripts/`
(one-off ops, builds, deploys), `canon/` itself, and anything else outside
`src/` are permanently excluded from audits, for every directive kind, not
only layer-scoped ones: directives are enforced on that code when it's
written or touched, not swept retroactively as tech debt. This is a fixed
outer boundary, not a per-directive judgment call.

`{{SEARCH_SCOPE}}`

Do not search outside that scope. It was set from the directive's
`applies_when`; widening it wastes the run and produces findings that will be
discarded.

**Exception — pattern-shaped directives (§1):** ignore `{{SEARCH_SCOPE}}`.
Scope is every git-tracked file under `src/` — full stop. Beyond the `src/`
boundary above, apply no further inclusion or exclusion logic of any kind:
no filtering by file type, by whether a file "looks relevant," by keyword
grep, or by subtree (frontend included). A directive like
`patt.entity.batch-processing` is not asking "does this known file do the
thing correctly" — it's asking "does anything, anywhere, need to be doing
this and isn't." That question has no bounded search, by construction: a
missing lock, a missing release, a hand-rolled queue-drain loop reads as
ordinary code and won't contain any of the directive's vocabulary for a
scoped grep to catch — which is exactly why grep-based triage cannot be used
to shrink this list before reading it.

Work this adversarially, and mean it. You did not write this code and you
cannot vouch for whoever did — read every file as if it came from a roommate
who might have been high the whole time he wrote it: well-meaning, loosely
aware of the pattern at best, and willing to cut whichever corner he thought
nobody would ever check. You are not confirming the code is fine. You are
hunting for the corner he cut, on the assumption that it exists somewhere in
this codebase right now, in a file that doesn't look like it belongs in this
audit at all — until you have actually looked hard enough to say why not.

Raise the stakes to match: a second, harsher auditor reviews your TSV after
you file it, and that auditor is grading *your audit*, not just the code. If
they turn up a violation you missed — especially one sitting in a file that
never shared a word of vocabulary with this directive — that miss is on you,
not on the code. An all-`A` TSV is not the safe answer here; it's the answer
that gets your work re-opened and your judgment questioned. The only way
through this clean is to have already found whatever they would have found.
Don't extend good faith or competence by default — make every file prove it's
fine rather than assuming it is because it looks unremarkable. "This looks
like ordinary code" is not evidence of compliance; it is exactly what a faux
pattern looks like before you check.

Repo shape, so you don't re-derive it:

```
src/core/       21 files   business orchestration; decides state, never does I/O
src/data/        5 files   SQL surface; database.py is 7,989 lines
src/external/    9 files   all I/O — HTTP, DOM, vendor SDKs
src/utils/      13 files   config.py (5,790 lines), logging, formatting
src/ui/api/     17 files   Python API layer
src/ui/frontend           94 .tsx + 34 .ts
scripts/        36 files   one-off ops — OUT OF SCOPE, not under src/, never audited
```

`src/utils/config.py` needs `ASTRAL_DB_DIR` set and Python 3.10+ to import.
Prefer static analysis (`ast`, grep) over importing it.

### What counts as a violation

A concrete instance where current code does the thing the directive forbids, or
omits the thing it requires. Cite `file:line`.

Do **not** count: code that merely resembles a violation, or cases where you
are unsure of intent. Put those under `arguable` instead — a false positive
poisons the roadmap worse than a missed one, because someone will schedule
work against it. (`scripts/` never enters this judgment at all — it's outside
the audit's territory per "Where to look" above, not a case to weigh file by
file.)

**For pattern-shaped directives, grade in both directions:**

- **Positive instances** — code already using the pattern's own mechanism —
  are graded against the directive's arc/shape like any other file.
- **Negative instances** — a faux pattern: something that needed the
  mechanism and quietly built its own path instead — are findings in their
  own right, and the more dangerous kind, because nothing about them fails
  loudly. Grade these `F` (a separate path was built around the requirement,
  not a variant of it), cite the file and the loop or write path in question,
  and give the effort estimate for retrofitting the real mechanism onto it.

Telling a negative instance apart from ordinary code that simply doesn't need
the pattern is a judgment call, not a string match — this is the "deeper
thinking than pattern-match" §1 flags patterns as requiring. Take the time
per file rather than skimming for the directive's own vocabulary; that
vocabulary is precisely what will be absent from the case you're looking for.

### Output — one TSV, nothing else

Write `canon/audit/audit-{{DIRECTIVE_ID}}-<SHA>.tsv`, where `<SHA>` is the
short commit hash of the code you audited (`git rev-parse --short HEAD`).

Tab-separated, one header row, then **one row per relevant file**:

```
file	grade	loe
src/utils/config.py	D	2
src/data/database.py	D	3
src/ui/api/api_admin.py	D	5
src/core/roster.py	A
src/core/tracker.py	A
src/utils/formatting.py	X
```

**`file`** — repo-relative path. Every file in the directive's territory gets a
row, whether it passes or not. Files outside the territory are simply absent.

**`grade`** — from the clerk's `instruction_preamble.md`: `A` as directed, `B`
slight variance within scope, `C` diverges, `D` ignores it, `F` builds a separate
path around it, `X` looked relevant but on inspection the directive does not
govern this file.

**One grade per file, worst case — never an average.** A file with nine clean
functions and one that ignores the directive is a `D`. Averaging hides the thing
you are looking for.

**`loe`** — the 1–5 effort estimate from the preamble, scoring the **correction**
of that file, not the severity of the violation:

```
1  mechanical — a single, safe global search/replace, or a very small code change
2  local edit inside one function; no signature change
3  changes a signature or its call sites; a handful of files
4  refactor the function
5  refactor the platform — multiple functions and files in scope
```

Grade and effort are independent — don't infer one from the other. Leave `loe`
empty for `A` and `X`: there is nothing to correct. `B` carries an loe only if
the variance is worth closing.

No verdict, no counts, no totals, no prose. The TSV is the whole deliverable —
sorting and summing are the reader's job, and a spreadsheet does them better
than a paragraph.

### After the TSV — file a change request only if the same problem recurs

If you graded the same way for the same reason across **multiple files**, the
directive may be the problem rather than the code. Append a request to
`CHANGELOG.md` § Requested, in the shape given there.

The bar is recurrence. One awkward file is a `C` and nothing more. What earns a
request is a pattern: wording that is ambiguous, over-broad, or unenforceable in
a way that made you decide the same question repeatedly — because a plan-stage
check and a code review will hit that same ambiguity every run, and each will
resolve it differently.

**State the problem, cite the evidence, stop.** Do not propose replacement
wording. Drafting is Chuckles' and Joan's, and Archie approves; an audit that
arrives with a patch has skipped both gates. Your evidence is the row count and
the file list — that is the part nobody else has.

No recurring problem means no request. A clean run files nothing.

### Notes

- Report honestly. A TSV of all `A` grades is a good outcome, not a failed run.
- If the directive is genuinely ambiguous against a file, grade it `C`. An
  ambiguity you cannot settle is a finding about the directive, not a pass.
- Do not read the other directives. One rule, one run.

---

## 3. Collation

Nothing to collate by hand. One TSV per directive per SHA, all in
`canon/audit/`, so the corpus-wide view is `cat`, a sort, or a spreadsheet.

Forward-only directives (§1) produce no TSV. They are enforced on changed code
and never swept.

The `BLOCKERS` field is the one that matters most for ordering. Expect
`stat.config.single-home` and anything touching the token engine to name the
`config` ↔ `formatting` cycle, which has to be broken first.
