from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportQueryError
from noloco.exceptions import (
    NolocoAccountApiKeyError,
    NolocoProjectApiKeyError,
    NolocoUnknownError)
from noloco.mutations import MutationBuilder
from noloco.queries import (
    PROJECT_API_KEYS_QUERY,
    PROJECT_DATA_TYPES_QUERY,
    QueryBuilder,
    VALIDATE_API_KEYS_QUERY)
from noloco.results import Result
from noloco.utils import (
    annotate_collection_args,
    change_where_to_lookup,
    find_data_type_by_name,
    flatten_args,
    gql_args,
    has_files)
from pydash import (
    get,
    pascal_case)


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
        self.__project_name = portal_name
        self.__mutation_builder = MutationBuilder()
        self.__query_builder = QueryBuilder()

        account_transport = AIOHTTPTransport(
            url=BASE_URL, headers={'Authorization': account_api_key})
        self.__account_client = Client(
            transport=account_transport,
            fetch_schema_from_transport=True)

        try:
            project_api_keys_query_result = self.__account_client.execute(
                gql(PROJECT_API_KEYS_QUERY),
                variable_values={'projectId': portal_name})
            project_api_key = get(
                project_api_keys_query_result,
                'project.apiKeys.project')
            self.__project_id = get(
                project_api_keys_query_result, 'project.id')
        except TransportQueryError as err:
            raise NolocoAccountApiKeyError(self.__project_name, err)
        except Exception as err:
            raise NolocoUnknownError(err)

        try:
            validate_api_keys_query_result = self.__account_client.execute(
                gql(VALIDATE_API_KEYS_QUERY),
                variable_values={'projectToken': project_api_key})
            self.__user_id = get(
                validate_api_keys_query_result,
                'validateApiKeys.user.id')
        except TransportQueryError as err:
            raise NolocoProjectApiKeyError(self.__project_name, err)
        except Exception as err:
            raise NolocoUnknownError(err)

        project_transport = AIOHTTPTransport(
            url=f'{BASE_URL}/data/{self.__project_name}',
            headers={'Authorization': project_api_key})
        self.__project_client = Client(
            transport=project_transport,
            fetch_schema_from_transport=True)

    def __get_data_types(self):
        project_with_data_types = self.__account_client.execute(
            gql(PROJECT_DATA_TYPES_QUERY),
            variable_values={'projectId': self.__project_name})

        project_data_types = get(
            project_with_data_types, 'project.dataTypes')

        return project_data_types

    def create(self, data_type_name, value, options={}):
        """Creates a record in a Noloco collection.

        Args:
            data_type_name: The name of the data type the collection is for.
                For example 'user'.
            value: The record to create. For example:

                {
                    'firstName': 'Jane',
                    'lastName': 'Doe',
                    'email': 'jane@noloco.io',
                    'company': {
                        'connect': {
                            id: 2
                        }
                    },
                    'profilePicture': [open file]
                }
            options: After creating the record in the Noloco collection, the
                created record will be returned along with it's top-level
                fields. If you would like to also return some relationship
                fields you can do them using options. For example:

                {
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
        data_types = self.__get_data_types()
        data_type = find_data_type_by_name(data_type_name, data_types)

        # Based on the value provided to update, derive the arguments that will
        # be used on the mutation.
        mutation_args = self.__mutation_builder.build_data_type_mutation_args(
            data_type,
            data_types,
            value)

        # Based on the options provided, derive the response options.
        typed_options = annotate_collection_args(
            data_type,
            data_types,
            options)

        # Join the mutation arguments with the response options.
        typed_options.update(mutation_args)

        # Flatten the options.
        mutation_type = 'create'
        mutation_name = mutation_type + pascal_case(data_type_name)
        flattened_options = flatten_args(mutation_name, typed_options)

        # Build the mutation.
        mutation = self.__mutation_builder.build_data_type_mutation(
            mutation_type,
            data_type,
            data_types,
            typed_options,
            flattened_options)

        # Execute the mutation and return the result.
        raw_result = self.__project_client.execute(
            gql(mutation),
            variable_values=gql_args(flattened_options),
            upload_files=has_files(mutation_args))

        return Result.build(
            data_type_name,
            mutation_name,
            raw_result,
            options,
            self.get)

    def delete(self, data_type_name, options={}):
        """Deletes a record from a Noloco collection.

        Args:
            data_type_name: The name of the data type the collection is for.
                For example 'user'.
            options: The configuration for the deletion. At a minimum this must
                identify the record to be deleted by any of its unique fields.:

                {
                    'where': {
                        'id': {
                            'equals': 2
                        }
                    }
                }

        Returns:
            None.
        """
        data_types = self.__get_data_types()
        data_type = find_data_type_by_name(data_type_name, data_types)

        # Based on the options provided, derive the response options and
        # configure the unique field lookup.
        typed_options = annotate_collection_args(
            data_type,
            data_types,
            options)
        typed_options = change_where_to_lookup(
            data_type,
            typed_options,
            id_type='ID!')

        # Flatten the options.
        mutation_type = 'delete'
        mutation_name = mutation_type + pascal_case(data_type_name)
        flattened_options = flatten_args(mutation_name, typed_options)

        # Build the mutation.
        mutation = self.__mutation_builder.build_data_type_mutation(
            'delete',
            data_type,
            data_types,
            typed_options,
            flattened_options)

        # Execute the mutation and return the result.
        raw_result = self.__project_client.execute(
            gql(mutation), variable_values=gql_args(flattened_options))

        return raw_result[mutation_name]

    def find(self, data_type_name, options={}):
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
        data_types = self.__get_data_types()
        data_type = find_data_type_by_name(data_type_name, data_types)

        # Based on the options provided, derive the search and response
        # options.
        typed_options = annotate_collection_args(
            data_type,
            data_types,
            options)

        # Flatten the options.
        query_name = data_type_name + 'Collection'
        flattened_options = flatten_args(query_name, typed_options)
        # Build the query.
        query = self.__query_builder.build_data_type_collection_query(
            data_type, data_types, typed_options, flattened_options)

        # Execute the query and return the result.
        raw_result = self.__project_client.execute(
            gql(query),
            variable_values=gql_args(flattened_options))

        return Result.build(
            data_type_name,
            query_name,
            raw_result,
            options,
            self.find)

    def get(self, data_type_name, options={}):
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
        data_types = self.__get_data_types()
        data_type = find_data_type_by_name(data_type_name, data_types)

        # Based on the options provided, derive the response options and
        # configure the unique field lookup.
        typed_options = annotate_collection_args(
            data_type,
            data_types,
            options)
        typed_options = change_where_to_lookup(data_type, typed_options)

        # Flatten the options.
        flattened_options = flatten_args(
            data_type_name,
            typed_options)

        # Build the query.
        query = self.__query_builder.build_data_type_query(
            data_type, data_types, typed_options, flattened_options)

        # Execute the query and return the result.
        raw_result = self.__project_client.execute(
            gql(query), variable_values=gql_args(flattened_options))

        return Result.build(
            data_type_name,
            data_type_name,
            raw_result,
            options,
            self.get)

    def update(self, data_type_name, value, options={}):
        """Updates a record in a collection.

        Args:
            data_type_name: The name of the data type the collection is for.
                For example 'user'.
            value: The record to update. For example:

                {
                    'firstName': 'Jane',
                    'lastName': 'Doe',
                    'email': 'jane@noloco.io',
                    'company': {
                        'connect': {
                            id: 2
                        }
                    },
                    'profilePicture': [open file]
                }
            options: The schema that you would like back from Noloco. For
                example:

                {
                    'include': {
                        'role': True
                    }
                    'where': {
                        'id': {
                            'equals': 2
                        }
                    }
                }

        Returns:
            The result of updating the Noloco record.
        """
        data_types = self.__get_data_types()
        data_type = find_data_type_by_name(data_type_name, data_types)

        # Based on the value provided to update, derive the arguments that will
        # be used on the mutation.
        mutation_args = self.__mutation_builder.build_data_type_mutation_args(
            data_type,
            data_types,
            value)

        # Based on the options provided, derive the response options and
        # configure the unique field lookup.
        typed_options = annotate_collection_args(
            data_type,
            data_types,
            options)
        typed_options = change_where_to_lookup(
            data_type,
            typed_options,
            id_type='ID!')

        # Join the mutation arguments with the lookup and response options.
        typed_options.update(mutation_args)

        # Flatten the options to be added to the top level of the mutation.
        mutation_type = 'update'
        mutation_name = mutation_type + pascal_case(data_type_name)
        flattened_options = flatten_args(mutation_name, typed_options)

        mutation = self.__mutation_builder.build_data_type_mutation(
            mutation_type,
            data_type,
            data_types,
            typed_options,
            flattened_options)

        raw_result = self.__project_client.execute(
            gql(mutation),
            variable_values=gql_args(flattened_options),
            upload_files=has_files(mutation_args))

        return Result.build(
            data_type_name,
            mutation_name,
            raw_result,
            options,
            self.get)
