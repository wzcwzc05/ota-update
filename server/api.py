from flask import Flask, request
import json
import os
import versionManager as vM
import hashlib

config = {}
with open("config.json", "r") as f:
    config = json.loads(f.read())
flask_host = config["flask"]["host"]
flask_port = int(config["flask"]["port"])
storage_path = config["storage"]["path"]
app = Flask(__name__)
required_keys = ["sha256", "version", "branch", "package", "local",
                 "remote", "BeforeUpdate", "AfterUpdate", "dependencies", "restore"]


def check_content(content: dict) -> bool:
    for i in required_keys:
        if i not in content:
            return False
    return True


@app.route("/test")
def hello_world():
    dic = {"status": 200}
    return str(json.dumps(dic))


@app.route("/maxVersion")
def maxVersion() -> str:
    dic = {"status": 200, "content.json": {}}
    package = request.args.get("package")
    branch = request.args.get("branch")
    if package is None or branch is None:
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
def getVersion() -> str:
    dic = {"status": 200}
    package = request.args.get("package")
    branch = request.args.get("branch")
    version = request.args.get("version")
    if package is None or branch is None or version is None:
        dic["status"] = 400
        return str(json.dumps(dic))
    content = vM.getCVersion(package, branch, version)
    if (content == None):
        dic["status"] = 404
        return str(json.dumps(dic))
    else:
        dic["content.json"] = content
        return str(json.dumps(dic))


@app.route("/ota-file/<path_s>")
def ota_file(path_s) -> bytes:
    if not os.path.exists(os.path.join(storage_path, path_s)):
        return str(404)
    f = open(os.path.join(storage_path, path_s), "rb")
    return f.read()


@app.route('/update', methods=['PUT'])
def update_file():
    dic = {"status": 200}
    # 检查是否有文件和JSON数据
    print(request.form)
    print(request.files)
    if 'file' not in request.files or 'content' not in request.form:
        dic["status"] = 400
        dic["error"] = "No file or content"
        return str(json.dumps(dic))

    file = request.files["file"]
    content = request.form['content']

    try:
        content_data = json.loads(content)
        if (check_content(content_data) == False):
            dic["status"] = 400
            dic["error"] = "Json Content Error"
            return str(json.dumps(dic))
        expected_sha256 = content_data.get('sha256')
    except json.JSONDecodeError:
        dic["status"] = 400
        dic["error"] = "JSONDecodeError"
        return str(json.dumps(dic))

    file_content = file.read()
    sha256_hash = hashlib.sha256(file_content).hexdigest()

    if sha256_hash != expected_sha256:
        dic["status"] = 400
        dic["error"] = "SHA256 Error"
        return str(json.dumps(dic))
    try:
        with open(os.path.join(storage_path, sha256_hash), "wb") as f:
            f.write(file_content)
    except:
        dic["status"] = 500
        dic["error"] = "Write file Error"
        return str(json.dumps(dic))
        
    try:
        if vM.writeinVersion(content_data) == False:
            dic["status"] = 409
            dic["error"] = "Write database Error"
            return str(json.dumps(dic))
    except:
        dic["status"] = 500
        dic["error"] = "Write database Error"
        return str(json.dumps(dic))
    
    return str(json.dumps(dic))


if (__name__ == "__main__"):
    app.run(host=flask_host, port=flask_port, debug=True)
