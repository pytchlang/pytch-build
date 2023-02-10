from dataclasses import dataclass, asdict, replace
from typing import List, Dict
from collections import defaultdict
from operator import attrgetter, concat
from functools import reduce
from pathlib import Path
from PIL import Image
import io
import hashlib


@dataclass
class MediaLibraryItem:
    # The field names end up as JSON, and ultimately as properties of
    # the front-end type "ClipArtGalleryItem", so use camelCase.
    name: str
    relativeUrl: str
    size: List[int]

    @classmethod
    def from_project_asset(cls, asset):
        path = Path(asset.path)
        hash = hashlib.sha256(asset.data).hexdigest()
        url = f"{hash}{path.suffix}"
        size = list(Image.open(io.BytesIO(asset.data)).size)
        return cls(path.name, url, size)

    def write_file(self, out_dir, data_from_url):
        data = data_from_url[self.relativeUrl]
        (out_dir / self.relativeUrl).write_bytes(data)


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

    def write_files(self, out_dir, data_from_url):
        for item in self.items:
            item.write_file(out_dir, data_from_url)

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

    def accumulate(self, other):
        self.entries.extend(other.entries)
        self.data_from_content_id.update(other.data_from_content_id)

    def with_entries_unified(self):
        unified_entries = MediaLibraryEntry.gather_equivalent(self.entries)
        return replace(self, entries=unified_entries)
