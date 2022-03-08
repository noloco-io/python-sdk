from noloco.fields import DataTypeFieldsBuilder
from noloco.utils import flatten_collection_args, flatten_operation_args


PROJECT_API_KEYS_QUERY = '''query ($projectId: String!) {
  project(projectId: $projectId) {
    id
    name
    apiKeys {
      user
      project
      __typename
    }
    __typename
  }
}'''


PROJECT_DATA_TYPES_QUERY = '''query ($projectId: String!) {
  project(projectId: $projectId) {
    id
    name
    dataTypes {
      id
      name
      display
      internal
      fields {
        id
        name
        display
        type
        unique
        relationship
        reverseDisplayName
        reverseName
        options {
          id
          name
          display
          __typename
        }
        __typename
      }
      __typename
    }
    __typename
  }
}'''


VALIDATE_API_KEYS_QUERY = '''query ($projectToken: String!) {
  validateApiKeys(projectToken: $projectToken) {
    user {
      id
      email
      __typename
    }
    projectName
    __typename
  }
}'''


DATA_TYPE_QUERY = '''query{query_args} {{
  {data_type_fragment}
}}'''


DATA_TYPE_COLLECTION_CSV_EXPORT_QUERY = '''query{query_args} {{
  {data_type_name}CsvExport{data_type_args} {{
    base64
  }}
}}'''


DATA_TYPE_COLLECTION_QUERY = '''query{query_args} {{
  {data_type_collection_fragment}
}}'''


class QueryBuilder:
    def __init__(self):
        self.fields_builder = DataTypeFieldsBuilder()

    def build_data_type_collection_csv_export_query(
            self, data_type, args):
        query_args = flatten_operation_args(data_type['name'], args)
        data_type_args = flatten_collection_args(data_type['name'], args)

        query = DATA_TYPE_COLLECTION_CSV_EXPORT_QUERY.format(
            query_args=query_args,
            data_type_name=data_type['name'],
            data_type_args=data_type_args)

        return query

    def build_data_type_collection_query(
            self, data_type, data_types, response):
        data_type_name = data_type['name'] + 'Collection'
        query_args = flatten_operation_args(data_type_name, response)

        query_fragment = self.fields_builder.build_fields(
            data_type_name,
            data_type,
            data_types,
            response,
            is_collection=True)
        query = DATA_TYPE_COLLECTION_QUERY.format(
            query_args=query_args,
            data_type_collection_fragment=query_fragment)

        return query

    def build_data_type_query(self, data_type, data_types, response):
        query_args = flatten_operation_args(data_type['name'], response)

        query_fragment = self.fields_builder.build_fields(
            data_type['name'],
            data_type,
            data_types,
            response)
        query = DATA_TYPE_QUERY.format(
            query_args=query_args,
            data_type_fragment=query_fragment)

        return query
