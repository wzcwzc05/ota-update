import tarfile
import os
import sys
import json
import hashlib

def isProperPack(path: str) -> bool:
    AllFiles = []
    for file in os.listdir(path):
        AllFiles.append(file)
    for file in AllFiles:
        if file == "data.json":
            print("[INFO] Find Package Json in "+os.path.join(path, file))
            # 读取data.json
            with open(os.path.join(path, file), "r") as f:
                data = f.read()
            if data == "":
                return False
            else:
                dic = json.loads(data)
                if ("name" in dic.keys()) and ("updateURL" in dic.keys()) and ("version" in dic.keys()) and ("branch" in dic.keys()):
                    if (dic["name"] in AllFiles):
                        return True
                    else:
                        return False
                else:
                    return False
    return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 pack.py <path>")
        print("with only <path> arg will pack")
        print("--config auto: According to git information, generate data.json")
        exit(1)
    path = sys.argv[1]
    if not os.path.exists(path):
        print("Path does not exist")
        exit(1)
    if not os.path.isdir(path):
        print("Path is not a directory")
        exit(1)
    if (not isProperPack(path)):
        print("Path is not a proper pack")
        exit(1)
    # 将文件夹打包
    print("Packing...")
    if (len(sys.argv) == 4 and sys.argv[2] == "--config" and sys.argv[3] == "auto"):
        try:
            version, branch = os.popen(
                "cd %s && git describe --tags" % (path)).read().split("-")
        except:
            print(
                "[Error] Failed to get git information, please check if the git repository is initialized")
            exit(1)
        if (version == "" or branch == ""):
            print(
                "[Error] Failed to get git information, please check if the git repository is initialized")
            exit(1)
        with open(os.path.join(path, "data.json"), "w") as f:
            f.write(json.dumps({
                "name": os.path.basename(path),
                "updateURL": "",
                "version": version,
                "branch": branch
            }))
        exit(0)
    else:
        with open(os.path.join(path, "data.json"), "r") as f:
            data = f.read()
        dic = json.loads(data)
        version = dic["version"]
        branch = dic["branch"]
        tar = tarfile.open(path+"-"+version+"-"+branch+".tar.gz", "w:gz")
        tar.add(path, arcname=os.path.basename(path))
        tar.close()
    # 计算SHA256
    print("Calculating SHA256...")
    with open(path+"-"+version+"-"+branch+".tar.gz", "rb") as f:
        data = f.read()
    print(hashlib.sha256(data).hexdigest())
    
    print("Done")
