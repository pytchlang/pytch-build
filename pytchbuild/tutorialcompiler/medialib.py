from dataclasses import dataclass, asdict, replace
from typing import List, Dict
from collections import defaultdict
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

    @classmethod
    def gather_equivalent(cls, groups):
        """Unify singleton asset-groups by name and content
        """
        singleton_groups = [g for g in groups if g.n_items == 1]
        proper_groups = [g for g in groups if g.n_items > 1]

        group_by_id = {}
        groups_by_key = defaultdict(set)
        for group in singleton_groups:
            group_by_id[group.id] = group
            asset = group.items[0]
            key = (asset.name, asset.relativeUrl)
            groups_by_key[key].add(group.id)

        canonical_singleton_groups = [
            cls.unify_equivalent([group_by_id[id] for id in group_ids])
            for group_ids in groups_by_key.values()
        ]

        canonical_assets = canonical_singleton_groups + proper_groups
        canonical_assets.sort(key=attrgetter("lowercase_name"))

        return canonical_assets


@dataclass
class MediaLibraryData:
    entries: List[MediaLibraryEntry]
    data_from_content_id: Dict[str, bytes]

    @classmethod
    def new_empty(cls):
        return cls([], {})
