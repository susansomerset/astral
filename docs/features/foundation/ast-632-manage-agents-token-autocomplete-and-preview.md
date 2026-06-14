# AST-632 — Manage Agents token autocomplete and preview (Support tokens in Agent prompts)

- **Linear (this ticket):** [AST-632](https://linear.app/astralcareermatch/issue/AST-632/manage-agents-token-autocomplete-and-preview-support-tokens-in-agent)
- **Parent:** [AST-574](https://linear.app/astralcareermatch/issue/AST-574/support-tokens-in-agent-prompts)
- **Publish ref:** `origin/sub/AST-574/AST-632-manage-agents-token-autocomplete-and-preview`
- **Depends on:** [AST-631](https://linear.app/astralcareermatch/issue/AST-631/runtime-token-resolution-in-agent-content-support-tokens-in-agent) (`resolved_agent_content` on `origin/ftr/ast-574-support-tokens-in-agent-prompts`)

## Summary

Manage Agents (`AdminAgentPrompts.tsx`) today uses plain `<textarea>` for agent `content`. This ticket adds the shared `TokenTextarea` autocomplete (same UX as Manage Tasks) with a token list appropriate for static agent templates — all registry tokens **except** chain/hop tokens (`{$CALLER_*}` and `{$SELECTED_AGENT}`). It adds a candidate-scoped **resolved preview** (same global candidate as Manage Tasks via `CandidateContext`) so Susan can verify persona copy while authoring. Storage continues to persist literal `{$TOKEN}` placeholders; preview is read-only server resolution.

## Out of scope (this ticket)

| Item | Owner |
|------|--------|
| Runtime token resolution in production / Manage Tasks preview | **AST-631** (landed on ftr) |
| New tokens or `TOKEN_SOURCES` entries | — |
| Task prompt UI (`AdminTaskPrompts.tsx`) | — |
| Betty test manifest / `tests/` edits | Betty (`qa-child`) |

## Reference implementation

- **Token picker + preview UX:** `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` — `TokenTextarea`, `useCandidate`, preview modal pattern.
- **Resolution helper (AST-631):** `resolved_agent_content` in `src/core/agent.py`.
- **Chain token exclusion:** `get_manage_tasks_chain_tokens()` in `src/utils/config.py` (source `"chain"` in `TOKEN_SOURCES`).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `get_manage_agents_tokens()` | utils |
| `src/ui/api/api_admin.py` | `GET /agents/meta/tokens`; `POST /agents/preview` | ui |
| `src/ui/frontend/src/pages/AdminAgentPrompts.tsx` | `TokenTextarea`, token load, preview modal, candidate context | ui |

No changes to `TokenTextarea.tsx` (reuse as-is).

## Stage 1: Agent token meta + preview API

**Done when:** `GET /api/admin/agents/meta/tokens` returns sorted token names excluding chain/hop tokens; `POST /api/admin/agents/preview` accepts draft `content` + optional `candidate_id` and returns `{ candidate_id, content }` with tokens resolved via `resolved_agent_content`; both routes require admin auth and return 400 with `{ "error": "..." }` on invalid candidate (same pattern as task preview).

1. In `src/utils/config.py`, immediately after `get_manage_tasks_chain_tokens()` (~line 2952), add:

```python
def get_manage_agents_tokens() -> list:
    """Sorted Manage Agents picker tokens — registry minus chain/hop tokens (AST-632)."""
    chain = set(get_manage_tasks_chain_tokens())
    return sorted(k for k in get_tokens() if k not in chain)
```

2. In `src/ui/api/api_admin.py`:
   - Add `get_manage_agents_tokens` to the existing import from `src.utils.config` (same block as `get_tokens`, `get_manage_tasks_chain_tokens`).
   - Add `resolved_agent_content` to the existing import from `src.core.agent` (same line as `_chain_context`, `resolved_task_system`).

3. Register **`GET /agents/meta/tokens`** after the existing `/agents/brain_settings` route (~line 117):

```python
@admin_bp.route("/agents/meta/tokens")
@require_admin
def agent_tokens():
    """Manage Agents picker: all registry tokens except chain/hop (AST-632)."""
    return jsonify(get_manage_agents_tokens())
```

4. Add a small helper **above** the new preview route (same file, near other agent routes):

```python
def _resolve_agent_preview_candidate(candidate_id: str):
    """Candidate row + candidate_data for agent preview (mirrors preview_task_prompt fallback)."""
    if candidate_id:
        candidate = database.get_candidate(candidate_id)
        if not candidate:
            raise ValueError(f"Candidate not found: {candidate_id}")
    else:
        candidates = database.list_candidates()
        if not candidates:
            raise ValueError("No active candidate found for preview.")
        candidate = candidates[0]
    cd = candidate.get("candidate_data") or {}
    cid = candidate.get("astral_candidate_id") or candidate_id
    return cid, cd
```

   ⚠️ **Decision:** Use `database.get_candidate` / `database.list_candidates` (already imported in `api_admin.py`) instead of importing `src.core.candidate` — preview only needs `candidate_data`, not job/chain simulation.

5. Register **`POST /agents/preview`** after `/agents/meta/tokens`:

```python
@admin_bp.route("/agents/preview", methods=["POST"])
@require_admin
def preview_agent():
    body = request.get_json(silent=True) or {}
    content = body.get("content")
    if content is None:
        return jsonify({"error": "content is required"}), 400
    candidate_id = (body.get("candidate_id") or "").strip()
    try:
        cid, cd = _resolve_agent_preview_candidate(candidate_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    agent_row = {"content": content}
    resolved = resolved_agent_content(agent_row, cd, "manage_agents_preview", None)
    return jsonify({"candidate_id": cid, "content": resolved})
```

   ⚠️ **Decision:** **POST with draft `content`** (not GET by `agent_id`) so preview works in add/edit modals **before save**, matching authoring flow for AC5. `task_key` sentinel `"manage_agents_preview"` — agent templates use candidate/config tokens only; no job context in Manage Agents preview (same as list token estimates in AST-631).

6. Run `python3 -m py_compile src/utils/config.py src/ui/api/api_admin.py`.

## Stage 2: Manage Agents UI — TokenTextarea + preview

**Done when:** Add and Edit modals use `TokenTextarea` with tokens from `/api/admin/agents/meta/tokens`; Edit modal has **Preview Resolved** button opening a read-only modal showing server-resolved text for the global selected candidate; Save/POST/PUT still send literal `content` unchanged; Add modal has the same preview button (draft content via POST preview).

1. In `src/ui/frontend/src/pages/AdminAgentPrompts.tsx`, add imports:

```typescript
import { useCandidate } from "../contexts/CandidateContext"
import TokenTextarea from "../components/TokenTextarea"
```

2. At module scope (after `LIST_COLUMNS`), add a one-line helper mirroring Manage Tasks naming:

```typescript
/** Agent template picker: registry minus chain/hop tokens (AST-632). */
function useAgentTokenList(): string[] {
  const [tokenList, setTokenList] = useState<string[]>([])
  useEffect(() => {
    api("/api/admin/agents/meta/tokens")
      .then(r => r.json())
      .then(data => setTokenList(Array.isArray(data) ? data : []))
      .catch(() => setTokenList([]))
  }, [])
  return tokenList
}
```

   ⚠️ **Decision:** Load tokens via dedicated `/agents/meta/tokens` (Stage 1) — do **not** client-merge `tasks/meta/tokens` + `chain_tokens`; server owns exclusion rules.

3. Inside `AgentPrompts` (default export component):
   - Call `const { selectedId } = useCandidate()` and `const tokenList = useAgentTokenList()` (or inline the fetch in existing `useEffect` if you prefer one load hook — keep a single `tokenList` state).
   - Add preview state:

```typescript
const [previewOpen, setPreviewOpen] = useState(false)
const [previewLoading, setPreviewLoading] = useState(false)
const [previewText, setPreviewText] = useState("")
const [previewCandidateId, setPreviewCandidateId] = useState("")
const [previewSource, setPreviewSource] = useState<"edit" | "add">("edit")
```

4. Add `function handlePreview(source: "edit" | "add")`:
   - Set `previewSource`, `previewLoading = true`.
   - `content` = `source === "edit" ? editContent : addContent`.
   - `POST /api/admin/agents/preview` with JSON `{ content, candidate_id: selectedId || undefined }`.
   - On success: set `previewText` from `data.content`, `previewCandidateId` from `data.candidate_id`, open preview modal.
   - On error: toast with `e.message` (same as other handlers).
   - `finally`: `previewLoading = false`.

5. **Edit modal** — replace the System Prompt Content `<textarea>` (~lines 255–264) with:

```tsx
<TokenTextarea
  className="dep-input"
  value={editContent}
  onChange={setEditContent}
  tokens={tokenList}
  rows={20}
  placeholder="Agent system prompt — type {$ to insert merge tokens."
/>
<div style={{ marginTop: 8, display: "flex", alignItems: "center", gap: 8 }}>
  <button
    className="dep-btn cancel"
    type="button"
    onClick={() => handlePreview("edit")}
    disabled={previewLoading}
    style={{ fontSize: 12, padding: "5px 12px" }}
  >
    {previewLoading && previewSource === "edit" ? "Loading..." : "Preview Resolved"}
  </button>
  <span style={{ fontSize: 11, color: "var(--text-secondary)" }}>
    Resolves tokens for the selected candidate (draft text)
  </span>
</div>
```

6. **Add modal** — same replacement for add content textarea (~lines 288–297), with `handlePreview("add")` and `previewSource === "add"` loading label.

7. **Preview modal** — after the Delete confirm modal, before `<Toast>`:

```tsx
<Modal
  open={previewOpen}
  onClose={() => setPreviewOpen(false)}
  title={`Preview${previewCandidateId ? `: ${previewCandidateId}` : ""}`}
>
  <pre style={{
    margin: 0, padding: 12, borderRadius: 4,
    background: "var(--bg-deep)", border: "1px solid var(--border)",
    color: "var(--text-primary)", fontFamily: "monospace", fontSize: 12,
    whiteSpace: "pre-wrap", wordBreak: "break-word",
    maxHeight: 500, overflow: "auto",
  }}>
    {previewText || "(empty)"}
  </pre>
</Modal>
```

   No Save button on preview modal — display only (`Modal` without `onSave` or with close-only; match `AdminTaskPrompts` preview modal which omits save).

8. Verify manually (build-child smoke):
   - `cd src/ui/frontend && npm run build` (must pass).
   - Edit agent with `{$FIRST_NAME}` in content → Preview shows resolved name for selected candidate.
   - Save → reload edit → textarea still shows literal `{$FIRST_NAME}`.

## Stage 3: Betty verification targets (manifest — not implemented in this ticket)

**Done when:** Betty's `qa-child` manifest covers parent AC4 and AC5 for Manage Agents.

Suggested coverage (Betty-owned):

| AC | Suggested test |
|----|----------------|
| AC4 — autocomplete excludes chain tokens | Component test: mock `/agents/meta/tokens` without `SELECTED_AGENT` / `CALLER_*`; assert `TokenTextarea` dropdown does not offer them |
| AC5 — preview + storage | Mock POST preview returns resolved text; save PUT sends literal template; reload GET returns literal template |

Extend `tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx` — do **not** edit in build-child.

## Self-Assessment

**Scope — Single-Component:** One admin page (`AdminAgentPrompts.tsx`) plus thin utils/API glue (`get_manage_agents_tokens`, two admin routes). No core resolution logic (AST-631).

**Conf — high:** Direct mirror of Manage Tasks `TokenTextarea` + preview patterns; AST-631 `resolved_agent_content` already on ftr; token exclusion reuses existing `get_manage_tasks_chain_tokens()`.

**Risk — low:** Admin-only authoring surface; save path unchanged (literal `content` in PUT/POST); preview is read-only POST with no DB writes.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Status |
|------|--------|
| §1.3 DRY | Reuses `TokenTextarea`, `resolved_agent_content`, `get_manage_tasks_chain_tokens` — no duplicate resolution |
| §2.1 config | Token list derived from `TOKEN_SOURCES` via new helper; no hardcoded token names in React |
| §3.3 imports | `api_admin` → `core.agent` + `utils.config` (existing patterns) |
| §3.5 naming | Page stays `AdminAgentPrompts.tsx` in `pages/`; flat components import |

No conflicts requiring `conf-!!-NONE`.
