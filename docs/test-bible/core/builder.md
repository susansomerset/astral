# Builder

**Test module:** `tests/component/core/test_builder.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/builder.py` | `tests/component/core/test_builder.py` | yes |

---

### AST-623 · AST-545

**AST-545 (parent):** Backfill **AST-538** §1.5.1 contract across **`src/core/builder.py`** — resume/cover letter/base-resume render entry points with Style D **`index 1/1`** headers, **`|`** detail for content-source resolution (job **`resume_content`** vs candidate **`base_resume`**, cover letter vs sample text), enabled structure keys, accent source, ATS keyword count, and truncated HTML preview via **`debug_detail_block`**; **`debug=False`** unchanged. **No Betty log-string tests** (parent + child explicit); plan Stage 4 is manual UAT spot-check only.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-623** | Contract debug on `build_resume`, `build_resume_from_job`, `build_cover_letter`, `build_cover_letter_from_job`, `build_base_resume`; read-only source label helpers; failure headers on `ValueError` paths | `src/core/builder.py` | **`tests/component/core/test_builder.py`** (full file — **`LOCKED_AT_100`**); **`tests/component/utils/test_debug_logging.py`** + **`tests/component/utils/test_logging_batch.py`** (**§7.13zt** contract regression) |

**AST-623** narrowed run (pytest-only — instrumentation-only child; no new log-string assertions):

```bash
.venv/bin/python -m pytest tests/component/core/test_builder.py tests/component/utils/test_debug_logging.py tests/component/utils/test_logging_batch.py -q
```

Equivalent harness:

```bash
./scripts/testing/run_component_tests.sh tests/component/core/test_builder.py
```

**Manifest focus (existing + branch-coverage extensions — no log-string asserts):**

| Touched path | Existing / extended tests |
| --- | --- |
| `build_resume_from_job` success + failure + `include_cover` + keyword shapes | **`TestBuildResumeFromJob`**, **`TestBuildResumeFromJobDebugPaths`**, **`TestAst581ResumeCoverSplit`** |
| `build_resume` load chain + failure headers | **`TestBuildResume`**, **`TestBuildResumeDebugPaths`** |
| `build_cover_letter` / `build_cover_letter_from_job` | **`TestAst581ResumeCoverSplit`**, **`TestBuildCoverLetterDebugPaths`**, **`TestBuildCoverLetterFromJobDebugPaths`** |
| `build_base_resume` | **`TestBuildBaseResume`**, **`TestBuildBaseResumeDebugPaths`** |
| Source label helpers | **`TestBuilderIdentifierHelpers`** |
| `debug=False` unchanged | All pre-AST-623 rows above; full-file branch lock |

**Betty test fix (AST-623):** Extended **`test_builder.py`** for **`LOCKED_AT_100`** on new **`debug=True`/`False`** branch pairs — not golden log-line asserts.

---

### AST-998 · AST-994

**AST-998:** Shared resume HTML emit (`build_session_base_resume` / `build_base_resume` / `build_resume_from_job`) recognizes AST-996 experience job arrays via `_emit_experience_jobs_html`; legacy string experience stays a single prose block. `BUILD_CONFIG` experience `body_kind` = `experience_jobs` (emit still keys off value shape). Cover letter unchanged. Prompt/schema = siblings **AST-996** / **AST-997**. **Role chrome** (subheader/meta/accomplishments) was superseded by **AST-1008** golden article classes — **`TestAst998ExperienceJobRender`** asserts the current golden emit shape.

| Area | Source | Component tests |
| --- | --- | --- |
| Per-role emit + session/base/job surfaces + legacy string | `src/core/builder.py` | **`TestAst998ExperienceJobRender`**; reuse **`TestAst987BuildSessionBaseResume`** (legacy string path) |
| `body_kind` literal | `src/utils/config.py` | **`TestAst998ExperienceBodyKind`** (primary: **`docs/test-bible/utils/config.md`**) |

**Broken / obsolete this pass:** none at AST-998 land — chrome asserts revised under **AST-1008**.

**AST-998** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst998ExperienceJobRender \
  tests/component/core/test_builder.py::TestAst987BuildSessionBaseResume \
  tests/component/utils/test_config.py::TestAst998ExperienceBodyKind \
  -q
```

---

### AST-1007 · AST-993

**AST-1007:** `_apply_resume_text_markers` deep-walks dict/list nests and applies `_resume_site_markers` (`__` → NBSP, `~~` → non-breaking hyphen, `" • "` → NBSP-bullet spacing) to every string leaf before session / base / job-tailored HTML emit. Layout chrome (role lead/bullets, education lines, skills grid, header/meta/styles) stays siblings **AST-1008** / **AST-1009** / **AST-1010**.

| Area | Source | Component tests |
| --- | --- | --- |
| Deep-walk helper (job-array + list/dict nests; no mutate; non-strings unchanged) | `src/core/builder.py` | **`TestAst1007NestedTypographyMarkers::test_apply_markers_deep_walks_job_array_and_list_leaves`** |
| Three-surface HTML: no literal `__` / `~~`; NBSP / `\u2011` visible | `src/core/builder.py` | **`TestAst1007NestedTypographyMarkers`** session / base / job methods |
| Existing top-level markers regression | `src/core/builder.py` | **`TestBuilderHelpers::test_applies_profile_contact_and_markers`** |
| Experience job-array emit still green | `src/core/builder.py` | **`TestAst998ExperienceJobRender`** |

**Broken / obsolete this pass:** none — prior shallow-copy helper tests remain valid (top-level strings + unmarked nested leaves).

**Integration:** no existing `tests/integration/` scenario asserts resume typography markers — no integration revision this pass.

**AST-1007** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1007NestedTypographyMarkers \
  tests/component/core/test_builder.py::TestBuilderHelpers::test_applies_profile_contact_and_markers \
  tests/component/core/test_builder.py::TestAst998ExperienceJobRender \
  -q
```


---

### AST-1008 · AST-993

**AST-1008:** Rewrite `_emit_experience_jobs_html` to golden role **articles**: `div.role-header` / `p.compact-title` (`Title • Company`) / `p.compact-location` (`dates: place (arrangement)` when `location` contains config sep), optional `p.role-description` for accomplishments lines prefixed with `BUILD_CONFIG["experience_role_layout"]["lead_line_prefix"]` (`<no bullet>`), then `<ul><li>` for remaining lines. Embedded CSS swaps AST-998 `.role-subheader` / `.role-meta` / `.role-accomplishments` for golden selectors. Education/skills/prior/header/meta stay siblings **AST-1009** / **AST-1010**. Markers remain **AST-1007**.

| Area | Source | Component tests |
| --- | --- | --- |
| Config literals (lead prefix + location sep) | `src/utils/config.py` | **`TestAst1008ExperienceGoldenLayout::test_experience_role_layout_config_keys`** (also **`docs/test-bible/utils/config.md`**) |
| Compact location + lead/bullet split helpers | `src/core/builder.py` | **`test_format_compact_location_helpers`**, **`test_split_role_accomplishments_lead_vs_bullets`** |
| Somerset lead paragraph vs list items + sibling no-lead role | `src/core/builder.py` | **`test_emit_somerset_lead_paragraph_not_list_item`** |
| Three-surface HTML parity | `src/core/builder.py` | session / base / job methods on **`TestAst1008ExperienceGoldenLayout`** |
| Revised AST-998 chrome asserts (golden classes) | `src/core/builder.py` | **`TestAst998ExperienceJobRender`** |

**Broken / obsolete this pass:** **`TestAst998ExperienceJobRender`** asserts on `.role-subheader` / `.role-meta` / `.role-accomplishments` — revised to golden article/compact/list markup in the same pass.

**Integration:** no existing scenario asserts experience role chrome — no integration revision.

**AST-1008** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1008ExperienceGoldenLayout \
  tests/component/core/test_builder.py::TestAst998ExperienceJobRender \
  tests/component/core/test_builder.py::TestAst1007NestedTypographyMarkers \
  tests/component/utils/test_config.py::TestAst998ExperienceBodyKind \
  -q
```

---

### AST-1009 · AST-993

**AST-1009:** `_emit_body_sections_html` emits education as per-line `div.education-list` (`<strong>` credential + post-marker `\u00a0• ` rest), technical skills as `div.skills-grid` with one `div.skill-category` per `Category: items` line (`h4` + items `<p>`), and prior experience remains `p.competencies-list` (markers from AST-1007). Experience role chrome / header-meta-styles stay siblings **AST-1008** / **AST-1010**.

| Area | Source | Component tests |
| --- | --- | --- |
| Education / skills helpers | `src/core/builder.py` | **`TestAst1009EducationSkillsPrior`** helper methods |
| Three-surface HTML (prior + edu ≥3 strong + skills ≥8 categories) | `src/core/builder.py` | **`TestAst1009EducationSkillsPrior`** session / base / job |
| Existing body-section regression | `src/core/builder.py` | **`TestBuilderHelpers::test_emits_body_sections_and_cover_blocks`** |

**Broken / obsolete this pass:** none — prior dump assertions still green (`skills-grid` present; section count unchanged).

**Integration:** no existing scenario asserts education/skills/prior markup — no revision.

**AST-1009** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1009EducationSkillsPrior \
  tests/component/core/test_builder.py::TestBuilderHelpers::test_emits_body_sections_and_cover_blocks \
  -q
```

---

### AST-1010 · AST-993

**AST-1010:** Shared resume HTML header joins `Name\u00a0• Title`; optional `candidate_tagline` feeds `<meta name="description">` (`Resume of {name}, {title}, specializing in {tagline}`) and never appears in header/main body; embedded CSS expands for golden layout class readiness (`.compact-title`, `.role-description`, `.education-list`, `.skills-grid`, …) without an external `styles07.css` link. Experience/education/skills **emit** markup stays siblings **AST-1008** / **AST-1009**.

| Area | Source | Component tests |
| --- | --- | --- |
| Header NBSP-bullet join + ATS meta present/omit + tagline body exclusion + CSS selectors | `src/core/builder.py` | **`TestAst1010HeaderContactMetaStyles`** (session / base / job) |
| Optional tagline contract + contact-adjacent structure | `src/utils/config.py` | **`TestAst1010CandidateTaglineConfig`** (primary: **`docs/test-bible/utils/config.md`**) |
| Experience emit regression (AST-998 / AST-1008 as present on tip) | `src/core/builder.py` | **`TestAst998ExperienceJobRender`** |
| Nested markers regression | `src/core/builder.py` | **`TestAst1007NestedTypographyMarkers`** |

**Broken / obsolete this pass:** none for header/meta/CSS on this product tip. Sibling emit chrome may already be revised on `origin/tests` by AST-1008/1009 — do not re-litigate here. **AST-1020** revises the pre–Take-2 negative contact-flex assert in **`TestAst1010HeaderContactMetaStyles`** (full golden stylesheet → **`TestAst1020GoldenStylesheet`**).

**Integration:** no existing scenario asserts resume header/meta/CSS — no revision.

**AST-1010** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1010HeaderContactMetaStyles \
  tests/component/utils/test_config.py::TestAst1010CandidateTaglineConfig \
  tests/component/core/test_builder.py::TestAst998ExperienceJobRender \
  tests/component/core/test_builder.py::TestAst1007NestedTypographyMarkers \
  -q
```

---

### AST-1020 · AST-1019

**AST-1020:** Shared resume embedded `<style>` matches Take 2 golden rules (contact flex, role/education/skills spacing/type, skills CSS grid, all-caps competencies/skills, unused `.title`/`.specialties`/`.job-title`/`.dates`, mobile + print including always-on `#prior-experience { page-break-before: always }`); `BUILD_CONFIG["default_style"]["colors"]` exposes golden text/border tokens; Astral `.prose-block` / cover / ATS appendages remain; no external stylesheet. Title/meta emit stays sibling **AST-1021**. Markup emit stays **AST-1008** / **AST-1009**.

| Area | Source | Component tests |
| --- | --- | --- |
| Golden stylesheet + three surfaces + Astral appendages | `src/core/builder.py` | **`TestAst1020GoldenStylesheet`** (session / base / job) |
| Text/border color tokens + accent/header/page_bg parity | `src/utils/config.py` | **`TestAst1020DefaultStyleColorTokens`** (primary: **`docs/test-bible/utils/config.md`**) |
| Header/meta/CSS selectors regression | `src/core/builder.py` | **`TestAst1010HeaderContactMetaStyles`** (negative flex assert removed) |
| Experience / education / skills emit regression | `src/core/builder.py` | **`TestAst998ExperienceJobRender`**, **`TestAst1008ExperienceGoldenLayout`**, **`TestAst1009EducationSkillsPrior`** |

**Broken / obsolete this pass:** **`TestAst1010HeaderContactMetaStyles`** one-line “contact flex not present” assert — obsolete under Take 2 golden CSS; removed; golden flex covered by **`TestAst1020GoldenStylesheet`**.

**Integration:** no existing scenario asserts resume stylesheet — no revision; do not invent new integration coverage.

**AST-1020** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1020GoldenStylesheet \
  tests/component/utils/test_config.py::TestAst1020DefaultStyleColorTokens \
  tests/component/core/test_builder.py::TestAst1010HeaderContactMetaStyles \
  tests/component/core/test_builder.py::TestAst998ExperienceJobRender \
  tests/component/core/test_builder.py::TestAst1008ExperienceGoldenLayout \
  tests/component/core/test_builder.py::TestAst1009EducationSkillsPrior \
  -q
```

---

### AST-1021 · AST-1019

**AST-1021:** Shared resume document `<title>` is `{candidate_name} Resume` (space; no em/en dash; empty name → `Resume`); ATS `<meta name="description">` stays the AST-1010 field-derived template (`Resume of {name}, {title}, specializing in {tagline}`) — never the golden HTML example Product Manager / Cloud Platforms literal. Stylesheet remains sibling **AST-1020**. Structural emit remains **AST-1007**–**AST-1010**.

| Area | Source | Component tests |
| --- | --- | --- |
| Title shape + empty-name fallback + meta lock (three surfaces) | `src/core/builder.py` | **`TestAst1021DocumentTitleChrome`** (session / base / job + empty name) |
| Meta present/omit + header join regression | `src/core/builder.py` | **`TestAst1010HeaderContactMetaStyles`** |
| Stylesheet regression | `src/core/builder.py` | **`TestAst1020GoldenStylesheet`** |

**Broken / obsolete this pass:** none — no prior asserts locked `{name} — Resume`.

**Integration:** no existing scenario asserts resume document title/meta chrome — no revision; do not invent new integration coverage.

**AST-1021** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1021DocumentTitleChrome \
  tests/component/core/test_builder.py::TestAst1010HeaderContactMetaStyles \
  tests/component/core/test_builder.py::TestAst1020GoldenStylesheet \
  -q
```

---

### AST-1027 · AST-1019

**AST-1027 (UAT):** `craft_resume_base` `cache_prompt` in `data/admin/agent_task.json` **preserves** `__` / `~~` digraphs (no strip-to-space/hyphen); skills/contact/prior/competencies instructions stay paste-faithful. Shared `_resume_site_markers` expand unchanged (**AST-1007**) — when digraphs survive parse, HTML shows 1:1 NBSP (including `__•__` both sides and word joins like `Jira__Align`). Stylesheet/title siblings **AST-1020** / **AST-1021** untouched. Primary prompt assert: **`docs/test-bible/core/candidate.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| UAT skill-line expand + session HTML | `src/core/builder.py` | **`TestAst1027UatMarkerExpand`** |
| Nested / three-surface marker expand regression | `src/core/builder.py` | **`TestAst1007NestedTypographyMarkers`** |

**Broken / obsolete this pass:** none — expand asserts already green; bug was prompt destroying digraphs.

**Integration:** no existing scenario asserts craft_resume_base marker preserve or `__`→NBSP in session HTML — no revision; do not invent new integration coverage.

**AST-1027** narrowed run (builder half — full manifest in candidate.md):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1027UatMarkerExpand \
  tests/component/core/test_builder.py::TestAst1007NestedTypographyMarkers \
  -q
```

---

### AST-1028 · AST-1019

**AST-1028 (UAT):** When `candidate_title` is title-only and `candidate_tagline` holds the specialty/keyword line, shared `_emit_html_document` keeps keywords out of header/main and in field-derived `<meta name="description">` (`Resume of {name}, {title}, specializing in {tagline}`). Prompt split: **`docs/test-bible/core/candidate.md`**. Stylesheet/title siblings **AST-1020** / **AST-1021** untouched.

| Area | Source | Component tests |
| --- | --- | --- |
| UAT Fractional TPM + keyword tagline session emit | `src/core/builder.py` | **`TestAst1028UatKeywordsMetaEmit`** |
| Header/meta/tagline body exclusion regression | `src/core/builder.py` | **`TestAst1010HeaderContactMetaStyles`**, **`TestAst1021DocumentTitleChrome`** |

**Broken / obsolete this pass:** none — no builder product edit; emit lock only.

**Integration:** no existing scenario asserts keywords-in-meta vs header — no revision; do not invent new integration coverage.

**AST-1028** narrowed run (builder half — full manifest in candidate.md):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1028UatKeywordsMetaEmit \
  tests/component/core/test_builder.py::TestAst1010HeaderContactMetaStyles \
  tests/component/core/test_builder.py::TestAst1021DocumentTitleChrome \
  -q
```

---

### AST-1039 · AST-1019

**AST-1039 (UAT):** Professional Summary paragraph split reuses `_session_cover_letter_paragraphs` (blank lines first, then single-`\n` fallback) so paste newlines become multiple `.summary-intro` `<p>` elements — not one paragraph with whitespace-collapsed newlines. Experience `\n` → `<li>` unchanged. CSS / prompt / Session Resume Paste chrome untouched.

| Area | Source | Component tests |
| --- | --- | --- |
| Single-`\n` + blank-line summary intros + Experience regression | `src/core/builder.py` | **`TestAst1039SummaryNewlineParagraphs`** |
| Cover-letter paragraph helper regression | same | **`TestAst1024BuildSessionCoverLetter::test_blank_line_paragraphs_and_single_chunk_newlines`** |

**Broken / obsolete this pass:** none — blank-line `"Para one\n\nPara two"` behavior preserved; only single-`\n` was missing.

**Integration:** no existing scenario asserts `.summary-intro` count — no revision; do not invent new integration coverage.

**AST-1039** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1039SummaryNewlineParagraphs \
  tests/component/core/test_builder.py::TestAst1024BuildSessionCoverLetter::test_blank_line_paragraphs_and_single_chunk_newlines \
  -q
```

---

### AST-1030 · AST-1019

**AST-1030 (UAT):** With `<no bullet>` on the first accomplishments line, shared emit uses `.role-description` and strips the marker from HTML; without the prefix the same prose is a first `<li>` (no first-line heuristic). Prompt preserve: **`docs/test-bible/core/candidate.md`**. Golden layout spine: **AST-1008**.

| Area | Source | Component tests |
| --- | --- | --- |
| UAT with/without `<no bullet>` session emit | `src/core/builder.py` | **`TestAst1030UatNoBulletLeadEmit`** |
| Golden lead / split / CSS regression | same | **`TestAst1008ExperienceGoldenLayout`** |

**Broken / obsolete this pass:** none — no builder product edit; emit lock only.

**Integration:** no existing scenario asserts `<no bullet>` → `.role-description` — no revision; do not invent new integration coverage.

**AST-1030** narrowed run (builder half — full manifest in candidate.md):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1030UatNoBulletLeadEmit \
  tests/component/core/test_builder.py::TestAst1008ExperienceGoldenLayout \
  -q
```

---

### AST-1029 · AST-1019

**AST-1029 (UAT):** When `core_competencies` / `prior_experience` already use `•` separators, shared emit puts that text in `.competencies-list` (HTML-escaped) with no pipe rewrite. Prompt harden: **`docs/test-bible/core/candidate.md`**. CSS chrome stays **AST-1020**.

| Area | Source | Component tests |
| --- | --- | --- |
| UAT bullet competencies + prior session emit | `src/core/builder.py` | **`TestAst1029UatCompetenciesBulletsEmit`** |
| Education/skills/prior markup regression | `src/core/builder.py` | **`TestAst1009EducationSkillsPrior`** |

**Broken / obsolete this pass:** none — no builder product edit; emit lock only.

**Integration:** no existing scenario asserts competencies bullet vs pipe — no revision; do not invent new integration coverage.

**AST-1029** narrowed run (builder half — full manifest in candidate.md):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1029UatCompetenciesBulletsEmit \
  tests/component/core/test_builder.py::TestAst1009EducationSkillsPrior \
  -q
```

---

### AST-1024 · AST-1023

**AST-1024:** `build_session_cover_letter` emits SomersetCover HTML from an in-memory field payload (no job load / artifact write). Shared document helper is `_emit_somerset_cover_html_document` (renamed from session-only; job cover-only reuse = **AST-1138**). Optional `candidate_id` loads candidate contact for signature image — **AST-1126** places the image only when signature text contains `{$SIGNATURE_IMAGE}` (path `contact.cover_letter_signature_image` via AST-1125 contract; no auto-inject). Empty form `from_block` → `resolve_cover_from_block` when candidate selected = **AST-1139**. Admin route: **`docs/test-bible/ui/api/api_admin.md`**. Config spine: **`docs/test-bible/utils/config.md`**. React Session Cover Letter page = sibling **AST-1025**; job Print Cover Letter emit = **AST-1138**.

| Area | Source | Component tests |
| --- | --- | --- |
| Validation + SomersetCover DOM/CSS + optional to/subject | `src/core/builder.py` | **`TestAst1024BuildSessionCoverLetter`** |
| Optional candidate signature image / miss / skip | same | same class — token-gated (AST-1126 revise) |
| Paragraph split + HTML escape | same | same class |
| Style D debug True/False (no log-string asserts) | same | success + failure debug paths |

**Broken / obsolete (superseded by AST-1126):** auto-inject image above session name without token; profile-path image lookup (now `contact.cover_letter_signature_image`).

**Integration:** no existing `tests/integration/` scenario asserts session cover HTML — no revision; do not invent new integration coverage.

**AST-1024** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1024BuildSessionCoverLetter \
  tests/component/ui/api/test_api_admin.py::TestAst1024SessionCoverLetterHtmlApi \
  tests/component/utils/test_config.py::TestAst1024SessionCoverLetterConfig \
  -q
```

---

### AST-1014 · AST-952

`_apply_contact_to_render_dict` + `_coerce_candidate_blob` `_first`/`_last`/`_full`. Primary: **`docs/test-bible/core/candidate.md`** § AST-1014 — **`TestAst1014BuilderContact`**, revised **`TestBuilderHelpers`**.

### AST-1100 · AST-1091

**Parent:** [AST-1091](https://linear.app/astralcareermatch/issue/AST-1091/job-resume-artifact-cover-letter-and-suggested-responses-is-not-saved). **Publish:** `origin/sub/AST-1091/AST-1100-resolve-artifact-agent-data-id`.

`_resolve_resume_sections` / `_resolve_cover_letter` resolve pin strings via `resolve_job_artifact_agent_data_body` when legacy body dicts are absent.

| Area | Source | Component tests |
| --- | --- | --- |
| Pin → HTML body | `src/core/builder.py` | **`TestAst1100BuilderPinResolve`** |

**Broken / obsolete:** none.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1100BuilderPinResolve \
  -q
```

### AST-1126 · AST-1123

**Parent:** [AST-1123 — Support Signature_Image as a token in the cover letter](https://linear.app/astralcareermatch/issue/AST-1123/support-signature-image-as-a-token-in-the-cover-letter). **Publish:** `origin/sub/AST-1123/AST-1126-cover-html-emit-token-replace-stop-auto-above`. **Blocked by:** AST-1125 config contract.

Job + session cover HTML: replace `{$SIGNATURE_IMAGE}` at token position via `get_cover_letter_render_token` + `_safe_image_src`; stop unconditional image prepend/inject; omit when token absent or image missing/rejected; Style D `signature_image_token=` / `signature_image=` on touched cover debug paths. Resume emit must not resolve the token. Config contract: **`docs/test-bible/utils/config.md`** § AST-1125.

| Area | Source | Component tests |
| --- | --- | --- |
| Job signoff token placement / omit / no auto-above | `src/core/builder.py` | **`TestAst1126CoverSignatureImageToken`** + revised **`TestBuilderHelpers::test_emits_cover_signoff_and_ats_tokens`** |
| Session token replace / no auto-inject | same | revised **`TestAst1024BuildSessionCoverLetter`** image cases |
| Token status matrix + resume non-resolution + job debug lines | same | **`TestAst1126CoverSignatureImageToken`** |

**Broken / obsolete (revised this pass):** `_emit_cover_signoff_html` image-only prepend; session `test_signature_image_from_profile` auto-inject + profile path.

**Integration:** none (no existing scenario asserts cover signature image placement).

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1126CoverSignatureImageToken \
  tests/component/core/test_builder.py::TestAst1024BuildSessionCoverLetter \
  tests/component/core/test_builder.py::TestBuilderHelpers::test_emits_cover_signoff_and_ats_tokens \
  tests/component/core/test_builder.py::TestBuildCoverLetterFromJobDebugPaths \
  -q
```

### AST-1138 · AST-1124

**Parent:** [AST-1124 — Cover Letter Header is incorrect](https://linear.app/astralcareermatch/issue/AST-1124/cover-letter-header-is-incorrect). **Publish:** `origin/sub/AST-1124/AST-1138-job-cover-html-somersetcover-fromblock-golden-css`. **Blocked by:** AST-1137 (`resolve_cover_from_block`).

`build_cover_letter_from_job` emits SomersetCover (shared `_emit_somerset_cover_html_document`) with `fromBlock` from `resolve_cover_from_block`; maps Subject/Letter/signature via `BUILD_CONFIG["job_cover_somerset"]`; no resume `h1`/`.contact` shell on cover-only; Style D `from_block_source=` / `document_path=somerset_cover`. Resume Print / materials `include_cover` stay on legacy cover sections. Session Admin defaults = **AST-1139**. Config map: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Default + custom fromBlock, golden CSS selectors, no resume chrome | `src/core/builder.py` | **`TestAst1138JobCoverSomersetFromBlock`** |
| Subject/Letter aliases + cover-only shell | same | revised **`TestAst581ResumeCoverSplit::test_build_cover_letter_from_job_emits_cover_only`**, **`TestAst518BuilderResumeStructure::test_cover_letter_subject_letter_aliases_render_on_cover_route`** |
| Field mapper + candidate shape helpers | same | **`TestAst1138JobCoverSomersetFromBlock`** mapper/shape cases |
| Style D fromBlock source / document path | same | same class — debug True/False |
| Resume Print unchanged | same | **`test_resume_print_unchanged_no_from_block`** (+ existing resume suites) |

**Broken / obsolete (revised this pass):** cover-only asserts on `aria-label="Cover body"` (resume cover-block) — cover-only is SomersetCover after this ticket.

**Integration:** none (no existing scenario asserts job Print Cover Letter DOM).

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1138JobCoverSomersetFromBlock \
  tests/component/core/test_builder.py::TestAst581ResumeCoverSplit::test_build_cover_letter_from_job_emits_cover_only \
  tests/component/core/test_builder.py::TestAst518BuilderResumeStructure::test_cover_letter_subject_letter_aliases_render_on_cover_route \
  tests/component/core/test_builder.py::TestAst1126CoverSignatureImageToken \
  tests/component/utils/test_config.py::TestAst1138JobCoverSomersetConfig \
  -q
```

### AST-1139 · AST-1124

**Parent:** [AST-1124 — Cover Letter Header is incorrect](https://linear.app/astralcareermatch/issue/AST-1124/cover-letter-header-is-incorrect). **Publish:** `origin/sub/AST-1124/AST-1139-session-cover-letter-golden-parity`. **Blocked by:** AST-1137.

`build_session_cover_letter`: empty form `from_block` + loaded candidate → `resolve_cover_from_block` (source `candidate`/`default`); non-empty form wins as `session` and is expanded by **AST-1148** `expand_cover_from_block_text`; no candidate + empty still required; Style D `from_block_source=` / `document_path=somerset_cover`; golden CSS selectors unchanged. Admin UI = **`docs/test-bible/frontend/pages.md`**. Config: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Empty from_block resolve + session win + Style D | `src/core/builder.py` | **`TestAst1139SessionCoverEmptyFromBlock`** |
| No-candidate empty still required | same | same class + existing **`TestAst1024BuildSessionCoverLetter::test_rejects_missing_required`** |
| Golden CSS selectors on session emit | same | **`test_empty_from_block_with_candidate_uses_default`** (+ **`TestAst1024BuildSessionCoverLetter`**) |

**Broken / obsolete:** none — additive defaulting path; required-without-candidate preserved.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1139SessionCoverEmptyFromBlock \
  tests/component/core/test_builder.py::TestAst1024BuildSessionCoverLetter \
  tests/component/utils/test_config.py::TestAst1139SessionCoverEmptyResolveConfig \
  -q
```

### AST-1148 · AST-1145

**Parent:** [AST-1145 — Allow contact info tokens and | chars in fromBlock](https://linear.app/astralcareermatch/issue/AST-1145/allow-contact-info-tokens-and-or-chars-in-fromblock). **Publish:** `origin/sub/AST-1145/AST-1148-resolve-tokens-in-from-block-emit-debug`.

Non-empty session `from_block` runs `expand_cover_from_block_text` before SomersetCover emit; empty→resolve already expands via **AST-1148** candidate helper; job Print Cover Letter consumes expanded resolve text (no second expand). Primary expand/resolve: **`docs/test-bible/core/candidate.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Session-typed token/`|` expand + job custom tokens | `src/core/builder.py` | **`TestAst1148SessionTypedFromBlockExpand`** |
| Empty→resolve golden shape (template expand) | same | **`TestAst1139SessionCoverEmptyFromBlock`**, **`TestAst1138JobCoverSomersetFromBlock`** |

**Broken / obsolete:** none for builder HTML asserts (golden Name/City/email still holds via template).

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1148SessionTypedFromBlockExpand \
  tests/component/core/test_builder.py::TestAst1139SessionCoverEmptyFromBlock \
  tests/component/core/test_builder.py::TestAst1138JobCoverSomersetFromBlock \
  -q
```

### AST-1162 · AST-1161

**Parent:** [AST-1161 — Signature Image now overlaps Name text in signature](https://linear.app/astralcareermatch/issue/AST-1161/signature-image-now-overlaps-name-text-in-signature). **Publish:** `origin/sub/AST-1161/AST-1162-fix-signature-image-name-vertical-spacing`.

Shared SomersetCover `.signature-img` vertical margin in `_emit_somerset_cover_html_document`: supersede AST-1024 / AST-1124 golden `margin: 8px 0 -25px 0` → `margin: 8px 0 8px 0` so image stacks above name with no overlap. Session + job cover surfaces inherit via the shared helper. Token / omit / from-block / resume emit unchanged.

| Area | Source | Component tests |
| --- | --- | --- |
| Session CSS margin + closing→img→name order | `src/core/builder.py` | **`TestAst1162SignatureImgVerticalSpacing::test_session_signature_img_margin_non_negative`** |
| Job SomersetCover same CSS rule | same | **`…::test_job_somerset_signature_img_margin_non_negative`** |
| No-image signoff (no empty img) | same | **`…::test_session_no_image_keeps_closing_and_name`** |
| Prior token placement / omit | same | existing **`TestAst1024BuildSessionCoverLetter`** image cases, **`TestAst1126CoverSignatureImageToken`** |

**Broken / obsolete:** none (prior suites asserted selector presence / DOM order, not the negative bottom margin).

**Integration:** none (no existing scenario asserts SomersetCover `.signature-img` CSS).

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1162SignatureImgVerticalSpacing \
  tests/component/core/test_builder.py::TestAst1024BuildSessionCoverLetter::test_token_replaces_with_contact_image \
  tests/component/core/test_builder.py::TestAst1024BuildSessionCoverLetter::test_no_image_without_token_even_with_contact_image \
  -q
```

### AST-1165 · AST-1161

**Parent:** [AST-1161 — Signature Image now overlaps Name text in signature](https://linear.app/astralcareermatch/issue/AST-1161/signature-image-now-overlaps-name-text-in-signature). **Publish:** `origin/sub/AST-1161/AST-1165-uat-signoff-loses-line-breaks-between-name-and-title`.

UAT: `_html_with_signature_image_token` escapes SomersetCover signature segments then converts authored newlines to `<br>` (token-present and token-absent paths). Session + job share the helper. Does not touch resume `_emit_cover_signoff_html`, AST-1162 `.signature-img` margin, or AST-1126 omit policies.

| Area | Source | Component tests |
| --- | --- | --- |
| Session name/title `<br>` after image + margin lock | `src/core/builder.py` | **`TestAst1165SignoffNewlineToBr::test_session_name_and_title_br_after_image`** |
| Job SomersetCover same fragment | same | **`…::test_job_somerset_name_and_title_br_after_image`** |
| Token-absent newlines, no empty img | same | **`…::test_token_absent_preserves_newlines_no_img`** |
| Prior overlap / token placement | same | **`TestAst1162SignatureImgVerticalSpacing`**, **`TestAst1024BuildSessionCoverLetter`** image cases |

**Broken / obsolete:** none (prior asserts used single-line names after the token; `<br>` after leading `\n` does not break order checks).

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1165SignoffNewlineToBr \
  tests/component/core/test_builder.py::TestAst1162SignatureImgVerticalSpacing \
  tests/component/core/test_builder.py::TestAst1024BuildSessionCoverLetter::test_token_replaces_with_contact_image \
  -q
```

