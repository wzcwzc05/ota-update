import requests
import json
import os
import zipfile
from urllib.parse import urljoin, urlencode


def testUrl(url: str) -> bool:
    post_url = urljoin(url, "/test")
    try:
        response = requests.get(post_url)
        data = json.loads(response.text)
        if (data["status"] == 200):
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


def getLatestVersion(url: str, package: str, branch: str) -> dict:
    post_url = urljoin(url, "/latestVersion")
    params = {
        "package": package,
        "branch": branch
    }
    post_url = post_url+"?"+urlencode(params)
    try:
        response = requests.get(post_url)
        data = json.loads(response.text)
        content = json.loads(data["content.json"])
        if (data["status"] == 200):
            return content
        else:
            return None
    except Exception as e:
        print(e)
        return None


def checkVersion(package: str, branch: str, version: str) -> bool:
    post_url = urljoin(url, "/getVersion")
    params = {
        "package": package,
        "branch": branch,
        "version": version
    }
    post_url = post_url+"?"+urlencode(params)
    try:
        response = requests.get(post_url)
        data = json.loads(response.text)
        clist = list(data["list"])
        if clist == []:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


def zipDir(dirpath, outFullName):
    """
    压缩指定文件夹
    :param dirpath: 目标文件夹路径
    :param outFullName: 压缩文件保存路径+xxxx.zip
    :return: 无
    """
    zip = zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED)
    for path, dirnames, filenames in os.walk(dirpath):
        # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
        fpath = path.replace(dirpath, '')

        for filename in filenames:
            zip.write(os.path.join(path, filename),
                      os.path.join(fpath, filename))


if (__name__ == "__main__"):
    is_overwrite = False
    url = input("·Please input the url of the server(necessary): ")
    if (testUrl(url) == False):
        print("[Error] The url is not available")
        os.system("pause")
        exit(0)
    else:
        print("[Info] The url is available")

    package = input("·Please input the name of the package(necessary): ")
    branch = input("·Please input the branch of the package(necessary): ")
    lastVersion = getLatestVersion(url, package, branch)
    if (lastVersion == None):
        print("[Warning] Get the latest version failed")
        os.system("pause")
        exit(0)
    else:
        print("[Info] The latest version on server is "+lastVersion["version"])
    a, b, c = map(int, lastVersion["version"].split("."))
    c += 1
    default_version = str(a)+"."+str(b)+"."+str(c)  # 默认版本号

    newVersion = input(
        "·Please input the version you want to pack(default:%s): " % default_version)
    if (newVersion == ""):
        newVersion = default_version
    if (checkVersion(package, branch, newVersion) == False):
        print("[Warning] The version has already existed")
        confirm = input("·Do you want to overwrite it?(y/n): ")
        if (confirm == "n"):
            os.system("pause")
            exit(0)
        elif (confirm == "y"):
            is_overwrite = True
        else:
            print("[Error] Invalid input")
            os.system("pause")
            exit(0)
    else:
        print("[Info] The version is available")

    folder_path = input(
        "·Please input the path of the folder you want to pack(necessary): ")
    if (not os.path.exists(folder_path)):
        print("[Error] The folder does not exist")
        os.system("pause")
        exit(0)

    try:
        print("[Info] Start packing...")
        zipDir(folder_path, "%s-%s-%s.zip" % (package, branch, newVersion))
        print("[Info] Pack success")
    except Exception as e:
        print("[Error] Pack failed")
        print(e)
        os.system("pause")
        exit(0)

    lastVersion["version"] = newVersion
    with open("content.json", "w") as f:
        f.write(json.dumps(lastVersion, indent=4))
    print("content.json has been generated according to the last version in the folder...")
    print("You can modify the content.json if you need")
    os.system("pause")

    try:
        post_url = urljoin(url, "/upload")
        files = {
            "file": open("%s-%s-%s.zip" % (package, branch, newVersion), "rb"),
            "content": open("content.json", "rb")
        }
        response = requests.put(post_url,  files=files)
        if (json.loads(response.text)["status"] == 200):
            print("[Info] Upload success")
        else:
            print("[Error] Upload failed")
    except Exception as e:
        print("[Error] Upload failed")
        print(e)
