import requests
token = "5MRKMmBbW1VpNDYjrLI8eJfUxIKY1W"

ip = "http://192.168.1.35"

json = { "token":token,
    "comment":"This is a test review",
    "star":1,
    "userid":123812312 }
webhookurl = ""
data = {
    "content":"test",
    "username":"User Reviews Reports"
}
res = requests.post(webhookurl,data=data)
print(res.text)