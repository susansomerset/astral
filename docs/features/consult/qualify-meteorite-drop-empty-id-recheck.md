# qualify_meteorite — drop empty `company_job_id` re-check

Fix plan / pre-diff. Not a Linear child. Also: subject title fallback, land JD fallback, empty-link leftover bind.

Schema already allows omit / `null` / `""` (`required: False`, AST-1127). Consult `process` must not fail the row when resolve returns empty. Title/JD floors stay, but use stored email subject / land body when Ruth left those fields short. Empty-link leftover rows bind by order so fabricated `astral_job_id` does not `error_state` a good extract.

## Stay / go


| Keep                                                                              | Drop / add                                                                          |
| --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `_resolve_company_job_id` (fill from UUID in `job_link` when Ruth omitted the id) | `if not company_job_id and not is_email_link: fail_reason = "empty company_job_id"` |
| Bot classify → `BOT_BLOCKED`                                                      | Failing QUALIFY solely because the id is blank                                      |
| `min_job_title_length` / `min_jd_chars` after fallbacks                           | Inventing `email-` / changing land `job_link`                                       |
| `initialize_job` (empty id is already a legal save)                               | Agent / schema / prompts                                                            |


Empty id + usable title + JD → `METEORITE_QUALIFIED`, `company_job_id=""`. Identity collision still only runs when both id and title are non-empty (`tracker._identity_triple_complete`).

## Product pre-diff

`**qualify_meteorite.process**` (`src/core/consult.py`):

- Delete the empty-id fail branch and `is_email_link`.
- Before length gates: if Ruth title is short and email subject meets `min_job_title_length`, use subject. If Ruth `jd_text` is short and land `job_description` meets `min_jd_chars`, use land body.
- Then title/JD floors; bot still first after those fills.

`**_bind_unmatched_empty_link_jobs_by_order**` (new): after digit bind + link bind, leftover unmatched claims with empty `job_link` zip to leftover response rows when counts match. Called from `_run_batch_consult` qualify_meteorite branch only. Count mismatch still → omitted/`error_state`. Claims that still have a `job_link` are not order-bound.

`email_prefix` stays for the link-source cascade. Comment-only on `email_link_prefix` in `config.py`.

**Unchanged:** assemble, `_resolve_company_job_id`, subject scrape helper (now consumed), `initialize_job`, agent schema, `run_land_meteorite`.

## Tests


| Lock                                                                            | Change                                                                                |
| ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| `TestAst1062QualifyMeteorite::test_content_gates_fail_state`                    | Short title + short land+Ruth JD only (empty land JD so land fallback cannot rescue). |
| `TestAst1062QualifyMeteorite::test_empty_company_job_id_qualifies`              | New pass.                                                                             |
| `TestAst1120…::test_empty_ai_no_uuid_qualifies_with_empty_id`                   | Replaces empty-id fail.                                                               |
| `TestAst1197…::test_empty_title_uses_email_subject_and_qualifies`               | New.                                                                                  |
| `TestAst1197…::test_short_ruth_jd_uses_land_body_and_qualifies`                 | New.                                                                                  |
| `TestAst1133Bind…::test_empty_link_leftovers_bind_by_order`                     | New helper.                                                                           |
| `TestAst1133Qualify…::test_empty_link_fabricated_ids_bind_by_order_and_qualify` | New batch.                                                                            |


## Check

```bash
.venv/bin/python3 -m pytest \
  tests/component/core/test_consult.py::TestAst1062QualifyMeteorite \
  tests/component/core/test_consult.py::TestAst1120CompanyJobIdFallback \
  tests/component/core/test_consult.py::TestAst1127QualifyMeteoriteOmitCompanyJobId \
  tests/component/core/test_consult.py::TestAst1197QualifyMeteoriteApply \
  tests/component/core/test_consult.py::TestAst1133BindResponseJobsByJobLink \
  tests/component/core/test_consult.py::TestAst1133QualifyMeteoriteListCreated \
  -q
```

