# Astral Boards (production)

Committed markdown here is for **production** board-channel work only (e.g. parent **[AST-379](https://linear.app/astralcareermatch/issue/AST-379)**, children **AST-415+**): parent plans on **`ftr/<parent-segment>`**, child plans on **`sub/<parent-id>/<child-segment>`** (id + title slug), per **`orientation-astral` § Branch law**.

## Spikes (R&D) — not in this folder

Board **spike** tickets (Playwright investigation, profile drafts) are research. Their output does **not** get committed under `docs/features/boards/`.

| What | Where |
|------|--------|
| Local files (captures, JSON, drafts) | `debug/spikes/<issue-id>/` (gitignored) |
| Review / handoff | **Linear** issue (comments + **file attachments**) |
| Runnable spike CLIs | `scripts/spikes/` (code only) |

See **`docs/ASTRAL_CODE_RULES.md`** §3.6 and **`orientation-astral`** § Local debug and spike output.

Pre-policy a16z spike markdown may exist **locally** under **`debug/spikes/older/`** (gitignored). Do not add spike run notes or schemas under `docs/features/boards/`.
