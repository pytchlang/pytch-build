import pygit2
import click
import colorlog

from .tutorialcompiler.fromgitrepo import git_repository
from .tutorialcompiler.gather_tutorials import TutorialCollection, commit_to_releases
from .tutorialcompiler.fromgitrepo.errors import TutorialStructureError


log_handler = colorlog.StreamHandler()
log_handler.setFormatter(colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)s : %(message)s"))

logger = colorlog.getLogger()  # Root logger
logger.addHandler(log_handler)


@click.command()
@click.option(
    "-o", "--output-file",
    type=click.File(mode="wb"),
    required=True,
    help="where to write the zipfile containing the tutorial collection",
)
@click.option(
    "-r", "--repository-path",
    default=pygit2.discover_repository("."),
    envvar="GIT_DIR",
    metavar="PATH",
    help="path to root of git repository",
)
@click.option(
    "--index-source",
    type=click.Choice([x.name for x in TutorialCollection.IndexSource],
                      case_sensitive=False),
    default=None,  # Set default manually, to tell whether user gave option
    help='what source to use for the "index.yaml" file of tutorials',
)
@click.option(
    "--make-release/--no-make-release",
    default=False,
    help="make a commit to the 'releases' branch",
)
@click.option(
    "--from-release",
    default=None,
    help='recreate the bundle as of a particular "releases" revision',
)
def main(output_file, repository_path, index_source, make_release, from_release):
    if from_release is not None:
        if make_release:
            raise click.BadArgumentUsage(
                "cannot make a new release from an old release"
            )
        if index_source is not None:
            raise click.BadArgumentUsage(
                "cannot specify index-source for an old release"
            )

    # Set default, or convert from string to enumerator.
    index_source = (
        TutorialCollection.IndexSource.WORKING_DIRECTORY
        if index_source is None
        else getattr(TutorialCollection.IndexSource, index_source)
    )

    try:
        tutorials = (
            TutorialCollection.from_repo_path(repository_path, index_source)
            if from_release is None
            else TutorialCollection.from_releases_commit(repository_path, from_release)
        )

        releases_commit_oid = None

        if make_release:
            with git_repository(repository_path) as repo:
                releases_commit_oid = commit_to_releases(repo, tutorials)

        tutorials.write_new_zipfile(releases_commit_oid, output_file)
    except TutorialStructureError as err:
        colorlog.error(str(err))
        return 1
    else:
        return 0
