import pytest

import pygit2
import pytchbuild.tutorialcompiler.fromgitrepo.tutorial_history as TH


class TestProjectAsset:
    def test_str(self):
        fname = "alien.png"
        data = b"not-a-real-PNG-file"
        pa = TH.ProjectAsset(fname, data)
        assert str(pa) == '<ProjectAsset "alien.png": 19 bytes>'

    def test_from_delta(self, this_raw_repo):
        commit_adding_file = this_raw_repo["d8496bd73702"]
        parent_commit = this_raw_repo[commit_adding_file.parent_ids[0]]
        diff = this_raw_repo.diff(a=parent_commit.tree,
                                  b=commit_adding_file.tree)
        deltas = list(diff.deltas)
        assert len(deltas) == 1
        delta = deltas[0]

        pa = TH.ProjectAsset.from_delta(this_raw_repo, delta)
        assert pa.path == "boing/project-assets/graphics/alien.png"
        assert pa.data == b"This is not a real PNG file!"


class TestProjectCommit:
    def test_short_oid(self, this_raw_repo):
        # Construct commit from shorter-than-short oid:
        pc = TH.ProjectCommit(this_raw_repo, "ae1fea2")
        assert pc.short_oid == "ae1fea2c9f21"

    def test_message_subject(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "ae1fea2c9f21")
        assert pc.message_subject == "{base} Add empty code file"

    def test_identifier_slug_with(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "c936f83f")
        assert pc.has_identifier_slug
        assert pc.maybe_identifier_slug == "add-Alien-skeleton"
        assert pc.identifier_slug == "add-Alien-skeleton"

    def test_identifier_slug_without(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "84f5bb76")
        assert not pc.has_identifier_slug
        assert pc.maybe_identifier_slug is None
        with pytest.raises(ValueError, match="commit .* has no identifier"):
            pc.identifier_slug

    def test_base_detection_yes(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "84f5bb76")
        assert pc.is_base

    def test_base_detection_no(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "c936f83f")
        assert not pc.is_base

    def test_whether_adds_assets_yes(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "9b4081817626")
        assert pc.adds_project_assets

    def test_whether_adds_assets_no(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "e41e02c9be03")
        assert not pc.adds_project_assets

    def test_whether_adds_assets_root_commit(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "156e4b616fce")
        assert not pc.adds_project_assets

    def test_whether_adds_assets_error(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "019fc857")
        with pytest.raises(ValueError, match="but also has"):
            pc.adds_project_assets

    def test_diff_against_parent_or_empty(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "fd166346")
        diff = pc.diff_against_parent_or_empty
        assert len(diff) == 1
        delta = list(diff.deltas)[0]
        assert delta.status == pygit2.GIT_DELTA_MODIFIED

    def test_diff_against_parent_or_empty_root_commit(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "156e4b616fce")
        assert len(pc.diff_against_parent_or_empty) == 0
