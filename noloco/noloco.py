from exceptions import NolocoAccountApiKeyError, NolocoProjectApiKeyError, \
    NolocoUnknownError
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportQueryError
from queries import PROJECT_API_KEYS_QUERY, QueryBuilder, \
    VALIDATE_API_KEYS_QUERY
import pydash
from utils import gql_args


BASE_URL = 'https://api.nolocolocal.io'


class Noloco:
    def __init__(self, account_api_key, portal_name):
        """Initialises a Noloco client.

        Args:
            account_api_key: The Account API Key from your Integrations & API
                Keys settings page.

        Returns:
            A Noloco client.

        Raises:
            NolocoAccountApiKeyError: If your Account API Key is incorrect.
            NolocoProjectApiKeyError: If we cannot fetch you Project API Key.
            NolocoUnknownError: If we are not sure what went wrong.
        """
        self.__project_name = portal_name
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
            project_api_key = pydash.get(
                project_api_keys_query_result,
                'project.apiKeys.project')
            self.__project_id = pydash.get(
                project_api_keys_query_result, 'project.id')
        except TransportQueryError as err:
            raise NolocoAccountApiKeyError(self.__project_name, err)
        except Exception as err:
            raise NolocoUnknownError(err)

        try:
            validate_api_keys_query_result = self.__account_client.execute(
                gql(VALIDATE_API_KEYS_QUERY),
                variable_values={'projectToken': project_api_key})
            self.__user_id = pydash.get(
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

    def exportCsv(
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
        args = {}

        if after is not None:
            args['after'] = {'type': 'String', 'value': after}
        if before is not None:
            args['before'] = {'type': 'String', 'value': before}
        if first is not None:
            args['first'] = {'type': 'Int', 'value': first}
        if order_by is not None:
            args['order_by'] = {'type': 'OrderBy', 'value': order_by}
        if where is not None:
            whereType = pydash.pascal_case(data_type_name) + 'WhereInput'
            args['where'] = {'type': whereType, 'value': where}

        query = self.__query_builder \
            .build_data_type_collection_csv_export_query(data_type_name, args)

        return self.__project_client.execute(
            gql(query), variable_values=gql_args(args))

    def find(
            self,
            data_type_name,
            include,
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

                {'lastName': True, 'firstName': True, 'role': {'name': True}}
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
        args = {}

        if after is not None:
            args['after'] = {'type': 'String', 'value': after}
        if before is not None:
            args['before'] = {'type': 'String', 'value': before}
        if first is not None:
            args['first'] = {'type': 'Int', 'value': first}
        if order_by is not None:
            args['order_by'] = {'type': 'OrderBy', 'value': order_by}
        if where is not None:
            whereType = pydash.pascal_case(data_type_name) + 'WhereInput'
            args['where'] = {'type': whereType, 'value': where}

        query = self.__query_builder.build_data_type_collection_query(
            data_type_name, include, args)

        return self.__project_client.execute(
            gql(query), variable_values=gql_args(args))

    def get(self, data_type_name, include, id=None, uuid=None, **kwargs):
        """Fetches the record of a collection you identify.

        Args:
            data_type_name: The name of the data type you want to fetch. For
                example 'user'.
            include: The schema that you would like back from Noloco. For
                example:

                {'lastName': True, 'firstName': True, 'role': {'name': True}}
            id: The ID of the record to fetch.
            uuid: The UUID of the record to fetch.
            **kwargs: Custom identifiers of the record to fetch. For example:

                email='team@noloco.io'

        Returns:
            The result of looking up the Noloco record.
        """
        if id is not None:
            kwargs['id'] = {'type': 'ID', 'value': id}
        if uuid is not None:
            kwargs['uuid'] = {'type': 'String', 'value': uuid}

        query = self.__query_builder.build_data_type_query(
            data_type_name, include, kwargs)
        print(query)

        result = self.__project_client.execute(
            gql(query), variable_values=gql_args(kwargs))
        print(result)
