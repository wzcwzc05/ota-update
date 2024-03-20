# OTA

包的`content.json`

| 键值         | 类型   | 备注                 |
| ------------ | ------ | -------------------- |
| package      | 字符串 | 包名称               |
| description  | 字符串 | 描述                 |
| updateInfo   | 字符串 | 更新描述             |
| version      | 字符串 | 版本号               |
| branch       | 字符串 | 分支                 |
| local        | 字符串 | 本地包位置           |
| remote       | 字符串 | OTA服务器            |
| sha256       | 字符串 | 升级包的SHA256校验码 |
| BeforeUpdate | 字符串 | 更新前指令           |
| AfterUpdate  | 字符串 | 更新后指令           |
| dependencies | JSON   | 依赖                 |

## 一、生产运行侧

daemon程序

依赖:`flask`、`requests`

<img src="https://picture-1304336638.cos.ap-nanjing.myqcloud.com/img/Client.png" alt="Client" style="zoom:67%;" />

### JSON配置文件

由于单个设备的包较少，所以维护一个json文件

daemon整体配置文件(`device.json`)：

| 键值        | 类型   | 备注                                               |
| ----------- | ------ | -------------------------------------------------- |
| id          | INT    | 设备唯一id                                         |
| device      | 字符串 | 设备名称                                           |
| registry    | 字符串 | 设备注册服务地址                                   |
| description | 字符串 | 描述                                               |
| flask       | JSON   | flask配置项（见下）                                |
| package     | 列表   | 列表中每一项是一个`json`，为每个包的`content.json` |

flask配置项：

| 键值  | 类型   | 备注              |
| ----- | ------ | ----------------- |
| host  | 字符串 | 设备启动IP        |
| port  | 整数   | 端口号            |
| debug | 布尔   | 是否开启debug模式 |

例如：

```json
{
    "device": "mytest",
    "device_id": 21,
    "description": "test device",
    "registry": "http://10.90.0.54:6500/",
    "flask": {
        "host": "0.0.0.0",
        "port": 10000,
        "debug": false
    },
    "packages": [
        {
            "local": "./test",
            "branch": "major",
            "remote": "http://127.0.0.1:5500",
            "sha256": "bca638ef441682e69eda19adeee00cd354b1384764529d19590d65d3a29e05b4",
            "package": "test",
            "restore": "",
            "version": "0.0.1",
            "AfterUpdate": "",
            "description": "",
            "BeforeUpdate": "",
            "dependencies": {}
        }
    ]
}
```

### 信息API接口

| 地址       | 参数 | 返回值                                         |
| ---------- | ---- | ---------------------------------------------- |
| `/getInfo` | 无   | -"status"<br/>-"content":该设备的`device.json` |

### 操作API接口

| 地址           | 内容类型                            | 参数                                           | 返回值 |
| -------------- | ----------------------------------- | ---------------------------------------------- | ------ |
| `/startUpdate` | `Content-Type: multipart/form-data` | content : `content.json`（包的`content.json`） | status |

## 二、OTA服务器

依赖:`flask`、`pymysql`

### 配置文件

### 数据库

ota表：

| 字段    | 类型    | 备注               |
| ------- | ------- | ------------------ |
| id      | INT     |                    |
| name    | VARCHAR | 包名               |
| version | VARCHAR | 版本号             |
| branch  | VARCHAR | 分支               |
| content | JSON    | 包的`content.json` |

### 文件管理

文件获取地址:`/otafiles/<package>/<branch>/<package>-<branch>-<version>.zip`

例如，我需要`helloworld`包的`major`分支的`0.1.0`版本的包

那么访问`http://IP:PORT/otafiles/helloworld/major/helloworld-major-0.1.0.zip`即可下载文件


### API接口

status正常返回200，404代表无法找到，400代表参数错误或服务器错误

|地址|参数|返回值|
|--|--|--|
|`/latestVersion`|`package=`包名<br/>`branch=`分支|-"status"<br/>-"content.json":该包的`content.json`|
|`/getVersion`|`package=` 包名(必须)<br/>`branch=`分支<br/>`version=`版本号|-"status"<br/>-"list":一个列表，存储所有的查询结果|

### 上传接口

用PUT的方式上传status正常返回`200`

为了以防上传丢包导致问题，服务器会重新进行包校验，如果与`content.json`不符，服务器不会接受这个文件

如果在上传时发现文件已存在或者数据库中已经有该版本的记录时，不会进行修改，

此时在url的参数里加上'overwrite=1'可以强制进行写入

- |地址|内容类型|参数|返回值|
  |--|--|--|--|
  |`/upload`|`Content-Type: multipart/form-data`|content : `content.json`<br/>file : 文件|status|

## 三、开发侧

依赖：`requests`

使用：`python pack.py`

主要流程：

1. 输入服务器的URL，并检查其可用性。
2. 输入包名和分支名，获取服务器上的最新版本信息。
3. 输入要打包的版本号，检查其是否已存在于服务器上。如果已存在，可以选择覆盖或退出。
4. 输入要打包的文件夹路径，如果文件夹存在，则开始打包。
5. 打包成功后，生成一个包含最新版本信息的`content.json`文件，开发者可以在上传前修改这个`content.json`文件。
6. 最后，将打包的zip文件和`content.json`文件上传到服务器

## 四、设备注册服务

<img src="https://picture-1304336638.cos.ap-nanjing.myqcloud.com/img/%E8%AE%BE%E5%A4%87%E6%B3%A8%E5%86%8C.png" alt="设备注册" style="zoom:67%;" />

### 数据库

devices表：

|字段|类型|备注|
|--|--|--|
|id|INT||
|device|VARCHAR|设备名|
|address|VARCHAR|设备地址|
|content|JSON|设备内包情况|
|status|JSON|设备状态|
|lastupdate|TIMESTAMP|最后更新时间|

### 设备侧API接口

接受从生产运行侧的注册和注销请求

每30s接受一次心跳包，超过120s未接收到心跳包即注销设备

|地址|内容类型|参数|返回值|
|--|--|--|--|
|`/register`|`Content-Type: multipart/form-data`|content : `device.json`<br/>address : 设备管理地址|status|
|`/logout`|`Content-Type: multipart/form-data`|id : 设备id|status|
|`/heartbeat`|`Content-Type: multipart/form-data`|id : 设备id|status|

接受从设备上的更新状态

|地址|内容类型|参数|返回值|
|--|--|--|--|
|`/updateInfo`|`Content-Type: multipart/form-data`|content : `update.json`|status|

`update.json`

若是正常过程升级：

```json
{
  "update": {
    "device": 1,	// 正在执行升级的设备id，若为0则代表没有任何任务在进行
    "package": {	// 正在执行升级的包
      "package": "test",
      "version": "1.0.0",
      "branch": "major"
    },
    "status": "Downloading"	// 升级状态
  }
}
```

若是出现错误：

```json
{
  "update": {
    "device": 1,	// 正在执行升级的设备id，若为0则代表没有任何任务在进行
    "package": {	// 正在执行升级的包
      "package": "test",
      "version": "1.0.0",
      "branch": "major"
    },
    "status": "Failed"	// 升级状态
  }
}
```

### 信息API接口

返回场景内的所有设备与包信息

|地址|参数|返回值||
|--|--|--|--|
|`/getAllInfo`|无|-"status"<br/>-"devices":所有设备的包的情况例子如下||

```json
{
  "devices": [    // 一个列表，存储所有的设备
    {
      "id": 1,    // 设备id
      "packages": [    // 设备上的所有的包，包含包名、包版本和包分支
        {
          "package": "test",
          "version": "1.0.0",
          "branch": "major"
        },
        ...
      ]
    },
    {
      "id": 2,    //    设备id    
      "packages": [
        {
          "package": "test1",
          "version": "1.0.0",
          "branch": "major"
        },
        ...
      ]
    },
    ...
  ]
}

```
|地址|参数|返回值||
|--|--|--|--|
|`/getDeviceInfo`|id=设备id|-"status"<br/>-"id":设备id<br/>-"packages":设备上所有的包||

```json
{
      "id": 1,    // 设备id
      "packages": [    // 设备上的所有的包，包含包名、包版本和包分支
        {
          "package": "test",
          "version": "1.0.0",
          "branch": "major"
        },
        ...
      ]
}
```
|地址|参数|返回值||
|--|--|--|--|
|`/getStatus`|无|-"status"<br/>-"update":升级状态||

```json
{
  "update": {
    "device": 1,	// 正在执行升级的设备id，若为0则代表没有任何任务在进行
    "package": {	// 正在执行升级的包
      "package": "test",
      "version": "1.0.0",
      "branch": "major"
    },
    "status": "Downloading"	// 升级状态
  }
}

```

升级状态分为：

- BeforeUpdate：升级前准备
- Downloading：下载包
- Updating：替换中
- AfterUpdate：升级后准备
- Restore：重建现场

| 地址             | 参数 | 返回值                                     |      |
| ---------------- | ---- | ------------------------------------------ | ---- |
| `/getUpdatelist` | 无   | -"status"<br/>-"list":注册服务中的更新队列 |      |

获取更新队列
```json
{
  "list": [
    {
      "id": 1,	// 设备id
      "package": "test",	// 包名
      "version": "1.0.1",	// 包版本
      "branch": "major"	// 包分支
    },
    ...
  ]
}
```
获取当前升级任务的日志

| 地址            | 参数 | 返回值                                                  |      |
| --------------- | ---- | ------------------------------------------------------- | ---- |
| `/getUpdatelog` | 无   | 一个字符串，自上次All Update Complete之后的所有日志内容 |      |

### 操作API接口

|地址|内容类型|参数|返回值|
|--|--|--|--|
|`/update`|`Content-Type: multipart/form-data`|content : `update.json`<br/>|status|

升级场景内的设备与包，content的内容例子如下

```json
{
  "devices": [    // 一个列表，存储所有需要升级的设备
    {
      "id": 1,    // 设备id
      "packages": [    // 需要升级的包的列表，包含包的名称,分支和版本
        {
          "package": "test",
          "branch": "major",
          "version": "0.0.1"
        },
        ...
      ]
    },
    {
      "id": 2,    
      "packages": [
        {
          "package": "test1",
          "version": "1.0.0",
          "branch": "major"
        },
        ...
      ]
    },
    ...
  ]
}
```
若当前存在非空的升级队列`status`返回400
|地址|内容类型|参数|返回值|
|--|--|--|--|
|`/delFromlist`|`Content-Type: multipart/form-data`|content : `delete.json`<br/>|status|

删除更新队列中的某些更新内容，`delete.json`的内容例子如下

```json
{
  "items": [
    {
      "id": 1,	// 设备id
      "package": "test",	// 包名
      "version": "1.0.1",	// 包版本
      "branch": "major"	// 包分支
    },
    ...
  ]
}

```