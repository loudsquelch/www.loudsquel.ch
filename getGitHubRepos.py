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
#x = getGitHubRepositoryInfo("<stick_key_here>")
exportPath = os.getenv("USERPROFILE") + "\\git-repo-info.json" 
#f = open(exportPath,"w+")
#f.write(json.dumps(x))
#f.close()

f = open(exportPath,"r")
j=json.loads(f.read())
f.close()

# Get repos that have at least one release
# and therefore warrant being displayed
htmlTable = '<table style="width:100%">\n'
htmlTable += '  <tr>\n'
htmlTable += '    <th>Name</th>\n'
htmlTable += '    <th>Description</th>\n'
htmlTable += '    <th>Updated</th>\n'
htmlTable += '  </tr>\n'
# print(j['data']['viewer']['repositories']['totalCount'])
for edge in j['data']['viewer']['repositories']['edges']:
  if len(edge['node']['releases']['nodes']) >= 1:
    htmlTable += '  <tr>\n'
    htmlTable += '    <td><a href="{0}">{1}</a></td>\n'.format(edge['node']['url'], edge['node']['name'])
    htmlTable += '    <td>{0}</td>\n'.format(edge['node']['description'])
    htmlTable += '    <td>{0}/td>\n'.format(edge['node']['updatedAt'])
    htmlTable += '  </tr>\n'

htmlTable += '</table>\n'
print(htmlTable)