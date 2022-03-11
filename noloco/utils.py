from noloco.constants import (
    BOOLEAN,
    DATE,
    DECIMAL,
    DURATION,
    INTEGER,
    TEXT)
from noloco.exceptions import (
    NolocoDataTypeNotFoundError,
    NolocoQueryNotSupportedError)
from pydash import (
    find,
    get,
    pascal_case)


def annotate_collection_args(data_type, data_types, args):
    annotated_args = {}

    # Process top-level supported parameters.
    if get(args, 'after') is not None:
        annotated_args['after'] = {'type': 'String', 'value': args['after']}
    if get(args, 'after') is None and get(args, 'before') is not None:
        annotated_args['before'] = {'type': 'String', 'value': args['before']}
    if get(args, 'first') is not None:
        annotated_args['first'] = {'type': 'Int', 'value': args['first']}
    if get(args, 'order_by') is not None:
        annotated_args['orderBy'] = {'type': 'OrderBy', 'value': args['order_by']}
    if get(args, 'where') is not None:
        whereType = pascal_case(data_type['name']) + 'WhereInput'
        annotated_args['where'] = {'type': whereType, 'value': args['where']}

    # Recursively process nested supported parameters.
    if get(args, 'include') is not None:
        annotated_args['include'] = {}

        for nested_data_type_name, nested_args in args['include'].items():
            if nested_args is not True:
                relationship_data_type = find_relationship_data_type(
                    nested_data_type_name,
                    data_type['name'],
                    data_type['fields'],
                    data_types)
                annotated_args['include'][nested_data_type_name] = \
                    annotate_collection_args(
                        relationship_data_type,
                        data_types,
                        nested_args)
            else:
                annotated_args['include'][nested_data_type_name] = True

    return annotated_args


def build_operation_arg(arg_name, arg_value):
    arg_type = arg_value['type']
    return f'${arg_name}: {arg_type}'


def build_operation_args(args):
    operation_arg_list = ', '.join([build_operation_arg(
        arg_name, arg_value) for arg_name, arg_value in args.items()])

    if operation_arg_list:
        return f'({operation_arg_list})'
    else:
        return ''


def build_data_type_arg(arg_full_name):
    arg_name = arg_full_name.split('_')[-1]
    return f'{arg_name}: ${arg_full_name}'


def build_data_type_args(args):
    data_type_arg_list = ', '.join(
        [build_data_type_arg(arg_name) for arg_name in args.keys()])
    if data_type_arg_list:
        return f'({data_type_arg_list})'
    else:
        return ''


def change_where_to_lookup(data_type, options, id_type='ID'):
    where = options.pop('where')['value']
    lookup_key = list(where.keys())[0]

    lookup_field = find_field_by_name(lookup_key, data_type['fields'])
    lookup_type = gql_type(lookup_field['type'])
    lookup_value = where[lookup_key]['equals']

    if lookup_key == 'id':
        lookup_type = id_type

    options[lookup_key] = {'type': lookup_type, 'value': lookup_value}

    return options


def find_data_type_by_name(data_type_name, data_types):
    data_type = find(
        data_types,
        lambda project_data_type: project_data_type['name'] == data_type_name)

    if data_type is None:
        raise NolocoDataTypeNotFoundError(data_type_name)
    else:
        return data_type


def find_field_by_name(field_name, fields):
    field = find(
        fields,
        lambda data_type_field: data_type_field['name'] == field_name)

    return field


def find_relationship_data_type(
        relationship_name,
        data_type_name,
        data_type_fields,
        data_types):
    relationship_field = find_field_by_name(
        relationship_name,
        data_type_fields)

    if relationship_field is not None:
        # If the relationship field exists on the parent data type then
        # this is a forward relationship and we can simply look up the
        # relationship data type by the corresponding field type.
        return find_data_type_by_name(relationship_field['type'], data_types)
    else:
        # If there isn't a corresponding relationship field on the
        # parent data type then this is a reverse relationship and we
        # have to search for the relationship data type by it having a
        # field of the expected reverseName and type matching the
        # parent type.
        for candidate_data_type in data_types:
            candidate_fields = [
                field
                for field
                in candidate_data_type['fields']
                if field['reverseName'] is not None]

            for field in candidate_fields:
                reverseName = field['reverseName'] + 'Collection'
                if field['type'] == data_type_name and \
                        reverseName == relationship_name:
                    return candidate_data_type


def flatten_args(data_type_name, args):
    flattened_args = {}

    for arg_name, arg_value in args.items():
        if arg_name != 'include':
            flattened_args[data_type_name + '_' + arg_name] = arg_value
        else:
            for nested_data_type_name, nested_args in args['include'].items():
                if nested_args is not True:
                    flattened_nested_args = flatten_args(
                        data_type_name + '_' + nested_data_type_name,
                        nested_args)

                    for flattened_nested_arg in flattened_nested_args.keys():
                        flattened_args[flattened_nested_arg] = \
                            flattened_nested_args[flattened_nested_arg]

    return flattened_args


def gql_args(args):
    variables = {}

    for arg in args:
        variables[arg] = args[arg]['value']

    return variables


def gql_type(field_type):
    if field_type == TEXT:
        return 'String'
    elif field_type == DATE:
        return 'DateTime'
    elif field_type == INTEGER:
        return 'Int'
    elif field_type == DECIMAL:
        return 'Float'
    elif field_type == DURATION:
        return 'Duration'
    elif field_type == BOOLEAN:
        return 'Boolean'


def has_files(args):
    for arg_value in args.values():
        if arg_value['type'] == 'Upload':
            return True

    return False


def result_name_suffix(query):
    if query == 'find':
        return 'Collection'
    elif query == 'get':
        return ''
    else:
        raise NolocoQueryNotSupportedError(query)
