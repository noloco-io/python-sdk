from constants import DATE, DECIMAL, INTEGER, TEXT
from exceptions import NolocoDataTypeNotFoundError, NolocoFieldNotFoundError, \
    NolocoFieldNotUniqueError
from pydash import find, pascal_case


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
