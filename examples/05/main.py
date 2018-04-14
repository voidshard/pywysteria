"""
Example05: Updating facets
"""

import wysteria


def main():
    client = wysteria.Client()
    with client:
        search = client.search()

        # Wysteria will have added some facets auto-magically for us,
        # and it pays when searching for Versions to be as specific as possible
        search.params(facets={
            wysteria.FACET_COLLECTION: "maps",
            wysteria.FACET_ITEM_TYPE: "2dmap",
            wysteria.FACET_ITEM_VARIANT: "forest",
        })

        # grab the version we made earlier
        forest_version = search.find_versions()[0]

        # we can also add more facets after object creation so you can
        # search for custom fields. The idea is to keep these small, metadata,
        # tags and short strings.
        forest_version.update_facets(publisher="batman")
        print("metadata added")


if __name__ == "__main__":
    main()
