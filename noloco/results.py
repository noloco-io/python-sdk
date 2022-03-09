from pydash import camel_case, get


class Result(dict):
    def __init__(self, result, options, client):
        for key, value in result.items():
            if type(value) is dict:
                key_options = get(options, f'include.{key}', {})

                if get(value, 'edges') is not None:
                    # Wrap a collection in a CollectionResult to give it pagination
                    # helpers.
                    result[key] = CollectionResult(value, key_options, client)
                else:
                    # Otherwise traverse each field in the result and recursively wrap
                    # any that are collections.
                    result[key] = Result(value, key_options, client)
            else:
                result[key] = value

        dict.__init__(self, result)

    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value

    @staticmethod
    def build(data_type_name, result, options, client):
        result = Result(result, {'include': {data_type_name: options}}, client)
        return result[data_type_name]


class CollectionResult:
    def __init__(self, result, options, client):
        self.__client = client
        self.__data_type_name = get(result, '__typename')
        self.__options = options
        self.__page_info = result['pageInfo']

        self.total_count = result['totalCount']
        self.data = []
        for edge in result['edges']:
            self.data.append(Result(edge['node'], options, client))

    def __data_type_to_paginate(self):
        return camel_case(self.__data_type_name).replace('Connection', '')

    def previous_page(self):
        if not self.__page_info['hasPreviousPage']:
            return None
        else:
            options = self.__options
            options.pop('after', None)
            options['before'] = self.__page_info['startCursor']
            return self.__client.find(
                self.__data_type_to_paginate(),
                options)

    def next_page(self):
        if not self.__page_info['hasNextPage']:
            return None
        else:
            options = self.__options
            options.pop('before', None)
            options['after'] = self.__page_info['endCursor']
            return self.__client.find(
                self.__data_type_to_paginate(),
                options)
