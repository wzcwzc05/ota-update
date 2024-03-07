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

### JSON配置文件

由于单个设备的包较少，所以维护一个json文件

daemon整体配置文件：

| 键值        | 类型   | 备注                                               |
| ----------- | ------ | -------------------------------------------------- |
| device      | 字符串 | 设备名称                                           |
| description | 字符串 | 描述                                               |
| flask       | JSON   | flask配置项（见下）                                |
| token       | 字符串 | TOKEN                                              |
| package     | 列表   | 列表中每一项是一个`json`，为每个包的`content.json` |

flask配置项：

| 键值  | 类型   | 备注              |
| ----- | ------ | ----------------- |
| host  | 字符串 | 设备启动IP        |
| port  | 整数   | 端口号            |
| debug | 布尔   | 是否开启debug模式 |



### 信息API接口

### 操作API接口

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

此时在url的参数里加上'force=1'可以强制进行写入

- |地址|内容类型|参数|返回值|
  |--|--|--|--|
  |`/upload`|`Content-Type: multipart/form-data`|content : `content.json`<br/>file : 文件|status|

## 三、开发侧

依赖：`requests`

使用：`python pack.py`
