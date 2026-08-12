# AST-988 — Integration tests are failing on GitHub

<!-- linear-archive: AST-988 archived 2026-08-05 -->

## Linear archive (AST-988)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-988/integration-tests-are-failing-on-github  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

GitHub Actions is red on the integration harness because a scenario still seeds the retired candidate state `NEW` after the candidate state registry renamed the early-lifecycle value to `NEW_CANDIDATE`. This epic restores a green GHA integration harness only.

**Orchestration (Susan 2026-07-27):** GHA runs the harness. Joan’s prior Railway post-deploy operator role has been repurposed — not a deliverable of this ticket. Betty ownership of ongoing integration-test monitoring (agent content + skills) is a **separate** Team Chuckles project ticket (AST-989), not in scope here.

## Functional scope

1. Make the candidate nav integration scenario use a **valid** early-lifecycle candidate state from the current registry so the “Jobs group hidden” assertion still holds without raising on save.
2. Confirm the full integration harness (all scenarios in that entry point) is green under the same conditions GitHub Actions uses.

## Boundaries

* Does **not** change the candidate state registry, transition rules, or nav_config product behavior beyond what the scenario already asserts.
* Does **not** add new integration scenarios or expand coverage beyond fixing registry drift.
* Does **not** document dual runners, rewrite Betty agent/skills, or change Joan operator automation (separate Team Chuckles ticket).
* Does **not** enable live external I/O or run against production.
* Must not break existing component-test / Vitest gates; this epic is integration-tier only.

## Acceptance criteria

1. GitHub Actions **Integration tests** job is green on the landed fix (harness exit 0; no invalid-state errors).
2. The nav scenario still proves: with an early-lifecycle candidate state from the live registry, the Jobs nav group is absent; with the seeded active-search candidate, Jobs / in-review stays enabled.

## Dependencies and blockers

none. (Registry rename already on `dev`; that is the cause of the red, not a blocker.)

## Open questions

none.

## Proposed child tickets

| # | Working title | What it delivers | Agent | Sequencing |
| -- | -- | -- | -- | -- |
| 1 | Align integration nav scenario with current candidate states | Restores green harness: early-lifecycle seed uses a registry-valid state that still hides the Jobs group; no product behavior change. Betty commits the test-tree change via qa. | Ada | — |

**Monolith check:** Functional scope N=2, proposed children M=1 — one inseparable harness fix (scenario + green entry point); intentional single child.

**New patterns:** none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-988 (parent) | ftr/AST-988-integration-tests-are-failing-on-github |
| AST-990 | sub/AST-988/AST-990-align-integration-nav-scenario-with-current-candidate-states |

**Epic worktree:** `astral-AST-988/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | f53ed507-05bd-4ac4-8bf2-30b8fca6bc4f |
| Betty | qa | 4f15b0c8-628c-45f8-b4a7-68c5bf57446b |
| Radia | review | 6d50ca06-6ce8-4f0d-8f7d-01c48421f440 |

---

## Original brief

Tell me how and who is orchestrating the integration tests?  Is this missing from our workflow?

```
2026-07-27T21:48:08.6526468Z ##[group]Run ./scripts/testing/run_integration_tests.sh
2026-07-27T21:48:08.6527453Z [36;1m./scripts/testing/run_integration_tests.sh[0m
2026-07-27T21:48:08.6604946Z shell: /usr/bin/bash -e {0}
2026-07-27T21:48:08.6605512Z env:
2026-07-27T21:48:08.6606065Z   pythonLocation: /opt/hostedtoolcache/Python/3.12.13/x64
2026-07-27T21:48:08.6606966Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.12.13/x64/lib/pkgconfig
2026-07-27T21:48:08.6607850Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.13/x64
2026-07-27T21:48:08.6608637Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.13/x64
2026-07-27T21:48:08.6609427Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.13/x64
2026-07-27T21:48:08.6610227Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.12.13/x64/lib
2026-07-27T21:48:08.6610934Z ##[endgroup]
2026-07-27T21:48:23.6034447Z 
2026-07-27T21:48:23.6035413Z [notice] A new release of pip is available: 25.0.1 -> 26.1.2
2026-07-27T21:48:23.6036266Z [notice] To update, run: python3.12 -m pip install --upgrade pip
2026-07-27T21:48:24.9402297Z ============================= test session starts ==============================
2026-07-27T21:48:24.9403572Z platform linux -- Python 3.12.13, pytest-9.1.1, pluggy-1.6.0
2026-07-27T21:48:24.9404309Z rootdir: /home/runner/work/astral/astral
2026-07-27T21:48:24.9404845Z configfile: pytest.ini
2026-07-27T21:48:24.9405361Z plugins: cov-7.1.0, anyio-4.14.2, asyncio-1.4.0
2026-07-27T21:48:24.9406354Z asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
2026-07-27T21:48:24.9407348Z collected 3 items
2026-07-27T21:48:24.9407649Z 
2026-07-27T21:48:26.6988878Z tests/integration/scenarios/test_candidate_nav_api.py .F.                [100%]
2026-07-27T21:48:26.6989674Z 
2026-07-27T21:48:26.6990030Z =================================== FAILURES ===================================
2026-07-27T21:48:26.6991528Z _______________ test_nav_config_reflects_seeded_candidate_state ________________
2026-07-27T21:48:26.6992085Z 
2026-07-27T21:48:26.6992385Z integration_app = <Flask 'tests.integration.conftest'>
2026-07-27T21:48:26.6993545Z seeded_candidate = <module 'src.data.database' from '/home/runner/work/astral/astral/src/data/database.py'>
2026-07-27T21:48:26.6994830Z auth_headers = {'Authorization': '***'}
2026-07-27T21:48:26.6995135Z 
2026-07-27T21:48:26.6995573Z     def test_nav_config_reflects_seeded_candidate_state(
2026-07-27T21:48:26.6996113Z         integration_app: Flask,
2026-07-27T21:48:26.6996518Z         seeded_candidate,
2026-07-27T21:48:26.6996882Z         auth_headers: dict[str, str],
2026-07-27T21:48:26.6997269Z     ) -> None:
2026-07-27T21:48:26.6997614Z         client = integration_app.test_client()
2026-07-27T21:48:26.6998206Z         resp = client.get("/api/nav_config?candidate_id=cand-1", headers=auth_headers)
2026-07-27T21:48:26.6999384Z         assert resp.status_code == 200
2026-07-27T21:48:26.6999835Z         payload = resp.get_json()
2026-07-27T21:48:26.7000314Z         jobs = _jobs_group(payload)
2026-07-27T21:48:26.7000775Z         assert jobs is not None
2026-07-27T21:48:26.7001388Z         in_review = next(item for item in jobs["items"] if item["path"] == "/jobs/in_review")
2026-07-27T21:48:26.7002073Z         assert in_review["enabled"] is True
2026-07-27T21:48:26.7002480Z     
2026-07-27T21:48:26.7002843Z         # ACTIVE_SEARCH satisfies Jobs group visible gate; NEW would hide the whole group.
2026-07-27T21:48:26.7003777Z >       seeded_candidate.save_candidate("cand-1", state="NEW", candidate_data={"name": "Integration Test"})
2026-07-27T21:48:26.7004185Z 
2026-07-27T21:48:26.7004363Z tests/integration/scenarios/test_candidate_nav_api.py:43: 
2026-07-27T21:48:26.7004771Z _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
2026-07-27T21:48:26.7005155Z src/data/database.py:3067: in save_candidate
2026-07-27T21:48:26.7005458Z     _run_with_retry(_with_conn)
2026-07-27T21:48:26.7005729Z src/data/database.py:259: in _run_with_retry
2026-07-27T21:48:26.7006004Z     return fn()
2026-07-27T21:48:26.7006473Z            ^^^^
2026-07-27T21:48:26.7006748Z _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
2026-07-27T21:48:26.7007002Z 
2026-07-27T21:48:26.7007110Z     def _with_conn() -> None:
2026-07-27T21:48:26.7007389Z         conn = _get_connection()
2026-07-27T21:48:26.7007637Z         try:
2026-07-27T21:48:26.7007869Z             _ensure_candidate_schema(conn)
2026-07-27T21:48:26.7008174Z             existing = conn.execute(
2026-07-27T21:48:26.7008657Z                 "SELECT astral_candidate_id, state, candidate_data FROM candidate WHERE astral_candidate_id = ?",
2026-07-27T21:48:26.7009166Z                 (astral_candidate_id,),
2026-07-27T21:48:26.7009449Z             ).fetchone()
2026-07-27T21:48:26.7009676Z     
2026-07-27T21:48:26.7009899Z             if existing is None:
2026-07-27T21:48:26.7010154Z                 if not state:
2026-07-27T21:48:26.7010476Z                     raise ValueError("state required for new candidate")
2026-07-27T21:48:26.7010893Z                 allowed = list(CANDIDATE_STATES.keys())
2026-07-27T21:48:26.7011208Z                 if state not in allowed:
2026-07-27T21:48:26.7011638Z                     raise ValueError(f"Invalid candidate state '{state}'. Must be one of: {allowed}")
2026-07-27T21:48:26.7012174Z                 cdata_str = json.dumps(candidate_data) if candidate_data else "{}"
2026-07-27T21:48:26.7012567Z                 conn.execute(
2026-07-27T21:48:26.7013134Z                     """INSERT INTO candidate (astral_candidate_id, state, candidate_data, candidate_api_key, created_at, updated_at, state_changed_at)
2026-07-27T21:48:26.7013950Z                        VALUES (?, ?, ?, ?, ?, ?, ?)""",
2026-07-27T21:48:26.7014367Z                     (astral_candidate_id, state, cdata_str, encrypted_key, now, now, now),
2026-07-27T21:48:26.7014772Z                 )
2026-07-27T21:48:26.7014978Z             else:
2026-07-27T21:48:26.7015191Z                 sets: List[str] = []
2026-07-27T21:48:26.7015466Z                 params: List[Any] = []
2026-07-27T21:48:26.7015750Z                 if state is not None:
2026-07-27T21:48:26.7016069Z                     allowed = list(CANDIDATE_STATES.keys())
2026-07-27T21:48:26.7016396Z                     if state not in allowed:
2026-07-27T21:48:26.7016843Z >                       raise ValueError(f"Invalid candidate state '{state}'. Must be one of: {allowed}")
2026-07-27T21:48:26.7018672Z E                       ValueError: Invalid candidate state 'NEW'. Must be one of: ['NEW_CANDIDATE', 'INTAKE_INITIATED', 'REQUIRED_TOPICS_READY', 'REQUIRED_TOPICS_READY_STALE', 'ALL_TOPICS_READY', 'ALL_TOPICS_READY_STALE', 'REQUESTED_RESUME', 'REQUESTED_RESUME_RETRY', 'REQUESTED_RESUME_ERROR', 'RESUME_READY', 'RESUME_READY_STALE', 'REQUESTED_ARTIFACTS', 'REQUESTED_ARTIFACTS_RETRY', 'REQUESTED_ARTIFACTS_ERROR', 'ARTIFACTS_READY', 'ARTIFACTS_READY_STALE', 'ACTIVE_SEARCH', 'PAUSE_SEARCH', 'INACTIVE', 'DELETED']
2026-07-27T21:48:26.7020504Z 
2026-07-27T21:48:26.7020625Z src/data/database.py:3036: ValueError
2026-07-27T21:48:26.7020981Z =========================== short test summary info ============================
2026-07-27T21:48:26.7023144Z FAILED tests/integration/scenarios/test_candidate_nav_api.py::test_nav_config_reflects_seeded_candidate_state - ValueError: Invalid candidate state 'NEW'. Must be one of: ['NEW_CANDIDATE', 'INTAKE_INITIATED', 'REQUIRED_TOPICS_READY', 'REQUIRED_TOPICS_READY_STALE', 'ALL_TOPICS_READY', 'ALL_TOPICS_READY_STALE', 'REQUESTED_RESUME', 'REQUESTED_RESUME_RETRY', 'REQUESTED_RESUME_ERROR', 'RESUME_READY', 'RESUME_READY_STALE', 'REQUESTED_ARTIFACTS', 'REQUESTED_ARTIFACTS_RETRY', 'REQUESTED_ARTIFACTS_ERROR', 'ARTIFACTS_READY', 'ARTIFACTS_READY_STALE', 'ACTIVE_SEARCH', 'PAUSE_SEARCH', 'INACTIVE', 'DELETED']
2026-07-27T21:48:26.7025521Z ========================= 1 failed, 2 passed in 1.70s ==========================
2026-07-27T21:48:26.8522688Z ##[error]Process completed with exit code 1.
```

### Comments

#### chuckles — 2026-07-28T04:01:28.063Z
[check-linear] PR Ready — [wrap]/finish-up owns retry (Chuckles stays assignee)

#### susan — 2026-07-28T04:00:59.620Z
@chuckles Try now?

#### chuckles — 2026-07-28T03:35:36.622Z
[thread-missing] blocked: Cursor chat session for `5ef6e276-c743-4d2c-851d-8896a07abb55` is not on this host (chuckles). Expected: `/home/susan/.cursor/chats/40f37617870e538aada0246cb9f8c346/5ef6e276-c743-4d2c-851d-8896a07abb55/store.db`. Run this job from **Susan's MacBook (laptop)** where that conversation exists.

Do **not** `agent create-chat` or `--resume` here — that forks a new thread the other host cannot use.

Watcher rule `wrap` on `AST-988`.

@susan — run this orchestration from your laptop.

— Chuckles

#### susan — 2026-07-28T02:47:19.005Z
@chuckles Try Again, please.

#### chuckles — 2026-07-28T01:08:04.225Z
[thread-missing] blocked: Cursor chat session for `8bf72022-b47e-4f62-bc1a-dfc6a64883fe` is not on this host (chuckles). Expected: `/home/susan/.cursor/chats/40f37617870e538aada0246cb9f8c346/8bf72022-b47e-4f62-bc1a-dfc6a64883fe/store.db`. Run this job from **Susan's MacBook (laptop)** where that conversation exists.

Do **not** `agent create-chat` or `--resume` here — that forks a new thread the other host cannot use.

Watcher rule `wrap` on `AST-988`.

@susan — run this orchestration from your laptop.

— Chuckles

#### chuckles — 2026-07-27T22:37:33.641Z
[check-linear] Todo — new Thread conversation; Chuckles assignee for datt resume

#### susan — 2026-07-27T22:28:36.034Z
@Chuckles we lost the thread on this for some reason (separate bug to address), for now, please spawn a new conversation and move directly to Todo to resume your work.

#### chuckles — 2026-07-27T22:24:14.213Z
[thread-missing] blocked: Cursor chat session for `2f96bb3a-9e52-4b2a-80a0-b832afadc55f` is not on this host (chuckles). Expected: `/home/susan/.cursor/chats/40f37617870e538aada0246cb9f8c346/2f96bb3a-9e52-4b2a-80a0-b832afadc55f/store.db`. Run this job from **Susan's MacBook (laptop)** where that conversation exists.

Do **not** `agent create-chat` or `--resume` here — that forks a new thread the other host cannot use.

@susan — run this orchestration from your laptop.

— Chuckles

#### chuckles — 2026-07-27T22:19:53.387Z
[check-linear] Discussion — open questions closed; green-harness scope; AST-989 filed (@susan)

#### susan — 2026-07-27T22:15:08.027Z
@chuckles answers: GHA runs it, Joan has been repurposed, but create a team chuckle project ticket in linear to make sure Betty is monitoring the integration tests as we go, and the deliverable for that ticket is an update to the Betty agent content and skills.  

Just green harness for this ticket.

#### chuckles — 2026-07-27T21:55:12.677Z
@susan

1. Keep **both** GHA CI and Joan’s Railway post-deploy gate, or retire one?
2. Scope: **(A)** green harness only, or **(B)** green harness + orchestration doc child?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
