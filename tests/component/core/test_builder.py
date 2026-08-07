"""Component tests for src/core/builder.py (AST-393)."""

from __future__ import annotations

import re
from typing import Any, Dict
from unittest.mock import MagicMock

import pytest

from src.core import builder as builder_mod


def _resume_blob(**sections: str) -> Dict[str, Any]:
    return {
        "candidate_name": "Ada Lovelace",
        "candidate_title": "Engineer",
        "candidate_contact_detail": "ada@example.com",
        **sections,
    }


def _candidate_row(**artifacts: Any) -> Dict[str, Any]:
    return {
        "first": "Ada",
        "last": "Lovelace",
        "full": "Ada Lovelace",
        "candidate_data": {
            "contact": {
                "contact_email": "ada@example.com",
                "cover_letter_signature_image": "https://example.com/sig.png",
            },
            "artifacts": artifacts,
            "context": {"raw_sample": "Dear team,\nThanks"},
        },
    }


class TestCoerceCandidateBlob:
    def test_unwraps_nested_candidate_rows(self) -> None:
        inner = {"contact": {"contact_email": "ada@example.com"}}
        wrapped = {"candidate_data": inner, "first": "Ada", "last": "Lovelace", "full": "Ada Lovelace"}
        assert builder_mod._coerce_candidate_blob(wrapped) == {
            **inner,
            "_first": "Ada",
            "_last": "Lovelace",
            "_full": "Ada Lovelace",
        }
        assert builder_mod._coerce_candidate_blob(inner) == inner
        assert builder_mod._coerce_candidate_blob("bad") == {}


class TestBuildResume:
    def test_raises_for_missing_job_company_or_candidate(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(builder_mod.tracker_mod, "get_job", lambda job_id: None)
        with pytest.raises(ValueError, match="Job not found"):
            builder_mod.build_resume("job-1")

        monkeypatch.setattr(builder_mod.tracker_mod, "get_job", lambda job_id: {"company": ""})
        with pytest.raises(ValueError, match="missing company"):
            builder_mod.build_resume("job-1")

        monkeypatch.setattr(builder_mod.tracker_mod, "get_job", lambda job_id: {"company": "co"})
        monkeypatch.setattr(builder_mod.database, "get_company", lambda short_name: None)
        with pytest.raises(ValueError, match="Company not found"):
            builder_mod.build_resume("job-1")

        monkeypatch.setattr(builder_mod.database, "get_company", lambda short_name: {"candidate_id": ""})
        with pytest.raises(ValueError, match="no candidate_id"):
            builder_mod.build_resume("job-1")

        monkeypatch.setattr(builder_mod.database, "get_company", lambda short_name: {"candidate_id": "cand-1"})
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", lambda candidate_id: None)
        with pytest.raises(ValueError, match="Candidate not found"):
            builder_mod.build_resume("job-1")

    def test_delegates_to_build_resume_from_job(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            builder_mod.tracker_mod,
            "get_job",
            lambda job_id: {"astral_job_id": job_id, "company": "co", "job_data": {"artifacts": {"resume_content": _resume_blob(professional_summary="Summary")}}},
        )
        monkeypatch.setattr(builder_mod.database, "get_company", lambda short_name: {"candidate_id": "cand-1"})
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", lambda candidate_id: _candidate_row(base_resume=_resume_blob()))
        monkeypatch.setattr(builder_mod, "build_resume_from_job", MagicMock(return_value="<html>ok</html>"))
        assert builder_mod.build_resume("job-1") == "<html>ok</html>"


class TestBuildResumeFromJob:
    def test_renders_job_resume_with_keywords_resume_only_by_default(self) -> None:
        job = {
            "job_data": {
                "artifacts": {
                    "resume_content": _resume_blob(
                        professional_summary="Para one\n\nPara two",
                        core_competencies="Python",
                        experience="Role A",
                        prior_experience="Role B",
                        education_certifications="School",
                        technical_skills="SQL",
                    ),
                    "cover_letter": {"re_line": "Re: Role", "body": "Hello", "signature": "Ada"},
                },
                "critical_keywords": "python, sql",
            }
        }
        html = builder_mod.build_resume_from_job(job, _candidate_row(base_resume=_resume_blob()))
        assert "Professional Summary" in html
        assert 'aria-label="Cover body"' not in html
        assert "ats-keywords" in html

    def test_falls_back_to_base_resume_and_non_dict_job_data(self) -> None:
        job = {"job_data": None}
        html = builder_mod.build_resume_from_job(
            job,
            _candidate_row(base_resume=_resume_blob(professional_summary="From base")),
        )
        assert "From base" in html

    def test_job_cover_letter_not_in_resume_unless_include_cover(self) -> None:
        job = {
            "job_data": {
                "artifacts": {
                    "resume_content": _resume_blob(professional_summary="Summary"),
                    "cover_letter": {"re_line": "Re", "body": "Body", "signature": ""},
                }
            }
        }
        cd = _candidate_row(base_resume=_resume_blob())
        resume_only = builder_mod.build_resume_from_job(job, cd)
        assert 'aria-label="Cover body"' not in resume_only
        combined = builder_mod.build_resume_from_job(job, cd, include_cover=True)
        assert 'aria-label="Cover body"' in combined
        assert "Re" in combined
        assert "Body" in combined

    def test_raises_when_no_resume_source_exists(self) -> None:
        with pytest.raises(ValueError, match="No resume_content"):
            builder_mod.build_resume_from_job({"job_data": {}}, {"artifacts": {}})


class TestAst581ResumeCoverSplit:
    """AST-581 — job resume HTML resume-only; separate cover-letter render."""

    def test_build_resume_from_job_omits_cover_when_include_cover_false(self) -> None:
        job = {
            "job_data": {
                "artifacts": {
                    "resume_content": _resume_blob(professional_summary="Summary text"),
                    "cover_letter": {"re_line": "Re", "body": "Cover body", "signature": ""},
                }
            }
        }
        html = builder_mod.build_resume_from_job(job, _candidate_row(base_resume=_resume_blob()), include_cover=False)
        assert "Summary text" in html
        assert 'aria-label="Cover body"' not in html

    def test_build_resume_from_job_includes_cover_when_include_cover_true(self) -> None:
        job = {
            "job_data": {
                "artifacts": {
                    "resume_content": _resume_blob(professional_summary="Summary text"),
                    "cover_letter": {"re_line": "Re", "body": "Cover body", "signature": ""},
                }
            }
        }
        html = builder_mod.build_resume_from_job(job, _candidate_row(base_resume=_resume_blob()), include_cover=True)
        assert 'aria-label="Cover body"' in html
        assert "Cover body" in html

    def test_build_cover_letter_from_job_emits_cover_only(self) -> None:
        # AST-1138: cover-only is SomersetCover (fromBlock), not resume cover-block aria.
        job = {
            "job_data": {
                "artifacts": {
                    "cover_letter": {"Subject": "", "Letter": "Dear team", "signature": ""},
                }
            }
        }
        html = builder_mod.build_cover_letter_from_job(job, _candidate_row(base_resume=_resume_blob()))
        assert 'class="fromBlock"' in html
        assert 'class="lettercontent"' in html
        assert "Dear team" in html
        assert 'aria-label="Cover body"' not in html
        assert 'id="summary"' not in html

    def test_build_cover_letter_raises_without_content(self) -> None:
        job = {"job_data": {"artifacts": {}}}
        cd = {"artifacts": {}, "context": {}}
        with pytest.raises(ValueError, match="No cover letter content"):
            builder_mod.build_cover_letter_from_job(job, cd)


class TestBuildBaseResume:
    def test_renders_candidate_only_resume(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            builder_mod.candidate_mod,
            "get_candidate",
            lambda candidate_id: _candidate_row(base_resume=_resume_blob(professional_summary="Base only")),
        )
        html = builder_mod.build_base_resume("cand-1")
        assert "Base only" in html
        assert "Cover body" not in html

    def test_requires_base_resume_artifact(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", lambda candidate_id: None)
        with pytest.raises(ValueError, match="Candidate not found"):
            builder_mod.build_base_resume("missing")
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", lambda candidate_id: {"candidate_data": {"artifacts": {}}})
        with pytest.raises(ValueError, match="missing artifacts.base_resume"):
            builder_mod.build_base_resume("cand-1")


class TestBuilderHelpers:
    def test_applies_profile_contact_and_markers(self) -> None:
        render = _resume_blob(professional_summary="__keep~~dash", experience={"role": "lead"})
        builder_mod._apply_contact_to_render_dict(
            render,
            {
                "contact_email": "ada@example.com",
                "phone": "555",
                "linkedin_url": "https://linkedin.com/in/ada",
                "github": "https://github.com/ada",
                "location": "London",
            },
            first="Ada",
            last="Lovelace",
        )
        marked = builder_mod._apply_resume_text_markers(render)
        assert marked["experience"] == {"role": "lead"}
        assert "\u00a0" in marked["professional_summary"]
        assert "555" in render["candidate_contact_detail"]

    def test_resolves_cover_letter_from_sample_text(self) -> None:
        resolved = builder_mod._resolve_cover_letter(
            {"artifacts": {}},
            {"context": {"raw_sample": "  Hello cover  "}},
        )
        assert resolved == {"re_line": "", "body": "Hello cover", "signature": ""}
        assert builder_mod._cover_letter_nonempty({"re_line": "", "body": "", "signature": ""}) is False
        assert builder_mod._cover_letter_nonempty({"re_line": "Re"}) is True
        assert builder_mod._cover_letter_nonempty({"re_line": 123, "body": None}) is True
        assert builder_mod._resolve_cover_letter({"artifacts": {}}, {"context": {}}) is None

    def test_profile_uses_reply_email_and_skips_empty_name(self) -> None:
        render = _resume_blob()
        builder_mod._apply_contact_to_render_dict(render, {"reply_email": "reply@example.com"})
        assert "reply@example.com" in render["candidate_contact_detail"]
        render = _resume_blob(candidate_name="Keep")
        builder_mod._apply_contact_to_render_dict(render, {}, first="  ", last="")
        assert render["candidate_name"] == "Keep"

    def test_emits_body_sections_and_cover_blocks(self) -> None:
        ordered = list(builder_mod._RESUME_BODY_KEYS)
        titles: dict[str, str] = {}
        body = builder_mod._emit_body_sections_html(
            {
                "professional_summary": "\n\n",
                "experience": ["role-a", "role-b"],
                "technical_skills": "Python",
            },
            ordered,
            titles,
        )
        assert "Technical Skills" in body
        assert "Professional Summary" not in body
        assert builder_mod._emit_body_sections_html({"professional_summary": " \n\n "}, ordered, titles) == ""
        assert builder_mod._emit_body_sections_html({"professional_summary": "   "}, ordered, titles) == ""
        assert "skills-grid" in builder_mod._emit_body_sections_html(
            {"technical_skills": ["Python", "SQL"]}, ["technical_skills"], titles
        )
        assert builder_mod._emit_body_sections_html(
            {
                "professional_summary": "Lead",
                "core_competencies": "Python",
                "experience": "Role",
                "prior_experience": "Earlier",
                "education_certifications": "School",
                "technical_skills": "SQL",
            },
            ordered,
            titles,
        ).count("<section") == 6
        cover = builder_mod._emit_cover_sections_html(
            {"re_line": "Re: Role", "body": "", "signature": ""},
            {},
        )
        assert "Cover re line" in cover
        assert "Cover sign-off" not in cover
        cover = builder_mod._emit_cover_sections_html(
            {"re_line": "", "body": "Hello", "signature": "Ada"},
            {"cover_letter_signature_image": "https://example.com/sig.png"},
        )
        assert "Cover body" in cover
        assert "Cover sign-off" in cover

    def test_merges_accent_color_into_style(self) -> None:
        style = builder_mod._merge_effective_style({"artifacts": {"base_resume": {"accent_color": "#112233"}}})
        assert style["colors"]["default_accent"] == "#112233"
        plain = builder_mod._merge_effective_style({"artifacts": {"base_resume": {"accent_color": 123}}})
        assert "default_accent" in plain["colors"]
        no_accent = builder_mod._merge_effective_style({"artifacts": {"base_resume": "not-a-dict"}})
        assert "default_accent" in no_accent["colors"]

    def test_formats_experience_and_filters_image_sources(self) -> None:
        assert builder_mod._format_experience_value("plain text") == "plain text"
        assert builder_mod._format_experience_value({"role": "lead"}) == '{\n  "role": "lead"\n}'
        bad = object()
        assert builder_mod._format_experience_value(bad) == str(bad)
        assert builder_mod._safe_image_src(123) is None
        assert builder_mod._safe_image_src("https://example.com/a.png") == "https://example.com/a.png"
        assert builder_mod._safe_image_src("http://bad\nurl") is None
        assert builder_mod._safe_image_src("javascript:alert(1)") is None
        assert builder_mod._safe_image_src("ftp://example.com/a.png") is None
        assert builder_mod._safe_image_src("data:image/jpeg;base64,abc") == "data:image/jpeg;base64,abc"

    def test_rejects_http_urls_with_unexpected_scheme(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            builder_mod,
            "urlparse",
            lambda value: type("R", (), {"scheme": "javascript"})(),
        )
        assert builder_mod._safe_image_src("http://example.com/a.png") is None

    def test_emits_cover_signoff_and_ats_tokens(self) -> None:
        assert builder_mod._emit_cover_signoff_html({"signature": ""}, {}) == ""
        # AST-1126: image alone (no {$SIGNATURE_IMAGE}) must not create a signoff.
        image_only = builder_mod._emit_cover_signoff_html(
            {"signature": ""},
            {"cover_letter_signature_image": "https://example.com/sig.png"},
        )
        assert image_only == ""
        signoff = builder_mod._emit_cover_signoff_html({"signature": "Thanks"}, {})
        assert "Thanks" in signoff
        assert "<img" not in signoff
        ak = builder_mod.BUILD_CONFIG["default_style"]["ats_keyword_block"]
        assert "python" in builder_mod._emit_ats_block("python, sql", ak)
        assert builder_mod._emit_ats_block(None, ak) == ""
        assert builder_mod._emit_ats_block(["python", "sql"], ak)
        assert builder_mod._emit_ats_block("   ", ak) == ""
        assert builder_mod._emit_ats_block(" , ", ak) == ""
        assert builder_mod._resume_site_markers("") == ""


class TestAst518BuilderResumeStructure:
    """AST-518: builder and cover read paths use per-candidate resume_structure catalog."""

    def _candidate_with_structure(self, structure: dict, **base_sections: str) -> dict:
        blob = _resume_blob(**base_sections)
        return {
            "first": "Ada",
            "last": "Lovelace",
            "full": "Ada Lovelace",
            "candidate_data": {
                "contact": {"contact_email": "ada@example.com"},
                "artifacts": {"resume_structure": structure, "base_resume": blob},
            },
        }

    def test_renders_catalog_section_titles_not_hardcoded_headings(self) -> None:
        structure = {
            "sections": {
                "professional_summary": {
                    "id": "professional_summary",
                    "title": "Executive Pitch",
                    "enabled": True,
                    "order": 0,
                    "job_agent_editable": True,
                },
                "candidate_name": {
                    "id": "candidate_name",
                    "title": "Name",
                    "enabled": True,
                    "order": 1,
                    "job_agent_editable": False,
                },
                "candidate_title": {
                    "id": "candidate_title",
                    "title": "Title",
                    "enabled": True,
                    "order": 2,
                    "job_agent_editable": False,
                },
                "candidate_contact_detail": {
                    "id": "candidate_contact_detail",
                    "title": "Contact",
                    "enabled": True,
                    "order": 3,
                    "job_agent_editable": False,
                },
            },
        }
        job = {"job_data": {"artifacts": {"resume_content": _resume_blob(professional_summary="Body text")}}}
        html = builder_mod.build_resume_from_job(job, self._candidate_with_structure(structure, professional_summary="Base"))
        assert "Executive Pitch" in html
        assert "Professional Summary" not in html

    def test_omits_orphan_keys_not_in_candidate_catalog(self) -> None:
        structure = {
            "sections": {
                "professional_summary": {
                    "id": "professional_summary",
                    "title": "Summary",
                    "enabled": True,
                    "order": 0,
                    "job_agent_editable": True,
                },
                "candidate_name": {
                    "id": "candidate_name",
                    "title": "Name",
                    "enabled": True,
                    "order": 1,
                    "job_agent_editable": False,
                },
                "candidate_title": {
                    "id": "candidate_title",
                    "title": "Title",
                    "enabled": True,
                    "order": 2,
                    "job_agent_editable": False,
                },
                "candidate_contact_detail": {
                    "id": "candidate_contact_detail",
                    "title": "Contact",
                    "enabled": True,
                    "order": 3,
                    "job_agent_editable": False,
                },
            },
        }
        job = {
            "job_data": {
                "artifacts": {
                    "resume_content": _resume_blob(
                        professional_summary="Keep me",
                        orphan_section="Secret orphan",
                    )
                }
            }
        }
        html = builder_mod.build_resume_from_job(job, self._candidate_with_structure(structure))
        assert "Keep me" in html
        assert "Secret orphan" not in html

    def test_accent_from_resume_structure_before_legacy_base_resume(self) -> None:
        palette = list((builder_mod.BUILD_CONFIG.get("accent_palette") or ["#1A1A2E"]))
        accent = palette[0].upper()
        structure = {
            "accent_color": accent,
            "sections": {
                "professional_summary": {
                    "id": "professional_summary",
                    "title": "S",
                    "enabled": True,
                    "order": 0,
                    "job_agent_editable": True,
                },
            },
        }
        cd = {
            "artifacts": {
                "resume_structure": structure,
                "base_resume": {"accent_color": "#000000", "professional_summary": "x"},
            }
        }
        style = builder_mod._merge_effective_style(cd)
        assert style["colors"]["default_accent"] == accent

    def test_cover_letter_subject_letter_aliases_render_on_cover_route(self) -> None:
        # AST-1138: Subject/Letter map into lettersubject / lettercontent (SomersetCover).
        job = {
            "job_data": {
                "artifacts": {
                    "cover_letter": {"Subject": "Re: Role", "Letter": "Hello there", "signature": ""},
                }
            }
        }
        html = builder_mod.build_cover_letter_from_job(job, _candidate_row(base_resume=_resume_blob()))
        assert 'class="lettersubject"' in html
        assert "Re: Role" in html
        assert "Hello there" in html
        assert 'aria-label="Cover body"' not in html
        assert "Professional Summary" not in html

    def test_ats_block_skips_blank_escaped_tokens(self, monkeypatch: pytest.MonkeyPatch) -> None:
        ak = builder_mod.BUILD_CONFIG["default_style"]["ats_keyword_block"]
        monkeypatch.setattr(builder_mod.html, "escape", lambda token: "")
        assert builder_mod._emit_ats_block("python", ak) == ""


class TestBuilderIdentifierHelpers:
    """AST-623 — read-only debug label helpers (no log-string asserts)."""

    def test_job_identifier_prefers_astral_job_id_then_title(self) -> None:
        assert builder_mod._builder_job_identifier({"astral_job_id": "job-1"}) == "job-1"
        assert builder_mod._builder_job_identifier({"job_title": "Role"}) == "Role"
        assert builder_mod._builder_job_identifier({}) == "?"

    def test_resume_content_source_labels(self) -> None:
        job_rc = {"artifacts": {"resume_content": _resume_blob(professional_summary="x")}}
        assert (
            builder_mod._resume_content_source_label(job_rc, {})
            == "job_data.artifacts.resume_content"
        )
        cd = _candidate_row(base_resume=_resume_blob(professional_summary="base"))
        assert (
            builder_mod._resume_content_source_label({"artifacts": {}}, cd["candidate_data"])
            == "candidate_data.artifacts.base_resume"
        )
        assert builder_mod._resume_content_source_label({}, {}) == "missing"

    def test_cover_letter_source_labels(self) -> None:
        job_cl = {
            "artifacts": {"cover_letter": {"re_line": "Re", "body": "Hi", "signature": ""}}
        }
        assert (
            builder_mod._cover_letter_source_label(job_cl, {})
            == "job_data.artifacts.cover_letter"
        )
        cd = _candidate_row()
        assert (
            builder_mod._cover_letter_source_label(
                {"artifacts": {}}, cd["candidate_data"]
            )
            == "candidate_data.context.raw_sample"
        )
        assert builder_mod._cover_letter_source_label({"artifacts": {}}, {"context": {}}) is None

    def test_accent_source_labels(self) -> None:
        structure_cd = {
            "artifacts": {
                "resume_structure": {
                    "accent_color": "#111111",
                    "sections": {
                        "professional_summary": {
                            "id": "professional_summary",
                            "title": "S",
                            "enabled": True,
                            "order": 0,
                            "job_agent_editable": True,
                        }
                    },
                },
                "base_resume": _resume_blob(),
            }
        }
        assert (
            builder_mod._accent_source_label(structure_cd)
            == "resume_structure.accent_color"
        )
        legacy_cd = {
            "artifacts": {
                "base_resume": {**_resume_blob(), "accent_color": "#445566"},
            }
        }
        assert (
            builder_mod._accent_source_label(legacy_cd)
            == "artifacts.base_resume.accent_color"
        )
        assert builder_mod._accent_source_label({"artifacts": {"base_resume": _resume_blob()}}) == (
            "BUILD_CONFIG.default_style"
        )
        whitespace_legacy = {
            "artifacts": {"base_resume": {**_resume_blob(), "accent_color": "   "}}
        }
        assert builder_mod._accent_source_label(whitespace_legacy) == "BUILD_CONFIG.default_style"
        non_string_legacy = {
            "artifacts": {"base_resume": {**_resume_blob(), "accent_color": None}}
        }
        assert builder_mod._accent_source_label(non_string_legacy) == "BUILD_CONFIG.default_style"
        assert builder_mod._accent_source_label({"artifacts": {"base_resume": "not-a-dict"}}) == (
            "BUILD_CONFIG.default_style"
        )


class TestBuildResumeFromJobDebugPaths:
    """AST-623 — contract debug branches on resume render (no golden log lines)."""

    def test_success_resume_job_source_with_debug(self) -> None:
        job = {
            "astral_job_id": "job-1",
            "job_data": {
                "artifacts": {
                    "resume_content": _resume_blob(professional_summary="Summary"),
                    "cover_letter": {"re_line": "Re", "body": "Body", "signature": ""},
                },
                "critical_keywords": "python, sql",
            },
        }
        html = builder_mod.build_resume_from_job(
            job, _candidate_row(base_resume=_resume_blob()), include_cover=True, debug=True
        )
        assert "Summary" in html
        assert 'aria-label="Cover body"' in html

    def test_success_resume_list_keywords_and_base_source_with_debug(self) -> None:
        job = {"job_data": {"critical_keywords": ["go", "rust"]}}
        html = builder_mod.build_resume_from_job(
            job,
            _candidate_row(base_resume=_resume_blob(professional_summary="From base")),
            debug=True,
        )
        assert "From base" in html

    def test_failure_no_resume_source_with_debug(self) -> None:
        with pytest.raises(ValueError, match="No resume_content"):
            builder_mod.build_resume_from_job({"job_data": {}}, {"artifacts": {}}, debug=True)


class TestBuildResumeDebugPaths:
    def test_failure_emits_debug_header_when_enabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(builder_mod.tracker_mod, "get_job", lambda job_id: None)
        with pytest.raises(ValueError, match="Job not found"):
            builder_mod.build_resume("job-missing", debug=True)

    def test_success_delegates_with_debug(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            builder_mod.tracker_mod,
            "get_job",
            lambda job_id: {
                "astral_job_id": job_id,
                "company": "co",
                "job_data": {"artifacts": {"resume_content": _resume_blob(professional_summary="x")}},
            },
        )
        monkeypatch.setattr(builder_mod.database, "get_company", lambda short_name: {"candidate_id": "cand-1"})
        monkeypatch.setattr(
            builder_mod.candidate_mod,
            "get_candidate",
            lambda candidate_id: _candidate_row(base_resume=_resume_blob()),
        )
        called: Dict[str, Any] = {}

        def _capture(job: Dict[str, Any], cd: Dict[str, Any], *, debug: bool = False) -> str:
            called["debug"] = debug
            return "<html>ok</html>"

        monkeypatch.setattr(builder_mod, "build_resume_from_job", _capture)
        assert builder_mod.build_resume("job-1", debug=True) == "<html>ok</html>"
        assert called["debug"] is True


class TestBuildCoverLetterDebugPaths:
    def test_failure_with_debug(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(builder_mod.tracker_mod, "get_job", lambda job_id: None)
        with pytest.raises(ValueError, match="Job not found"):
            builder_mod.build_cover_letter("job-missing", debug=True)

    def test_success_with_debug(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            builder_mod.tracker_mod,
            "get_job",
            lambda job_id: {
                "astral_job_id": job_id,
                "company": "co",
                "job_data": {
                    "artifacts": {"cover_letter": {"re_line": "Re", "body": "Hi", "signature": ""}}
                },
            },
        )
        monkeypatch.setattr(builder_mod.database, "get_company", lambda short_name: {"candidate_id": "cand-1"})
        monkeypatch.setattr(
            builder_mod.candidate_mod,
            "get_candidate",
            lambda candidate_id: _candidate_row(base_resume=_resume_blob()),
        )
        html = builder_mod.build_cover_letter("job-1", debug=True)
        assert "Hi" in html

    def test_company_and_candidate_failures_with_debug(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            builder_mod.tracker_mod,
            "get_job",
            lambda job_id: {"astral_job_id": job_id, "company": ""},
        )
        with pytest.raises(ValueError, match="missing company"):
            builder_mod.build_cover_letter("job-1", debug=True)

        monkeypatch.setattr(
            builder_mod.tracker_mod,
            "get_job",
            lambda job_id: {"astral_job_id": job_id, "company": "co"},
        )
        monkeypatch.setattr(builder_mod.database, "get_company", lambda short_name: None)
        with pytest.raises(ValueError, match="Company not found"):
            builder_mod.build_cover_letter("job-1", debug=True)

        monkeypatch.setattr(
            builder_mod.database,
            "get_company",
            lambda short_name: {"candidate_id": ""},
        )
        with pytest.raises(ValueError, match="no candidate_id"):
            builder_mod.build_cover_letter("job-1", debug=True)

        monkeypatch.setattr(
            builder_mod.database,
            "get_company",
            lambda short_name: {"candidate_id": "cand-1"},
        )
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", lambda candidate_id: None)
        with pytest.raises(ValueError, match="Candidate not found"):
            builder_mod.build_cover_letter("job-1", debug=True)


class TestBuildCoverLetterFromJobDebugPaths:
    def test_success_with_debug_and_signature_image(self) -> None:
        job = {
            "astral_job_id": "job-cl",
            "job_data": {
                "artifacts": {
                    "cover_letter": {"Subject": "Re: Role", "Letter": "Hello", "signature": "Ada"},
                }
            },
        }
        cd = _candidate_row(base_resume=_resume_blob())
        cd["candidate_data"]["contact"]["cover_letter_signature_image"] = "https://example.com/sig.png"
        html = builder_mod.build_cover_letter_from_job(job, cd, debug=True)
        assert "Hello" in html

    def test_failure_no_cover_with_debug(self) -> None:
        with pytest.raises(ValueError, match="No cover letter content"):
            builder_mod.build_cover_letter_from_job(
                {"job_data": {"artifacts": {}}}, {"artifacts": {}, "context": {}}, debug=True
            )

    def test_non_dict_job_data_with_debug(self) -> None:
        job = {"job_data": None}
        cd = _candidate_row()
        html = builder_mod.build_cover_letter_from_job(job, cd, debug=True)
        assert "Dear team" in html

    def test_rejected_signature_image_with_debug(self) -> None:
        job = {
            "job_data": {
                "artifacts": {
                    "cover_letter": {"Subject": "", "Letter": "Body", "signature": ""},
                }
            }
        }
        cd = _candidate_row(base_resume=_resume_blob())
        cd["candidate_data"]["contact"]["cover_letter_signature_image"] = "javascript:alert(1)"
        html = builder_mod.build_cover_letter_from_job(job, cd, debug=True)
        assert "Body" in html


class TestBuildBaseResumeDebugPaths:
    def test_success_with_debug(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            builder_mod.candidate_mod,
            "get_candidate",
            lambda candidate_id: _candidate_row(
                base_resume=_resume_blob(professional_summary="Base debug")
            ),
        )
        html = builder_mod.build_base_resume("cand-1", debug=True)
        assert "Base debug" in html

    def test_failures_with_debug(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", lambda candidate_id: None)
        with pytest.raises(ValueError, match="Candidate not found"):
            builder_mod.build_base_resume("missing", debug=True)
        monkeypatch.setattr(
            builder_mod.candidate_mod,
            "get_candidate",
            lambda candidate_id: {"candidate_data": {"artifacts": {}}},
        )
        with pytest.raises(ValueError, match="missing artifacts.base_resume"):
            builder_mod.build_base_resume("cand-1", debug=True)


# Branches: structure/sections validation; empty content; success emit; no get_candidate;
# debug Style D on/off (incl. failure headers).
class TestAst987BuildSessionBaseResume:
    def _structure(self) -> dict[str, Any]:
        return {
            "sections": {
                "candidate_name": {
                    "id": "candidate_name",
                    "title": "Name",
                    "enabled": True,
                    "order": 0,
                    "job_agent_editable": False,
                },
                "professional_summary": {
                    "id": "professional_summary",
                    "title": "Summary",
                    "enabled": True,
                    "order": 1,
                    "job_agent_editable": True,
                },
                "experience": {
                    "id": "experience",
                    "title": "Experience",
                    "enabled": True,
                    "order": 2,
                    "job_agent_editable": True,
                },
            }
        }

    def test_rejects_invalid_structure(self) -> None:
        with pytest.raises(ValueError, match="resume_structure with sections is required"):
            builder_mod.build_session_base_resume("bad", {"experience": "x"})  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="resume_structure with sections is required"):
            builder_mod.build_session_base_resume({}, {"experience": "x"})
        with pytest.raises(ValueError, match="resume_structure with sections is required"):
            builder_mod.build_session_base_resume({"sections": "nope"}, {"experience": "x"})

    def test_rejects_empty_base_resume(self) -> None:
        with pytest.raises(ValueError, match="base_resume content is required"):
            builder_mod.build_session_base_resume(self._structure(), {})
        with pytest.raises(ValueError, match="base_resume content is required"):
            builder_mod.build_session_base_resume(self._structure(), "bad")  # type: ignore[arg-type]

    def test_rejects_invalid_structure_with_debug(self) -> None:
        with pytest.raises(ValueError, match="resume_structure with sections is required"):
            builder_mod.build_session_base_resume({}, {"experience": "x"}, debug=True)

    def test_rejects_empty_content_with_debug(self) -> None:
        with pytest.raises(ValueError, match="base_resume content is required"):
            builder_mod.build_session_base_resume(self._structure(), {}, debug=True)

    def test_renders_from_in_memory_payload_no_candidate_bind(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        get_c = MagicMock()
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", get_c)
        monkeypatch.setattr(builder_mod.database, "get_candidate", get_c)
        html = builder_mod.build_session_base_resume(
            self._structure(),
            {
                "candidate_name": "Session User",
                "professional_summary": "Paste summary",
                "experience": "Paste jobs",
            },
        )
        assert "Paste summary" in html
        assert "Paste jobs" in html
        # Name from paste section strings — not profile (get_candidate never called).
        assert "Session User" in html
        get_c.assert_not_called()

    def test_success_with_debug(self, monkeypatch: pytest.MonkeyPatch) -> None:
        get_c = MagicMock()
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", get_c)
        html = builder_mod.build_session_base_resume(
            self._structure(),
            {"professional_summary": "Debug session", "experience": "Jobs"},
            debug=True,
        )
        assert "Debug session" in html
        get_c.assert_not_called()


class TestAst998ExperienceJobRender:
    """AST-998: shared builders emit per-role HTML for experience job arrays."""

    _JOBS = [
        {
            "company": "Acme Corp",
            "title": "Engineer",
            "dates": "2020-2023",
            "location": "Remote",
            "accomplishments": "Shipped widgets",
        },
        {
            "company": "Beta LLC",
            "title": "",
            "dates": "2023",
            "location": "",
            "accomplishments": "Led the team",
        },
    ]

    def _structure(self) -> dict[str, Any]:
        return {
            "sections": {
                "professional_summary": {
                    "id": "professional_summary",
                    "title": "Summary",
                    "enabled": True,
                    "order": 0,
                    "job_agent_editable": True,
                },
                "experience": {
                    "id": "experience",
                    "title": "Experience",
                    "enabled": True,
                    "order": 1,
                    "job_agent_editable": True,
                },
            }
        }

    def test_emit_experience_jobs_html_role_chrome(self) -> None:
        # AST-1008 superseded AST-998 subheader/meta/prose chrome with golden article classes.
        # Title joiner " • " becomes NBSP-bullet via _resume_site_markers.
        html = builder_mod._emit_experience_jobs_html(self._JOBS)
        assert '<article class="role">' in html
        assert 'class="compact-title"><strong>Engineer\u00a0• Acme Corp</strong></p>' in html
        assert 'class="compact-location"><em>2020-2023: Remote</em></p>' in html
        assert "<li>Shipped widgets</li>" in html
        # Title empty → company-only compact-title
        assert 'class="compact-title"><strong>Beta LLC</strong></p>' in html
        assert "<li>Led the team</li>" in html
        assert '"company"' not in html
        assert "role-subheader" not in html
        assert "role-accomplishments" not in html

    def test_emit_skips_non_dict_and_empty_roles(self) -> None:
        html = builder_mod._emit_experience_jobs_html(
            ["skip", {}, {"company": "", "title": "", "dates": "", "location": "", "accomplishments": ""}]
        )
        assert html == ""

    def test_emit_omits_empty_location_from_meta(self) -> None:
        html = builder_mod._emit_experience_jobs_html(
            [
                {
                    "company": "Solo",
                    "title": "Dev",
                    "dates": "2024",
                    "location": "",
                    "accomplishments": "Did stuff",
                }
            ]
        )
        assert 'class="compact-title"><strong>Dev\u00a0• Solo</strong></p>' in html
        # empty location → dates-only compact-location (no dangling place/arrangement)
        assert 'class="compact-location"><em>2024</em></p>' in html
        assert "Remote" not in html

    def test_render_content_keys_includes_job_array(self) -> None:
        keys = builder_mod._render_content_keys(
            {"professional_summary": "S", "experience": self._JOBS, "empty": "  "}
        )
        assert "professional_summary" in keys
        assert "experience" in keys
        assert "empty" not in keys

    def test_session_builder_renders_roles_not_blob(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", MagicMock())
        html = builder_mod.build_session_base_resume(
            self._structure(),
            {"professional_summary": "Summary", "experience": self._JOBS},
        )
        assert 'id="experience"' in html or ">Experience<" in html
        assert 'class="compact-title"><strong>Engineer\u00a0• Acme Corp</strong></p>' in html
        assert "<li>Shipped widgets</li>" in html
        assert 'class="compact-title"><strong>Beta LLC</strong></p>' in html
        assert ".compact-title" in html  # CSS present
        assert '"accomplishments"' not in html

    def test_session_legacy_string_experience_still_prose(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", MagicMock())
        html = builder_mod.build_session_base_resume(
            self._structure(),
            {"professional_summary": "Summary", "experience": "Legacy prose blob"},
        )
        assert "Legacy prose blob" in html
        assert '<article class="role">' not in html

    def test_base_resume_renders_job_array(self, monkeypatch: pytest.MonkeyPatch) -> None:
        structure = self._structure()
        cd = {
            "first": "Ada",
            "last": "Lovelace",
            "full": "Ada Lovelace",
            "candidate_data": {
                "contact": {"contact_email": "a@b.c"},
                "artifacts": {
                    "resume_structure": structure,
                    "base_resume": {
                        "professional_summary": "Base summary",
                        "experience": self._JOBS,
                    },
                },
            },
        }
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", lambda cid: cd)
        monkeypatch.setattr(builder_mod.database, "get_candidate", lambda cid: cd)
        html = builder_mod.build_base_resume("cand-1")
        assert 'class="compact-title"><strong>Engineer\u00a0• Acme Corp</strong></p>' in html
        assert "Acme Corp" in html
        assert "<li>Shipped widgets</li>" in html

    def test_job_resume_renders_job_array(self) -> None:
        jobs = self._JOBS
        job = {
            "astral_job_id": "job-1",
            "job_data": {
                "artifacts": {
                    "resume_content": {
                        "professional_summary": "Job summary",
                        "experience": jobs,
                    }
                }
            },
        }
        structure = self._structure()
        cd = _candidate_row(
            resume_structure=structure,
            base_resume={"professional_summary": "Base", "experience": "legacy"},
        )
        html = builder_mod.build_resume_from_job(job, cd)
        assert 'class="compact-title"><strong>Engineer\u00a0• Acme Corp</strong></p>' in html
        assert "<li>Shipped widgets</li>" in html
        assert "Job summary" in html


class TestAst1007NestedTypographyMarkers:
    """AST-1007: deep-walk markers on nested leaves; three-surface HTML proof."""

    # Fixture substrings shaped like parent AST-993 paste markers.
    _TITLE = "Fractional__TPM"
    _CONTACT = "hire@example.com__•__415-555-0100"
    _COMPETENCIES = "AI~~Assisted__Delivery • Cross~~Functional__Execution"
    _PRIOR = "Project__Manager__(4__yrs) • Systems__Analyst__(6__yrs)"
    _SKILLS = "Program: Jira__•__Confluence__•__Linear"
    _JOBS = [
        {
            "company": "Somerset__Consulting",
            "title": "Principal TPM",
            "dates": "2011 to Present",
            "location": "Remote",
            "accomplishments": "Achieved sprint~~level clarity across delivery.",
        }
    ]

    def _structure(self) -> dict[str, Any]:
        return {
            "sections": {
                "candidate_name": {
                    "id": "candidate_name",
                    "title": "Name",
                    "enabled": True,
                    "order": 0,
                    "job_agent_editable": False,
                },
                "candidate_title": {
                    "id": "candidate_title",
                    "title": "Title",
                    "enabled": True,
                    "order": 1,
                    "job_agent_editable": False,
                },
                "candidate_contact_detail": {
                    "id": "candidate_contact_detail",
                    "title": "Contact",
                    "enabled": True,
                    "order": 2,
                    "job_agent_editable": False,
                },
                "core_competencies": {
                    "id": "core_competencies",
                    "title": "Core Competencies",
                    "enabled": True,
                    "order": 3,
                    "job_agent_editable": True,
                },
                "experience": {
                    "id": "experience",
                    "title": "Experience",
                    "enabled": True,
                    "order": 4,
                    "job_agent_editable": True,
                },
                "prior_experience": {
                    "id": "prior_experience",
                    "title": "Prior Experience",
                    "enabled": True,
                    "order": 5,
                    "job_agent_editable": True,
                },
                "technical_skills": {
                    "id": "technical_skills",
                    "title": "Technical Skills",
                    "enabled": True,
                    "order": 6,
                    "job_agent_editable": True,
                },
            }
        }

    def _marker_blob(self) -> dict[str, Any]:
        return {
            "candidate_name": "Susan Somerset",
            "candidate_title": self._TITLE,
            "candidate_contact_detail": self._CONTACT,
            "core_competencies": self._COMPETENCIES,
            "experience": self._JOBS,
            "prior_experience": self._PRIOR,
            "technical_skills": self._SKILLS,
        }

    @staticmethod
    def _assert_markers_applied(html: str) -> None:
        # Transformed forms present after escape (NBSP / non-breaking hyphen survive escape).
        assert "Fractional\u00a0TPM" in html
        assert "hire@example.com\u00a0•\u00a0415-555-0100" in html
        assert "AI\u2011Assisted\u00a0Delivery" in html
        assert "Somerset\u00a0Consulting" in html
        assert "sprint\u2011level" in html
        assert "Jira\u00a0•\u00a0Confluence\u00a0•\u00a0Linear" in html
        assert "Project\u00a0Manager\u00a0(4\u00a0yrs)" in html
        # Literal marker digraphs must not remain in body text for these sections.
        assert "__" not in html
        assert "~~" not in html

    def test_apply_markers_deep_walks_job_array_and_list_leaves(self) -> None:
        render = {
            "candidate_title": self._TITLE,
            "core_competencies": self._COMPETENCIES,
            "experience": list(self._JOBS),
            "nested_list": ["AI~~Assisted__Delivery", {"inner": "sprint~~level"}],
            "keep_int": 7,
            "keep_none": None,
        }
        marked = builder_mod._apply_resume_text_markers(render)
        assert marked["candidate_title"] == "Fractional\u00a0TPM"
        assert marked["core_competencies"] == (
            "AI\u2011Assisted\u00a0Delivery\u00a0• Cross\u2011Functional\u00a0Execution"
        )
        job0 = marked["experience"][0]
        assert job0["company"] == "Somerset\u00a0Consulting"
        assert job0["accomplishments"] == "Achieved sprint\u2011level clarity across delivery."
        assert marked["nested_list"][0] == "AI\u2011Assisted\u00a0Delivery"
        assert marked["nested_list"][1]["inner"] == "sprint\u2011level"
        assert marked["keep_int"] == 7
        assert marked["keep_none"] is None
        # Input not mutated.
        assert render["experience"][0]["company"] == "Somerset__Consulting"
        assert render["candidate_title"] == self._TITLE

    def test_session_html_nested_markers_not_literal(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", MagicMock())
        html = builder_mod.build_session_base_resume(self._structure(), self._marker_blob())
        self._assert_markers_applied(html)

    def test_base_resume_html_nested_markers_not_literal(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        structure = self._structure()
        # No contact email/phone — otherwise _apply_contact_to_render_dict replaces
        # artifact contact and drops the marker-laden contact string under test.
        cd = {
            "first": "Susan",
            "last": "Somerset",
            "full": "Susan Somerset",
            "candidate_data": {
                "contact": {},
                "artifacts": {
                    "resume_structure": structure,
                    "base_resume": self._marker_blob(),
                },
            },
        }
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", lambda cid: cd)
        monkeypatch.setattr(builder_mod.database, "get_candidate", lambda cid: cd)
        html = builder_mod.build_base_resume("cand-1")
        self._assert_markers_applied(html)

    def test_job_resume_html_nested_markers_not_literal(self) -> None:
        structure = self._structure()
        job = {
            "astral_job_id": "job-1",
            "job_data": {
                "artifacts": {
                    "resume_content": self._marker_blob(),
                }
            },
        }
        # Column name only — keep resume_content contact markers for AC2 proof.
        cd = {
            "first": "Susan",
            "last": "Somerset",
            "full": "Susan Somerset",
            "candidate_data": {
                "contact": {},
                "artifacts": {
                    "resume_structure": structure,
                    "base_resume": {"professional_summary": "Base", "experience": "legacy"},
                },
            },
        }
        html = builder_mod.build_resume_from_job(job, cd)
        self._assert_markers_applied(html)


class TestAst1008ExperienceGoldenLayout:
    """AST-1008: golden role articles — compact title/location, lead vs bullets."""

    _LEAD = (
        "<no bullet>Solo practice delivering embedded technical program management "
        "across 30+ SaaS engagements."
    )
    _BULLET_A = "Diagnosed and mitigated blockers across distributed teams."
    _BULLET_B = "Led technical program delivery across globally distributed teams."
    _SOMERSET = {
        "company": "Somerset__Consulting",
        "title": "Principal Technical Program Manager",
        "dates": "2011 to Present",
        "location": "United States / Full-time Remote",
        "accomplishments": f"{_LEAD}\n{_BULLET_A}\n{_BULLET_B}",
    }
    _NO_LEAD = {
        "company": "PTown.tech",
        "title": "Technical Program Manager",
        "dates": "2022 to 2024",
        "location": "United States / Full-time Remote",
        "accomplishments": "Repaired a fractured relationship between decision makers and engineering.",
    }

    def _structure(self) -> dict[str, Any]:
        return {
            "sections": {
                "professional_summary": {
                    "id": "professional_summary",
                    "title": "Summary",
                    "enabled": True,
                    "order": 0,
                    "job_agent_editable": True,
                },
                "experience": {
                    "id": "experience",
                    "title": "Experience",
                    "enabled": True,
                    "order": 1,
                    "job_agent_editable": True,
                },
            }
        }

    def _jobs(self) -> list[dict[str, str]]:
        return [dict(self._SOMERSET), dict(self._NO_LEAD)]

    @staticmethod
    def _assert_golden_experience(html: str) -> None:
        assert '<article class="role">' in html
        # " • " joiner → NBSP-bullet via _resume_site_markers; company __ → NBSP
        assert (
            'class="compact-title"><strong>Principal Technical Program Manager\u00a0• '
            "Somerset\u00a0Consulting</strong></p>"
        ) in html
        assert 'class="compact-location"><em>2011 to Present: United States (Full-time Remote)</em></p>' in html
        assert (
            'class="role-description">Solo practice delivering embedded technical program management '
            "across 30+ SaaS engagements.</p>"
        ) in html
        assert "<no bullet>" not in html
        assert f"<li>{TestAst1008ExperienceGoldenLayout._BULLET_A}</li>" in html
        assert f"<li>{TestAst1008ExperienceGoldenLayout._BULLET_B}</li>" in html
        assert (
            'class="compact-title"><strong>Technical Program Manager\u00a0• PTown.tech</strong></p>'
            in html
        )
        assert (
            "<li>Repaired a fractured relationship between decision makers and engineering.</li>"
            in html
        )
        assert 'class="compact-title"' in html
        assert 'class="role-description"' in html
        assert "role-subheader" not in html

    def test_experience_role_layout_config_keys(self) -> None:
        layout = builder_mod.BUILD_CONFIG["experience_role_layout"]
        assert layout["lead_line_prefix"] == "<no bullet>"
        assert layout["location_arrangement_sep"] == " / "

    def test_format_compact_location_helpers(self) -> None:
        sep = " / "
        assert (
            builder_mod._format_compact_location(
                "2011 to Present", "United States / Full-time Remote", sep
            )
            == "2011 to Present: United States (Full-time Remote)"
        )
        assert builder_mod._format_compact_location("2024", "Remote", sep) == "2024: Remote"
        assert builder_mod._format_compact_location("2024", "", sep) == "2024"
        assert builder_mod._format_compact_location("", "Remote", sep) == "Remote"
        assert builder_mod._format_compact_location("", "", sep) == ""

    def test_split_role_accomplishments_lead_vs_bullets(self) -> None:
        leads, bullets = builder_mod._split_role_accomplishments(
            f"{self._LEAD}\n{self._BULLET_A}\n\n{self._BULLET_B}",
            "<no bullet>",
        )
        assert leads == [
            "Solo practice delivering embedded technical program management across 30+ SaaS engagements."
        ]
        assert bullets == [self._BULLET_A, self._BULLET_B]
        leads2, bullets2 = builder_mod._split_role_accomplishments(
            "<no bullet>   \nKeep", "<no bullet>"
        )
        assert leads2 == []
        assert bullets2 == ["Keep"]

    def test_emit_somerset_lead_paragraph_not_list_item(self) -> None:
        html = builder_mod._emit_experience_jobs_html(self._jobs())
        self._assert_golden_experience(html)
        assert "<li>Solo practice" not in html

    def test_session_html_golden_layout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", MagicMock())
        html = builder_mod.build_session_base_resume(
            self._structure(),
            {"professional_summary": "Summary", "experience": self._jobs()},
        )
        self._assert_golden_experience(html)
        # Full document CSS carries golden selectors (emit fragment alone does not).
        assert ".compact-title" in html
        assert ".role-description" in html

    def test_base_resume_html_golden_layout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        structure = self._structure()
        cd = {
            "first": "Susan",
            "last": "Somerset",
            "full": "Susan Somerset",
            "candidate_data": {
                "contact": {},
                "artifacts": {
                    "resume_structure": structure,
                    "base_resume": {
                        "professional_summary": "Base summary",
                        "experience": self._jobs(),
                    },
                },
            },
        }
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", lambda cid: cd)
        monkeypatch.setattr(builder_mod.database, "get_candidate", lambda cid: cd)
        html = builder_mod.build_base_resume("cand-1")
        self._assert_golden_experience(html)

    def test_job_resume_html_golden_layout(self) -> None:
        structure = self._structure()
        job = {
            "astral_job_id": "job-1",
            "job_data": {
                "artifacts": {
                    "resume_content": {
                        "professional_summary": "Job summary",
                        "experience": self._jobs(),
                    }
                }
            },
        }
        cd = {
            "first": "Susan",
            "last": "Somerset",
            "full": "Susan Somerset",
            "candidate_data": {
                "contact": {},
                "artifacts": {
                    "resume_structure": structure,
                    "base_resume": {"professional_summary": "Base", "experience": "legacy"},
                },
            },
        }
        html = builder_mod.build_resume_from_job(job, cd)
        self._assert_golden_experience(html)
        assert "Job summary" in html


class TestAst1009EducationSkillsPrior:
    """AST-1009: education per-line, skills category grid, prior competencies-list."""

    _PRIOR = (
        "Project__Manager__(4__yrs) • Systems__Analyst__(6__yrs) • "
        "ETL__Migration__Specialist__(2__yrs)"
    )
    _EDU = (
        "Certified ScrumMaster (CSM) • Scrum Alliance, 2024 to 2026\n"
        "Certified Scrum Product Owner (CSPO) • Scrum Alliance, 2024 to 2026\n"
        "UW Milwaukee • Completed coursework in Computer Science and Business Administration"
    )
    _SKILLS = (
        "Program & Delivery: Jira__•__Confluence__•__Linear\n"
        "AI Development & Orchestration: Claude__API__•__GPT~~4\n"
        "Design & Documentation: Lucidchart__•__Figma\n"
        "Development & APIs: Python__•__Next.js\n"
        "Data & Analytics: PostgreSQL__•__MySQL\n"
        "Integration & Automation: Zapier__•__GitHub__Actions\n"
        "Cloud & DevOps: AWS • Vercel • GitHub\n"
        "Collaboration: Slack__•__Discord"
    )

    def _structure(self) -> dict[str, Any]:
        return {
            "sections": {
                "prior_experience": {
                    "id": "prior_experience",
                    "title": "Prior Experience",
                    "enabled": True,
                    "order": 0,
                    "job_agent_editable": True,
                },
                "education_certifications": {
                    "id": "education_certifications",
                    "title": "Education & Certifications",
                    "enabled": True,
                    "order": 1,
                    "job_agent_editable": True,
                },
                "technical_skills": {
                    "id": "technical_skills",
                    "title": "Technical Skills",
                    "enabled": True,
                    "order": 2,
                    "job_agent_editable": True,
                },
            }
        }

    def _blob(self) -> dict[str, Any]:
        return {
            "prior_experience": self._PRIOR,
            "education_certifications": self._EDU,
            "technical_skills": self._SKILLS,
        }

    @staticmethod
    def _assert_section_markup(html: str) -> None:
        assert 'id="prior-experience"' in html
        assert 'class="competencies-list"' in html
        assert "Project\u00a0Manager\u00a0(4\u00a0yrs)" in html
        assert 'id="education"' in html or ">Education" in html
        assert 'class="education-list"' in html
        assert html.count("<strong>") >= 3
        assert "<strong>Certified ScrumMaster (CSM)</strong>" in html
        assert "<strong>Certified Scrum Product Owner (CSPO)</strong>" in html
        assert "<strong>UW Milwaukee</strong>" in html
        edu_section = html.split('id="education"', 1)[-1].split("</section>", 1)[0]
        assert 'class="prose-block"' not in edu_section
        assert 'class="skills-grid"' in html
        assert html.count('class="skill-category"') >= 8
        assert "<h4>Program &amp; Delivery</h4>" in html
        assert "<h4>AI Development &amp; Orchestration</h4>" in html
        assert "Jira\u00a0•\u00a0Confluence\u00a0•\u00a0Linear" in html
        assert "GPT\u20114" in html
        assert "__" not in html
        assert "~~" not in html

    def test_emit_education_list_html_splits_post_marker_bullet(self) -> None:
        marked = (
            "Certified ScrumMaster (CSM)\u00a0• Scrum Alliance, 2024 to 2026\n"
            "UW Milwaukee"
        )
        html = builder_mod._emit_education_list_html(marked)
        assert 'class="education-list"' in html
        assert (
            "<strong>Certified ScrumMaster (CSM)</strong>\u00a0• Scrum Alliance, 2024 to 2026"
            in html
        )
        assert "<strong>UW Milwaukee</strong>" in html
        assert "prose-block" not in html

    def test_emit_skills_grid_html_splits_category_colon(self) -> None:
        marked = (
            "Program & Delivery: Jira\u00a0•\u00a0Confluence\n"
            "Orphan line without colon"
        )
        html = builder_mod._emit_skills_grid_html(marked)
        assert 'class="skills-grid"' in html
        assert html.count('class="skill-category"') == 2
        assert "<h4>Program &amp; Delivery</h4>" in html
        assert "Jira\u00a0•\u00a0Confluence" in html
        orphan_block = html.split("Orphan line without colon")[0].rsplit("skill-category", 1)[-1]
        assert "<h4>" not in orphan_block
        assert "<p>Orphan line without colon</p>" in html

    def test_session_html_education_skills_prior(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", MagicMock())
        html = builder_mod.build_session_base_resume(self._structure(), self._blob())
        self._assert_section_markup(html)

    def test_base_resume_html_education_skills_prior(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        structure = self._structure()
        cd = {
            "first": "Susan",
            "last": "Somerset",
            "full": "Susan Somerset",
            "candidate_data": {
                "contact": {},
                "artifacts": {
                    "resume_structure": structure,
                    "base_resume": self._blob(),
                },
            },
        }
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", lambda cid: cd)
        monkeypatch.setattr(builder_mod.database, "get_candidate", lambda cid: cd)
        html = builder_mod.build_base_resume("cand-1")
        self._assert_section_markup(html)

    def test_job_resume_html_education_skills_prior(self) -> None:
        structure = self._structure()
        job = {
            "astral_job_id": "job-1",
            "job_data": {"artifacts": {"resume_content": self._blob()}},
        }
        cd = {
            "first": "Susan",
            "last": "Somerset",
            "full": "Susan Somerset",
            "candidate_data": {
                "contact": {},
                "artifacts": {
                    "resume_structure": structure,
                    "base_resume": {"professional_summary": "Base"},
                },
            },
        }
        html = builder_mod.build_resume_from_job(job, cd)
        self._assert_section_markup(html)


class TestAst1010HeaderContactMetaStyles:
    """AST-1010: Name NBSP-bullet Title header, ATS meta from tagline, golden CSS selectors."""

    _TAGLINE = (
        "Program Delivery • Cross-Functional Alignment • Cloud SaaS • AI-Assisted Engineering"
    )
    _META = (
        "Resume of Susan Somerset, Fractional TPM, specializing in "
        "Program Delivery • Cross-Functional Alignment • "
        "Cloud SaaS • AI-Assisted Engineering"
    )

    def _structure(self) -> dict[str, Any]:
        return {
            "sections": {
                "candidate_name": {
                    "id": "candidate_name",
                    "title": "Name",
                    "enabled": True,
                    "order": 0,
                    "job_agent_editable": False,
                },
                "candidate_title": {
                    "id": "candidate_title",
                    "title": "Title",
                    "enabled": True,
                    "order": 1,
                    "job_agent_editable": False,
                },
                "candidate_tagline": {
                    "id": "candidate_tagline",
                    "title": "Candidate Tagline",
                    "enabled": True,
                    "order": 2,
                    "job_agent_editable": False,
                },
                "candidate_contact_detail": {
                    "id": "candidate_contact_detail",
                    "title": "Contact",
                    "enabled": True,
                    "order": 3,
                    "job_agent_editable": False,
                },
                "professional_summary": {
                    "id": "professional_summary",
                    "title": "Summary",
                    "enabled": True,
                    "order": 4,
                    "job_agent_editable": True,
                },
            }
        }

    def _blob(self, *, tagline: str | None = _TAGLINE) -> dict[str, Any]:
        out: dict[str, Any] = {
            "candidate_name": "Susan Somerset",
            "candidate_title": "Fractional TPM",
            "candidate_contact_detail": "hire@example.com",
            "professional_summary": "Summary body",
        }
        if tagline is not None:
            out["candidate_tagline"] = tagline
        return out

    @classmethod
    def _assert_header_meta_css(cls, html: str, *, expect_meta: bool) -> None:
        assert "<h1>Susan Somerset • Fractional TPM</h1>" in html
        assert '<div class="contact"><span>hire@example.com</span></div>' in html
        header = html.split("<header", 1)[1].split("</header>", 1)[0]
        main = html.split("<main", 1)[1].split("</main>", 1)[0]
        assert "Program Delivery" not in header
        assert "Program Delivery" not in main
        if expect_meta:
            assert f'<meta name="description" content="{cls._META}" />' in html
        else:
            assert 'meta name="description"' not in html
        for sel in (
            ".compact-title",
            ".compact-location",
            ".role-description",
            ".education-list",
            ".skills-grid",
            ".skill-category h4",
        ):
            assert sel in html
        assert 'href="styles07.css"' not in html
        # AST-1020 owns golden contact-flex / full stylesheet parity asserts
        # (this class previously forbade the one-line flex rule before Take 2).

    def test_session_header_meta_and_css(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", MagicMock())
        html = builder_mod.build_session_base_resume(self._structure(), self._blob())
        self._assert_header_meta_css(html, expect_meta=True)

    def test_session_omits_meta_without_tagline(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", MagicMock())
        html = builder_mod.build_session_base_resume(
            self._structure(), self._blob(tagline=None)
        )
        self._assert_header_meta_css(html, expect_meta=False)

    def test_base_resume_header_meta_and_css(self, monkeypatch: pytest.MonkeyPatch) -> None:
        structure = self._structure()
        cd = {
            "first": "Susan",
            "last": "Somerset",
            "full": "Susan Somerset",
            "candidate_data": {
                "contact": {},
                "artifacts": {
                    "resume_structure": structure,
                    "base_resume": self._blob(),
                },
            },
        }
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", lambda cid: cd)
        monkeypatch.setattr(builder_mod.database, "get_candidate", lambda cid: cd)
        html = builder_mod.build_base_resume("cand-1")
        self._assert_header_meta_css(html, expect_meta=True)

    def test_job_resume_header_meta_and_css(self) -> None:
        structure = self._structure()
        job = {
            "astral_job_id": "job-1",
            "job_data": {"artifacts": {"resume_content": self._blob()}},
        }
        cd = {
            "first": "Susan",
            "last": "Somerset",
            "full": "Susan Somerset",
            "candidate_data": {
                "contact": {},
                "artifacts": {
                    "resume_structure": structure,
                    "base_resume": {"professional_summary": "Base"},
                },
            },
        }
        html = builder_mod.build_resume_from_job(job, cd)
        self._assert_header_meta_css(html, expect_meta=True)


class TestAst1020GoldenStylesheet:
    """AST-1020: embedded stylesheet golden parity + Astral CSS appendages."""

    def _structure(self) -> dict[str, Any]:
        # No prior_experience section — print CSS must still carry the golden break.
        return {
            "sections": {
                "candidate_name": {
                    "id": "candidate_name",
                    "title": "Name",
                    "enabled": True,
                    "order": 0,
                    "job_agent_editable": False,
                },
                "candidate_title": {
                    "id": "candidate_title",
                    "title": "Title",
                    "enabled": True,
                    "order": 1,
                    "job_agent_editable": False,
                },
                "candidate_contact_detail": {
                    "id": "candidate_contact_detail",
                    "title": "Contact",
                    "enabled": True,
                    "order": 2,
                    "job_agent_editable": False,
                },
                "professional_summary": {
                    "id": "professional_summary",
                    "title": "Summary",
                    "enabled": True,
                    "order": 3,
                    "job_agent_editable": True,
                },
            }
        }

    def _blob(self) -> dict[str, Any]:
        return {
            "candidate_name": "Susan Somerset",
            "candidate_title": "Senior Technical Program Manager",
            "candidate_contact_detail": "hire@example.com",
            "professional_summary": "Summary body",
        }

    @classmethod
    def _assert_golden_style(cls, html: str) -> None:
        style = html.split("<style>", 1)[1].split("</style>", 1)[0]
        assert "<h1>Susan Somerset • Senior Technical Program Manager</h1>" in html
        assert 'link rel="stylesheet"' not in html
        assert 'href="styles07.css"' not in html
        # :root tokens (interpolated from BUILD_CONFIG default_style colors/fonts)
        assert "--text-primary: #1a1a1a;" in style
        assert "--text-secondary: #444;" in style
        assert "--text-tertiary: #666;" in style
        assert "--border-light: #e0e0e0;" in style
        assert "--border-medium: #ccc;" in style
        assert "--accent-color: #3c2c6e;" in style
        assert "--header-color: #3c2c6e;" in style
        # Contact flex (multi-line golden block)
        assert "display: flex;" in style
        assert "flex-wrap: wrap;" in style
        assert "gap: 8px 16px;" in style
        assert "justify-content: center;" in style
        assert ".contact span { white-space: nowrap; }" in style
        # Experience / education / skills golden rules
        assert "font-size: 14.5px;" in style
        assert "margin-left: 0.5in;" in style
        assert "minmax(280px, 1fr)" in style
        assert "letter-spacing: 0.2px;" in style
        assert "text-transform: uppercase;" in style
        # Unused-but-present golden selectors
        for sel in (".title {", ".specialties {", ".job-title {", ".dates {"):
            assert sel in style
        # Mobile + print (prior break always — even without prior body section)
        assert "@media (max-width: 600px)" in style
        assert "#prior-experience { page-break-before: always; }" in style
        assert "#competencies { page-break-after: avoid; }" in style
        # Astral-only appendages between skills and mobile
        assert ".prose-block { white-space: pre-wrap; }" in style
        assert ".cover-block" in style
        assert ".ats-keywords" in style

    def test_session_golden_stylesheet(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", MagicMock())
        html = builder_mod.build_session_base_resume(self._structure(), self._blob())
        self._assert_golden_style(html)

    def test_base_resume_golden_stylesheet(self, monkeypatch: pytest.MonkeyPatch) -> None:
        structure = self._structure()
        cd = {
            "first": "Susan",
            "last": "Somerset",
            "full": "Susan Somerset",
            "candidate_data": {
                "contact": {},
                "artifacts": {
                    "resume_structure": structure,
                    "base_resume": self._blob(),
                },
            },
        }
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", lambda cid: cd)
        monkeypatch.setattr(builder_mod.database, "get_candidate", lambda cid: cd)
        html = builder_mod.build_base_resume("cand-1")
        self._assert_golden_style(html)

    def test_job_resume_golden_stylesheet(self) -> None:
        structure = self._structure()
        job = {
            "astral_job_id": "job-1",
            "job_data": {"artifacts": {"resume_content": self._blob()}},
        }
        cd = {
            "first": "Susan",
            "last": "Somerset",
            "full": "Susan Somerset",
            "candidate_data": {
                "contact": {},
                "artifacts": {
                    "resume_structure": structure,
                    "base_resume": {"professional_summary": "Base"},
                },
            },
        }
        html = builder_mod.build_resume_from_job(job, cd)
        self._assert_golden_style(html)


class TestAst1021DocumentTitleChrome:
    """AST-1021: document <title> `{name} Resume`; meta stays field-derived (no golden literal)."""

    _TAGLINE = "Enterprise Implementation • Service Delivery"
    # Non-golden title/tagline — proves meta is not the desired-HTML example string.
    _META = (
        "Resume of Susan Somerset, Fractional TPM, specializing in "
        "Enterprise Implementation • Service Delivery"
    )
    _GOLDEN_META_FRAGMENT = "Senior Technical Product Manager / Program Manager"
    _GOLDEN_META_FRAGMENT2 = "Cloud Platforms, Agile Delivery"

    def _structure(self, *, with_tagline: bool = True) -> dict[str, Any]:
        sections: dict[str, Any] = {
            "candidate_name": {
                "id": "candidate_name",
                "title": "Name",
                "enabled": True,
                "order": 0,
                "job_agent_editable": False,
            },
            "candidate_title": {
                "id": "candidate_title",
                "title": "Title",
                "enabled": True,
                "order": 1,
                "job_agent_editable": False,
            },
            "candidate_contact_detail": {
                "id": "candidate_contact_detail",
                "title": "Contact",
                "enabled": True,
                "order": 3 if with_tagline else 2,
                "job_agent_editable": False,
            },
            "professional_summary": {
                "id": "professional_summary",
                "title": "Summary",
                "enabled": True,
                "order": 4 if with_tagline else 3,
                "job_agent_editable": True,
            },
        }
        if with_tagline:
            sections["candidate_tagline"] = {
                "id": "candidate_tagline",
                "title": "Candidate Tagline",
                "enabled": True,
                "order": 2,
                "job_agent_editable": False,
            }
        return {"sections": sections}

    def _blob(
        self,
        *,
        name: str = "Susan Somerset",
        title: str = "Fractional TPM",
        tagline: str | None = _TAGLINE,
        contact: str = "hire@example.com",
    ) -> dict[str, Any]:
        out: dict[str, Any] = {
            "candidate_name": name,
            "candidate_title": title,
            "candidate_contact_detail": contact,
            "professional_summary": "Summary body",
        }
        if tagline is not None:
            out["candidate_tagline"] = tagline
        return out

    @classmethod
    def _assert_title_meta(
        cls,
        html: str,
        *,
        expect_title: str,
        expect_meta: bool,
    ) -> None:
        assert f"<title>{expect_title}</title>" in html
        # No em/en dash between name and Resume (old AST-1010 chrome).
        assert "— Resume" not in html
        assert "– Resume" not in html
        assert "SomersetResume" not in html
        assert '<div class="contact"><span>' in html
        if expect_meta:
            assert f'<meta name="description" content="{cls._META}" />' in html
            assert cls._GOLDEN_META_FRAGMENT not in html
            assert cls._GOLDEN_META_FRAGMENT2 not in html
        else:
            assert 'meta name="description"' not in html

    def test_session_title_and_field_meta(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", MagicMock())
        html = builder_mod.build_session_base_resume(self._structure(), self._blob())
        self._assert_title_meta(html, expect_title="Susan Somerset Resume", expect_meta=True)

    def test_session_empty_name_title_is_resume(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", MagicMock())
        html = builder_mod.build_session_base_resume(
            self._structure(with_tagline=False),
            self._blob(name="", tagline=None),
        )
        self._assert_title_meta(html, expect_title="Resume", expect_meta=False)

    def test_base_resume_title_and_field_meta(self, monkeypatch: pytest.MonkeyPatch) -> None:
        structure = self._structure()
        cd = {
            "first": "Susan",
            "last": "Somerset",
            "full": "Susan Somerset",
            "candidate_data": {
                "contact": {},
                "artifacts": {
                    "resume_structure": structure,
                    "base_resume": self._blob(),
                },
            },
        }
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", lambda cid: cd)
        monkeypatch.setattr(builder_mod.database, "get_candidate", lambda cid: cd)
        html = builder_mod.build_base_resume("cand-1")
        self._assert_title_meta(html, expect_title="Susan Somerset Resume", expect_meta=True)

    def test_job_resume_title_and_field_meta(self) -> None:
        structure = self._structure()
        job = {
            "astral_job_id": "job-1",
            "job_data": {"artifacts": {"resume_content": self._blob()}},
        }
        cd = {
            "first": "Susan",
            "last": "Somerset",
            "full": "Susan Somerset",
            "candidate_data": {
                "contact": {},
                "artifacts": {
                    "resume_structure": structure,
                    "base_resume": {"professional_summary": "Base"},
                },
            },
        }
        html = builder_mod.build_resume_from_job(job, cd)
        self._assert_title_meta(html, expect_title="Susan Somerset Resume", expect_meta=True)


class TestAst1027UatMarkerExpand:
    """AST-1027: when digraphs survive parse, shared expand is 1:1 for UAT skill sample."""

    def test_resume_site_markers_uat_skill_line(self) -> None:
        # UAT Actual was asymmetric nbsp-left-of-bullet + plain spaces on word joins.
        sample = (
            "Program & Delivery: Jira__•__Confluence__•__Linear__• "
            "Jira__Align__•__Azure__DevOps__•__Asana__• "
            "Trello__•__JAMA__•__Pivotal__Tracker"
        )
        out = builder_mod._resume_site_markers(sample)
        assert "Jira\u00a0•\u00a0Confluence\u00a0•\u00a0Linear" in out
        assert "Jira\u00a0Align" in out
        assert "Azure\u00a0DevOps" in out
        assert "Pivotal\u00a0Tracker" in out
        assert "__" not in out

    def test_session_html_expands_uat_skill_markers(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", MagicMock())
        structure = {
            "sections": {
                "candidate_name": {
                    "id": "candidate_name",
                    "title": "Name",
                    "enabled": True,
                    "order": 0,
                    "job_agent_editable": False,
                },
                "technical_skills": {
                    "id": "technical_skills",
                    "title": "Technical Skills",
                    "enabled": True,
                    "order": 1,
                    "job_agent_editable": True,
                },
            }
        }
        blob = {
            "candidate_name": "Susan Somerset",
            "technical_skills": (
                "Program & Delivery: Jira__•__Confluence__•__Linear__• "
                "Jira__Align__•__Azure__DevOps"
            ),
        }
        html = builder_mod.build_session_base_resume(structure, blob)
        assert "Jira\u00a0•\u00a0Confluence\u00a0•\u00a0Linear" in html
        assert "Jira\u00a0Align" in html
        assert "Azure\u00a0DevOps" in html
        assert "__" not in html


class TestAst1028UatKeywordsMetaEmit:
    """AST-1028: when title/tagline are split, keywords stay in meta — not header/body."""

    _TAGLINE = (
        "Program Delivery, Cross-Functional Alignment, Cloud SaaS, AI-Assisted Engineering"
    )
    _META = (
        "Resume of Susan Somerset, Fractional TPM, specializing in "
        "Program Delivery, Cross-Functional Alignment, Cloud SaaS, AI-Assisted Engineering"
    )

    def test_session_header_title_only_keywords_in_meta(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", MagicMock())
        structure = {
            "sections": {
                "candidate_name": {
                    "id": "candidate_name",
                    "title": "Name",
                    "enabled": True,
                    "order": 0,
                    "job_agent_editable": False,
                },
                "candidate_title": {
                    "id": "candidate_title",
                    "title": "Title",
                    "enabled": True,
                    "order": 1,
                    "job_agent_editable": False,
                },
                "candidate_tagline": {
                    "id": "candidate_tagline",
                    "title": "Candidate Tagline",
                    "enabled": True,
                    "order": 2,
                    "job_agent_editable": False,
                },
                "candidate_contact_detail": {
                    "id": "candidate_contact_detail",
                    "title": "Contact",
                    "enabled": True,
                    "order": 3,
                    "job_agent_editable": False,
                },
            }
        }
        blob = {
            "candidate_name": "Susan Somerset",
            "candidate_title": "Fractional TPM",
            "candidate_tagline": self._TAGLINE,
            "candidate_contact_detail": "hire@example.com",
        }
        html = builder_mod.build_session_base_resume(structure, blob)
        assert "<h1>Susan Somerset • Fractional TPM</h1>" in html
        header = html.split("<header", 1)[1].split("</header>", 1)[0]
        main = html.split("<main", 1)[1].split("</main>", 1)[0]
        assert "Program Delivery" not in header
        assert "Program Delivery" not in main
        assert "AI-Assisted Engineering" not in header
        assert "AI-Assisted Engineering" not in main
        assert f'<meta name="description" content="{self._META}" />' in html
        # Pre-fix mash shape must not appear in h1 when fields are split.
        assert "Fractional TPM — Program Delivery" not in html


class TestAst1029UatCompetenciesBulletsEmit:
    """AST-1029: bullet-joined competencies render in .competencies-list (no pipes)."""

    def test_session_competencies_list_uses_bullets_not_pipes(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", MagicMock())
        structure = {
            "sections": {
                "candidate_name": {
                    "id": "candidate_name",
                    "title": "Name",
                    "enabled": True,
                    "order": 0,
                    "job_agent_editable": False,
                },
                "core_competencies": {
                    "id": "core_competencies",
                    "title": "Core Competencies",
                    "enabled": True,
                    "order": 1,
                    "job_agent_editable": True,
                },
                "prior_experience": {
                    "id": "prior_experience",
                    "title": "Prior Experience",
                    "enabled": True,
                    "order": 2,
                    "job_agent_editable": True,
                },
            }
        }
        comps = (
            "AI-Assisted Delivery • Cross-Functional Execution • "
            "Risk and Dependency Management"
        )
        prior = "Project Manager (4 yrs) • Systems Analyst (6 yrs)"
        # Shared markers turn " • " into NBSP-bullet before emit.
        comps_html = comps.replace(" • ", "\u00a0• ")
        prior_html = prior.replace(" • ", "\u00a0• ")
        html = builder_mod.build_session_base_resume(
            structure,
            {
                "candidate_name": "Susan Somerset",
                "core_competencies": comps,
                "prior_experience": prior,
            },
        )
        assert 'class="competencies-list"' in html
        assert comps_html in html
        assert prior_html in html
        assert "AI-Assisted Delivery | Cross-Functional" not in html
        # No pipe separators in either competencies-list block.
        for block in html.split('class="competencies-list"')[1:]:
            text = block.split("</p>", 1)[0]
            assert " | " not in text
            assert "|" not in text


class TestAst1030UatNoBulletLeadEmit:
    """AST-1030: preserved `<no bullet>` → .role-description; stripped → first <li>."""

    def _structure(self) -> dict[str, Any]:
        return {
            "sections": {
                "experience": {
                    "id": "experience",
                    "title": "Experience",
                    "enabled": True,
                    "order": 0,
                    "job_agent_editable": True,
                },
            }
        }

    def test_with_prefix_lead_is_role_description_not_li(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", MagicMock())
        lead = (
            "<no bullet>Solo practice delivering embedded technical program management "
            "across 30+ SaaS engagements."
        )
        bullet = "Diagnosed and mitigated blockers across distributed teams."
        html = builder_mod.build_session_base_resume(
            self._structure(),
            {
                "experience": [
                    {
                        "company": "Somerset__Consulting",
                        "title": "Principal Technical Program Manager",
                        "dates": "2011 to Present",
                        "location": "United States / Full-time Remote",
                        "accomplishments": f"{lead}\n{bullet}",
                    }
                ],
            },
        )
        assert 'class="role-description"' in html
        assert "Solo practice delivering embedded technical program management" in html
        assert "<no bullet>" not in html
        # Lead must not appear as a list item.
        assert "<li>Solo practice delivering" not in html
        assert f"<li>{bullet}</li>" in html

    def test_without_prefix_first_line_is_li_not_role_description(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", MagicMock())
        first = (
            "Solo practice delivering embedded technical program management "
            "across 30+ SaaS engagements."
        )
        second = "Diagnosed and mitigated blockers across distributed teams."
        html = builder_mod.build_session_base_resume(
            self._structure(),
            {
                "experience": [
                    {
                        "company": "Somerset__Consulting",
                        "title": "Principal Technical Program Manager",
                        "dates": "2011 to Present",
                        "location": "United States / Full-time Remote",
                        "accomplishments": f"{first}\n{second}",
                    }
                ],
            },
        )
        assert 'class="role-description"' not in html
        assert f"<li>{first}</li>" in html
        assert f"<li>{second}</li>" in html


class TestAst1039SummaryNewlineParagraphs:
    """AST-1039: single-\\n summary → multiple .summary-intro; blank lines still work."""

    def _structure(self) -> dict[str, Any]:
        return {
            "sections": {
                "professional_summary": {
                    "id": "professional_summary",
                    "title": "Summary",
                    "enabled": True,
                    "order": 0,
                    "job_agent_editable": True,
                },
                "experience": {
                    "id": "experience",
                    "title": "Experience",
                    "enabled": True,
                    "order": 1,
                    "job_agent_editable": True,
                },
            }
        }

    def test_single_newline_yields_multiple_summary_intro(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", MagicMock())
        html = builder_mod.build_session_base_resume(
            self._structure(),
            {
                "professional_summary": "First para\nSecond para",
                "experience": "One bullet",
            },
        )
        intros = re.findall(
            r'<p class="summary-intro">(.*?)</p>', html, flags=re.DOTALL
        )
        assert intros == ["First para", "Second para"]
        # Must not be one collapsed paragraph with a literal newline inside.
        assert '<p class="summary-intro">First para\nSecond para</p>' not in html

    def test_blank_line_split_still_multiple_summary_intro(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", MagicMock())
        html = builder_mod.build_session_base_resume(
            self._structure(),
            {
                "professional_summary": "Para one\n\nPara two",
                "experience": "One bullet",
            },
        )
        intros = re.findall(
            r'<p class="summary-intro">(.*?)</p>', html, flags=re.DOTALL
        )
        assert intros == ["Para one", "Para two"]

    def test_experience_newlines_still_split_to_li(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", MagicMock())
        html = builder_mod.build_session_base_resume(
            self._structure(),
            {
                "professional_summary": "Keep me\nAs two",
                "experience": [
                    {
                        "company": "Acme",
                        "title": "TPM",
                        "dates": "2020 to 2021",
                        "location": "Remote",
                        "accomplishments": "Bullet A\nBullet B",
                    }
                ],
            },
        )
        assert "<li>Bullet A</li>" in html
        assert "<li>Bullet B</li>" in html
        assert re.findall(
            r'<p class="summary-intro">(.*?)</p>', html, flags=re.DOTALL
        ) == ["Keep me", "As two"]


class TestAst1014BuilderContact:
    """AST-1014: builder reads name columns + contact blob via _apply_contact_to_render_dict."""

    def test_coerce_row_injects_name_columns_for_render(self) -> None:
        row = _candidate_row(base_resume=_resume_blob())
        cd = builder_mod._coerce_candidate_blob(row)
        assert cd["_first"] == "Ada"
        assert cd["_full"] == "Ada Lovelace"
        assert cd["contact"]["contact_email"] == "ada@example.com"

    def test_apply_contact_uses_full_column_over_first_last(self) -> None:
        render = _resume_blob()
        builder_mod._apply_contact_to_render_dict(
            render,
            {"contact_email": "ada@example.com"},
            first="Ignored",
            last="Ignored",
            full="Ada Lovelace",
        )
        assert render["candidate_name"] == "Ada Lovelace"
        assert "ada@example.com" in render["candidate_contact_detail"]


# Branches: fields type/required/string; optional to/subject; candidate miss/image accept/reject;
# no-candidate skip; paragraph blank-line vs single-chunk newlines; debug True/False success+fail.
class TestAst1024BuildSessionCoverLetter:
    """AST-1024: session SomersetCover HTML from in-memory fields (no job load / artifact write)."""

    def _fields(self, **overrides: str) -> dict[str, Any]:
        base = {
            "from_block": "Susan Somerset • Oakland, CA\nhire@susansomerset.com",
            "letter_date": "July 27, 2026",
            "to_block": "",
            "subject": "",
            "letter": "Dear Hiring Team,\n\nParagraph two.",
            "signoff_closing": "Best,",
            "signature": "Susan Somerset",
        }
        base.update(overrides)
        return base

    def test_rejects_non_dict_fields(self) -> None:
        with pytest.raises(ValueError, match="session cover letter fields object is required"):
            builder_mod.build_session_cover_letter("bad")  # type: ignore[arg-type]

    def test_rejects_non_dict_fields_with_debug(self) -> None:
        with pytest.raises(ValueError, match="session cover letter fields object is required"):
            builder_mod.build_session_cover_letter("bad", debug=True)  # type: ignore[arg-type]

    def test_rejects_non_string_field(self) -> None:
        fields = self._fields()
        fields["letter"] = 42  # type: ignore[assignment]
        with pytest.raises(ValueError, match="letter must be a string"):
            builder_mod.build_session_cover_letter(fields)

    def test_rejects_missing_required(self) -> None:
        with pytest.raises(ValueError, match="from_block is required"):
            builder_mod.build_session_cover_letter(self._fields(from_block="  "))
        with pytest.raises(ValueError, match="letter is required"):
            builder_mod.build_session_cover_letter(self._fields(letter=""))

    def test_none_field_coerces_to_empty_then_required(self) -> None:
        fields = self._fields()
        fields["signature"] = None  # type: ignore[assignment]
        with pytest.raises(ValueError, match="signature is required"):
            builder_mod.build_session_cover_letter(fields)

    def test_rejects_invalid_with_debug(self) -> None:
        with pytest.raises(ValueError, match="letter is required"):
            builder_mod.build_session_cover_letter(self._fields(letter=""), debug=True)

    def test_renders_somerset_cover_without_candidate(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        get_c = MagicMock()
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", get_c)
        html = builder_mod.build_session_cover_letter(self._fields())
        assert "<title>SomersetCover</title>" in html
        assert 'class="fromBlock"' in html
        assert "Susan Somerset" in html
        assert "hire@susansomerset.com" in html
        assert 'class="letterdate"' in html
        assert "July 27, 2026" in html
        assert 'class="lettercontent"' in html
        assert "Dear Hiring Team," in html
        assert "Paragraph two." in html
        assert 'class="letterSignoff"' in html
        assert "Best," in html
        assert 'class="toBlock"' not in html
        assert 'class="lettersubject"' not in html
        assert "<img" not in html  # CSS may define .signature-img; body has no <img>
        get_c.assert_not_called()

    def test_optional_to_block_and_subject(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", MagicMock())
        html = builder_mod.build_session_cover_letter(
            self._fields(to_block="Acme Corp\nHiring Team", subject="Re: Staff Engineer")
        )
        assert 'class="toBlock"' in html
        assert "Acme Corp" in html
        assert 'class="lettersubject"' in html
        assert "Re: Staff Engineer" in html

    def test_ignores_unknown_extra_keys(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", MagicMock())
        fields = self._fields()
        fields["extra_noise"] = "ignored"
        html = builder_mod.build_session_cover_letter(fields)
        assert "ignored" not in html
        assert "Dear Hiring Team," in html

    def test_blank_line_paragraphs_and_single_chunk_newlines(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", MagicMock())
        html = builder_mod.build_session_cover_letter(
            self._fields(letter="Para A\n\nPara B")
        )
        assert "<p>Para A</p>" in html
        assert "<p>Para B</p>" in html
        html2 = builder_mod.build_session_cover_letter(
            self._fields(letter="Line one\nLine two")
        )
        assert "<p>Line one</p>" in html2
        assert "<p>Line two</p>" in html2
        # CRLF normalizes before paragraph split.
        html3 = builder_mod.build_session_cover_letter(
            self._fields(letter="CRLF A\r\n\r\nCRLF B")
        )
        assert "<p>CRLF A</p>" in html3
        assert "<p>CRLF B</p>" in html3

    def test_escapes_html_in_fields(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", MagicMock())
        html = builder_mod.build_session_cover_letter(
            self._fields(
                from_block="<b>From</b>",
                letter='Dear <script>alert(1)</script>',
                signature='Ada & Co',
            )
        )
        assert "<b>From</b>" not in html
        assert "&lt;b&gt;From&lt;/b&gt;" in html
        assert "<script>" not in html
        assert "Ada &amp; Co" in html

    def test_candidate_not_found(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", lambda cid: None)
        with pytest.raises(ValueError, match="Candidate not found: cand-x"):
            builder_mod.build_session_cover_letter(
                self._fields(), candidate_id="cand-x"
            )

    def test_candidate_not_found_with_debug(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", lambda cid: None)
        with pytest.raises(ValueError, match="Candidate not found"):
            builder_mod.build_session_cover_letter(
                self._fields(), candidate_id="cand-x", debug=True
            )

    def test_no_image_without_token_even_with_contact_image(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # AST-1126: stop auto-inject — image only when signature contains token.
        row = {
            "candidate_data": {
                "contact": {
                    "cover_letter_signature_image": "https://example.com/sig.png",
                }
            }
        }
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", lambda cid: row)
        html = builder_mod.build_session_cover_letter(
            self._fields(), candidate_id="cand-1"
        )
        assert "<img" not in html
        assert "Susan Somerset" in html

    def test_token_replaces_with_contact_image(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        row = {
            "candidate_data": {
                "contact": {
                    "cover_letter_signature_image": "https://example.com/sig.png",
                }
            }
        }
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", lambda cid: row)
        html = builder_mod.build_session_cover_letter(
            self._fields(signature="{$SIGNATURE_IMAGE}\nSusan Somerset"),
            candidate_id="cand-1",
        )
        # Signature may also appear in head meta; assert emit placement in signoff only.
        signoff = html.split('class="letterSignoff"', 1)[1].split("</div>", 1)[0]
        assert 'class="signature-img"' in signoff
        assert 'src="https://example.com/sig.png"' in signoff
        assert "{$SIGNATURE_IMAGE}" not in signoff
        assert "Susan Somerset" in signoff
        assert signoff.index("Best,") < signoff.index("<img") < signoff.index(
            "Susan Somerset"
        )

    def test_name_only_when_contact_image_absent_or_rejected(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        row_absent = {"candidate_data": {"contact": {}}}
        monkeypatch.setattr(
            builder_mod.candidate_mod, "get_candidate", lambda cid: row_absent
        )
        html = builder_mod.build_session_cover_letter(
            self._fields(signature="{$SIGNATURE_IMAGE}\nSusan Somerset"),
            candidate_id="cand-1",
        )
        signoff = html.split('class="letterSignoff"', 1)[1].split("</div>", 1)[0]
        assert "<img" not in signoff
        assert "{$SIGNATURE_IMAGE}" not in signoff
        assert "Susan Somerset" in signoff

        row_bad = {
            "candidate_data": {
                "contact": {"cover_letter_signature_image": "javascript:alert(1)"}
            }
        }
        monkeypatch.setattr(
            builder_mod.candidate_mod, "get_candidate", lambda cid: row_bad
        )
        html2 = builder_mod.build_session_cover_letter(
            self._fields(signature="{$SIGNATURE_IMAGE}\nSusan Somerset"),
            candidate_id="cand-1",
        )
        signoff2 = html2.split('class="letterSignoff"', 1)[1].split("</div>", 1)[0]
        assert "<img" not in signoff2
        assert "{$SIGNATURE_IMAGE}" not in signoff2

    def test_blank_candidate_id_skips_lookup(self, monkeypatch: pytest.MonkeyPatch) -> None:
        get_c = MagicMock()
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", get_c)
        html = builder_mod.build_session_cover_letter(self._fields(), candidate_id="  ")
        assert "<img" not in html
        get_c.assert_not_called()

    def test_success_with_debug(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", MagicMock())
        html = builder_mod.build_session_cover_letter(self._fields(), debug=True)
        assert "Dear Hiring Team," in html

    def test_non_string_field_with_debug(self) -> None:
        fields = self._fields()
        fields["letter_date"] = ["nope"]  # type: ignore[assignment]
        with pytest.raises(ValueError, match="letter_date must be a string"):
            builder_mod.build_session_cover_letter(fields, debug=True)


class TestAst1100BuilderPinResolve:
    """AST-1100: builder prefers resolved pins when legacy body dicts missing."""

    def test_resolve_resume_sections_from_pin(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "src.core.tracker.resolve_job_artifact_agent_data_body",
            lambda pin, debug=False: {"professional_summary": "From pin", "experience": "x"},
        )
        out = builder_mod._resolve_resume_sections(
            {"artifacts": {"job_resume": "pin-resume"}},
            {"artifacts": {}},
        )
        assert out["professional_summary"] == "From pin"

    def test_resolve_resume_prefers_legacy_resume_content(self, monkeypatch: pytest.MonkeyPatch) -> None:
        resolve = MagicMock(return_value={"professional_summary": "pin"})
        monkeypatch.setattr("src.core.tracker.resolve_job_artifact_agent_data_body", resolve)
        out = builder_mod._resolve_resume_sections(
            {
                "artifacts": {
                    "resume_content": {"professional_summary": "legacy", "experience": "e"},
                    "job_resume": "pin-resume",
                }
            },
            {"artifacts": {}},
        )
        assert out["professional_summary"] == "legacy"
        resolve.assert_not_called()

    def test_resolve_cover_letter_from_pin_string(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "src.core.tracker.resolve_job_artifact_agent_data_body",
            lambda pin, debug=False: {"re_line": "Re", "body": "Hello", "signature": ""},
        )
        out = builder_mod._resolve_cover_letter(
            {"artifacts": {"cover_letter": "pin-cover"}},
            {"context": {}},
        )
        assert out == {"re_line": "Re", "body": "Hello", "signature": ""}


class TestAst1126CoverSignatureImageToken:
    """AST-1126: token-only cover signature image; stop auto-above; Style D status lines."""

    _LIT = "{$SIGNATURE_IMAGE}"
    _SAFE = "https://example.com/sig.png"

    def test_job_signoff_image_between_closing_and_name(self) -> None:
        sig = f"Sincerely,\n\n{self._LIT}\nAda Lovelace\nEngineer"
        html = builder_mod._emit_cover_signoff_html(
            {"signature": sig},
            {"cover_letter_signature_image": self._SAFE},
        )
        assert "Cover letter signature" in html
        assert self._LIT not in html
        assert html.index("Sincerely") < html.index("<img") < html.index("Ada Lovelace")

    def test_job_no_image_without_token(self) -> None:
        html = builder_mod._emit_cover_signoff_html(
            {"signature": "Sincerely,\n\nAda Lovelace"},
            {"cover_letter_signature_image": self._SAFE},
        )
        assert "Ada Lovelace" in html
        assert "<img" not in html

    def test_job_token_omits_literal_when_image_rejected(self) -> None:
        html = builder_mod._emit_cover_signoff_html(
            {"signature": f"Ada\n{self._LIT}\nTitle"},
            {"cover_letter_signature_image": "javascript:alert(1)"},
        )
        assert "<img" not in html
        assert self._LIT not in html
        assert "Ada" in html and "Title" in html

    def test_token_status_matrix(self) -> None:
        root_ok = {"contact": {"cover_letter_signature_image": self._SAFE}}
        ts, src, im = builder_mod._signature_image_token_status(self._LIT, root_ok)
        assert (ts, src, im) == ("present", self._SAFE, "accepted")
        ts, src, im = builder_mod._signature_image_token_status("no token", root_ok)
        assert (ts, src, im) == ("absent", self._SAFE, "accepted")
        ts, src, im = builder_mod._signature_image_token_status(self._LIT, {"contact": {}})
        assert (ts, src, im) == ("present", None, "absent")
        ts, src, im = builder_mod._signature_image_token_status(
            self._LIT, {"contact": {"cover_letter_signature_image": "javascript:x"}}
        )
        assert (ts, src, im) == ("present", None, "rejected")
        assert builder_mod._lookup_dotted_path({"a": {"b": 1}}, "a.b") == 1
        assert builder_mod._lookup_dotted_path({"a": 1}, "a.b") is None

    def test_job_debug_emits_token_and_image_status(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        details: list[str] = []
        monkeypatch.setattr(builder_mod._log, "debug_detail", details.append)
        monkeypatch.setattr(builder_mod._log, "debug_detail_block", lambda *_a, **_k: None)
        monkeypatch.setattr(
            builder_mod._log, "debug_index", lambda **_k: None
        )
        job = {
            "astral_job_id": "job-1126",
            "job_data": {
                "artifacts": {
                    "cover_letter": {
                        "Subject": "Re",
                        "Letter": "Hello",
                        "signature": f"Sincerely,\n{self._LIT}\nAda",
                    },
                }
            },
        }
        cd = _candidate_row(base_resume=_resume_blob())
        cd["candidate_data"]["contact"]["cover_letter_signature_image"] = self._SAFE
        html = builder_mod.build_cover_letter_from_job(job, cd, debug=True)
        assert "<img" in html
        assert "signature_image_token=present" in details
        assert "signature_image=accepted" in details

    def test_resume_html_does_not_resolve_token(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            builder_mod.candidate_mod,
            "get_candidate",
            lambda candidate_id: _candidate_row(
                base_resume=_resume_blob(
                    professional_summary=f"Lead {self._LIT} line"
                )
            ),
        )
        html = builder_mod.build_base_resume("cand-1")
        assert self._LIT in html
        assert 'alt="Cover letter signature"' not in html
        assert 'class="signature-img"' not in html


class TestAst1139SessionCoverEmptyFromBlock:
    """AST-1139: session empty from_block → resolve_cover_from_block + Style D source."""

    def _fields(self, **overrides: str) -> dict[str, Any]:
        base = {
            "from_block": "Susan Somerset • Oakland, CA\nhire@susansomerset.com",
            "letter_date": "July 27, 2026",
            "to_block": "",
            "subject": "",
            "letter": "Dear Hiring Team,\n\nParagraph two.",
            "signoff_closing": "Best,",
            "signature": "Susan Somerset",
        }
        base.update(overrides)
        return base

    def _cand_row(self, **contact: Any) -> Dict[str, Any]:
        return {
            "astral_candidate_id": "cand-1139",
            "first": "Ada",
            "last": "Lovelace",
            "full": "Ada Lovelace",
            "candidate_data": {
                "contact": {
                    "contact_email": "ada@example.com",
                    "location": "London, UK",
                    **contact,
                },
                "artifacts": {},
                "context": {},
            },
        }

    def test_empty_from_block_with_candidate_uses_default(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            builder_mod.candidate_mod, "get_candidate", lambda _cid: self._cand_row()
        )
        html = builder_mod.build_session_cover_letter(
            self._fields(from_block="  "), candidate_id="cand-1139"
        )
        assert "<title>SomersetCover</title>" in html
        assert 'class="fromBlock"' in html
        from_html = html.split('class="fromBlock"', 1)[1].split("</div>", 1)[0]
        assert "Ada Lovelace" in from_html and "London, UK" in from_html
        assert "ada@example.com" in from_html
        assert "Susan Somerset" not in from_html
        style = html.split("<style>", 1)[1].split("</style>", 1)[0]
        for sel in (
            ".fromBlock",
            ".toBlock",
            ".letterdate",
            ".lettersubject",
            ".lettercontent",
            ".letterSignoff",
            ".signature-img",
        ):
            assert sel in style

    def test_empty_from_block_with_candidate_custom_text(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            builder_mod.candidate_mod,
            "get_candidate",
            lambda _cid: self._cand_row(
                cover_letter_from_block="Custom From\ncustom@example.com"
            ),
        )
        html = builder_mod.build_session_cover_letter(
            self._fields(from_block=""), candidate_id="cand-1139"
        )
        from_html = html.split('class="fromBlock"', 1)[1].split("</div>", 1)[0]
        assert "Custom From" in from_html
        assert "custom@example.com" in from_html
        assert "Ada Lovelace" not in from_html

    def test_nonempty_form_from_block_wins_as_session(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        get_c = MagicMock(return_value=self._cand_row())
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", get_c)
        details: list[str] = []
        monkeypatch.setattr(builder_mod._log, "debug_detail", details.append)
        monkeypatch.setattr(builder_mod._log, "debug_detail_block", lambda *_a, **_k: None)
        monkeypatch.setattr(builder_mod._log, "debug_index", lambda **_k: None)
        html = builder_mod.build_session_cover_letter(
            self._fields(from_block="Form Wins\nform@example.com"),
            candidate_id="cand-1139",
            debug=True,
        )
        from_html = html.split('class="fromBlock"', 1)[1].split("</div>", 1)[0]
        assert "Form Wins" in from_html
        assert "Ada Lovelace" not in from_html
        assert "from_block_source=session" in details
        assert "document_path=somerset_cover" in details
        get_c.assert_called_once_with("cand-1139")

    def test_empty_from_block_without_candidate_still_required(self) -> None:
        with pytest.raises(ValueError, match="from_block is required"):
            builder_mod.build_session_cover_letter(self._fields(from_block=""))

    def test_debug_default_source(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            builder_mod.candidate_mod, "get_candidate", lambda _cid: self._cand_row()
        )
        details: list[str] = []
        monkeypatch.setattr(builder_mod._log, "debug_detail", details.append)
        monkeypatch.setattr(builder_mod._log, "debug_detail_block", lambda *_a, **_k: None)
        monkeypatch.setattr(builder_mod._log, "debug_index", lambda **_k: None)
        builder_mod.build_session_cover_letter(
            self._fields(from_block=""), candidate_id="cand-1139", debug=True
        )
        assert "from_block_source=default" in details
        assert any(d.startswith("from_block_chars=") for d in details)
        assert "document_path=somerset_cover" in details



class TestAst1148SessionTypedFromBlockExpand:
    """AST-1148: non-empty session from_block expands tokens / | → • before emit."""

    def _fields(self, **overrides: str) -> dict[str, Any]:
        base = {
            "from_block": "",
            "letter_date": "July 27, 2026",
            "to_block": "",
            "subject": "",
            "letter": "Dear Hiring Team,\n\nParagraph two.",
            "signoff_closing": "Best,",
            "signature": "Susan Somerset",
        }
        base.update(overrides)
        return base

    def _cand_row(self, **contact: Any) -> Dict[str, Any]:
        return {
            "astral_candidate_id": "cand-1148",
            "first": "Ada",
            "last": "Lovelace",
            "full": "Ada Lovelace",
            "candidate_data": {
                "contact": {
                    "contact_email": "ada@example.com",
                    "location": "London, UK",
                    "phone": "555-0100",
                    **contact,
                },
                "artifacts": {},
                "context": {},
            },
        }

    def test_session_typed_tokens_and_pipe_expand(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            builder_mod.candidate_mod, "get_candidate", lambda _cid: self._cand_row()
        )
        html = builder_mod.build_session_cover_letter(
            self._fields(
                from_block="{$FULL_NAME} | {$LOCATION}\n{$CONTACT_EMAIL} | {$PHONE}"
            ),
            candidate_id="cand-1148",
        )
        from_html = html.split('class="fromBlock"', 1)[1].split("</div>", 1)[0]
        assert "Ada Lovelace" in from_html and "London, UK" in from_html
        assert "ada@example.com" in from_html and "555-0100" in from_html
        assert "{$FULL_NAME}" not in from_html
        assert "|" not in from_html.replace("&", "")  # authoring | rewritten
        assert "•" in from_html or "&#8226;" in from_html or "&bull;" in from_html

    def test_session_typed_without_candidate_drops_empty_tokens(self) -> None:
        html = builder_mod.build_session_cover_letter(
            self._fields(from_block="{$FULL_NAME} | Hello\nWorld")
        )
        from_html = html.split('class="fromBlock"', 1)[1].split("</div>", 1)[0]
        # FULL_NAME empty without candidate → segment dropped; literal Hello/World remain.
        assert "Hello" in from_html and "World" in from_html
        assert "{$FULL_NAME}" not in from_html

    def test_job_custom_tokens_expand(self) -> None:
        cd = _candidate_row(base_resume=_resume_blob())
        cd["candidate_data"]["contact"]["location"] = "London, UK"
        cd["candidate_data"]["contact"]["cover_letter_from_block"] = (
            "{$FULL_NAME} | {$LOCATION}\n{$CONTACT_EMAIL}"
        )
        html = builder_mod.build_cover_letter_from_job(
            {
                "astral_job_id": "job-1148",
                "job_data": {
                    "artifacts": {
                        "cover_letter": {
                            "Subject": "Re: Role",
                            "Letter": "Dear team,",
                            "signature": "Ada",
                        }
                    }
                },
            },
            cd,
        )
        from_html = html.split('class="fromBlock"', 1)[1].split("</div>", 1)[0]
        assert "Ada Lovelace" in from_html and "London, UK" in from_html
        assert "ada@example.com" in from_html
        assert "{$FULL_NAME}" not in from_html


class TestAst1138JobCoverSomersetFromBlock:
    """AST-1138: job Print Cover Letter → SomersetCover fromBlock + golden CSS."""

    _GOLDEN_SELECTORS = (
        ".fromBlock",
        ".toBlock",
        ".letterdate",
        ".lettersubject",
        ".lettercontent",
        ".letterSignoff",
        ".signature-img",
    )

    def _job(self, cover: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "astral_job_id": "job-1138",
            "job_data": {"artifacts": {"cover_letter": cover}},
        }

    def test_default_from_block_and_somerset_shell(self) -> None:
        cd = _candidate_row(base_resume=_resume_blob())
        cd["candidate_data"]["contact"]["location"] = "London, UK"
        html = builder_mod.build_cover_letter_from_job(
            self._job({"Subject": "Re: Role", "Letter": "Dear team,\n\nThanks.", "signature": "Ada"}),
            cd,
        )
        assert "<title>SomersetCover</title>" in html
        assert 'class="fromBlock"' in html
        # Default composition: Name • City / email (br between identity lines).
        assert "Ada Lovelace" in html and "London, UK" in html
        assert "ada@example.com" in html
        assert "<br>" in html.split('class="fromBlock"', 1)[1].split("</div>", 1)[0]
        assert 'class="lettersubject"' in html and "Re: Role" in html
        assert "Dear team," in html and "Thanks." in html
        assert 'class="letterSignoff"' in html and "Ada" in html
        assert 'class="letterdate"' in html  # empty date still emits selector
        assert 'class="toBlock"' not in html
        # No resume header/contact chrome on cover-only.
        assert 'aria-label="Cover body"' not in html
        assert re.search(r"<h1[^>]*>\s*Ada Lovelace\s*</h1>", html) is None
        assert 'class="contact"' not in html
        style = html.split("<style>", 1)[1].split("</style>", 1)[0]
        for sel in self._GOLDEN_SELECTORS:
            assert sel in style

    def test_candidate_from_block_text(self) -> None:
        cd = _candidate_row(base_resume=_resume_blob())
        cd["candidate_data"]["contact"]["cover_letter_from_block"] = (
            "Custom Name • Place\ncustom@example.com"
        )
        html = builder_mod.build_cover_letter_from_job(
            self._job({"Letter": "Body only", "signature": ""}),
            cd,
        )
        from_html = html.split('class="fromBlock"', 1)[1].split("</div>", 1)[0]
        assert "Custom Name" in from_html
        assert "custom@example.com" in from_html
        assert "Ada Lovelace" not in from_html

    def test_resume_print_unchanged_no_from_block(self) -> None:
        job = {
            "job_data": {
                "artifacts": {
                    "resume_content": _resume_blob(professional_summary="Summary text"),
                    "cover_letter": {"re_line": "Re", "body": "Cover body", "signature": ""},
                }
            }
        }
        html = builder_mod.build_resume_from_job(
            job, _candidate_row(base_resume=_resume_blob()), include_cover=False
        )
        assert "Summary text" in html
        assert 'class="fromBlock"' not in html
        assert "<title>SomersetCover</title>" not in html

    def test_debug_from_block_source_and_document_path(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        details: list[str] = []
        outcomes: list[str] = []

        def _index(**kwargs: Any) -> None:
            outcomes.append(str(kwargs.get("outcome") or ""))

        monkeypatch.setattr(builder_mod._log, "debug_detail", details.append)
        monkeypatch.setattr(builder_mod._log, "debug_detail_block", lambda *_a, **_k: None)
        monkeypatch.setattr(builder_mod._log, "debug_index", _index)
        cd = _candidate_row(base_resume=_resume_blob())
        cd["candidate_data"]["contact"]["cover_letter_from_block"] = "Line A\nLine B"
        html = builder_mod.build_cover_letter_from_job(
            self._job({"Letter": "Hello", "signature": "Ada"}),
            cd,
            debug=True,
        )
        assert "Hello" in html
        assert any("somerset cover html" in o for o in outcomes)
        assert "from_block_source=candidate" in details
        assert any(d.startswith("from_block_chars=") for d in details)
        assert "document_path=somerset_cover" in details

    def test_debug_false_skips_builder_index(self, monkeypatch: pytest.MonkeyPatch) -> None:
        called = {"index": 0}

        def _index(**_k: Any) -> None:
            called["index"] += 1

        monkeypatch.setattr(builder_mod._log, "debug_index", _index)
        monkeypatch.setattr(builder_mod._log, "debug_detail", lambda *_a, **_k: None)
        monkeypatch.setattr(builder_mod._log, "debug_detail_block", lambda *_a, **_k: None)
        builder_mod.build_cover_letter_from_job(
            self._job({"Letter": "Quiet", "signature": ""}),
            _candidate_row(base_resume=_resume_blob()),
            debug=False,
        )
        assert called["index"] == 0

    def test_job_cover_somerset_field_mapper(self) -> None:
        fields = builder_mod._job_cover_somerset_fields(
            {"re_line": "Subj", "body": "Letter body", "signature": "Sig"},
            "From text",
        )
        assert fields["from_block"] == "From text"
        assert fields["subject"] == "Subj"
        assert fields["letter"] == "Letter body"
        assert fields["signature"] == "Sig"
        assert fields["letter_date"] == ""
        assert fields["to_block"] == ""
        assert fields["signoff_closing"] == ""
        assert set(fields) == set(builder_mod.BUILD_CONFIG["session_cover_letter"]["fields"])

    def test_candidate_shape_for_resolve(self) -> None:
        shaped = builder_mod._candidate_for_cover_from_block(
            {
                "_full": "Ada Lovelace",
                "_first": "Ada",
                "_last": "Lovelace",
                "contact": {"contact_email": "ada@example.com"},
                "astral_candidate_id": "cand-1",
            }
        )
        assert shaped == {
            "full": "Ada Lovelace",
            "first": "Ada",
            "last": "Lovelace",
            "contact": {"contact_email": "ada@example.com"},
            "astral_candidate_id": "cand-1",
        }


class TestAst1162SignatureImgVerticalSpacing:
    """AST-1162: SomersetCover `.signature-img` non-negative bottom margin (no overlap)."""

    _LIT = "{$SIGNATURE_IMAGE}"
    _SAFE = "https://example.com/sig.png"
    # Supersedes AST-1024 / AST-1124 golden `margin: 8px 0 -25px 0`.
    _MARGIN = "margin: 8px 0 8px 0"

    @staticmethod
    def _signature_img_rule(html: str) -> str:
        style = html.split("<style>", 1)[1].split("</style>", 1)[0]
        m = re.search(r"\.signature-img\s*\{([^}]+)\}", style)
        assert m is not None, "missing .signature-img rule"
        return m.group(1)

    def _assert_positive_stack_margin(self, html: str) -> None:
        rule = self._signature_img_rule(html)
        assert "display: block" in rule
        assert "height: 61px" in rule
        assert self._MARGIN in rule
        assert "-25px" not in rule

    def test_session_signature_img_margin_non_negative(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            builder_mod.candidate_mod,
            "get_candidate",
            lambda _cid: {
                "candidate_data": {
                    "contact": {"cover_letter_signature_image": self._SAFE}
                }
            },
        )
        html = builder_mod.build_session_cover_letter(
            {
                "from_block": "Ada Lovelace\nada@example.com",
                "letter_date": "August 3, 2026",
                "to_block": "",
                "subject": "",
                "letter": "Dear Hiring Team,\n\nThanks.",
                "signoff_closing": "Best,",
                "signature": f"{self._LIT}\nSusan Somerset",
            },
            candidate_id="cand-1162",
        )
        self._assert_positive_stack_margin(html)
        signoff = html.split('class="letterSignoff"', 1)[1].split("</div>", 1)[0]
        assert 'class="signature-img"' in signoff
        assert signoff.index("Best,") < signoff.index("<img") < signoff.index(
            "Susan Somerset"
        )

    def test_job_somerset_signature_img_margin_non_negative(self) -> None:
        cd = _candidate_row(base_resume=_resume_blob())
        html = builder_mod.build_cover_letter_from_job(
            {
                "astral_job_id": "job-1162",
                "job_data": {
                    "artifacts": {
                        "cover_letter": {
                            "Subject": "Re: Role",
                            "Letter": "Dear team,",
                            "signature": f"{self._LIT}\nAda Lovelace",
                        }
                    }
                },
            },
            cd,
        )
        self._assert_positive_stack_margin(html)
        signoff = html.split('class="letterSignoff"', 1)[1].split("</div>", 1)[0]
        assert 'class="signature-img"' in signoff
        assert signoff.index("<img") < signoff.index("Ada Lovelace")

    def test_session_no_image_keeps_closing_and_name(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Token absent → no empty <img> / no image box from this CSS-only change.
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", MagicMock())
        html = builder_mod.build_session_cover_letter(
            {
                "from_block": "Ada Lovelace\nada@example.com",
                "letter_date": "August 3, 2026",
                "to_block": "",
                "subject": "",
                "letter": "Dear Hiring Team,",
                "signoff_closing": "Best,",
                "signature": "Susan Somerset",
            }
        )
        self._assert_positive_stack_margin(html)  # rule still present in stylesheet
        signoff = html.split('class="letterSignoff"', 1)[1].split("</div>", 1)[0]
        assert "<img" not in signoff
        assert "Best," in signoff and "Susan Somerset" in signoff


class TestAst1165SignoffNewlineToBr:
    """AST-1165: SomersetCover signature fragment newlines → <br> after escape."""

    _LIT = "{$SIGNATURE_IMAGE}"
    _SAFE = "https://example.com/sig.png"

    def test_session_name_and_title_br_after_image(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            builder_mod.candidate_mod,
            "get_candidate",
            lambda _cid: {
                "candidate_data": {
                    "contact": {"cover_letter_signature_image": self._SAFE}
                }
            },
        )
        html = builder_mod.build_session_cover_letter(
            {
                "from_block": "Ada Lovelace\nada@example.com",
                "letter_date": "August 3, 2026",
                "to_block": "",
                "subject": "",
                "letter": "Dear Hiring Team,",
                "signoff_closing": "Best,",
                "signature": f"{self._LIT}\nSusan Somerset\nSenior Product Manager",
            },
            candidate_id="cand-1165",
        )
        signoff = html.split('class="letterSignoff"', 1)[1].split("</div>", 1)[0]
        assert 'class="signature-img"' in signoff
        assert "Susan Somerset<br>Senior Product Manager" in signoff
        assert signoff.index("Best,") < signoff.index("<img") < signoff.index(
            "Susan Somerset"
        )
        # AST-1162 sibling: non-negative stack margin still present.
        style = html.split("<style>", 1)[1].split("</style>", 1)[0]
        assert "margin: 8px 0 8px 0" in style
        assert "-25px" not in style

    def test_job_somerset_name_and_title_br_after_image(self) -> None:
        cd = _candidate_row(base_resume=_resume_blob())
        html = builder_mod.build_cover_letter_from_job(
            {
                "astral_job_id": "job-1165",
                "job_data": {
                    "artifacts": {
                        "cover_letter": {
                            "Subject": "Re: Role",
                            "Letter": "Dear team,",
                            "signature": f"{self._LIT}\nAda Lovelace\nEngineer",
                        }
                    }
                },
            },
            cd,
        )
        signoff = html.split('class="letterSignoff"', 1)[1].split("</div>", 1)[0]
        assert 'class="signature-img"' in signoff
        assert "Ada Lovelace<br>Engineer" in signoff
        assert signoff.index("<img") < signoff.index("Ada Lovelace")

    def test_token_absent_preserves_newlines_no_img(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(builder_mod.candidate_mod, "get_candidate", MagicMock())
        html = builder_mod.build_session_cover_letter(
            {
                "from_block": "Ada Lovelace\nada@example.com",
                "letter_date": "August 3, 2026",
                "to_block": "",
                "subject": "",
                "letter": "Dear Hiring Team,",
                "signoff_closing": "Best,",
                "signature": "Susan Somerset\nSenior Product Manager",
            }
        )
        signoff = html.split('class="letterSignoff"', 1)[1].split("</div>", 1)[0]
        assert "<img" not in signoff
        assert "Susan Somerset<br>Senior Product Manager" in signoff
        assert "{$SIGNATURE_IMAGE}" not in signoff
