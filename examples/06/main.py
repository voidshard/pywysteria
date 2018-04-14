"""
Example06: Limits & offsets
"""

import wysteria


def main():
    client = wysteria.Client()
    with client:
        search = client.search()
        search.params(name="default")

        for i in range(0, 2):
            found = search.find_resources(limit=1, offset=i)
            print("found", len(found), "=>", found[0].name, found[0].location)


if __name__ == "__main__":
    main()
