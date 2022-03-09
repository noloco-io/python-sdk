from pydash import (
    get,
    set_)
from re import sub


class Result(dict):
    def __init__(
            self,
            data_type_name,
            result_name,
            result,
            options_path,
            options,
            client):
        for key, value in result.items():
            if options_path == '':
                next_options_path = '.'.join(['include', key])
            else:
                next_options_path = '.'.join([options_path, 'include', key])

            if type(value) is dict:
                if get(value, 'edges') is not None:
                    # Wrap a collection in a CollectionResult to give it
                    # pagination helpers.
                    result[key] = CollectionResult(
                        data_type_name,
                        result_name,
                        value,
                        next_options_path,
                        options,
                        client)
                else:
                    # Otherwise traverse each field in the result and
                    # recursively wrap any that are collections.
                    result[key] = Result(
                        data_type_name,
                        result_name,
                        value,
                        next_options_path,
                        options,
                        client)
            else:
                result[key] = value

        dict.__init__(self, result)

    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value

    @staticmethod
    def build(data_type_name, result_name, result, options, client):
        result = Result(
            data_type_name,
            result_name,
            result,
            '',
            {'include': {result_name: options}},
            client)

        return result[result_name]


class CollectionResult:
    def __init__(
            self,
            data_type_name,
            result_name,
            result,
            result_path,
            options,
            client):
        self.__client = client
        self.__data_type_name = data_type_name
        self.__options = options
        self.__result_path = result_path
        self.__page_info = result['pageInfo']
        self.__result_name = result_name

        self.total_count = result['totalCount']
        self.data = []
        for index, edge in enumerate(result['edges']):
            self.data.append(
                Result(
                    data_type_name,
                    result_name,
                    edge['node'],
                    result_path + f'[{index}]',
                    options,
                    client))

    def __options_path(self):
        return sub('\[[0-9]+\]', '', self.__result_path)

    def __page_path(self):
        unwrapped_path = sub(
            '^include\.' + self.__result_name,
            '',
            self.__result_path)
        return unwrapped_path.replace('include.', '').replace('[', 'data[')

    def __page(self, paged_options):
        # Overwrite the options that applied to this collection with the new
        # options and then unwrap these to remove the artificial
        # 'include': { data_type_name: ... } that we added when building the
        # result.
        client_options = self.__options
        set_(client_options, self.__options_path(), paged_options)
        client_options = get(
            client_options,
            f'include.{self.__result_name}')

        # Re-run the equivalent query that produced this page originally with
        # the new options.
        result = self.__client(
            self.__data_type_name,
            client_options)

        # Determine where in the result the page is returned and hoist it up to
        # return it back.
        page_path = self.__page_path()
        if page_path == '':
            return result
        else:
            return get(result, page_path)

    def previous_page(self):
        if not self.__page_info['hasPreviousPage']:
            return None
        else:
            # Fetch the options that applied to this collection, remove the
            # 'after' parameter if it exists and set the 'before' parameter to
            # the start cursor of the current page.
            options = get(self.__options, self.__options_path())
            options.pop('after', None)
            options['before'] = self.__page_info['startCursor']

            return self.__page(options)

    def next_page(self):
        if not self.__page_info['hasNextPage']:
            return None
        else:
            # Fetch the options that applied to this collection, remove the
            # 'before' parameter if it exists and set the 'after' parameter to
            # the end cursor of the current page.
            options = get(self.__options, self.__options_path())
            options.pop('before', None)
            options['after'] = self.__page_info['endCursor']

            return self.__page(options)
