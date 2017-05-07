"""
Example01: Creating, publishing & linking
  (Created objects here are used in following examples)
"""

import wysteria


def main():
    client = wysteria.Client()
    with client:
        tiles = client.create_collection("tiles")
        oak = tiles.create_item("tree", "oak")
        oak01 = oak.create_version()

        oak01.add_resource("default", "png", "url://images/oak01.png")
        oak01.add_resource("stats", "xml", "/path/to/file.xml")

        pine = tiles.create_item("tree", "pine")
        pine01 = pine.create_version({"foo": "bar"})
        pine01.add_resource("default", "png", "/path/to/pine01.png")

        maps = client.create_collection("maps")
        forest = maps.create_item("2dmap", "forest")
        forest01 = forest.create_version()

        oak01.publish()
        pine01.publish()

        forest01.link_to("input", oak01)
        forest01.link_to("input", pine01)

        print "--collections"
        print forest
        print tiles
        print "--items--"
        print oak
        print pine
        print "--versions--"
        print oak01
        print pine01


if __name__ == "__main__":
    main()
