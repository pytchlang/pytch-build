from pathlib import Path

import pytchbuild.tutorialcompiler.medialib as MLib
import pytchbuild.tutorialcompiler.fromgitrepo.tutorial_history as TH


def mkItem(name):
    return MLib.MediaLibraryItem(name, f"{name}.jpg", [200, 120])


banana = mkItem("banana")
apple = mkItem("apple")
cow = mkItem("cow")
horse = mkItem("horse")
block = mkItem("block")

block_singleton = MLib.MediaLibraryEntry(1001, "block", [block], ["block"])
other_block_singleton = MLib.MediaLibraryEntry(1002, "block", [block], ["cube"])
fruit_entry = MLib.MediaLibraryEntry(1003, "fruit", [banana, apple], ["fruit", "food"])

entries = [
    block_singleton,
    fruit_entry,
    MLib.MediaLibraryEntry(1004, "animals", [cow, horse], ["farm", "animal"]),
    other_block_singleton,
]


class TestMediaLibraryEntry:
    def test_as_output_dict(self):
        got_dict = entries[1].as_output_dict()
        exp_dict = {
            "id": 1003,
            "name": "fruit",
            "tags": ["fruit", "food"],
            "items": [
                {
                    "name": "banana",
                    "relativeUrl": "banana.jpg",
                    "size": [200, 120],
                },
                {
                    "name": "apple",
                    "relativeUrl": "apple.jpg",
                    "size": [200, 120],
                },
            ],
        }
        assert got_dict == exp_dict

    def test_unify_equivalent(self):
        unify_equiv = MLib.MediaLibraryEntry.unify_equivalent

        unified_group = unify_equiv([block_singleton, other_block_singleton])
        assert unified_group.id == 1001  # from first input block
        assert unified_group.name == "block"
        assert len(unified_group.items) == 1
        assert unified_group.items[0].relativeUrl == "block.jpg"
        assert unified_group.tags == ["block", "cube"]

        assert unify_equiv([fruit_entry]) == fruit_entry

    def test_gather_equivalent(self):
        cgroups = MLib.MediaLibraryEntry.gather_equivalent(entries)
        assert len(cgroups) == 3
        assert cgroups[0].name == "animals"
        assert cgroups[0].n_items == 2
        assert cgroups[0].tags == ["farm", "animal"]
        assert cgroups[1].name == "block"
        assert cgroups[1].n_items == 1
        assert cgroups[1].items[0].relativeUrl == "block.jpg"
        assert cgroups[1].tags == ["block", "cube"]
        assert cgroups[2].name == "fruit"
        assert cgroups[2].n_items == 2
        assert cgroups[2].tags == ["fruit", "food"]

    def test_n_items(self):
        assert [e.n_items for e in entries] == [1, 2, 2, 1]


class TestMediaLibraryItem:
    def test_from_project_asset(self):
        my_dir = Path(__file__).parent.resolve()
        with open(f"{my_dir}/fixtures/rectangle.png", "rb") as f_in:
            file_data = f_in.read()
        asset = TH.Asset("project-assets/images/rectangle.png", file_data)
        item = MLib.MediaLibraryItem.from_project_asset(asset)
        assert item.name == "rectangle.png"
        assert item.relativeUrl.endswith("3d610f3c7257a7137137ca2219ba1f0a.png")
        assert item.size == [80, 40]
