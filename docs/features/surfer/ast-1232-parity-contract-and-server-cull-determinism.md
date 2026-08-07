# AST-1232 — Parity contract and server cull determinism

**Linear:** [AST-1232](https://linear.app/astralcareermatch/issue/AST-1232/parity-contract-and-server-cull-determinism-client-side-dom-culling)  
**Parent:** [AST-1172](https://linear.app/astralcareermatch/issue/AST-1172/client-side-dom-culling-parity-for-captured-pages) — Client-side DOM culling parity for captured pages  
**Publish ref:** `origin/sub/AST-1172/AST-1232-parity-contract-and-server-cull-determinism`

Owns the written definition of what equivalent culled output means across the live-DOM / HTML-string gap (Joan open question 2: cull the live DOM under the same rule semantics; parity via normalized comparison), the normalization the comparison permits, and proof that the existing server `_cull_html` path is deterministic and anchor-safe enough that later children can depend on it. Does **not** deliver cull rules to the extension ([AST-1233](https://linear.app/astralcareermatch/issue/AST-1233/shared-cull-rule-delivery-client-side-dom-culling-parity-for-captured)) or apply the cull in the content script ([AST-1234](https://linear.app/astralcareermatch/issue/AST-1234/content-script-cull-fallback-and-parity-proof-client-side-dom)).

**Depends on (fixtures):** [AST-1194](https://linear.app/astralcareermatch/issue/AST-1194/page-capture-spike-what-does-the-extension-actually-get-from-a-job) captures at `$ASTRAL_MAIN/debug/spikes/AST-1194/captures/` (gitignored). Home proposed on that ticket; not committed (size + personal data).

---

## Parity contract (normative)

Siblings **AST-1233** and **AST-1234** treat this section as the definition of "equivalent." Build stages below implement the Python-side helpers that encode it; they do not reinterpret it.

### Inputs and ownership

| Side | Input type | Cull operation | Output compared |
|------|------------|----------------|-----------------|
| Server (reference) | HTML **string** | `_cull_html` in `src/external/playwright.py` reading **only** `ASTRAL_CONFIG["html_cull"]` | Culled HTML string |
| Extension (consumer; **AST-1234**) | **Live DOM** | In-place DOM mutation under the **same rule semantics** as `_cull_html` (not a second hand-maintained rule set) | Serialization of the culled subtree (content-script `outerHTML` of the culled root, typically `document.body` after cull) |

⚠️ **Decision — live DOM, not serialize-then-string-cull (Joan OQ2):** The client culls the live DOM directly. Parity is **not** byte-identity of raw serializations. Parity is `culled_html_equivalent(server_culled, client_culled)` after the normalization below.

⚠️ **Decision — rules stay single-sourced:** Rule literals remain only in `ASTRAL_CONFIG["html_cull"]` (`pattern.config.config-block` / `astral.config.config-source-of-truth`). This ticket does not ship rules to JS (**AST-1233**). Traversal code necessarily exists twice (Python vs content script); that duplication is acknowledged and out of scope for DRY extraction here (`astral.standards.dry-and-focused-functions` applies to the **comparison helpers** this ticket adds, not to collapsing the two cullers).

### Rule semantics the client must mirror (reference behavior of `_cull_html`)

These are observational of today's server function — **do not change keep/discard** on this ticket (parent boundary / this ticket Boundaries):

1. Operate on **body** inner content when a `<body>` exists; otherwise the whole document.
2. **Decompose** (remove element and descendants): `script`, `style`, `noscript`, `meta`, `link`, `svg`, HTML comments; `img` without non-empty `alt` and without `class`; elements with `aria-hidden="true"`, `hidden`, inline `display:none` / `display: none`, class tokens in `hidden_class_patterns`, or class/id substring match against `banner_patterns`.
3. **Special `img`:** if kept, retain only `alt` and `class`.
4. **Unwrap** every element whose tag is not in `allowed_tags` and is not the specially handled `img` (text/children preserved), repeating until stable (existing `max_passes` safety bound stays untouched — do not invent a new limit).
5. **Strip attributes** listed in `strip_attributes`, plus any `on*` when `strip_on_attrs` is true. Preserve all other attributes (including `href`, `id`, `class`, `data-*`, `aria-*`).

### Normalization the comparison permits

After both sides produce a culled HTML string, each string is passed through `normalize_culled_html` before equality. Normalization **may** erase:

| Permitted difference | Normalize action |
|----------------------|------------------|
| Tag name case | Lowercase all tag names |
| Attribute name case | Lowercase all attribute names |
| Attribute order on a tag | Emit attributes sorted by name |
| Attribute quote style | Always double-quote in canonical form |
| Self-closing vs open void tags | Canonical open form for void tags if any remain |
| Whitespace between tags | Remove inter-tag whitespace-only text nodes |
| Text-node whitespace | Collapse internal runs of whitespace in text nodes to a single space; strip leading/trailing space on each text node; drop empty text nodes |
| Character references that decode to the same Unicode | Decode to Unicode in text and attribute values before emit |

Normalization **must not** erase differences in: tag identity, nesting order of kept elements, attribute presence/values (after decode), or text content (after whitespace collapse).

### Equivalence predicate

```
culled_html_equivalent(a, b) := normalize_culled_html(a) == normalize_culled_html(b)
```

Both arguments are already-culled HTML strings (server `_cull_html` output, or client serialization after live-DOM cull). Do **not** re-cull inside the predicate.

### Anchor / job-URL preservation (AC3)

Independent of full-tree equivalence (search pages care about links even when markup shape differs across engines):

1. **Config preflight (raise, do not patch rules):**  
   - `'a' in ASTRAL_CONFIG["html_cull"]["allowed_tags"]`  
   - `'href' not in ASTRAL_CONFIG["html_cull"]["strip_attributes"]`  
   If either fails → stop and comment on **parent AST-1172** with the finding. Do **not** widen `allowed_tags` or shrink `strip_attributes` on this ticket.
2. **Href set:** `extract_anchor_hrefs(html)` returns the sorted unique list of `href` values from `<a>` tags where the value, stripped, is non-empty and not `#` and does not start with `javascript:` (case-insensitive). No other filtering (no site-specific job-link classifier — that is **AST-1171**).
3. **Preservation check:** for a given page HTML `raw`,  
   `extract_anchor_hrefs(raw) == extract_anchor_hrefs(_cull_html(raw))`  
   must hold. If it fails on a real AST-1194 search capture → stop and comment on **parent AST-1172** with the delta; do **not** change cull rules to force a pass.

⚠️ **Decision — full unculled href set, not a guessed "jobish" subset:** Discovery depends on posting URLs present as `href`s in the capture. Comparing the full non-empty/`#`/`javascript:` href set before vs after cull is the strictest check that still stays inside this ticket. Banner-pattern removals that delete anchors will surface as a parent finding (ticket Notes: raise if anchors are not preserved), not a silent allow-list edit.

### What this contract does not claim

- Byte-identical raw `outerHTML` vs BeautifulSoup `str(soup)`.
- Identical output if the live DOM and the captured HTML string are not the same page state.
- Client rule delivery, content-script placement, fallback, or payload size metrics (**AST-1233** / **AST-1234**).
- Changes to what the server keeps or discards.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `docs/features/surfer/ast-1232-parity-contract-and-server-cull-determinism.md` | This plan + normative parity contract | docs |
| `src/utils/html_cull_parity.py` | New: `normalize_culled_html`, `culled_html_equivalent`, `extract_anchor_hrefs`, `assert_html_cull_anchor_config` | utils |
| `src/external/playwright.py` | Remove `# pragma: no cover` from `_cull_html` only — no behavior change | external |
| `scripts/spikes/ast_1232_verify_server_cull.py` | Offline: determinism + href-set check on synthetic HTML and AST-1194 captures; write report under `debug/spikes/AST-1232/` | scripts |

**Out of files (siblings / boundaries):**

| File / area | Owner |
|-------------|-------|
| Extension rule delivery / Vite codegen / authenticated config endpoint | AST-1233 |
| Content-script cull, worker handoff, fallback, client↔server parity proof on real pages | AST-1234 |
| `ASTRAL_CONFIG["html_cull"]` keep/discard literals | unchanged (read-only; raise-only if anchors unsafe) |
| `tests/`, `docs/test-bible/**` | Betty |
| AST-1194 capture HTML (personal data) | gitignored under `debug/spikes/AST-1194/captures/` — never commit |

---

## Stage 1: Parity helpers in utils

**Done when:** `src/utils/html_cull_parity.py` exists with the four public functions below; importing the module does not import `src.external` or Playwright; a one-liner Python check shows `culled_html_equivalent` true for attribute-order variants and false when an `href` differs. No change to `_cull_html` behavior yet.

1. Create `src/utils/html_cull_parity.py` with module docstring citing AST-1232 and pointing at the **Parity contract (normative)** section of this plan as the prose authority.

2. Implement exactly these public functions (lazy-import BeautifulSoup inside each function that needs it — same pattern as `src/utils/formatting.py`):

```python
def assert_html_cull_anchor_config(html_cull: dict | None = None) -> None:
    """Raise ValueError if html_cull cannot preserve anchors (AC3 preflight)."""

def extract_anchor_hrefs(html: str) -> list[str]:
    """Sorted unique hrefs per Parity contract § Anchor / job-URL preservation."""

def normalize_culled_html(html: str) -> str:
    """Canonical form per Parity contract § Normalization the comparison permits."""

def culled_html_equivalent(a: str, b: str) -> bool:
    """True iff normalize_culled_html(a) == normalize_culled_html(b)."""
```

3. `assert_html_cull_anchor_config`: when `html_cull` is `None`, read `ASTRAL_CONFIG["html_cull"]` from `src.utils.config`. Require `allowed_tags` and `strip_attributes` keys. Raise `ValueError` with an explicit message if `'a'` is missing from `allowed_tags` or `'href'` is in `strip_attributes`. Do not mutate config.

4. `normalize_culled_html`: parse with `BeautifulSoup(html, "html.parser")`, walk the tree, apply the normalization table in the contract, emit a single canonical HTML string. Empty / non-string input → `""`.

5. Do **not** call `_cull_html` from this module (utils must not import external). Callers that need cull + compare import `_cull_html` from external and the helpers from utils.

⚠️ **Decision — helpers in utils, cull stays in external:** Comparison/normalization is pure string work and must be importable without Playwright. Moving `_cull_html` into utils is out of scope and would widen the external/utils boundary for no AC gain.

**Commit:** `code(AST-1232): Stage 1 — html_cull parity helpers`

---

## Stage 2: Server cull coverage surface (no behavior change)

**Done when:** `_cull_html` is no longer marked `# pragma: no cover`; behavior is byte-identical to pre-change for a fixed synthetic input; `assert_html_cull_anchor_config()` succeeds against live `ASTRAL_CONFIG["html_cull"]`.

1. In `src/external/playwright.py`, change the `_cull_html` definition line from:

```python
def _cull_html(html: str) -> str:  # pragma: no cover
```

to:

```python
def _cull_html(html: str) -> str:
```

Do not edit the function body. Do not rename. Do not add a public alias.

2. From the epic worktree (using the repo venv available on the host, e.g. `$ASTRAL_MAIN/.venv`), run a throwaway check that is **not** committed — **neutral** search-like HTML only (no banner-pattern classes wrapping job links):

```python
from src.external.playwright import _cull_html
from src.utils.html_cull_parity import assert_html_cull_anchor_config, extract_anchor_hrefs

assert_html_cull_anchor_config()
raw = (
    "<!DOCTYPE html><html><body>"
    '<div class="results"><a href="/jobs/123">Engineer</a>'
    '<a href="/jobs/456">Manager</a></div>'
    "<script>evil()</script></body></html>"
)
a = _cull_html(raw)
b = _cull_html(raw)
assert a == b, "determinism failed"
assert extract_anchor_hrefs(raw) == extract_anchor_hrefs(a), (
    extract_anchor_hrefs(raw),
    extract_anchor_hrefs(a),
)
```

3. Stage 3 owns the **banner-still-strips** synthetic separately. Do not fold banner-wrapped job links into the Stage 2 smoke check.

⚠️ **Decision — synthetic split:** One fixture proves determinism + href preservation without banner collision; one fixture proves banners still strip. Real AST-1194 search pages are the AC3 authority for production markup.

**Commit:** `code(AST-1232): Stage 2 — expose _cull_html to coverage`

---

## Stage 3: Offline verify script + AST-1194 capture gate

**Done when:** `scripts/spikes/ast_1232_verify_server_cull.py` runs clean on synthetic fixtures; when AST-1194 search captures exist, it also runs clean on those files and writes `debug/spikes/AST-1232/verify_report.json` (gitignored). If search captures are missing, the builder **stops** and comments (see gate below) — does not invent LinkedIn/Indeed HTML.

1. Add `scripts/spikes/ast_1232_verify_server_cull.py` (scripts are layer-exempt). Defaults:

   - `--captures-dir` default: `<repo>/debug/spikes/AST-1194/captures` if that path exists under the epic worktree, else `$ASTRAL_MAIN/debug/spikes/AST-1194/captures` when `ASTRAL_MAIN` is set, else `<repo>/debug/spikes/AST-1194/captures`.
   - `--out-dir` default: `<repo>/debug/spikes/AST-1232/` (create parents; never write under `docs/` or repo-root `artifacts/`).

2. Script behavior (exact checks):

   - Call `assert_html_cull_anchor_config()`.
   - **Synthetic determinism:** fixed HTML string (neutral search-like, job links not under banner patterns) → `_cull_html` twice → outputs `==`; also `extract_anchor_hrefs(raw) == extract_anchor_hrefs(culled)`.
   - **Synthetic banner still strips:** HTML with an `<a href>` inside an element whose class contains `cookie` → that href absent from culled href set (proves banner path still live).
   - **Normalize sanity:** two culled strings that differ only by attribute order → `culled_html_equivalent` is True.
   - **Captures (when present):** for each `*.html` in captures dir (skip names starting with `_`), run determinism (`_cull_html` twice → `==`) and href-set equality. Record per-file raw/culled byte sizes in the report (measurement only; payload-reduction AC is **AST-1234**).
   - Write `verify_report.json` under `--out-dir` with pass/fail per check. Exit non-zero on any failure.

3. **Capture gate:** Search-labelled captures are required to close AC3 on real pages. Treat a file as a search capture if its filename contains `search` (case-insensitive) **or** its sibling `*.meta.json` has a `label` / `kind` / `pageType` field equal to `search` (case-insensitive) when present.

   - If **zero** search captures are found: **STOP.** Do not mark the stage done. Comment on **AST-1232**:

     ```
     🛑 Stage 3 blocked: AST-1194 search captures missing
     Step: offline verify against real search pages
     Issue: debug/spikes/AST-1194/captures/ has no search-labelled .html (producer ready; captures not dropped in yet per AST-1194).
     Proposed resolutions: (1) Susan drops LinkedIn + Indeed search captures into that dir and re-assign Ada; (2) Chuckles re-opens AST-1194 capture handoff.
     ```

     Also comment one line on **parent AST-1172** pointing at that blocker. Leave product commits from Stages 1–2 on the publish ref; do not invent captures; do not skip the gate.

   - If search captures exist and href-set equality fails: **STOP** and comment on **parent AST-1172** with the delta (raise finding). Do not change `html_cull`.

4. Run the script once during build after Stages 1–2 land. Do not commit anything under `debug/`.

**Commit:** `code(AST-1232): Stage 3 — server cull offline verify spike`

---

## Betty handoff (not engineer work)

Engineers do not edit `tests/` or `docs/test-bible/**`. After Code Complete, Betty's `qa-child` should lock at least:

1. `assert_html_cull_anchor_config` passes on real config; fails when `'a'` removed or `'href'` added to strip list (mutate a copy dict in the test — do not edit `config.py`).
2. `_cull_html` determinism: same synthetic input → identical output across two calls.
3. Href preservation on the neutral search-like synthetic; banner synthetic drops the banner-wrapped href.
4. `culled_html_equivalent` true for attribute-order / whitespace variants of the same culled tree; false when an href value differs.
5. Missing required `html_cull` keys still raise `ValueError` from `_cull_html` (existing fail-fast paths).

Prefer small inline HTML strings in component tests (no committed LinkedIn dumps). Optional: tests may skip real-capture paths when the gitignored directory is empty.

---

## Self-Assessment

**Scope:** `Single-Component` — new utils parity helpers + one-line coverage-surface edit on `_cull_html` + committed spike verify script; no extension, no rule-delivery, no keep/discard config edits.

**Conf:** `Medium` — server cull behavior and allow-list are readable and already keep `<a href>`; real-page AC3 depends on AST-1194 search captures that are not on disk yet (producer ready, captures pending Susan), so Stage 3 has an explicit stop gate rather than a guessed fixture.

**Risk:** `Medium` — a wrong normalization predicate would let AST-1234 ship a divergent client cull that "passes" parity while dropping discovery hrefs; a false raise on AC3 would block the epic without a config bug.

---

## Code rules self-review

| Rule | Status |
|------|--------|
| §1.3 DRY | Helpers centralize normalize/compare/href extract; do not fork `_cull_html` |
| §1.4 / §2.1 config | Read `html_cull` only; no hardcoded allow-list copy; raise-only on unsafe config |
| §2.4 batch | N/A — no batch/claim work |
| §2.6 state machine | N/A |
| §3.3 imports | utils → utils/config only; spike script may import external + utils; no ui→external |
| §3.5 naming | `html_cull_parity.py`, snake_case functions |
| §3.6 spikes | Report/output under `debug/spikes/AST-1232/`; script under `scripts/spikes/`; no repo-root `artifacts/` |
| Test-tree ban | No `tests/` or bible edits in engineer commits |

No unresolved rule conflicts. Conf stays `Medium` for the capture gate, not `!!-NONE`.
