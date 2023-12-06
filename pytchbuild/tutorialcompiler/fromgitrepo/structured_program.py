from dataclasses import dataclass
from typing import Literal


########################################################################
#
# Mirror the TypeScript ones in the "structured-program" part of the
# front-end, used to represent the different kinds of hat-blocks
# (events).

@dataclass
class EventDescriptorGreenFlag:
    kind: Literal["green-flag"]


@dataclass
class EventDescriptorKeyPressed:
    kind: Literal["key-pressed"]
    keyName: str


@dataclass
class EventDescriptorMessageReceived:
    kind: Literal["message-received"]
    message: str


@dataclass
class EventDescriptorStartAsClone:
    kind: Literal["start-as-clone"]


@dataclass
class EventDescriptorClicked:
    kind: Literal["clicked"]


EventDescriptor = (
    EventDescriptorGreenFlag
    | EventDescriptorKeyPressed
    | EventDescriptorMessageReceived
    | EventDescriptorStartAsClone
    | EventDescriptorClicked
)
