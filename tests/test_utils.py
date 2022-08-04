from noloco.utils import (
    build_data_type_arg,
    build_data_type_args,
    build_operation_arg,
    build_operation_args,
    gql_args,
    has_files, pascal_case,
    gql_type,
    with_required)
from unittest import TestCase


class TestPascalCase(TestCase):
    def test_pascal_case(self):
        self.assertEqual('Name', pascal_case('name'))
        self.assertEqual('NameWithSpace', pascal_case('name with space'))
        self.assertEqual('NameWithSpace', pascal_case('name with space'))
        self.assertEqual('NameWithSpace', pascal_case('nameWithSpace'))
        self.assertEqual('Namewithoutspace', pascal_case('namewithoutspace'))


class TestBuildDataTypeArg(TestCase):
    def test_build_data_type_arg_builds_arg_from_name(self):
        arg_name = 'a'

        built_arg = build_data_type_arg(arg_name)

        self.assertEqual('a: $a', built_arg)


class TestBuildDataTypeArgs(TestCase):
    def test_build_data_type_args_builds_no_args(self):
        args = {}

        built_args = build_data_type_args(args)

        self.assertEqual('', built_args)

    def test_build_data_type_args_builds_single_arg(self):
        args = {}
        args['a'] = {'type': 'String', 'value': 'b'}

        built_args = build_data_type_args(args)

        self.assertEqual('(a: $a)', built_args)

    def test_build_data_type_args_builds_multiple_arg(self):
        args = {}
        args['a'] = {'type': 'String', 'value': 'b'}
        args['c'] = {'type': 'Int', 'value': 'd'}

        built_args = build_data_type_args(args)

        self.assertEqual('(a: $a, c: $c)', built_args)


class TestBuildOperationArg(TestCase):
    def test_build_operation_arg_builds_arg_from_name_and_type(self):
        arg_name = 'a'
        arg_value = {'type': 'String', 'value': 'b'}

        built_arg = build_operation_arg(arg_name, arg_value)

        self.assertEqual('$a: String', built_arg)


class TestBuildOperationArgs(TestCase):
    def test_build_operation_args_builds_no_args(self):
        args = {}

        built_args = build_operation_args(args)

        self.assertEqual('', built_args)

    def test_build_operation_args_builds_single_arg(self):
        args = {}
        args['a'] = {'type': 'String', 'value': 'b'}

        built_args = build_operation_args(args)

        self.assertEqual('($a: String)', built_args)

    def test_build_operation_args_builds_multiple_arg(self):
        args = {}
        args['a'] = {'type': 'String', 'value': 'b'}
        args['c'] = {'type': 'Int', 'value': 'd'}

        built_args = build_operation_args(args)

        self.assertEqual('($a: String, $c: Int)', built_args)


class TestGqlArgs(TestCase):
    def test_gql_args_builds_no_args(self):
        args = {}

        built_args = gql_args(args)

        self.assertEqual({}, built_args)

    def test_gql_args_builds_single_arg(self):
        args = {}
        args['a'] = {'type': 'String', 'value': 'b'}

        built_args = gql_args(args)

        self.assertEqual({'a': 'b'}, built_args)

    def test_gql_args_builds_multiple_args(self):
        args = {}
        args['a'] = {'type': 'String', 'value': 'b'}
        args['c'] = {'type': 'Int', 'value': 1}

        built_args = gql_args(args)

        self.assertEqual({'a': 'b', 'c': 1}, built_args)


class TestGqlType(TestCase):
    def test_gql_type_maps_optional_text_to_string(self):
        data_type = {}
        data_type_field = {'type': 'TEXT'}

        mapped_type = gql_type(data_type, data_type_field)

        self.assertEqual('String', mapped_type)

    def test_gql_type_maps_required_text_to_string(self):
        data_type = {}
        data_type_field = {'required': True, 'type': 'TEXT'}

        mapped_type = gql_type(data_type, data_type_field, True)

        self.assertEqual('String!', mapped_type)

    def test_gql_type_maps_optional_date_to_datetime(self):
        data_type = {}
        data_type_field = {'type': 'DATE'}

        mapped_type = gql_type(data_type, data_type_field)

        self.assertEqual('DateTime', mapped_type)

    def test_gql_type_maps_required_date_to_datetime(self):
        data_type = {}
        data_type_field = {'required': True, 'type': 'DATE'}

        mapped_type = gql_type(data_type, data_type_field, True)

        self.assertEqual('DateTime!', mapped_type)

    def test_gql_type_maps_optional_integer_to_int(self):
        data_type = {}
        data_type_field = {'type': 'INTEGER'}

        mapped_type = gql_type(data_type, data_type_field)

        self.assertEqual('Int', mapped_type)

    def test_gql_type_maps_required_integer_to_int(self):
        data_type = {}
        data_type_field = {'required': True, 'type': 'INTEGER'}

        mapped_type = gql_type(data_type, data_type_field, True)

        self.assertEqual('Int!', mapped_type)

    def test_gql_type_maps_optional_decimal_to_float(self):
        data_type = {}
        data_type_field = {'type': 'DECIMAL'}

        mapped_type = gql_type(data_type, data_type_field)

        self.assertEqual('Float', mapped_type)

    def test_gql_type_maps_required_decimal_to_float(self):
        data_type = {}
        data_type_field = {'required': True, 'type': 'DECIMAL'}

        mapped_type = gql_type(data_type, data_type_field, True)

        self.assertEqual('Float!', mapped_type)

    def test_gql_type_maps_optional_duration_to_duration(self):
        data_type = {}
        data_type_field = {'type': 'DURATION'}

        mapped_type = gql_type(data_type, data_type_field)

        self.assertEqual('Duration', mapped_type)

    def test_gql_type_maps_required_duration_to_duration(self):
        data_type = {}
        data_type_field = {'required': True, 'type': 'DURATION'}

        mapped_type = gql_type(data_type, data_type_field, True)

        self.assertEqual('Duration!', mapped_type)

    def test_gql_type_maps_optional_boolean_to_boolean(self):
        data_type = {}
        data_type_field = {'type': 'BOOLEAN'}

        mapped_type = gql_type(data_type, data_type_field)

        self.assertEqual('Boolean', mapped_type)

    def test_gql_type_maps_required_boolean_to_boolean(self):
        data_type = {}
        data_type_field = {'required': True, 'type': 'BOOLEAN'}

        mapped_type = gql_type(data_type, data_type_field, True)

        self.assertEqual('Boolean!', mapped_type)

    def test_gql_type_maps_optional_single_option_to_named_type(self):
        data_type = {'name': 'dataType'}
        data_type_field = {'name': 'dataField', 'type': 'SINGLE_OPTION'}

        mapped_type = gql_type(data_type, data_type_field)

        self.assertEqual('DataTypeDataField', mapped_type)

    def test_gql_type_maps_required_single_option_to_named_type(self):
        data_type = {'name': 'dataType'}
        data_type_field = {
            'name': 'dataField',
            'required': True,
            'type': 'SINGLE_OPTION'}

        mapped_type = gql_type(data_type, data_type_field, True)

        self.assertEqual('DataTypeDataField!', mapped_type)

    def test_gql_type_maps_optional_multiple_option_to_named_type(self):
        data_type = {'name': 'dataType'}
        data_type_field = {'name': 'dataField', 'type': 'MULTIPLE_OPTION'}

        mapped_type = gql_type(data_type, data_type_field)

        self.assertEqual('[DataTypeDataField!]', mapped_type)

    def test_gql_type_maps_required_multiple_option_to_named_type(self):
        data_type = {'name': 'dataType'}
        data_type_field = {
            'name': 'dataField',
            'required': True,
            'type': 'MULTIPLE_OPTION'}

        mapped_type = gql_type(data_type, data_type_field, True)

        self.assertEqual('[DataTypeDataField!]!', mapped_type)


class TestHasFiles(TestCase):
    def test_has_files_no_args(self):
        args = {}

        self.assertFalse(has_files(args))

    def test_has_files_single_file_arg(self):
        args = {}
        args['a'] = {'type': 'Upload'}

        self.assertTrue(has_files(args))

    def test_has_files_single_non_file_arg(self):
        args = {}
        args['a'] = {'type': 'String'}

        self.assertFalse(has_files(args))

    def test_has_files_multiple_args_with_file(self):
        args = {}
        args['a'] = {'type': 'Boolean'}
        args['b'] = {'type': 'DateTime'}
        args['c'] = {'type': 'Duration'}
        args['g'] = {'type': 'Upload'}
        args['d'] = {'type': 'Float'}
        args['e'] = {'type': 'Int'}
        args['f'] = {'type': 'String'}

        self.assertTrue(has_files(args))

    def test_has_files_multiple_args_without_file(self):
        args = {}
        args['a'] = {'type': 'Boolean'}
        args['b'] = {'type': 'DateTime'}
        args['c'] = {'type': 'Duration'}
        args['d'] = {'type': 'Float'}
        args['e'] = {'type': 'Int'}
        args['f'] = {'type': 'String'}

        self.assertFalse(has_files(args))


class TestWithRequired(TestCase):
    def test_with_required_optional(self):
        mapped_type = 'A'
        self.assertEqual(mapped_type, with_required(mapped_type, False))

    def test_with_required_required(self):
        mapped_type = 'A'
        self.assertEqual(f'{mapped_type}!', with_required(mapped_type, True))
