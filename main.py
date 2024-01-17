from flask import Flask, request
import pymysql
import configparser
import json
import os

config = configparser.ConfigParser()
config.read('./config.conf')
db_host = config.get('database', 'host')
db_user = config.get('database', 'user')
db_password = config.get('database', 'password')
db_database = config.get('database', 'database')
db_port = config.getint('database', 'port')
flask_host = config.get('flask', 'host')
flask_port = int(config.getint('flask', 'port'))
storage_path = config.get('storage', 'path')
app = Flask(__name__)


def getAllVersion(package: str, branch: str) -> list:  # 获取所有版本
    db = pymysql.connect(host=db_host,
                         user=db_user,
                         password=db_password,
                         database=db_database,
                         port=db_port)
    cursor = db.cursor()
    cursor.execute("SELECT version FROM otafiles WHERE package='%s' AND branch = '%s' ORDER BY version DESC" % (
        package, branch))
    results = cursor.fetchall()
    db.close()
    ans = []
    for i in range(len(results)):
        ans.append(results[i][0])
    return ans


@app.route("/test")
def hello_world():
    return "OK"


@app.route("/maxVersion")
def maxVersion():
    package = request.args.get("package")
    branch = request.args.get("branch")
    if package is None or branch is None:
        return "Error"
    allversion = getAllVersion(package, branch)
    if (allversion == []):
        return "Error"
    return str(allversion[0])


@app.route("/getVersion")
def getVersion():
    package = request.args.get("package")
    branch = request.args.get("branch")
    version = request.args.get("version")
    if package is None or branch is None or version is None:
        return "Error"
    db = pymysql.connect(host=db_host,
                         user=db_user,
                         password=db_password,
                         database=db_database,
                         port=db_port)
    cursor = db.cursor()
    cursor.execute("SELECT content FROM otafiles WHERE package='%s' AND branch = '%s' AND version = '%s'" % (
        package, branch, version))
    results = cursor.fetchall()
    db.close()
    if (len(results) == 0):
        return "Error"
    return json.dumps(results[0])


@app.route("/ota-file/<path_s>")
def ota_file(path_s):
    f = open(os.path.join(storage_path,path_s), "rb")
    return f.read()


@app.route("/lib/jquery.min.js")
def jqueryjs():
    f = open("lib/jquery.min.js", "r", encoding="utf-8")
    return f.read()


@app.route("/lib/main.js")
def mainjs():
    f = open("lib/main.js", "r", encoding="utf-8")
    return f.read()


if (__name__ == "__main__"):
    app.run(host=flask_host, port=flask_port, debug=True)
