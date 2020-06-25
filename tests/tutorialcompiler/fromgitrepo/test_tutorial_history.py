import pytchbuild.tutorialcompiler.fromgitrepo.tutorial_history as TH


class TestProjectCommit:
    def test_message_subject(self, this_raw_repo):
        pc = TH.ProjectCommit(this_raw_repo, "ae1fea2c9f21")
        assert pc.message_subject == "{base} Add empty code file"
