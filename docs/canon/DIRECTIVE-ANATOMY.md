# Directive anatomy

The file shape for every kind of canon directive. A drafting session reads this
plus [PROPOSED-TAXONOMY.md](PROPOSED-TAXONOMY.md) and produces files that match
each other.

Supersedes `canon/statutes/SCHEMA.md` and `canon/patterns/SCHEMA.md`, which
describe the old shape.

---

## 1. Frontmatter — all kinds

```yaml
---
id: s.config.single-home          # matches the filename stem
kind: statute                     # statute | pattern | term | orchestration
scope: config                     # the leading segment of the id
point: >                          # ONE sentence, ten words or less. This is what the index shows.
  Configuration lives in config.py and nowhere else.
status: active                    # active | retired. There is no `proposed`.
approved_by: Archie
approved_at: "2026-08-13"
supersedes: null
superseded_by: null
terms: []                         # term ids this directive uses
canonical_refs:                   # real code this points at; [] if none
  - path: src/utils/config.py
    symbol: EXTERNAL_CONFIG
---
```

`point` **is load-bearing.** The generated index carries `id` + `point`, and that
index is what Chuckles, Joan, and Archie read when selecting Canon Scope. A vague
`point` makes a directive unselectable. Write the rule, not the topic: "no secret
in config.py, read from environ and crash if missing" — not "secrets handling."

`status` **has two values.** `proposed` is gone; a draft lives on a branch or in
Linear until Archie approves it.

`canonical_refs` **is available to every kind**, not just patterns. A statute that
names a function needs a structured ref or it goes stale on the first rename.

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
# Preamble
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

# Scoring
| | |
|---|---|
| **5** | <what full compliance looks like for THIS rule> |
| **4** | <the acceptable variance> |
| **3** | <the ambiguous case worth discussing> |
| **2** | <ignoring it> |
| **1** | <building a separate path around it> |

# Notes            (optional, non-normative)
```

**Worked example:** [PROPOSED-TAXONOMY.md §12](PROPOSED-TAXONOMY.md) —
`s.config.single-home`.

**The Do/Don't is a classifier, not decoration.** If you cannot write literal code
where the violating version looks *different* from the conforming one, this is not
a statute — it's orchestration, and it's in the wrong namespace. Stop and reclassify.

**Scoring bands are per-directive.** Generic bands ("diverges from intention") tell
the scorer nothing. Say what a 3 looks like *for this rule*.

---



## 3. Pattern

Asserts **one arc** — steps with ownership at each step. Pointer-first: the value
is the canonical implementation, not a re-description of the rules.

```markdown
# Preamble
The recurring situation this arc exists for. What goes wrong without it.

# Arc
The steps, in order, with the owner of each. Prose or a numbered list, not code.

1. Core decides the target state from the registry
2. Tracker validates `prior_states` and raises if the transition is illegal
3. Data writes the row, choosing nothing

# Canonical implementation
The real code to read and follow. This is the body, not a frontmatter footnote.

- `src/core/tracker.py::transition_job_state` — the reference implementation
- `src/utils/config.py::JOB_STATES` — the registry it reads

# Data coupling            (only when one exists)
What else must move when this changes, written **for the scorer**: what to
compare, and what a mismatch means. Not a script — the rubric pass is the check.

# Constraints
Statute ids this arc must stay inside. Cite only — do not restate them.

- `s.core.decides-transitions`
- `s.state.prior-states-enforced`

# Scoring
| | |
|---|---|
| **5** | followed the arc, reused the canonical implementation |
| **4** | followed the arc, minor local variation |
| **3** | recognisable but a step is out of order or an owner is wrong |
| **2** | ignored the arc |
| **1** | built a parallel mechanism for the same workflow |

# When this doesn't apply
Genuine anti-triggers — situations where you should reach for something else.
**Not** a list of violations; those belong in Scoring.

# Notes            (optional)
```

`# Constraints` **cites; it never restates.** The old `pattern.state.entity-state-transitions`
listed three `related_statutes` and then paraphrased all three in prose. That is
the duplication that made patterns feel like padding.

`# When this doesn't apply` **is the section most often written wrong.** The old
template's version was a violation list wearing the wrong hat. If a bullet reads
"someone hardcodes the next state," it is a Scoring 2, not an anti-trigger.

---



## 4. Term

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

No `# Scoring`. No `# Do` / `# Don't`. A term is not a rule.

First terms to write, by how many directives use them undefined today:
`catalog` (7 directives), `carve-out` (4), `hop` (3), `CLICK` (3),
`coat-check` (2), `debug contract` (2).

---



## 5. Orchestration

Pipeline and team process. Same spine as a statute, but the examples are refs,
commands, and Linear states rather than code.

```markdown
# Preamble
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

# Scoring
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

1. **One directive per file.** Filename is the id plus `.md`.
2. **Never invent a scope.** Use the scopes in PROPOSED-TAXONOMY §1. A value that
  fits none of them means the directive is misfiled, not that a scope is missing.
3. **Do not restate another directive.** Cite the id. Duplication across files is
  the failure this whole corpus exists to prevent.
4. **Ground every example in this codebase — but do not take the codebase as the
  standard.** Real file, real function, real constant, so examples stay legible
  and locatable. The rule itself comes from best practice and the brief; `src/`
  is context, not authority. **State the rule first, then search the codebase for
  instances of both sides.** The `# Do` shows the correct shape whether or not any
  current code achieves it. The `# Don't` may cite real code directly — a real
  violation teaches better than an invented one.
5. **If a statute resists literal Do/Don't code, stop.** It's misfiled. Flag it
  rather than writing a vague example.
6. `approved_by: Archie` **is written by the drafter, but the approval is real.**
  A file carrying that field has been through Archie. Drafts stay on the branch.
7. **Terms before directives.** Define `catalog` before drafting the seven
  directives that use it, or you will write seven definitions.
8. **Report on each file the moment you finish it.** See §7. Append to
  `REVIEW-INDEX.md` before starting the next directive — never at the end.

---

## 7. The drafting report

Every directive gets one entry in `docs/canon/REVIEW-INDEX.md`, **appended the
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

### Four axes

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

### Entry shape

```markdown
## s.data.partial-update-allowlist
confidence: 3 — standard practice, but the brief didn't name a return contract; I chose rowcount.
detail:     4 — left out the JSON-serialisation behaviour; it belongs in p.data.entity-definition.
clarity:    4 — "allowlist enforced" may read as caller-side validation. Reworded to name the layer.
scope:      3 — stated for all entities from two examples. Did not sweep every update_*.
conforming_instance: src/data/database.py :: update_company
violations: src/data/database.py :: update_dispatch_task — returns None, not rowcount
```



