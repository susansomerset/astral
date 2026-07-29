# AST-879 — vet inflow discovery prompt redraft

<!-- linear-archive: AST-879 archived 2026-07-29 -->

## Linear archive (AST-879)

**Archived:** 2026-07-29  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-879/vet-inflow-discovery-prompt-redraft  
**Status at archive:** Archive  
**Project:** Astral Consult  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Roster inflow already records discovery hits as NEW companies and runs a separate `vet_inflow_discovery` step before website fetch. The current Admin prompt still speaks in `slug`/`ignore` JSON results, which is coarse and out of step with how other consult tasks return compact encoded payloads. This epic redrafts the vet contract so the model grades each discovery hit with an A–F link-type rubric, always returns company-website metadata (including on F), and only **F** fails the vet gate — **D** still passes to prefilter for later disqualification. Outcome: clearer mechanical triage at NEW, better homepage capture for non-homepage company hits, and an encoded response shape Susan can UAT like other encoded consult work.

## Functional scope

1. **Link-type rubric (replace slug/ignore).** The `vet_inflow_discovery` Admin prompt instructs the model to classify each discovery hit with exactly one Result Finding letter:
   * **A** — hit URL is a company homepage
   * **B** — hit URL is a deeplink on a company site (e.g. product page)
   * **C** — hit URL is a company-hosted blog/post on that company's site
   * **D** — hit is external to any one company but may still be worth parsing for a company pointer
   * **F** — unrelated / information-only / unlikely pointer to a pursue-able company site (wiki, directories, news-only, BBB, job boards, social profiles, and similar)
     Candidate-fit, industry preference, company quality, and role match remain forbidden at this step (still later pipeline, including prefilter for **D**).
2. **Encoded response contract.** Live content stays the existing pipe lines (`index|title|url|snippet`, including batch `000`/`001`/… indexing). The model responds with the product's standard outer JSON envelope and a **compact encoded** `agent_payload` (one encoded line per input hit), not a JSON `results[]` of `action: slug|ignore` objects. Decode still maps each hit back to its claimed company row by index.
3. **Website metadata on every hit.** For every graded hit — including **F** — the encoded line carries a company homepage URL (best official site the model can infer; may differ from the discovery URL). Empty website is not the success path for any grade.
4. **State outcomes from the grade (locked).** After decode:
   * **A / B / C / D** → **WEBSITE_FOUND** (record returned website)
   * **F** → **VET_FAILED** (rejected; URL not re-pursued on later discovery)
     **D** is intentionally allowed through this gate; prefilter (not vet) disqualifies external/unwanted **D** material later.
5. **Admin prompt + local seed.** Update the current `vet_inflow_discovery` Admin Task Prompt (and the local-dev seed/migration path the team already uses for this task) so UAT and fresh DBs see the new rubric and encoded instructions — not the AST-776 slug/ignore text.
6. **Debug traceability.** When `debug=True` on the vet path, Susan can see per-hit index headers and working detail for grade, website, and recorded state (AST-538 / Code Rules §1.5.1 style — found and recorded, not batch totals only).

## Boundaries

* Does **not** change `inflow_discovery` CSE search, hit recording, or NEW-only ingest.
* Does **not** rename company `short_name` from the vet response (DNS-label-without-TLD at ingest is deferred / out of scope here).
* Does **not** add candidate-fit / prefilter logic to vet (still `prefilter_company`, including **D** handling).
* Does **not** redesign `inflow_resolve_website`, `fetch_website`, or later job-page chain steps beyond consuming the website vet writes on pass.
* Does **not** introduce new company states or retire WEBSITE_FOUND / VET_FAILED.
* Does **not** require UI work beyond whatever Admin Task Prompts already expose for prompt text.
* Config-driven task/prompt wiring stays the source of truth (Code Rules §2.1); no parallel hard-coded prompt bodies in core beyond the established seed/migration pattern for this task.

## Acceptance criteria

1. Running `vet_inflow_discovery` against NEW companies with discovery blurbs uses the new Admin prompt text: A–F Result Finding rubric present; slug/ignore mechanical-only text gone.
2. Model output for a successful vet call is a compact encoded `agent_payload` (one line per input hit index), accepted by the task's decode path into per-hit grade + website.
3. For a controlled UAT batch, each returned hit (including **F**) shows a non-empty website metadata field in debug and/or Admin response view.
4. Grades **A/B/C/D** transition **NEW → WEBSITE_FOUND** with `company_website` set to the returned homepage; grade **F** transitions **NEW → VET_FAILED**.
5. Downstream `fetch_website` remains reachable after WEBSITE_FOUND; rejected (**F**) URLs still are not re-recorded on later discovery runs (AST-776 behavior preserved).
6. With `debug=True`, per-hit index + working detail shows grade, website, and recorded state for the batch Susan runs in UAT.

## Dependencies and blockers

none — builds on shipped AST-776 / AST-822 vet dispatch. No open sibling blockers on Astral Consult.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-879 (parent) | ftr/AST-879-vet-inflow-discovery-prompt-redraft |
| AST-880 | sub/AST-879/AST-880-encoded-af-link-type-vet |

**Epic worktree:** `astral-AST-879/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | 571511bb-f408-4a2d-ad30-54cc2a49f515 |
| Betty | qa | 1eb16e4b-2dcc-4bbe-a832-2ad40418ad27 |
| Radia | review | b276fff9-45f7-460a-95bb-aaadf969dfe9 |

---

## Original brief

## MECHANICAL LINK-TYPE VET ONLY ([AST-776](https://linear.app/astralcareermatch/issue/AST-776/vet-inflow-discovery-company-dispatch-and-mechanical-prompt-vet-inflow))

You vet a single discovery hit for roster inflow. Live content is one pipe line:

`index|title|url|snippet`

## Mechanical scope only

Reject (`action: "ignore"`) link types that are not useful for downstream job-page search:
news/articles, Wikipedia, directories/listicles, Better Business Bureau listings, job-board posts, social profiles.

Do **not** filter for candidate fit, industry preference, company quality, or role match — that belongs in later pipeline steps.

## Response

Use the standard two-key JSON envelope. In `agent_payload`, return:

```json
{"results": [{"hit_index": 0, "action": "slug"|"ignore", "website": "<homepage URL when slug>"}]}
```

* `action: "ignore"` — wrong page type; omit website or leave empty.
* `action: "slug"` — plausibly a company we can pursue for job listings; set `website` to the best official company homepage (may differ from the discovery hit URL).

```

I think we should redraft this to support encoded responses, and use this rubric:
Result Finding
A = This is a homepage url for a company website
B = This is a deeplink on a company website, like a product page.
C = This is a hosted blog post from the company website
D = This is content external to any particular company, may be worth parsing
F = This is an unrelated result, like a wiki page, information-only, etc., unlikely pointer to a company website for our candidate.

Have it return the main website link metadata in all conditions. 
Also, the short name should drop the .com or .org part, just slug the main dns name (between www and .com/org/gov)
```

### Comments

#### chuckles — 2026-07-12T22:33:32.480Z
@susan
1. Letter → state: A/B/C → WEBSITE_FOUND and D/F → VET_FAILED OK, or rewrite (esp. C and D)?
2. On fail grades, must website always be filled, or empty OK?
3. Returned short_name vs existing NEW row key: rename, only-if-empty, or metadata-only (no rename)?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
