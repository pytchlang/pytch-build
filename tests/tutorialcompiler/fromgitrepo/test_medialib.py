import pytchbuild.tutorialcompiler.medialib as MLib


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


class TestMediaLibrary:
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
