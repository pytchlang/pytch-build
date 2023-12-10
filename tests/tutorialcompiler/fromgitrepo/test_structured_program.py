import pytest
from pathlib import Path
import ast


def fixture_code_text(relative_path):
    this_dir = Path(__file__).parent
    full_path = this_dir / "structured-program-fixtures" / relative_path
    return full_path.open("rt").read()


def fixture_code_ast(relative_path):
    return ast.parse(fixture_code_text(relative_path))


def statements_of_kind(code, cls):
    return [stmt for stmt in code.body if isinstance(stmt, cls)]


def func_defs_of_path(relative_path):
    code_ast = fixture_code_ast(relative_path)
    return statements_of_kind(code_ast, ast.FunctionDef)


def class_defs_of_path(relative_path):
    code_ast = fixture_code_ast(relative_path)
    return statements_of_kind(code_ast, ast.ClassDef)


def sole_decorator_of_func_def(func_def):
    decorators = func_def.decorator_list
    assert len(decorators) == 1
    return decorators[0]
