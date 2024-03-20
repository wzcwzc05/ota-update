from multiprocessing import Process, Queue
from update_package import update_package
import time
import os
import sys
import logging
import json
import signal


def signal_handler(sig, frame):
    sys.exit(0)


def update(update_queue):
    signal.signal(signal.SIGTERM, signal_handler)

    logger = logging.getLogger('updatelogger')
    log_name = time.strftime(
        "%Y-%m-%d-%H-%M-%S", time.localtime())+"-update.log"
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

    while (True):
        if (not update_queue.empty()):  # 如果队列不为空
            package: update_package = update_queue.get()    # 从队列中获取一个更新包
            try:
                with open("device.json") as f:
                    device = json.loads(f.read())
                packlist = device["packages"]
                for item in packlist:
                    if (item["package"] == package.package_json["package"] and item["branch"] == package.package_json["branch"]):
                        logger.info(
                            package.package_json["package"]+" in device.json")  # 如果设备中有这个包
                        break
                else:
                    logger.info(
                        package.package_json["package"]+" not in device.json")  # 如果设备中没有这个包
                logger.info(package.package_json["package"]+" update start")
                if (not package.startUpdate()):
                    logger.info(
                        package.package_json["package"]+" update failed")
                    continue
                logger.info(package.package_json["package"]+" update finished")
                for i, item in enumerate(packlist):
                    if (item["package"] == package.package_json["package"] and item["branch"] == package.package_json["branch"]):
                        packlist[i] = package.package_json  # 更新device.json中的包信息
                        break
                else:
                    packlist.append(package.package_json)
                device["packages"] = packlist
                with open("device.json", "w") as f:
                    f.write(json.dumps(device))
            except BaseException as e:
                logger.info(package.package_json["package"]+" update error")    # 更新失败
        time.sleep(1)
