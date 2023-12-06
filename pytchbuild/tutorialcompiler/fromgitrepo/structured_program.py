import ast
from dataclasses import dataclass
from typing import Literal
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
