# The canon ecosystem

How written law, per-issue rubrics, and the pipeline stages fit together to drive
code quality.

> **Status.** `canon-v2/canon_clerk.py` is built and working. Everything else here
> is the agreed design — the corpus still has its old shape, the skills still run
> the old full-corpus sweep, and the migration hasn't happened. Read this as the
> target, not the current state. See [DIRECTIVES-DIRECTORY.md](DIRECTIVES-DIRECTORY.md)
> for the directive-level plan.

---

## 1. What canon is

Three kinds of directive, distinguished by what they assert.

| Kind | Asserts | Scoped by | Origin |
|---|---|---|---|
| **Statute** | one condition that must hold | construct (`variables`, `functions`, `component`) or layer (`core`, `data`, `config`) | ships as a base template, evolves per repo |
| **Pattern** | one arc — steps with ownership per step | subsystem (`entity`, `agent`, `dispatch`, `consult`) | born project-specific; no template |
| **Orchestration** | pipeline and team process | `git`, `pipeline`, `roles` | template copied per repo, amended locally |

The line between statute and pattern is **arity**. "Call `save_job_data()`, don't
roll your own" is one condition — a statute, even though it points at real code.
"Claim under a `batch_id`, process only claimed rows, release in `finally`" is a
sequence with ownership at each step — a pattern.

A fourth file kind, `term`, defines shared vocabulary (`catalog`, `coat-check`,
`hop`). Terms are cited by directives and resolved alongside them, but are never
scored.

**Naming:** `{p|s|o}.<scope>.<string-index>`, flat directory, kind in frontmatter.
Ids lead with scope so a flat listing groups usefully.

**A directive file carries** a preamble, an example scenario, and literal Do/Don't
code. Concise and detailed beats brief and vague — the corpus is small enough to
afford depth because only the relevant slice is ever loaded.

---

## 2. Who owns it

**Archie owns the canon.** Nothing is added, amended, or retired without Archie
approval recorded in frontmatter.

- **Drafts come from Chuckles or Joan only.** The party being graded does not
  write the rules.
- **Engineers file `[canon-handoff]`** — the same shape as `[qa-handoff]` for
  tests. They report the problem; they don't draft the law.
- **No canon changes in flight.** Amendments are decided at Discussion and land
  as their own tickets. A ticket that hits a wrong rule scores against it as
  written, ships, and queues the amendment.
- **Triage before escalation.** Joan and Chuckles resolve most reports; only the
  residue reaches Archie, as a properly-sourced draft.

The in-flight ban is not just hygiene. Scores cite directives by number against
text that must still mean what it meant at Plan Approved.

---

## 3. How directives reach an issue

### Canon Scope, set at Discussion

Archie, Chuckles, and Joan determine which directives govern the work. This is a
**determination, not an estimate**, and it is **locked at Discussion**.

That distinguishes it from the other three scopes the `define-` skill declares:

| Scope | Nature | Locks at |
|---|---|---|
| Component Scope | Chuckles's hipshot — "you'll likely touch `config.py` and `roster.py`" | tested during plan, settled at Plan Approved |
| Data Scope | hipshot | same |
| Test Scope | hipshot | same |
| **Canon Scope** | **determination — which law governs this work** | **Discussion. Changing it needs Archie** |

The asymmetry is deliberate, because **absence means different things**. No
`roster.py` in Component Scope means "probably won't need it." No persistence
directive in Canon Scope means *this ticket does not save anything*. One is a
guess; the other is a boundary.

So canon is **upstream** of the technical plan, not a coverage check over it. If
an agent finds herself needing to save data and no persistence directive is in
scope, the correct inference is usually not "canon is missing something" — it's
"I've misread the ticket." She asks the technical question — *what do I do with
this data if I'm not saving it?* — and Joan and Chuckles diagnose. She does not
propose law; she isn't the party who selects it.

### The rubric is the issue's directive list

The issue description enumerates the selected directives in full, numbered
locally. The enumeration is **append-only** after freeze — inserting a directive
mid-list would silently remap every score already posted.

---

## 4. How it's scored

One scale, both stages, terse output. The score line is just `slug: GRADE`,
because the directive text is already enumerated in the description.

| Grade | Meaning | Routes to |
|---|---|---|
| **A** | implemented as the directive directs | PROCEED |
| **B** | varied slightly, within the directive's scope | PROCEED |
| **C** | diverges from the directive's intention | DISCUSS |
| **D** | ignores the directive | FIX NOW |
| **F** | explicitly builds a separate path to the same result | FIX NOW |
| **X** | not applicable — outside the directive's territory | — |

**Aggregation takes the worst grade. Never average.** Eight A grades and a D is a FIX NOW, not a
B average. X is excluded from the roll-up — not applicable is not a passing grade,
and a directive graded X everywhere was mis-selected, not satisfied.

**A and B are bare; C, D, and F carry one line naming the file or decision, plus
an effort rating for the correction.** The grade carries the verdict, but location
isn't recoverable from the description, so findings pay for a line and passes don't.

The 5/4 and 2/1 splits carry no routing difference — they're *diagnostic*. A 2 is
an omission; a 1 is an architectural workaround. Those need completely different
fixes, and the old `violates` enum flattened them.

**The rubric pass is the only verification path.** Anything that checks canon
outside it is a second bridge — and a second bridge is, by this scale's own
definition, a 1.

---

## 5. Where it lands in the workflow

| Stage | Who | What canon does |
|---|---|---|
| **Discussion** | Archie / Chuckles / Joan | Canon Scope determined and locked. Amendments decided here or nowhere |
| **Define (parent)** | Chuckles | declares Component, Data, Test, and Canon Scope. First three are guesses; the envelope for children |
| **Plan (child)** | engineer | **patterns resident** — you cannot avoid rebuilding a bridge you haven't read. Plus the placement statutes, which decide where things go. Other statutes are id-only |
| **Plan validate** | Joan | scores the issue's vectors against the plan text |
| **Plan Approved** | — | **rubric freezes.** Component/Data/Test scope settle here too |
| **Build** | engineer | at the *end*, `full_text([statute ids])` — one call, late, so fat text sits in context for a few turns rather than forty. Self-correct before handoff |
| **Tests** | Betty | test tree only; not a canon consumer |
| **Review** | Radia | scores the **same vectors** against the diff |

Joan and Radia scoring one vector set is what makes the two passes comparable. A
vector Joan scored 5 and Radia scores 2 is the interesting case, and it falls out
of a column diff instead of needing a bolt-on straggler rule.

**Scope divergence is expected output, not an exception.** The plan states "you
scoped `config.py` and `roster.py`; I also need `store.py`, because X." If the
agent learns that testing the guess reads as failing it, she'll quietly stay
inside the bumpers whether or not they're right.

---

## 6. How agents get the content

`canon-v2/canon_clerk.py`. Two commands, matching the two things agents need.

```bash
python3 canon-v2/canon_clerk.py index --kind statute
python3 canon-v2/canon_clerk.py expand <id> [<id> ...]
```

**`index`** — id, kind, scope, status, and the one-line point of every directive.
Cheap enough to carry while selecting. Used by Chuckles, Joan, and Radia.

**`expand` / `full_text(ids)`** — full frontmatter and body for a curated list, as
one JSON object. Fed to the engineer in the issue thread and to Radia at review.
One call for nine directives instead of nine reads.

Two properties that matter:

- **Pinned.** Every response carries `corpus_sha` and `corpus_dirty`. A verdict
  scored against a dirty corpus isn't reproducible, and the payload says so.
- **Fails loudly.** Unknown id, retired statute, or unapproved pattern → non-zero
  exit with the id named. A stale rubric breaks visibly rather than silently
  serving less than it claims.

### Why staging matters

Context is re-sent every turn, so *when* you load is as important as *what*. The
whole corpus is ~12,100 tokens; a nine-vector selection is ~1,180. Loading the
corpus at turn 1 of a forty-turn build occupies the window for all forty.

Patterns are the exception worth paying for: bridge-recognition only works if the
bridges are in front of you while you design. Statutes are a terminal check, so
they arrive at the end.

> **Caveat.** `build-child`'s resume-spawn path inherits plan context, but its
> queue mode enters cold. The instruction must be *if the pattern bodies aren't
> already in context, load them* — not an assumption that they are.

---

## 7. The rules that keep it from rotting

Every failure this system has had was drift between an authority and its
executor, not a gap in expressiveness.

**One authority. Skills cite; they never restate.** The Plan Discuss cap is
currently hardcoded in eight places across five files in two repos — a single
integer, and changing it means finding all eight. That is the disease in
miniature, and it violates `stat.general.registry-not-literals` by the governance
layer that enforces it.

**The index is generated, never hand-maintained.** A hand-written registry
disagrees with the corpus, and consumers trust the registry.

**Slug uniqueness across the live set is a CI check.** Scoring on bare slugs
depends on it, and domain renames manufacture collisions by design.

**Directives that can't take a code example are misfiled.** The Do/Don't
requirement is a classifier, not a style rule: if the violating instance renders
identically to the conforming one, it isn't a statute — it's orchestration in the
wrong namespace.

**Shared vocabulary lives in one `term`, not in every preamble that uses it.**
`catalog` currently appears in seven directives and is defined in none.

---

## 8. Related documents

- [DIRECTIVES-DIRECTORY.md](DIRECTIVES-DIRECTORY.md) — the directive-level target:
  scopes, every pattern and statute, migration coverage, and the `config.py`
  decomposition
- [HARVEST-statutes.md](HARVEST-statutes.md), [HARVEST-patterns.md](HARVEST-patterns.md)
  — the 2026-07 migration registers, kept for the deliberate *non*-decisions they
  record
