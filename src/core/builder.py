"""
AST-294: print-oriented resume / cover HTML builder.

Read-only renderer — no do_task, no dispatcher, no ui/external imports.
Public: ``build_resume``, ``build_resume_from_job``, ``build_cover_letter``,
``build_cover_letter_from_job``, ``build_base_resume``.

``get_candidate`` / DB rows expose ``candidate_data`` as the nested blob that
contains ``profile``, ``artifacts``, and ``context``. ``build_resume_from_job``
expects that inner shape (or a full row — see ``_coerce_candidate_blob``).
"""

from __future__ import annotations

import copy
import html
import json
import re
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from src.core import candidate as candidate_mod
from src.core import tracker as tracker_mod
from src.data import database
from src.utils.config import BUILD_CONFIG, RESUME_STRUCTURE_CONTACT_SECTION_IDS
from src.utils.formatting import split_to_list

# Body section keys in render order (matches legacy ResumeSite layout / artifact keys).
_RESUME_BODY_KEYS: Tuple[str, ...] = (
    "professional_summary",
    "core_competencies",
    "experience",
    "prior_experience",
    "education_certifications",
    "technical_skills",
)

_KEY_TO_SECTION_ID: Dict[str, str] = {
    "professional_summary": "summary",
    "core_competencies": "competencies",
    "experience": "experience",
    "prior_experience": "prior-experience",
    "education_certifications": "education",
    "technical_skills": "skills",
}

_KEY_TO_HEADING: Dict[str, str] = {
    "professional_summary": "Professional Summary",
    "core_competencies": "Core Competencies",
    "experience": "Experience",
    "prior_experience": "Prior Experience",
    "education_certifications": "Education & Certifications",
    "technical_skills": "Technical Skills",
}


def _coerce_candidate_blob(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Inner ``candidate_data`` dict, or unwrap a full ``get_candidate`` row."""
    if not isinstance(raw, dict):
        return {}
    inner = raw.get("candidate_data")
    if isinstance(inner, dict):
        return inner
    return raw


def build_resume(job_id: str) -> str:
    """Load job + owning candidate by id, then render HTML (one DB read for job)."""
    job = tracker_mod.get_job(job_id)
    if not job:
        raise ValueError(f"Job not found: {job_id}")
    company_key = job.get("company")
    if not company_key or not isinstance(company_key, str):
        raise ValueError("Job missing company short name")
    company_row = database.get_company(company_key.strip())
    if not company_row:
        raise ValueError(f"Company not found: {company_key!r}")
    candidate_id = company_row.get("candidate_id")
    if not candidate_id:
        raise ValueError(f"Company {company_key!r} has no candidate_id")
    row = candidate_mod.get_candidate(str(candidate_id))
    if not row:
        raise ValueError(f"Candidate not found: {candidate_id}")
    return build_resume_from_job(job, _coerce_candidate_blob(row))


def build_resume_from_job(
    job: Dict[str, Any],
    candidate_data: Dict[str, Any],
    *,
    include_cover: bool = False,
) -> str:
    """Render job-tailored resume HTML from an in-memory job row + candidate blob (no job fetch).

    ``candidate_data`` is the inner dict (``profile``, ``artifacts``, ``context``) or a full
    DB row from ``get_candidate`` (nested ``candidate_data`` is unwrapped).
    """
    cd = _coerce_candidate_blob(candidate_data)
    job_data = job.get("job_data")
    if not isinstance(job_data, dict):
        job_data = {}
    structure = candidate_mod.resolve_resume_structure(cd)
    render = _resolve_resume_sections(job_data, cd)
    render = candidate_mod.filter_content_to_resume_structure(render, structure)
    _apply_profile_to_render_dict(render, cd.get("profile") or {})
    style = _merge_effective_style(cd)
    cover = _resolve_cover_letter(job_data, cd)
    markers = _apply_resume_text_markers(render)
    ordered_body = _structure_ordered_body_ids(structure)
    titles = candidate_mod.resume_section_titles(structure)
    kw = job_data.get("critical_keywords")
    return _emit_html_document(
        markers,
        style,
        include_cover=include_cover and cover is not None,
        cover_letter=cover or {},
        critical_keywords=kw,
        emit_prior_experience=bool((markers.get("prior_experience") or "").strip()),
        cover_profile=cd.get("profile") or {},
        body_section_ids=ordered_body,
        body_section_titles=titles,
    )


def build_cover_letter(job_id: str) -> str:
    """Load job + owning candidate by id, then render cover-letter HTML only."""
    job = tracker_mod.get_job(job_id)
    if not job:
        raise ValueError(f"Job not found: {job_id}")
    company_key = job.get("company")
    if not company_key or not isinstance(company_key, str):
        raise ValueError("Job missing company short name")
    company_row = database.get_company(company_key.strip())
    if not company_row:
        raise ValueError(f"Company not found: {company_key!r}")
    candidate_id = company_row.get("candidate_id")
    if not candidate_id:
        raise ValueError(f"Company {company_key!r} has no candidate_id")
    row = candidate_mod.get_candidate(str(candidate_id))
    if not row:
        raise ValueError(f"Candidate not found: {candidate_id}")
    return build_cover_letter_from_job(job, _coerce_candidate_blob(row))


def build_cover_letter_from_job(job: Dict[str, Any], candidate_data: Dict[str, Any]) -> str:
    """Render cover-letter HTML only from job artifacts (no resume body sections)."""
    cd = _coerce_candidate_blob(candidate_data)
    job_data = job.get("job_data")
    if not isinstance(job_data, dict):
        job_data = {}
    cover = _resolve_cover_letter(job_data, cd)
    if cover is None:
        raise ValueError("No cover letter content for job")
    render: Dict[str, Any] = {}
    _apply_profile_to_render_dict(render, cd.get("profile") or {})
    markers = _apply_resume_text_markers(render)
    style = _merge_effective_style(cd)
    return _emit_html_document(
        markers,
        style,
        include_cover=True,
        cover_letter=cover,
        critical_keywords=None,
        emit_prior_experience=False,
        cover_profile=cd.get("profile") or {},
        body_section_ids=[],
        body_section_titles={},
    )


def build_base_resume(candidate_id: str) -> str:
    """Candidate-only resume HTML from ``artifacts.base_resume`` (no job, no cover, no ATS strip)."""
    row = candidate_mod.get_candidate(candidate_id)
    if not row:
        raise ValueError(f"Candidate not found: {candidate_id}")
    cd = _coerce_candidate_blob(row)
    br = (cd.get("artifacts") or {}).get("base_resume")
    if not isinstance(br, dict) or not br:
        raise ValueError("Candidate missing artifacts.base_resume")
    structure = candidate_mod.resolve_resume_structure(cd)
    render = candidate_mod.filter_content_to_resume_structure(dict(br), structure)
    _apply_profile_to_render_dict(render, cd.get("profile") or {})
    style = _merge_effective_style(cd)
    markers = _apply_resume_text_markers(render)
    ordered_body = _structure_ordered_body_ids(structure)
    titles = candidate_mod.resume_section_titles(structure)
    return _emit_html_document(
        markers,
        style,
        include_cover=False,
        cover_letter={},
        critical_keywords=None,
        emit_prior_experience=bool((markers.get("prior_experience") or "").strip()),
        body_section_ids=ordered_body,
        body_section_titles=titles,
    )


def _resolve_resume_sections(job_data: dict, candidate_data: dict) -> dict:
    """Prefer job resume_content; else base_resume. Raises if neither is a non-empty dict."""
    artifacts = job_data.get("artifacts") or {}
    rc = artifacts.get("resume_content")
    if _is_nonempty_resume_dict(rc):
        return dict(rc)
    br = (candidate_data.get("artifacts") or {}).get("base_resume")
    if _is_nonempty_resume_dict(br):
        return dict(br)
    raise ValueError("No resume_content on job and no base_resume on candidate")


def _is_nonempty_resume_dict(val: Any) -> bool:
    if not isinstance(val, dict) or not val:
        return False
    return True


def _cover_letter_fields_for_read(cl: dict) -> dict:
    """Map Subject/Letter or legacy re_line/body to emit-friendly re_line/body/signature."""
    return {
        "re_line": str(cl.get("Subject") or cl.get("re_line") or ""),
        "body": str(cl.get("Letter") or cl.get("body") or ""),
        "signature": str(cl.get("signature") or ""),
    }


def _resolve_cover_letter(job_data: dict, candidate_data: dict) -> Optional[dict]:
    """Job cover_letter dict if any field non-empty; else sample_cover_text → body-only v1 mapping."""
    artifacts = job_data.get("artifacts") or {}
    cl = artifacts.get("cover_letter")
    if isinstance(cl, dict) and _cover_letter_nonempty(cl):
        return _cover_letter_fields_for_read(cl)
    sample = (candidate_data.get("context") or {}).get("sample_cover_text")
    if isinstance(sample, str) and sample.strip():
        # v1: entire sample string is body; re_line/signature empty until UI captures structured cover.
        return {"re_line": "", "body": sample.strip(), "signature": ""}
    return None


def _cover_letter_nonempty(cl: dict) -> bool:
    normalized = _cover_letter_fields_for_read(cl)
    for k in ("re_line", "body", "signature"):
        v = normalized.get(k)
        if isinstance(v, str) and v.strip():
            return True
    return False


def _apply_profile_to_render_dict(render: dict, profile: dict) -> None:
    """Overwrite identity/contact from profile; never use artifact strings for those fields when profile supplies."""
    first = (profile.get("first") or "").strip()
    last = (profile.get("last") or "").strip()
    name = f"{first} {last}".strip()
    if name:
        render["candidate_name"] = name
    # DATA_SHAPES has no profile headline for job title — keep artifact candidate_title (still escaped at emit).
    parts: List[str] = []
    email = (profile.get("contact_email") or profile.get("reply_email") or "").strip()
    if email:
        parts.append(email)
    phone = (profile.get("phone") or "").strip()
    if phone:
        parts.append(phone)
    li = (profile.get("linkedin_url") or "").strip()
    if li:
        parts.append(li)
    gh = (profile.get("github") or "").strip()
    if gh:
        parts.append(gh)
    loc = (profile.get("location") or "").strip()
    if loc:
        parts.append(loc)
    if parts:
        render["candidate_contact_detail"] = "\u00a0• ".join(parts)


def _merge_effective_style(candidate_data: dict) -> dict:
    """``default_style`` deep-copied; accent from resume_structure, else legacy base_resume."""
    base = copy.deepcopy(BUILD_CONFIG.get("default_style") or {})
    colors = base.setdefault("colors", {})
    structure = candidate_mod.resolve_resume_structure(candidate_data)
    ac = structure.get("accent_color")
    if isinstance(ac, str) and ac.strip():
        colors["default_accent"] = ac.strip()
        colors["default_header"] = ac.strip()
    else:
        br = (candidate_data.get("artifacts") or {}).get("base_resume")
        if isinstance(br, dict):
            legacy = br.get("accent_color")
            if isinstance(legacy, str) and legacy.strip():
                colors["default_accent"] = legacy.strip()
                colors["default_header"] = legacy.strip()
    return base


def _structure_ordered_body_ids(resume_structure: dict) -> List[str]:
    """Enabled section ids for body emission (excludes contact/header trio)."""
    contact = set(RESUME_STRUCTURE_CONTACT_SECTION_IDS)
    return [sid for sid in candidate_mod.enabled_resume_section_ids(resume_structure) if sid not in contact]


def _apply_resume_text_markers(render: dict) -> dict:
    """Return shallow copy with legacy marker transforms on string values (NBSP / hyphen conventions)."""
    out = dict(render)
    for k, v in list(out.items()):
        if isinstance(v, str):
            out[k] = _resume_site_markers(v)
        else:
            out[k] = v
    return out


def _resume_site_markers(text: str) -> str:
    """``__`` → NBSP, ``~~`` → non-breaking hyphen (legacy ResumeSite / PS pipeline)."""
    if not text:
        return text
    t = text.replace("__", "\u00a0")
    t = t.replace("~~", "\u2011")
    t = t.replace(" • ", "\u00a0• ")
    return t


def _emit_html_document(
    render: dict,
    style: dict,
    *,
    include_cover: bool,
    cover_letter: dict,
    critical_keywords: Any,
    emit_prior_experience: bool,
    cover_profile: Optional[dict] = None,
    body_section_ids: Optional[List[str]] = None,
    body_section_titles: Optional[Dict[str, str]] = None,
) -> str:
    fonts = style.get("fonts") or {}
    colors = style.get("colors") or {}
    ak = style.get("ats_keyword_block") or BUILD_CONFIG["default_style"]["ats_keyword_block"]
    accent = colors.get("default_accent", "#3c2c6e")
    header_c = colors.get("default_header", accent)
    page_bg = colors.get("page_background", "#f5f5f5")
    hstack = fonts.get("heading_stack", "sans-serif")
    bstack = fonts.get("body_stack", "serif")
    lstack = fonts.get("list_stack", hstack)

    name = html.escape(str(render.get("candidate_name") or ""))
    title = html.escape(str(render.get("candidate_title") or ""))
    contact = html.escape(str(render.get("candidate_contact_detail") or ""))

    body_sections_html = _emit_body_sections_html(
        render,
        body_section_ids or list(_RESUME_BODY_KEYS),
        body_section_titles or {},
    )

    cover_html = ""
    if include_cover and cover_letter:
        cover_html = _emit_cover_sections_html(cover_letter, cover_profile or {})

    ats_html = _emit_ats_block(critical_keywords, ak)

    prior_rule = ""
    if emit_prior_experience:
        prior_rule = "\n  #prior-experience { page-break-before: always; }"

    css = f""":root {{
  --max-width: 800px;
  --accent-color: {accent};
  --header-color: {header_c};
  --text-primary: #1a1a1a;
  --text-secondary: #444;
  --text-tertiary: #666;
  --header-font-family: {hstack};
  --body-font-family: {bstack};
  --list-font-family: {lstack};
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  padding: 14px 20px 20px;
  background: {page_bg};
  font-family: var(--body-font-family);
  color: var(--text-primary);
  line-height: 1.6;
  font-size: 15px;
}}
h1, h2, h3 {{
  font-family: var(--header-font-family);
  text-align: center;
}}
.contact, .competencies-list, .skill-category p {{
  font-family: var(--list-font-family);
  text-align: center;
}}
p, .prose-block, ul, li {{
  font-family: var(--body-font-family);
  text-align: left;
  line-height: 1.25;
  white-space: pre-wrap;
}}
.header {{ max-width: var(--max-width); margin: 0 auto 2px; }}
h1 {{
  margin: 20px 0 0;
  font-size: 33px;
  line-height: 1.1;
  font-weight: 700;
  letter-spacing: -0.5px;
  color: var(--header-color);
}}
.contact {{ margin: 6px 0 0; font-size: 14px; color: var(--text-secondary);
  display: flex; flex-wrap: wrap; gap: 8px 16px; justify-content: center; }}
.content {{ max-width: var(--max-width); margin: 0 auto; }}
h2 {{
  margin: 18px 0 2px;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  color: var(--accent-color);
  display: flex;
  align-items: center;
}}
h2::before, h2::after {{
  content: '';
  flex: 1;
  height: 1px;
  border-top: 1px solid var(--header-color);
}}
h2::before {{ margin-right: 12px; }}
h2::after {{ margin-left: 12px; }}
.summary-intro {{ margin: 6px; line-height: 1.25; }}
.competencies-list {{ margin: 6px 0 0; line-height: 1.8; color: var(--text-secondary);
  text-transform: uppercase; letter-spacing: 0.2px; font-size: 13.5px; }}
section {{ margin-bottom: 0; }}
.cover-block {{ margin-top: 24px; max-width: var(--max-width); margin-left: auto; margin-right: auto; text-align: left; }}
.cover-block p {{ white-space: pre-wrap; }}
.cover-signoff img {{ display: block; margin-bottom: 8px; }}
.cover-signoff p {{ white-space: pre-wrap; margin: 0; }}
.ats-keywords {{
  font-size: {ak["font_size_px"]}px;
  line-height: {ak["line_height"]};
  color: {ak["text_color"]};
  background: {ak["background"]};
  position: {ak["position"]};
  left: {ak["left_px"]}px;
  width: {ak["width_px"]}px;
  height: {ak["height_px"]}px;
  overflow: {ak["overflow"]};
}}
@media print {{
  body {{ background: #fff; padding: 0; }}
  h2 {{ page-break-after: avoid; }}
  #competencies {{ page-break-after: avoid; }}
  .role {{ page-break-inside: avoid; }}
  p, li {{ orphans: 3; widows: 3; }}{prior_rule}
}}
"""
    title_esc = html.escape(f"{render.get('candidate_name', '')} — Resume".strip() or "Resume")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title_esc}</title>
  <style>
{css}
  </style>
</head>
<body>
  <header class="header">
    <h1>{name}{" • " + title if title else ""}</h1>
    <div class="contact"><span>{contact}</span></div>
  </header>
  <main class="content">
{body_sections_html}
{cover_html}
  </main>
{ats_html}
</body>
</html>
"""


def _emit_body_sections_html(
    render: dict,
    ordered_ids: List[str],
    titles: Dict[str, str],
) -> str:
    chunks: List[str] = []
    for key in ordered_ids:
        raw = render.get(key)
        if raw is None:
            continue
        if isinstance(raw, (dict, list)):
            text = _format_experience_value(raw)
        else:
            text = str(raw) if raw is not None else ""
        if not str(text).strip():
            continue
        sid = _KEY_TO_SECTION_ID.get(key, key)
        heading = html.escape(titles.get(key, _KEY_TO_HEADING.get(key, key.replace("_", " ").title())))
        if key == "professional_summary":
            paras = [p.strip() for p in re.split(r"\n\s*\n", str(text)) if p.strip()]
            body = "\n".join(
                f'      <p class="summary-intro">{html.escape(p)}</p>' for p in paras
            )
            chunks.append(
                f"""    <section aria-labelledby="{sid}">
      <h2 id="{sid}">{heading}</h2>
{body}
    </section>"""
            )
            continue
        inner = html.escape(str(text))
        if key == "core_competencies":
            chunks.append(
                f"""    <section aria-labelledby="{sid}">
      <h2 id="{sid}">{heading}</h2>
      <p class="competencies-list">{inner}</p>
    </section>"""
            )
        elif key == "experience":
            chunks.append(
                f"""    <section aria-labelledby="{sid}">
      <h2 id="{sid}">{heading}</h2>
      <div class="prose-block">{inner}</div>
    </section>"""
            )
        elif key == "prior_experience":
            chunks.append(
                f"""    <section aria-labelledby="{sid}">
      <h2 id="{sid}">{heading}</h2>
      <p class="competencies-list">{inner}</p>
    </section>"""
            )
        elif key == "education_certifications":
            chunks.append(
                f"""    <section aria-labelledby="{sid}">
      <h2 id="{sid}">{heading}</h2>
      <div class="education-list"><p class="prose-block">{inner}</p></div>
    </section>"""
            )
        elif key == "technical_skills":  # pragma: no branch
            chunks.append(
                f"""    <section aria-labelledby="{sid}">
      <h2 id="{sid}">{heading}</h2>
      <div class="skills-grid"><div class="skill-category"><p>{inner}</p></div></div>
    </section>"""
            )
    return "\n".join(chunks)


def _format_experience_value(val: Any) -> str:
    """v1: structured experience not yet modeled — JSON for visibility in HTML source."""
    if isinstance(val, str):
        return val
    try:
        return json.dumps(val, indent=2)
    except TypeError:
        return str(val)


def _safe_image_src(raw: Any) -> Optional[str]:
    """Return ``src`` only for http(s) or ``data:image/(jpeg|png)`` URLs; else ``None``.

    Rejected values never reach the ``src`` attribute: non-strings, empty strings,
    wrong schemes (``javascript:``, ``file:``, ``data:text/html``, ``data:image/svg``,
    ``data:image/jpg`` without ``jpeg`` spelling, etc.), and strings containing CR/LF
    or ``<`` (attribute-break / injection hardening).
    """
    if not isinstance(raw, str):
        return None
    s = raw.strip()
    if not s or "\n" in s or "\r" in s or "<" in s:
        return None
    low = s.lower()
    if low.startswith("https://") or low.startswith("http://"):
        if urlparse(s).scheme not in ("http", "https"):
            return None
        return s
    if low.startswith("data:image/jpeg") or low.startswith("data:image/png"):
        return s
    return None


def _emit_cover_signoff_html(cover: dict, profile: dict) -> str:
    """Cover sign-off: optional profile image (validated ``src``) then signature text."""
    sig = (cover.get("signature") or "").strip()
    safe_src = _safe_image_src((profile or {}).get("cover_letter_signature_image"))
    if not sig and not safe_src:
        return ""
    inner_lines: List[str] = []
    if safe_src:
        src_esc = html.escape(safe_src, quote=True)
        inner_lines.append(
            # Non-empty alt: Radia review (a11y); static label only (src is already escaped).
            f'      <img src="{src_esc}" alt="Cover letter signature" style="max-width:240px;height:auto;" />'
        )
    if sig:
        inner_lines.append(f'      <p>{html.escape(sig)}</p>')
    inner = "\n".join(inner_lines)
    return f"""    <section class="cover-block cover-signoff" aria-label="Cover sign-off">
{inner}
    </section>"""


def _emit_cover_sections_html(cover: dict, profile: dict) -> str:
    parts: List[str] = []
    re_line = (cover.get("re_line") or "").strip()
    body = (cover.get("body") or "").strip()
    if re_line:
        parts.append(
            f'    <section class="cover-block" aria-label="Cover re line"><p>{html.escape(re_line)}</p></section>'
        )
    if body:
        parts.append(
            f'    <section class="cover-block" aria-label="Cover body"><p>{html.escape(body)}</p></section>'
        )
    signoff = _emit_cover_signoff_html(cover, profile)
    if signoff:
        parts.append(signoff)
    return "\n".join(parts)


def _emit_ats_block(critical_keywords: Any, ak: dict) -> str:
    if critical_keywords is None:
        return ""
    if isinstance(critical_keywords, str):
        raw = critical_keywords
    else:
        raw = str(critical_keywords)
    tokens = split_to_list(raw, ",") if raw.strip() else []
    if not tokens:
        return ""
    inner = " ".join(html.escape(t) for t in tokens if t)
    if not inner:
        return ""
    return f'  <div class="ats-keywords" aria-hidden="true">{inner}</div>\n'
