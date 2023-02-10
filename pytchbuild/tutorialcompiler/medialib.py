from dataclasses import dataclass, asdict, replace
from typing import List
from operator import attrgetter, concat
from functools import reduce


@dataclass
class MediaLibraryItem:
    # The field names end up as JSON, and ultimately as properties of
    # the front-end type "ClipArtGalleryItem", so use camelCase.
    name: str
    relativeUrl: str
    size: List[int]


@dataclass
class MediaLibraryEntry:
    # The field names end up as JSON, and ultimately as properties of
    # the front-end type "ClipArtGalleryEntry".
    id: int
    name: str
    items: List[MediaLibraryItem]
    tags: List[str]

    @property
    def lowercase_name(self):
        return self.name.lower()

    def as_output_dict(self):
        items_dicts = [asdict(item) for item in self.items]
        return {
            "id": self.id,
            "name": self.name,
            "items": items_dicts,
            "tags": self.tags,
        }

    @classmethod
    def unify_equivalent(cls, groups):
        # Avoid needless new objects:
        if len(groups) == 1:
            return groups[0]

        all_tags = reduce(concat, map(attrgetter("tags"), groups), [])
        return replace(groups[0], tags=sorted(all_tags))
