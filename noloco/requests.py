from gql import gql
from gql.transport.exceptions import TransportQueryError
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
from pydash import pascal_case


class Command:
    def __init__(self, project):
        self.project = project
        self.__mutation_builder = MutationBuilder()
        self.__query_builder = QueryBuilder()

    def for_data_type(self, data_type_name):
        self.data_type_name = data_type_name
        return self

    def with_lookup(self, lookup_id_type='ID'):
        self.lookup_id_type = lookup_id_type

    def with_options(self, options):
        self.options = options
        return self

    def with_pagination_callback(self, pagination_callback):
        self.pagination_callback = pagination_callback
        return self

    def value(self, value):
        self.value = value
        return self

    def mutate(self, mutation):
        self.mutation = mutation
        self.result_name = mutation + pascal_case(self.data_type_name)
        return self

    def query(self, query):
        self.query = query
        self.result_name = self.data_type_name + result_name_suffix(query)
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

            if self.mutation is not None and self.value is not None:
                mutation_args = self \
                    .__mutation_builder \
                    .build_data_type_mutation_args(
                        data_type,
                        data_types,
                        self.value)
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

            if self.query is not None:
                document = self.__query_builder.build_data_type_query(
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
        except TransportQueryError:
            if retry:
                self.__command.project.refresh()
                return self.__command.build().execute(retry=False)
            else:
                raise
