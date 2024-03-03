OTA


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

### 信息API接口

status正常返回200，400代表参数错误或服务器错误

| 地址             | 参数                 | 返回值 |
| ---------------- | -------------------- | ------ |
| `/getUpdateInfo` | `token=` |- status<br>- packages(一个列表，存储所有有升级的版本的包)        |
| `/getAll`        | `token=` |- status<br/>- packages(一个列表，存储所有的包) |
| `/getPackage` | `token=`<br>`package=`包名<br>`branch=`分支名 |- status<br/>- content(该包的content.json) |
| `/getStatus` | `token=` |- status<br/>- update(目前该设备所在的升级状态) |
| `/getUpdatelist` | `token=` |- status<br>- updateList(一个列表，当前的升级队列) |

例子如下:

- `http://192.168.1.100:5000/getUpdateInfo?token=123456`

  返回值例如：

    ```json
    {
        "status":200,	// 200代表正常返回，400代表服务器错误，403代表token错误
        "packages":[
            ["test","0.0.1","0.0.2"],	// 第一个是包名，第二个是设备版本，第三个是云端版本
            ...
        ]
    }
    ```

- `http://192.168.1.100:5000/getAll?token=123456`

  返回值例如：

  ```json
  {
  	"status":200,	// 200代表正常返回，400代表服务器错误，403代表token错误
      "packages":[
          ["test","0.0.1"],	// 第一个是包名，第二个是设备版本
          ...
      ]
  }
  ```

  - 

- `http://192.168.1.100:5000/getPackage?token=123456&package=test&branch=major`

  返回值例如：

  ```json
  {
  	"status":200,	// 200代表正常返回，400代表服务器错误，403代表token错误, 404代表未找到该包
      "content":{
          ...	// 参见上文中的content.json
      }
  }
  ```

- `http://192.168.1.100:5000/getStatus?token=123456`

  返回值例如：

  ```json
  {
  	"status":200,	// 200代表正常返回，400代表服务器错误，403代表token错误
      "update":{
        "status": "normal",  // normal, updating 分别为正常状态，正在升级
        "package": "",	//	如果正在进行更新，返回正在进行更新的包名
        "branch": "",		//	如果正在进行更新，返回正在进行更新的包分支
        "stage": "BeforeUpdate",  //BeforeUpdate, Downloading, Updating, AfterUpdate, restore
          					  //分别为升级前准备，正在下载，升级中，升级后，重建现场
      }
  }
  ```

- `http://192.168.1.100:5000/getUpdatelist?token=123456`

  返回值例如：

  ```json
  {
  	"status":200,	// 200代表正常返回，400代表服务器错误，403代表token错误
      "updateList":[	// 按照升级队列中的顺序
          ["test","0.0.1","0.0.2"],	// 第一个是包名，第二个是设备版本，第三个是云端版本
          ...
      ]
  }
  ```

  

### 操作API接口

status正常返回200，400代表参数错误或服务器错误

| 地址             | 参数                                            | 返回值        | 说明                             |
| ---------------- | ----------------------------------------------- | ------------- | -------------------------------- |
| `/updatePackage` | `token=`<br/>`package=`包名<br/>`branch=`分支名 | - status      | 将指定包的升级加入升级队列       |
| `/updateAll`     | `token=`                                        | - status      | 升级所有的包                     |
| `/stopUpdate`    | `token=`                                        | - status<br/> | 删除升级队列中除正在执行的所有包 |

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

| 地址             | 参数                                                       | 返回值               |
| ---------------- | ---------------------------------------------------------- | -------------------- |
| `/latestVersion` | `package=`包名<br>`branch=`分支                            | 该包的`content.json` |
| `/getVersion`    | `package=` 包名(必须)<br>`branch=`分支<br>`version=`版本号 | 该包的`content.json` |

### 上传接口

用PUT的方式上传

status正常返回200，`content.json`格式有误返回`400`，SHA256有误返回`304`

为了以防上传丢包导致问题，服务器会重新进行包校验，如果与`content.json`不符，服务器不会接受这个文件

- | 地址      | 内容类型                          | 参数                                    | 返回值 |
  | --------- | --------------------------------- | --------------------------------------- | ------ |
  | `/upload` | `Content-Type: multipart/form-data` | content : `content.json`<br>file : 文件 | status|

## 三、图示

<img src="https://picture-1304336638.cos.ap-nanjing.myqcloud.com/img/image-20240227200957899.png" alt="image-20240227200957899" style="zoom:67%;" />
