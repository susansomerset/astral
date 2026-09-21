---
id: stat.logging.debug
kind: statute
scope: logging
point: >
  logger.debug is a noisy, generous backstop; the logger ContextVar decides whether it prints.
approved_by: null
approved_at: null
supersedes: null
superseded_by: null
terms: []
applies_when:
  layers: ["core", "external", "utils", "ui"]
  paths: ["src/**"]
  change_types: ["add", "modify"]
canonical_refs:
  - path: src/utils/logging.py
    symbol: get_logger
  - path: src/utils/logging.py
    symbol: log_debug
---

# Abstract

When something is not working, debug is the backstop: watch the code walk
through its logic. That dump is **generous and noisy on purpose**. Every
loop logs begin and end (how many items going in, how many came out).
Every call into a callee like `agent.do_task` logs the param keys/values
on the way in and the full response string on the way out. Call sites
always call `logger.debug`; they do not inspect a flag.
`src.utils.logging` reads the `log_debug` ContextVar and either prints or
drops the line. `logger.info("[DEBUG] …")` is always-on noise. `print`
never reaches `app_log`.

# Statement

Call `logger.debug` through `get_logger(__name__)` from `src.utils.logging`
at the logic joints, not as a rare aside:

- **Loop start:** `Beginning <what> loop on N items`
- **Loop end:** `End <what> loop after X items`
- **Callee in:** `Calling <fn>: [<param key/values>]`
- **Callee out:** `Response from <fn>: <response string>`

Do not skip those because they are noisy. Do not wrap the call in
`if debug` / `if log_debug.get()`. The logger prefixes the caller source line
and emits only when `log_debug` is true. The run entry sets that
ContextVar; callees do not take a `debug=` just to log. No `print`, no
stdlib `getLogger`, no `logger.info("[DEBUG] …")`, no debug noise in
`src/data/`. Do not truncate the message.

# Scenario

A consult loop of N jobs is misbehaving and debug mode is on. The scan
must show the loop started on N, each `do_task` with its keys, the full
response string, and that the loop ended after X items — each line stamped
with the source line that emitted it. A single `summary={failed=3}` at
the bottom is not that walk. Wrapping the calls in `if debug` is how the
flag gets dropped three frames down. Checking the ContextVar at the call
site duplicates the logger. The same calls with debug off must be silent in
`app_log` — `info` / `warning` / `error` still fire.

# Do

```python
from src.utils.logging import get_logger

logger = get_logger(__name__)
# run entry already set log_debug; this file does not check it

logger.debug("Beginning filename loop on %s items", n)
logger.debug("Calling agent.do_task: %s", params)
logger.debug("Response from agent.do_task: %s", response)
logger.debug("End filename loop after %s items", x)
```

The logger stamps the caller line, e.g. `1847: Beginning filename loop on 12 items`.

# Don't

```python
if debug:
    logger.debug("Beginning loop")          # call site must not gate
if log_debug.get():
    logger.debug("Beginning loop")          # logger already reads the var
logger.info("[DEBUG] cse hits=%s", n)       # ungated, wrong level
print(prompt)                               # no app_log
log.debug_index(...)                        # Style D is not this statute
logger.debug("row missing id=%s", job_id)   # in src/data/ — data does not log
logger.debug("batch done summary=%s", s)   # instead of begin/end + call/response
logger.debug("Response from agent.do_task: %s…", response[:200])  # do not truncate
```

# Resolution

The dump is useful but the run might be production.

1. **Debug off?** The `logger.debug` calls still run; the logger drops them.
   `info` and item `warning` still fire — those statutes are not gated.
2. **Need who failed in production?** `stat.logging.warning` (per item).
   Task counts are `stat.logging.info.dispatcher`, not a warning tally and
   not a debug dump.
3. **Huge response / prompt?** Still `logger.debug` the whole string. Do not
   truncate. Noise is the point.
4. **Callee has no `debug=` argument?** Good. Do not add one for logging.
   The ContextVar is already in scope.
5. **`utils → data` for the sink?** Not this statute — the temporary late-import
   lives on `stat.layers.import-rules` until production monitoring exists.

# Notes

Backend only — no React debug-contract duty. Ungated progress stays `info`
(`stat.logging.info`); those lines are not debug. `log_llm_batch_summary`
success when `log_batch_id` is set stays `info`. The run entry (dispatcher
task debug, UI local debug) sets `log_debug`; it does not pass the flag down
for logging. `debug_index` / `debug_detail` remain in `logging.py` for
unconverted files until those audits; they are not the contract.
