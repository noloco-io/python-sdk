from noloco.constants import (
    MANY_TO_ONE,
    ONE_TO_ONE)
from noloco.mutations import MutationBuilder
from unittest import TestCase


class TestBuildDataTypeMutationArgs(TestCase):
    def setUp(self):
        self.__mutation_builder = MutationBuilder()

    def test_optional_top_level_field(self):
        data_type = {
            'fields': [
                {'name': 'a',
                 'type': 'TEXT',
                 'relationship': None,
                 'required': False}
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

    def test_required_top_level_field(self):
        data_type = {
            'fields': [
                {'name': 'a',
                 'type': 'TEXT',
                 'relationship': None,
                 'required': True}
            ]
        }
        data_types = [data_type]
        args = {'a': 'b'}

        mutation_args = self.__mutation_builder.build_data_type_mutation_args(
            data_type,
            data_types,
            args)

        self.assertEqual(
            {'a': {'type': 'String!', 'value': 'b'}},
            mutation_args)

    def test_optional_forward_relationship_field(self):
        data_type = {
            'fields': [
                {'name': 'a',
                 'type': 'A',
                 'relationship': MANY_TO_ONE,
                 'required': False}
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

    def test_required_forward_relationship_field(self):
        data_type = {
            'fields': [
                {'name': 'a',
                 'type': 'A',
                 'relationship': MANY_TO_ONE,
                 'required': True}
            ]
        }
        data_types = [data_type]
        args = {'a': {'connect': {'id': 1}}}

        mutation_args = self.__mutation_builder.build_data_type_mutation_args(
            data_type,
            data_types,
            args)

        self.assertEqual(
            {'aId': {'type': 'ID!', 'value': 1}},
            mutation_args)

    def test_optional_file_field(self):
        data_type = {
            'fields': [
                {'name': 'a',
                 'type': 'file',
                 'relationship': ONE_TO_ONE,
                 'required': False}
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

    def test_required_file_field(self):
        data_type = {
            'fields': [
                {'name': 'a',
                 'type': 'file',
                 'relationship': ONE_TO_ONE,
                 'required': True}
            ]
        }
        data_types = [data_type]
        args = {'a': 'b'}

        mutation_args = self.__mutation_builder.build_data_type_mutation_args(
            data_type,
            data_types,
            args)

        self.assertEqual(
            {'a': {'type': 'Upload!', 'value': 'b'}},
            mutation_args)

    def test_optional_reverse_relationship_field(self):
        data_type = {
            'type': 'data_type_1',
            'fields': []
        }
        related_data_type = {'type': 'data_type_2',
                             'fields': [{'name': 'b',
                                         'reverseName': 'a',
                                         'type': 'data_type_1',
                                         'relationship': MANY_TO_ONE,
                                         'required': False}]}
        data_types = [data_type, related_data_type]
        args = {'a': [1, 2, 3]}

        mutation_args = self.__mutation_builder.build_data_type_mutation_args(
            data_type,
            data_types,
            args)

        self.assertEqual(
            {'aId': {'type': '[ID!]', 'value': [1, 2, 3]}},
            mutation_args)

    def test_required_reverse_relationship_field(self):
        data_type = {
            'type': 'data_type_1',
            'fields': []
        }
        related_data_type = {'type': 'data_type_2',
                             'fields': [{'name': 'b',
                                         'reverseName': 'a',
                                         'type': 'data_type_1',
                                         'relationship': MANY_TO_ONE,
                                         'required': True}]}
        data_types = [data_type, related_data_type]
        args = {'a': [1, 2, 3]}

        mutation_args = self.__mutation_builder.build_data_type_mutation_args(
            data_type,
            data_types,
            args)

        self.assertEqual(
            {'aId': {'type': '[ID!]!', 'value': [1, 2, 3]}},
            mutation_args)
