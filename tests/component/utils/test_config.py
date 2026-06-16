"""Component tests for src/utils/config.py (AST-390)."""

from __future__ import annotations

import json

import pytest

from src.utils import config as cfg


# Branches: stable key list from TASK_CONFIG.
class TestGetTaskKeys:
    def test_returns_all_task_keys(self) -> None:
        keys = cfg.get_task_keys()
        assert "craft_resume_base" in keys
        assert keys == list(cfg.TASK_CONFIG.keys())


def _board_entry(adopted: bool) -> dict:
    """Minimal BOARD_CONFIG row for list_adopted_boards / get_board_entry (AST-457)."""
    return {
        "label": "L",
        "entry_url": "https://boards.example/",
        "scrape_mode": "deep_link",
        "craft_task_key": "craft_board_search_criteria",
        "adopted": adopted,
    }


class TestBoardRegistryAst457:
    def test_list_adopted_boards_skips_non_adopted_sorts_keys(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            cfg,
            "BOARD_CONFIG",
            {
                "z_skip": _board_entry(False),
                "m_pick": _board_entry(True),
            },
            raising=False,
        )
        rows = cfg.list_adopted_boards()
        assert rows == [
            {
                "board_key": "m_pick",
                "label": "L",
                "entry_url": "https://boards.example/",
                "scrape_mode": "deep_link",
                "craft_task_key": "craft_board_search_criteria",
            },
        ]

    def test_get_board_entry_none_when_unknown_or_not_adopted(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(cfg, "BOARD_CONFIG", {"x": _board_entry(False)}, raising=False)
        assert cfg.get_board_entry("missing") is None
        assert cfg.get_board_entry("x") is None

    def test_get_board_entry_returns_copy_when_adopted(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(cfg, "BOARD_CONFIG", {"b": _board_entry(True)}, raising=False)
        out = cfg.get_board_entry("b")
        assert out is not None
        assert out["label"] == "L"
        out["label"] = "mutated"
        assert cfg.BOARD_CONFIG["b"]["label"] == "L"


# BOARD_CONFIG adoption filter: explicit adopted:false/true and missing adopted key
# (see list_adopted_boards / get_board_entry, src/utils/config.py ~686-708).
class TestBoardRegistryAdoptedBranches:
    def test_list_adopted_boards_explicit_false_missing_key_vs_true(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            cfg,
            "BOARD_CONFIG",
            {
                "baa": {
                    "label": "A",
                    "entry_url": "https://a",
                    "scrape_mode": "s",
                    "craft_task_key": "k",
                    "adopted": False,
                },
                # No `adopted` key → .get("adopted") is falsy → same skip path as explicit false.
                "bbb": {"label": "B", "entry_url": "https://b", "scrape_mode": "s", "craft_task_key": "k"},
                "zzz": {
                    "label": "Z",
                    "entry_url": "https://z",
                    "scrape_mode": "s",
                    "craft_task_key": "k",
                    "adopted": True,
                },
            },
            raising=False,
        )
        rows = cfg.list_adopted_boards()
        assert [r["board_key"] for r in rows] == ["zzz"]

    def test_get_board_entry_explicit_false_missing_key_unknown_vs_true(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            cfg,
            "BOARD_CONFIG",
            {
                "bare": {"label": "L", "entry_url": "https://x", "scrape_mode": "s", "craft_task_key": "k"},
                "nope": {
                    "label": "L",
                    "entry_url": "https://x",
                    "scrape_mode": "s",
                    "craft_task_key": "k",
                    "adopted": False,
                },
                "yep": {
                    "label": "L",
                    "entry_url": "https://y",
                    "scrape_mode": "s",
                    "craft_task_key": "k",
                    "adopted": True,
                },
            },
            raising=False,
        )
        assert cfg.get_board_entry("missing_board") is None
        assert cfg.get_board_entry("bare") is None
        assert cfg.get_board_entry("nope") is None
        got = cfg.get_board_entry("yep")
        assert got is not None and got["adopted"] is True
        got["entry_url"] = "mutated"
        assert cfg.BOARD_CONFIG["yep"]["entry_url"] == "https://y"


# Branches: type guard; range; configured multiplier.
class TestImportanceMultiplier:
    def test_returns_configured_multiplier(self) -> None:
        assert cfg.importance_multiplier(5) == pytest.approx(1.06)

    def test_rejects_non_int_and_out_of_range(self) -> None:
        with pytest.raises(ValueError, match="importance must be int"):
            cfg.importance_multiplier(True)  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="out of range"):
            cfg.importance_multiplier(0)


class TestGradeValuesConfig:
    def test_grade_values_and_rubric_total(self) -> None:
        assert set(cfg.GRADE_VALUES) == {"A", "B", "C", "D"}
        assert cfg.GRADE_VALUES["A"] == 7
        assert cfg.RUBRIC_TOTAL == 3000
        assert cfg.grade_value("b") == 6

    def test_grade_value_rejects_unknown_letter(self) -> None:
        with pytest.raises(ValueError, match="Unknown grade"):
            cfg.grade_value("Z")
        with pytest.raises(ValueError, match="Unknown grade"):
            cfg.grade_value("")


# Branches: known model; unknown model.
class TestGetModel:
    def test_returns_model_entry(self) -> None:
        model = cfg.get_model("claude-sonnet-4-6")
        assert model["model_label"] == "Sonnet"

    def test_raises_for_unknown_model(self) -> None:
        with pytest.raises(ValueError, match="Unknown model_code"):
            cfg.get_model("missing-model")


# Branches: sorted token registry keys.
class TestGetTokens:
    def test_returns_sorted_token_names(self) -> None:
        tokens = cfg.get_tokens()
        assert tokens == sorted(cfg.TOKEN_SOURCES.keys())
        assert "FIRST_NAME" in tokens


class TestGetManageTasksChainTokens:
    def test_sorted_chain_registry_keys_only(self) -> None:
        expected = sorted(k for k, spec in cfg.TOKEN_SOURCES.items() if spec.get("source") == "chain")
        assert cfg.get_manage_tasks_chain_tokens() == expected
        assert "SELECTED_AGENT" in expected
        assert "FIRST_NAME" not in expected


class TestGetManageAgentsTokens:
    """AST-632: Manage Agents picker — registry minus chain/hop tokens."""

    def test_excludes_chain_and_hop_tokens(self) -> None:
        chain = set(cfg.get_manage_tasks_chain_tokens())
        agents = cfg.get_manage_agents_tokens()
        assert agents == sorted(k for k in cfg.get_tokens() if k not in chain)
        assert "FIRST_NAME" in agents
        assert "SELECTED_AGENT" not in agents
        assert not any(t.startswith("CALLER_") for t in agents)


# Branches: missing task/schema; encoded variants; JSON example envelope.
class TestStringifyResponseSchema:
    def test_returns_empty_for_unknown_task(self) -> None:
        assert cfg.stringify_response_schema("not-a-task") == ""

    def test_encoded_meta_notes_and_default_encoded_examples(self) -> None:
        meta = json.loads(cfg.stringify_response_schema("qualify_job_listings"))
        assert isinstance(meta["agent_payload"], str)
        assert "|" in meta["agent_payload"]

        encoded = json.loads(cfg.stringify_response_schema("evaluate_jd"))
        assert encoded["agent_payload"] == "000|ERC2|MEA3|PGA2"

        notes = json.loads(cfg.stringify_response_schema("grade_do"))
        assert "optional notes" in notes["agent_payload"]

    def test_builds_schema_example_envelope(self) -> None:
        out = json.loads(cfg.stringify_response_schema("craft_resume_base"))
        assert "resume_structure" in out["agent_payload"]
        assert out["agent_payload"]["candidate_name"] == "<candidate_name>"
        assert out["agent_performance"]["status"] == "success | failure"

    def test_prefilter_company_schema_shows_bracket_link_set_tails(self) -> None:
        # AST-697: RESPONSE_SCHEMA example documents positional bracket link_set tails.
        env = json.loads(cfg.stringify_response_schema("prefilter_company"))
        assert env["agent_payload"] == "000|ERC2|MEA3|PGA2|[13]|[3,6,19]"


# Branches: default empty agent; explicit prompt.
class TestChainContextSelectedAgent:
    def test_builds_selected_agent_context(self) -> None:
        assert cfg.chain_context_selected_agent() == {"SELECTED_AGENT": ""}
        assert cfg.chain_context_selected_agent("prompt") == {"SELECTED_AGENT": "prompt"}


# Branches: allowed value; rejected value.
class TestValidateValue:
    def test_accepts_allowed_value(self) -> None:
        cfg.validate_value(["A", "B"], "A")

    def test_raises_for_disallowed_value(self) -> None:
        with pytest.raises(ValueError, match="not in allowed list"):
            cfg.validate_value(["A"], "Z")


# Branches: unknown token; candidate; config; output_type; chain; empty warnings.
class TestResolveTokens:
    def test_leaves_unknown_tokens_unchanged(self) -> None:
        text = cfg.resolve_tokens("{$UNKNOWN_TOKEN}", {}, "craft_resume_base")
        assert text == "{$UNKNOWN_TOKEN}"

    def test_resolves_candidate_config_output_and_chain_tokens(self) -> None:
        candidate = {
            "profile": {"first": "Ada"},
            "context": {"strengths": "systems"},
            "artifacts": {"get_rubric": [{"label": "R", "content": "rule"}]},
        }
        chain = {
            "SELECTED_AGENT": "agent body",
            "CALLER_RESPONSE": "prior",
        }
        text = (
            "Hi {$FIRST_NAME}, agent={$SELECTED_AGENT}, prior={$CALLER_RESPONSE}, "
            "schema={$RESPONSE_SCHEMA}, output={$OUTPUT_INSTRUCTIONS}, rubric={$GET_RUBRIC}"
        )
        resolved = cfg.resolve_tokens(
            text,
            candidate,
            "grade_get",
            chain_context=chain,
        )
        assert "Hi Ada" in resolved
        assert "agent=agent body" in resolved
        assert "prior=prior" in resolved
        assert '"agent_payload"' in resolved
        assert "rubric=" in resolved

    def test_logs_and_returns_empty_for_missing_candidate_and_chain_values(self, caplog) -> None:
        caplog.set_level("WARNING")
        out = cfg.resolve_tokens("{$FIRST_NAME} {$CALLER_RESPONSE}", {}, "grade_get", chain_context={})
        assert out.strip() == ""
        assert any("resolved to empty" in rec.message for rec in caplog.records)

    def test_output_type_token_uses_task_instructions(self) -> None:
        text = cfg.resolve_tokens("{$OUTPUT_INSTRUCTIONS}", {}, "evaluate_jd")
        assert "grade segments" in text.lower() or "Each grade segment" in text

    def test_config_resolver_missing_name_returns_empty(self, monkeypatch) -> None:
        monkeypatch.setitem(cfg.TOKEN_SOURCES, "BROKEN_CONFIG", {"source": "config", "resolver": "missing"})
        assert cfg.resolve_tokens("{$BROKEN_CONFIG}", {}, "craft_resume_base") == ""

    def test_unknown_token_source_is_left_unchanged(self, monkeypatch) -> None:
        monkeypatch.setitem(cfg.TOKEN_SOURCES, "WEIRD", {"source": "other"})
        assert cfg.resolve_tokens("{$WEIRD}", {}, "craft_resume_base") == "{$WEIRD}"

    def test_output_type_missing_instructions_returns_empty(self) -> None:
        assert cfg.resolve_tokens("{$OUTPUT_INSTRUCTIONS}", {}, "craft_resume_base") == ""

    def test_chain_missing_value_returns_empty_string(self) -> None:
        assert cfg.resolve_tokens("{$CALLER_CACHE_A}", {}, "craft_resume_base", chain_context=None) == ""

    def test_resolves_writing_preferences_from_context(self) -> None:
        candidate = {"context": {"writing_preferences": "NO EM DASHES"}}
        assert cfg.resolve_tokens("{$WRITING_PREFERENCES}", candidate, "draft_cover_letter") == "NO EM DASHES"

    def test_resolves_cover_letter_signature_from_profile(self) -> None:
        candidate = {"profile": {"cover_letter_signature": "— Ada"}}
        assert cfg.resolve_tokens("{$COVER_LETTER_SIGNATURE}", candidate, "draft_cover_letter") == "— Ada"

    def test_base_resume_token_emits_section_json_not_markdown(self) -> None:
        from src.core.candidate import default_resume_structure

        structure = default_resume_structure()
        summary_title = structure["sections"]["professional_summary"]["title"]
        candidate = {
            "artifacts": {
                "resume_structure": structure,
                "base_resume": [{"label": summary_title, "content": "Token body"}],
            }
        }
        out = cfg.resolve_tokens("base={$BASE_RESUME}", candidate, "draft_job_resume")
        assert "###" not in out
        assert '"professional_summary": "Token body"' in out


class TestAst513JobTokens:
    """AST-513: job-scoped artifact prompt tokens resolve from job_context."""

    _NAMES = ("VISIBLE_JD", "ANALYSIS_JD", "ANALYSIS_DO", "ANALYSIS_GET", "ANALYSIS_LIKE")

    def test_get_tokens_includes_job_scoped_names(self) -> None:
        tokens = cfg.get_tokens()
        for name in self._NAMES:
            assert name in tokens
            assert cfg.TOKEN_SOURCES[name] == {"source": "job"}

    def test_job_token_config_maps_analysis_phases(self) -> None:
        phases = cfg.JOB_TOKEN_CONFIG["analysis_phases"]
        assert phases["ANALYSIS_JD"]["grades_key"] == "jd_grades"
        assert phases["ANALYSIS_LIKE"]["rubric_artifact"] == "like_rubric"

    def test_resolve_tokens_job_source_substitutes_value(self) -> None:
        jc = {"VISIBLE_JD": "Acme JD", "ANALYSIS_JD": "phase text"}
        out = cfg.resolve_tokens(
            "jd={$VISIBLE_JD} analysis={$ANALYSIS_JD}",
            {},
            "contemplate_job",
            job_context=jc,
        )
        assert out == "jd=Acme JD analysis=phase text"

    def test_resolve_tokens_job_empty_logs_warning(self, caplog) -> None:
        caplog.set_level("WARNING")
        out = cfg.resolve_tokens("{$VISIBLE_JD}", {}, "contemplate_job", job_context={})
        assert out == ""
        assert any("VISIBLE_JD" in rec.message and "job_context" in rec.message for rec in caplog.records)

    def test_resume_section_catalog_token_source(self) -> None:
        assert cfg.TOKEN_SOURCES["RESUME_SECTION_CATALOG"] == {"source": "job"}
        assert "RESUME_SECTION_CATALOG" in cfg.get_tokens()


class TestAst530ChainHopResolveTokens:
    def test_chain_entry_empty_caller_no_warning(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level("WARNING")
        cfg.resolve_tokens(
            "{$CALLER_SYSTEM}",
            {},
            "contemplate_job",
            chain_context={},
            chain_entry=True,
        )
        assert not any("mid-chain" in rec.message for rec in caplog.records)

    def test_mid_chain_empty_caller_enhanced_warning(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level("WARNING")
        cfg.resolve_tokens(
            "{$CALLER_SYSTEM}",
            {},
            "contemplate_job",
            chain_context={"CALLER_SYSTEM": ""},
            chain_entry=False,
            parent_task_key="anticipate_scan",
            parent_caller_summary={"CALLER_SYSTEM": "", "CALLER_RESPONSE": "x"},
        )
        msgs = [rec.message for rec in caplog.records]
        assert any("parent=anticipate_scan" in m for m in msgs)
        assert any("parent_caller=" in m and "CALLER_SYSTEM=empty" in m for m in msgs)

    def test_selected_agent_empty_still_warns(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level("WARNING")
        cfg.resolve_tokens(
            "{$SELECTED_AGENT}",
            {},
            "grade_get",
            chain_context={},
            chain_entry=True,
        )
        assert any("(chain_context, task=" in rec.message for rec in caplog.records)


class TestAst480AnalysisUpshotConfig:
    """AST-480 — synthesis dispatch at PASSED_LIKE; scored claim uses score_floor; JSON → RECOMMENDED."""

    def test_task_row_pass_and_error_targets(self) -> None:
        ac = cfg.TASK_CONFIG["analysis_upshot"]
        assert ac["pass_state"] == "RECOMMENDED"
        assert ac["error_state"] == "PASSED_LIKE_RETRY"
        assert ac["scored"] is True
        assert ac["agent_task"] == "analysis_upshot"

    def test_ast561_response_schema_includes_take_jd(self) -> None:
        """AST-561 — JD-phase take mirrors take_do/get/like; required string on synthesis JSON."""
        schema = cfg.TASK_CONFIG["analysis_upshot"]["response_schema"]
        assert schema["take_jd"] == {"type": "str", "required": True}
        keys = list(schema.keys())
        assert keys.index("take_jd") < keys.index("take_get")


class TestAst479LikePassStates:
    """AST-479 — LIKE queues at PASSED_LIKE; Recommended list states are post-upshot."""

    def test_grade_like_pass_state_is_passed_like_not_build_artifacts(self) -> None:
        assert cfg.TASK_CONFIG["grade_like"]["pass_state"] == "PASSED_LIKE"

    def test_recommended_job_states_post_synthesis_exclude_passed_like(self) -> None:
        states = cfg.RECOMMENDED_JOB_STATES
        assert states[0] == "RECOMMENDED"
        assert states[-1] == "CANDIDATE_REVIEW"
        assert "PASSED_LIKE" not in states
        assert all(s.startswith("BUILD_ARTIFACTS.") for s in states[1:-1])


class TestAst309CoverLetterTaskConfig:
    """Draft cover letter response schema (`draft_cover_letter` replaces legacy **`craft_job_*`** — **AST-450**)."""

    def test_draft_cover_letter_response_schema_keys(self) -> None:
        schema = cfg.TASK_CONFIG["draft_cover_letter"]["response_schema"]
        assert schema["re_line"]["required"] is True
        assert schema["body"]["required"] is True
        assert schema["signature"]["required"] is False


class TestAst450ArtifactPipelineTaskKeys:
    """Phase E dumb-chain registry keys (AST-450, AST-520); legacy craft_job_* removed from TASK_CONFIG."""

    KEYS = (
        "contemplate_job",
        "anticipate_scan",
        "advise_job_resume",
        "draft_job_resume",
        "check_job_resume",
        "finalize_job_resume",
        "draft_cover_letter",
        "check_cover_letter",
        "finalize_cover_letter",
        "propose_application_responses",
    )

    def test_ten_keys_in_registry(self) -> None:
        for key in self.KEYS:
            assert key in cfg.TASK_CONFIG
            assert key in cfg.get_task_keys()

    def test_legacy_craft_job_keys_absent(self) -> None:
        for legacy in ("craft_job_resume", "craft_job_cover_letter", "craft_application_responses"):
            assert legacy not in cfg.TASK_CONFIG


class TestAst594DraftJobResumeSchema:
    """AST-594: structure-keyed draft_job_resume hop — no graded-consult contract."""

    def test_draft_job_resume_metadata_only_schema(self) -> None:
        entry = cfg.TASK_CONFIG["draft_job_resume"]
        schema = entry["response_schema"]
        assert "grades" not in schema
        assert "vectors" not in entry
        assert "grading_mode" not in entry
        assert entry.get("context_format") is None
        assert entry.get("resume_section_payload") is True


class TestAst520AnticipateScanTaskKey:
    """AST-520: tenth Phase E key; non-dispatch hop; seq renumber only."""

    def test_anticipate_scan_stub_and_phase_e_seq(self) -> None:
        entry = cfg.TASK_CONFIG["anticipate_scan"]
        assert entry["phase"] == "E. Job Artifacts"
        assert entry["seq"] == 1
        assert entry["print_label"] == "Anticipate Scan"
        assert entry["trigger_state"] is None
        assert cfg.TASK_CONFIG["contemplate_job"]["seq"] == 2
        assert cfg.TASK_CONFIG["advise_job_resume"]["seq"] == 3
        assert cfg.TASK_CONFIG["propose_application_responses"]["seq"] == 10

    def test_build_artifacts_entry_unchanged(self) -> None:
        assert cfg.BUILD_CONFIG["resume_artifact_chain"]["first_task_key"] == "contemplate_job"
        assert "anticipate_scan" not in cfg.DISPATCH_SCHEDULABLE_TASK_KEYS
        assert (
            cfg.dispatch_task_admin_defaults("contemplate_job")["trigger_state"]
            == cfg.resume_artifact_compound_state("contemplate_job")
        )


class TestBuildStateUiManifest:
    def test_manifest_contains_expected_sections(self) -> None:
        manifest = cfg.build_state_ui_manifest()
        assert "jobs" in manifest and "candidate" in manifest and "company" in manifest
        assert manifest["jobs"]["skipped"]["bulk_retry_to_state"] == "NEW"

    def test_ast522_recommended_manifest_sections_and_phase_columns(self) -> None:
        manifest = cfg.build_state_ui_manifest()
        rec = manifest["jobs"]["recommended"]
        assert [row["state"] for row in rec["sections"]] == [
            "RECOMMENDED",
            *cfg.all_resume_artifact_compound_states(),
            "CANDIDATE_REVIEW",
        ]
        assert [col["field"] for col in rec["phase_score_columns"]] == [
            "jd_score",
            "do_score",
            "get_score",
            "like_score",
        ]

    def test_ast562_recommended_primary_actions_by_state(self) -> None:
        manifest = cfg.build_state_ui_manifest()
        actions = manifest["jobs"]["recommended"]["primary_actions_by_state"]
        assert actions["RECOMMENDED"][0]["action_key"] == "generate_artifacts"
        assert actions["RECOMMENDED"][0]["path_suffix"] == "generate_artifacts"
        for cs in cfg.all_resume_artifact_compound_states():
            assert actions[cs][0]["action_key"] == "cancel_build"
            assert actions[cs][0]["path_suffix"] == "cancel_artifact_build"

    def test_ast562_recommended_prior_states_allow_cancel_from_build(self) -> None:
        priors = cfg.JOB_STATES["RECOMMENDED"]["prior_states"]
        for cs in cfg.all_resume_artifact_compound_states():
            assert cs in priors

    def test_ast565_recommended_report_manifest_tabs(self) -> None:
        manifest = cfg.build_state_ui_manifest()
        rec = manifest["jobs"]["recommended"]
        assert [t["tab_id"] for t in rec["report_fixed_tabs"]] == ["summary", "jd_full"]
        assert len(rec["report_phase_tabs"]) == 4
        assert rec["report_phase_tabs"][0]["take_key"] == "take_jd"
        assert len(rec["report_artifact_tabs"]) == 3
        assert rec["primary_actions_by_state"]["CANDIDATE_REVIEW"][0]["action_key"] == "apply"


class TestSchemaToExample:
    def test_covers_schema_type_branches(self) -> None:
        schema = {
            "status": {"type": "str", "enum": ["ok", "no"]},
            "count": {"type": "int"},
            "flag": {"type": "bool"},
            "items": {"type": "list", "items_schema": {"name": {"type": "str"}}},
            "plain_list": {"type": "list"},
            "obj": {"type": "object"},
            "bag": {"type": "dict"},
            "other": {"type": "custom"},
        }
        example = cfg._schema_to_example(schema)
        assert example["status"] == "ok | no"
        assert example["count"] == 0
        assert example["flag"] is True
        assert example["items"] == [{"name": "<name>"}]
        assert example["plain_list"] == ["<plain_list item>"]
        assert example["obj"] == {"<key>": "<value>"}
        assert example["other"] == "<other>"


class TestImportanceMultiplierEdges:
    def test_raises_when_multiplier_missing(self, monkeypatch) -> None:
        ci = dict(cfg.ASTRAL_CONFIG["consult_importance"])
        ci["multipliers"] = {}
        monkeypatch.setitem(cfg.ASTRAL_CONFIG, "consult_importance", ci)
        with pytest.raises(ValueError, match="No multiplier configured"):
            cfg.importance_multiplier(5)


# Branches: AST-415 adopted board registry (list_adopted_boards / get_board_entry).
class TestAdoptedBoardHelpers:
    def test_list_skips_non_adopted_get_returns_copy(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(cfg, "BOARD_CONFIG", {
            "skip_me": {"adopted": False},
            "keep_me": {
                "adopted": True,
                "label": "L",
                "entry_url": "https://e",
                "scrape_mode": "sm",
                "craft_task_key": "craft_x",
                "extra": 1,
            },
        })
        rows = cfg.list_adopted_boards()
        assert rows == [{
            "board_key": "keep_me",
            "label": "L",
            "entry_url": "https://e",
            "scrape_mode": "sm",
            "craft_task_key": "craft_x",
        }]
        got = cfg.get_board_entry("keep_me")
        assert got is not None and got.pop("extra") == 1
        assert cfg.get_board_entry("missing") is None
        assert cfg.get_board_entry("skip_me") is None


# Dispatch admin defaults ↔ scored-step helpers (AST-379 / AST-468; AST-549 config-only).
class TestAst471DispatchConfigHelpers:
    def test_gaze_board_boards_config_scan_interval_hours(self) -> None:
        # Mirrors WATCH gaze cadence; dispatcher + count_eligible read this when freq_hrs is 0 (AST-482).
        gb = cfg.BOARDS_CONFIG.get("gaze_board") or {}
        assert gb.get("scan_interval_hours") == 24

    def test_resolve_maps_consult_to_grade_trimmed(self) -> None:
        assert cfg.resolve_dispatch_task_config_key("consult_do") == "grade_do"
        assert cfg.resolve_dispatch_task_config_key("  consult_like  ") == "grade_like"
        assert cfg.resolve_dispatch_task_config_key("gaze_board") == "gaze_board"

    def test_scored_grade_dispatch_not_board_gaze(self) -> None:
        assert cfg.dispatch_task_key_is_scored("consult_get") is True
        assert cfg.dispatch_task_key_is_scored("gaze_board") is False

    def test_dispatch_schedulable_keys_includes_board_gazer(self) -> None:
        assert "gaze_board" in cfg.DISPATCH_SCHEDULABLE_TASK_KEYS
        assert "analysis_upshot" in cfg.DISPATCH_SCHEDULABLE_TASK_KEYS

    def test_ast485_roster_dispatch_trio_matches_config_defaults(self) -> None:
        assert "locate_job_page" not in cfg.DISPATCH_SCHEDULABLE_TASK_KEYS
        trio = ("find_job_page", "select_job_page", "parse_job_list")
        for k in trio:
            assert k in cfg.DISPATCH_SCHEDULABLE_TASK_KEYS
            d = cfg.dispatch_task_admin_defaults(k)
            assert d["trigger_state"] == "TO_WATCH"
            assert d["entity_type"] == "company"

    def test_passed_like_trigger_attachs_analysis_upshot_scored(self) -> None:
        assert cfg.dispatch_task_admin_defaults("analysis_upshot")["trigger_state"] == "PASSED_LIKE"
        assert cfg.dispatch_task_key_is_scored("analysis_upshot") is True
        assert cfg.trigger_state_used_by_scored_dispatch_task("PASSED_LIKE") is True

    def test_active_trigger_not_scored_dispatch_row(self) -> None:
        # ACTIVE is gaze_board hook — not TASK_CONFIG graded multi-hop.
        assert cfg.trigger_state_used_by_scored_dispatch_task("ACTIVE") is False

    def test_trigger_state_guard_none_blank_whitespace_retry(self) -> None:
        # Early returns before seed / transition scan (branch coverage on trigger_state).
        assert cfg.trigger_state_used_by_scored_dispatch_task(None) is False
        assert cfg.trigger_state_used_by_scored_dispatch_task("") is False
        assert cfg.trigger_state_used_by_scored_dispatch_task("   ") is False
        assert cfg.trigger_state_used_by_scored_dispatch_task("PASSED_LIKE_RETRY") is False

    def test_transition_strings_skips_blank_and_nonstr(self) -> None:
        from src.utils.config import _task_config_transition_strings

        got = _task_config_transition_strings({
            "pass_state": "  OK  ",
            "fail_state": " \t ",
            "error_state": "",
            "not_ready_state": 99,
            "error_states": (" BAD ", "", None, 42, {}, " KEEP "),
        })
        assert got == frozenset({"OK", "BAD", "KEEP"})


class TestAst549DispatchAdminDefaults:
    """AST-549: config-built dispatch_task admin defaults; no parallel seed dicts."""

    def test_unknown_task_key_raises(self) -> None:
        with pytest.raises(KeyError, match="not schedulable"):
            cfg.dispatch_task_admin_defaults("anticipate_scan")

    def test_qualify_job_listings_batch_call_mode_and_sort(self) -> None:
        d = cfg.dispatch_task_admin_defaults("qualify_job_listings")
        assert d["entity_type"] == "job"
        assert d["trigger_state"] == "VALID_TITLE"
        assert d["sort_by"] == "updated_at"
        assert d["batch_call_mode"] == 1

    def test_contemplate_job_artifact_trigger_sort(self) -> None:
        d = cfg.dispatch_task_admin_defaults("contemplate_job")
        assert d["trigger_state"] == cfg.resume_artifact_compound_state("contemplate_job")
        assert d["sort_by"] == "state_changed_at"


class TestAst595CompoundBuildArtifactsHopStates:
    """AST-595: compound BUILD_ARTIFACTS.<task_key> registry and dispatch trigger alignment."""

    HOPS = (
        "anticipate_scan",
        "contemplate_job",
        "advise_job_resume",
        "draft_job_resume",
        "check_job_resume",
        "finalize_job_resume",
    )

    def test_flat_build_artifacts_removed_from_job_states(self) -> None:
        assert "BUILD_ARTIFACTS" not in cfg.JOB_STATES

    def test_compound_states_registered_with_prior_chain(self) -> None:
        for i, tk in enumerate(self.HOPS):
            cs = cfg.resume_artifact_compound_state(tk)
            entry = cfg.JOB_STATES[cs]
            if i == 0:
                assert entry["prior_states"] == ["RECOMMENDED"]
            else:
                prev = cfg.resume_artifact_compound_state(self.HOPS[i - 1])
                assert entry["prior_states"] == [prev]

    def test_recommended_job_states_includes_all_compound_hops(self) -> None:
        assert cfg.RECOMMENDED_JOB_STATES == [
            "RECOMMENDED",
            *cfg.all_resume_artifact_compound_states(),
            "CANDIDATE_REVIEW",
        ]

    def test_resume_artifact_helpers(self) -> None:
        first = cfg.resume_artifact_first_compound_state()
        assert first == cfg.resume_artifact_compound_state("anticipate_scan")
        assert cfg.parse_resume_artifact_hop(first) == "anticipate_scan"
        assert cfg.is_resume_artifact_in_progress(first) is True
        assert cfg.is_resume_artifact_in_progress("RECOMMENDED") is False
        assert (
            cfg.resume_artifact_next_compound_state("anticipate_scan")
            == cfg.resume_artifact_compound_state("contemplate_job")
        )
        assert cfg.resume_artifact_next_compound_state("finalize_job_resume") is None

    def test_dispatch_trigger_state_per_resume_hop(self) -> None:
        from src.utils.config import _dispatch_trigger_state_for_task_key

        for tk in self.HOPS:
            assert _dispatch_trigger_state_for_task_key(tk) == cfg.resume_artifact_compound_state(tk)

    def test_build_failed_prior_states_are_compound_only(self) -> None:
        assert cfg.JOB_STATES["BUILD_FAILED"]["prior_states"] == list(
            cfg.all_resume_artifact_compound_states()
        )


# AST-586 — dispatch claim score_floor vs task grading metadata (parent AST-547).
class TestAst586DispatchClaimScoreFloor:
    def test_valid_title_input_trigger_not_claim_scored(self) -> None:
        assert cfg.dispatch_claim_uses_score_floor("VALID_TITLE") is False
        assert cfg.dispatch_claim_uses_score_floor("VALID_TITLE_RETRY") is False

    def test_post_score_outcome_triggers_claim_scored(self) -> None:
        assert cfg.dispatch_claim_uses_score_floor("PASSED_JD") is True
        assert cfg.dispatch_claim_uses_score_floor("PASSED_JOBLIST") is True

    def test_guard_none_blank(self) -> None:
        assert cfg.dispatch_claim_uses_score_floor(None) is False
        assert cfg.dispatch_claim_uses_score_floor("") is False

    def test_legacy_helper_may_still_classify_valid_title_graded(self) -> None:
        # Claim helper diverges from grading metadata (AST-586); legacy helper unchanged.
        assert cfg.trigger_state_used_by_scored_dispatch_task("VALID_TITLE") is True


# AST-641 — primary + companion *_RETRY union for dispatch claim/count (parent AST-630).
class TestAst641DispatchClaimStates:
    def test_primary_job_includes_companion_retry(self) -> None:
        assert cfg.dispatch_claim_states("VALID_TITLE", "job") == ["VALID_TITLE", "VALID_TITLE_RETRY"]
        assert cfg.dispatch_claim_states("JD_READY", "job") == ["JD_READY", "JD_READY_RETRY"]

    def test_retry_only_job_single_state(self) -> None:
        assert cfg.dispatch_claim_states("VALID_TITLE_RETRY", "job") == ["VALID_TITLE_RETRY"]

    def test_primary_company_includes_companion_retry(self) -> None:
        assert cfg.dispatch_claim_states("WEBSITE_FOUND", "company") == [
            "WEBSITE_FOUND",
            "WEBSITE_FOUND_RETRY",
        ]

    def test_state_without_registry_companion_stays_single(self) -> None:
        assert cfg.dispatch_claim_states("NEW", "job") == ["NEW"]
        assert cfg.dispatch_claim_states("NEW", "company") == ["NEW"]

    def test_guard_none_blank(self) -> None:
        assert cfg.dispatch_claim_states(None, "job") == []
        assert cfg.dispatch_claim_states("", "company") == []


# LLM_PROVIDER_CONFIG brain tiers, Anthropic / DeepSeek tier maps, startup env parity (AST-492).
class TestAst492LlmBrainTierConfig:
    def test_resolve_anthropic_tier_maps_to_agent_config_keys(self) -> None:
        assert cfg.resolve_brain_setting_to_anthropic_agent_key(cfg.BRAIN_LITTLE) == "claude-haiku-4-5"
        assert cfg.resolve_brain_setting_to_anthropic_agent_key(cfg.BRAIN_MEDIUM) == "claude-sonnet-4-6"
        assert cfg.resolve_brain_setting_to_anthropic_agent_key(cfg.BRAIN_BIG) == "claude-opus-4-6"
        for tier in (cfg.BRAIN_LITTLE, cfg.BRAIN_MEDIUM, cfg.BRAIN_BIG):
            cfg.get_model(cfg.resolve_brain_setting_to_anthropic_agent_key(tier))

    def test_validate_allowed_brain_setting_rejects_unknown(self) -> None:
        with pytest.raises(ValueError, match="Invalid brain_setting"):
            cfg.validate_allowed_brain_setting("Small")

    def test_resolve_deepseek_tier_meta(self) -> None:
        little = cfg.resolve_brain_setting_to_deepseek_tier_meta(cfg.BRAIN_LITTLE)
        assert little["vendor_model"] == "deepseek-v4-flash"
        assert little["thinking"] is False
        medium = cfg.resolve_brain_setting_to_deepseek_tier_meta(cfg.BRAIN_MEDIUM)
        assert medium["vendor_model"] == "deepseek-v4-pro"
        assert medium["thinking"] is False
        big = cfg.resolve_brain_setting_to_deepseek_tier_meta(cfg.BRAIN_BIG)
        assert big["vendor_model"] == "deepseek-v4-pro"
        assert big["thinking"] is True

    def test_infer_brain_setting_from_legacy_model_code(self) -> None:
        assert cfg.infer_brain_setting_from_legacy_model_code("claude-haiku-4-5") == cfg.BRAIN_LITTLE
        assert cfg.infer_brain_setting_from_legacy_model_code("claude-sonnet-4-6") == cfg.BRAIN_MEDIUM
        assert cfg.infer_brain_setting_from_legacy_model_code("claude-opus-4-6") == cfg.BRAIN_BIG
        assert cfg.infer_brain_setting_from_legacy_model_code(None) == cfg.BRAIN_MEDIUM
        assert cfg.infer_brain_setting_from_legacy_model_code("") == cfg.BRAIN_MEDIUM
        assert cfg.infer_brain_setting_from_legacy_model_code("unknown-legacy-x") == cfg.BRAIN_MEDIUM

    def test_get_active_llm_provider_strips_and_rejects_invalid(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(cfg.LLM_PROVIDER_CONFIG, "active_provider", " deepseek ")
        assert cfg.get_active_llm_provider() == "deepseek"
        monkeypatch.setitem(cfg.LLM_PROVIDER_CONFIG, "active_provider", "   ")
        with pytest.raises(ValueError, match="invalid"):
            cfg.get_active_llm_provider()
        monkeypatch.setitem(cfg.LLM_PROVIDER_CONFIG, "active_provider", 999)  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="invalid"):
            cfg.get_active_llm_provider()

    def test_resolve_anthropic_raises_when_tier_maps_to_unknown_agent_config_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(cfg.LLM_PROVIDER_CONFIG["tier_map"]["anthropic"], cfg.BRAIN_MEDIUM, {"agent_config_key": "__not_in_agent_config__"})
        with pytest.raises(ValueError, match="No Anthropic tier mapping"):
            cfg.resolve_brain_setting_to_anthropic_agent_key(cfg.BRAIN_MEDIUM)

    def test_resolve_deepseek_raises_when_mapping_has_no_vendor_model(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(cfg.LLM_PROVIDER_CONFIG["tier_map"]["deepseek"], cfg.BRAIN_LITTLE, {"thinking": False})
        with pytest.raises(ValueError, match="No DeepSeek tier mapping"):
            cfg.resolve_brain_setting_to_deepseek_tier_meta(cfg.BRAIN_LITTLE)

    def test_validate_llm_provider_environment_unknown_active_provider(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(cfg.LLM_PROVIDER_CONFIG, "active_provider", "other-vendor")
        with pytest.raises(ValueError, match="Unknown LLM active_provider"):
            cfg.validate_llm_provider_environment()

    def test_brain_setting_for_anthropic_agent_key_inverse(self) -> None:
        assert cfg.brain_setting_for_anthropic_agent_key("claude-haiku-4-5") == cfg.BRAIN_LITTLE
        assert cfg.brain_setting_for_anthropic_agent_key("__no_such_alias__") is None

    def test_manage_agents_catalog_shape_via_resolve_matches_three_tiers(self) -> None:
        # Mirrors GET /agents/brain_settings payload using Ada-named tier resolution only.
        rows: list[dict] = []
        for tier in cfg.BRAIN_SETTINGS:
            mk = cfg.resolve_brain_setting_to_anthropic_agent_key(tier)
            m = cfg.get_model(mk)
            rows.append(
                {
                    "brain_setting": tier,
                    "label": tier,
                    "default_temperature": m["default_temperature"],
                    "default_max_tokens": m["default_max_tokens"],
                }
            )
        assert [r["brain_setting"] for r in rows] == list(cfg.BRAIN_SETTINGS)

    def test_validate_llm_provider_environment_deepseek_requires_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(cfg.LLM_PROVIDER_CONFIG, "active_provider", "deepseek")
        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        with pytest.raises(KeyError):
            cfg.validate_llm_provider_environment()
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-ds")
        cfg.validate_llm_provider_environment()
        monkeypatch.setitem(cfg.LLM_PROVIDER_CONFIG, "active_provider", "anthropic")

    def test_validate_llm_provider_environment_anthropic_requires_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(cfg.LLM_PROVIDER_CONFIG, "active_provider", "anthropic")
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        with pytest.raises(KeyError):
            cfg.validate_llm_provider_environment()
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-ant")
        cfg.validate_llm_provider_environment()


class TestAst702PrefilterBatchConfig:
    """AST-702: HOMEPAGE_READY prefilter dispatch + batch_call_mode."""

    def test_prefilter_input_state_and_retry_on_homepage_ready(self) -> None:
        pf = cfg.ROSTER_CONFIG["prefilter"]
        assert pf["input_state"] == "HOMEPAGE_READY"
        assert cfg.COMPANY_STATES["HOMEPAGE_READY"]["retry_state"] == "WEBSITE_FOUND_RETRY"

    def test_homepage_ready_evaluate_transitions(self) -> None:
        transitions = cfg.ASTRAL_CONFIG["company_state_transitions"]
        assert ("HOMEPAGE_READY", "PREFILTER_PASSED") in transitions
        assert ("HOMEPAGE_READY", "WEBSITE_FOUND_RETRY") in transitions
        assert ("HOMEPAGE_READY", "CANNOT_READ_WEBSITE") in transitions

    def test_prefilter_dispatch_batch_mode_and_defaults(self) -> None:
        from src.utils.config import _dispatch_batch_call_mode_for

        assert _dispatch_batch_call_mode_for("prefilter") == 1
        d = cfg.dispatch_task_admin_defaults("prefilter")
        assert d["trigger_state"] == "HOMEPAGE_READY"
        assert d["batch_call_mode"] == 1
        assert d["entity_type"] == "company"


class TestAst707EmbeddedPrefilterConfig:
    """AST-707: embedded RC criterion for company_prefilter hydration."""

    def test_embedded_rc_registry(self) -> None:
        rows = cfg.EMBEDDED_COMPANY_PREFILTER_CRITERIA
        assert len(rows) == 1
        rc = rows[0]
        assert rc["code"] == "RC"
        assert rc["label"] == "Reality Check"
        assert rc["importance"] == 8
        grades = {g["grade"] for g in rc["grade_descriptions"]}
        assert grades == {"A", "B", "C", "D", "E", "F"}


class TestAst701FetchWebsiteConfig:
    """AST-701: HOMEPAGE_READY state, fetch_website gazer batch + dispatch registry."""

    def test_homepage_ready_state_and_transitions(self) -> None:
        assert "HOMEPAGE_READY" in cfg.COMPANY_STATES
        transitions = cfg.ASTRAL_CONFIG["company_state_transitions"]
        assert ("WEBSITE_FOUND", "HOMEPAGE_READY") in transitions
        assert ("WEBSITE_FOUND", "CANNOT_READ_WEBSITE") in transitions
        assert ("WEBSITE_FOUND_RETRY", "HOMEPAGE_READY") in transitions
        assert ("WEBSITE_FOUND_RETRY", "CANNOT_READ_WEBSITE") in transitions

    def test_gazer_fetch_website_config(self) -> None:
        entry = cfg.GAZER_CONFIG["fetch_website"]
        assert entry["pass_state"] == "HOMEPAGE_READY"
        assert entry["fail_state"] == "CANNOT_READ_WEBSITE"
        assert entry["fallback_batch_size"] == 10

    def test_dispatch_registry_and_homepage_text_key(self) -> None:
        from src.utils.config import _dispatch_trigger_state_for_task_key

        assert "fetch_website" in cfg.DISPATCH_SCHEDULABLE_TASK_KEYS
        assert _dispatch_trigger_state_for_task_key("fetch_website") == "WEBSITE_FOUND"
        assert cfg.ROSTER_CONFIG["company_data_keys"]["homepage_text"] == "homepage_text"
        defaults = cfg.dispatch_task_admin_defaults("fetch_website")
        assert defaults["trigger_state"] == "WEBSITE_FOUND"
        assert defaults["entity_type"] == "company"


class TestAst507EncodedPrefilterConfig:
    """AST-507: PREFILTER_PASSED/FAILED states, transitions, grades_encoded prefilter task."""

    def test_company_states_and_transitions(self) -> None:
        assert "PREFILTER_PASSED" in cfg.COMPANY_STATES
        assert "PREFILTER_FAILED" in cfg.COMPANY_STATES
        assert "WEBSITE_FOUND_RETRY" in cfg.COMPANY_STATES
        assert cfg.ROSTER_CONFIG["prefilter"]["retry_state"] == "WEBSITE_FOUND_RETRY"
        transitions = cfg.ASTRAL_CONFIG["company_state_transitions"]
        assert ("WEBSITE_FOUND", "PREFILTER_PASSED") in transitions
        assert ("WEBSITE_FOUND", "PREFILTER_FAILED") in transitions
        assert ("WEBSITE_FOUND", "WEBSITE_FOUND_RETRY") in transitions
        assert ("WEBSITE_FOUND", "ERROR_PREFILTER") in transitions

    def test_prefilter_company_grades_encoded(self) -> None:
        entry = cfg.TASK_CONFIG["prefilter_company"]
        assert entry["output_type"] == "grades_encoded_prefilter_links"
        assert entry["pass_state"] == "PREFILTER_PASSED"
        assert entry["fail_state"] == "PREFILTER_FAILED"
        assert cfg.ROSTER_CONFIG["prefilter"]["pass_states"] == ["PREFILTER_PASSED", "TO_WATCH"]
        assert "grades_encoded_prefilter_links" in cfg.ASTRAL_CONFIG["output_types"]


class TestAst504CompanySearchTermsConfig:
    """AST-504: craft_company_search_terms task + COMPANY_SEARCH_TERMS token (Roster inflow Phase 0)."""

    def test_craft_company_search_terms_in_task_config(self) -> None:
        entry = cfg.TASK_CONFIG["craft_company_search_terms"]
        assert entry["phase"] == "B. Candidate Artifacts"
        assert entry["seq"] == 8
        assert entry["response_schema"]["search_terms"]["type"] == "str"
        assert entry["requires_candidate_key"] is True
        assert entry["entity_type"] is None

    def test_company_search_terms_token_source(self) -> None:
        assert cfg.TOKEN_SOURCES["COMPANY_SEARCH_TERMS"] == {
            "source": "candidate",
            "path": "artifacts.company_search_terms",
        }


class TestAst525InflowDiscoveryConfig:
    """AST-525: per-term scan interval for inflow_discovery cadence."""

    def test_scan_interval_hours_literal(self) -> None:
        assert cfg.INFLOW_CONFIG["discovery"]["scan_interval_hours"] == 168


class TestAst505InflowDiscoveryConfig:
    """AST-505: Phase 1 CSE discovery, vet task, NEW company state, inflow_discovery dispatch seed."""

    def test_inflow_config_discovery_literals(self) -> None:
        d = cfg.INFLOW_CONFIG["discovery"]
        assert d["max_results_per_query"] == 100
        assert d["date_restrict_days"] == 7
        assert d["dispatch_freq_hrs"] == 168
        assert d["dispatch_trigger_state"] == "LIVE_PROMPTS"
        assert d["task_key"] == "inflow_discovery"
        assert d["vet_task_key"] == "vet_inflow_discovery"

    def test_vet_inflow_discovery_task(self) -> None:
        entry = cfg.TASK_CONFIG["vet_inflow_discovery"]
        assert entry["phase"] == "C. Company Roster"
        assert entry["entity_type"] == "candidate"
        assert entry["requires_candidate_key"] is True
        items = entry["response_schema"]["results"]["items_schema"]
        assert items["action"]["type"] == "str"

    def test_new_company_state_and_transitions(self) -> None:
        assert "NEW" in cfg.COMPANY_STATES
        transitions = cfg.ASTRAL_CONFIG["company_state_transitions"]
        assert ("NEW", "WEBSITE_FOUND") in transitions
        assert ("NEW", "NO_WEBSITE") in transitions

    def test_inflow_discovery_dispatch_admin_defaults(self) -> None:
        d = cfg.dispatch_task_admin_defaults("inflow_discovery")
        assert d["entity_type"] == "candidate"
        assert d["trigger_state"] == "LIVE_PROMPTS"
        assert "inflow_discovery" in cfg.DISPATCH_SCHEDULABLE_TASK_KEYS


class TestAst506InflowResolveConfig:
    """AST-506: Phase 2 website resolution, empty-website claim filter, inflow_resolve_website dispatch."""

    def test_inflow_config_resolve_literals(self) -> None:
        r = cfg.INFLOW_CONFIG["resolve"]
        assert r["max_results"] == 20
        assert r["date_restrict_days"] is None
        assert r["dispatch_trigger_state"] == "NEW"
        assert r["task_key"] == "inflow_resolve_website"
        assert r["ai_task_key"] == "find_company_website"

    def test_inflow_resolve_website_dispatch_admin_defaults(self) -> None:
        d = cfg.dispatch_task_admin_defaults("inflow_resolve_website")
        assert d["entity_type"] == "company"
        assert d["trigger_state"] == "NEW"
        assert d["batch_call_mode"] == 0
        assert "inflow_resolve_website" in cfg.DISPATCH_SCHEDULABLE_TASK_KEYS


class TestAst508InflowLocateConfig:
    """AST-508: PREFILTER_PASSED locate dispatch input states and inflow score key."""

    def test_inflow_config_locate_literals(self) -> None:
        loc = cfg.INFLOW_CONFIG["locate"]
        assert loc["dispatch_trigger_state"] == "PREFILTER_PASSED"
        assert loc["score_json_path"] == "prefilter_score"

    def test_locate_dispatch_input_states_include_prefilter_passed(self) -> None:
        states = cfg.ROSTER_CONFIG["locate_job_page"]["dispatch_input_states"]
        assert "PREFILTER_PASSED" in states
        assert "TO_WATCH" in states
        assert "JOBS_FOUND" in states

    def test_prefilter_score_company_data_key(self) -> None:
        assert cfg.ROSTER_CONFIG["company_data_keys"]["prefilter_score"] == "prefilter_score"

    def test_prefilter_passed_locate_transitions(self) -> None:
        transitions = cfg.ASTRAL_CONFIG["company_state_transitions"]
        assert ("PREFILTER_PASSED", "WATCH") in transitions
        assert ("PREFILTER_PASSED", "NO_OPENINGS") in transitions


# Branches: registry; five-form resolution; default/invalid preference; FIRST_NAME unchanged.
class TestAst575PronounTokens:
    """AST-575: pronoun preference + five prompt tokens (parent AST-573)."""

    _NAMES = ("THEY", "THEIR", "THEIRS", "THEM", "THEMSELF")

    def test_get_tokens_includes_five_pronoun_names(self) -> None:
        tokens = cfg.get_tokens()
        for name in self._NAMES:
            assert name in tokens
            assert cfg.TOKEN_SOURCES[name] == {"source": "pronoun"}

    def test_resolve_all_five_tokens_she_her(self) -> None:
        candidate = {"profile": {"pronoun_preference": "she/her"}}
        text = "{$THEY} {$THEIR} {$THEIRS} {$THEM} {$THEMSELF}"
        out = cfg.resolve_tokens(text, candidate, "draft_cover_letter")
        assert out == "she her hers her herself"

    def test_resolve_default_when_preference_missing(self) -> None:
        text = "{$THEY} {$THEIR} {$THEIRS} {$THEM} {$THEMSELF}"
        for candidate in ({}, {"profile": {}}):
            out = cfg.resolve_tokens(text, candidate, "draft_cover_letter")
            assert out == "they their theirs them themselves"

    def test_resolve_default_when_preference_invalid(self) -> None:
        candidate = {"profile": {"pronoun_preference": "custom/xyz"}}
        out = cfg.resolve_tokens("{$THEY}", candidate, "draft_cover_letter")
        assert out == "they"

    @pytest.mark.parametrize(
        ("preference", "expected_they"),
        [
            ("he/him", "he"),
            ("ze/zir", "ze"),
            ("e/eir", "e"),
        ],
    )
    def test_resolve_preference_subject_form(self, preference: str, expected_they: str) -> None:
        candidate = {"profile": {"pronoun_preference": preference}}
        assert cfg.resolve_tokens("{$THEY}", candidate, "draft_cover_letter") == expected_they

    def test_first_name_unchanged_with_pronoun_set(self) -> None:
        candidate = {
            "profile": {"first": "Ada", "pronoun_preference": "she/her"},
        }
        out = cfg.resolve_tokens("Hi {$FIRST_NAME}, {$THEY}", candidate, "draft_cover_letter")
        assert out == "Hi Ada, she"


@pytest.mark.skip(reason="AST-510 canceled — middle name not in DATA_SHAPES on integration branches")
class TestAst510MiddleNameConfig:
    """AST-510: profile.middle DATA_SHAPES field + MIDDLE_NAME token."""

    def test_middle_name_in_candidate_profile_shapes(self) -> None:
        sections = cfg.DATA_SHAPES["candidates"]["detail"]["profile"]
        contact = next(s for s in sections if s["label"] == "Contact Information")
        keys = [f["key"] for f in contact["fields"]]
        assert keys.index("profile.middle") == keys.index("profile.first") + 1
        assert keys.index("profile.last") == keys.index("profile.middle") + 1

    def test_middle_name_token_source(self) -> None:
        assert cfg.TOKEN_SOURCES["MIDDLE_NAME"] == {"source": "candidate", "path": "profile.middle"}


class TestAst517ResumeStructureConfig:
    """AST-517: per-candidate resume_structure defaults and craft_resume_base schema."""

    def test_default_catalog_covers_known_section_ids(self) -> None:
        sections = cfg.RESUME_STRUCTURE_DEFAULT["sections"]
        assert set(sections) == set(cfg.RESUME_STRUCTURE_KNOWN_SECTION_IDS)

    def test_contact_sections_not_job_agent_editable(self) -> None:
        sections = cfg.RESUME_STRUCTURE_DEFAULT["sections"]
        for sid in cfg.RESUME_STRUCTURE_CONTACT_SECTION_IDS:
            assert sections[sid]["job_agent_editable"] is False

    def test_craft_resume_base_schema_lists_resume_structure_first(self) -> None:
        schema = cfg.TASK_CONFIG["craft_resume_base"]["response_schema"]
        keys = list(schema.keys())
        assert keys[0] == "resume_structure"
        assert schema["resume_structure"]["required"] is True


class TestAst676CraftRubricSchema:
    """AST-676: craft_prefilter_rubric rename + shared importance criterion schema."""

    _IMPORTANCE_SPEC = {"type": "int", "required": True, "min": 1, "max": 10}
    _RUBRIC_TASK_KEYS = (
        "craft_prefilter_rubric",
        "craft_joblist_rubric",
        "craft_jobdesc_rubric",
        "craft_get_rubric",
        "craft_do_rubric",
        "craft_like_rubric",
    )

    def test_prefilter_task_key_renamed(self) -> None:
        assert "craft_prefilter_rubric" in cfg.TASK_CONFIG
        assert "craft_company_prefilter" not in cfg.TASK_CONFIG

    def test_all_six_rubric_tasks_share_importance_schema(self) -> None:
        for task_key in self._RUBRIC_TASK_KEYS:
            items = cfg.TASK_CONFIG[task_key]["response_schema"]["criteria"]["items_schema"]
            assert items["importance"] == self._IMPORTANCE_SPEC

