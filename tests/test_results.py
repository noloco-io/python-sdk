from noloco.results import Result
from unittest import TestCase


class TestBuildResult(TestCase):
    def test_build_result_simple_result(self):
        options = {
            'where': {
                'id': {
                    'equals': 1
                }
            }
        }
        raw_result = {
            'mutateMyDataType': {
                'id': 1,
                'uuid': 'xxxxxxxxxxxxxxxxxxxx',
                'myField': 'My Value'
            }
        }

        result = Result.build(
            'myDataType',
            'mutateMyDataType',
            raw_result,
            options,
            lambda _: None)

        # Top-level assertions
        self.assertEqual(1, result.id)
        self.assertEqual('xxxxxxxxxxxxxxxxxxxx', result.uuid)
        self.assertEqual('My Value', result.myField)

    def test_build_result_nested_result(self):
        options = {
            'include': {
                'myRelationship': True
            },
            'where': {
                'id': {
                    'equals': 1
                }
            }
        }
        raw_result = {
            'myDataType': {
                'id': 1,
                'uuid': 'xxxxxxxxxxxxxxxxxxxx',
                'myField': 'My Value',
                'myRelationship': {
                    'id': 2,
                    'uuid': 'yyyyyyyyyyyyyyyyyyyy',
                    'myOtherField': 'My Other Value',
                }
            }
        }

        result = Result.build(
            'myDataType',
            'myDataType',
            raw_result,
            options,
            lambda _: None)

        # Top-level assertions
        self.assertEqual(1, result.id)
        self.assertEqual('xxxxxxxxxxxxxxxxxxxx', result.uuid)
        self.assertEqual('My Value', result.myField)

        # Relationship assertions
        self.assertEqual(2, result.myRelationship.id)
        self.assertEqual('yyyyyyyyyyyyyyyyyyyy', result.myRelationship.uuid)
        self.assertEqual('My Other Value', result.myRelationship.myOtherField)

    def test_build_result_nested_collection_result(self):
        options = {
            'include': {
                'myRelationship': True,
                'myReverseRelationshipCollection': True
            },
            'where': {
                'id': {
                    'equals': 1
                }
            }
        }
        raw_result = {
            'myDataType': {
                'id': 1,
                'uuid': 'xxxxxxxxxxxxxxxxxxxx',
                'myField': 'My Value',
                'myReverseRelationshipCollection': {
                    'totalCount': 2,
                    'edges': [
                        {
                            'node': {
                                'id': 2,
                                'uuid': 'yyyyyyyyyyyyyyyyyyyy',
                                'myOtherField': 'My Value A'
                            }
                        },
                        {
                            'node': {
                                'id': 3,
                                'uuid': 'zzzzzzzzzzzzzzzzzzzz',
                                'myOtherField': 'My Value B'
                            }
                        }
                    ],
                    'pageInfo': {
                        'hasPreviousPage': False,
                        'hasNextPage': False,
                        'startCursor': 'aaaaaaaaaaa=',
                        'endCursor': 'bbbbbbbbbbb='
                    },
                    '__typename': 'MyReverseRelationshipConnection'
                }
            }
        }

        result = Result.build(
            'myDataType',
            'myDataType',
            raw_result,
            options,
            lambda _: None)

        # Top-level assertions
        self.assertEqual(1, result.id)
        self.assertEqual('xxxxxxxxxxxxxxxxxxxx', result.uuid)
        self.assertEqual('My Value', result.myField)

        # Total count assertions
        self.assertEqual(2, result.myReverseRelationshipCollection.total_count)

        # Pagination assertions
        self.assertIsNone(result.myReverseRelationshipCollection.next_page())
        self.assertIsNone(result.myReverseRelationshipCollection.previous_page())

        # Data assertions
        self.assertEqual(2, len(result.myReverseRelationshipCollection.data))
        self.assertEqual(2, result.myReverseRelationshipCollection.data[0].id)
        self.assertEqual('yyyyyyyyyyyyyyyyyyyy', result.myReverseRelationshipCollection.data[0].uuid)
        self.assertEqual('My Value A', result.myReverseRelationshipCollection.data[0].myOtherField)
        self.assertEqual(3, result.myReverseRelationshipCollection.data[1].id)
        self.assertEqual('zzzzzzzzzzzzzzzzzzzz', result.myReverseRelationshipCollection.data[1].uuid)
        self.assertEqual('My Value B', result.myReverseRelationshipCollection.data[1].myOtherField)

    def test_build_result_simple_collection_result(self):
        options = {
            'where': {
                'id': {
                    'lt': 3
                }
            }
        }
        raw_result = {
            'myDataTypeCollection': {
                'totalCount': 2,
                'edges': [
                    {
                        'node': {
                            'id': 1,
                            'uuid': 'xxxxxxxxxxxxxxxxxxxx',
                            'myField': 'My Value A'
                        }
                    },
                    {
                        'node': {
                            'id': 2,
                            'uuid': 'yyyyyyyyyyyyyyyyyyyy',
                            'myField': 'My Value B'
                        }
                    }
                ],
                'pageInfo': {
                    'hasPreviousPage': False,
                    'hasNextPage': False,
                    'startCursor': 'aaaaaaaaaaa=',
                    'endCursor': 'bbbbbbbbbbb='
                },
                '__typename': 'MyDataTypeConnection'
            }
        }

        result = Result.build(
            'myDataType',
            'myDataTypeCollection',
            raw_result,
            options,
            lambda _: None)

        # Total count assertions
        self.assertEqual(2, result.total_count)

        # Pagination assertions
        self.assertIsNone(result.next_page())
        self.assertIsNone(result.previous_page())

        # Data assertions
        self.assertEqual(2, len(result.data))
        self.assertEqual(1, result.data[0].id)
        self.assertEqual('xxxxxxxxxxxxxxxxxxxx', result.data[0].uuid)
        self.assertEqual('My Value A', result.data[0].myField)
        self.assertEqual(2, result.data[1].id)
        self.assertEqual('yyyyyyyyyyyyyyyyyyyy', result.data[1].uuid)
        self.assertEqual('My Value B', result.data[1].myField)
