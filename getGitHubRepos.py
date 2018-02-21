#import re
import os
import requests
import simplejson as json

def getGitHubRepositoryInfo(apiToken):
  url = 'https://api.github.com/graphql'
  jsonQuery = """
  {
    viewer {
      repositories({{ repositoriesArgs }}) {
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
  repositoriesArgs = 'first: 5'
  query = { 'query' : jsonQuery.replace('{{ repositoriesArgs }}', repositoriesArgs)}
  headers = {'Authorization': 'token {0}'.format(apiToken)}
  queryResult = requests.post(url=url, json=query, headers=headers)
  results = json.loads(queryResult.text)

  repos = []
  for repository in results['data']['viewer']['repositories']['edges']:
    repos.append(repository)
  # Load next page of results (if there are more than 5 in total)
  while results['data']['viewer']['repositories']['pageInfo']['hasNextPage'] == True:
    # This substitution is failing and we are getting stuck in an infiniteloop!!!!!!!
    repositoriesArgs = 'first: 5, after: "' + results['data']['viewer']['repositories']['pageInfo']['endCursor'] + '"'
    nextPageQuery = { 'query' : jsonQuery.replace('{{ repositoriesArgs }}', repositoriesArgs)}
    queryResult = requests.post(url=url, json=nextPageQuery, headers=headers)
    results = json.loads(queryResult.text)
    for repository in results['data']['viewer']['repositories']['edges']:
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
for repository in j:
  if len(repository['node']['releases']['nodes']) >= 1:
    htmlTable += '  <tr>\n'
    htmlTable += '    <td><a href="{0}">{1}</a></td>\n'.format(repository['node']['url'], repository['node']['name'])
    htmlTable += '    <td>{0}</td>\n'.format(repository['node']['description'])
    htmlTable += '    <td>{0}/td>\n'.format(repository['node']['updatedAt'])
    htmlTable += '  </tr>\n'

htmlTable += '</table>\n'
print(htmlTable)