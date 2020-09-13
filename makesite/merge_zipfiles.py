import sys
import zipfile
from contextlib import closing
from pathlib import Path
import click


@click.command()
@click.option(
    "--out-path-prefix",
    default="",
)
@click.argument(
    "out-filename",
    type=click.Path(writable=True),
)
def merge_zipfiles(out_path_prefix, out_filename):
    zipfilenames = [
        line.rstrip().split()[1]
        for line in sys.stdin.readlines()
    ]

    with closing(zipfile.ZipFile(
        out_filename,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
    )) as out_zipfile:
        for in_filename in zipfilenames:
            with closing(zipfile.ZipFile(in_filename, mode="r")) as in_zipfile:
                for info_entry in in_zipfile.infolist():
                    if not info_entry.is_dir():
                        data = in_zipfile.open(info_entry).read()
                        out_path = Path(out_path_prefix) / info_entry.filename
                        # Modify ZipInfo to keep permissions.
                        info_entry.filename = str(out_path)
                        out_zipfile.writestr(info_entry, data)


if __name__ == "__main__":
    merge_zipfiles()
