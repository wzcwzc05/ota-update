from multiprocessing import Process, Queue
import os
import http_server
import update
import logging
import time

logger = logging.getLogger('daemonlogger')
log_name = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())+"-daemon.log" # 日志文件名
os.mkdir("log") if not os.path.exists("log") else None  # 创建log文件夹

logger.setLevel(logging.INFO)
file_log = logging.FileHandler(os.path.join("log", log_name))   # 文件输出
console_log = logging.StreamHandler()   # 控制台输出
file_log.setLevel(logging.INFO), console_log.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s') # 日志格式
file_log.setFormatter(formatter)
console_log.setFormatter(formatter)
logger.addHandler(file_log)
logger.addHandler(console_log)
update_queue = Queue()  # 用于进程间通信的队列

if (__name__ == "__main__"):
    logger.info("Daemon start...")
    try:
        server_process = Process(
            target=http_server.http_server, args=(update_queue,))   # 创建http server进程
        server_process.start()
        logger.info("http Server start...")
    except Exception as e:
        logger.error(e)
    try:
        update_process = Process(target=update.update,
                                 args=(update_queue,))    # update进程
        update_process.start()
        logger.info("update process start...")
    except Exception as e:
        logger.error(e)
    while (True):   # 监测进程是否存活
        if (not server_process.is_alive() and not update_process.is_alive()):
            logger.error("http server process and update process dead")
            exit(0)
        elif (not server_process.is_alive()):
            logger.error("http server process dead")
            update_process.terminate()
            exit(0)
        elif (not update_process.is_alive()):
            logger.error("update process dead")
            server_process.terminate()
            exit(0)
        time.sleep(1)
