from dataclasses import dataclass
from typing import Literal


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
