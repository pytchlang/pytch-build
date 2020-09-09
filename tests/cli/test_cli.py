from click.testing import CliRunner
from pytchbuild.cli import main


def test_cli_runs():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert "repository" in result.output
