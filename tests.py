import requests

"""
data = {'index': 0, 'query': '',"author":4}
data = requests.get("http://localhost:5000/getPlugins",json=data).json()
for a in data:
    print(a["plugin_name"])
"""


data= {'author': '3', 'sort_by': 'repo_stars', 'index': 0, 'query': ''}
print(requests.get("https://mantikralligi1.pythonanywhere.com/getPlugins",json=data).json())
