import re
import os
import requests
import simplejson as json

def getGitHubRepositoryInfo(apiToken):
  url = 'https://api.github.com/graphql'
  jsonQuery = """
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
  # Run initial query, limiting results to 5 (low enough to test code works as I only have 9 repos at the time of testing)
  query = { 'query' : jsonQuery}
  headers = {'Authorization': 'token {0}'.format(apiToken)}
  queryResult = requests.post(url=url, json=query, headers=headers)
  results = json.loads(queryResult.text)

  repos = []
  for repository in results['data']['viewer']['repositories']:
    repos.append(repository)
  # Load next page of results (if there are more than 5 in total)
  while results['data']['viewer']['repositories']['pageInfo']['hasNextPage'] == True:
    # This substitution is failing and we are getting stuck in an infiniteloop!!!!!!!
    nextPageQuery = { 'query' : re.sub('repositories(first: 5)','repositories(first: 5, after: {0})'.format(results['data']['viewer']['repositories']['pageInfo']['endCursor']),jsonQuery)}
    queryResult = requests.post(url=url, json=nextPageQuery, headers=headers)
    results = json.loads(queryResult.text)
    for repository in results['data']['viewer']['repositories']:
      repos.append(repository)    
  
  return repos

#  Need to work out how to securely store this in Azure
# https://github.com/blog/1509-personal-api-tokens
x = getGitHubRepositoryInfo("")
exportPath = os.getenv("USERPROFILE") + "\\git-repo-info2.json" 
f = open(exportPath,"w+")
f.write(json.dumps(x))
f.close()

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