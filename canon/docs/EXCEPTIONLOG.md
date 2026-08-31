# Canon exception log

Every `EXCEPTION` / `REASON` / `UNTIL` carved into a directive, in one place.
**Not** loaded at runtime — same as `CHANGELOG.md`, this exists so a human
(or an audit) can find every piece of sanctioned tech debt without opening
every directive file to check its Notes section.

An exception is not a violation, and it is not silently tolerated code — it
is a directive knowingly relaxing itself, with a stated reason and a stated
condition under which the relaxation ends. The exception's full text lives
in the directive it's an exception *to* (the rule and its exception are
never separated into different files); this log exists purely so the
corpus-wide view doesn't require opening every file to find them.

---

## Open exceptions

| Directive | Exception | Reason | Until | Logged |
|---|---|---|---|---|
| `stat.layers.import-rules` | `logging.py` may late-import `database.add_log_entry` inside `_DatabaseLogHandler._flush_buffer` — the one `utils → data` import in the codebase | Needed an easy way to pull log content from batch runs in the local environment | Proper console logging/monitoring is implemented, console logs are filterable by `batch_id`, and log content persists on a real retention policy instead of being kept forever | 2026-08-23 |

## Closed exceptions

None yet. An exception moves here — with a closed date and what replaced
it — once its `Until` condition is actually met and the code changes to
match. Deleting a row instead of moving it here loses the reason the
exception existed, which is exactly the history a future audit needs.

---

## What counts as a row here

Any `EXCEPTION` / `REASON` / `UNTIL` block written into a statute or
pattern. A directive's own "when this doesn't apply" list is **not** an
exception — that's the directive correctly not governing something outside
its territory. An exception is the directive governing something and
choosing, for a stated reason, not to enforce itself there yet.
