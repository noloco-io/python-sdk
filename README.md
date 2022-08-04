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
    'data': {
        'firstName': 'Jane',
        'lastName': 'Doe'
    }
})

book = client.create('book', {
    'data': {
        'title': 'My Biography',
        'author': {
            'connect': {
                'id': author.id
            }
        },
        'pageCount': 500
    },
    'include': {
        'author': True
    }
})
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
book = client.findUnique('book', {
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
book_collection = client.findMany('book', {
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
$ print(book_collection)

{
    'total_count': 51,
    'has_previous_page': False,
    'has_next_page': True,
    'data': [
        {'id': '10', ...},
        {'id': '14', ...},
        {'id': '16', ...},
        {'id': '17', ...},
        {'id': '22', ...},
    ]
}
```

We then provide two methods that let you page through the data:

```
$ print(book_collection.next_page().data)

{
    'total_count': 51,
    'has_previous_page': True,
    'has_next_page': True,
    'data': [
        {'id': '23', ...},
        {'id': '27', ...},
        {'id': '29', ...},
        {'id': '30', ...},
        {'id': '38', ...},
    ]
}

$ print(book_collection.next_page().previous_page())

{
    'total_count': 51,
    'has_previous_page': False,
    'has_next_page': True,
    'data': [
        {'id': '10', ...},
        {'id': '14', ...},
        {'id': '16', ...},
        {'id': '17', ...},
        {'id': '22', ...},
    ]
}
```

### Updating a record in a collection

If you know the ID of a record in a collection then you can update it in the collection:

```
book = client.update('book', 1, {
    'data': {
        'pageCount': 200
    },
    'include': {
        'author': True
    }
})
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

Finally, if you know the ID of a record in a collection then you can delete it from the collection:

```
client.delete('book', 1)
```

## Field types

You can use the following table to reference the mapping from Noloco field types onto Python types. For fields that are Python strings requiring a specific format, the format we expect is given here.

| Noloco Field Type | Python Type | Expected Formats           |
|-------------------|-------------|----------------------------|
| Boolean           | bool        |                            |
| Date              | str         | 'YYYY-MM-DDTHH:MM:SS.XXXZ' |
| Decimal           | float       |                            |
| Duration          | str         | 'HH:MM:SS'                 |
| File/Upload       | (see below) |                            |
| Integer           | int         |                            |
| Multiple Option   | list        | ['SCREAMING_SNAKE_CASE']   |
| Single Option     | str         | 'SCREAMING_SNAKE_CASE'     |
| Text              | str         |                            |

### Files

Note that unlike other the types, files have a different Python type depending on whether they are being given as an input or an output.

When you are inputting a file to the SDK to be uploaded, you need to give the SDK an opened file, for example:

```
profile_picture = open('/Users/user/Pictures/profile_picture.jpeg', 'rb')
```

You will need to manage the closing of this file yourself after the SDK is done with it.

When the SDK is outputting a file to you, it will give you a dictionary with information about the file:

```
{
    'id': '...',
    'uuid': '...',
    'fileType': 'IMAGE',
    'url': 'https://app-media.noloco.app/[project-name]/...profile_picture.jpeg',
    'name': '%2FUsers%2Fuser%2FPictures%2Fprofile_picture.jpeg'
}
```

You can use the URL to download the file if you need the contents.
