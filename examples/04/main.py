"""
Example04: Searching via builtin facets & using links
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

        # pull out all linked versions, regardless of their names
        result = forest_version.get_linked()

        # if you recall, we made two links from forest01 both named "input"
        print "All linked versions (link name: version)"
        for link_name, versions in result.iteritems():
            for version in versions:
                print link_name, version

        # On the other hand, we could just request linked versions named "input"
        print "linked 'input' versions"
        for version in forest_version.get_linked_by_name("input"):
            print version


if __name__ == "__main__":
    main()
