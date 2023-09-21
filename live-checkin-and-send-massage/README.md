## 直播自动签到，弹幕打卡  
关注的人越来越多了，包括小号，每天手动签到打卡也挺累的，写了这个自动化脚本。  
需安装的库 `requests`、 `brotli`、 `collections`、 `urllib3` 等。  

### 使用方法  
在代码开始部分实例化对象时设置：  
>1. `cookie` 填写自己的cookie  
>2. `blackList` 黑名单, 不发送打卡信息, 填写房间号，构成一个列表（很少有时房间号与roomid不同，可抓包查看roomid）  
例：`room_id = ['123456', '123457']`  
>4. `message` 填写弹幕打卡的内容，打卡时会随机抽取一项发送弹幕。数量不限。  
例：`room_massage = ['打卡', '打 卡', '(=・ω・=)', '（￣▽￣）', 'ε=ε=(｀・ω・´)', '(〜￣△￣)〜', '⁄(⁄ ⁄•⁄ω⁄•⁄ ⁄)⁄']`  

填写完成必需内容后运行即可，先签到，然后依次进行弹幕打卡，相隔时间8~20s。  

可在__init__部分更改发送弹幕的延时等。  

### 完整代码  
[查看完整代码](https://github.com/mlyde/bili-automatic/blob/main/live-checkin-and-send-massage/live-checkin-and-send-massage.py) (2023.9 by mlyde)  
