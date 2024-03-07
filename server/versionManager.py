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


def getCVersion(package: str, branch=None, version=None) -> list:
    # 建立数据库连接
    db = pymysql.connect(host=db_host,
                         user=db_user,
                         password=db_password,
                         database=db_database,
                         port=db_port)
    try:
        cursor = db.cursor(pymysql.cursors.DictCursor)
        # 基础查询语句
        sql = "SELECT name, branch, version, content FROM ota WHERE name=%s"
        params = [package]  # 查询参数列表

        if branch:
            sql += " AND branch=%s"
            params.append(branch)
        if version:
            sql += " AND version=%s"
            params.append(version)

        cursor.execute(sql, params)
        results = cursor.fetchall()
        return results
    finally:
        db.close()


def writeinVersion(content: dict) -> bool:  # 写入版本信息
    db = pymysql.connect(host=db_host,
                         user=db_user,
                         password=db_password,
                         database=db_database,
                         port=db_port)
    cursor = db.cursor()
    sql = ""
    if (checkVersion(content["package"], content["branch"], content["version"])):
        sql = "UPDATE ota SET content='%s' WHERE name='%s' AND branch='%s' AND version='%s'" % (
            json.dumps(content), content["package"], content["branch"], content["version"])
    else:
        sql = "INSERT INTO ota (name, version, branch, content) VALUES ('%s', '%s', '%s', '%s')" % (
            content["package"], content["version"], content["branch"], json.dumps(content))
    cursor.execute(sql)
    db.commit()
    db.close()
    return True


def checkContent(content: dict) -> bool:
    required_keys = ["sha256", "version", "branch", "package", "local",
                     "remote", "BeforeUpdate", "AfterUpdate", "dependencies", "restore"]
    for i in required_keys:
        if i not in content:
            return False
    return True


def checkVersion(package: str, branch: str, version: str) -> bool:
    db = pymysql.connect(host=db_host,
                         user=db_user,
                         password=db_password,
                         database=db_database,
                         port=db_port)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM ota WHERE name='%s' AND branch = '%s' AND version = '%s'" % (
        package, branch, version))
    results = cursor.fetchall()
    if (len(results) == 0):
        db.close()
        return False
    db.close()
    return True