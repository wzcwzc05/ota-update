from flask import Flask, request, send_from_directory
import json
import os
import hashlib

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


if (__name__ == "__main__"):
    app.run(host=flask_host, port=flask_port, debug=isDebug)
