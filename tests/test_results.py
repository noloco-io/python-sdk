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

class TestPagingCollectionResult(TestCase):
    def test_next_page_simple_collection_result(self):
        options = {
            'first': 1,
            'where': {
                'id': {
                    'lt': 3
                }
            }
        }
        raw_curr_result = {
            'myDataTypeCollection': {
                'totalCount': 2,
                'edges': [
                    {
                        'node': {
                            'id': 1,
                            'uuid': 'xxxxxxxxxxxxxxxxxxxx',
                            'myField': 'My Value A'
                        }
                    }
                ],
                'pageInfo': {
                    'hasPreviousPage': False,
                    'hasNextPage': True,
                    'startCursor': 'aaaaaaaaaaa=',
                    'endCursor': 'bbbbbbbbbbb='
                },
                '__typename': 'MyDataTypeConnection'
            }
        }
        raw_next_result = {
            'myDataTypeCollection': {
                'totalCount': 2,
                'edges': [
                    {
                        'node': {
                            'id': 2,
                            'uuid': 'yyyyyyyyyyyyyyyyyyyy',
                            'myField': 'My Value B'
                        }
                    }
                ],
                'pageInfo': {
                    'hasPreviousPage': True,
                    'hasNextPage': False,
                    'startCursor': 'bbbbbbbbbbb=',
                    'endCursor': 'ccccccccccc='
                },
                '__typename': 'MyDataTypeConnection'
            }
        }
        def callback(data_type_name, paged_options):
            # Parameter assertions
            self.assertEqual('myDataType', data_type_name)
            self.assertEqual({
                'after': 'bbbbbbbbbbb=',
                'first': 1,
                'where': {
                    'id': {
                        'lt': 3
                    }
                }
            }, paged_options)

            return Result.build(
                'myDataType',
                'myDataTypeCollection',
                raw_next_result,
                paged_options,
                lambda _: None)

        result = Result.build(
            'myDataType',
            'myDataTypeCollection',
            raw_curr_result,
            options,
            callback)

        next_page_result = result.next_page()

        # Total count assertions
        self.assertEqual(2, next_page_result.total_count)

        # Data assertions
        self.assertEqual(1, len(next_page_result.data))
        self.assertEqual(2, next_page_result.data[0].id)
        self.assertEqual('yyyyyyyyyyyyyyyyyyyy', next_page_result.data[0].uuid)
        self.assertEqual('My Value B', next_page_result.data[0].myField)

    def test_previous_page_simple_collection_result(self):
        options = {
            'after': 'bbbbbbbbbbb=',
            'first': 1,
            'where': {
                'id': {
                    'lt': 3
                }
            }
        }
        raw_curr_result = {
            'myDataTypeCollection': {
                'totalCount': 2,
                'edges': [
                    {
                        'node': {
                            'id': 2,
                            'uuid': 'yyyyyyyyyyyyyyyyyyyy',
                            'myField': 'My Value B'
                        }
                    }
                ],
                'pageInfo': {
                    'hasPreviousPage': True,
                    'hasNextPage': False,
                    'startCursor': 'bbbbbbbbbbb=',
                    'endCursor': 'ccccccccccc='
                },
                '__typename': 'MyDataTypeConnection'
            }
        }
        raw_prev_result = {
            'myDataTypeCollection': {
                'totalCount': 2,
                'edges': [
                    {
                        'node': {
                            'id': 1,
                            'uuid': 'xxxxxxxxxxxxxxxxxxxx',
                            'myField': 'My Value A'
                        }
                    }
                ],
                'pageInfo': {
                    'hasPreviousPage': False,
                    'hasNextPage': True,
                    'startCursor': 'aaaaaaaaaaa=',
                    'endCursor': 'bbbbbbbbbbb='
                },
                '__typename': 'MyDataTypeConnection'
            }
        }
        def callback(data_type_name, paged_options):
            # Parameter assertions
            self.assertEqual('myDataType', data_type_name)
            self.assertEqual({
                'before': 'bbbbbbbbbbb=',
                'first': 1,
                'where': {
                    'id': {
                        'lt': 3
                    }
                }
            }, paged_options)

            return Result.build(
                'myDataType',
                'myDataTypeCollection',
                raw_prev_result,
                paged_options,
                lambda _: None)

        result = Result.build(
            'myDataType',
            'myDataTypeCollection',
            raw_curr_result,
            options,
            callback)

        prev_page_result = result.previous_page()

        # Total count assertions
        self.assertEqual(2, prev_page_result.total_count)

        # Data assertions
        self.assertEqual(1, len(prev_page_result.data))
        self.assertEqual(1, prev_page_result.data[0].id)
        self.assertEqual('xxxxxxxxxxxxxxxxxxxx', prev_page_result.data[0].uuid)
        self.assertEqual('My Value A', prev_page_result.data[0].myField)

    def test_next_page_simple_result_nested_collection(self):
        options = {
            'include': {
                'myDataTypeCollection': {
                    'first': 1
                }
            },
            'where': {
                'id': {
                    'equals': 1
                }
            }
        }
        raw_curr_result = {
            'myDataType': {
                'myDataTypeCollection': {
                    'totalCount': 2,
                    'edges': [
                        {
                            'node': {
                                'id': 1,
                                'uuid': 'xxxxxxxxxxxxxxxxxxxx',
                                'myField': 'My Value A'
                            }
                        }
                    ],
                    'pageInfo': {
                        'hasPreviousPage': False,
                        'hasNextPage': True,
                        'startCursor': 'aaaaaaaaaaa=',
                        'endCursor': 'bbbbbbbbbbb='
                    },
                    '__typename': 'MyDataTypeConnection'
                }
            }
        }
        raw_next_result = {
            'myDataType': {
                'myDataTypeCollection': {
                    'totalCount': 2,
                    'edges': [
                        {
                            'node': {
                                'id': 2,
                                'uuid': 'yyyyyyyyyyyyyyyyyyyy',
                                'myField': 'My Value B'
                            }
                        }
                    ],
                    'pageInfo': {
                        'hasPreviousPage': True,
                        'hasNextPage': False,
                        'startCursor': 'bbbbbbbbbbb=',
                        'endCursor': 'ccccccccccc='
                    },
                    '__typename': 'MyDataTypeConnection'
                }
            }
        }
        def callback(data_type_name, paged_options):
            # Parameter assertions
            self.assertEqual('myDataType', data_type_name)
            self.assertEqual({
                'include': {
                    'myDataTypeCollection': {
                        'after': 'bbbbbbbbbbb=',
                        'first': 1
                    }
                },
                'where': {
                    'id': {
                        'equals': 1
                    }
                }
            }, paged_options)

            return Result.build(
                'myDataType',
                'myDataType',
                raw_next_result,
                paged_options,
                lambda _: None)

        result = Result.build(
            'myDataType',
            'myDataType',
            raw_curr_result,
            options,
            callback)

        next_page_result = result.myDataTypeCollection.next_page()

        # Total count assertions
        self.assertEqual(2, next_page_result.total_count)

        # Data assertions
        self.assertEqual(1, len(next_page_result.data))
        self.assertEqual(2, next_page_result.data[0].id)
        self.assertEqual('yyyyyyyyyyyyyyyyyyyy', next_page_result.data[0].uuid)
        self.assertEqual('My Value B', next_page_result.data[0].myField)

    def test_previous_page_simple_result_nested_collection(self):
        options = {
            'include': {
                'myDataTypeCollection': {
                    'after': 'bbbbbbbbbbb=',
                    'first': 1
                }
            },
            'where': {
                'id': {
                    'equals': 1
                }
            }
        }
        raw_curr_result = {
            'myDataType': {
                'myDataTypeCollection': {
                    'totalCount': 2,
                    'edges': [
                        {
                            'node': {
                                'id': 2,
                                'uuid': 'yyyyyyyyyyyyyyyyyyyy',
                                'myField': 'My Value B'
                            }
                        }
                    ],
                    'pageInfo': {
                        'hasPreviousPage': True,
                        'hasNextPage': False,
                        'startCursor': 'bbbbbbbbbbb=',
                        'endCursor': 'ccccccccccc='
                    },
                    '__typename': 'MyDataTypeConnection'
                }
            }
        }
        raw_prev_result = {
            'myDataType': {
                'myDataTypeCollection': {
                    'totalCount': 2,
                    'edges': [
                        {
                            'node': {
                                'id': 1,
                                'uuid': 'xxxxxxxxxxxxxxxxxxxx',
                                'myField': 'My Value A'
                            }
                        }
                    ],
                    'pageInfo': {
                        'hasPreviousPage': False,
                        'hasNextPage': True,
                        'startCursor': 'aaaaaaaaaaa=',
                        'endCursor': 'bbbbbbbbbbb='
                    },
                    '__typename': 'MyDataTypeConnection'
                }
            }
        }
        def callback(data_type_name, paged_options):
            # Parameter assertions
            self.assertEqual('myDataType', data_type_name)
            self.assertEqual({
                'include': {
                    'myDataTypeCollection': {
                        'before': 'bbbbbbbbbbb=',
                        'first': 1
                    }
                },
                'where': {
                    'id': {
                        'equals': 1
                    }
                }
            }, paged_options)

            return Result.build(
                'myDataType',
                'myDataType',
                raw_prev_result,
                paged_options,
                lambda _: None)

        result = Result.build(
            'myDataType',
            'myDataType',
            raw_curr_result,
            options,
            callback)

        prev_page_result = result.myDataTypeCollection.previous_page()

        # Total count assertions
        self.assertEqual(2, prev_page_result.total_count)

        # Data assertions
        self.assertEqual(1, len(prev_page_result.data))
        self.assertEqual(1, prev_page_result.data[0].id)
        self.assertEqual('xxxxxxxxxxxxxxxxxxxx', prev_page_result.data[0].uuid)
        self.assertEqual('My Value A', prev_page_result.data[0].myField)

    def test_next_page_collection_result_nested_collection(self):
        options = {
            'include': {
                'myWrapperDataType': {
                    'include': {
                        'myNestedDataTypeCollection': {
                            'first': 1
                        }
                    }
                }
            },
            'where': {
                'id': {
                    'equals': 1
                }
            }
        }
        raw_curr_result = {
            'myDataTypeCollection': {
                'totalCount': 10,
                'edges': [
                    {
                        'node': {
                            'myWrapperDataType': {
                                'myNestedDataTypeCollection': {
                                    'totalCount': 2,
                                    'edges': [
                                        {
                                            'node': {
                                                'id': 1,
                                                'uuid': 'xxxxxxxxxxxxxxxxxxxx',
                                                'myField': 'My Value A'
                                            }
                                        }
                                    ],
                                    'pageInfo': {
                                        'hasPreviousPage': False,
                                        'hasNextPage': True,
                                        'startCursor': 'ccccccccccc=',
                                        'endCursor': 'ddddddddddd='
                                    },
                                    '__typename': 'MyNestedDataTypeConnection'
                                }
                            }
                        }
                    }
                ],
                'pageInfo': {
                    'hasPreviousPage': False,
                    'hasNextPage': True,
                    'startCursor': 'aaaaaaaaaaa=',
                    'endCursor': 'bbbbbbbbbbb='
                },
                '__typename': 'MyDataTypeConnection'
            }
        }
        raw_next_result = {
            'myDataTypeCollection': {
                'totalCount': 10,
                'edges': [
                    {
                        'node': {
                            'myWrapperDataType': {
                                'myNestedDataTypeCollection': {
                                    'totalCount': 2,
                                    'edges': [
                                        {
                                            'node': {
                                                'id': 2,
                                                'uuid': 'yyyyyyyyyyyyyyyyyyyy',
                                                'myField': 'My Value B'
                                            }
                                        }
                                    ],
                                    'pageInfo': {
                                        'hasPreviousPage': True,
                                        'hasNextPage': False,
                                        'startCursor': 'ddddddddddd=',
                                        'endCursor': 'eeeeeeeeeee='
                                    },
                                    '__typename': 'MyNestedDataTypeConnection'
                                }
                            }
                        }
                    }
                ],
                'pageInfo': {
                    'hasPreviousPage': False,
                    'hasNextPage': True,
                    'startCursor': 'aaaaaaaaaaa=',
                    'endCursor': 'bbbbbbbbbbb='
                },
                '__typename': 'MyDataTypeConnection'
            }
        }
        def callback(data_type_name, paged_options):
            # Parameter assertions
            self.assertEqual('myDataType', data_type_name)
            self.assertEqual({
                'include': {
                    'myWrapperDataType': {
                        'include': {
                            'myNestedDataTypeCollection': {
                                'after': 'ddddddddddd=',
                                'first': 1
                            }
                        }
                    }
                },
                'where': {
                    'id': {
                        'equals': 1
                    }
                }
            }, paged_options)

            return Result.build(
                'myDataType',
                'myDataTypeCollection',
                raw_next_result,
                paged_options,
                lambda _: None)

        result = Result.build(
            'myDataType',
            'myDataTypeCollection',
            raw_curr_result,
            options,
            callback)

        next_page_result = result.data[0].myWrapperDataType.myNestedDataTypeCollection.next_page()

        # Total count assertions
        self.assertEqual(2, next_page_result.total_count)

        # Data assertions
        self.assertEqual(1, len(next_page_result.data))
        self.assertEqual(2, next_page_result.data[0].id)
        self.assertEqual('yyyyyyyyyyyyyyyyyyyy', next_page_result.data[0].uuid)
        self.assertEqual('My Value B', next_page_result.data[0].myField)

    def test_previous_page_collection_result_nested_collection(self):
        options = {
            'include': {
                'myWrapperDataType': {
                    'include': {
                        'myNestedDataTypeCollection': {
                            'after': 'ddddddddddd=',
                            'first': 1
                        }
                    }
                }
            },
            'where': {
                'id': {
                    'equals': 1
                }
            }
        }
        raw_curr_result = {
            'myDataTypeCollection': {
                'totalCount': 10,
                'edges': [
                    {
                        'node': {
                            'myWrapperDataType': {
                                'myNestedDataTypeCollection': {
                                    'totalCount': 2,
                                    'edges': [
                                        {
                                            'node': {
                                                'id': 2,
                                                'uuid': 'yyyyyyyyyyyyyyyyyyyy',
                                                'myField': 'My Value B'
                                            }
                                        }
                                    ],
                                    'pageInfo': {
                                        'hasPreviousPage': True,
                                        'hasNextPage': False,
                                        'startCursor': 'ddddddddddd=',
                                        'endCursor': 'eeeeeeeeeee='
                                    },
                                    '__typename': 'MyNestedDataTypeConnection'
                                }
                            }
                        }
                    }
                ],
                'pageInfo': {
                    'hasPreviousPage': False,
                    'hasNextPage': True,
                    'startCursor': 'aaaaaaaaaaa=',
                    'endCursor': 'bbbbbbbbbbb='
                },
                '__typename': 'MyDataTypeConnection'
            }
        }
        raw_prev_result = {
            'myDataTypeCollection': {
                'totalCount': 10,
                'edges': [
                    {
                        'node': {
                            'myWrapperDataType': {
                                'myNestedDataTypeCollection': {
                                    'totalCount': 2,
                                    'edges': [
                                        {
                                            'node': {
                                                'id': 1,
                                                'uuid': 'xxxxxxxxxxxxxxxxxxxx',
                                                'myField': 'My Value A'
                                            }
                                        }
                                    ],
                                    'pageInfo': {
                                        'hasPreviousPage': False,
                                        'hasNextPage': True,
                                        'startCursor': 'ccccccccccc=',
                                        'endCursor': 'ddddddddddd='
                                    },
                                    '__typename': 'MyNestedDataTypeConnection'
                                }
                            }
                        }
                    }
                ],
                'pageInfo': {
                    'hasPreviousPage': False,
                    'hasNextPage': True,
                    'startCursor': 'aaaaaaaaaaa=',
                    'endCursor': 'bbbbbbbbbbb='
                },
                '__typename': 'MyDataTypeConnection'
            }
        }
        def callback(data_type_name, paged_options):
            # Parameter assertions
            self.assertEqual('myDataType', data_type_name)
            self.assertEqual({
                'include': {
                    'myWrapperDataType': {
                        'include': {
                            'myNestedDataTypeCollection': {
                                'before': 'ddddddddddd=',
                                'first': 1
                            }
                        }
                    }
                },
                'where': {
                    'id': {
                        'equals': 1
                    }
                }
            }, paged_options)

            return Result.build(
                'myDataType',
                'myDataTypeCollection',
                raw_prev_result,
                paged_options,
                lambda _: None)

        result = Result.build(
            'myDataType',
            'myDataTypeCollection',
            raw_curr_result,
            options,
            callback)

        prev_page_result = result.data[0].myWrapperDataType.myNestedDataTypeCollection.previous_page()

        # Total count assertions
        self.assertEqual(2, prev_page_result.total_count)

        # Data assertions
        self.assertEqual(1, len(prev_page_result.data))
        self.assertEqual(1, prev_page_result.data[0].id)
        self.assertEqual('xxxxxxxxxxxxxxxxxxxx', prev_page_result.data[0].uuid)
        self.assertEqual('My Value A', prev_page_result.data[0].myField)
