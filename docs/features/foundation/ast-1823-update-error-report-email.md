# AST-1823 — Update error report email

<!-- linear-archive: AST-1823 archived 2026-10-07 -->

## Linear archive (AST-1823)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1823/update-error-report-email  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Right now, errors are sent to susan+astral@susansomerset.com

I believe this is set in config.py, and I want to send those emails to [`runtime-dispatch-error-498a58685f26@intake.linear.app`](<mailto:runtime-dispatch-error-498a58685f26@intake.linear.app>)

### Comments

#### chuckles — 2026-09-28T05:49:30.676Z
[check-linear] answered — `src/utils/config.py` line 4480, `ASTRAL_CONFIG["support_email"]` (the only address `src/core/monitor.py` reads). Committed as a56032db and pushed to origin/dev. User Testing (@susan)

#### chuckles — 2026-09-28T05:48:57.391Z
[fix-intake]

Changed `support_email` in `src/utils/config.py` (line 4480) from `susan+astral@susansomerset.com` to `runtime-dispatch-error-498a58685f26@intake.linear.app`. That key is the only one the error mailer reads (`src/core/monitor.py`); there is no environment variable override in the code.

Yes, it is committed and pushed: commit `a56032db` ("chore(AST-1823): route error report emails to Linear intake") is on `origin/dev`, and `git show origin/dev:src/utils/config.py` shows the new address.

#### chuckles — 2026-09-28T05:48:41.475Z
@susan Yes, it's committed and pushed to `origin/dev`: commit `a56032db` ("chore(AST-1823): route error report emails to Linear intake").

The change is one line in `src/utils/config.py` (line 4480): `ASTRAL_CONFIG["support_email"]` is now `runtime-dispatch-error-498a58685f26@intake.linear.app`. Its only reader is `src/core/monitor.py`, which sends the error report emails, and nothing in `src` overrides it with an env var. So once `dev` deploys, error emails go to the Linear intake address.

#### susan — 2026-09-28T05:08:19.316Z
@chuckles Where did you make this change, and did you commit/push it to origin dev?

---

_Implementation detail may live in git history on `origin/dev`._
