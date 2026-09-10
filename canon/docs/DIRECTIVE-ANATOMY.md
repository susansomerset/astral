# Directive anatomy

The file shape for every kind of canon directive. A drafting session reads this
plus [DIRECTIVES-DIRECTORY.md](DIRECTIVES-DIRECTORY.md) and produces files that match
each other.

Supersedes `canon/statutes/SCHEMA.md` and `canon/patterns/SCHEMA.md`, which
describe the old shape.

---

## 1. Frontmatter — all kinds

```yaml
---
id: stat.config.single-home          # matches the filename stem
kind: statute                     # statute | pattern | term | orchestration
scope: config                     # the leading segment of the id
point: >                          # ONE sentence, ten words or less. This is what the index shows.
  Configuration lives in config.py and nowhere else.
terms: ["<glossary_key>"...]                     # terms found in the glossary file used here.
code_refs: ["<component>.<function>"...]		      # code references made that may cause drift if code changes without revising this document.
---
```

`point` **is load-bearing.** The generated index carries `id` + `point`, and that
index is what Chuckles, Joan, and Archie read when selecting Canon Scope. A vague
`point` makes a directive unselectable. Write the rule, not the topic: "no secret
in config.py, read from environ and crash if missing" — not "secrets handling."

**There is no `status` field.** Status is determined by the directory a file lives in. A
directive under `.../directives/active/` is in force; a draft lives in `.../directives/draft/`
and an archived one in `.../directives/archive/`. Activating or retiring a directive
is a `git mv` in its own commit, which is a record a human can read without
opening 80 files.

### Additional fields by kind


| Kind            | Extra fields                                                                                            |
| --------------- | ------------------------------------------------------------------------------------------------------- |
| `statute`       | `applies_when: {layers, paths, change_types}` — informs Canon Scope selection and lets the clerk filter |
| `pattern`       | `related_statutes: [ids]` — the constraints this arc must stay inside. **Cite, never restate**          |
| `term`          | none                                                                                                    |
| `orchestration` | `applies_when`, plus `source_template` / `amended: true|false` for template provenance                  |


---



## 2. Statute

Asserts **one condition that must hold**. Sections in this order.

```markdown
# Abstract
Why this rule exists and the shape of the failure it prevents. Two or three
sentences. This is the retrieval body — an agent scanning for relevance reads
this, so lead with the situation, not the history.

# Statement
The rule, normatively, in one or two sentences. No hedging, no rationale.

# Scenario
The concrete moment this fires — a plausible thing an engineer is about to do
and why it looks reasonable. Use the real codebase where possible: naming the
file where this already went wrong beats inventing an example.

# Do
​```python
# literal, runnable-looking code showing the conforming shape
​```

# Don't
​```python
# literal code showing the violation, with a comment marking what is wrong
​```

# Resolution      (optional)
What to do when complying looks impossible. Ordered steps, **every one of which
is fully compliant.** This is not a way around the rule, it is the way through
it. Omit the section entirely rather than inventing steps for a rule that has no
hard case.

# Notes            (optional, non-normative)
```

**There is no `# Exception` section, deliberately.** What happens when Resolution
yields nothing is identical for every directive — escalate at the plan stage to
discuss the parent ticket's scopes — so it lives once in the clerk's `USAGE`
preamble, prepended to every expansion. Thirty copies of one process rule is the
drift this corpus exists to prevent. `# Resolution` stays per-file because its
steps are rule-specific; the escalation is not.

**Worked example:** [DIRECTIVES-DIRECTORY.md §12](DIRECTIVES-DIRECTORY.md) —
`stat.config.single-home`.

**The Do/Don't is a classifier, not decoration.** If you cannot write literal code
where the violating version looks *different* from the conforming one, this is not
a statute — it's either a pattern or orchestration, and it's in the wrong namespace. Stop and reclassify.

**Directives carry no `# Scoring` section.** The grade scale is universal and
lives once, in the clerk's `USAGE` preamble: **A** as directed, **B** slight
variance within scope, **C** substantially diverges, **D** ignores it, **F** builds a separate
path around it, **X** not applicable. Per-directive bands would break the roll-up
— aggregating grades only means something if a D means the same thing in every
file — and forty hand-written bands drift the way any forty copies do. Say what
the rule *is* in `# Statement`; the scale measures compliance with it.

`{A,B,C,D,F,X}` is deliberate: it is the same grade set the product already uses
for agent output (`GRADE_VALUES`, `astral.agent.grade-vector-validation`), so
there is one grading vocabulary in the system rather than two.

---

## 3. Pattern

Asserts **one arc** — steps with ownership at each step. Pointer-first: the value
is the canonical implementation, not a re-description of the rules.

```markdown
# Abstract
The recurring situation this arc exists for. What goes wrong without it.

# Arc
The steps, in order, with the owner of each. Prose or a numbered list, not code.

1. Core decides the target state from the registry
2. Tracker validates `prior_states` and raises if the transition is illegal
3. Data writes the row, choosing nothing

# Canonical implementation
Details of how the directive must be implemented, may or may not reference existing code.

# Technical Dependencies            (only when one exists)
What else must move when this changes, written **for the scorer**: what to
compare, and what a mismatch means. Not a script — the rubric pass is the check.

# When this doesn't apply
Genuine anti-triggers — situations where you should reach for something else.
**Not** a list of violations; a violation is a low score, not an anti-trigger.

# Notes            (optional)
```

`# When this doesn't apply` **is the section most often written wrong.** The old
template's version was a violation list wearing the wrong hat. If a bullet reads
"someone hardcodes the next state," that is a D, not an anti-trigger.

---


## 4. Glossary Term

Defines shared vocabulary. **Terms are resolvable but never scored** — they ride
along in the expansion so the directives citing them make sense.

```markdown
# Definition
One paragraph. What the word means here, specifically enough that two engineers
would agree on whether something is one.

# In practice
Where it shows up in the codebase, with refs.

# Not to be confused with            (optional)
The near-miss that causes the confusion.
```

No `# Do` / `# Don't`. A term is not a rule and is never scored.

First terms to write, by how many directives use them undefined today:
`catalog` (7 directives), `carve-out` (4), `hop` (3), `CLICK` (3),
`coat-check` (2), `debug contract` (2).

---



## 5. Orchestration

UNLIKE Patterns and Statutes, the Orchestration directives are NEVER mentioned in Linear tickets or the codebase.  They are explicit instructions referenced by the team-chuckles SKILLS how to perform orchestration work for this project.  Their existence here allows for project-specific tailoring of orchestration of the codebase, without forcing a universal approach to every project using team-chuckles.  

```markdown
# Abstract
# Statement
# Scenario

# Conforming
​```bash
git merge origin/ftr/AST-912-systemic-statutes
​```

# Violating
​```bash
git merge origin/tests      # tests never merges into dev
​```

# Notes            (optional)
```

For the judgment-shaped ones — `plan-is-bible`, `call-susan-for-product-decisions`
— replace `# Conforming` / `# Violating` with:

```markdown
# Decision procedure
When you notice <X>: do <Y>. Do not <Z>.
```

Those rules fire at a moment of judgement, and what an agent needs is the action
at that moment, not an example that narrows the rule to one instance.

---



## 6. Rules for the drafting session

1. **One directive per file.** Filename is the `<orch|stat|patt>.<scope>.<directive-name>.md`.
2. **Never invent a scope.** Use the scopes in DIRECTIVES-DIRECTORY §1. A value that
  fits none of them means the directive is misfiled, not that a scope is missing.
3. **NEVER restate another directive.** If it is critical content for the directive, cite the id. Duplication across files is the failure this whole corpus exists to prevent.
4. **Ground every example in this codebase — but do not take the codebase as the
  "Do" standard.** Real file, real function, real constant, so examples stay legible
  and locatable. The rule itself comes from best practice and the brief; `src/`
  is context, not authority. **State the rule first, then search the codebase for
  instances of both sides.** The `# Do` shows the correct shape whether or not any
  current code achieves it. The `# Don't` may cite real code directly — a real
  violation teaches better than an invented one.
5. **If a statute resists literal Do/Don't code, stop.** It's misfiled. Flag it
  rather than writing a vague example.
6. **Glossary Terms before directives.** Define `dispatch task` before drafting the seven
  directives that use it, or you will write seven definitions.
7. **Record the entry on each file to the index the moment you finish it.** See §7. Append to
  `REVIEW-INDEX.md` before starting the next directive — never at the end.

---

## 7. The drafting report

Every directive gets one entry in `canon-v2/docs/REVIEW-INDEX.md`, **appended the
moment that directive is finished and before the next one is started.** Not
batched at the end.

Two reasons, and the second matters more. A long run that dies — context
exhausted, session interrupted — otherwise loses every judgement made before it
died, and leaves no resume point. And grading forty-nine files from memory at the
end smooths them: by file 40 you will not remember what worried you about file
12. The doubt is only accurate while it is fresh.

This report is **not** frontmatter. It describes the drafting, not the rule, and
it would go stale the first time the directive is amended. It is disposable once
Archie has reviewed it.

### Four axes for the index

Score 1–5. Each also takes one sentence answering its question — and the question
is the substance; the number is only a summary. "No concerns" answers *any
concerns?* It does not answer any of these.

| Axis | The question |
|---|---|
| **Confidence** | Where did this rule come from — the brief, standard practice, or my judgement? |
| **Detail** | What did I leave out and why, and what is in here a reader could skip? |
| **Clarity** | Which sentence would a new engineer most likely misread? |
| **Scope** | Is this stated at the right generality, or did I overfit to what I happened to find? |

Only report what nobody else can check. Whether the directive is *accurate* is
not on this list: `canon_clerk.py verify` checks the refs, and Archie checks the
judgement. Confidence — how sure you are, and on what basis — is the thing only
you know.

### Confidence bands

| | |
|---|---|
| 5 | the brief specified this directly, and it is also standard practice |
| 4 | standard practice; the brief implied it and I filled in the specifics |
| 3 | a judgement call between defensible alternatives |
| 2 | extrapolated from a related directive; the brief did not cover it |
| 1 | invented because the scope seemed to need it |

**Min-wins, never averaged.** Any axis at 3 or below means the file does not reach
Archie until someone has looked at it. This scale grades *draft against brief* —
it is not the 1–5 that grades *code against directive*, and the two must not be
conflated in one thread.

### Two evidence fields

Facts, not grades:

- `conforming_instance:` — path + symbol of real code that already does this
  correctly, or `none found`. A found-and-judged instance is a good
  `canonical_ref`; the nearest thing that happens to exist is not. **`none found`
  is a real answer** — it means either the directive is genuinely new, or it is
  unimplementable as written, and Archie needs to tell those apart.
- `violations:` — path + line of code that contradicts this directive. Searching
  for the `# Don't` example produces this list for free, so there is no separate
  pass. A violation is a finding, not an obstacle: state the rule correctly and
  let the code be wrong.

### REVIEW-INDEX Entry shape

```markdown
## stat.data.partial-update-allowlist
confidence: 3 — standard practice, but the brief didn't name a return contract; I chose rowcount.
detail:     4 — left out the JSON-serialisation behaviour; it belongs in patt.data.entity-definition.
clarity:    4 — "allowlist enforced" may read as caller-side validation. Reworded to name the layer.
scope:      3 — stated for all entities from two examples. Did not sweep every update_*.
conforming_instance: src/data/database.py :: update_company
violations: src/data/database.py :: update_dispatch_task — returns None, not rowcount
```



