# AST-1685 — View related meteorite record data on recommended job modal

<!-- linear-archive: AST-1685 archived 2026-10-02 -->

## Linear archive (AST-1685)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1685/view-related-meteorite-record-data-on-recommended-job-modal  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Operators reviewing a Recommended meteorite job need the staging-row provenance that produced it — when it arrived, what link or inbox breadcrumb it carried, and what the AI classified/assembled — without leaving the Recommended Job Report modal for Manage Email or a raw DB peek. This epic surfaces the **related** `meteorite` **record** (AST-1557 spine) on that modal so timestamps, links, and AI-discerned fields are scannable next to Summary / Analysis / Artifacts / Discussion. Meteorites that still participate in an existing job are **not** purged by retention, so the pane can read the live row (no job-side snapshot).

## Functional scope

* On the Recommended Job Report modal, when a related `meteorite` staging row exists for the open job, operators can open a **Meteorite** top tab (config-driven, same shell as Discussion) and read that row’s provenance.
* The Meteorite pane shows **timestamps** from the staging row: at least `created_at`, `updated_at`, and `state_changed_at` (and `estelle_notified_at` when set).
* The Meteorite pane shows **link / breadcrumb** from `meteorite.link` (http(s) posting URL or inbox breadcrumb text). Http(s) values are navigable; non-http breadcrumbs render as plain text (same honesty as Job Detail “open listing”).
* The Meteorite pane shows **AI-discerned content** from the staging row only: `classify_outcome` and `content`. Read-only. Does **not** pull company-stem discernment or agent-story / qualify RESPONSE blocks (those stay on company/job Summary and Discussion).
* Supporting provenance on the same pane: `id`, `state`, `source_kind`, `source_id`, and `error` when present.
* When no related meteorite row is found for the job, the Meteorite top tab is **omitted** (not an empty tab). Gazed-only recommended jobs stay on the existing four tabs.
* **Lookup** uses today’s reverse link `meteorite.astral_job_id` → job (not blocked on AST-1640 `source_entity_*`).
* **Retention:** LANDED purge must **not** delete a meteorite row whose `astral_job_id` still points at an existing job row. Rows with null/blank `astral_job_id`, or whose job no longer exists, remain eligible for the existing age-based LANDED purge. No snapshot onto `job_data`.
* Does **not** change stage/scrape/land/qualify runners, Manage Email, Job Detail Agent Story, or implement AST-1640 parentage.

## Component scope

* `src/core/meteorite.py` — **modified** — `run_meteorite_retention` (or its purge selection) skips LANDED rows that still reference an existing job via `astral_job_id`.
* `src/data/database.py` — **modified** — (1) retention list/select helper adjustment if the skip is cleaner in SQL than in the runner; (2) read helper that returns the `meteorite` row for a given `astral_job_id`; header inventory for both.
* `src/utils/config.py` — **modified** — register Meteorite on `JOBS_RECOMMENDED_REPORT_TOP_TABS` (after Discussion); expose Meteorite pane section defs on the recommended-report UI manifest; retention config comment/assert only if a new literal is required (prefer behavior change without new magic numbers).
* `src/ui/api/api_system.py` — **modified** — attach Meteorite section defs on the jobs.recommended manifest surface.
* `src/ui/api/api_jobs.py` — **modified** — on `GET /api/jobs/<id>`, attach `related_meteorite` (object or `null`) from the reverse-link helper — only the fields named below.
* `src/ui/frontend/src/contexts/StateUiContext.tsx` — **modified** — type the new top-tab / Meteorite section manifest fields.
* `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` — **modified** — wire Meteorite top-tab pane when `related_meteorite` is present; omit the tab when null.
* `src/ui/frontend/src/components/JobMeteoritePane.tsx` — **new** — read-only Meteorite pane (ReportSectionList / CollapsiblePanel).
* `src/ui/frontend/src/App.css` — **modified** only if Meteorite needs report-local chrome beyond existing recommended-report classes.

## Technical scope

* `run_meteorite_retention` / retention helpers: before delete, exclude LANDED ids where `astral_job_id` is set and `get_job(astral_job_id)` (or equivalent EXISTS) returns a row; keep age cutoff for the remaining LANDED set.
* `database.py`: new read helper keyed by `astral_job_id` → one meteorite row or none; optional retention query tightening if owned here rather than in the runner loop.
* `config.py`: append `{tab_id: meteorite, nav_label: Meteorite}` to `JOBS_RECOMMENDED_REPORT_TOP_TABS`; ordered Meteorite section list (timestamps, link, AI `classify_outcome`+`content`, provenance `id`/`state`/`source_kind`/`source_id`/`error`).
* `api_system.py`: surface Meteorite section defs on the recommended-report manifest.
* `api_jobs.py`: after job detail assembly, attach `related_meteorite` flat object or `null`; log once at the completing route.
* `JobAnalysisReportModal`: `related_meteorite` on job detail type; `activeTopTab === "meteorite"` → `JobMeteoritePane`; filter top tabs so Meteorite appears only when payload non-null.
* `JobMeteoritePane`: map manifest sections to payload; http(s) `link` as href; otherwise plain text; read-only.

## Architectural definition

* **Patterns to reuse** — `no established pattern applies` for a read-only Recommended-report provenance pane. Follow the in-tree Recommended Job Report convention (config-driven `JOBS_RECOMMENDED_REPORT_TOP_TABS` + ReportSectionList / CollapsiblePanel, peer to AST-1541 Discussion). Retention skip is a criteria tweak on the existing retention runner, not a new claim arc — still no batch-processing pattern invent.
* **New patterns proposed** — none.
* **Applicable statutes** —
  * [`stat.logging.info.api`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.api.md>) — job detail route attaching `related_meteorite` logs once at the completing route.
  * [`stat.logging.info.entity`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.entity.md>) — retention skip/purge outcomes stay id-pipe entity info when the runner already info-logs state changes.
  * [`stat.logging.debug`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>) — hydrate/retention debug detail stays ContextVar-gated.
  * [`stat.logging.error`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md>) — lookup/route/retention handler failures log once with traceback.

## Acceptance criteria

1. Opening a Recommended job that has a `meteorite` row with matching `astral_job_id` shows top tabs Summary | Analysis | Artifacts | Discussion | **Meteorite**. Fail: Meteorite missing when such a row exists, or Meteorite appears for a job with no related row.
2. `GET /api/jobs/<id>` JSON includes `related_meteorite` with at least `id`, `created_at`, `updated_at`, `state_changed_at`, `link`, `classify_outcome`, `content`, `state`, `source_kind`, `source_id` when the reverse link hits; otherwise `null`. Fail: field absent, or object present when no row matches.
3. Meteorite pane timestamps match the staging row’s `created_at` / `updated_at` / `state_changed_at` (and `estelle_notified_at` when non-null). Fail: wrong values vs the row, or timestamps omitted when set.
4. When `meteorite.link` starts with `http://` or `https://`, the pane exposes a navigable href; otherwise plain text (not an href). Fail: non-http breadcrumb treated as href, or http link not clickable.
5. AI section shows `classify_outcome` and `content` only from the meteorite row (read-only) — no agent-story blocks and no company-stem fields required in this pane. Fail: stem/story content required for AC, values differ from the row, or section editable.
6. `grep` / manifest: Meteorite is on `JOBS_RECOMMENDED_REPORT_TOP_TABS` and section list comes from config/manifest, not a TSX-only tab array. Fail: label/order invented only in React.
7. Given a LANDED meteorite older than `landed_purge_days` whose `astral_job_id` still resolves to a job row, one retention run does **not** delete that meteorite id. Fail: row deleted while the job still exists.
8. Given a LANDED meteorite older than `landed_purge_days` with null `astral_job_id` or a missing job, retention may still purge it under existing age rules. Fail: all LANDED rows become immortal regardless of job link.
9. Stage/scrape/land/qualify runners and Manage Email are unchanged except the retention skip above. Fail: land/email paths edited for display.

## Open questions

none

## Proposed child tickets

#### 1!: **Retention skip for job-linked meteorites - Ada**

Exempt LANDED meteorite rows that still reference an existing job from age-based purge so Recommended provenance can stay on the live row. Does not own report API/UI (#2–#3).
**Citations:** `stat.logging.info.entity`, `stat.logging.debug`, `stat.logging.error`.
**Scope:** `src/core/meteorite.py` (`run_meteorite_retention` skip); `src/data/database.py` (retention helper adjustment only if SQL-side EXISTS is used); `src/utils/config.py` (only if a new retention literal/assert is required).
**Estimate: 2**

#### 2!: **Meteorite lookup + report config/API - Hedy**

Add `astral_job_id` → meteorite read helper, register Meteorite on recommended top tabs + section manifest, attach `related_meteorite` on job GET. Does not own retention (#1) or React pane (#3).
**Citations:** `stat.logging.info.api`, `stat.logging.debug`, `stat.logging.error`.
**Scope:** `src/data/database.py` (read helper + header inventory); `src/utils/config.py` (Meteorite top tab + section defs); `src/ui/api/api_system.py` (manifest sections); `src/ui/api/api_jobs.py` (`related_meteorite` on detail).
**Estimate: 3**

#### 3: **Meteorite pane on Recommended modal - Katherine**

Wire Meteorite top tab + read-only `JobMeteoritePane`; omit tab when `related_meteorite` is null. After #2.
**Citations:** none — presentational React only; API/logging statutes owned by #2.
**Scope:** `src/ui/frontend/src/contexts/StateUiContext.tsx`; `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`; `src/ui/frontend/src/components/JobMeteoritePane.tsx`; `src/ui/frontend/src/App.css` (only if needed).
**Estimate: 2** — after #2.

**Monolith check:** Functional scope has 8 capabilities; 3 children — OK (retention vs API vs React).

**Scope partition check:** Every Component/Technical item appears in exactly one child Scope block (`database.py` split: retention helper vs read helper; `config.py` split: retention literals vs report tabs — each child lists only its slice).

---

## Original brief

Including timestamps and links and ai discerned content.

### Comments

#### chuckles — 2026-09-22T00:26:55.194Z
[fix-intake] batch clear — AST-1769 already filed for Susan's [bug] (Discussion, assignee Susan). No new markers. Parent stays User Testing.

#### susan — 2026-09-22T00:20:57.310Z
\[bug\] I saw this working earlier, but it doesn't seem to be working in the latest deployment to main/production.  The meteorite tab does not appear in the job modal.

#### chuckles — 2026-09-16T23:36:08.827Z
AST-1692 REVIEW — merge §9a blocked on tests/component/core/test_meteorite.py vs ftr; recalling Betty White.

#### chuckles — 2026-09-16T23:14:32.237Z
AST-1691 REVIEW — merge-child blocked; recalling Hedy for sub not stacked on ftr (sync/republish).

#### chuckles — 2026-09-16T22:24:12.332Z
@susan — context for open question 3:

**`classify_outcome` + `content` (staging `meteorite` row)** — Ruth’s classify result (e.g. link_list / single_jd_*) and the assembled JD / visible text ingress stored on the row. This is the meteorite **record** itself.

**Company stem** — Ruth `qualify_meteorite` / land may discern a real employer stem and attach it (today via meteorite-company / job metadata; AST-1640 will use optional `company_id`). It is **not** a column on the meteorite staging row; it shows up on the job/company side (Summary company upshot / company fields), not as meteorite-table fields.

**Agent story** — the daisy-chain / consult RESPONSE blocks already on **Discussion** (and Job Detail Agent Story). Pulling those into Meteorite would duplicate Discussion.

Recommendation locked unless you say otherwise: Meteorite pane = staging-row fields only (`classify_outcome` + `content` for AI), not stem and not agent story.

#### chuckles — 2026-09-16T21:46:51.983Z
@susan

1. After AST-1562 purges `LANDED` meteorite rows (`landed_purge_days`, default 90), should the Recommended Meteorite tab **disappear** (live row only), or must land (or this epic) **snapshot** the display fields onto the job so provenance survives purge?
2. Ship lookup via today’s `meteorite.astral_job_id` reverse link now, or **block** this epic on AST-1640 `source_entity_type=meteorite` / `source_entity_id` as the SoT pointer?
3. Confirm AI-discerned surface is **`classify_outcome` + `content` only** (staging row). Or also pull Ruth qualify / company-stem fields from agent story / job_data into this pane?

---

_Implementation detail may live in git history on `origin/dev`._
