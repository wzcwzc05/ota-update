import requests
import json
import os
import zipfile
import hashlib
from urllib.parse import urljoin, urlencode

# 定义颜色代码


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def colored_output(color, message):
    return f"{color}{message}{Colors.ENDC}"


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
        print(colored_output(Colors.FAIL, e))
        return False


def getLatestVersion(url: str, package: str, branch: str) -> dict:
    post_url = urljoin(url, "/latestVersion")
    params = {
        "package": package,
        "branch": branch
    }
    post_url = post_url + "?" + urlencode(params)
    try:
        response = requests.get(post_url)
        data = json.loads(response.text)
        content = json.loads(str(data["content.json"]))
        if (data["status"] == 200):
            return content
        else:
            return None
    except Exception as e:
        print(colored_output(Colors.FAIL, e))
        return None


def checkVersion(url: str, package: str, branch: str, version: str) -> bool:
    post_url = urljoin(url, "/getVersion")
    params = {
        "package": package,
        "branch": branch,
        "version": version
    }
    post_url = post_url + "?" + urlencode(params)
    try:
        response = requests.get(post_url)
        data = json.loads(response.text)
        clist = list(data["list"])
        if clist == []:
            return True
        else:
            return False
    except Exception as e:
        print(colored_output(Colors.FAIL, e))
        return False


def zipDir(dirpath, outFullName):
    """
    压缩指定文件夹
    """
    zip = zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED)
    for path, dirnames, filenames in os.walk(dirpath):
        fpath = path.replace(dirpath, '')
        for filename in filenames:
            zip.write(os.path.join(path, filename),
                      os.path.join(fpath, filename))


if __name__ == "__main__":
    is_overwrite = False
    url = input(colored_output(Colors.OKBLUE,
                "·Please input the url of the server (necessary): "))
    if not testUrl(url):
        print(colored_output(Colors.FAIL, "[Error] The url is not available"))
        os.system("pause")
        exit(0)
    else:
        print(colored_output(Colors.OKGREEN, "[Info] The url is available"))

    package = input(colored_output(
        Colors.OKBLUE, "·Please input the name of the package (necessary): "))
    branch = input(colored_output(
        Colors.OKBLUE, "·Please input the branch of the package (necessary): "))
    local = input(colored_output(
        Colors.OKBLUE, "·Please input local storage of the package (necessary): "))
    lastVersion = getLatestVersion(url, package, branch)
    if lastVersion is None:
        print(colored_output(Colors.WARNING,
              "[Warning] Get the latest version failed"))
        lastVersion = {
            "local": local,
            "branch": branch,
            "remote": url,
            "sha256": "",
            "package": package,
            "restore": "",
            "version": "0.0.0",
            "AfterUpdate": "",
            "description": "",
            "BeforeUpdate": "",
            "dependencies": {}
        }

    else:
        print(colored_output(Colors.OKGREEN,
              f"[Info] The latest version on server is {lastVersion['version']}"))
    a, b, c = map(int, lastVersion["version"].split("."))
    c += 1
    default_version = f"{a}.{b}.{c}"

    newVersion = input(colored_output(
        Colors.OKBLUE, f"·Please input the version you want to pack (default:{default_version}): "))
    if newVersion == "":
        newVersion = default_version
    if not checkVersion(url, package, branch, newVersion):
        print(colored_output(Colors.WARNING,
              "[Warning] The version has already existed"))
        confirm = input(colored_output(
            Colors.OKBLUE, "·Do you want to overwrite it? (y/n): "))
        if confirm == "n":
            os.system("pause")
            exit(0)
        elif confirm == "y":
            is_overwrite = True
        else:
            print(colored_output(Colors.FAIL, "[Error] Invalid input"))
            os.system("pause")
            exit(0)
    else:
        print(colored_output(Colors.OKGREEN,
              "[Info] The version is available"))

    folder_path = input(colored_output(
        Colors.OKBLUE, "·Please input the path of the folder you want to pack (necessary): "))
    if not os.path.exists(folder_path):
        print(colored_output(Colors.FAIL, "[Error] The folder does not exist"))
        os.system("pause")
        exit(0)

    try:
        print(colored_output(Colors.OKGREEN, "[Info] Start packing..."))
        zipDir(folder_path, f"{package}-{branch}-{newVersion}.zip")
        with open(f"{package}-{branch}-{newVersion}.zip", "rb") as f:
            lastVersion["sha256"] = hashlib.sha256(f.read()).hexdigest()
        print(colored_output(Colors.OKGREEN, "[Info] Pack success"))
    except Exception as e:
        print(colored_output(Colors.FAIL, "[Error] Pack failed"))
        print(colored_output(Colors.FAIL, str(e)))
        os.system("pause")
        exit(0)

    lastVersion["version"] = newVersion
    with open("content.json", "w") as f:
        f.write(json.dumps(lastVersion, indent=4))
    print(colored_output(Colors.OKGREEN,
          "content.json has been generated according to the last version in the folder..."))
    print(colored_output(Colors.OKBLUE, "You can modify the content.json if you need"))
    print(lastVersion)
    os.system("pause")

    try:
        post_url = urljoin(url, "/upload")
        print(colored_output(Colors.OKGREEN,
              f"[Info] The upload url is {post_url}"))
        confirm = input(colored_output(
            Colors.OKBLUE, "· Do you want to upload now? (y/n): "))

        if confirm == "n":
            print(colored_output(Colors.OKBLUE,
                  "[Info] Upload cancelled by user."))
            os.system("pause")
            exit(0)
        elif confirm != "y":
            print(colored_output(Colors.FAIL, "[Error] Invalid input"))
            os.system("pause")
            exit(0)

        if is_overwrite:
            post_url += "?overwrite=1"

        with open(f"{package}-{branch}-{newVersion}.zip", "rb") as file:
            files = {"file": file}
            response = requests.put(post_url, files=files, data={
                                    "content": json.dumps(lastVersion)})

        print(colored_output(Colors.OKGREEN, "[Info] Uploading..."))

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == 200:
                print(colored_output(Colors.OKGREEN,
                      "[Info] Upload successful!"))
            else:
                print(colored_output(
                    Colors.FAIL, f"[Error] Upload failed: {data.get('error', 'No error message available.')}"))
        else:
            print(colored_output(Colors.FAIL,
                  f"[Error] HTTP error during upload: {response.status_code}"))
    except Exception as e:
        print(colored_output(Colors.FAIL, "[Error] Upload failed"))
        print(colored_output(Colors.FAIL, str(e)))
    finally:
        os.system("pause")
