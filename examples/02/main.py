"""
Example02: Getting children
"""

import wysteria


def main():
    client = wysteria.Client()
    with client:
        tiles = client.get_collection("tiles")

        # get all child items regardless of item_type / variant
        all_items = tiles.get_items()

        # or we can be more specific
        print "--items--"
        for i in tiles.get_items(item_type="tree", variant="oak"):
            print i

        # we can grab the published version of each
        published = []
        print "--versions--"
        for i in all_items:
            published_version = i.get_published()
            published.append(published_version)
            print published_version

        # and we can grab the version resources
        print "--resources--"
        for published_version in published:
            for resource in published_version.get_resources():
                print resource


if __name__ == "__main__":
    main()
