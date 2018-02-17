import re
import os
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
# https://github.com/blog/1509-personal-api-tokens
x = getGitHubRepositoryInfo("<stick_key_here>")
exportPath = os.getenv("USERPROFILE") + "\\git-repo-info.json" 
f = open(exportPath,"w+")
f.write(json.dumps(x))
f.close()

f = open(exportPath,"r")
j=json.loads(f.read())
f.close()



# Prints total count of repositories
print(j['data']['viewer']['repositories']['totalCount'])