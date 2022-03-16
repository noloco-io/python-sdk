from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport
from noloco.project import Project
from noloco.requests import Command
from noloco.utils import options_without_data


BASE_URL = 'https://api.portals.noloco.io'


class Noloco:
    def __init__(self, account_api_key, portal_name):
        """Initialises a Noloco client.

        Args:
            account_api_key: The Account API Key from your Integrations & API
                Keys settings page.
            portal_name: The name of your Noloco portal.

        Returns:
            A Noloco client.

        Raises:
            NolocoAccountApiKeyError: If your Account API Key is incorrect.
            NolocoProjectApiKeyError: If we cannot fetch you Project API Key.
            NolocoUnknownError: If we are not sure what went wrong.
        """
        # Build the account client that will be used to interact with the
        # project document.
        account_transport = AIOHTTPTransport(
            url=BASE_URL, headers={'Authorization': account_api_key})
        account_client = Client(
            transport=account_transport,
            fetch_schema_from_transport=False)

        # Fetch the project document, lookup and validate the project API key
        # and cache the data types locally.
        self.__project = Project(account_client, BASE_URL, portal_name)

    def create(self, data_type_name, options):
        """Creates a record in a Noloco collection.

        Args:
            data_type_name: The name of the data type the collection is for.
                For example 'user'.
            options: The record to create as the 'data' field and any other
                options; after creating the record in the Noloco collection,
                the created record will be returned along with it's top-level
                fields. If you would like to also return some relationship
                fields you can do them using options. For example:

                {
                    'data': {
                        'firstName': 'Jane',
                        'lastName': 'Doe',
                        'email': 'jane@noloco.io',
                        'company': {
                            'connect': {
                                id: 2
                            }
                        },
                        'profilePicture': [open file]
                    },
                    'include': {
                        'company': {
                            'include': {
                                'usersCollection': True
                            }
                        }
                    }
                }

        Returns:
            The record that was created in the Noloco collection.
        """
        return Command(self.__project) \
            .for_data_type(data_type_name) \
            .with_options(options_without_data(options)) \
            .mutate('create') \
            .value(options['data']) \
            .with_pagination_callback(self.findUnique) \
            .build() \
            .execute()

    def delete(self, data_type_name, id):
        """Deletes a record from a Noloco collection.

        Args:
            data_type_name: The name of the data type the collection is for.
                For example 'user'.
            id: The ID of the record to delete.

        Returns:
            None.
        """
        return Command(self.__project) \
            .for_data_type(data_type_name) \
            .mutate('delete') \
            .with_id_lookup(id) \
            .build() \
            .execute()

    def findMany(self, data_type_name, options={}):
        """Searches a Noloco collection for records matching the provided
        criteria.

        Args:
            data_type_name: The name of the data type the collection is for.
                For example 'user'.
            options: The configuration for the search. Any matching records
                will be returned along with their top-level fields. If you
                would like to also return some relationship fields you can do
                them using options. For example:

                {
                    'after': '...',
                    'before': '...',
                    'first': '...',
                    'include': {
                        'role': True
                    },
                    'order_by': {
                        'direction': 'ASC',
                        'field': 'createdAt'
                    }
                    'where': {
                        'id': {
                            'gt': 5
                        }
                    }
                }

        Returns:
            The result of querying the Noloco collection.
        """
        return Command(self.__project) \
            .for_data_type(data_type_name) \
            .with_options(options) \
            .query('findMany') \
            .with_pagination_callback(self.findMany) \
            .build() \
            .execute()

    def findUnique(self, data_type_name, options):
        """Fetches a record from a Noloco collection that you identify by any
        of its unique fields.

        Args:
            data_type_name: The name of the data type you want to fetch. For
                example 'user'.
            options: The configuration for the lookup. The matching record will
                be returned along with its top-level fields. If you would like
                to also return some relationship fields you can do them using
                options. For example:

                {
                    'include': {
                        'company': True,
                        'role': True
                    }
                    'where': {
                        'id': {
                            'equals': 2
                        }
                    }
                }

        Returns:
            The result of looking up the Noloco record.
        """
        return Command(self.__project) \
            .for_data_type(data_type_name) \
            .with_options(options) \
            .query('findUnique') \
            .with_unique_lookup() \
            .with_pagination_callback(self.findUnique) \
            .build() \
            .execute()

    def update(self, data_type_name, id, options):
        """Updates a record in a collection.

        Args:
            data_type_name: The name of the data type the collection is for.
                For example 'user'.
            id: the ID of the record to update.
            options: The record to update as the 'data' field and any other
                options; after creating the record in the Noloco collection,
                the created record will be returned along with it's top-level
                fields. If you would like to also return some relationship
                fields you can do them using options. For example:

                {
                    'data': {
                        'firstName': 'Jane',
                        'lastName': 'Doe',
                        'email': 'jane@noloco.io',
                        'company': {
                            'connect': {
                                id: 2
                            }
                        },
                        'profilePicture': [open file]
                    },
                    'include': {
                        'role': True
                    }
                }

        Returns:
            The result of updating the Noloco record.
        """
        return Command(self.__project) \
            .for_data_type(data_type_name) \
            .with_options(options_without_data(options)) \
            .mutate('update') \
            .with_id_lookup(id) \
            .value(options['data']) \
            .with_pagination_callback(self.findUnique) \
            .build() \
            .execute()
