"""Console script for pytchbuild
"""

import sys
import click

from .tutorialcompiler.fromgitrepo import compile as compile_fromgitrepo


@click.command()
@click.option(
    "-o", "output_file",
    type=click.File(mode="wb"),
    required=True,
)
@click.option(
    "-r", "--repository-path",
    required=True,
)
@click.argument("tip_revision")
def main(output_file, repository_path, tip_revision):
    compile_fromgitrepo(output_file, repository_path, tip_revision)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
