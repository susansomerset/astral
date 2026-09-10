# How to use this payload

These are the directives in Canon Scope for this ticket. This is the complete
set you are scored against: nothing outside it applies, and nothing in it is
optional.

Each directive carries:
  Statement    the rule, normatively.
  Scenario     the moment it fires.
  Do / Don't   literal code. The Don't is a real failure mode, not a strawman.
  Resolution   (some directives) what to do when compliance looks impossible.

## When you cannot comply

1. Work the directive's `# Resolution` section. Every option there is fully
   compliant. Resolution is not a way around the rule, it is the way through
   it, and most apparent conflicts end here.

2. If Resolution yields no compliant path, ESCALATE AT THE PLAN STAGE to
   discuss changing the scopes on the parent ticket. State what you needed,
   which Resolution steps you worked and what each returned, and which scope
   you believe is wrong.

     Component / Data / Test Scope  - Chuckles and Joan resolve it at plan.
     Canon Scope                    - locked at Discussion. Archie decides.

   Never ship a violation. Never decide alone. If you reach this during build
   rather than plan, stop and return the ticket to plan: drift escalates, it
   is not fixed in flight.

## Grading

  A  as directed                      B  slight variance, within scope
  C  diverges from the directive      D  ignores the directive
  F  builds a separate path around it
  X  not applicable - this file is outside the directive's territory

  A/B PROCEED   C DISCUSS   D/F FIX NOW

**Worst grade wins.** Never average, never count. One D among six A grades is
FIX NOW. X is excluded from the roll-up entirely: not applicable is not a low
grade, and a directive graded X for every file was mis-selected, not passed.

A finding carries one line naming the location; a pass is the bare grade.

## Effort

Every finding also carries an effort rating, scoring the CORRECTION, not the
violation. Written GRADE/EFFORT - `D/2`.

  1  mechanical - a low-risk global find/replace
  2  local edit inside one function; no signature change
  3  changes a signature or its call sites; a handful of files
  4  complete refactor of the function
  5  complete refactor of the solution - multiple functions and files in scope

Grade and effort are independent. An F can be effort 1 (one banned import to
delete); a C can be effort 5 (nearly the right shape, but fixing it moves four
modules). Never infer one from the other. X carries no effort.
