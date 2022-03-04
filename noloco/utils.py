def gql_args(args):
    variables = {}

    for arg in args:
        variables[arg] = args[arg]['value']

    return variables
