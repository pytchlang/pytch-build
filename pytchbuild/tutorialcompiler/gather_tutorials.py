from dataclasses import dataclass
import bs4


@dataclass
class TutorialSummary:
    name: str  # Currently just for human readers
    div: bs4.element.Tag
