"""Console script for pytchbuild
"""

import sys
import click

import pygit2

from .tutorialcompiler.fromgitrepo import compile as compile_fromgitrepo
from .tutorialcompiler.fromgitrepo.tutorial_history import ProjectHistory


@click.command()
@click.option(
    "-o", "output_file",
    type=click.File(mode="wb"),
    required=True,
    help="where to write the zipfile containing the tutorial content",
)
@click.option(
    "-r", "--repository-path",
    default=pygit2.discover_repository("."),
    envvar="GIT_DIR",
    metavar="PATH",
    help="path to root of git repository",
)
@click.option(
    "-b", "--tip-revision",
    default="HEAD",
    metavar="REVISION",
    help="revision (e.g., branch name) at tip of tutorial",
)
@click.option(
    "-t", "--tutorial-text-source",
    type=click.Choice([x.name for x in ProjectHistory.TutorialTextSource],
                      case_sensitive=False),
    default=ProjectHistory.TutorialTextSource.TIP_REVISION.name,
    help="what source to use for the tutorial text",
)
def main(output_file, repository_path, tip_revision, tutorial_text_source):
    if repository_path is None:
        raise click.UsageError(
            "\nUnable to discover repository.  Please specify one\n"
            "either with the -r/--repository-path option or via\n"
            "the GIT_DIR environment variable.")

    # Convert string to enumerator:
    tutorial_text_source = getattr(ProjectHistory.TutorialTextSource,
                                   tutorial_text_source)

    compile_fromgitrepo(output_file,
                        repository_path,
                        tip_revision,
                        tutorial_text_source)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
