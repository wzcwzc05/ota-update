import logging
import os
import subprocess


class update_package:
    def __init__(self, name, package_path, file_name, BeforeUpdate="", AfterUpdate="", restore="", log_handler=None):
        self.package_name = name
        self.package_path = package_path
        self.file_path = file_name
        self.BeforeUpdate = BeforeUpdate
        self.AfterUpdate = AfterUpdate
        self.restore = restore
        self.log_handler = log_handler

    def startUpdate(self):
        self.log_handler.info(self.package_name+"start update...")
        self.log_handler.info(self.package_name+"execute BeforeUpdate...")
        self.ExeBeforeUpdate()
        self.log_handler.info(self.package_name+"download package...")
        tmp_package = self.download(self.package_path)
        self.log_handler.info(self.package_name+"update package...")
        self.update(tmp_package, self.file_path)
        self.log_handler.info(self.package_name+"execute AfterUpdate...")
        self.ExeAfterUpdate()
        self.log_handler.info(self.package_name+"restore...")
        self.Exerestore()
        self.log_handler.info(self.package_name+"update finish...")

    def download(self, package_path):
        pass

    def ExeBeforeUpdate(self):
        if self.BeforeUpdate == "":
            return
        complete = subprocess.run(
            self.BeforeUpdate, text=True, capture_output=True)
        if complete.returncode != 0:
            self.log_handler.error(complete.stderr)
            raise Exception(complete.stderr)
        else:
            self.log_handler.info(complete.stdout)

    def ExeAfterUpdate(self):
        if self.AfterUpdate == "":
            return
        complete = subprocess.run(
            self.AfterUpdate, text=True, capture_output=True)
        if complete.returncode != 0:
            self.log_handler.error(complete.stderr)
            raise Exception(complete.stderr)
        else:
            self.log_handler.info(complete.stdout)

    def Exerestore(self):
        if self.restore == "":
            return
        complete = subprocess.run(
            self.restore, text=True, capture_output=True)
        if complete.returncode != 0:
            self.log_handler.error(complete.stderr)
            raise Exception(complete.stderr)
        else:
            self.log_handler.info(complete.stdout)

    def update(self, tmp_package, file_path):
        pass
