## 直播自动签到，弹幕打卡  
关注的人越来越多了，包括小号，每天手动签到打卡也挺累的，写了这个自动化脚本。  
需安装的库 `requests`、 `brotli`、 `collections`、 `urllib3` 等。  

### 使用方法  
在代码开始部分进行设置：  
>1. `cookie` 填写自己的cookie  
>2. `room_id` 填写房间号，构成一个列表（很少有时房间号与roomid不同，可抓包查看roomid）  
例：`room_id = ['123456', '123457']`  
>3. `room_name` 填写房间号对应up名称，填写顺序与room_id房间号顺序一致，方便读取log查看运行状态，若长度小于room_id长度，会报错。  
例：`room_name = ['up1号', 'up2号']`  
>4. `room_massage` 填写弹幕打卡的内容，打卡时会随机抽取一项发送弹幕。数量不限。  
例：`room_massage = ['打卡', '打 卡', '(=・ω・=)', '（￣▽￣）', 'ε=ε=(｀・ω・´)', '(〜￣△￣)〜', '⁄(⁄ ⁄•⁄ω⁄•⁄ ⁄)⁄']`  

填写完成必需内容后运行即可，先签到，然后依次进行弹幕打卡，相隔时间8~20s。  

### 完整代码  
[查看完整代码](https://github.com/mlyde/bili-automatic/blob/main/live-checkin-and-send-massage/live-checkin-and-send-massage.py) (2021.5 by mlyde)  
