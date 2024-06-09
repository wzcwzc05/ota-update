from flask import Flask, request, send_from_directory
import json
import logging
import os
import deviceManager as dM
import time
import multiprocessing

config = {}
with open("config.json", "r") as f:
    config = json.loads(f.read())
flask_host = config["flask"]["host"]
flask_port = int(config["flask"]["port"])
isDebug = bool(config["flask"]["debug"])
registerUrl = config["registerUrl"]
serverUrl = config["serverUrl"]
log_path = "log/"
app = Flask(__name__)

os.mkdir("log") if not os.path.exists("log") else None
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logfile_name = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())+"-http.log"
file_handler = logging.FileHandler(os.path.join(log_path, logfile_name))
console_handler = logging.StreamHandler()
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


@app.route("/test")
def hello_world():
    dic = {"status": 200}
    return str(json.dumps(dic))


if (__name__ == "__main__"):
    app.run(host=flask_host, port=flask_port, debug=isDebug)
