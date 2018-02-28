'''
This is designed to be run as a webjob as per:
https://github.com/projectkudu/kudu/wiki/WebJobs
'''

# Thank you https://lnx.azurewebsites.net/python-site-packages-in-azure-python-webjobs/
import sys
sitepackage = "D:\home\site\wwwroot\env\Lib\site-packages"
sys.path.append(sitepackage)

import os
import requests
import simplejson as json

def getGitHubRepositoryInfo(apiToken):
  '''Gets information pertaining to repositories in a GitHub account
  Args:
    apiToken (str): GitHb GraphQL API token (generated as per https://github.com/blog/1509-personal-api-tokens)
  Returns:
    list: A list of repositories with assocaiated information as JSON, e.g.:
      [
          {
              "node": {
                  "name": "www.loudsquel.ch",
                  "description": "Website content",
                  "updatedAt": "2018-02-01T22:49:06Z",
                  "url": "https://github.com/loudsquelch/www.loudsquel.ch",
                  "releases": {
                      "nodes": [
                          {
                              "name": "Initial Release"
                          }
                      ]
                  }
              }
          }
      ]
  '''
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
  
  try:
    queryResult = requests.post(url=url, json=query, headers=headers)
  except requests.exceptions.RequestException as e:
    print("Failed to connect to {0}. Error: {1}".format(url,e))
    return None
  except:
    print("Unexpected error: {0}".format(sys.exc_info()[0]))
    return None
  try:
    results = json.loads(queryResult.text)
    print()
    if 'message' in results:
      print("Query failed.  Error message: {0}".format(results['message']))
      return None
    elif results['data'] is None:
      # Let's not go overboard - the first error will be sufficient to start troubleshooting...
      print("Query failed.  Error message: {0}".format(results['errors'][0]['message']))
      return None
  except:
    print("Unknown error occured. Query result: {0}".format(results))
    return None

  repos = []
  try:
    for repository in results['data']['viewer']['repositories']['edges']:
      repos.append(repository)
  except:
    print("Error occurred whilst enumerating query results: {0}".format(results))

  # Load next page of results (if there are more than 5 in total)
  # Arghhh!!! should have written this as a recursive function, can't be bothered to change it now! Ctrl+C, Ctrl+V...
  while results['data']['viewer']['repositories']['pageInfo']['hasNextPage'] == True:
    # This substitution is failing and we are getting stuck in an infiniteloop!!!!!!!
    repositoriesArgs = 'first: 5, after: "' + results['data']['viewer']['repositories']['pageInfo']['endCursor'] + '"'
    nextPageQuery = { 'query' : jsonQuery.replace('{{ repositoriesArgs }}', repositoriesArgs)}
    try:
      queryResult = requests.post(url=url, json=nextPageQuery, headers=headers)
    except requests.exceptions.RequestException as e:
      print("Failed to connect to {0}. Error: {1}".format(url,e))
      return None
    except:
      print("Unexpected error: {0}".format(sys.exc_info()[0]))
      return None
    try:
      results = json.loads(queryResult.text)
      print()
      if 'message' in results:
        print("Query failed.  Error message: {0}".format(results['message']))
        return None
      elif results['data'] is None:
        # Let's not go overboard - the first error will be sufficient to start troubleshooting...
        print("Query failed.  Error message: {0}".format(results['errors'][0]['message']))
        return None
    except:
      print("Unknown error occured. Query result: {0}".format(results))
      return None

    try:
      for repository in results['data']['viewer']['repositories']['edges']:
        repos.append(repository)
    except:
      print("Error occurred whilst enumerating query results: {0}".format(results))
  
  return repos

# Initialize vars
apiToken = ''
repos = []
# Path to output data is determined relative to where this script is located ad=nd
scriptParentPath = os.path.abspath(os.path.dirname(__file__))                       # Gets us the parent dir of the script
appPath = scriptParentPath.replace('\\App_Data\\jobs\\triggered\\github-dump','')   # Gets us to path app
outputFilePath = os.path.join(appPath, "github-dump","github-repo-info.json")       # Gets us to the output path

# # Retrieve token from environmment variable
if 'WEBSITE_SITE_NAME' in os.environ:
  # Existence of variable confirms I am running in Azure so pull required information from the
  # from app settings configuration
  # API token for GitHub should be configured in environment variable 'GITHUB_API_TOKEN' site was correctly deployed
  if 'GITHUB_API_TOKEN' in os.environ:
    apiToken = os.environ['GITHUB_API_TOKEN']
  else:
    # Throw error and exit
    sys.exit("Environment variable 'GITHUB_API_TOKEN' undefined.")
else:
  # Assume I am running locally and get apiToken from a file in development environment that is not 
  # added to source control (assumed to be in ~\Documents\code\local-only\secrets\github-api-token)
  localApiTokenFilePath = os.path.join(appPath,"local","github-api-token")
  try:
    localApiTokenFile = open(localApiTokenFilePath, "r")
    apiToken = localApiTokenFile.read().strip()
  except IOError as e:
  	print("Failed to write to file. Error {0}: {1}".format(e.errno, e.strerror))
  except:
    print("Unexpected error: {0}".format(sys.exc_info()[0]))
  finally:
    localApiTokenFile.close()

# Without a token I need to bail!
if apiToken == '':
  sys.exit("Failed to retrieve API token for GitHub authentication")

# Connect to GitHub and pull back repository info
repos = getGitHubRepositoryInfo(apiToken)
if repos != None:
  # Write result out to file
  try:
    outFile = open(outputFilePath, "w+")
    try:
      outFile.write(json.dumps(repos,indent=2,sort_keys=True))
      print("Dumped query result to {0}".format(outputFilePath))
    except IOError as e:
      sys.exit("Failed to write to file {0}. Error: {1}".format(outputFilePath, e))
    except:
      sys.exit("Unexpected error writing to {0}: {1}".format(outputFilePath,sys.exc_info()[0]))
    finally:
      outFile.close()
  except IOError as e:
    sys.exit("Failed to open file {0} for writing. Error: {1}".format(outputFilePath, e))
  except:
    sys.exit("Unexpected error: {0}".format(sys.exc_info()[0]))
else:
  sys.exit("No GitHub repository info to dump out to file.")