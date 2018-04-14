# pywysteria

Python3 client for open source asset versioning and publishing system [wysteria](https://github.com/voidshard/wysteria)


### Basic Usage
##### Creating, publishing, linking
```python

import wysteria

# connect
client = wysteria.Client()
    
with client:
    # create collection named "tiles"    
    tiles = client.create_collection("tiles")
    
    # create sub item for an oak tree
    oak = tiles.create_item("tree", "oak")
    
    # create the next version (#1)
    oak01 = oak.create_version()

    # add some resources to our new version
    oak01.add_resource("default", "png", "url://images/oak01.png")
    oak01.add_resource("stats", "xml", "/path/to/file.xml")

    # create a pine item, version & resource
    pine = tiles.create_item("tree", "pine")
    pine01 = pine.create_version({"foo": "bar"})
    pine01.add_resource("default", "png", "/path/to/pine01.png")

    # mark these as published
    oak01.publish()
    pine01.publish()

    # create the next 
    oas02 = oak.create_version()
    
    # link our tree versions to each other
    oak01.link_to("foobar", pine01)
```    

##### Searching
```python
import wysteria

# connect
client = wysteria.Client()
    
with client:
    # create new search object
    search = client.search()

    # set some params to search for
    search.params(item_type="tree", item_variant="oak")

    # find any & all matching items
    print("Items of type 'tree' and variant 'oak'")
    items = search.find_items()
```

For more & more complicated examples please see the examples folder. 

More information available over on the main repo for [wysteria](https://github.com/voidshard/wysteria)



#### Requires

- Nats client: https://github.com/nats-io/asyncio-nats
- Config file parser: https://pypi.python.org/pypi/configparser
