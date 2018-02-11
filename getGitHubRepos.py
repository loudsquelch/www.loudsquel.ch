import re
import requests
import simplejson as json

def getGitHubRepositoryInfo(apiToken):
  url = 'https://api.github.com/graphql'
  # query = """
  # {
  #   viewer {
  #     repositories(first: 30) {
  #       totalCount
  #       pageInfo {
  #         hasNextPage
  #         endCursor
  #       }
  #       edges {
  #         node {
  #           name
            
  #         }
  #       }
  #     }
  #   }
  # }
  # """
  firstQuery = """
  {
    viewer {
      repositories(first: 5) {
        totalCount
        pageInfo {
          hasNextPage
          endCursor
        }
        edges {
          node {
            name
            description
            updatedAt
            url
            releases(first:1) {
              nodes {
                name
              }
            }
          }
        }
      }
    }
  }
  """
  # Sub 'repositories(first: 5) {' with 'repositories(first: 5, after: {{cursor}}) {' if there is pagination
  nextQuery = """
  {
    viewer {
      repositories(first: 5, after: {{cursor}}) {
        totalCount
        pageInfo {
          hasNextPage
          endCursor
        }
        edges {
          node {
            name
            description
            updatedAt
            url
            releases(first:1) {
              nodes {
                name
              }
            }
          }
        }
      }
    }
  }
  """
  query = { 'query' :  firstQuery}
  headers = {'Authorization': 'token %s' % apiToken}
  r = requests.post(url=url, json=query, headers=headers)
  j = json.loads(r.text)
  return j

#  Need to work out how to securely store this in Azure
x = getGitHubRepositoryInfo("<enter_key_here")

# Prints total count of repositories
print(x['data']['viewer']['repositories']['totalCount'])