import requests
from _secrets import ADD_DEVELOPER_TOKEN
API_URL = "https://mantikralligi1.pythonanywhere.com"


print(requests.get(API_URL + "/addDeveloper?token=" + ADD_DEVELOPER_TOKEN +"&githuburl=https://github.com/DavidNyan10/AliucordPlugins"))

"""
data = {'index': 0, 'query': '',"author":4}
data = requests.get("http://localhost:5000/getPlugins",json=data).json()
for a in data:
    print(a["plugin_name"])
"""

"""
data= {'author': '3', 'sort_by': 'repo_stars', 'index': 0, 'query': ''}
print(requests.get("https://mantikralligi1.pythonanywhere.com/getPlugins",json=data).json())
"""

data = {
    "token": ADD_DEVELOPER_TOKEN,
    "github_username": "mantikafasi",
    "plugins_repo_name": "AliucordPlugins",
    "ID": "7",
}
#requests.post(API_URL + "/updateDeveloper",json=data)
