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

entries = [
    block_singleton,
    MLib.MediaLibraryEntry(1003, "fruit", [banana, apple], ["fruit", "food"]),
    MLib.MediaLibraryEntry(1004, "animals", [cow, horse], ["farm", "animal"]),
    other_block_singleton,
]
