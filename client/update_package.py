import logging
import os
import subprocess
import requests
import zipfile
from urllib.parse import urljoin
import json
import hashlib
logger = logging.getLogger("update_package")
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
os.mkdir("log") if not os.path.exists("log") else None
file_handler = logging.FileHandler("log/update.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class update_package:
    def __init__(self, package_json: dict, register_path: str, device_id: int, log_handler=None):
        if (log_handler == None):   # 如果没有传入log_handler则使用默认的log_handler
            self.log_handler = logger
        else:
            self.log_handler = log_handler
        os.mkdir("tmp") if not os.path.exists("tmp") else None  # 创建tmp文件夹
        os.mkdir("log") if not os.path.exists("log") else None # 创建log文件夹
        self.package_json = package_json
        self.device_id = device_id
        self.package_name = "%s-%s-%s.zip" % (
            package_json["package"], package_json["branch"], package_json["version"])   # 下载的安装包文件名
        self.local_path = package_json["local"] # 安装包解压路径
        temp = "ota-files/%s/%s/%s" % (
            package_json["package"], package_json["branch"], self.package_name)

        self.remote_path = urljoin( # 安装包下载地址
            package_json["remote"], temp)
        temp = "/updateInfo"
        self.register_path = urljoin(register_path, temp)   # 上报更新状态地址
        self.BeforeUpdate = package_json["BeforeUpdate"]
        self.AfterUpdate = package_json["AfterUpdate"]
        self.restore = package_json["restore"]
        self.file_path = os.path.join(  # 安装包文件路径
            "tmp/", self.package_name)

    def startUpdate(self):
        self.log_handler.info(self.package_json["package"]+" start update...")
        self.log_handler.info(
            self.package_json["package"]+" execute BeforeUpdate...")
        try:
            self.report("BeforeUpdate")
            self.ExeBeforeUpdate()  # 执行BeforeUpdate
        except Exception as e:
            self.log_handler.error(e)
            self.report("Failed")
            return False

        self.log_handler.info(
            self.package_json["package"]+" download package...")
        try:
            self.report("Downloading")
            self.download() # 下载安装包
        except Exception as e:
            self.log_handler.error(e)
            self.report("Failed")
            return False

        self.log_handler.info(
            self.package_json["package"]+" update package...")
        try:
            self.report("Updating")
            self.update()   # 更新安装包
        except Exception as e:
            self.log_handler.error(e)
            self.report("Failed")
            return False

        self.log_handler.info(
            self.package_json["package"] + " execute AfterUpdate...")
        try:
            self.report("AfterUpdate")
            self.ExeAfterUpdate()   # 执行AfterUpdate
        except Exception as e:
            self.log_handler.error(e)
            self.report("Failed")
            return False

        self.log_handler.info(self.package_json["package"]+" restore...")
        try:
            self.report("Restore")
            self.Exerestore()   # 执行restore
        except Exception as e:
            self.log_handler.error(e)
            self.report("Failed")
            return False

        self.log_handler.info(self.package_json["package"]+" update finish...")
        self.report("Completed")    # 更新完成
        return True

    def download(self):
        sha256_o = self.package_json["sha256"]  # 期望的sha256
        with requests.get(self.remote_path, stream=True) as r:  # 下载安装包
            r.raise_for_status()
            with open(self.file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        sha256_n = hashlib.sha256() # 计算下载文件的sha256
        with open(self.file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_n.update(byte_block)
        if sha256_o != sha256_n.hexdigest():
            self.log_handler.error("sha256 not match")
            raise Exception("sha256 not match")

    def ExeBeforeUpdate(self):  # 执行BeforeUpdate
        if self.BeforeUpdate == "":
            return
        complete = subprocess.run(
            self.BeforeUpdate, text=True, capture_output=True, shell=True)
        if complete.returncode != 0:
            self.log_handler.error(complete.stderr)
            raise Exception(complete.stderr)
        else:
            self.log_handler.info(complete.stdout)

    def ExeAfterUpdate(self):   # 执行AfterUpdate
        if self.AfterUpdate == "":
            return
        complete = subprocess.run(
            self.AfterUpdate, text=True, capture_output=True, shell=True)
        if complete.returncode != 0:
            self.log_handler.error(complete.stderr)
            raise Exception(complete.stderr)
        else:
            self.log_handler.info(complete.stdout)

    def Exerestore(self):   # 执行restore
        if self.restore == "":
            return
        complete = subprocess.run(
            self.restore, text=True, capture_output=True, shell=True)
        if complete.returncode != 0:
            self.log_handler.error(complete.stderr)
            raise Exception(complete.stderr)
        else:
            self.log_handler.info(complete.stdout)

    def update(self):
        zipfile.ZipFile(self.file_path).extractall(self.local_path) # 解压安装包

    def report(self, status: str):  # 上报更新状态
        res = {
            "update": {
                "device": self.device_id,
                "package": {
                    "package": self.package_json["package"],
                    "version": self.package_json["version"],
                    "branch": self.package_json["branch"]
                },
                "status": status
            }
        }

        requests.post(self.register_path, data={
                      "content": str(json.dumps(res))})


if __name__ == "__main__":
    dic = {
        "local": "./test",
        "branch": "test",
        "remote": "http://127.0.0.1:5500",
        "sha256": "bca638ef441682e69eda19adeee00cd354b1384764529d19590d65d3a29e05b4",
        "package": "test",
        "restore": "",
        "version": "0.0.1",
        "AfterUpdate": "",
        "description": "",
        "BeforeUpdate": "",
        "dependencies": {}
    }

    upackage = update_package(dic, "http://localhost:6500/", 1, logger)
    upackage.startUpdate()
