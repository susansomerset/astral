# AST-2250 — Railway variable client

Linear: [AST-2250](https://linear.app/astralcareermatch/issue/AST-2250/railway-variable-client-manage-candidate-secrets-in-railway)
Parent: [AST-2246](https://linear.app/astralcareermatch/issue/AST-2246/manage-candidate-secrets-in-railway)
Publish ref: `sub/AST-2246/AST-2250-railway-variable-client`

Write, delete, and deploy-trigger for one Astral service variable, plus the candidate-secret catalog and the env names that point at Railway and at the local stubs. The running process does not read secrets back from Railway. Candidate rows, Admin UI, hydrate, migration, and the CSE client stay on later siblings.

## Scope check

This ticket's Scope names only:

- `src/external/railway.py` — new — upsert, delete, and deploy trigger for one service variable
- `src/utils/config.py` — modified — Railway project / environment / service / token env names, and the candidate-secret catalog (id → variable name shape, local stub env name)
- `env.example` — modified — names only for those Railway ids and local stubs; no secret values

Parent AC 2 ("component test of Admin set" plus a database write of status and expiry) spans this client and later siblings. This plan does not add Admin, database, or test files. Betty's later component test of the client is what this child can satisfy: one upsert and one deploy trigger, and no secret value in the log line.

`src/utils/config.py` already has `RAILWAY_CONFIG` for gunicorn (`workers`, `threads`, `timeout`, `access_log_quiet_paths`), read by `scripts/start_server.py`. Do not add keys to that dict.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `CANDIDATE_SECRET_RAILWAY_CONFIG`, `CANDIDATE_SECRET_CATALOG`, `candidate_secret_variable_name`, `candidate_secret_local_stub_env`, and the import-time asserts. One line in the module docstring section list. | utils |
| `env.example` | Comment the new Railway target names and the local stub names. No values. | config |
| `src/external/railway.py` | New module: upsert one variable, delete one variable, trigger one deploy. No read query. | external |

## Stage 1: Catalog and env names

**Done when:** Importing `src.utils.config` exposes the Railway target env names and one catalog row per LLM server plus the two search secrets, and `candidate_secret_variable_name("anthropic", "ada-1")` returns `CANDIDATE_ADA_1_ANTHROPIC`. `env.example` lists the new names and does not assign them.

1. In the module docstring section list at the top of `src/utils/config.py`, add one bullet after the existing `RAILWAY_CONFIG` gunicorn line: `CANDIDATE_SECRET_RAILWAY_CONFIG` / `CANDIDATE_SECRET_CATALOG` — Railway target env names and candidate-secret catalog (AST-2250). Do not edit the gunicorn `RAILWAY_CONFIG` block.

2. Immediately after `TIMESHEET_SEARCH_SERVER_ID = "google_cse"`, add:

```python
# AST-2250 — Railway write target. Readers use os.environ[CANDIDATE_SECRET_RAILWAY_CONFIG[…]]
# at call time (no .get). Not RAILWAY_CONFIG (that dict is gunicorn).
CANDIDATE_SECRET_RAILWAY_CONFIG = {
    "graphql_url": "https://backboard.railway.com/graphql/v2",
    "token_env": "ASTRAL_RAILWAY_TOKEN",
    "project_id_env": "ASTRAL_RAILWAY_PROJECT_ID",
    "environment_id_env": "ASTRAL_RAILWAY_ENVIRONMENT_ID",
    "service_id_env": "ASTRAL_RAILWAY_SERVICE_ID",
}

# id → production variable-name shape + local stub env name.
# production_suffix is appended after the sanitized candidate id.
# Local runs share one stub env per secret id for every candidate (sibling hydrate).
CANDIDATE_SECRET_CATALOG = {
    "anthropic": {
        "production_suffix": "ANTHROPIC",
        "local_stub_env": "CANDIDATE_SECRET_STUB_ANTHROPIC",
    },
    "kimi": {
        "production_suffix": "KIMI",
        "local_stub_env": "CANDIDATE_SECRET_STUB_KIMI",
    },
    "openrouter": {
        "production_suffix": "OPENROUTER",
        "local_stub_env": "CANDIDATE_SECRET_STUB_OPENROUTER",
    },
    "deepseek": {
        "production_suffix": "DEEPSEEK",
        "local_stub_env": "CANDIDATE_SECRET_STUB_DEEPSEEK",
    },
    "google_cse_api_key": {
        "production_suffix": "GOOGLE_CSE_API_KEY",
        "local_stub_env": "CANDIDATE_SECRET_STUB_GOOGLE_CSE_API_KEY",
    },
    "google_cse_id": {
        "production_suffix": "GOOGLE_CSE_ID",
        "local_stub_env": "CANDIDATE_SECRET_STUB_GOOGLE_CSE_ID",
    },
}


def candidate_secret_variable_name(secret_id: str, candidate_id: str) -> str:
    """Production Railway variable name for one candidate secret. No I/O."""
    row = CANDIDATE_SECRET_CATALOG.get(secret_id)
    if row is None:
        raise ValueError(
            f"Unknown candidate secret {secret_id!r}. Valid: {list(CANDIDATE_SECRET_CATALOG)}"
        )
    raw = (candidate_id or "").strip()
    if not raw:
        raise ValueError("candidate_id is required")
    token = "".join(ch if ch.isascii() and ch.isalnum() else "_" for ch in raw.upper())
    return f"CANDIDATE_{token}_{row['production_suffix']}"


def candidate_secret_local_stub_env(secret_id: str) -> str:
    """Env name of the shared local stub for this secret id. No I/O."""
    row = CANDIDATE_SECRET_CATALOG.get(secret_id)
    if row is None:
        raise ValueError(
            f"Unknown candidate secret {secret_id!r}. Valid: {list(CANDIDATE_SECRET_CATALOG)}"
        )
    return row["local_stub_env"]


assert set(CANDIDATE_SECRET_CATALOG) == set(LLM_SERVER_CONFIG) | {"google_cse_api_key", "google_cse_id"}
assert len({row["local_stub_env"] for row in CANDIDATE_SECRET_CATALOG.values()}) == len(CANDIDATE_SECRET_CATALOG)
assert len({row["production_suffix"] for row in CANDIDATE_SECRET_CATALOG.values()}) == len(CANDIDATE_SECRET_CATALOG)
```

3. In `env.example`, after the existing `# RAILWAY_TOKEN=...  # operator machine only — never commit` line, add a comment block. Leave that existing Joan CLI comment unchanged. New lines are comments only — do not assign values:

```
# Candidate secrets on the Astral service (AST-2250). Product client reads these
# with os.environ[...] at call time. Not the operator RAILWAY_TOKEN above.
# ASTRAL_RAILWAY_TOKEN=
# ASTRAL_RAILWAY_PROJECT_ID=
# ASTRAL_RAILWAY_ENVIRONMENT_ID=
# ASTRAL_RAILWAY_SERVICE_ID=
# Local stubs: one shared value per secret id for every candidate. Names only.
# CANDIDATE_SECRET_STUB_ANTHROPIC=
# CANDIDATE_SECRET_STUB_KIMI=
# CANDIDATE_SECRET_STUB_OPENROUTER=
# CANDIDATE_SECRET_STUB_DEEPSEEK=
# CANDIDATE_SECRET_STUB_GOOGLE_CSE_API_KEY=
# CANDIDATE_SECRET_STUB_GOOGLE_CSE_ID=
```

⚠️ **Decision:** Catalog ids for the LLM servers are the `LLM_SERVER_CONFIG` keys, matching today's `candidate_api_keys` map. Search is two ids (`google_cse_api_key`, `google_cse_id`) because the engine id is not an LLM server key. Local stubs are new `CANDIDATE_SECRET_STUB_*` names so they do not alias the process-wide `GOOGLE_CSE_*` / `ANTHROPIC_API_KEY` lines already in `env.example`.

## Stage 2: Railway variable client

**Done when:** `src/external/railway.py` imports, and a caller can upsert one named variable, delete one named variable, and trigger one deploy of the configured service. None of the three functions issue a variables query. A failed call logs one `logger.exception` line that does not contain the secret value or the token, then raises `RailwayCallFailed`.

1. Create `src/external/railway.py`. Import `os`, `requests`, `require_controlled_external_io` from `src.utils.integration_io`, `get_logger` from `src.utils.logging`, and `CANDIDATE_SECRET_RAILWAY_CONFIG` from `src.utils.config`. `logger = get_logger(__name__)`. Timeout constant `_POST_TIMEOUT_SEC = 30`. Do not import candidate, database, or CSE modules.

2. `class RailwayCallFailed(RuntimeError)`. Its message is the operation and the variable name only (`railway upsert failed for CANDIDATE_ADA_1_ANTHROPIC`, or `railway deploy failed` when there is no variable name). Never the value, the token, or the response body.

3. Module-level GraphQL strings, copied from Railway CLI `v4.58.0` `src/gql/mutations/strings/`:

- Upsert (collection upsert of a one-key object so `skipDeploys` is set):

```graphql
mutation VariableCollectionUpsert($projectId: String!, $serviceId: String!, $environmentId: String!, $variables: EnvironmentVariables!, $skipDeploys: Boolean) {
  variableCollectionUpsert(
    input: {projectId: $projectId, environmentId: $environmentId, serviceId: $serviceId, variables: $variables, skipDeploys: $skipDeploys}
  )
}
```

- Delete (`VariableDelete.graphql` — this mutation has no `skipDeploys` argument):

```graphql
mutation VariableDelete($projectId: String!, $environmentId: String!, $name: String!, $serviceId: String) {
  variableDelete(
    input: {projectId: $projectId, environmentId: $environmentId, name: $name, serviceId: $serviceId}
  )
}
```

- Deploy (`ServiceInstanceDeploy.graphql`):

```graphql
mutation ServiceInstanceDeploy($environmentId: String!, $serviceId: String!) {
  serviceInstanceDeployV2(environmentId: $environmentId, serviceId: $serviceId)
}
```

4. Private `_redact(text, *secrets) -> str`: replace each non-empty secret with `[redacted]`. Private `_post(query, variables, *, operation, variable_name, secret_value)`:
   - `require_controlled_external_io(f"railway.{operation}")`.
   - Read `token`, `project_id`, `environment_id`, and `service_id` with `os.environ[CANDIDATE_SECRET_RAILWAY_CONFIG["…"]]`. Do not catch `KeyError`. Do not log it here.
   - `requests.post` to `CANDIDATE_SECRET_RAILWAY_CONFIG["graphql_url"]` with JSON `{"query": query, "variables": variables}`, header `Authorization: Bearer {token}` and `Content-Type: application/json`, timeout `_POST_TIMEOUT_SEC`.
   - On `requests` failure or HTTP status >= 400: `logger.exception` once (below), then `raise RailwayCallFailed(...) from None`. Do not log `resp.text`. The logged exception string is status code only for HTTP errors (`HTTP 401`), redacted with `_redact` against `secret_value` and `token`.
   - On JSON `errors`: join `errors[].message`, redact, then the same `logger.exception` + `RailwayCallFailed` path. Do not return those messages to the caller.
   - Log shape (stat.logging.error — one handler line, facts, next step, traceback; no secret material):

```python
logger.exception(
    "railway %s | variable %s\n  %s: %s\n  The Railway call did not finish",
    operation,
    variable_name or "-",
    type(exc).__name__,
    _redact(str(exc), secret_value, token),
)
```

   - Do not `logger.warning` for these failures. Do not `print`. Do not log and also let the original exception propagate. `from None` so the chained HTTP body is not on `RailwayCallFailed`.
   - Success returns `payload["data"]`. No info log.

5. `upsert_service_variable(*, name: str, value: str) -> None`. Blank `name` or blank `value` (`not (name or "").strip()` or `value is None` or `value == ""`) raises `ValueError` before any HTTP call and does not log. POST the collection-upsert mutation with `variables` set to `{name: value}` (one key), `skipDeploys: true`, and the four ids from environ. Require `data["variableCollectionUpsert"] is True`; otherwise the same log-and-`RailwayCallFailed` path. Return `None`.

6. `delete_service_variable(*, name: str) -> None`. Blank `name` raises `ValueError` with no log and no HTTP. POST the delete mutation. Require `data["variableDelete"] is True`; otherwise log and raise `RailwayCallFailed`. Return `None`.

7. `trigger_service_deploy() -> str`. POST the deploy mutation (no variable name, `secret_value=""`). Require `data["serviceInstanceDeployV2"]` to be a non-empty `str`. Return that deployment id. Do not log the id.

8. `__all__` = `upsert_service_variable`, `delete_service_variable`, `trigger_service_deploy`, `RailwayCallFailed`.

⚠️ **Decision:** Upsert goes through `variableCollectionUpsert` with a one-key map and `skipDeploys: true`, not `variableUpsert`. Railway redeploys on variable changes by default; the parent pipeline wants one explicit `serviceInstanceDeployV2` after the write. The public delete mutation has no `skipDeploys` argument, so delete does not send one. Callers (later siblings) still call `trigger_service_deploy` after delete. This module does not combine write and deploy into one function.

⚠️ **Decision:** These three functions are the handler for Railway faults. Later siblings catch `RailwayCallFailed` and do not log that exception again. A missing `ASTRAL_RAILWAY_*` env var stays a bare `KeyError` from `os.environ[...]` (hard read, not logged here). `stat.logging.warning` (SET secret missing from the process environment, who + secret id, not the value) is the hydrate sibling, not this module.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-2250
**Overall:** APPROVED
**Corpus:** 65a2864973ecf09fd57732c2cfc9a4e1ff3e0b91
**Publish ref:** `sub/AST-2246/AST-2250-railway-variable-client` @ `55beb00ed9f74a472315e7c9978881d35923f2cd`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.error | A | | |
| stat.logging.warning | A | | |
| new candidate-secret pattern (pending Archie) | B | | |

## Traceability

`2 → Stage 2 (upsert/delete/deploy, no read-back, skipDeploys + explicit deploy); Scope check — full Admin component test + DB status-only write land on later siblings; this child supplies the Railway client Betty can exercise`

## Findings

### discuss — Canon Scope gap

- **Severity:** discuss
- **Location:** Linear Citations vs plan footprint (`config.py`, `railway.py`, `env.example`)
- **Finding:** `astral.config.config-source-of-truth`, `astral.config.secrets-and-env-specific-from-environ`, and `astral.layers.import-direction` plainly govern catalog placement, hard `os.environ[…]` reads, and `external → utils` imports; they are not on this child’s frozen Citations list.
- **Recommendation:** Archie may widen parent Canon Scope at Discussion for Radia comparability; do not insert ids on this pass. Plan behavior already matches those statutes (catalog literals in `config.py`, secrets read at call time in `railway.py`, no forbidden layer imports).

### discuss — Pattern not in corpus

- **Severity:** discuss
- **Location:** Parent Architectural definition / Citations
- **Finding:** The candidate-secret Railway + status/hydrate pattern is cited as “pending Archie” and has no `canon/patterns/**` file yet; epic children already depend on the parent’s proposed text.
- **Recommendation:** Track Archie approval before treating the pattern as in-force law; the plan text matches the parent proposal (no read-back, deploy after write, local stub names distinct from process-wide `GOOGLE_CSE_*` / provider keys).

### acceptable — Parent AC 2 is cross-child

- **Severity:** acceptable
- **Location:** Plan `## Scope check`
- **Finding:** Child AC quotes parent AC 2 (Admin component test + DB write); this ticket correctly does not add Admin, database, or test files.
- **Recommendation:** None — boundary is explicit and faithful to dispatch partition.

### acceptable — No formal conf/self-assessment block

- **Severity:** acceptable
- **Location:** Plan `## Estimate`
- **Finding:** Plan confirms estimate 5 only; no `conf:` axes.
- **Recommendation:** Optional polish for larger plans; not blocking here.

context_tokens≈32000

[plan-rubric] PROCEED (Commit: 55beb00) Railway client plan ready
