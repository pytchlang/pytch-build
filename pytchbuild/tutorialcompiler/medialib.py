from dataclasses import dataclass, asdict
from typing import List


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

    def as_output_dict(self):
        items_dicts = [asdict(item) for item in self.items]
        return {
            "id": self.id,
            "name": self.name,
            "items": items_dicts,
            "tags": self.tags,
        }
