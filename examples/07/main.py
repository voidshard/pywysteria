"""
Example07: Search everything
"""

import wysteria


def main():
    client = wysteria.Client()
    with client:
        search = client.search()
        search.params()

        # Although generally not good practice, we don't have to give query args
        # Most likely one should use pagination here!
        # Also note, the server does hard limit the number of results returned
        # by such 'match all' queries ..
        for c in search.find_collections():
            print(c)


if __name__ == "__main__":
    main()
