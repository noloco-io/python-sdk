from constants import MANY_TO_ONE, ONE_TO_ONE
from utils import find_data_type_by_name, find_field_by_name


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


DATA_TYPE_FRAGMENT = '''{data_type_name}{data_type_args}
{{
  {data_type_schema}
}}'''


DATA_TYPE_QUERY = '''query{query_args} {{
  {data_type_fragment}
}}'''


DATA_TYPE_COLLECTION_CSV_EXPORT_QUERY = '''query{query_args} {{
  {data_type_name}CsvExport{data_type_args} {{
    base64
  }}
}}'''


DATA_TYPE_COLLECTION_FRAGMENT = '''{data_type_name}{data_type_args} {{
    totalCount
    edges {{
      node {{
        {data_type_schema}
      }}
    }}
    pageInfo {{
      hasPreviousPage
      hasNextPage
      startCursor
      endCursor
    }}
  }}
'''


DATA_TYPE_COLLECTION_QUERY = '''query{query_args} {{
  {data_type_collection_fragment}
}}'''


FILE_QUERY = '''id uuid fileType url name'''


FILE_CONNECTION_QUERY = '''edges {{
  node {{
    {file_query}
  }}
}}'''.format(file_query=FILE_QUERY)


class QueryBuilder:
    def __build_query_arg(self, arg_name, arg_value):
        arg_type = arg_value['type']
        return f'${arg_name}: {arg_type}'

    def __build_query_args(self, args):
        query_arg_list = ', '.join([self.__build_query_arg(
            arg_name, arg_value) for arg_name, arg_value in args.items()])

        if query_arg_list:
            return f'({query_arg_list})'
        else:
            return ''

    def __build_type_arg(self, arg_name):
        return f'{arg_name}: ${arg_name}'

    def __build_type_args(self, args):
        type_arg_list = ', '.join(
            [self.__build_type_arg(arg_name) for arg_name in args.keys()])

        if type_arg_list:
            return f'({type_arg_list})'
        else:
            return ''

    def __build_related_fields(
          self,
          fields,
          include,
          data_types):
        related_fields = []

        for relationship_name, ignore_children in include.items():
            relationship_field = find_field_by_name(
              relationship_name, fields)
            relationship_data_type = find_data_type_by_name(
                relationship_field['type'], data_types)

            # For example if include={'usersCompleted': True} was passed in,
            # we will not include any relationships from the User data type.
            # when including the usersCompleted related field. However, if
            # include={'usersCompleted': {'include': {'company': True}}} was
            # passed in, we would recursively include the company relationship
            # against any returned users.
            if ignore_children is True:
                relationship_include = {}
            else:
                relationship_include = ignore_children['include']

            if relationship_field['relationship'] == ONE_TO_ONE or \
                    relationship_field['relationship'] == MANY_TO_ONE:
                relationship_schema = self.__build_data_type_query_fragment(
                    relationship_name,
                    relationship_data_type,
                    data_types,
                    relationship_include)
            else:
                relationship_schema = self \
                    .__build_data_type_collection_query_fragment(
                        relationship_name,
                        relationship_data_type,
                        data_types,
                        relationship_include)

            related_fields.append(relationship_schema)

        return related_fields

    def __build_file_fields(self, files):
        file_fields = []

        for file in files:
            if file['relationship'] == ONE_TO_ONE or \
                    file['relationship'] == MANY_TO_ONE:
                file_fields.append(
                    file['name'] + ' { ' + FILE_QUERY + ' }')
            else:
                file_fields.append(
                    file['name'] + ' { ' + FILE_CONNECTION_QUERY + ' }')

        return file_fields

    def __build_data_type_schema(
            self,
            data_type,
            data_types,
            include):
        # All non-relationship fields on the data type are automatically
        # included in the requested schema.
        primary_field_schema = [
            field['name']
            for field
            in data_type['fields']
            if field['relationship'] is None]

        # Only specified relationship types are included in the requested
        # schema. This principle is applied recursively so if we include a
        # relationship field, we only include relationships from that field if
        # they are also specified.
        related_field_schema = self.__build_related_fields(
            data_type['fields'], include, data_types)

        # All file relationship fields on the data type are automatically
        # included in the requested schema.
        file_field_schema = self.__build_file_fields(
          field for field in data_type['fields'] if field['type'] == 'file')

        all_field_names = primary_field_schema + \
            related_field_schema + \
            file_field_schema

        return '\n'.join(all_field_names)

    def __build_data_type_collection_query_fragment(
            self, data_type_name, data_type, data_types, include, args=''):
        data_type_schema = self.__build_data_type_schema(
            data_type, data_types, include)

        return DATA_TYPE_COLLECTION_FRAGMENT.format(
            data_type_name=data_type_name,
            data_type_args=args,
            data_type_schema=data_type_schema)

    def __build_data_type_query_fragment(
            self, data_type_name, data_type, data_types, include, args=''):
        data_type_schema = self.__build_data_type_schema(
            data_type, data_types, include)

        return DATA_TYPE_FRAGMENT.format(
            data_type_name=data_type_name,
            data_type_args=args,
            data_type_schema=data_type_schema)

    def build_data_type_collection_csv_export_query(
            self, data_type, args):
        query_args = self.__build_query_args(args)
        data_type_args = self.__build_type_args(args)

        query = DATA_TYPE_COLLECTION_CSV_EXPORT_QUERY.format(
            query_args=query_args,
            data_type_name=data_type['name'],
            data_type_args=data_type_args)
        return query

    def build_data_type_collection_query(
            self, data_type, data_types, include, args):
        query_args = self.__build_query_args(args)
        data_type_args = self.__build_type_args(args)

        query_fragment = self.__build_data_type_collection_query_fragment(
            data_type['name'] + 'Collection',
            data_type,
            data_types,
            include,
            data_type_args)
        query = DATA_TYPE_COLLECTION_QUERY.format(
            query_args=query_args,
            data_type_collection_fragment=query_fragment)
        return query

    def build_data_type_query(self, data_type, data_types, include, args):
        query_args = self.__build_query_args(args)
        data_type_args = self.__build_type_args(args)

        query_fragment = self.__build_data_type_query_fragment(
            data_type['name'], data_type, data_types, include, data_type_args)
        query = DATA_TYPE_QUERY.format(
            query_args=query_args,
            data_type_fragment=query_fragment)
        return query
