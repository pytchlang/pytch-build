import pytest
from pathlib import Path

import pytchbuild.tutorialcompiler.fromgitrepo.repo_functions as TCRF


class TestEnsureStatusClean:
    def test_when_is_clean(self, clean_cloned_repo):
        TCRF.ensure_status_clean(clean_cloned_repo)
        # If we get here without exception, test has passed.

    def test_when_modified_files(self, cloned_repo):
        # The cloned_repo fixture modifies two files.
        with pytest.raises(RuntimeError, match="repo not clean"):
            TCRF.ensure_status_clean(cloned_repo)

    def test_when_untracked_files(self, clean_cloned_repo):
        new_file_path = Path(clean_cloned_repo.workdir) / "hello.txt"
        with new_file_path.open("wt") as f_out:
            f_out.write("Hello world!\n")
        with pytest.raises(RuntimeError, match="repo not clean"):
            TCRF.ensure_status_clean(clean_cloned_repo)

    def test_when_removed_files(self, clean_cloned_repo):
        workdir_path = Path(clean_cloned_repo.workdir)
        path_to_remove = workdir_path / "boing" / "tutorial.md"
        assert path_to_remove.is_file()
        path_to_remove.unlink()
        with pytest.raises(RuntimeError, match="repo not clean"):
            TCRF.ensure_status_clean(clean_cloned_repo)


class TestCreateSignature:
    def test_returns_value(self, clean_cloned_repo):
        # Pretty weak test.
        sig = TCRF.create_signature(clean_cloned_repo)
        # If we get here, assume all OK; but use value of "sig".
        assert sig is not None


class TestCommitFiles:
    def test_commit_one_file(self, clean_cloned_repo):
        tutorial_text_pre = TCRF.file_contents_at_revision(
            clean_cloned_repo, "HEAD", "boing/tutorial.md"
        ).decode("utf8")
        assert not tutorial_text_pre.endswith("more text!\n")

        workdir_path = Path(clean_cloned_repo.workdir)
        path_to_modify = workdir_path / "boing" / "tutorial.md"
        with path_to_modify.open("at") as f_out:
            f_out.write("\n\nHello some more text!\n")

        sig = TCRF.create_signature(clean_cloned_repo)
        TCRF.commit_files(
            clean_cloned_repo,
            ["boing/tutorial.md"],
            sig,
            "Update tutorial",
        )

        tutorial_text_post = TCRF.file_contents_at_revision(
            clean_cloned_repo, "HEAD", "boing/tutorial.md"
        ).decode("utf8")
        assert tutorial_text_post.endswith("more text!\n")
