from noloco.exceptions import NolocoFieldNotFoundError, NolocoUnknownError
from noloco.fields import DataTypeFieldsBuilder
from noloco.utils import build_data_type_args, build_operation_args, gql_type
from pydash import get, pascal_case


DATA_TYPE_MUTATION = '''mutation{mutation_args} {{
  {mutation_fragment}
}}'''


class MutationBuilder:
    def __init__(self):
        self.fields_builder = DataTypeFieldsBuilder()

    def build_data_type_mutation_args(self, data_type, data_types, args):
        mutation_args = {}

        for arg_name, arg_value in args.items():
            data_type_fields = [
                field
                for field
                in data_type['fields']
                if field['name'] == arg_name]
            data_type_field = data_type_fields[0]

            if data_type_field is not None:
                # The field is either a top-level or relationship field on the
                # data type.
                if data_type_field['relationship'] is None and \
                        data_type_field['type'] != 'file':
                    # This is a top-level field, so map the arg onto a
                    # primitive.
                    mutation_args[arg_name] = {
                        'type': gql_type(data_type_field['type']),
                        'value': arg_value
                    }
                elif get(arg_value, 'connect') is not None:
                    # This is a relationship field, so map the arg onto an Id
                    # arg.
                    # TODO - stronger validation and error handling.
                    # TODO - consider supporting connecting on other fields.
                    mutation_args[arg_name + 'Id'] = {
                        'type': 'ID',
                        'value': arg_value['connect']['id']
                    }
                elif get(arg_value, 'upload') is not None and \
                        data_type_field['type'] == 'file':
                    # This is a file upload field, so map the arg onto an
                    # Upload arg, although do not open the file yet.
                    # TODO - stronger validation and error handling.
                    mutation_args[arg_name] = {
                        'type': 'Upload',
                        'value': arg_value['upload']['file']
                    }
                else:
                    raise NolocoUnknownError()
            else:
                # The field is a reverse relationship field to the data type or
                # doesn't exist.
                for related_data_type in data_types:
                    for field in related_data_type['fields']:
                        if field['type'] == data_type['type'] and \
                                field['reverseName'] == arg_name:
                            related_field = field

                if related_field is not None:
                    # This is a reverse relationship field and can be
                    # connected.
                    mutation_args[arg_name + 'Id'] = {
                        'type': '[ID!]',
                        'value': arg_value
                    }
                else:
                    # This field doesn't exist on the type.
                    raise NolocoFieldNotFoundError(arg_name)

        return mutation_args

    def build_data_type_mutation(
            self,
            mutation,
            data_type,
            data_types,
            include,
            args):
        mutation_args = build_operation_args(args)
        data_type_args = build_data_type_args(args)

        mutation_fragment = self.fields_builder.build_data_type_fields(
            mutation + pascal_case(data_type['name']),
            data_type,
            data_types,
            include,
            data_type_args)

        return DATA_TYPE_MUTATION.format(
            mutation_args=mutation_args,
            mutation_fragment=mutation_fragment)
