from flask import Flask, request, send_from_directory
from multiprocessing import Process, Queue
import json
import logging
import sys
import signal
import os
import time
from update_package import update_package
import requests
from urllib.parse import urljoin
import socket

app = Flask(__name__)
logger = logging.getLogger('http_server')
log_name = time.strftime(
    "%Y-%m-%d-%H-%M-%S", time.localtime())+"-http.log"  # 日志文件名
os.mkdir("log") if not os.path.exists("log") else None  # 创建log文件夹
logger.setLevel(logging.INFO)
file_log = logging.FileHandler(os.path.join("log", log_name))   # 文件输出
console_log = logging.StreamHandler()   # 控制台输出
file_log.setLevel(logging.INFO)
console_log.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # 日志格式
file_log.setFormatter(formatter)
console_log.setFormatter(formatter)
logger.addHandler(file_log)
logger.addHandler(console_log)


def signal_handler(sig, frame):
    process.terminate()
    sys.exit(0)


def get_local_ip():  # 获取本地ip
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return str(ip)


def heartbeat(addr: str, device_id: int):   # 心跳
    while (True):
        try:
            url = urljoin(addr, "/heartbeat")
            res = requests.post(url, data={"id": int(device_id)})
            if (res.status_code == 200):
                time.sleep(10)
            else:
                time.sleep(2)
        except Exception as e:
            logger.error("Heartbeat Failed")
            logger.error(e)
            time.sleep(10)


def checkContent(content: dict) -> bool:    # 检查content.json是否合法
    required_keys = ["sha256", "version", "branch", "package", "local",
                     "remote", "BeforeUpdate", "AfterUpdate", "dependencies", "restore"]
    for i in required_keys:
        if i not in content:
            return False
    return True


@app.route("/test", methods=["POST", "GET"])
def test():
    res = {"status": 200}
    return str(json.dumps(res))


@app.route("/", methods=["POST", "GET"])
def main():
    res = {"status": 200}
    return str(json.dumps(res))


@app.route("/startUpdate", methods=["POST", "GET"])
def startUpdate():  # 开始更新
    res = {"status": 200}
    try:
        if (not updateQueue.empty()):   # 队列不为空
            res["status"] = 400  # Bad Request
            res["error"] = "Queue not empty"
            return str(json.dumps(res))
        dic = json.loads(request.form.get("content"))   # 获取包的content.json
        dic = json.loads(dic)
        logger.info("Package:%s Branch:%s Version:%s Start Update" % (
            str(dic["package"]), str(dic["branch"]), str(dic["version"])))
        if (not checkContent(dic)):  # 检查content.json是否合法
            logger.error("Error Json Content")
            res["status"] = 400
            res["error"] = "Error Json Content"
            return str(json.dumps(res))
        t = update_package(dic, register_path, device_id, None)  # 创建更新包
        updateQueue.put(t)  # 加入队列
        logger.info("Package:%s Branch:%s Version:%s Added into the Queue" % (
            str(dic["package"]), str(dic["branch"]), str(dic["version"])))
        return str(json.dumps(res))
    except Exception as e:
        logger.error(e)
        res["status"] = 400
        return str(json.dumps(res))


@app.route("/getInfo", methods=["POST", "GET"])
def getInfo():  # 获取设备device.json信息
    res = {"status": 200}
    with open("device.json", "r") as f:
        res["content"] = f.read()
    return str(json.dumps(res))


def http_server(update_queue: Queue):   # http服务器
    with open("device.json", "r") as f:
        config = json.loads(f.read())
    flask_host = config["flask"]["host"]
    flask_port = int(config["flask"]["port"])
    isDebug = bool(config["flask"]["debug"])
    global updateQueue
    global register_path
    global device_id
    register_path = config["registry"]
    while (True):   # 注册设备
        try:
            url = urljoin(register_path, "/register")
            ip_addr = get_local_ip()
            addr = "http://"+ip_addr+":"+str(flask_port)
            res = requests.post(url, data={"content": str(
                json.dumps(config)), "address": addr})
            device_id = json.loads(res.text)["id"]
            config["device_id"] = device_id
            with open("device.json", "w") as f:
                f.write(str(json.dumps(config)))
            break
        except Exception as e:
            logger.error(e)
            logger.error("Register Failed")
            time.sleep(2)
    updateQueue = update_queue
    global process
    process = Process(target=heartbeat, args=(
        register_path, device_id))    # 心跳进程
    process.daemon = True
    process.start()
    app.logger.addHandler(file_log)
    app.logger.addHandler(console_log)
    app.run(host=flask_host, port=flask_port, debug=isDebug)
    signal.signal(signal.SIGTERM, signal_handler)
