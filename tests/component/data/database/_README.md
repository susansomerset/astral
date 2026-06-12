# `database.py` component clusters (AST-392)

Public API lives on `src.data.database`. Cluster files under this directory map to table groups in the module header inventory.

| Cluster file | Tables / focus |
| --- | --- |
| `test_schema.py` | `table_columns`, `apply_config_table_upsert`, encryption helpers |
| `test_companies.py` | `company` |
| `test_jobs.py` | `job` |
| `test_candidates.py` | `candidate` |
| `test_agents.py` | `agent` |
| `test_agent_tasks.py` | `agent_task` |
| `test_agent_data.py` | `agent_data` |
| `test_agent_responses.py` | `agent_responses` |
| `test_company_job_scans.py` | `company_job_scan` |
| `test_timesheets.py` | `timesheets` |
| `test_dispatch_tasks.py` | `dispatch_task` |
| `test_dispatch_ledger.py` | `dispatch_ledger` |
| `test_app_log.py` | `app_log` |
| `test_state_helpers.py` | batch helpers, score floors, legacy wrappers |

Adjust boundaries only with a Linear note and this file.
