OTA更新系统

# OTA更新系统

OTA（Over-The-Air）更新对于物联网（IoT）系统非常重要，在整个物联网系统中，各个设备的控制方式、编程语言、配置文件往往有着十分巨大的区别。本文旨在探索出一种高可用性、低耦合性的物联网升级结构。

## 一、更新包设计

由于各个设备（模块）之间的差异较大，我们需要一种特殊的打包方式，在保留文件各方面关系与属性的情况下对整个文件夹进行传输；同时，为了保证能方便地读取更新包的各类信息，例如版本号、包名、前后启动等方式，我们需要将文件格式进行一定程度的规范修改。

### 1.包结构

```bash
- package
	- AfterUpdate.bat
	- BeforeUpdate.bat
	- AfterUpdate.sh
	- BeforeUpdate.sh
	- data.json
	- folder
		- src
		- build
		- makefile
		- test.sln
		...
```
在打包方式方面，我们选择了`tar`这一文件归档类型。相比于其他的压缩类型，tar类型的压缩率不高，但是其能完整保留所归档文件的属性，例如Linux文件的权限等。

同时我们规定必须在一个规范的更新包中，在其根目录下必须包含一个`data.json`文件，以下是这个`json`文件的规范

```json
{
    "name": "test",
    "author": "test",   
    "description": "test",
    "updateURL": "https://localhost:8080/test",
    "version": "1.0.0",
    "branch": "major",
    "AfterUpdate": "",
    "BeforeUpdate": ""
}
```

`name`:包名，`author`:作者名，`description`:描述，`updateURL`是更新地址，`version`:当前包的版本，`branch`:当前分支，`AfterUpdate`:更新后执行的命令，`BeforeUpdate`:更新前执行的命令

最终得到的结果是`test-1.0.0-major.pk`

### 2.打包方式

开发者可通过提供的Python文件通过命令进行打包，假设脚本为`pack.py`

```bash
python3 pack.py FOLDER --config data.json
```

其中`data.json`同上文包结构的`data.json`文件

如果有git版本管理工具，可以尝试通过

```bash
python3 pack.py FOLDER --config auto
```

来自动生成`version`，`branch`，`name`，`author`这四个信息

如果要加入更新脚本，可以通过

```bash
python3 pack.py FOLDER --updatescript AfterUpdate.sh BeforeUpdate.sh
```

### 3.上传包

开发者可通过提供的Python文件通过命令上传包至OTA服务器，假设脚本为`update.py`

```bash
python3 update.py XXX.tar.gz
```

### 4.更新包

当本地的daemon程序检测到云端OTA服务器有更新的版本后，首先执行`data.json`中的`BeforeUpdate`中的命令，然后从云端下载新版的pk包，然后替换原先的文件夹中的所有内容，最后执行`data.json`中的`AfterUpdate`中的命令。

同时，我们允许内嵌更新脚本，当`data.json`中`AfterUpdate`或`BeforeUpdate`值为`default`时，根据系统类型，`Windows`执行`bat`文件，更新前执行`BeforeUpdate.bat`脚本，更新后执行`AfterUpdate.bat`脚本；`Linux`执行`sh`文件，更新前执行`BeforeUpdate.sh`脚本，更新后执行`AfterUpdate.sh`脚本

## 二、整体设计

### 1、服务端

服务端要实现的功能如下：

- 维护一个文件服务器，提供更新文件下载服务
- 反馈当前模块不同分支的版本
- 提供校验文件服务

例如，有个包是`test`，这个包有三个分支`major`、`beta`、`preRelease`.

那么OTA服务器的文件夹应当如下

```bash
- OTA
	- test
		- major
			- test-1.0.0-major.pk
			- test-2.0.0-major.pk
		- beta
			- test-1.0.1-beta.pk
			- test.2.0.1-beta.pk
		- preRelease
			- test-0.9.0-preRelease.pk
```

那么当我们访问文件服务器`http://127.0.0.1/test`时，返回如下`json`值

```json
{
  "status": 200,
  "major": {
    "version": "2.0.0",
    "SHA256": ""
  },
  "beta": {
    "version": "1.0.1",
    "SHA256": ""
  },
  "preRelease": {
    "version": "0.9.0",
    "SHA256": ""
  }
}

```

如果该包不存在，则返回

```json
{
  "status": 404
}
```

当我们访问文件服务器`http://127.0.0.1/test/major`时，返回如下`json`值

```json
{
  "status": 200,
  "files": {
    "test-1.0.0-major.pk": "SHA256",
    "test-2.0.0-major.pk": "SHA256"
  }
}
```

### 2、客户端

客户端要实现的功能如下：

- 监视所有注册的包
- 如果云端有更新的版本进行更新

`daemon`程序定时运行，每次运行时读取配置文件`config.json`，配置文件例如：

```json
{
    "cache": "/tmp",
    "test": {
        "localPath": "/home/wzcwzc0/test",
        "remotePath": "http://127.0.0.1/test"
    },
    "helloworld":{
        "localPath": "/home/wzcwzc0/helloworld",
        "remotePath": "http://127.0.0.1/helloworld"
    }
}
```

`cache`为下载包的位置，以下的所有内容即为监视的包，`localPath`为本地包所在路径，`remotePath`为远程更新服务器所在路径。

### 3、开发端

开发者可通过提供的Python文件通过命令进行打包，假设脚本为`pack.py`

```bash
python3 pack.py FOLDER --config data.json
```

其中`data.json`同上文包结构的`data.json`文件

如果有git版本管理工具，可以尝试通过

```bash
python3 pack.py FOLDER --config auto
```

来自动生成`version`，`branch`，`name`，`author`这四个信息

如果要加入更新脚本，可以通过

```bash
python3 pack.py FOLDER --updatescript AfterUpdate.sh BeforeUpdate.sh
```

开发者可通过提供的Python文件通过命令上传包至OTA服务器，假设脚本为`update.py`

```bash
python3 update.py XXX.pk
```

`update.py`可以通过读取目录下的`config.json`来决定所需要上传的服务器

```json
{
  "host":"127.0.0.1",
  "port":80
}
```

