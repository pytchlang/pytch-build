import pytchbuild.tutorialcompiler.fromgitrepo.repo_functions as TCRF


class TestEnsureStatusClean:
    def test_when_is_clean(self, clean_cloned_repo):
        TCRF.ensure_status_clean(clean_cloned_repo)
        # If we get here without exception, test has passed.
