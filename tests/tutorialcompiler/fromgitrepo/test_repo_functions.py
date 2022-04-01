import pytest

import pytchbuild.tutorialcompiler.fromgitrepo.repo_functions as TCRF


class TestEnsureStatusClean:
    def test_when_is_clean(self, clean_cloned_repo):
        TCRF.ensure_status_clean(clean_cloned_repo)
        # If we get here without exception, test has passed.

    def test_when_modified_files(self, cloned_repo):
        # The cloned_repo fixture modifies two files.
        with pytest.raises(RuntimeError, match="repo not clean"):
            TCRF.ensure_status_clean(cloned_repo)
