import pytest
from pathlib import Path
import ast


def fixture_code_text(relative_path):
    this_dir = Path(__file__).parent
    full_path = this_dir / "structured-program-fixtures" / relative_path
    return full_path.open("rt").read()


def fixture_code_ast(relative_path):
    return ast.parse(fixture_code_text(relative_path))
