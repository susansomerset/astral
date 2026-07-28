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
