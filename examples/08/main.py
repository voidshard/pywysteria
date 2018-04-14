"""
Example08: Sub collections
"""

import wysteria


def main():
    client = wysteria.Client()
    with client:
        collection = client.create_collection("foo")
        foo_maps = collection.create_collection("maps")

        print(collection)
        print(foo_maps)

        print("Parent of foo_maps", foo_maps.get_parent())


if __name__ == "__main__":
    main()
