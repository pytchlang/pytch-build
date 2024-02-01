from dataclasses import dataclass
from .utils import make_of_kind
from typing import Literal


########################################################################
#
# Mirror the TypeScript ones in the "structured-program" part of the
# front-end, used to represent the different kinds of hat-blocks
# (events).
#
# Use camelCase because these types are destined to be serialised as
# JSON ready for consumption by JavaScript.

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
#
# Types for exporting per-method tutorials as demos.

@dataclass
class AssetDescriptor:
    fileBasename: str


# "Bare" (without IDs) versions of types, leaving the front-end to
# create its own Uuids.

@dataclass
class NoIdEventHandler:
    event: EventDescriptor
    pythonCode: str


@dataclass
class NoIdActor:
    kind: Literal["stage", "sprite"]
    name: str
    handlers: list[NoIdEventHandler]
    assets: list[AssetDescriptor]


@dataclass
class NoIdsStructuredProject:
    actors: list[NoIdActor]
