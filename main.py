import os
import simplejson as json
import sys

from flask import Flask, send_from_directory
from flask_cache import Cache
from time import sleep

# simple cache type is recommended single process dev app
app = Flask(__name__)
cache = Cache(app,config={'CACHE_TYPE': 'simple'})

@cache.cached(timeout=10, key_prefix="getGitRepositoriesFromFile")
def getGitRepositoriesFromFile():
  # Construct path for file to read from (file is created by running get_github_repos.py)
  wwwroot = os.path.abspath(os.path.dirname(__file__))
  gitHubRepoJsonPath = os.path.join(wwwroot, "github-dump","github-repo-info.json")
  for i in range(0,4):
    if i > 0:
      # Retries to deal with the unfortunate case of a get_github_repos.py
      # having the file open for writing give it 20ms and try again!
      sleep(0.02)
      print("Retrying GitHub repository data import (retry {0})".format(i))
    try:
      importFile = open(gitHubRepoJsonPath,"r")
      repositories = json.loads(importFile.read())
      break
    except IOError as e:
      print("Failed to read from file {0}. Error: {1}".format(gitHubRepoJsonPath,e))
    except:
      print("Unexpected error: {0}".format(sys.exc_info()[0]))
    finally:
      try:
        importFile.close()
      except:
        pass
        
  html = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd\n">'
  html += '<html>\n'
  html += '<head>\n'
  html += '  <link rel="stylesheet" type="text/css" href="/static/styles/css/main.css">\n'
  html += '  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>\n'
  html += '  <title>loudsquel.ch</title>\n'
  html += '</head>\n'
  html += '<body>\n'
  html += '  <br>\n'
  html += '  <center><a href="https://github.com/loudsquelch"><img src="/static/images/title.png" alt="loudsquelch@github"></a></center>\n'
  html += '  <br><br>\n'
  htmlTable = '<table style="width:100%">\n'
  htmlTable += '  <tr>\n'
  htmlTable += '    <th>Name</th>\n'
  htmlTable += '    <th>Description</th>\n'
  htmlTable += '    <th>Updated</th>\n'
  htmlTable += '  </tr>\n'
  for repository in repositories:
    # Only render if there are 1 or more releases associated with the repository
    if len(repository['node']['releases']['nodes']) >= 1:
      htmlTable += '  <tr>\n'
      htmlTable += '    <td><a href="{0}">{1}</a></td>\n'.format(repository['node']['url'], repository['node']['name'])
      htmlTable += '    <td>{0}</td>\n'.format(repository['node']['description'])
      htmlTable += '    <td>{0}</td>\n'.format(repository['node']['updatedAt'])
      htmlTable += '  </tr>\n'
  htmlTable += '</table>\n'
  html += htmlTable
  html += '</body>\n'
  html += '</html>\n'
  return html

# Required for Let's Encrypt cert auto-renewal
@app.route('/.well-known/<path:filename>')
def letsencryptchallenges(filename):
  dotWellKnownPath = os.path.join(app.root_path, '.well-known')
  # return "{0} {1} {2}".format(app.root_path,filename,dotWellKnownPath)
  if filename[-1] == '/':
    # default to returning index.html if no filename is specified
    return send_from_directory(dotWellKnownPath, filename + 'index.html')
  else:
    return send_from_directory(dotWellKnownPath, filename)

@app.route('/')
def index():
  try:
    return getGitRepositoriesFromFile()
  except:
    print("Rendering default page without repository info")
    html = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd\n">'
    html += '<html>\n'
    html += '<head>\n'
    html += '  <link rel="stylesheet" type="text/css" href="/static/styles/css/main.css">\n'
    html += '  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>\n'
    html += '  <title>loudsquel.ch</title>\n'
    html += '</head>\n'
    html += '<body>\n'
    html += '  <br>\n'
    html += '  <center><a href="https://github.com/loudsquelch"><img src="/static/images/title.png" alt="loudsquelch@github"></a></center>\n'
    html += '  <br><br>\n'
    html += '  <center><h3>Unable to render GitHub repository information</h3></center>\n'
    html += '</body>\n'
    html += '</html>\n'
    return html    

if __name__ == '__main__':
  app.run()
