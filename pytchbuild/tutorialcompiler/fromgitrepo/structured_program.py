import ast
from dataclasses import dataclass
from typing import Any, Literal
from .errors import TutorialStructureError

# Some of the following have camelCase because they're destined to be
# serialised as JSON ready for consumption by JavaScript.


def make_of_kind(kind):
    def make(cls, *args):
        return cls(kind, *args)
    return classmethod(make)


########################################################################

EXPECTED_INDENT_LEN = 8
EXPECTED_INDENT = " " * EXPECTED_INDENT_LEN


def deindented_line(line):
    if line == "":
        return line
    else:
        if not line.startswith(EXPECTED_INDENT):
            raise TutorialStructureError(
                "expecting line to start with"
                f" {EXPECTED_INDENT_LEN} spaces but it did not"
            )
        return line[EXPECTED_INDENT_LEN:]


########################################################################
#
# Mirror the TypeScript ones in the "structured-program" part of the
# front-end, used to represent the different kinds of hat-blocks
# (events).

@dataclass
class EventDescriptorGreenFlag:
    kind: Literal["green-flag"]
    make = make_of_kind("green-flag")


@dataclass
class EventDescriptorKeyPressed:
    kind: Literal["key-pressed"]
    keyName: str
    make = make_of_kind("key-pressed")


@dataclass
class EventDescriptorMessageReceived:
    kind: Literal["message-received"]
    message: str
    make = make_of_kind("message-received")


@dataclass
class EventDescriptorStartAsClone:
    kind: Literal["start-as-clone"]
    make = make_of_kind("start-as-clone")


@dataclass
class EventDescriptorClicked:
    kind: Literal["clicked"]
    make = make_of_kind("clicked")


EventDescriptor = (
    EventDescriptorGreenFlag
    | EventDescriptorKeyPressed
    | EventDescriptorMessageReceived
    | EventDescriptorStartAsClone
    | EventDescriptorClicked
)


def EventDescriptor_from_decorator_node(node):
    # TODO: Replace if/elif/elif/else with match/case?
    if isinstance(node, ast.Attribute):
        assert_is_attribute_on_pytch(node, "attribute decorator")
        if node.attr == "when_green_flag_clicked":
            return EventDescriptorGreenFlag.make()
        elif node.attr in ["when_this_sprite_clicked", "when_stage_clicked"]:
            return EventDescriptorClicked.make()
        elif node.attr == "when_I_start_as_a_clone":
            return EventDescriptorStartAsClone.make()
        else:
            raise TutorialStructureError(
                f"unknown attribute decorator \"{node.attr}\""
            )
    elif isinstance(node, ast.Call):
        err = TutorialStructureError("unknown pytch function-call decorator")
        assert_is_attribute_on_pytch(node.func, "function-call decorator")
        if len(node.args) != 1:
            raise err
        decorator_arg = string_literal_value(node.args[0])
        if node.func.attr == "when_I_receive":
            return EventDescriptorMessageReceived.make(decorator_arg)
        elif node.func.attr == "when_key_pressed":
            return EventDescriptorKeyPressed.make(decorator_arg)
        raise err
    else:
        cls_name = node.__class__.__name__
        raise TutorialStructureError(
            "expecting decorator to be pytch bare attribute"
            f" or function call but found {cls_name}"
        )


########################################################################

def assert_is_attribute_on_pytch(node, node_description):
    """Raise error if `node` is not an Attribute "pytch.SOMETHING".

    The given `node_description` is included in the error message if
    the `node` is not such an Attribute.
    """
    if (
        not isinstance(node, ast.Attribute)
        or not isinstance(node.value, ast.Name)
        or node.value.id != "pytch"
    ):
        raise TutorialStructureError(
            f"expecting {node_description} to be Attribute"
            " on pytch but it is not"
        )


def string_literal_value(node):
    """The value of the string literal `node`.

    If `node` is not such a string literal, raise an error.
    """
    if not isinstance(node, ast.Constant):
        cls_name = node.__class__.__name__
        raise TutorialStructureError(
            f"expecting string literal but found {cls_name}"
        )
    if not isinstance(node.value, str):
        value_cls_name = node.value.__class__.__name__
        raise TutorialStructureError(
            "expecting string literal but found Constant"
            f" of class {value_cls_name}"
        )
    return node.value


########################################################################
#
# Mirror the front-end's ActorIdentifier.


@dataclass(frozen=True)
class ActorIdentifierStage:
    kind: Literal["stage"]
    make = make_of_kind("stage")


@dataclass(frozen=True)
class ActorIdentifierSprite:
    kind: Literal["sprite"]
    name: str
    make = make_of_kind("sprite")


ActorIdentifier = ActorIdentifierStage | ActorIdentifierSprite


def ActorIdentifier_make(kind, name):
    if kind == "stage":
        # Ignore name
        return ActorIdentifierStage.make()
    elif kind == "sprite":
        return ActorIdentifierSprite.make(name)
    else:
        raise ValueError(f'unknown kind "{kind}"')


########################################################################
#
# Mirrors the front-end's ScriptPath.

@dataclass(frozen=True)
class ScriptPath:
    """Location of a method within a Sprite/Stage."""
    actor: ActorIdentifier
    methodName: str  # Not clear whether/how this will be used.


########################################################################

@dataclass
class EventHandlerSummary:
    """Single script represented in Scratch-like form."""
    method_name: str  # For use in unit tests
    event: EventDescriptor
    code_text: str


########################################################################

@dataclass
class EventHandler:
    """Python event handler as it appears in AST."""
    actor_name: str
    method_name: str
    body_lineno_lb: int
    decorators: [Any]
    funcdef_lineno_lb: int
    funcdef_lineno_ub: int
    body_lines: [str]

    def __post_init__(self):
        n_decorators = len(self.decorators)
        if n_decorators != 1:
            raise TutorialStructureError(
                f"expecting method {self.actor_name}.{self.method_name}"
                f" to have one decorator but found {n_decorators}"
            )

    @property
    def body_suite_text(self):
        """Method body, deindented as if it were at top level."""

        lines = [line.rstrip() for line in self.body_lines]
        deindented_lines = [deindented_line(line) for line in lines]

        # When a commit adds an "empty" script, it in fact acts a script
        # with body just "pass".  This keeps the code syntactically valid.
        # Map back to truly empty when presenting to the learner:
        if deindented_lines == ["pass"]:
            return ""
        else:
            return "\n".join(deindented_lines)

    @property
    def _decorator(self):
        return self.decorators[0]

    @property
    def event(self):
        return EventDescriptor_from_decorator_node(self._decorator)

    @property
    def summary(self):
        return EventHandlerSummary(
            self.method_name,
            self.event,
            self.body_suite_text
        )


########################################################################


@dataclass
class ActorCode:
    """A Sprite (Stage) parsed into Costumes (Backdrops) and Scripts."""
    name: str
    kind: Literal["stage", "sprite"]
    appearances: list[str]
    handlers: list[EventHandler]

    @classmethod
    def new_empty(cls, cdef):
        n_bases = len(cdef.bases)
        if n_bases != 1:
            raise TutorialStructureError(
                f'expecting class "{cdef.name}" to have one base'
                f" but found {n_bases}"
            )
        base = cdef.bases[0]
        assert_is_attribute_on_pytch(base, f'base of class "{cdef.name}"')

        # Convert "Stage" (the name of the class within the pytch
        # module) to the kind "stage" and similarly "Sprite"/"sprite".
        kind = base.attr.lower()
        if kind not in ["sprite", "stage"]:
            raise TutorialStructureError(
                f'expecting base of class "{cdef.name}" to be either'
                f" pytch.Sprite or pytch.Stage but found {base.attr}"
            )

        return cls(cdef.name, kind, [], [])

    @property
    def identifier(self):
        return ActorIdentifier_make(self.kind, self.name)


########################################################################

@dataclass(frozen=True)
class ActorAppearance:
    """A costume/backdrop belonging to an actor."""
    actor_identifier: ActorIdentifier
    appearance_name: str


########################################################################

@dataclass
class ActorScript:
    """A script belonging to an actor."""
    actor_identifier: ActorIdentifier
    script: EventHandler

    @property
    def path(self):
        return ScriptPath(self.actor_identifier, self.script.method_name)


########################################################################

class StructuredPytchProgram:
    """Representation of a Pytch program as actors with scripts."""

    def __init__(self, code_text):
        # Line numbers reported in AST nodes are 1-based.  Prepend a
        # padding entry to give a list where we can use those 1-based
        # numbers as indexes:
        self.code_lines = ["PADDING"] + code_text.split("\n")
        self.top_level_classes = {}
        code_ast = ast.parse(code_text)
        for stmt in code_ast.body:
            if isinstance(stmt, ast.ClassDef):
                self.ingest_classdef(stmt)

    def ingest_classdef(self, cdef):
        """Add an ActorCode instance for a class definition."""
        actor_code = ActorCode.new_empty(cdef)
        self.top_level_classes[cdef.name] = actor_code
        for stmt in cdef.body:
            if isinstance(stmt, ast.FunctionDef):
                self.ingest_methoddef(actor_code, stmt)
            elif isinstance(stmt, ast.Assign):
                self.ingest_assignment(actor_code, stmt)
            else:
                cls_name = stmt.__class__.__name__
                raise TutorialStructureError(
                    f"unexpected {cls_name} statement in classdef"
                )

    def ingest_methoddef(self, actor_code, mdef):
        """Add a handler to actor_code for a method definition."""
        body_lineno_lb = mdef.body[0].lineno
        lineno_ub = mdef.end_lineno + 1
        handler = EventHandler(
            actor_code.name,
            mdef.name,
            body_lineno_lb,
            mdef.decorator_list,
            mdef.lineno,
            lineno_ub,
            self.code_lines[body_lineno_lb:lineno_ub]
        )
        actor_code.handlers.append(handler)

    def ingest_assignment(self, actor_code, stmt):
        """Handle class-level assignment to Costumes or Backdrops.

        Set actor_code.appearances to the list of costume/backdrop
        names if assignment is to either of Costumes or Backdrops.
        """
        if len(stmt.targets) != 1:
            # TODO: Warn?
            return
        target = stmt.targets[0]
        if not isinstance(target, ast.Name):
            # TODO: Warn?
            return
        class_attr_name = target.id
        if class_attr_name not in ["Costumes", "Backdrops"]:
            # TODO: Warn?
            return
        if not isinstance(stmt.value, ast.List):
            cls_name = stmt.value.__class__.__name__
            raise TutorialStructureError(
                "expecting Costumes/Backdrops to be list literal"
                f" but found {cls_name}"
            )
        # TODO: Check Sprite has Costumes and Stage has Backdrops?
        actor_code.appearances = [
            string_literal_value(elt)
            for elt in stmt.value.elts
        ]

    def all_handlers(self):
        """Flat iterator yielding all known handlers."""
        for actor_code in self.top_level_classes.values():
            yield from actor_code.handlers
