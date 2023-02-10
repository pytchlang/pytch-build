from dataclasses import dataclass
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
