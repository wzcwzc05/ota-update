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
                print("Failed to get content.json from " +
                      device + " at " + address)
        except Exception as e:
            print("Failed to get version from " + device + " at " + address)

        try:
            response = requests.get(urljoin(address, "/getStatus"))
            data = json.loads(response.text)
            if (data["status"] == 200):
                cursor.execute("UPDATE devices SET status='%s' WHERE address='%s'" % (
                    data["status"], address))
                db.commit()
            else:
                print("Failed to get status from " + device + " at " + address)
        except Exception as e:
            print("Failed to get status from " + device + " at " + address)
    db.close()


def updateToDevice(id, packages: list, address: str) -> None:
    db = pymysql.connect(host=db_host,
                         user=db_user,
                         password=db_password,
                         database=db_database,
                         port=db_port)
    cursor = db.cursor()
    post_url = urljoin(address, "/update")
    data = {
        "packages": packages
    }
    try:
        response = requests.post(post_url, data)
        data = json.loads(response.text)
        if (data["status"] == 200):
            cursor.execute("UPDATE devices SET status='%s' WHERE id='%s'" % (
                data["status"], id))
            db.commit()
        else:
            print("Failed to update " + id + " at " + address)
    except Exception as e:
        print("Failed to update " + id + " at " + address)
    db.close()


def registerDevice(content: str, address: str) -> str:
    db = pymysql.connect(host=db_host,
                         user=db_user,
                         password=db_password,
                         database=db_database,
                         port=db_port)
    device_name = content["device"]
    port = str(content["flask"]["port"])
    device_url = "http://"+address+":"+port
    cursor = db.cursor()
    cursor.execute("SELECT id FROM devices WHERE address='%s'" % device_url)
    results = cursor.fetchall()
    if (len(results) == 0):
        cursor.execute(
            "INSERT INTO devices (device, address, content) VALUES ('%s', '%s', '%s')" % (device_name, device_url, json.dumps(content)))
        device_id = db.insert_id()
        db.commit()
        db.close()
        return device_id
    else:
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


def heartBeatDevice(id: str) -> bool:
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
        cursor.execute(
            "UPDATE devices SET lastupdate=NOW() WHERE id='%s'" % id)
        db.commit()
        db.close()
        return True


if __name__ == "__main__":
    pass
