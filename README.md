# Noloco Python SDK

Our Python SDK provides CRUD operations over your Noloco Collections.

## Installation

The SDK is published on PyPI and can be installed with `pip`.

```
$ pip install noloco
```

## Getting started

The examples here will be based around two example collections, one called `author` and one called `book`.

The `author` collection will have this schema:

```
{
    'firstName': 'TEXT',
    'lastName': 'TEXT'
}
```

The book collection will have the following schema:

```
{
    'title': 'TEXT',
    'author': 'AUTHOR',
    'pageCount': 'INTEGER'
}
```

### Pre-requisites

You will need to know your account API key before you can use the SDK. To find this:
- Open your project dashboard
- Go to the Settings page
- Go to Integrations & API Keys
- Copy your Account API Key

You will also need to know your project name. If you access your site via the Noloco subdomain you can just copy it from the URL as it will be [project-name].noloco.co. If you use a custom domain you will need to look it up:
- Open your project dashboard
- Go to the Settings page
- Go to Domains
- Find the Production subdomain
- This will be [project-name].noloco.co

### Building a client

A client is provided in the SDK through which you can carry out CRUD operations on your collections. You can construct an instance of this client as follows:

```
from noloco.client import Noloco
...
# See pre-requisites above.
account_api_key = ...
project_name = ...
...
client = Noloco(account_api_key, project_name)
```

This construction step might take a few seconds to run. The `Noloco.__init__` method is going to do a few things. Firstly it will use your account API key to lookup your project document, it will then find your project API key from this document and validate it with Noloco. Assuming this is all OK we will cache the data types that exist on your project at the time you constructed your client. If you alter the schema of any data types in your portal, you may notice a slight delay in the next request as we fetch your new data types.

### Creating a record in a collection

To create a new author and then create a new book linked to them you would write the following code:

```
author = client.create('author', {
    'firstName': 'Jane',
    'lastName': 'Doe'
})

book = client.create('book', {
    'title': 'My Biography',
    'author': {
        'connect': {
            'id': author.id
        }
    },
    'pageCount': 500
}, {'include': {'author': True}})
```

You might be wondering what the significance of `{'include': {'author': True}}` is... Whenever we return a record from the API we will always return all the top-level fields (including files) by default. However we do not include relationship fields unless you specifically tell the client to include them in the `options` parameters. Because this call to create a `book` is including `author` in its `options`, when the created `book` is returned, the author relationship will also be included. In an interpreter we can see this:

```
$ print(book)

{
    'id': 1,
    'uuid': ...,
    'createdAt': ...,
    'updatedAt': ...,
    'title': 'My Biography',
    'author': {
        'id': 2,
        'uuid': ...,
        'createdAt': ...,
        'updatedAt': ...,
        'firstName': 'Jane',
        'lastName': 'Doe',
        '__typename': 'Author'
    },
    'pageCount': 500,
    '__typename': 'Book'
}
```

If we had omitted the `include` then the `book` that was returned would have just carried its top-level fields:

```
$ print(book)

{
    'id': ...,
    'uuid': ...,
    'createdAt': ...,
    'updatedAt': ...,
    'title': 'My Biography',
    'pageCount': 500,
    '__typename': 'Book'
}
```

### Reading a single record from a collection

If you know the value of a unique field of a record in a collection then you can read it from the collection:

```
book = client.get('book', {
    'where': {
        'id': {
            'equals': 1
        }
    },
    'include': {
        'author': True
    }
})
```

You can `print` it like we did in the previous example, or you can directly access fields on the result. This is because we wrap all responses in a `Result` class that inherits from `dict`:

```
$ print(book.author.firstName)

Jane
```

### Reading multiple records from a collection

If you do not know the value of a unique field, or you just want to read multiple fields at once then you can do so:

```
book_collection = client.find('book', {
    'where': {
        'pageCount': {
            'lt': 250
        }
    },
    'first': 5,
    'order_by': {
        'direction': 'ASC',
        'field': 'id'
    }
})
```

This will return a `CollectionResult` instance. This is a paginated set of results limited to the value of `first` at a time. You can check the total number of records that match your criteria:

```
$ print(book_collection.total_count)

51
```

You can access the current page of data:

```
$ print(book_collection.data)

[
    {'id': '10', ...},
    {'id': '14', ...},
    {'id': '16', ...},
    {'id': '17', ...},
    {'id': '22', ...},
]
```

We then provide two methods that let you page through the data:

```
$ print(book_collection.next_page().data)

[
    {'id': '23', ...},
    {'id': '27', ...},
    {'id': '29', ...},
    {'id': '30', ...},
    {'id': '38', ...},
]

$ print(book_collection.next_page().previous_page().data)

[
    {'id': '10', ...},
    {'id': '14', ...},
    {'id': '16', ...},
    {'id': '17', ...},
    {'id': '22', ...},
]
```

### Updating a record in a collection

If you know the value of a unique field of a record in a collection then you can update it in the collection:

```
book = client.update('book', {
    'pageCount': 499,
}, {'where': {'id': {'equals': 1}}})
```

You can `print` it like we did in the previous example, or you can directly access fields on the result. This is because we wrap all responses in a `Result` class that inherits from `dict`:

```
$ print(book)

{
    'id': 1,
    'uuid': ...,
    'createdAt': ...,
    'updatedAt': ...,
    'title': 'My Biography',
    'pageCount': 499,
    '__typename': 'Book'
}
```

### Deleting a record from a collection

Finally, if you know the value of a unique field of a record in a collection then you can delete it from the collection:

```
client.delete('book', {
    'where': {
        'id': {
            'equals': 1
        }
    }
})
```
