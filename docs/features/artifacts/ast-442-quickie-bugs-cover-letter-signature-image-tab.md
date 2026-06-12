# AST-442 — Quickie: Cover Letter Signature Image Tab

**Linear:** https://linear.app/astralcareermatch/issue/AST-442/quickie-bugs-cover-letter-signature-image-tab  
**Feature ref:** `sub/AST-436/AST-442-quickie-bugs-cover-letter-signature-image-tab` (origin only)

Move cover letter **signature image** upload, preview, remove, and limit messaging into the Candidate Profile **tab bar**. Signature **text** stays on the existing **Cover Letter Signature** tab. Tab label: **Signature Image**.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add **Signature Image** section to `DATA_SHAPES["candidates"]["detail"]["profile"]` with field type `signature_image` | utils |
| `src/ui/frontend/src/components/TabbedTextArea.tsx` | Optional `customPanels` map keyed by field `key` for non-textarea tab bodies | ui |
| `src/ui/frontend/src/pages/CandidateProfile.tsx` | Wire `customPanels` for signature image; remove standalone section below tabs | ui |

---

## Stage 1: DATA_SHAPES + tab panel hook

**Done when:** `GET /api/shapes/candidates` includes a **Signature Image** profile section; `TabbedTextArea` can render a custom panel for that tab key; Candidate Profile has no standalone signature-image block below the tabbed area.

1. In `src/utils/config.py`, inside `DATA_SHAPES["candidates"]["detail"]["profile"]`, **immediately after** the object with `"label": "Cover Letter Signature"` (the section whose field key is `profile.cover_letter_signature`), insert a new section:

```python
{
    "label": "Signature Image",
    "fields": [
        {
            "key": "profile.cover_letter_signature_image",
            "label": "Signature Image",
            "type": "signature_image",
        },
    ],
},
```

2. In `src/ui/frontend/src/components/TabbedTextArea.tsx`:
   - Extend `TextTab` with optional `panelKey?: string` (defaults to `key` for textarea tabs).
   - Add optional prop `customPanels?: Record<string, React.ReactNode>` (import `ReactNode` from `react`).
   - When building tab content: if `customPanels[tab.key]` is defined, render that node instead of `LabeledTextArea` for the active tab.
   - Tab bar labels still come from `tabs[].label`; index-based `TabBar` behavior unchanged.

3. In `src/ui/frontend/src/pages/CandidateProfile.tsx`:
   - When mapping `tabSections` to `textTabs`, include **all** sections from `sections.slice(1)` (not only textarea fields). For each section, use `f.key` from `sec.fields[0]`; keep existing resume-tab `disabled` / `placeholder` logic when `f.key === "context.starting_resume_text"`.
   - Define `signatureImagePanel` JSX by **moving** the current signature-image block from the bottom `dep-section` (file input, preview `img`, Remove button, limit text) into a `useMemo` or inline const passed as `customPanels["profile.cover_letter_signature_image"]`. Reuse existing handlers: `handleSignatureImagePick`, `handleClearSignatureImage`, `sigFileRef`, `sigImg`, `maxSigW`, `maxSigH`.
   - Pass `customPanels={{ "profile.cover_letter_signature_image": signatureImagePanel }}` to `TabbedTextArea`.
   - **Delete** the second `dep-section` below the tabbed area that wraps **Cover Letter Signature Image** (image-only block; contact + tabbed sections remain).

⚠️ **Decision:** Dedicated **Signature Image** tab (not combined with signature text tab) per Linear acceptance criteria and Susan’s tab label.

---

## Stage 2: Verify UI behavior

**Done when:** Manual smoke on Candidate Profile confirms acceptance criteria; TypeScript compiles.

1. `cd src/ui/frontend && npx tsc -b --noEmit`
2. Manual: open Candidate Profile → confirm tabs include **Signature Image**; upload JPEG within limits, preview, Remove; Save/Cancel still persist `profile.cover_letter_signature_image`; **Cover Letter Signature** text tab unchanged; no image UI below the tab strip.

---

## Self-Assessment

**Scope:** `scope-Single-Component` — Candidate Profile tab strip + one `DATA_SHAPES` section; no API or validation changes.

**Conf:** `conf-high` — Reuses existing AST-366 image handlers and `TabbedTextArea` / `TabBar` pattern; one small extension for custom panels.

**Risk:** `risk-low` — Wrong tab wiring only affects profile UX; signature text and contact fields untouched.

---

## Resolution (resolve-astral 2026-05-22)

- **fix-now:** none.
- **discuss:** none.
- **advisory:** No `CandidateProfile` integration test — accepted per Radia; manual smoke (Stage 2) is the bar.
- Radia review 2026-05-22: approve. No product changes on resolve pass.
