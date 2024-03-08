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


def getPackages(content: dict) -> list:
    packages = [()]

    return packages


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

