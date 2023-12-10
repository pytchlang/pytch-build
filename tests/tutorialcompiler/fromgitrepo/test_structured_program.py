import pytest
import pytchbuild.tutorialcompiler.fromgitrepo.structured_program as SP
import pytchbuild.tutorialcompiler.fromgitrepo.errors as TCE
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


def zip2(xs, ys):
    return zip(xs, ys, strict=True)


def raises_TutorialStructureError(match):
    return pytest.raises(TCE.TutorialStructureError, match=match)


class TestEventDescriptor:
    def test_ctor_valid(self):
        mk_EventDescriptor = SP.EventDescriptor_from_decorator_node
        func_defs = func_defs_of_path("valid_decorators.py")

        exp_names_with_event_descriptors = [
            ("h1", SP.EventDescriptorGreenFlag.make()),
            ("h2", SP.EventDescriptorStartAsClone.make()),
            ("h3", SP.EventDescriptorMessageReceived.make("hello-world")),
            ("h4", SP.EventDescriptorKeyPressed.make("b")),
            ("h5", SP.EventDescriptorClicked.make()),
            ("h6", SP.EventDescriptorClicked.make()),
        ]

        for func, (exp_name, exp_descriptor) in zip2(
            func_defs,
            exp_names_with_event_descriptors,
        ):
            assert func.name == exp_name
            decorator = sole_decorator_of_func_def(func)
            got_descriptor = mk_EventDescriptor(decorator)
            assert got_descriptor == exp_descriptor

    def test_ctor_invalid(self):
        func_defs = func_defs_of_path("invalid_decorators.py")

        exp_names_with_exception_matches = [
            ("h1", "but found Name"),
            ("h2", "unknown attribute decorator"),
            ("h3", "function-call decorator .* Attribute on pytch"),
            ("h4", "unknown pytch function-call"),
        ]

        for func, (exp_name, exp_exception_match) in zip2(
            func_defs,
            exp_names_with_exception_matches,
        ):
            assert func.name == exp_name
            decorator = sole_decorator_of_func_def(func)
            with raises_TutorialStructureError(exp_exception_match):
                SP.EventDescriptor_from_decorator_node(decorator)


class TestActorIdentifier:
    def test_ctor_invalid(self):
        with pytest.raises(ValueError, match="unknown kind"):
            SP.ActorIdentifier_make("banana", "banana")


class TestHelpers:
    def test_deindented_line(self):
        assert SP.deindented_line("        pass") == "pass"
        assert SP.deindented_line("        ") == ""
        assert SP.deindented_line("") == ""
        with pytest.raises(
            TCE.TutorialStructureError, match="8 spaces but it did not"
        ):
            SP.deindented_line("    # not enough indentation")


class TestActorCode:
    def test_new_empty_valid(self):
        class_defs = class_defs_of_path("valid_empty_classes.py")

        exp_names_with_kinds = [
            ("Banana", "sprite"),
            ("Landscape", "stage"),
        ]

        for cls, (exp_name, exp_kind) in zip2(
            class_defs, exp_names_with_kinds
        ):
            assert cls.name == exp_name
            actor_code = SP.ActorCode.new_empty(cls)
            assert actor_code.name == exp_name
            assert actor_code.kind == exp_kind
            exp_identifier = SP.ActorIdentifier_make(exp_kind, exp_name)
            assert actor_code.identifier == exp_identifier

    def test_new_empty_invalid(self):
        class_defs = class_defs_of_path("invalid_empty_classes.py")

        exp_names_with_exception_matches = [
            ("C1", "either pytch.Sprite or pytch.Stage"),
            ("C2", "have one base but found 2"),
            ("C3", "to be Attribute on pytch"),
            ("C4", "to be Attribute on pytch"),
        ]

        for cls, (exp_name, exp_exception_match) in zip2(
            class_defs,
            exp_names_with_exception_matches,
        ):
            assert cls.name == exp_name
            with raises_TutorialStructureError(exp_exception_match):
                SP.ActorCode.new_empty(cls)