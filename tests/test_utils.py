from noloco.utils import (
    build_data_type_arg,
    build_data_type_args,
    build_operation_arg,
    build_operation_args,
    gql_args,
    has_files)
from unittest import TestCase


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
