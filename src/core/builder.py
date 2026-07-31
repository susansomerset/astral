"""
AST-294: print-oriented resume / cover HTML builder.

Read-only renderer — no do_task, no dispatcher, no ui/external imports.
Public: ``build_resume``, ``build_resume_from_job``, ``build_cover_letter``,
``build_cover_letter_from_job``, ``build_base_resume``, ``build_session_base_resume``,
``build_session_cover_letter``.

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
from src.utils.logging import get_logger

_log = get_logger(__name__)

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


def _builder_job_identifier(job: Dict[str, Any]) -> str:
    """Primary debug identifier for a job row (§1.5.1 style D)."""
    return str(job.get("astral_job_id") or job.get("job_title") or "?")


def _resume_content_source_label(job_data: dict, candidate_data: dict) -> str:
    """Read-only label for which blob supplies resume sections (no raises)."""
    artifacts = (job_data or {}).get("artifacts") or {}
    rc = artifacts.get("resume_content")
    if _is_nonempty_resume_dict(rc):
        return "job_data.artifacts.resume_content"
    br = ((candidate_data or {}).get("artifacts") or {}).get("base_resume")
    if _is_nonempty_resume_dict(br):
        return "candidate_data.artifacts.base_resume"
    return "missing"


def _cover_letter_source_label(job_data: dict, candidate_data: dict) -> Optional[str]:
    """Read-only label for cover letter provenance, or None when no cover."""
    artifacts = (job_data or {}).get("artifacts") or {}
    cl = artifacts.get("cover_letter")
    if isinstance(cl, dict) and _cover_letter_nonempty(cl):
        return "job_data.artifacts.cover_letter"
    sample = ((candidate_data or {}).get("context") or {}).get("sample_cover_text")
    if isinstance(sample, str) and sample.strip():
        return "candidate_data.context.sample_cover_text"
    return None


def _accent_source_label(candidate_data: dict) -> str:
    """Read-only label for accent color resolution path."""
    structure = candidate_mod.resolve_resume_structure(candidate_data)
    ac = structure.get("accent_color")
    if isinstance(ac, str) and ac.strip():
        return "resume_structure.accent_color"
    br = ((candidate_data or {}).get("artifacts") or {}).get("base_resume")
    if isinstance(br, dict):
        legacy = br.get("accent_color")
        if isinstance(legacy, str) and legacy.strip():
            return "artifacts.base_resume.accent_color"
    return "BUILD_CONFIG.default_style"


def _emit_builder_failure(
    *,
    func: str,
    identifier: str,
    message: str,
    debug: bool,
) -> None:
    """Emit contract header for a terminal ValueError path."""
    if not debug:
        return
    _log.set_debug_flag(True)
    _log.debug_index(
        func=func,
        index=1,
        total=1,
        identifier=identifier,
        outcome=f"error — {message}",
    )


def build_resume(job_id: str, *, debug: bool = False) -> str:
    """Load job + owning candidate by id, then render HTML (one DB read for job)."""
    job = tracker_mod.get_job(job_id)
    if not job:
        msg = f"Job not found: {job_id}"
        _emit_builder_failure(
            func="builder.build_resume", identifier=job_id, message=msg, debug=debug
        )
        raise ValueError(msg)
    company_key = job.get("company")
    if not company_key or not isinstance(company_key, str):
        msg = "Job missing company short name"
        _emit_builder_failure(
            func="builder.build_resume", identifier=job_id, message=msg, debug=debug
        )
        raise ValueError(msg)
    company_row = database.get_company(company_key.strip())
    if not company_row:
        msg = f"Company not found: {company_key!r}"
        _emit_builder_failure(
            func="builder.build_resume", identifier=job_id, message=msg, debug=debug
        )
        raise ValueError(msg)
    candidate_id = company_row.get("candidate_id")
    if not candidate_id:
        msg = f"Company {company_key!r} has no candidate_id"
        _emit_builder_failure(
            func="builder.build_resume", identifier=job_id, message=msg, debug=debug
        )
        raise ValueError(msg)
    row = candidate_mod.get_candidate(str(candidate_id))
    if not row:
        msg = f"Candidate not found: {candidate_id}"
        _emit_builder_failure(
            func="builder.build_resume", identifier=job_id, message=msg, debug=debug
        )
        raise ValueError(msg)
    return build_resume_from_job(job, _coerce_candidate_blob(row), debug=debug)


def build_resume_from_job(
    job: Dict[str, Any],
    candidate_data: Dict[str, Any],
    *,
    include_cover: bool = False,
    debug: bool = False,
) -> str:
    """Render job-tailored resume HTML from an in-memory job row + candidate blob (no job fetch).

    ``candidate_data`` is the inner dict (``profile``, ``artifacts``, ``context``) or a full
    DB row from ``get_candidate`` (nested ``candidate_data`` is unwrapped).
    """
    cd = _coerce_candidate_blob(candidate_data)
    if debug:
        _log.set_debug_flag(True)
    identifier = _builder_job_identifier(job)
    job_data = job.get("job_data")
    if not isinstance(job_data, dict):
        job_data = {}
    structure = candidate_mod.resolve_resume_structure(cd)
    try:
        render = _resolve_resume_sections(job_data, cd)
    except ValueError as exc:
        _emit_builder_failure(
            func="builder.build_resume_from_job",
            identifier=identifier,
            message=str(exc),
            debug=debug,
        )
        raise
    render = candidate_mod.filter_content_to_resume_structure(render, structure)
    _apply_profile_to_render_dict(render, cd.get("profile") or {})
    style = _merge_effective_style(cd)
    cover = _resolve_cover_letter(job_data, cd)
    markers = _apply_resume_text_markers(render)
    ordered_body = _structure_ordered_body_ids(structure)
    titles = candidate_mod.resume_section_titles(structure)
    kw = job_data.get("critical_keywords")
    html_out = _emit_html_document(
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
    if debug:
        enabled = candidate_mod.enabled_resume_section_ids(structure)
        content_keys = _render_content_keys(markers)
        cover_src = _cover_letter_source_label(job_data, cd)
        kw_count = (
            len(split_to_list(str(kw), ","))
            if isinstance(kw, str) and kw.strip()
            else (len(kw) if isinstance(kw, (list, tuple)) else 0)
        )
        _log.debug_index(
            func="builder.build_resume_from_job",
            index=1,
            total=1,
            identifier=identifier,
            outcome="success — resume html",
        )
        _log.debug_detail(f"resume_source={_resume_content_source_label(job_data, cd)!r}")
        _log.debug_detail(f"enabled_sections={enabled!r}")
        _log.debug_detail(f"body_section_ids={ordered_body!r}")
        _log.debug_detail(f"render_keys={content_keys!r}")
        _log.debug_detail(
            f"include_cover={include_cover} cover_source={cover_src!r} "
            f"cover_included={include_cover and cover is not None}"
        )
        _log.debug_detail(f"accent_source={_accent_source_label(cd)!r}")
        _log.debug_detail(f"ats_keywords_count={kw_count}")
        _log.debug_detail(f"html_chars={len(html_out)}")
        _log.debug_detail("html_preview:")
        _log.debug_detail_block(html_out)
    return html_out


def build_cover_letter(job_id: str, *, debug: bool = False) -> str:
    """Load job + owning candidate by id, then render cover-letter HTML only."""
    job = tracker_mod.get_job(job_id)
    if not job:
        msg = f"Job not found: {job_id}"
        _emit_builder_failure(
            func="builder.build_cover_letter", identifier=job_id, message=msg, debug=debug
        )
        raise ValueError(msg)
    company_key = job.get("company")
    if not company_key or not isinstance(company_key, str):
        msg = "Job missing company short name"
        _emit_builder_failure(
            func="builder.build_cover_letter", identifier=job_id, message=msg, debug=debug
        )
        raise ValueError(msg)
    company_row = database.get_company(company_key.strip())
    if not company_row:
        msg = f"Company not found: {company_key!r}"
        _emit_builder_failure(
            func="builder.build_cover_letter", identifier=job_id, message=msg, debug=debug
        )
        raise ValueError(msg)
    candidate_id = company_row.get("candidate_id")
    if not candidate_id:
        msg = f"Company {company_key!r} has no candidate_id"
        _emit_builder_failure(
            func="builder.build_cover_letter", identifier=job_id, message=msg, debug=debug
        )
        raise ValueError(msg)
    row = candidate_mod.get_candidate(str(candidate_id))
    if not row:
        msg = f"Candidate not found: {candidate_id}"
        _emit_builder_failure(
            func="builder.build_cover_letter", identifier=job_id, message=msg, debug=debug
        )
        raise ValueError(msg)
    return build_cover_letter_from_job(job, _coerce_candidate_blob(row), debug=debug)


def build_cover_letter_from_job(
    job: Dict[str, Any],
    candidate_data: Dict[str, Any],
    *,
    debug: bool = False,
) -> str:
    """Render cover-letter HTML only from job artifacts (no resume body sections)."""
    cd = _coerce_candidate_blob(candidate_data)
    if debug:
        _log.set_debug_flag(True)
    identifier = _builder_job_identifier(job)
    job_data = job.get("job_data")
    if not isinstance(job_data, dict):
        job_data = {}
    cover = _resolve_cover_letter(job_data, cd)
    if cover is None:
        msg = "No cover letter content for job"
        _emit_builder_failure(
            func="builder.build_cover_letter_from_job",
            identifier=identifier,
            message=msg,
            debug=debug,
        )
        raise ValueError(msg)
    render: Dict[str, Any] = {}
    _apply_profile_to_render_dict(render, cd.get("profile") or {})
    markers = _apply_resume_text_markers(render)
    style = _merge_effective_style(cd)
    html_out = _emit_html_document(
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
    if debug:
        cover_src = _cover_letter_source_label(job_data, cd)
        profile = cd.get("profile") or {}
        safe_sig = _safe_image_src(profile.get("cover_letter_signature_image"))
        _log.debug_index(
            func="builder.build_cover_letter_from_job",
            index=1,
            total=1,
            identifier=identifier,
            outcome="success — cover letter html",
        )
        _log.debug_detail(f"cover_source={cover_src!r}")
        _log.debug_detail(
            f"fields re_line={bool((cover.get('re_line') or '').strip())} "
            f"body={bool((cover.get('body') or '').strip())} "
            f"signature={bool((cover.get('signature') or '').strip())}"
        )
        _log.debug_detail(
            f"signature_image={'accepted' if safe_sig else 'absent_or_rejected'}"
        )
        _log.debug_detail(f"html_chars={len(html_out)}")
        _log.debug_detail("html_preview:")
        _log.debug_detail_block(html_out)
    return html_out


def build_base_resume(candidate_id: str, *, debug: bool = False) -> str:
    """Candidate-only resume HTML from ``artifacts.base_resume`` (no job, no cover, no ATS strip)."""
    if debug:
        _log.set_debug_flag(True)
    identifier = candidate_id
    row = candidate_mod.get_candidate(candidate_id)
    if not row:
        msg = f"Candidate not found: {candidate_id}"
        _emit_builder_failure(
            func="builder.build_base_resume", identifier=identifier, message=msg, debug=debug
        )
        raise ValueError(msg)
    cd = _coerce_candidate_blob(row)
    br = (cd.get("artifacts") or {}).get("base_resume")
    if not isinstance(br, dict) or not br:
        msg = "Candidate missing artifacts.base_resume"
        _emit_builder_failure(
            func="builder.build_base_resume", identifier=identifier, message=msg, debug=debug
        )
        raise ValueError(msg)
    structure = candidate_mod.resolve_resume_structure(cd)
    render = candidate_mod.filter_content_to_resume_structure(dict(br), structure)
    _apply_profile_to_render_dict(render, cd.get("profile") or {})
    style = _merge_effective_style(cd)
    markers = _apply_resume_text_markers(render)
    ordered_body = _structure_ordered_body_ids(structure)
    titles = candidate_mod.resume_section_titles(structure)
    html_out = _emit_html_document(
        markers,
        style,
        include_cover=False,
        cover_letter={},
        critical_keywords=None,
        emit_prior_experience=bool((markers.get("prior_experience") or "").strip()),
        body_section_ids=ordered_body,
        body_section_titles=titles,
    )
    if debug:
        enabled = candidate_mod.enabled_resume_section_ids(structure)
        content_keys = _render_content_keys(markers)
        _log.debug_index(
            func="builder.build_base_resume",
            index=1,
            total=1,
            identifier=identifier,
            outcome="success — base resume html",
        )
        _log.debug_detail("resume_source=candidate_data.artifacts.base_resume")
        _log.debug_detail(f"enabled_sections={enabled!r}")
        _log.debug_detail(f"body_section_ids={ordered_body!r}")
        _log.debug_detail(f"render_keys={content_keys!r}")
        _log.debug_detail(f"accent_source={_accent_source_label(cd)!r}")
        _log.debug_detail(f"html_chars={len(html_out)}")
        _log.debug_detail("html_preview:")
        _log.debug_detail_block(html_out)
    return html_out


def build_session_base_resume(
    resume_structure: dict,
    base_resume: dict,
    *,
    debug: bool = False,
) -> str:
    """AST-987: print HTML from in-memory structure + content — no candidate/DB bind."""
    if debug:
        _log.set_debug_flag(True)
    if not isinstance(resume_structure, dict) or not isinstance(
        resume_structure.get("sections"), dict
    ):
        msg = "resume_structure with sections is required"
        _emit_builder_failure(
            func="builder.build_session_base_resume",
            identifier="session",
            message=msg,
            debug=debug,
        )
        raise ValueError(msg)
    if not _is_nonempty_resume_dict(base_resume):
        msg = "base_resume content is required"
        _emit_builder_failure(
            func="builder.build_session_base_resume",
            identifier="session",
            message=msg,
            debug=debug,
        )
        raise ValueError(msg)
    # Synthetic blob only — never get_candidate / selected-candidate profile.
    cd = {
        "artifacts": {
            "resume_structure": resume_structure,
            "base_resume": base_resume,
        },
        "profile": {},
    }
    structure = candidate_mod.resolve_resume_structure(cd)
    render = candidate_mod.filter_content_to_resume_structure(dict(base_resume), structure)
    # Skip _apply_profile_to_render_dict — contact/header from paste section strings.
    style = _merge_effective_style(cd)
    markers = _apply_resume_text_markers(render)
    ordered_body = _structure_ordered_body_ids(structure)
    titles = candidate_mod.resume_section_titles(structure)
    html_out = _emit_html_document(
        markers,
        style,
        include_cover=False,
        cover_letter={},
        critical_keywords=None,
        emit_prior_experience=bool((markers.get("prior_experience") or "").strip()),
        body_section_ids=ordered_body,
        body_section_titles=titles,
    )
    if debug:
        enabled = candidate_mod.enabled_resume_section_ids(structure)
        content_keys = _render_content_keys(markers)
        _log.debug_index(
            func="builder.build_session_base_resume",
            index=1,
            total=1,
            identifier="session",
            outcome="success — session resume html",
        )
        _log.debug_detail("resume_source=session.in_memory")
        _log.debug_detail(f"enabled_sections={enabled!r}")
        _log.debug_detail(f"body_section_ids={ordered_body!r}")
        _log.debug_detail(f"render_keys={content_keys!r}")
        _log.debug_detail(f"accent_source={_accent_source_label(cd)!r}")
        _log.debug_detail(f"html_chars={len(html_out)}")
        _log.debug_detail("html_preview:")
        _log.debug_detail_block(html_out)
    return html_out


def build_session_cover_letter(
    fields: dict,
    *,
    candidate_id: Optional[str] = None,
    debug: bool = False,
) -> str:
    """AST-1024: SomersetCover HTML from in-memory fields — no job load / artifact write."""
    if debug:
        _log.set_debug_flag(True)
    identifier = (
        candidate_id.strip()
        if isinstance(candidate_id, str) and candidate_id.strip()
        else "session"
    )
    if not isinstance(fields, dict):
        msg = "session cover letter fields object is required"
        _emit_builder_failure(
            func="builder.build_session_cover_letter",
            identifier=identifier,
            message=msg,
            debug=debug,
        )
        raise ValueError(msg)
    cfg = BUILD_CONFIG["session_cover_letter"]
    field_defs = cfg["fields"]
    normalized: Dict[str, str] = {}
    for key, meta in field_defs.items():
        raw = fields.get(key, "")
        if raw is None:
            raw = ""
        if not isinstance(raw, str):
            msg = f"{key} must be a string"
            _emit_builder_failure(
                func="builder.build_session_cover_letter",
                identifier=identifier,
                message=msg,
                debug=debug,
            )
            raise ValueError(msg)
        if meta.get("required") and not raw.strip():
            msg = f"{key} is required"
            _emit_builder_failure(
                func="builder.build_session_cover_letter",
                identifier=identifier,
                message=msg,
                debug=debug,
            )
            raise ValueError(msg)
        normalized[key] = raw

    sig_src: Optional[str] = None
    sig_image_status = "skipped_no_candidate"
    cid = candidate_id.strip() if isinstance(candidate_id, str) else ""
    if cid:
        row = candidate_mod.get_candidate(cid)
        if not row:
            msg = f"Candidate not found: {cid}"
            _emit_builder_failure(
                func="builder.build_session_cover_letter",
                identifier=identifier,
                message=msg,
                debug=debug,
            )
            raise ValueError(msg)
        profile = _coerce_candidate_blob(row).get("profile") or {}
        sig_src = _safe_image_src(profile.get("cover_letter_signature_image"))
        sig_image_status = "accepted" if sig_src else "absent_or_rejected"

    html_out = _emit_session_cover_html_document(normalized, signature_image_src=sig_src)
    if debug:
        _log.debug_index(
            func="builder.build_session_cover_letter",
            index=1,
            total=1,
            identifier=identifier,
            outcome="success — session cover html",
        )
        for key, meta in field_defs.items():
            if meta.get("required"):
                _log.debug_detail(f"{key}_nonempty={bool(normalized[key].strip())}")
        _log.debug_detail(
            f"to_block={'present' if normalized['to_block'].strip() else 'omitted'}"
        )
        _log.debug_detail(
            f"subject={'present' if normalized['subject'].strip() else 'omitted'}"
        )
        _log.debug_detail(f"candidate_id={'used' if cid else 'not_used'}")
        _log.debug_detail(f"signature_image={sig_image_status}")
        _log.debug_detail(f"html_chars={len(html_out)}")
        _log.debug_detail("html_preview:")
        _log.debug_detail_block(html_out)
    return html_out


def _session_cover_letter_paragraphs(letter: str) -> List[str]:
    """Blank-line paragraphs; single-chunk newlines become separate paragraphs."""
    text = letter.replace("\r\n", "\n").strip()
    chunks = [c.strip() for c in re.split(r"\n\s*\n", text) if c.strip()]
    if len(chunks) == 1 and "\n" in chunks[0]:
        chunks = [c.strip() for c in chunks[0].split("\n") if c.strip()]
    return chunks


def _emit_session_cover_html_document(
    fields: dict,
    *,
    signature_image_src: Optional[str] = None,
) -> str:
    """Standalone SomersetCover DOM/CSS (session-only; does not touch job cover emit)."""
    style = BUILD_CONFIG["default_style"]
    fonts = style.get("fonts") or {}
    colors = style.get("colors") or {}
    accent = colors.get("default_accent", "#3c2c6e")
    header_c = colors.get("default_header", accent)
    page_bg = colors.get("page_background", "#f5f5f5")
    hstack = fonts.get("heading_stack", "sans-serif")
    bstack = fonts.get("body_stack", "serif")
    lstack = fonts.get("list_stack", hstack)
    text_primary = colors.get("text_primary", "#1a1a1a")
    text_secondary = colors.get("text_secondary", "#444")
    text_tertiary = colors.get("text_tertiary", "#666")
    border_light = colors.get("border_light", "#e0e0e0")
    border_medium = colors.get("border_medium", "#ccc")
    doc_title = BUILD_CONFIG["session_cover_letter"]["document_title"]
    sig_name = (fields.get("signature") or "").strip()
    meta_content = f"Cover Letter - {sig_name}" if sig_name else doc_title
    meta_tag = f'\n  <meta name="description" content="{html.escape(meta_content)}" />'

    from_lines = (fields.get("from_block") or "").replace("\r\n", "\n").split("\n")
    from_html = "<br>\n        ".join(html.escape(line) for line in from_lines)

    blocks: List[str] = [
        f'      <div class="fromBlock">\n        {from_html}\n      </div>'
    ]
    to_block = (fields.get("to_block") or "").strip()
    if to_block:
        to_lines = to_block.replace("\r\n", "\n").split("\n")
        to_html = "<br>\n        ".join(html.escape(line) for line in to_lines)
        blocks.append(f'      <div class="toBlock">\n        {to_html}\n      </div>')
    blocks.append(
        f'      <div class="letterdate">{html.escape((fields.get("letter_date") or "").strip())}</div>'
    )
    subject = (fields.get("subject") or "").strip()
    if subject:
        blocks.append(
            f'      <div class="lettersubject">{html.escape(subject)}</div>'
        )
    paras = _session_cover_letter_paragraphs(fields.get("letter") or "")
    p_html = "\n".join(
        f"        <p>{html.escape(p).replace(chr(10), '<br>')}</p>" for p in paras
    )
    blocks.append(f'      <div class="lettercontent">\n{p_html}\n      </div>')

    signoff_parts = [html.escape((fields.get("signoff_closing") or "").strip()), "<br>"]
    if signature_image_src:
        src_esc = html.escape(signature_image_src, quote=True)
        signoff_parts.append(
            f'<img src="{src_esc}" class="signature-img" alt="Signature">'
        )
        signoff_parts.append("<br>")
    signoff_parts.append(html.escape(sig_name))
    blocks.append(
        "      <div class=\"letterSignoff\">\n        "
        + "\n        ".join(signoff_parts)
        + "\n      </div>"
    )
    body_inner = "\n\n".join(blocks)

    css = f""":root {{
  --max-width: 800px;
  --accent-color: {accent};
  --header-color: {header_c};
  --text-primary: {text_primary};
  --text-secondary: {text_secondary};
  --text-tertiary: {text_tertiary};
  --border-light: {border_light};
  --border-medium: {border_medium};
  --header-font-family: {hstack};
  --body-font-family: {bstack};
  --list-font-family: {lstack};
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  padding: 40px 20px;
  background: {page_bg};
  font-family: var(--body-font-family);
  color: var(--text-primary);
  line-height: 1.65;
  font-size: 15px;
}}
.cover-letter {{
  max-width: 700px;
  margin: 0 auto;
  padding: 14px 35px 35px 35px;
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  color: var(--text-primary);
  line-height: 1.65;
}}
.fromBlock {{
  margin: 0 0 32px;
  padding-bottom: 20px;
  border-bottom: 2px solid var(--accent-color);
  font-size: 17px;
  color: var(--accent-color);
  text-align: left;
  line-height: 1.5;
  font-weight: 700;
}}
.toBlock {{
  margin: 16px 0 16px;
  font-size: 15px;
  color: var(--text-primary);
  text-align: left;
  line-height: 1.5;
  font-weight: 400;
}}
.letterdate {{
  margin: 40px 0 16px;
  font-size: 14px;
  color: var(--text-secondary);
  text-align: left;
}}
.lettersubject {{
  margin: 0 0 24px;
  font-size: 15px;
  font-weight: 400;
  color: var(--text-primary);
  text-align: left;
}}
.lettercontent {{
  margin: 0 0 24px;
  text-align: left;
}}
.lettercontent p {{
  margin: 0 0 16px;
  font-size: 15px;
  line-height: 1.65;
  color: var(--text-primary);
}}
.lettercontent p:last-child {{
  margin-bottom: 0;
}}
.letterSignoff {{
  margin: 24px 0 0;
  font-size: 15px;
  text-align: left;
  line-height: 1.5;
}}
.signature-img {{
  display: block;
  height: 61px;
  margin: 8px 0 -25px 0;
}}
@page {{
  margin-top: 1in;
  orphans: 3;
  widows: 3;
}}
@page :first {{
  margin-top: 0.5in;
}}
@media print {{
  body {{
    background: #fff;
    padding: 0;
  }}
  .cover-letter {{
    box-shadow: none;
    padding: 0.5in;
  }}
  .lettercontent {{
    orphans: 3;
    widows: 3;
  }}
  .lettercontent p {{
    orphans: 3;
    widows: 3;
    page-break-inside: auto;
    break-inside: auto;
  }}
}}"""

    title_esc = html.escape(doc_title)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title_esc}</title>
  <style>
{css}
  </style>{meta_tag}
</head>
<body>
  <main>
    <div class="cover-letter">
{body_inner}
    </div>
  </main>
</body>
</html>
"""


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
    """Deep-walk dict/list nests; apply ``_resume_site_markers`` to every string leaf."""
    return {k: _mark_resume_value(v) for k, v in render.items()}


def _mark_resume_value(val: Any) -> Any:
    """Recurse into dict/list; transform string leaves; leave other types unchanged."""
    if isinstance(val, str):
        return _resume_site_markers(val)
    if isinstance(val, dict):
        return {k: _mark_resume_value(v) for k, v in val.items()}
    if isinstance(val, (list, tuple)):
        return [_mark_resume_value(item) for item in val]
    return val


def _render_content_keys(markers: dict) -> List[str]:
    """Keys present for Style D — strings with content, plus non-empty experience job arrays."""
    keys = [k for k, v in markers.items() if isinstance(v, str) and v.strip()]
    exp = markers.get("experience")
    if candidate_mod.is_experience_job_array(exp) and exp:
        keys.append("experience")
    return sorted(set(keys))


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
    text_primary = colors.get("text_primary", "#1a1a1a")
    text_secondary = colors.get("text_secondary", "#444")
    text_tertiary = colors.get("text_tertiary", "#666")
    border_light = colors.get("border_light", "#e0e0e0")
    border_medium = colors.get("border_medium", "#ccc")
    # emit_prior_experience still drives body-section inclusion via callers; print CSS always has the golden prior-experience break.

    name_raw = str(render.get("candidate_name") or "").strip()
    title_raw = str(render.get("candidate_title") or "").strip()
    tagline_raw = str(render.get("candidate_tagline") or "").strip()
    name = html.escape(name_raw)
    title = html.escape(title_raw)
    contact = html.escape(str(render.get("candidate_contact_detail") or ""))

    if name and title:
        h1_inner = f"{name}\u00a0• {title}"
    elif name:
        h1_inner = name
    elif title:
        h1_inner = title
    else:
        h1_inner = ""

    meta_tag = ""
    if name_raw and title_raw and tagline_raw:
        meta_esc = html.escape(
            f"Resume of {name_raw}, {title_raw}, specializing in {tagline_raw}"
        )
        meta_tag = f'\n  <meta name="description" content="{meta_esc}" />'

    body_sections_html = _emit_body_sections_html(
        render,
        body_section_ids or list(_RESUME_BODY_KEYS),
        body_section_titles or {},
    )

    cover_html = ""
    if include_cover and cover_letter:
        cover_html = _emit_cover_sections_html(cover_letter, cover_profile or {})

    ats_html = _emit_ats_block(critical_keywords, ak)

    # AST-1020: golden resume stylesheet + Astral cover/ATS/prose-block appendages.
    css = f""":root {{
  --max-width: 800px;
  --accent-color: {accent};
  --header-color: {header_c};
  --text-primary: {text_primary};
  --text-secondary: {text_secondary};
  --text-tertiary: {text_tertiary};
  --border-light: {border_light};
  --border-medium: {border_medium};
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
h1, h2, h3, .title, .specialties {{
  font-family: var(--header-font-family);
  text-align: center;
}}
.contact, .competencies-list, .skill-category p {{
  font-family: var(--list-font-family);
  text-align: center;
}}
.skill-category h4 {{
  font-family: var(--header-font-family);
  text-align: center;
}}
p, .role-description, ul, li {{
  font-family: var(--body-font-family);
  text-align: left;
  line-height: 1.25;
}}
p {{ margin-bottom: 12px; }}
.job-title {{
  font-family: var(--header-font-family);
  text-align: left;
}}
.dates {{
  font-family: var(--body-font-family);
  text-align: left;
}}
.competencies-list {{
  text-transform: uppercase;
  letter-spacing: 0.2px;
  font-size: 13.5px;
}}
.skill-category p {{
  text-transform: uppercase;
  letter-spacing: 0.2px;
  font-size: 13.5px;
}}
.header {{
  max-width: var(--max-width);
  margin: 0 auto 2px;
  padding-bottom: 0;
}}
h1 {{
  margin: 20px 0 0;
  font-size: 33px;
  line-height: 1.1;
  font-weight: 700;
  letter-spacing: -0.5px;
  color: var(--header-color);
}}
.title {{
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  color: var(--text-secondary);
}}
.specialties {{
  margin: 0;
  font-size: 14px;
  color: var(--text-tertiary);
  font-weight: 500;
}}
.contact {{
  margin: 6px 0 0;
  font-size: 14px;
  color: var(--text-secondary);
  display: flex;
  flex-wrap: wrap;
  gap: 8px 16px;
  justify-content: center;
}}
.contact span {{ white-space: nowrap; }}
.content {{ max-width: var(--max-width); margin: 0 auto; }}
section {{ margin-bottom: 0; }}
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
.summary-intro {{
  margin: 6px;
  line-height: 1.25;
  font-family: var(--body-font-family);
  text-align: left;
}}
.summary-intro:last-child {{ margin-bottom: 0; }}
.competencies-list {{
  margin: 6px 0 0;
  line-height: 1.8;
  color: var(--text-secondary);
}}
.role {{
  margin-bottom: 12px;
  page-break-inside: avoid;
}}
.role-header {{
  margin-top: 20px;
  margin-bottom: 8px;
}}
.role-description {{ margin: 8px 0; }}
.compact-title {{
  margin: 5px 0 2px;
  font-size: 16px;
  font-family: var(--header-font-family);
  text-align: left;
}}
.compact-title strong {{
  font-weight: 700;
  color: var(--text-primary);
}}
.compact-location {{
  margin: 0 0 4px;
  font-size: 14.5px;
  color: var(--text-tertiary);
  font-family: var(--body-font-family);
  text-align: left;
  line-height: 1.4;
}}
.compact-location em {{
  font-style: italic;
  font-size: 14.5px;
}}
.role ul {{
  margin: 4px 0 0;
  padding-left: 20px;
}}
.role li {{ margin-bottom: 6px; }}
.role li:last-child {{ margin-bottom: 0; }}
.education-list {{
  margin: 8px 0 0;
  margin-left: 0.5in;
}}
.education-list p {{
  margin-bottom: 3px;
  line-height: 1.1;
}}
.education-list p:last-child {{ margin-bottom: 0; }}
.education-list strong {{
  font-family: var(--header-font-family);
  font-weight: 700;
}}
.skills-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
  margin-top: 12px;
}}
.skill-category {{ margin: 0; }}
.skill-category h4 {{
  margin: 0 0 4px;
  font-size: 13.5px;
  font-weight: 700;
  color: var(--accent-color);
  text-transform: uppercase;
  letter-spacing: 0.2px;
}}
.skill-category p {{
  margin: 0;
  line-height: 1.5;
  color: var(--text-secondary);
}}
.prose-block {{ white-space: pre-wrap; }}
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
@media (max-width: 600px) {{
  body {{ padding: 12px; }}
  h1 {{ font-size: 28px; }}
  .title {{ font-size: 15px; }}
  h2 {{ font-size: 18px; }}
  .contact {{ flex-direction: column; gap: 4px; }}
  .skills-grid {{ grid-template-columns: 1fr; gap: 12px; }}
}}
@media print {{
  body {{ background: #fff; padding: 0; }}
  h2 {{ page-break-after: avoid; }}
  #competencies {{ page-break-after: avoid; }}
  #prior-experience {{ page-break-before: always; }}
  .role {{ page-break-inside: avoid; }}
  p, li {{ orphans: 3; widows: 3; }}
}}
"""
    # AST-1021: `{name} Resume` (space, no em/en dash); empty name → `Resume`.
    title_esc = html.escape(f"{name_raw} Resume" if name_raw else "Resume")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title_esc}</title>{meta_tag}
  <style>
{css}
  </style>
</head>
<body>
  <header class="header">
    <h1>{h1_inner}</h1>
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


def _emit_education_list_html(text: str) -> str:
    """Per-line education rows: ``<strong>credential</strong>`` + post-marker bullet rest."""
    bullet = "\u00a0• "
    rows: List[str] = []
    for line in str(text).splitlines():
        line = line.strip()
        if not line:
            continue
        if bullet in line:
            cred, _, rest = line.partition(bullet)
            rows.append(
                f"        <p><strong>{html.escape(cred)}</strong>{bullet}{html.escape(rest)}</p>"
            )
        else:
            rows.append(f"        <p><strong>{html.escape(line)}</strong></p>")
    if not rows:
        return ""
    return "      <div class=\"education-list\">\n" + "\n".join(rows) + "\n      </div>"


def _emit_skills_grid_html(text: str) -> str:
    """Per-line skills categories: ``Category: items`` → ``h4`` + items ``<p>``."""
    cats: List[str] = []
    for line in str(text).splitlines():
        line = line.strip()
        if not line:
            continue
        if ": " in line:
            category, _, items = line.partition(": ")
            cats.append(
                "        <div class=\"skill-category\">\n"
                f"          <h4>{html.escape(category)}</h4>\n"
                f"          <p>{html.escape(items)}</p>\n"
                "        </div>"
            )
        else:
            cats.append(
                "        <div class=\"skill-category\">\n"
                f"          <p>{html.escape(line)}</p>\n"
                "        </div>"
            )
    if not cats:
        return ""
    return "      <div class=\"skills-grid\">\n" + "\n".join(cats) + "\n      </div>"


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
        sid = _KEY_TO_SECTION_ID.get(key, key)
        heading = html.escape(titles.get(key, _KEY_TO_HEADING.get(key, key.replace("_", " ").title())))
        # Experience job array: emit per-role HTML before generic dict/list → JSON coercion.
        if key == "experience" and candidate_mod.is_experience_job_array(raw):
            roles_html = _emit_experience_jobs_html(raw)
            if not roles_html.strip():
                continue
            chunks.append(
                f"""    <section aria-labelledby="{sid}">
      <h2 id="{sid}">{heading}</h2>
{roles_html}
    </section>"""
            )
            continue
        if isinstance(raw, (dict, list)):
            text = _format_experience_value(raw)
        else:
            text = str(raw) if raw is not None else ""
        if not str(text).strip():
            continue
        if key == "professional_summary":
            # Blank lines first; single-\n fallback (same as cover letter) → multiple .summary-intro
            paras = _session_cover_letter_paragraphs(str(text))
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
        if key == "education_certifications":
            edu_html = _emit_education_list_html(str(text))
            if not edu_html.strip():
                continue
            chunks.append(
                f"""    <section aria-labelledby="{sid}">
      <h2 id="{sid}">{heading}</h2>
{edu_html}
    </section>"""
            )
            continue
        if key == "technical_skills":
            skills_html = _emit_skills_grid_html(str(text))
            if not skills_html.strip():
                continue
            chunks.append(
                f"""    <section aria-labelledby="{sid}">
      <h2 id="{sid}">{heading}</h2>
{skills_html}
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
    return "\n".join(chunks)


def _format_compact_location(dates: str, location: str, sep: str) -> str:
    """Golden compact-location: ``dates: place (arrangement)`` when ``sep`` splits location."""
    dates = dates.strip()
    location = location.strip()
    if sep in location:
        place, _, arrangement = location.partition(sep)
        place, arrangement = place.strip(), arrangement.strip()
        if place and arrangement:
            text = f"{dates}: {place} ({arrangement})" if dates else f"{place} ({arrangement})"
            return _resume_site_markers(text) if text else ""
        # Empty arrangement after split → treat remaining place as plain location.
        location = place or location
    if dates and location:
        text = f"{dates}: {location}"
    elif dates:
        text = dates
    elif location:
        text = location
    else:
        text = ""
    return _resume_site_markers(text) if text else ""


def _split_role_accomplishments(
    accomplishments: str, lead_prefix: str
) -> Tuple[List[str], List[str]]:
    """Split accomplishments into lead paragraphs (prefix lines) and bullet lines."""
    leads: List[str] = []
    bullets: List[str] = []
    for raw_line in accomplishments.split("\n"):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(lead_prefix):
            rest = line.removeprefix(lead_prefix).strip()
            if rest:
                leads.append(_resume_site_markers(rest))
        else:
            bullets.append(_resume_site_markers(line))
    return leads, bullets


def _emit_experience_jobs_html(jobs: list) -> str:
    """Golden role articles: compact title/location, optional lead, then achievement bullets."""
    layout = BUILD_CONFIG["experience_role_layout"]
    lead_prefix = layout["lead_line_prefix"]
    loc_sep = layout["location_arrangement_sep"]
    role_chunks: List[str] = []
    for item in jobs:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "").strip()
        company = str(item.get("company") or "").strip()
        dates = str(item.get("dates") or "").strip()
        location = str(item.get("location") or "").strip()
        accomplishments = str(item.get("accomplishments") or "").strip()
        if not (title or company or dates or location or accomplishments):
            continue

        if title and company:
            title_text = _resume_site_markers(f"{title} • {company}")
        elif title:
            title_text = _resume_site_markers(title)
        elif company:
            title_text = _resume_site_markers(company)
        else:
            title_text = ""
        loc_text = _format_compact_location(dates, location, loc_sep)
        leads, bullets = _split_role_accomplishments(accomplishments, lead_prefix)
        if not (title_text or loc_text or leads or bullets):
            continue

        lines: List[str] = ['      <article class="role">', '        <div class="role-header">']
        if title_text:
            lines.append(
                f'          <p class="compact-title"><strong>{html.escape(title_text)}</strong></p>'
            )
        if loc_text:
            lines.append(
                f'          <p class="compact-location"><em>{html.escape(loc_text)}</em></p>'
            )
        lines.append("        </div>")
        for lead in leads:
            lines.append(f'        <p class="role-description">{html.escape(lead)}</p>')
        if bullets:
            lines.append("        <ul>")
            for bullet in bullets:
                lines.append(f"          <li>{html.escape(bullet)}</li>")
            lines.append("        </ul>")
        lines.append("      </article>")
        role_chunks.append("\n".join(lines))
    return "\n".join(role_chunks)


def _format_experience_value(val: Any) -> str:
    """JSON visibility for unexpected structured values — job arrays use ``_emit_experience_jobs_html``."""
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
