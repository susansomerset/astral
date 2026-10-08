# AST-2049 — Move component inline colors onto tokens (User Theme)

- **Parent:** [AST-2042 User Theme](https://linear.app/astralcareermatch/issue/AST-2042)
- **Ticket:** [AST-2049](https://linear.app/astralcareermatch/issue/AST-2049)
- **Publish ref:** `sub/AST-2042/AST-2049-inline-color-tokens` (origin only)
- **Depends on:** [AST-2047](https://linear.app/astralcareermatch/issue/AST-2047) (the `App.css` token blocks this ticket targets). It is merged on `origin/ftr/AST-2042-user-theme`, and this branch is synced onto it.
- **Canon Scope:** none (locked at Discussion).

AST-2047 turned the `App.css` token block into the Dark palette and added three Light palettes that redefine every token. Components that paint with inline literal hex colors, hex fallbacks inside `var(--x, #…)`, or custom properties no block defines stay dark-only, or unstyled, under Light. This ticket repoints each of those in the 19 files named in this ticket's Scope onto a token `App.css` already defines. It makes no layout or behavior change, and it does not edit `App.css` or `CandidateProfile.tsx`. Once it lands, the parent's AC 9 holds epic-wide.

## Ground truth (verified on this branch at `e83fb292e`, the `origin/ftr/AST-2042-user-theme` tip)

- **Defined tokens:** the Dark block (`App.css` L40–82, `:root, [data-theme="dark"]`) declares 38 names. This plan targets only these: `--bg-deep`, `--bg-card`, `--border`, `--text-primary`, `--text-secondary`, `--text-muted`, `--accent-gold`, `--danger`, `--accent-gold-dim`, `--success`, `--warning`, `--error`. Every Light block declares the same names (AST-2047 AC 8).
- **AC 9 hex grep, epic-wide:** `rg -n "[\"' ,(]#[0-9a-fA-F]{3,8}\b" src/ui/frontend/src --glob '*.{ts,tsx}' --glob '!*.test.*' -l` hits exactly 18 files, all in this ticket's Scope. `CandidateProfile.tsx` is already clean (AST-2048). The 19th Scope file, `AdminDataManagement.tsx`, has an `rgba(…)` fallback, not a hex.
- **Undefined custom properties, epic-wide:** exactly four, all in Scope files. `--accent` (StateTimeline L59–60), `--border-color` / `--bg-secondary` (AdminScheduledQueries L185/188/271/274), and `--color-pass` (AdminTaskPrompts L146). Because `--border-color` and `--bg-secondary` are undefined with no fallback, those two `AdminScheduledQueries` boxes currently render with no border and a transparent background.
- **Mapping precedent:** AST-2048 mapped CandidateProfile's `#8b949e` to `--text-secondary`, loading/empty `#fff` to `--text-primary`, and `#ff6b6b` to `--error`. AST-2047 mapped `#888` (`.intake-hold`) to `--text-muted`, `#333` borders to `--border`, and dropped `#c44` fallbacks on `--danger`. Inputs and search fields (`.sidebar-candidate-select select`, `.list-page-search`) use `--bg-deep`. `.modal-card` is `--bg-card`.
- **Neutral overlays stay:** `rgba(0,0,0,0.6)` at ArtifactEditor L1269 and ArtifactsCompanySearchTerms L225 is a neutral overlay (parent Functional scope 5). Not edited.
- **No test asserts these literals:** a grep of `tests/` and `*.test.*` for every literal and undefined name below finds no hit.
- **AST-2041 overlap:** `origin/ftr/AST-2041-resume-autosave` (User Testing, not on `dev`) edits `ArtifactEditor.tsx`. Its hunks are at L303–L1005 (dev numbering), and the nearest is L998. This plan's ArtifactEditor edits are single-line replacements at L965, L972, L977, L1272, L1277, and L1303, and none shares a hunk with AST-2041. Whichever lands second merges cleanly.
- **Lint baseline (this tip):** `npm run lint` in `src/ui/frontend` reports **31 problems (26 errors, 5 warnings)**. Of those, the 19 Scope files hold these 7: `ContextTextPage.tsx:43`, `NavigationShell.tsx:104`, `NavigationShell.tsx:108`, `ProfileTextPage.tsx:22` (`react-hooks/set-state-in-effect`); `AdminScheduledActions.tsx:597`, `:625` (`no-extra-boolean-cast`); `ArtifactsCompanySearchTerms.tsx:75` (`react-hooks/exhaustive-deps`, warning). They are pre-existing and out of scope. Do **not** fix them.
- **Scope count:** the ticket's Boundaries says "18 files", but its Scope list names 19 (7 components + 12 pages). This plan covers the 19 the Scope names.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | 6 inline hex → tokens | ui |
| `src/ui/frontend/src/components/ContextTextPage.tsx` | 2 inline `#fff` → `--text-primary` | ui |
| `src/ui/frontend/src/components/NavigationShell.tsx` | nav badge `#888` → `--text-muted` | ui |
| `src/ui/frontend/src/components/ProfileTextPage.tsx` | 2 inline `#fff` → `--text-primary` | ui |
| `src/ui/frontend/src/components/RepoJsonDivergenceBanner.tsx` | drop 4 `#f87171` fallbacks on `--error` | ui |
| `src/ui/frontend/src/components/StateTimeline.tsx` | 6 hex + undefined `--accent` → tokens | ui |
| `src/ui/frontend/src/components/TabbedTextArea.tsx` | `#8b949e` → `--text-secondary` | ui |
| `src/ui/frontend/src/pages/AdminCostReconciliation.tsx` | variance `#ff6b6b` / `#4caf50` → `--error` / `--success` | ui |
| `src/ui/frontend/src/pages/AdminDataManagement.tsx` | drop `rgba` fallback on `--accent-gold-dim` | ui |
| `src/ui/frontend/src/pages/AdminManageCandidates.tsx` | `#fff`, `#e0e0e0`, `#1a1a2e` → tokens; drop 3 fallbacks | ui |
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | drop `#8b949e` fallback on `--text-secondary` | ui |
| `src/ui/frontend/src/pages/AdminScheduledQueries.tsx` | undefined `--border-color` / `--bg-secondary` → `--border` / `--bg-card`; drop `#c44` fallback | ui |
| `src/ui/frontend/src/pages/AdminSessionCoverLetter.tsx` | `#8b949e` → `--text-secondary`; drop `#c44` fallback | ui |
| `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx` | `#e0e0e0`, `#1a1a2e` → tokens; drop `#c44` fallback | ui |
| `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` | undefined `--color-pass` → `--success`; 2 `#f87171` → `--error` | ui |
| `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` | drop `#c44` fallback on `--danger` | ui |
| `src/ui/frontend/src/pages/ArtifactsCompanySearchTerms.tsx` | 2 `#fff` + 2 `#ff6b6b` → tokens | ui |
| `src/ui/frontend/src/pages/CompaniesNewList.tsx` | `#aaa`, `#1a1a2e`, `#e0e0e0`, `#333` → tokens | ui |
| `src/ui/frontend/src/pages/CompaniesWatchHistory.tsx` | drop `#4caf50` / `#f44336` fallbacks | ui |

**Scope gate:** every row is a file this ticket's `## Scope` names, and every change is the kind Scope describes: an inline literal, a `var(--x, #…)` fallback, or an undefined custom-property reference moved onto a token `App.css` defines. No `App.css`, no `CandidateProfile.tsx`, no new token, and no file outside the list.

**Edit rule for every step:** replace only the quoted string literal shown in **Old** with **New**, on the stated line, with nothing else on the line changed. Line numbers are at `e83fb292e`. Edits are single-line, so they do not shift each other. If a line's current text does not match **Old** exactly, stop (Execution contract).

⚠️ **Decision — global literal map** (applied consistently below and matching AST-2047/AST-2048 precedent):

| Literal / ref | Token | Why |
|---|---|---|
| `#fff` (loading / empty-state text), `#e0e0e0` (body text) | `--text-primary` | AST-2048 precedent; primary readable text |
| `#8b949e`, `#aaa` (helper text) | `--text-secondary` | AST-2048 precedent; secondary copy |
| `#888` (timestamps, counts, empty note) | `--text-muted` | AST-2047 `.intake-hold` precedent |
| `#ff6b6b`, `#f87171` (error text / error border) | `--error` | AST-2047 decision: soft red for error text, separate from the `--danger` fill. `#f87171` is `--error`'s exact Dark value. |
| `#4caf50`, `--color-pass` (`#34d399`) | `--success` | `#4caf50` is `--success`'s exact Dark value. `--color-pass` is undefined, and "pass" is success. |
| `#1a1a2e` (inset textarea / `<pre>` inside a modal) | `--bg-deep` | Inputs use `--bg-deep`. This keeps the inset darker than the `--bg-card` modal it sits in. |
| `#333`, `#444` (borders / connector line) | `--border` | AST-2047 `#333` precedent |
| `#555` / `#666` (inactive timeline dot fill / ring) | `--text-muted` | The dot must stay visible against `--bg-card`. `--border` would make it nearly vanish. |
| `--accent` (undefined; fallback `#5b8cff`) | `--accent-gold` | The only accent token. The latest-state dot goes from blue to gold on Dark. |
| `--border-color` / `--bg-secondary` (undefined) | `--border` / `--bg-card` | Card box convention. These boxes gain a visible border and card background. That is intended (they rendered unstyled). |
| `var(--x, <fallback>)` where `--x` is defined | `var(--x)` | Fallback is dead and holds a hex. Same as AST-2047 `#c44` removals. |

Visible Dark-mode deltas this accepts (no token value changes, so AC 7 is unaffected): `#888` → `#6b6280`, `#fff`/`#e0e0e0` → `#e8e4f0`, `#8b949e`/`#aaa` → `#9a8fb8`, `#ff6b6b` → `#f87171`, `#1a1a2e` → `#0f0b18`, `#333`/`#444` → `#2c1b47`, `#555`/`#666` → `#6b6280`, StateTimeline's latest dot blue → gold, `#34d399` → `#4caf50`, and the two AdminScheduledQueries boxes gaining a border and background.

## Stage 1: Components onto tokens

**Done when:** `rg -n "[\"' ,(]#[0-9a-fA-F]{3,8}\b" src/ui/frontend/src/components --glob '*.{ts,tsx}' --glob '!*.test.*'` returns nothing, no `var(--accent` remains in `src/ui/frontend/src/components`, and `cd src/ui/frontend && npx tsc -b --noEmit` exits 0.

All paths are under `src/ui/frontend/src/components/`.

1. `ArtifactEditor.tsx`:

   | Line | Old | New |
   |---|---|---|
   | 965 | `color: "#fff"` | `color: "var(--text-primary)"` |
   | 972 | `color: "#ff6b6b"` | `color: "var(--error)"` |
   | 977 | `color: "#fff"` | `color: "var(--text-primary)"` |
   | 1272 | `border: "2px solid #ff6b6b"` | `border: "2px solid var(--error)"` |
   | 1277 | `color: "#ff6b6b"` | `color: "var(--error)"` |
   | 1303 | `color: "#ff6b6b"` | `color: "var(--error)"` |

   L1269 `background: "rgba(0,0,0,0.6)"` stays (neutral overlay).

2. `ContextTextPage.tsx`, L83 and L84: `color: "#fff"` → `color: "var(--text-primary)"`.

3. `NavigationShell.tsx`, L235: `color: "#888"` → `color: "var(--text-muted)"`.

4. `ProfileTextPage.tsx`, L60 and L61: `color: "#fff"` → `color: "var(--text-primary)"`.

5. `RepoJsonDivergenceBanner.tsx`: at L187 (`border`), L188, L233, and L257 (`color`), replace `var(--error, #f87171)` with `var(--error)`. L187 becomes `border: "1px solid var(--error)"`.

6. `StateTimeline.tsx`:

   | Line | Old | New |
   |---|---|---|
   | 24 | `color: "#888"` | `color: "var(--text-muted)"` |
   | 59 | `"var(--accent, #5b8cff)" : "#555"` | `"var(--accent-gold)" : "var(--text-muted)"` |
   | 60 | `"2px solid var(--accent, #5b8cff)" : "2px solid #666"` | `"2px solid var(--accent-gold)" : "2px solid var(--text-muted)"` |
   | 63 | `background: "#444"` | `background: "var(--border)"` |
   | 67 | `color: "#e0e0e0"` | `color: "var(--text-primary)"` |
   | 68 | `color: "#888"` | `color: "var(--text-muted)"` |

7. `TabbedTextArea.tsx`, L64: `color: "#8b949e"` → `color: "var(--text-secondary)"`.

8. Run `cd src/ui/frontend && npx tsc -b --noEmit` and the Done-when greps.

9. Commit: `git add` the 7 files above only. Then `git commit -m "code(AST-2049): component inline colors onto theme tokens"` and `git push origin HEAD:sub/AST-2042/AST-2049-inline-color-tokens`.

## Stage 2: Pages onto tokens, then the epic-wide AC 9 / AC 10 check

**Done when:** all four checks in step 14 pass. That means AC 9's hex grep returns nothing across `src/ui/frontend/src`, every `var(--name` there names a Dark-block token, `npm run build` exits 0, and `npm run lint` reports exactly the 31-problem baseline.

All paths are under `src/ui/frontend/src/pages/`.

1. `AdminCostReconciliation.tsx`, L257: `totals.variance > 0 ? "#ff6b6b" : "#4caf50"` → `totals.variance > 0 ? "var(--error)" : "var(--success)"`.

2. `AdminDataManagement.tsx`, L350: `"var(--accent-gold-dim, rgba(212,168,67,0.15))"` → `"var(--accent-gold-dim)"`.

3. `AdminManageCandidates.tsx`:

   | Line | Old | New |
   |---|---|---|
   | 588 | `color: "#fff"` | `color: "var(--text-primary)"` |
   | 607 | `"var(--success, #4caf50)" : "var(--warning, #ff9800)"` | `"var(--success)" : "var(--warning)"` |
   | 675 | `color: "var(--warning, #ff9800)"` | `color: "var(--warning)"` |
   | 714 | `color: "#e0e0e0", background: "#1a1a2e"` | `color: "var(--text-primary)", background: "var(--bg-deep)"` |

4. `AdminScheduledActions.tsx`, L997: `"var(--text-secondary, #8b949e)"` → `"var(--text-secondary)"`.

5. `AdminScheduledQueries.tsx`:

   | Line | Old | New |
   |---|---|---|
   | 185 | `"1px solid var(--border-color)"` | `"1px solid var(--border)"` |
   | 188 | `"var(--bg-secondary)"` | `"var(--bg-card)"` |
   | 271 | `"1px solid var(--border-color)"` | `"1px solid var(--border)"` |
   | 274 | `"var(--bg-secondary)"` | `"var(--bg-card)"` |
   | 307 | `"var(--danger, #c44)"` | `"var(--danger)"` |

6. `AdminSessionCoverLetter.tsx`: at L212, `color: "#8b949e"` → `color: "var(--text-secondary)"`. At L234, `"var(--danger, #c44)"` → `"var(--danger)"`.

7. `AdminSessionResumePaste.tsx`: at L231, `"var(--danger, #c44)"` → `"var(--danger)"`. At L243, `color: "#e0e0e0", background: "#1a1a2e"` → `color: "var(--text-primary)", background: "var(--bg-deep)"`.

8. `AdminTaskPrompts.tsx`:

   | Line | Old | New |
   |---|---|---|
   | 146 | `"var(--color-pass, #34d399)"` | `"var(--success)"` |
   | 428 | `color: "#f87171"` | `color: "var(--error)"` |
   | 499 | `color: "#f87171"` | `color: "var(--error)"` |

9. `ArtifactsBaseResumeContent.tsx`, L226: `"var(--danger, #c44)"` → `"var(--danger)"`.

10. `ArtifactsCompanySearchTerms.tsx`:

    | Line | Old | New |
    |---|---|---|
    | 176 | `color: "#fff"` | `color: "var(--text-primary)"` |
    | 179 | `color: "#fff"` | `color: "var(--text-primary)"` |
    | 228 | `border: "2px solid #ff6b6b"` | `border: "2px solid var(--error)"` |
    | 231 | `color: "#ff6b6b"` | `color: "var(--error)"` |

    L225 `background: "rgba(0,0,0,0.6)"` stays (neutral overlay).

11. `CompaniesNewList.tsx`: at L97, `color: "#aaa"` → `color: "var(--text-secondary)"`. At L106, `background: "#1a1a2e", color: "#e0e0e0", border: "1px solid #333"` → `background: "var(--bg-deep)", color: "var(--text-primary)", border: "1px solid var(--border)"`.

12. `CompaniesWatchHistory.tsx`, L47: `"var(--success, #4caf50)" : "var(--danger, #f44336)"` → `"var(--success)" : "var(--danger)"`.

13. `cd src/ui/frontend && npx tsc -b --noEmit` exits 0.

14. Verification. Run every check from the repo root:
    - **AC 9 hex:** `rg -n "[\"' ,(]#[0-9a-fA-F]{3,8}\b" src/ui/frontend/src --glob '*.{ts,tsx}' --glob '!*.test.*'` prints nothing.
    - **AC 9 undefined refs:** the command below prints nothing.
      ```bash
      cd src/ui/frontend/src && DEF=$(awk '/^:root, \[data-theme="dark"\] \{/{f=1;next} f&&/^\}/{exit} f' App.css | rg -oP -- '--[a-z0-9-]+(?=:)' | sort -u); rg -o --no-filename 'var\(--[a-z0-9-]+' --glob '*.{ts,tsx,css}' --glob '!*.test.*' . | sed 's/var(//' | sort -u | comm -23 - <(echo "$DEF"); cd -
      ```
    - **AC 10 build:** `cd src/ui/frontend && npm run build` exits 0.
    - **AC 10 lint:** `cd src/ui/frontend && npm run lint` reports `✖ 31 problems (26 errors, 5 warnings)`, and the 19 Scope files still show exactly the 7 baseline entries listed under Ground truth. Any other count or entry → stop (Execution contract).

15. Commit: `git add` the 12 page files above only. Then `git commit -m "code(AST-2049): page inline colors onto theme tokens"` and `git push origin HEAD:sub/AST-2042/AST-2049-inline-color-tokens`.

## Execution contract

The plan is binding. Execute steps in order and stages in order. Do not add files, tokens, or edits beyond the tables. Do not touch `App.css`, `CandidateProfile.tsx`, or the pre-existing lint problems. If a line's text does not match **Old**, a check in Stage 2 step 14 fails, or anything is ambiguous, stop and comment on the parent [AST-2042](https://linear.app/astralcareermatch/issue/AST-2042) in the `🛑 Stage N blocked:` format (plan-child § Execution contract). Then wait.

## Estimate

Confirm Chuckles estimate: 3 — revise to 2 because it is a known pattern (single-line literal → existing-token swaps across 19 files), with no new tokens, no logic, and a clear happy path.

## Joan validate

[plan-rubric]
**Ticket:** AST-2049
**Overall:** APPROVED
**Corpus:** cc0ca67ac7e3ffd6f9067ccd857cb47fdb2c6f50 (`canon/` at publish tip; no `docs/canon-index.md` on ref)
**Publish ref:** `7107fa7e8a6c1e7996d47657028c7f9bb760dd3a` (`origin/sub/AST-2042/AST-2049-inline-color-tokens`)

## Canon scores

Frozen list empty (child **Citations:** none; parent **Canon Scope:** none — locked at Discussion). No directive rows to score; not §4a ESCALATE.

## Traceability

Child AC9→Stage 1+2 (epic-wide hex + undefined-`var` checks in Stage 2 step 14, contingent on #2 already clean per Boundaries); AC10→Stage 2 step 14. Parent AC1–8,11 → N/A (#1/#2); parent AC9 `.ts`/`.tsx` half → this ticket after #2; parent AC10 → Stage 2.

## Findings

### fix-now

(none)

### discuss

- **acceptable — Ticket Boundaries “18 files” vs Scope list (19)** — Plan names all 19 Scope files and explains `AdminDataManagement.tsx` has `rgba` fallback only (no hex). Matches parent Component scope file count (7 components + 12 pages).

- **acceptable — Ground truth re-verified on worktree** — AC 9 hex grep hits exactly 18 `.ts`/`.tsx` files, all in Scope; `CandidateProfile.tsx` has no hex (#2). Undefined `var(--*)` epic-wide: `--accent`, `--bg-secondary`, `--border-color`, `--color-pass` only, each addressed in the tables.

- **acceptable — Intentional Dark visual deltas** — Global map documents shifts (e.g. StateTimeline latest dot blue→`--accent-gold`, AdminScheduledQueries boxes gaining border/background, `#f44336`→`--danger` on CompaniesWatchHistory). No `App.css` edits; parent AC 7 unaffected.

- **acceptable — AST-2041 / ArtifactEditor** — Overlap analysis and hunk isolation documented; merge-order risk noted, not a plan defect.

- **acceptable — Estimate line** — “Confirm … 3 — revise to 2” matches Linear estimate 2; pattern is mechanical swaps only.

- **acceptable — Stage commits include `git push`** — Engineer publish step; within build-child norms.

### acceptable

- **Gates:** Plan Ready, assignee Joan Clarke; 0/2 `[plan-discuss]` rounds.
- **Scope fidelity:** 19 files only; no `App.css`, no `CandidateProfile.tsx`, no new tokens; neutral `rgba(0,0,0,…)` overlays preserved.
- **Verification:** Stage 2 step 14 epic-wide AC 9/10 checks align with parent wording; lint held to documented 31-problem baseline in Scope files.

context_tokens≈42000
