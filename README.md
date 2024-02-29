OTA


## 一、生产运行侧

### daemon程序

由于单个设备的包较少，所以维护一个json文件

daemon整体配置文件：

| 键值        | 类型   | 备注                                               |
| ----------- | ------ | -------------------------------------------------- |
| device      | 字符串 | 设备名称                                           |
| description | 字符串 | 描述                                               |
| package     | 列表   | 列表中每一项是一个`json`，为每个包的`content.json` |

包的`content.json`

| 键值         | 类型   | 备注                 |
| ------------ | ------ | -------------------- |
| package      | 字符串 | 包名称               |
| description  | 字符串 | 描述                 |
| version      | 字符串 | 版本号               |
| branch       | 字符串 | 分支                 |
| local        | 字符串 | 本地包位置           |
| remote       | 字符串 | OTA服务器            |
| sha256       | 字符串 | 升级包的SHA256校验码 |
| BeforeUpdate | 字符串 | 更新前指令           |
| AfterUpdate  | 字符串 | 更新后指令           |
| dependencies | JSON   | 依赖                 |
| restore      | 字符串 | 更新后执行的脚本地址 |

## 二、OTA服务器

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

API地址:`/otafiles/<SHA256>`

文件的文件名会被重命名为SHA256的格式存储，以期避免复杂的目录结构，也方便直接取用。

### API接口

status正常返回200，404代表无法找到，400代表参数错误或服务器错误

| 地址          | 参数                                                 | 返回值               |
| ------------- | ---------------------------------------------------- | -------------------- |
| `/maxVersion` | `package=` 包名<br>`branch=`分支                     | 该包的`content.json` |
| `/getVersion` | `package=` 包名<br>`branch=`分支<br>`version=`版本号 | 该包的`content.json` |

### 上传接口

用PUT的方式上传

status正常返回200，`content.json`格式有误返回`400`，SHA256有误返回`304`

为了以防上传丢包导致问题，服务器会重新进行包校验，如果与`content.json`不符，服务器不会接受这个文件

- | 地址      | 内容类型                          | 参数                                    | 返回值 |
  | --------- | --------------------------------- | --------------------------------------- | ------ |
  | `/update` | `Content-Type: multipart/form-data` | content : `content.json`<br>file : 文件 | status|

## 三、图示

<img src="https://picture-1304336638.cos.ap-nanjing.myqcloud.com/img/image-20240227200957899.png" alt="image-20240227200957899" style="zoom:67%;" />
