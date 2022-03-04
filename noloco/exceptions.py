class NolocoAccountApiKeyError(Exception):
    def __init__(self, project_name, error):
        super().__init__(
            'Your account API key did not authenticate for portal '
            f'{project_name}')
        self.project_name = project_name
        self.error = error


class NolocoProjectApiKeyError(Exception):
    def __init__(self, project_name, error):
        super().__init__(
            'We could not validate the API client we setup for portal '
            f'{project_name}')
        self.project_name = project_name
        self.error = error


class NolocoUnknownError(Exception):
    def __init__(self, error):
        super().__init__('Something went wrong!')
        self.error = error
