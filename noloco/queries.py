project_api_keys_query = '''
  query ($projectId: String!) {
    project(projectId: $projectId) {
      id
      name
      apiKeys {
        user
        project
        __typename
      }
      __typename
    }
  }
'''


validate_api_keys_query = '''
  query ($projectToken: String!) {
    validateApiKeys(projectToken: $projectToken) {
      user {
        id
        email
        __typename
      }
      projectName
      __typename
    }
  }
'''
