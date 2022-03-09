from noloco.fields import DataTypeFieldsBuilder
from noloco.utils import build_operation_args


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


DATA_TYPE_COLLECTION_QUERY = '''query{query_args} {{
  {data_type_collection_fragment}
}}'''


class QueryBuilder:
    def __init__(self):
        self.fields_builder = DataTypeFieldsBuilder()

    def build_data_type_collection_query(
            self, data_type, data_types, options, flattened_options):
        data_type_name = data_type['name'] + 'Collection'
        query_args = build_operation_args(flattened_options)

        query_fragment = self.fields_builder.build_fields(
            data_type_name,
            data_type,
            data_types,
            options,
            is_collection=True)
        query = DATA_TYPE_COLLECTION_QUERY.format(
            query_args=query_args,
            data_type_collection_fragment=query_fragment)

        return query

    def build_data_type_query(
            self,
            data_type,
            data_types,
            options,
            flattened_options):
        query_args = build_operation_args(flattened_options)

        query_fragment = self.fields_builder.build_fields(
            data_type['name'],
            data_type,
            data_types,
            options)
        query = DATA_TYPE_QUERY.format(
            query_args=query_args,
            data_type_fragment=query_fragment)

        return query
