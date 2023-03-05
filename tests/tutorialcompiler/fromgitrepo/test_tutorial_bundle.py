import pytchbuild.tutorialcompiler.fromgitrepo.tutorial_bundle as TB
import zipfile
import io


def test_bundle(project_history):
    bundle = TB.TutorialBundle.from_project_history(project_history)
    assert bundle is not None


def test_bundle_zipfile(project_history):
    bundle = TB.TutorialBundle.from_project_history(project_history)
    round_trip_file = io.BytesIO()
    bundle.write_new_zipfile(round_trip_file)
    zfile = zipfile.ZipFile(round_trip_file, "r")
    paths = [i.filename for i in zfile.infolist()]

    assert sorted(paths) == [
        "boing/project-assets.json",
        "boing/project-assets/bell-ping.mp3",
        "boing/project-assets/graphics/alien.png",
        "boing/project-assets/graphics/small-blue.png",
        "boing/project-assets/graphics/small-red.png",
        "boing/summary.html",
        "boing/tutorial-assets/not-a-real-png.png",
        "boing/tutorial.html",
    ]
