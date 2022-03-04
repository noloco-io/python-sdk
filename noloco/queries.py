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
  {data_type_name}{data_type_args} {{
    {include}
  }}
}}'''


DATA_TYPE_COLLECTION_CSV_EXPORT_QUERY = '''query{query_args} {{
  {data_type_name}CsvExport{data_type_args} {{
    base64
  }}
}}'''


DATA_TYPE_COLLECTION_QUERY = '''query{query_args} {{
  {data_type_name}Collection{data_type_args} {{
    totalCount
    edges {{
      node {{
        {include}
      }}
    }}
    pageInfo {{
      hasNextPage
      endCursor
    }}
  }}
}}'''


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

    def __serialise_field(self, field_name, field_value):
        if field_value is True:
            return field_name
        else:
            return field_name + \
                ' { ' + self.__serialise_fields(field_value) + ' }'

    def __serialise_fields(self, include):
        return '\n'.join([self.__serialise_field(field_name, field_value)
                          for field_name, field_value in include.items()])

    def build_data_type_collection_csv_export_query(
            self, data_type_name, args):
        query_args = self.__build_query_args(args)
        data_type_args = self.__build_type_args(args)

        query = DATA_TYPE_COLLECTION_CSV_EXPORT_QUERY.format(
            query_args=query_args,
            data_type_name=data_type_name,
            data_type_args=data_type_args)
        return query

    def build_data_type_collection_query(self, data_type_name, include, args):
        query_args = self.__build_query_args(args)
        data_type_args = self.__build_type_args(args)
        serialised_include = self.__serialise_fields(include)

        query = DATA_TYPE_COLLECTION_QUERY.format(
            query_args=query_args,
            data_type_name=data_type_name,
            data_type_args=data_type_args,
            include=serialised_include)
        return query

    def build_data_type_query(self, data_type_name, include, args):
        query_args = self.__build_query_args(args)
        data_type_args = self.__build_type_args(args)
        serialised_include = self.__serialise_fields(include)

        query = DATA_TYPE_QUERY.format(
            query_args=query_args,
            data_type_name=data_type_name,
            data_type_args=data_type_args,
            include=serialised_include)
        return query
