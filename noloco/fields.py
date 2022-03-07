from noloco.constants import MANY_TO_ONE, ONE_TO_ONE
from noloco.utils import (
    find_data_type_by_name,
    find_field_by_name)


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
  }}
'''


FILE_FIELDS = '''id uuid fileType url name'''


FILE_CONNECTION_FIELDS = '''edges {{
  node {{
    {file_query}
  }}
}}'''.format(file_query=FILE_FIELDS)


class DataTypeFieldsBuilder:
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
                relationship_schema = self.build_data_type_fields(
                    relationship_name,
                    relationship_data_type,
                    data_types,
                    relationship_include)
            else:
                relationship_schema = self.build_data_type_collection_fields(
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
                    file['name'] + ' { ' + FILE_FIELDS + ' }')
            else:
                file_fields.append(
                    file['name'] + ' { ' + FILE_CONNECTION_FIELDS + ' }')

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

    def build_data_type_fields(
            self, data_type_name, data_type, data_types, include, args=''):
        data_type_schema = self.__build_data_type_schema(
            data_type, data_types, include)

        return DATA_TYPE_FIELDS.format(
            data_type_name=data_type_name,
            data_type_args=args,
            data_type_schema=data_type_schema)

    def build_data_type_collection_fields(
            self, data_type_name, data_type, data_types, include, args=''):
        data_type_schema = self.__build_data_type_schema(
            data_type, data_types, include)

        return DATA_TYPE_COLLECTION_FIELDS.format(
            data_type_name=data_type_name,
            data_type_args=args,
            data_type_schema=data_type_schema)
