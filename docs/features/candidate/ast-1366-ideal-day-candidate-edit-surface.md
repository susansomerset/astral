# AST-1366 — Ideal Day Candidate edit surface

**Linear:** [AST-1366](https://linear.app/astralcareermatch/issue/AST-1366/ideal-day-candidate-edit-surface-add-ideal-day-to-the-set-of-candidate)
**Parent:** [AST-1360](https://linear.app/astralcareermatch/issue/AST-1360/add-ideal-day-to-the-set-of-candidate-context-strengths-priorities-etc) — Add `ideal_day` to the set of candidate context (strengths, priorities, etc.)
**Publish ref:** `sub/AST-1360/AST-1366-ideal-day-candidate-edit-surface`

Ship Candidate nav + Ideal Day edit page as a peer of Strengths / Priorities / Deal Breakers / Backstory, wired to the `ideal_day` library key from AST-1365. Reuse `ContextTextPage` and the existing `PUT /api/candidates/<id>/data` merge path — no new save API. This ticket does **not** own Topic Menu informs / Estelle allowlists (AST-1367) or JD/DO/LIKE craft prompt text (AST-1368). Library vocabulary, `{$IDEAL_DAY}` token, and completeness gate already land via AST-1365 on `origin/ftr/AST-1360-ideal-day-candidate-context` (merge that ftr before coding).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add Ideal Day item to Candidate group in `NAV_CONFIG` | utils |
| `src/ui/frontend/src/pages/CandidateIdealDay.tsx` | New thin `ContextTextPage` wrapper (`contextKey="ideal_day"`) | ui |
| `src/ui/frontend/src/routes.tsx` | Import Ideal Day page; add `candidate/ideal_day` route (keep SYNC comment with `NAV_CONFIG`) | ui |

**Out of scope (do not touch):**

| File / area | Owner |
|-------------|--------|
| `CANDIDATE_LIBRARY_CONFIG`, `TOKEN_SOURCES["IDEAL_DAY"]`, `check_context_complete` / `context_completeness_keys` | AST-1365 (already on parent ftr) |
| `TOPIC_MENU_CONFIG["informs"]`, `TOPIC_MENU_GEN_CONFIG` packet/patch allowlists | AST-1367 |
| `data/admin/agent_task.json` / craft rubric prompt bodies for JD/DO/LIKE | AST-1368 |
| `DATA_SHAPES` Profile detail | N/A — peer context pages are not Profile shape fields (same as Strengths today) |
| `ContextTextPage.tsx` itself | unchanged — Ideal Day is another caller |
| Candidate state machine / survey unlock gates | Parent: no new state transitions for Ideal Day |
| Migrations / backfill | Parent: empty until edited or Topic Menu writes |

## Stages

### Stage 1: Nav + Ideal Day page + route

**Done when:** Candidate sidebar shows **Ideal Day** (path `/candidate/ideal_day`) between Backstory and Writing Preferences; navigating there loads a textarea page titled Ideal Day; Save persists `candidate_data.context.ideal_day` via the same `PUT .../data` merge as Strengths and reload shows the prose.

1. In `src/utils/config.py`, inside `NAV_CONFIG`, in the Candidate group `items` list, insert Ideal Day **immediately after** the Backstory item and **before** Writing Preferences:

```python
{"label": "Backstory", "path": "/candidate/backstory"},
{"label": "Ideal Day", "path": "/candidate/ideal_day"},
{"label": "Writing Preferences", "path": "/candidate/writing_preferences"},
```

   No `enabled` / `visible` on the item — Strengths / Priorities / Deal Breakers / Backstory have none; Ideal Day matches.

   ⚠️ **Decision:** Nav placement after Backstory keeps the five gated completeness-context pages contiguous (Strengths → … → Backstory → Ideal Day) before ungated Writing Preferences. Path segment `ideal_day` matches the library key (same snake_case pattern as `deal_breakers`).

2. Create `src/ui/frontend/src/pages/CandidateIdealDay.tsx` as a one-liner peer of `CandidateStrengths.tsx`:

```tsx
import ContextTextPage from "../components/ContextTextPage"
export default function IdealDay() { return <ContextTextPage title="Ideal Day" contextKey="ideal_day" /> }
```

   Do **not** edit `ContextTextPage.tsx`. Save/load already deep-merges `context.<key>` through `PUT /api/candidates/<id>/data`.

3. In `src/ui/frontend/src/routes.tsx`:

   - Add import with the other Candidate page imports:
     `import IdealDay from "./pages/CandidateIdealDay"`
   - Add route next to the other context routes, immediately after Backstory and before Writing Preferences:
     `{ path: "candidate/ideal_day", element: <IdealDay /> },`

   Honor the file header SYNC comment: every route must have a matching `NAV_CONFIG` item (step 1).

4. Do **not** change Flask API modules — no new endpoint. Do **not** change `docs/features/candidate/CANDIDATE_DATA_MODEL.md` (AST-1365 already documents `context.ideal_day`).

## Estimate

Confirm Chuckles estimate: 2 — agree
