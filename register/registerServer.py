from flask import Flask, request, send_from_directory
import json
import os
import hashlib
import deviceManager as dM

config = {}
with open("config.json", "r") as f:
    config = json.loads(f.read())
flask_host = config["flask"]["host"]
flask_port = int(config["flask"]["port"])
isDebug = bool(config["flask"]["debug"])
storage_path = config["storage"]["path"]
app = Flask(__name__)


@app.route("/test")
def hello_world():
    dic = {"status": 200}
    return str(json.dumps(dic))


@app.route("/register")
def register():
    remote_ip = request.remote_addr
    print(remote_ip)
    content = json.loads(request.form.get("content"))
    address = request.form.get("address")
    if (content == None or address == None):
        dic = {"status": 400, "error": "Bad Request"}
        return str(json.dumps(dic))
    else:
        dic = {"status": 200}
        id = dM.registerDevice(content, remote_ip)
        dic["id"] = id
        return str(json.dumps(dic))


@app.route("/heartbeat")
def heartbeat():
    id = request.form.get("id")
    if (id == None):
        dic = {"status": 400, "error": "Bad Request"}
        return str(json.dumps(dic))
    else:
        dic = {"status": 200}
        if (dM.heartBeatDevice(id)):
            return str(json.dumps(dic))
        else:
            dic = {"status": 404, "error": "Device Not Found"}
            return str(json.dumps(dic))


@app.route("/logout")
def register():
    id = request.form.get("id")
    if (id == None):
        dic = {"status": 400, "error": "Bad Request"}
        return str(json.dumps(dic))
    else:
        dic = {"status": 200}
        if (dM.logoutDevice(id)):
            return str(json.dumps(dic))
        else:
            dic = {"status": 404, "error": "Device Not Found"}
            return str(json.dumps(dic))


if (__name__ == "__main__"):
    app.run(host=flask_host, port=flask_port, debug=isDebug)
