import requests
data = {'index': 0, 'query': ''}
data = requests.get("http://mantikralligi1.pythonanywhere.com5000/getPlugins",json=data).json()
for a in data:
    print(a["plugin_name"])