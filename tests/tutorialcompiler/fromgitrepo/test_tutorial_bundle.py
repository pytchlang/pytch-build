import pytchbuild.tutorialcompiler.fromgitrepo.tutorial_bundle as TB
import zipfile
import io


def test_bundle(project_history):
    bundle = TB.TutorialBundle.from_project_history(project_history)
    assert bundle is not None


def test_bundle_zipfile(project_history):
    bundle = TB.TutorialBundle.from_project_history(project_history)
    round_trip_file = io.BytesIO()
    bundle.write_zipfile(round_trip_file)
    zfile = zipfile.ZipFile(round_trip_file, "r")
    paths = [i.filename for i in zfile.infolist()]

    # Asset sequence is like this because we gather assets from tip
    # commit back to base:
    assert paths == [
        'boing/tutorial.html',
        'boing/summary.html',
        'boing/tutorial-assets/not-a-real-png.png',
        'boing/project-assets/graphics/alien.png',
    ]
