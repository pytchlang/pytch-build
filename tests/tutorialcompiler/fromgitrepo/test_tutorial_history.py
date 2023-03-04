import pytest
import re
import logging
import io
import json

import pygit2
from PIL import Image
import pytchbuild.tutorialcompiler.fromgitrepo.tutorial_history as TH
import pytchbuild.tutorialcompiler.fromgitrepo.errors as TCE


def _assert_data_content(exp_content):
    def do_assert(got_data):
        assert got_data == exp_content
    return do_assert


def _assert_data_length(exp_length):
    def do_assert(got_data):
        assert len(got_data) == exp_length
    return do_assert


class TestAsset:
    def test_str(self):
        fname = "alien.png"
        data = b"not-a-real-PNG-file"
        pa = TH.Asset(fname, data)
        assert str(pa) == '<Asset "alien.png": 19 bytes>'

    def _test_from_delta(self, repo, oid, exp_path, assert_data):
        commit_adding_file = repo[oid]
        parent_commit = repo[commit_adding_file.parent_ids[0]]
        diff = repo.diff(a=parent_commit.tree, b=commit_adding_file.tree)
        deltas = list(diff.deltas)
        assert len(deltas) == 1
        delta = deltas[0]

        pa = TH.Asset.from_delta(repo, delta)
        assert pa.path == exp_path
        assert_data(pa.data)

    def test_from_delta_add(self, this_raw_repo):
        self._test_from_delta(
            this_raw_repo,
            "9b40818176",
            "boing/project-assets/graphics/alien.png",
            _assert_data_content(b"This is not a real PNG file!"),
        )

    def test_from_delta_modify(self, this_raw_repo):
        self._test_from_delta(
            this_raw_repo,
            "c87cb28d15ba",
            "boing/project-assets/graphics/alien.png",
            _assert_data_length(288),  # Taken from "ls -l"
        )


class TestProjectCommit:
    def test_short_oid(self, this_raw_repo):
        # Construct commit from shorter-than-short oid:
        pc = TH.ProjectCommit(this_raw_repo, "ae1fea2")
        assert pc.short_oid == "ae1fea2c9f21"

    @pytest.mark.parametrize(
        "oid, exp_summary",
        [
            ("ae1fea2c", "BASE"),
            ("e1655214", "tutorial-text"),
            ("e41e02c9", "#add-Alien-skeleton"),
            ("9b408181", 'add-assets("boing/project-assets/graphics/alien.png")'),
            ("c87cb28d", 'modify-assets("boing/project-assets/graphics/alien.png")'),
            ("bf0e5cfa", 'add-assets("boing/tutorial-assets/not-a-real-png.png")'),
            ("b36564cb", "asset-source"),
        ])
    def test_summary_label(self, this_raw_repo, oid, exp_summary):
        pc = TH.ProjectCommit(this_raw_repo, oid)
        assert pc.summary_label == exp_summary

    def test_str(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "ae1fea2")
        assert str(pc) == "<ProjectCommit: ae1fea2c9f21 BASE>"

    def test_message_subject(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "ae1fea2c9f21")
        assert pc.message_subject == "{base} Add empty code file"

    def test_message_body(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "2f1f4fb")
        assert pc.message_body.startswith("This sound")

    def test_message_body_empty(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "9b40818")
        assert pc.message_body == ""

    def test_message_body_rejects(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "d5f7ae0")
        with pytest.raises(TCE.TutorialStructureError,
                           match="malformed commit message"):
            pc.message_body

    def test_asset_credits_with(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "2f1f4fb")
        assert len(pc.assets_credits) == 1
        credit = pc.assets_credits[0]
        assert credit.asset_basenames == ["bell-ping.mp3"]
        assert credit.asset_usage == "the project"
        assert "candle damper" in credit.credit_markdown

    @pytest.mark.parametrize("oid", ["9b40818", "c87cb28"])
    def test_asset_credits_without(self, this_raw_repo, oid, caplog):
        with caplog.at_level(logging.WARNING):
            pc = TH.ProjectCommit(this_raw_repo, oid)
            assert len(pc.assets_credits) == 0
            assert "has no body" in caplog.text

    def test_identifier_slug_with(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "e41e02c9be")
        assert pc.has_identifier_slug
        assert pc.maybe_identifier_slug == "add-Alien-skeleton"
        assert pc.identifier_slug == "add-Alien-skeleton"

    def test_identifier_slug_without(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "ae1fea2c9f21")
        assert not pc.has_identifier_slug
        assert pc.maybe_identifier_slug is None
        with pytest.raises(TCE.InternalError,
                           match="commit .* has no identifier"):
            pc.identifier_slug

    def test_base_detection_yes(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "ae1fea2c9f21")
        assert pc.is_base

    def test_base_detection_no(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "e41e02c9be")
        assert not pc.is_base

    def test_whether_adds_project_assets_yes(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "9b4081817626")
        assert pc.adds_project_assets

    def test_whether_adds_project_assets_no(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "e41e02c9be03")
        assert not pc.adds_project_assets

    def test_whether_adds_project_assets_root_commit(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "156e4b616fce")
        assert not pc.adds_project_assets

    def test_whether_adds_project_assets_error(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "019fc857")
        with pytest.raises(TCE.TutorialStructureError,
                           match="project assets but also has"):
            pc.adds_project_assets

    def test_whether_adds_tutorial_assets_yes(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "bf0e5cfa4b44")
        assert pc.adds_tutorial_assets

    def test_whether_adds_tutorial_assets_no(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "e41e02c9be03")
        assert not pc.adds_tutorial_assets

    def test_whether_adds_tutorial_assets_root_commit(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "156e4b616fce")
        assert not pc.adds_tutorial_assets

    def test_whether_adds_tutorial_assets_error(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "6b71bac9f1c1")
        with pytest.raises(TCE.TutorialStructureError,
                           match="tutorial assets but also has"):
            pc.adds_tutorial_assets

    def test_modifies_tutorial_text_yes(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "e1655214c662")
        assert pc.modifies_tutorial_text

    def test_modifies_tutorial_text_no(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "e41e02c9be03")
        assert not pc.modifies_tutorial_text

    def test_modifies_python_code_yes(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "e41e02c9be03")
        assert pc.modifies_python_code

    def test_modifies_python_code_no(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "9b4081817626")
        assert not pc.modifies_python_code

    def test_diff_against_parent_or_empty(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "fd166346")
        diff = pc.diff_against_parent_or_empty
        assert len(diff) == 1
        delta = list(diff.deltas)[0]
        assert delta.status == pygit2.GIT_DELTA_MODIFIED

    def test_diff_against_parent_or_empty_root_commit(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "156e4b616fce")
        assert len(pc.diff_against_parent_or_empty) == 0

    def test_sole_modify_against_parent(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "e41e02c9be03")
        assert pc.sole_modify_against_parent.old_file.path == "boing/code.py"

    def test_sole_modify_against_parent_not_sole(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "c2642880a6fc")
        with pytest.raises(TCE.TutorialStructureError,
                           match="not have exactly one"):
            pc.sole_modify_against_parent

    def test_sole_modify_against_parent_not_modified(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "ae1fea2")
        with pytest.raises(TCE.TutorialStructureError,
                           match="not of type MODIFIED"):
            pc.sole_modify_against_parent

    def test_added_assets_one_asset(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "9b40818176")
        got_assets = pc.added_assets
        assert len(got_assets) == 1
        assert got_assets[0].path == "boing/project-assets/graphics/alien.png"
        assert got_assets[0].data == b"This is not a real PNG file!"

    def test_added_assets_no_assets(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "fd166346")
        assert pc.added_assets == []

    def test_code_patch(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "e41e02c9be")
        patch = pc.code_patch_against_parent
        context, n_adds, n_dels = patch.line_stats
        assert n_adds == 4
        assert n_dels == 0

    def test_code_patch_error(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "9b40818176")
        with pytest.raises(TCE.TutorialStructureError,
                           match="does not modify the Python code"):
            pc.code_patch_against_parent

    def test_text_file_contents(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "fd16634610de")
        assert pc.text_file_contents("boing/code.py") == "import pytch\n"

    def test_text_file_contents_missing(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "fd16634610de")
        with pytest.raises(TCE.TutorialStructureError,
                           match="file .* not found"):
            assert pc.text_file_contents("boing/no-such-file.txt")


class TestProjectHistory:
    def test_project_commits(self, project_history):
        # Fairly weak test, to avoid having to keep updating it.
        assert len(project_history.project_commits) >= 4

    def test_dupd_slugs_1(self, cloned_repo):
        with pytest.raises(
            TCE.TutorialStructureError,
            match=r"duplicate .* \['greet-more'\]"
        ):
            TH.ProjectHistory(cloned_repo.workdir,
                              "origin/unit-tests-dupd-slugs-1")

    def test_dupd_slugs_2(self, cloned_repo):
        with pytest.raises(
            TCE.TutorialStructureError,
            match=r"duplicate .* \['greet-more', 'greet-less'\]"
        ):
            TH.ProjectHistory(cloned_repo.workdir,
                              "origin/unit-tests-dupd-slugs-2")

    def test_no_base_commit(self, cloned_repo):
        with pytest.raises(TCE.TutorialStructureError,
                           match=r"did not find \{base\}"):
            TH.ProjectHistory(cloned_repo.workdir, "d5f7ae0")

    def test_tip_oid_string(self, this_raw_repo, project_history):
        exp_oid = this_raw_repo.revparse_single("unit-tests-commits").oid
        assert project_history.tip_oid_string == str(exp_oid)

    def test_top_level_directory_name(self, project_history):
        assert project_history.top_level_directory_name == "boing"

    def test_python_code_path(self, project_history):
        assert project_history.python_code_path == "boing/code.py"

    def test_tutorial_text_path(self, project_history):
        assert project_history.tutorial_text_path == "boing/tutorial.md"

    def test_tutorial_text(self, project_history):
        TTS = TH.ProjectHistory.TutorialTextSource
        text_source = project_history.tutorial_text_source
        target_text = ("# Boing!" if text_source == TTS.TIP_REVISION
                       else "Working copy")
        assert project_history.tutorial_text.startswith(target_text)

    def test_summary_text(self, project_history):
        TTS = TH.ProjectHistory.TutorialTextSource
        text_source = project_history.tutorial_text_source
        target_text = ("# Summary for Boing" if text_source == TTS.TIP_REVISION
                       else "# Working summary for Boing")
        assert project_history.summary_text.startswith(target_text)

    def test_metadata_text(self, project_history):
        metadata = json.loads(project_history.metadata_text)
        TTS = TH.ProjectHistory.TutorialTextSource
        text_source = project_history.tutorial_text_source
        target_text = ("advance" if text_source == TTS.TIP_REVISION
                       else "easy")
        assert metadata["difficulty"] == target_text

    def test_initial_code_text(self, project_history):
        assert project_history.initial_code_text == ""

    def test_final_code_text(self, project_history):
        assert re.match(r"import pytch", project_history.final_code_text)

    def test_slug_is_known(self, project_history):
        # Assert we get actual True and False, not just things which evaluate
        # to True/False when converted to bool.
        assert project_history.slug_is_known("add-Alien-skeleton") is True
        assert project_history.slug_is_known("no-such-slug-in-repo") is False

    def test_ordered_commit_slugs(self, project_history):
        assert project_history.ordered_commit_slugs == [
            "import-pytch",
            "add-Alien-skeleton",
        ]

    def test_commit_from_slug(self, project_history):
        assert len(project_history.commit_from_slug) == 2
        got_oid = project_history.commit_from_slug["add-Alien-skeleton"].oid
        exp_oid = "e41e02c9be0398f0a89e275da6edf5d3110add54"
        assert str(got_oid) == exp_oid

    def test_all_assets(self, project_history):
        got_paths = sorted([a.path for a in project_history.all_assets])
        assert got_paths == [
            "boing/project-assets/bell-ping.mp3",
            "boing/project-assets/graphics/alien.png",
            "boing/project-assets/graphics/small-blue.png",
            "boing/project-assets/graphics/small-red.png",
            "boing/tutorial-assets/not-a-real-png.png",
        ]

    def test_all_asset_credits(self, fresh_project_history, caplog):
        with caplog.at_level(logging.WARNING):
            credits = fresh_project_history.all_asset_credits
            assert len(credits) == 1
            assert "bf0e5cf" in caplog.text
            assert "9b40818" in caplog.text

    def test_all_project_assets(self, project_history):
        got_paths = sorted([a.path for a in project_history.all_project_assets])
        assert got_paths == [
            "boing/project-assets/bell-ping.mp3",
            "boing/project-assets/graphics/alien.png",
            "boing/project-assets/graphics/small-blue.png",
            "boing/project-assets/graphics/small-red.png",
        ]
        alien_assets = [
            a for a in project_history.all_project_assets
            if a.path.endswith("alien.png")
        ]
        assert len(alien_assets) == 1
        alien_asset = alien_assets[0]
        got_size = Image.open(io.BytesIO(alien_asset.data)).size
        assert got_size == (80, 40)

    def test_code_text_from_slug(self, project_history):
        text = project_history.code_text_from_slug("add-Alien-skeleton")
        assert re.match(r"^import.*pass$", text, re.DOTALL)

    def test_code_patch(self, project_history):
        patch = project_history.code_patch_against_parent("add-Alien-skeleton")
        context, n_adds, n_dels = patch.line_stats
        assert n_adds == 4
        assert n_dels == 0
