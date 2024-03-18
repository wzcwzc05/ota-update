from flask import Flask, request, send_from_directory
from multiprocessing import Process, Queue
import json
import logging
import sys
import signal
import os
import time

app = Flask(__name__)
global updateQueue
updateQueue = Queue()

logger = logging.getLogger('http_server')
log_name = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())+"-http.log"
os.mkdir("log") if not os.path.exists("log") else None
logger.setLevel(logging.INFO)
file_log = logging.FileHandler(os.path.join("log", log_name))
console_log = logging.StreamHandler()
file_log.setLevel(logging.INFO)
console_log.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_log.setFormatter(formatter)
console_log.setFormatter(formatter)
logger.addHandler(file_log)
logger.addHandler(console_log)


def signal_handler(sig, frame):
    sys.exit(0)


@app.route("/startUpate", methods=["POST", "GET"])
def startUpdate():
    res = {"status": 200}
    try:
        dic = json.loads(request.form.get("content"))
        if (dic["package"] == None or dic["version"] == None or dic["branch"] == None):
            logger.error("Error Json Content")
            res["status"] = 400
            res["error"] = "Error Json Content"
            return str(json.dumps(res))
        updateQueue.put(dic)
        logger.info("Package:%s Branch:%s Version:%s Added into the Queue" % (
            str(dic["package"]), str(dic["branch"]), str(dic["version"])))
        return str(json.dumps(res))
    except Exception as e:
        logger.error(e)
        res["status"] = 400
        return str(json.dumps(res))


def http_server(update_queue):
    updateQueue = update_queue
    signal.signal(signal.SIGTERM, signal_handler)
