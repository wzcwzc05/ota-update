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
