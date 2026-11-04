import pytest
import json

import pytchbuild.tutorialcompiler.fromgitrepo.tutorial_history as TH
import pytchbuild.tutorialcompiler.fromgitrepo.errors as TCE


@pytest.fixture
def history_with(fresh_project_history):
    """
    Function which overwrites the "metadata_text" (from the given
    dict) and optionally the "summary_text" of a fresh ProjectHistory,
    and returns that ProjectHistory.
    """
    def make(metadata, summary_text="# Summary title\n\nHello.\n"):
        history = fresh_project_history
        history.metadata_text = json.dumps(metadata)
        history.summary_text = summary_text
        return history
    return make


class TestSummaryDisplayName:
    def test_from_repo(self, project_history):
        TTS = TH.ProjectHistory.TutorialTextSource
        exp_name = (
            "Summary for Boing"
            if project_history.tutorial_text_source == TTS.TIP_REVISION
            else "Working summary for Boing"
        )
        assert project_history.summary_display_name == exp_name

    def test_inline_markup(self, history_with):
        history = history_with({}, "# Boing — a *Pong-like* `game`\n")
        assert history.summary_display_name == "Boing — a Pong-like game"

    @pytest.mark.parametrize(
        "summary_text, exp_match",
        [
            ("Hello.\n", "summary has 0 <h1> elements"),
            ("# One\n\n# Two\n", "summary has 2 <h1> elements"),
            ("#\n\nHello.\n", "summary has empty <h1>"),
        ],
    )
    def test_bad_h1(self, history_with, summary_text, exp_match):
        history = history_with({}, summary_text)
        with pytest.raises(TCE.TutorialStructureError, match=exp_match):
            history.summary_display_name


class TestCompletedMetadata:
    def test_defaults(self, history_with):
        history = history_with({"difficulty": "medium"})
        assert history.completed_metadata == {
            "programKind": "flat",
            "difficulty": "medium",
            "language": "en",
            "tutorialId": "boing",
            "displayName": "Summary title",
        }

    def test_explicit_values(self, history_with):
        history = history_with({
            "programKind": "per-method",
            "difficulty": "getting-started",
            "language": "ga",
            "tutorialId": "boing-original",
        })
        assert history.completed_metadata == {
            "programKind": "per-method",
            "difficulty": "getting-started",
            "language": "ga",
            "tutorialId": "boing-original",
            "displayName": "Summary title",
        }

    def test_build_only_slots_kept(self, history_with):
        grouped_assets = [{"name": "rects", "assets": ["a.png"]}]
        history = history_with({
            "difficulty": "advanced",
            "groupedProjectAssets": grouped_assets,
            "orderedProjectAssets": ["a.png"],
            "intentionallyUnusedAssets": [],
        })
        completed = history.completed_metadata
        assert completed["groupedProjectAssets"] == grouped_assets
        assert completed["orderedProjectAssets"] == ["a.png"]
        assert completed["intentionallyUnusedAssets"] == []

    @pytest.mark.parametrize(
        "metadata, exp_match",
        [
            ({}, 'no "difficulty"'),
            ({"difficulty": "easy"}, '"difficulty" is "easy"'),
            (
                {"difficulty": "getting started"},
                '"difficulty" is "getting started"',
            ),
            ({"difficulty": "medium", "language": "fr"}, '"language" is "fr"'),
            (
                {"difficulty": "medium", "programKind": "jr"},
                '"programKind" is "jr"',
            ),
            (
                {"difficulty": "medium", "displayName": "Boing"},
                'must not contain "displayName"',
            ),
            (
                {"difficulty": "medium", "tutorialId": ""},
                '"tutorialId" must be a non-empty string',
            ),
            (
                {"difficulty": "medium", "tutorialId": 42},
                '"tutorialId" must be a non-empty string',
            ),
        ],
    )
    def test_invalid(self, history_with, metadata, exp_match):
        history = history_with(metadata)
        with pytest.raises(TCE.TutorialStructureError, match=exp_match):
            history.completed_metadata


class TestEmittedMetadata:
    def test_allow_list(self, history_with):
        history = history_with({
            "difficulty": "advanced",
            "language": "de",
            "groupedProjectAssets": [],
            "orderedProjectAssets": [],
            "intentionallyUnusedAssets": [],
        })
        assert history.emitted_metadata == {
            "programKind": "flat",
            "difficulty": "advanced",
            "language": "de",
            "tutorialId": "boing",
            "displayName": "Summary title",
        }
        assert list(history.emitted_metadata.keys()) == TH.EMITTED_METADATA_SLOTS
