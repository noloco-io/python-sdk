class NolocoAccountApiKeyError(Exception):
    def __init__(self, project_name, error):
        super().__init__(
            'Your account API key did not authenticate for portal '
            f'{project_name}')
        self.project_name = project_name
        self.error = error


class NolocoDataTypeNotFoundError(Exception):
    def __init__(self, data_type_name):
        super().__init__(
            f'Could not find data type {data_type_name} in your project.')


class NolocoFieldNotFoundError(Exception):
    def __init__(self, field_name):
        super().__init__(
            f'Could not find field {field_name}.')


class NolocoFieldNotUniqueError(Exception):
    def __init__(self, data_type_name, field_name):
        super().__init__(
            f'Field {field_name} in data type {data_type_name} is not unique.')


class NolocoProjectApiKeyError(Exception):
    def __init__(self, project_name, error):
        super().__init__(
            'We could not validate the API client we setup for portal '
            f'{project_name}')
        self.project_name = project_name
        self.error = error


class NolocoQueryNotSupportedError(Exception):
    def __init__(self, query_name):
        super().__init__(
            f'{query_name} queries are not supported.')

class NolocoUnknownError(Exception):
    def __init__(self, error):
        super().__init__('Something went wrong!')
        self.error = error
