import requests
data = {
    "query":"",
    "index":0,
    "sort_by":"timestamp"
}
data = requests.get("http://localhost:5000/getPlugins",json=data).json()
for a in data:
    print(a["plugin_name"])