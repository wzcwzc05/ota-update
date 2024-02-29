import pymysql
import json

config = {}
with open("config.json", "r") as f:
    config = json.loads(f.read())
db_host = config["database"]["host"]
db_user = config["database"]['user']
db_password = config["database"]["password"]
db_database = config["database"]["database"]
db_port = int(config["database"]["port"])


def getMaxVersion(package: str, branch: str) -> dict:   # 获取最新版本的信息
    db = pymysql.connect(host=db_host,
                         user=db_user,
                         password=db_password,
                         database=db_database,
                         port=db_port)
    cursor = db.cursor()
    cursor.execute("SELECT content FROM ota WHERE name='%s' AND branch = '%s' ORDER BY version DESC" % (
        package, branch))
    results = cursor.fetchall()
    db.close()
    if (len(results) == 0):
        return None
    else:
        return results[0][0]


def getCVersion(package: str, branch: str, version: str) -> dict:   # 获取特定版本的信息
    db = pymysql.connect(host=db_host,
                         user=db_user,
                         password=db_password,
                         database=db_database,
                         port=db_port)
    cursor = db.cursor()
    cursor.execute("SELECT content FROM ota WHERE name='%s' AND branch = '%s' AND version = '%s'" % (
        package, branch, version))
    results = cursor.fetchall()
    db.close()
    if (len(results) == 0):
        return None
    else:
        return results[0][0]


def writeinVersion(content: dict) -> bool:  # 写入版本信息
    db = pymysql.connect(host=db_host,
                         user=db_user,
                         password=db_password,
                         database=db_database,
                         port=db_port)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM ota WHERE name='%s' AND branch = '%s' AND version = '%s'" % (
        content["package"], content["branch"], content["version"]))
    results = cursor.fetchall()
    if (len(results) != 0):
        db.close()
        return False
    cursor.execute("INSERT INTO ota (name, version, branch, content) VALUES ('%s', '%s', '%s', '%s')" % (
        content["package"], content["version"], content["branch"], json.dumps(content)))
    db.commit()
    db.close()
    return True
