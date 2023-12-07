import ast
from dataclasses import dataclass
from typing import Literal
from .errors import TutorialStructureError


def make_of_kind(kind):
    def make(cls, *args):
        return cls(kind, *args)
    return classmethod(make)


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
