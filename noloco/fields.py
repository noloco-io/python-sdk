from noloco.constants import (
    MANY_TO_MANY,
    MANY_TO_ONE,
    ONE_TO_ONE)
from noloco.utils import (
    build_data_type_args,
    find_field_by_name,
    find_relationship_data_type)


DATA_TYPE_FIELDS = '''{data_type_name}{data_type_args}
{{
  {data_type_schema}
}}'''


DATA_TYPE_COLLECTION_FIELDS = '''{data_type_name}{data_type_args} {{
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
    __typename
  }}
'''


FILE_FIELDS = '''id uuid fileType url name'''


FILE_CONNECTION_FIELDS = '''totalCount
edges {{
  node {{
    {file_query}
  }}
}}
pageInfo {{
  hasPreviousPage
  hasNextPage
  startCursor
  endCursor
}}
__typename'''.format(file_query=FILE_FIELDS)


class DataTypeFieldsBuilder:
    def __build_related_fields(
          self,
          data_type_name,
          data_type_full_name,
          fields,
          include,
          data_types):
        related_fields = []

        for relationship_name, ignore_children in include.items():
            relationship_field = find_field_by_name(
              relationship_name, fields)
            relationship_data_type = find_relationship_data_type(
                relationship_name,
                data_type_name,
                fields,
                data_types)

            # For example if include={'usersCompleted': True} was passed in,
            # we will not include any relationships from the User data type.
            # when including the usersCompleted related field. However, if
            # include={'usersCompleted': {'include': {'company': True}}} was
            # passed in, we would recursively include the company relationship
            # against any returned users.
            if ignore_children is True:
                response = {}
            else:
                response = ignore_children

            is_collection = relationship_field is None or \
                relationship_field['relationship'] == MANY_TO_MANY
            relationship_schema = self.build_fields(
                    relationship_name,
                    relationship_data_type,
                    data_types,
                    response,
                    data_type_path=data_type_full_name + '_',
                    is_collection=is_collection)

            related_fields.append(relationship_schema)

        return related_fields

    def __build_file_fields(self, files):
        file_fields = []

        for file in files:
            if file['relationship'] == ONE_TO_ONE or \
                    file['relationship'] == MANY_TO_ONE:
                file_fields.append(
                    file['name'] + ' { ' + FILE_FIELDS + ' }')
            else:
                file_fields.append(
                    file['name'] + ' { ' + FILE_CONNECTION_FIELDS + ' }')

        return file_fields

    def __build_data_type_schema(
            self,
            data_type_full_name,
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
            data_type['name'],
            data_type_full_name,
            data_type['fields'],
            include,
            data_types)

        # All file relationship fields on the data type are automatically
        # included in the requested schema.
        file_field_schema = self.__build_file_fields(
          field for field in data_type['fields'] if field['type'] == 'file')

        all_field_names = primary_field_schema + \
            related_field_schema + \
            file_field_schema + ['__typename']

        return '\n'.join(all_field_names)

    def build_fields(
            self,
            data_type_name,
            data_type,
            data_types,
            response,
            data_type_path='',
            is_collection=False):
        data_type_full_name = data_type_path + data_type_name

        # Each top level key on the response object gets fully qualified by the
        # nesting path and mapped ont
        args = {}
        include = {}
        for arg_name, arg_value in response.items():
            if arg_name == 'include':
                include = arg_value
            else:
                args[data_type_full_name + '_' + arg_name] = arg_value
        data_type_args = build_data_type_args(args)

        data_type_schema = self.__build_data_type_schema(
            data_type_full_name, data_type, data_types, include)

        if is_collection:
            base_fragment = DATA_TYPE_COLLECTION_FIELDS
        else:
            base_fragment = DATA_TYPE_FIELDS

        return base_fragment.format(
            data_type_name=data_type_name,
            data_type_args=data_type_args,
            data_type_schema=data_type_schema)
