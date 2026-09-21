# AST-1203 — Need to be able to set the "Debug" flag for Slack messages

<!-- linear-archive: AST-1203 archived 2026-08-17 -->

## Linear archive (AST-1203)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1203/need-to-be-able-to-set-the-debug-flag-for-slack-messages  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Operators cannot turn on Astral’s verbose backend debug trail for Slack-driven Contact the way they can for agent runs. Slack Events currently only get auto-debug on local deploy; on staging/production the inbound path stays quiet, so UAT cannot see what Contact did, found, or recorded. This epic adds a Manage Slack **Debug** control (per environment) so Contact Slack traffic can be wordy on demand, with that flag passed through the Contact call chain and debug-gated lines landing in `app_log` as DEBUG — while off keeps production-shaped INFO/WARNING/ERROR only.

## Functional scope

1. **Manage Slack Debug toggle.** On the admin Manage Slack page, operators can turn Contact Slack debug on or off for the current deploy environment. The choice survives process restart (same durable-per-env idea as the existing listen switch).
2. **Ingress and Contact chain honor the flag.** When a Slack call comes in, Contact reads that durable debug setting and passes `debug` through the Contact hear/resolve/turn/reply path and into other core functions that already accept `debug`, so wordiness matches agent-style debug runs when the flag is on.
3. **app_log severity contract.** When Debug is on, debug-contract emissions (what was found and what was recorded per step) persist as DEBUG rows in `app_log` / Execution History. When Debug is off, Contact Slack processing does not emit those debug-contract lines — only normal INFO/WARNING/ERROR.
4. **Contact Slack path wordiness.** With Debug on, Contact Slack handling is Style D–wordy end-to-end on the inbound path (index headers with `index N/M`, primary identifier, outcome; working detail under `|`; long payloads truncated per the backend debug contract). Gaps where a step already accepts `debug` but is silent or summary-only relative to agent Ad Hoc are filled on that same path — not a rewrite of unrelated Astral modules.

## Architectural definition

* **Patterns to reuse**
  * `pattern.config.config-block` — Contact debug default and durable filename live in `CONTACT_CONFIG` (extend the existing Contact block; do not invent a second SoT).
  * `pattern.ui.admin-endpoint` — thin admin GET/PUT for the debug flag on the existing Contact admin API surface; React only renders/toggles resolved state.
  * `pattern.layers.import-discipline` — UI → core → data/external; data stays values-only (no logging); external Slack stays dumb transport.
* **New patterns proposed** — none. Durable per-env JSON under the env `db_dir` already shipped for listen ([AST-1067](https://linear.app/astralcareermatch/issue/AST-1067/manage-slack-admin-listen-switch-per-environment-non-prod-reply-tag)); reuse that shape for debug (separate file/key — do not overload the listen file’s meaning).
* **Applicable statutes**
  * `astral.standards.debug-contract-gated` — emit Style D only when `debug=True`; no new ungated `[DEBUG]` INFO lines.
  * `astral.standards.logging-via-utils` — all backend logging through utils logging / AST-538 helpers.
  * `astral.config.config-source-of-truth` / `astral.standards.no-hardcoded-sets` — flag names, filenames, defaults in config.
  * `astral.patterns.require-auth-on-protected-endpoints` — Manage Slack mutators stay admin-protected; Slack Events auth remains signature verify (no Bearer).
  * `astral.layers.ui-config-driven-business-logic` — UI does not invent debug rules; core/config own SoT.
  * `astral.layers.import-direction` / `astral.layers.core-vs-external-bright-line` — Contact orchestration owns flag hydration and pass-through; external does not decide debug.
  * `astral.standards.in-scope-only` / `astral.standards.dry-and-focused-functions` — no drive-by Contact redesign.
  * `astral.ui.single-gunicorn-worker` — no multi-worker sync story for the durable file (same as listen).
  * Universal product set as applicable on touched product code (logging, config, layers, in-scope-only).

## Boundaries

* Does **not** redesign Estelle conversational quality, skill ACL, Events verify/ack mechanics, or Socket Mode production ingress.
* Does **not** change listen on/off behavior or the listen durable file’s schema meaning.
* Does **not** require React/UI debug-contract logging (backend only).
* Does **not** invent Betty log-string golden tests for Style D text (Radia enforces instrumentation on review; AST-538 precedent).
* Does **not** backfill historical `app_log` rows or redesign Execution History Level UI (DEBUG level already exists via [AST-976](https://linear.app/astralcareermatch/issue/AST-976/add-level-debug-to-app-log-table) family).
* Does **not** expand into non-Contact modules (gazer/consult/agent Ad Hoc already have their own debug triggers).
* Must not break Manage Slack listen controls, Estelle activity table, or quiet production logging when Debug is off.

## Acceptance criteria

1. On Manage Slack, an admin can turn **Debug** on and off; after refresh or process restart on that environment, the page still shows the last saved Debug state.
2. With Debug **on**, a Slack inbound that Contact accepts produces scannable backend debug-contract lines (Style D index headers + `|` detail for found/recorded steps on the Contact path), and those lines appear as **DEBUG** in `app_log` / Execution History.
3. With Debug **off**, the same inbound path does **not** emit those debug-contract lines; INFO/WARNING/ERROR behavior for normal Contact operations remains available.
4. Downstream Contact/core calls that already accept `debug` on the Slack hear → resolve → turn → reply path receive the Manage Slack Debug value (observable via debug-contract detail when on).
5. Listen toggle, Estelle activity list, and non-prod reply prefix behavior are unchanged when toggling Debug.

## Dependencies and blockers

none. Astral Contact Slack foundation ([AST-1043](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent) / Manage Slack listen [AST-1067](https://linear.app/astralcareermatch/issue/AST-1067/manage-slack-admin-listen-switch-per-environment-non-prod-reply-tag) / Events [AST-1069](https://linear.app/astralcareermatch/issue/AST-1069/slack-events-api-webhook-ingress-external-slack-contact) / Estelle turn [AST-1073](https://linear.app/astralcareermatch/issue/AST-1073/contact-estelle-turn-loop-over-ast-1043-contact-contact-estelle)) is Done on the board. No in-flight Contact siblings overlap this scope.

## Open questions

none.

**Resolved (Archie):** (1) Slack Events are exercised on prod/staging — Manage Slack Debug is the sole SoT for Contact Slack Events debug (local auto-debug / `ui_llm_debug` is not the Events path). (2) Better Contact logging for this epic stays on the Contact Slack path gated by this flag only — no sibling Contact-wide logging parent for now.

## Proposed child tickets

#### 1!: **Contact debug flag foundation (config, durable persist, core + admin API) - Ada**

Owns `CONTACT_CONFIG` debug default + durable filename, data-layer read/write under the env `db_dir`, core get/set/hydrate (mirror listen), and admin GET/PUT so the flag is readable/writable without React. Does **not** own Events ingress wiring (#2) or Manage Slack React (#3). **Citations:** `pattern.config.config-block`, `pattern.ui.admin-endpoint`, `astral.config.config-source-of-truth`, `astral.standards.debug-contract-gated`, `astral.patterns.require-auth-on-protected-endpoints`.

#### 2: **Slack Events + Contact inbound honor durable debug and Style D depth - Hedy**

After #1: Events/Contact hear path uses the durable Contact debug SoT (not only local auto-debug), passes `debug` through resolve/turn/reply and configured core callees, and fills Style D found/recorded gaps on that path when debug is on. Does **not** own the Manage Slack React toggle (#3) or listen semantics. **Citations:** `astral.standards.debug-contract-gated`, `astral.standards.logging-via-utils`, `pattern.layers.import-discipline`, `astral.layers.core-vs-external-bright-line`.

#### 3: **Manage Slack UI Debug toggle - Katherine**

After #1: Manage Slack page shows Debug on/off beside listen, loads/saves via the admin API from #1, and does not alter listen or activity table behavior. No React debug-contract logging. **Citations:** `pattern.ui.admin-endpoint`, `astral.layers.ui-config-driven-business-logic`, `astral.patterns.require-auth-on-protected-endpoints`.

Monolith check: four functional capabilities → three children (foundation/API, Events+Style D wire, UI). Intentional split across config/data/core vs ingress wordiness vs React.

---

## Original brief

On the Manage Slack page, create a debug toggle so that when a call comes in from slack, we are very wordy about what it does, how it works, etc., just as we are for agent calls, and pass the debug flag through to other core functions as configured.  When it's on, everything is saved in the app_log table.  When it's off, it's just info/warning/error only.

We also need better logging for Astral Contact in general.

## Git (authoritative — ignore Linear `gitBranchName`)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Ticket | `origin/…` |
| -- | -- |
| [AST-1203](https://linear.app/astralcareermatch/issue/AST-1203/need-to-be-able-to-set-the-debug-flag-for-slack-messages) (parent) | ftr/AST-1203-need-to-be-able-to-set-the-debug-flag-for-slack-messages |
| [AST-1206](https://linear.app/astralcareermatch/issue/AST-1206/contact-debug-flag-foundation-config-durable-persist-core-admin-api) | sub/AST-1203/AST-1206-contact-debug-flag-foundation |
| [AST-1207](https://linear.app/astralcareermatch/issue/AST-1207/slack-events-contact-inbound-honor-durable-debug-and-style-d-depth) | sub/AST-1203/AST-1207-slack-events-contact-inbound-durable-debug |
| [AST-1208](https://linear.app/astralcareermatch/issue/AST-1208/manage-slack-ui-debug-toggle-need-to-be-able-to-set-the-debug-flag-for) | sub/AST-1203/AST-1208-manage-slack-ui-debug-toggle |

**Epic worktree:** `astral-AST-1203/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/84b1630ee141f9bc6bf62e701704f4c1/318e60d6-098b-47bb-97a0-186b327e3c2e/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/84b1630ee141f9bc6bf62e701704f4c1/b04325fe-d340-4981-b293-d1b7b5e0dfa5/store.db` |
| Katherine | engineer | `/home/susan/.cursor/chats/84b1630ee141f9bc6bf62e701704f4c1/395f8234-23d8-4c16-8709-2f644145ca94/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/c451356c-95a2-4040-a2ba-3b9ae30d6b96/store.db` |
| Radia | review | `/home/susan/.cursor/chats/84b1630ee141f9bc6bf62e701704f4c1/aca4c864-9a25-4195-a9a9-1af9608d66ef/store.db` |

### Comments

#### chuckles — 2026-08-06T05:17:59.040Z
@susan

Dispatch blocked — open questions still unanswered (Description ## Open questions + prior comment):

1. Local deploy vs Manage Slack Debug: OR with `ui_llm_debug()` local auto-debug, or Manage Slack Debug as sole SoT for Contact Slack Events (Off = quiet even on local)?
2. Confirm “better logging for Astral Contact in general” stays scoped to the Contact Slack path gated by this Debug flag — or name a separate sibling parent for non-Slack Contact logging.

Answer (or edit Open questions out of the Description), then Todo + assign Chuckles to re-run datt.

— Chuckles

#### chuckles — 2026-08-06T03:07:16.039Z
@susan

1. Local deploy vs Manage Slack Debug: OR with `ui_llm_debug()` local auto-debug, or Manage Slack Debug as sole SoT for Contact Slack Events (Off = quiet even on local)?
2. Confirm “better logging for Astral Contact in general” stays scoped to the Contact Slack path gated by this Debug flag — or call out a separate sibling parent for non-Slack Contact logging.

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
