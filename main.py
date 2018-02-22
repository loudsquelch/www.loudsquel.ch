import os
import simplejson as json

from flask import Flask
app = Flask(__name__)

def getGitRepositoriesFromFile():
  wwwroot = os.path.abspath(os.path.dirname(__file__))
  gitHubRepoJsonPath = os.path.join(wwwroot, "github-dump","git-repo-info.json")
  f = open(gitHubRepoJsonPath,"r")
  j=json.loads(f.read())
  f.close()
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
  for repository in j:
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

@app.route('/')
def hello_world():
  #return 'Hello, World!'
  return getGitRepositoriesFromFile()

if __name__ == '__main__':
  app.run()