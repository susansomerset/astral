# AST-2048 — Save and apply the candidate's theme (User Theme)

- **Parent:** [AST-2042 User Theme](https://linear.app/astralcareermatch/issue/AST-2042)
- **Ticket:** [AST-2048](https://linear.app/astralcareermatch/issue/AST-2048)
- **Publish ref:** `sub/AST-2042/AST-2048-theme-save-apply` (origin only)
- **Depends on:** [AST-2047](https://linear.app/astralcareermatch/issue/AST-2047) (registry, profile Theme select, `[data-theme]` palette blocks). It is merged on `origin/ftr/AST-2042-user-theme`, and this branch is synced onto it.
- **Canon Scope:** none (locked at Discussion).

AST-2047 added the theme registry (`UI_CONFIG["themes"]`, `UI_CONFIG["default_theme"]`), a profile **Theme** select whose options come from that registry, and one `[data-theme="<id>"]` token block per palette in `App.css`, with `:root` as Dark. This ticket closes the loop. The server rejects any `theme` that is not a profile-selectable registry id. Candidate Profile loads the stored theme, or the served default when none is stored, and saves it with the existing Save. `CandidateContext` sets `data-theme` on `<html>` from the selected candidate, so the SPA repaints on load, after Save, and when the admin picker switches candidates. CandidateProfile's own inline hex colors move onto tokens.

## Ground truth (verified on this branch at `b61c7c619`)

- **Registry:** `src/utils/config.py` ~L5687 has `UI_CONFIG["themes"]` with `dark`, `light` (`profile_selectable: True`) and `light_parchment`, `light_slate` (`profile_selectable: False`), plus `"default_theme": "dark"`. The profile shape field is `{"key": "theme", "type": "select", ...}`, a **top-level** key, not under `contact`.
- **Save path:** `PUT /api/candidates/<id>/data` (`src/ui/api/api_candidate.py` `update_candidate_data`) passes the remaining body to `save_candidate_data(candidate_id, body, replace=False, ...)`. `theme` is not a name column, so it lands in `blob_merge` as a candidate_data meta key. Every exception in that handler returns `400 {"error": str(e)}` (L508–525). `save_candidate_data` (`src/core/candidate.py` L918–1039) validates before `database.save_candidate`, so a raise there leaves the stored value unchanged.
- **Pronouns precedent:** `src/core/candidate.py` L950–953 raises `ValueError(f"Invalid pronouns value: {pref!r}")`.
- **Served config route:** Flask serves `UI_CONFIG` at **`/api/ui_config`** (`api_system.py` L197, blueprint prefix `/api`). CandidateProfile already fetches that route on mount, for `cover_letter_signature_image`.
- **Candidate list:** `GET /api/candidates` returns full `candidate_data` per candidate (`_sanitize_candidate` strips only API keys), so `CandidateContext` can read `candidate_data.theme` directly. The existing timezone effect reads `candidate_data.contact.timezone` the same way.
- **Provider lifetime:** `CandidateProvider` sits inside `RequireAuth` (`routes.tsx` L75–82). It is not mounted on `/authenticate`, and it unmounts when auth drops.
- **CandidateProfile inline hex:** L189 and L193 `"#8b949e"`, L216 and L217 `"#fff"`, L237 `"#ff6b6b"`. These are the only hex literals in the file.
- **Lint baseline:** `npx eslint src/pages/CandidateProfile.tsx src/contexts/CandidateContext.tsx` reports exactly one pre-existing warning, `CandidateContext.tsx` `react-hooks/exhaustive-deps` on `load` (the `[authLoading, loginEmail]` effect). The planned edits were prototyped and then reverted. The prototype produced no new lint problem, and `npx tsc -b` passed.

### Finding outside this ticket (not fixed here)

`src/ui/frontend/src/lib/uiConfig.ts` `loadUiConfig` fetches **`/api/system/ui_config`**. No Flask route matches that path, so the request falls through to `serve_react`'s catch-all, which returns `index.html`. `r.json()` then throws, and the `.catch` sets `_uiConfig = { column_types: {} }`. So `getUiConfig()?.themes` and `default_theme` are always `undefined` at runtime. This dates from AST-647. It also affects AST-2047's `AdminThemeExamples` (`themes` undefined renders "Loading..."). `uiConfig.ts` belongs to AST-2047's scope, not this ticket's. **This plan therefore does not use `getUiConfig()`.** CandidateProfile reads `default_theme` from the `/api/ui_config` response it already fetches.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Import `UI_CONFIG`. `save_candidate_data` raises `ValueError` when `theme` is present and is not a profile-selectable registry id. | core |
| `src/ui/frontend/src/pages/CandidateProfile.tsx` | `defaultTheme` state from `/api/ui_config`. `editValuesFromCandidate` gains `theme`. Candidate fetch waits for the default. Inline hex onto tokens. | ui |
| `src/ui/frontend/src/contexts/CandidateContext.tsx` | New effect sets or removes `data-theme` on `document.documentElement` from the selected candidate. | ui |

**Scope gate:** all three rows are files this ticket's `## Scope` names, and each change is the kind it describes: an allowlist `ValueError` like pronouns, `editValuesFromCandidate` gaining `theme` with the served default plus inline literals onto tokens, and a new effect on the document root attribute. No config, `App.css`, `uiConfig.ts`, routes, Theme Examples page, or #3 component files.

## Stage 1: Server rejects an unregistered theme

**Done when:** `PUT /api/candidates/<id>/data` with `{"theme": "neon"}` or `{"theme": "light_slate"}` returns 400 and leaves the stored theme unchanged, while `{"theme": "light"}` returns 200 and stores `candidate_data.theme == "light"`. `python -m py_compile src/core/candidate.py` exits 0.

1. In `src/core/candidate.py`, in the `from src.utils.config import (...)` block (L57–102), add the line `    UI_CONFIG,` directly after `    TASK_CONFIG,` (L90).
2. In `src/core/candidate.py` `save_candidate_data`, immediately after the pronouns block that ends `raise ValueError(f"Invalid pronouns value: {pref!r}")` (L950–953) and before `contact = blob_merge.get("contact")`, insert exactly:

   ```python
       # AST-2042: theme is a candidate_data meta key; only profile-selectable registry ids may be stored
       # (examples-only palettes are rejected too). List, not set, so an unhashable value fails cleanly.
       if "theme" in blob_merge:
           selectable = [tid for tid, t in UI_CONFIG["themes"].items() if t["profile_selectable"]]
           if blob_merge["theme"] not in selectable:
               raise ValueError(f"Invalid theme value: {blob_merge['theme']!r}")
   ```

   ⚠️ **Decision:** Strict allowlist. `None`, `""`, non-strings, unregistered ids, and examples-only ids all raise. Clearing a theme is not a supported write, and the profile always sends a registry id (Stage 2). The check runs only when the key is present, so every other caller of `save_candidate_data` is unaffected.

   ⚠️ **Decision:** No change to `api_candidate.py`. Its existing `except Exception` returns `400 {"error": "Invalid theme value: 'neon'"}`, and the raise comes before `database.save_candidate`, so the stored value is unchanged (AC 4).

3. Run `python3 -m py_compile src/core/candidate.py` and confirm exit 0. Commit: `code(AST-2048): reject unregistered theme on candidate data save`.

## Stage 2: Candidate Profile loads and saves the theme

**Done when:** On Candidate Profile, a candidate with no stored theme shows **Dark** selected and the form is not dirty. Choosing Light and clicking Save persists `candidate_data.theme == "light"`, and reloading shows Light selected. CandidateProfile.tsx contains no hex literal.

All edits are in `src/ui/frontend/src/pages/CandidateProfile.tsx`.

1. After `const [sigLimits, setSigLimits] = useState<SigImageLimits | null>(null)` (L63), add:

   ```tsx
     // AST-2042: served UI_CONFIG.default_theme — what a candidate with no stored theme shows/saves.
     const [defaultTheme, setDefaultTheme] = useState<string | null>(null)
   ```

2. In the mount effect's `/api/ui_config` `.then(cfg => { ... })` (L73–75), add this line after `setSigLimits(cfg.cover_letter_signature_image ?? null)`. Leave the `.catch` unchanged.

   ```tsx
         setDefaultTheme(typeof cfg.default_theme === "string" ? cfg.default_theme : null)
   ```

3. Change the signature `function editValuesFromCandidate(c: Record<string, unknown>): Record<string, unknown> {` (L78) to:

   ```tsx
     function editValuesFromCandidate(c: Record<string, unknown>, fallbackTheme: string | null): Record<string, unknown> {
   ```

   In its returned object, directly after `pronouns: c.pronouns ?? "",`, add:

   ```tsx
         // Stored theme, else the served default, so the select never sits on a value Save would reject.
         theme: (typeof d.theme === "string" && d.theme) || fallbackTheme,
   ```

4. Replace the candidate-fetch effect (L99–106):

   ```tsx
     useEffect(() => {
       if (!selectedId) return
       api(`/api/candidates/${selectedId}`).then(r => r.json()).then(c => {
         const vals = editValuesFromCandidate(c)
         setFetched({ id: selectedId, data: vals })
         setValues({ ...vals })
       })
     }, [selectedId])
   ```

   with:

   ```tsx
     useEffect(() => {
       // Wait for the served default so a candidate with no stored theme loads as that default.
       if (!selectedId || !defaultTheme) return
       api(`/api/candidates/${selectedId}`).then(r => r.json()).then(c => {
         const vals = editValuesFromCandidate(c, defaultTheme)
         setFetched({ id: selectedId, data: vals })
         setValues({ ...vals })
       })
     }, [selectedId, defaultTheme])
   ```

   ⚠️ **Decision:** Wait for `default_theme` rather than hard-coding a fallback id. A literal `"dark"` would be a second theme list (parent AC 2). Not sending `theme` would contradict Scope ("defaulting to the served default id"). Side effect: if `/api/ui_config` fails, the profile stays on "Loading..." instead of rendering. Today that failure only hides the signature-image limits. That endpoint also serves the profile's own config, so a failure means the server is broken. Flag for Susan if she prefers a different failure behavior.

5. In `persistProfile`'s success `.then(candidate => { ... })` (L133–139), change `const vals = editValuesFromCandidate(candidate)` to `const vals = editValuesFromCandidate(candidate, defaultTheme)`. Change the `useCallback` dependency array `[selectedId, values, refreshCandidate]` (L149) to `[selectedId, values, refreshCandidate, defaultTheme]`.

   No other Save change is needed. `values.theme` is set by the existing `FormFields` select through `set("theme", …)` (top-level key), and `JSON.stringify(values)` sends it. `refreshCandidate()` (already called after Save) reloads the candidate list, which drives the Stage 3 repaint.

6. Inline literals onto tokens (AST-2047 defines all three tokens in every palette block):
   - L189: `style={{ color: "#8b949e" }}` → `style={{ color: "var(--text-secondary)" }}`
   - L193: `style={{ color: "#8b949e", marginBottom: 8 }}` → `style={{ color: "var(--text-secondary)", marginBottom: 8 }}`
   - L216: `style={{ padding: 20, color: "#fff" }}` → `style={{ padding: 20, color: "var(--text-primary)" }}`
   - L217: `style={{ padding: 20, color: "#fff" }}` → `style={{ padding: 20, color: "var(--text-primary)" }}`
   - L237: `style={{ padding: "8px 20px", color: "#ff6b6b" }}` → `style={{ padding: "8px 20px", color: "var(--error)" }}`

   ⚠️ **Decision:** These texts sit on the page background, so they map to `--text-primary` (body text), not `--text-on-color`, which is white in every palette and would be invisible on Light. Helper gray maps to `--text-secondary`. Soft-red error text maps to `--error`, the token AST-2047 added for exactly these `.tsx` soft reds (its plan, Decision at "Defining `--error`"). On Dark these shift slightly (`#fff`→`#e8e4f0`, `#8b949e`→`#9a8fb8`, `#ff6b6b`→`#f87171`). Parent AC 7 compares `App.css` token values only, which this ticket does not touch.

7. Run `rg -n '#[0-9a-fA-F]{3,8}\b' src/ui/frontend/src/pages/CandidateProfile.tsx` and confirm no output. Commit: `code(AST-2048): Candidate Profile loads/saves theme; inline colors onto tokens`.

## Stage 3: SPA repaints to the selected candidate's theme

**Done when:** With the selected candidate on Light, `document.documentElement.getAttribute("data-theme") === "light"` and `getComputedStyle(document.body).backgroundColor !== "rgb(15, 11, 24)"`. With a no-theme candidate selected, the attribute is absent and the body background is `rgb(15, 11, 24)`. Switching candidates in the admin picker flips both without a reload.

1. In `src/ui/frontend/src/contexts/CandidateContext.tsx`, insert this effect directly after the timezone effect (which ends `}, [selectedId, candidates])` at L126) and before the `document.title` effect:

   ```tsx
     // AST-2042: paint the page in the selected candidate's theme ([data-theme] blocks in App.css).
     // No stored theme, nothing selected, or provider unmounted (logout) → no attribute → :root Dark.
     useEffect(() => {
       const c = candidates.find(x => x.astral_candidate_id === selectedId)
       const theme = c?.candidate_data?.theme
       const root = document.documentElement
       if (typeof theme === "string" && theme) root.setAttribute("data-theme", theme)
       else root.removeAttribute("data-theme")
       return () => root.removeAttribute("data-theme")
     }, [selectedId, candidates])
   ```

   ⚠️ **Decision:** A missing theme removes the attribute rather than setting `data-theme="<default_theme>"`. `:root` is Dark per AST-2047's contract ("No attribute means Dark"), and AC 5 accepts either. This also avoids depending on `getUiConfig()`, which never has `default_theme` at runtime (see Finding). Before candidates load, `candidates` is empty, so no attribute is set: Dark (parent Functional scope 3).

   ⚠️ **Decision:** The cleanup runs on every dependency change and on unmount. On a switch, React runs cleanup and the new effect in the same commit, so the attribute goes straight to the new value without a visible gap. On logout the provider unmounts, so the login screen is Dark. No server-side check of the stored id happens here: the API only stores selectable ids (Stage 1), and an id without a CSS block falls back to `:root` Dark anyway.

2. From `src/ui/frontend`: run `npm run build` and confirm exit 0. Run `npm run lint` and diff its problem list against the same command on `origin/dev`. The only allowed problem in the touched files is the pre-existing `CandidateContext.tsx` `exhaustive-deps` warning on `load`. It stays at L119 because the new effect is inserted below it. Still, diff by rule and message, not by line. Commit: `code(AST-2048): repaint SPA to selected candidate's theme`.

## Acceptance mapping

| AC | Covered by |
|----|------------|
| 3 Profile saves the theme | Stage 1 (accepts `light`) + Stage 2 (load/default/save) |
| 4 Bad values rejected | Stage 1 |
| 5 App repaints | Stage 3 |
| 6 Picker follows the candidate | Stage 3 (`[selectedId, candidates]` deps) |
| 7 Builds clean; no new lint | Stage 2 step 7 + Stage 3 step 2 |
| Parent AC 9 (CandidateProfile share of `.tsx` hex grep) | Stage 2 step 6 |

## For QA (not a test-tree edit — Betty owns tests)

- Server: `PUT …/data` with `{"theme": "neon"}`, `{"theme": "light_parchment"}`, `{"theme": ""}`, and `{"theme": null}` should each return 400 with the stored theme unchanged. `{"theme": "light"}` returns 200.
- Browser: AC 5 and AC 6 need computed-style checks on `<html>` and `<body>`. The login screen (provider unmounted) should be Dark.

## Estimate

Confirm Chuckles estimate: 2 — agree


## Joan validate

[plan-rubric]
**Ticket:** AST-2048
**Overall:** APPROVED
**Corpus:** cc0ca67ac7e3ffd6f9067ccd857cb47fdb2c6f50 (`canon/` at publish tip; no `docs/canon-index.md` on ref)
**Publish ref:** `16e114d0122083097a322676d1b2c2bd93a30b66` (`origin/sub/AST-2042/AST-2048-theme-save-apply`)

## Canon scores

Frozen list empty (child **Citations:** none; parent **Canon Scope:** none — locked at Discussion). No directive rows to score; not §4a ESCALATE (explicit empty scope, same as AST-2047).

## Traceability

Child AC3→Stage 1+2; AC4→Stage 1; AC5→Stage 3; AC6→Stage 3; AC7→Stage 2–3. Parent AC1–2,7–11 → N/A (#1/#3); parent AC9 `.tsx` hex share → Stage 2 step 6 (per Boundaries).

## Findings

### fix-now

(none)

### discuss

- **acceptable — `/api/system/ui_config` vs `/api/ui_config` (AST-647)** — Plan documents `loadUiConfig` breakage and correctly avoids `getUiConfig()` here; `default_theme` comes from CandidateProfile’s existing `/api/ui_config` fetch. Fixing `uiConfig.ts` is out of scope (AST-2047 file); epic UAT should still track Theme Examples “Loading…” until that path is fixed elsewhere.

- **acceptable — Profile gated on `defaultTheme`** — Waiting on served `default_theme` avoids a hard-coded `"dark"` second list (parent AC 2). Documented tradeoff if `/api/ui_config` fails (stay on Loading…); consistent with treating that endpoint as required infrastructure.

- **acceptable — `UI_CONFIG` import in `candidate.py`** — Matches existing config-driven allowlist pattern (`PRONOUN_PREFERENCE_OPTIONS`); theme lands in `blob_merge`, validation placement before contact merge/save is correct; `ValueError` → existing 400 handler satisfies AC 4 without `api_candidate.py` edits.

- **acceptable — Dark-only visual nudge on CandidateProfile inline token swap** — Plan calls out `#fff`→`--text-primary` etc.; parent AC 7 is `App.css`-only; in scope per ticket Boundaries.

- **acceptable — No `## Self-assessment`** — Estimate confirm `2 — agree`; three-file footprint with anchored stages; no `!!-NONE` conf gap.

### acceptable

- **Gates:** Plan Ready, assignee Joan Clarke; 0/2 `[plan-discuss]` rounds.
- **Scope fidelity:** Three files only; no config/`App.css`/`uiConfig.ts`/routes/#3 components; `theme` as top-level `candidate_data` meta key aligned with DATA_SHAPES field key and `save_candidate_data` blob merge.
- **Data path:** `editValuesFromCandidate` uses `d.theme` from `candidate_data` (not column `pronouns` pattern); Save PUT + `refreshCandidate()` repaints via Stage 3 deps; cleanup on unmount → login Dark per parent Functional scope 3.
- **Dependency:** Explicit AST-2047 merge on `ftr`; registry/tokens assumed present.

context_tokens≈38000
