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


def checkUserAndPasswd(user: str, passwd: str) -> bool:
    conn = pymysql.connect(host=db_host, user=db_user,
                           password=db_password, database=db_database, port=db_port)
    cursor = conn.cursor()
    sql = "select * from users where username=%s and password=%s"
    cursor.execute(sql, (user, passwd))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return len(result) > 0


def api_getPackageList():
    conn = pymysql.connect(host=db_host, user=db_user,
                           password=db_password, database=db_database, port=db_port)
    cursor = conn.cursor()
    sql = "select name,version,branch from ota"
    cursor.execute(sql)
    result = cursor.fetchall()
    json_result = {}
    for package in result:
        if package[0] not in json_result:
            json_result[package[0]] = {}
        if package[2] not in json_result[package[0]]:
            json_result[package[0]][package[2]] = []
        json_result[package[0]][package[2]].append(package[1])
    last_result = []
    total_id = 0
    for package in json_result:
        current_package = {
            "name": package,
            "branches": []
        }
        for branch in json_result[package]:
            current_package["branches"].append({
                "name": branch,
                "packages": []
            })
            for version in json_result[package][branch]:
                total_id += 1
                current_version = {
                    "id": total_id,
                    "name": package,
                    "branch": branch,
                    "version": version,
                    "contentJson": ""
                }
                current_package["branches"][-1]["packages"].append(
                    current_version)
        last_result.append(current_package)

    cursor.close()
    conn.close()
    return last_result


def api_getDevices():
    conn = pymysql.connect(host=db_host, user=db_user,
                           password=db_password, database=db_database, port=db_port)
    cursor = conn.cursor()
    sql = "select id,device,content from devices"
    result = cursor.execute(sql)
    result = cursor.fetchall()
    for device in result:
        pass
    return []

if __name__ == "__main__":
    print(json.dumps(api_getPackageList()))
