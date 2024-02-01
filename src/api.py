from flask import Flask, request
import pymysql
import configparser
import json
import os

config = configparser.ConfigParser()
config.read('./config.conf')
db_host: str = config.get('database', 'host')
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
    dic = {"status": 200}
    return str(json.dumps(dic))


@app.route("/maxVersion")
def maxVersion():
    dic = {"status": 200}
    package = request.args.get("package")
    branch = request.args.get("branch")
    if package is None or branch is None:
        dic["status"] = 400
        return str(json.dumps(dic))
    allversion = getAllVersion(package, branch)
    if (allversion == []):
        dic["status"] = 404
        return str(json.dumps(dic))
    else:
        dic["version"] = allversion[0]
        return str(json.dumps(dic))


@app.route("/getVersion")
def getVersion() -> str:
    dic = {"status": 200}
    package = request.args.get("package")
    branch = request.args.get("branch")
    version = request.args.get("version")
    if package is None or branch is None or version is None:
        dic["status"] = 400
        return str(json.dumps(dic))
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
        dic["status"] = 404
        return str(json.dumps(dic))
    else:
        dic["content"] = json.loads(results[0][0])
        return str(json.dumps(dic))


@app.route("/currentVersion")
def currentVersion() -> str:
    dic = {"status": 200}
    package = request.args.get("package")
    branch = request.args.get("branch")
    if package is None or branch is None:
        dic["status"] = 400
        return str(json.dumps(dic))
    db = pymysql.connect(host=db_host,
                         user=db_user,
                         password=db_password,
                         database=db_database,
                         port=db_port)
    cursor = db.cursor()
    cursor.execute("SELECT version FROM otafiles WHERE package='%s' AND branch = '%s' AND tag = '1'" % (
        package, branch))
    results = cursor.fetchall()
    db.close()
    if (len(results) == 0):
        dic["status"] = 404
        return str(json.dumps(dic))
    else:
        dic["version"] = results[0][0]
        return str(json.dumps(dic))

@app.route("/updateVersion")
def updateVersion() -> str:
    dic = {"status": 200}
    package = request.args.get("package")
    branch = request.args.get("branch")
    version = request.args.get("version")
    if package is None or branch is None or version is None:
        dic["status"] = 400
        return str(json.dumps(dic))
    db = pymysql.connect(host=db_host,
                         user=db_user,
                         password=db_password,
                         database=db_database,
                         port=db_port)
    cursor = db.cursor()
    cursor.execute("UPDATE otafiles SET tag = '0' WHERE package='%s' AND branch = '%s' AND tag='1'" % (
        package, branch))
    cursor.execute("UPDATE otafiles SET tag = '1' WHERE package='%s' AND branch = '%s' AND version = '%s'" % (
        package, branch, version))
    db.commit()
    db.close()
    return str(json.dumps(dic))

@app.route("/ota-file/<path_s>")
def ota_file(path_s) -> bytes:
    f = open(os.path.join(storage_path, path_s), "rb")
    return f.read()


if (__name__ == "__main__"):
    app.run(host=flask_host, port=flask_port, debug=True)

# 576081444
