import json

config = {
    "courseFile": "pick.txt",
    "timeInterval": 0.3
}

with open("./config/config.json", "r") as f:
    str = f.read()
    dic = json.loads(str)
    for (k, v) in dic.items():
        config[k] = v