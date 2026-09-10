# AST-465 — Table Data Upsert from JSON: Data Management UI and admin API

**Linear:** [AST-465](https://linear.app/astralcareermatch/issue/AST-465/table-data-upsert-from-json-data-management-ui-and-admin-api)  
**Parent:** [AST-373 — Table Data Upsert from JSON](https://linear.app/astralcareermatch/issue/AST-373/table-data-upsert-from-json)  
**Sibling contract:** [AST-464](https://linear.app/astralcareermatch/issue/AST-464/table-data-upsert-from-json-generic-upsert-data-layer-and-core) — core module `apply_copy_output_table_upsert` (see **`docs/features/administrator/ast-464-table-data-upsert-from-json-generic-upsert-data-layer-and-core.md`** on **`origin/sub/AST-373/AST-464-table-data-upsert-from-json-generic-upsert-data-layer-and-core`**)  
**Feature ref:** `ftr/AST-465` (origin only — orientation-astral § Branch law)

## Summary

Replaces **Backfill Culture Links** on the Data Management admin page with **Table Upsert**: a table picker (every user-visible table listing, same discovery query as today’s schema browser), an **Update** button that opens a modal with a large JSON paste field, **`window.confirm`** before apply, and a new **`POST /api/admin/data/table_copy_upsert`** route that **`@require_auth`** wraps thinly around **`apply_copy_output_table_upsert`** from **`src.core.table_copy_upsert`** so Susan can paste Copy Output rows from another environment and receive **inserted / updated / skipped** counts from the **`ok: true`** path or actionable **`error`** text from validation / FK failures with **zero** rows committed on failure (**AST-464**).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_admin.py` | Add `POST /api/admin/data/table_copy_upsert`; import `apply_copy_output_table_upsert` from **`src.core.table_copy_upsert`** (group with other **`src.core`** imports — follow existing alphabetical / section grouping); **keep** `/api/admin/script/backfill_culture_links/*` Flask routes untouched (dead from UI perspective; Betty may remove elsewhere) | ui |
| `src/ui/frontend/src/pages/AdminDataManagement.tsx` | Remove backfill JSX + hooks + **`BackfillCompany`**/`api` polling; add Table Upsert card + **`Modal`** + **`runSql`/API wiring** for table dropdown + **`table_copy_upsert`** POST handling + toasts | ui |
| `src/ui/frontend/src/App.css` | Optional TOC + rules only if **`Modal`/textarea** clipping requires it (reuse **`modal-*`**/`dep-input` patterns first — add lines only when default layout fails) | ui |

**Betty-owned (explicit handoff — do not edit in build-astral):** `tests/component/frontend/pages/test_AdminDataManagement.test.tsx` must drop mocks and assertions for **`/api/admin/script/backfill_culture_links/*`** once the UI no longer renders **Backfill Culture Links** (`[qa-handoff]` comment at **Code Complete**).

---

## Preflight blocker (STOP without guessing — build-astral step 4)

After **`dev-kath`** is rebased onto **`origin/dev`** and **`origin/ftr/AST-465`** is merged (plan-astrals Step 4 + 4a), **`build-astral`** must run only when **`origin/dev`** includes **AST-464** (**`blockedBy`** in Linear; typical order: Ada **Review Posted** → Katherine **Plan Approved** / build). Before **Stage 1** code:

1. Confirm **`python3`** can import **`from src.core.table_copy_upsert import apply_copy_output_table_upsert`** from repo root **`src/`** PYTHONPATH parity that **`python src/ui/server.py`** uses (`build-astral` **`py_compile`** on changed files validates syntax).
2. Confirm function signature **`apply_copy_output_table_upsert(*, table_name: str, json_payload: str) -> dict[str, Any]`** and return mapping **`ok`**, **`inserted`**, **`updated`**, **`skipped`**, **`error`** (**None** vs absent when **`ok`** per actual **`AST-464`** implementation — inspect **`table_copy_upsert.py`** and match Flask JSON shape literal-for-literal).

If module or signature mismatches **`AST-464` plan excerpt** (`## Stage 3: agent_task … 3b` return shape section) → **STOP**: Linear comment **`🛑`** on **`AST-373`** per execution contract.

---

## Stage 1: Flask admin endpoint

**Done when:** `curl`/browser POST with Bearer token succeeds on happy path (**200**, counts) and rejects empty table / missing body (**400**) without touching **`require_ip`**.

1. **`api_admin.py`:** add **`from src.core.table_copy_upsert import apply_copy_output_table_upsert`** next to sibling **`src.core`** imports (**do not import `src.data`** in UI layer).

2. After **`run_sql`** in the **Data Management** section (**before **`upsert_config_table`****, same auth story), declare:

```
@admin_bp.route("/data/table_copy_upsert", methods=["POST"])
@require_auth
def admin_table_copy_upsert():
```

3. **`body = request.get_json(silent=True) or {}`**. **`table = (body.get("table") or "").strip()`**; **`json_payload = body.get("json_payload")`**.

4. If **`not table`** → **`return jsonify({"ok": False, "error": "table is required"}), 400`** (mirror count keys if **`AST-464`** guarantees them only on **`ok`** — omit zero counts vs include zeros consistently with consumer below; **`AST-465` UI reads only `inserted`/`updated`/`skipped` when **`ok`** from core).

5. If **`json_payload is None`** (key missing entirely) → **400**, **`{"ok":false,"error":"json_payload is required"}`**.

6. If **`not isinstance(json_payload, str)`** → **400**, **`{"ok":false,"error":"json_payload must be a JSON text string — paste Copy Output verbatim"}`** (Copy Output pasted into **`textarea`** still travels as **`string`** nested inside HTTP JSON body).

7. Call **`result = apply_copy_output_table_upsert(table_name=table, json_payload=json_payload)`**.

8. Return **`jsonify(result)`**. Use HTTP **400 whenever `result["ok"] is False`** (admin-visible validation/FK/engine errors); reserve **500** only if **`apply_copy_output_table_upsert` raises** (**unexpected**) — Flask handler catches **`Exception`** → rollback not needed at UI (**core owns transaction**) → **`return jsonify({"ok":False,"error":str(e)})`, 500** so Susan sees traceback text only until hardened.

⚠️ **Decision:** **No duplicated **`json.loads`** in Flask — all semantics live in **`table_copy_upsert`** per **§3.3** layer separation.

**Ritual:** **`python3 -m py_compile src/ui/api/api_admin.py`**; **`dev-kath`** commit **`feat(AST-465): …`** (exact subject wording per **build-astral**); cherry-pick publish **`origin/ftr/AST-465`**.

---

## Stage 2: Remove Backfill UI + scaffolding

**Done when:** `AdminDataManagement.tsx` renders no **Backfill Culture Links**, no **`/api/admin/script/backfill_culture_links` calls**, TypeScript **`tsc` clean**.

1. Delete **`interface BackfillCompany`** and all **backfill prefixed** **`useState`**, **`useRef`**, **`useEffect`**, **`fetchBackfillCompanies`**, **`handleBackfill`**, JSX block (**lines spanning “Backfill culture links section”** through closing wrapper **`</div>`** before flex row with Schema browser).

2. Remove **`confirm("Backfill`** usage.

⚠️ **Decision:** Leaving **`api_admin`** backfill routes avoids engineer-owned **`tests/component/ui/api`** churn; **`Betty`** updates **`AdminDataManagement` component test only** (`[qa-handoff]`).

**Ritual:** **`feat(AST-465): …`**; publish.

---

## Stage 3: Table Upsert UX + **`Modal`** + wire-up

**Done when:** User selects a table → **Update** opens a wide modal (`size="wide"`) with a monospace textarea (**rows ≥ 16**, **width `"100%"`**) → **Save** ensures a non-empty paste → **`window.confirm("Apply JSON upsert into table \"${table}\"? Unrelated rows remain untouched.")`** → **`POST /api/admin/data/table_copy_upsert`** → success **Toast** (`variant="success"`) lists inserted / updated / skipped counts; **`ok: false` or HTTP error** → **`Toast variant="error"`** with **`error`** text; on success optionally clear **`upsertJson`** and close modal.

1. **`state` additions:** **`upsertTable`**, **`upsertModalOpen`**, **`upsertJson`**, **`upsertPosting`**.

2. **Table dropdown:** Reuse **`tables`** from the schema **`useEffect`** that calls **`runSql`** with **`SELECT name FROM sqlite_master WHERE type='table' ORDER BY name`**. Bind a **second `<select>`** to **`upsertTable`** only (**`selectedTable`** stays for sidebar column browsing). ⚠️ **Decision:** Single SQL fetch — no duplicate state for names.

3. Placeholder row **— select table —** with **`value=""`**.

4. **Update:** opens modal (**`setUpsertModalOpen(true)`**); button **`disabled`** when **`!upsertTable.trim() || upsertPosting`**.

5. **`import Modal`** from **`../components/Modal`**. Pass **`title={`Upsert rows — ${upsertTable}`}`**, **`size="wide"`**, **`dirty={upsertJson.trim().length > 0}`**, **`open={upsertModalOpen}`**. **`onClose`** must reset modal-visible state **without** leaving **`upsertPosting` stuck **`true`** (close should clear busy when safe or after terminal toast).

6. **`onSave`** (modal footer Save): **`if (!upsertJson.trim())`** → Toast error **`Paste JSON rows first.`** → **`return`**. **`if (upsertPosting) return`**. **`setUpsertPosting(true)`**; **`try`/`finally`**: **`window.confirm`**; **`POST`** body **`JSON.stringify({ table: upsertTable.trim(), json_payload: upsertJson })`** via **`api(...)`**; **`const data = await r.json()`**; if **`!r.ok || data.ok === false`** throw **`new Error(...)`** from **`data.error`**; otherwise Toast success **`Upsert completed: inserted …, updated …, skipped …`** using numeric **`inserted`, `updated`, `skipped`** from **`data`**; **`finally`** **`setUpsertPosting(false)`**.

⚠️ **Decision:** **`Modal` does not `await`** async handlers — **`onSave` must **`void`-invoke an **`async`** IIFE or named **`handleApply`** that performs the awaits.

7. **Errors:** same **`catch`** Toast pattern as **`handleRun`** (**`Toast` **`variant="error"`**, message **`(e as Error).message`**).

**`App.css`** only if QA finds modal overflow clipping.

**Ritual:** **`feat(AST-465): …`** **`tsc`**, **`py_compile`** for touched **`py`**; publish.

---

## Execution contract

- **§464 only through import** — no edits **`database.save_agent_task`** / **`table_copy_upsert`** on **`AST-465`**.
- Blocking ambiguity → **`🛑`** on **`AST-373`** quoting step + **`AST-465` plan**.
- **`build-astral`** **one Linear id per cherry-picked commit** strictly.

---

## Self-Assessment

**Scope:** `Single-Component` — One Flask route + one-page React refactor (admin Data Management shell only); **`core`/`data`** authored under **`AST-464`**.

**Conf:** `Medium` — Written contract (**`apply_copy_output_table_upsert`** return shape + kwargs) ships on **`AST-464`** (**`origin/sub/AST-373/AST-464-table-data-upsert-from-json-generic-upsert-data-layer-and-core`**); preflight on **`dev`** blocks surprises; **`Modal`** / **`Toast`** / **`runSql`** patterns match other admin screens.

**Risk:** `HIGH` — Wrong HTTP/body shaping or swallowed errors could confuse Susan during cross-environment merges; transactional safety stays in **`AST-464`** — this ticket must faithfully surface **`ok`** and **`error`** and HTTP status.

---

## Self-review vs ASTRAL_CODE_RULES

| Section | Alignment |
|---------|-----------|
| §1.3 DRY | Reuses **`runSql`/schema table list`; no second table-discovery SQL path unless **`tables`** state proves insufficient. |
| §2.1 Config | No new config keys — endpoints under existing admin auth. |
| §3.3 Imports | Flask imports **`src.core.table_copy_upsert`** only — **never** **`src.data`** from **`api_admin`**. |
| §3.5 Naming | `AdminDataManagement.tsx` under flat **`pages/`**; **`snake_case`** path **`/api/admin/data/table_copy_upsert`**; reuse shared **`Modal`** |

No **`conf-!!-NONE`**.

---

## Build record

**Built by Katherine.** Publish ref `sub/AST-373/AST-465-table-data-upsert-from-json-data-management-ui-and-admin-api`. Product commits: `b6c69025` (Flask route), `f4ced60e` (Data Management UI). Preflight: sibling `origin/sub/AST-373/AST-464-table-data-upsert-from-json-generic-upsert-data-layer-and-core` merged onto `dev-kath` before implementation.

---

## Review

**Baseline:** `origin/dev` … `origin/sub/AST-373/AST-465-table-data-upsert-from-json-data-management-ui-and-admin-api` (tip reviewed: `724310b9`; doc commit replaces only this appendix).

### What’s solid

- Flask `POST /api/admin/data/table_copy_upsert` matches the staged plan (body validation for `table` / `json_payload` type string, **`apply_copy_output_table_upsert`** delegate, **`400` when `ok` false**, **`500` on unexpected raises). Imports stay **ui → core** only (**§3.3** — no **`src.data`** in **`api_admin`**).
- **`AdminDataManagement`**: Backfill Culture Links UI and polling removed; table list reuses **`tables`** from **`sqlite_master`** discovery; **`Modal`** + dirty guard + async **`Save`** (**`void` IIFE**) + **`window.confirm`** + success/error **Toast** align with **`## Stage 3`** and **HIGH** operational risk mitigation.
- Tests: **`test_api_admin`** covers HTTP validation, mocked core **`ok`** branches, exception → **500**; frontend **`AdminDataManagement`** covers upsert UX, **`ok:false`**, SQL error regression without backfill mocks.

### Issues

| Severity   | Bucket / rule                         | Finding |
|-----------|----------------------------------------|---------|
| *none*    |                                        | No **fix-now** items versus **§3** / **`ASTRAL_CODE_RULES`** or plan boundaries. |

### Recommended actions

| Severity   | Action |
|-----------|--------|
| Advisory  | Optionally distinguish **invalid JSON** in the Flask body (**`silent=True`** today becomes empty dict → generic **400**) with an explicit parse error — admin-only ergonomics; not required for sign-off. |

**Linear summary:** **`fix-now`** 0, **`discuss`** 0, **`advisory`** 1 (optional JSON-parse clarity). Boundary check: no **AST-381** export scope; upsert engine stays in sibling **AST-464** (**import-only**).

---

## Resolution

**2026-05-24 — Katherine (`resolve-astral`, Astral Administrator, parent AST-373):**

1. **Advisory — HTTP envelope JSON malformed:** **`admin_table_copy_upsert`** no longer folds **`request.get_json(silent=True)`** parse failures into **`{}`** when the client sends a non‑empty **`application/json`** body (Flask **`request.is_json`**). Parse failure → **`400`**, **`{"ok": false, "error": "Request body must be valid JSON."}`**, instead of misleading **`table is required`**. **Copy-output row JSON** parsing remains only in **`src.core.table_copy_upsert`** (plan Stage 1).
2. **Defense in depth:** Top-level decoded value must be a **JSON object**; a bare array or scalar → **`400`** with **`Request body must be a JSON object with table and json_payload fields.`** so **`.get(...)`** paths stay safe without touching **`tests/`** this pass (**happy-path resolve → User Testing**).

---
