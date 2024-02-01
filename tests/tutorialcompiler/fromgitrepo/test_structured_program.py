import pytest
import pytchbuild.tutorialcompiler.fromgitrepo.tutorial_history as TH
import pytchbuild.tutorialcompiler.fromgitrepo.structured_program as SP
import pytchbuild.tutorialcompiler.fromgitrepo.structured_diff as SD
import pytchbuild.tutorialcompiler.fromgitrepo.errors as TCE
from pathlib import Path
import ast


def fixture_code_text(relative_path):
    this_dir = Path(__file__).parent
    full_path = this_dir / "structured-program-fixtures" / relative_path
    return full_path.open("rt").read()


def structured_program_from_path(relative_path):
    code = fixture_code_text(relative_path)
    return SP.StructuredPytchProgram(code)


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


@pytest.fixture(scope="session")
def valid_program_text():
    return fixture_code_text("valid_classes.py")


@pytest.fixture(scope="session")
def valid_program(valid_program_text):
    return SP.StructuredPytchProgram(valid_program_text)


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


class TestStructuredProgram:
    def assert_handlers(self, handlers, exp_details):
        for handler, (exp_name, exp_event, exp_body) in zip2(
            handlers, exp_details
        ):
            assert handler.method_name == exp_name
            assert handler.event == exp_event
            assert handler.body_suite_text == exp_body

    def test_valid_individual_classes(self, valid_program):
        bowl = valid_program.top_level_classes["Bowl"]
        assert bowl.name == "Bowl"
        assert bowl.kind == "sprite"
        assert bowl.appearances == ["bowl.png", "basket.png"]
        self.assert_handlers(
            bowl.handlers,
            [("move_with_keys", SP.EventDescriptorGreenFlag.make(), "")],
        )

        apple = valid_program.top_level_classes["Apple"]
        assert apple.name == "Apple"
        assert apple.kind == "sprite"
        assert apple.appearances == ["apple.png"]
        self.assert_handlers(
            apple.handlers,
            [
                (
                    "move_down_stage",
                    SP.EventDescriptorMessageReceived.make("drop-apple"),
                    "print(1)\nprint(2)\nprint(3)",
                )
            ],
        )

        scorekeeper = valid_program.top_level_classes["ScoreKeeper"]
        assert scorekeeper.name == "ScoreKeeper"
        assert scorekeeper.kind == "stage"
        assert scorekeeper.appearances == ["Dani.png"]
        self.assert_handlers(
            scorekeeper.handlers,
            [
                (
                    "initialise",
                    SP.EventDescriptorGreenFlag.make(),
                    "print(100)",
                ),
                (
                    "award_point",
                    SP.EventDescriptorMessageReceived.make("award-point"),
                    "",
                ),
                ("drop_apples", SP.EventDescriptorGreenFlag.make(), ""),
            ],
        )

    def test_invalid(self):
        paths_with_exp_exception_match = [
            (
                "invalid_class_costumes_not_list.py",
                "list literal but found Constant",
            ),
            (
                "invalid_class_costumes_contains_lambda.py",
                "string literal but found Lambda",
            ),
            (
                "invalid_class_costumes_contains_int.py",
                "string literal but found Constant of class int",
            ),
            ("invalid_class_statement.py", "unexpected ClassDef"),
            ("invalid_multiple_decorators.py", "Bowl.bad .* found 2"),
            ("invalid_no_decorators.py", "Bowl.bad .* found 0"),
        ]
        for path, exp_exception_match in paths_with_exp_exception_match:
            with raises_TutorialStructureError(exp_exception_match):
                structured_program_from_path(path)

    def test_valid_all_handlers(self, valid_program):
        got_handler_names = [
            handler.method_name for handler in valid_program.all_handlers()
        ]
        exp_handler_names = [
            "move_with_keys",
            "move_down_stage",
            "initialise",
            "award_point",
            "drop_apples",
        ]
        assert got_handler_names == exp_handler_names

    def test_valid_actor_names(self, valid_program):
        got_actor_names = valid_program.all_actor_names
        exp_actor_names = ["Bowl", "Apple", "ScoreKeeper"]
        assert got_actor_names == exp_actor_names

    def test_valid_appearances(self, valid_program):
        got_appearances = valid_program.all_appearances
        App = SP.ActorAppearance
        Id = SP.ActorIdentifier_make
        exp_appearances = [
            App(Id("sprite", "Bowl"), "bowl.png"),
            App(Id("sprite", "Bowl"), "basket.png"),
            App(Id("sprite", "Apple"), "apple.png"),
            App(Id("stage", "--ignored--"), "Dani.png"),
        ]
        assert got_appearances == exp_appearances

    def test_valid_scripts(self, valid_program):
        got_scripts = valid_program.all_scripts
        got_script_projections = [
            (script.actor_identifier, script.script.method_name)
            for script in got_scripts
        ]
        Id = SP.ActorIdentifier_make
        exp_script_projections = [
            (Id("sprite", "Bowl"), "move_with_keys"),
            (Id("sprite", "Apple"), "move_down_stage"),
            (Id("stage", "--ignored--"), "initialise"),
            (Id("stage", "--ignored--"), "award_point"),
            (Id("stage", "--ignored--"), "drop_apples"),
        ]
        assert got_script_projections == exp_script_projections

    def test_valid_handler_from_path_valid(self, valid_program):
        Id = SP.ActorIdentifier_make
        paths_with_exp_codes = [
            (
                SP.ScriptPath(Id("sprite", "Apple"), "move_down_stage"),
                "print(1)\nprint(2)\nprint(3)",
            ),
            (SP.ScriptPath(Id("stage", "--ignored--"), "award_point"), ""),
        ]
        for path, exp_code in paths_with_exp_codes:
            handler = valid_program.handler_from_path(path)
            got_code = handler.body_suite_text
            assert got_code == exp_code

    def test_valid_handler_from_path_invalid(self, valid_program):
        Id = SP.ActorIdentifier_make
        Path = SP.ScriptPath
        with raises_TutorialStructureError("expecting exactly one"):
            path = Path(Id("sprite", "Banana"), "nothing")
            valid_program.handler_from_path(path)

    def test_canonical_actors_too_many(self):
        sp = structured_program_from_path("canon_actors_too_many.py")
        with raises_TutorialStructureError("expecting at most.*found 2"):
            sp.canonical_actors()

    def assert_first_stage_second_sprite(self, structured_program):
        actors = structured_program.canonical_actors()
        assert len(actors) == 2
        assert actors[0].kind == "stage"
        assert actors[1].kind == "sprite"

    def test_canonical_actors_none(self):
        sp = structured_program_from_path("canon_actors_none.py")
        assert len(sp.actors) == 1
        self.assert_first_stage_second_sprite(sp)

    def test_canonical_actors_one_last(self):
        sp = structured_program_from_path("canon_actors_one_last.py")
        assert len(sp.actors) == 2
        self.assert_first_stage_second_sprite(sp)


########################################################################


@pytest.fixture(scope="session")
def apple_history(this_raw_repo):
    return TH.ProjectHistory(
        this_raw_repo.workdir,
        "unit-tests-catch-apple",
    )


class TestRichCommits:
    slugs_with_kinds_and_args = [
        ("add-empty-Bowl", "add-sprite"),
        ("add-Bowl-costume", "add-medialib-appearance", "the bowl"),
        ("add-empty-move-with-keys-handler", "add-script"),
        ("add-move-with-keys-initial-body", "edit-script"),
        ("move-bowl-right", "edit-script"),
        ("clamp-bowl-at-right", "edit-script"),
        ("move-clamp-bowl-left", "edit-script"),
        ("add-empty-Apple-class", "add-sprite"),
        ("give-Apple-costume", "add-medialib-appearance", "the Apple"),
        ("define-skeleton-apple-move-down-screen", "add-script"),
        ("make-apple-fall-down-screen", "edit-script"),
        ("hide-Apple-when-caught", "edit-script"),
        ("define-skeleton-ScoreKeeper-sprite", "add-sprite"),
        ("give-ScoreKeeper-costume", "add-medialib-appearance", "Dani"),
        ("move-ScoreKeeper-to-right-place", "add-script"),
        ("add-ScoreKeeper-score-attribute", "edit-script"),
        ("announce-starting-score", "edit-script"),
        ("add-empty-award-point-handler", "add-script"),
        ("increment-score", "edit-script"),
        ("refresh-score-speech", "edit-script"),
        ("broadcast-when-apple-caught", "edit-script"),
        ("choose-random-drop-x", "edit-script"),
        ("drop-from-random-abscissa", "edit-script"),
        ("launch-apple-on-message-not-green-flag", "change-hat-block"),
        ("add-empty-drop-apples-loop-script", "add-script"),
        ("add-broadcast-drop-apple-loop", "edit-script"),
        ("show-apple-when-fall-starts", "edit-script"),
    ]

    all_kinds = set(
        [
            "add-sprite",
            "add-medialib-appearance",
            "add-script",
            "edit-script",
            "change-hat-block",
        ]
    )

    def test_examples(self, apple_history):
        for slug, kind, *args in self.slugs_with_kinds_and_args:
            codes = apple_history.old_and_new_code(slug)
            diff = SD.StructuredPytchDiff(*codes)
            # Ignore return value; test that it runs without error:
            diff.rich_commit(kind, *args)

    def test_examples_wrong_kind(self, apple_history):
        for slug, kind, *args in self.slugs_with_kinds_and_args:
            codes = apple_history.old_and_new_code(slug)
            diff = SD.StructuredPytchDiff(*codes)
            wrong_kinds = self.all_kinds - {kind}
            for wrong_kind in wrong_kinds:
                with pytest.raises(TCE.TutorialStructureError):
                    wrong_kind_args = (
                        ["some costume"]
                        if wrong_kind == "add-medialib-appearance"
                        else []
                    )
                    diff.rich_commit(wrong_kind, *wrong_kind_args)
