from noloco.constants import (
    BOOLEAN,
    DATE,
    DECIMAL,
    DURATION,
    INTEGER,
    RICH_TEXT,
    TEXT)
from noloco.exceptions import (
    NolocoDataTypeNotFoundError,
    NolocoFieldNotFoundError,
    NolocoFieldNotUniqueError,
    NolocoUnknownError)
from pydash import find, pascal_case


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


def build_data_type_arg(arg_name):
    return f'{arg_name}: ${arg_name}'


def build_data_type_args(args):
    data_type_arg_list = ', '.join(
        [build_data_type_arg(arg_name) for arg_name in args.keys()])
    if data_type_arg_list:
        return f'({data_type_arg_list})'
    else:
        return ''


def collection_args(data_type_name, after, before, first, order_by, where):
    args = {}

    if after is not None:
        args['after'] = {'type': 'String', 'value': after}
    if after is None and before is not None:
        args['before'] = {'type': 'String', 'value': before}
    if first is not None:
        args['first'] = {'type': 'Int', 'value': first}
    if order_by is not None:
        args['order_by'] = {'type': 'OrderBy', 'value': order_by}
    if where is not None:
        whereType = pascal_case(data_type_name) + 'WhereInput'
        args['where'] = {'type': whereType, 'value': where}

    return args


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

    if field is None:
        raise NolocoFieldNotFoundError(field_name)
    else:
        return field


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
    elif field_type == RICH_TEXT:
        return 'String'


def open_files(args):
    opened_files = []

    try:
        for arg_name, arg_value in args.items():
            if arg_value['type'] == 'Upload':
                file_path = arg_value['value']
                open_file = open(file_path, 'rb')
                args[arg_name]['value'] = open_file
                opened_files.append(open_file)
    except Exception:
        for open_file in opened_files:
            open_file.close()

    return args


def has_files(args):
    for arg_value in args.values():
        if arg_value['type'] == 'Upload':
            return True

    return False


def close_files(args):
    for arg_value in args.values():
        if arg_value['type'] == 'Upload':
            open_file = arg_value['value']
            open_file.close()


def unique_args(data_type, args):
    for arg_name, arg_value in args:
        arg_field = find_field_by_name(arg_name, data_type['fields'])

        if arg_field['unique'] is not True:
            raise NolocoFieldNotUniqueError(data_type['name'], arg_name)

        if arg_field['type'] == TEXT:
            arg_type = 'String'
        if arg_field['type'] == DATE:
            arg_type = 'DateTime'
        elif arg_field['type'] == INTEGER:
            arg_type = 'Int'
        elif arg_field['type'] == DECIMAL:
            arg_type = 'Float'
        else:
            # TODO - confirm which types can be unique
            raise NolocoFieldNotUniqueError(data_type['name'], arg_name)

        args[arg_name] = {'type': arg_type, 'value': arg_value}

    return args
