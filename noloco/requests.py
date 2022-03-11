from gql import gql
from gql.transport.exceptions import TransportQueryError
from noloco.constants import GRAPHQL_VALIDATION_FAILED
from noloco.exceptions import (
    NolocoDataTypeNotFoundError,
    NolocoFieldNotFoundError)
from noloco.mutations import MutationBuilder
from noloco.queries import QueryBuilder
from noloco.results import Result
from noloco.utils import (
    annotate_collection_args,
    change_where_to_lookup,
    find_data_type_by_name,
    flatten_args,
    gql_args,
    has_files,
    result_name_suffix)
from pydash import (
    get,
    pascal_case)


class Command:
    def __init__(self, project):
        self.project = project
        self.__mutation_builder = MutationBuilder()
        self.__query_builder = QueryBuilder()

        self.data_type_name = None
        self.lookup_id_type = None
        self.mutation = None
        self.new_value = None
        self.options = None
        self.pagination_callback = None
        self.query_type = None
        self.result_name = None

    def for_data_type(self, data_type_name):
        self.data_type_name = data_type_name
        return self

    def with_lookup(self, lookup_id_type='ID'):
        self.lookup_id_type = lookup_id_type
        return self

    def with_options(self, options):
        self.options = options
        return self

    def with_pagination_callback(self, pagination_callback):
        self.pagination_callback = pagination_callback
        return self

    def value(self, new_value):
        self.new_value = new_value
        return self

    def mutate(self, mutation):
        self.mutation = mutation
        self.result_name = mutation + pascal_case(self.data_type_name)
        return self

    def query(self, query_type):
        self.query_type = query_type
        self.result_name = self.data_type_name + result_name_suffix(query_type)
        return self

    def build(self, retry=True):
        try:
            data_types = self.project.data_types
            data_type = find_data_type_by_name(self.data_type_name, data_types)

            typed_options = annotate_collection_args(
                data_type,
                data_types,
                self.options)

            if self.lookup_id_type is not None:
                typed_options = change_where_to_lookup(
                    data_type,
                    typed_options,
                    self.lookup_id_type)

            if self.new_value is not None:
                mutation_args = self \
                    .__mutation_builder \
                    .build_data_type_mutation_args(
                        data_type,
                        data_types,
                        self.new_value)
                upload_files = has_files(mutation_args)
                typed_options.update(mutation_args)
            else:
                upload_files = False

            flattened_options = flatten_args(self.result_name, typed_options)

            if self.mutation is not None:
                document = self.__mutation_builder.build_data_type_mutation(
                    self.mutation,
                    data_type,
                    data_types,
                    typed_options,
                    flattened_options)

            if self.query_type is not None:
                document = self.__query_builder.build_data_type_query(
                    self.query_type,
                    self.result_name,
                    data_type,
                    data_types,
                    typed_options,
                    flattened_options)

            return BuiltCommand(
                self,
                gql(document),
                gql_args(flattened_options),
                upload_files,
                self.pagination_callback)
        except (NolocoDataTypeNotFoundError, NolocoFieldNotFoundError):
            if retry:
                self.project.refresh()
                self.build(retry=False)
            else:
                raise


class BuiltCommand:
    def __init__(
            self,
            command,
            document,
            variable_values,
            upload_files,
            pagination_callback):
        self.__command = command
        self.__document = document
        self.__variable_values = variable_values
        self.__upload_files = upload_files
        self.__pagination_callback = pagination_callback

    def execute(self, retry=True):
        try:
            raw_result = self.__command.project.client.execute(
                self.__document,
                variable_values=self.__variable_values,
                upload_files=self.__upload_files)

            return Result.build(
                self.__command.data_type_name,
                self.__command.result_name,
                raw_result,
                self.__command.options,
                self.__pagination_callback)
        except TransportQueryError as err:
            if get(err, 'extensions.code') == GRAPHQL_VALIDATION_FAILED and retry:
                self.__command.project.refresh()
                return self.__command.build().execute(retry=False)
            else:
                raise
