import pytchbuild.tutorialcompiler.fromgitrepo.tutorial_bundle as TB


def test_bundle(project_history):
    bundle = TB.TutorialBundle.from_project_history(project_history)
    assert bundle is not None
