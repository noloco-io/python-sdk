from noloco.constants import (
    MANY_TO_MANY,
    MANY_TO_ONE,
    ONE_TO_MANY,
    ONE_TO_ONE)
from noloco.exceptions import NolocoInvalidMultiFieldConnectionError, NolocoInvalidSingleFieldConnectionError
from noloco.mutations import MutationBuilder
from unittest import TestCase


class TestBuildDataTypeMutationArgs(TestCase):
    def setUp(self):
        self.__mutation_builder = MutationBuilder()

    def test_top_level_field(self):
        data_type = {
            'fields': [
                {'name': 'a', 'type': 'TEXT', 'relationship': None}
            ]
        }
        data_types = [data_type]
        args = {'a': 'b'}

        mutation_args = self.__mutation_builder.build_data_type_mutation_args(
            data_type,
            data_types,
            args)

        self.assertEqual(
            {'a': {'type': 'String', 'value': 'b'}},
            mutation_args)

    def test_forward_many_to_one_relationship_field(self):
        data_type = {
            'fields': [
                {'name': 'a', 'type': 'A', 'relationship': MANY_TO_ONE}
            ]
        }
        data_types = [data_type]
        args = {'a': {'connect': {'id': 1}}}

        mutation_args = self.__mutation_builder.build_data_type_mutation_args(
            data_type,
            data_types,
            args)

        self.assertEqual(
            {'aId': {'type': 'ID', 'value': 1}},
            mutation_args)

    def test_forward_one_to_one_relationship_field(self):
        data_type = {
            'fields': [
                {'name': 'a', 'type': 'A', 'relationship': ONE_TO_ONE}
            ]
        }
        data_types = [data_type]
        args = {'a': {'connect': {'id': 1}}}

        mutation_args = self.__mutation_builder.build_data_type_mutation_args(
            data_type,
            data_types,
            args)

        self.assertEqual(
            {'aId': {'type': 'ID', 'value': 1}},
            mutation_args)

    def test_forward_one_to_many_relationship_field(self):
        data_type = {
            'fields': [
                {'name': 'a', 'type': 'A', 'relationship': ONE_TO_MANY}
            ]
        }
        data_types = [data_type]
        args = {'a': {'connect': [{'id': 1}, {'id': 2}]}}

        mutation_args = self.__mutation_builder.build_data_type_mutation_args(
            data_type,
            data_types,
            args)

        self.assertEqual(
            {'aId': {'type': '[ID!]', 'value': [1, 2]}},
            mutation_args)

    def test_forward_many_to_many_relationship_field(self):
        data_type = {
            'fields': [
                {'name': 'a', 'type': 'A', 'relationship': MANY_TO_MANY}
            ]
        }
        data_types = [data_type]
        args = {'a': {'connect': [{'id': 1}, {'id': 2}]}}

        mutation_args = self.__mutation_builder.build_data_type_mutation_args(
            data_type,
            data_types,
            args)

        self.assertEqual(
            {'aId': {'type': '[ID!]', 'value': [1, 2]}},
            mutation_args)

    def test_forward_many_to_many_relationship_field_raises_error_for_non_list_value(self):
        data_type = {
            'fields': [
                {'name': 'a', 'type': 'A', 'relationship': MANY_TO_MANY}
            ]
        }
        data_types = [data_type]
        args = {'a': {'connect': {'id': 1}}}

        with self.assertRaises(NolocoInvalidMultiFieldConnectionError):
            self.__mutation_builder.build_data_type_mutation_args(
                data_type,
                data_types,
                args)
    
    def test_forward_many_to_one_relationship_field_raises_error_for_non_dict_value(self):
        data_type = {
            'fields': [
                {'name': 'a', 'type': 'A', 'relationship': MANY_TO_ONE}
            ]
        }
        data_types = [data_type]
        args = {'a': {'connect':  1 }}

        with self.assertRaises(NolocoInvalidSingleFieldConnectionError):
            self.__mutation_builder.build_data_type_mutation_args(
                data_type,
                data_types,
                args)


    def test_file_field(self):
        data_type = {
            'fields': [
                {'name': 'a', 'type': 'file', 'relationship': ONE_TO_ONE}
            ]
        }
        data_types = [data_type]
        args = {'a': 'b'}

        mutation_args = self.__mutation_builder.build_data_type_mutation_args(
            data_type,
            data_types,
            args)

        self.assertEqual(
            {'a': {'type': 'Upload', 'value': 'b'}},
            mutation_args)

    def test_reverse_many_to_one_relationship_field(self):
        data_type = {
            'type': 'data_type_1',
            'fields': []
        }
        related_data_type = {
            'type': 'data_type_2',
            'fields': [
                {'name': 'b', 'reverseName': 'a', 'type': 'data_type_1', 'relationship': MANY_TO_ONE}
            ]
        }
        data_types = [data_type, related_data_type]
        args = {'a': {'connect': [{'id': 1}, {'id': 2}, {'id': 3}]}}

        mutation_args = self.__mutation_builder.build_data_type_mutation_args(
            data_type,
            data_types,
            args)

        self.assertEqual(
            {'aId': {'type': '[ID!]', 'value': [1, 2, 3]}},
            mutation_args)

    def test_reverse_one_to_one_relationship_field(self):
        data_type = {
            'type': 'data_type_1',
            'fields': []
        }
        related_data_type = {
            'type': 'data_type_2',
            'fields': [
                {'name': 'b', 'reverseName': 'a', 'type': 'data_type_1', 'relationship': ONE_TO_ONE}
            ]
        }
        data_types = [data_type, related_data_type]
        args = {'a': {'connect': {'id': 1} } }

        mutation_args = self.__mutation_builder.build_data_type_mutation_args(
            data_type,
            data_types,
            args)

        self.assertEqual(
            {'aId': {'type': 'ID', 'value': 1}},
            mutation_args)

    def test_reverse_one_to_many_relationship_field(self):
        data_type = {
            'type': 'data_type_1',
            'fields': []
        }
        related_data_type = {
            'type': 'data_type_2',
            'fields': [
                {'name': 'b', 'reverseName': 'a', 'type': 'data_type_1', 'relationship': ONE_TO_MANY}
            ]
        }
        data_types = [data_type, related_data_type]
        args = {'a': {'connect': {'id': 1} } }

        mutation_args = self.__mutation_builder.build_data_type_mutation_args(
            data_type,
            data_types,
            args)

        self.assertEqual(
            {'aId': {'type': 'ID', 'value': 1}},
            mutation_args)

    def test_reverse_many_to_many_relationship_field(self):
        data_type = {
            'type': 'data_type_1',
            'fields': []
        }
        related_data_type = {
            'type': 'data_type_2',
            'fields': [
                {'name': 'b', 'reverseName': 'a', 'type': 'data_type_1', 'relationship': MANY_TO_MANY}
            ]
        }
        data_types = [data_type, related_data_type]
        args = {'a': {'connect': [{'id': 1}, {'id': 2}, {'id': 3}]}}

        mutation_args = self.__mutation_builder.build_data_type_mutation_args(
            data_type,
            data_types,
            args)

        self.assertEqual(
            {'aId': {'type': '[ID!]', 'value': [1, 2, 3]}},
            mutation_args)
