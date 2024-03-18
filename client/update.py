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
        print("update process start...")
        if (not update_queue.empty()):
            package = update_queue.get()
            try:
                package.startUpdate()
            except Exception as e:
                logger.INFO(name+" update error")
        time.sleep(1)
