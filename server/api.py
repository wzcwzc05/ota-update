from flask import Flask, request, send_from_directory
import json
import os
import versionManager as vM
import hashlib

config = {}
with open("config.json", "r") as f:
    config = json.loads(f.read())
flask_host = config["flask"]["host"]
flask_port = int(config["flask"]["port"])
isDebug = bool(config["flask"]["debug"])
storage_path = config["storage"]["path"]
app = Flask(__name__)
required_keys = ["sha256", "version", "branch", "package", "local",
                 "remote", "BeforeUpdate", "AfterUpdate", "dependencies", "restore"]


@app.route("/test")
def hello_world():
    dic = {"status": 200}
    return str(json.dumps(dic))


@app.route("/latestVersion")
def maxVersion() -> str:    # 获取最新版本
    dic = {"status": 200, "content.json": {}}
    package = request.args.get("package")
    branch = request.args.get("branch")
    if package is None or branch is None:   # 检查参数
        dic["status"] = 400
        return str(json.dumps(dic))
    content = vM.getMaxVersion(package, branch)
    if (content == None):
        dic["status"] = 404
        return str(json.dumps(dic))
    else:
        dic["content.json"] = content
        return str(json.dumps(dic))


@app.route("/getVersion")
def getVersion() -> str:    # 获取指定版本
    dic = {"status": 200}
    package = request.args.get("package")
    branch = request.args.get("branch")
    version = request.args.get("version")
    if package is None:  # 检查参数
        dic["status"] = 400
        return str(json.dumps(dic))
    content = vM.getCVersion(package, branch, version)
    if (content == None):   # 检查版本是否存在
        dic["status"] = 404
        return str(json.dumps(dic))
    else:
        dic["list"] = content
        return str(json.dumps(dic))


@app.route('/ota-files/<path:filename>')    # 通过路由参数来获取文件名
def ota_files(filename):
    dic = {"status": 200}
    safe_path = os.path.join(storage_path, filename)
    if not os.path.exists(safe_path):
        dic["status"] = 404
        return str(json.dumps(dic))
    return send_from_directory(storage_path, filename)  # 返回文件


@app.route('/upload', methods=['PUT'])
def upload_file():  # 上传文件
    dic = {"status": 200}
    isForce = request.args.get("overwrite") == "1"  # 是否强制更新
    if 'file' not in request.files or 'content' not in request.form:        # 检查是否有文件和JSON数据
        dic["status"] = 400
        dic["error"] = "No file or content"
        return str(json.dumps(dic))

    file = request.files["file"]
    content = request.form['content']
    content_data = {}
    try:
        content_data = json.loads(content)
        if (vM.checkContent(content_data) == False):    # 检查content.json是否合法
            dic["status"] = 400
            dic["error"] = "Json Content Error"
            return str(json.dumps(dic))
        expected_sha256 = content_data['sha256']
    except json.JSONDecodeError:
        dic["status"] = 400
        dic["error"] = "JSONDecodeError"
        return str(json.dumps(dic))

    name = content_data["package"]
    branch = content_data["branch"]
    version = content_data["version"]
    file_name = name+"-"+branch+"-"+version+".zip"
    file_path = os.path.join(storage_path, name, branch, file_name)
    file_content = file.read()
    sha256_hash = hashlib.sha256(file_content).hexdigest()

    if os.path.exists(file_path) and not isForce:   # 检查文件是否存在
        dic["status"] = 409
        dic["error"] = "File exists"
        dic["TIP"] = "If you want to force update, please add a query parameter 'overwrite=1' to the URL"
        return str(json.dumps(dic))
    if vM.checkVersion(name, branch, version) == True and not isForce:  # 检查版本是否存在
        dic["status"] = 409
        dic["error"] = "Version exists"
        dic["TIP"] = "If you want to force update, please add a query parameter 'overwrite=1' to the URL"
        return str(json.dumps(dic))

    if sha256_hash != expected_sha256:  # 检查文件SHA256
        dic["status"] = 400
        dic["error"] = "SHA256 Error"
        return str(json.dumps(dic))
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(file_content)
    except:
        dic["status"] = 500
        dic["error"] = "Write file Error"
        return str(json.dumps(dic))

    try:
        print(content_data)
        if vM.writeinVersion(content_data) == False:    # 写入数据库
            dic["status"] = 409
            dic["error"] = "Write database Error"   # 写入数据库失败
            # 删除文件
            os.remove(file_path)
            return str(json.dumps(dic))
    except:
        dic["status"] = 500
        dic["error"] = "Write database Error"
        # 删除文件
        os.remove(file_path)
        return str(json.dumps(dic))

    return str(json.dumps(dic))


if (__name__ == "__main__"):
    app.run(host=flask_host, port=flask_port, debug=isDebug)
