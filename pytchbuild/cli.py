"""Console script for pytchbuild
"""

import sys
import click

import pygit2

from .tutorialcompiler.fromgitrepo import compile as compile_fromgitrepo


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
@click.argument("tip_revision")
def main(output_file, repository_path, tip_revision):
    compile_fromgitrepo(output_file, repository_path, tip_revision)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
