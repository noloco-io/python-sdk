from pydash import get


class Result:
    @staticmethod
    def traverse(data_type_name, result, options, client):
        if get(result, 'edges') is not None:
            # Wrap a collection in a CollectionResult to give it pagination
            # helpers.
            return CollectionResult(data_type_name, result, options, client)
        else:
            # Otherwise traverse each field in the result and recursively wrap
            # any that are collections.
            for key, value in result.items():
                if type(value) is dict:
                    key_options = get(options, f'include.{key}', {})
                    result[key] = Result.traverse(
                        value,
                        data_type_name,
                        key_options,
                        client)
            return result

    @staticmethod
    def unwrap(data_type_name, result):
        return result[data_type_name]


class CollectionResult:
    def __init__(self, data_type_name, result, options, client):
        self.__client = client
        self.__data_type_name = data_type_name
        self.__options = options
        self.__page_info = result['pageInfo']

        self.total_count = result['totalCount']
        self.data = []
        for edge in result['edges']:
            self.data.append(
                Result.traverse(
                    data_type_name,
                    edge['node'],
                    get(options, f'include.{data_type_name}', {}),
                    client))

    def previous_page(self):
        if not self.__page_info['hasPreviousPage']:
            return None
        else:
            options = self.__options
            options.pop('after', None)
            options['before'] = self.__page_info['startCursor']
            return self.__client.find(
                self.__data_type_name,
                options)

    def next_page(self):
        if not self.__page_info['hasNextPage']:
            return None
        else:
            options = self.__options
            options.pop('before', None)
            options['after'] = self.__page_info['endCursor']
            return self.__client.find(
                self.__data_type_name,
                options)
