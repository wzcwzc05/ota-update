import pymysql
import json
import requests
from urllib.parse import urljoin, urlencode
config = {}
with open("config.json", "r") as f:
    config = json.loads(f.read())
db_host = config["database"]["host"]
db_user = config["database"]['user']
db_password = config["database"]["password"]
db_database = config["database"]["database"]
db_port = int(config["database"]["port"])
global updateStatus
global updateList
updateStatus = {"device": 0, "package": {"package": "0",
                                         "version": "0", "branch": "0"}, "status": "complete"}
updateList = []


def getPackages(content: dict) -> list:
    packages = []
    try:
        for item in content["packages"]:
            temp = {}
            temp["package"] = item["package"]
            temp["version"] = item["version"]
            temp["branch"] = item["branch"]
            packages.append(temp)
        return packages
    except Exception as e:
        print(e)
        return None


def deleteExpiredDevices():
    db = pymysql.connect(host=db_host,
                         user=db_user,
                         password=db_password,
                         database=db_database,
                         port=db_port)
    cursor = db.cursor()
    cursor.execute(
        "DELETE FROM devices WHERE lastupdate < DATE_SUB(NOW(), INTERVAL 2 MINUTE)")  # 1 minute
    db.commit()
    db.close()


def getAllDevicesId():
    try:
        db = pymysql.connect(host=db_host,
                             user=db_user,
                             password=db_password,
                             database=db_database,
                             port=db_port)
        cursor = db.cursor()
        cursor.execute("SELECT id FROM devices")
        results = cursor.fetchall()
        lst = []
        for row in results:
            lst.append(row[0])
        db.close()
        return lst
    except Exception as e:
        print(e)
        return None


def getDeviceById(id: int) -> list:
    try:
        db = pymysql.connect(host=db_host,
                             user=db_user,
                             password=db_password,
                             database=db_database,
                             port=db_port)
        cursor = db.cursor()
        cursor.execute("SELECT content FROM devices WHERE id='%s'" % id)
        results = cursor.fetchall()
        if (len(results) == 0):
            db.close()
            return None
        else:
            db.close()
            return getPackages(json.loads(results[0][0]))
    except Exception as e:
        print(e)
        return None


def updateFromDevice():
    db = pymysql.connect(host=db_host,
                         user=db_user,
                         password=db_password,
                         database=db_database,
                         port=db_port)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM devices")
    results = cursor.fetchall()
    for row in results:
        device = row[1]
        address = row[2]
        post_url = urljoin(address, "/getInfo")
        try:
            response = requests.get(post_url)
            data = json.loads(response.text)
            if (data["status"] == 200):
                cursor.execute("UPDATE devices SET content='%s' WHERE address='%s'" % (
                    data["content"], address))
                db.commit()
            else:
                deleteExpiredDevices()
                print("Failed to get content.json from " +
                      device + " at " + address)
        except Exception as e:
            deleteExpiredDevices()
            print("Failed to get version from " + device + " at " + address)

    db.close()


def updateToDevice(id, packages: dict, address: str) -> None:
    post_url = urljoin(address, "/startUpdate")
    data = {
        "content": str(json.dumps(packages))
    }
    try:
        response = requests.post(post_url, data)
        data = json.loads(response.text)
        if (data["status"] == 200):
            return True
        else:
            return False
    except Exception as e:
        return False


def registerDevice(content: str, address: str) -> str:
    db = pymysql.connect(host=db_host,
                         user=db_user,
                         password=db_password,
                         database=db_database,
                         port=db_port)
    device_name = content["device"]
    cursor = db.cursor()
    cursor.execute("SELECT id FROM devices WHERE address='%s'" % address)
    results = cursor.fetchall()
    if (len(results) == 0):
        cursor.execute(
            "INSERT INTO devices (device, address, content) VALUES ('%s', '%s', '%s')" % (device_name, address, json.dumps(content)))
        device_id = db.insert_id()
        db.commit()
        db.close()
        return device_id
    else:
        cursor.execute("UPDATE devices SET content='%s' WHERE address='%s'" % (
            json.dumps(content), address))
        db.close()
        return results[0][0]


def logoutDevice(id: str) -> bool:
    db = pymysql.connect(host=db_host,
                         user=db_user,
                         password=db_password,
                         database=db_database,
                         port=db_port)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM devices WHERE id='%s'" % id)
    results = cursor.fetchall()
    if (len(results) == 0):
        db.close()
        return False
    else:
        cursor.execute("DELETE FROM devices WHERE id='%s'" % id)
        db.commit()
        db.close()
        return True


def heartBeatDevice(device_id: str) -> bool:
    db = pymysql.connect(host=db_host,
                         user=db_user,
                         password=db_password,
                         database=db_database,
                         port=db_port)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM devices WHERE id='%s'" % device_id)
    results = cursor.fetchall()
    if (len(results) == 0):
        db.close()
        return False
    else:
        cursor.execute(
            "UPDATE devices SET lastupdate=NOW() WHERE id='%s'" % device_id)
        db.commit()
        db.close()
        return True


def getAddress(id: int) -> str:
    db = pymysql.connect(host=db_host,
                         user=db_user,
                         password=db_password,
                         database=db_database,
                         port=db_port)
    cursor = db.cursor()
    cursor.execute("SELECT address FROM devices WHERE id='%s'" % id)
    results = cursor.fetchall()
    if (len(results) == 0):
        db.close()
        return None
    else:
        db.close()
        return results[0][0]


def getPackage(package: str, branch: str, version: str) -> dict:
    with open("config.json", "r") as f:
        config = json.loads(f.read())
    ota_server = config["ota_server"]
    dic: dict = requests.get(urljoin(ota_server, "/getVersion?"+urlencode(
        {"package": package, "branch": branch, "version": version}))).json()
    if (dic["status"] == 200):
        package_json = dic["list"][0]["content"]
    else:
        package_json = None
    return package_json


def update(updatePackage: dict) -> dict:
    id = updatePackage["id"]
    package = updatePackage["package"]
    branch = updatePackage["branch"]
    version = updatePackage["version"]
    address = getAddress(id)
    package_json = getPackage(package, branch, version)
    if (address == None):
        return False
    else:
        if (updateToDevice(id, package_json, address)):
            return True
        else:
            return False


if __name__ == "__main__":
    updateFromDevice()
