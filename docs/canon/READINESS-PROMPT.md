# Canon readiness analysis — subagent prompt

One stateless Sonnet agent per directive. Triage first (§1), then run agents only
for the directives that a sweep can actually answer (§2).

---

## 1. Triage before spawning anything

Directives split three ways, and only the middle group needs an agent.

| Class | Test | Handling |
|---|---|---|
| **Forward-only** | applies to all 47k lines with no bounded search — `functions.dont-repeat-yourself`, `functions.helper-functions`, `component.comment-hygiene`, `variables.local-if-one-off`, `functions.clear-names` | **No agent.** Enforce on new and changed code only. A sweep produces an unbounded, unreliable list and burns context proving it |
| **Bounded** | a mechanical search answers it — `s.config.single-home`, `s.data.partial-update-allowlist`, `s.ui.require-auth`, `s.general.import-rules` | **One agent each.** This is what the prompt below is for |
| **Already measured** | this session already counted it — `p.config.task-config` (47/52/44), `s.config.derive-dont-restate` (2 literal state sets), `s.data.no-mirror-columns` (`agent_responses_legacy`) | **No agent.** Carry the number forward |

**The drafting report already did some of this triage.** `REVIEW-INDEX.md`
(DIRECTIVE-ANATOMY §7) carries a `violations:` and `conforming_instance:` field per
directive, produced while drafting. A directive that already has violations listed
is **bounded** — the search is known to terminate. One with `conforming_instance:
none found` and no violations is either new or **forward-only**. Read the review
index before sorting by hand.

Sorting the corpus this way is a ten-minute judgement, not thirty agent runs.
Roughly a third of the construct statutes are forward-only, and forcing an agent
to "find all DRY violations" is how you get a 200-item list nobody trusts.

**Why not a directive × folder matrix:** 30 directives × 7 folders is 210 cells,
and `applies_when` already says most are empty — `s.ui.naming-conventions` against
`src/data/` is not a question. The scoping metadata makes the matrix redundant;
put the folder scope *inside* each agent's prompt instead.

---

## 2. The prompt

Substitute `{{DIRECTIVE_ID}}` and `{{SEARCH_SCOPE}}`. One agent per directive,
run in parallel, no shared state.

---

You are assessing whether **one** canon directive can be enforced against this
codebase today, or whether enforcing it would halt work until a remediation
ticket lands.

**You are not fixing anything.** Do not edit files, propose refactors, or suggest
better designs. Your only job is to count what exists and size the gap.

### The directive

```bash
python3 canon/canon_clerk.py expand {{DIRECTIVE_ID}}
```

Read the statement, rationale, and examples. If the directive names specific
functions, paths, or constants, those are your search anchors.

### Where to look

`{{SEARCH_SCOPE}}`

Do not search outside that scope. It was set from the directive's
`applies_when`; widening it wastes the run and produces findings that will be
discarded.

Repo shape, so you don't re-derive it:

```
src/core/       21 files   business orchestration; decides state, never does I/O
src/data/        5 files   SQL surface; database.py is 7,989 lines
src/external/    9 files   all I/O — HTTP, DOM, vendor SDKs
src/utils/      13 files   config.py (5,790 lines), logging, formatting
src/ui/api/     17 files   Python API layer
src/ui/frontend           94 .tsx + 34 .ts
scripts/        36 files   one-off ops; exempt from layer rules
```

`src/utils/config.py` needs `ASTRAL_DB_DIR` set and Python 3.10+ to import.
Prefer static analysis (`ast`, grep) over importing it.

### What counts as a violation

A concrete instance where current code does the thing the directive forbids, or
omits the thing it requires. Cite `file:line`.

Do **not** count: code that merely resembles a violation, cases where you are
unsure of intent, or anything in `scripts/` when the directive is layer-scoped.
Put those under `arguable` instead — a false positive poisons the roadmap worse
than a missed one, because someone will schedule work against it.

### The readiness bar

> A directive is **READY** if enforcing it today would require touching **2 or
> fewer files**, with no significant restructuring of any single file.

"Significant restructuring" means moving or rewriting a substantial block, not a
one-line change. Splitting a function, relocating a constant across modules, or
changing a signature with callers all count as significant.

### Output — exactly this, nothing else

```
DIRECTIVE: <id>
VERDICT: READY | REMEDIATE | BLOCKED

VIOLATIONS: <n>
FILES_TOUCHED: <n>
LARGEST_SINGLE_FILE_CHANGE: trivial | moderate | significant

INSTANCES:
  <file:line> — <what is wrong, one line>
  ...   (cap at 20; if more, say "+N more" and give the count)

ARGUABLE: <n>
  <file:line> — <why it is unclear, one line>
  ...

REMEDIATION_SHAPE: <2-3 sentences: what the fix pass would do. No code.>

BLOCKERS: <anything preventing enforcement even after remediation — a
           dependency on an unbuilt refactor, an unresolved Archie decision,
           or a coupling that cannot be fixed in isolation. "none" if none.>
```

`VERDICT` rules, applied mechanically:

- **READY** — 0 violations, or ≤2 files and no significant single-file change
- **REMEDIATE** — violations exist and are bounded; a fix ticket would close them
- **BLOCKED** — cannot be enforced until something else happens first (name it in
  `BLOCKERS`)

### Notes

- Report honestly. Zero violations is a good outcome, not a failed run.
- If the directive is ambiguous against real code, say so in `ARGUABLE` rather
  than guessing — that ambiguity is itself a finding about the directive.
- Do not read the other directives. One rule, one run.

---

## 3. Collation

Each run returns a fixed block, so the roadmap is a sort:

1. **READY** — enforce immediately
2. **REMEDIATE**, ordered by `FILES_TOUCHED` ascending — cheapest first
3. **BLOCKED** — sequence behind whatever they name
4. **Forward-only** (from §1) — enforce on changed code, never swept

The `BLOCKERS` field is the one that matters most for ordering. Expect
`s.config.single-home` and anything touching the token engine to name the
`config` ↔ `formatting` cycle, which has to be broken first.
