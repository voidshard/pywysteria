"""
Example03: Searching for things
"""

import wysteria


def main():
    client = wysteria.Client()
    with client:
        # create new search object
        search = client.search()

        # set
        search.params(item_type="tree", item_variant="oak")

        # find any & all matching items
        print "Items of type 'tree' and variant 'oak'"
        items = search.find_items()
        for item in items:
            print item

        # You can add more query params to find more matches at a time.
        # Better than doing lots of single queries if you can manage it.
        # create new search object
        search = client.search()

        # build up a search query
        # This is understood as
        # (type "tree" AND variant oak) OR (type tree AND variant pine)
        print "items of type tree and variant oak or pine"
        search.params(item_type="tree", item_variant="oak")
        search.params(item_type="tree", item_variant="pine")

        # grab matching items
        items = search.find_items()
        for item in items:
            print item


if __name__ == "__main__":
    main()
