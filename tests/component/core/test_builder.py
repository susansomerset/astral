"""Component tests for src/core/builder.py (AST-393)."""

from __future__ import annotations

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
        "candidate_data": {
            "profile": {
                "first": "Ada",
                "last": "Lovelace",
                "contact_email": "ada@example.com",
                "cover_letter_signature_image": "https://example.com/sig.png",
            },
            "artifacts": artifacts,
            "context": {"sample_cover_text": "Dear team,\nThanks"},
        }
    }


class TestCoerceCandidateBlob:
    def test_unwraps_nested_candidate_rows(self) -> None:
        inner = {"profile": {"first": "Ada"}}
        assert builder_mod._coerce_candidate_blob({"candidate_data": inner}) == inner
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
        job = {
            "job_data": {
                "artifacts": {
                    "cover_letter": {"Subject": "", "Letter": "Dear team", "signature": ""},
                }
            }
        }
        html = builder_mod.build_cover_letter_from_job(job, _candidate_row(base_resume=_resume_blob()))
        assert 'aria-label="Cover body"' in html
        assert "Dear team" in html
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
        builder_mod._apply_profile_to_render_dict(
            render,
            {
                "first": "Ada",
                "last": "Lovelace",
                "contact_email": "ada@example.com",
                "phone": "555",
                "linkedin_url": "https://linkedin.com/in/ada",
                "github": "https://github.com/ada",
                "location": "London",
            },
        )
        marked = builder_mod._apply_resume_text_markers(render)
        assert marked["experience"] == {"role": "lead"}
        assert "\u00a0" in marked["professional_summary"]
        assert "555" in render["candidate_contact_detail"]

    def test_resolves_cover_letter_from_sample_text(self) -> None:
        resolved = builder_mod._resolve_cover_letter(
            {"artifacts": {}},
            {"context": {"sample_cover_text": "  Hello cover  "}},
        )
        assert resolved == {"re_line": "", "body": "Hello cover", "signature": ""}
        assert builder_mod._cover_letter_nonempty({"re_line": "", "body": "", "signature": ""}) is False
        assert builder_mod._cover_letter_nonempty({"re_line": "Re"}) is True
        assert builder_mod._cover_letter_nonempty({"re_line": 123, "body": None}) is True
        assert builder_mod._resolve_cover_letter({"artifacts": {}}, {"context": {}}) is None

    def test_profile_uses_reply_email_and_skips_empty_name(self) -> None:
        render = _resume_blob()
        builder_mod._apply_profile_to_render_dict(render, {"reply_email": "reply@example.com"})
        assert "reply@example.com" in render["candidate_contact_detail"]
        render = _resume_blob(candidate_name="Keep")
        builder_mod._apply_profile_to_render_dict(render, {"first": "  ", "last": ""})
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
        image_only = builder_mod._emit_cover_signoff_html(
            {"signature": ""},
            {"cover_letter_signature_image": "https://example.com/sig.png"},
        )
        assert "Cover letter signature" in image_only
        signoff = builder_mod._emit_cover_signoff_html({"signature": "Thanks"}, {})
        assert "Thanks" in signoff
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
            "profile": {"first": "Ada", "last": "Lovelace", "contact_email": "ada@example.com"},
            "artifacts": {"resume_structure": structure, "base_resume": blob},
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
        job = {
            "job_data": {
                "artifacts": {
                    "cover_letter": {"Subject": "Re: Role", "Letter": "Hello there", "signature": ""},
                }
            }
        }
        html = builder_mod.build_cover_letter_from_job(job, _candidate_row(base_resume=_resume_blob()))
        assert 'aria-label="Cover body"' in html
        assert "Re: Role" in html
        assert "Hello there" in html
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
            == "candidate_data.context.sample_cover_text"
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
        cd["candidate_data"]["profile"]["cover_letter_signature_image"] = "https://example.com/sig.png"
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
        cd["candidate_data"]["profile"]["cover_letter_signature_image"] = "javascript:alert(1)"
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
