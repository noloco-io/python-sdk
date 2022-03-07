from datetime import datetime
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
from noloco.utils import (
    close_files,
    collection_args,
    find_data_type_by_name,
    gql_args,
    has_files,
    open_files,
    unique_args)
from pydash import get


BASE_URL = 'https://api.nolocolocal.io'


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

    def create(self, data_type_name, args, include={}):
        """Creates a record in a collection.

        Args:
            data_type_name: The name of the data type the collection is for.
                For example 'user'.
            args: The record to create. For example:

                {
                    firstName: 'Jane',
                    lastName: 'Doe',
                    email: 'jane@noloco.io',
                    company: {
                        connect: {
                            id: 2
                        }
                    },
                    profilePicture: {
                        upload: {
                            file: '~/Pictures/profile.jpeg'
                        }
                    }
                }
            include: The schema that you would like back from Noloco. For
                example:

                {
                    'role': {
                        'include': {
                            'name': True
                        }
                    }
                }

        Returns:
            The result of creating the Noloco record.
        """
        data_types = self.__get_data_types()
        data_type = find_data_type_by_name(data_type_name, data_types)

        args = self.__mutation_builder.build_data_type_mutation_args(
            data_type,
            data_types,
            args)
        args = open_files(args)

        mutation = self.__mutation_builder.build_data_type_mutation(
            'create',
            data_type,
            data_types,
            include,
            args)

        result = self.__project_client.execute(
            gql(mutation),
            variable_values=gql_args(args),
            upload_files=has_files(args))
        close_files(args)
        return result

    def delete(self, data_type_name, id, include={}):
        """Deletes a member of a collection.

        Args:
            data_type_name: The name of the data type the collection is for.
                For example 'user'.
            id: The ID of the record to delete.
            include: The schema that you would like back from Noloco. For
                example:

                {
                    'role': {
                        'include': {
                            'name': True
                        }
                    }
                }

        Returns:
            The result of deleting the Noloco record.
        """
        data_types = self.__get_data_types()
        data_type = find_data_type_by_name(data_type_name, data_types)

        args = {'id': {'type': 'ID!', 'value': id}}

        mutation = self.__mutation_builder.build_data_type_mutation(
            'delete',
            data_type,
            data_types,
            include,
            args)

        return self.__project_client.execute(
            gql(mutation), variable_values=gql_args(args))

    def export_csv(
            self,
            data_type_name,
            after=None,
            before=None,
            first=None,
            order_by=None,
            where=None):
        """Exports the members of a collection meeting the criteria you
            specified to a base64 string.

        Args:
            data_type_name: The name of the data type the collection is for.
                For example 'user'.
            after: The cursor to paginate results after.
            before: The cursor to paginate results before.
            first: The number of results to paginate to.
            order_by: The order to sort results in. For example:

                { 'direction': 'ASC', field: 'createdAt' }
            where: The filter that you would like to apply to the collection.
                For example:

                { 'roleId': { 'equals': 2 } }

        Returns:
            The base64 encoded string result of querying the Noloco collection
            and exporting it as a CSV.
        """
        args = collection_args(
            data_type_name, after, before, first, order_by, where)

        query = self.__query_builder \
            .build_data_type_collection_csv_export_query(data_type_name, args)

        return self.__project_client.execute(
            gql(query), variable_values=gql_args(args))

    def find(
            self,
            data_type_name,
            include={},
            after=None,
            before=None,
            first=None,
            order_by=None,
            where=None):
        """Finds the members of a collection meeting the criteria you
            specified.

        Args:
            data_type_name: The name of the data type the collection is for.
                For example 'user'.
            include: The schema that you would like back from Noloco. For
                example:

                {
                    'lastName': True,
                    'firstName': True,
                    'role': {
                        'include': {
                            'name': True
                        }
                    }
                }
            after: The cursor to paginate results after.
            before: The cursor to paginate results before.
            first: The number of results to paginate to.
            order_by: The order to sort results in. For example:

                { 'direction': 'ASC', field: 'createdAt' }
            where: The filter that you would like to apply to the collection.
                For example:

                { 'roleId': { 'equals': 2 } }

        Returns:
            The result of querying the Noloco collection.
        """
        data_types = self.__get_data_types()
        data_type = find_data_type_by_name(data_type_name, data_types)

        args = collection_args(
            data_type_name, after, before, first, order_by, where)

        query = self.__query_builder.build_data_type_collection_query(
            data_type, data_types, include, args)

        return self.__project_client.execute(
            gql(query), variable_values=gql_args(args))

    def get(self, data_type_name, include={}, id=None, uuid=None, **kwargs):
        """Fetches the record of a collection you identify.

        Args:
            data_type_name: The name of the data type you want to fetch. For
                example 'user'.
            include: The schema that you would like back from Noloco. For
                example:

                {
                    'lastName': True,
                    'firstName': True,
                    'role': {
                        'include': {
                            'name': True
                        }
                    }
                }
            id: The ID of the record to fetch.
            uuid: The UUID of the record to fetch.
            **kwargs: Custom unique identifiers of the record to fetch. For
                example:

                email='team@noloco.io'

        Returns:
            The result of looking up the Noloco record.
        """
        data_types = self.__get_data_types()
        data_type = find_data_type_by_name(data_type_name, data_types)

        args = unique_args(data_type, kwargs)
        if id is not None:
            args['id'] = {'type': 'ID', 'value': id}
        if uuid is not None:
            args['uuid'] = {'type': 'String', 'value': uuid}

        query = self.__query_builder.build_data_type_query(
            data_type, data_types, include, args)

        return self.__project_client.execute(
            gql(query), variable_values=gql_args(args))

    def update(self, data_type_name, id, args, include={}):
        """Updates a record in a collection.

        Args:
            data_type_name: The name of the data type the collection is for.
                For example 'user'.
            id: The ID of the record to update.
            args: The record to update. For example:

                {
                    firstName: 'Jane',
                    lastName: 'Doe',
                    email: 'jane@noloco.io',
                    company: {
                        connect: {
                            id: 2
                        }
                    },
                    profilePicture: {
                        upload: {
                            file: '~/Pictures/profile.jpeg'
                        }
                    }
                }
            include: The schema that you would like back from Noloco. For
                example:

                {
                    'role': {
                        'include': {
                            'name': True
                        }
                    }
                }

        Returns:
            The result of updating the Noloco record.
        """
        data_types = self.__get_data_types()
        data_type = find_data_type_by_name(data_type_name, data_types)

        args = self.__mutation_builder.build_data_type_mutation_args(
            data_type,
            data_types,
            args)
        args['id'] = {'type': 'ID!', 'value': id}
        args = open_files(args)

        mutation = self.__mutation_builder.build_data_type_mutation(
            'update',
            data_type,
            data_types,
            include,
            args)

        result = self.__project_client.execute(
            gql(mutation),
            variable_values=gql_args(args),
            upload_files=has_files(args))
        close_files(args)
        return result
