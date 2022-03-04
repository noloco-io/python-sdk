from exceptions import NolocoAccountApiKeyError, NolocoProjectApiKeyError, \
    NolocoUnknownError
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportQueryError
import queries
import pydash


BASE_URL = 'https://api.nolocolocal.io'


class Noloco:
    def __init__(self, account_api_key, portal_name):
        self.project_name = portal_name

        account_transport = AIOHTTPTransport(
            url=BASE_URL, headers={'Authorization': account_api_key})
        self.account_client = Client(
            transport=account_transport,
            fetch_schema_from_transport=True)

        try:
            project_api_keys_query_result = self.account_client.execute(
                gql(queries.project_api_keys_query),
                variable_values={'projectId': portal_name})
            project_api_key = pydash.get(
                project_api_keys_query_result,
                'project.apiKeys.project')
            self.project_id = pydash.get(
                project_api_keys_query_result, 'project.id')
        except TransportQueryError as err:
            raise NolocoAccountApiKeyError(self.project_name, err)
        except Exception as err:
            raise NolocoUnknownError(err)

        try:
            validate_api_keys_query_result = self.account_client.execute(
                gql(queries.validate_api_keys_query),
                variable_values={'projectToken': project_api_key})
            self.user_id = pydash.get(
                validate_api_keys_query_result,
                'validateApiKeys.user.id')
        except TransportQueryError as err:
            raise NolocoProjectApiKeyError(self.project_name, err)
        except Exception as err:
            raise NolocoUnknownError(err)

        project_transport = AIOHTTPTransport(
            url=f'{BASE_URL}/data/{self.project_name}',
            headers={'Authorization': project_api_key})
        self.project_client = Client(
            transport=project_transport,
            fetch_schema_from_transport=True)
