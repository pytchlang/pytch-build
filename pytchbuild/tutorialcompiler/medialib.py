from dataclasses import dataclass, asdict, replace
from typing import List, Dict
from collections import defaultdict
from operator import attrgetter, concat
from functools import reduce
from pathlib import Path
from PIL import Image
import io
import hashlib
import json


@dataclass
class MediaLibraryItem:
    """A named individual graphic asset

    MediaLibraryItem instances are gathered into MediaLibraryEntry
    instances.
    """

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
    """A named, tagged bundle of MediaLibraryItem instances

    In the front-end, the user is presented with a catalogue of
    MediaLibraryEntry instances, and can choose to add a subset of
    them to their project.
    """

    # The field names end up as JSON, and ultimately as properties of
    # the front-end type "ClipArtGalleryEntry".
    id: int
    name: str
    items: List[MediaLibraryItem]
    tags: List[str]

    @property
    def lowercase_name(self):
        return self.name.lower()

    @property
    def n_items(self):
        return len(self.items)

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
    def gather_equivalent(cls, entries):
        """Unify singleton MediaLibraryEntry instances by name and content
        """
        singleton_entries = [e for e in entries if e.n_items == 1]
        proper_entries = [e for e in entries if e.n_items > 1]

        entry_by_id = {}
        entries_by_key = defaultdict(set)
        for entry in entries:
            entry_by_id[entry.id] = entry
            key_tail = tuple(
                (item.name, item.relativeUrl)
                for item in entry.items
            )
            key = (entry.name,) + key_tail
            entries_by_key[key].add(entry.id)

        canonical_entries = [
            cls.unify_equivalent([entry_by_id[id] for id in entry_ids])
            for entry_ids in entries_by_key.values()
        ]

        return sorted(canonical_entries, key=attrgetter("lowercase_name"))


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

    def write_files(self, out_dir):
        for entry in self.entries:
            entry.write_files(out_dir, self.data_from_content_id)

        index_data = [e.as_output_dict() for e in self.entries]
        with (out_dir / "index.json").open("wt") as f_out:
            json.dump(index_data, f_out, indent=2)
