# App and routes

**Test tree:** `tests/component/root/`

## Coverage map

Vitest tests live under **`tests/component/frontend/`** (mirror `components/`, `pages/`, `contexts/`, `lib/`, and higher-level **`test_App`** / **`test_routes`** as needed).

There is **no** per-source-file branch-lock table (**§6b**). Prefer adding or extending tests beside the modules they guard. Coverage artifacts land in **`tests/.coverage/frontend/`** when `./scripts/testing/run_component_tests.sh` runs the Vitest **coverage** target.

---

### AST-649 · AST-648 (historical — SUNSET AST-757)

**Historical (AST-649):** Candidate **Board Searches** nav/route/page retired; **`gaze_board`** hidden from Admin Scheduled Actions APIs. Backend boards module and **`/api/boards`** removed **AST-765**; schema dropped **AST-766**. No active boards manifest. See **`docs/ASTRAL_CODE_RULES.md` §3.7**.
