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
log_path = "log/"
totallength = 0
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


def updateNext():   # 从队列中更新下一个设备
    if (len(dM.updateList) > 0):
        updatePackage = dM.updateList[0]
        status = dM.update(updatePackage)   # 更新设备
        if (not status):    # 更新失败
            info = "Device:%s Package:%s Branch:%s Start Update Failed" % (
                updatePackage["id"], updatePackage["package"], updatePackage["branch"])
            logger.error(info)
            dM.updateByDeviceId(updatePackage["id"])
            dM.updateList.pop(0)
            updateNext()
            return
        dM.updateList.pop(0)
    else:   # 更新队列为空
        time.sleep(2)
        dM.updateFromDevice()
        info = "All Update Complete"
        logger.info(info)
        dM.updateStatus = {"device": 0, "package": {"package": "0",
                                                    "version": "0", "branch": "0"}, "status": "complete"}


def updateDevice():  # 从设备获取设备信息
    while (True):
        try:
            dM.updateFromDevice()
            time.sleep(10)
        except Exception as e:
            logger.error(e)
            time.sleep(5)


@app.route("/test")
def hello_world():
    dic = {"status": 200}
    return str(json.dumps(dic))


@app.route("/register", methods=["POST", "GET"])
def register():
    remote_ip = request.remote_addr
    content = json.loads(request.form.get("content"))
    address = request.form.get("address")
    if (content == None or address == None):
        dic = {"status": 400, "error": "Bad Request"}
        return str(json.dumps(dic))
    else:
        dic = {"status": 200}
        id = dM.registerDevice(content, address)
        dic["id"] = id
        return str(json.dumps(dic))


@app.route("/heartbeat", methods=["POST", "GET"])
def heartbeat():
    device_id = request.form.get("id")
    if (device_id == None):
        dic = {"status": 400, "error": "Bad Request"}
        return str(json.dumps(dic))
    else:
        dic = {"status": 200}
        if (dM.heartBeatDevice(device_id)):
            return str(json.dumps(dic))
        else:
            dic = {"status": 404, "error": "Device Not Found"}
            return str(json.dumps(dic))


@app.route("/logout", methods=["POST", "GET"])
def logout():
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


@app.route("/getAllInfo", methods=["POST", "GET"])
def getAllInfo():
    dic = {"status": 200, "devices": []}
    dM.deleteExpiredDevices()
    devices = dM.getAllDevicesId()
    if (devices != None):
        for id in devices:
            temp = {}
            temp["id"] = id
            temp["packages"] = dM.getDeviceById(id)
            temp["device"] = dM.getDeviceNameById(id)
            if (temp["packages"] == None):
                continue
            dic["devices"].append(temp)
        return str(json.dumps(dic))
    else:
        dic = {"status": 400, "error": "Server Error"}
        return str(json.dumps(dic))


@app.route("/getDeviceInfo", methods=["POST", "GET"])
def getDeviceInfo():
    dM.deleteExpiredDevices()
    id = request.args.get("id")
    dic = {"status": 200}
    lst = dM.getDeviceById(id)
    if (lst == None):
        dic = {"status": 404, "error": "Device Not Found"}
        return str(json.dumps(dic))
    else:
        dic["id"] = id
        dic["packages"] = lst
        dic["device"] = dM.getDeviceNameById(id)
        return str(json.dumps(dic))


@app.route("/getStatus", methods=["POST", "GET"])
def getStatus():
    dic = {"status": 200}
    dic["update"] = dM.updateStatus
    return str(json.dumps(dic))


@app.route("/getUpdatelist", methods=["POST", "GET"])
def getUpdatelist():
    dic = {"status": 200}
    dic["list"] = dM.updateList
    if (totallength != 0):
        dic["progress"] = (totallength - len(dM.updateList))/totallength*100
    else:
        dic["progress"] = 0
    return str(json.dumps(dic))


@app.route("/delFromlist", methods=["POST", "GET"])
def delFromlist():
    content = json.loads(request.form.get("content"))
    delitems = content["items"]
    for i in delitems:
        for j in dM.updateList:
            if (i == j):
                dM.updateList.remove(i)


@app.route("/updateInfo", methods=["POST", "GET"])
def updateInfo():
    dic = {"status": 200}
    content = json.loads(request.form.get("content"))
    if (content == None):
        dic = {"status": 400, "error": "Bad Request"}
        return str(json.dumps(dic))
    update = content["update"]
    if (update["status"] == "Failed"):
        dM.updateByDeviceId(update["device"])
        info = "Device:%s Package:%s Branch:%s Status:%s Failed" % (
            update["device"], update["package"]["package"], update["package"]["branch"], update["status"])
        logger.error(info)
        updateNext()
    elif (update["status"] == "Completed"):
        time.sleep(2)
        print(update["device"], dM.updateByDeviceId(update["device"]))
        info = "Device:%s Package:%s Branch:%s  Complete" % (
            update["device"], update["package"]["package"], update["package"]["branch"])
        logger.info(info)
        dM.updateStatus = update
        updateNext()
    else:
        info = "Device:%s Package:%s Branch:%s Status:%s" % (
            update["device"], update["package"]["package"], update["package"]["branch"], update["status"])
        logger.info(info)
        dM.updateStatus = update
    return str(json.dumps(dic))


@app.route("/update", methods=["POST", "GET"])
def update():
    # with open("config.json", "r") as f:
    #     config = json.loads(f.read())
    # ota_server = config["ota_server"]
    content = json.loads(request.form.get("content"))
    dic = {"status": 200}
    if (content == None):
        dic = {"status": 400, "error": "Bad Request"}
        return str(json.dumps(dic))
    else:
        isEmpty = len(dM.updateList) == 0
        updatelist: list = content["devices"]
        for item in updatelist:
            device_id = item["id"]
            packlist = item["packages"]
            for pack in packlist:
                dM.updateList.append(
                    {"id": device_id, "package": pack["package"], "branch": pack["branch"], "version": pack["version"]})
        if (isEmpty):
            updateNext()
        totallength = len(dM.updateList)
        return str(json.dumps(dic))


@app.route("/getLog", methods=["POST", "GET"])
def getLog():
    with open(os.path.join(log_path, logfile_name), "r") as f:
        logs = f.read()
    # 进行日志切割，直到上一个All Update Complete
    log_lines = logs.strip().split('\n')
    count = 0
    last_complete_index = None
    if ("All Update Complete" in log_lines[len(log_lines)-1]):
        line = 2
    else:
        line = 1
    for i in range(len(log_lines)-1, -1, -1):
        if "All Update Complete" in log_lines[i]:
            last_complete_index = i
            count += 1
            if (count == line):
                break
    if (count < line):
        last_complete_index = 0
    if last_complete_index is None:
        return []
    latest_logs = log_lines[last_complete_index:]

    return '\n'.join(latest_logs)


@app.route("/cancelUpdate", methods=["POST", "GET"])
def cancelUpdate():
    dM.updateList = []
    dic = {"status": 200}
    return str(json.dumps(dic))


@app.route("/updateNext", methods=["POST", "GET"])
def PupdateNext():
    dic = {"status": 200}
    updateNext()
    return str(json.dumps(dic))


if (__name__ == "__main__"):
    process = multiprocessing.Process(target=updateDevice)
    process.daemon = True
    process.start()
    app.run(host=flask_host, port=flask_port, debug=isDebug)
