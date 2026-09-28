# Formatting

**Test module:** `tests/component/utils/test_formatting.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/utils/formatting.py` | `tests/component/utils/test_formatting.py` | yes |

---

### AST-827 · AST-824

**AST-827 (child):** **`find_job_containers`** Phase 2b — sibling leaf tags each carrying one title (medicarerights-style flat `<a>` job rows) return one outerHTML per title-bearing leaf when the union covers all requested titles.

| Area | Source | Component tests |
| --- | --- | --- |
| Sibling anchor two-title cull | `src/utils/formatting.py` | `tests/component/utils/test_formatting.py::TestFindJobContainers::test_sibling_anchor_links_two_titles` |

Roster handoff + parse dispatch: **`docs/test-bible/core/roster.md`** (**AST-827**).

**AST-827** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_formatting.py::TestFindJobContainers::test_sibling_anchor_links_two_titles \
  tests/component/utils/test_formatting.py::TestFindJobContainers::test_phase_one_deepest_container \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless **`test-child`** widens.

---

### AST-713 · AST-710

**`collapse_consecutive_blank_lines`** in `formatting.py` — collapses runs of two or more consecutive blank (whitespace-only) lines to a single blank line; preserves non-empty line content unchanged. Parent **AST-710** removes redundant empty rows from persisted visible text.

| Area | Source | Component tests |
| --- | --- | --- |
| Blank-line normalizer | `src/utils/formatting.py` | `tests/component/utils/test_formatting.py::TestCollapseConsecutiveBlankLines` |

---

### AST-718 · AST-716

**`normalize_link()`** — pure PJL URL ledger key (scheme strip, fragment drop, slash collapse, index filename trim). Parent **AST-716** decomposed prefilter path.

| Area | Source | Component tests |
| --- | --- | --- |
| PJL URL normalizer | `src/utils/formatting.py` | `tests/component/utils/test_formatting.py::TestNormalizeLink` |

**AST-718** narrowed run:

```bash
./scripts/testing/run_component_tests.sh tests/component/utils/test_formatting.py::TestNormalizeLink -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless **`test-child`** widens.

### AST-1120 · AST-1119

**Parent:** [AST-1119 — Fallback for company job id](https://linear.app/astralcareermatch/issue/AST-1119/fallback-for-company-job-id). **Publish:** `origin/sub/AST-1119/AST-1120-uuid-from-job-link-company-job-id-fallback`.

`uuid_path_segment_from_url(url, segment_pattern)` — rightmost path segment that fullmatches the pattern (query/fragment ignored; case preserved). Apply surface: **`docs/test-bible/core/consult.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| UUID path extract | `src/utils/formatting.py` | **`TestUuidPathSegmentFromUrl`** |

**Broken / obsolete:** none.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_formatting.py::TestUuidPathSegmentFromUrl \
  -q
```

**AST-713** narrowed run:

```bash
./scripts/testing/run_component_tests.sh tests/component/utils/test_formatting.py::TestCollapseConsecutiveBlankLines -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless **`test-child`** widens.

---

### AST-1131 · AST-1130

**Parent:** [AST-1130 — Manage Email create button for job lists isn't working](https://linear.app/astralcareermatch/issue/AST-1130/manage-email-create-button-for-job-lists-isnt-working). **Publish:** `origin/sub/AST-1130/AST-1131-normalize-pasted-list-email-html`.

`normalize_pasted_list_email_html(html)` — gated entity-unescape → unwrap Gmail nested auto-links in configured attrs → promote bare http(s) URLs when no anchors remain. Wire surfaces: **`docs/test-bible/core/inbox.md`** · **`docs/test-bible/core/gazer.md`**; knobs: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Paste/list HTML normalize | `src/utils/formatting.py` | **`TestNormalizePastedListEmailHtml`** |

**Broken / obsolete:** none — additive helper; existing `TestNormalizeLink` / AST-1061 ingest paths stay valid (idempotent on clean HTML).

**Integration:** none revised (no existing Manage Email create / paste-normalize scenario).

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_formatting.py::TestNormalizePastedListEmailHtml \
  tests/component/utils/test_config.py::TestAst1131MeteoriteEmailIngestPasteNormalizeConfig \
  tests/component/core/test_inbox.py::TestAst1131StripNormalizePastedList \
  tests/component/core/test_gazer.py::TestAst1131NormalizePastedListEmailIngest \
  tests/component/core/test_gazer.py::TestAst1061MeteoriteEmailIngest \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless **`test-child`** widens.

### AST-1840 · AST-1844 (`find_job_containers` linear rewrite equivalence)

**Parent:** [AST-1838](https://linear.app/astralcareermatch/issue/AST-1838). Product **AST-1840** replaced per-descendant `get_text` with one ordered text walk + char spans + cached `_titles_in` (same signature, same containers — cost-only change). Pins equivalence on shapes where a parent's `get_text` excludes text a child sees (comments, `script` / `style` / `template` / `rt` / `rp`) plus an 8,000-row DOM. Green on both pre-fix `31846c28` and AST-1840 (`fb472a98`). Closes the rewrite's uncovered branches on this **LOCKED_AT_100** file: `345→350` (whitespace-only string), `356→353` (comment / non-main string), `375→377` (special-string-container fallback). Structural asserts only; no timing assertion, no size cap.

| Area | Source | Component tests |
| --- | --- | --- |
| Comment/whitespace, script, style, ruby rt/rp → single deepest container | `src/utils/formatting.py` | **`TestAst1840FindJobContainersEquivalence::test_single_deepest_container`** (ids `comment_ws`, `script`, `style`, `ruby_rt`, `ruby_rp`) |
| `template` → Phase 2 sibling union | same | **`TestAst1840FindJobContainersEquivalence::test_template_sibling_union`** |
| Large DOM (8,000 rows) same containers | same | **`TestAst1840FindJobContainersEquivalence::test_large_dom_same_containers`** |

**Broken / obsolete:** none — existing **`TestFindJobContainers`** unchanged.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_formatting.py::TestAst1840FindJobContainersEquivalence \
  tests/component/utils/test_formatting.py::TestFindJobContainers \
  -q
```
