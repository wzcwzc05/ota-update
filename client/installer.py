import os
import json
import time
# 判断系统环境是否为Linux
if os.name != 'posix':
    print('Only support Linux system!')
    exit(0)

# 判断是否root用户
if os.getuid() != 0:
    print('Not root!')
    exit(0)

print("--------------安装环境--------------")
# 安装依赖
os.system("apt-get install python3-pip -y")
os.system('pip install flask requests')
print("--------------环境安装完成--------------\n")
time.sleep(1)
print("--------------初始化配置文件--------------")
try:
    with open("device.json", "r", encoding="utf-8") as f:
        device_json = json.load(f)
    device_json['device_id'] = 0
    device_json['device'] = input("输入设备名称:")
    device_json["description"] = input("输入设备描述:")
    st = input(
        "输入注册服务地址(default:%s):" % device_json["registry"])
    if (st != ""):
        device_json["registry"] = st
    print(device_json)
    with open("device.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(device_json))
    print("--------------配置文件初始化完成--------------\n")
    time.sleep(1)
except Exception as e:
    print("[Error] 配置文件初始化失败！")
    print(e)
    exit(0)

# 创建服务
print("--------------创建服务--------------")
try:
    with open("start.sh", 'w', encoding="utf-8") as f:
        cmd_str = "#!/bin/sh\ncd %s && python3 daemon.py" % os.getcwd()
        f.write(cmd_str)
    os.system("chmod +x start.sh")
    service_name = input("输入服务名称(default:ota-client):")
    if service_name == "":
        service_name = "ota-client"
    with open("%s.service" % (service_name), "w", encoding="utf-8") as f:
        f.write("[Unit]\nDescription=ota-client\nAfter=network.target\n\n[Service]\nExecStart=%s/start.sh\nRestart=always\nRestartSec=1\n[Install]\nWantedBy=multi-user.target\n" % os.getcwd())
    os.system('cp ./%s.service /etc/systemd/system/' % service_name)
    os.system('systemctl daemon-reload')
    time.sleep(1)
    print("--------------服务创建完成--------------\n")

except Exception as e:
    print("[Error] 服务创建失败！")
    print(e)
    exit(0)

print("服务名称：%s" % service_name)
print("地址：%s" % os.getcwd())
print("安装完成！")
