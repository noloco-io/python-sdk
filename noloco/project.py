from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportQueryError
from noloco.exceptions import (
    NolocoAccountApiKeyError,
    NolocoProjectApiKeyError,
    NolocoUnknownError)
from noloco.queries import (
    PROJECT_DOCUMENT_QUERY,
    VALIDATE_API_KEYS_QUERY)
from pydash import get


class Project:
    def __init__(self, account_client, base_url, name):
        self.__account_client = account_client
        self.__base_url = base_url
        self.__project_name = name

        self.refresh()

    def refresh(self):
        # Try to validate the account API key and fetch the project API key.
        try:
            project_document_query_result = self.__account_client.execute(
                gql(PROJECT_DOCUMENT_QUERY),
                variable_values={'projectId': self.__project_name})
            project_api_key = get(
                project_document_query_result,
                'project.apiKeys.project')
            self.data_types = get(
                project_document_query_result, 'project.dataTypes')
        except TransportQueryError as err:
            raise NolocoAccountApiKeyError(self.__project_name, err)
        except Exception as err:
            raise NolocoUnknownError(err)

        # Try to validate the project API key.
        try:
            self.__account_client.execute(
                gql(VALIDATE_API_KEYS_QUERY),
                variable_values={'projectToken': project_api_key})
        except TransportQueryError as err:
            raise NolocoProjectApiKeyError(self.__project_name, err)
        except Exception as err:
            raise NolocoUnknownError(err)

        # Build the project client that will be used to interact with
        # collections.
        project_transport = AIOHTTPTransport(
            url=f'{self.__base_url}/data/{self.__project_name}',
            headers={'Authorization': project_api_key})
        self.client = Client(
            transport=project_transport,
            fetch_schema_from_transport=False)
